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

Run from the repo root, e.g. `uv run gis-research/scripts/download_gis_parquet.py`.

## Data (`data/`)

- `ercot_generation_interconnect.parquet` — full base table (121,354 × 43).
- `ercot_generation_interconnect_view.parquet` — full view (121,354 × 38).
