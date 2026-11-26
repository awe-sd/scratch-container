"""
Pull 5-min SCED wind dispatch for the 6945 binding window (Jul 5-6 2026,
the topology psenShiftID 86037069 was built for). Read-only; parquet only.

Join isoErcotScedGen (dim, WIND only, latest per genId) to
isoErcotScedGenResource (fact) server-side in Snowflake, then cache.
"""
from pathlib import Path

import awconnect
from awconnect import snowflake

DATA = Path(__file__).resolve().parents[1] / "data"
START, END = "2026-07-05 00:00:00", "2026-07-07 00:00:00"


def main():
    awconnect.configure("read_only")
    out = DATA / "sced_wind_jul0506.parquet"
    sql = f"""
        WITH dim AS (
            SELECT genId, ResourceName, cpnodeid, ResourceType
            FROM AW.DBO.isoErcotScedGen
            WHERE ResourceType = 'WIND'
            QUALIFY ROW_NUMBER() OVER (PARTITION BY genId ORDER BY insertDate DESC) = 1
        )
        SELECT gr.TimeStamp, gr.genId, d.ResourceName, d.cpnodeid,
               gr.HSL, gr.BasePoint, gr.TelemeteredOutput, gr.HASL, gr.HDL
        FROM AW.DBO.isoErcotScedGenResource gr
        JOIN dim d ON d.genId = gr.genId
        WHERE gr.TimeStamp >= TO_TIMESTAMP_NTZ('{START}')
          AND gr.TimeStamp <  TO_TIMESTAMP_NTZ('{END}')
    """
    print("Pulling SCED wind dispatch ...")
    df = snowflake.performQuery(dbName="AW", sqlQuery=sql,
                                warehouse=snowflake.READ_ONLY_WH, retryLimit=2)
    print(f"{len(df):,} rows; {df['TimeStamp'].min()} .. {df['TimeStamp'].max()}; "
          f"{df['genId'].nunique()} units")
    df.to_parquet(out, index=False)
    print(f"-> {out.name} ({out.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
