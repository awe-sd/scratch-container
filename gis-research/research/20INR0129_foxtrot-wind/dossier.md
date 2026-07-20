# Dossier — Foxtrot Wind (20INR0129)

Researched 2026-07-19 · site 28.6220, -97.9376 · verdict **operating**

## 1. Verdict

- **Operating** — [EIA Form 860 2025ER](sources/2026-07-19_eia860_2025er_bee-county-wind.txt) records "Helena Wind" (268.2 MW, Bee County TX, status OP) operating since June 2022, identical capacity to Foxtrot Wind; project renamed/transferred before COD
- Construction: **operating**, turbines in service since 2022-06 per EIA 860
- Site: 28.6220, -97.9376 — EIA 860 plant coordinates corroborated by 72 OSM turbine nodes + Sentinel-2 ([map](https://google.com/maps/@28.622,-97.9376,5000m/data=!3m1!1e3))
- COD: reported 2026-08-31 → independent **2022-Q2 (already operating)**, drift risk **not applicable** (queue entry orphaned after name change)

## 2. Site identification

- Derivation: EIA Form 860 2025ER plant record for Helena Wind, plant code 63738, lat 28.621959, lon -97.937625 ([EIA source](sources/2026-07-19_eia860_2025er_bee-county-wind.txt))
- **Stated project area: unknown** — PUCT Interchange (HTTP 402) and Bee County CAD both inaccessible; IA acreage not retrieved
- Cross-checks: EIA plant coords (28.622, -97.938) agree with OSM turbine cluster centroid ([OSM source](sources/2026-07-19_osm-overpass_bee-county-wind-turbines.txt)) within < 0.1 km; Sentinel-2 2026-07-01 chip ([imagery](imagery/s2_28.62_-97.94_2026-07-01.png)) shows white turbine dots + access roads at this location
- Not obtainable: exact POI switch coords (CEII / PUCT 402); exact parcel boundaries; IA acreage exhibit

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Foxtrot Wind, LLC | SPV / IA signatory | [ERCOT queue timeline](timeline.md) — IA signed 2020-05-05 |
| Helena Wind, LLC | Operating entity (EIA 860 utility) | [EIA 860](sources/2026-07-19_eia860_2025er_bee-county-wind.txt) |
| Lincoln Clean Energy LLC | Developer (likely) | Triage: ERCOT queue identified; [GLEIF Chicago HQ](sources/2026-07-19_gleif_helena-wind-llc.txt) consistent |
| Ørsted A/S | Ultimate parent (likely) | Acquired Lincoln Clean Energy 2018 |

- Financing: project operating since 2022 — financing closed prior to COD; specifics not obtained (no press releases found, PUCT 402)

## 4. Land & county records

- Tenure: **leased** (inferred — wind farms in South Texas operate on agricultural lease land)
- Abatements/agreements: not obtained — TX Comptroller Ch.312/313 search requires JS form; Bee County CAD (esearch.beecad.org) returned HTTP 404 on all owner-name queries
- CAD: 0 hits for "foxtrot" or "lincoln" owner names; portal search endpoint not functional via fetch

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: AEP 88689 Tango 345kV station; EIA 860 shows final grid connection via South Texas Electric Coop at 345kV
- IA: signed 2020-05-05 per ERCOT milestone data; PDF not retrieved (PUCT Interchange HTTP 402)
- Equipment per EIA 860: 180 Vestas V150-4.2 turbines

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2020-05-05 | unknown — PUCT 402 |

| Milestone | ERCOT queue record |
|---|---|
| IA signed | 2020-05-05 |
| FIS approved | 2021-07-30 |
| Approved for energization | 2022-02-23 |
| Approved for synchronization | 2022-03-09 |
| Commercial operation approved (ERCOT) | — (never recorded) |
| EIA 860 operating date | 2022-06 |

- Queue-history COD drift ([timeline.md](timeline.md)): 45 changes, 2020-05-01 → 2026-08-31 (8 years); COD rolling monthly since early 2022 with no construction dates ever reported

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Turbines visible as white dots with access road network across ~10 km × 10 km area; solar panels in lower frame (different project) | [png](imagery/s2_28.62_-97.94_2026-07-01.png) |
| 2026-07-01 (prior triage) | Imagery at county centroid (28.39, -97.77) — hit Beeville town center, not turbine site | [png](imagery/s2_28.39_-97.77_2026-07-01.png) |

- Verdict: **operating** — turbines installed and visible at the Helena Wind / Foxtrot Wind site; access road network consistent with 180-turbine operational wind farm

## 7. COD assessment

- The ERCOT queue entry 20INR0129 shows approved-for-synchronization 2022-03-09 but no approved-for-commercial-operation date — strongly consistent with a project that achieved commercial operation under a renamed entity (Helena Wind LLC) without the original Foxtrot Wind LLC queue entry ever being formally closed
- EIA Form 860 confirms Helena Wind (exact 268.2 MW match) has been operating since June 2022 — 4+ years before the reported queue COD of 2026-08-31
- The reported COD of 2026-08-31 is a queue artifact: 45 COD changes over 8 years, with the COD rolling forward every month since 2022 without construction start/end dates ever being reported — a classic stale-open queue entry
- **Independent COD estimate: 2022-Q2** (June 2022 per EIA 860) — not a future date
- **Drift risk: not applicable** — project is already operating; the queue entry may close on its own schedule or remain indefinitely open if the developer never filed a formal queue withdrawal

## 8. Could not determine

- **Definitive proof of Foxtrot Wind LLC = Helena Wind LLC project identity**: PUCT Interchange IA (HTTP 402) would confirm shared POI and parties; FAA OE shutdown prevents turbine-coordinate cross-check
- Financial security amount in original IA and any amendments
- Exact site acreage from IA or CAD parcels
- Developer/owner chain documentation (TX SOS HTTP 403; TX Comptroller JS-only; no press releases returned)
- Pentagon wind-pause status (May 2026, 54 TX projects): unconfirmed for this project — irrelevant if already operating
- Whether ERCOT will formally close 20INR0129 or leave it as an open queue entry
