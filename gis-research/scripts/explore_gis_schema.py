"""Explore schema + size of the ERCOT GIS tables before bulk download.

Objects (SQL Server AW.dbo):
  - ercotGenerationInterconnect       (BASE TABLE)
  - ercotGenerationInterconnectView   (VIEW)

These live in SQL Server, not Snowflake (confirmed: no matching object is
visible to the read-only Snowflake user in any database).

Read-only investigation only. Run:
  uv run gis-research/scripts/explore_gis_schema.py
"""

import awconnect
from awconnect import db

OBJECTS = ["ercotGenerationInterconnect", "ercotGenerationInterconnectView"]


def main() -> None:
    awconnect.configure("read_only")

    for obj in OBJECTS:
        print("=" * 80)
        print(f"OBJECT: AW.dbo.{obj}")
        print("=" * 80)

        cols = db.getDfFromAwDb(
            f"""
            SELECT ORDINAL_POSITION, COLUMN_NAME, DATA_TYPE,
                   CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE,
                   IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{obj}'
            ORDER BY ORDINAL_POSITION
            """
        )
        print(f"\n-- columns ({len(cols)}):")
        print(cols.to_string(index=False))

        cnt = db.getDfFromAwDb(f"SELECT COUNT(*) AS n FROM dbo.{obj}")
        print(f"\n-- row count: {int(cnt['n'].iloc[0]):,}")

        sample = db.getDfFromAwDb(f"SELECT TOP 5 * FROM dbo.{obj}")
        print("\n-- sample (5 rows):")
        print(sample.to_string(index=False))
        print()


if __name__ == "__main__":
    main()
