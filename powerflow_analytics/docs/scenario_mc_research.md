# Scenario Monte Carlo for constraint P(bind) and λ — research & phasing

**Author:** research pass, 2026-08-10. No pipeline code changed by this doc.
**Question:** can we replace the 11-scenario SCOPF sample with a linearized
scenario Monte Carlo (10k+ draws) to get P(bind) and λ distributions per
constraint, on this stack (pandas/numpy, Snowflake, one analyst)?

## Executive recommendation

**Phase 1 (build now, days not weeks): flow regression, not dispatch simulation.**
fast-scan already stores historical realized flow per constraint per hour, and
`ercotWindRegionHourly` + the existing `calculate_wind_price_histogram`
machinery already do bin-conditional wind/load probability (house method,
memory item 11). Regress (or, better, condition/bin) each constraint's
historical flow on regional wind CF, zonal load, and solar CF, stratified by
`PRICECLASSID` (2 = OnPeak, 6 = OffPeak — item 8/12), then read P(bind) off
the conditional distribution of predicted flow vs. limit. This skips dispatch
entirely, reuses code that already exists, and is trivially validated against
`CONGHRPRICE` because it's fit on the same table it's validated against. This
is the right *first* deliverable because it's cheap and because it exposes,
per constraint, whether flow is even wind/load-driven enough for a scenario
MC to be worth building on top of.

**Do NOT let the regression touch λ.** Per the house method (memory item 6),
constraint λ is structural — offer spread ÷ ΔSF — and `CONGHRPRICE` is
validation-only, never a λ source. Phase 1 gives you P(bind); it does not
give you λ. Keep those two outputs on separate code paths even though they
share the same conditioning variables.

**Phase 2: unit-level SF Monte Carlo for λ, skip bus-level PTDF injection allocation.**
Checked live during this research: `SHIFT_FACTORS.DBO.DEVICE_SHIFTS` **is**
readable by the read_only role (confirmed via a `LIMIT 1` query — 25 columns
including `BUSNUM`, `DEVICE_TYPE`, `ID`, `PSENS`, `ISRADIAL`, keyed by
`(STUDYID, TOPOLOGYID, CTGLABEL/BRANCHLABEL)`). This means unit-level shift
factors for the existing SCOPF topologies are available *today* — the
CPNODE/BUS view outage only blocks bus-level nodal PTDF, which you'd need for
the full "allocate zonal load to buses, dispatch, push through PTDF" pipeline
described in the prompt. You don't need that pipeline to get λ. Given
`DEVICE_SHIFTS` + `PSENS`, per constraint you already have the ~20-unit
screen (offers × ΔSF) that memory item 3/7 describes as the manual method —
this is a Monte Carlo *over scenario system-λ position on the merit-order
curve*, not over nodal power flow. Draw system-λ scenarios (the item-6
conditional model: recent price distribution × last-Sep weather rescaled to
current capacity), position the merit-order stack, read off the marginal
pair per draw, price λ = spread ÷ ΔSF from `DEVICE_SHIFTS.PSENS`. This is
buildable without bus-level PTDF access.

**Phase 3 (optional, gated on CPNODE/BUS_SHIFTS_VIEW access): full nodal
injection Monte Carlo.** Only worth building if phase 1 shows constraints
where flow is *not* well explained by zonal wind/load/solar alone (i.e.,
topology- or unit-commitment-driven binding that a flow regression can't
capture) — those are the cases where explicit dispatch + nodal PTDF earns
its complexity. Revisit once access lands; don't build it speculatively.

**On sample size:** "10k+ scenarios" is not automatically 10k independent
data points. See §1 — for a day-block bootstrap off a 5-year, single-month
pool, the *effective* sample size is bounded by the number of distinct
historical blocks (~150 day-blocks for a Sep-only pool), not the draw count.
Report binomial CIs on block count, not scenario count, or the precision
claim is wrong.

---

## 1. Scenario generation

### 1a. Block bootstrap of historical joint hours

**Mechanics:** resample contiguous blocks (hour-block or day-block) from
historical (zonal load, wind CF by region, solar CF) triples, preserving the
joint dependence structure within a block by construction (Moving Block
Bootstrap — see Politis & Romano; applied to wind/load jointly in reliability
studies, e.g. the bivariate wind-demand block bootstrap literature and its
use in generation-adequacy Monte Carlo).

- **Day-block vs hour-block:** day-blocks (24h) preserve the diurnal
  load/solar shape and the persistence of wind fronts (multi-hour wind
  regimes are real in ERCOT — Panhandle/West troughs and ramps last many
  hours). Hour-blocks destroy that and understate the duration of binding
  episodes, which matters for λ (a constraint that binds for a 6-hour ramp
  event has correlated λ draws, not independent ones). **Use day-blocks**, or
  at minimum 4-6h blocks aligned to price-class boundaries (HE7-22 vs
  HE23-6) so a block doesn't straddle OnPeak/OffPeak.
- **Pooling:** same-calendar-month-across-years (e.g., all Sep days 2021-2025)
  is the right pool — it captures weather-driven wind/load seasonality without
  conditioning away the very correlation you're trying to sample. Pooling
  across months would flatten the wind-load correlation structure that drives
  binding in the first place (e.g., Parker-Hicks needing high West wind —
  memory item 5 — is a within-month, not cross-month, phenomenon).
- **Rescaling for growth without breaking correlation:** rescale *levels*,
  not draws. For load: multiply each historical day-block by
  `(current month's forecast peak load) / (that historical Sep's peak load)`
  — a single scalar per block, applied to all hours in the block, preserves
  the intra-day and cross-region shape. For wind: rescale by
  `installed_capacity_ratio` per region (current MW / that year's MW) applied
  to `avgHSLPct` before converting to MW — this is exactly the rescaling
  already used in the item-6 system-λ conditional model ("gen scaled by
  installed capacity growth"), so reuse that code rather than inventing a
  second rescaler. Do NOT independently jitter regions or hours after
  rescaling — that's what destroys the joint structure block bootstrap is
  supposed to preserve.
- **Effective sample size — the number that matters:** a Sep-only, 5-year
  pool has on the order of 5 × 30 = 150 distinct day-blocks. Resampling with
  replacement to "10,000 scenarios" draws each of those ~150 blocks ~67
  times on average — for statistics that are roughly constant *within* a
  block (e.g., "did this constraint bind on this day"), the binomial
  variance is governed by n≈150, not n=10,000. At p≈0.1 binding rate, the
  95% CI on 150 effective draws is ±4.8 points (√(0.1×0.9/150)×1.96), vs.
  ±0.6 points if the 10,000 draws were truly independent. **Report CIs on
  block count.** This is the strongest practical argument for copulas (§1b):
  they can synthesize joint draws the historical record never saw, which
  block bootstrap fundamentally cannot.

### 1b. Gaussian / vine copulas over regional wind CF + load + solar, conditioned on hour-block

Fit marginals per region/hour-block (empirical CDF or a bounded distribution
for CF, since wind/solar CF ∈ [0,1]), fit a copula (Gaussian for a first cut;
vine/C-vine if pairwise tail dependence between adjacent wind regions matters
— literature explicitly recommends vine copulas over Gaussian for wind+load
spatio-temporal dependence in transmission overloading risk assessment,
because wind regions show asymmetric tail dependence Gaussian copulas
flatten) [Karki risk-based line-overload vine copula paper, IET RPG 2019].
Then draw joint uniforms, invert marginals, convert to MW using the same
installed-capacity scaling as §1a.

- **Why this over block bootstrap:** genuinely new joint combinations
  (e.g., a load level historically never paired with today's West wind
  buildout, because West capacity has grown since); breaks the n≈pool-size
  ceiling in §1a.
- **Cost:** fitting 5 regional wind CFs + zonal load + solar (~7-8
  dimensions) with a Gaussian copula is a `scipy`/`copulas`-library one-liner
  per hour-block × month; vine copula needs `pyvinecopulib` or R's
  `VineCopula` via subprocess — heavier tooling for one analyst to maintain.
  **Recommend Gaussian copula first**, check via a QQ/tail-dependence
  diagnostic whether the flattened tail matters for your binding constraints
  specifically (most ERCOT binding events are driven by wind *troughs*, i.e.
  lower-tail co-movement, which Gaussian underweights) — only invest in vine
  if that diagnostic shows it matters.
- **Parameterization to start with:** fit per (month, price-class) cell —
  6-12 months × 2 classes = 12-24 copulas, each fit on ~150-450
  historical hourly observations (day-blocks × 24, restricted to the class's
  hours). Draw 500-1000 scenarios per cell for a 10k-20k total scenario set.

### 1c. Conditional / importance sampling for high-wind × high-load tails

Standard block bootstrap and copula sampling under-populate the joint tail
that actually drives binding (memory item 5: Parker-Hicks needs *high* West
wind specifically). Importance sampling — oversample the tail region, then
reweight each scenario's contribution to the P(bind) estimate by
`w_i = p(x_i)/q(x_i)` (true density over the biased sampling density) — is
the standard fix, and has documented, large variance-reduction wins in
adjacent power-system rare-event work: an importance-sampling estimator for
grid rare events with 5,772 constraints in 326 dimensions at true
probabilities below 1e-22 achieved coefficient of variation ~0.0024 with only
n=10,000 draws [Owen & Maximov, "Importance sampling the union of rare
events," EJS 2019, arXiv:1710.06965] — three-plus orders of magnitude fewer
draws than naive MC would need for that precision.

- **Practical recipe for this stack:** shift the copula/bootstrap
  conditioning distribution toward the top wind-quantile bin per region (the
  same HSL bins — H/M/I/L at 80/50/20% — already used in memory item 5's
  wind-region classification) crossed with the top load-quantile bin, oversample
  that cell 3-5x its natural frequency, undersample nothing else (mixture, not
  full replacement), then reweight every scenario's P(bind) contribution by
  the ratio of the natural HSL-bin×load-bin joint frequency (computed once
  from `ercotWindRegionHourly` + load history) to the biased sampling
  frequency actually used.
- **Where this pays vs. doesn't:** worth it for constraints already
  identified from the SCOPF 11-scenario runs as needing an extreme cell
  (e.g., "needs high West wind" per memory item 5) — you know which tail to
  bias toward. Not worth it as a blanket default across all 100 constraints,
  since the reweighting adds bookkeeping and most constraints don't bind in
  an extreme cell at all. **Recommend: run the unbiased copula/bootstrap
  sample first, flag constraints whose P(bind) estimate has a wide CI or
  zero draws in the binding region, then re-run only those with importance
  sampling.**

### 1d. Weather-ensemble-driven approaches (cost/benefit only, not recommended for phase 1-3)

Using NWP ensemble members (e.g., GEFS/ECMWF ensemble) to drive wind/solar/
load scenarios directly, rather than resampling history, would capture
forward-looking weather regime shifts (new wind buildout siting, changing
storm tracks) that a historical pool by construction cannot. Cost: requires
an ensemble data feed/subscription, a wind-farm-siting → CF conversion model,
and materially more pipeline complexity (weather ensemble → CF model →
scenario, vs. reading a table). For one analyst maintaining this alongside
CRR valuation work, this is not worth building unless phase-1/2 validation
(§4) shows systematic bias that historical resampling can't fix because the
grid's physical wind/load geography has shifted enough that recent history no
longer represents it. Revisit only if that specific failure mode shows up.

---

## 2. Dispatch approximation

### Merit-order stack from DAM offer curves as SCED proxy

**Known pitfalls:**
- **Commitment / min-gen:** a merit-order stack from offers alone treats
  every unit as available at any output level; it ignores that thermal units
  below min-gen must either run at min-gen or be off, and that DAM-committed
  units carry commitment costs that don't show up as marginal offers. This
  overstates dispatch flexibility, especially in low-net-load scenarios where
  the merit order would want units below their min-gen floor.
- **Hydro/BESS:** these bid near-zero or negative and get dispatched first in
  a naive merit order regardless of state of charge / water availability —
  a scenario draw that assumes a battery is available at 2pm every draw
  overstates relief capacity system-wide.
- **Self-schedules:** self-scheduled MW are price-insensitive and dispatch
  regardless of merit order; excluding them (treating self-sched MW as a
  fixed injection, not part of the offer stack) is a cheap, important
  correction — otherwise the merit order double-counts that capacity as
  price-responsive.
- **Reserves:** SCED holds back capacity for ancillary services; a pure
  energy merit-order stack over-dispatches available energy capacity by
  ignoring the reserve carve-out, understating how tight the margin actually
  is in the higher-net-load scenarios that matter most for binding.
- **Cheap corrections:** (1) fix self-scheduled and must-run units as
  inelastic injections, not part of the offer stack; (2) floor thermal units
  at min-gen or exclude them below a net-load threshold where they'd
  historically be off; (3) apply a flat reserve haircut to available thermal
  capacity before merit-ordering. None of these require solving a UC problem
  — they're stack-construction rules applied once per scenario.

### Alternative: regress historical constraint flow on regional wind/load (skip dispatch)

This is exactly phase 1 above. Given fast-scan already stores realized flow
per constraint per hour and the wind/load history tables already exist, the
regression/binning approach is **strictly cheaper and more defensible** than
merit-order redispatch for the P(bind) question specifically, because:

1. It's fit and validated on the same measurement (flow → CONGHRPRICE
   binding), so there's no dispatch-model-vs-reality gap to explain.
2. It sidesteps every pitfall in the merit-order list above — no commitment,
   hydro, self-sched, or reserve assumptions needed.
3. It degrades gracefully to "this constraint's flow isn't well explained by
   zonal wind/load/solar" as an honest signal that dispatch/topology detail
   is actually needed for that specific constraint — which is exactly the
   trigger for phase 3.

**When merit-order dispatch is better despite the extra complexity:** for
constraints that don't yet have enough binding history to regress on (new
topology, recently-uprated line, newly interconnected generation nearby) —
there the regression has no data to fit, and a forward-looking dispatch
approximation is the only option. This is the practical scope boundary:
**regress where there's history, dispatch-approximate where there isn't.**

---

## 3. λ estimation per scenario

### Offer-spread ÷ ΔSF vs. tiny per-constraint LP

The house method (memory item 4/6) already commits to structural λ = offer
spread ÷ ΔSF, never a regression on price history. The open question here is
just *how* to compute it at scenario scale.

- **Screen first, per memory item 7:** exclude LZ_/WZ_ shift nodes and units
  with `|SF| ≥ ~0.9` (radial/bottled, `ISRADIAL` flag is present directly in
  `DEVICE_SHIFTS` — no separate lookup needed) — these aren't dispatchable
  relief. Also exclude `|SF| < 0.03` (below dispatch-sensitivity noise floor,
  per the existing offer_lambda convention). That leaves roughly the ~20-unit
  window the house method already uses per constraint, out of whatever the
  full connected set is — this shrinks the "100 constraints" scope to
  however many post-screen actually have qualifying dispatch (constraints
  with none are a separate, non-target class per item 7, not a phase-1
  compute problem at all).
- **Marginal-pair offer-spread method:** for a scenario's system-λ position
  (from the item-6 conditional model), locate where each screened unit sits
  on its own offer curve relative to that λ, find the adjacent marginal pair
  on the constraint's own screened set, λ_constraint = (offer_j − offer_i) /
  (SF_i − SF_j). This is an O(1) lookup once units are sorted by offer price
  — **no LP needed** if the merit-order position is a deterministic function
  of scalar system-λ (which it is, given a fixed stack per topology/hour).
  **Precompute the sorted stack once per (topology, hour-of-day-type), then
  resolve each of the 10k scenarios via `np.searchsorted` on system-λ** —
  this turns "10k scenarios × 100 constraints" into an array lookup, not
  10k×100 optimization calls.
- **When you'd actually need the LP:** only if the marginal pair is *not* a
  pure function of scalar system-λ — e.g., if scenario draws change which
  units are available (outages, self-sched changes) in a way that reorders
  the stack per-scenario rather than just moving a single λ threshold along
  a fixed stack. If that's the case for some fraction of scenarios, a tiny
  LP over ~20 screened units (bounded box constraints, one equality) is
  cheap: HiGHS via `scipy.linprog` on a ~20-variable, ~2-constraint problem
  is low-single-digit milliseconds. At 10k scenarios × 100 constraints = 1M
  solves, that's roughly 30 min single-core (and trivially
  parallelizable across constraints, since each constraint's screened set is
  independent) — feasible as a nightly batch job, not interactive. **Use the
  lookup as the primary path; keep the LP as a spot-check harness** run on a
  sample of scenarios per constraint to confirm the lookup and LP agree,
  rather than running the LP at full scale by default.

---

## 4. Validation design

**Three-way calibration**, each answering a different question:

1. **Study scenarios (the 11 SCOPF runs) vs. scenario-MC P(bind):** do the
   SCOPF-flagged binding conditions (e.g., "Parker-Hicks needs high West
   wind") fall inside the MC's binding region, and does the MC assign them
   sensible relative probability? This checks the MC isn't missing a
   binding mode the deterministic study found — a false negative here is
   the dangerous failure mode (a constraint the desk would trade on that the
   MC says never binds).
2. **Realized `CONGHRPRICE` binding frequency vs. scenario-MC P(bind):**
   for historical months already in `CONGHRPRICE`, compare realized
   fraction-of-hours-bound (by price class) to the MC's predicted P(bind)
   for the matching wind/load conditions of those same historical hours.
   This is the most direct calibration check and should be run first,
   since it's nearly free (both sides come from tables that already exist).
   Compare via reliability/calibration curve (predicted P(bind) decile vs.
   observed binding frequency in that decile) rather than a single
   aggregate number — aggregate P(bind) can match while the MC is wrong
   about *which* hours bind.
3. **Fast-scan historical replay:** replay historical hours through the same
   phase-1/2 pipeline (feed the actual historical wind/load/solar for that
   hour rather than a scenario draw) and compare the pipeline's *implied*
   flow/λ to fast-scan's stored actual flow/λ for that hour. This isolates
   pipeline error (regression fit quality, SF staleness, merit-order
   approximation error) from scenario-generation error (§1), which
   calibration #2 conflates.

**Systematic bias detection:** track calibration #2's reliability curve over
time (by month, refit quarterly) — a curve that's well-calibrated in-sample
but drifts out-of-sample by season is a sign the historical pool (§1a) is
stale relative to current capacity/topology, which is a rescaling problem,
not a model-form problem, and points back to tightening the capacity-growth
rescaler rather than rebuilding the sampler.

---

## 5. Variance / compute budget

- **Matrix sizes:** `DEVICE_SHIFTS` gives shift factors already scoped to
  the constraint's own topology, so there's no need to carry a full 2-5k-bus
  PTDF matrix per constraint in memory for phases 1-2 — the screened set per
  constraint (post |SF| filter) is on the order of tens of rows, not
  thousands. A dense bus-level PTDF (phase 3 only, gated on access) would be
  the 2-5k × constraint-count matrix the prompt anticipates; until that
  access lands this is a non-issue.
- **Scenario storage:** 10k-20k scenarios × (5 wind regions + load + solar) is
  a trivial in-memory DataFrame (well under 1M cells); the expensive object
  is the per-scenario, per-constraint λ/flow output — 10k × 100 = 1M rows,
  still small (tens of MB as a long DataFrame, parquet-friendly, fits the
  existing `cache/study_<id>/` convention).
- **Where importance sampling pays (§1c):** compute cost of the reweighted
  estimator is identical to the unbiased one (same lookup/LP per scenario);
  the payoff is precision per draw, not speed. It pays specifically for the
  subset of constraints already flagged (from SCOPF study conditions) as
  needing a tail cell — running it as a blanket default wastes the
  bookkeeping on constraints that never approach their tail.
- **Compute is not the bottleneck; scenario generation and validation are.**
  The λ lookup (§3) and the flow regression (phase 1) are both
  vectorized/array-scale operations. The real cost centers are: fitting and
  QA'ing the copula per month/class cell (§1b), and building the three-way
  validation harness (§4) — both one-time engineering investments, not
  recurring compute.

---

## Open questions for the desk

1. **Regression conditioning granularity:** should the phase-1 flow
   regression condition on wind CF *per region* (5 dims) or on a smaller set
   of derived features (e.g., West+Panhandle sum, since many West-heavy
   constraints don't care about Coastal/South wind)? Fewer features means
   more stable regression on a ~150-block-equivalent history; more features
   risks overfitting an already-small effective sample. Needs a per-constraint
   feature-selection pass, not a single global choice.
2. **Which constraints get phase-3 nodal treatment, and when does
   CPNODE/BUS_SHIFTS_VIEW access actually land?** Worth a standing check
   (reuse `shifts.py::probe_access`) rather than a one-time question — the
   moment access lands, re-run phase 1's "flow not explained by zonal
   wind/load" flag list to decide which constraints justify the phase-3
   build.
3. **How much does system-λ scenario generation (item-6 conditional model)
   need to be re-validated jointly with the wind/load copula draws?**
   Currently that model is fit independently of the wind-region scenario
   generator in §1; if system-λ correlates with wind/load beyond what's
   already captured in the historical block/copula draws (it plausibly does
   — high wind depresses system λ), drawing them independently double-counts
   or under-counts that correlation. Needs a decision: fold system-λ into
   the same copula, or explicitly condition the λ draw on the wind/load draw
   for that scenario.
4. **Self-schedule and outage data freshness for phase 2's merit-order
   stack:** how current does the self-sched/must-run exclusion list need to
   be per scenario — daily snapshot, or is a monthly-typical stack good
   enough for a probabilistic (not day-ahead-specific) P(bind) estimate?
   Affects how much pipeline maintenance phase 2 actually costs the desk
   ongoing.
5. **Desk risk tolerance on importance-sampling reweighting:** is a
   reweighted tail estimate (§1c) trusted the same as an unbiased one for
   sizing a position, or does the desk want the unbiased number reported
   alongside it with the reweighted CI flagged separately? Affects whether
   §1c ships as a default output or an analyst-invoked diagnostic.

---

## Sources

- [Synthesis of hourly wind power series using the Moving Block Bootstrap method](https://e-archivo.uc3m.es/bitstreams/f86fd4d0-f69f-4589-8317-ca39816be1be/download)
- [Estimation of Joint Distribution of Demand and Available Renewables for Generation Adequacy Assessment](https://arxiv.org/pdf/1412.1786)
- [Risk-based security assessment of transmission line overloading considering spatio-temporal dependence of load and wind power using vine copula, IET Renewable Power Generation (2019)](https://digital-library.theiet.org/doi/full/10.1049/iet-rpg.2018.6091)
- [Owen & Maximov, "Importance sampling the union of rare events with an application to power systems analysis," Electronic Journal of Statistics 13(1), 2019](https://arxiv.org/abs/1710.06965)
- [Shift factors in ERCOT congestion pricing — Ross Baldick](https://users.ece.utexas.edu/~baldick/papers/shiftfactors.pdf)
- Internal: `powerflow_analytics/pfa/extract/shifts.py`, `pfa/analysis/offer_lambda.py`, `pfa/analysis/market.py`, `pfa/analysis/fastscan.py`, `docs/auction_schema_notes.md`, and `AW.dbo.ercotWindRegionHourly` access pattern (memory: `powerflow_crr_valuation_method.md`).
