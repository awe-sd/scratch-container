"""Download all rows of the ERCOT GIS objects and save as parquet.

Source: SQL Server AW.dbo (read-only). These objects are NOT accessible via
Snowflake for the agent's read-only role, so SQL Server is the source.

Objects:
  - ercotGenerationInterconnect       (BASE TABLE, 43 cols)  -> ercot_generation_interconnect.parquet
  - ercotGenerationInterconnectView   (VIEW, 38 cols)        -> ercot_generation_interconnect_view.parquet

Read-only; never inserts. Run:
  uv run gis-research/scripts/download_gis_parquet.py
"""

from pathlib import Path

import awconnect
from awconnect import db

OUT_DIR = Path(__file__).resolve().parents[1] / "data"

OBJECTS = {
    "ercotGenerationInterconnect": "ercot_generation_interconnect.parquet",
    "ercotGenerationInterconnectView": "ercot_generation_interconnect_view.parquet",
}


def main() -> None:
    awconnect.configure("read_only")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for obj, fname in OBJECTS.items():
        print(f"downloading dbo.{obj} ...")
        df = db.getDfFromAwDb(f"SELECT * FROM dbo.{obj}")
        out = OUT_DIR / fname
        df.to_parquet(out, index=False)
        size_mb = out.stat().st_size / 1e6
        print(f"  -> {out.name}: {len(df):,} rows x {df.shape[1]} cols, {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
