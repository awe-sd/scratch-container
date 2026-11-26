-- Rerun driver for today's study-14218 validation configs after the B1/B2 staged rewrite.
-- Edit the '2026-09-25 16:00' cutoff literal in all five places (4 worksheet blocks + post-check) before running.
-- 2026-09-25

-- Preview: configs and rows about to be cleared.
WITH Configs AS (
    SELECT CONFIG_ID, CREATED_AT FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
    WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
)
SELECT
    (SELECT COUNT(*) FROM Configs) AS CONFIGS,
    (SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS r WHERE r.CONFIG_ID IN (SELECT CONFIG_ID FROM Configs)) AS RESULT_ROWS,
    (SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS t WHERE t.CONFIG_ID IN (SELECT CONFIG_ID FROM Configs)) AS CONSTRAINT_ROWS;

SELECT c.CONFIG_ID, c.CREATED_AT,
       (SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS r WHERE r.CONFIG_ID = c.CONFIG_ID) AS RESULT_ROWS,
       (SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS t WHERE t.CONFIG_ID = c.CONFIG_ID) AS CONSTRAINT_ROWS
FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG c
WHERE c.STUDY_ID = 14218 AND c.SOURCE_TYPE = 'VALIDATION' AND c.CREATED_AT >= '2026-09-25'
ORDER BY c.CREATED_AT;

-- 115 configs match (today's 107 batch clones plus 256601 and 256701-256707) -- intended: every
-- V2 validation result computed before this rewrite carries the injection PAR defect.
DELETE FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS
WHERE CONFIG_ID IN (
    SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
    WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
);

DELETE FROM FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS
WHERE CONFIG_ID IN (
    SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
    WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
);

-- Worksheet 0
-- A legitimate zero-row config (member hours all past the injection table's data) logs SUCCESS with 0 rows, so it is correctly not retried.
EXECUTE IMMEDIATE $$
DECLARE
    c_configs CURSOR FOR
        SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
          AND MOD(CONFIG_ID, 4) = 0
          AND NOT EXISTS (
              SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG l
              WHERE l.CONFIG_ID = FAST_SCAN_CONFIG.CONFIG_ID AND l.STATUS = 'SUCCESS' AND l.RUN_AT >= '2026-09-25 16:00'
          )
        ORDER BY 1;
    v_config_id NUMBER(38,0); v_run INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_configs DO
        v_config_id := rec.CONFIG_ID;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
            v_run := v_run + 1;
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'ran ' || v_run || ', failed ' || v_failed;
END;
$$;
-- Worksheet 1
EXECUTE IMMEDIATE $$
DECLARE
    c_configs CURSOR FOR
        SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
          AND MOD(CONFIG_ID, 4) = 1
          AND NOT EXISTS (
              SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG l
              WHERE l.CONFIG_ID = FAST_SCAN_CONFIG.CONFIG_ID AND l.STATUS = 'SUCCESS' AND l.RUN_AT >= '2026-09-25 16:00'
          )
        ORDER BY 1;
    v_config_id NUMBER(38,0); v_run INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_configs DO
        v_config_id := rec.CONFIG_ID;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
            v_run := v_run + 1;
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'ran ' || v_run || ', failed ' || v_failed;
END;
$$;
-- Worksheet 2
EXECUTE IMMEDIATE $$
DECLARE
    c_configs CURSOR FOR
        SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
          AND MOD(CONFIG_ID, 4) = 2
          AND NOT EXISTS (
              SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG l
              WHERE l.CONFIG_ID = FAST_SCAN_CONFIG.CONFIG_ID AND l.STATUS = 'SUCCESS' AND l.RUN_AT >= '2026-09-25 16:00'
          )
        ORDER BY 1;
    v_config_id NUMBER(38,0); v_run INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_configs DO
        v_config_id := rec.CONFIG_ID;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
            v_run := v_run + 1;
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'ran ' || v_run || ', failed ' || v_failed;
END;
$$;
-- Worksheet 3
EXECUTE IMMEDIATE $$
DECLARE
    c_configs CURSOR FOR
        SELECT CONFIG_ID FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE STUDY_ID = 14218 AND SOURCE_TYPE = 'VALIDATION' AND CREATED_AT >= '2026-09-25'
          AND MOD(CONFIG_ID, 4) = 3
          AND NOT EXISTS (
              SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG l
              WHERE l.CONFIG_ID = FAST_SCAN_CONFIG.CONFIG_ID AND l.STATUS = 'SUCCESS' AND l.RUN_AT >= '2026-09-25 16:00'
          )
        ORDER BY 1;
    v_config_id NUMBER(38,0); v_run INT DEFAULT 0; v_failed INT DEFAULT 0;
BEGIN
    FOR rec IN c_configs DO
        v_config_id := rec.CONFIG_ID;
        BEGIN
            CALL AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2(:v_config_id, NULL, NULL, TRUE, 6);
            v_run := v_run + 1;
        EXCEPTION WHEN OTHER THEN v_failed := v_failed + 1; END;
    END FOR;
    RETURN 'ran ' || v_run || ', failed ' || v_failed;
END;
$$;
-- Post-check: today's configs, with row counts; failed runs show in FAST_SCAN_RUN_LOG by STATUS.
SELECT c.CONFIG_ID, c.BASELINE_CONFIG_ID, c.TOPOLOGYSHIFTSETID, COUNT(r.CONFIG_ID) AS RESULT_ROWS,
       MAX((SELECT COUNT(*) FROM FLOW_ANALYSIS.FAST_SCAN_RUN_LOG l
             WHERE l.CONFIG_ID = c.CONFIG_ID AND l.STATUS = 'SUCCESS' AND l.RUN_AT >= '2026-09-25 16:00')) AS RERUN_SUCCESS_LOG_ROWS
FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG c
LEFT JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS r ON r.CONFIG_ID = c.CONFIG_ID
WHERE c.STUDY_ID = 14218 AND c.SOURCE_TYPE = 'VALIDATION' AND c.CREATED_AT >= '2026-09-25'
GROUP BY c.CONFIG_ID, c.BASELINE_CONFIG_ID, c.TOPOLOGYSHIFTSETID
ORDER BY c.BASELINE_CONFIG_ID;
