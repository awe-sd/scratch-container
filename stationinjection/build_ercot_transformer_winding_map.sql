-- ============================================================================
-- ERCOT SE transformer winding attribution: three objects.
--
--   AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE       VIEW  - timestamp -> CIM model in force
--   AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING   TABLE - hand-maintained corrected
--                                         winding name, one row per device that
--                                         fails the strict join below
--   AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP   VIEW  - SE transformer device -> each
--                                         real winding of its transformer
--
-- sdalvi's principle: the device KVLEVEL is trustworthy; TRANSFORMERENDNAME is
-- not. So the map joins winding name AND kV (strict), and the name-correcting table is the
-- only place that ever repairs a bad name - it is hand-maintained and reviewed
-- (ercotsetransformernamecorrecting_seed_review.csv), everything else here is a pure
-- derivation. Extend the name-correcting table when verification F below flags a new
-- device; never loosen the join to compensate.
--
-- AWDEV.ERCOTRT.SP_LOAD_ERCOT_STATION_INJECTION joins the CIM-effective and
-- winding-map objects and aggregates. See that file for the attribution rule.
--
-- Role: AW_ACCESS.
-- ============================================================================


-- ============================================================================
-- 1. AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE - which CIM model applies to a given
--    TIMESTAMP
--
-- Built directly on ERCOT's own publication schedule,
-- AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE, with the CIMFILEID attached.
-- CIMFILE.CIMDATE equals the schedule's EFFECTIVE_THROUGH, which is the join key.
--
-- Verified 2026-09-24: the SE switches to a new model at 23:00 on the eve of
-- the schedule's PRODUCTION_LOAD, not at midnight - retired devices' last
-- sample is 22:57 that eve for 216 of 236 retiring devices, and new devices'
-- first sample is 23:57 that eve for 637 of 757 (00:xx on the day for the
-- other 120). EFFECTIVE_FROM is therefore PRODUCTION_LOAD minus one hour.
--
-- EFFECTIVE_TO is exclusive and is the NEXT row's EFFECTIVE_FROM, not the
-- schedule's own EFFECTIVE_THROUGH column. That distinction matters: the
-- schedule occasionally skips a load, leaving its EFFECTIVE_THROUGH short of
-- the next load. ERCOT skipped the 2024 holiday loads, so 2024Dec.L2 ends
-- 2024-12-17 while the next row (2025Jan.L1) starts 2025-01-08 - a 21-day hole
-- in which the December model was still in force. Deriving the end from the
-- next PRODUCTION_LOAD closes every such hole.
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
--       carries windings. Note also that CIMFILEID is not monotone with model
--       recency - CIMFILEID 376 is a 2023-07-18 model loaded late - so never
--       pick "the newest model" by MAX(CIMFILEID).
--
-- The newest model gets EFFECTIVE_TO = 9999-12-31 so current data always
-- resolves rather than silently losing its transformer terminals.
-- ============================================================================

CREATE OR REPLACE VIEW AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE AS
WITH sched AS (
    SELECT p.CIM_LABEL, p.PRODUCTION_LOAD, c.CIMFILEID, c.CIMDATE
    FROM AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE p
    JOIN AW.DBO.CIMFILE c ON c.CIMDATE = p.EFFECTIVE_THROUGH
    WHERE c.ISOMARKETID = 6
      AND c.CIMPATH NOT LIKE '%MP_MarketModel%'
      AND EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w
                   WHERE w.CIMFILEID = c.CIMFILEID)
)
SELECT CIM_LABEL, CIMFILEID, CIMDATE,
       DATEADD(HOUR, -1, PRODUCTION_LOAD::TIMESTAMP_NTZ)                        AS EFFECTIVE_FROM,   -- 23:00 the eve of the load
       COALESCE(LEAD(DATEADD(HOUR, -1, PRODUCTION_LOAD::TIMESTAMP_NTZ))
                    OVER (ORDER BY PRODUCTION_LOAD),
                '9999-12-31'::TIMESTAMP_NTZ)                                    AS EFFECTIVE_TO      -- exclusive
FROM sched;


-- ============================================================================
-- 2. AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING - hand-maintained name-correcting table
--
-- The ONLY hand-maintained object in this pipeline. Stores the corrected
-- WINDING name for a device whose reported TRANSFORMERENDNAME has no winding
-- at its own KVLEVEL in some model it overlaps - i.e. the device's kV is
-- trusted, its name isn't. Stores the corrected name, not the transformer
-- name, because ERCOT renames windings between models (see §3 of the map
-- view below): the map tries the reported name first and the correction second, so
-- either can be right depending on which model is in force.
-- ============================================================================

CREATE OR REPLACE TABLE AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING (
    BRANCHDEVICEID     NUMBER       NOT NULL,
    TRANSFORMERENDNAME VARCHAR(255) NOT NULL COMMENT 'The winding ERCOT should have named for this device (its KVLEVEL is correct)'
);


-- ============================================================================
-- 3. Seed AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING - ONE-TIME, run once at build
--    time only. This is the only place a name-without-kV match ever runs
--    anywhere in this pipeline - it exists purely to bootstrap the name-correcting table,
--    never to serve a query.
--
-- For each active-since-2022 device that fails the strict join in some model
-- it overlaps, take the transformer its reported name points at (ignoring kV)
-- and that transformer's winding at the device's own kV - that winding's name
-- is the correction.
--
-- Verified 2026-09-24: 133 rows, every device unique across all its failing
-- models (see verification A). Reviewed at
-- ercotsetransformernamecorrecting_seed_review.csv. Examples: DUNLAP_AT1H reports AT1H@138
-- -> corrected AT1L; HRZN_SLR_T1 reports T1@34.5 -> T1_L; BEVO_HIGH reports
-- HIGH@69 -> LOW.
-- ============================================================================

INSERT INTO AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING (BRANCHDEVICEID, TRANSFORMERENDNAME)
WITH winding AS (
    SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, WINDINGNAME,
           CAST(NOMINALKV AS NUMBER(6,2)) AS NOMINALKV
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
    WHERE NOMINALKV <> 1
),
device AS (
    SELECT BRANCHDEVICEID, FROMSTATIONNAME AS STATION, TRANSFORMERENDNAME,
           CAST(KVLEVEL AS NUMBER(6,2)) AS DEVICEKV,
           GREATEST(DATEACTIVESTART, '2022-01-01'::TIMESTAMP_NTZ) AS ACTIVE_FROM,
           DATEACTIVEEND AS ACTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE BRANCHDEVICETYPE = 'Transformer' AND DATEACTIVEEND >= '2022-01-01'
),
pairs AS (                                     -- (device, model) pairs whose windows overlap
    SELECT d.*, e.CIMFILEID
    FROM device d
    JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
      ON e.EFFECTIVE_FROM < d.ACTIVE_TO AND e.EFFECTIVE_TO > d.ACTIVE_FROM
),
failing AS (                                   -- reported name has no winding at the device kV
    SELECT p.* FROM pairs p
    WHERE NOT EXISTS (SELECT 1 FROM winding w
                       WHERE w.CIMFILEID = p.CIMFILEID AND w.STATION = p.STATION
                         AND w.WINDINGNAME = p.TRANSFORMERENDNAME
                         AND ABS(w.NOMINALKV - p.DEVICEKV) <= 0.05)
)
SELECT f.BRANCHDEVICEID, MIN(k.WINDINGNAME)
FROM failing f
JOIN winding n                                 -- the transformer the reported name points at
  ON n.CIMFILEID = f.CIMFILEID AND n.STATION = f.STATION AND n.WINDINGNAME = f.TRANSFORMERENDNAME
JOIN winding k                                 -- its winding at the device kV = the corrected name
  ON k.CIMFILEID = n.CIMFILEID AND k.STATION = n.STATION AND k.TRANSFORMERNAME = n.TRANSFORMERNAME
 AND ABS(k.NOMINALKV - f.DEVICEKV) <= 0.05
GROUP BY f.BRANCHDEVICEID
HAVING COUNT(DISTINCT k.WINDINGNAME) = 1;      -- verified: 133 devices, every one unique


-- ============================================================================
-- 4. AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP - device -> each real winding of its
--    transformer, strict join
--
-- One row per (CIM model, SE transformer device, real winding of that device's
-- transformer) - including the winding the device itself reports. The join
-- requires winding name AND kV to agree (ABS diff <= 0.05); the reported name
-- is tried first, the name-correcting-table name second.
--
-- Why IN (reported, fixed) rather than COALESCE: ERCOT renames windings
-- between models - PEARSALL 69_4 had both windings named 138_69_4 (at 138 and
-- 69) until model 204, then the 69 side became 138_69_4_L. The reported name
-- is right in the old models and the correction is right in the new; the kV match
-- picks whichever is correct for that model, so both must be tried.
--
-- COLUMNS
--   DEVICEKV      the device's own KVLEVEL - the voltage ERCOT reports flow on.
--   TRANSFORMERNAME/WINDINGNAME/NOMINALKV  one real winding of that device's
--                  transformer. A device with a 2-winding transformer produces
--                  2 rows (itself + the other winding); a star leg with only
--                  one real winding produces 1 row (itself only).
--
-- NOMINALKV = 1 rows are excluded throughout: they are fictitious star points
-- used to model 3-winding banks as three star-equivalent legs. ACSSW's bank is
-- three TRANSFORMERNAME entries (AX1H/AX1L/AX1T), each a real winding plus a
-- 1 kV leg, so TRANSFORMERNAME is per-LEG there, not per-bank.
--
-- Verified 2026-09-24 with this form: 473,250 of 473,485 (device, model) pairs
-- mapped, 0 devices resolving to more than one transformer in a model, at most
-- 1 winding differing from DEVICEKV per (model, device) - i.e. the mirror is
-- never ambiguous by construction (see verification C, D).
-- ============================================================================

CREATE OR REPLACE VIEW AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP AS
WITH winding AS (
    SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, WINDINGNAME,
           CAST(NOMINALKV AS NUMBER(6,2)) AS NOMINALKV
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
    WHERE NOMINALKV <> 1                       -- fictitious star points
),
device AS (
    SELECT d.BRANCHDEVICEID, d.BRANCHDEVICENAME, d.FROMSTATIONNAME AS STATION,
           d.TRANSFORMERENDNAME, f.TRANSFORMERENDNAME AS FIXEDENDNAME,
           CAST(d.KVLEVEL AS NUMBER(6,2)) AS DEVICEKV
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE d
    LEFT JOIN AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING f ON f.BRANCHDEVICEID = d.BRANCHDEVICEID
    WHERE d.BRANCHDEVICETYPE = 'Transformer'
)
SELECT DISTINCT
    k.CIMFILEID, d.BRANCHDEVICEID, d.BRANCHDEVICENAME, d.STATION, d.DEVICEKV,
    k.TRANSFORMERNAME, k.WINDINGNAME, k.NOMINALKV
FROM device d
JOIN winding n                                 -- name AND kV must agree; reported name first, correction second
  ON n.STATION = d.STATION
 AND n.WINDINGNAME IN (d.TRANSFORMERENDNAME, d.FIXEDENDNAME)
 AND ABS(n.NOMINALKV - d.DEVICEKV) <= 0.05
JOIN winding k                                 -- all real windings of that transformer
  ON k.CIMFILEID = n.CIMFILEID AND k.STATION = n.STATION AND k.TRANSFORMERNAME = n.TRANSFORMERNAME;


-- ============================================================================
-- 5. VERIFICATION
-- ============================================================================

-- A. Name-correcting table sanity. First MUST return 133. Second MUST return 0 rows - a
--    device the seed excluded because the corrected name was not unique
--    (rerun of the seed's SELECT with the HAVING flipped).
SELECT COUNT(*) AS FIX_TABLE_ROWS FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERNAMECORRECTING;

WITH winding AS (
    SELECT DISTINCT CIMFILEID, STATION, TRANSFORMERNAME, WINDINGNAME,
           CAST(NOMINALKV AS NUMBER(6,2)) AS NOMINALKV
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
    WHERE NOMINALKV <> 1
),
device AS (
    SELECT BRANCHDEVICEID, FROMSTATIONNAME AS STATION, TRANSFORMERENDNAME,
           CAST(KVLEVEL AS NUMBER(6,2)) AS DEVICEKV,
           GREATEST(DATEACTIVESTART, '2022-01-01'::TIMESTAMP_NTZ) AS ACTIVE_FROM,
           DATEACTIVEEND AS ACTIVE_TO
    FROM AW.DBO.ISOERCOTSEBRANCHDEVICE
    WHERE BRANCHDEVICETYPE = 'Transformer' AND DATEACTIVEEND >= '2022-01-01'
),
pairs AS (
    SELECT d.*, e.CIMFILEID
    FROM device d
    JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
      ON e.EFFECTIVE_FROM < d.ACTIVE_TO AND e.EFFECTIVE_TO > d.ACTIVE_FROM
),
failing AS (
    SELECT p.* FROM pairs p
    WHERE NOT EXISTS (SELECT 1 FROM winding w
                       WHERE w.CIMFILEID = p.CIMFILEID AND w.STATION = p.STATION
                         AND w.WINDINGNAME = p.TRANSFORMERENDNAME
                         AND ABS(w.NOMINALKV - p.DEVICEKV) <= 0.05)
)
SELECT f.BRANCHDEVICEID, COUNT(DISTINCT k.WINDINGNAME) AS N_CANDIDATES
FROM failing f
JOIN winding n
  ON n.CIMFILEID = f.CIMFILEID AND n.STATION = f.STATION AND n.WINDINGNAME = f.TRANSFORMERENDNAME
JOIN winding k
  ON k.CIMFILEID = n.CIMFILEID AND k.STATION = n.STATION AND k.TRANSFORMERNAME = n.TRANSFORMERNAME
 AND ABS(k.NOMINALKV - f.DEVICEKV) <= 0.05
GROUP BY f.BRANCHDEVICEID
HAVING COUNT(DISTINCT k.WINDINGNAME) > 1;      -- MUST return 0 rows

-- B. CIM-effective contiguity. First MUST return 0 - every row's EFFECTIVE_TO
--    equals the next row's EFFECTIVE_FROM. Second: earliest EFFECTIVE_FROM
--    MUST be <= 2022-01-01.
SELECT COUNT(*) AS NON_CONTIGUOUS_ROWS
FROM (
    SELECT EFFECTIVE_TO,
           LEAD(EFFECTIVE_FROM) OVER (ORDER BY EFFECTIVE_FROM) AS NEXT_FROM
    FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE
)
WHERE NEXT_FROM IS NOT NULL AND EFFECTIVE_TO <> NEXT_FROM;

SELECT MIN(EFFECTIVE_FROM) AS EARLIEST_EFFECTIVE_FROM FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE;

-- C. MUST return 0. A device may resolve to only one TRANSFORMERNAME per model.
SELECT COUNT(*) AS AMBIGUOUS_DEVICES
FROM (
    SELECT CIMFILEID, BRANCHDEVICEID
    FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP
    GROUP BY CIMFILEID, BRANCHDEVICEID
    HAVING COUNT(DISTINCT TRANSFORMERNAME) > 1
);

-- D. MUST return 0. Mirror uniqueness: no (model, device) pair may have more
--    than one distinct NOMINALKV differing from DEVICEKV - this replaces the
--    old runtime HAVING guard in the procedure's mirror leg.
SELECT COUNT(*) AS AMBIGUOUS_MIRROR_PAIRS
FROM (
    SELECT CIMFILEID, BRANCHDEVICEID
    FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP
    WHERE ABS(NOMINALKV - DEVICEKV) > 0.05
    GROUP BY CIMFILEID, BRANCHDEVICEID
    HAVING COUNT(DISTINCT NOMINALKV) > 1
);

-- E. MUST return 0. No transformer has more than two real voltages.
SELECT COUNT(*) AS TRANSFORMERS_WITH_GT2_REAL_KV
FROM (
    SELECT CIMFILEID, STATION, TRANSFORMERNAME
    FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING
    WHERE NOMINALKV <> 1
    GROUP BY CIMFILEID, STATION, TRANSFORMERNAME
    HAVING COUNT(DISTINCT NOMINALKV) > 2
);

-- F. Devices carrying flow on a loaded day with no map row for the model in
--    force. Run after every CIM publish; adjust the date to a day you have
--    loaded. Expected residual, NOT bugs:
--      FAYETT AT2H_H / AT2L_H / AT2T_H   - 0 MW, dead
--      GARZA 1_138_1_H / 1_69_1_H,
--      MDLNE AXFMR1H / AXFMR1L           - BOTH real sides are reported as
--                                          devices; deliberately left
--                                          unmapped (see SP header) - must
--                                          NOT be mirrored
--      PCT KT1                           - winding table lagged the
--                                          station's first model by one
--                                          model period
--    Anything else new -> candidate for the name-correcting table.

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
-- LEFT JOIN AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
--        ON '2026-07-01 12:00:00'::TIMESTAMP_NTZ >= e.EFFECTIVE_FROM
--       AND '2026-07-01 12:00:00'::TIMESTAMP_NTZ <  e.EFFECTIVE_TO
-- WHERE NOT EXISTS (
--     SELECT 1 FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP m
--     WHERE m.CIMFILEID = e.CIMFILEID AND m.BRANCHDEVICEID = d.BRANCHDEVICEID
-- )
-- ORDER BY d.MAX_ABS_MW DESC;

-- G. Spot check, for the model with EFFECTIVE_TO = 9999-12-31:
--    STP MT1A device @345      -> windings 345 & 25 (GSU, mirror makes gen visible)
--    ACSSW AX1HH device @345   -> single winding 345 (star leg, no mirror)
--    DUNLAP AT1H device @138   -> via correction (AT1L) -> windings 345 & 138
--    PEARSALL 138_69_4 @69     -> windings 138 & 69
SELECT STATION, BRANCHDEVICENAME, DEVICEKV, TRANSFORMERNAME, WINDINGNAME, NOMINALKV
FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP
WHERE CIMFILEID = (SELECT CIMFILEID FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE
                    WHERE EFFECTIVE_TO = '9999-12-31')
  AND STATION IN ('STP','ACSSW','DUNLAP','PEARSALL')
ORDER BY STATION, BRANCHDEVICENAME, NOMINALKV;
