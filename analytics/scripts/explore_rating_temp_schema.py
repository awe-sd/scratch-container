"""
Read-only exploration for the 6945 RT-rating vs temperature plot.
elementTEID = 748510 (given by user = 6945 MGSES->CATSW element).
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

    show("ercotRtDynamicRatingTEIDDef for elementTEID=748510",
         "SELECT * FROM dbo.ercotRtDynamicRatingTEIDDef WHERE elementTEID = 748510")

    show("ercotRtDynamicRating cols",
         "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
         "WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='ercotRtDynamicRating' ORDER BY ORDINAL_POSITION")
    show("ercotRtDynamicRating sample for 748510 (recent)",
         "SELECT TOP 5 * FROM dbo.ercotRtDynamicRating WHERE elementTEID = 748510 ORDER BY createTime DESC")
    show("ercotRtDynamicRating range/count for 748510",
         "SELECT COUNT(*) n, MIN(createTime) mn, MAX(createTime) mx FROM dbo.ercotRtDynamicRating WHERE elementTEID = 748510")

    # weather station: find Midland (and nearby West-TX) TX stations
    show("weatherWXStation cols",
         "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
         "WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='weatherWXStation' ORDER BY ORDINAL_POSITION")
    show("weatherWXStation rows LIKE Midland/West TX",
         "SELECT * FROM dbo.weatherWXStation WHERE state='TX' AND "
         "(identifier LIKE '%MAF%' OR identifier LIKE '%MID%' OR name LIKE '%MIDLAND%' "
         "OR name LIKE '%ODESSA%' OR name LIKE '%BIG SPRING%' OR name LIKE '%SNYDER%')")

    show("weatherWXTempHourlyObservations cols",
         "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
         "WHERE TABLE_SCHEMA='dbo' AND TABLE_NAME='weatherWXTempHourlyObservations' ORDER BY ORDINAL_POSITION")
    show("weatherWXTempHourlyObservations sample",
         "SELECT TOP 3 * FROM dbo.weatherWXTempHourlyObservations ORDER BY local_time DESC")


if __name__ == "__main__":
    main()
