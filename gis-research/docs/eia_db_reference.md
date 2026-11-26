# EIA tables in `AW.dbo` — reference for queue research

Schema review of the EIA objects in SQL Server `AW.dbo`, for the queue-research second-source
work. Goal: verify a queued project's **planned COD**, **capacity (MW and, for storage, MWh)**,
**location**, **entity/SPV**, and **operational status** against what the operating entity
independently reports to EIA.

Pulled `INFORMATION_SCHEMA.COLUMNS`, row counts, sample rows, and grain for each table on
2026-07-19 (read-only role). Relevance is judged against the five verification axes above.

**Headline finding — where the data actually lives:** the monthly **`eiaGenerator`** table is
the single best source and already carries everything the tools need, including
`nameplateEnergyCapacity` (storage MWh), `county`, `latitude`, `longitude`. The task's working
hypothesis that storage MWh lives in `eiaEnergyStorage` is **wrong** — that table is monthly
*net-generation* data, not planned capacity. The annual `*Annual` tables and `eia860*` files
are superseded by the monthly grain for COD/status change-point tracking. Two candidate tables
are dead ends (`namEia860GridMap` has no ERCOT rows; `genUnitEIAPlant` is empty).

Only the **generator** and **plant** slices are pulled by `eia_snapshot.py`; the rationale for
skipping each other table is recorded below so it does not have to be re-derived.

---

## Slices pulled by `eia_snapshot.py`

### `eiaGenerator` — PRIMARY. Monthly generator inventory (EIA-860M). **PULLED**
- **Rows:** 1,696,459 total; **141,817** `plantState='TX'`.
- **Grain:** one row per `(reportDate, plantId, generatorId)` — a monthly snapshot. TX
  `reportDate` spans **2022-04-01 → 2026-05-01** (47 monthly snapshots).
- **Key columns:** `reportDate`, `plantId`, `entityId`, `generatorId`, `eiaStatusId`,
  `eiaTechnologyId`, `nameplateCapacity` (MW), `netSummerCapacity`,
  **`nameplateEnergyCapacity` (MWh — storage energy capacity)**, `plannedOperationYear/Month`
  (planned COD), `operatingYear/Month` (actual in-service), `plannedRetirementYear/Month`,
  `primeMoverCode`, `energySourceCode`, **`county`, `latitude`, `longitude`**,
  `balancingAuthorityCode`.
- **Join keys** (denormalize to names): `plantId → eiaPlant.eiaPlantId` (`eiaPlantName`),
  `entityId → eiaEntity.eiaEntityId` (`eiaEntityName`), `eiaStatusId → eiaStatus.eiaStatusId`
  (`eiaStatus`), `eiaTechnologyId → eiaTechnology.eiaTechnologyId` (`eiaTechnology`).
- **Column population (TX):** `county` **100%**, `latitude` **99.8%**, `nameplateEnergyCapacity`
  present on **5,141 / 12,201 battery rows** (BA/ES prime movers) — i.e. every reporting BESS.
  > Corrects the note in `gis-research/CLAUDE.md` / `eia_history.py` docstring that "the DB
  > history table has NO county/lat-lon". It does — fully populated. Matching still uses the
  > 860M workbook county map for byte-exact backward compatibility (see `eia_history.py`); the
  > DB `county/lat/lon` are surfaced as an **additive cross-check**, not a new match input.
- **Relevance:** HIGH on every axis — COD (`plannedOperationYear/Month`), status
  (`eiaStatusId`), MW (`nameplateCapacity`), MWh (`nameplateEnergyCapacity`), location
  (`county/lat/lon`), entity (`entityId`). This is the backbone of `eia_history.py`.
- **Exact snapshot filter (reproduces `eia_generator_tx.parquet`, 114,584 rows):**
  `WHERE plantState='TX'` with an **INNER JOIN on `eiaStatus`** (drops 27,233 null-status rows:
  141,817 − 27,233 = 114,584) and LEFT joins to plant/entity/technology. Verified byte-for-byte
  against the existing parquet.

### `eia860plant` — Annual plant-location file (EIA-860). **PULLED (plant slice)**
- **Rows:** 16,580 total; **945** `state='TX'` (only years **2013–2014** exist for TX).
- **Grain:** one row per `(yr, plantCode)`.
- **Key columns:** `plantCode`, `plantName`, `utilityId`, `utilityName`, `city`, `county`,
  `latitude`, `longitude`, `balancingAuthorityCode` (subset pulled), plus address/FERC/sector.
- **Join keys:** `plantCode = eiaGenerator.plantId` (EIA plant code is the shared key).
- **Relevance:** HIGH for **location** (lat/lon/county for a fixed plant). Source of
  `eia_plant_tx.parquet`. Filter `WHERE state='TX'` reproduces the parquet exactly (945 rows).
  Note the TX rows are stale (2013–2014); `eiaGenerator.latitude/longitude` is the current
  coordinate source for recent projects.

---

## Tables reviewed and NOT pulled (with reason)

### `eiaEnergyStorage` — monthly storage **net generation**, NOT capacity. SKIP
- **Rows:** 77,244. **Grain:** `(year, month, plantId, fuelTypeId)`, 2014–2026.
- **Columns:** `quantity`, `electricQuantity`, `grossGen`, `netGen`, `primeMover` — realized
  monthly generation/consumption (sample rows are future placeholder months with all-zero gen).
- **Verdict:** LOW / not used. This is 923-style *operational* data, **not** planned energy
  capacity. The task hypothesis that storage MWh lives here is incorrect — MWh is
  `eiaGenerator.nameplateEnergyCapacity` (monthly, with change-point history). No COD, no
  planned capacity, no entity. Could later serve as an "is it actually generating" signal.

### `eiaStorageAnnual` — **annual** EIA-860 storage supplement. SKIP (superseded)
- **Rows:** 4,266. **Grain:** `(reportDate, entityId, plantId, generatorId)`, `reportDate` =
  Jan-1 of **2017–2025** (annual).
- **Columns:** `nameplateCapacity`, **`nameplateEnergyCapacity` (MWh)**, `maxChargeRate`,
  `maxDischargeRate`, storage tech + grid-service flags, `eiaStatusId`, `operating/retirement`.
- **Verdict:** MEDIUM but **deliberately not pulled**. It has the same MWh field plus
  charge/discharge detail, but at an **annual** grain that ends in 2025 and skews to already-
  operating units — worse than the monthly `eiaGenerator` for COD/capacity change-point
  tracking. MWh is folded into the monthly generator slice instead. Revisit only if
  charge/discharge power ratings are ever needed.

### `eiaGeneratorAnnual` — annual counterpart of `eiaGenerator` (75 cols). SKIP (superseded)
- **Rows:** 308,066. **Grain:** `(reportDate, entityId, plantId, generatorId)`, annual.
- **Columns:** everything in `eiaGenerator` plus `ownership`, `rtoIsoNode`, `plannedNameplateCapacity`, etc.
- **Verdict:** MEDIUM, superseded. Annual grain loses the monthly change-point resolution that
  makes the second-source comparison useful. `ownership`/`rtoIsoNode` are interesting for a
  future entity/SPV pass but are not needed for COD/capacity/status verification now.

### `eiaSolarAnnual` (50,398) / `eiaWindAnnual` (15,371) — annual 860 tech detail. SKIP
- **Grain:** `(reportDate, entityId, plantId, generatorId)`, annual.
- **Columns:** technology detail — solar: tracking/tilt/module chemistry; wind: `numTurbines`,
  `turbineManufacturer`, `turbineModelNum`, `turbineHubHeight`, `designWindSpeed`.
- **Verdict:** LOW for the COD/capacity/status/location core. `numTurbines`/turbine model could
  aid *site* verification of a specific wind farm, but that is a niche, per-project lookup, not
  a slice the tools depend on. Not pulled.

### `eia860Gen` — raw annual EIA-860 generator file, nationwide. SKIP (superseded)
- **Rows:** 37,748. **Grain:** `(yr, plantCode, generatorId)`.
- **Columns:** `status`, `plannedOperation*`, `technology`, `primeMover`, capacities.
- **Verdict:** LOW. Annual and nationwide; the monthly TX `eiaGenerator` supersedes it for TX
  COD tracking. Useful only as the upstream of the annual files above.

### `eiaGeneration` — EIA-923 monthly **net generation**. SKIP (out of scope)
- **Rows:** 3,082,953. **Grain:** `(year, month, plantId, generatorId, primeMover)`.
- **Columns:** `netGeneration`, `fuelTypeId`.
- **Verdict:** MEDIUM as a future *operational-confirmation* signal (a plant with net
  generation is definitely online), but it carries no COD/capacity/location/entity, so it is
  outside this task's scope. Noted for a possible "already generating" cross-check.

### `eia923Plant` — plant crosswalk/lookup. SKIP
- **Rows:** 21,238. **Grain:** `(plantId)`. Columns: `eiaPlantId`, `eiaPlantName`,
  `eiaOperatorName`.
- **Verdict:** LOW. A name/operator lookup keyed by `plantId`; adds nothing over `eiaPlant`.

### `genUnitEIAPlant` — internal GenUnit ↔ EIA plant bridge. SKIP (EMPTY)
- **Rows:** **0**. **Grain (intended):** `(genUnitID, eiaPlantCode, generatorId)`.
- **Verdict:** Would be the bridge from EIA plants to the internal `GenUnit`/SCED namespace
  (the parked SCED-exclusion TODO), but it has **no rows** — unusable. Flag if it is ever
  populated.

### `namEia860GridMap` — EIA plant ↔ ISO/grid map. SKIP (no ERCOT rows)
- **Rows:** 271. **Grain:** `(plantCode)`. Columns: `isoMarketId`, `plantLat`, `plantLong`,
  `gridId`.
- **Verdict:** NOT RELEVANT for TX/ERCOT. `isoMarketId` values are only **2 (n=21)** and
  **3 (n=250)** — there are **no `isoMarketId=6` (ERCOT)** and no TX rows. Tiny, non-ERCOT map.

---

## Lookup tables (dimension joins, not sliced)

| table | key | gives |
|---|---|---|
| `eiaPlant` | `eiaPlantId` | `eiaPlantName`, `operatorName` |
| `eiaEntity` | `eiaEntityId` | `eiaEntityName` (the operating company / SPV) |
| `eiaStatus` | `eiaStatusId` | `eiaStatus` text (e.g. `(U) Under construction, ≤50% complete`) |
| `eiaTechnology` | `eiaTechnologyId` | `eiaTechnology` text |
| `eiaPrimeMoverCode` | `eiaPrimeMoverCode` | prime-mover description |
| `eiaEnergySourceCode` | `eiaEnergySourceCode` | fuel type / heat content |
| `eiaSector` | `eiaSectorId` | sector name |

## EIA status codes seen in TX `eiaGenerator` (frequency, all snapshots)
`(OP) Operating` 96,325 · `(P) Planned, approvals not initiated` 5,146 ·
`(L) Approvals pending, not under construction` 3,524 ·
`(V) Under construction >50%` 2,149 · `(U) Under construction ≤50%` 2,036 ·
`(TS) Construction complete, not yet commercial` 1,533 ·
`(T) Approvals received, not under construction` 1,247 · `(SB) Standby` 1,210 ·
`(OS) Out of service, not returning` 1,085 · `(OA) Out of service, returning` 280 · `(OT) Other` 49.
(27,233 TX rows carry a null status and are dropped by the INNER-JOIN filter.)
