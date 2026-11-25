# Bus-grain SE net injection: design (2026-11-10, amended 2026-11-25)

## Intent

`AW.DBO.ERCOTSTATIONINJECTION` holds SE net injection at (station, kV). The fast scan
multiplies it by the average shift factor of the buses at that station-kV. 918 station-kV
pairs at 69 kV and above split into two or more PSSE buses (WAP 138 kV has eight, DOW 138 kV
six, BRAUNIG 138 kV an east and a west bus), and one third of all SE line-end flow lands at
such pairs. Averaging shift factors across those buses is the remaining grain error in the scan.

`AWDEV.ERCOTRT.ERCOTLINESEGMENT` (CIM line export, one row per ACLineSegment or SeriesCompensator, refreshed 2026-11-24 so each end carries its station, nominal kV, PSSE bus number and name, connectivity node and, where ERCOT defines one, electrical bus) now lets every SE line end be placed on its
CIM bus, and the winding export already does the same for transformer ends. This design adds
a table at bus grain, built from the same SE branch flows as the station table, plus the
derived map tables it needs. It also materialises the list of CIM lines ERCOT does not report
in the SE feed (redacted lines, almost all private-use-network ties), because a bus-grain
residual at the visible end of such a line is the tie flow itself. Backing those flows out is
a later step over this table, not part of this build.

## Goals

- `AWDEV.ERCOTRT.ERCOTBUSINJECTION`, grain (TIMESTAMP, BUSNUMBER), with station, kV and
  CIMFILEID carried so it rolls up to the station table and joins `SHIFT_FACTORS.DBO.BUS_SHIFTS`
  on BUSNUM directly. Range: the loader takes a date range; the line export covers every CIM
  file in force from 2021-12-21 on and the winding export every file, so any range from
  2021-12-21 through the end of `ISOERCOTSEBRANCH` is valid. sdalvi asked for July 2023 onward
  first. One snapshot per hour, same selection rule as the V2
  station loader.
- Loader `SP_LOAD_ERCOT_BUS_INJECTION(P_START_DATE, P_END_DATE)` in
  `sp_load_ercot_bus_injection.sql`, same shape and size discipline as
  `sp_load_ercot_station_injection_v2.sql` (no verbose comments, two temp tables or fewer,
  delete-range-then-insert, in-force model per snapshot with fallback).
- `AWDEV.ERCOTRT.ERCOTSEBRANCHBUSMAP`: per CIM file, each SE branch device (line or
  transformer) with its from-bus and to-bus and how the link was made. Each line end also
  carries the CIM connectivity node name and electrical bus name from the export
  (FROMCONNECTIVITYNODE, TOCONNECTIVITYNODE, FROMELECTRICALBUS, TOELECTRICALBUS, nullable), for
  later finer aggregation; transformer ends have none.
- `AWDEV.ERCOTRT.ERCOTREDACTEDLINE`: per CIM file, each CIM line segment with no SE device,
  with both end buses, stations, kV and which end is SE-visible.
- Verification queries committed next to the proc, as for V2.

## Non-goals

- Changing `ERCOTSTATIONINJECTION`, its V2 loader, or the fast-scan procs. A bus-grain scan
  variant comes after this table exists and is verified.
- The PUN back-out itself. The September design (`ercot_pun_tie_map.sql`,
  `sp_load_ercot_pun_injection.sql`, never deployed) is to be redone as a view over this table
  once it exists.
- Bus-level load or generation columns. Only the SE residual is stored.
- Injection below bus grain. Electrical buses exist on 2,192 of 8,646 line ends in file 387 and
  on no transformer end, and 844 buses hold more than one, so an electrical-bus residual would
  mix labelled and unlabelled ends. A connectivity-node residual needs breaker status, which we
  do not have. Both names are stored in the map so a later model can aggregate differently.

## Anti-goals

- A bus with a wrong orientation on a 700 MW generator lead line. 482 SE line devices start
  and end in the same station (generator leads, series capacitors, reactors, taps) and carry
  33 GW of gross flow at a noon snapshot. Station names cannot orient them; the export's near-terminal convention does (see decision 6), but a file loaded in the old convention would silently reverse them. The map build must therefore prove the convention on every file before using it.
- Silent fallback to a different CIM file without recording it. CIMFILEID in every row.
- Joining line ends through `CIMCONNODE`. Since the 2026-11-24 refresh
  `ERCOTLINESEGMENT.FROMNUM` and `TONUM` are the node-group PSSE bus (equal to FROMCNGPSSENUM
  and TOCNGPSSENUM in 8,645 of 8,646 rows, and including the exporter's grouping corrections
  that the node table lacks, 4 ends per file). The node table is used only for the bus name,
  station and kV of buses that appear on transformer windings alone.
- Joining DAM-model bus numbers (`ERCOTDAMPSSELDVIEW.PSSEBUSNUMBER`) to CIM buses. Different
  numbering, 1 match in 7,773.

## Facts established (file 387 = 2026Sep.L1 unless stated)

- `ERCOTLINESEGMENT` (70 columns since 2026-11-24) gives per end FROMSTATION, FROMKV, FROMNUM
  and FROMCNGPSSENAME (PSSE bus number and name of the node group), FROMCNNAME (connectivity
  node), FROMEBNAME and FROMEBCODE (electrical bus, present where FROMSTATUS is `resolved`),
  FROMGROUPINGSTATUS (`consistent` 8,306 ends, `detached_from_declared_primary` 328,
  `discrepancy_candidate` 10, `ambiguous_candidates` 2 in file 387) and FROMCORRECTEDCNGNAME
  where the exporter overrode the node-table grouping, and the same for the TO end.
  FROMTERMINALSEQ and TOTERMINALSEQ are null in every row. FROMRDFID and TORDFID still equal
  `CIMCONNODE.NODEGROUPID`.
- Same-station segments in file 387: 566 (563 join two different buses, 3 start and end on one
  bus); all are exported as class SeriesCompensator, so class does not separate generator
  leads, CREZ series devices and bus ties.
- SE line device name = CIM `LINENAME` for single-segment lines (6,088 devices) or
  `LINENAME || SEGMENTNAME` for multi-segment lines (2,344 devices, SE reports each segment).
  Two devices differ only in case (`BRINKR_RC138kV`). Five collide when both rules are tried
  at once (SE `411` is not CIM line `41` segment `1`), so the whole-line rule wins and the
  segment rule applies only to lines with more than one segment, guarded by station match.
- SE from/to orientation follows the EMS attribute `etx:Terminal.near` in the CIM XML: the SE
  from-end is the terminal with near = true. Verified on file 187 for 8,013 of 8,013 two-station
  devices with no counterexample (`se_direction_truth.sql`, output in
  `output/se_direction_truth_187.csv`); all 471 same-station devices in that file have exactly
  one near end. The export as loaded today ignores the flag and orders ends by terminal GUID
  (from = smaller id in 7,952 of 7,952 devices of file 387), which is why 49 percent of devices
  appeared reversed. The exporter (tessera) will be re-released with FROM = near terminal, and
  both the line and the winding tables re-uploaded.
- `AW.DBO.BRANCH.TEID` (ISOMARKETID 6) equals the CIM `SEGMENTTEID` for lines and the CIM
  `TRANSFORMERTEID` for transformers, but only 3,196 of 7,952 two-station SE line devices and
  2,161 of 2,664 transformer devices have a BRANCH row. 461 of the 482 same-station devices
  reach a CIM segment through BRANCH by name (`BRANCHNAME` = SE name or SE name plus `1`).
- `ERCOTTRANSFORMERWINDING.FROMNUM` is the winding's own PSSE bus and `TONUM` the partner bus
  (BRAUNIG 18_2 at 345 kV: 5475 → 170135; 18_2_L at 18 kV: 170135 → 5475). Star points are
  the NOMINALKV = 1 rows.
- `BUS_SHIFTS` (PSENSHIFTID 119661676) has a row for 7,824 of 7,828 CIM buses at or above
  69 kV and 2,890 of 2,895 below.
- CIM file ids are not chronological (393 = 2023Mar.L5, 400 = 2026Oct.L4). Always resolve the
  model through `ERCOTCIMEFFECTIVEDATE`.
- Coverage: lines exist for every CIM file in force from 2021-12-21 on; windings exist for 220
  files (ids 2 to 408), so the earlier gap for files in force 2026-07-28 to 2026-10-27 is
  closed; connectivity nodes are missing for files in force 2021-12-21 to 2023-07-06, which now
  only costs bus names on transformer-only buses in that window. `ERCOTCIMEFFECTIVEDATE`
  columns are CIM_LABEL, CIMFILEID, PRODUCTION_LOAD, EFFECTIVE_FROM, EFFECTIVE_TO; the newest
  file is 408 (2026Nov.L3) from 2026-11-17 23:00.
- Winding bus numbers: in file 387, 5,570 of 5,640 windings have a FROMNUM that is a bus in the
  node table. 58 non-star windings on 55 buses carry 9xxxxx numbers (DCSES 900240, EXPSW 901529,
  LEG 901873, NEDIN 902199 and others) that are in no node table, and 12 star rows are likewise
  absent. sdalvi is correcting these in the winding export.
- Redacted lines against SE devices active 2026-09-05: 129 ACLineSegment lines (130 segments)
  and 84 series compensators have no SE device. 30 lines run PUN to PUN, 96 have exactly one
  visible end, 4 are radial customer taps or the NASA tap (FT_NA_06, NA_WEB06). At most
  visible ends the bus has one redacted line, no resource node and one to three visible lines.
- Generators resolve to a CIM bus through `CIMCONNODE.NAME_RESOURCENODE` = `CPNODE.NAME` =
  `ISOERCOTSCEDGEN.CPNODEID` for 1,719 of 1,819 SCED units. RT PSSE load definitions carry CIM
  bus numbers and share `LOADNAME` with 5,070 of 7,760 DAM loads. Both are for the later
  back-out step, recorded here so the builder does not rediscover them.

## Decisions

1. **Target objects** live in `AWDEV.ERCOTRT`, uppercase, no underscores in table names, like
   the winding tables. My call; `ERCOTSTATIONINJECTION` is in `AW.DBO` and sdalvi may prefer
   that.
2. **Columns of ERCOTBUSINJECTION**: `TIMESTAMP` TIMESTAMP_NTZ(0), `CIMFILEID`, `BUSNUMBER`,
   `BUSNAME`, `NMMSSTATIONCODE`, `KVLEVEL` NUMBER(6,2), `NETINJECTIONMW`. Rows only for buses
   with at least one SE branch end at that snapshot; zero rows are kept (a bus with balanced
   flows is information). Sign convention identical to the station table.
3. **Line ends**: FROMMW to the bus at the SE from-station, TOMW to the bus at the SE
   to-station, each taken from the CIM segment the device maps to in the in-force file.
4. **Transformer ends**: the SE device's FROMMW goes to the mapped winding's own bus
   (`FROMNUM` of that winding row) and the mirror leg, TOMW as in V2, goes to the other real
   winding's own bus. The mirror test is "the device's transformer has another real winding
   on a different bus", not V2's different-kV test: at bus grain a phase shifter or any
   same-kV two-winding transformer sits between two real buses and must be booked at both.
   The V2 PAR exclusion is therefore dropped; at station-kV roll-up a PAR nets to its loss.
   Star-leg devices (one real winding, partner is the NOMINALKV = 1 star bus) get no mirror,
   as in V2. Same-kV transformers (7 phase shifters in file 387) have no own winding by kV, so the
   winding named by the device's TRANSFORMERENDNAME takes FROMMW, or the near winding once the
   re-uploaded winding table carries that flag.
5. **No sub-69 kV re-key.** At bus grain the generator sits on its own low-side bus, that bus
   has its own shift factor, and the re-key was only a workaround for kV averaging. My call.
   Consequence: the station-kV roll-up of this table equals the V2 table only after moving the
   V2 re-key amounts back; the verification query must do that, not expect equality.
6. **Orientation comes from the export.** After the re-upload, `ERCOTLINESEGMENT.FROMNUM` is
   the SE from-bus and `TONUM` the SE to-bus for every line device, same-station or not, and
   the map records ORIENTATIONMETHOD `NEAR`. The map build proves the convention per file
   before trusting it: among the file's two-station devices matched by name, the share whose
   export from-station equals the SE from-station must be at least 0.999. A file that fails is
   marked `OLDCONVENTION` in the map build output; its two-station devices are oriented by
   station name (`STATION`) and its same-station devices are placed with both ends on the
   lower bus number (`UNRESOLVED`, netting to the loss) until the file is re-uploaded. No
   flow-based derivation and no manual override table are built. Transformers are unaffected:
   FROMMW goes to the winding matching the device kV as in decision 4; if the re-uploaded
   winding table carries a near flag it is used only as the tie-break for same-kV banks and as
   a verification that the near winding is the device-kV winding.
7. **Model in force and fallback**: per snapshot, the CIM file from `ERCOTCIMEFFECTIVEDATE`
   is the `CIMFILEID` written to the row. Line segments, windings and nodes are each taken
   from the in-force file if it has them, else from the latest earlier file that does; the
   map table records the three source files per in-force file (LINEFILEID, WINDINGFILEID,
   NODEFILEID), so a fallback is visible without a flag on 200 million rows. Bus number, name,
   station and kV for a line end come from the line row itself. For a winding end the bus
   number comes from the winding row and the name from any line end on that bus in the same
   file, else from the node table, else null.
8. **Map table build** is a separate statement (or small proc) that fills
   `ERCOTSEBRANCHBUSMAP` and `ERCOTREDACTEDLINE` for every CIM file that has nodes and lines,
   and is re-run when a new CIM file is loaded. The loader only reads the maps. Redacted =
   CIM segment at or above 69 kV, two different stations, with no SE device by the name rules
   and no SE device on the same station pair and kV while the file is in force.
9. **Unmapped device ends** never block the load and never drop flow. An end with no CIM
   link is placed on the single bus of its SE station-kV when that station-kV has exactly one
   bus in the nodes file (MATCHMETHOD `STATIONKV`), else on the lowest-numbered bus of that
   station-kV (MATCHMETHOD `STATIONKV_AMBIGUOUS`). Each end is treated separately. The map
   build prints the count and the list by method, and `STATIONKV_AMBIGUOUS` ends with flow are
   the ones to chase. A winding whose FROMNUM is not a bus known to any line end or node row
   in its file (the 9xxxxx numbers above) is placed the same way with MATCHMETHOD
   `WINDINGBUSUNKNOWN`; when sdalvi's corrected winding export lands, the map rebuild picks it
   up and the loader is re-run for the affected range. Expectation from the probes: two
   case-only misses on lines, the 58 split-bus windings, and nothing else of size for 2026
   files.

## Verification (committed with the proc)

- Roll-up: for a sampled snapshot, SUM(NETINJECTIONMW) by station-kV, after adding back the V2
  re-key moves, equals the `ERCOTSTATIONINJECTION` row within 1 MW for every station-kV (the
  residual is PAR losses, which V2 excludes and this table keeps).
- Switching-bus residual: buses with no resource node, no transformer and no redacted line
  have |net| under 2 MW at the 99th percentile across the sample.
- Known ties: the residual at CHB bus 40255 (BTE ties), CITGO_NO bus 8426 (CCEC) and GRNBELT
  bus 38575 (AMOCOOIL) tracks the PUN's SCED telemetry the way the September truth test did
  (correlation above 0.99 over a month).
- Convention check: per CIM file, the share of two-station devices whose export from-station
  equals the SE from-station, expected 1.000 for every re-uploaded file; files below 0.999
  listed as OLDCONVENTION with their windows.
- Braunig at 2026-06-23 13:57: 345 kV bus 5475 and 18 kV buses 5474/170135 shown, with the
  station-kV sums matching the V2 table once the re-key is added back.

## Open for sdalvi

- Delivered 2026-11-24: station, kV, bus number and name, connectivity node and electrical bus
  per line end. Delivered 2026-11-25: the orientation rule (`etx:Terminal.near`), to be baked
  into the next tessera release as the from/to convention of both exports; the build waits for
  that re-upload.
- The 58 split-bus windings (9xxxxx FROMNUM) per file, in progress on sdalvi's side.
- `AWDEV.ERCOTRT` versus `AW.DBO` for the new tables.

## Left to the builder

- SQL structure, temp-table count (at most V2's two), clustering, and performance.
- Exact matching order and guards inside the name rules, as long as the facts above hold.
- Whether the map build is one SQL script or a proc.
