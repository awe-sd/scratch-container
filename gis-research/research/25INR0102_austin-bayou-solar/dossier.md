# Dossier — Austin Bayou Solar (25INR0102)

Researched 2026-07-20 · site 29.32227, -95.38916 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2023-11-15 ([PUCT 35077-1704](sources/unverified_2026-07-20_puct_35077-1704_ercot-standard-generation-interconnection-agreem.pdf)), financial security posted per queue, co-located storage IA executed 2025-02-14 ([PUCT 35077-2079](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf))
- Construction: **no_activity** — zero clearing/grading/racking in Sentinel-2 frames Mar 2025, Dec 2025, Jul 2026 ([s2_2025-03-01](imagery/s2_2025-03-01.png), [s2_2025-12-01](imagery/s2_2025-12-01.png), [s2_2026-07-01](imagery/s2_2026-07-01.png))
- Site: 29.32227, -95.38916 — POI from co-located storage IA Exhibit C (storage+solar share the 345kV Savana–Seabreeze tap), Danbury TX area, Brazoria County ([POI source](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf))
- COD: reported 2027-06-01 → independent **2028-Q4 to 2029+**, drift risk **high** (zero ground activity + FIS stalled + storage TIF not ready until 2029-10)

## 2. Site identification

- Derivation: POI coordinates 29.3222714N, -95.3891644W extracted from storage IA Exhibit C ([pdf p.43](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf)) — solar and storage share the same 345kV interconnection tap on Savana 43180–Seabreeze 43020 Ckt 27
- **Stated project area: unknown** — solar IA is image-only (unreadable); no Ch.313/JETI abatement; Brazoria CAD portal JS-driven (no parcel hit)
- Cross-checks: POI in Brazoria County ✓ · Austin Bayou Golf Course at 29.291,-95.364 confirms Danbury TX area · Cottonwood Bayou Solar (neighbor, same CenterPoint service territory) at 29.261,-95.272 · no Google Maps construction delivery pin found
- Not obtainable: exact array parcel; switch coordinates for Savana/Seabreeze (CEII); static map (Maps Static API not enabled)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Austin Bayou Solar, LLC | SPV / PUCT signatory | [Storage IA cover](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf) |
| SunChase Power (Austin TX) | Developer | [IA Exhibit D](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf) p.51 — Mark Soutter VP, mark@sunchasepower.com; confirmed at [sunchasepower.com/about-us-5/](https://sunchasepower.com/about-us-5/) |
| Lagniappe Renewable Energy, LLC | EFT beneficiary / financing | [IA Exhibit D](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf) p.51 — BancFirst Oklahoma City |
| Unknown | PPA / offtaker | Not found |
| Unknown | EPC | Not found |

- Financing: Lagniappe Renewable Energy LLC (BancFirst OK) named as EFT recipient — financing relationship established but structure unknown; NOT in EIA-860M (no operating registration)

## 4. Land & county records

- Tenure: **unknown** — solar IA is image-only scan; no Ch.313/JETI abatement filing; Brazoria CAD portal not searchable via script
- Abatements/agreements: Ch.313 NEGATIVE, JETI NEGATIVE (expected post-2022); no county commissioner minutes found
- CAD: no parcels returned — Brazoria CAD portal is JS-rendered; direct URL search returned 404

## 5. Interconnection & contractual schedule

- POI per storage IA: "TSP system side of Plant's terminating structure(s), located approximately at 29.3222714N: -95.3891644W, Brazoria County, Texas. Delivery Voltage: 345 kV." ([IA Exhibit C p.43](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf))
- Queue POI description: "Tap 345 kV Savana 43180 to Seabreeze 43020 - Ckt 27" (solar + storage share tap)
- FIS: requested 2022-07-26, **NEVER approved** through 2026-06-01 — 4-year stall; persistent interconnection risk
- Solar IA schedule: **unknown** — Exhibit B is in image-only PDF

| IA document | Signed | Financial security posted |
|---|---|---|
| Solar SGIA ([pdf](sources/unverified_2026-07-20_puct_35077-1704_ercot-standard-generation-interconnection-agreem.pdf)) | 2023-11-15 | Unknown — image-only PDF |
| Storage SGIA ([pdf](sources/2026-07-19_puct_35077-2079_austin-bayou-solar-IA_main.pdf)) | 2025-02-14 | $21,830,000 irrevocable LC |

| Milestone | Solar IA (2023) | Storage IA (2025) |
|---|---|---|
| Prerequisites due | unknown (image-only) | 2025-02-14 |
| TIF In-Service | unknown | 2029-10-11 (or 56 mo.) |
| Scheduled COD | unknown | 2030-01-11 |

- Queue-history COD drift ([timeline.md](timeline.md)): 2 changes — 2025-02-04 → 2025-03-01 → **2027-06-01** (~2.3yr total slip from first-reported)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-03 | Undisturbed agricultural land, bare/fallow fields | [png](imagery/s2_2025-03-01.png) |
| 2025-12 | Undisturbed agricultural land, bare/fallow, minor cloud | [png](imagery/s2_2025-12-01.png) |
| 2026-07 | Undisturbed agricultural land, partly cloudy, no disturbance | [png](imagery/s2_2026-07-01.png) |

- Verdict: **no_activity** — 16 months of frames show zero site preparation; cannot confirm exact array parcel from POI-centered view alone; CDSE tool failing for additional chips

## 7. COD assessment

- Claimed 2027-06-01 COD is **not achievable**: zero ground activity through July 2026 (11 months to claimed COD); 502 MW solar requires ~12–18 months of active construction after mobilization
- FIS never approved (4+ year stall since 2022-07-26) creates a hard interconnection-timing dependency; solar cannot connect until FIS infrastructure is built
- Co-located storage IA contractually places shared TIF In-Service at **2029-10-11** — if solar relies on the same tap infrastructure, it cannot COD before the TIF is ready
- COD slipped twice already (+2.3 yr); the absence of an EIA-860M registration (unlike most real active-build projects) adds to late-stage risk
- Independent estimate: **2028-Q4** if construction mobilizes in mid-2027 and FIS clears; **2029-H1** is equally plausible given storage TIF timeline; slip past 2029 possible if FIS remains open
- Drift risk: **high**

## 8. Could not determine

- Solar IA milestone schedule (Exhibit B) — image-only scan, unreadable
- Solar IA financial security amount
- Exact project parcel / acreage (CAD portal inaccessible, no abatement docs)
- PPA counterparty / offtaker
- EPC contractor
- Whether FIS stall is a ERCOT study queue hold or a developer-side issue
- Whether storage and solar share the same TIF or have independent interconnection paths
