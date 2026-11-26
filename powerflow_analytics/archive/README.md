# powerflow_analytics/archive

- `brandon_source_ranking.py` — one-off ranking of sources for the BRANDON_RN sink (cpnodeid 56563) from FwdAuctionDecomp marks (auction 626261); no live importer.
- `insert_brandon_sink_paths.sql` — one-off SQL appending BRANDON_RN-sink paths to AWVAL.DBO.FwdAuctionDecompByPath (ptoID 1504), written 2026-08-12.
- `rt_prices.py` — extractor for real-time settlement-point LMPs from AW.DBO.SPTHRPRICEHOURLYVIEW, written for the LMP-pinning test; no live importer.
