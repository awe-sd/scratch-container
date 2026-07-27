# Dossier — SanPat Solar I (25INR0081)

Researched 2026-07-19 · site 28.0150, -97.4100 · verdict **real_active**

## 1. Verdict

- **real_active** — large installed solar array confirmed at site matching IA location description; signed Second Amended IA (Feb 2026) with $37.5M security posted ([IA](sources/2026-07-19_puct_35077-2434_aep-sanpat-solar-IA-amend2.pdf))
- Construction: **substantially_complete**, first panels **2024-Q4** ([Nov 2024 frame](imagery/key/s2_2024-11-01.png))
- Site: 28.0150, -97.4100 — Sentinel-2 imagery feature, high confidence ([satellite view](https://www.google.com/maps/@28.015,-97.41,5000m/data=!3m1!1e3))
- COD: reported 2027-07-08 → independent **2027-Q2**, drift risk **medium** (TSP Lucero Station TIF outstanding; 5 prior COD slips)

## 2. Site identification

- Derivation: Sentinel-2 2026-07-10 shows large multi-block solar array at 28.015N, 97.41W; cross-validated against IA Exhibit C "approximately 6.6 miles north of Gregory, Texas" ([First Amended IA](sources/2026-07-19_puct_35077-1780_aep-sanpat-solar-IA-amend1.pdf))
- **Stated project area: not in IA or available county docs** — imagery footprint spans ~4-5 km diagonal, consistent with ~308 MW
- Cross-checks: IA location "6.6 mi N of Gregory TX" → calculated 28.018N, 97.293W; actual array found at 28.015N, 97.41W (6.3 mi NNW of Gregory — consistent within ~1 mi of stated distance)
- Not obtainable: exact Lucero Station coordinates (new station not yet in OSM/Nominatim); CAD parcels (0 hits, expected for leased land)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Padre Solar LLC | SPV (25INR0081) | [Second Amended IA](sources/2026-07-19_puct_35077-2434_aep-sanpat-solar-IA-amend2.pdf) §1.5 |
| CGRP 10, LLC | Designated Interconnection Agent | [Second Amended IA](sources/2026-07-19_puct_35077-2434_aep-sanpat-solar-IA-amend2.pdf) preamble |
| CleanGen Inc. | Developer (Bechtel's renewable subsidiary) | [First Amended IA](sources/2026-07-19_puct_35077-1780_aep-sanpat-solar-IA-amend1.pdf) Exhibit D (notices to hchi@bechtel.com, padresolar@bechtel.com) |
| Bechtel Enterprises, Inc. | Parent company | [First Amended IA](sources/2026-07-19_puct_35077-1780_aep-sanpat-solar-IA-amend1.pdf) Exhibit D copy to klmeikle@bechtel.com; banking via Bechtel Capital Management |
| AEP Texas Inc. | TSP (transmission) | [Second Amended IA](sources/2026-07-19_puct_35077-2434_aep-sanpat-solar-IA-amend2.pdf) |

- Financing: no public announcement found; $37.5M security posted with AEP Texas = substantial committed capital. No PPA or lender named in public record.

## 4. Land & county records

- Tenure: **unknown** — no CAD hits for Padre Solar, SanPat Solar, CGRP, or CleanGen in San Patricio CAD; likely leased agricultural land
- Abatements: none found (expected; Ch.313 expired 2022, JETI not required)
- CAD: 0 results for any project/developer entity — normal for leased farmland
- Commissioners court: not searched (no abatement exists to locate there)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Lucero Station" — new AEP 345kV station tapping existing Angstrom–Naismith 345kV line; ~10 mi from Angstrom, ~7 mi from Naismith ([First Amended IA Exhibit C-1](sources/2026-07-19_puct_35077-1780_aep-sanpat-solar-IA-amend1.pdf))
- Equipment (Exhibit C, Second Amended): 82 × Sungrow SG4400UD-MV-US inverters; 308.8 MW
- Note: project originally filed as "Copano Solar" → renamed SanPat Solar I per First Amended IA

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2023-10-18 | $28,000,000 |
| First Amended and Restated ([pdf](sources/2026-07-19_puct_35077-1780_aep-sanpat-solar-IA-amend1.pdf)) | 2024-03-26 | $28,000,000 (confirmed) |
| Second Amended and Restated ([pdf](sources/2026-07-19_puct_35077-2434_aep-sanpat-solar-IA-amend2.pdf)) | 2026-02-23 | $37,500,000 (+$9.5M increase) |

| Milestone | Original IA (months from 2023-10-18) | Second Amended IA |
|---|---|---|
| In-Service | 36 mo → 2026-10-18 | same |
| Trial Operation (Phase 1) | 37 mo → 2026-11-18 | **43 mo → 2027-05-18** |
| Scheduled COD (Phase 1) | 38 mo → 2026-12-18 | **44 mo → 2027-06-18** |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2025-07-01 → 2027-05-31 → 2026-12-31 → 2027-06-01 → 2027-10-01 → 2027-07-08 (held since 2025-10)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-01 | Graded/cleared fields — site preparation, no panels | [png](imagery/key/s2_2024-01-01.png) |
| 2024-08 | Cleared fields; no panels (partly cloudy) | [png](imagery/key/s2_2024-08-01.png) |
| 2024-11 | **Panel arrays first visible** — racking installed | [png](imagery/key/s2_2024-11-01.png) |
| 2025-01 | Panels clearly installed, multiple parcels | [png](imagery/key/s2_2025-01-01.png) |
| 2026-01 | Panels installed, operational appearance | [png](imagery/key/s2_2026-01-01.png) |
| 2026-07 | **Substantially complete** — large multi-block array | [png](imagery/key/s2_2026-07-10_center.png) |

- Verdict: **substantially_complete** — full panel footprint installed; substation/electrical not visually confirmed at 10 m/px

## 7. COD assessment

- Contractual COD (Second Amended IA, Phase 1): **2027-06-18**; reported queue COD 2027-07-08 is ~3 weeks later — within rounding, consistent
- Observed pace: panels substantially installed Jul 2026, ~12 months ahead of TSP In-Service date (Oct 2026); generator-side work effectively complete
- Primary remaining risk: **TSP Lucero Station TIF** — AEP must complete the new 345kV station; this is outside generator control and is the binding constraint for the In-Service Date (Oct 2026)
- Financial security increased $9.5M in Feb 2026 amendment → active engagement, not stalled
- No public PPA or financing announcement; Bechtel's balance sheet backstops security
- For: construction substantially done, Bechtel-grade developer, security posted, COD stable since Oct 2025
- Against: FIS not approved, "Meets all 6.9" not achieved — suggests TSP-side work incomplete; 5 prior COD slips; no lender/PPA public confirmation
- **Independent estimate: 2027-Q2, drift risk medium**

## 8. Could not determine

- Exact Lucero Station coordinates (new station not in public databases; CEII-protected)
- Land tenure/parcel owner names (0 CAD hits; leased farmland assumed)
- PPA offtaker or project financing lender (no public announcement)
- CleanGen Inc. corporate structure beyond Bechtel affiliation (no public website)
- Timelapse dekad (CDSE throttled after first timelapse attempt)
- First activity date tighter than Aug–Nov 2024 bracket
