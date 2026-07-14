"""
Round-2 read-only schema review (detailed, per user request) for the tables
short-listed by explore_market_schema.py. Columns + tiny samples only —
no big scans. Never writes to the DB.
"""
import awconnect
from awconnect import db

# SQL Server dbo candidates. (table, where-ish sample hint or None)
TABLES = [
    # constraint / shadow price side
    "ercot_sppCongConstRecord",     # likely ERCOT SCED/DAM shadow-price records
    "branchConstraint",
    "branchConstraintActiveList",
    "branchConstraintRegion",
    "congDefConstraint",
    "congConstraintRegion",
    "congConstraintType",
    "seCongAnalysisSPP",
    "FinalConstraintsTable",
    # wind / solar / load side
    "windGenAct",
    "windGenActByWeatherZone",
    "ercotWindRegionHourly",
    "windFcstType",
    "solarGenAct",
    "solarGenActByWeatherZone",
    "ercotLoadView",
    "ldFcstLoad",
    "loadAggType",
]


def main():
    awconnect.configure("read_only")

    for t in TABLES:
        print(f"\n{'='*70}\n=== {t} ===")
        try:
            cols = db.getDfFromAwDb(
                f"""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{t}'
                ORDER BY ORDINAL_POSITION
                """
            )
            print(cols.to_string())
            sample = db.getDfFromAwDb(f"SELECT TOP 3 * FROM dbo.[{t}]")
            print("--- sample ---")
            print(sample.to_string())
        except Exception as e:  # keep going — review everything we can
            print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
