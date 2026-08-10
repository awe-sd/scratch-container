# powerflow_analytics — SCOPF results → CRR opportunity finder

**Date:** 2026-08-10 · **Branch:** `powerflow-analytics` · **Dev study:** 14411 (SEP2026_V6, ERCOT, ptoid 1504) · **Target:** monthly CRR auctions

## Purpose

Read SCOPF simulation output for a given `studyid` from Snowflake (AWOPF), identify binding constraints and rank them as CRR trading targets, explain each constraint (marginal units, outage/topology driver), and surface everything in a reusable Python package + Dash dashboard. Fast-scan / path-optimization overlay comes later (permissions pending).

## Data sources (verified 2026-08-09)

| Source | Table | Notes |
|---|---|---|
| Snowflake AWOPF.DBO | OPFSTUDY, OPFRUN, OPFRUNSCENARIO | STUDYID → RUNID (study 14411: 210 runs, RUNID 1946934–1947143, 11 scenarios/run). All output tables key on RUNID only. |
| Snowflake AWOPF.DBO | OUTCTGVIOL2 | Binding/violated constraints; self-describing (FROMNAME/TONAME/CTGLABEL inline). ~1.16M rows for study 14411. |
| Snowflake AWOPF.DBO | OUTBRANCH2 | Branch flows + MARGCOSTMVA (shadow price), OPFBINDING. v1 OUTBRANCH is EMPTY for this study — use the "2" tables. Schema to verify on first pull. |
| Snowflake AWOPF.DBO | OUTINTERFACE2 | Interface flows; LIMITUSED=99999 sentinel = unbounded. |
| Snowflake AWOPF.DBO | OUTGEN2 | Gen dispatch; LPDELTAMW = SCOPF redispatch; GENUNITID is NULL — identity via (BUSNUM, ID) → OUTGENREF. |
| Snowflake AWOPF.DBO | OUTTOFINDERMAX2 | Outage-group impact per constraint (FLOWDELTA, OUTAGE_GROUP text). |
| Snowflake AWOPF.DBO | OUTGENREF, OUTBRANCHREF | ID → name bridges. OUTCTGREF has no ERCOT rows; not needed. |
| Snowflake SHIFT_FACTORS.DBO | CPNODE_SHIFTS_VIEW, BUS_SHIFTS_VIEW | **Currently not authorized to the read_only role** — user resolving. Reader must be schema-tolerant; expected shape ≈ DEVICE_SHIFTS (keys ISOMARKETID, STUDYID, TOPOLOGYID, PSENSHIFTID). |
| Snowflake AWDEV.FLOW_ANALYSIS | FAST_SCAN_RESULTS (+ path-opt) | **Not authorized** — stub interface only for now. |
| Snowflake AW.DBO | ERCOT60DDAMGENRESOURCE | DAM offer curves; join to CRR space via SETTLEMENTPOINTNAME. Valuation layer — deferred. |
| Snowflake AWDEV.DBO | GENUNIT | Gen master (GENUNITID). |
| SQL Server AW.dbo | toAllIsos (+ to* family) | Outage tickets. **Targeted single-branch lookups only (BranchId/teid + study window); never bulk queries.** |

## Architecture

```
powerflow_analytics/
├── CLAUDE.md
├── pfa/
│   ├── config.py              # study id, cache paths, warehouse (AI_READ_ONLY), profile read_only
│   ├── extract/               # readers → parquet cache (each validates expected columns, fails loudly)
│   │   ├── study.py           # OPFSTUDY/OPFRUN/OPFRUNSCENARIO
│   │   ├── results.py         # OUTCTGVIOL2, OUTINTERFACE2, OUTBRANCH2, OUTGEN2, OUTTOFINDERMAX2
│   │   ├── shifts.py          # CPNODE_SHIFTS_VIEW / BUS_SHIFTS_VIEW (schema-tolerant; blocked)
│   │   ├── gen_mapping.py     # OUTGENREF, GENUNIT, ERCOT60DDAMGENRESOURCE (offer reader stubbed)
│   │   └── outages.py         # toAllIsos targeted lookups
│   ├── cache.py               # cache/study_<id>/<table>.parquet + DuckDB view layer
│   ├── analysis/
│   │   ├── constraints.py     # binding constraints: freq, % of runs/scenarios, shadow price stats, rank
│   │   ├── marginal_units.py  # units resolving each constraint: |shift factor| × |LPDELTAMW| (LPDELTAMW-only fallback until shift views open)
│   │   ├── drivers.py         # tofinder + outage-ticket classification: outage-driven / topology-suspect / baseline
│   │   └── fastscan.py        # interface stub (permissions pending)
│   └── report.py              # per-study CSV/HTML summary
├── app/                       # Dash: pages/explorer.py (ranked grid + drill-down), pages/comparison.py
└── scripts/ pull_study.py, build_report.py
```

## Key decisions

- **Constraint identity** = (FROMNUM, TONUM, CKT, CTGLABEL); human names inline from the "2" tables.
- **Extract once, analyze locally**: `pull_study.py --study 14411` resolves RUNIDs then pulls OUT* slices to parquet; analysis and Dash read only the cache (DuckDB). `--refresh` re-pulls.
- **Marginal units** ranked by redispatch response (LPDELTAMW) weighted by constraint shift factor once views are accessible; identifies who resolves the constraint. Offer-curve valuation is a later layer.
- **Driver classification** per constraint from OUTTOFINDERMAX2 top impactors, verified against toAllIsos tickets in the study window (Sept 2026): `outage-driven` / `topology-suspect` (impact but no ticket) / `baseline`.
- **Dash never queries Snowflake in callbacks** — cache only.

## Error handling

- Column validation on every extract; loud failure with observed schema (defends against renames like BUS_SHIFTS → DEVICE_SHIFTS).
- SQL Server reader enforces parameterized single-entity lookups.
- Missing-permission tables degrade gracefully: analysis marks affected columns as unavailable rather than crashing.

## Testing

- pytest unit tests for analysis functions on small fixture parquet slices.
- Extract layer smoke-tested against study 14411.

## Build order

1. Scaffold + extract/cache + `pull_study.py` (study 14411)
2. `constraints.py` + ranked-constraint report
3. `marginal_units.py` (LPDELTAMW fallback until shift views authorized)
4. `drivers.py` (tofinder + toAllIsos)
5. Dash explorer, then comparison page
6. `fastscan.py` when FLOW_ANALYSIS access lands
