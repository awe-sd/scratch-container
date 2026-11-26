# Task 09 grading review (Opus gate, 2026-08-26)

Reviewer: Opus grading agent. Scope: the CORRECTED Task 09 deliverable
(`docs/task09_benchmark_findings.md`, `output/task09_injection_benchmark.csv`,
`output/task09_station_summary.csv`, `src/injection_benchmark.py`,
`src/pull_load_estimation.py`) against `tasks/09_injection_benchmark.md`.

**VERDICT: CONDITIONAL PASS — the CSVs pass and may be relied on; the findings
doc DOES NOT SHIP to sdalvi until items 1–6 in §6 are done.**

The data artifacts pass. Every headline number in the findings doc reproduces
exactly from the CSVs and from cached raw parquet — I re-derived them
independently and found no arithmetic fabrication anywhere. The net-basis
correction is right, and better-evidenced than the doc itself claims.

The **write-up does not pass as written**. Two outright factual errors (D4,
D5) in a document that already failed one gate, plus a framing defect that
presents a near-tautological agreement rate as validation (§2), plus a
worst-offenders section that omits its own top offender (D2). The final
recommendation ("yes for net injection by station") is correct, but almost
none of the reasoning the doc offers in support of it actually supports it.

---

## 1. The net basis — CONFIRMED CORRECT (implementer right, spec wrong)

`ercotStationLoad.WithdrawMW` **is already a net quantity.** The spec's
`net = WithdrawMW - GenMW` was a genuine bug; `net = WithdrawMW` is right.
Verified three independent ways, not taken on faith:

1. **Code/doc:** `src/organic_load.py:16-24` — "for generator-affiliated
   roster stations … `WithdrawMW` is a branch-flow-derived NET quantity (load
   minus generation) … not the station's own load draw."

2. **Reproduced from cache** (all 198 stations, 2026-01-01→2026-03-04,
   282,240 merged station-hours). At the 18,066 station-hours with
   `GenMW >= 5 MW` — the doc's exact denominator:

   | Quantity | I measured | Doc claims |
   |---|---|---|
   | median \|`WithdrawMW` − `TOTAL_NET_LOAD_MW`\| | **0.1652 MW** | 0.17 |
   | frac within 0.5 MW | **0.8163** | 0.82 |
   | median \|`WithdrawMW` − `GenMW` − `TOTAL_NET_LOAD_MW`\| (spec formula) | **78.49 MW** | 78.5 |
   | median \|`WithdrawMW` + `GenMW` − `TOTAL_EST_LOAD_MW`\| | **8.74 MW** | 8.7 |
   | median \|`WithdrawMW` − `TOTAL_EST_LOAD_MW`\| | **79.70 MW** | 79.7 |

   WHCCS2 @ 2026-01-27 00:00 reproduces exactly as printed: `TOTAL_EST_LOAD=0`,
   `TOTAL_EST_GENERATION=1142.776`, `TOTAL_NET=-1142.776`, `GenMW=1134.520`,
   `WithdrawMW=-1143.985`.

3. **A stronger, discriminating test the doc did not run.** If `WithdrawMW`
   were gross withdrawal it could never go materially negative. It does — and
   it does so *at stations where `GenMW` is NULL for the entire window*, so
   the generation being netted out is generation `GenMW` never measured:

   | Station | window hrs | GenMW NULL hrs | hrs `WithdrawMW` ≤ −1 | min `WithdrawMW` |
   |---|---:|---:|---:|---:|
   | BER | 1415 | 1415 | 1360 | **−184.57** |
   | BYP | 1440 | 1440 | 85 | **−199.42** |
   | WZRD_ESS | 1440 | 1440 | 93 | −151.12 |
   | DOW | 1440 | 1440 | 222 | −126.33 |
   | BLACKSPR | 1440 | 1440 | 194 | −120.09 |
   | LON_HILL | 1439 | 1439 | 275 | −77.99 |

   12 stations show ≥24 hours of material net injection with `GenMW` NULL
   throughout. This settles the basis question and simultaneously proves
   `GenMW` and `WithdrawMW` come from **different upstream pipelines** —
   which is why net reconciles to 0.17 MW while `W+G` vs load only reaches
   8.7 MW. Worth adding to the doc; it is the cleanest proof available.

**No residual doubt. The corrected direction is the right one.**

---

## 2. Independence — THE LOAD-BEARING DEFECT. The two sources share lineage.

**The tightness is not evidence of accuracy. It is evidence of a common
input.** Item 1 and item 2 are the same measurement read two ways.

The probative population is the **18,066 materially-generating station-hours**
(`GenMW >= 5 MW`) — the hours where two genuinely independent estimators
*would* diverge, because generation is being netted against load rather than
both sources reporting a quiet load:

```
median |WithdrawMW − TOTAL_NET_LOAD_MW| = 0.165 MW ;  81.6% within 0.50 MW
```

Across **all 282,240 merged station-hours** it is tighter still — median
**0.0125 MW (12.5 kW)**, 87.9% within 0.50 MW, 63.1% within 0.05 MW — though
that figure is partly carried by the ~73% of hours where both sources report
small quiet loads that would agree under almost any construction.

Two genuinely independent estimates of station net injection — different
metering, different estimator, different topology model — do not agree to
**0.165 MW at the median on generating hours**. That is not a measurement
comparison; it is two implementations of the same accounting identity over
the same input rows.

Three corroborating lines:

- **Documented provenance, both sides.** `ercotStationLoad` is, in sdalvi's
  own words, "imperfect, built from **branch flow data**"
  (`docs/large_load_research.md:13-14`, repeated at `docs/project_brief.md`
  data-inventory row: "Branch-flow-derived hourly station MW"). The
  LoadEstimation family carries `ERCOTLOADESTIMATION_AUDIT` — 496M rows of
  **per-branch flow detail** (`BRANCHID, BRANCHDEVICENAME, FROMSTATIONNAME,
  TOSTATIONNAME, FROMMW, TOMW, FLOW_KIND`, `docs/load_estimation_schema.md`
  §2). Both products are "sum the branch flows crossing the station
  boundary." Same accounting, same hourly SE snapshot.
- **The failure structure is bimodal, not noisy.** Per-station net-leg strict
  flagged rate across all 195 stations: **124 at exactly 0%**, 32 in (0,1%],
  6 in (1,5%], 6 in (5,20%], 15 in (20,50%], 7 in (50,90%], 5 above 90%.
  Independent measurements produce a continuous, magnitude-scaling error
  distribution. A near-empty middle with a hard mode at exactly zero is the
  signature of one shared input processed through two topology/mapping
  tables: identical where the mappings agree, structurally broken where they
  don't.
- **The disagreements are station-constant, not hour-varying.** JCK's hourly
  ratio over 1,416 material hours: median 3.034, q10 2.11, q90 3.98 — a
  persistent scaling offset, not scatter. The same station measured 3.28× in
  a different window by a separate investigation.

**Consequence for the deliverable.** "98.1% of comparable station-hours
agree" is close to tautological. It measures *reimplementation consistency* —
whether two branch-flow summations over the same SE snapshot land in the same
place — not whether either one is a correct estimate of physical station net
injection. Neither source validates the other; a systematic error in the
shared upstream (bad branch mapping, missing terminal, sign convention on a
transformer) is invisible to this benchmark **by construction**, because both
sides inherit it.

This does not make the family unusable — see §10. It makes the agreement rate
the wrong argument for using it, and the doc leads with exactly that argument
in its first bullet (`task09_benchmark_findings.md:17-24`).

---

## 3. Defects

### D1 — BLOCKING (disclosure, not method). The materiality filter is the negation of the blind-spot condition, and that is never disclosed.

`MATERIALITY_FLOOR_MW = 1.0` (`src/injection_benchmark.py:148`).
"Materially-loaded" = `max|WithdrawMW| >= 1 MW` over the window — a threshold
**on the ercotStationLoad side only**. The `station_load_blind_to_load`
statistic (§10 of the findings) is `max|WithdrawMW| < 1 MW` while term_bal
sees real MW — *the logical negation of the same threshold on the same
variable*. The crosstab from `task09_station_summary.csv` (leg=net) is exact:

```
station_load_blind_to_load   materially_loaded=False   materially_loaded=True
False                                  30                      155
True                                   10                        0
```

**All 10 blind-spot stations are excluded from the headline by construction.**
The doc reports the 98.1% agreement rate (§5) and the blind-spot finding (§10)
eleven pages apart and never notes they are complementary definitions.

What the filter removes is not trivia:

| | stations | comparable hrs | strict flagged | strict rate |
|---|---:|---:|---:|---:|
| Retained ("materially loaded") | 155 | 220,385 | 4,151 | **1.88%** |
| **Excluded** | 40 | 56,632 | 18,707 | **33.03%** |
| All | 195 | 277,017 | 22,858 | 8.25% |

Excluded stations include ATHEY (94.8% flagged; term_bal sees 56.6 MW,
ercotStationLoad 0.010 MW), HLJ (94.5%; 14.2 MW vs 0.027), DOLAN (88.2%),
BELCNTY (75.3%), RILEY (61.9%; 30.9 MW vs 0.025) — real load that
`ercotStationLoad` cannot see.

**To be fair to the implementer: a 1 MW materiality floor is a defensible
analytical choice, not a rigged one.** Almost any station-level benchmark
needs one, and the excluded MW is genuinely small — **1.03%** of summed
`max_abs_grid_facing_mw`. This is a disclosure defect, not a methodological
fraud, and it is the least severe of the blocking items.

**The sharper problem is the threshold's behaviour at the boundary.** 1 MW is
arbitrary enough that TINPD — reading 1.56 MW in `ercotStationLoad` against
123 MW in term_bal, i.e. a blind-spot station in everything but name — lands
*inside* the headline population and becomes its largest single source of
flags (D2), while ten materially identical stations land outside it. The
threshold is doing unprincipled work exactly where it matters most.

**Fix:** state the excluded MW share (1.03%) and the filter's complementarity
with the blind-spot statistic **in the same sentence as the 1.88% rate**, and
give the all-station rate equal billing. Also note that
`net_ratio_tb_over_sl` is NaN for all 40 excluded stations *and* for TINPD, so
"149 stations, median 1.001, IQR [0.998, 1.006]" is computed on the same
reduced population.

### D2 — BLOCKING. §11 "Worst offenders" names the wrong stations, and the top offender is absent.

Spec §6 requires "the worst offenders with a plausible cause for each." §11
(`task09_benchmark_findings.md:286-294`) names JCK, MCK, HCKSW, WTRML and
asserts "the remaining materially-loaded stations predominantly show 0%."
Actual top contributors to the 4,151 materially-loaded net-leg strict flags:

| Station | strict flags | share of 4,151 | flagged rate | max\|Withdraw\| | max\|tb net\| | in doc? |
|---|---:|---:|---:|---:|---:|---|
| **TINPD** | **1,398** | **33.7%** | **99.1%** | 1.56 MW | 123.0 MW | **no** |
| JCK | 1,390 | 33.5% | 96.9% | 16.7 | 37.4 | yes |
| **LON_HILL** | **457** | 11.0% | **31.8%** | 78.0 | 79.1 | only as a non-offender |
| **TRSES** | **432** | 10.4% | **30.1%** | 242.5 | 239.1 | **no** |
| **MARBFA** | **238** | 5.7% | **16.6%** | 20.3 | 20.2 | **no** |
| MCK | 30 | 0.7% | 2.1% | 6.2 | 350.2 | yes, as a headline outlier |

**TINPD is the single largest contributor and is never mentioned.** It is an
11th blind-spot station that squeaked past the 1 MW materiality floor at
1.56 MW: `ercotStationLoad` sees ≤1.56 MW while term_bal sees up to 123 MW,
99.1% of hours flagged. Its `net_ratio` is NaN, so it also escapes the §7
ratio statistic. It is doubly invisible in the write-up.

**LON_HILL is 31.8% flagged and materially loaded**, yet §7 presents it as
reassurance ("does not appear in this window's tail") — true of its *ratio*,
misleading about its *flagged rate*. **TRSES is a 242 MW station flagged 30%
of hours** — the largest genuinely-material disagreement in the sample, absent
from the doc.

**Fix:** replace §11 with the actual ranked top-N by strict flag count, each
with a stated cause or an explicit "cause not determined."

### D3 — BLOCKING (documentation). The PUN dispute: §3.1 is false, but §4 proves it wrong and draws a dangerous conclusion.

**Adjudication: the Task 09 grader's verdict is right; `jck_lonhill_generation.md`
§3.1's generalization is false. But `task09_benchmark_findings.md` §4's proof is
a non-sequitur and its practical advice is unsafe. Both need correction.**

Population evidence — bounded single-day Snowflake query, **all 5,575
stations / 133,800 station-hours** at 2026-02-20, kv-summed:

```
N_STATION_HOURS                                  133,800
PUN_TOTAL_LOAD == PUN_TOTAL_GEN  (the §3.1 claim)  5,950   = 4.4%
   ...of which PUN columns are non-zero               478   = 0.36%
PUN_TOTAL_* == TOTAL_*  (PUN cols are a copy)    130,414   = 97.5%
PUN_TOTAL_NET == TOTAL_NET                       130,414   = 97.5%
```

The `PUN_TOTAL_*` columns run in **two regimes**:
- **Copy regime (97.5%)** — no PUN component; `PUN_TOTAL_* ≡ TOTAL_*` exactly.
- **Mirror regime (0.36% non-trivially)** — a genuine PUN; gross load booked
  at one kv terminal and mirrored as generation at another, netting to ~0.
  `docs/jck_lonhill_generation.md` §3.2 shows the mechanism directly (JCK:
  138 kV `PUN_LOAD`=839.13/`PUN_GEN`=0; 345 kV `PUN_LOAD`=0/`PUN_GEN`=839.13).

Per-station confirmation from the cached term_bal parquet, Jan 1–Mar 4:

| Station | frac \|PUN_LOAD−PUN_GEN\|<1e-6 | frac PUN_NET==TOTAL_NET | regime |
|---|---:|---:|---|
| LON_HILL | **0.9917** | 0.0167 | mirror |
| JCK | **0.4500** | 0.5667 | **switches hour to hour** |
| MCK | 0.0000 | **1.0000** | copy |

**`jck_lonhill_generation.md` §3.1 is wrong.** Not merely "unjustified from
n=2" — it is falsified *on one of its own two stations* once the window
widens. §3.1's table reports JCK's `PUN_LOAD − PUN_GEN` as mean/min/max/std
all exactly 0.0; over Jan–Mar the identity holds on only 45% of JCK's hours.
The Feb 19–26 probe week was unrepresentative. Its "binding recommendation"
framing must be downgraded.

**But `task09_benchmark_findings.md:136-149` gets there by an invalid route.**
It refutes §3.1 with "net-leg `pun_to_grid_ratio` has median 1.00 across 193
stations, 182 of 193 above 0.5 — i.e. for most stations the PUN and
grid-facing net figures are close, not zero." That statistic is
`max|PUN_TOTAL_NET|/max|TOTAL_NET|` (`src/injection_benchmark.py:697-699`).
From the summary CSV: **179 of 193 are exactly 1.0** (bitwise; `(p==1.0).sum()`
= 179). They are 1.0 because the columns are *definitional copies* at non-PUN
stations, not because anything physical was measured. The statistic cannot
test the identity; it counts how many stations aren't PUNs. Right answer,
wrong proof — and the 11 stations at ratio < 1e-6 are precisely the mirror-regime
stations whose existence §4 is implicitly denying.

**§4's practical instruction is unsafe as written:** "Treat
`pun_value_term_bal`/`pun_to_grid_ratio` at face value per-station." At
mirror-regime stations these are a bookkeeping construct — JCK's
`PUN_TOTAL_EST_LOAD_MW` reaches **1,000.4 MW** at a station whose real net
never exceeds 37.4 MW. Taking that at face value is exactly the error
`jck_lonhill_generation.md` was right to warn about. §4 throws out the valid
warning along with the invalid generalization.

**Correct general rule, for `project_brief.md`:**
> `PUN_TOTAL_*` has two regimes. At ~97.5% of station-hours there is no PUN
> component and `PUN_TOTAL_* ≡ TOTAL_*` exactly (a copy — it carries no extra
> information). At genuine PUN stations it is a mirrored gross construct that
> nets to ~0 and can be tens of times the station's real net; some stations
> switch regime hour to hour (JCK: 45% mirror / 57% copy). Never read
> `PUN_TOTAL_EST_LOAD_MW`/`_GENERATION_MW` as physical MW, and never assume
> `PUN_TOTAL_NET_LOAD_MW` is zero. Use `TOTAL_NET_LOAD_MW` for net.

`docs/project_brief.md:58` currently carries the disputed claim marked
"⚠️ DISPUTED (under Opus adjudication)" pending this review — good practice.
It must now be replaced with the rule above. **Also fix, same line:** it still
reads "`BRANCH_MAPPING` **0 rows (still empty — no bus-level bridge)**" and
then contradicts itself later in the same cell with the corrected 7,544-row
SQL Server finding.

### D4 — BLOCKING (factual). The generation-leg pass rate is wrong by 9.6 pp, and is described backwards.

`task09_benchmark_findings.md:32-37`: "generation-leg agreement is weaker
(75.6% strict pass) and gross-load agreement is moderate (75.6% strict pass)."
The same number is given for two different legs. From
`task09_station_summary.csv`:

| Leg | comparable | strict flagged | strict rate | **strict pass** |
|---|---:|---:|---:|---:|
| load (gross) | 74,629 | 18,179 | 24.36% | **75.64%** ✓ |
| generation | 74,629 | 11,068 | 14.83% | **85.17%** ✗ doc says 75.6% |

**The denominators are identical (74,629 both legs, same 53 stations)** — both
legs are gated on `GenMW` being non-NULL, so the obvious objection ("different
populations explain the gap") is ruled out. The difference is entirely in the
numerator: 18,179 vs 11,068 strict flags.

The load number was duplicated into the generation cell. Generation is not
"weaker" than load — it is **9.5 pp stronger**. §5's table
(`:174-180`) then leaves the generation cell as a bare em-dash, "reported in
CSV" — so the doc asserts in its recommendation a figure it declines to state
in its results section, and the asserted figure is wrong.

### D5 — BLOCKING (factual). HCKSW/WTRML are not "100% flagged," and are not in the population the sentence places them in.

`task09_benchmark_findings.md:288-291` — "the documented HCKSW/WTRML
blind-spot cases (§10, both 100% flagged on net — correctly …)". Actual, from
the summary CSV, leg=net: **HCKSW 34.36%, WTRML 42.79%.** Both are
`materially_loaded_in_station_load = False`, so they are not members of the
materially-loaded set the surrounding sentence is enumerating. Two errors in
one clause.

### D6 — NON-BLOCKING but material. MCK's 0.30× is an outlier artifact, not a scaling difference; the doc's reading is backwards.

§7 presents MCK as a genuine tail case: "0.30x — term_bal reads ~1/3 of
`ercotStationLoad`." From the cached parquet, 1,416 merged hours:

```
median (TOTAL_NET_LOAD_MW − WithdrawMW) =  0.038 MW
q25 = 0.004 MW,  q75 = 0.247 MW
hours |diff| >= 5 MW: 25 of 1,416  (1.8%)
ratio-of-sums = 0.294
```

MCK is a ~5 MW station where the two sources agree to **38 kW at the median**.
The 0.30× ratio-of-sums is produced entirely by ~25 hours in which term_bal
reports `TOTAL_EST_GENERATION_MW` spiking to **350.19 MW** at a station whose
load never exceeds 6.9 MW. That is not a 3× scaling offset in the opposite
direction — it is a **spurious generation spike in term_bal**, i.e. a data
quality defect in the candidate source, and a far more interesting finding for
sdalvi than the one reported. It is also why MCK's strict flagged rate is only
2.1% while its ratio is 0.30 — an internal inconsistency the doc prints
without noticing (§7 vs the CSV).

Two consequences the doc should state: (a) `net_ratio_tb_over_sl` is a
ratio-of-sums and is outlier-dominated — it should be reported alongside the
median hourly ratio; (b) §7's "3× hypothesis" discussion is weakened on one
side and strengthened on the other — MCK's 0.30× is *not* a counter-example in
"the opposite direction" because it isn't a scaling factor at all, while JCK's
**median hourly** ratio is 3.034 (not the 2.90 ratio-of-sums the doc quotes),
which sits closer to exactly 3 than the doc's own number.

### D7 — NON-BLOCKING. "Strict" does not mean what the doc says it means: 72% of all-station strict net flags are sub-floor sign flips.

`:152-158` describes strict as "also clears the ≥5 MW absolute floor," and
justifies it as the number that stops "trivial-magnitude noise" inflating the
headline. But `sign` rows bypass the floor entirely
(`src/injection_benchmark.py:626,633` — spec-compliant, §4 requires sign flags
"regardless of magnitude"), and sign rows are then folded into strict:

| Population | strict total | of which `sign` | sign rows with \|diff\| < 5 MW | strict rate excl. sub-floor signs |
|---|---:|---:|---:|---:|
| All 195 stations | 22,858 | 18,138 | **16,446 (90.7%)** | 8.25% → **2.31%** |
| Materially loaded | 4,151 | 1,728 | 697 (40.3%) | 1.88% → **1.57%** |

13,511 of the all-station net sign flips are under **1 MW**. So the "All
stations 8.25%" figure in §5's table is inflated roughly 3.6× by exactly the
trivial-magnitude noise the doc says strict was designed to exclude. The
implementation follows the spec; the *description* of what strict means does
not match what it computes.

### D8 — NON-BLOCKING. Spec §4's floor-suppression count is computed but never reported.

Spec §4: "report how many rows the floor suppresses so the choice is auditable
and tunable." The number exists in the CSV as `flag_category == 'relative'`
but appears nowhere in the findings doc: **net 35,718 rows (61.0% of loose
flags), load 19,740 (52.1%), generation 21,856 (66.4%)**. Add to §5.

### D9 — NON-BLOCKING. Stale comment asserting the exact bug that caused the prior FAIL.

`src/injection_benchmark.py:598-601`, inside `classify_flags`: "…AND the net
leg (b=sl_net=WithdrawMW-GenMW, NULL whenever GenMW is…)". That is the
superseded formula. The code above it is correct
(`:571` `"net": ("TOTAL_NET_LOAD_MW", "WithdrawMW", …)`), but a comment
asserting the wrong basis — in the function whose basis caused the FAIL — is
more than cosmetic. Also `:552-555`'s claim that this comment describes is
right; only `:598-601` is stale.

### D10 — NON-BLOCKING. Precision theatre: "~220k", "~4,150", "~18,180".

§5 uses tildes where exact counts are one `groupby` away (220,385 / 4,151 /
18,179). It impedes exactly the verification this gate performs. Replace.

---

## 4. Items that PASS — verified, no action

- **NULL vs zero handling (item 4): correct.** `GenMW` is genuinely NaN in the
  cached parquet, never zero-filled (`src/pull_station_load.py` selects
  `GENMW` raw; raw window data has 207,239 NULL hours *and* 51,357 genuine
  `GenMW == 0` hours — the two are distinct). `compute_legs_long`
  (`:567`) never coalesces. `classify_flags` (`:607-609`) routes NULLs to
  `null_in_station_load` / `null_in_term_bal`, excluded from the flagged CSV
  and from every rate denominator, but carried in the summary as their own
  columns. Verified: gen-leg `n_null_in_station_load` = **202,388**, matching
  the doc's claim exactly; net-leg nulls = 0 (WithdrawMW always populated when
  the row exists). This is done properly and the doc's §3 statement is
  accurate.
- **Reproducibility (item 9): every claim checked reproduces.** 277,017
  comparable ✓; 22,858 strict ✓; 8.25% ✓; 1.88% (4,151/220,385) ✓; 146/155
  ≤1% ✓; 150/155 ≤5% ✓; median 0% / mean 1.878% ✓; net ratio n=149, median
  1.00085, IQR [0.99804, 1.00645], p90 1.0285 ✓; 2 outside [0.5,2.0] ✓;
  202,388/277,017 NULL ✓; NCL 1.6075% / non-NCL 2.1515% materially-loaded ✓;
  loose 11.08%→5.61% and 28.67%→7.99% ✓; namespace 5,680/5,699/5,660 =
  **99.648%** ✓; flagged CSV 129,647 rows, categories reconcile
  (77,314 relative + 22,529 relative+absolute + 29,576 sign + 228
  missing_in_term_bal) ✓; station list 197 = 110 non-NCL random + 85 NCL +
  2 non-NCL forced ✓. **No fabricated numbers found.**
- **Sample bias (item 8): handled correctly.** NCL and non-NCL rates are
  reported separately and reproduce. The blind-spot headline is explicitly
  drawn from the *unbiased* subset (7 of 10 hits from the random 110 = 6.4%),
  which is the right call and is stated. §10's sample-composition paragraph is
  the strongest reasoning in the document.
- **Hour alignment (item 7, spec §3.3): methodology is sound.** The
  implementer caught that the top-1-by-range candidate (TRSES) was
  noise-dominated at a 1.007 decisiveness ratio and would have picked the
  wrong offset; replaced it with a decisive-tests-only tally across the
  candidate pool (`find_alignment_offset`, `:389-461`). Offset 0, 97.4% of
  decisive tests on the full 5,627 pool. Correct, and correctly reported.
- **kv-summing:** SQL groups by `(STATION, SE_TIMESTAMP)` before return
  (`src/pull_load_estimation.py:175-186`) — no fan-out. Uses `TOTAL_*`, never
  the pipeline-zeroed plain `STATION_*` columns. Spec §2.1 and §3.1 satisfied.
- **`run_id`, `pun_score` NULL, bad intervals, no `SELECT *`, batched
  station-bounded queries:** all per spec. Bad intervals are excluded
  symmetrically from both sides post-merge (`:521-527`) — a subtle point the
  implementer got right and explained.
- **Bus-level (item 6 of spec §6): correct and correctly scoped.** Blocked on
  both platforms; `BRANCH_MAPPING` maps branch device → `(station, kv)`, never
  to `SswgBusNumber`. Independent of everything else.

---

## 5. My own answer to sdalvi's question

Stated independently of the deliverable's conclusion.

**Can the `ERCOTLOADESTIMATION_*` family replace `ercotStationLoad` for net
injection by station? — Yes, and it is the better source. But not for the
reason the benchmark gives.**

- **The agreement rate is not the argument.** The two sources are both
  branch-flow summations over the same hourly state-estimator snapshot. They
  agree to 12.5 kW at the median because they are computing the same thing
  from the same rows. That is a reimplementation check, not a validation, and
  it tells you nothing about whether either is right in absolute terms. Any
  error in the shared upstream is invisible to this test.
- **The real arguments for switching are structural, and they are strong:**
  (1) **coverage** — 99.6% namespace overlap, plus the family sees material
  load where `ercotStationLoad` reads zero at **7 of 110 stations (6.4%) in an
  unbiased random draw** (10 of 195 across the whole sample), with essentially
  no counterpart failure in the other direction (1 station, WBOSE). Note this
  rate is measured on 110 stations and should not be projected onto the
  5,680-station universe without a wider draw; (2) **an explicit
  load/generation/net decomposition**, where `ercotStationLoad` gives you
  `GenMW` NULL at 73% of station-hours and 14–29% of actual generators;
  (3) **`RAW_*` columns that survive the PUN zeroing** which silently guts the
  plain `STATION_*` columns; (4) **`BAD_INTERVALS`** as a maintained
  failed-interval reference instead of a hand-rolled threshold.
- **Frame the `GenMW` gap correctly.** It is an `ercotStationLoad`
  *limitation*, not a family limitation — the doc lists it as a caveat against
  the family, which is backwards. It is one of the better reasons to switch.
- **No for bus-level**, unconditionally and independently. Neither platform
  carries a bus identifier; the finest grain is `(station, kv)`. Getting to
  `SswgBusNumber` still requires the same external `ercotDataDictionary`
  crosswalk. Switching sources does not move this at all.
- **Two operational preconditions, both real:** the family stops at
  **2026-03-04** (vs `ercotStationLoad`'s 2026-06-15) — it is currently the
  *staler* source, and the SWE backfill has to land before production use;
  and the Snowflake/SQL Server copies are independently-computed
  near-duplicates (6,676 vs 6,729 rows at a matched instant, divergent
  `pun_score` and zeroing behaviour), so pick one platform and do not mix.
- **Carry a per-station exception list, don't assume uniform quality.** The
  disagreements are whole-station and structural, not hourly noise: TINPD,
  JCK, LON_HILL, TRSES, MARBFA account for ~94% of material-station flags.
  And the family has its own defects — MCK's spurious 350 MW generation spikes
  at a 5 MW station are in the candidate source, not the incumbent.
- **What would actually validate either source** (not in scope here, worth
  naming): reconcile station net injection against a genuinely independent
  quantity — settlement-metered load by load zone, DAM LDF-allocated load, or
  telemetered resource output from `ercotStationLoad`'s own generation feed.
  Until then, "the two branch-flow products agree" is the only claim the
  evidence supports.

---

## 6. Required before this reaches sdalvi

In severity order:

1. **§2 (independence)** — add a plain statement that both sources are
   branch-flow summations over the same SE snapshot, that the agreement rate
   therefore measures reimplementation consistency rather than accuracy, and
   that the case for the family rests on coverage and structure instead.
   Rewrite the opening recommendation bullets accordingly.
2. **D4** — generation leg is 85.17% strict pass, stronger than load, not
   weaker. Fill in §5's em-dash with the real number.
3. **D5** — HCKSW 34.36%, WTRML 42.79%, neither materially loaded.
4. **D2** — replace §11 with the true ranked offender list (TINPD first, at
   33.7% of all material-station flags).
5. **D3** — correct `docs/project_brief.md:58` to the two-regime rule; drop
   §4's `pun_to_grid_ratio` argument and its "face value" advice; downgrade
   `jck_lonhill_generation.md` §3.1 from a binding rule to a
   window-and-station-specific observation, noting it fails on JCK itself over
   a wider window; fix the self-contradicting `BRANCH_MAPPING` sentence.
6. **D1** — disclose the 1.03% excluded MW share and the materiality/blind-spot
   complementarity in the same sentence as the 1.88% rate; give the
   all-station rate equal billing.

D6–D10 should be fixed in the same pass but do not gate.
