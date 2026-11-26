-- Test variant of AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG for repeated/forced creation.
-- Adds P_FORCE_NEW: when TRUE, skips the EXISTING short-circuit and always inserts a new
-- VALIDATION row (status CREATED_FORCED), returning prior_config_ids (configs already on
-- that shift set before this insert). P_FORCE_NEW FALSE behaves exactly like the source proc.
-- 2026-09-25
CREATE OR REPLACE PROCEDURE AW.FLOW_ANALYSIS.SP_CREATE_VALIDATION_CONFIG_TEST("P_SOURCE_CONFIG_ID" NUMBER(38,0), "P_FORCE_NEW" BOOLEAN DEFAULT FALSE)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_study_id      INT;
    v_source_type   VARCHAR;
    v_from_num      INT;
    v_to_num        INT;
    v_ckt           VARCHAR;
    v_ctg_label     VARCHAR;
    v_direction     INT;
    v_branch_label  VARCHAR;
    v_tssid         INT;
    v_config_id     INT;
    v_members       INT;
    v_expected      INT;
    v_status        VARCHAR := ''CREATED'';
    v_prior_ids     ARRAY := ARRAY_CONSTRUCT();
BEGIN
    SELECT STUDY_ID, SOURCE_TYPE, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECTION, BRANCH_LABEL
      INTO :v_study_id, :v_source_type, :v_from_num, :v_to_num, :v_ckt, :v_ctg_label,
           :v_direction, :v_branch_label
      FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
     WHERE CONFIG_ID = :P_SOURCE_CONFIG_ID;

    IF (v_study_id IS NULL) THEN
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'',
                                ''error'', ''source config not found or has no STUDY_ID'');
    END IF;
    IF (v_source_type = ''VALIDATION'') THEN
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'',
                                ''error'', ''source config is itself a VALIDATION config'');
    END IF;

    -- build / reuse the shift set on the bus key
    CALL AW.POPT.SP_CREATETOPOLOGYSHIFTSET_BYBRANCH(
        :v_study_id, :v_from_num, :v_to_num, :v_ckt, :v_ctg_label, :v_direction, :v_branch_label);
    v_tssid := (SELECT $1 FROM TABLE(RESULT_SCAN(LAST_QUERY_ID())));

    -- idempotent unless forced: one validation config per shift set
    IF (:P_FORCE_NEW) THEN
        SELECT ARRAY_AGG(CONFIG_ID) WITHIN GROUP (ORDER BY CONFIG_ID) INTO :v_prior_ids
          FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
         WHERE SOURCE_TYPE = ''VALIDATION'' AND TOPOLOGYSHIFTSETID = :v_tssid;
        IF (v_prior_ids IS NULL) THEN
            v_prior_ids := ARRAY_CONSTRUCT();
        END IF;
        v_config_id := NULL;
    ELSE
        SELECT MIN(CONFIG_ID) INTO :v_config_id
          FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
         WHERE SOURCE_TYPE = ''VALIDATION'' AND TOPOLOGYSHIFTSETID = :v_tssid;
    END IF;

    IF (v_config_id IS NOT NULL) THEN
        v_status := ''EXISTING'';
    ELSE
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_CONFIG (
            PSENSHIFTID, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECTION, PTOID,
            BRANCH_LABEL, SOURCE_TYPE, STUDY_ID, TOPOLOGY_ID,
            DEFAULT_RATE_B, DEFAULT_RATE_B_RT, IS_ACTIVE,
            BRANCHID, FROM_STATION, TO_STATION, DEVICE_TYPE, BRANCH_NAME, ISO_DIRECTION,
            TOPOLOGYSHIFTSETID, BASELINE_CONFIG_ID)
        SELECT
            NULL, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECTION, PTOID,
            BRANCH_LABEL, ''VALIDATION'', STUDY_ID, NULL,
            DEFAULT_RATE_B, DEFAULT_RATE_B_RT, TRUE,
            BRANCHID, FROM_STATION, TO_STATION, DEVICE_TYPE, BRANCH_NAME, ISO_DIRECTION,
            :v_tssid, CONFIG_ID
        FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE CONFIG_ID = :P_SOURCE_CONFIG_ID;

        SELECT MAX(CONFIG_ID) INTO :v_config_id
          FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
         WHERE SOURCE_TYPE = ''VALIDATION'' AND TOPOLOGYSHIFTSETID = :v_tssid;

        IF (:P_FORCE_NEW) THEN
            v_status := ''CREATED_FORCED'';
        END IF;
    END IF;

    SELECT COUNT(DISTINCT TOPOLOGYID) INTO :v_members
      FROM AW.POPT.TOPOLOGYSHIFTSET WHERE TOPOLOGYSHIFTSETID = :v_tssid;
    SELECT COUNT(DISTINCT TOPOLOGYID) INTO :v_expected
      FROM AWOPF.DBO.OPFRUN WHERE STUDYID = :v_study_id AND TOPOLOGYID IS NOT NULL;

    IF (:P_FORCE_NEW) THEN
        RETURN OBJECT_CONSTRUCT(
            ''status'',             :v_status,
            ''config_id'',          :v_config_id,
            ''baseline_config_id'', :P_SOURCE_CONFIG_ID,
            ''topologyshiftsetid'', :v_tssid,
            ''study_id'',           :v_study_id,
            ''branch_label'',       :v_branch_label,
            ''members'',            :v_members,
            ''expected_members'',   :v_expected,
            ''missing_members'',    :v_expected - :v_members,
            ''prior_config_ids'',   :v_prior_ids
        );
    ELSE
        RETURN OBJECT_CONSTRUCT(
            ''status'',             :v_status,
            ''config_id'',          :v_config_id,
            ''baseline_config_id'', :P_SOURCE_CONFIG_ID,
            ''topologyshiftsetid'', :v_tssid,
            ''study_id'',           :v_study_id,
            ''branch_label'',       :v_branch_label,
            ''members'',            :v_members,
            ''expected_members'',   :v_expected,
            ''missing_members'',    :v_expected - :v_members
        );
    END IF;
EXCEPTION
    WHEN OTHER THEN
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'', ''error'', :SQLERRM);
END;
';
