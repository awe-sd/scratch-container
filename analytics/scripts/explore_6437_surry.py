"""
Read-only lookup for the second temp-vs-rating plot:
 - element: ercotRtDynamicRatingTEIDDef WHERE EquipmentID = '6437_F'  -> elementTEID
 - weather station in Surry county (via countyLocation + weatherwxstationmapping)
"""
import awconnect
import pandas as pd
from awconnect import db


def show(title, sql):
    print(f"\n{'='*70}\n=== {title} ===")
    try:
        print(db.getDfFromAwDb(sql).to_string())
    except Exception as e:
        print("ERROR:", e)


def main():
    pd.set_option("display.width", 260)
    pd.set_option("display.max_columns", 60)
    awconnect.configure("read_only")

    show("ercotRtDynamicRatingTEIDDef WHERE EquipmentID = '6437_F'",
         "SELECT * FROM dbo.ercotRtDynamicRatingTEIDDef WHERE EquipmentID = '6437_F'")

    show("rating count/range per elementTEID for 6437_F",
         "SELECT r.elementTEID, COUNT(*) n, MIN(r.createTime) mn, MAX(r.createTime) mx "
         "FROM dbo.ercotRtDynamicRating r "
         "WHERE r.elementTEID IN (SELECT elementTEID FROM dbo.ercotRtDynamicRatingTEIDDef "
         "WHERE EquipmentID = '6437_F') GROUP BY r.elementTEID")

    show("countyLocation cols",
         "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
         "WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='countyLocation' ORDER BY ORDINAL_POSITION")
    show("countyLocation WHERE county LIKE Surry",
         "SELECT * FROM dbo.countyLocation WHERE county LIKE '%Surry%'")

    show("weatherwxstationmapping cols",
         "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
         "WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='weatherwxstationmapping' ORDER BY ORDINAL_POSITION")

    show("stations mapped to Surry county",
         "SELECT cl.countyId, cl.county, ws.weatherWXStationId, ws.identifier, ws.name, "
         "ws.state, ws.lat, ws.lon "
         "FROM dbo.countyLocation cl "
         "JOIN dbo.weatherwxstationmapping m ON m.countyId = cl.countyId "
         "JOIN dbo.weatherWXStation ws ON ws.weatherWXStationId = m.weatherWxStationId "
         "WHERE cl.county LIKE '%Surry%'")

    # direct name search as a fallback
    show("weatherWXStation name/identifier LIKE Surry / Wakefield (nearby VA)",
         "SELECT weatherWXStationId, identifier, name, state, lat, lon FROM dbo.weatherWXStation "
         "WHERE name LIKE '%SURRY%' OR name LIKE '%WAKEFIELD%' OR identifier IN ('KAKQ','KFKN','KPHF')")


if __name__ == "__main__":
    main()
