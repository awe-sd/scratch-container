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
-- A phase-angle regulator has both windings at the same kV, so no mirror ever
-- fires for it; PARs are excluded from the FROMMW leg entirely (matched against
-- AW.DBO.PARERCOTSTATION by station + transformer end name), since a PAR's
-- through-flow is internal to one station, not an injection.
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
-- PAR losses (under 0.25 MW) are dropped instead, since the PAR is excluded
-- rather than mirrored.
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
-- faster). The whole range runs as a single pass in one transaction, which is
-- fast enough on its own. Daily incremental: CALL ...(d, d).
-- Backfill: one call for the whole range on a LARGE+ warehouse.
--
-- One snapshot per hour. SE stamps :57 for the top of the next hour, so hours
-- are bucketed by nearest hour and the date range is applied in those terms
-- (a 23:57 row belongs to the next day). Per bucket the most complete
-- snapshot wins, latest on ties, which drops the model-rollout stubs and
-- accepts a delayed :00 solve. A bucket whose best snapshot has under half
-- the active devices (five known days with no line rows) is skipped.
--
-- ---------------------------------------------------------------------------
-- OTHER NOTES
--
-- GENMW and WITHDRAWMW are left NULL; only NETINJECTIONMW is solved for.
-- TIMESTAMP is kept at the source snapshot's own resolution (one row per
--   hour bucket - see above). SE timestamps are irregular - :57 recently,
--   :58 in 2021-2022, occasionally on the hour or a delayed :00.
-- The DELETE+INSERT runs in one transaction for the whole call; an empty
--   source range leaves the target untouched.
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

-- The 3-argument version WAS deployed; drop it so only the 2-argument proc remains:
--   DROP PROCEDURE IF EXISTS AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION(DATE, DATE, INTEGER);
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
    v_end      TIMESTAMP_NTZ;
    v_devices  INTEGER;
    v_deleted  INTEGER DEFAULT 0;
    v_inserted INTEGER DEFAULT 0;
BEGIN
    IF (P_START_DATE IS NULL OR P_END_DATE IS NULL OR P_START_DATE > P_END_DATE) THEN
        RETURN 'ERROR: need non-null P_START_DATE <= P_END_DATE.';
    END IF;
    v_end := DATEADD(DAY, 1, P_END_DATE);

    -- One row per (device, terminal): where the flow is booked, which MW column, and when the row applies.
    CREATE OR REPLACE TEMPORARY TABLE TMP_TERMINAL AS
    -- FROMMW at the from-station: a line's from end, or the winding ERCOT reports on a transformer
    SELECT d.BRANCHDEVICEID, d.FROMSTATIONNAME AS STATIONNAME, CAST(d.KVLEVEL AS NUMBER(6,2)) AS KVLEVEL,
           TRUE AS USE_FROMMW, '1900-01-01'::TIMESTAMP_NTZ AS EFFECTIVE_FROM, '9999-12-31'::TIMESTAMP_NTZ AS EFFECTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE d
    WHERE d.BRANCHDEVICETYPE IN ('Line', 'Transformer')
      AND NOT EXISTS (
          SELECT 1 FROM AW.DBO.PARERCOTSTATION p
          WHERE p.STATION = d.FROMSTATIONNAME AND p.TRANSFORMERENDNAME = d.TRANSFORMERENDNAME
      )
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
            SELECT e.EFFECTIVE_FROM, e.EFFECTIVE_TO, MAX(IFF(w.CIMFILEID IS NULL, NULL, e.CIMFILEID)) AS WINDING_CIMFILEID
            FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
            LEFT JOIN (SELECT DISTINCT CIMFILEID FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING) w ON w.CIMFILEID = e.CIMFILEID
            GROUP BY e.EFFECTIVE_FROM, e.EFFECTIVE_TO
        )
    ) e
    JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m ON m.CIMFILEID = e.CIMFILEID
    WHERE ABS(m.NOMINALKV - m.DEVICEKV) > 0.05;

    -- The only scan of ISOERCOTSEBRANCH. Snapshots are stamped :57 for the top of the NEXT hour, so the
    -- range is taken in nearest-hour terms: a 23:57 snapshot belongs to the following day.
    CREATE OR REPLACE TEMPORARY TABLE TMP_FLOW AS
    SELECT BRANCHDEVICEID, "TIMESTAMP", FROMMW, TOMW
    FROM AW.DBO.ISOERCOTSEBRANCH
    WHERE "TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ)
      AND "TIMESTAMP" <  DATEADD(MINUTE, -30, :v_end);

    -- One snapshot per hour: the most complete one in the bucket, latest on ties (rollout-night stubs and
    -- delayed :00 solves resolve here). Buckets whose best snapshot has under half the active devices are
    -- partial publishes (e.g. lines missing) and are skipped.
    SELECT COUNT(*) INTO :v_devices FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE DATEACTIVESTART < :v_end AND DATEACTIVEEND >= :P_START_DATE;

    CREATE OR REPLACE TEMPORARY TABLE TMP_SNAPSHOT AS
    SELECT "TIMESTAMP"
    FROM (SELECT "TIMESTAMP", COUNT(*) AS N FROM TMP_FLOW GROUP BY "TIMESTAMP")
    QUALIFY ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC('HOUR', DATEADD(MINUTE, 30, "TIMESTAMP"))
                               ORDER BY N DESC, "TIMESTAMP" DESC) = 1
        AND N >= 0.5 * :v_devices;

    -- Staged first (DDL autocommits, so outside the transaction): an empty source range leaves the target untouched.
    CREATE OR REPLACE TEMPORARY TABLE TMP_STATION_INJECTION AS
    SELECT CAST(br."TIMESTAMP" AS TIMESTAMP_NTZ(0)) AS "TIMESTAMP", t.STATIONNAME AS NMMSSTATIONCODE, t.KVLEVEL,
           SUM(ZEROIFNULL(IFF(t.USE_FROMMW, br.FROMMW, br.TOMW))) AS NETINJECTIONMW
    FROM TMP_FLOW br
    JOIN TMP_SNAPSHOT s ON s."TIMESTAMP" = br."TIMESTAMP"
    JOIN TMP_TERMINAL t ON t.BRANCHDEVICEID = br.BRANCHDEVICEID
                       AND br."TIMESTAMP" >= t.EFFECTIVE_FROM AND br."TIMESTAMP" < t.EFFECTIVE_TO
    GROUP BY 1, 2, 3;

    IF ((SELECT COUNT(*) FROM TMP_STATION_INJECTION) = 0) THEN
        RETURN 'OK: no usable SE snapshots for ' || :P_START_DATE::VARCHAR || '..' || :P_END_DATE::VARCHAR || ', target untouched.';
    END IF;

    BEGIN TRANSACTION;
    DELETE FROM AW.DBO.ERCOTSTATIONINJECTION
    WHERE "TIMESTAMP" >= DATEADD(MINUTE, -30, :P_START_DATE::TIMESTAMP_NTZ)
      AND "TIMESTAMP" <  DATEADD(MINUTE, -30, :v_end);
    v_deleted := SQLROWCOUNT;
    INSERT INTO AW.DBO.ERCOTSTATIONINJECTION ("TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, NETINJECTIONMW)
    SELECT "TIMESTAMP", NMMSSTATIONCODE, KVLEVEL, NETINJECTIONMW
    FROM TMP_STATION_INJECTION ORDER BY 1, 2, 3;   -- target clusters on (date, station)
    v_inserted := SQLROWCOUNT;
    COMMIT;

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
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION('2022-01-01', '2026-07-25');
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
