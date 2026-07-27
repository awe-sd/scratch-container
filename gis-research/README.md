# gis-research

Research on the ERCOT GIS (Generation Interconnection Status) monthly report.

## Source

**SQL Server `AW.dbo`** (read-only via `awconnect.db`). These objects are **not**
accessible from Snowflake for the agent's read-only role (`AW.DBO.ERCOTGENERATIONINTERCONNECT`
returns "does not exist or not authorized"), so SQL Server is the source of truth here.

| Object | Type | Cols | Rows |
|---|---|---|---|
| `ercotGenerationInterconnect` | BASE TABLE | 43 | 121,354 |
| `ercotGenerationInterconnectView` | VIEW | 38 | 121,354 |

The view exposes the same rows as the base table but drops 5 columns:
`approvalDateForSubmissionOfProofOfSiteControl`, `economyStudyRequired`,
`colocatedFlag`, `modelReadyDate`, `isSmall`.

Grain: one row per (`INR` project, `fileDate` monthly snapshot). 3,854 distinct
`INR` projects; `fileDate` spans 2014-05-01 → 2026-06-01.

## Scripts (`scripts/`)

- `explore_gis_schema.py` — columns, row counts, sample for both objects (SQL Server).
- `find_gis_objects.py` — locates the GIS objects across Snowflake databases (used to
  confirm they are not in Snowflake for the read-only role).
- `download_gis_parquet.py` — pulls all rows of both objects and writes parquet to `data/`.
- `build_queue_report.py` — builds a self-contained interactive HTML queue report from
  the base-table parquet. Picks one `--report-date` snapshot (default = latest fileDate),
  excludes terminal/online projects, and embeds the active-queue rows + Plotly.js + a TX
  county GeoJSON as JSON. In-browser: Fuel Technology dropdown + Projected COD range filter
  (defaults start = today); a table (rows = CDR Reporting Zone; column groups = milestone
  gates Screening / FIS / IA / Financial Security / 6.9(1) / all 6.9, each showing Capacity
  in **GW** and # Projects); and a **Texas county choropleth** — click a table cell to filter
  the map, hover a county for its projects + GW, click a county for a side list (name, GW,
  COD, status). No server needed.

Run from the repo root, e.g. `uv run gis-research/scripts/download_gis_parquet.py`
or `uv run gis-research/scripts/build_queue_report.py --report-date 2025-06-01`.

## Data (`data/`)

- `ercot_generation_interconnect.parquet` — full base table (121,354 × 43).
- `ercot_generation_interconnect_view.parquet` — full view (121,354 × 38).
- `RPT.*GIS_Report_*.xlsx` — official ERCOT GIS monthly workbook (validation reference).
  Its *Project Details – Large/Small Gen* sheets match the parquet snapshot 1:1 (INR set +
  per-fuel capacity), confirming the parquet IS the same report.

## Assets (`assets/`) — inlined into the HTML at build time

- `plotly.min.js` (v2.35.2), `tx_counties.geojson` (STATE=48 subset), `tx_county_fips.json`
  (alnum-normalized county name → FIPS).

## Output (`output/`)

- `gis_queue_report_<report-date>.html` — one self-contained interactive report per
  report date (open in any browser). ~5 MB (Plotly + GeoJSON inlined).
