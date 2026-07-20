# Dossier — Three Canes Solar (26INR0543)

Researched 2026-07-19 · site 31.9640, -96.5180 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed with Oncor Nov 2024 ([PUCT docket 35077-2019](https://interchange.puc.texas.gov/)); Solar Proponent (EnCap-backed) is a credible active ERCOT developer
- Construction: **pre_construction**, no activity confirmed in 9 satellite chips across Navarro County (2026-06-15)
- Site: 31.9640, -96.5180 — nearest 345kV node matching POI "68091 Navarro circuit" is Navarro Switching Station per [OSM Overpass](sources/2026-07-19_osm_overpass_navarro_substations.json); low-medium confidence (no parcel or IA map)
- COD: reported 2028-02-01 → independent **2029-Q1**, drift risk **high** (FIS still unapproved Jun 2026; 14-month slip history)

## 2. Site identification

- Derivation: OSM Overpass identified "Navarro Switching Station" (NextEra Energy, 345kV) at 31.9640°N, -96.5180°W as the best match for ERCOT node 68091 "Navarro" on the Big Brown–Navarro 345kV circuit ([source](sources/2026-07-19_osm_overpass_navarro_substations.json))
- **Stated project area: unknown** — no abatement application, CAD parcel, or IA exhibit retrieved; 334.5 MW solar implies ~1,500–2,500 acres; imagery footprint unverifiable
- Cross-checks: POI "68091 Navarro circuit" → OSM "Navarro Switching Station" at 31.964°N agree on county and 345kV voltage; no parcel or delivery pin available to confirm
- Not obtainable: exact POI switch coordinates (CEII); IA site map (PUCT Interchange JS-rendered, HTTP 402 during all access attempts)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Three Canes Solar, LLC | SPV | TX Comptroller entity #32095228121, formed 2024-05-23 (triage) |
| Solar Proponent LLC | Developer | [solarproponent.com](sources/2026-07-19_solarproponent_homepage.html); 9111 Jollyville Rd Ste 115, Austin TX 78759 |
| EnCap Investments LP | Majority backer (Energy Transition Fund) | [solarproponent.com](sources/2026-07-19_solarproponent_homepage.html) |
| Yorktown Partners | Co-investor | [solarproponent.com](sources/2026-07-19_solarproponent_homepage.html) |
| Mercuria Energy | Co-investor | [solarproponent.com](sources/2026-07-19_solarproponent_homepage.html) |
| EPC | unknown | not found |
| Offtaker/PPA | unknown | not found |

- Financing: PE-backed at development stage; no debt financing or PPA announcement found

## 4. Land & county records

- Tenure: **unknown** — Solar Proponent describes "purchases or leases land" for utility-scale projects; no specific land record found for this project
- Abatements/agreements: **none found** — Ch.313 closed 2022 (project entered queue 2024); JETI applicable but JETI applications portal JS-rendered, no data accessible; no county commissioners-court minutes found referencing project
- CAD: Navarro CAD portal ([navarrocad.com](https://navarrocad.com)) JS-gated; owner-name search returned 0 results (portal may require session cookies; absence inconclusive)

## 5. Interconnection & contractual schedule

- POI per queue data: "Tap 345kV 3381 Big Brown – 68091 Navarro circuit" (Oncor territory)
- IA signed 2024-11-27; filed at PUCT docket 35077-2019 on 2024-12-20
- IA PDF not retrieved — PUCT Interchange requires JavaScript; HTTP 402 on all direct access attempts

| IA document | Signed | Financial security posted |
|---|---|---|
| Oncor Standard Gen IA (docket 35077-2019) | 2024-11-27 | not retrieved |

| Milestone | Queue data |
|---|---|
| IA signed | 2024-11-27 |
| Meets 6.9(1) | 2025-02-12 |
| FIS approved | not achieved (as of 2026-06-01) |
| Construction start | not achieved |
| Scheduled COD (current) | 2028-02-01 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes**, 2026-12-31 → 2027-03-10 → 2027-07-31 → 2028-02-01 (+14 months total)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-15 | Undisturbed agricultural land at Navarro SW Station (6km buffer) | [png](imagery/s2_navarro_sw_2026-06-15.png) |
| 2026-06-15 | 4-point grid (N/S/E/W ±0.05°, 3km chips): no activity | [sheet](imagery/grid_sheet.png) |
| 2026-06-15 | Corridor mid (31.89, -96.29) and east (31.93, -96.18), 6km: no activity | [sheet](imagery/corridor_sheet.png) |
| 2026-06-15 | NW Navarro (31.97, -96.40) and SC (31.85, -96.35), 6km: no activity | [sheet](imagery/county_sheet2.png) |

- Verdict: **pre_construction** — no grading, clearing, or racking across 9 chips covering ~12×10 km of Navarro County; consistent with FIS-pending stage

## 7. COD assessment

- IA signed (Nov 2024) and 6.9(1) met (Feb 2025) are hard milestones confirming real project commitment by an active developer
- FIS not approved as of Jun 2026 (8 months post-IA) — unusual delay; FIS is a prerequisite for EPC and financing close
- No construction visible Jul 2026; even assuming FIS approved Q3 2026, 18-month build puts COD at earliest Q1 2028 — matching the claimed date with zero margin
- Three prior slips (+14 months total from original 2026-12-31) establish a pattern; any FIS delay or ERCOT study hold pushes to 2029+
- Independent estimate: **2029-Q1** with high drift risk; 2028-Q4 is possible only if FIS imminent and no further study issues

## 8. Could not determine

- Exact site lat/lon (no parcel, delivery pin, or IA map; OSM-derived candidate at 31.964°N, 96.518°W is approximate)
- Project area in acres
- Contractual milestone schedule (IA PDF inaccessible)
- Financial security amount
- EPC contractor
- PPA / offtaker
- Reason FIS is unapproved 8 months after IA signing
