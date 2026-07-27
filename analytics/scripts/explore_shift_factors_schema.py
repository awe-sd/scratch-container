"""
Metadata-only exploration (no data pulls) for the SCED-gen x shift-factor
decomposition of 6945: SHIFT_FACTORS db (psen runs, cpnode shifts),
resource-adequacy fuel mapping, wind region grouping tables, SCED gen tables.
"""
import awconnect
from awconnect import snowflake

Q = lambda db, sql: snowflake.performQuery(dbName=db, sqlQuery=sql, warehouse=snowflake.READ_ONLY_WH)


def main():
    awconnect.configure("read_only")

    print("=== SHIFT_FACTORS schemas/tables ===")
    try:
        t = Q("SHIFT_FACTORS", """
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, ROW_COUNT
            FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME
        """)
        print(t.to_string())
    except Exception as e:
        print("ERROR:", e)

    for tbl in ["CPNODE_SHIFTS_VIEW", "PSENSHIFT", "PSEN_SHIFTS", "PSENSHIFTID"]:
        print(f"\n=== SHIFT_FACTORS columns LIKE {tbl} ===")
        try:
            c = Q("SHIFT_FACTORS", f"""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME LIKE '%{tbl}%'
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """)
            print(c.to_string())
        except Exception as e:
            print("ERROR:", e)

    print("\n=== AW.DBO: resource adequacy / wind mapping / SCED gen columns ===")
    for tbl in [
        "ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW",
        "ERCOTWINDREGIONCOUNTYMAPPING",
        "ERCOTWINDCLUSTERUNITMAPPING",
        "ERCOTDAMWINDMAP",
        "ISOERCOTSCEDGEN",
        "ISOERCOTSCEDGENRESOURCE",
    ]:
        try:
            c = Q("AW", f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA='DBO' AND TABLE_NAME='{tbl}'
                ORDER BY ORDINAL_POSITION
            """)
            print(f"--- {tbl} ({len(c)} cols) ---")
            print(c.to_string())
        except Exception as e:
            print(f"--- {tbl} ERROR: {e}")


if __name__ == "__main__":
    main()
