# powerflow_analytics

SCOPF study results → CRR opportunity finder. See `CLAUDE.md` for conventions
and `docs/superpowers/specs/2026-08-10-powerflow-analytics-design.md` for the design.

## Workflow

1. Pull a study into the local cache (Snowflake, one-time per study):
   `uv run powerflow_analytics/scripts/pull_study.py --study 14411`
2. Analyze it (writes CSVs to `output/study_14411/`):
   `uv run powerflow_analytics/scripts/build_report.py --study 14411 --tickets`
3. Dashboard (reads only local files):
   `uv run powerflow_analytics/app/app.py` → http://127.0.0.1:8050
   - **Explorer**: ranked binding constraints; click a row for binding-hours
     profile, marginal units, and tofinder outage evidence.
   - **Comparison**: constraint deltas between two analyzed studies.

## Tests

`uv run python -m pytest powerflow_analytics/tests/ -q`
