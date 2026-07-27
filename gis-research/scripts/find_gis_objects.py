"""Locate the ERCOT GIS objects across Snowflake databases/schemas."""

import awconnect
from awconnect import snowflake

PATTERNS = ["%Interconnect%", "%GenerationInter%", "%ercotGen%", "%GIS%"]


def main() -> None:
    awconnect.configure("read_only")

    dbs = snowflake.performQuery(
        dbName="AW",
        sqlQuery="SHOW DATABASES",
        warehouse=snowflake.READ_ONLY_WH,
        logInfo=False,
    )
    name_col = "name" if "name" in dbs.columns else dbs.columns[1]
    db_names = [d for d in dbs[name_col] if not str(d).startswith("SNOWFLAKE")]

    where = " OR ".join(f"TABLE_NAME ILIKE '{p}'" for p in PATTERNS)
    for db_name in db_names:
        try:
            hits = snowflake.performQuery(
                dbName=db_name,
                sqlQuery=(
                    "SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
                    f"FROM {db_name}.INFORMATION_SCHEMA.TABLES WHERE {where}"
                ),
                warehouse=snowflake.READ_ONLY_WH,
                logInfo=False,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"  [{db_name}] skipped: {str(exc)[:80]}")
            continue
        if len(hits):
            print(f"\n== hits in {db_name} ==")
            print(hits.to_string(index=False))
        else:
            print(f"  [{db_name}] no matches")


if __name__ == "__main__":
    main()
