-- SP_RUN_VALIDATION_FAST_SCAN_TEST_V2: validation-set counterpart of
-- SP_RUN_FAST_SCAN_TEST_V2 (sp_fast_scan_v2.sql), same ERCOTSTATIONINJECTION source and
-- snapshot grain, but one PSENSHIFTID per member hour (TOPOLOGYSHIFTSETID configs) instead
-- of a single fixed shift. Member-hour skeleton (TMP_VAL_MEMBER_HOURS, NOT_A_VALIDATION_CONFIG
-- guard, date-range defaulting, already_present/hours_missing) is V1's, compared by hour
-- bucket since results now carry :57 stamps. Calls SP_LOAD_FAST_SCAN_RT_CONSTRAINTS after
-- the main insert, same as V2.

CREATE OR REPLACE PROCEDURE AW.FLOW_ANALYSIS.SP_RUN_VALIDATION_FAST_SCAN_TEST_V2("P_CONFIG_ID" NUMBER(38,0), "P_START_DATE" DATE DEFAULT null, "P_END_DATE" DATE DEFAULT null, "P_INCLUDE_CURTAILMENT" BOOLEAN DEFAULT TRUE, "P_ISO_MARKET_ID" NUMBER(38,0) DEFAULT 6)
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
    v_ctg_label         VARCHAR(100);
    v_direction         INT;
    v_ptoid             INT;
    v_branch_label      VARCHAR(200);
    v_branch_name       VARCHAR(400);
    v_default_rate_b    FLOAT;
    v_default_rate_b_rt FLOAT;
    v_cim_file_id       INT := 205;
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
    SELECT SOURCE_TYPE, TOPOLOGYSHIFTSETID, STUDY_ID, FROM_NUM, TO_NUM, CKT, CTG_LABEL, DIRECTION, PTOID,
           BRANCH_LABEL, BRANCH_NAME, DEFAULT_RATE_B, DEFAULT_RATE_B_RT
      INTO :v_source_type, :v_tssid, :v_study_id, :v_from_num, :v_to_num, :v_ckt, :v_ctg_label, :v_direction,
           :v_ptoid, :v_branch_label, :v_branch_name, :v_default_rate_b, :v_default_rate_b_rt
      FROM FLOW_ANALYSIS.FAST_SCAN_CONFIG
     WHERE CONFIG_ID = :P_CONFIG_ID;

    IF (v_source_type IS DISTINCT FROM ''VALIDATION'' OR v_tssid IS NULL) THEN
        INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RUN_LOG (CONFIG_ID, START_DATE, END_DATE, ROWS_INSERTED, STATUS)
        VALUES (:P_CONFIG_ID, :P_START_DATE, :P_END_DATE, 0, ''NOT_A_VALIDATION_CONFIG'');
        RETURN OBJECT_CONSTRUCT(''status'', ''NOT_A_VALIDATION_CONFIG'', ''config_id'', :P_CONFIG_ID,
                                ''rows_inserted'', 0);
    END IF;

    -- 2. member hours
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

    SELECT COUNT(*) INTO :v_dupes_dropped FROM TMP_VAL_MEMBER_HOURS WHERE RN > 1;
    DELETE FROM TMP_VAL_MEMBER_HOURS WHERE RN > 1;

    -- 3. date range
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
      JOIN FLOW_ANALYSIS.FAST_SCAN_RESULTS x
        ON x.CONFIG_ID = :P_CONFIG_ID
       AND DATE_TRUNC(''HOUR'', DATEADD(''MINUTE'', 30, x.TIMESTAMP)) = mh.TS;

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
    Members AS (
        SELECT PSENSHIFTID, TS FROM TMP_VAL_MEMBER_HOURS
    ),
    MemberShifts AS (
        SELECT DISTINCT PSENSHIFTID FROM TMP_VAL_MEMBER_HOURS
    ),

    -- Bus -> (station, kV). CIM 205 for the current model, plus every monthly ERCOT data
    -- dictionary so stations/levels retired before model 205 still map.
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

    -- Shift factor per (member shift, station, kV). AVG(PSENS) not -AVG(PSENS): the new
    -- table holds net injection, not withdrawal.
    StationShifts AS (
        SELECT bs.PSENSHIFTID, m.StationCode, m.KV, AVG(bs.PSENS) AS StationPSENS
        FROM SHIFT_FACTORS.DBO.BUS_SHIFTS bs
        JOIN MemberShifts ms ON ms.PSENSHIFTID = bs.PSENSHIFTID
        JOIN StationBusMapping m ON bs.BUSNUM = m.BusNum
        WHERE bs.ISOMARKETID = :P_ISO_MARKET_ID
        GROUP BY bs.PSENSHIFTID, m.StationCode, m.KV
        HAVING ABS(AVG(bs.PSENS)) > 0.00001
    ),

    -- SE (station, kV) pairs in range, snapped to the nearest CIM kV of that station (within
    -- 1.0 kV) per member shift. Range padded -30 min to match InjectionFlow''s shifted window.
    StationKvShifts AS (
        SELECT ss.PSENSHIFTID, si.NMMSSTATIONCODE AS StationCode, si.KVLEVEL, ss.StationPSENS
        FROM (
            SELECT DISTINCT NMMSSTATIONCODE, KVLEVEL
            FROM AW.DBO.ERCOTSTATIONINJECTION
            WHERE "TIMESTAMP" >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
              AND "TIMESTAMP" <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
        ) si
        JOIN StationShifts ss
          ON ss.StationCode = si.NMMSSTATIONCODE AND ABS(ss.KV - si.KVLEVEL) <= 1.0
        QUALIFY ROW_NUMBER() OVER (PARTITION BY ss.PSENSHIFTID, si.NMMSSTATIONCODE, si.KVLEVEL ORDER BY ABS(ss.KV - si.KVLEVEL)) = 1
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

    -- Flow per SE snapshot per member shift. HOUR_BUCKET = the hour the snapshot describes
    -- (a :57 snapshot describes the top of the next hour), used to join hourly sources (DAM, PAR).
    InjectionFlow AS (
        SELECT
            si."TIMESTAMP" AS TIMESTAMP,
            mb.TS AS HOUR_BUCKET,
            mb.PSENSHIFTID,
            SUM(ks.StationPSENS * si.NETINJECTIONMW) AS FLOW
        FROM Members mb
        JOIN Snapshots sn ON sn.BUCKET = mb.TS
        JOIN AW.DBO.ERCOTSTATIONINJECTION si
          ON si."TIMESTAMP" = sn."TIMESTAMP"
         AND si."TIMESTAMP" >= DATEADD(''MINUTE'', -30, :v_actual_start::TIMESTAMP_NTZ)
         AND si."TIMESTAMP" <  DATEADD(''MINUTE'', -30, DATEADD(''DAY'', 1, :v_actual_end)::TIMESTAMP_NTZ)
        JOIN StationKvShifts ks
          ON ks.PSENSHIFTID = mb.PSENSHIFTID AND ks.StationCode = si.NMMSSTATIONCODE AND ks.KVLEVEL = si.KVLEVEL
        GROUP BY 1, 2, 3
    ),

    -- One row per snapshot timestamp, even though the RN dedup already guarantees a single
    -- PSENSHIFTID per member hour -- drives RT rating/constraint safely either way.
    InjectionTimestamps AS (
        SELECT DISTINCT TIMESTAMP FROM InjectionFlow
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

    -- Hourly source: SUM here is across PAR stations at a given hour, not over time.
    ParInjectionFlow AS (
        SELECT
            mb.TS AS HOUR_START,
            SUM(((-30.0 + (pe.FROMTAP - 1.0) * 1.875) * prs.DIRECTION) * prs.SENSDVALUEDPHASE) AS PAR_FLOW
        FROM Members mb
        JOIN AW.DBO.PARERCOTVIEW pe
            ON DATEADD(''HOUR'', pe.HE - 1, pe.DATE) = mb.TS
        JOIN ParSens prs
            ON prs.PSENSHIFTID = mb.PSENSHIFTID AND prs.PARSTATIONID = pe.PARSTATIONID
        WHERE pe.DATE >= :v_actual_start AND pe.DATE <= :v_actual_end
        GROUP BY mb.TS
    ),

    -- Hourly source: exactly one row per branch per HE in ercotDampsseLnView, no aggregate needed.
    DAMLimits AS (
        SELECT DATEADD(''HOUR'', HE - 1, DATE) AS HOUR_START, RATEB AS DAM_RATE_B
        FROM AW.DBO.ercotDampsseLnView
        WHERE DATE >= :v_actual_start AND DATE <= :v_actual_end
          AND branchname = :v_branch_name
    ),

    -- Nearest rating timestamp to the snapshot within +/-30 min; MIN across segments at that
    -- timestamp (the tightest segment is the branch limit).
    RTDynamicRating AS (
        SELECT TIMESTAMP, RT_RATING_TIME, REALTIME_RATE_B FROM (
            SELECT f.TIMESTAMP, r.createTime AS RT_RATING_TIME, MIN(r.EMERGENCYRATINGS) AS REALTIME_RATE_B
            FROM InjectionTimestamps f
            JOIN AW.DBO.ERCOTRTDYNAMICRATINGVIEW r
              ON r.branchname = :v_branch_name
             AND r.createTime BETWEEN DATEADD(''MINUTE'', -30, f.TIMESTAMP) AND DATEADD(''MINUTE'', 30, f.TIMESTAMP)
            GROUP BY f.TIMESTAMP, r.createTime
        )
        QUALIFY ROW_NUMBER() OVER (PARTITION BY TIMESTAMP ORDER BY ABS(TIMESTAMPDIFF(SECOND, TIMESTAMP, RT_RATING_TIME)), RT_RATING_TIME DESC) = 1
    ),

    -- Only the config''s own contingency (spelling normalised); nearest SCED interval within +/-30 min.
    RTConstraint AS (
        SELECT f.TIMESTAMP, cfp.DATETIME AS RT_INTERVAL, cdc.CONGCONTNAME AS CONTINGENCY,
               ABS(cfp.CONSTRAINTVALUE) AS RT_VALUE, cfp.CONSTRAINTLIMIT AS RT_LIMIT
        FROM InjectionTimestamps f
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

    -- Sensitivity factors at each cpnode per member shift (shared by wind and solar).
    CurtailSens AS (
        SELECT cs.PSENSHIFTID, cs.CPNODEID, cs.PSENS
        FROM SHIFT_FACTORS.DBO.CPNODE_SHIFTS cs
        JOIN MemberShifts ms ON ms.PSENSHIFTID = cs.PSENSHIFTID
        WHERE cs.ISOMARKETID = :P_ISO_MARKET_ID
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

    -- Per member hour: own shift only, SCED runs within +/-60 min of the hour bucket.
    CurtailmentPerTs AS (
        SELECT
            mb.TS AS HOUR_BUCKET,
            mb.PSENSHIFTID,
            gr.TimeStamp,
            ru.FUEL_TYPE,
            SUM(GREATEST(gr.HSL - gr.BasePoint, 0) * s.PSENS) AS Impact
        FROM Members mb
        JOIN AW.DBO.ISOERCOTSCEDGENRESOURCE gr
          ON gr.TimeStamp >= DATEADD(''MINUTE'', -60, mb.TS) AND gr.TimeStamp < DATEADD(''MINUTE'', 60, mb.TS)
        JOIN AW.DBO.ISOERCOTSCEDGEN g ON g.genId = gr.genID
        JOIN RenewableUnits ru ON g.ResourceName = ru.UNIT_CODE
        JOIN CurtailSens s ON s.PSENSHIFTID = mb.PSENSHIFTID AND g.cpnodeid = s.CPNODEID
        WHERE :P_INCLUDE_CURTAILMENT = TRUE
        GROUP BY mb.TS, mb.PSENSHIFTID, gr.TimeStamp, ru.FUEL_TYPE
    ),

    -- Nearest SCED run to the snapshot within +/-30 min, per fuel, matched to the same
    -- member hour/shift as the snapshot.
    CurtailAtSnapshot AS (
        SELECT f.TIMESTAMP, c.FUEL_TYPE, c.Impact
        FROM InjectionFlow f
        JOIN CurtailmentPerTs c
          ON c.HOUR_BUCKET = f.HOUR_BUCKET AND c.PSENSHIFTID = f.PSENSHIFTID
         AND c.TimeStamp BETWEEN DATEADD(''MINUTE'', -30, f.TIMESTAMP) AND DATEADD(''MINUTE'', 30, f.TIMESTAMP)
        QUALIFY ROW_NUMBER() OVER (PARTITION BY f.TIMESTAMP, c.FUEL_TYPE ORDER BY ABS(TIMESTAMPDIFF(SECOND, f.TIMESTAMP, c.TimeStamp)), c.TimeStamp DESC) = 1
    ),
    WindImpact  AS (SELECT TIMESTAMP, Impact AS WIND_IMPACT  FROM CurtailAtSnapshot WHERE FUEL_TYPE = ''WIND''),
    SolarImpact AS (SELECT TIMESTAMP, Impact AS SOLAR_IMPACT FROM CurtailAtSnapshot WHERE FUEL_TYPE = ''SOLAR'')

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
        f.PSENSHIFTID AS PSENSHIFTID
    FROM InjectionFlow f
    LEFT JOIN ParInjectionFlow pf   ON pf.HOUR_START = f.HOUR_BUCKET
    LEFT JOIN DAMLimits d           ON d.HOUR_START = f.HOUR_BUCKET
    LEFT JOIN RTDynamicRating rt_dr ON rt_dr.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN RTConstraint r        ON r.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN WindImpact wi         ON wi.TIMESTAMP = f.TIMESTAMP
    LEFT JOIN SolarImpact si        ON si.TIMESTAMP = f.TIMESTAMP
    WHERE NOT EXISTS (
        SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS existing
        WHERE existing.CONFIG_ID = :P_CONFIG_ID AND existing.TIMESTAMP = f.TIMESTAMP
    );

    v_rows_inserted := SQLROWCOUNT;

    -- 4b. Every contingency binding on the branch at the same intervals -> FAST_SCAN_RT_CONSTRAINTS
    CALL FLOW_ANALYSIS.SP_LOAD_FAST_SCAN_RT_CONSTRAINTS(:P_CONFIG_ID, :v_actual_start, :v_actual_end, :P_ISO_MARKET_ID);

    -- 5. coverage check
    SELECT COUNT(*) INTO :v_hours_missing
      FROM TMP_VAL_MEMBER_HOURS mh
     WHERE NOT EXISTS (SELECT 1 FROM FLOW_ANALYSIS.FAST_SCAN_RESULTS x
                        WHERE x.CONFIG_ID = :P_CONFIG_ID
                          AND DATE_TRUNC(''HOUR'', DATEADD(''MINUTE'', 30, x.TIMESTAMP)) = mh.TS);

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
