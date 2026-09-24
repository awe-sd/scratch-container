# ERCOT Station Injection — Session Handoff

Porting `Station_injection.py` to a Snowflake stored procedure, producing station
net injection **broken out by voltage level**, computed purely from State
Estimator (SE) branch flow data.

Account `nnb00838`, user `SDALVI`. Roles: `READ_ONLY` (default, read-only) and
`AW_ACCESS` (has `CREATE TABLE` on `AW.DBO`). Warehouse `READ_ONLY_WH`.

Connectivity from this workspace is now via `awconnect` 1.5, key-pair auth, as
`ai_read_only_user` / role `AI_READ_ONLY` — **read-only**. All DDL in this
pipeline (the name-correcting table, the two views, the procedure) must be executed by
sdalvi directly as `AW_ACCESS`; this container can compile-validate and verify
logic via `SELECT` but cannot run it.

---

## 1. Status

| Item | State |
|---|---|
| Target table `AW.DBO.ERCOTSTATIONINJECTION` | **Created** |
| `build_ercot_transformer_winding_map.sql` — `ERCOTCIMEFFECTIVEDATE` view, `ERCOTSETRANSFORMERNAMECORRECTING` table + seed, `ERCOTSETRANSFORMERWINDINGMAP` view, all in `AWDEV.ERCOTRT` | Written, compiles, **not executed** |
| `sp_load_ercot_station_injection.sql` — proc in `AWDEV.ERCOTRT` | Written, compiles, **not executed** |
| Name-correcting table `ERCOTSETRANSFORMERNAMECORRECTING` | **Reinstated** 2026-09-24, redesigned as a strict-join complement — see §7 |
| Backfill | Not started |

Nothing has been run against the database. This container connects only as
`ai_read_only_user` / role `AI_READ_ONLY`, which is **read-only** — it can
compile-validate (`only_compile`) and verify logic via `SELECT`, but cannot
execute DDL. All DDL in this pipeline (the name-correcting table, the two views, the
procedure) must be executed by sdalvi directly as `AW_ACCESS`.

---

## 2. Files in the workspace

| File | Purpose |
|---|---|
| `build_ercot_transformer_winding_map.sql` | Creates `ERCOTCIMEFFECTIVEDATE`, `ERCOTSETRANSFORMERNAMECORRECTING` (+ seed), `ERCOTSETRANSFORMERWINDINGMAP` in `AWDEV.ERCOTRT`. **Run first.** |
| `sp_load_ercot_station_injection.sql` | Creates the loader procedure in `AWDEV.ERCOTRT`. **Run second.** |
| `ercotsetransformernamecorrecting_seed_review.csv` | Review copy of the 133-row name-correcting-table seed (BRANCHDEVICEID, names, kV, corrected winding) — sanity-check before running the seed INSERT. |
| `snowflake_test.py` | Connectivity smoke test — `awconnect` (`read_only` profile) → Snowflake. |
| `SESSION_HANDOFF.md` | This file. |

Target table DDL (`AW.DBO.ERCOTSTATIONINJECTION`) already executed; see §3.

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

Four objects. Three are pure derivations; one (`ERCOTSETRANSFORMERNAMECORRECTING`) is
hand-maintained — the only hand-maintained data anywhere in this pipeline.

### `AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE` — view

A pure mapping of CIMFILEID to `AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE`
rows — no filter on winding coverage, nothing to do with
`ERCOTTRANSFORMERWINDING`. Every DATE in the output comes from the schedule;
`CIMDATE = EFFECTIVE_THROUGH` is only the join key. Timestamp grain (not date
grain — the SE switches models at 23:00 the eve of the schedule's
`PRODUCTION_LOAD`, see §8).

Caveat: a schedule row can map to TWO CIMFILEIDs when ERCOT re-posts a model
(2023Sep.L4 → 15 and 18; 2025Dec.L1 → 141 and 145) — the view lists both, since
they're the same model. Downstream this is harmless because the winding table
holds only one of each pair (build-script verification H asserts that), but it
means winding coverage is not this view's job — a model with no winding rows
loaded yet still resolves here and simply produces no map rows (verification
F / I in the build script).

### `AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING` — table (hand-maintained)

`BRANCHDEVICEID → TRANSFORMERENDNAME` (the corrected winding name). One row
per device whose reported `TRANSFORMERENDNAME` has no winding at its own
`KVLEVEL` in some model it overlaps. sdalvi's principle: the device `KVLEVEL`
is trustworthy, `TRANSFORMERENDNAME` is not — so this table is the only place
a name gets corrected, and everything downstream trusts kV. Seeded once
(133 rows, reviewed at `ercotsetransformernamecorrecting_seed_review.csv`); extend it by
hand when the build script's verification F flags a new device.

### `AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP` — view

`(CIMFILEID, BRANCHDEVICEID)` → one row per real winding of that device's
transformer, including the device's own reported winding. Strict join: winding
name (reported OR fixed) AND kV must both agree (`ABS(diff) <= 0.05`) — no
fuzzy matching at query time. Verified unambiguous for every device in every
model (see §7).

### `AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION(P_START_DATE, P_END_DATE)`

Stages into a temp table, then `DELETE` + `INSERT` into
`AW.DBO.ERCOTSTATIONINJECTION` for the range inside one transaction. Returns a
status string. The reported terminal is read straight off
`ISOERCOTSEBRANCHDEVICE`; the winding map only supplies the mirror.

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
  `(CIMFILEID, STATION, TRANSFORMERNAME)` combinations exceed 2, so the mirror
  terminal derived from the winding map is never ambiguous.
- **The device table is versioned.** A kV re-rating closes the old
  `BRANCHDEVICEID` and opens a new one, in step with the CIM model — so a
  device's `KVLEVEL` is stable and correct for its own active window; it is
  only the reported `TRANSFORMERENDNAME` that can be wrong.

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
| Transformer, reported terminal | device's own `KVLEVEL` (from `ISOERCOTSEBRANCHDEVICE`) | `FROMMW` |
| Transformer, other real winding | the winding map's other real winding at that device (none if the device has no map row) | `-FROMMW` |

The reported terminal is read straight off the device table, not the map, so a
transformer that fails to resolve in the winding map — no map row for that
(model, device) — still contributes its reported side and only loses the
mirror. Because `ERCOTSETRANSFORMERWINDINGMAP` is a strict name+kV join, the mirror is
unique by construction whenever a map row exists (verified, build script
verification D) — there is no "ambiguous, so skip" case to handle at query
time, only "unmapped, so no mirror."

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

### Strict name+kV join, no fallback — REJECTED, then restored WITH a fallback
A bare strict join (winding name AND kV must agree, nothing else) silently
dropped 108 devices / 4,908 MW absolute on 2026-07-01 — mostly solar plants,
losing their entire output. That's the current design's failure mode too, but
now it's covered: `ERCOTSETRANSFORMERNAMECORRECTING` supplies the 133 corrected names the
strict join needs, seeded once and hand-extended from there (see "Name-correcting table
stores TRANSFORMERNAME — REJECTED" below and §7's name-only-join entry for why
the alternative of dropping kV instead was rejected).

### Fallback keyed on `TRANSFORMERNAME` — REJECTED
Matching `TRANSFORMERENDNAME` directly to `TRANSFORMERNAME` works for
`DUNLAP AT2` and `HRZN_SLR T1` but fails for `AT1H` → `AT1` and `ENS7TR1H` →
`7TR1`. The name-correcting table stores the corrected WINDING name instead (see below).

### Name-only join (ignore kV) — REJECTED
Briefly the design 2026-09-24: drop the kV requirement entirely and join on
`(STATION, WINDINGNAME)` alone, since it resolved every device unambiguously.
Rejected on review: it trusts `TRANSFORMERENDNAME`, the field sdalvi's
principle says is unreliable, while `KVLEVEL` — the field that principle says
IS reliable — goes unused. Reverted to a strict join plus a small hand-checked
name-correcting table for the names that fail it, so the trustworthy field (kV) is what
actually decides the match.

### CIM selection by `MAX(CIMFILEID)` — REJECTED
Not time-correct; the model reloads every 1–2 weeks so one call spans versions.
Also unsafe as a "pick the newest model" shortcut for another reason: `CIMFILEID`
is not monotone with model recency — `CIMFILEID` 376 is a 2023-07-18 model
loaded late (see §8).

### CIM selection by nearest-forward `CIMDATE` — REPLACED
Worked (79/79 months) but was a derivation. Superseded by the schedule view,
which is authoritative and also gives 100% coverage.

### Date-grain CIM-effective — REPLACED
`ERCOTCIMEFFECTIVEDATE` used to key on `DATE` (`EFFECTIVE_FROM`/`EFFECTIVE_THROUGH`
= `PRODUCTION_LOAD` day boundaries). Verified 2026-09-24 the SE actually
switches models at 23:00 on the eve of `PRODUCTION_LOAD`, not midnight —
retired devices' last sample is 22:57 that eve for 216/236 of them, new
devices' first sample is 23:57 that eve for 637/757 (00:xx for the rest).
Replaced with a `TIMESTAMP_NTZ` grain (`EFFECTIVE_FROM` = `PRODUCTION_LOAD`
minus one hour), so consumers join on `ts >= EFFECTIVE_FROM AND ts <
EFFECTIVE_TO` instead of a date `BETWEEN`.

### CIM-effective filtered on winding rows — REJECTED (sdalvi)
The view maps CIM IDs to the schedule, nothing more; winding coverage is a
loader concern surfaced by verification F/I, not a filter this view should
apply.

### Name-correcting table stores `TRANSFORMERNAME` — REJECTED
Storing the transformer name a device's bad `TRANSFORMERENDNAME` points at,
rather than the corrected winding name, seemed simpler but breaks under
renames: ERCOT renames windings between models — `PEARSALL 69_4` had both
windings named `138_69_4` (at 138 and 69) until model 204, when the 69 side
became `138_69_4_L`. A `TRANSFORMERNAME`-keyed correction can't express "the reported
name is right in old models, the correction is right in new ones." So the name-correcting table
stores the corrected WINDING name, and `ERCOTSETRANSFORMERWINDINGMAP` tries the
reported name first and the correction second (`WINDINGNAME IN (reported, corrected)`),
letting the kV match pick whichever is actually correct for that model.

### Mirror uniqueness guard moved from the procedure to the map — REPLACED
Under the earlier (2026-09-24) ignore-kV winding map, a device's `DEVICEKV`
could match NEITHER real winding of its transformer — ERCOT relabels reported
kV across CIM models (e.g. `BRIGHTSD_T1` @138 vs windings `T1`@69 / `T1_L`@34.5
in 47 models). A naive mirror join against that map would pass both winding
rows and double-count the flow, so the SP carried a runtime `mirror` CTE with
`HAVING COUNT(DISTINCT NOMINALKV) = 1` to suppress the ambiguous case.
That situation does not occur within a device's active window under the
current strict map — it was an artifact of pairing a device with a model from
before the device existed (or after a kV re-rating closed it; see §5's
versioned-device fact). With the strict join, the mirror is unique by
construction whenever a map row exists (build-script verification D, MUST
return 0), so the `mirror` CTE and its `HAVING` guard are gone from the
procedure entirely — the SP's `terminals` CTE joins `ERCOTSETRANSFORMERWINDINGMAP`
directly and filters `ABS(NOMINALKV - DEVICEKV) > 0.05`.

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
| CIM resolution 2022+ | **1,666 / 1,666 days**, exactly one model each (date-grain check; superseded by the TIMESTAMP-grain contiguity check, verification B) |
| SE model switchover | **23:00 on the eve of `PRODUCTION_LOAD`**, not midnight — retired devices' last sample 22:57 that eve (216/236 devices), new devices' first sample 23:57 that eve (637/757; 00:xx for the other 120) |
| Name-correcting table (`ERCOTSETRANSFORMERNAMECORRECTING`) | **133 rows** — one corrected winding name per device that fails the strict name+kV join in some model it overlaps; every device's correction unique across all its failing models (verification A) |
| Device table is versioned | A kV re-rating closes the old `BRANCHDEVICEID` and opens a new one, in step with the CIM model — `KVLEVEL` is correct for a device's own active window |
| `CIMFILEID` is not recency-ordered | `CIMFILEID` 376 is a 2023-07-18 model, loaded late — **never** pick "the newest model" via `MAX(CIMFILEID)` |
| `ISOERCOTSEBRANCHDEVICE` | 16,733 rows, `BRANCHDEVICEID` unique (no fanout risk) |
| View `ISOERCOTSEBRANCHVIEW` | Safe — 0 orphan rows, no row loss vs base tables |
| Station names | 4,418 / 4,418 branch stations exist in `ERCOTDAMPSSESTATION` — one namespace |
| **SE timestamps are irregular** | `:57` recently, `:58` in 2021–2022, occasionally on the hour (2022-01-01 has a `13:00:00` sample where every other hour is `:58`). Stored verbatim. Do not assume a fixed minute downstream. |
| Winding coverage gap | Models **377–392** (2026-07-29 onward) have no windings loaded as of 2026-09-24 — `ERCOTCIMEFFECTIVEDATE` still resolves them (it is not filtered on winding coverage), so those periods lose the transformer mirror until the loader catches up (verification I) |

### CIM model gotchas

- `CIMPATH LIKE '%MP_MarketModel%'` marks **test** models published ~45 days
  early, never in force. They also extend further forward than production
  models, so they would win a nearest-forward lookup outright.
- `CIMDATE` is **not unique** in `CIMFILE` even after excluding test models —
  models get re-posted. 2023-10-03 has CIMFILEID 15 and 18; 2025-12-09 has 141
  and 145 (`RTC_Native`). `ERCOTCIMEFFECTIVEDATE` does **not** break this tie —
  it's a pure mapping, so both CIMFILEIDs appear against the same schedule row
  (build-script verification H asserts exactly one of each pair carries
  windings, so downstream is unaffected).
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

`ERCOTSETRANSFORMERWINDINGMAP` scans ~504k winding rows against 16.7k devices on every
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
-- 1. Build the CIM-effective view (role AW_ACCESS) - section 1 of
--    build_ercot_transformer_winding_map.sql.

-- 2. Create the name-correcting table (section 2), then run its one-time seed (section 3).
--    Review ercotsetransformernamecorrecting_seed_review.csv first.

-- 3. Build the winding map view (section 4) - it depends on both the CIM
--    view and the (now-seeded) name-correcting table.

-- 4. Run verification A-G (section 5).
--    Expect: 0 for every "MUST return 0" check (A's second query, B's first
--    query, C, D, E). A's first query = 133. B's second query
--    (earliest EFFECTIVE_FROM) <= 2022-01-01. F is informational - expect
--    only the documented residual (FAYETT, GARZA, MDLNE, PCT). G is a spot
--    check against known values.

-- 5. Create the procedure (role AW_ACCESS)
--    Run sp_load_ercot_station_injection.sql

-- 6. Load one month and inspect before committing to the backfill
CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2022-01-31');

-- 7. Verify generation is visible at machine voltages.
--    NOTE: 2022-era timestamps are stamped :58, not :57.
SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2)
FROM AW.DBO.ERCOTSTATIONINJECTION
WHERE "TIMESTAMP" = '2022-01-03 12:58:00'
  AND NMMSSTATIONCODE IN ('STP','CPSES','HRZN_SLR','ACSSW')
ORDER BY NMMSSTATIONCODE, KVLEVEL;
-- STP should be ~+2600 at 25 kV and ~0 at 345 kV.
-- If these read ~0, the transformer mirror did not fire.

-- 8. Backfill month by month, 2022-01 onward.

-- 9. Ongoing: the Python ran a 3-day window lagging 60-63 days to let SE data
--    settle. Given the clustering, a weekly run over a wider window is cheaper.
--    Candidate for a scheduled `cortex automation`.
```

After a CIM publish, run verification **F** in the build script (the standing
"devices with flow but no map row" detection query) to catch a device that
newly fails the strict join. If it's one of the documented residual devices
(FAYETT, GARZA, MDLNE, PCT), ignore it. If it's a new device, extend
`ERCOTSETRANSFORMERNAMECORRECTING` by hand with the corrected winding name and re-run
verification A to confirm the correction is unique.

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
