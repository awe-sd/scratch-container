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

Three stages, run in order, via `uv run --project powerflow_analytics`
(repo root; `pfa.sf.query` lives there). Reference run — study 14218,
validation sets created 2026-09-11+, June 2026 window:

```bash
uv run --project powerflow_analytics python fast_scan/compare_validation_shifts.py --study 14218 --created-after 2026-09-11 --date-from 2026-06-01 --date-to 2026-06-30 --workers 4
uv run --project powerflow_analytics python fast_scan/mismatch_analysis.py --study 14218 --created-after 2026-09-11 --date-from 2026-06-01 --date-to 2026-06-30 --out-subdir june
uv run --project powerflow_analytics python fast_scan/build_mismatch_report.py --study 14218 --created-after 2026-09-11 --out-subdir june
```

- `compare_validation_shifts.py` — pulls raw joined rows/set (cached to `cache/<set_id>[_<date_from>_<date_to>].parquet`), fits sign, writes `summary.csv`/`per_topology.parquet`/`per_cpnode.parquet` (study root or `--out-subdir`; cache always at study root). `--sets id1,id2` restricts; `--limit` caps count; `--no-cache` forces re-pull.
- `mismatch_analysis.py` — re-reads the same per-set cache (must match `--date-from`/`--date-to`), does row-level mismatch/classification: REF_OFFSET correction, per-topology-hour sign resolution (`--sign-guard`, default 0.02), thresholds (`--rank-tol`, `--node-rate`, `--hour-bad-share`). Writes under `--out-subdir` (default `june`).
- `build_mismatch_report.py` — reads only `--out-subdir` outputs above, renders `report.html` (sortable tables) into the same subdir.
- `archive/shift_benchmarking.py` — legacy notebook conversion, imports `AWUtil`/`AWDecomp`, **not installed in this venv**; do not run. Kept as reference for the original join logic `compare_validation_shifts.py` reused (see that script's docstring).

## Output layout

`fast_scan/output/validation_shift_compare/<study>/`
- `cache/*.parquet` — raw per-set pulls, shared across subdirs/runs
- `summary.csv`/`per_topology.parquet`/`per_cpnode.parquet`/`skipped.csv`/`report.html` — a `compare_validation_shifts.py` run with no `--out-subdir`
- `<out_subdir>/` (e.g. `june/`) — full mismatch pipeline output: `mismatch_summary.csv` (per-set classification: OK/LOCALIZED_NODES/LOCALIZED_TOPOLOGIES/SYSTEMATIC/DIFFUSE/SIGN_UNRESOLVED), `topology_hours.parquet`/`bad_topology_hours.csv` (topology-hour grain, severity-sorted), `mismatch_rows.parquet` (raw bad rows), `node_day_matrix.csv`/`day_summary.csv`/`node_summary.csv` (node/day rollups: SYSTEMIC/CONSTRAINT_SPECIFIC/MIXED), `per_topology_detail.parquet`/`per_node_detail.parquet`, `dup_fanout_flags.csv`, `mismatch_params.json` (CLI thresholds used), `report.html` (final deliverable).

## Data gotchas

- `AW.POPT.TOPOLOGYSHIFTSETDEF` = one row/set (STUDYID, BRANCHLABEL, CTGLABEL, DIRECTION, NOTES, CREATEDATE); `TOPOLOGYSHIFTSET` = members (TOPOLOGYSHIFTSETID, PSENSHIFTID, TOPOLOGYID). Study 14218 validation: CREATEDATE >= 2026-09-11, 110 sets, ~885 members each.
- `AW.FLOW_ANALYSIS.FAST_SCAN_CONFIG`/`SP_BENCHMARK_VALIDATION_SCANS` not accessible to this container's Snowflake role — drive configs off `TOPOLOGYSHIFTSETDEF` directly.
- **Sign resolved per topology, never per config**: same branch/ctg label maps to different DART `congConstraintID` versions over time with opposite orientation (e.g. set 112443 FORTMA_YELWJC11/DBIGKEN5: congConstraintID 96849 → −1, 163597 → +1). A per-config fit fabricates 2×|psens| errors. `DIRECTION`/`cv.direction` do NOT predict it. Guard: `SIGN_UNRESOLVED` when `min(MAE+, MAE−) > 0.02`.
- `AW.dbo.PSENSHIFT` has bit-identical duplicate rows for some psenshiftids (85019908: 2222 rows / 1111 cpnodes) — both CTEs `QUALIFY ROW_NUMBER()` dedupe on this.
- Multiple study topology **variants** (different TOPOLOGYID/RUNID) can share one clock-hour; DART has one psenshiftid per constraint-hour — always report both grains: topology-variant × hour vs. distinct clock-hour.
- Constant reference-normalization offsets exist per config (REF_OFFSET: `|bias| > 0.8·MAE` and ≥90% of nodes within ±0.002 of bias, e.g. 6945_A/SRGRMGS5 bias −0.0072) — subtract before counting mismatches.
- Tolerance 0.0005 saturates (37% of rows, all nodes) — rank at 0.01 instead. With ~7–20 clock-hours/constraint/month, "nodes off in ≥10% of hours" is cleared by one bad hour — rank by topology-hour severity (max nodes off in a bad hour), not raw node counts.
- DART only has shifts for hours the constraint was active — low coverage expected. Sets with no overlapping hour are `NO_HOUR_OVERLAP` (DART rows do exist, just not at the study's simulated hours).
- Study `BRANCHLABEL` == `AW.dbo.branch.branchName` exactly — use equality, not `LIKE` (`_` is a SQL wildcard).
- `SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW.deadbus` is not boolean (values seen: 0, 4). All/most `LZ_*`/`HB_*` aggregate cpnodes (load zones, hubs) are stamped `deadbus=4` — the standard `pull_joined_raw` `deadbus=0` filter silently drops 9-15 of the 15 LZ/HB names (only HB_HOUSTON/HB_SOUTH/HB_WEST/LZ_AEN/LZ_CPS/LZ_LCRA have deadbus=0 rows, and even those are missing a handful of topology-hours). `constraint_deep_dive.py::pull_zone_raw` re-pulls LZ_/HB_ rows without the deadbus filter (preferring deadbus=0 when both exist) to get the full zone comparison.
