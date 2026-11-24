# ERCOT Bus-Grain SE Net Injection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `AWDEV.ERCOTRT.ERCOTBUSINJECTION`, SE net injection per PSSE bus per hourly snapshot, from July 2023 onward, with the map tables that place every SE branch end on a CIM bus.

**Architecture:** Three SQL files, run in order by sdalvi as `AW_ACCESS`. A map-build proc places every SE device active in each CIM file's in-force window on its from-bus and to-bus (lines by name against `ERCOTLINESEGMENT`, transformers through `ERCOTSETRANSFORMERWINDINGMAP` to the winding's own bus) and lists the CIM lines with no SE device. An orientation proc settles, from flow data, which end of a same-station device gets FROMMW. The loader is a copy of the V2 station loader's skeleton that joins flows to the map and sums by bus.

**Tech Stack:** Snowflake SQL stored procedures (SQL scripting, `EXECUTE AS CALLER`), verified through read-only SELECTs from Python (`awconnect`, role `AI_READ_ONLY`).

**Spec:** `stationinjection/BUS_INJECTION_DESIGN.md` (decisions 1 to 9, verification section).

## Global Constraints

- Role split: the implementer holds `AI_READ_ONLY` and can only SELECT. Every CREATE, CALL, GRANT, INSERT is run by sdalvi. Each task therefore prototypes its SELECT logic read-only first, then hands the file to sdalvi, then verifies. Never attempt DDL from the implementer's session.
- Python: `/workspaces/scratch-workspace/.venv/bin/python`, `awconnect.configure("read_only")`, `snowflake.performQuery("AW", sql, warehouse=snowflake.READ_ONLY_WH, logInfo=False)`. Probe scripts go in `/tmp/probes/`.
- New objects live in `AWDEV.ERCOTRT`, names uppercase, no underscores in table names (`ERCOTSEBRANCHBUSMAP`, `ERCOTREDACTEDLINE`, `ERCOTSEBRANCHORIENTATION`, `ERCOTBUSINJECTION`), procs `SP_...` as in V2.
- Style of `sp_load_ercot_station_injection_v2.sql`: header block, no verbose comments inside the body, at most two temporary tables in the loader, delete-range-then-insert in a transaction, `EXCEPTION WHEN OTHER THEN ROLLBACK; RAISE;`.
- Snowflake traps already hit: correlated `NOT EXISTS ... OR` fails ("Unsupported subquery type"), use LEFT JOINs; `ROWS` is a reserved alias; `ERCOTLINESEGMENT.FROMNUM`, `TONUM` and `ERCOTTRANSFORMERWINDING.FROMNUM`, `TONUM` are VARCHAR, always `TRY_TO_NUMBER`; `AW.DBO.BRANCH.B1` is an empty string; `ISOERCOTSEBRANCH."TIMESTAMP"` needs the quotes.
- CIM file ids are not chronological. The model in force comes only from `ERCOTCIMEFFECTIVEDATE` (columns CIM_LABEL, CIMFILEID, PRODUCTION_LOAD, EFFECTIVE_FROM, EFFECTIVE_TO). A schedule window can carry two CIMFILEIDs (re-posted models, e.g. 141 and 145); every object keyed by in-force file uses the lower CIMFILEID of a window and nothing else.
- Sign convention: positive is flow from the bus into the branch, as in `ERCOTSTATIONINJECTION`.
- Commit after each task in `/tmp/station-injection` on branch `station-injection`; do not push.

## Review Focus

1. A re-posted model (two CIMFILEIDs sharing one EFFECTIVE_FROM) must not double the flow for that window. Test in Task 1 (map has one CIMFILEID per window) and Task 3 (no flow timestamp joins two CIMFILEIDs).
2. A transformer whose two windings share one WINDINGNAME (121 in file 387, e.g. 16TH_ST TRF1 `138_69_1` at 138 and 69 kV) must still get a mirror; keying the other winding by name would find none. Test in Task 1.
3. A retired SE device (82 transformers have a replaced device with a disjoint active window) must not appear in the map for a file whose window it does not overlap. Test in Task 1.
4. A 9xxxxx split-bus winding number must land on the station-kV fallback with `WINDINGBUSUNKNOWN`, not on a nonexistent bus and not dropped. Test in Task 1.
5. A range that crosses a model switch at 23:00 must take each snapshot's file from its own timestamp, not one file for the whole range. Test in Task 3 Step 4.

---

### Task 1: Map tables and map-build proc

**Files:**
- Create: `stationinjection/build_ercot_bus_injection_map.sql`
- Create: `/tmp/probes/map_prototype.py` (read-only prototype of the map SELECT, not committed)

**Interfaces:**
- Consumes: `AW.DBO.ISOERCOTSEBRANCHDEVICE` (BRANCHDEVICEID, BRANCHDEVICENAME, BRANCHDEVICETYPE in ('Line','Transformer'), KVLEVEL, FROMSTATIONNAME, TOSTATIONNAME, DATEACTIVESTART, DATEACTIVEEND, TRANSFORMERENDNAME); `AWDEV.ERCOTRT.ERCOTLINESEGMENT`; `AWDEV.ERCOTRT.ERCOTTRANSFORMERWINDING` (CIMFILEID, STATION, TRANSFORMERNAME, WINDINGNAME, NOMINALKV, FROMNUM, TONUM, WINDINGTEID, TRANSFORMERRDFID); view `AWDEV.ERCOTRT.ERCOTSETRANSFORMERWINDINGMAP` (CIMFILEID, BRANCHDEVICEID, BRANCHDEVICENAME, STATION, DEVICEKV, TRANSFORMERNAME, WINDINGNAME, NOMINALKV); `AW.DBO.CIMCONNODE` + `AW.DBO.CIMSTATIONVOLTAGELEVEL` for names of transformer-only buses; `AWDEV.ERCOTRT.ERCOTCIMEFFECTIVEDATE`.
- Produces:
  - Table `AWDEV.ERCOTRT.ERCOTSEBRANCHORIENTATION` (BRANCHDEVICEID NUMBER NOT NULL, FROMBUSNUMBER NUMBER NOT NULL, TOBUSNUMBER NUMBER NOT NULL, NOTE VARCHAR(255)). Hand-maintained, created empty.
  - Table `AWDEV.ERCOTRT.ERCOTSEBRANCHBUSMAP` (CIMFILEID NUMBER, BRANCHDEVICEID NUMBER, BRANCHDEVICENAME VARCHAR(255), BRANCHDEVICETYPE VARCHAR(31), FROMBUSNUMBER NUMBER, FROMBUSNAME VARCHAR(128), FROMSTATION VARCHAR(128), FROMKV NUMBER(6,2), TOBUSNUMBER NUMBER, TOBUSNAME VARCHAR(128), TOSTATION VARCHAR(128), TOKV NUMBER(6,2), CIMFROMBUSNUMBER NUMBER, CIMTOBUSNUMBER NUMBER, FROMCONNECTIVITYNODE VARCHAR(128), TOCONNECTIVITYNODE VARCHAR(128), FROMELECTRICALBUS VARCHAR(128), TOELECTRICALBUS VARCHAR(128), CIMRDFID VARCHAR(64), MATCHMETHOD VARCHAR(32), ORIENTATIONMETHOD VARCHAR(32), ORIENTATIONSCORE1 NUMBER(10,2), ORIENTATIONSCORE2 NUMBER(10,2), LINEFILEID NUMBER, WINDINGFILEID NUMBER, NODEFILEID NUMBER, BUILDTIMESTAMP TIMESTAMP_NTZ). Primary grain (CIMFILEID, BRANCHDEVICEID). TOMW is booked only when TOBUSNUMBER is not null.
  - Table `AWDEV.ERCOTRT.ERCOTREDACTEDLINE` (CIMFILEID, LINENAME, SEGMENTNAME, SEGMENTCLASS, SEGMENTRDFID, FROMBUSNUMBER, FROMBUSNAME, FROMSTATION, FROMKV, TOBUSNUMBER, TOBUSNAME, TOSTATION, TOKV, FROMVISIBLE BOOLEAN, TOVISIBLE BOOLEAN, BUILDTIMESTAMP).
  - Proc `AWDEV.ERCOTRT.SP_BUILD_ERCOT_BUS_INJECTION_MAP()` RETURNS VARCHAR: deletes and refills both tables for every window in `ERCOTCIMEFFECTIVEDATE` whose lower CIMFILEID has a line file at or before it; returns row counts and the count by MATCHMETHOD. Existing rows with ORIENTATIONMETHOD in ('OVERRIDE','CARRIED','DERIVEDCLEAN','DERIVEDFIT') are preserved by copying them back when (CIMFILEID, BRANCHDEVICEID, CIMFROMBUSNUMBER, CIMTOBUSNUMBER) is unchanged, so a rebuild does not undo Task 2.
  - MATCHMETHOD values: `LINENAME`, `LINESEGMENT`, `WINDINGKV`, `WINDINGNAME`, `STATIONKV`, `STATIONKV_AMBIGUOUS`, `WINDINGBUSUNKNOWN`, `NONE`.
  - ORIENTATIONMETHOD values: `STATION`, `KV`, `WINDINGNAME`, `NONE`, `SAMEBUS`, `UNRESOLVED`, and from Task 2 `OVERRIDE`, `CARRIED`, `DERIVEDCLEAN`, `DERIVEDFIT`.

Rules the SELECT implements (spec decisions 3, 4, 7, 8, 9):

- Window set: one row per EFFECTIVE_FROM in `ERCOTCIMEFFECTIVEDATE` with CIMFILEID = MIN(CIMFILEID) of that window. LINEFILEID = that CIMFILEID if `ERCOTLINESEGMENT` has it, else the CIMFILEID of the latest earlier window that does; WINDINGFILEID and NODEFILEID the same against `ERCOTTRANSFORMERWINDING` and `CIMCONNODE`. Windows with no LINEFILEID are skipped.
- Device set per window: `BRANCHDEVICETYPE IN ('Line','Transformer')` and `DATEACTIVESTART < EFFECTIVE_TO AND DATEACTIVEEND >= EFFECTIVE_FROM`.
- Bus dimension per window: UNION of line ends (TRY_TO_NUMBER(FROMNUM), FROMCNGPSSENAME, FROMSTATION, FROMKV and the TO columns) from LINEFILEID and winding buses (TRY_TO_NUMBER(FROMNUM), STATION, NOMINALKV, name from a line end on that bus in the same window else `CIMCONNODE.PSSEBUSNAME` in NODEFILEID else null) from WINDINGFILEID, `NOMINALKV <> 1` only.
- Line match, in order, first hit wins, compared with UPPER on both sides: (a) `LINENAME` when the line has one segment in LINEFILEID; (b) `LINENAME || SEGMENTNAME` when the line has more than one segment. A hit counts only if the set {FROMSTATION, TOSTATION} of the segment equals {FROMSTATIONNAME, TOSTATIONNAME} of the device. If two or more segments hit, treat as no hit. Two-station hit: FROMBUS = end whose station = FROMSTATIONNAME, ORIENTATIONMETHOD `STATION`. Same-station hit with different buses: FROMBUSNUMBER = TOBUSNUMBER = LEAST(CIMFROM, CIMTO), ORIENTATIONMETHOD `UNRESOLVED`, CIMFROMBUSNUMBER/CIMTOBUSNUMBER keep the export order. Same-station hit with one bus: both ends on it, `SAMEBUS`.
- Transformer match: own winding = `ERCOTSETRANSFORMERWINDINGMAP` row for the device in WINDINGFILEID with ABS(NOMINALKV - DEVICEKV) <= 0.05 and, when two rows qualify (same-kV bank), WINDINGNAME = TRANSFORMERENDNAME (`WINDINGNAME`), else `WINDINGKV`. FROMBUSNUMBER = that winding's FROMNUM looked up in `ERCOTTRANSFORMERWINDING` on (CIMFILEID, STATION, TRANSFORMERNAME, WINDINGNAME, NOMINALKV). Mirror: the transformer's other real winding is the `ERCOTTRANSFORMERWINDING` row with the same (CIMFILEID, STATION, TRANSFORMERNAME), `NOMINALKV <> 1`, and a different WINDINGTEID; if exactly one exists and its FROMNUM differs from the own bus, TOBUSNUMBER = its FROMNUM, ORIENTATIONMETHOD `KV` (or `WINDINGNAME`); if none, TOBUSNUMBER null, `NONE`. No PAR exclusion. CIMRDFID = TRANSFORMERRDFID.
- Fallback for any end still without a bus: if its (station, kV) has exactly one bus in the bus dimension, that bus, `STATIONKV`; if several, the lowest number, `STATIONKV_AMBIGUOUS`; a transformer whose own winding FROMNUM is not in the bus dimension gets this with `WINDINGBUSUNKNOWN`; if the station-kV has no bus at all, FROMBUSNUMBER null and `NONE`. Fallback transformer ends get no mirror. MATCHMETHOD records the FROM end's method; a line whose two ends used different methods records the FROM end's.
- Redacted: segment in LINEFILEID with FROMKV >= 69 and TOKV >= 69, FROMSTATION <> TOSTATION, no map row with its SEGMENTRDFID in that window, and no mapped line device in that window with the same station set and ABS(KVLEVEL - FROMKV) <= 0.05. FROMVISIBLE = some map row in the window has FROMBUSNUMBER or TOBUSNUMBER equal to the segment's from-bus.

- [ ] **Step 1: Prototype the map SELECT read-only for window CIMFILEID 387 (2026-09-01 23:00 to 2026-09-15 23:00) in `/tmp/probes/map_prototype.py`, printing counts by (BRANCHDEVICETYPE, MATCHMETHOD, ORIENTATIONMETHOD)**

Expected, from the probes already run on file 387: Line devices mapped by `LINENAME` + `LINESEGMENT` at least 8,400; `UNRESOLVED` between 450 and 570; `SAMEBUS` 3 or fewer; Transformer `WINDINGKV` + `WINDINGNAME` at least 2,700, of which `WINDINGNAME` between 5 and 12; `WINDINGBUSUNKNOWN` between 40 and 70; `STATIONKV_AMBIGUOUS` under 40; `NONE` under 10. Every active device appears exactly once.

- [ ] **Step 2: Assert the Review Focus cases in the same prototype**

```sql
-- one CIMFILEID per window
SELECT EFFECTIVE_FROM, COUNT(DISTINCT CIMFILEID) FROM <window CTE> GROUP BY 1 HAVING COUNT(DISTINCT CIMFILEID) > 1;   -- expect 0 rows
-- shared winding name still mirrored
SELECT * FROM <map CTE> WHERE BRANCHDEVICENAME LIKE '16TH_ST%' ;   -- TOBUSNUMBER not null, FROMBUSNUMBER <> TOBUSNUMBER
-- retired device absent
SELECT COUNT(*) FROM <map CTE> WHERE BRANCHDEVICEID IN (6174, 6175, 6176, 6296);   -- expect 0 (AZ devices ended 2019-07-16)
-- split-bus winding on fallback
SELECT BRANCHDEVICENAME, MATCHMETHOD, FROMBUSNUMBER FROM <map CTE> WHERE BRANCHDEVICETYPE = 'Transformer' AND FROMSTATION IN ('DCSES','EXPSW','LEG','NEDIN') AND MATCHMETHOD = 'WINDINGBUSUNKNOWN';   -- at least one row, FROMBUSNUMBER not null
-- Braunig and Bosque placement
SELECT BRANCHDEVICENAME, FROMBUSNUMBER, TOBUSNUMBER, ORIENTATIONMETHOD FROM <map CTE> WHERE BRANCHDEVICENAME IN ('BOSQUESW_FMR1','BOS_WHI','OLKW_BOS','LEGGEN01');
-- expect BOSQUESW_FMR1 246 -> 150141 KV; BOS_WHI 252 -> 241 STATION; OLKW_BOS 252 -> 37410 STATION; LEGGEN01 46020 -> 46020 UNRESOLVED (CIM 49208 / 46020)
```

- [ ] **Step 3: Write `stationinjection/build_ercot_bus_injection_map.sql`**: header block in the V2 style, the three CREATE TABLE IF NOT EXISTS statements, `CREATE OR REPLACE PROCEDURE AWDEV.ERCOTRT.SP_BUILD_ERCOT_BUS_INJECTION_MAP() RETURNS VARCHAR LANGUAGE SQL EXECUTE AS CALLER`, and a Verification section holding the Step 1 count query and the Step 2 queries rewritten against the real tables, plus `SELECT MATCHMETHOD, COUNT(*) FROM AWDEV.ERCOTRT.ERCOTSEBRANCHBUSMAP WHERE CIMFILEID = 387 GROUP BY 1` and the list of `STATIONKV_AMBIGUOUS` and `NONE` devices with their station and kV.

- [ ] **Step 4: Hand the file to sdalvi** with the single command to run: `CALL AWDEV.ERCOTRT.SP_BUILD_ERCOT_BUS_INJECTION_MAP();` and the grant `GRANT SELECT ON ALL TABLES IN SCHEMA AWDEV.ERCOTRT TO ROLE AI_READ_ONLY;`. Stop until sdalvi reports it ran.

- [ ] **Step 5: Run the Verification section read-only**

Expected: the Step 1 counts within the stated ranges for file 387; windows covered from the first window on or after 2021-12-21 through the current one (408); `ERCOTREDACTEDLINE` for file 387 between 110 and 140 ACLineSegment rows and between 70 and 95 SeriesCompensator rows.

- [ ] **Step 6: Commit**

```bash
cd /tmp/station-injection && git add stationinjection/build_ercot_bus_injection_map.sql && git commit -m "Bus injection map build: ERCOTSEBRANCHBUSMAP, ERCOTREDACTEDLINE, orientation override table"
```

### Task 2: Orientation derivation proc

**Files:**
- Create: `stationinjection/sp_derive_ercot_bus_orientation.sql`
- Create: `/tmp/probes/orientation_prototype.py` (read-only, not committed)

**Interfaces:**
- Consumes: `ERCOTSEBRANCHBUSMAP`, `ERCOTSEBRANCHORIENTATION`, `ERCOTREDACTEDLINE` from Task 1; `AW.DBO.ISOERCOTSEBRANCH` (BRANCHDEVICEID, "TIMESTAMP", FROMMW, TOMW); `AW.DBO.CIMCONNODE` (RESOURCENODEID by PSSEBUSNUMBER in NODEFILEID); `ERCOTTRANSFORMERWINDING` (buses with a winding in WINDINGFILEID).
- Produces: proc `AWDEV.ERCOTRT.SP_DERIVE_ERCOT_BUS_ORIENTATION(P_CIMFILEID NUMBER)` RETURNS VARCHAR that updates FROMBUSNUMBER, FROMBUSNAME, FROMSTATION, FROMKV, TOBUSNUMBER, TOBUSNAME, TOSTATION, TOKV, ORIENTATIONMETHOD, ORIENTATIONSCORE1, ORIENTATIONSCORE2 on that window's `UNRESOLVED` rows, and proc `AWDEV.ERCOTRT.SP_DERIVE_ERCOT_BUS_ORIENTATION_ALL()` that calls it for every window in `ERCOTSEBRANCHBUSMAP` in EFFECTIVE_FROM order.

Rules (spec decision 6):

- Order inside one call: (1) `OVERRIDE`: rows whose BRANCHDEVICEID is in `ERCOTSEBRANCHORIENTATION` and whose {FROMBUSNUMBER, TOBUSNUMBER} equals {CIMFROMBUSNUMBER, CIMTOBUSNUMBER}. (2) `CARRIED`: copy from the latest earlier window's row for the same device with the same unordered CIM bus pair and ORIENTATIONMETHOD in ('OVERRIDE','CARRIED','DERIVEDCLEAN','DERIVEDFIT'). (3) Derivation for the rest.
- Sample: hourly snapshots inside [EFFECTIVE_FROM, EFFECTIVE_TO) chosen by the V2 rule (most complete snapshot per hour bucket, at least half the active devices). Fewer than 200: return `'SKIPPED: n snapshots'` and leave rows `UNRESOLVED`. More than 400: keep every k-th so that about 400 remain.
- Known residual R(bus, t) = sum over map rows of the window with ORIENTATIONMETHOD <> 'UNRESOLVED' of FROMMW at FROMBUSNUMBER plus TOMW at TOBUSNUMBER where not null; zero where nothing is booked.
- For candidate c between A = CIMFROMBUSNUMBER and B = CIMTOBUSNUMBER with F = FROMMW, T = TOMW: SAF = mean|R(A) + F|, SAT = mean|R(A) + T|, SBF = mean|R(B) + F|, SBT = mean|R(B) + T| over the sample, nulls as zero. Clean(X) = X has no `CIMCONNODE` row with RESOURCENODEID in NODEFILEID, no `ERCOTTRANSFORMERWINDING` row with FROMNUM = X in WINDINGFILEID, no `ERCOTREDACTEDLINE` end in the window, and no other still-`UNRESOLVED` candidate touching X. Score1 (FROMMW to A, TOMW to B) and Score2 (the reverse): if Clean(A) and not Clean(B): Score1 = SAF, Score2 = SAT; if Clean(B) and not Clean(A): Score1 = SBT, Score2 = SBF; else Score1 = SAF + SBT, Score2 = SAT + SBF. If ABS(Score1 - Score2) >= 5 the lower score wins, method `DERIVEDCLEAN` when a clean bus decided it else `DERIVEDFIT`; otherwise stay `UNRESOLVED`. Scores are stored in ORIENTATIONSCORE1/2 in either case.
- Three passes: after each pass, newly settled rows join the known residual and the clean test is re-evaluated.
- Any call that changes rows requires `SP_LOAD_ERCOT_BUS_INJECTION` to be re-run for that window; the return string lists the windows changed so sdalvi knows which ranges to reload.

- [ ] **Step 1: Prototype one pass read-only for window 387 in `/tmp/probes/orientation_prototype.py`, 200 snapshots from 2026-09-01 23:00 onward, printing device, A, B, SAF, SAT, SBF, SBT, Clean(A), Clean(B), chosen method**

Expected: LEGGEN01 (CIM pair 49208 / 46020) and LEGGEN02 (46020 / 49209) settle with ABS(Score1 - Score2) above 100, and for the chosen orientation the mean |R(generator bus) + booked lead flow| is under 5 MW, meaning the lead cancels the GSU flow at 49208 or 49209; WAPGEN05 settles; at least 70 percent of candidates settle in pass 1; no settled device has both scores above 50.

- [ ] **Step 2: Write `stationinjection/sp_derive_ercot_bus_orientation.sql`** with both procs and a Verification section: count by ORIENTATIONMETHOD per CIMFILEID; the `UNRESOLVED` list with scores for the newest window; LEGGEN01, WAPGEN05, LEGGEN02 rows.

- [ ] **Step 3: Hand to sdalvi**: `CALL AWDEV.ERCOTRT.SP_DERIVE_ERCOT_BUS_ORIENTATION_ALL();`. Stop until it ran.

- [ ] **Step 4: Run the Verification section read-only**

Expected: for window 387, `UNRESOLVED` under 15 percent of same-station devices; every `UNRESOLVED` row has both scores stored; `CARRIED` dominates in windows after the first derived one.

- [ ] **Step 5: Commit**

```bash
cd /tmp/station-injection && git add stationinjection/sp_derive_ercot_bus_orientation.sql && git commit -m "Bus injection: derive same-station device orientation from bus residuals"
```

### Task 3: Target table and loader

**Files:**
- Create: `stationinjection/sp_load_ercot_bus_injection.sql`

**Interfaces:**
- Consumes: `ERCOTSEBRANCHBUSMAP` (Task 1, after Task 2), `ERCOTCIMEFFECTIVEDATE`, `ISOERCOTSEBRANCH`, `ISOERCOTSEBRANCHDEVICE`.
- Produces: table `AWDEV.ERCOTRT.ERCOTBUSINJECTION` ("TIMESTAMP" TIMESTAMP_NTZ(0), CIMFILEID NUMBER, BUSNUMBER NUMBER, BUSNAME VARCHAR(128), NMMSSTATIONCODE VARCHAR(128), KVLEVEL NUMBER(6,2), NETINJECTIONMW FLOAT) CLUSTER BY (TO_DATE("TIMESTAMP"), BUSNUMBER); proc `AWDEV.ERCOTRT.SP_LOAD_ERCOT_BUS_INJECTION(P_START_DATE DATE, P_END_DATE DATE)` RETURNS VARCHAR with the V2 return string format.

Rules: copy TMP_FLOW and TMP_SNAPSHOT from V2 verbatim (same padding, same half-the-devices rule); DELETE the range; INSERT from TMP_FLOW joined to TMP_SNAPSHOT, to the window set (one CIMFILEID per EFFECTIVE_FROM, row chosen per flow timestamp by `"TIMESTAMP" >= EFFECTIVE_FROM AND "TIMESTAMP" < EFFECTIVE_TO`), to the map on (CIMFILEID, BRANCHDEVICEID); two legs UNION ALL: FROMMW at FROMBUSNUMBER where not null, TOMW at TOBUSNUMBER where not null; GROUP BY timestamp, BUSNUMBER with MIN(BUSNAME), MIN(station), MIN(kV); ORDER BY 1, 3. A flow row whose device has no map row in its window is counted into a variable and reported in the return string as `unmapped_flow_rows`.

- [ ] **Step 1: Prototype the INSERT SELECT read-only for 2026-09-05 12:57 only, into a DataFrame**

Expected: between 8,000 and 10,500 bus rows; no flow timestamp in the week joins two CIMFILEIDs (`SELECT "TIMESTAMP", COUNT(DISTINCT CIMFILEID) ... HAVING > 1` returns nothing); SUM by station equals `ERCOTSTATIONINJECTION` summed over KVLEVEL at the same timestamp within 1 MW for every station except those holding a device listed in `AW.DBO.PARERCOTSTATION` (print those with the difference; expect each under 15 MW in magnitude, the PAR loss); BRAUNIG rows at 5475, 5474 and 170135 present.

- [ ] **Step 2: Write `stationinjection/sp_load_ercot_bus_injection.sql`**: header in V2 style, CREATE TABLE IF NOT EXISTS, the proc, Usage lines `CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_BUS_INJECTION('2023-07-13', '2023-07-31');` and the full range `('2023-07-13', '2026-09-24')`, and a Verification section containing the Step 1 station roll-up query against the real table, the Braunig 2026-06-23 13:57 query, and `SELECT COUNT(*), COUNT(DISTINCT "TIMESTAMP") FROM AWDEV.ERCOTRT.ERCOTBUSINJECTION WHERE "TIMESTAMP" >= '2026-09-01' AND "TIMESTAMP" < '2026-09-08'`.

- [ ] **Step 3: Hand to sdalvi**: run the file, then `CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_BUS_INJECTION('2026-09-01', '2026-09-07');` first (one week spanning the 2026-09-01 23:00 switch into file 387). Stop until it ran.

- [ ] **Step 4: Run the Verification section read-only for that week**

Expected: 168 distinct timestamps or the same count as `ERCOTSTATIONINJECTION` has in the week; rows before 2026-09-01 23:00 carry the previous window's CIMFILEID and rows after carry 387; station roll-up within 1 MW except PAR stations; `unmapped_flow_rows` in the return string under 0.1 percent of flow rows.

- [ ] **Step 5: Commit**

```bash
cd /tmp/station-injection && git add stationinjection/sp_load_ercot_bus_injection.sql && git commit -m "Bus injection loader SP_LOAD_ERCOT_BUS_INJECTION"
```

### Task 4: Verification script, full load, Opus grade

**Files:**
- Create: `stationinjection/verify_ercot_bus_injection.sql`
- Create: `stationinjection/verify_ercot_bus_injection.py` (runs every query in the .sql read-only and prints results; same `awconnect` pattern as `benchmark_vs_stationload.py`)

**Interfaces:**
- Consumes: `ERCOTBUSINJECTION`, `ERCOTSEBRANCHBUSMAP`, `ERCOTREDACTEDLINE`, `ERCOTSTATIONINJECTION`, `AW.DBO.ISOERCOTSCEDGEN` + `AW.DBO.CPNODE` + `CIMCONNODE` resource nodes for the known-tie check.
- Produces: a printed report, saved to `stationinjection/output/bus_injection_verification_<date>.txt`.

Queries (spec Verification section), each with its pass line:

1. Station roll-up for 24 sampled timestamps (one per month July 2023 to September 2026, 12:57): max absolute station difference vs `ERCOTSTATIONINJECTION` summed over kV, excluding PAR stations. Pass: under 1 MW at every sample.
2. Switching-bus residual: buses with no resource node, no winding, no redacted end, no `UNRESOLVED` device, over the same 24 timestamps: 99th percentile of |NETINJECTIONMW|. Pass: under 2 MW.
3. Known ties: CHB bus 40255, CITGO_NO bus 8426, GRNBELT bus 38575, hourly over September 2026, correlation of the bus injection with the PUN's SCED net telemetry as in `pun_analysis/PUN_BACKOUT_FINDINGS.md`. Pass: above 0.99 for each.
4. Orientation: count by ORIENTATIONMETHOD for the newest window and the `UNRESOLVED` list with scores and gross flow at 2026-09-05 12:57.
5. Braunig 2026-06-23 13:57: 5475, 5474, 170135 rows and the BRAUNIG station sums vs `ERCOTSTATIONINJECTION`.
6. Row counts per month and distinct timestamps per month vs `ERCOTSTATIONINJECTION`. Pass: identical timestamp counts.

- [ ] **Step 1: Write both files; run the .py against the one loaded week from Task 3 (queries 2, 4, 5 adapted to that week)**. Expected: query 2 under 2 MW, query 5 matches.
- [ ] **Step 2: Hand to sdalvi**: `CALL AWDEV.ERCOTRT.SP_LOAD_ERCOT_BUS_INJECTION('2023-07-13', '2026-09-24');` (expect hours; V2 ran the same range). Stop until it ran.
- [ ] **Step 3: Run `verify_ercot_bus_injection.py`, save the output file.** Expected: the pass lines above; anything failing goes back to the owning task.
- [ ] **Step 4: Opus grading gate**: dispatch an Opus reviewer with the spec, the three .sql files, the verification output, and the questions: does the station roll-up prove conservation; would a wrong orientation on a 700 MW lead be visible in query 2 or 4; is any `UNRESOLVED` device large enough to matter for a shift-factor scan; is the redacted-line list credible against `/tmp/probes/absent_from_se_387.csv`. Fix and re-run until it passes.
- [ ] **Step 5: Commit**

```bash
cd /tmp/station-injection && git add stationinjection/verify_ercot_bus_injection.sql stationinjection/verify_ercot_bus_injection.py stationinjection/output/bus_injection_verification_*.txt && git commit -m "Bus injection verification script and full-range results"
```
