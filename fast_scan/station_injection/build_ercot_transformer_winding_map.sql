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
-- Pure mapping CIMFILEID <-> schedule row. CIMFILE.CIMDATE = schedule.EFFECTIVE_THROUGH
-- is the only link between the two tables, so it is the join key; every DATE
-- in the output comes from the schedule.
--
-- EFFECTIVE_TO is the NEXT loaded row's start, not the schedule's own
-- EFFECTIVE_THROUGH/NEXT_PRODUCTION_LOAD: ERCOT skipped 2024Dec.L3 (schedule
-- row exists, no CIM file), so 2024Dec.L2 (CIMFILEID 85) stays in force
-- 2024-12-10 23:00 -> 2025-01-07 23:00.
--
-- Verified 2026-09-24: the SE switches to a new model at 23:00 on the eve of
-- the schedule's PRODUCTION_LOAD, not at midnight - retired devices' last
-- sample is 22:57 that eve for 216 of 236 retiring devices, and new devices'
-- first sample is 23:57 that eve for 637 of 757 (00:xx on the day for the
-- other 120). EFFECTIVE_FROM is therefore PRODUCTION_LOAD minus one hour.
--
-- MP_MarketModel = test models, published ~45 days early, never in force
-- (188 vs 205 share CIMDATE 2026-07-14); excluded because they are not
-- production files, nothing to do with windings.
--
-- Re-posted models: a schedule row can map to TWO CIMFILEIDs (2023Sep.L4 ->
-- 15 and 18; 2025Dec.L1 -> 141 and 145). The view lists both - they are the
-- same model. Downstream this is harmless because the winding table holds
-- only one of each pair; verification H asserts that.
--
-- Winding coverage is NOT this view's job: models with no winding rows
-- (currently 377-392, 2026-07-29 onward) still resolve; they simply produce
-- no map rows, so transformers lose their mirror until the winding loader
-- catches up - verification F is where that shows.
--
-- Note also that CIMFILEID is not monotone with model recency - CIMFILEID 376
-- is a 2023-07-18 model loaded late - so never pick "the newest model" by
-- MAX(CIMFILEID).
--
-- Verified 2026-09-24: 306 rows / 304 loads, contiguous, first EFFECTIVE_FROM
-- 2020-01-07 23:00.
-- ============================================================================

CREATE OR REPLACE VIEW AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE AS
WITH models AS (                                -- production CIM files; test models are never in force
    SELECT CIMFILEID, CIMDATE
    FROM AW.DBO.CIMFILE
    WHERE ISOMARKETID = 6
      AND CIMPATH NOT LIKE '%MP_MarketModel%'
),
loads AS (                                      -- schedule rows that have a CIM file; skipped loads drop out
    SELECT p.CIM_LABEL, p.PRODUCTION_LOAD, p.EFFECTIVE_THROUGH
    FROM AWDEV.ERCOTRT.ERCOT_PRODUCTION_LOAD_SCHEDULE p
    WHERE EXISTS (SELECT 1 FROM models m WHERE m.CIMDATE = p.EFFECTIVE_THROUGH)
),
ranges AS (                                     -- in force from 23:00 the eve of the load until the next load does the same
    SELECT CIM_LABEL, PRODUCTION_LOAD, EFFECTIVE_THROUGH,
           DATEADD(HOUR, -1, PRODUCTION_LOAD::TIMESTAMP_NTZ)                          AS EFFECTIVE_FROM,
           COALESCE(LEAD(DATEADD(HOUR, -1, PRODUCTION_LOAD::TIMESTAMP_NTZ))
                        OVER (ORDER BY PRODUCTION_LOAD),
                    '9999-12-31'::TIMESTAMP_NTZ)                                      AS EFFECTIVE_TO   -- exclusive
    FROM loads
)
SELECT r.CIM_LABEL, m.CIMFILEID, r.PRODUCTION_LOAD, r.EFFECTIVE_FROM, r.EFFECTIVE_TO
FROM ranges r
JOIN models m ON m.CIMDATE = r.EFFECTIVE_THROUGH;


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
failing AS (                                   -- anti-join: reported name has no winding at the device kV
    SELECT p.*                                 -- (a correlated NOT EXISTS with the ABS() inequality is
    FROM pairs p                               --  "Unsupported subquery type" inside INSERT on Snowflake)
    LEFT JOIN winding w
      ON w.CIMFILEID = p.CIMFILEID AND w.STATION = p.STATION
     AND w.WINDINGNAME = p.TRANSFORMERENDNAME
     AND ABS(w.NOMINALKV - p.DEVICEKV) <= 0.05
    WHERE w.CIMFILEID IS NULL
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
failing AS (                                   -- anti-join, as in the seed
    SELECT p.*
    FROM pairs p
    LEFT JOIN winding w
      ON w.CIMFILEID = p.CIMFILEID AND w.STATION = p.STATION
     AND w.WINDINGNAME = p.TRANSFORMERENDNAME
     AND ABS(w.NOMINALKV - p.DEVICEKV) <= 0.05
    WHERE w.CIMFILEID IS NULL
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

-- B. CIM-effective contiguity, computed over DISTINCT (EFFECTIVE_FROM,
--    EFFECTIVE_TO) - re-posted loads produce two CIMFILEID rows per range, and
--    those duplicates would otherwise look like overlaps. First MUST return 0
--    - every distinct range's EFFECTIVE_TO equals the next range's
--    EFFECTIVE_FROM. Second: earliest EFFECTIVE_FROM MUST be <= 2022-01-01.
SELECT COUNT(*)
FROM (SELECT EFFECTIVE_TO, LEAD(EFFECTIVE_FROM) OVER (ORDER BY EFFECTIVE_FROM) NXT
      FROM (SELECT DISTINCT EFFECTIVE_FROM, EFFECTIVE_TO FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE))
WHERE NXT IS NOT NULL AND NXT <> EFFECTIVE_TO;

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

-- G. Spot check, for the newest model THAT HAS windings (not simply the model
--    with EFFECTIVE_TO = 9999-12-31 - that model may itself have no windings
--    loaded yet, see verification I; and never MAX(CIMFILEID), see §1):
--    STP MT1A device @345      -> windings 345 & 25 (GSU, mirror makes gen visible)
--    ACSSW AX1HH device @345   -> single winding 345 (star leg, no mirror)
--    DUNLAP AT1H device @138   -> via correction (AT1L) -> windings 345 & 138
--    PEARSALL 138_69_4 @69     -> windings 138 & 69
SELECT STATION, BRANCHDEVICENAME, DEVICEKV, TRANSFORMERNAME, WINDINGNAME, NOMINALKV
FROM AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP
WHERE CIMFILEID = (SELECT e.CIMFILEID FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
                    WHERE EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w WHERE w.CIMFILEID = e.CIMFILEID)
                    ORDER BY e.EFFECTIVE_FROM DESC LIMIT 1)
  AND STATION IN ('STP','ACSSW','DUNLAP','PEARSALL')
ORDER BY STATION, BRANCHDEVICENAME, NOMINALKV;

-- H. MUST return 0. A load with more than one winding-bearing CIMFILEID would
--    make the SP's mirror double-count for that period - the re-posting
--    duplicates the view now carries (see §1) must always resolve to at most
--    one CIMFILEID that actually has windings.
SELECT COUNT(*) AS LOADS_WITH_2PLUS_WINDING_MODELS
FROM (
    SELECT e.CIM_LABEL
    FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
    WHERE EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w WHERE w.CIMFILEID = e.CIMFILEID)
    GROUP BY e.CIM_LABEL
    HAVING COUNT(*) > 1
);

-- I. Informational - loads in force with NO winding rows at all: these
--    periods have no transformer mirrors (see verification F / SP header).
--    Expect 18 (re-post twin) and 141 (re-post twin) plus the newest models
--    until the winding loader catches up.
SELECT e.CIM_LABEL, e.CIMFILEID, e.EFFECTIVE_FROM, e.EFFECTIVE_TO
FROM AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE e
WHERE NOT EXISTS (SELECT 1 FROM AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING w WHERE w.CIMFILEID = e.CIMFILEID)
  AND e.EFFECTIVE_TO > '2022-01-01'
ORDER BY e.EFFECTIVE_FROM;
