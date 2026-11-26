-- Reference copy of the DEPLOYED V1 validation proc, pasted by sdalvi on 2026-09-25 (GET_DDL returns an
-- empty body under AI_READ_ONLY). Not to be redeployed; validation_spV2.sql is the V2 rewrite.
-- Source: AW.DBO.ERCOTSTATIONLOAD at station grain, floor-hour convention (HOUR = hour of the :57 snapshot).

CREATE OR REPLACE PROCEDURE AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN("P_CONFIG_ID" NUMBER(38,0), "P_START_DATE" DATE DEFAULT null, "P_END_DATE" DATE DEFAULT null, "P_INCLUDE_CURTAILMENT" BOOLEAN DEFAULT TRUE, "P_ISO_MARKET_ID" NUMBER(38,0) DEFAULT 6)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_source_type       VARCHAR;
    v_tssid             INT;
    v_study_id          INT;
    v_from_num          INT;
    v_to_num            INT;
    v_ckt               VARCHAR(10);
    v_direction         INT;
    v_ptoid             INT;
    v_branch_label      VARCHAR(200);
    v_branch_name       VARCHAR(400);
    v_default_rate_b    FLOAT;
    v_default_rate_b_rt FLOAT;
    v_cim_file_id       INT := 205;           -- same station map as SP_RUN_FAST_SCAN
    v_actual_start      DATE;
    v_actual_end        DATE;
    v_members_total     INT;
    v_members_in_range  INT;
    v_dupes_dropped     INT;
    v_already_present   INT;
    v_rows_inserted     INT;
    v_hours_missing     INT;
    v_start_time        TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    v_elapsed_ms        INT;
BEGIN
    -- 1. config
    SELECT SOURCE_TYPE, TOPOLOGYSHIFTSETID, STUDY_ID, FROM_NUM, TO_NUM, CKT, DIRECTION, PTOID,
           BRANCH_LABEL, BRANCH_NAME, DEFAULT_RATE_B, DEFAULT_RATE_B_RT
      INTO :v_source_type, :v_tssid, :v_study_id, :v_from_num, :v_to_num, :v_ckt, :v_direction,
           :v_ptoid, :v_branch_label, :v_branch_name, :v_default_rate_b, :v_default_rate_b_rt
      FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
     WHERE CONFIG_ID = :P_CONFIG_ID;

    IF (v_source_type IS DISTINCT FROM ''VALIDATION'' OR v_tssid IS NULL) THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
        VALUES (:P_CONFIG_ID, :P_START_DATE, :P_END_DATE, 0, ''NOT_A_VALIDATION_CONFIG'');
        RETURN OBJECT_CONSTRUCT(''status'', ''NOT_A_VALIDATION_CONFIG'', ''config_id'', :P_CONFIG_ID,
                                ''rows_inserted'', 0);
    END IF;

    -- 2. member hours: one (psenShiftId, timestamp) per set member. SIMHOUR is hour-ending.
    --    A daily study gets re-run (day-ahead, present, after the fact), so the same hour can
    --    carry one shift per run. RUNID comes from the shift''s own def row (psenShiftDef.runId)
    --    and decides which one survives: the newest RUN wins, psenShiftId only breaks ties.
    CREATE OR REPLACE TEMPORARY TABLE TMP_VAL_MEMBER_HOURS (
        PSENSHIFTID NUMBER(38,0),
        TOPOLOGYID  NUMBER(38,0),
        RUNID       NUMBER(38,0),
        TS          TIMESTAMP_NTZ,
        RN          NUMBER(38,0)
    );
    INSERT INTO TMP_VAL_MEMBER_HOURS
    SELECT PSENSHIFTID, TOPOLOGYID, RUNID, TS,
           ROW_NUMBER() OVER (PARTITION BY TS ORDER BY RUNID DESC NULLS LAST, PSENSHIFTID DESC) AS RN
    FROM (
        SELECT DISTINCT
               tss.PSENSHIFTID, tss.TOPOLOGYID, psd.RUNID,
               DATEADD(hour, r.SIMHOUR - 1, r.SIMDATE::DATE) AS TS
        FROM AW.POPT.TOPOLOGYSHIFTSET tss
        LEFT JOIN AW.DBO.PSENSHIFTDEF psd ON psd.PSENSHIFTID = tss.PSENSHIFTID
        JOIN (
            SELECT DISTINCT STUDYID, TOPOLOGYID, SIMDATE, SIMHOUR
            FROM AWOPF.DBO.OPFRUN
            WHERE STUDYID = :v_study_id AND SIMDATE IS NOT NULL AND SIMHOUR IS NOT NULL
        ) r ON r.TOPOLOGYID = tss.TOPOLOGYID
        WHERE tss.TOPOLOGYSHIFTSETID = :v_tssid
    );

    SELECT COUNT(*) INTO :v_members_total FROM TMP_VAL_MEMBER_HOURS;
    IF (v_members_total = 0) THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
        VALUES (:P_CONFIG_ID, :P_START_DATE, :P_END_DATE, 0, ''NO_MEMBERS'');
        RETURN OBJECT_CONSTRUCT(''status'', ''NO_MEMBERS'', ''config_id'', :P_CONFIG_ID,
                                ''topologyshiftsetid'', :v_tssid, ''rows_inserted'', 0);
    END IF;

    -- more than one psenShiftId resolved to the same hour: keep the highest runId, count the rest
    SELECT COUNT(*) INTO :v_dupes_dropped FROM TMP_VAL_MEMBER_HOURS WHERE RN > 1;
    DELETE FROM TMP_VAL_MEMBER_HOURS WHERE RN > 1;

    -- 3. date range: NULL = the members'' own span
    IF (P_START_DATE IS NULL) THEN
        SELECT MIN(TS)::DATE INTO :v_actual_start FROM TMP_VAL_MEMBER_HOURS;
    ELSE
        v_actual_start := :P_START_DATE;
    END IF;
    IF (P_END_DATE IS NULL) THEN
        SELECT MAX(TS)::DATE INTO :v_actual_end FROM TMP_VAL_MEMBER_HOURS;
    ELSE
        v_actual_end := :P_END_DATE;
    END IF;
    DELETE FROM TMP_VAL_MEMBER_HOURS
     WHERE TS::DATE < :v_actual_start
        OR TS::DATE > :v_actual_end;

    SELECT COUNT(*) INTO :v_members_in_range FROM TMP_VAL_MEMBER_HOURS;
    SELECT COUNT(*) INTO :v_already_present
      FROM TMP_VAL_MEMBER_HOURS mh
      JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS x ON x.CONFIG_ID = :P_CONFIG_ID AND x.TIMESTAMP = mh.TS;

    -- 4. THE MAIN CALCULATION - same CTEs as SP_RUN_FAST_SCAN, keyed by PSENSHIFTID where
    --    the shift matters and joined to the member''s own hour.
    INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RESULTS (
        CONFIG_ID, TIMESTAMP, INJECTION_FLOW,
        DAM_RATE_B, HEADROOM,
        REALTIME_RATE_B, HEADROOM_RT,
        RT_CONSTRAINT_VALUE, RT_CONSTRAINT_LIMIT, RT_ACTUAL_HEADROOM,
        WIND_IMPACT, SOLAR_IMPACT, HEADROOM_AFTER_CURTAILMENT,
        HEADROOM_DAM_WIND_CURTAILMENT, HEADROOM_DAM_SOLAR_CURTAILMENT,
        PSENSHIFTID
    )
    WITH
    Members AS (
        SELECT PSENSHIFTID, TS FROM TMP_VAL_MEMBER_HOURS
    ),
    MemberShifts AS (
        SELECT DISTINCT PSENSHIFTID FROM TMP_VAL_MEMBER_HOURS
    ),
    StationBusMapping AS (
        SELECT StationCode, BusNum FROM (
            SELECT
                d.NmmsStationCode AS StationCode,
                d.SswgBusNumber AS BusNum,
                ROW_NUMBER() OVER (PARTITION BY d.NmmsStationCode, d.SswgBusNumber
                                   ORDER BY d.fileDateMonth DESC) AS rn
            FROM AW.DBO.ERCOTDATADICTIONARY d
            WHERE d.NmmsStationCode IS NOT NULL AND d.SswgBusNumber IS NOT NULL
        ) WHERE rn = 1
        UNION
        SELECT sv.name_substation AS StationCode, cn.psseBusNumber AS BusNum
        FROM AW.DBO.CIMSTATIONVOLTAGELEVEL sv
        JOIN AW.DBO.CIMCONNODE cn
            ON sv.cimFileId = cn.cimFileId
            AND sv.cimStationVoltageLevelId = cn.cimStationVoltageLevelId
        WHERE sv.cimFileId = :v_cim_file_id
          AND sv.name_substation IS NOT NULL
          AND cn.psseBusNumber IS NOT NULL
    ),

    -- station shift per member shift (same bus->station aggregation as the production proc,
    -- kept identical so validation and baseline series are comparable)
    StationShifts AS (
        SELECT
            bs.PSENSHIFTID,
            m.StationCode,
            -AVG(bs.PSENS) AS StationPSENS
        FROM SHIFT_FACTORS.DBO.BUS_SHIFTS bs
        JOIN MemberShifts ms ON ms.PSENSHIFTID = bs.PSENSHIFTID
        JOIN StationBusMapping m ON bs.BUSNUM = m.BusNum
        WHERE bs.ISOMARKETID = :P_ISO_MARKET_ID
        GROUP BY bs.PSENSHIFTID, m.StationCode
        HAVING ABS(AVG(bs.PSENS)) > 0.00001
    ),

    -- load at the member''s own hour only (ERCOTSTATIONLOAD.HOUR is 0..23, hour-beginning)
    InjectionFlow AS (
        SELECT
            mb.TS AS TIMESTAMP,
            mb.PSENSHIFTID,
            SUM(ss.StationPSENS * sl.WITHDRAWMW) AS FLOW
        FROM Members mb
        JOIN AW.DBO.ERCOTSTATIONLOAD sl
            ON sl.DATE = mb.TS::DATE AND sl.HOUR = HOUR(mb.TS)
        JOIN StationShifts ss
            ON ss.PSENSHIFTID = mb.PSENSHIFTID AND ss.StationCode = sl.NMMSSTATIONCODE
        WHERE sl.DATE >= :v_actual_start AND sl.DATE <= :v_actual_end   -- partition pruning
        GROUP BY mb.TS, mb.PSENSHIFTID
    ),

    ParSens AS (
        SELECT
            ps.PSENSHIFTID,
            ps.BUSNUMFROM, ps.BUSNUMTO, ps.CKT, ps.SENSDVALUEDPHASE,
            pes.PARSTATIONID, pes.DIRECTION
        FROM SHIFT_FACTORS.DBO.PAR_SHIFTS ps
        JOIN MemberShifts ms ON ms.PSENSHIFTID = ps.PSENSHIFTID
        INNER JOIN AW.DBO.PARERCOTSTATION pes
            ON ((pes.FROM_BUS_NUM = ps.BUSNUMFROM AND pes.TO_BUS_NUM = ps.BUSNUMTO
                 AND TRIM(CAST(pes.CKT AS VARCHAR)) = TRIM(CAST(ps.CKT AS VARCHAR)))
             OR (pes.FROM_BUS_NUM = ps.BUSNUMTO AND pes.TO_BUS_NUM = ps.BUSNUMFROM
                 AND TRIM(CAST(pes.CKT AS VARCHAR)) = TRIM(CAST(ps.CKT AS VARCHAR))))
        WHERE ps.ISOMARKETID = :P_ISO_MARKET_ID
    ),

    ParInjectionFlow AS (
        SELECT
            mb.TS AS TIMESTAMP,
            SUM(((-30.0 + (pe.FROMTAP - 1.0) * 1.875) * prs.DIRECTION) * prs.SENSDVALUEDPHASE) AS PAR_FLOW
        FROM Members mb
        JOIN AW.DBO.PARERCOTVIEW pe
            ON DATEADD(''HOUR'', pe.HE - 1, pe.DATE) = mb.TS
        JOIN ParSens prs
            ON prs.PSENSHIFTID = mb.PSENSHIFTID AND prs.PARSTATIONID = pe.PARSTATIONID
        WHERE pe.DATE >= :v_actual_start AND pe.DATE <= :v_actual_end
        GROUP BY mb.TS
    ),

    DAMLimits AS (
        SELECT
            DATEADD(''HOUR'', HE - 1, DATE) AS TIMESTAMP,
            MAX(RATEB) AS DAM_RATE_B
        FROM AW.DBO.ercotDampsseLnView
        WHERE DATE >= :v_actual_start AND DATE <= :v_actual_end
          AND branchname = :v_branch_name
        GROUP BY DATE, HE
    ),

    RTDynamicRating AS (
        SELECT
            DATE_TRUNC(''HOUR'', erdrv.createTime) AS TIMESTAMP,
            AVG(erdrv.EMERGENCYRATINGS) AS REALTIME_RATE_B
        FROM AW.DBO.ERCOTRTDYNAMICRATINGVIEW erdrv
        WHERE erdrv.branchname = :v_branch_name
          AND erdrv.createTime >= :v_actual_start
          AND erdrv.createTime < DATEADD(''DAY'', 1, :v_actual_end)
        GROUP BY DATE_TRUNC(''HOUR'', erdrv.createTime)
    ),

    -- ERCOT reports CONSTRAINTVALUE with a sign that follows the monitored direction, so the
    -- same physical loading shows up positive in one interval and negative in the next.
    -- Headroom is limit minus |flow| regardless, hence ABS rather than a direction flip.
    RTConstraint AS (
        SELECT
            DATE_TRUNC(''HOUR'', cfp.DATETIME) AS TIMESTAMP,
            AVG(ABS(cfp.CONSTRAINTVALUE)) AS RT_VALUE,
            AVG(cfp.CONSTRAINTLIMIT) AS RT_LIMIT
        FROM AW.DBO.CONGFQPRICEVIEW cfp
        JOIN AW.DBO.CONGDEFCONSTRAINTVIEW cdc ON cfp.CONGCONSTRAINTID = cdc.CONGCONSTRAINTID
        WHERE cfp.ISOMARKETID = :P_ISO_MARKET_ID AND cfp.PRICETYPEID = 2
          AND cfp.DATE >= :v_actual_start AND cfp.DATE <= :v_actual_end
          AND cdc.BRANCHID IN (
              SELECT DISTINCT BRANCHID FROM AW.DBO.PTOBRANCH
              WHERE ((FROMNUM = :v_from_num AND TONUM = :v_to_num
                      AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR)))
                  OR (FROMNUM = :v_to_num AND TONUM = :v_from_num
                      AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR))))
                AND PTOID = :v_ptoid
          )
        GROUP BY DATE_TRUNC(''HOUR'', cfp.DATETIME)
    ),

    CurtailSens AS (
        SELECT cs.PSENSHIFTID, cs.CPNODEID, cs.PSENS
        FROM SHIFT_FACTORS.DBO.CPNODE_SHIFTS cs
        JOIN MemberShifts ms ON ms.PSENSHIFTID = cs.PSENSHIFTID
        WHERE cs.ISOMARKETID = :P_ISO_MARKET_ID
    ),

    RenewableUnits AS (
        SELECT UNIT_CODE,
               CASE WHEN FUEL ILIKE ''%WIND%'' THEN ''WIND'' ELSE ''SOLAR'' END AS FUEL_TYPE
        FROM AW.DBO.ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW
        WHERE UNIT_CODE != ''NA''
          AND (FUEL ILIKE ''%WIND%'' OR FUEL ILIKE ''%SOLAR%'')
        QUALIFY ROW_NUMBER() OVER (PARTITION BY UNIT_CODE ORDER BY report_date DESC) = 1
    ),

    -- 5-minute SCED curtailment weighted by the member hour''s OWN sensitivities
    CurtailmentPerTs AS (
        SELECT
            gr.TimeStamp,
            ru.FUEL_TYPE,
            SUM(GREATEST(gr.HSL - gr.BasePoint, 0) * s.PSENS) AS Impact
        FROM Members mb
        JOIN AW.DBO.ISOERCOTSCEDGENRESOURCE gr
            ON DATE_TRUNC(''HOUR'', gr.TimeStamp) = mb.TS      -- equi-join, not a band join
        JOIN AW.DBO.ISOERCOTSCEDGEN g ON g.genId = gr.genID
        JOIN RenewableUnits ru ON g.ResourceName = ru.UNIT_CODE
        JOIN CurtailSens s ON s.PSENSHIFTID = mb.PSENSHIFTID AND g.cpnodeid = s.CPNODEID
        WHERE :P_INCLUDE_CURTAILMENT = TRUE
          AND gr.TimeStamp >= :v_actual_start
          AND gr.TimeStamp < DATEADD(''DAY'', 1, :v_actual_end)
        GROUP BY gr.TimeStamp, ru.FUEL_TYPE
    ),

    CurtailImpactHourly AS (
        SELECT DATE_TRUNC(''HOUR'', TimeStamp) AS TIMESTAMP, FUEL_TYPE, AVG(Impact) AS IMPACT
        FROM CurtailmentPerTs
        GROUP BY 1, 2
    ),
    WindImpact  AS (SELECT TIMESTAMP, IMPACT AS WIND_IMPACT  FROM CurtailImpactHourly WHERE FUEL_TYPE = ''WIND''),
    SolarImpact AS (SELECT TIMESTAMP, IMPACT AS SOLAR_IMPACT FROM CurtailImpactHourly WHERE FUEL_TYPE = ''SOLAR'')

    SELECT
        :P_CONFIG_ID AS CONFIG_ID,
        f.TIMESTAMP,
        ROUND(f.FLOW + COALESCE(pf.PAR_FLOW, 0), 2) AS INJECTION_FLOW,
        ROUND(COALESCE(d.DAM_RATE_B, :v_default_rate_b), 2) AS DAM_RATE_B,
        ROUND(COALESCE(d.DAM_RATE_B, :v_default_rate_b) - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)), 2) AS HEADROOM,
        ROUND(COALESCE(rt_dr.REALTIME_RATE_B, :v_default_rate_b_rt, d.DAM_RATE_B, :v_default_rate_b), 2) AS REALTIME_RATE_B,
        ROUND(COALESCE(rt_dr.REALTIME_RATE_B, :v_default_rate_b_rt, d.DAM_RATE_B, :v_default_rate_b)
              - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)), 2) AS HEADROOM_RT,
        ROUND(r.RT_VALUE, 2) AS RT_CONSTRAINT_VALUE,
        ROUND(r.RT_LIMIT, 2) AS RT_CONSTRAINT_LIMIT,
        ROUND(r.RT_LIMIT - r.RT_VALUE, 2) AS RT_ACTUAL_HEADROOM,
        CASE WHEN :P_INCLUDE_CURTAILMENT THEN ROUND(COALESCE(wi.WIND_IMPACT, 0), 2) END AS WIND_IMPACT,
        CASE WHEN :P_INCLUDE_CURTAILMENT THEN ROUND(COALESCE(si.SOLAR_IMPACT, 0), 2) END AS SOLAR_IMPACT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
             THEN ROUND((COALESCE(rt_dr.REALTIME_RATE_B, :v_default_rate_b_rt, d.DAM_RATE_B, :v_default_rate_b)
                        - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
                        - (COALESCE(wi.WIND_IMPACT, 0) + COALESCE(si.SOLAR_IMPACT, 0)), 2) END AS HEADROOM_AFTER_CURTAILMENT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
             THEN ROUND((COALESCE(d.DAM_RATE_B, :v_default_rate_b) - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
                        - COALESCE(wi.WIND_IMPACT, 0), 2) END AS HEADROOM_DAM_WIND_CURTAILMENT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
             THEN ROUND((COALESCE(d.DAM_RATE_B, :v_default_rate_b) - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
                        - COALESCE(si.SOLAR_IMPACT, 0), 2) END AS HEADROOM_DAM_SOLAR_CURTAILMENT,
        f.PSENSHIFTID
    FROM InjectionFlow f
    LEFT JOIN ParInjectionFlow pf   ON f.TIMESTAMP = pf.TIMESTAMP
    LEFT JOIN DAMLimits d           ON f.TIMESTAMP = d.TIMESTAMP
    LEFT JOIN RTDynamicRating rt_dr ON f.TIMESTAMP = rt_dr.TIMESTAMP
    LEFT JOIN RTConstraint r        ON f.TIMESTAMP = r.TIMESTAMP
    LEFT JOIN WindImpact wi         ON f.TIMESTAMP = wi.TIMESTAMP
    LEFT JOIN SolarImpact si        ON f.TIMESTAMP = si.TIMESTAMP
    WHERE NOT EXISTS (
        SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS existing
        WHERE existing.CONFIG_ID = :P_CONFIG_ID AND existing.TIMESTAMP = f.TIMESTAMP
    );

    v_rows_inserted := SQLROWCOUNT;

    -- 5. coverage: member hours in range that STILL have no result row (no load data for
    --    that hour, or the shift had no station mapping) - the honest remainder
    SELECT COUNT(*) INTO :v_hours_missing
      FROM TMP_VAL_MEMBER_HOURS mh
     WHERE NOT EXISTS (SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS x
                        WHERE x.CONFIG_ID = :P_CONFIG_ID AND x.TIMESTAMP = mh.TS);

    INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
    VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, :v_rows_inserted, ''SUCCESS'');

    v_elapsed_ms := DATEDIFF(''millisecond'', v_start_time, CURRENT_TIMESTAMP());

    RETURN OBJECT_CONSTRUCT(
        ''status'',                  ''SUCCESS'',
        ''config_id'',               :P_CONFIG_ID,
        ''topologyshiftsetid'',      :v_tssid,
        ''branch_label'',            :v_branch_label,
        ''date_range'',              :v_actual_start || '' to '' || :v_actual_end,
        ''members_total'',           :v_members_total,
        ''members_in_range'',        :v_members_in_range,
        ''duplicate_hours_dropped'', :v_dupes_dropped,
        ''already_present'',         :v_already_present,
        ''rows_inserted'',           :v_rows_inserted,
        ''hours_missing'',           :v_hours_missing,
        ''include_curtailment'',     :P_INCLUDE_CURTAILMENT,
        ''run_ms'',                  :v_elapsed_ms
    );

EXCEPTION
    WHEN OTHER THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, STATUS, ERROR_MESSAGE)
        VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, ''FAILED'', :SQLERRM);
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'', ''config_id'', :P_CONFIG_ID, ''error'', :SQLERRM);
END;
';
