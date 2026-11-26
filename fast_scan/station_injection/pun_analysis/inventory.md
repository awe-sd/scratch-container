# PUN back-out: schema inventory

Read-only Snowflake, role AI_READ_ONLY. Sources: `pun1_out.txt`..`pun12_out.txt` in the scratchpad (query logs), not copied here.

## 1. AWDEV.ERCOTRT schema (SE / real-time PSSE model)

`SHOW TABLES` (28) + `SHOW VIEWS` (3). No table is literally named "SE gen" or "SE load" or "PUN" — the closest candidates are the `ERCOTRTPSSE*` family, which is a **real-time PSSE network-model snapshot** (topology + ratings), analogous to the DAM PSSE model (`ERCOTDAMPSSE*`) but built from ERCOT's hourly CIM/State-Estimator publications:

- **`ERCOTRTPSSECASE`** — one row per hourly RT case (720 rows in June 2026 = 24/day x 30 days). `CASETYPE` is always `'RT'`. `RAWNAME` embeds the source CIM filename, e.g. `CIM_May_ML3_1_06022026_Redacted_20260601-220015...` — "Redacted" is ERCOT's standard public-CIM-model filename token, **not** evidence this particular case has PUN devices stripped (see below).
- **`ERCOTRTPSSEGNDEF`** (generator definitions, keyed by `RDFID`/`TEID`, with `STATIONID`, `CPNODEID`) + **`ERCOTRTPSSEGNTIMESERIES`** (per-hour per-case: `GENMWMAX/MIN`, `GENMVRMAX/MIN`, `VSETPOINT`, `INSERVICE` — **capacity/limit fields, not a solved MW output**). 1,197,696 rows in June 2026.
- **`ERCOTRTPSSELDDEF`** (load definitions, `STATIONID`, `LOADZONENAME`, `WEATHERZONENAME`) + **`ERCOTRTPSSELDTIMESERIES`** (`LOADDISTRIBUTIONFACTOR` — a scaling factor, not actual MW). 3,714,984 rows in June 2026.
- **`ERCOTRTPSSESTATION`** — 5,858 stations, `STATIONNAME`/`STATIONKV` (KV mostly NULL).

**Important finding:** PUN stations ARE present in this model. `EXN`, `FORMOSA`, `DOW`, `NCARBIDE`, `VISTRON`, `EQUISTAR`, `OXY_CC`, `OXY_INGL`, `CELANEBI`, `UCC_COGN` all exist as `ERCOTRTPSSESTATION` rows, and EXN (12 gens) and FORMOSA (15 gens) have `ERCOTRTPSSEGNDEF` rows joined to them. So the CIM/PSSE network **topology** model is not redacted for these PUN stations — only the **live SE branch telemetry** table (`ISOERCOTSEBRANCHDEVICE` / the hourly SE branch solve) drops the tie lines and the flows across them. This means: **there is no SE gen-or-load-per-station table with actual solved MW values for PUN stations.** The RT PSSE tables give topology/ratings only — no per-hour actual injection to subtract. The back-out method (Gen_S − Load_S − tie flow, computed from *visible* SCED/DAM data at the neighbour station S, not from a PUN-side table) remains the only viable path.

- `ERCOTSETRANSFORMERNAMECORRECTING`, `ERCOTTRANSFORMERWINDING`, `ERCOTXFMRWINDINGRUN`, `ERCOT_PRODUCTION_LOAD_SCHEDULE`, `RT_TOPOLOGY_SNAPSHOT` — none of these are gen/load-per-station tables (transformer winding taps, a load-schedule staging table, and a topology-run job-tracking table respectively). Not investigated further (out of scope / no PUN content expected).

**Conclusion for deliverable 1a: no SE gen/load-per-station table with actual MW values exists in AWDEV.ERCOTRT.**

## 2. ISOERCOTSCEDGENRESOURCE / ISOERCOTSCEDGEN

- `ISOERCOTSCEDGENRESOURCE`: keyed by `"TIMESTAMP"` + `GENID`. Telemetry columns: **`TELEMETEREDOUTPUT`** (the SCADA-metered MW seen by ERCOT for that generation resource — this is the "actual output" column), **`BASEPOINT`** (SCED's dispatch instruction/target MW), **`HSL`**/`HASL` (high sustained/ancillary limit), `LSL`/`LASL` (low sustained limit), `TELEMETEREDSTATUS` (ON/ONOS/OFF/OUT). No station/name column — join via `GENID`.
- `ISOERCOTSCEDGEN`: the dimension table — `GENID`, `RESOURCENAME`, `RESOURCETYPE`, `QSE`, `DME`, `CPNODEID`. `CPNODEID` is the join key to `GENUNIT`.
- Run cadence, June 2026: 9,807,728 rows across the month; 290 distinct `"TIMESTAMP"` values on June 1 alone. `MINUTE("TIMESTAMP")` is spread evenly across all ten 5-minute buckets (`:00,:05,:10,...,:55`, each ~189,493 rows/week) — **runs are NOT anchored only at `:55`; SCED reports at every 5-minute interval** (the `:55` landing mentioned in the brief does not hold in this table — cadence is uniform 5-min throughout the hour).

## 3. GENUNIT / GENUNITSCEDNAME

- `GENUNIT` (AWDEV.DBO): 1,617 ISO-6 (ERCOT) rows, 682 distinct `BUSNAME`. No direct "NMMS station code" column — the station/company identity is embedded as a **prefix on `BUSNAME`** (e.g. `EXXON__POI_8`, `PSARCO_POI_8`, `AMOCOOIL_5_8`) and, for PUN resources specifically, **`UNITNAME` is literally the string `'PUN'`** (a clean flag — 118 rows, 23 distinct `BUSNAME`s, i.e. 23 curated PUN plants are modeled as gen units, not all 56 PUN stations found in the topology work).
- `GENUNITSCEDNAME`: `GENUNITID` -> `NAME`/`KIND`/`EPOCH` — a name-history/alias table, joined on `GENUNITID`.
- Mapping SCED resource -> station: `ISOERCOTSCEDGEN.CPNODEID = GENUNIT.CPNODEID`. Of 1,798 distinct SCED `RESOURCENAME`s overall, **1,614 (90%) map to a `GENUNIT` row; 184 (10%) do not** (retired/decommissioned or DC-tie/import resources with no ERCOT GENUNIT record).
- Station **name** resolution for a `GENUNIT` (needed for deliverable 2's "does neighbour S have SCED gens") goes through the **DAM** model, not GENUNIT directly: `GENUNIT.CPNODEID = ERCOTDAMPSSEGNDEF.CPNODEID -> ERCOTDAMPSSEGNDEF.STATIONID -> ERCOTDAMPSSESTATION.STATIONNAME`.

## 4. DAM bus-level load/gen model (AW.DBO, `%DAMPSSE%`)

`SHOW TABLES LIKE '%DAMPSSE%'` (19 tables) + `SHOW VIEWS LIKE '%DAMPSSE%'` (4 views: `ERCOTDAMPSSELDVIEW`, `ERCOTDAMPSSELNVIEW`, `ERCOTDAMPSSEVIEW`, `ERCOTDAMPSSEXFVIEW`).

- **`ERCOTDAMPSSELDVIEW`** — the DAM bus-level **load** model: `STATIONNAME`, `STATIONKV`, `PSSEBUSNUMBER`, `LOADZONENAME`, `WEATHERZONENAME`, `RAWMWLDF` (raw MW load-distribution factor — this is the LDF the brief was looking for), `RAWMVARLDF`, `INSERVICE`, `"DATE"`/`HE`. This IS the DAM load model with station name directly on it.
- **`ERCOTDAMPSSEVIEW`** — the DAM **branch** model (from/to bus + station + kV, ratings, monitored flags — same shape as `ERCOTDAMPSSELNVIEW` used to build the redacted-lines CSV).
- **`ERCOTDAMPSSEGNDEF`** (table, not view) — generator-to-bus mapping: `ERCOTDAMPSSEGENID`, `GENNAME`, `STATIONID` (-> `ERCOTDAMPSSESTATION.ERCOTDAMPSSESTATIONID`, gives `STATIONNAME`/`STATIONKV`), `CPNODEID` (-> `GENUNIT`/`ISOERCOTSCEDGEN`), `DCTIE` flag.
- No separate `ERCOTDAMPSSEGNVIEW`; use the table + `ERCOTDAMPSSESTATION` join directly (used above).

## Row-count / sample notes
All row counts and 3-sample-row pulls for the above are in `pun1_out.txt` through `pun3_out.txt` (scratchpad) rather than duplicated here; the key ones are quoted above.
