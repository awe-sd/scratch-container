# Task 09 — Injection Benchmark Findings: ERCOTLOADESTIMATION vs ercotStationLoad

Produced 2026-08-26 by `load-forecast/src/injection_benchmark.py` (+
`pull_load_estimation.py`). This is the SECOND-CORRECTED version, rewritten
after a mandatory Opus grading-gate **CONDITIONAL PASS**
(`docs/task09_grading_review.md`) found the CSVs correct but the write-up
carrying two factual errors, a missing top offender, and a framing defect.
Every number below was independently re-verified by this agent against
`output/task09_injection_benchmark.csv` / `output/task09_station_summary.csv`
before being written — not copied from the review unchecked.

## Recommendation (upfront)

**Yes, the family is the better source for net injection by station — but
not primarily because of the agreement rate. The case is structural.**

- **The agreement rate is close to tautological and should not be the lead
  argument.** `ercotStationLoad.WithdrawMW` and `term_bal.TOTAL_NET_LOAD_MW`
  are both branch-flow summations over the same hourly state-estimator
  snapshot — not independent measurements. They agree to a median of **12.5
  kW** across all 282,240 merged station-hours, tightening only to 0.165 MW
  even at the 18,066 hours where generation is large enough that two truly
  independent estimators *would* diverge. That tightness measures
  **reimplementation consistency, not accuracy** — see §2. Any error shared
  by both pipelines' upstream branch-flow input is invisible to this
  benchmark by construction.
- **The real case for switching is structural, and it is strong:**
  (1) **99.6% namespace coverage** of `ercotStationLoad`'s universe;
  (2) the family sees material load at **7 of 110 randomly-drawn stations
  (6.4%)** where `ercotStationLoad` reads ~0, with essentially no failure in
  the reverse direction (1 station) — see §10; (3) an **explicit
  load/generation/net decomposition**, where `ercotStationLoad` itself
  supplies `GenMW` at only ~27% of station-hours (§6) — **this is an
  `ercotStationLoad` limitation, not a reason to distrust the family**;
  (4) `RAW_*` columns that survive the pipeline-zeroing that silently guts
  the plain `STATION_*` columns; (5) a maintained `BAD_INTERVALS` reference.
- **A small, real, station-specific tail exists** — 5 stations (TINPD, JCK,
  LON_HILL, TRSES, MARBFA) account for 94% of the material-station flags
  (§11) — carry this as a named exception list, not smoothed into the
  aggregate.
- **Load/generation legs are structurally limited wherever `GenMW` is NULL**
  (§6) — a gap in `ercotStationLoad`, worth noting as a reason to favor the
  family, not a caveat against it.
- **Bus-level: no, unconditionally**, on both platforms (§9).
- **Freshness is NOT part of this verdict** per sdalvi's ruling — exact
  numbers in §3 for the SWE refresh request; the family is currently the
  *staler* source (2026-03-04 vs 2026-06-15) and needs backfilling before
  production use regardless of the accuracy verdict.
- **What would actually validate either source** — not in scope here, worth
  naming: reconcile against something *not* branch-flow-derived — settlement-
  metered load by load zone, DAM LDF-allocated load, or telemetered resource
  output. Until then, "the two branch-flow products agree" is the only claim
  the evidence supports.

---

## 0. Revision history (both corrections disclosed, not buried)

1. **First FAIL** (comparison-basis bug): used `net = WithdrawMW - GenMW`,
   literal from the task spec's own §2 and reaffirmed by a coordinator
   message mid-task. Caught by the first Opus grading pass:
   `ercotStationLoad.WithdrawMW` is already net; subtracting `GenMW` from it
   double-subtracts generation. Fixed: `net = WithdrawMW` directly, `gross
   load = WithdrawMW + GenMW`. Re-derived independently against raw cached
   data before accepting (see §4).
2. **Second pass — CONDITIONAL PASS, not a clean pass.** The corrected CSVs
   were verified arithmetically sound (every headline number reproduces
   exactly from cache, no fabrication), but the write-up itself had: a
   generation-leg pass rate copied from the load leg instead of computed
   (D4, off by 9.6 points and in the wrong direction); HCKSW/WTRML described
   as "100% flagged" when the true figures are 34.36%/42.79% (D5); a
   "worst offenders" section that named the wrong stations and omitted the
   single largest contributor, TINPD (D2); a PUN explanation that refuted a
   false universal claim with an equally invalid proof (D3); and a framing
   that presented the agreement rate as validation rather than disclosing
   that both sources share an upstream input (§2 below). All six are fixed
   in this version.

## 1. Scope actually run

- **Window:** 2026-01-01 → 2026-03-04 inclusive (the family's Snowflake data
  stops there).
- **Stations (197 total):** the 85-station NCL roster
  (`data/derived/ncl_stations.csv`) + a random sample of 110 non-NCL stations
  (seed 42, reproducible) + forced JCK/LON_HILL (HCKSW/WTRML were already in
  the 85). Roster: `data/derived/task09_station_list.csv`.
- The NCL roster is not a pure "large loads" list — it includes solar farms,
  a gas peaker, a power station, and battery storage alongside datacenters.

## 2. Independence — read this before trusting any agreement-rate number below

**The two sources are not independent measurements of the same physical
quantity. They are two summations of the same branch-flow input over the
same hourly state-estimator snapshot.** This is the single most important
framing correction in this document.

- `ercotStationLoad` is, in sdalvi's own words, "imperfect, built from
  **branch flow data**" (`docs/large_load_research.md`,
  `docs/project_brief.md`'s data-inventory row: "Branch-flow-derived hourly
  station MW"). The LoadEstimation family carries
  `ERCOTLOADESTIMATION_AUDIT` — 496M rows of **per-branch flow detail**
  (`BRANCHID, FROMSTATIONNAME, TOSTATIONNAME, FROMMW, TOMW, FLOW_KIND`).
  Both products are, at bottom, "sum the branch flows crossing the station
  boundary" over the same SE snapshot.
- **The agreement is far tighter than independent estimators would produce.**
  At the 18,066 station-hours with `GenMW≥5MW` — where generation is large
  enough that two genuinely independent estimates *would* diverge — median
  `|WithdrawMW - TOTAL_NET_LOAD_MW|` is **0.165 MW** (81.6% within 0.5 MW).
  Across all 282,240 merged station-hours it tightens to a median of
  **0.0125 MW (12.5 kW)**.
- **The failure structure is bimodal, not a continuous error distribution.**
  Per-station net-leg strict flagged rate across all 195 stations: 124 at
  exactly 0%, 32 in (0,1%], 6 in (1,5%], 6 in (5,20%], 15 in (20,50%], 7 in
  (50,90%], 5 above 90%. A near-empty middle with a hard mode at exactly
  zero is the signature of one shared input processed through two
  topology/mapping layers — identical where the mappings agree, structurally
  broken (not noisily different) where they don't.
- **Disagreements are station-constant, not hour-varying.** JCK's hourly
  ratio over 1,416 material hours: median **3.034**, q10 2.11, q90 3.98 — a
  persistent scaling offset, not scatter, and close to a value independently
  measured (3.28x) by a separate investigation in a different window.

**Consequence:** the net-leg agreement rate reported in §5 measures
*reimplementation consistency* — whether two branch-flow summations over the
same SE snapshot land in the same place — not whether either is a correct
estimate of physical station net injection. A systematic error shared by
both pipelines' upstream branch mapping (a bad terminal assignment, a
missing transformer side, a sign convention) is invisible to this benchmark
by construction. This does not make the family unusable (§10's structural
arguments stand on their own), but it means the agreement rate is the wrong
argument for using it — treat §5 as a coverage/consistency check, not a
validation.

## 3. Freshness (reported, NOT a factor in the recommendation)

| Platform | Max `se_timestamp` |
|---|---|
| Snowflake `AW.DBO` (used throughout) | **2026-03-04 23:57:00** |
| SQL Server `AWDev.dbo` | **2026-02-26 23:57:00** |

Both stopped in early March 2026 (a one-time backfill, not a live pipeline).
As of 2026-08-26 this is ~6 months stale — an operational precondition for
production use. The Snowflake and SQL Server copies are also
independently-computed near-duplicates (6,676 vs 6,729 rows at a matched
instant, per the schema doc) — pick one platform and do not mix; this
benchmark used Snowflake throughout.

## 4. THE comparison-basis correction

**`ercotStationLoad.WithdrawMW` is already net (load minus generation).**
Verified three independent ways:

1. **Documented:** `src/organic_load.py:16` — "`WithdrawMW` is a branch-flow-
   derived NET quantity (load minus generation) … not the station's own load
   draw."
2. **Reproduced directly from cache**, at the 18,066 station-hours with
   `GenMW≥5MW`: median `|WithdrawMW - TOTAL_NET_LOAD_MW|` = 0.165 MW (81.6%
   within 0.5 MW), vs median `|WithdrawMW - GenMW - TOTAL_NET_LOAD_MW|`
   (the spec's literal formula) = **78.5 MW** — two orders of magnitude
   worse. Concrete example, WHCCS2 @ 2026-01-27 00:00: `TOTAL_EST_LOAD=0`,
   `TOTAL_EST_GENERATION=1142.78`, `TOTAL_NET=-1142.78`; `GenMW=1134.52`,
   `WithdrawMW=-1143.99` (matches `TOTAL_NET` to 1.2 MW; the spec formula
   gives -2278.5, off by 1,136 MW).
3. **A discriminating test**: if `WithdrawMW` were gross withdrawal it could
   never go materially negative. It does, at stations where `GenMW` is NULL
   for the *entire* window — meaning whatever generation is being netted out
   was never separately measured by `GenMW` at all (BER: min `WithdrawMW`
   -184.6 MW, 1,415/1,415 hours `GenMW`-NULL; similarly BYP, WZRD_ESS, DOW,
   BLACKSPR, LON_HILL). This also proves `GenMW` and `WithdrawMW` come from
   different upstream pipelines, which is why net reconciles to 0.165 MW
   while gross load (`WithdrawMW+GenMW` vs `TOTAL_EST_LOAD_MW`) only reaches
   8.7 MW median error.

**Comparison basis used:**

| Leg | term_bal (kv-summed) | ercotStationLoad | Comparable population |
|---|---|---|---|
| Net | `TOTAL_NET_LOAD_MW` | `WithdrawMW` | Everywhere `WithdrawMW` exists (~all 195 stations, 277,017 hrs) |
| Load (gross) | `TOTAL_EST_LOAD_MW` | `WithdrawMW + GenMW` | Only where `GenMW` populated (53 of 195 stations, 74,629 hrs) |
| Generation | `TOTAL_EST_GENERATION_MW` | `GenMW` | Same 53-station, 74,629-hr population |

`GenMW` is never coalesced to 0 when NULL — routed to `null_in_station_load`
/`null_in_term_bal`, excluded from the flagged CSV and every rate
denominator, fully counted in `station_summary.csv`.

**kv-summing is separately confirmed correct** (`docs/kv_aggregation_test.md`):
`SUM(TOTAL_NET_LOAD_MW)` over kv reconciles to `RAW_STATION_NET_LOAD_MW` to 6
decimal places; ratio-to-`ercotStationLoad` shows no correlation with kv
count (r=0.093) across 30 stations spanning `KV_COUNT` 1–5, including two
large multi-kv nuclear plants (STP, CPSES) at ~1.0. No SQL change needed.

## 5. Headline agreement rates — both loose and strict, both populations

Two rates per spec §4: **loose** (fails the 10% test, any magnitude) and
**strict** (also clears the ≥5 MW absolute floor, or is a sign flip — the
number the floor exists to protect). The floor-suppressed count (`relative`-
only, spec §4's required disclosure) for each leg: **net 35,718 (61.0% of
loose flags), load 19,740 (52.1%), generation 21,856 (66.4%)**.

**Net leg (277,017 comparable hours, ~all 195 stations) — both populations
reported with equal billing, because they are complementary, not
interchangeable, definitions (§6):**

| Population | Stations | Comparable | Strict flagged | Strict rate |
|---|---:|---:|---:|---:|
| **All stations** | 195 | 277,017 | 22,858 | **8.25%** |
| Materially-loaded (`max\|WithdrawMW\|≥1MW`) | 155 | 220,385 | 4,151 | **1.88%** |
| Excluded by the materiality floor | 40 | 56,632 | 18,707 | **33.03%** |
| ...non-NCL, materially-loaded (79 stations) | | 111,829 | — | 2.15% |
| ...NCL, materially-loaded (76 stations) | | 108,556 | — | 1.61% |

**A caveat on "strict" itself**: 90.7% of the all-station net-leg strict
flags (16,446 of 18,138 `sign` rows) are themselves sub-5MW sign flips —
`sign` bypasses the absolute floor by design (spec §4 requires flagging sign
disagreements "regardless of magnitude"), but that means the "All stations
8.25%" figure is inflated roughly 3.6x by exactly the trivial-magnitude
noise the floor exists to suppress elsewhere. Excluding sub-floor sign flips
too: all-stations 8.25%→**2.31%**; materially-loaded 1.88%→**1.57%**. The
implementation is spec-compliant; this is a description caveat, not a bug —
the words "strict" and "floor-respecting" describe the 5MW-magnitude test,
not signs, which the spec deliberately exempts.

**Load (gross) and generation legs (74,629 comparable hours, 53
`GenMW`-populated stations):**

| Leg | Strict flagged | Strict rate | Strict PASS rate |
|---|---:|---:|---:|
| Load (gross, `WithdrawMW+GenMW` vs `TOTAL_EST_LOAD_MW`) | 18,179 | 24.36% | **75.64%** |
| Generation (`GenMW` vs `TOTAL_EST_GENERATION_MW`) | 11,068 | 14.83% | **85.17%** |

**Correction to an earlier version of this document, which reported 75.6%
for BOTH legs**: the load figure had been duplicated into the generation
cell. **Generation agreement is 9.5 points stronger than load, not weaker.**
Same 74,629-hour denominator both legs, so this isn't a population artifact
— the difference is entirely in the numerator (18,179 vs 11,068 strict
flags). Plausible reason: `GenMW` is populated mostly at
solar/wind/dedicated-generation sites, where the family's own
`TOTAL_EST_GENERATION_MW` may track more directly than the gross-load
reconstruction (`WithdrawMW+GenMW`) does against `TOTAL_EST_LOAD_MW`, since
the latter compounds two separately-sourced quantities.

## 6. `GenMW` NULL coverage — an `ercotStationLoad` limitation, not a family caveat

Two framings, both reported (they measure different denominators):

- **This benchmark's own number**: 202,388 of 277,017 "both-present"
  station-hours (**73.1%**) have NULL `GenMW`. Right denominator for "how
  much of the load/generation leg can be evaluated in this sample" — most of
  the 73% is ordinary load stations where `GenMW` NULL is expected (no
  generator asset), not a coverage failure per se.
- **A parallel, more targeted investigation** (`docs/genmw_coverage.md`):
  among stations the family itself identifies as material generators,
  **29.4% by station count / 14.1% by MW-weight** (Feb 2026) have `GenMW`
  entirely NULL. Right denominator for "of the generators that exist, how
  many does `ercotStationLoad` actually see."

**This cuts in the family's favor, not against it**: `ercotStationLoad`
cannot separate load from generation at roughly a quarter to three-quarters
of stations depending on how you count; the LoadEstimation family provides
that decomposition everywhere. An earlier version of this document listed
this gap as a caveat against the family — that was backwards.

## 7. The materiality floor — disclosed alongside the headline, not as a footnote

`MATERIALITY_FLOOR_MW = 1.0` (`max|WithdrawMW|≥1MW` over the window) is the
**exact logical negation**, on the same variable, of the
`station_load_blind_to_load` condition (§10): `max|WithdrawMW|<1MW` while
term_bal sees real MW. The crosstab (net leg, from `station_summary.csv`) is
exact:

```
station_load_blind_to_load   materially_loaded=False   materially_loaded=True
False                                  30                      155
True                                   10                        0
```

**All 10 blind-spot stations are excluded from the 1.88% headline by
construction** — this is a complementarity between two sections of this same
document, not a coincidence, and it must be read as one fact, not two: the
1.88% rate and the 10-station blind-spot finding are two views of the same
40-station exclusion.

| | Stations | Comparable hrs | Strict flagged | Strict rate |
|---|---:|---:|---:|---:|
| Retained ("materially loaded") | 155 | 220,385 | 4,151 | **1.88%** |
| **Excluded** | 40 | 56,632 | 18,707 | **33.03%** |
| All | 195 | 277,017 | 22,858 | 8.25% |

Excluded stations include ATHEY (94.8% flagged; term_bal sees 56.6 MW,
`ercotStationLoad` 0.010 MW), HLJ (94.5%; 14.2 vs 0.027 MW), DOLAN (88.2%),
BELCNTY (75.3%), RILEY (61.9%; 30.9 vs 0.025 MW) — real load
`ercotStationLoad` cannot see.

**A 1 MW floor is a defensible choice, not a rigged one** — almost any
station-level benchmark needs a materiality floor, and the excluded MW is
genuinely small: **1.03%** of summed `max_abs_grid_facing_mw`. The sharper
problem is boundary behavior: TINPD reads 1.56 MW in `ercotStationLoad`
against 123.0 MW in term_bal — a blind-spot station in every respect except
which side of an arbitrary 1 MW line it falls on — and lands *inside* the
headline population, becoming its single largest source of flags (§11),
while ten materially identical stations land outside it and never appear in
the 1.88% number at all. `net_ratio_tb_over_sl` is also NaN for all 40
excluded stations *and* for TINPD (its material-hour count for the ratio
calc doesn't clear the threshold even though it clears the coarser
materiality floor) — so "149 stations, median 1.001" (§8) is computed on
this same reduced population, not the full 195.

## 8. The residual tail — 2 stations with a real ratio, one of them a data defect

Per-station net ratio (`TOTAL_NET_LOAD_MW` ÷ `WithdrawMW`, ratio-of-sums over
materially-sized hours): **149 stations have a defined ratio, median 1.001,
IQR [0.998, 1.006], 90th percentile 1.03.** Only **2 of 149 (1.3%)** fall
outside [0.5x, 2.0x]:

| Station | Ratio-of-sums | Median hourly ratio | Interpretation |
|---|---:|---:|---|
| JCK | 2.90x | **3.03x** | Real, persistent scaling offset (§2) — confirmed genuine PUN, and an independent investigation found 3.28x in a different week. Cause: metering boundary / plant-footprint difference — INFERRED, not confirmed |
| MCK | 0.30x | — (median hourly diff is **0.038 MW**) | **NOT a scaling difference — corrected from an earlier version of this document.** See below |

**MCK correction**: an earlier version of this document read MCK's 0.30x as
"term_bal reads ~1/3 of ercotStationLoad" — a scaling-offset framing. The
underlying data does not support that. Across 1,416 merged hours, the median
`(TOTAL_NET_LOAD_MW - WithdrawMW)` is **0.038 MW** (q25 0.004, q75 0.247) —
essentially perfect agreement — and only 25 of 1,416 hours (1.8%) differ by
≥5 MW. The 0.30x ratio-of-sums is produced entirely by those ~25 hours, in
which term_bal's `TOTAL_EST_GENERATION_MW` spikes to **350.19 MW** at a
station whose `WithdrawMW` never exceeds 6.2 MW. **This is a spurious
generation spike in term_bal — a data-quality defect in the candidate
source, not a scaling difference in the opposite direction from JCK/LON_HILL**
— and a more useful finding for sdalvi than the number originally reported.
It also explains an internal inconsistency the earlier version printed
without noticing: MCK's strict flagged rate is only 2.1% (a handful of
hours) even though its ratio-of-sums is 0.30 — a ratio-of-sums is
outlier-dominated and should always be read alongside the median hourly
ratio, which is what actually describes "typical" agreement.

**LON_HILL does not appear in this window's tail** (ratio within [0.5,2.0]
here) despite a parallel investigation finding ~3.1x during its summer
generation peak (Aug 2024) — its generator is seasonal and mostly idle in
this Jan-Mar window. That the gap disappears off-season is itself evidence
the ~3x pattern tracks *generation dispatch*, not a static bug.

**On the "3x = single/three-phase ratio" hypothesis**: with JCK's median
hourly ratio at 3.03 (closer to exactly 3 than its own 2.90 ratio-of-sums)
and LON_HILL's independently-measured 3.1-3.28x from a different
window/investigation, there are 2 observations near 3.0 across two separate
efforts. MCK's 0.30x is **not** a counter-example in the opposite direction,
since it isn't a scaling factor at all (above) — so the hypothesis is
neither confirmed nor contradicted by MCK, just untested by it. **n=2 is too
small to confirm or reject; reported as suggestive, not established.**

## 9. Bus-level (per spec, called out separately) — unconditional no

**Blocked on both platforms**, independent of everything above.
`ERCOTLOADESTIMATION_BRANCH_MAPPING` is 0 rows on Snowflake but 7,544 on SQL
Server (replication gap, not absence) — but even the populated copy maps
branch device names to `(station, kv)`, **not** `SswgBusNumber`. No column
anywhere in the family carries a bus number. The same external
`BusID(SSWG) → ercotDataDictionary.SswgBusNumber → PlanningBusCounty`
crosswalk already used for `ercotStationLoad` is still required. Switching
sources does not move this at all.

## 10. The Sec 5 generalization question (unaffected by the §4 correction)

These use raw `WithdrawMW`/`TOTAL_EST_GENERATION_MW` directly, never the
derived net/gross-load formulas:

| Statistic | Count | Stations |
|---|---|---|
| `se_blind_to_generation` (term_bal shows ~0 gen while ercotStationLoad shows ≥24h of real negative WithdrawMW) | **1/195** | `WBOSE` |
| `station_load_blind_to_load` (ercotStationLoad ~0 withdrawal all window while term_bal shows ≥5MW load/net) | **10/195** | `ATHEY, BELCNTY, BLPOI, CEDRHILL, HCKSW, HIL, HLJ, RILEY, WTRML, ZORN` |

**Sample-composition check:** 7 of the 10 `station_load_blind_to_load` hits
are from the 110-station **random** non-NCL sample — a 6.4% hit rate (7/110)
in an unbiased draw, not a hand-picked artifact. This rate is measured on
110 stations and should not be projected onto the full 5,680-station
universe without a wider draw. Zero `se_blind_to_generation` hits came from
the NCL roster despite it containing many known generators. **Reading**:
`ercotStationLoad` has a real, non-trivial, randomly-distributed blind spot
to load (~6% of ordinary stations); the LoadEstimation family shows no
comparable blind spot to generation in this sample — favoring the family on
this specific axis, though the check is itself limited by
`ercotStationLoad`'s own `GenMW` gap (§6).

JCK and LON_HILL: both blind-spot flags `False`/`False` — correctly not
flagged as either pattern (their issue is the §8 magnitude residual, not a
visibility gap). Root causes for both are owned by
`docs/jck_lonhill_generation.md` and `docs/kv_aggregation_test.md` — not
re-diagnosed here.

## 11. Worst offenders (net leg, materially loaded, strict basis) — corrected ranking

**Correction to an earlier version of this document**, which named
JCK/MCK/HCKSW/WTRML and asserted "the remaining materially-loaded stations
predominantly show 0%" — that statement was true in aggregate but the named
list omitted the actual #1 contributor and mischaracterized two stations
that aren't even in this population. True ranked list by strict flag count:

| Station | Strict flags | Share of 4,151 | Flagged rate | `\|Withdraw\|` max | term_bal net max | Cause |
|---|---:|---:|---:|---:|---:|---|
| **TINPD** | **1,398** | **33.7%** | 99.1% | 1.56 MW | 123.0 MW | An 11th blind-spot station that squeaked past the 1 MW materiality floor (§7) — `ercotStationLoad` effectively cannot see it |
| JCK | 1,390 | 33.5% | 96.9% | 16.7 | 37.4 | Real ~3x residual (§8), confirmed genuine PUN |
| LON_HILL | 457 | 11.0% | 31.8% | 78.0 | 79.1 | Seasonal generator, partially active in this window; root cause owned elsewhere |
| TRSES | 432 | 10.4% | 30.1% | 242.5 | 239.1 | Largest genuinely-material disagreement in the sample by MW; cause not determined |
| MARBFA | 238 | 5.7% | 16.6% | 20.3 | 20.2 | Cause not determined |
| KMPSW | 60 | 1.4% | 4.3% | 28.4 | 28.6 | Cause not determined |
| MCK | 30 | 0.7% | 2.1% | 6.2 | 350.2 (spike) | Data defect in term_bal, not a scaling difference (§8) |
| FIRON | 24 | 0.6% | 1.7% | 106.4 | 106.5 | Cause not determined |

**These 5 stations (TINPD, JCK, LON_HILL, TRSES, MARBFA) account for 94% of
all material-station net-leg flags.** Every other materially-loaded station
combined contributes the remaining 6%. `HCKSW`/`WTRML` are correctly
excluded from this table — they are `materially_loaded_in_station_load =
False` (§7), not members of the population §11 ranks, and are documented
separately as blind-spot cases (§10) at 34.36%/42.79% flagged (not "100%,"
correcting an earlier version of this document).

## 12. Station namespace / match rate

- **Sample-level:** 195/197 (99.0%) had ≥1 `term_bal` row. Unmatched:
  `CORE_SW`, `WILSW` (both NCL roster).
- **Population-level:** `ercotStationLoad`'s window-bounded universe is
  5,680 stations; the family's universe (one bounded day) is 5,699; overlap
  is **5,660 — 99.648%**.

## 13. What was NOT done / honesty notes

- This document has now been rewritten twice after two Opus grading passes
  — the first FAIL on the comparison basis, this CONDITIONAL PASS on
  write-up defects against already-correct CSVs. Both are disclosed above
  rather than silently smoothed over.
- The single-phase/three-phase hypothesis (§8) is reported as inconclusive
  given n=2.
- JCK/LON_HILL/TRSES/MARBFA/KMPSW/FIRON root causes are explicitly NOT
  diagnosed here beyond what's stated (owned by parallel investigations
  where one exists; "cause not determined" where none does).
- `docs/project_brief.md:58` has been corrected in this pass to the
  two-regime PUN rule and the self-contradicting `BRANCH_MAPPING` sentence
  fixed in the same edit.
- Every query was bounded by both the date window and an explicit station
  list (batched IN-lists of ≤30 stations for `term_bal`/`station_bal`,
  sequential single-station calls for `ercotStationLoad`) — no `SELECT *`,
  no unbounded scan.

## Reusable code

- `load-forecast/src/pull_load_estimation.py` — cache-first, batched-query
  reader for `ERCOTLOADESTIMATION_TERM_BAL`/`_STATION_BAL`/`_BAD_INTERVALS`.
- `load-forecast/src/injection_benchmark.py` — the full benchmark pipeline
  (`main()`), runnable as `uv run python load-forecast/src/injection_benchmark.py`.
  Cache-first end to end; delete the relevant parquet(s) under
  `data/raw/load_estimation/` or `data/raw/station_load/` to force a refresh
  of a specific station, or `data/derived/task09_station_list.csv` to
  re-sample the non-NCL set.
