# fast_scan/

## Purpose

Validate study shift factors (`SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW`, ERCOT
SCOPF studies) against DART actual shifts (`AW.dbo.psenShiftDef`,
`psenShiftTypeId=14`) for every "validation" topology-shift-set config of a
study. One set = one (BRANCHLABEL, CTGLABEL) pair with study topology
variants (`AW.POPT.TOPOLOGYSHIFTSET` members). Core comparison, per row:
`sign · study_psen + ref_psen(cpnode 12791) − dart_psen`, both signs tried,
better fit kept per topology-hour (never per config — see gotchas).

## Division of labor

Same as repo root: Sonnet codes (all edits/debugging/new scripts), Fable
(main session) plans/grades only, Opus grading gate before any deliverable
is presented to the user.

## Pipeline / how to run

Run from the repo root with `uv run --project <repo root> python ...` (`pfa` and `awconnect` are installed editable in the root venv; no `sys.path` tricks). Scripts import siblings and `shift_common.py` as plain modules (script folder is on `sys.path`). Reference run: study 14218, validation sets created 2026-09-11+, June 2026 window. The window and output sub-folder are always explicit arguments; nothing defaults to a month.

```bash
uv run --project . python fast_scan/compare_validation_shifts.py --study 14218 --created-after 2026-09-11 --date-from 2026-06-01 --date-to 2026-06-30 --workers 4
uv run --project . python fast_scan/mismatch_analysis.py --study 14218 --created-after 2026-09-11 --date-from 2026-06-01 --date-to 2026-06-30 --out-subdir june
uv run --project . python fast_scan/build_mismatch_report.py --study 14218 --created-after 2026-09-11 --date-from 2026-06-01 --date-to 2026-06-30 --out-subdir june
uv run --project . python fast_scan/build_validation_shift_report.py --study 14218 --created-after 2026-09-11
# single-constraint drilldowns
uv run --project . python fast_scan/shift_constraint_deep_dive.py --study 14218 --branch MDOPHR99A --ctg DWAP_OB5 --date-from 2026-06-01 --date-to 2026-06-30 --out-subdir june
uv run --project . python fast_scan/bad_hour_detail.py --study 14218 --branch MDOPHR99A --ctg DWAP_OB5 --set-id 112431 --date-from 2026-06-01 --date-to 2026-06-30 --out-subdir june
```

Scripts, in pipeline order:
- `shift_common.py` — shared module: `get_configs`/`get_config_labels` (validation-set lookup off `TOPOLOGYSHIFTSETDEF`), `REFERENCE_CPNODEID` (12791), `dart_chain_sql` (the one builder of the DART lookup chain psenShiftDef -> [PSENSHIFT] -> congDefConstraint -> congDefMonitor -> congDefContingency -> branchMonitored -> branch -> [CPNODE]), output-folder helpers (`output_dir`, `cache_dir`), `window_label`.
- `compare_validation_shifts.py` (stage 1) — args `--study`, `--created-after` (required); `--date-from/--date-to`, `--out-subdir` (optional; none = study root), `--sets id1,id2`, `--limit`, `--workers`, `--no-cache`. Pulls raw joined rows/set (cached to `cache/<set_id>[_<date_from>_<date_to>].parquet`), fits sign, writes `summary.csv`/`per_topology.parquet`/`per_cpnode.parquet`/`skipped.csv`. Even with a warm cache it still issues three small DART/study metadata queries per set (date range, duplicate check, member count); the duplicate check joins `AW.DBO.PSENSHIFT`, so it fails per set if the role cannot read that table (see gotchas). Output row order of the two parquet files depends on thread completion order.
- `mismatch_analysis.py` (stage 2) — args `--study`, `--created-after`, `--date-from`, `--date-to`, `--out-subdir` (all required); `--rank-tol` 0.01, `--node-rate` 0.10, `--hour-bad-share` 0.05, `--sign-guard` 0.02. Re-reads the per-set cache (window must match stage 1): REF_OFFSET correction, per-topology-hour sign resolution, row-level mismatch classification.
- `build_mismatch_report.py` (stage 3) — args `--study`, `--created-after`, `--date-from`, `--date-to`, `--out-subdir` (all required). Reads the stage-2 outputs, renders `report.html`; the dates only feed the title.
- `build_validation_shift_report.py` — args `--study`, `--created-after` (required), `--out-subdir` (optional). HTML report of the stage-1 outputs.
- `shift_constraint_deep_dive.py` — args `--study --branch --ctg --date-from --date-to --out-subdir` (required), `--check-id`, `--sign-guard`, `--no-cache`. One constraint: per-topology-hour table, top nodes, load-zone/hub comparison (own deadbus-free pull), DART congConstraintID count. A few live queries.
- `bad_hour_detail.py` — args `--study --branch --ctg --set-id --date-from --date-to --out-subdir` (required), `--rank-tol`, `--sign-guard`. Worst clock-hour drilldown from the cache only; writes `deep_dive_<branch>_<ctg>_bad_hour.csv`.
- `archive/shift_benchmarking.py` — legacy notebook conversion, imports `AWUtil`/`AWDecomp`, **not installed in this venv**; do not run. Reference for the original join logic.
- `tests/` — pytest, no database: `uv run --project <repo root> python -m pytest fast_scan/tests -q` (covers sign/offset resolution, mismatch classifiers and thresholds, the DART chain builder). Not yet in the root `testpaths`.

## Output layout

`fast_scan/output/validation_shift_compare/<study>/` (git-ignored)
- `cache/*.parquet` — raw per-set pulls, shared across subdirs/runs
- `summary.csv`/`per_topology.parquet`/`per_cpnode.parquet`/`skipped.csv`/`report.html` — a `compare_validation_shifts.py` run with no `--out-subdir`
- `<out_subdir>/` (e.g. `june/`) — full mismatch pipeline output: `mismatch_summary.csv` (per-set classification: OK/LOCALIZED_NODES/LOCALIZED_TOPOLOGIES/SYSTEMATIC/DIFFUSE/SIGN_UNRESOLVED), `topology_hours.parquet`/`bad_topology_hours.csv` (topology-hour grain, severity-sorted), `mismatch_rows.parquet` (raw bad rows), `node_day_matrix.csv`/`day_summary.csv`/`node_summary.csv` (node/day rollups: SYSTEMIC/CONSTRAINT_SPECIFIC/MIXED), `per_topology_detail.parquet`/`per_node_detail.parquet`, `dup_fanout_flags.csv`, `mismatch_params.json` (CLI thresholds used), `report.html` (final deliverable).

## Data gotchas

- `AW.POPT.TOPOLOGYSHIFTSETDEF` = one row/set (STUDYID, BRANCHLABEL, CTGLABEL, DIRECTION, NOTES, CREATEDATE); `TOPOLOGYSHIFTSET` = members (TOPOLOGYSHIFTSETID, PSENSHIFTID, TOPOLOGYID). Study 14218 validation: CREATEDATE >= 2026-09-11, `get_configs` returns 110 sets (none with INTERFACENAME, none with null CTGLABEL), ~885 members each. Of those, 96 have a June-window cache file (89 produce a mismatch summary row; the rest have no hour overlap, no study data, or no cache).
- `AW.FLOW_ANALYSIS.FAST_SCAN_CONFIG`/`FAST_SCAN_RESULTS` are readable by the read-only role as of 2026-11-26 (`AWDEV.FLOW_ANALYSIS` was renamed `_DEPRECATED`). This pipeline still drives configs off `TOPOLOGYSHIFTSETDEF` directly.
- As of 2026-11-26 the read-only role (`AI_READ_ONLY`) gets "does not exist or not authorized" on `AW.DBO.PSENSHIFT`, so everything that joins DART shifts (stage-1 duplicate check and pulls, deep dive) fails; stages 2-3, the stage-1 report and `bad_hour_detail.py` only need the cache and `TOPOLOGYSHIFTSETDEF`.
- **Sign resolved per topology, never per config**: same branch/ctg label maps to different DART `congConstraintID` versions over time with opposite orientation (e.g. set 112443 FORTMA_YELWJC11/DBIGKEN5: congConstraintID 96849 → −1, 163597 → +1). A per-config fit fabricates 2×|psens| errors. `DIRECTION`/`cv.direction` do NOT predict it. Guard: `SIGN_UNRESOLVED` when `min(MAE+, MAE−) > 0.02`.
- `AW.dbo.PSENSHIFT` has bit-identical duplicate rows for some psenshiftids (85019908: 2222 rows / 1111 cpnodes) — both CTEs `QUALIFY ROW_NUMBER()` dedupe on this.
- Multiple study topology **variants** (different TOPOLOGYID/RUNID) can share one clock-hour; DART has one psenshiftid per constraint-hour — always report both grains: topology-variant × hour vs. distinct clock-hour.
- Constant reference-normalization offsets exist per config (REF_OFFSET: `|bias| > 0.8·MAE` and ≥90% of nodes within ±0.002 of bias, e.g. 6945_A/SRGRMGS5 bias −0.0072) — subtract before counting mismatches.
- Tolerance 0.0005 saturates (37% of rows, all nodes) — rank at 0.01 instead. With ~7–20 clock-hours/constraint/month, "nodes off in ≥10% of hours" is cleared by one bad hour — rank by topology-hour severity (max nodes off in a bad hour), not raw node counts.
- DART only has shifts for hours the constraint was active — low coverage expected. Sets with no overlapping hour are `NO_HOUR_OVERLAP` (DART rows do exist, just not at the study's simulated hours).
- Study `BRANCHLABEL` == `AW.dbo.branch.branchName` exactly — use equality, not `LIKE` (`_` is a SQL wildcard).
- `SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW.deadbus` is not boolean (values seen: 0, 4). All/most `LZ_*`/`HB_*` aggregate cpnodes (load zones, hubs) are stamped `deadbus=4` — the standard `pull_joined_raw` `deadbus=0` filter silently drops 9-15 of the 15 LZ/HB names (only HB_HOUSTON/HB_SOUTH/HB_WEST/LZ_AEN/LZ_CPS/LZ_LCRA have deadbus=0 rows, and even those are missing a handful of topology-hours). `shift_constraint_deep_dive.py::pull_zone_raw` re-pulls LZ_/HB_ rows without the deadbus filter (preferring deadbus=0 when both exist) to get the full zone comparison.
