-- Parallel driver for validation_create_all_14218.sql: open 4 worksheets on the same warehouse and run block k in worksheet k (k = 0,1,2,3), each covering one MOD(BASELINE_CONFIG_ID,4) slice.
-- Cancel any single-session run of validation_create_all_14218.sql first -- its cursor was materialised at start and would re-create baselines these 4 blocks already handle.
-- 2026-09-25
-- Worksheet 0
EXECUTE IMMEDIATE $$
DECLARE
    c_baselines CURSOR FOR
        SELECT DISTINCT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND MOD(BASELINE_CONFIG_ID, 4) = 0
           AND BASELINE_CONFIG_ID NOT IN (SELECT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25 12:55') ORDER BY 1;
    v_baseline NUMBER(38,0); v_result VARIANT; v_config_id NUMBER(38,0); v_created INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_baselines DO
        v_baseline := rec.BASELINE_CONFIG_ID;
        CALL AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST(:v_baseline, TRUE);
        v_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))); v_config_id := v_result:config_id::NUMBER(38,0); v_created := v_created + 1;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'created ' || v_created || ', runs failed ' || v_failed;
END;
$$;
-- Worksheet 1
EXECUTE IMMEDIATE $$
DECLARE
    c_baselines CURSOR FOR
        SELECT DISTINCT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND MOD(BASELINE_CONFIG_ID, 4) = 1
           AND BASELINE_CONFIG_ID NOT IN (SELECT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25 12:55') ORDER BY 1;
    v_baseline NUMBER(38,0); v_result VARIANT; v_config_id NUMBER(38,0); v_created INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_baselines DO
        v_baseline := rec.BASELINE_CONFIG_ID;
        CALL AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST(:v_baseline, TRUE);
        v_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))); v_config_id := v_result:config_id::NUMBER(38,0); v_created := v_created + 1;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'created ' || v_created || ', runs failed ' || v_failed;
END;
$$;
-- Worksheet 2
EXECUTE IMMEDIATE $$
DECLARE
    c_baselines CURSOR FOR
        SELECT DISTINCT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND MOD(BASELINE_CONFIG_ID, 4) = 2
           AND BASELINE_CONFIG_ID NOT IN (SELECT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25 12:55') ORDER BY 1;
    v_baseline NUMBER(38,0); v_result VARIANT; v_config_id NUMBER(38,0); v_created INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_baselines DO
        v_baseline := rec.BASELINE_CONFIG_ID;
        CALL AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST(:v_baseline, TRUE);
        v_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))); v_config_id := v_result:config_id::NUMBER(38,0); v_created := v_created + 1;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'created ' || v_created || ', runs failed ' || v_failed;
END;
$$;
-- Worksheet 3
EXECUTE IMMEDIATE $$
DECLARE
    c_baselines CURSOR FOR
        SELECT DISTINCT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND MOD(BASELINE_CONFIG_ID, 4) = 3
           AND BASELINE_CONFIG_ID NOT IN (SELECT BASELINE_CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25 12:55') ORDER BY 1;
    v_baseline NUMBER(38,0); v_result VARIANT; v_config_id NUMBER(38,0); v_created INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_baselines DO
        v_baseline := rec.BASELINE_CONFIG_ID;
        CALL AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST(:v_baseline, TRUE);
        v_result := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))); v_config_id := v_result:config_id::NUMBER(38,0); v_created := v_created + 1;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'created ' || v_created || ', runs failed ' || v_failed;
END;
$$;
-- Post-check: new configs created today, with row counts. Failed V2 runs are visible in
-- FLOW_ANALYSIS.FAST_SCAN_RUN_LOG by STATUS.
SELECT c.CONFIG_ID, c.BASELINE_CONFIG_ID, c.TOPOLOGYSHIFTSETID, COUNT(r.CONFIG_ID) AS RESULT_ROWS
FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG c
LEFT JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS r ON r.CONFIG_ID = c.CONFIG_ID
WHERE c.STUDY_ID = 14218 AND c.SOURCE_TYPE = 'VALIDATION' AND c.CREATED_AT >= CURRENT_DATE()
GROUP BY c.CONFIG_ID, c.BASELINE_CONFIG_ID, c.TOPOLOGYSHIFTSETID
ORDER BY c.BASELINE_CONFIG_ID;
