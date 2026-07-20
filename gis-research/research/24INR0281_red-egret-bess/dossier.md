# Dossier — Red Egret BESS (24INR0281)

Researched 2026-07-19 · site 29.4040, -94.9951 · verdict **real_active**

## 1. Verdict

- **real_active** — ERCOT TPIT Project 90452 (2026-07-13) lists the gen tie as "Under Construction," in-service target 2026-08-31 ([TPIT xlsx](sources/2026-07-19_ercot_tpit-july-2026.xlsx))
- Construction: **under_construction** (TPIT-confirmed); no satellite visual confirmation (CDSE auth expired mid-session)
- Site: 29.4040, -94.9951 — Freeway Park Substation centroid, TNMP 138kV ([OSM way 336628605](https://www.openstreetmap.org/way/336628605)); BESS pad within 1.15 mi, exact location unknown ([satellite view](https://www.google.com/maps/@29.4040,-94.9951,14z/data=!3m1!1e3))
- COD: reported 2026-08-31 → independent **2026-Q4**, drift risk **high** (6 prior slips; gen tie still listed "under construction" 43 days before COD)

## 2. Site identification

- Derivation: POI "38820 FREEWAY PARK 138KV" → OSM query confirmed TNMP Freeway Park Substation at 29.4040, -94.9951 ([OSM way 336628605](https://www.openstreetmap.org/way/336628605))
- **Stated project area: unknown** — no abatement, no IA exhibit retrieved, Galveston CAD server refused connections; BESS 310 MW ≈ 40-60 acres expected
- Cross-checks: TPIT bus 38820 = Freeway Park (POI match); TPIT 1.15-mi gen tie = new bus 113533 (BESS pad within 1.85 km of substation)
- Not obtainable: exact BESS pad coordinates (no IA exhibit, no pin, no CAD parcel, no news); CDSE imagery inconclusive

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Red Egret LLC | SPV | [TX Comptroller entity](sources/2026-07-19_txcpa_red-egret-llc-entity.json) — DE corp, SOS reg 2022-11, ZIP 78746 |
| Clearway Energy Group LLC | developer/owner (private) | Officers at 300 Carnegie Center Dr Suite 300 Princeton NJ 08540 = Clearway HQ; Craig Cornelius (President) = CEG CEO ([TX Comptroller](sources/2026-07-19_txcpa_red-egret-llc-entity.json)) |
| TotalEnergies SE (~51%) / GIP (~49%) | ultimate owners of Clearway Energy Group | public record |
| EPC / PPA offtaker | unknown | zero web footprint |

- Financing: unknown — no press release for construction start or financing close; Clearway Energy Group is private (no SEC reporting)

## 4. Land & county records

- Tenure: **unknown** — Galveston CAD server refused connections (ECONNREFUSED); no parcels found under Red Egret or Clearway; leased land expected for BESS
- Abatements/agreements: none found — Ch.313 expired 2022; no JETI agreement; normal for 2024 INR BESS project in Galveston (little land)
- CAD: 0 parcels confirmed (server offline); 0 results on prior attempt — consistent with leased land under a private lease

## 5. Interconnection & contractual schedule

- POI per TPIT: Bus 38820 (FREEWAY PARK 138kV), Galveston County, TNMP ([TPIT xlsx](sources/2026-07-19_ercot_tpit-july-2026.xlsx))
- Gen tie: 1.15 miles, 138kV, TNMP project 90452; new BESS bus 113533
- IA signed 2023-06-07 (queue milestone) — document not retrieved (PUCT Interchange requires auth, HTTP 402)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2023-06-07 | unknown — document not retrieved |

| Milestone | Source |
|---|---|
| In-Service | 2026-08-31 per TPIT; original IA schedule unknown |
| Scheduled COD | 2026-08-31 per ERCOT queue (6th revision) |

- Queue-history COD drift ([timeline.md](timeline.md)): **6 changes** — 2024-12-01 → 2025-10-23 → 2025-06-01 → 2025-09-01 → 2025-08-01 → 2025-12-31 → 2026-08-31

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-01-15 | Suburban/industrial corridor along I-45; substation at 29.4040, -94.9951 area visible; no compact BESS pad signature | [2026-01](imagery/s2_2026-01-15.png) |
| 2026-05-01 | Same area, partial cloud; no BESS pad signature | [2026-05](imagery/s2_2026-05-01.png) |
| 2026-06-15 | Mostly cloudy | [2026-06](imagery/s2_2026-06-15.png) |
| 2026-07 (grid) | 8 tight chips (1km buffer) around substation; no BESS pad visible | [contact grid](imagery/grid/contact_grid.png) |

- Verdict: **inconclusive** — CDSE authentication expired mid-session; confirmed substation but BESS pad (≈40-60 ac) not located in any frame; suburban/industrial setting with mixed ground cover makes small pads easy to miss at 10 m/px

## 7. COD assessment

- Reported 2026-08-31 matches **exactly** the ERCOT TPIT in-service date — these are likely the same milestone, not independent corroboration
- TPIT "Under Construction" as of 2026-07-13 confirms physical work is real and underway — decisive against a "paper project" conclusion
- FIS approved only 2025-08-21 (11 months before claimed COD) — BESS builds take 12-18 months; this is structurally tight
- Six prior COD slips (net 20 months of drift from 2024-12-01 original) signals systematic schedule optimism
- No commissioning announcement, no press release, gen tie still listed "under construction" not "energized" 43 days before COD
- BESS commissioning and testing alone can take 2-4 months after gen tie energization
- **Independent estimate: 2026-Q4, drift risk high** — construction is real, but 2026-08-31 COD is extremely unlikely; 2026-Q4 achievable if no major issues; 2027-Q1 or later plausible

## 8. Could not determine

- Exact BESS pad lat/lon (no IA exhibit, no delivery pin, no CAD parcel, CDSE auth expired)
- Project acreage (no IA, no abatement)
- IA milestone schedule and financial security amounts (PUCT Interchange requires paid authentication)
- EPC contractor and PPA offtaker (zero web footprint)
- Financing status (Clearway Energy Group is private, no SEC reporting for this asset)
- Construction start date (CDSE imagery inconclusive; no visible grading in available frames)
