"""
Round-3 read-only schema review: find the hourly binding-constraint /
shadow-price fact table and the dimension lookups (congMont/congCont,
isoZone, weatherZone, awDate anchor, wind regions).
"""
import awconnect
from awconnect import db, snowflake


def cols_and_sample(t, top=3, where=""):
    print(f"\n{'='*70}\n=== {t} ===")
    try:
        cols = db.getDfFromAwDb(
            f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{t}'
            ORDER BY ORDINAL_POSITION
            """
        )
        print(cols.to_string())
        sample = db.getDfFromAwDb(f"SELECT TOP {top} * FROM dbo.[{t}] {where}")
        print("--- sample ---")
        print(sample.to_string())
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    awconnect.configure("read_only")

    print("=== SQL Server tables LIKE %cong% / %mont% / %cont% ===")
    t = db.getDfFromAwDb(
        """
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo'
          AND (LOWER(TABLE_NAME) LIKE '%cong%'
               OR LOWER(TABLE_NAME) LIKE 'congmont%'
               OR LOWER(TABLE_NAME) LIKE '%exposure%'
               OR LOWER(TABLE_NAME) LIKE '%isozone%'
               OR LOWER(TABLE_NAME) LIKE '%weatherzone%'
               OR LOWER(TABLE_NAME) LIKE 'awdate%')
        ORDER BY TABLE_NAME
        """
    )
    print(t.to_string())

    for tbl in ["congMont", "congCont", "isoZone", "weatherZone", "awDate"]:
        cols_and_sample(tbl)

    # wind regions available
    print(f"\n{'='*70}\n=== ercotWindRegionHourly distinct regions ===")
    try:
        r = db.getDfFromAwDb(
            "SELECT windRegion, MIN(TimeStamp) AS minTs, MAX(TimeStamp) AS maxTs, COUNT(*) AS n "
            "FROM dbo.ercotWindRegionHourly GROUP BY windRegion"
        )
        print(r.to_string())
    except Exception as e:
        print(f"ERROR: {e}")

    # Snowflake-only fact tables
    for sft in ["CONSTRAINTEXPOSURE", "SHADOWPRICELOADINGPERCENT", "PATHCONSTRAINTEXPOSURE"]:
        print(f"\n{'='*70}\n=== Snowflake AW.DBO.{sft} ===")
        try:
            cols = snowflake.performQuery(
                dbName="AW",
                sqlQuery=f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA='DBO' AND TABLE_NAME='{sft}'
                ORDER BY ORDINAL_POSITION
                """,
                warehouse=snowflake.READ_ONLY_WH,
            )
            print(cols.to_string())
            s = snowflake.performQuery(
                dbName="AW",
                sqlQuery=f"SELECT * FROM DBO.{sft} LIMIT 3",
                warehouse=snowflake.READ_ONLY_WH,
            )
            print("--- sample ---")
            print(s.to_string())
        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
