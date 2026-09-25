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

Builds a terminal dimension ONCE per call (the four attribution rules below,
one row per device terminal) and joins it ONCE to `ISOERCOTSEBRANCH`, instead
of the earlier 4-leg `UNION ALL` that Snowflake inlined into four separate
scans of that table. Single pass, one transaction — the whole range runs as
one `DELETE` + `INSERT`. Returns a status string. The reported terminal is
read straight off `ISOERCOTSEBRANCHDEVICE`; the winding map only supplies the
mirror.

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
| Transformer, other real winding | the winding map's other real winding at that device (none if the device has no map row) | `TOMW` |

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

### Mirror = `TOMW` (not `-FROMMW`)
`TOMW` is populated on all transformer rows, carries losses.

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

### Single-pass terminal dimension (not 4-leg UNION over `br`)
Identical output, 1.5–2.8x faster (verified 1 day: 170,064 rows; 1 month:
5,098,241 rows; 0 mismatches at 0.001 MW). `ISOERCOTSEBRANCH` is clustered by
device, not timestamp, so scans are ~fixed per call regardless of window size
→ bulk loading means few large calls, not many small ones.

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

### Mirror falls back to the latest earlier winding-bearing model (2026-09-24)
Benchmark vs `ERCOTSTATIONLOAD` exposed 2023-03-28 23:00 → 2023-04-04 23:00
(`CIMFILEID` 393, no windings) with 376 stations off >10 MW; verification I in
the build script is exactly this condition.

### One snapshot per nearest-hour bucket (most complete, latest on ties); partial publishes skipped; range = bucket terms — 2026-09-24

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

### c) Transformer losses are attributed

The mirror uses `TOMW`, and `TOMW = -FROMMW + losses`, so summing across
`KVLEVEL` gives the station figure INCLUDING transformer losses. "Lines only"
below is the net of every line terminal at the station (what actually leaves
on the wires); the difference is the losses inside the station's transformers:

| Station | Sum over kV | Lines only | Diff (losses) |
|---|---|---|---|
| STP | 2604.11 | 2602.60 | +1.51 |
| CPSES | 2380.06 | 2376.28 | +3.79 |
| CBY | 1198.43 | 1195.76 | +2.68 |
| GUADG | 941.93 | 939.98 | +1.94 |

This matches the convention of the old `ERCOTSTATIONLOAD`, which summed
`FROMMW + TOMW` per transformer, so the two should agree at station level.

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
-- Backfill from here: single pass, one transaction, one call for the whole range, e.g.
-- CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2026-07-25');
-- After deploying the fallback proc, re-run CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2023-03-28', '2023-04-04');

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

## Fast-scan V2 (2026-09-24)

Files: `sp_fast_scan_v2.sql`, `sp_load_fast_scan_rt_constraints.sql`, `validate_fast_scan_v2.py`.

Design:
- SE-snapshot grain: output carries the raw :57 stamp, not hour-floored/aggregated.
- DAM/PAR keyed to nearest hour, so a 12:57 snapshot joins the DAM hour starting 13:00.
- RT rating = nearest CREATETIME, MIN across segments (tightest segment is the branch limit).
- RT constraint = config's own contingency only, nearest interval, base-case spelling normalised; every other contingency binding at the same intervals goes to FAST_SCAN_RT_CONSTRAINTS.
- Curtailment = nearest SCED run; shifts are per station-kV from CIM 205 ∪ data dictionary, nearest-kV snap within 1.0.

Validation, config 254330 (651_B / DMBDRKC5, 2026-06-01..06-14; PAR and renewable legs stubbed — PARERCOTVIEW and ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW are not readable by AI_READ_ONLY):
- 338 V2 rows vs 336 V1.
- DAM_RATE_B identical to V1 at the next hour (0.0000 diff, 338/338).
- REALTIME_RATE_B mean |diff| 0.23 (nearest :55 vs hourly average).
- INJECTION_FLOW differs by a near-constant 82–86 MW, entirely from CPSES: V1 averaged the station's four bus shifts (three at +0.00676, the 138kV bus at −0.126) to −0.0265 and applied it to ~2,400 MW → −63 MW; V2 applies +0.00676 to the 2,418 MW at 22kV → +17 MW. V1 was wrong; V2 is the reason the kV grain exists.
- RT_CONSTRAINT_VALUE NULL in V2 for 102 hours: only DMBDRKC5 (24 hours) is the config's own contingency; DBUCRGP5/SCMNCPS5/DKLNRGP5 etc. bound in the rest — by design, those are in the detail table.

Deploy order: (1) `ALTER TABLE FAST_SCAN_RESULTS ADD COLUMN RT_INTERVAL`; (2) `sp_load_fast_scan_rt_constraints.sql` (table + sub-proc); (3) `sp_fast_scan_v2.sql`; (4) `CALL SP_RUN_FAST_SCAN_TEST_V2(<config>, start, end)` on a config with a PSENSHIFTID (the 115 VALIDATION configs keyed by TOPOLOGYSHIFTSETID aren't served by V1 or V2).

### Validation fast-scan V2 (2026-09-25)

Files: `validation_spV2.sql` (`SP_RUN_VALIDATION_FAST_SCAN_TEST_V2`), `sp_run_validation_fast_scan_v1.sql` (reference copy of the deployed V1 validation proc, pasted since `GET_DDL` returns empty under `AI_READ_ONLY`), `validate_validation_fast_scan_v2.py`.

Design: V1's skeleton (config lookup + `NOT_A_VALIDATION_CONFIG` guard, `TMP_VAL_MEMBER_HOURS` RN dedup, date-range defaulting, `already_present`/`hours_missing`, RUN_LOG, RETURN, EXCEPTION), with V2's snapshot-grain CTEs (`ERCOTSTATIONINJECTION`, station+kV mapping, nearest-hour DAM/PAR join, +/-30min nearest RT rating/constraint, +/-30min curtailment) keyed additionally by `PSENSHIFTID` throughout (one shift per member hour, not one fixed shift). Config lookup now also reads `CTG_LABEL`. Calls `SP_LOAD_FAST_SCAN_RT_CONSTRAINTS` after the main insert, same as V2. Only change made during review: trimmed `sp_load_fast_scan_rt_constraints.sql`'s header comment (the "Snapshots come from..." paragraph) to 2 lines — no logic changes; the file's `Snapshots` CTE (reading the config's own `FAST_SCAN_RESULTS` rows rather than raw `ERCOTSTATIONINJECTION`) was already correct from the prior session.

Deploy order: (1) `ALTER TABLE FAST_SCAN_RESULTS ADD COLUMN RT_INTERVAL` (DONE by sdalvi 2026-09-25: `RT_INTERVAL TIMESTAMP_NTZ` present); (2) `sp_load_fast_scan_rt_constraints.sql` (DONE 2026-09-25: `FAST_SCAN_RT_CONSTRAINTS` exists, empty); (3) `sp_fast_scan_v2.sql`; (4) `validation_spV2.sql` (both created 2026-09-25; not visible to `AI_READ_ONLY`). Smoke test: V2 refuses any config that already has rows (`EXISTING_CONFIG_ID` guard), so it runs on a fresh clone of the config -- sdalvi created 256501 (clone of 254330) for this; the validation config is cloned the same way via sdalvi's validation-config proc. See `DEPLOY_FAST_SCAN_V2.md` for the full runbook (compile check, deploy steps, smoke tests, verification queries).

Floor-vs-nearest note: the deployed V1 validation proc reads `ERCOTSTATIONLOAD` (station grain) with `sl.HOUR = HOUR(mb.TS)` — a floor convention where a 12:57 SE snapshot lands on `ERCOTSTATIONLOAD.HOUR = 12`, and DAM is joined directly at that same `TIMESTAMP` (`HOUR-1 = 12` -> `HE = 13`). V2 keeps the raw `:57` snapshot stamp and buckets to the nearest hour (`HOUR_BUCKET = floor(snapshot + 30min)`), so the same 12:57 snapshot gets `HOUR_BUCKET = 13:00` and independently lands on `HE = 13` for DAM. The two conventions agree on which DAM/hour a snapshot belongs to, they just spell the join key differently — hence two comparison joins are needed: `V2.HOUR_BUCKET == V1.TIMESTAMP` (DAM/PSENSHIFTID; convention-invariant, should match exactly) and `floor(V2.TIMESTAMP) == V1.TIMESTAMP` (INJECTION_FLOW/REALTIME_RATE_B; genuinely different sources so a real diff is expected).

Dry run, config 256315 (branch 651_B, CTG DBUCRGP5), 2026-06-02..2026-06-08:
- Row counts: 156 member hours in range, 156 V1 rows already in `FAST_SCAN_RESULTS`, 157 V2 snapshot rows (SE snapshots aren't always exactly `:57`; one extra near a boundary).
- Same-bucket join (157 rows): `DAM_RATE_B` mean/max |diff| = 0.0000 (identical); `PSENSHIFTID` match rate 100% (157/157) — confirms the member-hour skeleton lines up exactly with V1's.
- Flow-alignment join (145 rows): `INJECTION_FLOW` mean |diff| 65.27, but that average hides two populations — 143/145 rows sit in a tight band (roughly 60-72 MW, V1 lower than V2, i.e. *near-constant* per the CPSES bug below) and a single outlier row: the 2026-06-02 23:52:00 snapshot (V2 flow -0.01). Verified cause: this is a model-rollout-night stub snapshot (a handful of retiring devices only) still present in `ERCOTSTATIONINJECTION` because the table was backfilled before the current one-snapshot-per-hour selection rule existed — the CPSES bus shifts for that hour's `PSENSHIFTID` (82296033) are identical to neighbouring hours (345kV +0.0035, 138kV -0.1035, 22kV +0.0035), so this is not a topology or CPSES-shift issue. It vanishes once the table is rebuilt with the current `SP_LOAD_ERCOT_STATION_INJECTION`; this is also why V2 has 157 rows for 156 member hours. Same root cause as the 254330 run for the near-constant population: V1 averages CPSES's bus shifts (three small-positive + one large-negative 138kV bus) into one wrong per-station number; V2 keeps kV levels separate. `REALTIME_RATE_B` mean |diff| 0.15, max 2.00 (nearest :55 tick vs V1's hourly average — expected).
- `RT_CONSTRAINT_VALUE` non-null: V1 = 41/156 (V1 averages every contingency together), V2 = 37/157 (V2 keeps only the config's own contingency, DBUCRGP5; the rest — SCMNCPS5, DCPSST58, DKLNRGP5 — moved to the detail table).
- Sub-proc (`SP_LOAD_FAST_SCAN_RT_CONSTRAINTS`, `Snapshots` inlined from the V2 dry run's own timestamps): 117 rows, 4 distinct contingencies (SCMNCPS5 40, DBUCRGP5 33, DCPSST58 22, DKLNRGP5 22). Of the 37 V2 snapshots with a non-null `RT_CONSTRAINT_VALUE`, 33/37 have exactly one `IS_CONFIG_CTG = TRUE` row in the sub-proc output with the matching value. The other 4 (06-08 22:57, 06-07 21:57/20:57/18:57) are an explicable edge case, not a bug: the sub-proc's old `NearestInterval` picked one SCED interval per snapshot across *all* contingencies binding on the branch, while `FAST_SCAN_RESULTS.RT_CONSTRAINT_VALUE` picks the nearest interval *for DBUCRGP5 specifically* — when a different contingency happens to bind strictly closer to the snapshot than DBUCRGP5 does (e.g. 22:55 vs DBUCRGP5's 23:20, both within the +/-30min window), the chosen single interval had no DBUCRGP5 row even though DBUCRGP5 was still binding a bit further out. Resolved: the sub-proc now picks the nearest binding interval per (snapshot, contingency) instead of one shared interval per snapshot, so the `IS_CONFIG_CTG = TRUE` row always equals the main proc's own `RT_CONSTRAINT_VALUE`/`RT_INTERVAL` and all 4 exceptions go away.
- Verified unverifiable-in-this-role legs (`PARERCOTVIEW`, `ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW`) were stubbed to empty/zero in the dry run only, same as `validate_fast_scan_v2.py`; the committed proc file is untouched (real `AW.DBO.PARERCOTVIEW`/`ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW` joins, unstubbed).

Output sample: `output/validation_fast_scan_v2_sample_256315.csv` (157 rows).

## PUN injection loader (2026-09-25)

Files: `ercot_pun_tie_map.sql` (`AWDEV.ERCOTRT.ERCOTPUNTIEMAP` DDL + 90 INSERT rows), `sp_load_ercot_pun_injection.sql` (`AWDEV.ERCOTRT.ERCOTPUNINJECTION` DDL + `SP_LOAD_ERCOT_PUN_INJECTION`), `validate_pun_injection.py`. Implements the Section 7 design in `pun_analysis/PUN_BACKOUT_FINDINGS.md` (56-PUN back-out, June 2026 spike).

Grain: `ERCOTPUNTIEMAP` is (PUNSTATION, NEIGHBORSTATION), 90 rows (78 PUN/neighbour pairs + 12 NOT_ESTIMABLE inventory rows with a NULL neighbour). `ERCOTPUNINJECTION` is (TIMESTAMP, PUNSTATION), one row per estimable PUN per hour (44 of 56 PUNs; NOT_ESTIMABLE PUNs produce no rows).

Deploy order: (1) `ercot_pun_tie_map.sql` (table + inserts); (2) `sp_load_ercot_pun_injection.sql` (table + proc); (3) `CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_PUN_INJECTION('2026-06-01','2026-06-30')` for one month; (4) the verification queries at the bottom of `sp_load_ercot_pun_injection.sql` (grain uniqueness, EXACT_SWITCHING NULL count, per-PUN mean vs `backout_pun_estimates.csv`).

Implementation decisions the design sketch got wrong or left underspecified:
- **NULL-vs-zero gating for gen/load.** Gate each neighbour's contribution through whether it has any mapped SCED unit (gen) / any `ERCOTDAMPSSELDVIEW` row anywhere in the call's date range (load) — absent entirely -> hard 0, never NULL (this is what keeps EXACT_SWITCHING clean); present but this specific tick/HE missing -> NULL, propagated via `IFF(COUNT_IF(...)>0, NULL, SUM(...))`.
- **Row-existence-with-INSERVICE-fallback for load VALUES (2026-09-25 grading-gate fix).** The first version required `INSERVICE=1` to even read a (STATIONNAME,DATE,HE) key, which misdiagnosed two real cases: CO on 2026-06-30 HE8-20 has all 48 rows present with `INSERVICE=0` but real, continuous `RAWMWLDF` (~8.8 MW) — a modelled bus transfer (`PSSEBUSNUMBER` 820->818 at HE21), not a missing row — and COHMA has all 720 June rows `INSERVICE=0` but a real ~0.37 MW. Both were silently read as missing (NULL) instead of counted. Fixed: per key, sum `INSERVICE=1` rows when any exist; if rows exist but none are in service, sum ALL rows for that key instead (`NEIGHBORLOADOUTOFSERVICECOUNT` counts how often this fires); NULL only when the key has zero rows at all (a genuine gap, e.g. LOLITA 2026-06-16 HE9-14, still absent). The station-level "is this a load station" flag was dropped and replaced by a presence-only check (any row, any INSERVICE) used solely to tell "never reports load this month" (0 — e.g. FM524/MTS/DPW/BOG/SRB-in-June, permanently zero rows) from "reports elsewhere this month but this exact key is empty" (NULL). Presence is keyed by (NEIGHBORSTATION, calendar MONTH) and computed over every whole calendar month the call touches, independent of `P_START_DATE`/`P_END_DATE`'s exact day boundaries — a call-range-scoped version re-introduced the granularity dependence the original `TMP_LOAD_STATIONS` had (a 1-day call could see a different presence verdict than a full-month call covering the same day); monthly granularity fixes it, since 2026-06-10 resolves to the same calendar month (June) either way. Proved in `validate_pun_injection.py` (`monthly_vs_daily_identical_check`): a `('2026-06-10','2026-06-10')` call and a `('2026-06-01','2026-06-30')` call produce byte-identical rows for 2026-06-10 (1,056 rows, 0 mismatches).
- **N_S itself had no NULL gate.** `TMP_GROUP_INJECTION` used to inner-join and `SUM()` the neighbours' `NETINJECTIONMW` directly, so a group neighbour with no `ERCOTSTATIONINJECTION` row at a snapshot silently vanished from the dominant term instead of nulling it (risk concentrated in multi-neighbour groups: LKVPD 5, NCARBIDE 6, PSA/LY 4). Fixed: build a full (snapshot x neighbour) grid first (`TMP_NEIGHBOR_GRID`), LEFT JOIN SI onto it, then `IFF(COUNT_IF(NET_INJ_MW IS NULL)>0, NULL, SUM(...))`; `NEIGHBORINJECTIONMISSINGCOUNT` tracks how often this fires (0 for every PUN in the June dry run).
- **Duplicate SE snapshots.** `ERCOTSTATIONINJECTION` is at-most-one-snapshot-per-hour-bucket *account-wide*, not guaranteed restricted to any 72-station subset at every historical range, so the neighbour temp table now re-applies `SP_LOAD_ERCOT_STATION_INJECTION`'s own dedup rule (most neighbour rows in the bucket wins, latest `SE_TS` on ties) before anything else touches it. June 2026 has 0 affected buckets for the 72 neighbours (verified by `validate_pun_injection.py`'s item-7(i) check), but the earlier claim of "zero hour buckets with more than one distinct source TIMESTAMP" was an overclaim — the account-wide guarantee doesn't imply a subset guarantee, and other months (the 2026-06-02 23:52-style stub snapshots) can differ.
- **EXACT_SWITCHING is now structural, not empirical.** DOW sits in the load leg (720 HEs, all `RAWMWLDF=0`), so one missing DOW HE could still NULL DOWGEN under the general gen/load logic. Fixed: for `METHODTAG='EXACT_SWITCHING'`, `PUNNETINJECTIONMW = NEIGHBORNETINJECTIONMW` directly, with `NEIGHBORSCEDGENMW`/`NEIGHBORDAMLOADMW` reported as a hard 0 — no dependency on the gen/load legs at all.
- **HOUR_BUCKET -> DAM (DATE, HE)** (lead ruling, 2026-09-25): DAM load is the hour *starting* at the nearest-hour bucket (`HE = HOUR(HOURBUCKET)+1`), matching `sp_fast_scan_v2.sql`'s own convention; the SE `:57` solve is the initial condition for that hour. The alternative (`HE = HOUR(bucket)`) differs by ~1 MW on PSA's P10. Join unchanged from the first version, which already matched this convention.

Crosswalk (deliverable 1, part (e)): all 72 distinct neighbour stations resolve under the same spelling in `ERCOTSTATIONINJECTION.NMMSSTATIONCODE` and `ERCOTDAMPSSESTATION.STATIONNAME` for June 2026 — 72/72, zero mismatches. `ISOMARKETID` was confirmed absent (via `DESCRIBE TABLE`) from all six tables the proc touches, so no filter is added anywhere.

Dry-run PASS/FAIL (`validate_pun_injection.py`, defaults, run 2026-09-25, post grading-gate fixes):
```
[PASS] (c) grain unique (TIMESTAMP,PUNSTATION)                         — 0 duplicate keys
[PASS] (d) EXACT_SWITCHING has zero NULLs                              — 0 NULL rows (structural)
[PASS] (item7-i) 1 distinct SE TIMESTAMP per HOURBUCKET after dedup    — 0 dup buckets before and after (June 2026)
[FAIL] (a) standalone PUN mean/P10/P90 within 1.0 MW                    — 1 of 32 PUNs exceed 1.0 MW (DOWGEN only)
[FAIL] (a) entangled group combined figures within 1.0 MW               — 1 of 6 groups exceed 1.0 MW (LY, P90 only)
[PASS] (b) BTE/AMOCOOIL/CCEC corr>=0.99 & |mean diff|<=6MW               — 0.994/-4.92MW, 0.9999/-0.55MW, 0.998/+2.08MW
[PASS] (e) all neighbours present in ERCOTSTATIONINJECTION              — 0 missing
```
- **PL** (was FAIL, D_MEAN -1.224; now PASS, D_MEAN +0.210, N=720): the 13 2026-06-30-afternoon hours that used to NULL are now real values including CO's ~8.8 MW out-of-service-but-real load (`NEIGHBORLOADOUTOFSERVICECOUNT`=13 for PL).
- **CARBN** (was PASS, D_MEAN -0.000; now PASS, D_MEAN +0.374, `NEIGHBORLOADOUTOFSERVICECOUNT`=720): COHMA's ~0.37 MW out-of-service load now counts every hour instead of reading 0; matches the predicted shift from the doc's -3.22 MW figure to about -2.85 MW.
- **FORMOSA**: unchanged, still N=714 (LOLITA 2026-06-16 HE9-14 genuinely absent, a different gap than CO/COHMA's).
- **DOWGEN** (D_MEAN -0.232, D_P90 -1.462) and **LY group** (D_MEAN +0.146, D_P90 +1.494): unchanged from the first dry run, both fully reproduced by a controlled recompute isolating one cause — `backout_master.sql`'s own `se_base` filter (unpadded `TIMESTAMP >= start AND < end`) samples a set of hour-buckets shifted one hour later than true calendar June (drops HE1 of June 1, includes HE1 of July 1), because a `:57` snapshot's raw `TIMESTAMP` falls inside that unpadded window while its `HOUR_BUCKET` describes the *next* hour. This proc's `-30min`-padded range (matching `sp_load_ercot_station_injection.sql`, the deliberately calendar-correct convention) samples the true calendar month instead; recomputing DOWGEN/LY with the padded convention reproduces this proc's actual output to 6 decimals. Confirmed by the grader as an accepted residual of the reference artifact's boundary handling, not a defect here.

Output sample: `output/pun_injection_sample_2026-06.csv` (31,680 rows, all 44 estimable PUNs x up to 720 hours).
