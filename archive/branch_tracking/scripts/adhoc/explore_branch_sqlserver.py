"""
Read-only schema/data exploration for the ERCOT BRANCH table via SQL Server
(awconnect.db). Companion to explore_branch_schema.py, which does the same
thing against the Snowflake AW.DBO mirror -- row counts and column
casing/nullability differ between the two sources, so both are worth
checking rather than assuming they agree.

Never inserts, never creates tables. Investigation only.
"""
import awconnect
from awconnect import db

ISOMARKETID_ERCOT = 6  # always ERCOT going forward


def main():
    awconnect.configure("read_only")

    print("=== BRANCH SCHEMA (SQL Server dbo.BRANCH) ===")
    cols = db.getDfFromAwDb(
        """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE,
               NUMERIC_PRECISION, NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'BRANCH'
        ORDER BY ORDINAL_POSITION
        """
    )
    print(cols.to_string())

    print(f"\n=== BRANCH SAMPLE (isomarketid = {ISOMARKETID_ERCOT}) ===")
    sample = db.getDfFromAwDb(
        f"SELECT TOP 5 * FROM dbo.BRANCH WHERE isomarketid = {ISOMARKETID_ERCOT}"
    )
    print(sample.to_string())

    print(f"\n=== BRANCH ROW COUNT (isomarketid = {ISOMARKETID_ERCOT}) ===")
    cnt = db.getDfFromAwDb(
        f"SELECT COUNT(*) AS n FROM dbo.BRANCH WHERE isomarketid = {ISOMARKETID_ERCOT}"
    )
    print(cnt.to_string())


if __name__ == "__main__":
    main()
