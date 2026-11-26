"""
Round-4 read-only schema review: hourly congestion fact tables + ERCOT
dims + locate the '6945' GSES->CATSW constraint by name.
"""
import awconnect
from awconnect import db


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

    for t in [
        "congHrPrice", "congHrType", "congFqPrice", "congFqType", "congType",
        "congDefMonitor", "congDefContingency",
        "ercotCongConstRecord", "appDailyCongPaths", "appDailyCongNotes",
    ]:
        cols_and_sample(t)

    print(f"\n{'='*70}\n=== ERCOT isoZones (isomarketid=6) ===")
    z = db.getDfFromAwDb(
        "SELECT isoZoneId, isoZoneName, isoZoneDescr, ldTypeID FROM dbo.isoZone WHERE isomarketid = 6"
    )
    print(z.to_string())

    print(f"\n{'='*70}\n=== hunt: constraint names with 6945 / CATSW / GSES (ERCOT) ===")
    for pat in ["%6945%", "%CATSW%", "%GSES%"]:
        try:
            hits = db.getDfFromAwDb(
                f"""
                SELECT TOP 20 congConstraintID, isoConstraintName, congMontID, congContID, insertDate
                FROM dbo.congDefConstraint
                WHERE isomarketid = 6 AND isoConstraintName LIKE '{pat}'
                ORDER BY insertDate DESC
                """
            )
            print(f"--- congDefConstraint LIKE {pat}: {len(hits)} ---")
            print(hits.to_string())
        except Exception as e:
            print(f"ERROR {pat}: {e}")


if __name__ == "__main__":
    main()
