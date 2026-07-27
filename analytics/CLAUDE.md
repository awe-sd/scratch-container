# CLAUDE.md — `analytics/` (analytics-dev side project)

Read this before touching anything under `analytics/`.

## Purpose

Analysis-focused ERCOT side project (isomarketid = 6): transmission-constraint
congestion, wind flow-impact decomposition, RT dynamic line-rating vs weather,
and load/price relationships. Deliverables are **plotly HTML plots + CSVs** for
the user to open in VS Code — not a production pipeline.

## Hard rules

- **Read-only against the DB. Never write.** Only `SELECT`. Never run
  `INSERT`/`UPDATE`/`CREATE`/`writeDF`/`dfInsert`. (The user once pasted an
  `INSERT INTO AW.dbo.psenShiftDef ... VALUES(0,0,...)` — that was only to show
  the column layout; it must never be executed.)
- **Fetch once into parquet, then analyze locally.** All DB pulls cache to
  `analytics/data/*.parquet` (gitignored). Re-running a build reads the cache.
- Run everything through uv from the repo root context:
  `uv run --project /workspaces/scratch-workspace analytics/scripts/<name>.py`
  (a stray `VIRTUAL_ENV` warning is harmless). pandas / pyarrow / plotly /
  awconnect are installed there.
- `awconnect.configure("read_only")` once at the top of every script.
  SQL Server: `from awconnect import db; db.getDfFromAwDb(sql)`. Snowflake:
  `from awconnect import snowflake; snowflake.performQuery(dbName="AW", sqlQuery=..., warehouse=snowflake.READ_ONLY_WH)`
  (do NOT use `performQuery_Async` — its return handling is broken here).

## Worktree + plot delivery

- This branch's worktree lives at `/workspaces/scratch-workspace/.claude/worktrees/analytics-dev`
  (under `.claude/worktrees/`, gitignored on master) so it's visible/switchable in VS Code.
- Canonical outputs are committed under `analytics/output/`. They are ALSO copied to
  `/workspaces/scratch-workspace/analytics-plots/` as a view-only convenience — that
  folder is untracked and can vanish on a workspace reset; the committed copies are truth.
- After building a plot: copy the HTML(+CSV) to `analytics-plots/` and commit the
  script + output on `analytics-dev`.

## Layout

- `scripts/` — checked-in scripts (fetch / explore / analyze / build). Never `/tmp`.
- `data/` — parquet caches of DB pulls (gitignored). `analytics/scripts/fetch_data.py`
  does the original one-time constraint/load/wind/solar fetch.
- `output/` — committed HTML plots + CSVs.

## Scripts

Exploration (schema discovery, safe to re-run): `explore_market_schema*.py`,
`explore_shift_factors_schema*.py`, `explore_rating_temp_schema.py`,
`explore_6437_surry.py`, `explore_thm_35055.py`, `explore_thm_genunit.py`.

Analysis / builds:
- `analyze_net_load_constraints.py` — rank summer days by peak net load
  (load−wind−solar); score constraints active on top days → `output/august_watchlist.csv`
  + `SUMMARY.md`. Constraint naming variants deduped to `elem|contingency` by parsing
  `isoConstraintName`.
- `analyze_6945_wind_skew.py` — 6945 (MGSES→CATSW) binding vs West/Panhandle wind skew
  (summer congHrPrice). Finding: binds on LOW West wind / high Pan-minus-West spread /
  LOW West-zone load / high net load.
- `fetch_sced_wind_augusts.py` + `build_aug_wind_impact_6945.py` — West-vs-Panhandle
  wind flow-impact on 6945 across Augusts 2021-2025. contribution = SCED BasePoint ×
  PSENS (psenShiftID 86037069). Shows ALL hourly data (one full-month panel per year);
  top row = two side-by-side summary panels (mean/P90 | %net-loaded vs %net-relieved).
  Supporting: `fetch_sced_6945_*.py`, `verify_psen_6945.py`, `pick_may_psen_and_compare.py`.
- `build_rating_temp_plot.py` — **parameterized** emergency-2hr RT-rating vs local temp
  plots. Edit the `CONFIGS` list (dict per element: elem teid, station, temp_start,
  labels, optional temperature `schedule`, output basename). Design: one dot/hour colored
  by month; two panels on-peak **HE 7-22** / off-peak **HE 23-6** (classified by the
  observation's clock hour, NOT +1); median-per-5°F line; optional published temp-schedule
  line; **composing Year+Month filters** via injected JS `<select>` controls + per-month
  proxy legend traces (plotly's native dropdowns can't AND-compose). 6945 config
  (`_FROZEN_6945`) is intentionally NOT rebuilt — its committed plot must not be overwritten.
- `build_supply_stack_constraint.py` — **supply stack behind a constraint** from SCED
  offer curves (`isoErcotScedGenResource.CurveMW/CurvePrice1..15`, cumulative → diffed to
  incremental tranches). Resources "behind" the constraint = signed shift ≥ threshold on
  its psenShiftID (`psenShiftView`, `psen*psenShiftSign`). One HTML, two panels: **A** a
  single SCED interval (ON units, merit order; marginal unit = interior-dispatch unit
  LSL<BP<HSL, starred + named), **B** average offer stack over a period+HE set (diff per
  (unit,interval) → pool → 1/N weight → cumsum). RT energy price = `ercotLambda.SystemLambda`
  drawn as a horizontal ref (renewable offers sit far below it — that gap = shift×shadow-price
  congestion, not a bug). Config in `CONFIGS` (psenShiftID, threshold, single_ts, period +
  period_HEs, out). Built: 35055 (SAMSW→VENSW, psen 87025608, 2026-05-05 14:40 + May-2026
  HE 12–16). No 5-min RT shadow-price table exists (`ftrResult*` are FTR-auction; congHrPrice
  is hourly).
- `build_supply_stack_shift_weighted.py` — supply stack with **x = cumulative (offered MW ×
  signed shift)** = MW of constraint loading (vs raw offered MW). Compares the SAME gen stack
  (2026-05-05 14:40) under two shift vectors — PRE `75138717` vs POST `87025608` — to isolate a
  topology change. NON-thermal only (denylist: everything except CLLIG/CCGT*/SCGT*/GS*/NUC/DSL);
  per-gen-type legend groups (Combined/PVGR/WIND/HYDRO…) with `groupclick='togglegroup'` so you
  click a type to show/hide. Finding: loading behind 35055 fell −30% (2,570→1,798 MW) post-topology.
- `analyze_thermal_behind_35055.py` (+ `fetch_thm_35055_vectors.py`, `explore_thm_*.py`) —
  thermal gens electrically behind 35055 under the current shift; explains the 859→109 footprint
  collapse between the two shift vectors (same node universe, sensitivity localized meshed→radial);
  summer-2025 run behavior (gas CCGTs near-baseload, Sandy Creek coal offline) + load correlation.
- `analyze_thermal_sink_35055_runfreq.py` — sink-side (VENSW/DFW, negative shift) thermal fleet
  run-frequency for summer 2025 (the relief side; ~11 GW of gas that actually runs).
- `analyze_july_hot_constraints.py` — ranks July-2026 operating days by **peak net load**
  (load−wind−solar, RT actuals), then lists every RT-binding constraint on the top-N days
  (`congHrPrice isomarketid=6, priceTypeID=2, congTypeID=1`), deduped to `elem|contingency`, plus a
  recurring rollup (`>=2` hot days = August watch-list). Keyed on `awDateID`.
- `build_houston_vs_ntx_temp.py` — Houston (KIAH) vs avg North-TX (DFW metro) Aug temps.
- `build_netload_vs_price.py` — effective net load vs `ercotLambda.SystemLambda` (RT
  energy price), summer 2025.
- `analysis_common.py` — shared loaders: `hourly_net_load()`, `wind_by_region()`,
  constraint-name parsing, date-window helpers. **Build/analyze scripts import siblings by
  same-directory path** (`analysis_common`, `build_supply_stack_constraint`), so the scripts dir
  is kept flat + prefix-organized (`explore_`/`fetch_`/`analyze_`/`build_`) rather than nested.

## Key data gotchas (see also the project memory)

- One physical constraint = MANY `congConstraintID`s (naming variants); dedupe via parsed
  `elem|contingency`.
- `ercotRtDynamicRatingTEIDDef.FromStationID/ToStationID` hold station **name strings**, not
  ids. Look elements up by `EquipmentID` (ERCOT line code, e.g. '6945','587').
- **SCED Gen Resource is a 60-day disclosure** — `isoErcotScedGenResource` stops ~today−60d
  (both Snowflake and SQL Server). Recent months unavailable; historical Augusts are fine.
- `ercotWindRegionHourly` `isActual=1` rows stop 2026-05-14, but the forecast rows after
  that sum 1:1 to actual ERCOT total wind — safe to use as actuals.
- **`congHrPrice` is multi-ISO — ALWAYS filter `isomarketid = 6`** or you get PJM/MISO names
  (Cayuga, Sussex…) mixed in. RT binding = `priceTypeID=2, congTypeID=1`; `Price` = shadow price.
  Available near-real-time (NOT 60-day lagged like SCED gen). `dt` is tz-aware; key on `awDateID`
  (`awDate.date`) for a clean ERCOT operating day across load/wind/solar/congestion.
- Wind/solar actual totals: `windGenAct`/`solarGenAct` `isoZoneID=67` (ERCOT_ALL), `priceTypeID=2`
  (=RT actual; join `awDate` on `awDateID` for the date). **Net-load peak is the EVENING ramp**
  (solar → ~0, load still high), NOT the afternoon load peak — e.g. 2026-07-06 peak net load 63.9 GW
  at HE21 vs peak load 83.2 GW at HE17 (net only 49.6 GW there).
- Dead/stale: `windGenActByWeatherZone`/`solarGenActByWeatherZone` (stop 2025-01),
  `ercotCongConstRecord`/`ercot_sppCongConstRecord` (notes end 2020).
- Weather temp history starts ~2022-05.
