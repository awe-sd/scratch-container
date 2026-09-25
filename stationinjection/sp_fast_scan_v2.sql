-- SP_RUN_FAST_SCAN_TEST_V2, snapshot-grain rewrite:
-- - Output grain is the raw SE snapshot (e.g. :57), not hour-floored/aggregated.
--   V1 rows land on the hour (:00); V2 rows carry :57 -- that's what tells them apart.
--   ALTER below adds the one new output column, RT_INTERVAL.
-- - HOUR_BUCKET (snapshot rounded to the hour it describes, :57 -> next hour's top) is an
--   internal CTE column, used to join hourly DAM/PAR sources -- not written to the table.
-- - DAM/PAR stay hourly (ercotDampsseLnView is one row per branch per HE, no GROUP BY/MAX
--   needed; PAR still SUMs across stations per hour); both join on HOUR_START = HOUR_BUCKET.
-- - RT dynamic rating, RT constraint and curtailment are nearest-in-time picks within
--   +/-30 min of the snapshot (QUALIFY by time distance), not hourly AVG. RT rating: MIN
--   across segments at the chosen timestamp (tightest segment is the branch limit).
--   RT constraint: restricted to the config's own contingency (spelling normalised).
-- - Source: AW.DBO.ERCOTSTATIONINJECTION; StationBusMapping/StationShifts/StationKvShifts
--   unchanged (CIM 205 + retired-station coverage, nearest-kV snap within 1.0).
-- - Calls SP_LOAD_FAST_SCAN_RT_CONSTRAINTS (sp_load_fast_scan_rt_constraints.sql) after the
--   main insert; deploy that file first.

-- Run once; existing rows get NULL for this column.
ALTER TABLE AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS ADD COLUMN RT_INTERVAL TIMESTAMP_NTZ;

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
        CONFIG_ID, TIMESTAMP, INJECTION_FLOW,
        DAM_RATE_B, HEADROOM,
        REALTIME_RATE_B, HEADROOM_RT,
        RT_CONSTRAINT_VALUE, RT_CONSTRAINT_LIMIT, RT_ACTUAL_HEADROOM, RT_INTERVAL,
        WIND_IMPACT, SOLAR_IMPACT, HEADROOM_AFTER_CURTAILMENT,
        HEADROOM_DAM_WIND_CURTAILMENT, HEADROOM_DAM_SOLAR_CURTAILMENT, PSENSHIFTID
    )
    WITH
    -- Bus -> (station, kV). CIM 205 for the current model, plus every monthly ERCOT data
    -- dictionary so stations/levels retired before model 205 still map (SE history goes back to 2022).
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
        UNION
        SELECT NMMSSTATIONCODE, SSWGBUSNUMBER, COALESCE(NMMSBASEKV, TRY_TO_DOUBLE(SSWGBASEKV))
        FROM AW.DBO.ERCOTDATADICTIONARY
        WHERE NMMSSTATIONCODE IS NOT NULL AND SSWGBUSNUMBER IS NOT NULL
          AND COALESCE(NMMSBASEKV, TRY_TO_DOUBLE(SSWGBASEKV)) IS NOT NULL
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

    -- SE (station, kV) pairs in range, snapped to the nearest CIM kV of that station (within 1.0 kV).
    -- Range padded -30 min to match InjectionFlow''s shifted snapshot window.
    StationKvShifts AS (
        SELECT si.NMMSSTATIONCODE AS StationCode, si.KVLEVEL, ss.StationPSENS
        FROM (
            SELECT DISTINCT NMMSSTATIONCODE, KVLEVEL
            FROM AW.DBO.ERCOTSTATIONINJECTION
            WHERE "TIMESTAMP" >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
              AND "TIMESTAMP" <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
        ) si
        JOIN StationShifts ss
          ON ss.StationCode = si.NMMSSTATIONCODE AND ABS(ss.KV - si.KVLEVEL) <= 1.0
        QUALIFY ROW_NUMBER() OVER (PARTITION BY si.NMMSSTATIONCODE, si.KVLEVEL ORDER BY ABS(ss.KV - si.KVLEVEL)) = 1
    ),

    -- One SE TIMESTAMP per nearest-hour bucket: most station rows in the bucket wins, latest on ties
    -- (drops the model-rollout-night stub snapshots) -- same rule as SP_LOAD_ERCOT_STATION_INJECTION''s TMP_SNAPSHOT.
    Snapshots AS (
        SELECT "TIMESTAMP", BUCKET FROM (
            SELECT "TIMESTAMP", DATE_TRUNC(''HOUR'', DATEADD(''MINUTE'', 30, "TIMESTAMP")) AS BUCKET, COUNT(*) AS N
            FROM AW.DBO.ERCOTSTATIONINJECTION
            WHERE "TIMESTAMP" >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
              AND "TIMESTAMP" <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
            GROUP BY 1, 2
        )
        QUALIFY ROW_NUMBER() OVER (PARTITION BY BUCKET ORDER BY N DESC, "TIMESTAMP" DESC) = 1
    ),

    -- Flow per SE snapshot, no hourly aggregation. HOUR_BUCKET = the hour the snapshot
    -- describes (a :57 snapshot describes the top of the next hour), used to join hourly
    -- sources (DAM, PAR).
    InjectionFlow AS (
        SELECT si."TIMESTAMP" AS TIMESTAMP,
               DATE_TRUNC(''HOUR'', DATEADD(''MINUTE'', 30, si."TIMESTAMP")) AS HOUR_BUCKET,   -- :57 describes the top of the next hour
               SUM(ks.StationPSENS * si.NETINJECTIONMW) AS FLOW
        FROM AW.DBO.ERCOTSTATIONINJECTION si
        JOIN Snapshots sn ON sn."TIMESTAMP" = si."TIMESTAMP"
        JOIN StationKvShifts ks ON ks.StationCode = si.NMMSSTATIONCODE AND ks.KVLEVEL = si.KVLEVEL
        WHERE si."TIMESTAMP" >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
          AND si."TIMESTAMP" <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
        GROUP BY si."TIMESTAMP"
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

    -- Hourly source: SUM here is across PAR stations at a given hour, not over time.
    ParInjectionFlow AS (
        SELECT DISTINCT
            DATEADD(''HOUR'', pe.HE - 1, pe.DATE) AS HOUR_START,
            SUM(((-30.0 + (pe.FROMTAP - 1.0) * 1.875) * prs.DIRECTION) * prs.SENSDVALUEDPHASE) AS PAR_FLOW
        FROM AW.DBO.PARERCOTVIEW pe
        INNER JOIN ParSens prs ON prs.PARSTATIONID = pe.PARSTATIONID
        WHERE pe.DATE >= :v_actual_start
          AND pe.DATE <= :v_actual_end
        GROUP BY pe.DATE, pe.HE
    ),

    -- Hourly source: exactly one row per branch per HE in ercotDampsseLnView, no aggregate needed.
    DAMLimits AS (
        SELECT DATEADD(''HOUR'', HE - 1, DATE) AS HOUR_START, RATEB AS DAM_RATE_B
        FROM AW.DBO.ercotDampsseLnView
        WHERE DATE >= :v_actual_start AND DATE <= :v_actual_end
          AND branchname = :v_branch_name
    ),

    -- Nearest rating timestamp to the snapshot within +/-30 min; MIN across segments at
    -- that timestamp (the tightest segment is the branch limit).
    RTDynamicRating AS (
        SELECT TIMESTAMP, RT_RATING_TIME, REALTIME_RATE_B FROM (
            SELECT f.TIMESTAMP, r.createTime AS RT_RATING_TIME, MIN(r.EMERGENCYRATINGS) AS REALTIME_RATE_B
            FROM InjectionFlow f
            JOIN AW.DBO.ERCOTRTDYNAMICRATINGVIEW r
              ON r.branchname = :v_branch_name
             AND r.createTime BETWEEN DATEADD(''MINUTE'', -30, f.TIMESTAMP) AND DATEADD(''MINUTE'', 30, f.TIMESTAMP)
            GROUP BY f.TIMESTAMP, r.createTime
        )
        QUALIFY ROW_NUMBER() OVER (PARTITION BY TIMESTAMP ORDER BY ABS(TIMESTAMPDIFF(SECOND, TIMESTAMP, RT_RATING_TIME)), RT_RATING_TIME DESC) = 1
    ),

    -- ERCOT reports CONSTRAINTVALUE with a sign that follows the monitored direction, so the
    -- same physical loading shows up positive in one interval and negative in the next.
    -- Headroom is limit minus |flow| regardless, hence ABS rather than a direction flip.
    -- Only the config''s own contingency (spelling normalised); nearest SCED interval within +/-30 min.
    RTConstraint AS (
        SELECT f.TIMESTAMP, cfp.DATETIME AS RT_INTERVAL, cdc.CONGCONTNAME AS CONTINGENCY,
               ABS(cfp.CONSTRAINTVALUE) AS RT_VALUE, cfp.CONSTRAINTLIMIT AS RT_LIMIT
        FROM InjectionFlow f
        JOIN AW.DBO.CONGFQPRICEVIEW cfp
          ON cfp.ISOMARKETID = :P_ISO_MARKET_ID AND cfp.PRICETYPEID = 2
         AND cfp.DATETIME BETWEEN DATEADD(''MINUTE'', -30, f.TIMESTAMP) AND DATEADD(''MINUTE'', 30, f.TIMESTAMP)
         AND cfp."DATE" BETWEEN DATEADD(''DAY'', -1, :v_actual_start) AND DATEADD(''DAY'', 1, :v_actual_end)
        JOIN AW.DBO.CONGDEFCONSTRAINTVIEW cdc ON cdc.CONGCONSTRAINTID = cfp.CONGCONSTRAINTID
        WHERE cdc.BRANCHID IN (
              SELECT DISTINCT BRANCHID FROM AW.DBO.PTOBRANCH
              WHERE ((FROMNUM = :v_from_num AND TONUM = :v_to_num AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR)))
                  OR (FROMNUM = :v_to_num AND TONUM = :v_from_num AND TRIM(CAST(CKT AS VARCHAR)) = TRIM(CAST(:v_ckt AS VARCHAR))))
                AND PTOID = :v_ptoid)
          AND REPLACE(UPPER(cdc.CONGCONTNAME), '' '', '''') = REPLACE(UPPER(:v_ctg_label), '' '', '''')
        -- same tie-break as SP_LOAD_FAST_SCAN_RT_CONSTRAINTS''s Binding QUALIFY, so a duplicate CONGCONSTRAINTID for the same branch/contingency/interval resolves the same way in both places
        QUALIFY ROW_NUMBER() OVER (PARTITION BY f.TIMESTAMP ORDER BY ABS(TIMESTAMPDIFF(SECOND, f.TIMESTAMP, cfp.DATETIME)), cfp.DATETIME DESC, ABS(cfp.CONSTRAINTVALUE) DESC) = 1
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
    -- summed per 5-minute timestamp per fuel. Window shifted -30 min to match InjectionFlow.
    CurtailmentPerTs AS (
        SELECT
            gr.TimeStamp,
            ru.FUEL_TYPE,
            SUM(GREATEST(gr.HSL - gr.BasePoint, 0) * s.PSENS) AS Impact
        FROM AW.DBO.ISOERCOTSCEDGEN g
        JOIN AW.DBO.ISOERCOTSCEDGENRESOURCE gr ON g.genId = gr.genID
        JOIN RenewableUnits ru ON g.ResourceName = ru.UNIT_CODE
        JOIN CurtailSens s ON g.cpnodeid = s.CPNODEID
        WHERE gr.TimeStamp >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
          AND gr.TimeStamp <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
          AND :P_INCLUDE_CURTAILMENT = TRUE
        GROUP BY gr.TimeStamp, ru.FUEL_TYPE
    ),

    -- Nearest SCED run to the snapshot within +/-30 min, per fuel.
    CurtailAtSnapshot AS (
        SELECT f.TIMESTAMP, c.TimeStamp AS SCED_RUN, c.FUEL_TYPE, c.Impact
        FROM InjectionFlow f
        JOIN CurtailmentPerTs c ON c.TimeStamp BETWEEN DATEADD(''MINUTE'', -30, f.TIMESTAMP) AND DATEADD(''MINUTE'', 30, f.TIMESTAMP)
        QUALIFY ROW_NUMBER() OVER (PARTITION BY f.TIMESTAMP, c.FUEL_TYPE ORDER BY ABS(TIMESTAMPDIFF(SECOND, f.TIMESTAMP, c.TimeStamp)), c.TimeStamp DESC) = 1
    ),
    WindImpact  AS (SELECT TIMESTAMP, SCED_RUN, Impact AS WIND_IMPACT  FROM CurtailAtSnapshot WHERE FUEL_TYPE = ''WIND''),
    SolarImpact AS (SELECT TIMESTAMP, SCED_RUN, Impact AS SOLAR_IMPACT FROM CurtailAtSnapshot WHERE FUEL_TYPE = ''SOLAR'')

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
        r.RT_INTERVAL,
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
             ELSE NULL END AS HEADROOM_DAM_SOLAR_CURTAILMENT,
        :v_psenshiftid AS PSENSHIFTID
    FROM InjectionFlow f
    LEFT JOIN ParInjectionFlow pf ON pf.HOUR_START = f.HOUR_BUCKET
    LEFT JOIN DAMLimits d ON d.HOUR_START = f.HOUR_BUCKET
    LEFT JOIN RTDynamicRating rt_dr ON rt_dr.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN RTConstraint r ON r.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN WindImpact wi ON wi.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN SolarImpact si ON si.TIMESTAMP = f.TIMESTAMP
    WHERE NOT EXISTS (
        SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS existing
        WHERE existing.CONFIG_ID = :P_CONFIG_ID AND existing.TIMESTAMP = f.TIMESTAMP
    );

    v_rows_inserted := SQLROWCOUNT;

    -- 4b. Every contingency binding on the branch at the same intervals -> FAST_SCAN_RT_CONSTRAINTS
    CALL FLOW_ANALYSIS.SP_LOAD_FAST_SCAN_RT_CONSTRAINTS(:P_CONFIG_ID, :v_actual_start, :v_actual_end, :P_ISO_MARKET_ID);

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
