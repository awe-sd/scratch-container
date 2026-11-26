# Screen + deep-dive productization — design & review spec (2026-08-12)

Two features being productized from session-inline code. This doc is the grading
rubric for reviewing the implementations before they are accepted.

## Feature 1: `scripts/build_stage2_list.py` — two-step constraint screen

One command per study: `uv run powerflow_analytics/scripts/build_stage2_list.py --study <id> [--cutoff 2026-09-15]`.

Pipeline stages (each a named function, cache/CSV in → DataFrame out):

1. `constraint_directions(cache) -> Series[C -> DIR]` — mode of OUTBRANCHDIRECTION per constraint from cached outctgviol2.
2. `build_universe(cache, cutoff) -> DataFrame` — ctgviol binders (LIMVIOLPCT>=99.5) UNION LP-priced constraints; pre/post bind counts, post days, λ P50/IQR/mean.
3. `signed_impact(tofinder_summary, dirs) -> Series` — top outage-group flow share, direction-signed.
4. `bulk_dispatch_nodes(study, constraints) -> Series[NQUAL]` — ONE grouped CPNODE_SHIFTS_VIEW query (DEADBUS=0, no LZ_/WZ_, 0.03<=|SF|<=0.9).
5. `classify(row) -> class` — D bearish / C no-dispatch (flatness test: λP50 exactly 500|3500 & IQR<1; or NQUAL<2) / B baseline / A target / weak.
6. `detect_flips(df) -> DataFrame` — D members sharing an endpoint bus with post-only emergers.
7. `stage2_gate(df, flips) -> DataFrame` — share>=0.25, post_days>=3, RENT_POST>=200k, NQUAL>=2, intensity post_binds*λP50>=1000 OR flip target (flip_exempt column, visible not silent).
8. `render_html(df, cache) -> str` — the approved column set, filterable.

## Feature 2: `scripts/constraint_deep_dive.py` — per-constraint research recipe

`--study --constraint <C or line label> [repeatable] --history-start/--history-end --out`.

Four stages, each a function returning a plain dict/DataFrame consumed by a
markdown renderer:

1. `binding_conditions(...)` — fast-scan headroom × wind-region/solar history → thresholds, driver attribution, historical condition frequency (never study-run frequencies as P(bind)).
2. `dispatch_profile(...)` — qualifying relief nodes, fuel-typed, direction-corrected.
3. `price_formation(...)` — LP λ dist in binding runs, marginal units (LMP≈offer, off-limits), structural λ from DAM stacks shallow vs deep, regime attribution.
4. `flip_attribution(...)` — tofinder outage-group flow transfer between the passed constraints (only when 2+ passed).

## Extensibility requirements (the review bar)

- **Thresholds are named constants or CLI args, never inline literals** — cutoff date, 99.5 binding pct, 0.25 share, 3 post-days, $200k rent, 1000 intensity, 0.03/0.9 SF band, 500/3500 penalty tiers. Future studies WILL need different gates.
- **Stage functions are pure(ish)**: cache/CSV/paths in, frames out; no stage reads another stage's file side-effect when it can take the frame. `main()` is only orchestration + I/O, so a notebook or the Dash app can import any stage.
- **No study-specific or month-specific hardcoding**: no Sept literals except as defaults derivable from the study's SIMDATE range; no constraint IDs, ticket IDs, or one-off drops in code.
- **Reuse `pfa` modules, don't fork them**: fastscan/offer_lambda/lambda_engine/gen_mapping/buskv are the single implementations. New generic logic belongs in `pfa/analysis/`, not in the script.
- **Constraint identity through one helper** (`constraints.constraint_key` / one parse function) — no repeated ad-hoc string splitting per stage.
- **Additive output schema**: HTML/CSV columns generated from one column-spec list so adding a column is a one-line change; CSV keeps raw values (no lossy rounding) so downstream stage-2 can consume it.
- **Deep-dive stages tolerant of missing data**: no fast-scan config / no offers / no shifts → the stage reports the gap explicitly and the rest of the report still renders (no crash, no silent zero).
- **Memory discipline**: column-selective parquet loads, del/gc after big joins (<2.5GB peak).
- **SQL discipline**: single bulk Snowflake queries where possible; SQL Server sequential + scoped.

## Acceptance for this session

- build_stage2_list.py runs clean on 14412 (regression: reproduces the approved 17-row list modulo the two manual edits) and on 14431.
- constraint_deep_dive.py runs on 14412 for 35045 + 35055_A and its report answers wind/solar thresholds, dispatch, λ regimes, flip mechanism.
- Opus grading gate on both deliverables before user presentation.
