# Task 08-X — Probabilistic Size Index: Minimum Viable Experiment

**Status:** SPEC — first scored run completed 2026-08-16 (see training_log)
**Written:** 2026-08-15 (relayed from planning session with sdalvi; saved to
the repo verbatim 2026-08-16)
**Repo:** `load-forecast` — read `CLAUDE.md` first; all its rules are binding and
override anything here if in conflict.
**Runs in:** the existing 8 GiB container. No big-compute machine. No production
retrain. Runtime target: minutes.

---

## 0. Context — why this task exists (read before coding)

The rule-sweep (training_log round 4) proved that **no history-only point
extrapolation rule gets NCENT growth right** at wall-2024 (production ols3:
−3.68 pp on the sweep basis / −3.13 pp on the validate basis — always name the
basis). Task 07 proved the miss is **not explained by confirmed large loads**
(NCENT confirmed-NCL share is ~0.13%→0.79%; subtracting it made 3/3 backtest
folds worse).

Decision (sdalvi, 2026-08-15): **stop chasing a point forecast for growth.
Pivot the size index to a probability distribution over forward paths.** The
shape model is untouched — it passes everywhere. All new uncertainty lives in
the size-index forward rule only.

This task is the cheap viability test. It either promotes the probabilistic
approach, kills it, or routes to a defined iteration — per pre-registered
criteria in §7. Do not tune past the criteria.

**Scope rulings already made:**
- Historical NCL attribution (Task 07 organic-series path) is **abandoned as a
  production path**. The 18 UNKNOWN PUN stations no longer block anything.
- The sdalvi tracking sheet (`data/derived/large_loads_sites.csv`) is now IN
  scope as a **forward-only jump prior** (this reverses the Task 07 "forward
  additions OUT" ruling — re-confirmed for this task).
- History stays TOTAL load. No subtraction anywhere in this task.
- Zones: NCENT, COAST, SCENT only.

---

## 1. What gets built

Three components, one experiment harness:

1. **Monthly canonical size index** (new fitting grain — the key enabler).
2. **Model P: LLT + jumps** — local linear trend state-space model on the
   monthly index, simulated forward, plus a discrete large-load jump layer
   drawn from the tracking sheet.
3. **Baselines B0, B1, B2** (B2 is data-dependent, see §5; it may end in
   NEEDS_CONTEXT — that is an acceptable outcome for B2 only).
4. **Probabilistic backtest harness** scoring P/B0/B1(/B2) on the existing
   rolling-origin walls with truth values from the existing
   validate/backtest basis.

Nothing else changes. `scenario.py`, `shape_model.py`, `train_all.py`,
`validate.py`, `backtest.py` are **read-only** for this task.

---

## 2. New files

| File | Purpose |
|---|---|
| `src/size_index_monthly.py` | Fit monthly canonical size index per zone per wall |
| `src/prob_size.py` | LLT fit + forward path simulation + jump layer |
| `scripts/experiment_prob_size.py` | Orchestrates folds, baselines, metrics, artifacts |
| `output/task08x_folds.csv` | Fold-level scorecard (schema §6) |
| `output/task08x_samples.parquet` | Full sample paths (schema §6) |
| `docs/training_log.md` | TWO new entries: pre-registration entry BEFORE the run, results entry after (see §7) |

Deliverables live in the repo. Never hosted artifacts.

---

## 3. Component A — monthly canonical size index

`src/size_index_monthly.py`

**Why:** the annual index gives ~6–10 obs/zone — too thin to estimate a
stochastic-slope variance. Monthly grain gives ~100–130 obs/zone.

**Spec — reuse `src/size_index.py` internals wherever possible:**
- Same WLS on daily energy, but replace year fixed effects with
  **year-month fixed effects** (one FE per calendar year-month). Keep the
  piecewise-linear daily temp (knots 55/65/75°F) and weekday/holiday dummies
  exactly as production.
- Same event handling, zone-scoped: Uri 2021-02-10..20 excluded from all fits;
  COVID 2020-03..06 weight 0.25; COAST windows 2024-05-16..19 and
  2024-07-08..21 excluded. Same hour-ending CPT and `(ts − 1h)` day/year
  attribution.
- Canonical monthly level: for each year-month FE, predict every calendar day
  of that month at climate-normal temps, sum, normalize by that month's
  climate-normal-predicted energy in the base period so that the **average of
  the 12 monthly values for 2019 = 1.0** (consistent with the annual index's
  2019 = 1.0 anchor). Seasonality is removed by the normals-based
  normalization by construction; the resulting series should look like a
  slowly-drifting level. Sanity check (assert + report, do not silently fix):
  the 12-month mean of the monthly index per year must match the production
  annual `size_idx` within 0.5% for every zone-year both compute.
- Per wall W ∈ {2021, 2022, 2023, 2024}: fit using data ≤ W-12-31 only.
  Nothing after the wall enters the fit — same discipline as production
  train-wall.
- Output: `data/derived/size_index_monthly_w{W}.parquet` with columns
  `zone (str), ym (date, month start), size_idx_m (float), n_days_used (int)`.

---

## 4. Component B — Model P: LLT + jump layer

`src/prob_size.py`

### B.1 Trend: local linear trend

- Per zone, per wall: `statsmodels.tsa.statespace.UnobservedComponents` with
  `level='local linear trend'` (stochastic level + stochastic slope), MLE fit
  on the monthly index. Deterministic seed for the simulation stage:
  `numpy` default_rng(42) fixed and recorded in artifacts.
- Simulate **N = 10,000** forward paths, **24 months** past the wall
  (`simulate` with filtered state at the wall as initial condition, drawing
  state and observation innovations).
- If MLE hits a boundary (slope variance → 0, plausible for COAST/SCENT):
  record it in the results entry and proceed — a degenerate-to-deterministic
  slope is an admissible fit, not an error. Do NOT hand-tune variances.

### B.2 Jump layer: tracking-sheet large loads

- Input: `data/derived/large_loads_sites.csv` (118 sites). Filter to the 3
  zones and to sites with **online date strictly after the wall** (double-count
  guard: sites online before the wall are already inside the fitted trend;
  the residual overlap from partially-ramped sites is an accepted, logged,
  UPWARD bias on band width — do not attempt to correct it in this task).
- Per site, per path: draw Bernoulli(p_mat) materialization. Status→p_mat
  prior (crude, logged as knobs in the pre-registration entry):
  `energized/under_construction: 0.85, signed/committed: 0.5,
  announced/other: 0.25`. Map the sheet's actual status vocabulary to these
  three buckets; if the sheet has no usable status column, use 0.5 for all
  and record NEEDS_CONTEXT for sdalvi to supply per-site probabilities —
  but DO NOT block the run on it.
- If materialized: linear ramp from the site's online date over a drawn ramp
  length ~ Uniform(6, 18) months. MW → monthly GWh = MW × hours-in-month /
  1000 × ramp fraction. Use **Expected MW** column (not DAM MW); if a site
  has only one of the two, use what exists and count it in a reported
  `mw_source` tally.
- Convert monthly GWh to size-index units by dividing by the zone's
  climate-normal annual energy at index=1.0 (derivable from the §3
  normalization base — expose it as a returned constant, do not re-derive
  inline).
- Path total: `size_path = llt_path + jump_path`.

### B.3 Fold outputs

Per zone × wall: annualize wall+1 and wall+2 (mean of the 12 monthly path
values × the same ×365.25/n convention issues do NOT arise here since the
monthly index is already normalized — just take the 12-month mean). Report
quantiles p5/p10/p25/p50/p75/p90/p95 and keep the full sample array.

---

## 5. Baselines

- **B0 — production + naive band:** ols3 point forecast (call the existing
  extrapolation code — do not reimplement) + Gaussian band with σ = std of
  ols3's wall+1 errors across all available zone-wall folds (pooled;
  compute once, report it).
- **B1 — random walk with drift:** annual size index, drift = mean of last 3
  annual diffs, forecast variance = sample variance of annual diffs ×
  horizon. Analytic normal quantiles.
- **B2 — ERCOT vintage forecast + empirical error band (conditional):**
  ERCOT's published long-term load forecasts by weather zone, historical
  vintages. **Data availability is unverified.** First action for this arm:
  check whether vintages by weather zone at annual grain, ≥5 vintages deep,
  are already in the repo/warehouse or trivially retrievable via anonymous
  HTTPS within the allowed-domain rules. If not: emit `NEEDS_CONTEXT: ERCOT
  LTLF vintages by weather zone — does sdalvi have these internally?` and run
  the experiment WITHOUT B2. Do not scrape, do not improvise credentials, do
  not spend more than one focused attempt on this. If available: B2 forecast
  = vintage-at-wall growth for wall+1/wall+2, band = empirical quantiles of
  that vintage series' historical errors at matching horizon.

---

## 6. Harness, artifacts, schemas

`scripts/experiment_prob_size.py` — folds = 3 zones × walls {2021, 2022,
2023, 2024} = 12 primary folds. Truth = realized size index on the
**validate/backtest matched-hour basis** (reuse the existing truth
computation; NEVER the rule-sweep basis; print the basis name in every
artifact header — this repo has been burned by basis confusion before, see
handoff brief §5 BASIS WARNING).

**`output/task08x_folds.csv`** — one row per zone × wall × horizon × model:

```
zone, wall, horizon (1|2), model (P|B0|B1|B2),
truth, truth_quantile, p5, p10, p25, p50, p75, p90, p95,
crps, covered_10_90 (bool), covered_5_95 (bool),
band_width_10_90, seed, basis (str), notes
```

CRPS: compute sample-based for P (`properscoring.crps_ensemble` or a
hand-rolled empirical CRPS — 20 lines; if adding `properscoring` to the env
is friction, hand-roll and unit-test it), analytic-Gaussian for B0/B1,
empirical for B2.

**`output/task08x_samples.parquet`**:

```
zone (str), wall (int), sample_id (int32), horizon_month (int, 1..24),
size_idx (float), llt_component (float), jump_component (float)
```

Keeping llt/jump split in the samples is mandatory — the results review will
ask how much coverage the jump layer bought.

Leaderboard: append one summary row per model to `output/experiments.csv`
per the existing pattern.

Tests: add to the suite — (a) monthly-index consistency assert from §3,
(b) jump-layer unit test with a synthetic 2-site sheet and fixed seed,
(c) empirical-CRPS correctness against a known closed-form Gaussian case.
`uv run pytest load-forecast` must stay green.

Environment: `uv run` everywhere; LightGBM is not used in this task but the
8 GiB cap still applies — 10k paths × 24 months × 3 zones × 4 walls in
float32 is ~12 MB, a non-issue; keep it that way.

---

## 7. Pre-registration and verdict (BINDING — write before running)

Before the first full run, append a pre-registration entry to
`docs/training_log.md` containing: the criteria below verbatim, the p_mat
knob values, ramp distribution, N, seed, and fold list. Then run. Then append
the results entry. No criterion may be edited after the first run.

**PROMOTE** (proceed to Task 08 production integration) if ALL of:
1. NCENT wall-2024 truth ≤ P95 of Model P (horizon 1, validate basis).
2. Coverage: truth ∈ [P10, P90] in ≥ 8 of 12 primary folds (horizon 1).
3. Model P aggregate CRPS (horizon 1, mean over folds) beats BOTH B0 and B1.
4. Band sanity: COAST and SCENT wall+1 P10–P90 width ≤ ±2.5 pp of annual
   growth each.

**KILL** if EITHER:
- NCENT wall-2024 truth > P95 of Model P even with the jump layer → the
  sheet does not contain the missing growth; the miss is distributed organic
  growth; escalate to the exogenous-covariate / hierarchical route (§8), or
- Achieving criterion 2 requires bands > ±4 pp on COAST/SCENT (vagueness
  bought coverage — useless for trading).

**ITERATE** (one defined iteration only) if coverage passes but Model P loses
CRPS to B1: refit with damped slope (`damped_trend` cycle or shrink slope
variance via a fixed prior scale), rerun, then final verdict. Any other
failure pattern → stop and report; do not free-form tune.

If B2 ran and B2 ALONE meets criteria 1–3: report that prominently — it
changes the roadmap (blend against ERCOT rather than build more model) and
sdalvi must see it before any Task 08 production work starts.

---

## 8. Explicitly OUT of scope (v2 backlog — do not build now)

Recorded so the results entry can reference them:
- Hierarchical Bayesian trend across all 8 ERCOT zones + EIA-861 utility
  panel (cross-sectional prior on slope-shift behavior).
- Heavy-tailed (Student-t) or Markov regime-switching slope innovations —
  the expected fix if Gaussian LLT under-covers NCENT specifically.
- Exogenous slope regressors (building permits, ESIID/premise counts).
- Sheet-calibrated materialization probabilities (announced→energized base
  rates from the sheet's own history).
- Joint-zone correlation of growth shocks.
- Conformal calibration wrapper over the folds.
- Peak-hours size track (separate parked item).
- Any change to `scenario.py` — the growth-quantile scenario axis is Task 08
  production work, contingent on PROMOTE.

---

## 9. Process rules for the agent

- Main session writes the code; subagents only for data verification /
  coverage checks. Sonnet for legwork; **Opus grading gate is mandatory
  before the results are presented as a finding.** No Fable-tier agents.
- Data/access questions → NEEDS_CONTEXT to sdalvi; never improvise access.
  DB access, if any is needed at all, is `awconnect.configure('read_only')`;
  expected answer is that everything needed is already in
  `data/derived/` except possibly B2.
- Rebuild-discipline: this task promotes NOTHING into production artifacts;
  `scenario_hourly.parquet` must NOT be rebuilt or touched.
- Quote no numbers from intermediate artifacts mid-run; the folds CSV after
  a complete run is the only citable source.
- Every experiment variant (including the ITERATE rerun) gets its own
  `docs/training_log.md` entry.
