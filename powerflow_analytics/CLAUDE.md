# powerflow_analytics

Reads SCOPF study output (Snowflake AWOPF) and finds CRR trading opportunities:
binding constraints → marginal units → outage/topology driver → (later) fast-scan
headroom + path optimization. Design spec: `docs/superpowers/specs/2026-08-10-powerflow-analytics-design.md`.

## Conventions

- All DB access via `awconnect` with profile `read_only`, Snowflake warehouse `AI_READ_ONLY` (`pfa/config.py`).
- Extract once per study: `uv run powerflow_analytics/scripts/pull_study.py --study <id>` → parquet in `cache/study_<id>/` (gitignored). Analysis and Dash read the cache only — never Snowflake in callbacks.
- Analyze: `uv run powerflow_analytics/scripts/build_report.py --study <id> [--tickets]` → CSVs in `output/study_<id>/`.
- SQL Server (`AW.dbo.toAllIsos`) gets ONLY targeted single-branch lookups (`pfa/extract/outages.py`) — never bulk queries.
- Constraint identity = (FROMNUM, TONUM, CKT, CTGLABEL). Use the `*2` output tables; v1 OUTBRANCH is empty for recent studies, and OUTGEN2.GENUNITID is NULL — gen identity routes (BUSNUM, ID) → OUTGENREF → AWDEV.DBO.GENUNIT.
- Binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2 (SCOPF holds constraints at ~100; >100 = unresolved violation). OPFBINDING/MARGCOSTMVA in OUTBRANCH2 are only set for base-case (pre-ctg) binders.

## Known blockers (2026-08-10)

- `SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW` / `BUS_SHIFTS_VIEW` and `AWDEV.FLOW_ANALYSIS.*`
  are not authorized to the read_only role yet (user resolving). `pfa/extract/shifts.py`
  probes and returns None; marginal-unit analysis falls back to differential LPDELTAMW.
