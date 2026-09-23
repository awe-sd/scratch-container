-- ============================================================================
-- ERCOT SE transformer winding attribution: one exception TABLE + two VIEWS
--
--   AW.DBO.ERCOTSEXFMRDEVICEFIX    TABLE, 159 rows - ONLY the devices ERCOT
--                                  reports incorrectly. The single piece of
--                                  hand-maintained data in this pipeline.
--   AW.DBO.ERCOTCIMEFFECTIVE       VIEW - date -> CIM model in force
--   AW.DBO.ERCOTSEXFMRWINDINGMAP   VIEW - device -> REPORTED_KV, MIRROR_KV
--
-- The views are pure derivations, so they never need rebuilding when ERCOT
-- publishes a new CIM model. Only the exception table is static, and it only has
-- to change if ERCOT mislabels a NEW device - use the detection query in
-- section 4 to find those.
--
-- SP_LOAD_ERCOT_STATION_INJECTION just joins the two views and aggregates.
--
-- Role: AW_ACCESS.
-- ============================================================================


-- ============================================================================
-- 1. AW.DBO.ERCOTSEXFMRDEVICEFIX - the ERCOT reporting bug, as data
--
-- BACKGROUND
--
-- ISOERCOTSEBRANCHVIEW.KVLEVEL identifies only ONE end of a transformer. ERCOT
-- reports the flow on that one side and expects the other side to carry the same
-- magnitude with opposite sign, but the other side's VOLTAGE never appears in the
-- branch data. AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING supplies it, joined on
-- winding name.
--
-- THE BUG: for 159 devices, ERCOT's TRANSFORMERENDNAME names the WRONG winding.
-- The kV is correct; the name is not. The name points at one winding while
-- KVLEVEL is the other winding's voltage:
--
--     DUNLAP    end AT1H     @138   windings AT1H@345, AT1L@138
--     EINSTEIN  end ENS7TR1H @138   windings ENS7TR1H@345, ENS7TR1@138
--     HRZN_SLR  end T1       @34.5  windings T1@138, T1_L@34.5
--     SUN_SLR   end T101     @34.5  windings T101@138, T101_L@34.5
--
-- Joining on name AND kV drops these devices entirely - they contribute neither a
-- reported nor a mirrored terminal, so the station/kV balance is short by their
-- flow. On 2026-07-01 that was 108 devices and 4,908 MW absolute, mostly solar
-- plants, losing their whole output (HRZN_SLR +197 MW, SUN_SLR +175 MW at
-- 34.5 kV).
--
-- This table records, per device, which TRANSFORMER it really belongs to. The
-- correction is stable: each of the 159 devices maps to exactly one transformer
-- across all 202 CIM models, so no CIMFILEID column is needed.
--
-- Note that the correction cannot be derived by matching TRANSFORMERENDNAME to
-- TRANSFORMERNAME. That works for DUNLAP AT2 and HRZN_SLR T1, but not
-- AT1H -> AT1 or ENS7TR1H -> 7TR1. Hence a stored mapping.
-- ============================================================================

CREATE OR REPLACE TABLE AW.DBO.ERCOTSEXFMRDEVICEFIX (
    BRANCHDEVICEID          NUMBER       NOT NULL,
    BRANCHDEVICENAME        VARCHAR(255),
    STATION                 VARCHAR(255),
    REPORTED_ENDNAME        VARCHAR(255) COMMENT 'What ERCOT reports as TRANSFORMERENDNAME - the wrong winding',
    REPORTED_KVLEVEL        NUMBER(6,2)  COMMENT 'The device KVLEVEL, which IS correct',
    CORRECT_TRANSFORMERNAME VARCHAR(128) COMMENT 'The transformer this device actually belongs to',
    NOTE                    VARCHAR(500)
);

COMMENT ON TABLE AW.DBO.ERCOTSEXFMRDEVICEFIX IS
    'Exception list: SE transformer branch devices whose TRANSFORMERENDNAME names the wrong winding. Maps each to its real transformer so ERCOTSEXFMRWINDINGMAP can resolve both voltages. Hand-maintained; extend using the detection query in build_ercot_xfmr_winding_map.sql.';

-- One-time seed. This is the ONLY place the fuzzy name-ignoring-kV match runs;
-- it never executes at query time. After seeding, inspect the 159 rows and treat
-- the table as static data.
INSERT INTO AW.DBO.ERCOTSEXFMRDEVICEFIX
    (BRANCHDEVICEID, BRANCHDEVICENAME, STATION, REPORTED_ENDNAME,
     REPORTED_KVLEVEL, CORRECT_TRANSFORMERNAME, NOTE)
WITH usable AS (
    SELECT DISTINCT c.CIMFILEID
    FROM AW.DBO.CIMFILE c
    WHERE c.ISOMARKETID = 6
      AND c.CIMPATH NOT LIKE '%MP_MarketModel%'
      AND EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w
                   WHERE w.CIMFILEID = c.CIMFILEID)
),
term AS (
    SELECT DISTINCT w.CIMFILEID, w.STATION, w.TRANSFORMERNAME, w.WINDINGNAME,
           CAST(w.NOMINALKV AS NUMBER(6,2)) AS NOMINALKV
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w
    JOIN usable u ON u.CIMFILEID = w.CIMFILEID
    WHERE w.NOMINALKV <> 1
),
term_kv AS (SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, NOMINALKV FROM term),
xdev AS (
    SELECT BRANCHDEVICEID, BRANCHDEVICENAME, FROMSTATIONNAME AS STATION,
           TRANSFORMERENDNAME, CAST(KVLEVEL AS NUMBER(6,2)) AS KVLEVEL
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE BRANCHDEVICETYPE = 'Transformer' AND FROMSTATIONNAME IS NOT NULL
),
-- devices ERCOT reports correctly: winding name and voltage agree
ok_keys AS (
    SELECT DISTINCT t.CIMFILEID, x.BRANCHDEVICEID
    FROM xdev x
    JOIN term t
      ON t.STATION     = x.STATION
     AND t.WINDINGNAME = x.TRANSFORMERENDNAME
     AND ABS(t.NOMINALKV - x.KVLEVEL) <= 0.05
)
SELECT DISTINCT
       x.BRANCHDEVICEID,
       x.BRANCHDEVICENAME,
       x.STATION,
       x.TRANSFORMERENDNAME,
       x.KVLEVEL,
       t.TRANSFORMERNAME,
       'Seeded: ERCOT TRANSFORMERENDNAME names a winding at a different voltage'
FROM xdev x
JOIN term t
  ON t.STATION     = x.STATION
 AND t.WINDINGNAME = x.TRANSFORMERENDNAME      -- name matches, kV deliberately not
JOIN term_kv v
  ON v.CIMFILEID       = t.CIMFILEID
 AND v.STATION         = t.STATION
 AND v.TRANSFORMERNAME = t.TRANSFORMERNAME
 AND ABS(v.NOMINALKV - x.KVLEVEL) <= 0.05      -- device kV IS a real winding kV
LEFT JOIN ok_keys k
  ON k.BRANCHDEVICEID = x.BRANCHDEVICEID
 AND k.CIMFILEID      = t.CIMFILEID
WHERE k.BRANCHDEVICEID IS NULL;                -- only devices the clean join misses


-- ============================================================================
-- 2. AW.DBO.ERCOTCIMEFFECTIVE - which CIM model applies to a given date
--
-- Built directly on ERCOT's own publication schedule,
-- AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE, with the CIMFILEID attached.
-- CIMFILE.CIMDATE equals the schedule's EFFECTIVE_THROUGH, which is the join key.
--
-- EFFECTIVE_FROM is the schedule's PRODUCTION_LOAD - the day the model goes into
-- service. EFFECTIVE_THROUGH is the day BEFORE the next PRODUCTION_LOAD, NOT the
-- schedule's own EFFECTIVE_THROUGH column. That distinction matters: the schedule
-- occasionally skips a load, leaving its EFFECTIVE_THROUGH short of the next
-- load. ERCOT skipped the 2024 holiday loads, so 2024Dec.L2 ends 2024-12-17 while
-- the next row (2025Jan.L1) starts 2025-01-08 - a 21-day hole in which the
-- December model was still in force. 2024Dec.L2.NEXT_PRODUCTION_LOAD is
-- 2024-12-18, confirming the intent. Deriving the end from the next
-- PRODUCTION_LOAD closes every such hole.
--
-- Two filters decide which models are usable:
--   CIMPATH NOT LIKE '%MP_MarketModel%'  excludes TEST models, published ~45
--       days ahead of the production load and never actually in force.
--       2026-07-14 has CIMFILEID 188 (MP_MarketModel, test) and 205
--       (CIM_Jul_ML1, production).
--   EXISTS winding rows  only 202 of 308 production models are loaded into the
--       winding table, and a model without windings can map nothing. This filter
--       also breaks re-posting ties, where one CIMDATE has two CIMFILEIDs:
--       2023-10-03 has 15 (posted-20230927) and 18 (posted-20231018);
--       2025-12-09 has 141 and 145 (RTC_Native). Exactly one of each pair
--       carries windings.
--
-- Verified over 2022-01-01 .. 2026-07-24: 1,666 of 1,666 days resolve to EXACTLY
-- ONE model - 0 unresolved, 0 ambiguous, 0 invalid ranges. First EFFECTIVE_FROM
-- is 2021-12-22, so the 2022 backfill is fully covered.
--
-- The newest model gets EFFECTIVE_THROUGH = 9999-12-31 so current data always
-- resolves rather than silently losing its transformer terminals.
--
-- There is no winding data before 2022 (earliest usable CIMDATE 2022-01-04),
-- which is the real reason the backfill starts there.
-- ============================================================================

CREATE OR REPLACE VIEW AWDEV.ERCOTRT.ERCOTCIMEFFECTIVE AS
WITH sched AS (
    SELECT p.CIM_LABEL,
           p.PRODUCTION_LOAD,
           c.CIMFILEID,
           c.CIMDATE
    FROM AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE p
    JOIN AW.DBO.CIMFILE c
      ON c.CIMDATE = p.EFFECTIVE_THROUGH
    WHERE c.ISOMARKETID = 6
      AND c.CIMPATH NOT LIKE '%MP_MarketModel%'
      AND EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w
                   WHERE w.CIMFILEID = c.CIMFILEID)
)
SELECT
    CIM_LABEL,
    CIMFILEID,
    CIMDATE,
    PRODUCTION_LOAD AS EFFECTIVE_FROM,
    COALESCE(DATEADD(DAY, -1, LEAD(PRODUCTION_LOAD) OVER (ORDER BY PRODUCTION_LOAD)),
             '9999-12-31'::DATE) AS EFFECTIVE_THROUGH
FROM sched;

-- ============================================================================
-- 3. AW.DBO.ERCOTSEXFMRWINDINGMAP - device -> voltage levels
--
-- Two halves, and neither contains any fuzzy matching:
--   ERCOT  devices ERCOT reports correctly - winding name AND voltage agree
--   FIX    devices listed in ERCOTSEXFMRDEVICEFIX - transformer taken from that
--          table, voltage from the device's own KVLEVEL
-- Devices in the fix table are excluded from the ERCOT half, so the two cannot
-- overlap and a flow can never be counted twice.
--
-- COLUMNS
--   REPORTED_KV  voltage of the bus whose flow ERCOT reports. Use with +FROMMW.
--   MIRROR_KV    the other real winding, inferred equal and opposite. Use with
--                -FROMMW. NULL for star-equivalent legs, whose only other
--                winding is the fictitious 1 kV star point.
--   SOURCE       'ERCOT' or 'FIX', for auditing.
--
-- NOMINALKV = 1 rows are excluded throughout: they are fictitious star points
-- used to model 3-winding banks as three star-equivalent legs. ACSSW's bank is
-- three TRANSFORMERNAME entries (AX1H/AX1L/AX1T), each a real winding plus a
-- 1 kV leg, so TRANSFORMERNAME is per-LEG there, not per-bank.
--
-- MIRROR_KV is never ambiguous: no transformer has more than two real voltages
-- (verified 0 of 504,790 combinations exceed 2), so MAX() collapses at most one
-- candidate.
-- ============================================================================

CREATE OR REPLACE VIEW AW.DBO.ERCOTSEXFMRWINDINGMAP AS
WITH term AS (
    SELECT DISTINCT w.CIMFILEID, w.STATION, w.TRANSFORMERNAME, w.WINDINGNAME,
           CAST(w.NOMINALKV AS NUMBER(6,2)) AS NOMINALKV
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w
    JOIN AW.DBO.ERCOTCIMEFFECTIVE e ON e.CIMFILEID = w.CIMFILEID
    WHERE w.NOMINALKV <> 1
),
term_kv AS (
    SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, NOMINALKV FROM term
),
xdev AS (
    SELECT BRANCHDEVICEID, BRANCHDEVICENAME, FROMSTATIONNAME AS STATION,
           TRANSFORMERENDNAME, CAST(KVLEVEL AS NUMBER(6,2)) AS KVLEVEL
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE BRANCHDEVICETYPE = 'Transformer' AND FROMSTATIONNAME IS NOT NULL
),
-- half 1: ERCOT reports this device correctly
from_ercot AS (
    SELECT t.CIMFILEID, x.BRANCHDEVICEID, x.BRANCHDEVICENAME, x.STATION,
           t.TRANSFORMERNAME, x.KVLEVEL AS REPORTED_KV, 'ERCOT' AS SOURCE
    FROM xdev x
    JOIN term t
      ON t.STATION     = x.STATION
     AND t.WINDINGNAME = x.TRANSFORMERENDNAME
     AND ABS(t.NOMINALKV - x.KVLEVEL) <= 0.05
    LEFT JOIN AW.DBO.ERCOTSEXFMRDEVICEFIX f
      ON f.BRANCHDEVICEID = x.BRANCHDEVICEID
    WHERE f.BRANCHDEVICEID IS NULL
),
-- half 2: transformer supplied by the exception table
from_fix AS (
    SELECT k.CIMFILEID, x.BRANCHDEVICEID, x.BRANCHDEVICENAME, x.STATION,
           f.CORRECT_TRANSFORMERNAME AS TRANSFORMERNAME,
           x.KVLEVEL AS REPORTED_KV, 'FIX' AS SOURCE
    FROM AW.DBO.ERCOTSEXFMRDEVICEFIX f
    JOIN xdev x
      ON x.BRANCHDEVICEID = f.BRANCHDEVICEID
    JOIN term_kv k
      ON k.STATION         = x.STATION
     AND k.TRANSFORMERNAME = f.CORRECT_TRANSFORMERNAME
     AND ABS(k.NOMINALKV - x.KVLEVEL) <= 0.05
),
rep AS (
    SELECT * FROM from_ercot
    UNION ALL
    SELECT * FROM from_fix
)
SELECT
    r.CIMFILEID,
    r.BRANCHDEVICEID,
    r.BRANCHDEVICENAME,
    r.STATION,
    r.TRANSFORMERNAME,
    r.REPORTED_KV,
    MAX(m.NOMINALKV) AS MIRROR_KV,
    r.SOURCE
FROM rep r
LEFT JOIN term_kv m
       ON m.CIMFILEID       = r.CIMFILEID
      AND m.STATION         = r.STATION
      AND m.TRANSFORMERNAME = r.TRANSFORMERNAME
      AND ABS(m.NOMINALKV - r.REPORTED_KV) > 0.05
GROUP BY r.CIMFILEID, r.BRANCHDEVICEID, r.BRANCHDEVICENAME, r.STATION,
         r.TRANSFORMERNAME, r.REPORTED_KV, r.SOURCE;


-- ============================================================================
-- 4. DETECTION - find NEW devices ERCOT has started mislabelling
--
-- Run after ERCOT publishes a new CIM model. Any rows returned are devices that
-- carry flow but resolve through neither half of the map; add them to
-- ERCOTSEXFMRDEVICEFIX. Adjust the date range to a day you have loaded.
-- ============================================================================

-- WITH d AS (
--     SELECT b.BRANCHDEVICEID, MAX(ABS(b.FROMMW)) AS MAX_ABS_MW
--     FROM AW.DBO.ISOERCOTSEBRANCH b
--     JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE dv
--       ON dv.BRANCHDEVICEID = b.BRANCHDEVICEID
--      AND dv.BRANCHDEVICETYPE = 'Transformer'
--     WHERE b."TIMESTAMP" >= '2026-07-01' AND b."TIMESTAMP" < '2026-07-02'
--       AND b.FROMMW IS NOT NULL
--     GROUP BY b.BRANCHDEVICEID
-- )
-- SELECT dv.FROMSTATIONNAME AS STATION, dv.BRANCHDEVICENAME,
--        dv.TRANSFORMERENDNAME, dv.KVLEVEL, ROUND(d.MAX_ABS_MW,1) AS MAX_ABS_MW
-- FROM d
-- JOIN AW.DBO.ISOERCOTSEBRANCHDEVICE dv ON dv.BRANCHDEVICEID = d.BRANCHDEVICEID
-- LEFT JOIN AW.DBO.ERCOTCIMEFFECTIVE e
--        ON '2026-07-01'::DATE BETWEEN e.EFFECTIVE_FROM AND e.EFFECTIVE_THROUGH
-- LEFT JOIN AW.DBO.ERCOTSEXFMRWINDINGMAP m
--        ON m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = d.BRANCHDEVICEID
-- WHERE m.BRANCHDEVICEID IS NULL
-- ORDER BY d.MAX_ABS_MW DESC;


-- ============================================================================
-- 5. VERIFICATION - run after seeding
-- ============================================================================

-- A. Exception table size. Expect 159.
SELECT COUNT(*) AS FIX_ROWS,
       COUNT(DISTINCT BRANCHDEVICEID) AS DISTINCT_DEVICES
FROM AW.DBO.ERCOTSEXFMRDEVICEFIX;

-- B. MUST return 0. A device may appear only once per model, or its flow would
--    be counted twice.
SELECT COUNT(*) AS DEVICES_MAPPED_TWICE
FROM (
    SELECT CIMFILEID, BRANCHDEVICEID
    FROM AW.DBO.ERCOTSEXFMRWINDINGMAP
    GROUP BY CIMFILEID, BRANCHDEVICEID
    HAVING COUNT(*) > 1
);

-- C. MUST return 0 for both. Calendar ranges may not overlap, and every day of
--    the backfill window must resolve to exactly one model.
SELECT
    (SELECT COUNT(*)
     FROM AW.DBO.ERCOTCIMEFFECTIVE a
     JOIN AW.DBO.ERCOTCIMEFFECTIVE b
       ON a.CIMFILEID <> b.CIMFILEID
      AND a.EFFECTIVE_FROM <= b.EFFECTIVE_THROUGH
      AND b.EFFECTIVE_FROM <= a.EFFECTIVE_THROUGH)          AS OVERLAPPING_RANGES,
    (SELECT COUNT(*) FROM (
        SELECT d.D, COUNT(e.CIMFILEID) AS MATCHES
        FROM (SELECT DATEADD(DAY, SEQ4(), '2022-01-01'::DATE) AS D
              FROM TABLE(GENERATOR(ROWCOUNT => 1666))) d
        LEFT JOIN AW.DBO.ERCOTCIMEFFECTIVE e
               ON d.D BETWEEN e.EFFECTIVE_FROM AND e.EFFECTIVE_THROUGH
        GROUP BY d.D
        HAVING COUNT(e.CIMFILEID) <> 1))                    AS DAYS_NOT_EXACTLY_ONE;

-- D. MUST return 0. Mirror must never be ambiguous.
SELECT COUNT(*) AS XFMRS_WITH_GT2_REAL_KV
FROM (
    SELECT CIMFILEID, STATION, TRANSFORMERNAME
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
    WHERE NOMINALKV <> 1
    GROUP BY CIMFILEID, STATION, TRANSFORMERNAME
    HAVING COUNT(DISTINCT NOMINALKV) > 2
);

-- E. Map composition for the current model. Expect ~2,540 ERCOT + 108 FIX
--    among devices that carry flow.
SELECT SOURCE, COUNT(*) AS DEVICES,
       SUM(CASE WHEN MIRROR_KV IS NULL THEN 1 ELSE 0 END) AS NO_MIRROR_STAR_LEGS
FROM AW.DBO.ERCOTSEXFMRWINDINGMAP
WHERE CIMFILEID = (SELECT CIMFILEID FROM AW.DBO.ERCOTCIMEFFECTIVE
                    WHERE EFFECTIVE_THROUGH = '9999-12-31')
GROUP BY SOURCE ORDER BY SOURCE;

-- F. Spot check. STP GSUs 345 -> mirror 25 via ERCOT; ACSSW star legs no mirror;
--    DUNLAP and HRZN_SLR via FIX.
SELECT STATION, BRANCHDEVICENAME, TRANSFORMERNAME,
       REPORTED_KV, MIRROR_KV, SOURCE
FROM AW.DBO.ERCOTSEXFMRWINDINGMAP
WHERE CIMFILEID = (SELECT CIMFILEID FROM AW.DBO.ERCOTCIMEFFECTIVE
                    WHERE EFFECTIVE_THROUGH = '9999-12-31')
  AND STATION IN ('STP','ACSSW','DUNLAP','HRZN_SLR')
ORDER BY STATION, BRANCHDEVICENAME;
