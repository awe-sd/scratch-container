-- ============================================================================
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION
--
-- Station net injection per voltage level, from SE branch flow data.
-- Target: AW.DBO.ERCOTSTATIONINJECTION, grain (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL)
--
-- DEPENDS ON the three objects built by build_ercot_xfmr_winding_map.sql:
--     AWDEV.ERCOTRT.ERCOTCIMEFFECTIVE       timestamp -> CIM model in force
--     AWDEV.ERCOTRT.ERCOTSEXFMRENDNAMEFIX   hand-maintained corrected winding
--                                            names (the only hand-maintained
--                                            object in this pipeline)
--     AWDEV.ERCOTRT.ERCOTSEXFMRWINDINGMAP   CIM model + device -> each real
--                                            winding of its transformer
-- All CIM-version and winding-name handling lives in those objects. Rebuild
-- the views when ERCOT publishes a new CIM model (they're pure derivations,
-- so in practice nothing needs rebuilding - just CREATE OR REPLACE to pick up
-- new source rows); extend the fix table only when verification F there flags
-- a new device.
--
-- ---------------------------------------------------------------------------
-- ATTRIBUTION RULE
--
-- Every branch terminal is attributed to the bus it physically touches, signed
-- positive when flowing FROM that bus INTO the branch. Summing per
-- (station, kV) gives net injection at that bus: positive = net source, which is
-- where generation becomes visible.
--
--   Line, station is the FROM end       ->  FROMMW  at the line's KVLEVEL
--   Line, station is the TO end         ->  TOMW    at the line's KVLEVEL
--   Transformer, reported terminal      ->  FROMMW  at the device's own KVLEVEL
--   Transformer, other real winding     -> -FROMMW  at that winding's NOMINALKV
--
-- The transformer mirror is what makes generation visible. ERCOT reports flow on
-- only one winding and expects the other to be equal and opposite; verified over
-- 2026-01-01..2026-07-25 that no transformer ever reports both sides
-- (281,126 timestamp/transformer pairs, always exactly one).
--
-- The reported terminal is read straight off ISOERCOTSEBRANCHDEVICE, not off
-- the map - so a transformer that fails to resolve in the winding map (e.g. a
-- brand-new device before the winding table catches up) still contributes its
-- reported side and only loses the mirror; the old design dropped it entirely.
-- Star-equivalent legs (one real winding, equal to the device's own kV)
-- naturally produce no mirror row.
--
-- The mirror leg needs no uniqueness guard here: ERCOTSEXFMRWINDINGMAP is a
-- strict name+kV join, so it is verified (build script, verification D) that
-- no (model, device) pair ever has more than one distinct NOMINALKV differing
-- from DEVICEKV. That situation cannot occur within a device's active window;
-- it was only ever an artifact of pairing a device with a model from before
-- the device existed.
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
-- A transformer whose BOTH sides are reported as devices (GARZA
--   1_138_1_H/1_69_1_H, MDLNE AXFMR1H/AXFMR1L) is deliberately left unmapped:
--   mirroring either side would double count, and both reported sides already
--   give the right answer between them.
-- ============================================================================

CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION(
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
        SELECT BRANCHDEVICEID, "TIMESTAMP", FROMMW, TOMW
        FROM AW.DBO.ISOERCOTSEBRANCH
        WHERE "TIMESTAMP" >= :P_START_DATE
          AND "TIMESTAMP" <  DATEADD(DAY, 1, :P_END_DATE)
    ),
    ldev AS (
        SELECT BRANCHDEVICEID, FROMSTATIONNAME, TOSTATIONNAME, CAST(KVLEVEL AS NUMBER(6,2)) AS KVLEVEL
        FROM AW.DBO.ISOERCOTSEBRANCHDEVICE WHERE BRANCHDEVICETYPE = 'Line'
    ),
    xdev AS (
        SELECT BRANCHDEVICEID, FROMSTATIONNAME AS STATION, CAST(KVLEVEL AS NUMBER(6,2)) AS KVLEVEL
        FROM AW.DBO.ISOERCOTSEBRANCHDEVICE WHERE BRANCHDEVICETYPE = 'Transformer'
    ),
    terminals AS (
        -- line, from end
        SELECT br."TIMESTAMP", l.FROMSTATIONNAME AS STATIONNAME, l.KVLEVEL, ZEROIFNULL(br.FROMMW) AS MW
        FROM br JOIN ldev l ON l.BRANCHDEVICEID = br.BRANCHDEVICEID
        UNION ALL
        -- line, to end
        SELECT br."TIMESTAMP", l.TOSTATIONNAME, l.KVLEVEL, ZEROIFNULL(br.TOMW)
        FROM br JOIN ldev l ON l.BRANCHDEVICEID = br.BRANCHDEVICEID
        UNION ALL
        -- transformer, the winding ERCOT reports: at the device's own kV
        SELECT br."TIMESTAMP", x.STATION, x.KVLEVEL, ZEROIFNULL(br.FROMMW)
        FROM br JOIN xdev x ON x.BRANCHDEVICEID = br.BRANCHDEVICEID
        UNION ALL
        -- transformer, the other real winding: equal and opposite
        SELECT br."TIMESTAMP", m.STATION, m.NOMINALKV, -ZEROIFNULL(br.FROMMW)
        FROM br
        JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVE e
          ON br."TIMESTAMP" >= e.EFFECTIVE_FROM AND br."TIMESTAMP" < e.EFFECTIVE_TO
        JOIN AWDEV.ERCOTRT.ERCOTSEXFMRWINDINGMAP m
          ON m.CIMFILEID      = e.CIMFILEID
         AND m.BRANCHDEVICEID = br.BRANCHDEVICEID
        WHERE ABS(m.NOMINALKV - m.DEVICEKV) > 0.05
    )
    SELECT CAST("TIMESTAMP" AS TIMESTAMP_NTZ(0)) AS "TIMESTAMP",
           STATIONNAME AS NMMSSTATIONCODE, KVLEVEL,
           CAST(NULL AS FLOAT) AS GENMW, CAST(NULL AS FLOAT) AS WITHDRAWMW,
           SUM(MW) AS NETINJECTIONMW
    FROM terminals
    WHERE STATIONNAME IS NOT NULL AND KVLEVEL IS NOT NULL
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
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2022-01-31');
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2026-07-01', '2026-07-24');


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
-- Any transformer flow NOT covered by the map on a loaded day. Should be 0 or
-- a short, stable list (see verification F in the build script for the
-- expected residual); if it's growing, extend the fix table.
--
-- SELECT COUNT(*) AS UNMAPPED_XFMR_ROWS
-- FROM AW.DBO.ISOERCOTSEBRANCH b
-- JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE d
--   ON d.BRANCHDEVICEID = b.BRANCHDEVICEID AND d.BRANCHDEVICETYPE = 'Transformer'
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVE e
--   ON b."TIMESTAMP" >= e.EFFECTIVE_FROM AND b."TIMESTAMP" < e.EFFECTIVE_TO
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTSEXFMRWINDINGMAP m
--   ON m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = b.BRANCHDEVICEID
-- WHERE b."TIMESTAMP" >= '2026-07-01' AND b."TIMESTAMP" < '2026-07-02'
--   AND b.FROMMW IS NOT NULL
--   AND m.BRANCHDEVICEID IS NULL;
