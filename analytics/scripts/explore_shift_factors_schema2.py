"""
Round-2 metadata for the 6945 decomposition: SHIFT_FACTORS column layouts,
BATCH_RUN control rows (tiny table), and locating the resource-adequacy /
wind-grouping views. Still no big data pulls.
"""
import awconnect
from awconnect import snowflake

Q = lambda db, sql: snowflake.performQuery(dbName=db, sqlQuery=sql, warehouse=snowflake.READ_ONLY_WH)


def main():
    awconnect.configure("read_only")

    for tbl in ["BATCH_RUN", "CPNODE_SHIFTS_V1", "DEVICE_SHIFTS_VIEW", "BUS_SHIFTS"]:
        print(f"\n=== SHIFT_FACTORS.DBO.{tbl} columns ===")
        c = Q("SHIFT_FACTORS", f"""
            SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA='DBO' AND TABLE_NAME='{tbl}' ORDER BY ORDINAL_POSITION
        """)
        print(c.to_string())

    print("\n=== BATCH_RUN sample (control table, 2.8k rows) ===")
    s = Q("SHIFT_FACTORS", "SELECT * FROM DBO.BATCH_RUN ORDER BY 1 DESC LIMIT 5")
    print(s.to_string())

    print("\n=== BATCH_RUN rows mentioning 6945 / MGSES (July 2026) ===")
    # discover text columns dynamically is overkill; try the obvious ones after seeing sample
    print("(see sample above; follow-up query printed by hand if needed)")

    print("\n=== AW: tables LIKE %ADEQUACY% (any schema) ===")
    t = Q("AW", """
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE '%ADEQUACY%' ORDER BY 1, 2
    """)
    print(t.to_string())

    print("\n=== Snowflake databases available ===")
    d = Q("AW", "SHOW DATABASES")
    print(d[["name"]].to_string() if "name" in d.columns else d.to_string())


if __name__ == "__main__":
    main()
