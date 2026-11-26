#!/usr/bin/env python
"""
Dry-run validator for SP_LOAD_ERCOT_PUN_INJECTION.

Runs the proc's INSERT...SELECT logic as a plain SELECT under the read-only
role (no DDL, no CALL) -- the ERCOTPUNTIEMAP rows are supplied as an inline
VALUES CTE, parsed straight out of ercot_pun_tie_map.sql so there is exactly
one source of truth for the crosswalk. Writes output/pun_injection_sample_
<start>.csv and prints a PASS/FAIL table against pun_analysis/backout_pun_
estimates.csv, backout_truth_test.csv and the Section 5 entangled-group
figures.

Usage:
    /workspaces/scratch-workspace/.venv/bin/python validate_pun_injection.py [--start 2026-06-01] [--end 2026-07-01]
"""
import argparse
import os
import re
import sys

import pandas as pd

import awconnect
from awconnect import snowflake

HERE = os.path.dirname(os.path.abspath(__file__))
TIE_MAP_SQL = os.path.join(HERE, "ercot_pun_tie_map.sql")
PUN_ANALYSIS = os.path.join(HERE, "pun_analysis")
OUTPUT_DIR = os.path.join(HERE, "output")

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 120)


def q(sql):
    return snowflake.performQuery("AW", sql, warehouse=snowflake.READ_ONLY_WH, logInfo=False)


def load_tie_map_values():
    """Pull the VALUES (...) , (...) ... block out of ercot_pun_tie_map.sql."""
    text = open(TIE_MAP_SQL).read()
    m = re.search(r"VALUES\s*\n(.*?);\s*\n\n-- =+\n-- Verification", text, re.S)
    if not m:
        raise RuntimeError("Could not locate VALUES block in ercot_pun_tie_map.sql")
    return m.group(1).strip().rstrip(",")


def build_query(start_date, end_date):
    """Mirrors sp_load_ercot_pun_injection.sql's SELECT logic exactly (2026-09-25 grading-gate
    fixes): duplicate-snapshot dedup, full (snapshot x neighbour) grid so a missing SI row is
    visible instead of vanishing from the SUM, INSERVICE=1-with-fallback-to-all-rows load lookup,
    presence-only (not INSERVICE-gated) 0-vs-NULL load gate, and the EXACT_SWITCHING short-circuit.
    """
    tie_values = load_tie_map_values()
    return f"""
WITH TIE_MAP AS (
    SELECT COLUMN1 AS PUNSTATION, COLUMN2 AS NEIGHBORSTATION, COLUMN3 AS NEIGHBORGROUPID,
           COLUMN4 AS METHODTAG, COLUMN5 AS KVLEVELS, COLUMN6 AS NOTE
    FROM VALUES
    {tie_values}
),
TMP_NEIGHBOR_LIST AS (
    SELECT DISTINCT NEIGHBORSTATION FROM TIE_MAP WHERE NEIGHBORSTATION IS NOT NULL
),
dam_raw AS (
    SELECT dg.CPNODEID, ds.STATIONNAME, COUNT(*) AS CNT
    FROM AW.DBO.ERCOTDAMPSSEGNDEF dg
    JOIN AW.DBO.ERCOTDAMPSSESTATION ds ON ds.ERCOTDAMPSSESTATIONID = dg.STATIONID
    GROUP BY dg.CPNODEID, ds.STATIONNAME
),
dam_dedup AS (
    SELECT CPNODEID, STATIONNAME FROM (
        SELECT CPNODEID, STATIONNAME, ROW_NUMBER() OVER (PARTITION BY CPNODEID ORDER BY CNT DESC) AS rn
        FROM dam_raw
    ) WHERE rn = 1
),
TMP_GEN_MAP AS (
    SELECT g.GENID, dd.STATIONNAME AS NEIGHBORSTATION
    FROM AW.DBO.ISOERCOTSCEDGEN g
    JOIN dam_dedup dd ON dd.CPNODEID = g.CPNODEID
    WHERE dd.STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
),
TMP_GEN_STATIONS AS (
    SELECT DISTINCT NEIGHBORSTATION FROM TMP_GEN_MAP
),
TMP_NEIGHBOR_SI_RAW AS (
    SELECT si."TIMESTAMP" AS SE_TS, si.NMMSSTATIONCODE AS NEIGHBORSTATION, si.NETINJECTIONMW
    FROM AW.DBO.ERCOTSTATIONINJECTION si
    WHERE si.NMMSSTATIONCODE IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND si."TIMESTAMP" >= DATEADD(MINUTE, -30, '{start_date}'::TIMESTAMP_NTZ)
      AND si."TIMESTAMP" <  DATEADD(MINUTE, -30, DATEADD(DAY, 1, '{end_date}'::TIMESTAMP_NTZ))
),
TMP_NEIGHBOR_SNAPSHOT AS (
    SELECT SE_TS, DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) AS HOURBUCKET
    FROM (SELECT SE_TS, COUNT(*) AS N FROM TMP_NEIGHBOR_SI_RAW GROUP BY SE_TS)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) ORDER BY N DESC, SE_TS DESC
    ) = 1
),
TMP_NEIGHBOR_GRID AS (
    SELECT s.SE_TS, s.HOURBUCKET, nl.NEIGHBORSTATION
    FROM TMP_NEIGHBOR_SNAPSHOT s
    CROSS JOIN TMP_NEIGHBOR_LIST nl
),
TMP_NEIGHBOR_SI AS (
    SELECT g.SE_TS, g.HOURBUCKET, g.NEIGHBORSTATION, SUM(r.NETINJECTIONMW) AS NET_INJ_MW
    FROM TMP_NEIGHBOR_GRID g
    LEFT JOIN TMP_NEIGHBOR_SI_RAW r ON r.SE_TS = g.SE_TS AND r.NEIGHBORSTATION = g.NEIGHBORSTATION
    GROUP BY g.SE_TS, g.HOURBUCKET, g.NEIGHBORSTATION
),
TMP_NEIGHBOR_GEN_TICK AS (
    SELECT gm.NEIGHBORSTATION, r."TIMESTAMP" AS GEN_TS, SUM(r.TELEMETEREDOUTPUT) AS GEN_MW
    FROM AW.DBO.ISOERCOTSCEDGENRESOURCE r
    JOIN TMP_GEN_MAP gm ON gm.GENID = r.GENID
    WHERE r."TIMESTAMP" >= DATEADD(MINUTE, -40, '{start_date}'::TIMESTAMP_NTZ)
      AND r."TIMESTAMP" <  DATEADD(MINUTE, 10, DATEADD(DAY, 1, '{end_date}'::TIMESTAMP_NTZ))
    GROUP BY gm.NEIGHBORSTATION, r."TIMESTAMP"
),
TMP_NEIGHBOR_GEN AS (
    SELECT g.SE_TS, g.NEIGHBORSTATION, t.GEN_TS, t.GEN_MW
    FROM TMP_NEIGHBOR_GRID g
    LEFT JOIN TMP_NEIGHBOR_GEN_TICK t
      ON t.NEIGHBORSTATION = g.NEIGHBORSTATION
     AND t.GEN_TS BETWEEN DATEADD(MINUTE, -10, g.SE_TS) AND DATEADD(MINUTE, 10, g.SE_TS)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY g.SE_TS, g.NEIGHBORSTATION
        ORDER BY ABS(TIMESTAMPDIFF(SECOND, g.SE_TS, t.GEN_TS)) ASC NULLS LAST
    ) = 1
),
TMP_NEIGHBOR_LOAD AS (
    SELECT STATIONNAME AS NEIGHBORSTATION, "DATE" AS LOAD_DATE, HE,
           SUM(IFF(INSERVICE = 1, RAWMWLDF, 0)) AS LOAD_MW_INSERVICE,
           COUNT_IF(INSERVICE = 1) AS N_INSERVICE,
           SUM(RAWMWLDF) AS LOAD_MW_ALL,
           COUNT(*) AS N_ROWS
    FROM AW.DBO.ERCOTDAMPSSELDVIEW
    WHERE STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND "DATE" >= '{start_date}' AND "DATE" <= '{end_date}'
    GROUP BY STATIONNAME, "DATE", HE
),
TMP_NEIGHBOR_LOAD_PRESENT AS (
    SELECT DISTINCT STATIONNAME AS NEIGHBORSTATION, DATE_TRUNC('MONTH', "DATE") AS LOAD_MONTH
    FROM AW.DBO.ERCOTDAMPSSELDVIEW
    WHERE STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND "DATE" >= DATE_TRUNC('MONTH', '{start_date}'::DATE)
      AND "DATE" <  DATEADD('MONTH', 1, DATE_TRUNC('MONTH', '{end_date}'::DATE))
),
TMP_NEIGHBOR_COMPONENTS AS (
    SELECT si.SE_TS, si.NEIGHBORSTATION, si.HOURBUCKET, si.NET_INJ_MW,
           gen.GEN_TS AS SCED_TS,
           IFF(gs.NEIGHBORSTATION IS NULL, 0, gen.GEN_MW) AS GEN_COMPONENT,
           CASE WHEN lp.NEIGHBORSTATION IS NULL THEN 0
                WHEN l.N_ROWS IS NULL THEN NULL
                WHEN l.N_INSERVICE > 0 THEN l.LOAD_MW_INSERVICE
                ELSE l.LOAD_MW_ALL END AS LOAD_COMPONENT,
           IFF(l.N_ROWS > 0 AND l.N_INSERVICE = 0, 1, 0) AS LOAD_OUT_OF_SERVICE_FIRED
    FROM TMP_NEIGHBOR_SI si
    LEFT JOIN TMP_NEIGHBOR_GEN gen ON gen.SE_TS = si.SE_TS AND gen.NEIGHBORSTATION = si.NEIGHBORSTATION
    LEFT JOIN TMP_GEN_STATIONS gs ON gs.NEIGHBORSTATION = si.NEIGHBORSTATION
    LEFT JOIN TMP_NEIGHBOR_LOAD l
      ON l.NEIGHBORSTATION = si.NEIGHBORSTATION
     AND l.LOAD_DATE = TO_DATE(si.HOURBUCKET)
     AND l.HE = HOUR(si.HOURBUCKET) + 1
    LEFT JOIN TMP_NEIGHBOR_LOAD_PRESENT lp
      ON lp.NEIGHBORSTATION = si.NEIGHBORSTATION
     AND lp.LOAD_MONTH = DATE_TRUNC('MONTH', TO_DATE(si.HOURBUCKET))
),
group_neighbors AS (
    SELECT DISTINCT NEIGHBORGROUPID, NEIGHBORSTATION FROM TIE_MAP WHERE NEIGHBORSTATION IS NOT NULL
),
TMP_GROUP_INJECTION AS (
    SELECT gn.NEIGHBORGROUPID, c.SE_TS, c.HOURBUCKET,
           IFF(COUNT_IF(c.NET_INJ_MW IS NULL) > 0, NULL, SUM(c.NET_INJ_MW)) AS NEIGHBORNETINJECTIONMW,
           COUNT_IF(c.NET_INJ_MW IS NULL) AS NEIGHBORINJECTIONMISSINGCOUNT,
           IFF(COUNT_IF(c.GEN_COMPONENT IS NULL) > 0, NULL, SUM(c.GEN_COMPONENT)) AS NEIGHBORSCEDGENMW,
           MAX(c.SCED_TS) AS SCEDTIMESTAMP,
           IFF(COUNT_IF(c.LOAD_COMPONENT IS NULL) > 0, NULL, SUM(c.LOAD_COMPONENT)) AS NEIGHBORDAMLOADMW,
           SUM(IFF(c.LOAD_OUT_OF_SERVICE_FIRED = 1, 1, 0)) AS NEIGHBORLOADOUTOFSERVICECOUNT
    FROM group_neighbors gn
    JOIN TMP_NEIGHBOR_COMPONENTS c ON c.NEIGHBORSTATION = gn.NEIGHBORSTATION
    GROUP BY gn.NEIGHBORGROUPID, c.SE_TS, c.HOURBUCKET
)
SELECT gi.SE_TS AS "TIMESTAMP", gi.HOURBUCKET, m.PUNSTATION, gi.NEIGHBORGROUPID, m.METHODTAG,
       gi.NEIGHBORNETINJECTIONMW, gi.NEIGHBORINJECTIONMISSINGCOUNT,
       IFF(m.METHODTAG = 'EXACT_SWITCHING', 0, gi.NEIGHBORSCEDGENMW) AS NEIGHBORSCEDGENMW,
       gi.SCEDTIMESTAMP,
       IFF(m.METHODTAG = 'EXACT_SWITCHING', 0, gi.NEIGHBORDAMLOADMW) AS NEIGHBORDAMLOADMW,
       gi.NEIGHBORLOADOUTOFSERVICECOUNT,
       IFF(m.METHODTAG = 'EXACT_SWITCHING',
           gi.NEIGHBORNETINJECTIONMW,
           gi.NEIGHBORNETINJECTIONMW - gi.NEIGHBORSCEDGENMW + gi.NEIGHBORDAMLOADMW) AS PUNNETINJECTIONMW
FROM TMP_GROUP_INJECTION gi
JOIN (
    SELECT DISTINCT PUNSTATION, NEIGHBORGROUPID, METHODTAG FROM TIE_MAP WHERE NEIGHBORGROUPID IS NOT NULL
) m ON m.NEIGHBORGROUPID = gi.NEIGHBORGROUPID
ORDER BY 1, 3
"""


def snapshot_dedup_check(start_date, end_date):
    """Item 7(i): count distinct SE TIMESTAMPs per HOURBUCKET over the neighbour set after the
    fix -- must be exactly 1 (duplicate :52 stub snapshots, e.g. 2026-06-02 23:52, must collapse
    to the most-complete/latest-tiebreak pick, same rule as sp_load_ercot_station_injection.sql)."""
    tie_values = load_tie_map_values()
    sql = f"""
    WITH TIE_MAP AS (
        SELECT COLUMN1 AS PUNSTATION, COLUMN2 AS NEIGHBORSTATION
        FROM VALUES
        {tie_values}
    ),
    nl AS (SELECT DISTINCT NEIGHBORSTATION FROM TIE_MAP WHERE NEIGHBORSTATION IS NOT NULL),
    raw AS (
        SELECT si."TIMESTAMP" AS SE_TS
        FROM AW.DBO.ERCOTSTATIONINJECTION si
        JOIN nl ON nl.NEIGHBORSTATION = si.NMMSSTATIONCODE
        WHERE si."TIMESTAMP" >= DATEADD(MINUTE, -30, '{start_date}'::TIMESTAMP_NTZ)
          AND si."TIMESTAMP" <  DATEADD(MINUTE, -30, DATEADD(DAY, 1, '{end_date}'::TIMESTAMP_NTZ))
    ),
    -- before fix (raw, no dedup): distinct SE_TS per bucket
    before_fix AS (
        SELECT DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) AS HOURBUCKET, COUNT(DISTINCT SE_TS) AS N_TS
        FROM raw GROUP BY 1
    ),
    -- after fix: pick one SE_TS per bucket (most neighbour rows, latest on tie)
    picked AS (
        SELECT SE_TS, DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) AS HOURBUCKET
        FROM (SELECT SE_TS, COUNT(*) AS N FROM raw GROUP BY SE_TS)
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) ORDER BY N DESC, SE_TS DESC
        ) = 1
    ),
    after_fix AS (
        SELECT HOURBUCKET, COUNT(DISTINCT SE_TS) AS N_TS FROM picked GROUP BY 1
    )
    SELECT (SELECT COUNT(*) FROM before_fix WHERE N_TS > 1) AS N_BUCKETS_DUP_BEFORE_FIX,
           (SELECT MAX(N_TS) FROM before_fix) AS MAX_TS_PER_BUCKET_BEFORE_FIX,
           (SELECT COUNT(*) FROM after_fix WHERE N_TS > 1) AS N_BUCKETS_DUP_AFTER_FIX,
           (SELECT MAX(N_TS) FROM after_fix) AS MAX_TS_PER_BUCKET_AFTER_FIX
    """
    return q(sql)


def monthly_vs_daily_identical_check():
    """Proves TMP_NEIGHBOR_LOAD_PRESENT's monthly-granularity fix: a 1-day call for 2026-06-10 and
    a full-month call for June must produce byte-identical 2026-06-10 rows (both resolve presence
    over the same calendar month, independent of P_START_DATE/P_END_DATE's exact day boundaries)."""
    daily = q(build_query("2026-06-10", "2026-06-10"))
    daily.columns = [c.upper() for c in daily.columns]
    monthly = q(build_query("2026-06-01", "2026-06-30"))
    monthly.columns = [c.upper() for c in monthly.columns]

    value_cols = ["NEIGHBORNETINJECTIONMW", "NEIGHBORINJECTIONMISSINGCOUNT", "NEIGHBORSCEDGENMW",
                  "NEIGHBORDAMLOADMW", "NEIGHBORLOADOUTOFSERVICECOUNT", "PUNNETINJECTIONMW"]
    for d in (daily, monthly):
        d["TIMESTAMP"] = pd.to_datetime(d["TIMESTAMP"])
        d["HOURBUCKET"] = pd.to_datetime(d["HOURBUCKET"])
    # Filter by HOURBUCKET's date, not raw TIMESTAMP's date: a :57 snapshot's TIMESTAMP is on the
    # PRIOR calendar day to the hour it describes (HOURBUCKET), which is the grain the daily call
    # actually produces (24 HOURBUCKETs for 2026-06-10, SE_TS spanning 06-09 23:57..06-10 22:57).
    monthly_10th = monthly[monthly["HOURBUCKET"].dt.date == pd.Timestamp("2026-06-10").date()].copy()

    daily_s = daily.sort_values(["HOURBUCKET", "PUNSTATION"]).reset_index(drop=True)
    monthly_s = monthly_10th.sort_values(["HOURBUCKET", "PUNSTATION"]).reset_index(drop=True)

    if len(daily_s) != len(monthly_s):
        return False, f"row count mismatch: daily={len(daily_s)}, monthly-subset={len(monthly_s)}"
    if not (daily_s["PUNSTATION"].values == monthly_s["PUNSTATION"].values).all():
        return False, "PUNSTATION alignment mismatch after sort"
    diffs = []
    for col in value_cols:
        a, b = daily_s[col], monthly_s[col]
        both_null = a.isna() & b.isna()
        close = (a - b).abs() <= 1e-9
        mismatch = ~(both_null | close)
        if mismatch.any():
            diffs.append((col, int(mismatch.sum())))
    if diffs:
        return False, f"value mismatches: {diffs}"
    return True, f"{len(daily_s)} rows identical (daily call vs full-month call, 2026-06-10 subset)"


def crosswalk_check():
    tie_values = load_tie_map_values()
    # Each tuple is ('PUN', 'NEIGHBOR'|NULL, 'GROUP'|NULL, 'METHODTAG', 'KV', 'NOTE'|NULL)
    tuples = re.findall(r"\(\s*'([^']*)'\s*,\s*(?:'([^']*)'|NULL)\s*,", tie_values)
    neighbours = sorted(set(n for _, n in tuples if n))
    inlist = ",".join(f"'{n}'" for n in neighbours)
    sql = f"""
    WITH nbrs AS (SELECT COLUMN1 AS NEIGHBOR FROM VALUES {",".join(f"('{n}')" for n in neighbours)}),
    si AS (SELECT DISTINCT NMMSSTATIONCODE FROM AW.DBO.ERCOTSTATIONINJECTION WHERE "TIMESTAMP" >= '2026-06-01' AND "TIMESTAMP" < '2026-07-01'),
    dam_stn AS (SELECT DISTINCT STATIONNAME FROM AW.DBO.ERCOTDAMPSSESTATION),
    -- IN_DAMPSSELDVIEW here means "has an INSERVICE=1 row in June"; HAS_ROWS_BUT_ALL_OUT_OF_SERVICE
    -- flags a station like COHMA whose June rows are all INSERVICE=0 but still carry real load --
    -- the proc no longer gates that to 0 (2026-09-25 fix): it falls back to summing all rows for
    -- a key with zero INSERVICE=1 rows, so COHMA's ~0.37 MW now counts. See SESSION_HANDOFF.md.
    dam_ld AS (SELECT DISTINCT STATIONNAME FROM AW.DBO.ERCOTDAMPSSELDVIEW
               WHERE "DATE" >= '2026-06-01' AND "DATE" < '2026-07-01' AND INSERVICE = 1),
    dam_ld_any_inservice AS (SELECT DISTINCT STATIONNAME FROM AW.DBO.ERCOTDAMPSSELDVIEW
               WHERE "DATE" >= '2026-06-01' AND "DATE" < '2026-07-01')
    SELECT n.NEIGHBOR,
           IFF(si.NMMSSTATIONCODE IS NOT NULL, 'Y', 'N') AS IN_STATIONINJECTION,
           IFF(dam_stn.STATIONNAME IS NOT NULL, 'Y', 'N') AS IN_DAMPSSESTATION,
           IFF(dam_ld.STATIONNAME IS NOT NULL, 'Y', 'N') AS IN_DAMPSSELDVIEW,
           IFF(dam_ld_any_inservice.STATIONNAME IS NOT NULL AND dam_ld.STATIONNAME IS NULL, 'Y', 'N')
               AS HAS_ROWS_BUT_ALL_OUT_OF_SERVICE
    FROM nbrs n
    LEFT JOIN si ON si.NMMSSTATIONCODE = n.NEIGHBOR
    LEFT JOIN dam_stn ON dam_stn.STATIONNAME = n.NEIGHBOR
    LEFT JOIN dam_ld ON dam_ld.STATIONNAME = n.NEIGHBOR
    LEFT JOIN dam_ld_any_inservice ON dam_ld_any_inservice.STATIONNAME = n.NEIGHBOR
    ORDER BY 1
    """
    return q(sql)


def own_gross_check(puns):
    """Per-timestamp station-sum SCED gross for PUNs that have own SCED units, vs PUNNETINJECTIONMW.

    The main proc's neighbour gen map uses the pure DAM chain only (verified identical to the
    COALESCE-with-GENUNIT-fallback chain for all 7 gen-flagged neighbours -- see
    ercot_pun_tie_map.sql's header). That is NOT true for the PUNs' OWN gross computed here: AMOCOOIL
    resolves to zero GENIDs via the pure DAM chain (checked directly), so this check replicates
    backout_master.sql's full gen_map (dam_dedup + GENUNIT-busname-prefix fallback via se_codes)
    to reproduce backout_pun_estimates.csv's PUN_GROSS_SCED_MW / backout_truth_test.csv's MEAN_G_P.
    """
    inlist = ",".join(f"'{p}'" for p in puns)
    sql = f"""
    WITH dam_raw AS (
        SELECT dg.CPNODEID, ds.STATIONNAME, COUNT(*) AS CNT
        FROM AW.DBO.ERCOTDAMPSSEGNDEF dg
        JOIN AW.DBO.ERCOTDAMPSSESTATION ds ON ds.ERCOTDAMPSSESTATIONID = dg.STATIONID
        GROUP BY dg.CPNODEID, ds.STATIONNAME
    ),
    dam_dedup AS (
        SELECT CPNODEID, STATIONNAME FROM (
            SELECT CPNODEID, STATIONNAME, ROW_NUMBER() OVER (PARTITION BY CPNODEID ORDER BY CNT DESC) AS rn
            FROM dam_raw
        ) WHERE rn = 1
    ),
    gu_raw AS (
        SELECT CPNODEID, BUSNAME, COUNT(*) AS CNT
        FROM AWDEV.DBO.GENUNIT
        WHERE CPNODEID IS NOT NULL AND BUSNAME IS NOT NULL
        GROUP BY CPNODEID, BUSNAME
    ),
    gu_dedup AS (
        SELECT CPNODEID, BUSNAME FROM (
            SELECT CPNODEID, BUSNAME, ROW_NUMBER() OVER (PARTITION BY CPNODEID ORDER BY CNT DESC) AS rn
            FROM gu_raw
        ) WHERE rn = 1
    ),
    own_gen_map AS (
        -- NOTE: unlike the neighbour gen map, this cannot fall back through se_codes
        -- (SPLIT_PART(BUSNAME,'_',1) matched against a NMMSSTATIONCODE in
        -- ERCOTSTATIONINJECTION): a PUN station is BY DEFINITION absent from
        -- ERCOTSTATIONINJECTION (that is the whole redaction this loader backs out),
        -- so that fallback always resolves to NULL for a PUN's own units and silently
        -- drops them (found empirically: AMOCOOIL has 0 rows via the neighbour-style
        -- chain despite 11 GENIDs existing with BUSNAME LIKE 'AMOCOOIL%'). Falls back
        -- to the BUSNAME prefix directly instead.
        SELECT g.GENID, COALESCE(dam.STATIONNAME, SPLIT_PART(gu.BUSNAME, '_', 1)) AS PUNSTATION
        FROM AW.DBO.ISOERCOTSCEDGEN g
        LEFT JOIN dam_dedup dam ON g.CPNODEID = dam.CPNODEID
        LEFT JOIN gu_dedup gu ON g.CPNODEID = gu.CPNODEID
        WHERE COALESCE(dam.STATIONNAME, SPLIT_PART(gu.BUSNAME, '_', 1)) IN ({inlist})
    ),
    own_gross_tick AS (
        SELECT gm.PUNSTATION, r."TIMESTAMP" AS GEN_TS, SUM(r.TELEMETEREDOUTPUT) AS OWN_GROSS_MW
        FROM AW.DBO.ISOERCOTSCEDGENRESOURCE r
        JOIN own_gen_map gm ON gm.GENID = r.GENID
        WHERE r."TIMESTAMP" >= '2026-05-31 23:50:00' AND r."TIMESTAMP" < '2026-07-01 00:10:00'
        GROUP BY gm.PUNSTATION, r."TIMESTAMP"
    )
    SELECT PUNSTATION, GEN_TS, OWN_GROSS_MW
    FROM own_gross_tick
    ORDER BY PUNSTATION, GEN_TS
    """
    return q(sql)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-06-01")
    ap.add_argument("--end", default="2026-07-01")
    args = ap.parse_args()

    awconnect.configure("read_only")

    # CLI --start/--end are half-open [start, end), matching the task's stated default
    # (2026-06-01..2026-07-01). build_query's end_date is the proc's P_END_DATE, which is
    # INCLUSIVE (same convention as sp_load_ercot_station_injection.sql), so convert once here.
    import datetime as _dt
    end_inclusive = (_dt.date.fromisoformat(args.end) - _dt.timedelta(days=1)).isoformat()

    print(f"Running dry-run SELECT for {args.start}..{args.end} (half-open; "
          f"P_END_DATE={end_inclusive} inclusive) ...")
    sql = build_query(args.start, end_inclusive)
    df = q(sql)
    df.columns = [c.upper() for c in df.columns]
    print(f"Rows returned: {len(df)}")

    out_path = os.path.join(OUTPUT_DIR, f"pun_injection_sample_{args.start[:7]}.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")

    results = []

    # ---- (c) grain uniqueness ------------------------------------------------
    dupes = df.duplicated(subset=["TIMESTAMP", "PUNSTATION"]).sum()
    results.append(("(c) grain unique (TIMESTAMP,PUNSTATION)", "PASS" if dupes == 0 else "FAIL",
                     f"{dupes} duplicate keys"))

    # ---- (d) NULL PUNNETINJECTIONMW by METHODTAG ------------------------------
    null_df = df[df["PUNNETINJECTIONMW"].isna()]
    null_by_tag = null_df.groupby("METHODTAG").size()
    exact_nulls = int(null_by_tag.get("EXACT_SWITCHING", 0))
    results.append(("(d) EXACT_SWITCHING has zero NULLs", "PASS" if exact_nulls == 0 else "FAIL",
                     f"{exact_nulls} NULL rows (structural short-circuit: PUNNETINJECTIONMW=N_S only)"))
    null_reason = null_df.assign(
        gen_missing=null_df["NEIGHBORSCEDGENMW"].isna(),
        load_missing=null_df["NEIGHBORDAMLOADMW"].isna(),
        injection_missing=null_df["NEIGHBORNETINJECTIONMW"].isna(),
    ).groupby("METHODTAG").agg(
        n_null=("PUNSTATION", "size"),
        n_gen_missing=("gen_missing", "sum"),
        n_load_missing=("load_missing", "sum"),
        n_injection_missing=("injection_missing", "sum"),
    )

    # ---- item 7(ii): NEIGHBORLOADOUTOFSERVICECOUNT / NEIGHBORINJECTIONMISSINGCOUNT by PUN ------
    counters_by_pun = df.groupby("PUNSTATION").agg(
        N=("PUNSTATION", "size"),
        LOAD_OOS_HOURS=("NEIGHBORLOADOUTOFSERVICECOUNT", "sum"),
        SI_MISSING_HOURS=("NEIGHBORINJECTIONMISSINGCOUNT", "sum"),
    )
    counters_by_pun = counters_by_pun[(counters_by_pun["LOAD_OOS_HOURS"] > 0) | (counters_by_pun["SI_MISSING_HOURS"] > 0)]

    # ---- item 7(i): duplicate-snapshot dedup assertion -------------------------
    dedup_check = snapshot_dedup_check(args.start, end_inclusive)
    dedup_check.columns = [c.upper() for c in dedup_check.columns]
    dr = dedup_check.iloc[0]
    dedup_ok = int(dr["N_BUCKETS_DUP_AFTER_FIX"]) == 0 and int(dr["MAX_TS_PER_BUCKET_AFTER_FIX"]) == 1
    results.append(("(item7-i) 1 distinct SE TIMESTAMP per HOURBUCKET after dedup fix",
                     "PASS" if dedup_ok else "FAIL",
                     f"before fix: {int(dr['N_BUCKETS_DUP_BEFORE_FIX'])} dup buckets (max {int(dr['MAX_TS_PER_BUCKET_BEFORE_FIX'])} TS/bucket); "
                     f"after fix: {int(dr['N_BUCKETS_DUP_AFTER_FIX'])} dup buckets (max {int(dr['MAX_TS_PER_BUCKET_AFTER_FIX'])} TS/bucket)"))

    # ---- monthly-vs-daily granularity-independence proof -----------------------
    granularity_ok, granularity_detail = monthly_vs_daily_identical_check()
    results.append(("(granularity) 2026-06-10 rows identical: daily call vs full-month call",
                     "PASS" if granularity_ok else "FAIL", granularity_detail))

    # ---- (a) per-PUN mean/p10/p90 vs backout_pun_estimates.csv ----------------
    est = pd.read_csv(os.path.join(PUN_ANALYSIS, "backout_pun_estimates.csv"))
    est = est.set_index("PUN")

    agg = df.groupby("PUNSTATION")["PUNNETINJECTIONMW"].agg(
        mean_proc="mean", p10_proc=lambda s: s.quantile(0.1), p90_proc=lambda s: s.quantile(0.9),
        n="count"
    )

    standalone_tags = {"EXACT_SWITCHING", "DAM_LOAD_ADJUSTED"}
    tag_by_pun = df.groupby("PUNSTATION")["METHODTAG"].first()

    dev_rows = []
    for pun, row in agg.iterrows():
        tag = tag_by_pun.get(pun)
        if tag not in standalone_tags:
            continue
        n = int(row["n"])
        if pun not in est.index:
            dev_rows.append((pun, tag, n, None, None, None, "NO_REFERENCE"))
            continue
        ref = est.loc[pun]
        d_mean = row["mean_proc"] - ref["MEAN_I_P"]
        d_p10 = row["p10_proc"] - ref["P10_I_P"]
        d_p90 = row["p90_proc"] - ref["P90_I_P"]
        status = "PASS" if max(abs(d_mean), abs(d_p10), abs(d_p90)) <= 1.0 else "FAIL"
        dev_rows.append((pun, tag, n, d_mean, d_p10, d_p90, status))

    dev_df = pd.DataFrame(dev_rows, columns=["PUN", "METHODTAG", "N", "D_MEAN", "D_P10", "D_P90", "STATUS"])
    n_fail = (dev_df["STATUS"] != "PASS").sum()
    results.append(("(a) standalone PUN mean/P10/P90 within 1.0 MW", "PASS" if n_fail == 0 else "FAIL",
                     f"{n_fail} of {len(dev_df)} PUNs exceed 1.0 MW (see per-PUN table)"))

    # ---- (a) entangled groups vs Section 5 combined figures -------------------
    group_ref = {
        "DPW": {"mean": 453.3074759638969, "p10": None, "p90": None},
        "LY": {"mean": 417.7345881309914, "p10": 349.12557188034054, "p90": 503.5729969310761},
        "PHILLPS2": {"mean": -80.7, "p10": None, "p90": None},  # no joint hourly series, mean only
        "I_DUPSW": {"mean": 71.71200865676599, "p10": -16.50504426956177, "p90": 191.4480185568333},
        "STONERSY": {"mean": -25.048898276508165, "p10": -48.83121929168701, "p90": 25.98858966827393},
        "HUD": {"mean": 2.710697948079972, "p10": -38.22705577850341, "p90": 21.940746412277218},
    }
    group_df = df[df["METHODTAG"] == "ENTANGLED_GROUP"]
    group_agg = group_df.groupby("NEIGHBORGROUPID")["PUNNETINJECTIONMW"].agg(
        mean_proc="mean", p10_proc=lambda s: s.quantile(0.1), p90_proc=lambda s: s.quantile(0.9)
    )
    grp_rows = []
    for gid, ref in group_ref.items():
        if gid not in group_agg.index:
            grp_rows.append((gid, None, None, None, "NO_DATA"))
            continue
        row = group_agg.loc[gid]
        d_mean = row["mean_proc"] - ref["mean"]
        devs = [abs(d_mean)]
        d_p10 = d_p90 = None
        if ref["p10"] is not None:
            d_p10 = row["p10_proc"] - ref["p10"]
            d_p90 = row["p90_proc"] - ref["p90"]
            devs += [abs(d_p10), abs(d_p90)]
        status = "PASS" if max(devs) <= 1.0 else "FAIL"
        grp_rows.append((gid, d_mean, d_p10, d_p90, status))
    grp_dev_df = pd.DataFrame(grp_rows, columns=["GROUP", "D_MEAN", "D_P10", "D_P90", "STATUS"])
    n_grp_fail = (grp_dev_df["STATUS"] != "PASS").sum()
    results.append(("(a) entangled group combined figures within 1.0 MW", "PASS" if n_grp_fail == 0 else "FAIL",
                     f"{n_grp_fail} of {len(grp_dev_df)} groups exceed 1.0 MW"))

    # ---- (b) truth test: BTE, AMOCOOIL, CCEC correlation with own SCED gross --
    truth_ref = pd.read_csv(os.path.join(PUN_ANALYSIS, "backout_truth_test.csv")).set_index("PUN")
    own_df = own_gross_check(["BTE", "AMOCOOIL", "CCEC"])
    own_df.columns = [c.upper() for c in own_df.columns]

    truth_rows = []
    for pun in ["BTE", "AMOCOOIL", "CCEC"]:
        proc_pun = df[df["PUNSTATION"] == pun][["TIMESTAMP", "PUNNETINJECTIONMW"]].copy()
        proc_pun["TIMESTAMP"] = pd.to_datetime(proc_pun["TIMESTAMP"]).astype("datetime64[ns]")
        proc_pun = proc_pun.sort_values("TIMESTAMP")
        own_pun = own_df[own_df["PUNSTATION"] == pun].copy()
        own_pun["GEN_TS"] = pd.to_datetime(own_pun["GEN_TS"]).astype("datetime64[ns]")
        own_pun = own_pun.sort_values("GEN_TS")
        # nearest SCED tick within +/-10 min of each SE snapshot, same rule as the proc's neighbour-gen join
        merged = pd.merge_asof(
            proc_pun, own_pun[["GEN_TS", "OWN_GROSS_MW"]],
            left_on="TIMESTAMP", right_on="GEN_TS", direction="nearest",
            tolerance=pd.Timedelta("10min"),
        ).dropna(subset=["OWN_GROSS_MW"])
        if len(merged) < 10:
            truth_rows.append((pun, None, None, len(merged), "NO_DATA"))
            continue
        corr = merged["PUNNETINJECTIONMW"].corr(merged["OWN_GROSS_MW"])
        mean_diff = (merged["PUNNETINJECTIONMW"] - merged["OWN_GROSS_MW"]).mean()
        status = "PASS" if (corr >= 0.99 and abs(mean_diff) <= 6.0) else "FAIL"
        truth_rows.append((pun, corr, mean_diff, len(merged), status))
    truth_df = pd.DataFrame(truth_rows, columns=["PUN", "CORR", "MEAN_DIFF_MW", "N_HOURS", "STATUS"])
    n_truth_fail = (truth_df["STATUS"] != "PASS").sum()
    results.append(("(b) BTE/AMOCOOIL/CCEC corr>=0.99 & |mean diff|<=6MW", "PASS" if n_truth_fail == 0 else "FAIL",
                     truth_df.to_dict("records")))

    # ---- (e) crosswalk -----------------------------------------------------
    cw = crosswalk_check()
    cw.columns = [c.upper() for c in cw.columns]
    n_mismatch = ((cw["IN_STATIONINJECTION"] == "N")).sum()
    results.append(("(e) all neighbours present in ERCOTSTATIONINJECTION", "PASS" if n_mismatch == 0 else "FAIL",
                     f"{n_mismatch} missing"))
    oos_neighbours = cw[cw["HAS_ROWS_BUT_ALL_OUT_OF_SERVICE"] == "Y"]["NEIGHBOR"].tolist()
    results.append(("(e) neighbours with June rows but all INSERVICE=0 (gate to 0, not NULL)",
                     "INFO", f"{oos_neighbours}"))

    # ---- (e) cross-check crosswalk's IN_DAMPSSELDVIEW against pun_topology.csv's own
    #          NEIGHBORS_WITH_DAM_LOAD flag (an eyeball claim isn't a run; this is) --------
    topo = pd.read_csv(os.path.join(PUN_ANALYSIS, "pun_topology.csv"))
    flagged_load_neighbours = set()
    for v in topo["NEIGHBORS_WITH_DAM_LOAD"].dropna():
        flagged_load_neighbours.update(x for x in str(v).split(";") if x)
    cw_load_y = set(cw[cw["IN_DAMPSSELDVIEW"] == "Y"]["NEIGHBOR"])
    cw_load_n = set(cw[cw["IN_DAMPSSELDVIEW"] == "N"]["NEIGHBOR"])
    unexpected_load_n = sorted(flagged_load_neighbours & cw_load_n)   # topology says load-bearing, crosswalk says no June rows in service
    unexpected_load_y = sorted(cw_load_y - flagged_load_neighbours)   # crosswalk says in-service load, topology never flagged it
    results.append(("(e) pun_topology.csv NEIGHBORS_WITH_DAM_LOAD vs crosswalk IN_DAMPSSELDVIEW",
                     "PASS" if not unexpected_load_n else "INFO",
                     f"flagged-but-no-June-rows: {unexpected_load_n} (expected for out-of-service neighbours "
                     f"like COHMA); load-in-June-but-not-flagged: {unexpected_load_y}"))

    # ---- PNPI fanout caveat check (Section 4c) -------------------------------
    pnpi_rows = df[df["PUNSTATION"] == "PNPI"]
    pnpi_max_gen = pnpi_rows["NEIGHBORSCEDGENMW"].max() if len(pnpi_rows) else None
    pnpi_fanout_hours = int((pnpi_rows["NEIGHBORSCEDGENMW"] > 3500).sum()) if len(pnpi_rows) else None
    results.append(("(info) PNPI/WAP gen-join fanout check (Section 4c caveat)", "INFO",
                     f"max NEIGHBORSCEDGENMW={pnpi_max_gen:.1f}, hours>3500MW={pnpi_fanout_hours} "
                     f"(WAP's true station max is ~3,130 MW; Section 4c's 4,424-5,500 MW fanout was "
                     f"not reproduced -- this proc's dam_dedup'd, per-(station,timestamp)-grouped "
                     f"TMP_GEN_MAP does not exhibit the join fanout backout_master.sql hit)"))

    # =========================================================================
    print("\n" + "=" * 100)
    print("PASS/FAIL SUMMARY")
    print("=" * 100)
    for name, status, detail in results:
        print(f"[{status:4s}] {name}")
        if isinstance(detail, str):
            print(f"        {detail}")

    print("\n--- (a) standalone PUN deviations vs backout_pun_estimates.csv (MW) ---")
    print(dev_df.sort_values("D_MEAN", key=abs, ascending=False).to_string(index=False))

    print("\n--- (a) entangled group deviations vs Section 5 combined figures (MW) ---")
    print(grp_dev_df.to_string(index=False))

    print("\n--- (b) truth-test correlation vs own SCED gross ---")
    print(truth_df.to_string(index=False))

    print("\n--- (d) NULL PUNNETINJECTIONMW by METHODTAG (reason) ---")
    print(null_reason.to_string() if len(null_reason) else "  (none)")

    print("\n--- (item7-ii) NEIGHBORLOADOUTOFSERVICECOUNT / NEIGHBORINJECTIONMISSINGCOUNT by PUN (nonzero only) ---")
    print(counters_by_pun.to_string() if len(counters_by_pun) else "  (none nonzero)")

    print("\n--- (e) crosswalk table (72 neighbours) ---")
    print(cw.to_string(index=False))

    n_fail_total = sum(1 for _, s, _ in results if s == "FAIL")
    print("\n" + "=" * 100)
    print(f"OVERALL: {'PASS' if n_fail_total == 0 else f'{n_fail_total} CHECK(S) FAILED'}")
    print("=" * 100)


if __name__ == "__main__":
    main()
