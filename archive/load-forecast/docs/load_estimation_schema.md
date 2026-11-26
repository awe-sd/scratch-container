# `ercotLoadEstimation_*` family — schema reference

Read-only Snowflake/SQL Server investigation, 2026-08-26. Answers: can this
family replace `AW.dbo.ercotStationLoad` as the source for net injection by
station/bus? All queries below were actually run (Snowflake `AI_READ_ONLY`
warehouse via `pfa.sf.query`, SQL Server `AWDev` via `awconnect.db.getDfFromAwDb`)
and are reproducible as written. Anything not directly queried is marked
**INFERRED**.

Bounded probe window used throughout: **2026-02-20** (single day, inside the
known-good week documented in `docs/pun_audit_top25.md`), station samples
JCK/GBY/SNDSW/HCKSW/WTRML (mixed generator/load/PUN characters) and the known
generator set JCK/LON_HILL/LCSES/GBY/DPW/HUD (per sdalvi rulings in
`docs/pun_audit_top25.md`).

---

## 0. Headline verdict (Question 1)

**Generation leg: PRESENT — but not in the one column every existing doc in
this repo cites.** Every prior reference (`large_load_research.md`,
`pun_audit_top25.md`, `organic_load.py`, `project_brief.md`, `tasks/09_*`)
only ever names `pun_total_est_load_mw`. Nobody had run a full `DESCRIBE
TABLE` before this investigation. The real column set is far richer:

| Quantity | `term_bal` columns (terminal grain) | `station_bal` columns (station grain) |
|---|---|---|
| Load (withdrawal) | `EXT_EST_LOAD_MW`, `TOTAL_EST_LOAD_MW`, `PUN_EXT_EST_LOAD_MW`, `PUN_TOTAL_EST_LOAD_MW` | `STATION_EST_LOAD_MW`, `RAW_STATION_EST_LOAD_MW` |
| **Generation (injection)** | `EXT_EST_GENERATION_MW`, `TOTAL_EST_GENERATION_MW`, `PUN_EXT_EST_GENERATION_MW`, `PUN_TOTAL_EST_GENERATION_MW` | `STATION_EST_GENERATION_MW`, `RAW_STATION_EST_GENERATION_MW` |
| **Net (signed injection)** | `EXT_NET_LOAD_MW`, `TOTAL_NET_LOAD_MW`, `PUN_EXT_NET_LOAD_MW`, `PUN_TOTAL_NET_LOAD_MW` | `STATION_NET_LOAD_MW`, `RAW_STATION_NET_LOAD_MW` |

Verified sign convention (§3): `NET = LOAD − GENERATION`. Positive = net
withdrawal (consumer), negative = net injection (producer) — the same
convention as `ercotStationLoad`'s `WithdrawMW` (never `abs()`'d for
generator station service). Mapping to `ercotStationLoad`:
`WithdrawMW ↔ *_EST_LOAD_MW`, `GenMW ↔ *_EST_GENERATION_MW`, true net
injection ↔ signed `*_NET_LOAD_MW` (negate if you want "injection positive").

**The trap that would have produced a silently-broken benchmark:**
`STATION_EST_LOAD_MW` / `STATION_EST_GENERATION_MW` / `STATION_NET_LOAD_MW`
(the *non*-`RAW_` columns) are **zeroed by the pipeline itself** for a subset
of station-hours — this is baked into the stored value, not a filter a caller
applies. Verified directly (§3.2): at `2026-02-20 00:57:00`, `SNDSW` reads
`STATION_EST_LOAD_MW = 0.0` on Snowflake while `term_bal` summed over kv for
the same station/instant gives `685.46 MW`, and `RAW_STATION_EST_LOAD_MW`
for that same row is `685.46 MW` — an exact match. Use the `RAW_` columns
(station grain) or `SUM(TOTAL_*)` over kv (term grain) — never the plain
`STATION_EST_*`/`STATION_NET_LOAD_MW` columns — for any comparison against
`ercotStationLoad`. This is a stronger, data-proven version of the caution
`tasks/09_injection_benchmark.md` §3.2 already gives for `pun_score`.

**Second-order caveat, also load-bearing:** the whole family appears to have
**stopped updating around early March 2026** on both platforms (§2.2) — as of
today (2026-08-26) it is *more* stale than `ercotStationLoad` (which itself
ends 2026-06-15), not fresher. This does not change the column-level verdict
above, but it matters enormously for whether "replace" is even the right verb
— see §2.2 and the Recommendations section.

---

## 1. Which copy exists where (Question 2)

```sql
SHOW TABLES LIKE 'ERCOTLOADEST%' IN AW.DBO        -- Snowflake
SHOW TABLES LIKE 'ERCOTLOADEST%' IN AWDEV.DBO      -- Snowflake
SHOW DATABASES LIKE 'AWDEV%'                       -- Snowflake
SHOW SCHEMAS IN DATABASE AWDEV                     -- Snowflake
SHOW TABLES LIKE 'ERCOTLOAD%' IN AWDEV.SE          -- Snowflake ("SE" schema, created 2026-08-25, comment "State Estimator" -- checked in case it held a newer copy)
SHOW TABLES LIKE 'ERCOTLOAD%' IN AWDEV.ERCOTRT     -- Snowflake
-- SQL Server (database "AWDev"):
SELECT TABLE_NAME, TABLE_SCHEMA FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME LIKE 'ercotLoadEst%'
SELECT t.name, t.modify_date, SUM(p.rows) FROM sys.tables t JOIN sys.partitions p ON p.object_id=t.object_id AND p.index_id IN (0,1) WHERE t.name LIKE 'ercotLoadEst%' GROUP BY t.name, t.modify_date
```

**Snowflake `AW.DBO`** (6 tables, all confirmed present, `created_on`
2026-04-28/29):

| Table | Rows (SHOW TABLES metadata) |
|---|---|
| `ERCOTLOADESTIMATION_TERM_BAL` | 325,528,991 |
| `ERCOTLOADESTIMATION_STATION_BAL` | 283,436,771 |
| `ERCOTLOADESTIMATION_AUDIT` | 496,192,744 |
| `ERCOTLOADESTIMATION_RUN_AUDIT` | 54,047 |
| `ERCOTLOADESTIMATION_BAD_INTERVALS` | 618 |
| `ERCOTLOADESTIMATION_BRANCH_MAPPING` | **0** |

**Snowflake `AWDEV`** (the database exists, created 2026-03-16, with 8
schemas: `BASELINE`, `DBO`, `ERCOTRT`, `FLOW_ANALYSIS`, `INFORMATION_SCHEMA`,
`PRECOG`, `PUBLIC`, `SE`) — **zero `ERCOTLOADEST*`/`ERCOTLOAD*` tables in any
schema checked** (`DBO`, `SE`, `ERCOTRT` — the other four are other-project
schemas by name/ownership, not investigated further, per the escalation rule
against extended hunts). This confirms the family does **not** exist on
Snowflake under the `AWDEV` database at all — it lives only under `AW`.
`BASELINE`/`PRECOG` are unrelated repos per user memory; not investigated.

**SQL Server `AWDev`** (5 tables — **no `BAD_INTERVALS`**, Snowflake-only):

| Table | Approx. rows (`sys.partitions`, no scan) | `modify_date` |
|---|---|---|
| `ercotLoadEstimation_term_bal` | 273,550,142 | 2026-03-10 11:48:28 |
| `ercotLoadEstimation_station_bal` | 237,593,855 | 2026-03-10 11:42:47 |
| `ercotLoadEstimation_audit` | 417,657,003 | 2026-03-10 11:49:28 |
| `ercotLoadEstimation_run_audit` | 44,986 | 2026-02-27 19:40:50 |
| `ercotLoadEstimation_branch_mapping` | **7,544** | 2026-03-04 03:07:56 |

**Verdict: mirrored, not moved, and not a clean 1:1 mirror.** Both platforms
carry `term_bal`/`station_bal`/`audit`/`run_audit`. `branch_mapping` is the
one exception: **populated only on SQL Server (7,544 rows), empty on
Snowflake (0 rows)** — a replication gap, not evidence the bridge doesn't
exist (the pre-existing `project_brief.md` note reads the 0-row Snowflake
copy as "no bus-level bridge"; that's the wrong database — see §4).
`ercotLoadEstimation_bad_intervals` is Snowflake-only (no SQL Server
equivalent found).

### 1.1 Column-level schema comparison

Every column in `term_bal`/`station_bal` matches 1:1 between platforms
(verified via Snowflake `DESCRIBE TABLE` vs SQL Server
`INFORMATION_SCHEMA.COLUMNS`), **with exactly one difference: Snowflake's
copy has no `RUN_ID` column at all.** SQL Server's `term_bal`/`station_bal`/
`run_audit` all carry `run_id` (ordinal position 2, `nvarchar`); every
existing query in this repo filters `run_id='1'`. Snowflake simply omits the
column — see §3.3 for what this means in practice (it is *not* a clean
single-run-per-timestamp guarantee).

`branch_mapping` never had `run_id` on either platform (it's a static
reference table, not a timeseries).

---

## 2. Full column lists (every family member, `DESCRIBE TABLE AW.DBO.<table>`)

### `ERCOTLOADESTIMATION_TERM_BAL` (grain: see §3.1 — `se_timestamp, station, kv`; 28 cols on Snowflake, 27 incl. `run_id` on SQL Server)

`ID, SE_TIMESTAMP, DAM_DATE, DAM_HE, DAM_SNAPSHOT_TS, PROCESSED_AT_UTC,
TERMINAL, STATION, KV, EXT_IMPORT_MW, EXT_EXPORT_MW, EXT_NET_LOAD_MW,
EXT_EST_LOAD_MW, EXT_EST_GENERATION_MW, INT_IMPORT_MW, INT_EXPORT_MW,
TOTAL_IMPORT_MW, TOTAL_EXPORT_MW, TOTAL_NET_LOAD_MW, TOTAL_EST_LOAD_MW,
TOTAL_EST_GENERATION_MW, PUN_EXT_NET_LOAD_MW, PUN_EXT_EST_LOAD_MW,
PUN_EXT_EST_GENERATION_MW, PUN_TOTAL_NET_LOAD_MW, PUN_TOTAL_EST_LOAD_MW,
PUN_TOTAL_EST_GENERATION_MW`

(+ `RUN_ID` on SQL Server only, ordinal 2.)

`EXT_*` = flows across the station's external tie boundary; `INT_*` = internal
(within-station, e.g. between buses/xfmrs at the station) — but `INT_*` only
exists as an actual column for `IMPORT_MW`/`EXPORT_MW`; there is no
`INT_EST_LOAD_MW` or `INT_EST_GENERATION_MW` column in this table (see the
column list above), so the claim below only type-checks for `IMPORT`/`EXPORT`.

**CORRECTED 2026-08-26** (was: `TOTAL_* = EXT_* + INT_*`, marked INFERRED and
never verified — empirically contradicted for the LOAD/GENERATION columns;
see `jck_lonhill_generation.md` §3.3 and `genmw_coverage.md` Q4 for the
evidence). What actually holds, verified directly (row/kv grain, 6 stations
JCK/GBY/HCKSW/SNDSW/WTRML/DPW, 2026-02-19→26):
- `TOTAL_IMPORT_MW = EXT_IMPORT_MW + INT_IMPORT_MW` and
  `TOTAL_EXPORT_MW = EXT_EXPORT_MW + INT_EXPORT_MW` hold **exactly** (max
  `|residual|` = 0.00 MW, all 6 stations) — so the original naming-based
  inference is correct, but only for `IMPORT_MW`/`EXPORT_MW`, the one column
  family where `INT_*` actually exists.
- For `LOAD_MW`/`GENERATION_MW` (no `INT_*` variant exists), what holds
  instead, kv-summed per timestamp: `EXT_EST_LOAD_MW = TOTAL_EST_LOAD_MW +
  EXT_EST_GENERATION_MW`. This is **exact** (residual ≈0.00 MW) for
  non-generating/small-net stations (JCK, SNDSW, HCKSW) but **breaks down**
  for stations with material external generation (DPW, WTRML, GBY: average
  residual 100-250 MW, max residual up to ~475 MW) — treat as a property of
  load-only stations, not a general pipeline identity.
- Separately, `TOTAL_IMPORT_MW - EXT_IMPORT_MW = PUN_TOTAL_EST_LOAD_MW` and
  `TOTAL_EXPORT_MW - EXT_EXPORT_MW = PUN_TOTAL_EST_GENERATION_MW` hold almost
  exactly for 5 of the 6 stations tested, with a small unexplained residual
  (~35 MW avg / ~150 MW max) at GBY specifically — not resolved further.

### `ERCOTLOADESTIMATION_STATION_BAL` (grain: `se_timestamp, station`; 41 cols Snowflake, 42 incl. `run_id` SQL Server)

`ID, SE_TIMESTAMP, DAM_DATE, DAM_HE, DAM_SNAPSHOT_TS, PROCESSED_AT_UTC,
STATION, EXT_IMPORT_MW, EXT_EXPORT_MW, STATION_NET_LOAD_MW,
STATION_EST_LOAD_MW, STATION_EST_GENERATION_MW, UNRESOLVED_XFMR_COUNT,
UNRESOLVED_ABS_MW, COVERAGE_FLAG, EXPECTED_TIE_EDGES, OBSERVED_TIE_EDGES,
MISSING_TIE_EDGES, PUN_SCORE, REDACTED_BUCKET_MW, REDACTED_BUCKET_NOTE,
HAS_GENERATOR, HAS_LOAD, RAW_STATION_NET_LOAD_MW, RAW_STATION_EST_LOAD_MW,
RAW_STATION_EST_GENERATION_MW, PUN_COMPONENT_ID, PUN_COMPONENT_STATIONS,
PUN_COMPONENT_NET_LOAD_MW, PUN_COMPONENT_REPRESENTATIVE,
PUN_COMPONENT_AMBIGUOUS, PUN_PASSTHROUGH_MW, PUN_PASSTHROUGH_TO,
PUN_EXPORT_WITHOUT_GEN_MW, PUN_MISSING_EDGE_COUNT, PUN_EXPECTED_TIE_EDGES,
PUN_OBSERVED_TIE_EDGES, PUN_MISSING_EDGE_FRAC,
PUN_COMPONENT_MISSING_EDGE_COUNT, HAS_ERCOT_LOAD, HAS_NON_ERCOT_LOAD`

(+ `RUN_ID` on SQL Server only, ordinal 2.) Notably richer than any prior doc
recorded: PUN handling is modeled as **connected components** across
physically-tied stations (`PUN_COMPONENT_*`), with explicit
`PUN_EXPORT_WITHOUT_GEN_MW` (anomaly flag) and `REDACTED_BUCKET_MW`/`_NOTE`
(explicit redaction tracking — this appears to be the mechanism behind the
"PUN redactions... manual fill-in table" note in
`docs/large_load_research.md`, though that connection is **INFERRED**, not
directly tested here). `COVERAGE_FLAG` observed values (bounded-day sample,
§6): `HIGH` (97.6% of rows), `NULL` (2.2%), `LOW` (0.2%), `MEDIUM` (0.04%) —
exact semantics of the four levels not documented anywhere found; **INFERRED**
that they describe topology-resolution confidence, consistent with
`EXPECTED_TIE_EDGES`/`OBSERVED_TIE_EDGES`/`MISSING_TIE_EDGES` living on the
same row.

### `ERCOTLOADESTIMATION_BRANCH_MAPPING` (20 cols both platforms; no `run_id` — static reference table)

`ID, BRANCHDEVICENAME, FROMSTATIONNAME, BRANCHDEVICETYPE, BRANCH_TYPE,
KVLEVEL, TOSTATIONNAME, FROMNAME, TONAME, FROM_TERMINAL, TO_TERMINAL,
IS_EXCLUDED, SE_TIMESTAMP, DAM_DATE, DAM_HE, MATCH_METHOD, CREATED_BY,
CREATED_AT_UTC, UPDATED_AT_UTC, NOTES`

### `ERCOTLOADESTIMATION_AUDIT` (23 cols; per-branch flow detail, one row per branch endpoint per timestamp — grain not independently re-derived beyond what §5 sampling shows)

`ID, SE_TIMESTAMP, DAM_DATE, DAM_HE, DAM_SNAPSHOT_TS, PROCESSED_AT_UTC,
BRANCHID, BRANCHDEVICENAME, BRANCHDEVICETYPE, KVLEVEL, FROMSTATIONNAME,
TOSTATIONNAME, FROMNAME, TONAME, FROMMW, TOMW, STATUS, REASON, FLOW_KIND,
FROM_TERMINAL, TO_TERMINAL, XFMR_GROUP_KEY, MATCH_METHOD`

### `ERCOTLOADESTIMATION_RUN_AUDIT` (14 cols; one row per SE-timestamp processing run)

`ID, SE_TIMESTAMP, DAM_DATE, DAM_HE, DAM_SNAPSHOT_TS, STATUS, ERROR_TEXT,
START_UTC, END_UTC, DURATION_MS, STATION_ROW_COUNT, TERM_ROW_COUNT,
AUDIT_ROW_COUNT, PROCESSED_AT_UTC`

### `ERCOTLOADESTIMATION_BAD_INTERVALS` (4 cols; Snowflake only, 618 rows total)

`ID, INTERVAL, NUM_ENTRIES, QUERY_DATETIME`

**No column anywhere in the family is named `BUSNUM`, `SswgBusNumber`,
`MRIDLOAD`, or any numeric bus identifier** — see §4.

---

## 3. Grain, resolution, and the generation-leg/reconciliation evidence (Questions 1 & 3)

### 3.1 Grain — confirmed by direct duplicate check, one exact instant

```sql
SELECT COUNT(*) n_rows,
       COUNT(DISTINCT STATION || '|' || TO_VARCHAR(KV)) n_distinct_station_kv,
       COUNT(DISTINCT TERMINAL) n_distinct_terminal,
       COUNT(DISTINCT STATION || '|' || TO_VARCHAR(KV) || '|' || TERMINAL) n_distinct_full_key
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP = '2026-02-20 00:57:00'
-- result: n_rows = n_distinct_station_kv = n_distinct_terminal = n_distinct_full_key = 6,676
```

**`(se_timestamp, station, kv)` is a unique key on Snowflake** (no run_id to
additionally partition by). **`TERMINAL` is *not* a finer grain than
`station+kv`** — contrary to what its presence suggests, sampled values are
literally the string `('GBY', 138.0)` etc. — i.e. `TERMINAL` is a serialized
label *of* `(station, kv)`, not an independent identifier (verified: every
`(station, kv)` combination sampled had exactly 1 row and 1 distinct
`TERMINAL` value). The "SUM over kv per station before joining `station_bal`"
folklore in `docs/pun_audit_top25.md` is therefore correct as stated — kv is
the only real fan-out dimension, terminal adds nothing beyond it.

`station_bal` grain is `(se_timestamp, station)` — one row per station per
timestamp; not independently duplicate-checked beyond the population query
in §3.2 returning exactly one row per station per instant in all samples.

### 3.2 Population, sign convention, and the reconciliation test

Population, bounded day (`SE_TIMESTAMP >= '2026-02-20' AND < '2026-02-21'`), all stations, `term_bal` (160,224 rows):

```sql
SELECT COUNT(*) n_rows,
       COUNT(TOTAL_EST_LOAD_MW) n_nn_load, COUNT_IF(TOTAL_EST_LOAD_MW <> 0) n_nz_load,
       COUNT(TOTAL_EST_GENERATION_MW) n_nn_gen, COUNT_IF(TOTAL_EST_GENERATION_MW <> 0) n_nz_gen,
       COUNT(TOTAL_NET_LOAD_MW) n_nn_net, COUNT_IF(TOTAL_NET_LOAD_MW <> 0) n_nz_net,
       MIN(TOTAL_EST_LOAD_MW) min_load, MAX(TOTAL_EST_LOAD_MW) max_load,
       MIN(TOTAL_EST_GENERATION_MW) min_gen, MAX(TOTAL_EST_GENERATION_MW) max_gen,
       MIN(TOTAL_NET_LOAD_MW) min_net, MAX(TOTAL_NET_LOAD_MW) max_net,
       MIN(PUN_TOTAL_EST_LOAD_MW) min_punload, MAX(PUN_TOTAL_EST_LOAD_MW) max_punload
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP >= '2026-02-20 00:00:00' AND SE_TIMESTAMP < '2026-02-21 00:00:00'
```

Result: `n_rows=160224`; load 100% non-null, 85% non-zero (`min=0, max=898.0`);
**generation 100% non-null, 11.4% non-zero** (`min=0, max=2678.9`) — non-null
everywhere, genuinely populated (not all-zero) at the terminals that carry
generation; net 100% non-null, 96% non-zero (`min=-2678.9, max=898.0`).
**`min(TOTAL_EST_GENERATION_MW) = 0.0` and `min(PUN_TOTAL_EST_LOAD_MW) = 0.0`
— load and generation never go negative; only the `NET` columns carry sign.**
`min(net) ≈ -max(gen)` at the extreme (a near-pure generator terminal, load≈0)
— confirms **`NET = LOAD − GENERATION`**.

Restricted to the known sdalvi-ruled generator stations (`term_bal`, same day):

| Station | rows | nonzero-gen rows | max gen (MW) | avg gen (MW) |
|---|---|---|---|---|
| DPW | 72 | 48 (67%) | 272.0 | 142.8 |
| GBY | 96 | 24 (25%) | 124.9 | 28.5 |
| HUD | 48 | 36 (75%) | 136.7 | 44.4 |
| LCSES | 72 | 16 (22%) | 321.3 | 34.6 |
| JCK | 48 | **0 (0%)** | 0.0 | 0.0 |
| LON_HILL | 72 | **0 (0%)** | 0.0 | 0.0 |

**JCK and LON_HILL show zero generation in this family across the entire
day**, despite being ruled generator stations from `ercotStationLoad`
evidence (`pun_audit_top25.md`). This is a genuine cross-source
disagreement, not a query artifact — flagged as a finding, not smoothed
over: the two sources are independent measurements and don't have to agree;
whether this SE-based family is simply blind to JCK/LON_HILL's generation
(a blind spot analogous to `ercotStationLoad`'s documented blindness to
HCKSW/WTRML) is **not resolved here** and would need its own investigation.

**The reconciliation test — this is where the "clean" `STATION_BAL` columns
turned out to be a trap:**

```sql
-- term_bal, summed over kv, at one instant, for 5 test stations:
SELECT STATION, SUM(TOTAL_EST_LOAD_MW) sum_total_load, SUM(TOTAL_EST_GENERATION_MW) sum_total_gen,
       SUM(TOTAL_NET_LOAD_MW) sum_total_net, COUNT(*) n_rows
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP = '2026-02-20 00:57:00' AND STATION IN ('JCK','GBY','SNDSW','HCKSW','WTRML')
GROUP BY STATION
-- station_bal, same instant/stations, both the plain and RAW_ columns:
SELECT STATION, STATION_EST_LOAD_MW, RAW_STATION_EST_LOAD_MW,
       STATION_EST_GENERATION_MW, RAW_STATION_EST_GENERATION_MW,
       STATION_NET_LOAD_MW, RAW_STATION_NET_LOAD_MW, PUN_SCORE, COVERAGE_FLAG
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE SE_TIMESTAMP = '2026-02-20 00:57:00' AND STATION IN ('JCK','GBY','SNDSW','HCKSW','WTRML')
```

| Station | `term_bal` Σload | `term_bal` Σnet | `station_bal.STATION_EST_LOAD_MW` | `station_bal.RAW_STATION_EST_LOAD_MW` | `station_bal.RAW_STATION_NET_LOAD_MW` | pun_score |
|---|---|---|---|---|---|---|
| GBY | 0.90 | -116.19 | **0.0** | 0.0 | **-116.19** ✓ | 0.083 |
| HCKSW | 1.76 | 1.76 | **0.0** | 1.76 ✓ | 1.76 ✓ | 0.083 |
| JCK | 25.15 | 25.15 | **0.0** | 25.15 ✓ | 25.15 ✓ | 0.182 |
| SNDSW | 685.46 | 685.46 | **0.0** | 685.46 ✓ | 685.46 ✓ | 0.154 |
| WTRML | 80.01 | 0.33 | **0.0** | 0.0 | **0.33** ✓ | 0.167 |

`RAW_STATION_NET_LOAD_MW` reconciles **exactly** to `term_bal`'s
`SUM(TOTAL_NET_LOAD_MW)` in all 5 cases. `RAW_STATION_EST_LOAD_MW` reconciles
exactly for the 3 "pure load" stations but reads `0.0` for GBY and WTRML
(both mixed generator+load stations) even though their `term_bal` load
component is genuinely nonzero (0.90 and 80.01 MW respectively) — i.e. the
station-level load/generation *split* can lose a small load component at
mixed stations, but the **net** figure is always right. **Recommendation:
use `RAW_STATION_NET_LOAD_MW` (station grain) or `SUM(TOTAL_NET_LOAD_MW)`
over kv (term grain) as the net-injection quantity; if load and generation
need to be separated, compute them from `term_bal`'s per-kv rows, not from
`station_bal`'s load/generation split.**

Every one of `GBY`/`HCKSW`/`JCK`/`SNDSW`/`WTRML` had `PUN_SCORE > 0` at this
instant, yet **`STATION_EST_LOAD_MW = 0.0` for all five** — confirming the
"clean" columns are zeroed whenever `pun_score` is nonzero, not just for the
famously-flagged stations. Checked and ruled out as a bad-interval artifact:

```sql
SELECT INTERVAL, NUM_ENTRIES, QUERY_DATETIME FROM AW.DBO.ERCOTLOADESTIMATION_BAD_INTERVALS
WHERE INTERVAL IN ('2026-02-20 00:57:00','2026-02-20 01:57:00')  -- 0 rows returned; not a flagged bad interval
```

System-wide at the same instant: `SUM(STATION_EST_LOAD_MW) = 45,713 MW` vs
`SUM(RAW_STATION_EST_LOAD_MW) = 46,771 MW` (clean is ~2.3% lower than raw at
this hour — order-of-magnitude consistent with the "9.5–12% of system load"
PUN exclusion figure in `docs/large_load_research.md`, though that figure was
for a different metric/window and this is not a direct confirmation).

**Cross-platform note (important, not just a footnote):** re-running the
identical reconciliation query against **SQL Server** at the same instant
(`run_id='1'`) reproduces the `term_bal` numbers almost exactly (SNDSW
685.62 MW vs Snowflake's 685.46 MW — 0.02% apart, consistent with two
independently-computed near-duplicate loads of the same underlying SE input,
not a bug) — **but the "clean"-column zeroing behavior differs by
platform.** On SQL Server, `SNDSW` and `WTRML`'s plain `station_est_load_mw`
were **not** zeroed (they equal the raw values) despite `pun_score > 0` on
both platforms; `GBY`/`HCKSW`/`JCK` were zeroed on both. The `pun_score`
values themselves differ between platforms for `SNDSW` (0.154 Snowflake vs
0.077 SQL Server) and `WTRML` (0.167 vs 0.091) while matching exactly for the
other three stations. **The exact zeroing rule could not be determined from
data alone** (it is not simply "`pun_score>0` zeros the row" — SQL Server's
nonzero-`pun_score` SNDSW/WTRML were not zeroed) and appears to depend on
pipeline internals (possibly the `PUN_COMPONENT_*` classification) not
visible from the table alone. **Practical takeaway: treat the Snowflake and
SQL Server copies as independently-computed near-duplicates, not guaranteed-
identical mirrors — pick one platform as ground truth per analysis and don't
mix rows across them.**

### 3.3 The missing `run_id` on Snowflake — sharper test

```sql
-- Snowflake, term_bal, exact instant: 6,676 rows (§3.1)
-- SQL Server, term_bal, same instant, grouped by run_id:
SELECT run_id, COUNT(*) n_rows FROM dbo.ercotLoadEstimation_term_bal WHERE se_timestamp = '2026-02-20 00:57:00' GROUP BY run_id
-- result: run_id='1', n_rows=6,729
```

**6,676 (Snowflake) vs 6,729 (SQL Server `run_id='1'`) — close but not
equal** (99.2% match, 53-row gap). Also confirmed only one `run_id` value
(`'1'`) exists in the `2026-01-01`–`2026-03-23` window on SQL Server (no
hidden newer run under a different id). Conclusion: Snowflake's missing
`run_id` is **not proof of a clean single-run collapse** — the row-count
mismatch shows Snowflake's copy isn't a byte-identical extract of SQL
Server's `run_id='1'` rows either; it's a separately-loaded near-duplicate
(consistent with §3.2's platform-divergence finding).

### 3.4 Resolution

```sql
SELECT DISTINCT SE_TIMESTAMP FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE SE_TIMESTAMP >= '2026-02-20 00:00:00' AND SE_TIMESTAMP < '2026-02-20 03:00:00' ORDER BY SE_TIMESTAMP
-- result: 2026-02-20 00:57:00, 01:57:00, 02:57:00
```

**Hourly**, snapshotted at `:57` past each hour (3 minutes before the top of
the hour) — not 5-minute or 15-minute.

---

## 4. History depth (Question 4) and freshness (Question 2, cont'd)

```sql
-- Snowflake, no predicate (metadata-served):
SELECT MIN(SE_TIMESTAMP), MAX(SE_TIMESTAMP), MAX(PROCESSED_AT_UTC) FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
SELECT MIN(SE_TIMESTAMP), MAX(SE_TIMESTAMP), MAX(PROCESSED_AT_UTC) FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
-- SQL Server, index-seek instead of MAX():
SELECT TOP 1 se_timestamp, processed_at_utc FROM dbo.ercotLoadEstimation_term_bal WHERE run_id='1' ORDER BY se_timestamp DESC
SELECT TOP 1 se_timestamp FROM dbo.ercotLoadEstimation_term_bal WHERE run_id='1' ORDER BY se_timestamp ASC
```

| | Snowflake `AW.DBO.TERM_BAL`/`STATION_BAL` | SQL Server `AWDev.dbo.term_bal` (`run_id='1'`) |
|---|---|---|
| Min `se_timestamp` | **2020-01-01 00:58** | 2021-01-01 00:58 |
| Max `se_timestamp` | **2026-03-04 23:57** | 2026-02-26 23:57 |
| `processed_at_utc` of latest row | corrupt sentinel value (`56342130-01-09...` — clearly a data-quality bug, not a real date; ignored) | 2026-04-28 10:56:59 |

**Snowflake's `MAX(PROCESSED_AT_UTC)` is unusable for freshness** — it
returns a corrupt sentinel (year `56342130`, not a real timestamp; likely an
overflow or placeholder value baked into some row during the load). That is
why the freshness argument below leans on `ERCOTLOADESTIMATION_RUN_AUDIT`
(a separate table, itself Snowflake-hosted but not affected) and on SQL
Server's `processed_at_utc`, not on this column directly — noted explicitly
so the substitution is auditable rather than looking like cherry-picked
timestamps.

**Report only, per instructions — not judging sufficiency:** Snowflake's
window is wider on both ends (extra year of back-history, 6 more days at the
end) than SQL Server's. **Both stop in early March 2026 — as of today
(2026-08-26), neither copy has been updated in roughly six months.**

**This looks like a one-time historical backfill, not a live pipeline.**
`RUN_AUDIT`'s own latest 20 rows (ordered by `se_timestamp DESC`, no
predicate — whole table is only 54,047 rows) all show `se_timestamp =
2026-03-04 *:57:00` with `STATUS='SUCCESS'` and `START_UTC`/`END_UTC` on
**2026-05-04** — i.e., the row describing `se_timestamp=2026-03-04` was
itself *computed* two months later, on 2026-05-04. Combined with the Snowflake
table `created_on` dates (2026-04-28/29) and the SQL Server latest row's
`processed_at_utc` (2026-04-28 10:56:59, matching almost to the hour), the
evidence points to a **single backfill campaign that ran ~2026-04-28 through
2026-05-04**, populated both platforms with SE history from 2020/2021 through
2026-03-04, and has **no evidence of any run since**. Not independently
confirmed there is no *newer*, differently-named run somewhere else — this
is the strongest read of the evidence gathered, not a certainty.

`ERCOTLOADESTIMATION_BAD_INTERVALS` (Snowflake only, 618 rows total) spans
`2020-01-07` to `2026-03-03` — consistent with the same backfill window, and
too sparse (618 flagged intervals across ~6 years of hourly data, i.e. a
tiny fraction of the ~53,000 hourly SE snapshots implied by the window) to
say anything about overall continuity beyond "not obviously riddled with
gaps" — a proper gap census was **not run** (would require an unbounded
scan against the discipline rules in scope here) and is not claimed.

---

## 5. Bus-level bridge (Question 5)

**No column anywhere in the family carries a bus number.** Checked every
`DESCRIBE TABLE` in §2 for `BUSNUM`/`SswgBusNumber`/`MRIDLOAD`/any numeric
bus id — none exist. The finest identifier available throughout the family
is `STATION` + `KV` (`TERMINAL` is the same thing serialized as text, §3.1).

`ERCOTLOADESTIMATION_BRANCH_MAPPING` — the one table whose name suggested a
bridge — is **populated only on SQL Server (7,544 rows; 0 on Snowflake, a
replication gap, not evidence against the bridge's existence — corrects the
pre-existing `project_brief.md` note, which read the Snowflake 0-row count
as "still empty — no bus-level bridge" without checking SQL Server)**.
Sampled content:

```sql
SELECT TOP 20 branchDeviceName, fromStationName, toStationName, branch_type,
       kvLevel, from_terminal, to_terminal, is_excluded, match_method, notes
FROM dbo.ercotLoadEstimation_branch_mapping ORDER BY id
-- SELECT match_method, is_excluded, COUNT(*) FROM ... GROUP BY match_method, is_excluded
-- -> single group: match_method='AUTO_MATCHED', is_excluded=False, n=7544 (ALL rows)
```

It maps ERCOT branch/circuit device names (e.g. `6630_C`, `100_A`) to their
from/to **station** names and `(station, kv)` terminal pairs — a
branch-to-station reconciliation table for the pipeline's own internal use,
100% `AUTO_MATCHED` in the full sample (no manual corrections observed,
`notes` null throughout). **It is a branch↔station/terminal map, not a
bus-number bridge** — it does not get you to `SswgBusNumber` or any bus
granularity finer than station+kv.

`AUDIT`'s `BRANCHID` column (sample values like `60103483.0`, `60005003.0`)
is a numeric-looking branch identifier that **might** correspond to the
branch-numbering scheme `powerflow_analytics` uses (`FROMNUM`/`TONUM`,
`BRANCHID` join to `OUTGENREF`/`GENUNIT` per that project's `CLAUDE.md`) —
**not tested here** (would require pulling `powerflow_analytics`' branch
tables and joining, out of this task's scope) and **not the same numbering
system as `SswgBusNumber`**, which is what this codebase's existing
station→county→zone crosswalk actually keys on.

**Verdict: bus-level (`SswgBusNumber`) is not reachable from within this
family on either platform.** Getting from station/kv to bus still requires
the same external crosswalk this codebase already uses for
`ercotStationLoad` (`BusID(SSWG) → ercotDataDictionary.SswgBusNumber →
PlanningBusCounty`) — this family does not shortcut that step, it only gets
you cleanly to station (and, if you need it, kv-level) grain.

---

## 6. Station namespace (Question 6)

```sql
SELECT DISTINCT STATION FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE STATION IN ('JCK','RNKSW','SNDSW','DOW','LON_HILL','GBY','STEWART','HCKSW','BOG','GILLCR',
                   'AZ','FIRON','WTRML','SDMSW','STILES','OYS','DPW','ATKINS','HUD','CANAL_RD',
                   'CL','BST','LCSES','MAINLAND','RYSSW')
  AND SE_TIMESTAMP >= '2026-02-20' AND SE_TIMESTAMP < '2026-02-21'
```

**All 25 of 25** known `NmmsStationCode` values from
`docs/pun_audit_top25.md`'s roster matched `STATION` via **direct text
equality** — confirms `docs/pun_audit_top25.md`'s claim (`SE station ==
NmmsStationCode`) over `organic_load.py`'s more hedged phrasing, at least for
this 25-station sample. This is a sample confirmation, not a full-roster
match-rate audit (`tasks/09_injection_benchmark.md` §3.6 already calls for
that as its own headline number — not repeated here).

---

## 7. `pun_score` and `unresolved_xfmr_count` distributions (Question 7)

Bounded day, `station_bal`, 136,776 rows:

```sql
SELECT MIN(PUN_SCORE), MAX(PUN_SCORE), AVG(PUN_SCORE),
       COUNT_IF(PUN_SCORE > 0) n_pun_gt0, COUNT_IF(PUN_SCORE = 0) n_pun_eq0,
       MIN(UNRESOLVED_XFMR_COUNT), MAX(UNRESOLVED_XFMR_COUNT), COUNT_IF(UNRESOLVED_XFMR_COUNT > 0)
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE SE_TIMESTAMP >= '2026-02-20' AND SE_TIMESTAMP < '2026-02-21'
```

- `pun_score`: range **[0.0, 1.0]**, mean **0.0122** (most stations are near
  zero). `n_pun_gt0 = 5,160` (3.8%), `n_pun_eq0 = 128,640` (94.0%). The
  remaining 2,976 rows (2.2%) are `NULL` pun_score — **verified directly**:

  ```sql
  SELECT COUNT_IF(PUN_SCORE IS NULL) n_pun_null,
         COUNT_IF(COVERAGE_FLAG IS NULL) n_cov_null,
         COUNT_IF(PUN_SCORE IS NULL AND COVERAGE_FLAG IS NULL) n_both_null,
         COUNT(*) n_rows
  FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
  WHERE SE_TIMESTAMP >= '2026-02-20' AND SE_TIMESTAMP < '2026-02-21'
  -- result: n_pun_null = n_cov_null = n_both_null = 2,976 (exact match, all three)
  ```

  `PUN_SCORE IS NULL` and `COVERAGE_FLAG IS NULL` are the **exact same 2,976
  rows** — incomplete topology resolution suppresses both fields together.
  **Consequence for anyone reusing sdalvi's reference queries in
  `docs/large_load_research.md`:** those queries wrap `pun_score` in
  `COALESCE(sb.pun_score, 0)`, which silently treats these 2,976
  unresolved-topology station-hours (2.2% of the day) as *clean* (`pun_score
  = 0`) rather than *unknown* — worth a conscious decision, not a silent
  default, if this family is used going forward.
- `unresolved_xfmr_count`: range **[0, 6]**, `n>0 = 391` of 136,776 (0.29%)
  — the large majority of station-hours are fully topology-resolved.

---

## 8. Recommendations (for `tasks/09_injection_benchmark.md`, not executed here)

1. Question 1's `task09` §2 branch is now decided: **use the first branch**
   (true net injection is comparable) — `GenMW - WithdrawMW` (ercotStationLoad)
   against signed `*_NET_LOAD_MW` (this family), **not** the load-only
   fallback branch. But pull from `RAW_STATION_NET_LOAD_MW`
   (`station_bal`) or `SUM(TOTAL_NET_LOAD_MW)` over kv (`term_bal`) —
   **never the plain `STATION_NET_LOAD_MW`**, which is silently zeroed for a
   meaningful share of PUN-scored station-hours (§3.2).
2. Platform choice: **Snowflake `AW.DBO`** is the right platform for bulk/
   scan-style comparison work per this repo's DB-access rules (SQL Server is
   sequential/TOP-capped only) — but expect small (<0.1%) numeric
   differences and occasional clean-column disagreements versus the SQL
   Server copy that `organic_load.py` currently queries; don't mix rows
   across platforms in one comparison.
3. **Before running the task09 benchmark against 2026 data, resolve the
   freshness finding with sdalvi.** Both copies stop around early March
   2026; the task09 spec's window (`2026-01-01 → 2026-03-23`) is only
   partially covered: Snowflake's data ends 2026-03-04, **missing the last
   ~19 days** of that window, and SQL Server's ends 2026-02-26, **missing
   ~25 days** (a quarter of the requested window). If the intent was a
   source to extend *past* `ercotStationLoad`'s 2026-06-15 cutoff, this
   family as it stands today cannot do that — it currently stops *earlier*
   than `ercotStationLoad`, not later.
4. Bus-level: not reachable from this family on either platform (§5) — no
   change to the existing station→`SswgBusNumber` crosswalk dependency.

---

## Appendix: all queries run, in order

Section references above carry the exact SQL. Bounded day used throughout:
`2026-02-20 00:00:00` ≤ `SE_TIMESTAMP` < `2026-02-21 00:00:00` (Snowflake);
single instants `2026-02-20 00:57:00` / `01:57:00` for grain/reconciliation;
SQL Server window `2026-01-01` – `2026-03-23` for `run_id` cardinality (per
sdalvi's own reference window in `docs/large_load_research.md`). No
`SELECT *` was issued against any family table. Probe scripts (not part of
the deliverable, kept for reproducibility of exact query text/ordering only):
`p1_show_tables.py`, `p2_describe.py`, `p2b_more_schemas.py`,
`p3_sf_probes.py`, `p4_sf_followup.py`, `p5_sqlserver.py`, `p6_verify_null.py`
— all ran from a scratch dir, not checked into the repo.
