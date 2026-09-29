-- ============================================================================
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2
--
-- Station net injection per voltage level, from SE branch flow data.
-- Target: AW.DBO.ERCOTSTATIONINJECTION, grain (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL)
--
-- DEPENDS ON (build_ercot_transformer_winding_map.sql):
--   AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE            timestamp -> CIM model in force
--   AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING hand-maintained winding-name fixes
--   AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP     CIM model + device -> each real winding
--
-- ATTRIBUTION (signed positive flowing FROM the bus INTO the branch):
--   Line, FROM end                   -> FROMMW at the line's KVLEVEL
--   Line, TO end                     -> TOMW   at the line's KVLEVEL
--   Transformer, reported terminal   -> FROMMW at the device's KVLEVEL, re-keyed below 69 kV
--   Transformer, other real winding  -> TOMW   at that winding's NOMINALKV, re-keyed below 69 kV
--
-- SUB-69 kV RE-KEY: a terminal under 69 kV moves to the transformer's transmission-side kV.
--   mapped (2 real windings)          -> re-key to the other winding's kV
--   single real winding               -> re-key via the CIM star bus its bank's real legs share
--   0 or 2+ transmission-kV siblings  -> left alone (no transmission leg / ambiguous tertiary)
--   PARs excluded (AW.DBO.PARERCOTSTATION); losses land in the transmission cell
--
-- No windings loaded for the in-force CIM model -> falls back to the latest earlier model that does.
--
-- Rebuild: CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2022-01-01', '2026-07-25');
-- ============================================================================
CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2(P_START_DATE DATE, P_END_DATE DATE)
RETURNS VARCHAR LANGUAGE SQL EXECUTE AS CALLER
AS
$$
DECLARE
    v_end TIMESTAMP_NTZ; v_devices INTEGER; v_deleted INTEGER DEFAULT 0; v_inserted INTEGER DEFAULT 0;
BEGIN
    IF (P_START_DATE IS NULL OR P_END_DATE IS NULL OR P_START_DATE > P_END_DATE) THEN RETURN 'ERROR: need non-null P_START_DATE <= P_END_DATE.'; END IF;
    v_end := DATEADD(DAY, 1, P_END_DATE);

    -- The only scan of ISOERCOTSEBRANCH, padded -30min for the :57-stamped-to-next-hour convention.
    CREATE OR REPLACE TEMPORARY TABLE TMP_FLOW AS
    SELECT BRANCHDEVICEID, "TIMESTAMP", FROMMW, TOMW FROM AW.DBO.ISOERCOTSEBRANCH
    WHERE "TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ) AND "TIMESTAMP" < DATEADD(MINUTE, -30, :v_end);

    -- One snapshot per hour bucket: most complete, latest on ties; skip buckets under half the devices.
    SELECT COUNT(*) INTO :v_devices FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE DATEACTIVESTART < :v_end AND DATEACTIVEEND >= :P_START_DATE;
    CREATE OR REPLACE TEMPORARY TABLE TMP_SNAPSHOT AS
    SELECT "TIMESTAMP" FROM (SELECT "TIMESTAMP", COUNT(*) AS N FROM TMP_FLOW GROUP BY "TIMESTAMP")
    QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC('HOUR', DATEADD(MINUTE, 30, "TIMESTAMP")) ORDER BY N DESC, "TIMESTAMP" DESC) = 1
        AND N >= 0.5 * :v_devices;

    IF ((SELECT COUNT(*) FROM TMP_SNAPSHOT) = 0) THEN
        RETURN 'OK: no usable SE snapshots for ' || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR || ', target untouched.'; END IF;
    BEGIN TRANSACTION;
    DELETE FROM AW.DBO.ERCOTSTATIONINJECTION
    WHERE "TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ) AND "TIMESTAMP" < DATEADD(MINUTE, -30, :v_end);
    v_deleted := SQLROWCOUNT;

    -- One row per (device, terminal): where the flow is booked, which MW column, and when it applies.
    INSERT INTO AW.DBO.ERCOTSTATIONINJECTION ("TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, NETINJECTIONMW)
    WITH MIRROR AS (   -- the transformer's other real winding, per the CIM model in force (with fallback)
        SELECT m.BRANCHDEVICEID, m.STATION, m.DEVICEKV, m.NOMINALKV AS MIRRORKV, w.EFFECTIVE_FROM, w.EFFECTIVE_TO
        FROM (
            SELECT EFFECTIVE_FROM, EFFECTIVE_TO, LAST_VALUE(WINDING_CIMFILEID) IGNORE NULLS
                       OVER (ORDER BY EFFECTIVE_FROM ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CIMFILEID
            FROM (
                SELECT e.EFFECTIVE_FROM, e.EFFECTIVE_TO, MAX(IFF(w.CIMFILEID IS NULL, NULL, e.CIMFILEID)) AS WINDING_CIMFILEID
                FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
                LEFT JOIN (SELECT DISTINCT CIMFILEID FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING) w ON w.CIMFILEID = e.CIMFILEID
                GROUP BY e.EFFECTIVE_FROM, e.EFFECTIVE_TO
            )
        ) w
        JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m ON m.CIMFILEID = w.CIMFILEID
        WHERE ABS(m.NOMINALKV - m.DEVICEKV) > 0.05
    ),
    REKEY_TARGET AS (   -- reported-leg re-key target: mirror-based, then star-based, one row per device
        SELECT BRANCHDEVICEID, MAX(MIRRORKV) AS TARGETKV FROM MIRROR WHERE DEVICEKV < 69 AND MIRRORKV >= 69 GROUP BY BRANCHDEVICEID
        UNION ALL
        SELECT c.BRANCHDEVICEID, MAX(sk.REALKV)
        FROM (
            SELECT CIMFILEID, BRANCHDEVICEID, STATION, TRANSFORMERNAME
            FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m1
            WHERE DEVICEKV < 69
              AND NOT EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m2
                              WHERE m2.CIMFILEID = m1.CIMFILEID AND m2.BRANCHDEVICEID = m1.BRANCHDEVICEID AND ABS(m2.NOMINALKV - m2.DEVICEKV) > 0.05)
            GROUP BY CIMFILEID, BRANCHDEVICEID, STATION, TRANSFORMERNAME
            HAVING MAX(NOMINALKV) < 69
        ) c
        JOIN (   -- real (>= 69 kV) windings of every leg sharing a device's CIM star bus
            SELECT DISTINCT s.CIMFILEID, s.STATION, s.TRANSFORMERNAME, CAST(rw.NOMINALKV AS NUMBER(6,2)) AS REALKV
            FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING s
            JOIN AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING sib ON sib.CIMFILEID = s.CIMFILEID AND sib.STATION = s.STATION AND sib.FROMNUM = s.FROMNUM AND sib.NOMINALKV = 1
            JOIN AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING rw ON rw.CIMFILEID = sib.CIMFILEID AND rw.STATION = sib.STATION AND rw.TRANSFORMERNAME = sib.TRANSFORMERNAME AND rw.NOMINALKV >= 69
            WHERE s.NOMINALKV = 1
        ) sk ON sk.CIMFILEID = c.CIMFILEID AND sk.STATION = c.STATION AND sk.TRANSFORMERNAME = c.TRANSFORMERNAME
        GROUP BY c.BRANCHDEVICEID
        HAVING COUNT(DISTINCT sk.REALKV) = 1
    ),
    TERMINAL AS (   -- FROMMW at the from-station (line, or re-keyed transformer terminal); TOMW at the to-station/mirror
        SELECT d.BRANCHDEVICEID, d.FROMSTATIONNAME AS STATIONNAME, CAST(COALESCE(r.TARGETKV, d.KVLEVEL) AS NUMBER(6,2)) AS KVLEVEL,
               TRUE AS USE_FROMMW, '1900-01-01'::TIMESTAMP_NTZ AS EFFECTIVE_FROM, '9999-12-31'::TIMESTAMP_NTZ AS EFFECTIVE_TO
        FROM AW.DBO.ISOERCOTSEBRANCHDEVICE d
        LEFT JOIN REKEY_TARGET r ON r.BRANCHDEVICEID = d.BRANCHDEVICEID
        WHERE d.BRANCHDEVICETYPE IN ('Line', 'Transformer')
          AND NOT EXISTS (SELECT 1 FROM AW.DBO.PARERCOTSTATION p WHERE p.STATION = d.FROMSTATIONNAME AND p.TRANSFORMERENDNAME = d.TRANSFORMERENDNAME)
        UNION ALL
        SELECT BRANCHDEVICEID, TOSTATIONNAME, CAST(KVLEVEL AS NUMBER(6,2)), FALSE, '1900-01-01', '9999-12-31'
        FROM AW.DBO.ISOERCOTSEBRANCHDEVICE WHERE BRANCHDEVICETYPE = 'Line'
        UNION ALL
        SELECT BRANCHDEVICEID, STATION, IFF(MIRRORKV < 69 AND DEVICEKV >= 69, DEVICEKV, MIRRORKV), FALSE, EFFECTIVE_FROM, EFFECTIVE_TO FROM MIRROR
    )
    SELECT CAST(br."TIMESTAMP" AS TIMESTAMP_NTZ(0)), t.STATIONNAME, t.KVLEVEL, SUM(ZEROIFNULL(IFF(t.USE_FROMMW, br.FROMMW, br.TOMW)))
    FROM TMP_FLOW br
    JOIN TMP_SNAPSHOT s ON s."TIMESTAMP" = br."TIMESTAMP"
    JOIN TERMINAL t ON t.BRANCHDEVICEID = br.BRANCHDEVICEID AND br."TIMESTAMP" >= t.EFFECTIVE_FROM AND br."TIMESTAMP" < t.EFFECTIVE_TO
    GROUP BY 1, 2, 3
    ORDER BY 1, 2, 3;   -- target clusters on (date, station)
    v_inserted := SQLROWCOUNT;
    COMMIT;

    RETURN 'OK: ' || v_deleted || ' rows deleted, ' || v_inserted || ' rows inserted for ' || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR;

EXCEPTION
    WHEN OTHER THEN ROLLBACK; RAISE;
END;
$$;

-- ===========================================================================
-- Usage
-- ===========================================================================
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2022-01-01', '2022-01-31');
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2022-01-01', '2026-07-25');

-- ===========================================================================
-- Verification
-- ===========================================================================
-- Transmission-cell spot check (~0 means the mirror/re-key did not fire):
-- SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2) AS NETINJECTIONMW
-- FROM AW.DBO.ERCOTSTATIONINJECTION
-- WHERE "TIMESTAMP" = '2026-06-23 13:57:00'
--   AND NMMSSTATIONCODE IN ('STP','CPSES','HRZN_SLR','SUN_SLR','BRAUNIG','BOSQUESW')
-- ORDER BY NMMSSTATIONCODE, KVLEVEL;
--
-- Transformer flow not covered by the map on a loaded day (expect 0, or see build script verification F):
-- SELECT COUNT(*) AS UNMAPPED_TRANSFORMER_ROWS
-- FROM AW.DBO.ISOERCOTSEBRANCH b
-- JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE d ON d.BRANCHDEVICEID = b.BRANCHDEVICEID AND d.BRANCHDEVICETYPE = 'Transformer'
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e ON b."TIMESTAMP" >= e.EFFECTIVE_FROM AND b."TIMESTAMP" < e.EFFECTIVE_TO
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m ON m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = b.BRANCHDEVICEID
-- WHERE b."TIMESTAMP" >= '2026-07-01' AND b."TIMESTAMP" < '2026-07-02' AND b.FROMMW IS NOT NULL AND m.BRANCHDEVICEID IS NULL;
