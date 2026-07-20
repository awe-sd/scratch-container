# Dossier — Cottonwood Bayou Solar (19INR0134)

Researched 2026-07-19 · site 29.2512, -95.2589 · verdict **real_active**

## 1. Verdict

- **real_active** — 17 OSM solar-plant polygons confirm installed footprint between Liverpool and Petson 138kV substations; ERCOT energization approved 2024-05-01; timelapse shows modules installed by 2024-01 ([contact sheet](imagery/contact_sheet.png))
- Construction: **substantially_complete**, first activity 2023-01 ([frame](imagery/cluster_2024-01.png))
- Site: 29.2512, -95.2589 — OSM polygon-cluster centroid, confidence **high** ([map](https://google.com/maps/@29.2512,-95.2589,5000m/data=!3m1!1e3))
- COD: reported 2026-08-29 → independent **2026-Q3/Q4**, drift risk **high** (14+ months of monthly slipping post-energization; physical build done)

## 2. Site identification

- Derivation: POI names "138kV Liverpool–Petson tap"; OSM Overpass confirmed Liverpool Substation at 29.2791, -95.2949 (CenterPoint Energy, [OSM way/336253179](sources/2026-07-19_osm_overpass_solar_plants_brazoria.json)) and Petson Substation at 29.2530, -95.2203 ([OSM way/336253275](sources/2026-07-19_osm_overpass_solar_plants_brazoria.json)); 17 unnamed solar-plant polygons cluster between them
- **Stated project area: not confirmed** — IA not retrieved; OSM polygon bounding box ~29.227–29.267N, -95.242 to -95.277 implies ~3,000–4,000 acres; consistent with 455 MW at ~5–8 ac/MW — imagery footprint consistent with this range
- Cross-checks: POI substations ↔ OSM solar cluster agree within 0.5 km; farmland-to-panels transition in timelapse centered on same polygon cluster
- Not obtainable: exact parcel description, acreage per IA (PUCT portal JS-blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Cottonwood Bayou Solar, LLC | SPV | ERCOT queue data; SEC XBRL |
| TotalEnergies SE | developer / operator (ultimate parent) | [6-K 2024-01-02](sources/2024-01-02_totalenergies_6k_lyondellbasell_cppa.htm) |
| Cottonwood Solar Cash Equity HoldCo, LLC | direct owner (100%) | TotalEnergies FY2024 20-F (SEC 0001104659-25-029751) |
| Cottonwood Solar Class B HoldCo, LLC | 50% equity investor (sold Dec 2024) | TotalEnergies FY2024 20-F |
| LyondellBasell | offtaker (12-yr CPPA, 2022) | [6-K 2024-01-02](sources/2024-01-02_totalenergies_6k_lyondellbasell_cppa.htm) |

- Financing: Dec 2024 — TotalEnergies sold 50% stake in 3-project portfolio (Cottonwood + Danish Fields + Hill Solar I) but retained operatorship ([TotalEnergies FY2024 20-F](sources/2024-02-07_totalenergies_6k_results.htm))

## 4. Land & county records

- Tenure: **unknown** — BCAD portal JS-blocked, no parcel lookup completed; TotalEnergies likely leases or owns farmland in Brazoria County (typical for utility-scale solar)
- Abatements/agreements: No Ch.313/JETI record found (TX Comptroller search blocked; Ch.313 program ended 2022; 2019 vintage could have applied)
- CAD: 0 hits confirmed — portal inaccessible during research

## 5. Interconnection & contractual schedule

- POI per queue data: "tap 138kV 42870 Liverpool - 43070 Petson" — both substations confirmed via OSM ([evidence](sources/2026-07-19_osm_overpass_solar_plants_brazoria.json))
- Equipment: 455 MW per TotalEnergies disclosure ([6-K](sources/2024-01-02_totalenergies_6k_lyondellbasell_cppa.htm)); ERCOT queue shows 351.4 MW (net capacity registered differs from nameplate)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2019-11-13 | not retrieved (PUCT portal JS-blocked) |

| Milestone | Status |
|---|---|
| IA Signed | 2019-11-13 |
| FIS Approved | 2023-04-27 |
| Meets all 6.9 | 2023-04-27 |
| Approved for Energization | 2024-05-01 |
| Approved for Synchronization | 2024-05-29 |
| Commercial Operation Approved | — (pending) |

- Queue-history COD drift (from [timeline.md](timeline.md)): **25 changes**, 2020-11-01 → 2026-08-29; monthly slipping since mid-2024

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2022-01 to 2022-12 | Agricultural land — rice/crop fields, no construction | [contact sheet](imagery/contact_sheet.png) |
| 2023-01 | First rectangular clearing/grading distinct from farm patterns | [contact sheet](imagery/contact_sheet.png) |
| 2023-06 to 2023-12 | Active construction — graded rectangular parcels expanding | [contact sheet](imagery/contact_sheet.png) |
| 2024-01 | Uniform dark rectangular blocks across site — modules installed | [2024-01](imagery/cluster_2024-01.png) |
| 2024-05 | ERCOT energization approved | — |
| 2026-06 | Same dark panel signature, stable footprint | [2026-06](imagery/cluster_centroid_4km.png) |

- Verdict: **substantially_complete** — dark PV-module signature present from 2024-01 through latest frame; energization/sync approved May 2024; COD milestone still pending in ERCOT

## 7. COD assessment

- Project is **physically complete**: modules installed ~2024-Q1, energization + sync both ERCOT-approved May 2024
- TotalEnergies announced COD "end of 2024" in Dec 2023 press release; has slipped 18+ months
- 25 queue COD changes total; 14+ consecutive monthly slips after energization approval — unusually persistent for a built project
- Gating issue is unknown but not construction: likely ERCOT commercial-operation testing protocol, PPA commercial terms with LyondellBasell, or project-level contract trigger
- **Independent estimate: 2026-Q3 to 2026-Q4** — the 2026-08-29 reported date is plausible since the project is built; but pattern strongly suggests another slip is possible
- **Drift risk: HIGH** — 25 prior slips; monthly cadence; no commercial-operation approval as of June 2026

## 8. Could not determine

- Exact parcel acreage and tract description (IA not retrieved; BCAD portal blocked)
- Financial security amount in IA (document not obtained)
- Precise COD hold reason (ERCOT admin / PPA commercial terms / permitting — unknown)
- Ch.313/JETI abatement details (TX Comptroller portal blocked; program ended 2022)
- EPC contractor identity (no press release or news found)
