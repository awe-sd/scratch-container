-- ============================================================================
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2
--
-- V2 adds the sub-69 kV re-key (mirror-based and CIM-star-bus-based) on top of
-- the deployed SP_LOAD_ERCOT_STATION_INJECTION; that proc and file are
-- untouched. Same signature, same target table, same delete-and-insert
-- behaviour - deploy this alongside it, verify, then retire the old one.
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
--   Transformer, reported terminal      ->  FROMMW  at the device's own KVLEVEL, re-keyed to the
--                                            transmission-side kV when that own KVLEVEL is under 69
--   Transformer, other real winding     ->  TOMW    at that winding's NOMINALKV, similarly re-keyed
--                                            when the winding itself is under 69
--
-- These four rules are materialized ONCE per call as the TMP_TERMINAL dimension
-- and joined ONCE to the flow table (see PERFORMANCE / BULK LOADING below).
--
-- A transformer terminal (reported or mirror) under 69 kV is re-keyed to that
-- transformer's transmission-side kV (its highest mapped winding at or above
-- 69 kV) - a generator step-up reports at machine kV (18, 13.1, 34.5...), and
-- at a split station (e.g. BOSQUESW, 345 kV units and a 138 kV unit sharing
-- one low-kV cell) that hides which transmission bus the generation belongs
-- to. Nothing is deleted: both the reported terminal and its mirror move to
-- the same transmission-side cell and cancel to losses there, same as any
-- other transformer, and station totals are unchanged by construction. Lines
-- are never re-keyed. A device whose own winding-map rows have no winding at
-- or above 69 kV falls into two different sub-cases. One has no real mirror
-- at all - a single real winding (e.g. a GSU or autotransformer tertiary
-- modeled as a separate per-leg device: BRAUNIG_ST/CT1, WHCCS_1X/1Y,
-- DOW_A2T/A3T/A5T) - and is instead resolved through the CIM star point its
-- bank's real legs share (ERCOTTRANSFORMERWINDING's NOMINALKV=1 row, keyed by
-- FROMNUM): re-keyed if exactly one sibling leg is at or above 69 kV, left
-- alone if none (no transmission leg) or two or more (an ambiguous
-- autotransformer tertiary sitting between two transmission kVs, e.g.
-- DOW_A2T/A3T/A5T between 345 and 138). The star partner is a re-key target
-- only, never a mirror - both legs are already independently reported, so
-- mirroring the pair would double count. The other sub-case already has a
-- real mirror of its own, both windings under 69 kV (e.g. MSN/TRTG,
-- APTXCITY/P131, 34.5/13.8 two-winding devices) - the star rule explicitly
-- skips these; re-keying only the reported side through an unrelated star
-- bus would desynchronize it from its own mirror, which stays put. ERCOT
-- reports flow on only one winding and expects the other to be equal and
-- opposite; verified over 2026-01-01..2026-07-25 that no transformer ever
-- reports both sides (281,126 timestamp/transformer pairs, always exactly
-- one).
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
-- generation visibility and low-side-reported GSUs double-count. A low-side-
-- reported step-up whose reported terminal is already re-keyed (LOWKV_REKEY,
-- sourced from that same fallback CIMFILEID) keeps re-keying straight through
-- such a gap - if the gap outlasts a real topology change underneath it, the
-- stale target and the still-firing mirror can both land at the same
-- transmission kV together, and the transmission cell reads doubled rather
-- than dropping to 0. After loading windings for such a model, re-run the
-- proc over its range.
--
-- Result at 2026-06-23 13:57 (simulated read-only from this file's TMP_TERMINAL
-- body against the live tables, pre-rebuild - AW.DBO.ERCOTSTATIONINJECTION
-- itself only shows these values after the rebuild call in Usage below):
--     STP      345   -> +1290.3   generation, via the re-keyed mirror
--     CPSES    345   -> +2383.1   generation
--     HRZN_SLR 138   ->  +179.8   solar generation, via the re-keyed mirror
--     SUN_SLR  138   ->  +183.6   solar generation
--     BRAUNIG  345   ->  +524.2   generation (BRAUNIG_ST/CT1 re-keyed via the
--                                 star bus BRAUNIG_18_3 also sits on)
--     BOSQUESW 138   ->  +197.0   generation (FMR3/FMR4)
--     BOSQUESW 345   ->  +468.3   generation (FMR1/FMR2/FMR5)
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

CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2(
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
    -- A transformer terminal under 69 kV is re-keyed to that transformer's transmission-side kV (see header).
    CREATE OR REPLACE TEMPORARY TABLE TMP_TERMINAL AS
    WITH CIM_WINDOW AS (
        -- Which CIM model's windings apply at a given time. If the in-force model has no windings loaded
        -- yet, falls back to the latest earlier model that does.
        SELECT EFFECTIVE_FROM, EFFECTIVE_TO,
               LAST_VALUE(WINDING_CIMFILEID) IGNORE NULLS
                   OVER (ORDER BY EFFECTIVE_FROM ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CIMFILEID
        FROM (
            SELECT e.EFFECTIVE_FROM, e.EFFECTIVE_TO, MAX(IFF(w.CIMFILEID IS NULL, NULL, e.CIMFILEID)) AS WINDING_CIMFILEID
            FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
            LEFT JOIN (SELECT DISTINCT CIMFILEID FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING) w ON w.CIMFILEID = e.CIMFILEID
            GROUP BY e.EFFECTIVE_FROM, e.EFFECTIVE_TO
        )
    ),
    MIRROR AS (
        -- The transformer's other real winding, while that CIM model is in force.
        SELECT m.BRANCHDEVICEID, m.STATION, m.DEVICEKV, m.NOMINALKV AS MIRRORKV, w.EFFECTIVE_FROM, w.EFFECTIVE_TO
        FROM CIM_WINDOW w
        JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m ON m.CIMFILEID = w.CIMFILEID
        WHERE ABS(m.NOMINALKV - m.DEVICEKV) > 0.05
    ),
    LOWKV_REKEY AS (
        -- Case 2: reported terminal under 69 kV whose OWN transformer's other real winding is at or above
        -- (the mirror side needs no lookup here - it is already at or above 69 kV, so the inline IFF in the
        -- last UNION branch below leaves it untouched): the kV it moves to, and the earliest window it is
        -- known from. Collapsed to one row per device - verified every such device has exactly one MIRRORKV
        -- value across every model it maps in, so MIN(EFFECTIVE_FROM) is a safe single cutover point.
        SELECT BRANCHDEVICEID, MIN(EFFECTIVE_FROM) AS MAPPED_FROM, MAX(MIRRORKV) AS TARGETKV
        FROM MIRROR
        WHERE DEVICEKV < 69 AND MIRRORKV >= 69
        GROUP BY BRANCHDEVICEID
    ),
    STAR_BUS AS (
        -- A 3+-winding bank is modeled as separate per-leg TRANSFORMERNAMEs, each with its own NOMINALKV=1
        -- star-point row (see build_ercot_transformer_winding_map.sql); every real leg of the same physical
        -- bank shares that row's FROMNUM (verified against BRAUNIG 18_3/ST/CT1, MT56/MT5L/MT6L,
        -- MT78/MT7L/MT8L; DOW A2P/A2S/A2T; WHCCS 1H/1X/1Y; CVC XT1H/XT1X/XT1Y).
        SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, FROMNUM AS STARBUS
        FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
        WHERE NOMINALKV = 1
    ),
    STAR_SIBLING_KV AS (
        -- Real windings at or above 69 kV sharing a star bus. A candidate's own leg never appears here by
        -- construction (its own real kV is under 69, so it never passes the >= 69 filter below). Read-only
        -- against the CIM winding table; never feeds the winding-map view, so a star partner is a re-key
        -- target only and never becomes a mirror (both legs are already independently reported - mirroring
        -- would double count).
        SELECT DISTINCT sb.CIMFILEID, sb.STATION, sb.STARBUS, CAST(rw.NOMINALKV AS NUMBER(6,2)) AS REALKV
        FROM STAR_BUS sb
        JOIN AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING rw
          ON rw.CIMFILEID = sb.CIMFILEID AND rw.STATION = sb.STATION AND rw.TRANSFORMERNAME = sb.TRANSFORMERNAME
         AND rw.NOMINALKV >= 69
    ),
    STAR_REKEY_WINDOW AS (
        -- Case 3: a device's own map rows have no winding at or above 69 kV (e.g. an autotransformer
        -- tertiary or a GSU whose bank is split into per-leg devices) AND it has no real mirror of its own
        -- (a device that already has a same-bank mirror under 69 kV must keep that pairing - re-keying only
        -- the reported side here would desynchronize it from its own mirror, which stays put). Resolved via
        -- its star-bus siblings instead - exactly one candidate is a re-key target; zero or two-or-more is
        -- left alone (no transmission leg, or an ambiguous tertiary sitting between two transmission kVs).
        SELECT c.BRANCHDEVICEID, w.EFFECTIVE_FROM, w.EFFECTIVE_TO,
               COUNT(DISTINCT sk.REALKV) AS CANDIDATE_COUNT, MAX(sk.REALKV) AS TARGETKV
        FROM (
            SELECT CIMFILEID, BRANCHDEVICEID, STATION, TRANSFORMERNAME
            FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m1
            WHERE DEVICEKV < 69
              AND NOT EXISTS (
                  SELECT 1 FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m2
                  WHERE m2.CIMFILEID = m1.CIMFILEID AND m2.BRANCHDEVICEID = m1.BRANCHDEVICEID
                    AND ABS(m2.NOMINALKV - m2.DEVICEKV) > 0.05
              )
            GROUP BY CIMFILEID, BRANCHDEVICEID, STATION, TRANSFORMERNAME
            HAVING MAX(NOMINALKV) < 69
        ) c
        JOIN STAR_BUS sb ON sb.CIMFILEID = c.CIMFILEID AND sb.STATION = c.STATION AND sb.TRANSFORMERNAME = c.TRANSFORMERNAME
        JOIN STAR_SIBLING_KV sk ON sk.CIMFILEID = sb.CIMFILEID AND sk.STATION = sb.STATION AND sk.STARBUS = sb.STARBUS
        JOIN CIM_WINDOW w ON w.CIMFILEID = c.CIMFILEID
        GROUP BY c.BRANCHDEVICEID, w.EFFECTIVE_FROM, w.EFFECTIVE_TO
    ),
    STAR_REKEY AS (
        -- Collapsed to one row per device, same as LOWKV_REKEY - verified 0 devices ever resolve to more
        -- than one target kV, and 0 devices flip between resolved and ambiguous/none across models.
        SELECT BRANCHDEVICEID, MIN(EFFECTIVE_FROM) AS MAPPED_FROM, MAX(TARGETKV) AS TARGETKV
        FROM STAR_REKEY_WINDOW
        WHERE CANDIDATE_COUNT = 1
        GROUP BY BRANCHDEVICEID
    ),
    REKEY_TARGET AS (       -- combined leg-1 re-key lookup: mirror-based (case 2) and star-based (case 3)
        SELECT BRANCHDEVICEID, MAPPED_FROM, TARGETKV FROM LOWKV_REKEY
        UNION ALL
        SELECT BRANCHDEVICEID, MAPPED_FROM, TARGETKV FROM STAR_REKEY
    )
    -- FROMMW at the from-station, before its transformer is first re-keyed to a transmission-side kV: a
    -- re-keyed device's own low kV, dropped once MAPPED_FROM arrives (next branch takes over). Membership
    -- in REKEY_TARGET is the only condition (no redundant BRANCHDEVICETYPE/KVLEVEL predicate, so this branch
    -- can never desynchronize from the next one). Emits no flow rows over the 2022-01-01..2026-07-25
    -- backfill range in practice (39 devices, all first active at or after their own MAPPED_FROM cutover) -
    -- kept for completeness against a future backfill that reaches further back.
    SELECT d.BRANCHDEVICEID, d.FROMSTATIONNAME AS STATIONNAME, CAST(d.KVLEVEL AS NUMBER(6,2)) AS KVLEVEL,
           TRUE AS USE_FROMMW, '1900-01-01'::TIMESTAMP_NTZ AS EFFECTIVE_FROM, r.MAPPED_FROM AS EFFECTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE d
    JOIN REKEY_TARGET r ON r.BRANCHDEVICEID = d.BRANCHDEVICEID
    WHERE NOT EXISTS (
          SELECT 1 FROM AW.DBO.PARERCOTSTATION p
          WHERE p.STATION = d.FROMSTATIONNAME AND p.TRANSFORMERENDNAME = d.TRANSFORMERENDNAME
      )
    UNION ALL
    -- FROMMW at the from-station: a line's from end, or the winding ERCOT reports on a transformer, re-keyed
    -- to the transmission-side kV once resolved if that own kV is under 69.
    SELECT d.BRANCHDEVICEID, d.FROMSTATIONNAME AS STATIONNAME, CAST(COALESCE(r.TARGETKV, d.KVLEVEL) AS NUMBER(6,2)) AS KVLEVEL,
           TRUE AS USE_FROMMW, COALESCE(r.MAPPED_FROM, '1900-01-01'::TIMESTAMP_NTZ) AS EFFECTIVE_FROM, '9999-12-31'::TIMESTAMP_NTZ AS EFFECTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE d
    LEFT JOIN REKEY_TARGET r ON r.BRANCHDEVICEID = d.BRANCHDEVICEID
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
    -- TOMW at the transformer's other real winding; re-keyed to DEVICEKV when the mirror itself is under 69 kV
    -- and the reported side is transmission (both-under-69 devices are left alone, per the header).
    SELECT BRANCHDEVICEID, STATION, IFF(MIRRORKV < 69 AND DEVICEKV >= 69, DEVICEKV, MIRRORKV), FALSE, EFFECTIVE_FROM, EFFECTIVE_TO
    FROM MIRROR;

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
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2022-01-01', '2022-01-31');
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2026-07-01', '2026-07-24');
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2022-01-01', '2026-07-25');
--   CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION_V2('2023-03-28', '2023-04-04');  -- re-run after deploying the fallback


-- ===========================================================================
-- Verification: generation must be visible at the TRANSMISSION bus (re-keyed),
-- not at machine voltages - the whole point of the re-key is that a GSU or
-- autotransformer tertiary no longer shows up at its own low kV.
-- At 2026-06-23 13:57: STP ~ +1290 at 345 kV, CPSES ~ +2383 at 345 kV,
-- HRZN_SLR ~ +180 and SUN_SLR ~ +184 at 138 kV, BRAUNIG ~ +524 at 345 kV,
-- BOSQUESW ~ +197 at 138 kV and ~ +468 at 345 kV.
-- If these read ~0 at the transmission cell, the transformer mirror did not
-- fire - check that ERCOTSETRANSFORMERWINDINGMAP and ERCOTCIMEFFECTIVEDATE
-- cover the dates loaded.
-- Note 2022-era timestamps are stamped :58, recent ones :57.
-- ===========================================================================
-- SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2) AS NETINJECTIONMW
-- FROM AW.DBO.ERCOTSTATIONINJECTION
-- WHERE "TIMESTAMP" = '2026-06-23 13:57:00'
--   AND NMMSSTATIONCODE IN ('STP','CPSES','HRZN_SLR','SUN_SLR','BRAUNIG','BOSQUESW')
-- ORDER BY NMMSSTATIONCODE, KVLEVEL;
--
-- Largest injections account-wide should now be at 138/345 kV buses, not
-- machine voltages:
--
-- SELECT NMMSSTATIONCODE, KVLEVEL, ROUND(NETINJECTIONMW,2) AS NETINJECTIONMW
-- FROM AW.DBO.ERCOTSTATIONINJECTION
-- WHERE "TIMESTAMP" = '2026-06-23 13:57:00'
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
