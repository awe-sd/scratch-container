-- Runbook (role AW_ACCESS): create a fresh, forced VALIDATION config for every existing
-- validation scan of study 14218, run V2 on each immediately, and log V1-vs-V2 timing/results
-- so both can be compared side by side. Verified 2026-09-25 (role AI_READ_ONLY): 116 VALIDATION
-- configs / 114 distinct TOPOLOGYSHIFTSETID / 114 distinct BASELINE_CONFIG_ID; 105 of the 116
-- configs have FAST_SCAN_RESULTS rows (103 of 114 baselines have >=1 result-bearing config);
-- 747 STUDY (non-VALIDATION) configs under 14218. SP_CREATE_VALIDATION_CONFIG_TEST must exist
-- first (validation_create_test.sql) -- this role cannot compile it, only sdalvi/AW_ACCESS can.

-- ============================================================================
-- 1. PREVIEW -- one row per BASELINE_CONFIG_ID with existing VALIDATION config(s),
--    shift set(s), and whether results already exist.
--    Row count verified today: 114 rows (matches 114 distinct BASELINE_CONFIG_ID above).
-- ============================================================================
SELECT
    v.BASELINE_CONFIG_ID,
    ARRAY_AGG(DISTINCT v.CONFIG_ID) WITHIN GROUP (ORDER BY v.CONFIG_ID)               AS EXISTING_VALIDATION_CONFIG_IDS,
    ARRAY_AGG(DISTINCT v.TOPOLOGYSHIFTSETID) WITHIN GROUP (ORDER BY v.TOPOLOGYSHIFTSETID) AS SHIFTSET_IDS,
    COUNT(DISTINCT v.CONFIG_ID)                                                        AS N_EXISTING_CONFIGS,
    MAX(CASE WHEN r.CONFIG_ID IS NOT NULL THEN TRUE ELSE FALSE END)                    AS HAS_RESULTS
FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG v
LEFT JOIN (SELECT DISTINCT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS) r
  ON r.CONFIG_ID = v.CONFIG_ID
WHERE v.STUDY_ID = 14218 AND v.SOURCE_TYPE = 'VALIDATION'
GROUP BY v.BASELINE_CONFIG_ID
ORDER BY v.BASELINE_CONFIG_ID;

-- ============================================================================
-- 2. CREATE forced-new validation configs for every distinct baseline above, run V2 on each
--    one immediately, and log the V1<->V2 mapping plus V2 timing durably. AW_ACCESS only
--    (AI_READ_ONLY cannot CREATE TABLE or CALL). Cursor/loop syntax and the CALL+RESULT_SCAN
--    pattern below match the account style already used in validation_create.sql; not
--    independently compiled/run here (this role cannot compile/call the target procs).
--    A failing V2 call is caught in its own sub-block so it does not abort the loop -- its
--    error text lands in V2_RUN_RESULT and the row is still logged.
-- ============================================================================
EXECUTE IMMEDIATE $$
DECLARE
    c_baselines CURSOR FOR
        SELECT DISTINCT BASELINE_CONFIG_ID
          FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
         WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION';
    v_create_result   VARIANT;
    v_run_result      VARIANT;
    v_v1_config_id    INT;
    v_v2_config_id    INT;
    v_tssid           INT;
    v_run_started_at  TIMESTAMP_NTZ;
    v_run_ended_at    TIMESTAMP_NTZ;
    v_count           INT DEFAULT 0;
    v_baseline_config_id NUMBER(38,0);
BEGIN
    CREATE TRANSIENT TABLE AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 (
        BASELINE_CONFIG_ID  NUMBER(38,0),
        V1_CONFIG_ID        NUMBER(38,0),
        TOPOLOGYSHIFTSETID  NUMBER(38,0),
        V2_CONFIG_ID        NUMBER(38,0),
        CREATE_RESULT       VARIANT,
        V2_RUN_STARTED_AT   TIMESTAMP_NTZ(9),
        V2_RUN_ENDED_AT     TIMESTAMP_NTZ(9),
        V2_ELAPSED_S        FLOAT,
        V2_RUN_RESULT       VARIANT,
        CREATED_AT          TIMESTAMP_NTZ(9) DEFAULT CURRENT_TIMESTAMP()
    );

    FOR rec IN c_baselines DO
        v_baseline_config_id := rec.BASELINE_CONFIG_ID;

        -- create (forced): also returns prior_config_ids, the pre-existing V1 config(s) on this shift set
        CALL AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST(:v_baseline_config_id, TRUE);
        v_create_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())));
        v_v2_config_id  := v_create_result:config_id::NUMBER(38,0);
        v_tssid         := v_create_result:topologyshiftsetid::NUMBER(38,0);

        v_v1_config_id := NULL;
        SELECT MIN(value::NUMBER(38,0)) INTO :v_v1_config_id
          FROM TABLE(FLATTEN(input => v_create_result:prior_config_ids));

        -- run V2, timed; own exception so one bad scan does not kill the loop
        v_run_started_at := CURRENT_TIMESTAMP();
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_v2_config_id, NULL, NULL, TRUE, 6);
            v_run_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())));
        EXCEPTION
            WHEN OTHER THEN
                v_run_result := OBJECT_CONSTRUCT('status', 'FAILED', 'error', SQLERRM);
        END;
        v_run_ended_at := CURRENT_TIMESTAMP();

        INSERT INTO AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 (
            BASELINE_CONFIG_ID, V1_CONFIG_ID, TOPOLOGYSHIFTSETID, V2_CONFIG_ID, CREATE_RESULT,
            V2_RUN_STARTED_AT, V2_RUN_ENDED_AT, V2_ELAPSED_S, V2_RUN_RESULT)
        VALUES (
            :v_baseline_config_id, :v_v1_config_id, :v_tssid, :v_v2_config_id, :v_create_result,
            :v_run_started_at, :v_run_ended_at,
            DATEDIFF('millisecond', :v_run_started_at, :v_run_ended_at) / 1000.0, :v_run_result
        );

        v_count := v_count + 1;
    END FOR;

    RETURN v_count;
END;
$$;

-- ============================================================================
-- 3. POST-CHECK -- new config id, its baseline, shift set, and which prior config id(s)
--    it duplicates. Expect COUNT = 114.
-- ============================================================================
SELECT
    l.V2_CONFIG_ID AS NEW_CONFIG_ID,
    l.BASELINE_CONFIG_ID,
    l.TOPOLOGYSHIFTSETID,
    l.CREATE_RESULT:prior_config_ids AS PRIOR_CONFIG_IDS
FROM AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 l
ORDER BY l.BASELINE_CONFIG_ID;

SELECT COUNT(*) AS N_NEW_CONFIGS  -- expect 114
FROM AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925;

-- ============================================================================
-- 4. V1-vs-V2 COMPARISON -- one row per baseline, for the benchmark workflow. Reuses the
--    same alignment already established in validate_validation_fast_scan_v2.py: V1 is on the
--    FLOOR convention (its TIMESTAMP is the floor hour); V2 is nearest-hour (its TIMESTAMP is
--    a :57 snapshot whose HOUR_BUCKET rounds up to the next hour). So:
--      (a) same-bucket: V2.HOUR_BUCKET == V1.TIMESTAMP  -> DAM_RATE_B diff, PSENSHIFTID match
--      (b) flow alignment: floor(V2.TIMESTAMP) == V1.TIMESTAMP -> INJECTION_FLOW diff
--    MEMBER_COUNT reuses the same COUNT(DISTINCT TOPOLOGYID) metric SP_CREATE_VALIDATION_CONFIG(_TEST)
--    already reports as 'members', for consistency.
--    V1_ELAPSED_S needs SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY, which this role (AI_READ_ONLY) does
--    NOT have -- confirmed today: "Schema 'SNOWFLAKE.ACCOUNT_USAGE' does not exist or not
--    authorized". Left NULL below; if AW_ACCESS has the grant, replace that column with:
--      LEFT JOIN (
--          SELECT REGEXP_SUBSTR(QUERY_TEXT, 'SP_RUN_VALIDATION_FAST_SCAN\\(\\s*(\\d+)', 1, 1, 'e')::NUMBER AS CFG_ID,
--                 TOTAL_ELAPSED_TIME / 1000.0 AS V1_ELAPSED_S
--          FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
--          WHERE QUERY_TEXT ILIKE '%SP_RUN_VALIDATION_FAST_SCAN(%'
--          QUALIFY ROW_NUMBER() OVER (PARTITION BY CFG_ID ORDER BY START_TIME DESC) = 1
--      ) qh ON qh.CFG_ID = l.V1_CONFIG_ID
--    and select qh.V1_ELAPSED_S instead of the NULL literal.
--    Verified (EXPLAIN, this role) against a stubbed log table -- plan compiles; see report.
-- ============================================================================
WITH v1_results AS (
    SELECT CONFIG_ID, COUNT(*) AS V1_ROWS
    FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS
    GROUP BY CONFIG_ID
),
v1_run AS (
    SELECT CONFIG_ID, MAX(RUN_AT) AS V1_LAST_SUCCESS_RUN_AT
    FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG
    WHERE STATUS = 'SUCCESS'
    GROUP BY CONFIG_ID
),
v2_results AS (
    SELECT CONFIG_ID, COUNT(*) AS V2_ROWS,
           COUNT(CASE WHEN RT_CONSTRAINT_VALUE IS NOT NULL THEN 1 END) AS V2_HOURS_WITH_OWN_CONTINGENCY_RT
    FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS
    GROUP BY CONFIG_ID
),
member_hours AS (
    SELECT TOPOLOGYSHIFTSETID, COUNT(DISTINCT TOPOLOGYID) AS MEMBER_COUNT
    FROM AW.POPT.TOPOLOGYSHIFTSET
    GROUP BY TOPOLOGYSHIFTSETID
),
same_bucket AS (
    SELECT
        l.BASELINE_CONFIG_ID,
        MAX(ABS(v1.DAM_RATE_B - v2.DAM_RATE_B)) AS DAM_RATE_B_MAX_ABS_DIFF,
        AVG(CASE WHEN v1.PSENSHIFTID = v2.PSENSHIFTID THEN 1.0 ELSE 0.0 END) AS PSENSHIFTID_MATCH_RATE
    FROM AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 l
    JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS v1 ON v1.CONFIG_ID = l.V1_CONFIG_ID
    JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS v2
      ON v2.CONFIG_ID = l.V2_CONFIG_ID
     AND DATE_TRUNC('HOUR', DATEADD('MINUTE', 30, v2.TIMESTAMP)) = v1.TIMESTAMP
    GROUP BY l.BASELINE_CONFIG_ID
),
flow_align AS (
    SELECT
        l.BASELINE_CONFIG_ID,
        AVG(ABS(v1.INJECTION_FLOW - v2.INJECTION_FLOW)) AS INJECTION_FLOW_MEAN_ABS_DIFF
    FROM AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 l
    JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS v1 ON v1.CONFIG_ID = l.V1_CONFIG_ID
    JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS v2
      ON v2.CONFIG_ID = l.V2_CONFIG_ID
     AND DATE_TRUNC('HOUR', v2.TIMESTAMP) = v1.TIMESTAMP
    GROUP BY l.BASELINE_CONFIG_ID
)
SELECT
    l.BASELINE_CONFIG_ID,
    l.V1_CONFIG_ID,
    v1r.V1_ROWS,
    v1run.V1_LAST_SUCCESS_RUN_AT,
    NULL::FLOAT AS V1_ELAPSED_S,              -- see ACCOUNT_USAGE note above
    l.V2_CONFIG_ID,
    v2r.V2_ROWS,
    v2r.V2_HOURS_WITH_OWN_CONTINGENCY_RT,
    l.V2_RUN_STARTED_AT,
    l.V2_ELAPSED_S,
    mh.MEMBER_COUNT,
    sb.DAM_RATE_B_MAX_ABS_DIFF,
    sb.PSENSHIFTID_MATCH_RATE,
    fa.INJECTION_FLOW_MEAN_ABS_DIFF
FROM AW.FLOW_ANALYSIS.VALIDATION_CONFIG_CREATE_LOG_20260925 l
LEFT JOIN v1_results v1r   ON v1r.CONFIG_ID = l.V1_CONFIG_ID
LEFT JOIN v1_run     v1run ON v1run.CONFIG_ID = l.V1_CONFIG_ID
LEFT JOIN v2_results v2r   ON v2r.CONFIG_ID = l.V2_CONFIG_ID
LEFT JOIN member_hours mh  ON mh.TOPOLOGYSHIFTSETID = l.TOPOLOGYSHIFTSETID
LEFT JOIN same_bucket sb   ON sb.BASELINE_CONFIG_ID = l.BASELINE_CONFIG_ID
LEFT JOIN flow_align  fa   ON fa.BASELINE_CONFIG_ID = l.BASELINE_CONFIG_ID
ORDER BY l.BASELINE_CONFIG_ID;
