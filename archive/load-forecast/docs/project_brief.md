# load-forecast — handoff brief (2026-08-15)

Written for a fresh model/session (e.g. the big-compute training run) that needs
the full picture up to the current roadblock. Everything here is backed by files
in this repo; read `CLAUDE.md` first — its rules are binding and not repeated in
full here.

## 1. What this is

ERCOT zonal load-growth and scenario-replay engine for three weather zones —
NCENT (DFW), COAST (Houston), SCENT (Austin + San Antonio) — built 2026-08-14/15
for sdalvi (power trader, Appian Way Energy). It answers:

1. Replay: what would load be on the year-Y system under historical weather X
   ("2023 summer on the 2026 system")?
2. Forward: what does 2028 look like if the growth trend holds, under any
   chosen weather year?
3. New (Task 07): how much of measured growth is *organic/conforming* vs
   identifiable large loads (datacenters, crypto, industrial)?

It replays actual historical weather; it is deliberately NOT a weather generator.

## 2. Method

Two-stage decomposition: `load(ts) ≈ size_idx[zone, year] × shape(weather, calendar)`.

- **Size index** (`src/size_index.py`): per-zone WLS on daily energy with
  **year fixed effects** (sdalvi ruling — not a linear trend), piecewise-linear
  daily temp with knots 55/65/75°F, weekday/holiday dummies. Canonical level =
  predict every calendar day at climate-normal temps, scale ×365.25/n →
  normalized annual GWh → `size_idx` (2019 = 1.0). Forward extrapolation:
  OLS on the last k fitted years, per-zone `SIZE_EXTRAP_YEARS =
  {NCENT: 3, COAST: 3, SCENT: 6}`.
- **Shape model** (`src/shape_model.py`): per-zone LightGBM on per-unit load
  (`load_mw / size_idx[year]`). Features: `temp_f_popwt, temp_f_avg24,
  temp_f_ewm3d, dewpoint_f_popwt, hour, month, weekday, holiday` — **nothing
  date-indexed** (trees cannot extrapolate a trend; growth lives only in the
  size index). `num_leaves 63, lr 0.05, 600 rounds, num_threads 4` (8 GiB
  container cgroup cap).
- **Events**: Uri (2021-02-10..20) excluded from ALL fits; COVID (2020-03..06)
  weight 0.25 in the size fit only; COAST outage windows (2024-05-16..19
  derecho, 2024-07-08..21 Beryl) excluded from all fits, zone-scoped.
- **Conventions that bite**: hour-ending CPT everywhere; day/year attribution
  via `(ts − 1h)`; train wall 2024-12-31 (nothing later enters any fit);
  raw data immutable, every derived table reproducible.

## 3. Data inventory

| Source | Derived file | Notes |
|---|---|---|
| SQL Server `AW.dbo.ercotLoadView` | `data/derived/load_hourly.parquet` (305,409 rows, 2015–2026 × 3 zones) | Holes: 2016-07-01 missing entirely; 8 genuine 23-hour days (Nov 2020 ×4, 2021-03-04, 2021-03-25, 2022-08-14, 2025-12-04) — March-DST 23-hour days are expected, not holes |
| NOAA ISD (AWS bucket, anonymous HTTPS) + IEM Mesonet patch | `data/derived/zone_weather_hourly.parquet` | NOAA bucket truncates ~2025-08-25 and lacks 2026 → Mesonet patch (`src/pull_weather_mesonet.py`). JWY + CPT patched 0 hours (undiagnosed, ~5% NCENT weight, absorbed) |
| Census PEP 2023 county pops + TX Gazetteer + isd-history | `data/derived/crosswalk_county_station.csv` | 22 counties / 21 ASOS stations, ~91% pop coverage per zone, split-county overrides (COLLIN→NCENT, WILLIAMSON→SCENT, …). Weights frozen |
| sdalvi county → weather-zone map | `data/raw/crosswalk/ercot_county_weatherzone.csv` | From internal ercotDataDictionary |
| sdalvi datacenter tracking sheet | `data/derived/large_loads{,_sites}.csv` (244 rows / 118 sites), raw verbatim in `data/raw/large_loads/` | Per-bus DAM/Expected MW + online dates through 2030 |
| SQL Server `AW.dbo.ercotManuallyUpdatedLoad` | roster inside `data/derived/ncl_stations.csv` | PUN manual fill-ins; the `isConforming` flag lives HERE. Roster is generator-station-service heavy (negative WithdrawMW — never abs()'d; production floors each station-hour at 0, see §6) |
| `ercotStationLoad` (Snowflake copy for scans) | `data/raw/station_load/` + `data/derived/organic_load_hourly.parquet` | Branch-flow-derived hourly station MW; ends ~2026-06 |
| `ercotLoadEstimation_*` family — **Snowflake `AW.DBO`** (verified 2026-08-26: `AWDev.DBO` on Snowflake is EMPTY; only the SQL Server copy uses the `AWDev` database, which is what `src/organic_load.py` still queries) | cross-check only | State-estimator rebuild; `run_id='1'` (SQL Server only). `term_bal` grain includes kv — **SUM over kv per (station, timestamp) is CONFIRMED CORRECT** (`docs/kv_aggregation_test.md`, 2026-08-26): double-counting was tested and **falsified** — `SUM(TOTAL_NET_LOAD_MW)` ≡ `RAW_STATION_NET_LOAD_MW` to 6 decimals, kv-count vs ratio correlation r=0.093, and single-kv stations sit at the same ~1.0 baseline. **Separate open issue: a SUBSET of stations reads ~3× `ercotStationLoad` on net** (JCK 3.28×, LON_HILL ~3.1× in summer dispatch, small `*SES` solar) while the 30-station median is ~1.0 — station-and-dispatch-specific, needs per-station reconciliation/flagging, NOT an aggregation change. Untested hypothesis worth checking: 3× is the single-phase↔three-phase ratio. `pun_score` is continuous, exclusion threshold `>0` is hair-trigger; 2.2% of rows have NULL `pun_score` (== `COVERAGE_FLAG IS NULL`) that `COALESCE(...,0)` silently calls clean. **RESOLVED (`docs/task09_grading_review.md` §3/D3, 2026-08-26): `PUN_TOTAL_*` runs in TWO REGIMES, confirmed on a bounded population sweep (5,575 stations / 133,800 station-hours, 2026-02-20).** At ~97.5% of station-hours there is no PUN component and `PUN_TOTAL_* ≡ TOTAL_*` exactly — a copy, carrying no extra information. At genuine PUN stations (0.36% of hours non-trivially) it is a mirrored gross construct — load booked at one kv terminal, mirrored as generation at another — that nets to ~0 and can read tens of times the station's real net (JCK's `PUN_TOTAL_EST_LOAD_MW` hits 1,000+ MW at a station whose real net never exceeds 37 MW). `jck_lonhill_generation.md` §3.1's "tautologically zero" claim is FALSE as a universal rule and even fails on JCK itself over a wider window (holds only 45% of JCK's Jan–Mar hours vs ~100% in the narrower Feb 19–26 probe week that originally produced the claim) — downgrade that section from a binding rule to a window-specific observation. Some stations switch regime hour to hour. **Never read `PUN_TOTAL_EST_LOAD_MW`/`_GENERATION_MW` as physical MW, never assume `PUN_TOTAL_NET_LOAD_MW` is zero, and always use `TOTAL_NET_LOAD_MW` for net.** Snowflake `AW.DBO` members + row counts (created 2026-04-28/29): `TERM_BAL` 325.5M, `STATION_BAL` 283.4M, `AUDIT` 496.2M, `RUN_AUDIT` 54,047, `BAD_INTERVALS` 618, `BRANCH_MAPPING` **0 rows on Snowflake (7,544 on SQL Server — a replication gap, not absence; either way it maps branch device → `(station, kv)`, never to `SswgBusNumber`, so bus-level stays unreachable regardless of platform)**. `BAD_INTERVALS` supersedes the hand-rolled `HAVING ABS(SUM(...)) <= 50` failed-interval subquery. **Generation leg EXISTS** — `*_EST_GENERATION_MW` and signed `*_NET_LOAD_MW` alongside `*_EST_LOAD_MW`; `NET = LOAD − GENERATION`. **Trap: the plain `STATION_EST_*`/`STATION_NET_LOAD_MW` columns are pipeline-zeroed for PUN station-hours — use `RAW_STATION_*` or `SUM(TOTAL_*)` over kv.** Snowflake copy has NO `run_id` column. **STALE: both platforms stop ~2026-03-04, i.e. more stale than `ercotStationLoad` (2026-06-15) — sdalvi can have SWE refresh it, see `docs/swe_refresh_request.md`.** **Verdict on replacing `ercotStationLoad` for net injection (Opus-gated, `docs/task09_grading_review.md`): YES by station and the family is the BETTER source — on structural grounds (99.6% namespace overlap, sees load at 7/110 stations where SL reads zero, explicit load/gen/net decomposition, `RAW_*` survives PUN zeroing) — NOT on the 98.1% agreement rate, which is near-tautological because both products sum the same branch flows over the same SE snapshot (median |diff| 12.5 kW over 282,240 hours). NO for bus-level, unconditionally.** Full schema: `docs/load_estimation_schema.md`; benchmark: `docs/task09_benchmark_findings.md` |
| `AW.DBO.ERCOTLOADDISTRIBUTIONFACTORS` (SNOWFLAKE, not SQL Server) | unused so far | Quarterly 7-day study clusters; own SUBSTATION/LOADID namespace; no conforming flag |

Station-namespace map (trap): state-estimator `station` ==
`NmmsStationCode` (roster, ercotStationLoad) == ercotDataDictionary; zone
attribution = `SswgBusNumber → PlanningBusCounty → county→zone crosswalk`.
The sheet's `dam_bus_name` and the LDF `SUBSTATION` are DIFFERENT conventions;
`MRIDLOAD` (GUID) is the only durable cross-source key candidate.

## 4. Pipeline (always `uv run`, from repo root)

`src/build_crosswalk.py` (county/station crosswalk) → `src/pull_load.py` →
`src/pull_weather.py` + `src/pull_weather_mesonet.py` + `src/zone_weather.py`
→ `src/size_index.py` → `scripts/train_all.py` → `src/validate.py` (2025–26
scorecard) / `src/backtest.py` (rolling-origin 2019–24) / `src/analog.py`
(weather-analog replay) → `src/scenario.py --all` (24-scenario matrix) →
`scripts/build_viz_report.py` (`output/model_report.html`). Task 07 chain:
`src/build_large_loads.py` (parse sdalvi's sheet) then `scripts/run_task07.py`
(`src/ncl_stations.py` → `src/pull_station_load.py` → `src/organic_load.py` →
organic size index → NCENT backtest comparison; persists
`output/task07_organic_table.csv` + `output/task07_organic_backtest.csv`).

Iteration goes through `scripts/experiment.py` (fast fold ~4s, leaderboard
`output/experiments.csv`, promote winners with `--promote`); EVERY experiment
gets an entry in `docs/training_log.md`. Tests: `uv run pytest load-forecast`
→ 58/58. Full production retrain is DEFERRED to the large compute machine —
never run heavyweight sweeps in this 8 GiB container.

## 5. Where the model stands (train ≤2024, score 2025–26)

| Zone | Monthly MAPE | 2025 growth err | Worst-year hourly MAPE | Verdict |
|---|---|---|---|---|
| COAST | 1.18% | −0.03 pp | 3.08% | PASS |
| SCENT | 1.40% | −0.27 pp | 3.39% | PASS |
| NCENT | 3.25% | **−3.13 pp** (2026 2-yr annualized: −1.77) | 4.18% | **FAIL on growth only** |

- sdalvi's <10% hourly-MAPE gate: met everywhere (max across 18 backtest folds
  6.51%; wall validation 2.85–4.18%).
- Known bias: COAST/SCENT run hot on top-50 load hours while passing monthly
  MAPE (COAST +1.88/+3.21%, SCENT +2.01/+2.83% for 2025/26; candidate fix:
  separate peak-hours size track, parked).
- Analog benchmark: 15/21 pass. Failures: NCENT 2026-03/04/06 (the level
  shortfall + a cold-analog artifact) and SCENT 2026-01/03/05 (analog-distance
  noise — the gate needs a min-closeness rule, open item).
- **The structural claim (reviewer-verified)**: across walls 2021–24 and five
  extrapolation rules (ols2/ols3/ols6/anchored/CAGR), NO rule gets NCENT ≤1 pp
  at wall 2024 (rule-sweep basis: truth +5.24% growth, best rule −1.67 pp,
  production ols3 −3.68 pp on that fold). NCENT's 2025–26 acceleration is not
  forecastable from load history alone — do not tune history harder (overfit
  risk). The fix must be exogenous data. Full table in `docs/training_log.md`
  round 4. BASIS WARNING: the rule-sweep and `validate.py`/`backtest.py`
  compute growth on different matched-hour bases — the same wall-2024 fold
  prints truth +5.24%/err −3.68 pp (sweep) vs +4.81%/−3.13 pp (validate/
  backtest). Always name the source when quoting NCENT growth numbers.

## 6. Task 07 — organic vs large-load growth (done 2026-08-15)

sdalvi rulings: subtraction source = HYBRID (`ercotStationLoad` primary,
LoadEstimation cross-check with >20% monthly-disagreement flags — 1,506
station-months flagged, agent-reported: the cross-check queries run live
inside `src/organic_load.py`, no cached artifact); NCL set = CONFIRMED ONLY (sheet ∪ roster = **85
stations**: NCENT 36 / SCENT 25 / COAST 24); forward additions OUT of scope
(deliverable = conforming growth only); 3 zones only.

Mechanics: hourly zone NCL sum, **each station-hour floored at 0**
(`sign_mode='floor'` — the production default; the literal signed sum is a
diagnostic only and is WRONG for roster stations: it drove NCENT's NCL share
to −7% and made 2/3 folds worse — see `src/organic_load.py` docstring),
online-date gated, subtracted from zone load → `organic_load_hourly.parquet`
→ organic size index (`size_index_organic.parquet`). Guards: organic >50% of
total every hour (reported, NOT silently clipped); online-date gating carries
an upward-only "phantom" clip bias (≥11% of gated NCL energy, in-sample lower
bound — NCL shares are conservative). 32 sheet rows have no dictionary match
(mostly future sites; 6 do carry bus ids that don't resolve).

**Finding:**
- SCENT's boom IS the large loads: 2023 organic growth +1.56% vs total +4.74%
  (NCL energy share 0.52% → 3.54% → 3.05% over 2022–24). Verified sound:
  `ercotStationLoad` sees SNDSW/Riot Rockdale properly (143→612 MW ramp,
  consistent with the state estimator's 679 and the sheet's 600).
- NCENT was NOT explained by this pass: confirmed-NCL share only
  0.13% → 0.79%, organic series backtests WORSE in 3/3 folds (wall-2024
  growth error −3.54 pp organic vs −3.13 pp total). **BUT this conclusion is
  now known to be PREMATURE — see §7: the subtraction source is blind to the
  two biggest confirmed NCENT datacenters.**

## 7. CURRENT ROADBLOCK

NCENT's −3.13 pp growth under-forecast is unexplained by the confirmed
large-load set *as subtracted so far*. Competing hypotheses (ordering
REVISED 2026-08-15 after the mapper agent's coverage-gap finding):

- **(a′ — NEW LEAD) The confirmed set was under-subtracted, not too narrow.**
  Verified by direct cache reads: `ercotStationLoad` reads **~0 MW in every
  year** for HCKSW (CyrusOne DFW7, TARRANT/NCENT) and WTRML
  (Databank+Skybox+Stack, DALLAS/NCENT), while the state estimator shows them
  drawing **389 + 150 ≈ 539 MW in Feb-2026** — vs the ≈432 MW needed to close
  the NCENT gap. Two stacked mechanisms: the branch-flow table simply doesn't
  see these stations (true-PUN-like invisibility), and their sheet online
  dates (2026-07-01) gate them to zero anyway even where data exists. It is
  NOT blind everywhere — SNDSW/Riot (SCENT) is seen correctly — so this is a
  per-station problem concentrated, so far, in NCENT. Fix candidate ("hybrid
  v2", needs sdalvi ruling): for confirmed stations where ercotStationLoad ≈0
  but the SE shows material load, subtract the SE series instead — using raw
  `pun_total_est_load_mw` (kv-summed), NOT `clean_plus_internal_mw`, since
  pun_score>0 zeroes exactly these stations; SE history covers ~2021→2026-02.
  The 1,506-flag cross-check leg was the right instinct but its output was
  never used to switch sources.

- **(a) Confirmed set too narrow (unknown PUN stations).** Mostly resolved by
  the mapper (`docs/pun_unknowns_map.md` + `data/derived/pun_unknowns_map.csv`)
  plus sdalvi rulings 2026-08-15: JCK, LON_HILL, LCSES, GBY = generators;
  DOW = real PUN; RNKSW = no PUN load (over-flag; DENTON/NCENT, real but
  small: 20→42 MW). Of the NCENT-zone rows only **SDMSW (FALLS, 136 MW in
  the SE week, ~31% of the gap) stays OPEN** — its ~0 ercotStationLoad
  reading is INCONCLUSIVE given the (a′) blindness — and RYSSW is real but
  flat. Materiality yardstick: closing NCENT's ~3 pp gap needs ≈3,781 GWh/yr
  ≈ **432 MW of average continuous load**; the confirmed NCENT set as
  subtracted was ≈999 GWh ≈ 114 MW (itself understated per (a′)). Data
  caveat: `ercotStationLoad` ends **2026-06-15**, so any 2026 station stat is
  a partial year missing the summer peak — compare seasonally matched
  windows, never raw 2026 yearly energy.
- **(b) NCENT organic growth is real and distributed** (suburban build-out,
  electrification, small commercial). Then no subtraction fixes it — the size
  index needs a different forward rule or an exogenous covariate (permits,
  interconnection queue, ERCOT load forecasts).
- **(c) Unexploited signals**: `ercotManuallyUpdatedLoad.isConforming` (dirty
  — signal not truth), the LDF table, ERCOT's published large-load queue.

Next step is sdalvi's ruling once the mapper lands.

## 8. Rules of engagement (binding — details in CLAUDE.md)

- DB: `awconnect.configure('read_only')`; Snowflake warehouse `AI_READ_ONLY`
  for anything scan-like; SQL Server STRICTLY sequential, TOP-capped,
  date-bounded; extract-once → parquet cache; NOAA/Census/IEM via anonymous
  HTTPS only (never corporate creds).
- Division of labor for THIS project (`load-forecast/CLAUDE.md`, overrides the
  repo-root rule): the MAIN session writes the code; subagents do data
  verification and coverage checks; data/access questions go to sdalvi
  (agents stop with NEEDS_CONTEXT rather than improvise).
- Agents: Sonnet for legwork, Opus for the mandatory grading gate before any
  deliverable is presented; no Fable-tier agents (sdalvi session ruling
  2026-08-14, recorded in session memory — not in a repo file).
- Deliverables live in the repo — never hosted artifacts.
- Always `uv run`; 8 GiB memory cap (LightGBM `num_threads 4`).
- Bug classes already paid for once: stale derived artifacts after a promotion
  (ALWAYS rebuild `scenario_hourly.parquet` after size-index/model changes);
  one-sided event filtering in growth math (use symmetric matched hour sets);
  kv-grain fan-out in LoadEstimation joins; station-namespace confusion;
  quoting numbers from intermediate artifacts mid-run.

## 9. Open items

"hybrid v2" subtraction decision (SE series for stationLoad-blind confirmed
stations — sdalvi ruling needed) · SDMSW true-load determination (needs a
source beyond ercotStationLoad) · peak-hours
size-track experiment (top-50h +2–3% bias) · ERCOT API key wiring · Task 07
results into `output/model_report.html` · data-owner questions (2016-07-01
hole, 23-hour days) · Census ACS key switch-back · JWY/CPT mesonet 0-hour
patch mystery · SCENT analog-gate min-closeness rule.
