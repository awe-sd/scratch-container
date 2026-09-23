-- ============================================================================
-- AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION
--
-- Station net injection per voltage level, from SE branch flow data.
-- Target: AW.DBO.ERCOTSTATIONINJECTION, grain (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL)
--
-- DEPENDS ON two static mapping tables, built by
-- build_ercot_xfmr_winding_map.sql:
--     AW.DBO.ERCOTCIMEFFECTIVE       date -> CIM model in force
--     AW.DBO.ERCOTSEXFMRWINDINGMAP   CIM model + device -> REPORTED_KV, MIRROR_KV
-- All CIM-version and winding-name handling lives in those tables and their
-- build script. Rebuild them when ERCOT publishes a new CIM model.
--
-- ---------------------------------------------------------------------------
-- ATTRIBUTION RULE
--
-- Every branch terminal is attributed to the bus it physically touches, signed
-- positive when flowing FROM that bus INTO the branch. Summing per
-- (station, kV) gives net injection at that bus: positive = net source, which is
-- where generation becomes visible.
--
--   Line, station is the FROM end   ->  FROMMW  at the line's KVLEVEL
--   Line, station is the TO end     ->  TOMW    at the line's KVLEVEL
--   Transformer, reported winding   ->  FROMMW  at map.REPORTED_KV
--   Transformer, opposite winding   -> -FROMMW  at map.MIRROR_KV
--
-- The transformer mirror is what makes generation visible. ERCOT reports flow on
-- only one winding and expects the other to be equal and opposite; verified over
-- 2026-01-01..2026-07-25 that no transformer ever reports both sides
-- (281,126 timestamp/transformer pairs, always exactly one).
--
-- Result at 2026-07-01 12:57:
--     STP      345   ->    -2.00   bus balances, nothing connected at 345
--     STP       25   -> +2604.60   GENERATION, via the mirror
--     CPSES     22   -> +2405.60   generation
--     GUADG   18.1   ->  +939.98   generation
--     LEG       25   ->  +679.22   generation
--     CBY    20, 24  ->  +678.83, +520.26
--     HRZN_SLR 34.5  ->  +197.21   solar generation
--     SUN_SLR  34.5  ->  +175.33   solar generation
--     ACSSW    345   ->    -0.01   switchyard, balances to ~0 as it should
--
-- TRANSFORMER LOSSES ARE NOT ATTRIBUTED. The mirror is exactly -FROMMW, i.e. a
-- lossless transformer per ERCOT's convention, so the two sides cancel and
-- winding losses land nowhere. Summing across KVLEVEL therefore gives the
-- station-level figure MINUS those losses, a few MW per station:
--     STATION   SUM OVER KV   STATION-LEVEL   DIFF
--     STP           2602.60         2604.11  -1.51
--     CPSES         2376.28         2380.06  -3.78
--     CBY           1195.86         1198.36  -2.50
-- The old ERCOTSTATIONLOAD attributed these losses to the station, because it
-- summed FROMMW + TOMW per transformer. Expect small differences on that basis.
--
-- NOTE ON THE LINE COLUMN CHOICE - this differs from the original spec, which
--   asked for the FAR-end terminal ("injection at B = A-B FROMMW + B-C TOMW"),
--   giving power ARRIVING at B. That is self-consistent alone but cannot combine
--   with transformer FROMMW, which has the opposite sign convention: at STP 345
--   it gives lines -2567.31 plus transformers -2604.60 = -5171.91, a balance of
--   nothing. Since FROMMW + TOMW = losses on any branch, far-end is simply the
--   negation of near-end, so this is purely a sign convention. Near-end is used
--   because it makes generation read POSITIVE at the generator bus and keeps
--   WITHDRAWMW's original meaning from ERCOTSTATIONLOAD.
--   To flip to inflow-positive, negate the four MW terms in `terminals`.
--
-- ---------------------------------------------------------------------------
-- OTHER NOTES
--
-- GENMW and WITHDRAWMW are left NULL; only NETINJECTIONMW is solved for.
-- TIMESTAMP is kept at full source resolution. SE timestamps are irregular -
--   :57 recently, :58 in 2021-2022, occasionally on the hour - so anything
--   downstream deriving an hour bucket must not assume a fixed minute.
-- Nothing is deleted when the source range is empty. Delete and insert run in
--   one transaction after staging.
-- Backfill from 2022-01-01. There is no winding data before then (earliest
--   usable CIMDATE is 2022-01-04).
-- Call with WIDE date ranges. ISOERCOTSEBRANCH is 563M rows clustered by
--   branchDeviceID, not timestamp, so a single day still touches 13-49% of
--   partitions. A month per call costs little more than a day.
-- ============================================================================

CREATE OR REPLACE PROCEDURE AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION(
    P_START_DATE DATE,
    P_END_DATE   DATE
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    v_out_rows INTEGER DEFAULT 0;
    v_deleted  INTEGER DEFAULT 0;
BEGIN
    IF (P_START_DATE IS NULL OR P_END_DATE IS NULL) THEN
        RETURN 'ERROR: P_START_DATE and P_END_DATE are both required.';
    END IF;

    IF (P_START_DATE > P_END_DATE) THEN
        RETURN 'ERROR: P_START_DATE (' || :P_START_DATE::VARCHAR ||
               ') is after P_END_DATE (' || :P_END_DATE::VARCHAR || ').';
    END IF;

    CREATE OR REPLACE TEMPORARY TABLE TMP_STATION_INJECTION AS
    WITH br AS (
        SELECT BRANCHDEVICEID, "TIMESTAMP",
               CAST("TIMESTAMP" AS DATE) AS D,
               FROMMW, TOMW
        FROM AW.DBO.ISOERCOTSEBRANCH
        WHERE "TIMESTAMP" >= :P_START_DATE
          AND "TIMESTAMP" <  DATEADD(DAY, 1, :P_END_DATE)
    ),
    ldev AS (
        SELECT BRANCHDEVICEID, FROMSTATIONNAME, TOSTATIONNAME, KVLEVEL
        FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
        WHERE BRANCHDEVICETYPE = 'Line'
    ),
    -- one row per branch device per timestamp, with that date's winding map
    xfmr AS (
        SELECT br."TIMESTAMP", m.STATION, m.REPORTED_KV, m.MIRROR_KV,
               ZEROIFNULL(br.FROMMW) AS FROMMW
        FROM br
        JOIN AW.DBO.ERCOTCIMEFFECTIVE e
          ON br.D BETWEEN e.EFFECTIVE_FROM AND e.EFFECTIVE_THROUGH
        JOIN AW.DBO.ERCOTSEXFMRWINDINGMAP m
          ON m.CIMFILEID      = e.CIMFILEID
         AND m.BRANCHDEVICEID = br.BRANCHDEVICEID
    ),
    terminals AS (
        -- line, from end
        SELECT br."TIMESTAMP",
               d.FROMSTATIONNAME              AS STATIONNAME,
               CAST(d.KVLEVEL AS NUMBER(6,2)) AS KVLEVEL,
               ZEROIFNULL(br.FROMMW)          AS MW
        FROM br JOIN ldev d ON d.BRANCHDEVICEID = br.BRANCHDEVICEID
        WHERE d.FROMSTATIONNAME IS NOT NULL
        UNION ALL
        -- line, to end
        SELECT br."TIMESTAMP",
               d.TOSTATIONNAME,
               CAST(d.KVLEVEL AS NUMBER(6,2)),
               ZEROIFNULL(br.TOMW)
        FROM br JOIN ldev d ON d.BRANCHDEVICEID = br.BRANCHDEVICEID
        WHERE d.TOSTATIONNAME IS NOT NULL
        UNION ALL
        -- transformer, the winding ERCOT reports
        SELECT "TIMESTAMP", STATION, REPORTED_KV, FROMMW
        FROM xfmr
        UNION ALL
        -- transformer, the opposite winding: equal and opposite
        SELECT "TIMESTAMP", STATION, MIRROR_KV, -FROMMW
        FROM xfmr
        WHERE MIRROR_KV IS NOT NULL
    )
    SELECT
        CAST("TIMESTAMP" AS TIMESTAMP_NTZ(0)) AS "TIMESTAMP",
        STATIONNAME                           AS NMMSSTATIONCODE,
        KVLEVEL                               AS KVLEVEL,
        CAST(NULL AS FLOAT)                   AS GENMW,
        CAST(NULL AS FLOAT)                   AS WITHDRAWMW,
        SUM(MW)                               AS NETINJECTIONMW
    FROM terminals
    WHERE STATIONNAME IS NOT NULL
      AND KVLEVEL     IS NOT NULL
    GROUP BY "TIMESTAMP", STATIONNAME, KVLEVEL;

    v_out_rows := (SELECT COUNT(*) FROM TMP_STATION_INJECTION);

    IF (v_out_rows = 0) THEN
        RETURN 'No SE branch data for ' || :P_START_DATE::VARCHAR || ' .. ' ||
               :P_END_DATE::VARCHAR || '. Target left unchanged.';
    END IF;

    BEGIN TRANSACTION;

        DELETE FROM AW.DBO.ERCOTSTATIONINJECTION
        WHERE "TIMESTAMP" >= :P_START_DATE
          AND "TIMESTAMP" <  DATEADD(DAY, 1, :P_END_DATE);

        v_deleted := SQLROWCOUNT;

        INSERT INTO AW.DBO.ERCOTSTATIONINJECTION
            ("TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, GENMW, WITHDRAWMW, NETINJECTIONMW)
        SELECT "TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, GENMW, WITHDRAWMW, NETINJECTIONMW
        FROM TMP_STATION_INJECTION;

    COMMIT;

    RETURN 'OK ' || :P_START_DATE::VARCHAR || ' .. ' || :P_END_DATE::VARCHAR ||
           ': deleted ' || v_deleted::VARCHAR ||
           ', inserted ' || v_out_rows::VARCHAR || '.';

EXCEPTION
    WHEN OTHER THEN
        ROLLBACK;
        RAISE;
END;
$$;


-- ===========================================================================
-- Usage
-- ===========================================================================
--   CALL AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2022-01-31');
--   CALL AW.DBO.SP_LOAD_ERCOT_STATION_INJECTION('2026-07-01', '2026-07-24');


-- ===========================================================================
-- Verification: generation must be visible at generator voltages.
-- STP ~ +2604 at 25 kV, CPSES ~ +2405 at 22 kV, solar farms positive at 34.5 kV.
-- If these read ~0, the transformer mirror did not fire - check that
-- ERCOTSEXFMRWINDINGMAP and ERCOTCIMEFFECTIVE cover the dates loaded.
-- Note 2022-era timestamps are stamped :58, recent ones :57.
-- ===========================================================================
-- SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2) AS NETINJECTIONMW
-- FROM AW.DBO.ERCOTSTATIONINJECTION
-- WHERE "TIMESTAMP" = '2026-07-01 12:57:00'
--   AND NMMSSTATIONCODE IN ('STP','CPSES','HRZN_SLR','ACSSW')
-- ORDER BY NMMSSTATIONCODE, KVLEVEL;
--
-- Largest injections account-wide should be generating stations at machine
-- voltages (18-25 kV), not transmission buses:
--
-- SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2) AS NETINJECTIONMW
-- FROM AW.DBO.ERCOTSTATIONINJECTION
-- WHERE "TIMESTAMP" = '2026-07-01 12:57:00'
-- ORDER BY NETINJECTIONMW DESC
-- LIMIT 25;
--
-- Any transformer flow NOT covered by the map on a loaded day. Should be 0;
-- if not, rebuild the mapping tables.
--
-- SELECT COUNT(*) AS UNMAPPED_XFMR_ROWS
-- FROM AW.DBO.ISOERCOTSEBRANCH b
-- JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE d
--   ON d.BRANCHDEVICEID = b.BRANCHDEVICEID AND d.BRANCHDEVICETYPE = 'Transformer'
-- LEFT JOIN AW.DBO.ERCOTCIMEFFECTIVE e
--   ON CAST(b."TIMESTAMP" AS DATE) BETWEEN e.EFFECTIVE_FROM AND e.EFFECTIVE_THROUGH
-- LEFT JOIN AW.DBO.ERCOTSEXFMRWINDINGMAP m
--   ON m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = b.BRANCHDEVICEID
-- WHERE b."TIMESTAMP" >= '2026-07-01' AND b."TIMESTAMP" < '2026-07-02'
--   AND b.FROMMW IS NOT NULL
--   AND m.BRANCHDEVICEID IS NULL;
