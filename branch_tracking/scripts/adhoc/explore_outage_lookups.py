"""
Follow-up to explore_outage_schema.py: toOutageTypeId (toState) and
outageTypeID (toChangesAllIsos) turned out to be NULL for every ERCOT
(isoMarketId=6) row -- so they can't be used to identify "new equipment" /
"retirement" outages directly. Dumping the small lookup tables
(toReason, toCause, toOutageType) to find where that semantic actually
lives (ReasonID on toState/toChangesAllIsos is the likely candidate --
sample data showed values like 5, 7, 14, 18 with human GroupLabel text
like crew/location names, but the toReason table itself may have a
cleaner description column).

Read-only. Writes nothing.
"""
import awconnect
from awconnect import db


def show_schema_and_sample(table_name, top_n=200):
    print(f"=== {table_name} SCHEMA ===")
    cols = db.getDfFromAwDb(
        f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
    )
    print(cols.to_string())
    print()

    print(f"=== {table_name} FULL CONTENTS (TOP {top_n}) ===")
    data = db.getDfFromAwDb(f"SELECT TOP {top_n} * FROM dbo.{table_name}")
    print(f"({len(data)} rows shown)")
    print(data.to_string())
    print()


def main():
    awconnect.configure("read_only")

    for table in ["toReason", "toCause", "toOutageType", "toStatus"]:
        show_schema_and_sample(table)


if __name__ == "__main__":
    main()
