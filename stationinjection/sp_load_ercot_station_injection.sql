-- ============================================================================
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION
--
-- Station net injection per voltage level, from SE branch flow data.
-- Target: AW.DBO.ERCOTSTATIONINJECTION, grain (TIMESTAMP, NMMSSTATIONCODE, KVLEVEL)
--
-- DEPENDS ON the three objects built by build_ercot_transformer_winding_map.sql:
--     AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE       timestamp -> CIM model in force
--     AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING   hand-maintained corrected winding
--                                            names (the only hand-maintained
--                                            object in this pipeline)
--     AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP   CIM model + device -> each real
--                                            winding of its transformer
-- All CIM-version and winding-name handling lives in those objects. Rebuild
-- the views when ERCOT publishes a new CIM model (they're pure derivations,
-- so in practice nothing needs rebuilding - just CREATE OR REPLACE to pick up
-- new source rows); extend the name-correcting table only when verification F there flags
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
--   Transformer, other real winding     ->  TOMW    at that winding's NOMINALKV
--
-- These four rules are materialized ONCE per call as the TMP_TERMINAL dimension
-- and joined ONCE to the flow table (see PERFORMANCE / BULK LOADING below) -
-- the rules themselves are unchanged from the original 4-leg UNION ALL design.
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
-- The mirror leg needs no uniqueness guard here: ERCOTSETRANSFORMERWINDINGMAP is a
-- strict name+kV join, so it is verified (build script, verification D) that
-- no (model, device) pair ever has more than one distinct NOMINALKV differing
-- from DEVICEKV. That situation cannot occur within a device's active window;
-- it was only ever an artifact of pairing a device with a model from before
-- the device existed.
--
-- If the in-force CIM model has no windings loaded (e.g. 393 = 2023Mar.L5, and
-- all models from 2026-07-29 on as of 2026-09-24), the mirror falls back to
-- the latest earlier model with windings; without this the whole range loses
-- generation visibility and low-side-reported GSUs double-count. After
-- loading windings for such a model, re-run the proc over its range.
--
-- Result at 2026-07-01 12:57:
--     STP      345   ->    -2.00   bus balances, nothing connected at 345
--     STP       25   -> +2606.10   GENERATION, via the mirror
--     CPSES     22   -> +2409.38   generation
--     GUADG   18.1   ->  +941.93   generation
--     LEG       25   ->  +679.65   generation
--     CBY    20, 24  ->  +681.09, +520.57
--     HRZN_SLR 34.5  ->  +197.21   solar generation
--     SUN_SLR  34.5  ->  +175.33   solar generation
--     ACSSW    345   ->    -0.01   switchyard, balances to ~0 as it should
--
-- TRANSFORMER LOSSES ARE ATTRIBUTED. The mirror uses TOMW (not -FROMMW), and
-- TOMW = -FROMMW + losses, so FROMMW + TOMW = losses shows up as a small
-- station-level imbalance across kV levels, the same as it does for lines.
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
--   To flip to inflow-positive, negate the MW expression in the INSERT's SUM.
--
-- ---------------------------------------------------------------------------
-- PERFORMANCE / BULK LOADING
--
-- ISOERCOTSEBRANCH (563M rows, 12 GB) is clustered by BRANCHDEVICEID, not
-- TIMESTAMP: a 1-day range scans 6.0 GB, a 1-month range scans 8.8 GB - each
-- call pays a near-fixed scan cost, so bulk loads want FEW LARGE calls, not
-- many small ones. TMP_TERMINAL (the four rules above) is built ONCE per call
-- and joined ONCE to the flow table, replacing an earlier 4-leg UNION ALL that
-- Snowflake inlined into 4 separate scans (proven identical output, 1.5-2.8x
-- faster). Daily incremental: CALL ...(d, d). Backfill: as few calls as
-- possible on a LARGE+ warehouse - e.g. one call per year with
-- P_CHUNK_DAYS = 0, or one call for the whole range with P_CHUNK_DAYS = 365
-- for per-year commits/restartability.
--
-- ---------------------------------------------------------------------------
-- OTHER NOTES
--
-- GENMW and WITHDRAWMW are left NULL; only NETINJECTIONMW is solved for.
-- TIMESTAMP is kept at full source resolution. SE timestamps are irregular -
--   :57 recently, :58 in 2021-2022, occasionally on the hour - so anything
--   downstream deriving an hour bucket must not assume a fixed minute.
-- Each chunk's DELETE+INSERT runs in one transaction; an empty source range
--   leaves the target untouched (per chunk) - see P_CHUNK_DAYS above for
--   controlling blast radius on a backfill.
-- Backfill from 2022-01-01. There is no winding data before then (earliest
--   usable CIMDATE is 2022-01-04).
-- A transformer whose BOTH sides are reported as devices (GARZA
--   1_138_1_H/1_69_1_H, MDLNE AXFMR1H/AXFMR1L) is deliberately left unmapped:
--   mirroring either side would double count, and both reported sides already
--   give the right answer between them.
-- A period whose in-force model has no winding rows loaded yet gets reported
--   transformer terminals but no mirrors (generation behind GSUs reads ~0 at
--   the transmission bus and is absent at machine kV) - check verification I
--   in the build script before trusting recent months.
-- ============================================================================

-- Signature changed (3rd arg): procedures are keyed by name+argtypes, so
-- CREATE OR REPLACE here adds a new (DATE, DATE, INTEGER) overload rather than
-- replacing an existing (DATE, DATE) one. Drop the old overload once so a
-- 2-arg CALL can't resolve to it (or be ambiguous against the defaulted arg):
--   DROP PROCEDURE IF EXISTS AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION(DATE, DATE);
CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION(
    P_START_DATE DATE,
    P_END_DATE   DATE,
    P_CHUNK_DAYS INTEGER DEFAULT 0   -- <= 0: whole range in one transaction; N: commit every N days
)
RETURNS VARCHAR
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    v_from     DATE;
    v_to       DATE;
    v_step     INTEGER;
    v_deleted  INTEGER DEFAULT 0;
    v_inserted INTEGER DEFAULT 0;
BEGIN
    IF (P_START_DATE IS NULL OR P_END_DATE IS NULL OR P_START_DATE > P_END_DATE) THEN
        RETURN 'ERROR: need non-null P_START_DATE <= P_END_DATE.';
    END IF;

    -- One row per (device, terminal): where the flow is booked, which MW column, and when the row applies.
    CREATE OR REPLACE TEMPORARY TABLE TMP_TERMINAL AS
    -- FROMMW at the from-station: a line's from end, or the winding ERCOT reports on a transformer
    SELECT BRANCHDEVICEID, FROMSTATIONNAME AS STATIONNAME, CAST(KVLEVEL AS NUMBER(6,2)) AS KVLEVEL,
           TRUE AS USE_FROMMW, '1900-01-01'::TIMESTAMP_NTZ AS EFFECTIVE_FROM, '9999-12-31'::TIMESTAMP_NTZ AS EFFECTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE WHERE BRANCHDEVICETYPE IN ('Line', 'Transformer')
    UNION ALL
    -- TOMW at the to-station: a line's to end
    SELECT BRANCHDEVICEID, TOSTATIONNAME, CAST(KVLEVEL AS NUMBER(6,2)), FALSE, '1900-01-01', '9999-12-31'
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE WHERE BRANCHDEVICETYPE = 'Line'
    UNION ALL
    -- TOMW at the transformer's other real winding, while that CIM model is in force.
    -- If the in-force model has no windings loaded yet, mirror with the latest earlier model that does.
    SELECT m.BRANCHDEVICEID, m.STATION, m.NOMINALKV, FALSE, e.EFFECTIVE_FROM, e.EFFECTIVE_TO
    FROM (
        SELECT EFFECTIVE_FROM, EFFECTIVE_TO,
               LAST_VALUE(WINDING_CIMFILEID) IGNORE NULLS
                   OVER (ORDER BY EFFECTIVE_FROM ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CIMFILEID
        FROM (
            SELECT e.EFFECTIVE_FROM, e.EFFECTIVE_TO,
                   MAX(IFF(w.CIMFILEID IS NULL, NULL, e.CIMFILEID)) AS WINDING_CIMFILEID
            FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
            LEFT JOIN (SELECT DISTINCT CIMFILEID FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING) w ON w.CIMFILEID = e.CIMFILEID
            GROUP BY e.EFFECTIVE_FROM, e.EFFECTIVE_TO
        )
    ) e
    JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m ON m.CIMFILEID = e.CIMFILEID
    WHERE ABS(m.NOMINALKV - m.DEVICEKV) > 0.05;

    v_from := P_START_DATE;
    v_step := IFF(P_CHUNK_DAYS > 0, P_CHUNK_DAYS, DATEDIFF(DAY, P_START_DATE, P_END_DATE) + 1);

    WHILE (v_from <= P_END_DATE) DO
        v_to := LEAST(DATEADD(DAY, v_step, v_from), DATEADD(DAY, 1, P_END_DATE));

        -- Staged first (DDL autocommits, so outside the transaction): an empty source range leaves the target untouched.
        CREATE OR REPLACE TEMPORARY TABLE TMP_STATION_INJECTION AS
        SELECT CAST(br."TIMESTAMP" AS TIMESTAMP_NTZ(0)) AS "TIMESTAMP", t.STATIONNAME AS NMMSSTATIONCODE, t.KVLEVEL,
               SUM(ZEROIFNULL(IFF(t.USE_FROMMW, br.FROMMW, br.TOMW))) AS NETINJECTIONMW
        FROM AW.DBO.ISOERCOTSEBRANCH br
        JOIN TMP_TERMINAL t ON t.BRANCHDEVICEID = br.BRANCHDEVICEID
                           AND br."TIMESTAMP" >= t.EFFECTIVE_FROM AND br."TIMESTAMP" < t.EFFECTIVE_TO
        WHERE br."TIMESTAMP" >= :v_from AND br."TIMESTAMP" < :v_to
        GROUP BY 1, 2, 3;

        IF ((SELECT COUNT(*) FROM TMP_STATION_INJECTION) > 0) THEN
            BEGIN TRANSACTION;
            DELETE FROM AW.DBO.ERCOTSTATIONINJECTION WHERE "TIMESTAMP" >= :v_from AND "TIMESTAMP" < :v_to;
            v_deleted := v_deleted + SQLROWCOUNT;
            INSERT INTO AW.DBO.ERCOTSTATIONINJECTION ("TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, NETINJECTIONMW)
            SELECT "TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, NETINJECTIONMW
            FROM TMP_STATION_INJECTION ORDER BY 1, 2, 3;   -- target clusters on (date, station)
            v_inserted := v_inserted + SQLROWCOUNT;
            COMMIT;
        END IF;

        v_from := v_to;
    END WHILE;

    RETURN 'OK: ' || v_deleted || ' rows deleted, ' || v_inserted || ' rows inserted for '
           || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR;

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
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2026-07-24', 365);
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2023-03-28', '2023-04-04');  -- re-run after deploying the fallback


-- ===========================================================================
-- Verification: generation must be visible at generator voltages.
-- STP ~ +2606 at 25 kV, CPSES ~ +2409 at 22 kV, solar farms positive at 34.5 kV.
-- If these read ~0, the transformer mirror did not fire - check that
-- ERCOTSETRANSFORMERWINDINGMAP and ERCOTCIMEFFECTIVEDATE cover the dates loaded.
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
-- expected residual); if it's growing, extend the name-correcting table.
--
-- SELECT COUNT(*) AS UNMAPPED_TRANSFORMER_ROWS
-- FROM AW.DBO.ISOERCOTSEBRANCH b
-- JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE d
--   ON d.BRANCHDEVICEID = b.BRANCHDEVICEID AND d.BRANCHDEVICETYPE = 'Transformer'
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
--   ON b."TIMESTAMP" >= e.EFFECTIVE_FROM AND b."TIMESTAMP" < e.EFFECTIVE_TO
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m
--   ON m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = b.BRANCHDEVICEID
-- WHERE b."TIMESTAMP" >= '2026-07-01' AND b."TIMESTAMP" < '2026-07-02'
--   AND b.FROMMW IS NOT NULL
--   AND m.BRANCHDEVICEID IS NULL;
