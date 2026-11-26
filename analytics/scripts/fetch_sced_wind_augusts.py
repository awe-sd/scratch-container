"""
Pull HOURLY-AVERAGED SCED wind dispatch for each of the last 5 Augusts
(2021-2025). Read-only; caches one parquet per August under analytics/data/.

For each August, only WIND ResourceType genIds are pulled (join to dim
server-side), and BasePoint/HSL are averaged per genId per hour to keep
the pull light (5-min cadence would be ~9x bigger).

Skips any August whose cache file already exists. Logs and continues past
any August that returns 0 rows (early years may be sparse/unavailable).
"""
from pathlib import Path

import awconnect
from awconnect import snowflake

DATA = Path(__file__).resolve().parents[1] / "data"
AUGUSTS = [2021, 2022, 2023, 2024, 2025]


def fetch_one(year):
    out = DATA / f"sced_wind_aug{year}.parquet"
    if out.exists():
        print(f"[{year}] cache exists -> {out.name}, skipping")
        return

    start = f"{year}-08-01 00:00:00"
    end = f"{year}-09-01 00:00:00"
    sql = f"""
        WITH dim AS (
            SELECT genId, ResourceName, cpnodeid, ResourceType
            FROM AW.DBO.isoErcotScedGen
            WHERE ResourceType = 'WIND'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY genId ORDER BY insertDate DESC) = 1
        )
        SELECT DATE_TRUNC('hour', gr.TimeStamp) AS hr,
               gr.genId,
               d.ResourceName,
               d.cpnodeid,
               AVG(gr.BasePoint) AS basepoint,
               AVG(gr.HSL) AS hsl
        FROM AW.DBO.isoErcotScedGenResource gr
        JOIN dim d ON d.genId = gr.genId
        WHERE gr.TimeStamp >= TO_TIMESTAMP_NTZ('{start}')
          AND gr.TimeStamp <  TO_TIMESTAMP_NTZ('{end}')
        GROUP BY 1, 2, 3, 4
    """
    print(f"[{year}] pulling hourly wind SCED dispatch {start} .. {end} ...")
    df = snowflake.performQuery(
        dbName="AW", sqlQuery=sql, warehouse=snowflake.READ_ONLY_WH, retryLimit=2
    )
    if len(df) == 0:
        print(f"[{year}] WARNING: 0 rows returned. Skipping cache write, continuing.")
        return
    print(
        f"[{year}] {len(df):,} rows; {df['hr'].min()} .. {df['hr'].max()}; "
        f"{df['genId'].nunique()} units"
    )
    df.to_parquet(out, index=False)
    print(f"[{year}] -> {out.name} ({out.stat().st_size / 1e6:.2f} MB)")


def main():
    awconnect.configure("read_only")
    for year in AUGUSTS:
        try:
            fetch_one(year)
        except Exception as e:
            print(f"[{year}] ERROR: {e}. Continuing to next August.")


if __name__ == "__main__":
    main()
