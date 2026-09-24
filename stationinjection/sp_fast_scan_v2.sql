-- SP_RUN_FAST_SCAN_TEST_V2 vs SP_RUN_FAST_SCAN:
-- - Source: AW.DBO.ERCOTSTATIONINJECTION (per-kV net injection) instead of
--   AW.DBO.ERCOTSTATIONLOAD (station-grain withdrawal).
-- - StationBusMapping is CIM-only (v_cim_file_id 205) and carries KV.
-- - Shift factors computed per (StationCode, KV) in StationShifts.
-- - Sign: AVG(PSENS) directly (table is net injection, not withdrawal;
--   no leading minus).
-- - StationKvShifts snaps each SE (station, kV) to the nearest CIM kV
--   within 0.5 (SE/CIM kV rounding mismatch, e.g. 12.5 vs 12.4).
-- - InjectionFlow computes flow per SE snapshot, keeps the latest snapshot per hour.
CREATE OR REPLACE PROCEDURE AW.FLOW_ANALYSIS.SP_RUN_FAST_SCAN_TEST_V2("P_CONFIG_ID" NUMBER(38,0), "P_START_DATE" DATE DEFAULT null, "P_END_DATE" DATE DEFAULT null, "P_INCLUDE_CURTAILMENT" BOOLEAN DEFAULT TRUE, "P_ISO_MARKET_ID" NUMBER(38,0) DEFAULT 6)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS OWNER
AS '
DECLARE
    v_psenshiftid INT;
    v_from_num INT;
    v_to_num INT;
    v_ckt VARCHAR(10);
    v_ctg_label VARCHAR(100);
    v_direction INT;
    v_ptoid INT;
    v_branch_label VARCHAR(200);
    v_branch_name VARCHAR(400);
    v_default_rate_b FLOAT;
    v_default_rate_b_rt FLOAT;
    v_cim_file_id INT := 205;
    v_actual_start DATE;
    v_actual_end DATE;
    v_rows_inserted INT;
    v_start_time TIMESTAMP_NTZ := CURRENT_TIMESTAMP();
    v_wh_name VARCHAR := CURRENT_WAREHOUSE();
    v_elapsed_ms INT;
    v_existing_row_count INT;
BEGIN

    -- 0. Ensure this is a new config:
    SELECT COUNT(*) INTO v_existing_row_count FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS WHERE CONFIG_ID = :P_CONFIG_ID;
    IF (v_existing_row_count > 0) THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
        VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, 0, ''EXISTING_CONFIG_ID'');
        RETURN OBJECT_CONSTRUCT(''status'', ''EXISTING_CONFIG_ID'', ''rows'', 0);
    END IF;

    -- 1. Get config parameters (now includes BRANCH_NAME)
    SELECT PSENSHIFTID, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECTION, PTOID,
           BRANCH_LABEL, DEFAULT_RATE_B, DEFAULT_RATE_B_RT, BRANCH_NAME
    INTO :v_psenshiftid, :v_from_num, :v_to_num, :v_ckt, :v_ctg_label,
         :v_direction, :v_ptoid, :v_branch_label, :v_default_rate_b, :v_default_rate_b_rt, :v_branch_name
    FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
    WHERE CONFIG_ID = :P_CONFIG_ID;

    -- 2. Determine date range
    IF (P_START_DATE IS NULL) THEN
        SELECT COALESCE(DATE_TRUNC(''DAY'', MAX(TIMESTAMP)) + INTERVAL ''1 DAY'', ''2022-01-01'')
        INTO v_actual_start
        FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = :P_CONFIG_ID;
    ELSE
        v_actual_start := :P_START_DATE;
    END IF;
    IF (P_END_DATE IS NULL) THEN
        v_actual_end := DATEADD(''year'', 2, v_actual_start);
    ELSE
        v_actual_end := :P_END_DATE;
    END IF;

    -- 3. Skip if no new data needed
    IF (v_actual_start > v_actual_end) THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
        VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, 0, ''NO_NEW_DATA'');
        RETURN OBJECT_CONSTRUCT(''status'', ''NO_NEW_DATA'', ''rows'', 0);
    END IF;

    -- 4. THE MAIN CALCULATION
    INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RESULTS (
        CONFIG_ID, TIMESTAMP, INJECTION_FLOW, -- PAR_INJECTION_FLOW,
        DAM_RATE_B, HEADROOM,
        REALTIME_RATE_B, HEADROOM_RT,
        RT_CONSTRAINT_VALUE, RT_CONSTRAINT_LIMIT, RT_ACTUAL_HEADROOM,
        WIND_IMPACT, SOLAR_IMPACT, HEADROOM_AFTER_CURTAILMENT,
        HEADROOM_DAM_WIND_CURTAILMENT, HEADROOM_DAM_SOLAR_CURTAILMENT
    )
    WITH
    StationBusMapping AS (
        SELECT sv.NAME_SUBSTATION AS StationCode, cn.PSSEBUSNUMBER AS BusNum, TRY_TO_DOUBLE(sv.NAME) AS KV
        FROM (
            SELECT CIMSTATIONVOLTAGELEVELID, CIMFILEID, PSSEBUSNUMBER
            FROM AW.DBO.CIMCONNODE
            WHERE CIMFILEID = :v_cim_file_id AND PSSEBUSNUMBER IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (PARTITION BY PSSEBUSNUMBER ORDER BY CIMCONNODEID) = 1
        ) cn
        JOIN AW.DBO.CIMSTATIONVOLTAGELEVEL sv
          ON sv.CIMFILEID = cn.CIMFILEID AND sv.CIMSTATIONVOLTAGELEVELID = cn.CIMSTATIONVOLTAGELEVELID
        WHERE sv.NAME_SUBSTATION IS NOT NULL AND TRY_TO_DOUBLE(sv.NAME) IS NOT NULL
    ),

    -- Shift factor per (station, kV): buses at the same voltage level of a station are averaged.
    -- AVG(PSENS) not -AVG(PSENS): the new table holds net injection, not withdrawal.
    StationShifts AS (
        SELECT m.StationCode, m.KV, AVG(bs.PSENS) AS StationPSENS
        FROM SHIFT_FACTORS.DBO.BUS_SHIFTS bs
        JOIN StationBusMapping m ON bs.BUSNUM = m.BusNum
        WHERE bs.ISOMARKETID = :P_ISO_MARKET_ID AND bs.PSENSHIFTID = :v_psenshiftid
        GROUP BY m.StationCode, m.KV
        HAVING ABS(AVG(bs.PSENS)) > 0.00001
    ),

    -- SE (station, kV) pairs in range, snapped to the nearest CIM kV of that station (within 0.5 kV)
    StationKvShifts AS (
        SELECT si.NMMSSTATIONCODE AS StationCode, si.KVLEVEL, ss.StationPSENS
        FROM (
            SELECT DISTINCT NMMSSTATIONCODE, KVLEVEL
            FROM AW.DBO.ERCOTSTATIONINJECTION
            WHERE "TIMESTAMP" >= :v_actual_start AND "TIMESTAMP" < DATEADD(''DAY'', 1, :v_actual_end)
        ) si
        JOIN StationShifts ss
          ON ss.StationCode = si.NMMSSTATIONCODE AND ABS(ss.KV - si.KVLEVEL) <= 0.5
        QUALIFY ROW_NUMBER() OVER (PARTITION BY si.NMMSSTATIONCODE, si.KVLEVEL ORDER BY ABS(ss.KV - si.KVLEVEL)) = 1
    ),

    -- Flow per SE snapshot; where an hour has two snapshots (:57 and :58) keep the latest one
    InjectionFlow AS (
        SELECT DATE_TRUNC(''HOUR'', si."TIMESTAMP") AS TIMESTAMP,
               SUM(ks.StationPSENS * si.NETINJECTIONMW) AS FLOW
        FROM AW.DBO.ERCOTSTATIONINJECTION si
        JOIN StationKvShifts ks ON ks.StationCode = si.NMMSSTATIONCODE AND ks.KVLEVEL = si.KVLEVEL
        WHERE si."TIMESTAMP" >= :v_actual_start AND si."TIMESTAMP" < DATEADD(''DAY'', 1, :v_actual_end)
        GROUP BY si."TIMESTAMP"
        QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC(''HOUR'', si."TIMESTAMP") ORDER BY si."TIMESTAMP" DESC) = 1
    ),

    ParSens AS (
        SELECT
            ps.BUSNUMFROM,
            ps.BUSNUMTO,
            ps.CKT,
            ps.SENSDVALUEDPHASE,
            pes.PARSTATIONID,
            pes.DIRECTION
        FROM SHIFT_FACTORS.DBO.PAR_SHIFTS ps
        INNER JOIN AW.DBO.PARERCOTSTATION pes
            ON ((pes.FROM_BUS_NUM = ps.BUSNUMFROM
                AND pes.TO_BUS_NUM = ps.BUSNUMTO
                AND TRIM(CAST(pes.CKT AS VARCHAR)) = TRIM(CAST(ps.CKT AS VARCHAR)))
            OR (pes.FROM_BUS_NUM = ps.BUSNUMTO
                AND pes.TO_BUS_NUM = ps.BUSNUMFROM
                AND TRIM(CAST(pes.CKT AS VARCHAR)) = TRIM(CAST(ps.CKT AS VARCHAR))))
        WHERE ps.ISOMARKETID = :p_ISO_MARKET_ID and ps.PSENSHIFTID = :v_psenshiftid
    ),

    ParInjectionFlow AS (
        SELECT DISTINCT
            DATEADD(''HOUR'', pe.HE - 1, pe.DATE) AS TIMESTAMP,
            SUM(((-30.0 + (pe.FROMTAP - 1.0) * 1.875) * prs.DIRECTION) * prs.SENSDVALUEDPHASE) AS PAR_FLOW
        FROM AW.DBO.PARERCOTVIEW pe
        INNER JOIN ParSens prs ON prs.PARSTATIONID = pe.PARSTATIONID
        WHERE pe.DATE >= :v_actual_start
          AND pe.DATE <= :v_actual_end
        GROUP BY pe.DATE, pe.HE
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
        WHERE cfp.ISOMARKETID = :p_ISO_MARKET_ID AND cfp.PRICETYPEID = 2
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

    -- Sensitivity factors at each cpnode for this shift (shared by wind and solar).
    CurtailSens AS (
        SELECT CPNODEID, PSENS
        FROM SHIFT_FACTORS.DBO.CPNODE_SHIFTS
        WHERE ISOMARKETID = :p_ISO_MARKET_ID and PSENSHIFTID = :v_psenshiftid
    ),

   -- One pass over the resource adequacy report for both fuels.
    RenewableUnits AS (
        SELECT UNIT_CODE,
               CASE WHEN FUEL ILIKE ''%WIND%'' THEN ''WIND'' ELSE ''SOLAR'' END AS FUEL_TYPE
        FROM AW.DBO.ERCOT_RESOURCE_ADEQUACY_REPORT_VIEW
        WHERE UNIT_CODE != ''NA''
          AND (FUEL ILIKE ''%WIND%'' OR FUEL ILIKE ''%SOLAR%'')
        QUALIFY ROW_NUMBER() OVER (PARTITION BY UNIT_CODE ORDER BY report_date DESC) = 1
    ),

    -- One pass over SCED for both fuels, curtailment weighted by sensitivity,
    -- summed per 5-minute timestamp per fuel.
    CurtailmentPerTs AS (
        SELECT
            gr.TimeStamp,
            ru.FUEL_TYPE,
            SUM(GREATEST(gr.HSL - gr.BasePoint, 0) * s.PSENS) AS Impact
        FROM AW.DBO.ISOERCOTSCEDGEN g
        JOIN AW.DBO.ISOERCOTSCEDGENRESOURCE gr ON g.genId = gr.genID
        JOIN RenewableUnits ru ON g.ResourceName = ru.UNIT_CODE
        JOIN CurtailSens s ON g.cpnodeid = s.CPNODEID
        WHERE gr.TimeStamp >= :v_actual_start
          AND gr.TimeStamp < DATEADD(''DAY'', 1, :v_actual_end)
          AND :P_INCLUDE_CURTAILMENT = TRUE
        GROUP BY gr.TimeStamp, ru.FUEL_TYPE
    ),

    -- Hourly rollup for both fuels at once.
    CurtailImpactHourly AS (
        SELECT
            DATE_TRUNC(''HOUR'', TimeStamp) AS TIMESTAMP,
            FUEL_TYPE,
            AVG(Impact) AS IMPACT
        FROM CurtailmentPerTs
        GROUP BY 1, 2
    ),

    WindImpact AS (
        SELECT TIMESTAMP, IMPACT AS WIND_IMPACT
        FROM CurtailImpactHourly
        WHERE FUEL_TYPE = ''WIND''
    ),

    SolarImpact AS (
        SELECT TIMESTAMP, IMPACT AS SOLAR_IMPACT
        FROM CurtailImpactHourly
        WHERE FUEL_TYPE = ''SOLAR''
    )

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
        CASE WHEN :P_INCLUDE_CURTAILMENT THEN ROUND(COALESCE(wi.WIND_IMPACT, 0), 2) ELSE NULL END AS WIND_IMPACT,
        CASE WHEN :P_INCLUDE_CURTAILMENT THEN ROUND(COALESCE(si.SOLAR_IMPACT, 0), 2) ELSE NULL END AS SOLAR_IMPACT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
         THEN ROUND((COALESCE(rt_dr.REALTIME_RATE_B, :v_default_rate_b_rt, d.DAM_RATE_B, :v_default_rate_b)
               - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
              - (COALESCE(wi.WIND_IMPACT, 0) + COALESCE(si.SOLAR_IMPACT, 0)), 2)
         ELSE NULL END AS HEADROOM_AFTER_CURTAILMENT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
             THEN ROUND((COALESCE(d.DAM_RATE_B, :v_default_rate_b) - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
                  - COALESCE(wi.WIND_IMPACT, 0), 2)
             ELSE NULL END AS HEADROOM_DAM_WIND_CURTAILMENT,
        CASE WHEN :P_INCLUDE_CURTAILMENT
             THEN ROUND((COALESCE(d.DAM_RATE_B, :v_default_rate_b) - ABS(f.FLOW + COALESCE(pf.PAR_FLOW, 0)))
                  - COALESCE(si.SOLAR_IMPACT, 0), 2)
             ELSE NULL END AS HEADROOM_DAM_SOLAR_CURTAILMENT
    FROM InjectionFlow f
    LEFT JOIN ParInjectionFlow pf ON f.TIMESTAMP = pf.TIMESTAMP
    LEFT JOIN DAMLimits d ON f.TIMESTAMP = d.TIMESTAMP
    LEFT JOIN RTDynamicRating rt_dr ON f.TIMESTAMP = rt_dr.TIMESTAMP
    LEFT JOIN RTConstraint r ON f.TIMESTAMP = r.TIMESTAMP
    LEFT JOIN WindImpact wi ON f.TIMESTAMP = wi.TIMESTAMP
    LEFT JOIN SolarImpact si ON f.TIMESTAMP = si.TIMESTAMP
    WHERE NOT EXISTS (
        SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS existing
        WHERE existing.CONFIG_ID = :P_CONFIG_ID AND existing.TIMESTAMP = f.TIMESTAMP
    );

    v_rows_inserted := SQLROWCOUNT;

    -- 5. Log the run
    INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
    VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, :v_rows_inserted, ''SUCCESS'');

    v_elapsed_ms := DATEDIFF(''millisecond'', v_start_time, CURRENT_TIMESTAMP());

    RETURN OBJECT_CONSTRUCT(
        ''status'', ''SUCCESS'',
        ''config_id'', :P_CONFIG_ID,
        ''psenShiftID'', :v_psenshiftid,
        ''branch_label'', :v_branch_label,
        ''include_curtailment'', :P_INCLUDE_CURTAILMENT,
        ''date_range'', :v_actual_start || '' to '' || :v_actual_end,
        ''rows_inserted'', :v_rows_inserted,
        ''run_ms'', :v_elapsed_ms,
        ''v_wh_name'', :v_wh_name
    );

EXCEPTION
    WHEN OTHER THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, STATUS, ERROR_MESSAGE)
        VALUES (:P_CONFIG_ID, :v_actual_start, :v_actual_end, ''FAILED'', :SQLERRM);
        RETURN OBJECT_CONSTRUCT(''status'', ''FAILED'', ''error'', :SQLERRM);
END;
';
