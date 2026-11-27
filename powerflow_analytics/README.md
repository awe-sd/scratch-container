# powerflow_analytics

SCOPF study results → CRR opportunity finder. See `CLAUDE.md` for conventions
(the design spec no longer exists; see the tracking issue "Clean-up of powerflow_analytics and fast_scan" on awe-sd/scratch-container).

## Workflow

1. Pull a study into the local cache (Snowflake, one-time per study):
   `uv run powerflow_analytics/scripts/pull_study.py --study 14411`
2. Analyze it (writes CSVs to `output/study_14411/`):
   `uv run powerflow_analytics/scripts/build_report.py --study 14411 --cutoff 2026-09-15 --tickets`
3. Dashboard (reads only local files):
   `uv run powerflow_analytics/app/app.py` → http://127.0.0.1:8050
   - **Explorer**: ranked binding constraints; click a row for binding-hours
     profile, marginal units, and tofinder outage evidence.
   - **Comparison**: constraint deltas between two analyzed studies.

4. Value one constraint (fact sheet, then the monthly on-peak $/MWh mark when `--window` is given):
   `uv run powerflow_analytics/scripts/value_constraint.py --study 14412 --constraint "1436-2081-1@DWCSRAM5" --month 2026-09 --window 2026-09-16 2026-10-02`
   The two sections use different binding definitions (labelled in the output).

## Tests

`uv run python -m pytest powerflow_analytics/tests/ -q`
