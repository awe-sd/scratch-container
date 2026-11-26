# Scenario Monte Carlo for Constraint P(λ) — Feature Plan

> Owner: architect (Fable) plans/grades; ALL coding by Sonnet 5 subagents (repo CLAUDE.md "Division of labor").
> Status: DRAFT — finalize task briefs after the data-inventory agent (auction_schema_notes.md §Scenario MC)
> and the methodology research agent (docs/scenario_mc_research.md) report.

**Goal:** Replace the study's 11-scenario sampling with a 10k+ scenario Monte Carlo that yields, per candidate
constraint, a calibrated P(bind) and λ distribution — driven by joint (zonal load, regional wind CF, solar CF)
scenarios pushed through stored shift factors, with dispatch priced off DAM offer curves.

**Why linear MC, not more SCOPF:** flow_c = Σ SF_c,i · inj_i. The SCOPF's irreplaceable outputs (topology,
contingency set, SF matrices) are already computed and stored; binding probability and price are then linear
algebra + merit order. 10k scenarios × 100 constraints is a local matrix multiply, not 10k PowerWorld solves.

**Data spine (from sdalvi + explorers):**
- Wind CF: SQL Server `AW.dbo.ercotWindRegionHourly` (TimeStamp, windRegion, avgHSLPct, totalInstalledCapacityMW,
  isActual) — sequential queries only, port of `get_wind_region_cf`.
- Load: zonal actuals (ercotLoadView path) / ERCOT published forecasts for forward anchoring; rescale by
  target-month peak load. Solar: solarGenAct (zone 67) rescaled by installed capacity.
- Bus allocation: study `OUTLOAD` per-run bus loads (participation factors); gen mapping via GENUNIT SCED keys.
- SF matrices: SHIFT_FACTORS BUS_SHIFTS_VIEW per (study, topology, constraint), |SF| ≥ 0.02 slice.
- Offers: ERCOT60DDAMGENRESOURCE curves (60-day lag; positioned by scenario system λ).
- Dispatch-relief rules: exclude LZ_/WZ_ nodes and radial |SF|≈1.0 units (unenforceable class).

## Phases

### Phase 0 — REVISED per research (docs/scenario_mc_research.md): regression P(bind), no dispatch sim
0a. **P(bind|weather)**: regress/bin each candidate constraint's HISTORICAL FAST-SCAN FLOWS (already stored per
    timestamp in FAST_SCAN_RESULTS) against regional wind CF (ercotWindRegionHourly), zonal load (ercotLoadView /
    LDFCSTLOAD forward), and solar — stratified by price class 2/6. P(bind) = P(flow > limit | weather cell).
    Validate vs CONGHRPRICE realized frequencies. No injection modeling needed where this works.
0b. **λ scenario engine**: structural λ per scenario via merit-order stack (np.searchsorted on DAM offer curves,
    positioned by scenario system λ), marginal pair from DEVICE_SHIFTS unit-level SFs with the dispatch screen
    (exclude LZ_/WZ_, |SF|≥0.9, ISRADIAL). No per-scenario LP unless stack order changes.
0c. **Caveat carried from research**: day-block bootstrap of one month × 5 years ≈ 150 effective blocks — report
    CIs on block count; copula sampler (Phase 2) is the fix for tails, not more redraws.
Load allocation when Phase 3 needs it: AW.DBO.ERCOTDAMPSSELDVIEW (per-bus RAWMWLDF by zone/date/HE); gen by
OUTGEN set + 60d SCED plant data or region avg CF (sdalvi).

### Phase 1 — Historical bootstrap MC (only for constraints where Phase 0 regression fails)
1. **Scenario sampler**: same-month-across-years pool (last 5 Septembers), day-block bootstrap of joint
   (load, wind-by-region, solar) hours; rescale wind/solar by installed capacity ratio, load by peak-load ratio.
   Module `pfa/mc/scenarios.py`; cached local parquet of the historical pool.
2. **Injection builder**: scenario → bus injection vector (wind/solar to plant buses by capacity share within
   region; load to buses by OUTLOAD participation; thermal residual by offer merit order).
   Module `pfa/mc/injections.py`.
3. **Flow engine**: per candidate constraint, SF vector × injection matrix → flow distribution, P(flow > limit)
   with contingency direction; validation hooks. Module `pfa/mc/flows.py`.
4. **λ engine**: for binding scenarios, marginal-pair offer spread ÷ ΔSF at that scenario's dispatch point
   (reuse offer_lambda with the dispatch-relief exclusions). Output per constraint: P(bind), E[λ|bind], P75/P95 λ.
5. **Calibration report**: MC vs study-scenario P(bind) vs realized CONGHRPRICE binding frequency, per constraint.

### Phase 2 — Tail control
6. Conditional/importance sampling of the high-wind × high-load × low-solar corner with reweighting;
   or copula sampler if research agent recommends it. Target: stable P95 λ estimates.
7. Optional tiny-LP λ (scipy.linprog over the |SF|>0.03 unit set) if the pair method biases λ (research §3).

### Phase 3 — Integration
8. Wire MC outputs into the constraint report (replace equal-weighted P(bind); Value = Σ P(scenario)·λ(scenario))
   and the path Edge computation; wind-scenario cells shown per constraint (which weather cell pays).
9. Evaluate extending the fast-scan collector to accept synthetic injection sets (owner: sdalvi's infra) as the
   production home for the flow engine.

## Task-brief discipline
Each numbered item = one Sonnet task brief with exact interfaces, test-first, sequential SQL etiquette,
committed separately. Architect grades each against: calibration vs the three references, runtime
(<10 min for 10k × 100 on this box), and no parallel SQL Server access.

## Open questions (for sdalvi)
- Where does the fast-scan collector code live / can this container reach it? (Phase 3.9)
- Forward anchor: bootstrap around ERCOT published load forecast (current practice) or pure climatology + growth?
- Which peak-load number is authoritative for the September rescale?
- BESS/hydro treatment in the merit-order residual (ignore, or fixed profiles)?
