"""
Round-1 read-only schema discovery for the analytics-dev side project.

Goal: find the AW tables that hold
  1. ERCOT RT/DAM binding transmission constraints + shadow prices
  2. Actual system load (and weather-zone load) for net-load ranking
  3. Wind generation by geographic region (West vs Panhandle split)
  4. Solar generation (for net load = load - wind - solar)

Never writes to the DB. Prints candidate table names from both sources
(SQL Server dbo via awconnect.db, Snowflake AW.DBO via awconnect.snowflake)
so round 2 can dump columns/samples for the winners.
"""
import awconnect
from awconnect import db, snowflake

KEYWORDS = [
    "constraint", "shadow", "sced", "bindin",
    "wind", "solar", "pvgr",
    "load", "netload",
    "lmp", "spp",
]


def main():
    awconnect.configure("read_only")

    like_clauses = " OR ".join(
        f"LOWER(TABLE_NAME) LIKE '%{kw}%'" for kw in KEYWORDS
    )

    print("=== SQL SERVER dbo — candidate tables ===")
    tables = db.getDfFromAwDb(
        f"""
        SELECT TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo' AND ({like_clauses})
        ORDER BY TABLE_NAME
        """
    )
    print(tables.to_string())

    print("\n=== SNOWFLAKE AW.DBO — candidate tables ===")
    sf_tables = snowflake.performQuery(
        dbName="AW",
        sqlQuery=f"""
        SELECT TABLE_NAME, TABLE_TYPE, ROW_COUNT
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'DBO' AND ({like_clauses})
        ORDER BY TABLE_NAME
        """,
        warehouse=snowflake.READ_ONLY_WH,
    )
    print(sf_tables.to_string())


if __name__ == "__main__":
    main()
