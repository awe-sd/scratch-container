-- FAST_SCAN_RT_CONSTRAINTS: every constraint binding on a fast-scan config's branch at the
-- SCED interval nearest each SE snapshot, one row per contingency (grain: CONFIG_ID, TIMESTAMP,
-- CONTINGENCY). FAST_SCAN_RESULTS keeps only the config's own contingency; this table lets the
-- other contingencies binding at the same time be pulled in by join.
-- Only binding intervals exist in CONGFQPRICEVIEW, so absence of a (snapshot, contingency) row
-- means that contingency was not binding near that snapshot -- not that data is missing.
-- Called by SP_RUN_FAST_SCAN_TEST_V2 after its main insert, but runs standalone too.

CREATE TABLE IF NOT EXISTS AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS (
    CONFIG_ID           NUMBER        NOT NULL,
    TIMESTAMP           TIMESTAMP_NTZ NOT NULL,   -- SE snapshot stamp, same as FAST_SCAN_RESULTS.TIMESTAMP
    RT_INTERVAL         TIMESTAMP_NTZ NOT NULL,   -- SCED interval nearest the snapshot with any binding row for the branch
    CONTINGENCY         VARCHAR       NOT NULL,   -- CONGDEFCONSTRAINTVIEW.CONGCONTNAME
    IS_CONFIG_CTG       BOOLEAN       NOT NULL,   -- TRUE for the contingency the fast scan is for
    CONSTRAINT_NAME     VARCHAR,                  -- CONGDEFCONSTRAINTVIEW.ISOCONSTRAINTNAME
    RT_CONSTRAINT_VALUE FLOAT,                    -- ABS(CONSTRAINTVALUE)
    RT_CONSTRAINT_LIMIT FLOAT,
    RT_ACTUAL_HEADROOM  FLOAT,                    -- limit - value
    COMPUTED_AT         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE PROCEDURE AW.FLOW_ANALYSIS.SP_LOAD_FAST_SCAN_RT_CONSTRAINTS("P_CONFIG_ID" NUMBER(38,0), "P_START_DATE" DATE, "P_END_DATE" DATE, "P_ISO_MARKET_ID" NUMBER(38,0) DEFAULT 6)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_from_num INT;
    v_to_num INT;
    v_ckt VARCHAR(10);
    v_ptoid INT;
    v_ctg_label VARCHAR(100);
    v_start TIMESTAMP_NTZ;
    v_end TIMESTAMP_NTZ;
    v_rows_deleted INT;
    v_rows_inserted INT;
BEGIN

    -- 1. Get config parameters
    IF (:P_START_DATE IS NULL OR :P_END_DATE IS NULL) THEN
        RETURN OBJECT_CONSTRUCT(''status'', ''ERROR'', ''error'', ''dates required'');
    END IF;

    SELECT FROM_NUM, TO_NUM, CKT, PTOID, CTG_LABEL
    INTO :v_from_num, :v_to_num, :v_ckt, :v_ptoid, :v_ctg_label
    FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
    WHERE CONFIG_ID = :P_CONFIG_ID;

    -- 2. SE snapshots are stamped :57 for the top of the next hour, so the date range is
    -- applied in nearest-hour terms by shifting 30 minutes earlier on both ends.
    v_start := DATEADD(''MINUTE'', -30, :P_START_DATE::TIMESTAMP_NTZ);
    v_end := DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :P_END_DATE)::TIMESTAMP_NTZ);

    -- 3. Clear any existing rows for this config in the date range
    DELETE FROM FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS
    WHERE CONFIG_ID = :P_CONFIG_ID AND TIMESTAMP >= :v_start AND TIMESTAMP < :v_end;
    v_rows_deleted := SQLROWCOUNT;

    -- 4. Load every binding contingency on the branch near each snapshot
    INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS (
        CONFIG_ID, TIMESTAMP, RT_INTERVAL, CONTINGENCY, IS_CONFIG_CTG,
        CONSTRAINT_NAME, RT_CONSTRAINT_VALUE, RT_CONSTRAINT_LIMIT, RT_ACTUAL_HEADROOM
    )
    WITH Snapshots AS (
        SELECT DISTINCT "TIMESTAMP" AS TIMESTAMP
        FROM AW.DBO.ERCOTSTATIONINJECTION
        WHERE "TIMESTAMP" >= :v_start AND "TIMESTAMP" < :v_end
    ),
    BranchIds AS (
        SELECT DISTINCT BRANCHID FROM AW.DBO.PTOBRANCH
        WHERE ((FROMNUM = :v_from_num AND TONUM = :v_to_num AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR)))
            OR (FROMNUM = :v_to_num AND TONUM = :v_from_num AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR))))
          AND PTOID = :v_ptoid
    ),
    Binding AS (   -- every binding row for the branch within 30 min of a snapshot
        SELECT s.TIMESTAMP, cfp.DATETIME AS RT_INTERVAL, cdc.CONGCONTNAME AS CONTINGENCY, cdc.ISOCONSTRAINTNAME AS CONSTRAINT_NAME,
               ABS(cfp.CONSTRAINTVALUE) AS RT_VALUE, cfp.CONSTRAINTLIMIT AS RT_LIMIT
        FROM Snapshots s
        JOIN AW.DBO.CONGFQPRICEVIEW cfp
          ON cfp.ISOMARKETID = :P_ISO_MARKET_ID AND cfp.PRICETYPEID = 2
         AND cfp."DATE" BETWEEN DATEADD(''DAY'', -1, :P_START_DATE) AND DATEADD(''DAY'', 1, :P_END_DATE)
         AND cfp.DATETIME BETWEEN DATEADD(''MINUTE'', -30, s.TIMESTAMP) AND DATEADD(''MINUTE'', 30, s.TIMESTAMP)
        JOIN AW.DBO.CONGDEFCONSTRAINTVIEW cdc ON cdc.CONGCONSTRAINTID = cfp.CONGCONSTRAINTID
        JOIN BranchIds b ON b.BRANCHID = cdc.BRANCHID
    ),
    NearestInterval AS (   -- one interval per snapshot: nearest to the snapshot, latest on ties
        SELECT TIMESTAMP, RT_INTERVAL
        FROM (SELECT DISTINCT TIMESTAMP, RT_INTERVAL FROM Binding)
        QUALIFY ROW_NUMBER() OVER (PARTITION BY TIMESTAMP ORDER BY ABS(TIMESTAMPDIFF(SECOND, TIMESTAMP, RT_INTERVAL)), RT_INTERVAL DESC) = 1
    )
    SELECT :P_CONFIG_ID, b.TIMESTAMP, b.RT_INTERVAL, b.CONTINGENCY,
           REPLACE(UPPER(b.CONTINGENCY), '' '', '''') = REPLACE(UPPER(:v_ctg_label), '' '', '''') AS IS_CONFIG_CTG,
           b.CONSTRAINT_NAME, ROUND(b.RT_VALUE, 2), ROUND(b.RT_LIMIT, 2), ROUND(b.RT_LIMIT - b.RT_VALUE, 2)
    FROM Binding b
    JOIN NearestInterval n ON n.TIMESTAMP = b.TIMESTAMP AND n.RT_INTERVAL = b.RT_INTERVAL
    QUALIFY ROW_NUMBER() OVER (PARTITION BY b.TIMESTAMP, b.CONTINGENCY ORDER BY b.RT_VALUE DESC) = 1;   -- one row per contingency

    v_rows_inserted := SQLROWCOUNT;

    RETURN OBJECT_CONSTRUCT(
        ''status'', ''SUCCESS'',
        ''config_id'', :P_CONFIG_ID,
        ''date_range'', :P_START_DATE || '' to '' || :P_END_DATE,
        ''rows_deleted'', :v_rows_deleted,
        ''rows_inserted'', :v_rows_inserted
    );

EXCEPTION
    WHEN OTHER THEN
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'', ''error'', :SQLERRM);
END;
';

-- Standalone usage:
-- CALL AW.FLOW_ANALYSIS.SP_LOAD_FAST_SCAN_RT_CONSTRAINTS(1, '2024-06-01', '2024-06-07');

-- Worst other contingency binding alongside the config's own, per snapshot:
-- SELECT r.CONFIG_ID, r.TIMESTAMP, MIN(c.RT_ACTUAL_HEADROOM) AS WORST_OTHER_HEADROOM, COUNT(*) AS OTHER_BINDING_CTGS
-- FROM AW.FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS c JOIN AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS r ON r.CONFIG_ID = c.CONFIG_ID AND r.TIMESTAMP = c.TIMESTAMP
-- WHERE NOT c.IS_CONFIG_CTG GROUP BY 1, 2;
