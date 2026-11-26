-- ============================================================================
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_PUN_INJECTION
--
-- PUN net export, backed out from the ERCOT-side neighbour of each redacted
-- tie (I_PUN = N_S - Gen_S + Load_S). Target: AWDEV.ERCOTRT.ERCOTPUNINJECTION,
-- grain (TIMESTAMP, PUNSTATION). Depends on AWDEV.ERCOTRT.ERCOTPUNTIEMAP.
-- Positive PUNNETINJECTIONMW = PUN exports to the grid.
--
-- See SESSION_HANDOFF.md ("PUN injection loader") for the NULL-vs-zero
-- design, the HOUR_BUCKET/HE convention, and the 2026-09-25 grading-gate
-- fixes (CO/COHMA out-of-service fallback, duplicate-snapshot dedup, N_S
-- NULL gate, EXACT_SWITCHING short-circuit); PUN_BACKOUT_FINDINGS.md
-- Section 7 for the physics and design sketch this implements.
-- ============================================================================

CREATE OR REPLACE TABLE AWDEV.ERCOTRT.ERCOTPUNINJECTION (
    "TIMESTAMP"                     TIMESTAMP_NTZ(0),
    HOURBUCKET                      TIMESTAMP_NTZ(0),
    PUNSTATION                      VARCHAR(30),
    NEIGHBORGROUPID                 VARCHAR(30),
    METHODTAG                       VARCHAR(30),
    NEIGHBORNETINJECTIONMW          FLOAT,
    NEIGHBORINJECTIONMISSINGCOUNT   INTEGER,
    NEIGHBORSCEDGENMW               FLOAT,
    SCEDTIMESTAMP                   TIMESTAMP_NTZ(9),
    NEIGHBORDAMLOADMW               FLOAT,
    NEIGHBORLOADOUTOFSERVICECOUNT   INTEGER,
    PUNNETINJECTIONMW               FLOAT,
    LOADTS                          TIMESTAMP_NTZ(9)
);

CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_LOAD_ERCOT_PUN_INJECTION(
    P_START_DATE DATE,
    P_END_DATE   DATE
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    v_end      TIMESTAMP_NTZ;
    v_deleted  INTEGER DEFAULT 0;
    v_inserted INTEGER DEFAULT 0;
BEGIN
    IF (P_START_DATE IS NULL OR P_END_DATE IS NULL OR P_START_DATE > P_END_DATE) THEN
        RETURN 'ERROR: need non-null P_START_DATE <= P_END_DATE.';
    END IF;
    v_end := DATEADD(DAY, 1, P_END_DATE);

    -- Small: the 72-neighbour inventory from the tie map. Every downstream
    -- filter against a large table goes through this first.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_LIST AS
    SELECT DISTINCT NEIGHBORSTATION
    FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP
    WHERE NEIGHBORSTATION IS NOT NULL;

    -- Small tables only; dam_dedup guards a CPNODEID resolving to >1 station
    -- (ROW_NUMBER by row-count DESC), deduped over the FULL population before
    -- the neighbour filter so restricting the station list can't change a tie.
    CREATE OR REPLACE TEMPORARY TABLE TMP_GEN_MAP AS
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
    )
    SELECT g.GENID, dd.STATIONNAME AS NEIGHBORSTATION
    FROM AW.DBO.ISOERCOTSCEDGEN g
    JOIN dam_dedup dd ON dd.CPNODEID = g.CPNODEID
    WHERE dd.STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST);

    CREATE OR REPLACE TEMPORARY TABLE TMP_GEN_STATIONS AS
    SELECT DISTINCT NEIGHBORSTATION FROM TMP_GEN_MAP;

    -- The only scan of ERCOTSTATIONINJECTION (259M rows): station list AND
    -- range filtered first. One row per (TIMESTAMP, NEIGHBORSTATION, KVLEVEL).
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_SI_RAW AS
    SELECT si."TIMESTAMP" AS SE_TS, si.NMMSSTATIONCODE AS NEIGHBORSTATION, si.NETINJECTIONMW
    FROM AW.DBO.ERCOTSTATIONINJECTION si
    WHERE si.NMMSSTATIONCODE IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND si."TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ)
      AND si."TIMESTAMP" <  DATEADD(MINUTE, -30, :v_end);

    -- One SE_TS per HOURBUCKET across the neighbour set: most neighbour rows
    -- in the bucket wins, latest SE_TS on ties -- same rule as
    -- SP_LOAD_ERCOT_STATION_INJECTION's own TMP_SNAPSHOT, applied here too
    -- since that global dedup only guarantees uniqueness account-wide, not
    -- necessarily restricted to a 72-station subset at every historical range.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_SNAPSHOT AS
    SELECT SE_TS, DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) AS HOURBUCKET
    FROM (SELECT SE_TS, COUNT(*) AS N FROM TMP_NEIGHBOR_SI_RAW GROUP BY SE_TS)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, SE_TS)) ORDER BY N DESC, SE_TS DESC
    ) = 1;

    -- Full (snapshot x neighbour) grid: every neighbour gets a row at every
    -- chosen snapshot, so a neighbour with NO ERCOTSTATIONINJECTION row that
    -- hour is visible as a gap (NULL below) instead of silently vanishing
    -- from the group SUM.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_GRID AS
    SELECT s.SE_TS, s.HOURBUCKET, nl.NEIGHBORSTATION
    FROM TMP_NEIGHBOR_SNAPSHOT s
    CROSS JOIN TMP_NEIGHBOR_LIST nl;

    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_SI AS
    SELECT g.SE_TS, g.HOURBUCKET, g.NEIGHBORSTATION, SUM(r.NETINJECTIONMW) AS NET_INJ_MW
    FROM TMP_NEIGHBOR_GRID g
    LEFT JOIN TMP_NEIGHBOR_SI_RAW r ON r.SE_TS = g.SE_TS AND r.NEIGHBORSTATION = g.NEIGHBORSTATION
    GROUP BY g.SE_TS, g.HOURBUCKET, g.NEIGHBORSTATION;

    -- The only scan of ISOERCOTSCEDGENRESOURCE (large, 5-min ticks): GENID
    -- set from TMP_GEN_MAP (a handful of units across 5 stations) AND range
    -- filtered first, padded +/-10 min beyond the SE range for the nearest-
    -- tick match below.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_GEN_TICK AS
    SELECT gm.NEIGHBORSTATION, r."TIMESTAMP" AS GEN_TS, SUM(r.TELEMETEREDOUTPUT) AS GEN_MW
    FROM AW.DBO.ISOERCOTSCEDGENRESOURCE r
    JOIN TMP_GEN_MAP gm ON gm.GENID = r.GENID
    WHERE r."TIMESTAMP" >= DATEADD(MINUTE, -40, :P_START_DATE::TIMESTAMP_NTZ)
      AND r."TIMESTAMP" <  DATEADD(MINUTE, 10, :v_end)
    GROUP BY gm.NEIGHBORSTATION, r."TIMESTAMP";

    -- Nearest SCED tick within +/-10 min of each snapshot, per neighbour.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_GEN AS
    SELECT g.SE_TS, g.NEIGHBORSTATION, t.GEN_TS, t.GEN_MW
    FROM TMP_NEIGHBOR_GRID g
    LEFT JOIN TMP_NEIGHBOR_GEN_TICK t
      ON t.NEIGHBORSTATION = g.NEIGHBORSTATION
     AND t.GEN_TS BETWEEN DATEADD(MINUTE, -10, g.SE_TS) AND DATEADD(MINUTE, 10, g.SE_TS)
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY g.SE_TS, g.NEIGHBORSTATION
        ORDER BY ABS(TIMESTAMPDIFF(SECOND, g.SE_TS, t.GEN_TS)) ASC NULLS LAST
    ) = 1;

    -- DAM load per neighbour, keyed (STATIONNAME, DATE, HE). Carries both the
    -- INSERVICE=1 sum and the all-rows sum, plus row/inservice counts, so the
    -- component logic below can fall back to the all-rows sum for a key whose
    -- rows are all INSERVICE=0 but carry real load (a modelled bus transfer,
    -- e.g. CO 2026-06-30 HE8-20 / COHMA all June), instead of reading that
    -- key as missing. "DATE" >= P_START_DATE/<= P_END_DATE is exact under the
    -- HE=HOUR(HOURBUCKET)+1 convention (see SESSION_HANDOFF.md): the -30min
    -- SE padding never pushes HOURBUCKET's calendar date outside that range.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_LOAD AS
    SELECT STATIONNAME AS NEIGHBORSTATION, "DATE" AS LOAD_DATE, HE,
           SUM(IFF(INSERVICE = 1, RAWMWLDF, 0)) AS LOAD_MW_INSERVICE,
           COUNT_IF(INSERVICE = 1) AS N_INSERVICE,
           SUM(RAWMWLDF) AS LOAD_MW_ALL,
           COUNT(*) AS N_ROWS
    FROM AW.DBO.ERCOTDAMPSSELDVIEW
    WHERE STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND "DATE" >= :P_START_DATE AND "DATE" <= :P_END_DATE
    GROUP BY STATIONNAME, "DATE", HE;

    -- Presence-only check (any row at all, any INSERVICE), keyed by
    -- (NEIGHBORSTATION, calendar MONTH) and computed over every WHOLE
    -- calendar month the call range touches -- independent of
    -- P_START_DATE/P_END_DATE's exact day boundaries, so a 1-day call and a
    -- full-month call covering the same month agree on presence (2026-09-25
    -- fix: the first version scoped presence to [P_START_DATE,P_END_DATE]
    -- exactly, which reintroduced the granularity dependence the range-scoped
    -- TMP_LOAD_STATIONS flag had -- a daily call could see a different
    -- presence verdict for a neighbour than a monthly call covering the same
    -- day). Distinguishes "this neighbour never reports load this month" (0,
    -- structural -- e.g. FM524/MTS/DPW, zero rows ever; SRB, zero rows in
    -- June though it has rows pre-2022) from "reports elsewhere this month
    -- but this exact (DATE,HE) key is empty" (NULL -- e.g. LOLITA 2026-06-16
    -- HE9-14). Needed because several groups (SL/BOG, DIB/SRB, EQUISTAR/
    -- LON_HILL, LY/MTS, DPW-group/DPW, PHILLPS2-group/FM524+LINVILLE+
    -- WCOLMAIN, NCARBIDE/CANGREJO+PV_TAP) have a real neighbour that has
    -- never had a load row -- without this gate those groups NULL forever.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_LOAD_PRESENT AS
    SELECT DISTINCT STATIONNAME AS NEIGHBORSTATION, DATE_TRUNC('MONTH', "DATE") AS LOAD_MONTH
    FROM AW.DBO.ERCOTDAMPSSELDVIEW
    WHERE STATIONNAME IN (SELECT NEIGHBORSTATION FROM TMP_NEIGHBOR_LIST)
      AND "DATE" >= DATE_TRUNC('MONTH', :P_START_DATE)
      AND "DATE" <  DATEADD('MONTH', 1, DATE_TRUNC('MONTH', :P_END_DATE));

    -- Per (snapshot, neighbour) component. GEN: absent from TMP_GEN_STATIONS
    -- (no mapped unit at all) -> 0; mapped but no tick within +/-10 min ->
    -- NULL. LOAD: absent from TMP_NEIGHBOR_LOAD_PRESENT -> 0; present but
    -- this (DATE,HE) key has zero rows -> NULL; key has rows, none in
    -- service -> LOAD_MW_ALL (fallback fired, counted); else LOAD_MW_INSERVICE.
    CREATE OR REPLACE TEMPORARY TABLE TMP_NEIGHBOR_COMPONENTS AS
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
     AND lp.LOAD_MONTH = DATE_TRUNC('MONTH', TO_DATE(si.HOURBUCKET));

    -- Fan each neighbour's component out to every group containing it
    -- (DISTINCT, so a neighbour shared across PUNs, e.g. DPW under LYD and
    -- CHE, is summed once per group), then collapse to (TIMESTAMP,
    -- NEIGHBORGROUPID). TMP_NEIGHBOR_COMPONENTS already covers the full grid
    -- (every neighbour x every chosen snapshot), so this JOIN never drops a
    -- neighbour silently; a missing N_S/gen/load reading surfaces as NULL via
    -- the IFF(COUNT_IF...) pattern instead.
    CREATE OR REPLACE TEMPORARY TABLE TMP_GROUP_INJECTION AS
    WITH group_neighbors AS (
        SELECT DISTINCT NEIGHBORGROUPID, NEIGHBORSTATION
        FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP
        WHERE NEIGHBORSTATION IS NOT NULL
    )
    SELECT gn.NEIGHBORGROUPID, c.SE_TS, c.HOURBUCKET,
           IFF(COUNT_IF(c.NET_INJ_MW IS NULL) > 0, NULL, SUM(c.NET_INJ_MW)) AS NEIGHBORNETINJECTIONMW,
           COUNT_IF(c.NET_INJ_MW IS NULL) AS NEIGHBORINJECTIONMISSINGCOUNT,
           IFF(COUNT_IF(c.GEN_COMPONENT IS NULL) > 0, NULL, SUM(c.GEN_COMPONENT)) AS NEIGHBORSCEDGENMW,
           MAX(c.SCED_TS) AS SCEDTIMESTAMP,
           IFF(COUNT_IF(c.LOAD_COMPONENT IS NULL) > 0, NULL, SUM(c.LOAD_COMPONENT)) AS NEIGHBORDAMLOADMW,
           SUM(IFF(c.LOAD_OUT_OF_SERVICE_FIRED = 1, 1, 0)) AS NEIGHBORLOADOUTOFSERVICECOUNT
    FROM group_neighbors gn
    JOIN TMP_NEIGHBOR_COMPONENTS c ON c.NEIGHBORSTATION = gn.NEIGHBORSTATION
    GROUP BY gn.NEIGHBORGROUPID, c.SE_TS, c.HOURBUCKET;

    -- Fan the group figure out to every PUN in the group. EXACT_SWITCHING is
    -- structural, not empirical: PUNNETINJECTIONMW = N_S directly, with no
    -- dependency on the gen/load legs at all (so a genuinely missing DOW HE,
    -- say, can never NULL DOWGEN); NEIGHBORSCEDGENMW/NEIGHBORDAMLOADMW are
    -- reported as 0 for those rows regardless of what the general computation
    -- produced. NOT_ESTIMABLE PUNs carry no NEIGHBORGROUPID and so never
    -- produce a row here.
    CREATE OR REPLACE TEMPORARY TABLE TMP_PUN_INJECTION AS
    SELECT gi.SE_TS AS "TIMESTAMP", gi.HOURBUCKET, m.PUNSTATION, gi.NEIGHBORGROUPID, m.METHODTAG,
           gi.NEIGHBORNETINJECTIONMW, gi.NEIGHBORINJECTIONMISSINGCOUNT,
           IFF(m.METHODTAG = 'EXACT_SWITCHING', 0, gi.NEIGHBORSCEDGENMW) AS NEIGHBORSCEDGENMW,
           gi.SCEDTIMESTAMP,
           IFF(m.METHODTAG = 'EXACT_SWITCHING', 0, gi.NEIGHBORDAMLOADMW) AS NEIGHBORDAMLOADMW,
           gi.NEIGHBORLOADOUTOFSERVICECOUNT,
           IFF(m.METHODTAG = 'EXACT_SWITCHING',
               gi.NEIGHBORNETINJECTIONMW,
               gi.NEIGHBORNETINJECTIONMW - gi.NEIGHBORSCEDGENMW + gi.NEIGHBORDAMLOADMW) AS PUNNETINJECTIONMW,
           CURRENT_TIMESTAMP() AS LOADTS
    FROM TMP_GROUP_INJECTION gi
    JOIN (
        SELECT DISTINCT PUNSTATION, NEIGHBORGROUPID, METHODTAG
        FROM AWDEV.ERCOTRT.ERCOTPUNTIEMAP
        WHERE NEIGHBORGROUPID IS NOT NULL
    ) m ON m.NEIGHBORGROUPID = gi.NEIGHBORGROUPID;

    IF ((SELECT COUNT(*) FROM TMP_PUN_INJECTION) = 0) THEN
        RETURN 'OK: no usable rows for ' || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR || ', target untouched.';
    END IF;

    BEGIN TRANSACTION;
    DELETE FROM AWDEV.ERCOTRT.ERCOTPUNINJECTION
    WHERE "TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ)
      AND "TIMESTAMP" <  DATEADD(MINUTE, -30, :v_end);
    v_deleted := SQLROWCOUNT;
    INSERT INTO AWDEV.ERCOTRT.ERCOTPUNINJECTION
        ("TIMESTAMP", HOURBUCKET, PUNSTATION, NEIGHBORGROUPID, METHODTAG,
         NEIGHBORNETINJECTIONMW, NEIGHBORINJECTIONMISSINGCOUNT,
         NEIGHBORSCEDGENMW, SCEDTIMESTAMP,
         NEIGHBORDAMLOADMW, NEIGHBORLOADOUTOFSERVICECOUNT,
         PUNNETINJECTIONMW, LOADTS)
    SELECT "TIMESTAMP", HOURBUCKET, PUNSTATION, NEIGHBORGROUPID, METHODTAG,
           NEIGHBORNETINJECTIONMW, NEIGHBORINJECTIONMISSINGCOUNT,
           NEIGHBORSCEDGENMW, SCEDTIMESTAMP,
           NEIGHBORDAMLOADMW, NEIGHBORLOADOUTOFSERVICECOUNT,
           PUNNETINJECTIONMW, LOADTS
    FROM TMP_PUN_INJECTION
    ORDER BY 1, 3;   -- (TIMESTAMP, PUNSTATION)
    v_inserted := SQLROWCOUNT;
    COMMIT;

    RETURN 'OK: ' || v_deleted || ' rows deleted, ' || v_inserted || ' rows inserted for '
           || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR;

EXCEPTION
    WHEN OTHER THEN
        ROLLBACK;
        RAISE;
END;
$$;


-- ===========================================================================
-- Usage
-- ===========================================================================
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_PUN_INJECTION('2026-06-01', '2026-06-30');


-- ===========================================================================
-- Verification
-- ===========================================================================
-- Grain uniqueness:
-- SELECT "TIMESTAMP", PUNSTATION, COUNT(*) FROM AWDEV.ERCOTRT.ERCOTPUNINJECTION
-- GROUP BY 1,2 HAVING COUNT(*) > 1;
--
-- EXACT_SWITCHING must never carry a NULL PUNNETINJECTIONMW:
-- SELECT PUNSTATION, COUNT(*) AS N_NULL FROM AWDEV.ERCOTRT.ERCOTPUNINJECTION
-- WHERE METHODTAG = 'EXACT_SWITCHING' AND PUNNETINJECTIONMW IS NULL
-- GROUP BY PUNSTATION;
--
-- Per-PUN mean vs backout_pun_estimates.csv (should match within ~1 MW for
-- EXACT_SWITCHING/DAM_LOAD_ADJUSTED; see validate_pun_injection.py):
-- SELECT PUNSTATION, METHODTAG, COUNT(*) N_HOURS, AVG(PUNNETINJECTIONMW) MEAN_I_P,
--        SUM(NEIGHBORLOADOUTOFSERVICECOUNT) OOS_HOURS, SUM(NEIGHBORINJECTIONMISSINGCOUNT) MISSING_SI_HOURS
-- FROM AWDEV.ERCOTRT.ERCOTPUNINJECTION GROUP BY 1,2 ORDER BY 1;
