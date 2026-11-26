# ERCOT Zonal Load Growth — CLAUDE.md

## What this project is

A small, decoupled load-growth and scenario-replay engine for ERCOT
weather zones — v0 built on **NCENT, COAST, SCENT**; the 08-Y direction
(sdalvi 2026-08-19, see below) expands to **all 8 zones + system-wide**.
It answers two questions:

1. What would load be in year Y under the weather of some historical year?
   ("2023 summer on the 2026 system")
2. What does load look like in 2028 if the current growth trend holds,
   under any chosen weather year?

Load is split into two independently-modeled components:

- **Size index** `L_z(y)`: weather-normalized annual load level per zone.
  All growth lives here. Slow, parametric, extrapolatable.
- **Shape model** `f_z(weather, calendar)`: per-unit hourly load response
  to weather. Assumed stable across years. Gradient-boosted, per zone,
  NO time trend inside.

Scenario answer = `f_z(weather scenario) × L_z(scenario year)`.

Deliberately NOT a weather generator (contrast: Sunairio reference doc).
We replay actual historical weather. Synthetic weather can be bolted on
later without touching the load model.

## Hard design rules (do not violate)

1. No time trend, year feature, or date index inside the shape model.
   Trees cannot extrapolate trends; growth is carried only by size_idx.
2. Weights and vintages are frozen: population weights from one fixed ACS
   vintage (2023 5-yr); station sets fixed for the full history. Changing
   either mid-history contaminates the load trend with an input trend.
3. Events: Feb 10–20 2021 (Uri) excluded from all fitting (flagged, never
   deleted from raw). Mar–Jun 2020 downweighted (0.25) in size-index
   fitting, normal weight in shape fitting. Outage-suppression windows
   (zone-scoped, `config.OUTAGE_WINDOWS`: May 2024 derecho + Hurricane Beryl,
   COAST) excluded from ALL fitting like Uri — served load ≠ demand there
   (added 2026-08-14 after review).
4. Train/test wall: nothing after 2024-12-31 enters any fit.
   2025–2026 is validation only.
5. Raw data is immutable; every derived table reproducible from raw + code.

## Zones in scope

| Zone  | Anchor metros        | Notes |
|-------|----------------------|-------|
| NCENT | DFW metroplex        | DFW dominates population |
| COAST | Houston / Harris Co. | Dewpoint is a required feature |
| SCENT | Austin + San Antonio | Separated metros — pop weighting matters most here |

FWEST/WEST (flat-load surgery) explicitly out of scope for v0.
**Superseded for 08-Y (sdalvi 2026-08-18):** all 8 weather zones in scope
(add EAST, FWEST, NORTH, SOUTH, WEST) — a study needs all 8, and the
system-wide forecast (sum of zones, validated against total system load)
is the headline deliverable. FWEST/WEST are step-jump zones; expect the
smooth-trend machinery to need a jump term there.

## Current direction — 08-Y (designed 2026-08-19, spec pending sdalvi go)

The probabilistic track's 08-X experiment ended **KILL→§8** (full record in
`docs/training_log.md`, task08x/task08x2 entries + corrections). Standing
design for the next round, per sdalvi rulings:

- **Fan × Dial × Shape**: growth fan (uncertain, integrate) × weather
  (a DIAL — sampled historical weather years, never hand-curated scenarios;
  condition on e.g. "100°F day-4 of a wave" by filtering sampled paths)
  × shape model (deterministic given weather) + weather-conditional residual.
- Growth fan = **joint 8-zone state space** on the monthly normalized size
  index: per-zone level+slope; slope shocks share a common ERCOT factor
  (ζ_z = λ_z·c_t + idio). Joint fit, not per-zone-then-shrink — the
  cross-zone covariance is what makes the summed SYSTEM distribution honest.
- **B0/B1 extend to all 8 zones + system first** — incumbent benchmark
  scorecard before any new model is scored.
- **LLWG vintages: energized series ONLY** as a candidate covariate
  (approved-to-energize / in-study = display only, never model input).
- Heat-soak / wave-day shape features: TODO backlog, not in 08-Y scope.
- Conformal recalibration wrapper: ruled out (see training_log task08x2
  correction — n=12 LOFO coverage is a mathematical identity).

## Data sources

| Source | What | Access |
|--------|------|--------|
| SQL Server `AW.dbo.ercotLoadView` | Hourly MW: `ERCOT_ALL_LD` + one `WZ_*_LD` column per weather zone; `date` + `he` (1–24, hour-ending CPT); covers back to ≥2011 | awconnect (see DB access rules) |
| ERCOT Native Load archives (ercot.com) | FALLBACK only, if a year is missing from the view | Free, annual xlsx |
| NOAA Global Hourly (ISD CSV), bucket `noaa-global-hourly-pds` | Hourly temp + dewpoint per station, anonymous HTTPS | Free |
| Census PEP 2023 county estimates (`co-est2023-alldata.csv`, static file) | County population, 254 TX counties. Replaces ACS B01003 — the ACS API now needs a key (sdalvi ruling 2026-08-14; key requested, switch back is one line) | Free |
| ERCOT county → weather-zone assignment | User-provided from internal `ercotDataDictionary` (`data/raw/crosswalk/ercot_county_weatherzone.csv`) | Internal |
| CEII (future) | NCL identification for clean organic growth | Task 07 only, NOT v0 |

Zone column mapping in `ercotLoadView` (confirmed in `powerflow_analytics/pfa/extract/load.py`):
NCENT → `WZ_NORTH_CENTRAL_LD`, COAST → `WZ_COAST_LD`, SCENT → `WZ_SOUTH_CENTRAL_LD`
(also NORTH → `WZ_NORTH_LD`, FWEST → `WZ_FAR_WEST_LD`, SOUTH → `WZ_SOUTHERN_LD`,
EAST → `WZ_EAST_LD`, WEST → `WZ_WEST_LD`). Prior art: `pfa/extract/load.py`
`get_load_window()` (windowed per-year pulls + parquet cache) — this project has
its own puller in `src/` for full-year all-zone pulls, same hygiene.

## DB access rules (borrowed from powerflow_analytics — binding here too)

- All DB access via `awconnect` with profile `read_only`; Snowflake (if ever
  needed) uses warehouse `AI_READ_ONLY`. Reuse `powerflow_analytics/pfa/config.py`'s
  `configure()` pattern.
- SQL Server queries are **strictly sequential** — ONE query at a time, never
  parallel, never fan-out. Pull one year per query.
- Extract-once, cache-first: every pull lands as parquet under `data/raw/`;
  analysis/model code reads the cache ONLY, never the DB. Re-running a pull
  must be a no-op when the cache file exists (delete the file to force refresh).
- Queries must be date-bounded (`WHERE date BETWEEN ...`) — no unbounded scans.
- Container has a hard 8 GiB cgroup memory cap — load parquet columns
  selectively, free frames aggressively.

## Division of labor (sdalvi, 2026-08-14 — overrides repo-root rule for this project)

Main session writes the code. Subagents do data verification and coverage
checks. Data/access questions go to sdalvi directly — agents must stop with
NEEDS_CONTEXT rather than improvise when a named resource is missing.

## Canonical tables
(v0: parquet + DuckDB; schemas translate 1:1 to Snowflake DDL for promotion)

### crosswalk_county_station  (static — Task 01)
county_fips varchar(5) | county_name varchar | weather_zone varchar |
population int (ACS 2023) | station_id varchar (USAF-WBAN) |
station_name varchar | dist_km float | weight float
  -- weight = population / Σ zone population over selected counties

### weather_hourly  (Task 02)
station_id | ts_local timestamp (CPT, hour-ending, matched to ERCOT) |
temp_f float | dewpoint_f float | qc_flag varchar (raw/interp/suspect)

### zone_weather_hourly  (Task 02)
weather_zone | ts_local | temp_f_popwt | dewpoint_f_popwt |
temp_f_avg24 (trailing 24h mean) | temp_f_ewm3d (EWM, halflife 36h)

### load_hourly  (Task 02)
weather_zone | ts_local (hour-ending CPT) | load_mw float |
event_flag varchar (null/uri/covid)

### size_index  (Task 03)
weather_zone | year int | normalized_gwh float |
size_idx float (base year = 1.0) | source varchar (fitted/extrapolated)

### scenario_hourly  (Task 05)
weather_zone | scenario_id varchar (e.g. wx2023_sys2026) |
ts_local (calendar of weather year) | load_mw_pred float

## Acceptance targets (v0)
- Monthly zonal energy MAPE, 2025–2026: ≤ 4% (stretch 2%)
- Annual growth-rate error per zone: ≤ 1 pp/yr
- Hourly MAPE < 10% per zone on every honest test (rolling backtest folds,
  2025–2026 wall validation, analog replays) — sdalvi 2026-08-14; keep
  iterating via scripts/experiment.py until met everywhere
- Analog-replay benchmark (src/analog.py): for the TWO closest-by-distance
  analogs per (zone, target month), |energy error| ≤ 5%; peak error is
  reported, not gated (a single analog hot day can print a peak the target
  month never saw). Run multiple target months — one month is one test.

## Compute policy (sdalvi 2026-08-14)
ALL iteration happens on the tiny efficient setup (experiment.py fast folds,
num_threads 4, this 8 GiB container). The full production training run is
DEFERRED to the large compute machine — do not run heavyweight sweeps here.

## Working preferences
- Peer-level collaboration. Ask before assuming anything not written here.
- All schemas explicit; no silent column additions.
- Each task file self-contained given this CLAUDE.md.
- Model iteration goes through `scripts/experiment.py` (fast fold, leaderboard
  in `output/experiments.csv`) and EVERY experiment gets a qualitative entry in
  `docs/training_log.md` (same tag): setup, what worked, what didn't. Winners
  are promoted via `--promote <tag>` before touching the full model.
