# Fleet-wide `ercotStationLoad.GenMW` coverage vs the `term_bal` family (2026-08-26)

Read-only Snowflake investigation (`AW.DBO`, via `pfa.sf.query`), answering
whether the ERCOT load-estimation family
(`ERCOTLOADESTIMATION_TERM_BAL`/`_STATION_BAL`) can replace
`AW.dbo.ercotStationLoad` for **net injection by station**. Triggered by a
prior n=2 finding (`jck_lonhill_generation.md` §1: `GenMW` entirely NULL for
JCK and LON_HILL, all 150 station-months 2020-01→2026-03) plus one anecdote
(`pun_audit_top25.md`: GBY "the only control station with a populated `GenMW`
column" among those reviewed). This report quantifies the gap fleet-wide.

All queries aggregate in SQL (`GROUP BY` station, or station+timestamp then
re-aggregated) except two explicitly-scoped row-level pulls (5 stations x 1
week each) used for the kv double-counting diagnostic. Script:
`/tmp/claude-1000/-workspaces-scratch-workspace/42f42055-457d-4044-a2ff-deac470ca995/scratchpad/genmw_investigation.py`
(cache-first; parquet snapshots of every query result alongside it, not
checked into the repo).

---

## Headline — the money number (Q1.5)

**`ercotStationLoad.GenMW` is *not* broadly unpopulated across the fleet in
the way the n=2 JCK/LON_HILL finding implied — but a real, material gap
exists.** Restricting to family-identified *material* generators
(`TOTAL_EST_GENERATION_MW` monthly max > 20 MW):

| Window | material-gen stations (family) | station-count with `GenMW` NULL/absent | **MW-weighted** — family generation-MWh sitting at NULL-`GenMW` stations |
|---|---:|---:|---:|
| **Feb 2026** (primary) | 650 | 191 (**29.4%**) | **14.1%** (5.35M of 37.86M MW-hrs) |
| **Jul 2023** (time control) | 490 | 99 (**20.2%**) | **9.9%** (4.92M of 49.75M MW-hrs) |

So: **roughly 86-90% of the fleet's material-generation MW-hours ARE visible
in `ercotStationLoad.GenMW`**; JCK and LON_HILL are real instances of a real
gap, not representative of "most generators." **This does not invert the
recommendation to "the family is the only option" — but it does mean
`ercotStationLoad` alone is insufficient for a complete net-injection
product**: a fifth to three-tenths of generator-stations (by count), carrying
roughly a tenth to a seventh of total generator MW-hours, would silently read
as zero generation if `GenMW` were trusted alone (NULL, not zero — see Q1.2).
Zero stations were "absent from `ercotStationLoad`" in either window's
material-generator set (all 191/99 are *present* with `GenMW` all-NULL, not
missing rows — see Q1.5 detail).

**This must be read together with the freshness finding already on record**
(`load_estimation_schema.md` §0/§4, not re-derived here): the family stops
updating **2026-03-04**; `ercotStationLoad` runs to **2026-06-15**. The
family cannot extend net-injection coverage *past* `ercotStationLoad` — it
can only backfill/supplement `GenMW` gaps *within* the overlapping history.
**Neither source alone is a complete answer to "net injection by station";
a hybrid (SL as primary, family-sourced generation fill for the ~10-14%
MW-weighted gap, within the window both cover) is the option this data
supports — a wholesale "replace" is not.**

---

## Q1 — fleet-wide `GenMW` coverage, unconditional and conditional

### Q1.1-1.3 — unconditional NULL rates (all stations, not just generators)

```sql
SELECT NMMSSTATIONCODE AS STATION,
       COUNT(*) AS N_ROWS,
       COUNT(GENMW) AS N_NOTNULL_GEN, COUNT_IF(GENMW <> 0) AS N_NONZERO_GEN,
       SUM(GENMW) AS SUM_GEN, MAX(GENMW) AS MAX_GEN, MIN(GENMW) AS MIN_GEN,
       COUNT(WITHDRAWMW) AS N_NOTNULL_WD, COUNT_IF(WITHDRAWMW <> 0) AS N_NONZERO_WD,
       SUM(ABS(WITHDRAWMW)) AS SUM_ABS_WD, AVG(WITHDRAWMW) AS AVG_WD,
       STDDEV(WITHDRAWMW) AS STD_WD, AVG(ABS(WITHDRAWMW)) AS MEAN_ABS_WD,
       MAX(WITHDRAWMW) AS MAX_WD, MIN(WITHDRAWMW) AS MIN_WD
FROM AW.dbo.ercotStationLoad
WHERE DATE >= '{start}' AND DATE < '{end}'
GROUP BY NMMSSTATIONCODE
```

| Window | n stations | `GENMW` entirely NULL | any non-NULL | any non-zero | `WITHDRAWMW` entirely NULL | any non-NULL | any non-zero |
|---|---:|---:|---:|---:|---:|---:|---:|
| Feb 2026 | 5,662 | 5,129 (90.6%) | 533 (9.4%) | 502 (8.9%) | 22 (0.4%) | 5,640 (99.6%) | 5,512 (97.4%) |
| Jul 2023 | 5,227 | 4,713 (90.2%) | 514 (9.8%) | 471 (9.0%) | 23 (0.4%) | 5,204 (99.6%) | 5,101 (97.6%) |

**Restricted to near-full-hourly-coverage stations** (`N_ROWS >= 90%` of
expected hours — 672h Feb/744h Jul), to rule out sparse-row stations
distorting the picture: **essentially unchanged** (Feb: 5,119/5,652 = 90.6%
entirely-NULL; Jul: 4,702/5,211 = 90.2%). The NULL rate is not a low-coverage
artifact.

**Contrast is stark but must not be read as the money number on its own**:
`WITHDRAWMW` is populated for 99.6% of stations; `GENMW` for only 9.4%. But
most of that 90%+ "NULL" is **correctly** NULL — most stations in
`ercotStationLoad` are pure-load stations that never generate, so an
unconditional NULL rate mixes "station doesn't generate" (not a data gap)
with "station does generate but `GenMW` wasn't populated" (a real gap). Only
the latter matters for net injection — that is what Q1.5 isolates.

### Q1.4 — MW weight behind the NULL vs. populated `GenMW` groups

```text
Feb 2026:
                 n_stations  total_abs_wd  avg_abs_wd_per_station   max_abs_wd
GENMW_ALL_NULL         5129  33,293,435.2                6,491.21    437,994.0
GENMW_POPULATED         533  31,775,966.0               62,183.89  1,736,913.3
  (family-side, n=508 matched): SUM_GEN_MW total = 32,516,476.2, max(MAX_GEN_MW) = 3,267.1

Jul 2023:
                 n_stations  total_abs_wd  avg_abs_wd_per_station   max_abs_wd
GENMW_ALL_NULL         4713  44,717,460.9                9,488.11    445,897.6
GENMW_POPULATED         514  43,310,745.2               88,209.26  1,800,410.0
  (family-side, n=491 matched): SUM_GEN_MW total = 44,842,596.5, max(MAX_GEN_MW) = 2,842.1
```

The two groups carry **roughly equal total `WithdrawMW` weight** despite the
NULL group having ~10x more stations — i.e. NULL-`GenMW` stations are, on
average, much smaller individually (avg ~6.5-9.5K vs ~62-88K MW-hrs/station),
consistent with most of them being small pure-load stations. This is a
different cut from Q1.5's money number (which conditions on the family
already having flagged the station as a material generator); it's reported
because station-count alone would understate how much total system activity
sits in each group.

### Q1.5 — the money number, in full

```sql
WITH per_ts AS (
  SELECT STATION, SE_TIMESTAMP,
         SUM(TOTAL_EST_GENERATION_MW) AS GEN_MW, SUM(TOTAL_EST_LOAD_MW) AS LOAD_MW,
         SUM(TOTAL_NET_LOAD_MW) AS NET_MW
  FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
  WHERE SE_TIMESTAMP >= '{start}' AND SE_TIMESTAMP < '{end}'
  GROUP BY STATION, SE_TIMESTAMP
)
SELECT STATION, COUNT(*) AS N_TS, MAX(GEN_MW) AS MAX_GEN_MW, AVG(GEN_MW) AS AVG_GEN_MW,
       SUM(GEN_MW) AS SUM_GEN_MW, MAX(LOAD_MW) AS MAX_LOAD_MW, SUM(LOAD_MW) AS SUM_LOAD_MW,
       AVG(NET_MW) AS AVG_NET, STDDEV(NET_MW) AS STD_NET, AVG(ABS(NET_MW)) AS MEAN_ABS_NET,
       MIN(NET_MW) AS MIN_NET, MAX(NET_MW) AS MAX_NET
FROM per_ts GROUP BY STATION
-- then, in pandas: left-join onto the ercotStationLoad per-station aggregate on STATION,
-- filter to MAX_GEN_MW > 20, classify each row ABSENT_FROM_SL / PRESENT_GENMW_NULL / PRESENT_GENMW_POPULATED
```

**Feb 2026** — 650 material-generation stations (family-side; ~11.7% of the
5,576 stations the family carries that month):

| status | stations | family `SUM_GEN_MW` (MW-hrs) | share |
|---|---:|---:|---:|
| `ABSENT_FROM_SL` | 0 | 0.0 | 0.0% |
| `PRESENT_GENMW_NULL` | 191 | 5,349,578.0 | **14.1%** |
| `PRESENT_GENMW_POPULATED` | 459 | 32,513,444.5 | 85.9% |

**Jul 2023** — 490 material-generation stations (~9.5% of 5,186):

| status | stations | family `SUM_GEN_MW` (MW-hrs) | share |
|---|---:|---:|---:|
| `ABSENT_FROM_SL` | 0 | 0.0 | 0.0% |
| `PRESENT_GENMW_NULL` | 99 | 4,921,739.4 | **9.9%** |
| `PRESENT_GENMW_POPULATED` | 391 | 44,829,414.3 | 90.1% |

Every unpopulated case is **present in `ercotStationLoad` with `GenMW`
all-NULL for the window**, not a missing station — worth stating plainly
since "absent" and "NULL" would need different fixes (they turned out to be
the same fix here: none of the material-generation gap comes from missing
station rows).

**Top offenders (material-generation stations with unpopulated `GenMW`),
Feb 2026, by family `SUM_GEN_MW`:**

| Station | Max gen (MW) | Monthly gen (MW-hrs) |
|---|---:|---:|
| LWSSW | 881.0 | 308,754 |
| PKRSW | 883.9 | 227,347 |
| DPW | 638.2 | 207,775 |
| GRNBELT | 271.5 | 164,344 |
| CHB | 630.9 | 163,041 |
| DOW | 366.1 | 149,781 |
| BCV | 291.2 | 142,629 |
| STEWART | 438.4 | 127,372 |
| REATA | 539.3 | 125,781 |
| EMSES | 323.0 | 117,981 |

(10 of 20 shown; full 20 in the script's stdout log. **DPW** appearing here
is consistent with — not a contradiction of — `pun_audit_top25.md`'s
original claim that GBY was "the *only*" control station with populated
`GenMW`: DPW's `term_bal` generation profile was documented in
`load_estimation_schema.md` §3.2, but nothing there claimed DPW's
`ercotStationLoad.GenMW` was populated, and this investigation now shows it
is not. GBY itself does **not** appear in either window's offender list,
i.e. GBY's `GenMW` is populated, matching the anecdote directly.)

**Caveat on generalizing:** two bounded months, ~5-6 months apart, in
different seasons. The money number moved from 9.9% (Jul) to 14.1% (Feb) and
the offender station roster is only partially overlapping (CHB, DPW, BCV,
GRNBELT, EMSES, I_DUPSW, LPLYH, PWL recur in both; most others don't) — this
looks like which specific units are dispatching materially shifts
seasonally, not that the coverage gap itself is random noise. **State this
as a range (roughly 10-14% MW-weighted, 20-29% by station count), not a
single point estimate** — a full-history run would be needed to pin down a
precise fleet-wide figure or a seasonal pattern, which was out of scope here
(two bounded-month probes, per the query-discipline instructions).

---

## Q2 — bidirectional station-namespace coverage

```python
# outer merge of the Q1 unified per-station frames (family vs SL) on STATION, indicator=True
```

| Window | family stations NOT in `ercotStationLoad` | `ercotStationLoad` stations NOT in family | MW weight of the latter |
|---|---:|---:|---:|
| Feb 2026 | **0** | 86 | 72,383 (SUM\|WithdrawMW\|, vs ~65M fleet total — <0.2%) |
| Jul 2023 | **0** | 41 | 59,015 (similarly <0.2%) |

Internal consistency check: `5,576 (family) + 86 (SL-only) = 5,662 (SL total)`
for Feb 2026, and `5,186 + 41 = 5,227` for Jul 2023 — exact both times.

**Coverage is asymmetric and favorable to "family as generation source":
every family station is also in `ercotStationLoad`'s namespace** (0 in
either window) — the family is not missing any station `ercotStationLoad`
carries. The reverse gap (`ercotStationLoad` has some names the family
doesn't) is small and low-weight: the biggest are `RENOS_LC`, `ACKRLY`,
`BRKSTNLC`, `BLANCO`, `ELMNT_RC` (Feb 2026) and `ELMNT_RC`, `SCHOTTKY`,
`NIMROD`, `ACKRLY`, `WHTS_RC` (Jul 2023) — several recur across windows, and
the `_LC`/`_RC` suffix pattern (seen repeatedly on both sides) suggests a
consistent small-station naming class (plausibly "Load Center"/"Resource
Center" or similar), not random gaps. **Station-namespace coverage is not
the blocker for "replace" — the `GenMW`-population gap quantified in Q1 is.**

---

## Q3 — out of scope for this report

**Dropped per coordinator scope reduction (2026-08-26):** the 3x scale-gap /
kv double-counting test is owned by a separate, dedicated agent writing
`docs/kv_aggregation_test.md`. Not investigated here to avoid duplicating
that work. (An earlier draft of this report contained a full Q3 section,
including a 31-station ratio-distribution scan and a 5-station kv
sign-structure diagnostic for Aug 2024; it was removed for this reason, not
because the underlying queries failed — see `run2.log` in the Files section
below if that superseded work is ever useful as a cross-check.)

---

## Q4 — `EXT_*`/`TOTAL_*`/`PUN_*` relationships (feeds the doc correction)

`load_estimation_schema.md` §2 previously inferred `TOTAL_* = EXT_* + INT_*`
generically. **The spine of the correction is column existence, checkable
from that same doc's own column list without running anything: `INT_*`
exists as a real column only for `IMPORT_MW`/`EXPORT_MW` — there is no
`INT_EST_LOAD_MW` or `INT_EST_GENERATION_MW` column at all**, so the claim
as written is not even well-formed for the `LOAD`/`GENERATION`/`NET_LOAD`
families. Verified empirically on top of that (6 stations —
JCK/GBY/HCKSW/SNDSW/WTRML/DPW — chosen to extend `jck_lonhill_generation.md`
§3.3's n=1-station JCK-only test to both load-only and generator stations;
window 2026-02-19→26, the same week that report used):

```sql
-- row grain (per station/kv/timestamp, no pre-summing):
SELECT STATION, COUNT(*) AS N_ROWS,
  AVG(TOTAL_IMPORT_MW - EXT_IMPORT_MW - INT_IMPORT_MW) AS AVG_RESID_IMPORT,
  MAX(ABS(TOTAL_IMPORT_MW - EXT_IMPORT_MW - INT_IMPORT_MW)) AS MAXABS_RESID_IMPORT,
  AVG(TOTAL_EXPORT_MW - EXT_EXPORT_MW - INT_EXPORT_MW) AS AVG_RESID_EXPORT,
  MAX(ABS(TOTAL_EXPORT_MW - EXT_EXPORT_MW - INT_EXPORT_MW)) AS MAXABS_RESID_EXPORT
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION IN ('JCK','GBY','HCKSW','SNDSW','WTRML','DPW')
  AND SE_TIMESTAMP >= '2026-02-19 00:00:00' AND SE_TIMESTAMP < '2026-02-26 00:00:00'
GROUP BY STATION
```

**Result: `TOTAL_IMPORT_MW = EXT_IMPORT_MW + INT_IMPORT_MW` and
`TOTAL_EXPORT_MW = EXT_EXPORT_MW + INT_EXPORT_MW` hold EXACTLY** (max
`|residual|` = 0.00 MW) **for all 6 stations** — load-only and generator
alike. **The original naming-based inference was correct — but only for the
one column family (`IMPORT`/`EXPORT`) where `INT_*` actually exists.**

For `LOAD_MW`/`GENERATION_MW` (no `INT_*` variant), tested at kv-summed
grain (matching `jck_lonhill_generation.md` §3.3's method) across the same 6
stations:

```sql
WITH per_ts AS (
  SELECT STATION, SE_TIMESTAMP,
    SUM(EXT_EST_LOAD_MW) AS EXT_LOAD, SUM(TOTAL_EST_LOAD_MW) AS TOT_LOAD, SUM(EXT_EST_GENERATION_MW) AS EXT_GEN,
    SUM(TOTAL_IMPORT_MW) AS TOT_IMP, SUM(EXT_IMPORT_MW) AS EXT_IMP,
    SUM(TOTAL_EXPORT_MW) AS TOT_EXP, SUM(EXT_EXPORT_MW) AS EXT_EXP,
    SUM(PUN_TOTAL_EST_LOAD_MW) AS PUNTOT_LOAD, SUM(PUN_TOTAL_EST_GENERATION_MW) AS PUNTOT_GEN
  FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
  WHERE STATION IN ('JCK','GBY','HCKSW','SNDSW','WTRML','DPW')
    AND SE_TIMESTAMP >= '2026-02-19 00:00:00' AND SE_TIMESTAMP < '2026-02-26 00:00:00'
  GROUP BY STATION, SE_TIMESTAMP
)
SELECT STATION, COUNT(*) AS N_TS,
  AVG(EXT_LOAD - TOT_LOAD - EXT_GEN) AS AVG_RESID, MAX(ABS(EXT_LOAD - TOT_LOAD - EXT_GEN)) AS MAXABS_RESID,
  AVG((TOT_IMP-EXT_IMP)-PUNTOT_LOAD) AS AVG_RESID_PUNLOAD, AVG((TOT_EXP-EXT_EXP)-PUNTOT_GEN) AS AVG_RESID_PUNGEN
FROM per_ts GROUP BY STATION
```

| Station | `EXT_LOAD - TOTAL_LOAD - EXT_GEN` avg / max\|resid\| (MW) | `(TOTAL_IMP-EXT_IMP) - PUN_TOTAL_LOAD` avg/max (MW) |
|---|---|---|
| JCK | -0.00 / 0.00 | -0.00 / 0.00 |
| SNDSW | 0.00 / 0.00 | -0.00 / 0.00 |
| HCKSW | 0.00 / 0.00 | 0.00 / 0.00 |
| DPW | -241.89 / 473.53 | 0.00 / 0.00 |
| WTRML | -148.06 / 250.79 | 0.00 / 0.00 |
| GBY | -127.58 / 302.46 | **35.25 / 150.15** |

**`EXT_EST_LOAD_MW = TOTAL_EST_LOAD_MW + EXT_EST_GENERATION_MW` holds exactly
for load-only/small-net stations (JCK, SNDSW, HCKSW) but breaks down for
stations with material external generation (DPW, WTRML, GBY: 100-250 MW
average residual, up to ~475 MW max).** The original doc's test was JCK-only
and (correctly, as far as it went) reported this identity holding — extending
to generator stations shows **it does not generalize; it is a property of
non-generating stations, not a general pipeline identity.** Separately, the
`TOTAL_IMPORT-EXT_IMPORT = PUN_TOTAL_EST_LOAD_MW` identity (and its export/
generation mirror) holds almost exactly for 5 of 6 stations but shows a
small, real, unexplained residual specifically at **GBY** (~35 MW avg, ~150
MW max) — flagged, not resolved (would need pipeline source access).

**`load_estimation_schema.md` has been corrected in place** (the one
sentence inferring `TOTAL_* = EXT_* + INT_*`), marked corrected 2026-08-26
with a pointer to this evidence. Nothing else in that document was touched.

---

## Scope and limitations (read before reusing these numbers)

- Q1/Q2: two bounded months (Feb 2026, Jul 2023) — the money number moved
  ~4 points between them (9.9% → 14.1% MW-weighted); treat as a range, not a
  precise fleet constant, and don't assume it's stable across seasons without
  checking more months.
- Q3 (3x scale-gap / kv double-counting) was dropped from this report's scope
  — see the separate agent's `docs/kv_aggregation_test.md` for that finding.
- Q4's identity tests are 6 stations x 1 week (the same week
  `jck_lonhill_generation.md` used, for direct comparability) — extended
  across station *types*, not across *time*.
- No pipeline source code was available for any of this — every relationship
  reported is empirical (observed in the data), not confirmed against how
  the pipeline actually computes these columns.

## Files

- This report: `/workspaces/scratch-workspace/load-forecast/docs/genmw_coverage.md`
- Doc correction: `/workspaces/scratch-workspace/load-forecast/docs/load_estimation_schema.md` (one paragraph, §2, marked corrected 2026-08-26)
- Investigation script (cache-first, all exact queries):
  `/tmp/claude-1000/-workspaces-scratch-workspace/42f42055-457d-4044-a2ff-deac470ca995/scratchpad/genmw_investigation.py`
- Cached query results (parquet, not checked in): alongside the script,
  `sl_unified_*.parquet`, `fam_unified_*.parquet`,
  `q4_rowgrain_identity.parquet`, `q4_kvsum_identity.parquet`. (Q3-specific
  parquet files — `q3_kv_diag_*.parquet`, `q3_ratio_table.parquet`,
  `q3_kv_variant_table.parquet` — also exist in the same scratch directory
  from the superseded run but are not part of this report's deliverable.)
- Full stdout logs: `run1.log` (crashed mid-run on a Decimal/float bug after
  the 6 primary queries completed and cached), `run2.log` (clean full run
  after the fix, all sections) — same scratchpad directory.
