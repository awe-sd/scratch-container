"""
Read-only schema/data exploration for the ERCOT branch tables.

Source: Snowflake AW.DBO (the SQL Server aw.dbo mirror was tried first but
the ai_read_only_user / SQL Server password had expired -- Snowflake works).

Never inserts, never creates tables. Investigation only.
"""
import awconnect
from awconnect import snowflake

ISOMARKETID_ERCOT = 6  # always ERCOT going forward

DB_NAME = "AW"
SCHEMA = "DBO"


def get_columns(table_name):
    return snowflake.performQuery(
        dbName=DB_NAME,
        sqlQuery=f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE,
                   NUMERIC_PRECISION, NUMERIC_SCALE, ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{SCHEMA}' AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """,
        logInfo=False,
    )


def main():
    awconnect.configure("read_only")

    print("=== BRANCH SCHEMA ===")
    print(get_columns("BRANCH").to_string())

    print("\n=== PTOBRANCH SCHEMA ===")
    print(get_columns("PTOBRANCH").to_string())

    print(f"\n=== BRANCH ROW COUNT (ISOMARKETID = {ISOMARKETID_ERCOT}) ===")
    count_df = snowflake.performQuery(
        dbName=DB_NAME,
        sqlQuery=f"SELECT COUNT(*) AS N FROM {SCHEMA}.BRANCH WHERE ISOMARKETID = {ISOMARKETID_ERCOT}",
        logInfo=False,
    )
    print(count_df.to_string())

    print(f"\n=== BRANCH SAMPLE (ISOMARKETID = {ISOMARKETID_ERCOT}) ===")
    sample_df = snowflake.performQuery(
        dbName=DB_NAME,
        sqlQuery=f"SELECT * FROM {SCHEMA}.BRANCH WHERE ISOMARKETID = {ISOMARKETID_ERCOT} LIMIT 5",
        logInfo=False,
    )
    print(sample_df.to_string())


if __name__ == "__main__":
    main()
