# kv-aggregation test: does summing `TOTAL_NET_LOAD_MW` over kv double-count? (2026-08-26)

Read-only Snowflake investigation (`AW.DBO`, warehouse `AI_READ_ONLY`, via
`pfa.sf.query`). No pipeline built, no existing source file modified.
Script: `/tmp/claude-1000/-workspaces-scratch-workspace/42f42055-457d-4044-a2ff-deac470ca995/scratchpad/kv_aggregation_test.py`
(scratchpad only, not checked in). Raw query results cached as CSVs in the
same directory (`s0_*`, `s1_*`, `s2_*`, `s3_*`).

## Headline answers

- **Q1 — the double-counting hypothesis is FALSIFIED.** `SUM(TOTAL_NET_LOAD_MW)`
  over kv — the current approach, numerically identical to
  `RAW_STATION_NET_LOAD_MW` — is the correct aggregation rule and needs no
  change. It reconciles to ~1.0 for the large majority of stations regardless
  of kv count (median ratio 1.001 across 30 stations spanning `KV_COUNT`
  1–5; correlation between `KV_COUNT` and the ratio is r=0.093, i.e. none).
  LON_HILL's ~3.1x gap survives *every* kv-selection variant tried, because
  its three kv rows are non-overlapping physical readings, not a mirrored
  pair — there is nothing to "un-double-count."
- **Q2 — JCK's correctly-aggregated net is ~28 MW average** (range 20–37 MW)
  over the test week, **not** ~839 MW (that figure is confirmed, again, to
  live only in the `PUN_TOTAL_*` family) and **not exactly** ~8.5 MW either
  (`ercotStationLoad.WithdrawMW`'s average over the identical hours). The PUN
  reading wins **directionally and decisively** — JCK is a tens-of-MW
  station, nowhere close to a top-tier 839 MW load — but the exact ~8 MW
  claim is not reproduced by the family's own correct column: there is an
  unexplained **3.28x** residual, the same character and similar magnitude
  as LON_HILL's unresolved Q1 gap.

---

## Q1a. LON_HILL mechanism test, Aug 4–6 2024 (peak-generation window per `jck_lonhill_generation.md` §2.3)

Peak day identified in that doc as **2024-08-04** (`DAY_SUM_GEN=4193.78`,
highest in Aug-2024). Reused the doc's exact 48-hour window (Aug 4→6) for
direct comparability with its r=0.97 correlation finding.

### Query 1 — kv-level detail (mechanism)

```sql
SELECT SE_TIMESTAMP, KV, TOTAL_EST_LOAD_MW, TOTAL_EST_GENERATION_MW, TOTAL_NET_LOAD_MW
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION = 'LON_HILL' AND SE_TIMESTAMP >= '2024-08-04 00:00:00' AND SE_TIMESTAMP < '2024-08-06 00:00:00'
ORDER BY SE_TIMESTAMP, KV
```

Result: LON_HILL has exactly 3 kv rows every hour, and they are **not
overlapping readings of the same thing**:

| kV | role (all 48 hours) | magnitude |
|---|---|---|
| 69  | LOAD only (`GEN`≡0) | ~0.04 – 0.10 MW |
| 138 | GENERATION only (`LOAD`≡0) | ~125 – 253 MW — this is LON_HILL's real generator (matches doc §2.3/§2.5) |
| 345 | LOAD only (`GEN`≡0) | ~0.02 – 1.35 MW |

Nothing here is mirrored or double-booked — each kv row is a distinct,
non-overlapping physical reading. That is itself evidence against the
double-counting hypothesis, independent of the ratio arithmetic below.

### Query 2 — station_bal

```sql
SELECT SE_TIMESTAMP, RAW_STATION_NET_LOAD_MW, RAW_STATION_EST_LOAD_MW, RAW_STATION_EST_GENERATION_MW,
       PUN_SCORE, UNRESOLVED_XFMR_COUNT, COVERAGE_FLAG
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE STATION = 'LON_HILL' AND SE_TIMESTAMP >= '2024-08-04 00:00:00' AND SE_TIMESTAMP < '2024-08-06 00:00:00'
ORDER BY SE_TIMESTAMP
```

### Query 3 — ercotStationLoad

```sql
SELECT DATE, HOUR, WITHDRAWMW, GENMW
FROM AW.dbo.ercotStationLoad
WHERE NMMSSTATIONCODE = 'LON_HILL' AND DATE >= '2024-08-04' AND DATE < '2024-08-06'
ORDER BY DATE, HOUR
```

### Five variants vs `WithdrawMW` (48 hours)

| Variant | Definition | ratio-of-sums | median hourly ratio | range |
|---|---|---:|---:|---:|
| (a) SUM_ALL_KV | current approach | 3.125 | 3.149 | 2.80 – 3.96 |
| (b) HIGHEST_KV | 345 kV alone | −0.008 | −0.005 | −0.04 – 0.00 |
| (c) LARGEST_MAGNITUDE | 138 kV alone (the generation row) | 3.134 | 3.155 | 2.80 – 3.98 |
| (d) SUM_EXCL_HIGHEST | 69+138 kV | 3.133 | 3.154 | 2.80 – 3.98 |
| (e) RAW_STATION_NET_LOAD_MW | station_bal | 3.125 | 3.149 | 2.80 – 3.96 |

**(a) and (e) are identical to 6 decimal places on every one of the 48
hours** — confirms `load_estimation_schema.md`'s reconciliation finding
holds for LON_HILL/Aug-2024 specifically, not just the stations/instant it
was originally tested on. (e) can therefore never be an independent fix for
(a)'s gap.

(b) is nonsensical (wrong sign, near-zero) because "highest kv" (345) is not
where LON_HILL's real generation lives (that's 138 kV, the *middle*
voltage) — "pick the highest kv" is not even a coherent rule across
stations. (c) and (d) both land within noise of (a) because the two
non-generation kv rows (69, 345) are two to three orders of magnitude
smaller than the 138 kV generation and barely move the total.

**None of the five variants reconciles to ~1.0.** The ~3.1x gap is not an
aggregation artifact — it is a genuine magnitude difference between how the
family estimates LON_HILL's 138 kV generator output and how
`ercotStationLoad.WithdrawMW` measures the same asset. Cause not
determined here (same open item as `jck_lonhill_generation.md` §2.3:
metering boundary / station-service treatment / plant-footprint difference
— **all INFERRED, none confirmed**).

## Q1b. Generality sweep — 30 stations, `KV_COUNT` 1–5, Feb 16–23 2026

### Candidate discovery

```sql
-- kv count per station, all stations, 1-hour window (cheap: single hour, not a full-day scan)
SELECT STATION, COUNT(DISTINCT KV) AS KV_COUNT
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE SE_TIMESTAMP >= '2026-02-16 00:00:00' AND SE_TIMESTAMP < '2026-02-16 01:00:00'
GROUP BY STATION
-- 5575 stations returned; KV_COUNT distribution: 1→4560, 2→941, 3→64, 4→8, 5→2

-- size ranking, 1 day
SELECT NMMSSTATIONCODE, AVG(ABS(WITHDRAWMW)) AS AVG_ABS_WITHDRAW, COUNT(*) AS N
FROM AW.dbo.ercotStationLoad
WHERE DATE = '2026-02-16'
GROUP BY NMMSSTATIONCODE
```

Stratified by `KV_COUNT` bucket (1/2/3/4/5+), picked up to 7 stations per
bucket spanning the size range, then force-included JCK and LON_HILL as
reference cases. Final n=30 (7/8/8/5/2 across buckets 1–5), sizes spanning
~1 MW to ~2,680 MW average |withdraw| — includes two nuclear plants (STP,
CPSES) and several solar plants (`*SES`, `*SLR` suffixes) alongside small
single-kv load stations.

### Sweep queries (30-station IN-list, 2026-02-16 → 2026-02-23, 168 hours/station)

```sql
SELECT STATION, SE_TIMESTAMP, SUM(TOTAL_NET_LOAD_MW) AS SUM_NET, COUNT(DISTINCT KV) AS KV_COUNT
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION IN (<30 stations>) AND SE_TIMESTAMP >= '2026-02-16 00:00:00' AND SE_TIMESTAMP < '2026-02-23 00:00:00'
GROUP BY STATION, SE_TIMESTAMP

SELECT STATION, SE_TIMESTAMP, RAW_STATION_NET_LOAD_MW
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE STATION IN (<30 stations>) AND SE_TIMESTAMP >= '2026-02-16 00:00:00' AND SE_TIMESTAMP < '2026-02-23 00:00:00'

SELECT NMMSSTATIONCODE, DATE, HOUR, WITHDRAWMW
FROM AW.dbo.ercotStationLoad
WHERE NMMSSTATIONCODE IN (<30 stations>) AND DATE >= '2026-02-16' AND DATE < '2026-02-23'
```

### Results (ratio = ratio-of-sums over the 168-hour window; none hit the |ΣWithdrawMW|<5 MW "undefined" floor)

| Station | KV_COUNT | Sum WithdrawMW | Sum (a) SUM_ALL_KV | Sum (e) RAW_STATION_BAL | Ratio (a) | Ratio (e) | Median hourly ratio (a) | Sign-disagree hrs/168 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CBECII | 1 | -136808.2 | -136702.3 | -136702.3 | 0.999 | 0.999 | 0.999 | 0 |
| DENT_RD | 1 | 1527.5 | 1527.5 | 1527.5 | 1.000 | 1.000 | 1.000 | 0 |
| GVAVE | 1 | 4033.4 | 4034.0 | 4034.0 | 1.000 | 1.000 | 1.000 | 0 |
| T2 | 1 | 2682.8 | 2686.5 | 2686.5 | 1.001 | 1.001 | 1.001 | 0 |
| SUNNILAN | 1 | 774.6 | 784.3 | 784.3 | 1.013 | 1.013 | 1.008 | 0 |
| WEAVERRD | 1 | 431.4 | 437.7 | 437.7 | 1.015 | 1.015 | 1.014 | 0 |
| OZONA | 1 | 399.4 | 410.9 | 410.9 | 1.029 | 1.029 | 1.050 | 0 |
| KEO | 2 | -11363.2 | -11275.0 | -11275.0 | 0.992 | 0.992 | 0.992 | 2 |
| WEBBER_S | 2 | -637.8 | -635.7 | -635.7 | 0.997 | 0.997 | 0.999 | 0 |
| VERTIGO | 2 | -4242.2 | -4232.9 | -4232.9 | 0.998 | 0.998 | 0.999 | 1 |
| HKSN_SLR | 2 | -11799.8 | -11774.4 | -11774.4 | 0.998 | 0.998 | 0.999 | 0 |
| STP | 2 | -449721.4 | -449315.9 | -449315.9 | 0.999 | 0.999 | 0.999 | 0 |
| LOMA_ALT | 2 | 188.1 | 189.3 | 189.3 | 1.006 | 1.006 | 1.006 | 0 |
| BRNWD | 2 | 2463.0 | 2506.1 | 2506.1 | 1.017 | 1.017 | 1.015 | 0 |
| JCK | 2 | 1431.1 | 4689.9 | 4689.9 | 3.277 | 3.277 | 3.268 | 0 |
| SWEETWN3 | 3 | -10023.2 | -9887.0 | -9887.0 | 0.986 | 0.986 | 0.990 | 0 |
| DPW | 3 | -45499.4 | -45343.5 | -45343.5 | 0.997 | 0.997 | 0.995 | 0 |
| CPSES | 3 | -406663.7 | -405644.8 | -405644.8 | 0.997 | 0.997 | 0.998 | 0 |
| NORTHLAN | 3 | 3774.9 | 3788.6 | 3788.6 | 1.004 | 1.004 | 1.003 | 0 |
| LPLYH | 3 | 1895.1 | 1905.7 | 1905.7 | 1.006 | 1.006 | 1.005 | 0 |
| LON_HILL | 3 | 6708.6 | 7498.0 | 7498.0 | 1.118 | 1.118 | 1.083 | 0 |
| SCSES | 3 | 660.0 | 747.8 | 747.8 | 1.133 | 1.133 | 1.121 | 0 |
| MGSES | 3 | 62.2 | 1297.6 | 1297.6 | 20.860 | 20.860 | 5.909 | 45 |
| DCSES | 4 | -64.7 | -50.0 | -50.0 | 0.774 | 0.774 | 1.024 | 3 |
| WAP | 4 | -94098.9 | -91090.1 | -91090.1 | 0.968 | 0.968 | 0.967 | 0 |
| CALAVERS | 4 | -202044.2 | -201434.9 | -201434.9 | 0.997 | 0.997 | 0.999 | 0 |
| WO | 4 | 7294.1 | 7460.1 | 7460.1 | 1.023 | 1.023 | 1.022 | 0 |
| GRSES | 4 | 390.1 | 1731.3 | 1731.3 | 4.438 | 4.438 | 3.075 | 0 |
| BRAUNIG | 5 | -82895.8 | -82583.5 | -82583.5 | 0.996 | 0.996 | 0.996 | 0 |
| THW | 5 | 13666.4 | 14342.6 | 14342.6 | 1.049 | 1.049 | 1.051 | 0 |

**(a) and (e) match to 6 decimal places on every station-hour** in this
sweep too (5,040 rows) — confirms, again, that `RAW_STATION_NET_LOAD_MW`
is a materialized copy of `SUM(TOTAL_NET_LOAD_MW)`, not an independent
figure.

Note LON_HILL specifically: ratio here is **1.118**, not the ~3.1x seen in
the Aug-2024 peak window. LON_HILL's generator is seasonal (per
`jck_lonhill_generation.md` §2 — dispatched mostly in summer); in this Feb
window it isn't running, and the gap collapses toward the population
baseline (1.118 sits in the same band as e.g. SCSES's 1.133 — not a
perfectly clean 1.000, but far from 3.1x). That is further evidence the gap
tracks **generation dispatch**, not kv-aggregation mechanics — a static
double-counting bug would not shrink by ~3x when the season changes.

### kv-count correlation test

Pearson **corr(KV_COUNT, RATIO_A) = 0.093** across the 30 stations —
essentially zero.

| KV_COUNT | mean RATIO_A | median RATIO_A | n |
|---:|---:|---:|---:|
| 1 | 1.008 | 1.001 | 7 |
| 2 | 1.286 | 0.998 | 8 |
| 3 | 3.513 | 1.005 | 8 |
| 4 | 1.640 | 0.997 | 5 |
| 5 | 1.023 | 1.023 | 2 |

Medians are flat at ~1.0 across every `KV_COUNT` bucket from 1 to 5; means
are dragged around entirely by 2–3 named outliers per bucket (below), not
by kv count itself. **`KV_COUNT`=1 stations (n=7, no kv-summing possible at
all) already sit at median 1.001, range 0.999–1.03** — the same band as the
multi-kv stations. If summing over kv double-counted, ratio would scale
with `KV_COUNT`; it manifestly does not.

Two of the largest, most complex multi-kv stations in the sweep are also
the cleanest reconciliations: **STP** (South Texas Project, nuclear,
`KV_COUNT`=2, ratio 0.999) and **CPSES** (Comanche Peak, nuclear,
`KV_COUNT`=3, ratio 0.997). Large real generators with genuine multi-kv
topology are not inherently broken by summing over kv.

**Named outliers, not explained by `KV_COUNT`:**
- **JCK** (3.28x) — see Q2 below.
- **MGSES** (20.86x): small absolute magnitude (family ~7.7 MW mean vs
  `ercotStationLoad` ~0.37 MW mean — a real ~7 MW absolute disagreement,
  not nothing) but an *unstable* ratio (median hourly ratio 5.9 vs
  ratio-of-sums 20.9 — the two summary statistics disagree by 3.5x on the
  same data) — near-zero denominator makes the ratio itself noisy even
  though the underlying gap is real. 45/168 hours (27%) disagree in *sign*
  between the family and `ercotStationLoad` — consistent with solar
  production-timing/curtailment differences between sources. **Not
  investigated further — out of task scope.**
- **GRSES** (4.44x) and **DCSES** (0.77x, 3 sign-disagreement hours): both
  small (`*SES` suffix, ~2–9 MW average), plausibly the same solar-timing
  mismatch category as MGSES. **Not investigated further — out of task
  scope.**
- `DCSES` (`KV_COUNT`=4, ratio 0.77, *below* 1) vs `GRSES` (`KV_COUNT`=4,
  ratio 4.44, *above* 1) sitting in the same kv-count bucket with opposite
  deviations is itself further evidence against a kv-count-driven
  mechanism.

## Q1 answer

**`SUM(TOTAL_NET_LOAD_MW)` over kv — the current approach, numerically
identical to `RAW_STATION_NET_LOAD_MW` — is the correct aggregation rule.
Do not change it.** It already reconciles to ~1.0 (median 1.001 across 30
stations spanning `KV_COUNT` 1–5, including two large multi-kv nuclear
generators at 0.997–0.999).

The task's opening hypothesis — that summing over kv counts both sides of a
transformer — is **falsified**, on two independent lines of evidence:
1. LON_HILL's per-kv breakdown shows three non-overlapping physical
   readings (a small 69 kV load, the real 138 kV generator, a small 345 kV
   load), not a mirrored pair. No combination of its kv rows reconciles the
   ~3.1x gap, including the row containing 100% of the generation. There is
   nothing to "un-double-count."
2. Across the 30-station sweep, the ratio shows no correlation with kv
   count (r=0.093); `KV_COUNT`=1 stations (nothing to sum) sit at the same
   ~1.0 baseline as multi-kv stations, including large, complex, genuinely
   multi-terminal nuclear generators.

The handful of stations that don't reconcile (JCK, MGSES, GRSES, DCSES) are
station-specific anomalies — a PUN with unusual internal topology, and
small solar plants with likely production-timing mismatches vs
`ercotStationLoad` — not a systematic kv-aggregation bug.

**Architecture implication:** because the residual is station-and-dispatch-
specific rather than systematic, the fix is not an aggregation-rule change
anywhere in the pipeline — it is a per-station reconciliation/flagging step
(JCK, LON_HILL during summer dispatch, and `*SES` small solar plants are
candidates) layered on top of the existing, already-correct `SUM`/
`RAW_STATION_NET_LOAD_MW` rule.

---

## Q2. JCK's actual net, Feb 16–23 2026 (7 days, using the Q1-correct rule = SUM over kv)

### Queries

```sql
SELECT SE_TIMESTAMP, KV, TOTAL_EST_LOAD_MW, TOTAL_EST_GENERATION_MW, TOTAL_NET_LOAD_MW
FROM AW.DBO.ERCOTLOADESTIMATION_TERM_BAL
WHERE STATION = 'JCK' AND SE_TIMESTAMP >= '2026-02-16 00:00:00' AND SE_TIMESTAMP < '2026-02-23 00:00:00'
ORDER BY SE_TIMESTAMP, KV

SELECT SE_TIMESTAMP, RAW_STATION_NET_LOAD_MW, RAW_STATION_EST_LOAD_MW, RAW_STATION_EST_GENERATION_MW,
       PUN_SCORE, UNRESOLVED_XFMR_COUNT, COVERAGE_FLAG
FROM AW.DBO.ERCOTLOADESTIMATION_STATION_BAL
WHERE STATION = 'JCK' AND SE_TIMESTAMP >= '2026-02-16 00:00:00' AND SE_TIMESTAMP < '2026-02-23 00:00:00'
ORDER BY SE_TIMESTAMP

SELECT DATE, HOUR, WITHDRAWMW, GENMW
FROM AW.dbo.ercotStationLoad
WHERE NMMSSTATIONCODE = 'JCK' AND DATE >= '2026-02-16' AND DATE < '2026-02-23'
ORDER BY DATE, HOUR
```

### kv-level mechanism (new — not previously documented for the TOTAL/non-PUN family)

JCK has exactly 2 kv rows, and **both are pure LOAD** in the TOTAL
(non-PUN) family — `TOTAL_EST_GENERATION_MW` = 0.0 at every one of the 168
hours, both kv levels (consistent with `jck_lonhill_generation.md` §2.1's
finding that JCK shows 0% nonzero-generation rows in this family):

| kV | avg `TOTAL_EST_LOAD_MW` | min | max |
|---:|---:|---:|---:|
| 138 | 9.05 | 7.11 | 11.70 |
| 345 | 18.86 | 11.67 | 26.75 |

Why 345 kV carries a second, larger LOAD reading on top of 138 kV's is not
established by this data — **INFERRED, not confirmed**: given JCK is a
genuine PUN with internal generation-load transfer that the `PUN_*` family
mirrors explicitly (138 kV PUN-load / 345 kV PUN-gen, both ≈839 MW, per
`jck_lonhill_generation.md` §3.2), it is plausible some residual of that
same internal complexity leaks into the non-PUN `TOTAL_*` columns at 345 kV
— but this was not traced to source and should not be treated as certain.

### Five variants vs `WithdrawMW` (ratio-of-sums, 168 hours)

| Variant | avg MW | ratio to WithdrawMW |
|---|---:|---:|
| (a) SUM_ALL_KV | 27.92 | 3.277 |
| (b) HIGHEST_KV (345 kV) | 18.86 | 2.214 |
| (c) LARGEST_MAGNITUDE (345 kV, same as b) | 18.86 | 2.214 |
| (d) SUM_EXCL_HIGHEST (138 kV alone) | 9.05 | 1.063 |
| (e) RAW_STATION_NET_LOAD_MW | 27.92 | 3.277 (identical to (a)) |
| `ercotStationLoad.WITHDRAWMW` | 8.52 | 1.000 |

(d)'s 1.06x looks tempting but **is a 2-kv-station coincidence, not
evidence for a general rule** — with only two kv rows, "exclude the
highest" is mechanically identical to "use the other row," and for any
2-row station one of the two rows will land closer to an external target by
construction. Q1's sweep already shows excluding/reweighting kv rows is not
a valid general rule: it would break STP, CPSES, and the ~26 other stations
where plain SUM (a) already reconciles to ~1.0. **Applying the Q1-correct
rule — (a)/(e), plain sum over kv — gives JCK's net as 27.92 MW average
(range 20.2–37.4 MW across the week).**

### Q2 answer

**Neither framed hypothesis is exactly right; here is the number.**

- The **839 MW "attribution-error" reading is dead**. That figure lives
  only in the `PUN_TOTAL_*` family (established fact, reconfirmed here —
  not requeried), a different, tautologically-mirrored quantity per
  `jck_lonhill_generation.md` §3.1. Under the correct grid-facing column,
  correctly aggregated, JCK's net is ~28 MW — about **30x smaller** than
  839 MW. The family is not claiming JCK is an 839 MW top-tier ERCOT load.
- The **"~8 MW, PUN reading matches exactly" claim is not reproduced**
  either. The family's own correctly-aggregated `TOTAL_NET_LOAD_MW`
  averages **27.92 MW**; `ercotStationLoad.WithdrawMW` averages **8.52 MW**
  over the identical 168 hours — a **3.28x** residual gap, same direction
  and similar magnitude to LON_HILL's unresolved Q1 gap. All 168 hours
  agree in sign (no sign-disagreement hours, unlike MGSES/DCSES above).
- **Directionally, the PUN reading wins decisively**: JCK is a tens-of-MW
  station, not a top-tier load, and both sources agree on sign and rough
  order of magnitude (single-digit-to-tens of MW, not hundreds). But
  **precisely, there is an unexplained ~3.3x residual** between the
  family's grid-facing figure and `ercotStationLoad` — of the same
  unresolved character as LON_HILL's Q1 gap (metering boundary / footprint
  difference — **INFERRED, not confirmed**). This does not overturn
  sdalvi's ruling that JCK is a genuine PUN and the family's estimate is
  "correct" (out of scope to relitigate here); it adds that "correct" and
  "reconciles to `ercotStationLoad` at 1.0x" are not the same claim.
- **Independent corroboration** (a different, concurrently-running agent's
  thread, not otherwise touched by this task — flagged as their number, not
  re-verified here): `load-forecast/src/pull_load_estimation.py`'s
  docstring states JCK's `TOTAL_EST_LOAD_MW` (grid-facing) is "~25 MW...
  weekly avg" vs `PUN_TOTAL_EST_LOAD_MW` "~800 MW weekly avg" gross
  internal — consistent with this test's independently-computed 27.92 MW
  (different week, different method).

---

## Files

- Script (scratchpad, not checked in): `kv_aggregation_test.py`
- Raw query CSVs (scratchpad, not checked in): `s0_kv_count.csv`,
  `s0_size.csv`, `s0_candidates.csv`, `s0_selected.csv`,
  `s1_lonhill_term_kv.csv`, `s1_lonhill_stationbal.csv`,
  `s1_lonhill_stationload.csv`, `s1_lonhill_variants.csv`, `s2_term.csv`,
  `s2_stbal.csv`, `s2_wsl.csv`, `s2_merged.csv`, `s2_summary.csv`,
  `s3_jck_term_kv.csv`, `s3_jck_stationbal.csv`, `s3_jck_stationload.csv`,
  `s3_jck_variants.csv`
  — all under
  `/tmp/claude-1000/-workspaces-scratch-workspace/42f42055-457d-4044-a2ff-deac470ca995/scratchpad/`.
