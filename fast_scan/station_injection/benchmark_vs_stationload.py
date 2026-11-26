#!/usr/bin/env python
"""Benchmark AW.DBO.ERCOTSTATIONINJECTION against the legacy AW.DBO.ERCOTSTATIONLOAD
table at station-hour grain.

Comparison: SUM(NETINJECTIONMW) over KVLEVEL, per (station, hour) in the new
table, vs -WITHDRAWMW in the old table. Join key: TO_DATE(NEW."TIMESTAMP") =
OLD."DATE" AND HOUR(NEW."TIMESTAMP") = OLD."HOUR" AND station code.

Usage:
    /workspaces/scratch-workspace/.venv/bin/python benchmark_vs_stationload.py \
        --start 2022-01-01 --end 2026-07-25 --out fast_scan/station_injection/output/
"""
import argparse
import sys
from pathlib import Path

import awconnect
from awconnect import snowflake

NEW_TABLE = "AW.DBO.ERCOTSTATIONINJECTION"
OLD_TABLE = "AW.DBO.ERCOTSTATIONLOAD"

DDL_TMP_NEW = """
CREATE OR REPLACE TEMPORARY TABLE TMP_NEW AS
SELECT
    TO_DATE("TIMESTAMP")   AS D,
    HOUR("TIMESTAMP")      AS H,
    "TIMESTAMP"            AS TS,
    NMMSSTATIONCODE        AS STATION,
    SUM(NETINJECTIONMW)    AS NEW_NET,
    COUNT(*)               AS N_KV
FROM {new_table}
WHERE TO_DATE("TIMESTAMP") BETWEEN %(start)s AND %(end)s
GROUP BY 1, 2, 3, 4
""".format(new_table=NEW_TABLE)

DDL_TMP_CMP = """
CREATE OR REPLACE TEMPORARY TABLE TMP_CMP AS
SELECT
    COALESCE(N.D, O."DATE")               AS D,
    COALESCE(N.H, O."HOUR")                AS H,
    N.TS                                    AS TS,
    COALESCE(N.STATION, O.NMMSSTATIONCODE) AS STATION,
    N.NEW_NET                               AS NEW_NET,
    -O.WITHDRAWMW                           AS OLD_NET,
    N.NEW_NET - (-O.WITHDRAWMW)             AS DIFF,
    CASE
        WHEN N.STATION IS NOT NULL AND O.NMMSSTATIONCODE IS NOT NULL THEN 'BOTH'
        WHEN N.STATION IS NOT NULL THEN 'NEW_ONLY'
        ELSE 'OLD_ONLY'
    END AS STATUS
FROM TMP_NEW N
FULL OUTER JOIN (
    SELECT "DATE", "HOUR", NMMSSTATIONCODE, WITHDRAWMW
    FROM {old_table}
    WHERE "DATE" BETWEEN %(start)s AND %(end)s
) O
    ON N.D = O."DATE"
   AND N.H = O."HOUR"
   AND N.STATION = O.NMMSSTATIONCODE
""".format(old_table=OLD_TABLE)

Q_SUMMARY_BY_YEAR = """
WITH BASE AS (
    SELECT *, YEAR(D) AS YR FROM TMP_CMP
)
SELECT
    YR AS YEAR,
    COUNT_IF(STATUS = 'BOTH')      AS ROWS_BOTH,
    COUNT_IF(STATUS = 'NEW_ONLY')  AS ROWS_NEW_ONLY,
    COUNT_IF(STATUS = 'OLD_ONLY')  AS ROWS_OLD_ONLY,
    COUNT_IF(STATUS = 'BOTH' AND ABS(DIFF) <= 0.01)                        AS N_DIFF_LE_0_01,
    COUNT_IF(STATUS = 'BOTH' AND ABS(DIFF) > 0.01 AND ABS(DIFF) <= 0.1)    AS N_DIFF_0_01_TO_0_1,
    COUNT_IF(STATUS = 'BOTH' AND ABS(DIFF) > 0.1  AND ABS(DIFF) <= 1)      AS N_DIFF_0_1_TO_1,
    COUNT_IF(STATUS = 'BOTH' AND ABS(DIFF) > 1    AND ABS(DIFF) <= 10)     AS N_DIFF_1_TO_10,
    COUNT_IF(STATUS = 'BOTH' AND ABS(DIFF) > 10)                          AS N_DIFF_GT_10,
    MAX(CASE WHEN STATUS = 'BOTH' THEN ABS(DIFF) END)                     AS MAX_ABS_DIFF,
    COUNT_IF(STATUS = 'BOTH' AND DIFF IS NULL)                             AS N_NULL_DIFF,
    COUNT_IF(
        STATUS = 'BOTH'
        AND SIGN(NEW_NET) = -SIGN(OLD_NET)
        AND ABS(NEW_NET) > 5
        AND ABS(NEW_NET + OLD_NET) < 0.1
    ) AS N_SIGN_FLIPS
FROM BASE
GROUP BY YR
ORDER BY YR
"""

Q_WORST_STATIONS = """
SELECT
    STATION,
    COUNT(*)                                   AS N_HOURS,
    COUNT_IF(DIFF IS NULL)                      AS N_NULL_DIFF,
    COUNT_IF(ABS(DIFF) > 1)                     AS N_BAD,
    COUNT_IF(ABS(DIFF) > 1) / COUNT(*)          AS PCT_BAD,
    AVG(ABS(DIFF))                              AS MEAN_ABS_DIFF,
    MAX(ABS(DIFF))                              AS MAX_ABS_DIFF,
    AVG(NEW_NET)                                AS MEAN_NEW_NET,
    AVG(OLD_NET)                                AS MEAN_OLD_NET,
    MIN(CASE WHEN ABS(DIFF) > 1 THEN TS END)    AS FIRST_BAD_TS,
    MAX(CASE WHEN ABS(DIFF) > 1 THEN TS END)    AS LAST_BAD_TS
FROM TMP_CMP
WHERE STATUS = 'BOTH'
GROUP BY STATION
ORDER BY N_BAD DESC
LIMIT 100
"""

Q_NEW_ONLY_STATIONS = """
SELECT
    STATION,
    COUNT(*)        AS N_HOURS,
    MIN(TS)         AS FIRST_TS,
    MAX(TS)         AS LAST_TS,
    AVG(NEW_NET)    AS MEAN_NEW_NET
FROM TMP_CMP
WHERE STATUS = 'NEW_ONLY'
GROUP BY STATION
ORDER BY N_HOURS DESC
LIMIT 100
"""

Q_OLD_ONLY_STATIONS = """
SELECT
    STATION,
    COUNT(*)                                       AS N_HOURS,
    MIN(DATEADD('hour', H, TO_TIMESTAMP_NTZ(D)))    AS FIRST_TS,
    MAX(DATEADD('hour', H, TO_TIMESTAMP_NTZ(D)))    AS LAST_TS,
    AVG(OLD_NET)                                    AS MEAN_OLD_NET
FROM TMP_CMP
WHERE STATUS = 'OLD_ONLY'
GROUP BY STATION
ORDER BY N_HOURS DESC
LIMIT 100
"""

Q_DUP_YEAR_COUNTS = """
SELECT
    'YEAR_SUMMARY' AS SECTION,
    YEAR(D)        AS YEAR,
    NULL           AS D,
    NULL           AS H,
    NULL           AS STATION,
    COUNT(*)       AS N_DUP_GROUPS,
    SUM(N_TS) - COUNT(*) AS N_EXCESS_TS
FROM (
    SELECT D, H, STATION, COUNT(*) AS N_TS
    FROM TMP_NEW
    GROUP BY D, H, STATION
    HAVING COUNT(*) >= 2
)
GROUP BY YEAR(D)
ORDER BY YEAR
"""

Q_DUP_EXAMPLES = """
SELECT
    'EXAMPLE' AS SECTION,
    NULL      AS YEAR,
    D, H, STATION,
    COUNT(*)  AS N_TS,
    NULL      AS N_EXCESS_TS
FROM TMP_NEW
GROUP BY D, H, STATION
HAVING COUNT(*) >= 2
ORDER BY D, H, STATION
LIMIT 20
"""

Q_BAD_BY_MONTH = """
SELECT
    DATE_TRUNC('month', D)::DATE               AS MONTH,
    COUNT(*)                                    AS N_BOTH,
    COUNT_IF(DIFF IS NULL)                       AS N_NULL_DIFF,
    COUNT_IF(ABS(DIFF) > 1)                      AS N_BAD,
    COUNT_IF(ABS(DIFF) > 1) / COUNT(*)           AS PCT_BAD,
    AVG(ABS(DIFF))                               AS MEAN_ABS_DIFF
FROM TMP_CMP
WHERE STATUS = 'BOTH'
GROUP BY DATE_TRUNC('month', D)
ORDER BY MONTH
"""

Q_WORST_EXAMPLES = """
SELECT D, H, TS, STATION, NEW_NET, OLD_NET, DIFF, STATUS
FROM TMP_CMP
WHERE STATUS = 'BOTH' AND DIFF IS NOT NULL
ORDER BY ABS(DIFF) DESC
LIMIT 200
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default="2026-07-25")
    ap.add_argument("--out", default="fast_scan/station_injection/output/")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    awconnect.configure("read_only")
    conn = snowflake.getSnowflakeConnection(
        database="AW", warehouse=snowflake.READ_ONLY_WH, use_pool=False
    )
    cur = conn.cursor()
    cur.execute("ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 3600")

    params = {"start": args.start, "end": args.end}

    print(f"Building TMP_NEW ({args.start} .. {args.end}) ...")
    cur.execute(DDL_TMP_NEW, params)

    print("Building TMP_CMP (full outer join vs ERCOTSTATIONLOAD) ...")
    cur.execute(DDL_TMP_CMP, params)

    outputs = {
        "summary_by_year.csv": Q_SUMMARY_BY_YEAR,
        "worst_stations.csv": Q_WORST_STATIONS,
        "new_only_stations.csv": Q_NEW_ONLY_STATIONS,
        "old_only_stations.csv": Q_OLD_ONLY_STATIONS,
        "bad_by_month.csv": Q_BAD_BY_MONTH,
        "worst_examples.csv": Q_WORST_EXAMPLES,
    }

    dfs = {}
    for fname, sql in outputs.items():
        print(f"Running query for {fname} ...")
        cur.execute(sql)
        df = cur.fetch_pandas_all()
        dfs[fname] = df
        out_path = out_dir / fname
        df.to_csv(out_path, index=False)
        print(f"  wrote {out_path} ({len(df)} rows)")

    # dup_hours.csv is two sections (year summary + examples) stacked.
    print("Running queries for dup_hours.csv ...")
    cur.execute(Q_DUP_YEAR_COUNTS)
    dup_year_df = cur.fetch_pandas_all()
    cur.execute(Q_DUP_EXAMPLES)
    dup_examples_df = cur.fetch_pandas_all()
    import pandas as pd

    dup_df = pd.concat([dup_year_df, dup_examples_df], ignore_index=True)
    dfs["dup_hours.csv"] = dup_df
    dup_path = out_dir / "dup_hours.csv"
    dup_df.to_csv(dup_path, index=False)
    print(f"  wrote {dup_path} ({len(dup_df)} rows)")

    cur.close()
    conn.close()

    print("\n" + "=" * 100)
    print("CONSOLE SUMMARY")
    print("=" * 100)
    for fname, df in dfs.items():
        print(f"\n--- {fname} (head 20 of {len(df)}) ---")
        with __import__("pandas").option_context(
            "display.width", 200, "display.max_columns", 30
        ):
            print(df.head(20).to_string())

    return 0


if __name__ == "__main__":
    sys.exit(main())
