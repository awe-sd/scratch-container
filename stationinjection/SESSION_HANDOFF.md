# ERCOT Station Injection — Session Handoff

Porting `Station_injection.py` to a Snowflake stored procedure, producing station
net injection **broken out by voltage level**, computed purely from State
Estimator (SE) branch flow data.

Account `nnb00838`, user `SDALVI`. Roles: `READ_ONLY` (default, read-only) and
`AW_ACCESS` (has `CREATE TABLE` on `AW.DBO`). Warehouse `READ_ONLY_WH`.

---

## 1. Status

| Item | State |
|---|---|
| Target table `AW.DBO.ERCOTSTATIONINJECTION` | **Created** |
| `build_ercot_xfmr_winding_map.sql` | Written, compiles, **not executed** |
| `sp_load_ercot_station_injection.sql` | Written, compiles, **not executed** |
| Backfill | Not started |

Nothing has been run against the database except read-only exploration. All SQL
in both files has been compile-validated (`only_compile`), and all logic has been
verified against real data via equivalent `SELECT`s.

---

## 2. Files in the workspace

| File | Purpose |
|---|---|
| `Station_injection.py` | **Original Python** being ported. Read-only reference. |
| `build_ercot_xfmr_winding_map.sql` | Creates the exception table + 2 views. **Run first.** |
| `sp_load_ercot_station_injection.sql` | Creates the loader procedure. **Run second.** |
| `create_ercotstationinjection.sql` | DDL for the target table. Already executed. |
| `create_ercotstationloadkv.sql` | Empty/superseded — safe to delete. |
| `Station_Injection.sql`, `Untitled 1.sql` | Ad-hoc scratch. Not part of the pipeline. |

---

## 3. Target table (already created)

```sql
CREATE OR REPLACE TABLE AW.DBO.ERCOTSTATIONINJECTION
    CLUSTER BY (TO_DATE("TIMESTAMP"), NMMSSTATIONCODE, KVLEVEL)
(
    TIMESTAMP       TIMESTAMP_NTZ(0),
    NMMSSTATIONCODE VARCHAR(100),
    KVLEVEL         NUMBER(6,2),
    GENMW           FLOAT,   -- left NULL
    WITHDRAWMW      FLOAT,   -- left NULL
    NETINJECTIONMW  FLOAT
);
```

Modelled on `AW.DBO.ERCOTSTATIONLOAD` (`DATE`, `HOUR`, `NMMSSTATIONCODE`,
`GENMW`, `WITHDRAWMW`, clustered by `date, hour, NmmsStationCode`), with these
deliberate changes:

- `DATE` + `HOUR` replaced by a single full-resolution `TIMESTAMP`
- `KVLEVEL NUMBER(6,2)` added — verified lossless against all 2,242,800 rows of
  `CIMSTATIONVOLTAGELEVEL`: 0 failed casts, range 0.35–765.00, 0 rounding loss.
  Numeric typing also collapses 184 distinct text values to 139 real ones,
  merging `'69'`/`'69.0'`, `'.35'`/`'0.35'` and float noise like
  `'13.1999999999999'`.
- `NETINJECTIONMW` added
- Cluster key uses `TO_DATE("TIMESTAMP")` rather than the raw timestamp — raw
  hourly values give ~8,760 distinct keys/year, which fragments partitions.
  `TO_DATE` is monotonic so range predicates still prune.
- `"TIMESTAMP"` is quoted in the cluster key to avoid a parser ambiguity with
  the type keyword.

---

## 4. Objects the pipeline creates

### `AW.DBO.ERCOTSEXFMRDEVICEFIX` — table, 159 rows

The **only hand-maintained artifact.** Lists the SE transformer devices whose
`TRANSFORMERENDNAME` names the wrong winding (an ERCOT reporting bug). Columns:
`BRANCHDEVICEID`, `BRANCHDEVICENAME`, `STATION`, `REPORTED_ENDNAME`,
`REPORTED_KVLEVEL`, `CORRECT_TRANSFORMERNAME`, `NOTE`.

Seeded by a one-time `INSERT ... SELECT` in the build script. That insert is the
**only** place the fuzzy name-ignoring-kV match runs; it never executes at query
time.

159 rows suffices because the correction is stable — each device maps to exactly
one transformer across all 202 CIM models, so no `CIMFILEID` column is needed.

### `AW.DBO.ERCOTCIMEFFECTIVE` — view

Date → CIM model in force. Built on
`AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE` joined to `AW.DBO.CIMFILE` on
`CIMDATE = EFFECTIVE_THROUGH`.

### `AW.DBO.ERCOTSEXFMRWINDINGMAP` — view

`(CIMFILEID, BRANCHDEVICEID)` → `REPORTED_KV`, `MIRROR_KV`, `SOURCE`. Two halves,
neither containing fuzzy logic:

- `ERCOT` — winding name **and** voltage agree
- `FIX` — transformer from the exception table, voltage from the device's own
  `KVLEVEL`

Devices in the fix table are excluded from the `ERCOT` half, so they cannot
overlap.

### `AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION(P_START_DATE, P_END_DATE)`

Stages into a temp table, then `DELETE` + `INSERT` for the range inside one
transaction. Returns a status string.

---

## 5. The core insight — why the winding table is needed

`ISOERCOTSEBRANCHVIEW.KVLEVEL` identifies **only one end** of a transformer.
ERCOT reports flow on that one side and expects the other side to be equal and
opposite, but the other side's **voltage never appears in the branch data**.
Which side is reported is inconsistent:

| Station | Device | Reported kV | Other winding |
|---|---|---|---|
| STP | `STP_MT1A` | 345 | 25 (generator) |
| CALAVERS | `CALAVERS_22_1_L` | 22 | 138 (transmission) |
| ACSSW | `ACSSW_AX1HH` / `_AX1LH` | 345, 138 | 1 kV star point |

Without the other voltage, **generation behind a GSU is invisible**: STP's 345 kV
bus balances to −2 MW because its 2,604 MW of generation sits at 25 kV, a level
that appears on no branch row.

`AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING` supplies the missing voltage.

### Winding table semantics (established from data, not assumed)

- **One row per winding TERMINAL**, so a winding appears twice with
  `FROMNUM`/`TONUM` reversed. LYTTON_S `AT1H`: `LY_AT1H@345` (real bus) and
  `LY_AT1H@1` (star point). This caused 465 apparent kV mismatches on a
  name-only join — it was fanout, not bad data.
- **`NOMINALKV = 1` is a fictitious star point**, used to model 3-winding banks
  as three star-equivalent legs. ACSSW's bank is three `TRANSFORMERNAME` entries
  (`AX1H`/`AX1L`/`AX1T`), each a real winding plus a 1 kV leg. So
  `TRANSFORMERNAME` is **per-leg**, not per-bank, for star models.
- **No transformer has more than 2 real voltages** — verified 0 of 504,790
  `(CIMFILEID, STATION, TRANSFORMERNAME)` combinations exceed 2, so `MIRROR_KV`
  is never ambiguous.

---

## 6. Attribution rule

Every branch terminal is attributed to the bus it physically touches, signed
positive when flowing **from that bus into the branch**. Summing per
`(station, kV)` gives net injection at that bus; positive = net source, which is
where generation becomes visible.

| Terminal | Level | MW |
|---|---|---|
| Line, station is FROM end | line `KVLEVEL` | `FROMMW` |
| Line, station is TO end | line `KVLEVEL` | `TOMW` |
| Transformer, reported winding | `map.REPORTED_KV` | `FROMMW` |
| Transformer, opposite winding | `map.MIRROR_KV` | `-FROMMW` |

### Verified results at `2026-07-01 12:57`

```
STP      345   ->    -2.00   bus balances, nothing connected at 345
STP       25   -> +2604.60   GENERATION, via the mirror
CPSES     22   -> +2405.60   generation
GUADG   18.1   ->  +939.98   generation
LEG       25   ->  +679.22   generation
CBY    20, 24  ->  +678.83, +520.26
HRZN_SLR 34.5  ->  +197.21   solar generation
SUN_SLR  34.5  ->  +175.33   solar generation
ACSSW    345   ->    -0.01   switchyard, balances to ~0 as it should
```

---

## 7. Decisions and rejected alternatives

Each of these was tried and rejected **with measurement** — worth not re-litigating.

### Mirroring must be unconditional
An earlier version gated it on "only one side reported", counting rows in
`ISOERCOTSEBRANCHDEVICE`. Wrong: 58 transformers have **both** windings defined
as devices, but the second device carries **no flow rows**. Verified over
2026-01-01 → 2026-07-25: sides-with-flow = 1 for **281,126** timestamp/transformer
pairs, and **2 for zero** of them. ERCOT never reports both sides. The guard
suppressed the mirror for CPSES, GUADG, LEG and CBY — CPSES read −29 MW instead
of ~2,380 MW.

### Per-kV bus balance (transformer bus-side terminal only) — REJECTED
Counting only `FROMMW` for transformers gives a true bus balance, but it reads
~0 wherever load or generation sits behind a transformer, i.e. nearly everywhere.
STP returns −2 MW instead of 2,604 MW. Useless for load analysis.

### Strict name+kV join with no fallback — REJECTED
Silently dropped 108 devices / 4,908 MW absolute on 2026-07-01 — mostly solar
plants, losing their entire output. Hence the fix table.

### Fallback keyed on `TRANSFORMERNAME` — REJECTED
Matching `TRANSFORMERENDNAME` directly to `TRANSFORMERNAME` works for
`DUNLAP AT2` and `HRZN_SLR T1` but fails for `AT1H` → `AT1` and `ENS7TR1H` →
`7TR1`. The fix table stores the resolved transformer instead.

### CIM selection by `MAX(CIMFILEID)` — REJECTED
Not time-correct; the model reloads every 1–2 weeks so one call spans versions.

### CIM selection by nearest-forward `CIMDATE` — REPLACED
Worked (79/79 months) but was a derivation. Superseded by the schedule view,
which is authoritative and also gives 100% coverage.

### Line sign convention — OPEN, see §9

---

## 8. Data facts worth keeping

| Fact | Detail |
|---|---|
| `ISOERCOTSEBRANCH` size | **563M rows / 12 GB**, clustered `LINEAR(branchDeviceID)` — **not** by timestamp |
| Pruning | A single day still scans **13–49%** of partitions. **Call with wide date ranges** — a month costs little more than a day. |
| SE branch data range | 2020-01-01 → 2026-07-24 |
| SCED gen data range | 2014-12-03 → 2026-07-25 |
| Winding data starts | **2022-01-04** — the real reason the backfill starts 2022 |
| CIM resolution 2022+ | **1,666 / 1,666 days**, exactly one model each |
| Transformer mapping | 2,540 via `ERCOT` + 108 via `FIX` = **2,648 = 100%**, 0 double-placed |
| `ISOERCOTSEBRANCHDEVICE` | 16,733 rows, `BRANCHDEVICEID` unique (no fanout risk) |
| View `ISOERCOTSEBRANCHVIEW` | Safe — 0 orphan rows, no row loss vs base tables |
| Station names | 4,418 / 4,418 branch stations exist in `ERCOTDAMPSSESTATION` — one namespace |
| **SE timestamps are irregular** | `:57` recently, `:58` in 2021–2022, occasionally on the hour (2022-01-01 has a `13:00:00` sample where every other hour is `:58`). Stored verbatim. Do not assume a fixed minute downstream. |

### CIM model gotchas

- `CIMPATH LIKE '%MP_MarketModel%'` marks **test** models published ~45 days
  early, never in force. They also extend further forward than production
  models, so they would win a nearest-forward lookup outright.
- `CIMDATE` is **not unique** in `CIMFILE` even after excluding test models —
  models get re-posted. 2023-10-03 has CIMFILEID 15 and 18; 2025-12-09 has 141
  and 145 (`RTC_Native`). The "has winding rows" filter breaks these ties
  (exactly one of each pair carries windings).
- The schedule **skips loads**: ERCOT skipped the 2024 holiday loads, so
  `2024Dec.L2` ends 2024-12-17 while the next row starts 2025-01-08 — a 21-day
  hole. Hence `EFFECTIVE_THROUGH` is derived as the day before the **next
  `PRODUCTION_LOAD`**, not the schedule's own `EFFECTIVE_THROUGH` column (which
  is still used as the join key to `CIMDATE`).

---

## 9. Open items

### a) Line sign convention — the one unresolved design question

The stated spec was the **far-end** terminal: "injection at B = A-B `FROMMW` +
B-C `TOMW`", i.e. power *arriving* at B. The implementation uses the **near-end**
instead.

Reason: far-end lines cannot combine with transformer `FROMMW` — opposite sign
conventions. At STP 345 it gives lines −2567.31 plus transformers −2604.60 =
**−5171.91**, a balance of nothing. Since `FROMMW + TOMW` = losses on any branch,
far-end is simply the negation of near-end, so this is purely a sign convention.
Near-end makes generation read **positive** at the generator bus and preserves
`WITHDRAWMW`'s meaning from `ERCOTSTATIONLOAD`.

**To flip to inflow-positive: negate the four MW terms in the `terminals` CTE.**

### b) `GENMW` / `WITHDRAWMW` left NULL

Per instruction, only `NETINJECTIONMW` is solved for. Consequence: with
generation excluded, `NETINJECTIONMW` is exactly `-WITHDRAWMW` would have been,
so the two are redundant by construction.

If generation is wanted later, the SCED path was already mapped out:
`ISOERCOTSCEDGENRESOURCE.GENID` → `ISOERCOTSCEDGEN.GENID` → `RESOURCENAME`
(100% match), then `RESOURCENAME` → station via `ERCOTDAMPSSEGNDEF.GENNAME`.
Three deterministic rules reach ~100%: exact match (1,034), longest `TRAINNAME`
prefix (+96, combined-cycle trains), strip `_J\d+` (+28, joint-ownership shares).
Use **longest**-match, not the Python's first-match-wins. Note `Station_injection.py`
had `isoErcotScedGenResourceView`, which does **not** exist in Snowflake.

### c) Transformer losses are not attributed

The mirror is exactly `-FROMMW`, i.e. a lossless transformer per ERCOT's
convention, so the two sides cancel and winding losses land nowhere. Summing
across `KVLEVEL` gives the station-level figure minus a few MW:

| Station | Sum over kV | Station-level | Diff |
|---|---|---|---|
| STP | 2602.60 | 2604.11 | −1.51 |
| CPSES | 2376.28 | 2380.06 | −3.78 |
| CBY | 1195.86 | 1198.36 | −2.50 |

The old `ERCOTSTATIONLOAD` attributed losses to the station (it summed
`FROMMW + TOMW`), so expect small differences when comparing.

### d) View materialization

`ERCOTSEXFMRWINDINGMAP` scans ~504k winding rows against 16.7k devices on every
procedure run. Cheap relative to the 563M-row branch scan. If it becomes hot,
`CREATE TABLE AS SELECT * FROM` the view and add a refresh step — trade-off is
remembering to refresh.

### e) Clustering mismatch on the source table

`ISOERCOTSEBRANCH` is clustered by `branchDeviceID` while every query here
filters on `TIMESTAMP`. The real fix is on the table (add `TIMESTAMP` as a
leading cluster key, or keep a timestamp-clustered derived table), but it is a
563M-row shared table with other consumers — not a unilateral change.

---

## 10. Next steps

```sql
-- 1. Build mapping objects (role AW_ACCESS)
--    Run build_ercot_xfmr_winding_map.sql sections 1-3, then verification A-F.
--    Expect: 159 fix rows; 0 for all four "MUST return 0" checks.

-- 2. Create the procedure
--    Run sp_load_ercot_station_injection.sql

-- 3. Load one month and inspect before committing to the backfill
CALL AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2022-01-31');

-- 4. Verify generation is visible at machine voltages.
--    NOTE: 2022-era timestamps are stamped :58, not :57.
SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2)
FROM AW.DBO.ERCOTSTATIONINJECTION
WHERE "TIMESTAMP" = '2022-01-03 12:58:00'
  AND NMMSSTATIONCODE IN ('STP','CPSES','HRZN_SLR','ACSSW')
ORDER BY NMMSSTATIONCODE, KVLEVEL;
-- STP should be ~+2600 at 25 kV and ~0 at 345 kV.
-- If these read ~0, the transformer mirror did not fire.

-- 5. Backfill month by month, 2022-01 onward.

-- 6. Ongoing: the Python ran a 3-day window lagging 60-63 days to let SE data
--    settle. Given the clustering, a weekly run over a wider window is cheaper.
--    Candidate for a scheduled `cortex automation`.
```

After a CIM publish, run the detection query in **section 4** of the build script
to catch any newly mislabelled devices, and add them to
`ERCOTSEXFMRDEVICEFIX`. The `SOURCE` column on the map view is a standing
signal — rising `FIX` volume means ERCOT's naming has degraded further.

---

## 11. What the original Python did

Kept for reference; the procedure deliberately diverges in places.

1. **`getStationMW`** — branch flows from `isoErcotSeBranchView`; null station
   names backfilled from the opposite end; `fromMW` summed by
   `(timeStamp, fromStationName)` and `toMW` by `(timeStamp, toStationName)`;
   outer-joined; `WithdrawMW = -fromMW - toMW`.
2. **`getGenMW`** — SCED `TelemeteredOutput` over a window shifted `+15 min`, then
   `ResourceName` → station by **regex-extracting** a `trainName` from an
   alternation of every train name.
3. **`combineStationMW`** — gen summed per `(timestamp, station)` then averaged to
   hourly; withdrawal averaged to hourly; outer-joined on
   `(Date, Hour, NmmsStationCode)`.

Defects found in the original, not carried over:

- **Delete-before-compute.** It deleted the day from SQL Server *and* Snowflake,
  then computed generation. A failure lost the day. The procedure stages first
  and wraps delete+insert in one transaction.
- **Asymmetric error handling.** SQL Server writes unguarded; both Snowflake
  operations wrapped in `try/except` that only logs, so a failure left the two
  systems silently diverged.
- **Regex was order-dependent.** `str.extract` on an alternation is
  first-alternative-wins over `unique()` order, not longest-match. Same data in a
  different order gives a different answer.
- **`drop_duplicates` masked join fanout.** The merge on `trainName` fans out;
  the dedup collapsed it back. Side effect: two distinct units in the same train
  reporting identical MW at the same timestamp are collapsed into one, losing the
  second unit's output.
- **Unmatched generation vanished silently** — `NaN` station → `groupby` drops it,
  no warning.
- **Early return on no branch data** skipped the whole day, so 2014–2019 produced
  nothing despite SCED data existing (branch data starts 2020).
- `genMW["newTimeStamp"] = TimeStamp - 0 minutes` is a no-op.
- The outer merge passes `timeStamp` in both `left_on` and `right_on` and
  downstream code reads `stationMW["timeStamp"]` — relies on pandas collapsing
  the shared key name rather than emitting `_x`/`_y`. Version-sensitive.

One thing the original got right and the port preserves: generation is **summed
across units first, then averaged over intervals** within the hour. Reversing
those changes the answer when units report at different cadences.
