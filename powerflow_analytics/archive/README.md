# powerflow_analytics/archive

- `brandon_source_ranking.py` — one-off ranking of sources for the BRANDON_RN sink (cpnodeid 56563) from FwdAuctionDecomp marks (auction 626261); no live importer.
- `insert_brandon_sink_paths.sql` — one-off SQL appending BRANDON_RN-sink paths to AWVAL.DBO.FwdAuctionDecompByPath (ptoID 1504), written 2026-08-12.
- `rt_prices.py` — extractor for real-time settlement-point LMPs from AW.DBO.SPTHRPRICEHOURLYVIEW, written for the LMP-pinning test; no live importer.
- `value_constraint_quick.py` — the fact-sheet half of the old two-command valuation (binding run count, lambda spread, marginal units); merged into `scripts/value_constraint.py` (2026-11-27). Imports a module that no longer exists.
- `build_high_confidence_report.py` — the all-in-one report (every binder with a penalty-tier flag, realized DA/RT history, offer price, fast-scan headroom, cheapest path); replaced by the shortlist (`pfa shortlist` / `scripts/build_stage2_list.py`). Kept for reference only, not maintained (its imports may no longer resolve).
- `build_screening_report.py` — the A/B/C/D/U classification report with a step-2 valuation of class A; replaced by the shortlist, which uses the A/B/C/D/weak classification and carries the valuation columns. Kept for reference only, not maintained (its imports may no longer resolve).
- `tests/` — the unit tests of the two retired reports; not collected.
