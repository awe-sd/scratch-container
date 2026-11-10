# Bus-grain SE net injection: design (2026-11-10)

## Intent

`AW.DBO.ERCOTSTATIONINJECTION` holds SE net injection at (station, kV). The fast scan
multiplies it by the average shift factor of the buses at that station-kV. 918 station-kV
pairs at 69 kV and above split into two or more PSSE buses (WAP 138 kV has eight, DOW 138 kV
six, BRAUNIG 138 kV an east and a west bus), and one third of all SE line-end flow lands at
such pairs. Averaging shift factors across those buses is the remaining grain error in the scan.

`AWDEV.ERCOTRT.ERCOTLINESEGMENT` (CIM line export, one row per ACLineSegment or
SeriesCompensator with its two end node groups) now lets every SE line end be placed on its
CIM bus, and the winding export already does the same for transformer ends. This design adds
a table at bus grain, built from the same SE branch flows as the station table, plus the
derived map tables it needs. It also materialises the list of CIM lines ERCOT does not report
in the SE feed (redacted lines, almost all private-use-network ties), because a bus-grain
residual at the visible end of such a line is the tie flow itself. Backing those flows out is
a later step over this table, not part of this build.

## Goals

- `AWDEV.ERCOTRT.ERCOTBUSINJECTION`, grain (TIMESTAMP, BUSNUMBER), with station, kV and
  CIMFILEID carried so it rolls up to the station table and joins `SHIFT_FACTORS.DBO.BUS_SHIFTS`
  on BUSNUM directly. Range: snapshots from the first in-force CIM file that has connectivity
  nodes after 2023-07-06 (nodes are missing for files in force 2021-12-21 to 2023-07-06)
  through the end of `ISOERCOTSEBRANCH`. One snapshot per hour, same selection rule as the V2
  station loader.
- Loader `SP_LOAD_ERCOT_BUS_INJECTION(P_START_DATE, P_END_DATE)` in
  `sp_load_ercot_bus_injection.sql`, same shape and size discipline as
  `sp_load_ercot_station_injection_v2.sql` (no verbose comments, two temp tables or fewer,
  delete-range-then-insert, in-force model per snapshot with fallback).
- `AWDEV.ERCOTRT.ERCOTSEBRANCHBUSMAP`: per CIM file, each SE branch device (line or
  transformer) with its from-bus and to-bus and how the link was made.
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
- History before July 2023 (no connectivity nodes for those CIM files).

## Anti-goals

- A bus with a wrong orientation on a 700 MW generator lead line. 482 SE line devices start
  and end in the same station (generator leads, series capacitors, reactors, taps) and carry
  33 GW of gross flow at a noon snapshot. Station names cannot orient them. Getting these
  wrong puts plus and minus the full flow on the wrong pair of buses. A device whose
  orientation cannot be settled must be reported, not guessed silently.
- Silent fallback to a different CIM file without recording it. CIMFILEID in every row.
- Joining anything on `ERCOTLINESEGMENT.FROMNUM` or `TONUM`. They are the PSSE bus only for
  63 percent of rows.
- Joining DAM-model bus numbers (`ERCOTDAMPSSELDVIEW.PSSEBUSNUMBER`) to CIM buses. Different
  numbering, 1 match in 7,773.

## Facts established (file 387 = 2026Sep.L1 unless stated)

- `ERCOTLINESEGMENT.FROMRDFID` / `TORDFID` equal `AW.DBO.CIMCONNODE.NODEGROUPID`. A node group
  is one PSSE bus at one station and voltage level (10,723 groups, none spanning two stations
  or two bus numbers). 8,643 of 8,646 segments resolve at both ends; the 3 that do not are
  series compensators with null end ids.
- SE line device name = CIM `LINENAME` for single-segment lines (6,088 devices) or
  `LINENAME || SEGMENTNAME` for multi-segment lines (2,344 devices, SE reports each segment).
  Two devices differ only in case (`BRINKR_RC138kV`). Five collide when both rules are tried
  at once (SE `411` is not CIM line `41` segment `1`), so the whole-line rule wins and the
  segment rule applies only to lines with more than one segment, guarded by station match.
- SE from/to orientation is not CIM order (3,526 of 8,436 two-station devices reversed), not
  alphabetical, not `AW.DBO.BRANCH` order, not the RT PSSE case order. For two-station devices
  this does not matter: each end is placed by station name. For same-station devices it must
  be derived (below).
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
- Coverage: connectivity nodes exist for all files in force from 2023-07-13 on; windings are
  missing for the 12 files in force 2026-07-28 to 2026-10-27; lines exist for all files from
  2021-12-21 on.
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
   as in V2. Same-kV transformers have no "own" winding by kV, so which bus takes FROMMW is
   settled by the orientation rule in decision 6, like same-station lines (9 PAR devices plus
   any other same-kV banks in the file).
5. **No sub-69 kV re-key.** At bus grain the generator sits on its own low-side bus, that bus
   has its own shift factor, and the re-key was only a workaround for kV averaging. My call.
   Consequence: the station-kV roll-up of this table equals the V2 table only after moving the
   V2 re-key amounts back; the verification query must do that, not expect equality.
6. **Same-station device orientation** is derived from the data, per device per CIM file, and
   stored in `ERCOTSEBRANCHBUSMAP` with `ORIENTATIONMETHOD`. Rule: for a device between buses A
   and B, over a sample of at least 200 snapshots in the file's in-force window, compute the
   residual at each bus from all other mapped branch ends. The orientation that makes the
   device's flow cancel the residual at the bus that has no resource node and no transformer
   (a pure switching or tap bus) is kept. If both buses carry injections, use the bus whose
   residual is explained better (smaller mean absolute residual after adding the device). If
   the two orientations are within 5 MW mean absolute residual of each other, mark the device
   `UNRESOLVED`, place its flow at the bus pair's shared station-kV (both ends on the lower bus
   number, netting to the loss), and list it in the verification output. A manual override
   table `ERCOTSEBRANCHORIENTATION` (BRANCHDEVICEID, FROMBUS, TOBUS, NOTE) wins over the rule.
   Devices sharing a bus (generator lead into series capacitor into tap) are resolved
   iteratively: pass 1 uses only two-station lines and transformers as the known residual,
   resolves every device that has a clean bus, then passes 2 and 3 add the resolved devices
   and retry the rest; whatever is left after pass 3 is UNRESOLVED. A generator lead's
   generator-side bus carries the step-up transformer, which is a known mirrored flow, so the
   "explained better" test is expected to settle leads, not the clean-bus test.
   Orientation is a property of (BRANCHDEVICEID, FROMBUS, TOBUS) and carries forward across
   CIM files while that bus pair is unchanged (PSSE bus numbers are stable: 10,707 of 10,710
   buses keep their station and kV from file 387 to 400). Only new bus pairs are derived, and
   only once their file has 200 in-force snapshots; until then they are UNRESOLVED, and the
   loader is re-run for that window after the map build catches up.
7. **Model in force and fallback**: per snapshot, the CIM file from `ERCOTCIMEFFECTIVEDATE`
   is the `CIMFILEID` written to the row. Nodes, line segments and windings are each taken
   from the in-force file if it has them, else from the latest earlier file that does; the
   map table records the three source files per in-force file (NODEFILEID, LINEFILEID,
   WINDINGFILEID), so a fallback is visible without a flag on 200 million rows. Bus numbers
   are stable across files, so a winding bus from a fallback file is used as is; if it does
   not exist in the nodes file, the end is placed by decision 9's station-kV rule and flagged.
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
   the ones to chase. Expectation from the probes: two case-only misses and the 21
   same-station devices without a BRANCH TEID, all of which the name rule against `LINENAME`
   should still catch, so the fallback should be near empty for 2026 files.

## Verification (committed with the proc)

- Roll-up: for a sampled snapshot, SUM(NETINJECTIONMW) by station-kV, after adding back the V2
  re-key moves, equals the `ERCOTSTATIONINJECTION` row within 1 MW for every station-kV (the
  residual is PAR losses, which V2 excludes and this table keeps).
- Switching-bus residual: buses with no resource node, no transformer and no redacted line
  have |net| under 2 MW at the 99th percentile across the sample.
- Known ties: the residual at CHB bus 40255 (BTE ties), CITGO_NO bus 8426 (CCEC) and GRNBELT
  bus 38575 (AMOCOOIL) tracks the PUN's SCED telemetry the way the September truth test did
  (correlation above 0.99 over a month).
- Same-station orientation: count by method, and the UNRESOLVED list, printed by the build.
- Braunig at 2026-06-23 13:57: 345 kV bus 5475 and 18 kV buses 5474/170135 shown, with the
  station-kV sums matching the V2 table once the re-key is added back.

## Open for sdalvi

- Can the line export add, per end, the node group's PSSE bus number and name, the station,
  the nominal kV, and the CIM Terminal sequence number? Sequence number would replace decision
  6 for every device that has it. Likewise for the winding export.
- Does the raw ERCOT SE branch feed carry from-bus and to-bus names that were dropped when
  `ISOERCOTSEBRANCHDEVICE` was loaded? If so, reloading them removes the orientation problem.
- Windings for the 12 newest CIM files, so the fallback is not used for Aug to Oct 2026.
- `AWDEV.ERCOTRT` versus `AW.DBO` for the new tables.

## Left to the builder

- SQL structure, temp-table count (at most V2's two), clustering, and performance.
- Exact matching order and guards inside the name rules, as long as the facts above hold.
- How the sample of snapshots for orientation is drawn.
- Whether the map build is one SQL script or a proc.
