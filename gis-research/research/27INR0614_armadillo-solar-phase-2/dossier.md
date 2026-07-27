# Dossier — Armadillo Solar Phase 2 (27INR0614)

Researched 2026-07-23 · site 32.008418, -96.374303 · verdict **real_early**

## 1. Verdict

- **real_early** — no IA of its own, but co-located with an actively-building sibling (21INR0421) sharing SPV, EPC, and POI ([TCEQ storm registry](sources/armadillo_row_p6_map.png), [Phase 1 IA](sources/2026-07-23_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf))
- Construction: **racking** (attributable to Phase 1, not confirmed for Phase 2 specifically), first activity bracketed 2025-Q3/Q4 ([2025-11 frame](imagery/grid_current/s2_2025-11-01.png))
- Site: 32.008418, -96.374303 — Google Places pin + TCEQ physical-location text cross-check, high confidence ([map](https://www.google.com/maps/@32.008418,-96.374303,5000m/data=!3m1!1e3))
- COD: reported 2027-03-04 → independent **2027-Q4 (low confidence)**, drift risk **high** (no IA yet; sibling slipped 4 years)

## 2. Site identification

- Derivation: Google Places pin "Armadillo Solar", 5950 SE 2050, Corsicana TX ([gmaps.py places](sources/t3_aes_project_page.md)) matches TCEQ Central Registry physical-location text "SOUTH OF THE INTERSECTION OF STATE HIGHWAY 287 AND SE COUNTY ROAD 2040 BETWEEN THE CITIES OF MILDRED AND NAVARRO TX" (facility RN112015482)
- **Stated project area: 2,300 acres** per [Corsicana Daily Sun 2020](sources/2026-07-23_corsicanadailysun_solar-center-planned.html) — independently cross-checked by summing the 27 parcels in the [Ch.312 abatement Exhibit B](sources/2026-07-23_navarrocounty_tax-abatement-armadillo-solar.pdf) = 2,335.6 acres; imagery footprint consistent (two large graded clusters spanning ~2-3 km)
- Cross-checks (each linked): TCEQ physical-location description; [2021 ROW-agreement project-area map](sources/armadillo_row_p6_map.png) (two adjoining polygons, 8.91 mi of adjacent county roads); [2020 Ch.312 reinvestment-zone map](sources/armadillo_ch312_p19_map.png) (same dogleg boundary); Sentinel-2 imagery shows matching two-cluster grading — all agree within ~1 km
- Not obtainable: which of the two graded polygons is Phase 1 (21INR0421) vs Phase 2 (27INR0614) specifically — no document splits the original combined footprint by queue number

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Armadillo Solar Center, LLC | SPV (shell, shared by Phase 1 & Phase 2) | [TCEQ RN112015482](sources/2026-07-23_navarrocounty_row-agreement-armadillo-solar.pdf); IA party on [Phase 1 IA](sources/2026-07-23_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf) |
| The AES Corporation | developer/owner (post-2024) | TCEQ RN111934428 storm permit; [AES project page](sources/t3_aes_project_page.md); Generator notice address in IA Amendment 5 is AES's Louisville CO office |
| Ørsted Onshore North America, LLC | original developer (2020-2024) | sole-member chain on [2021 ROW agreement](sources/2026-07-23_navarrocounty_row-agreement-armadillo-solar.pdf) signature page; [Corsicana Daily Sun 2020](sources/2026-07-23_corsicanadailysun_solar-center-planned.html) |
| Hanwha Q Cells EPC USA LLC | EPC | [TCEQ RN112015482](sources/2026-07-23_navarrocounty_row-agreement-armadillo-solar.pdf), ACTIVE storm permit TXR1538TO co-owner since 2025-02-07 |

- Financing: not disclosed in any artifact found; no PR Newswire / financing-close announcement located

## 4. Land & county records

- Tenure: **leased** — Corsicana Daily Sun: "reinvestment zone includes connected properties under lease from six property owners" ([article](sources/2026-07-23_corsicanadailysun_solar-center-planned.html)); Ch.312 Exhibit B lists 8 distinct landowner groups across 27 parcels ([agreement](sources/2026-07-23_navarrocounty_tax-abatement-armadillo-solar.pdf))
- Abatements: Ch.312 Tax Abatement Agreement, Navarro County + Armadillo Solar Center LLC, approved 2020-10-12 — ≥175 MW, ≥$140M investment, 100%/10-yr abatement, anticipated COD 2024-12-31 (missed) ([agreement](sources/2026-07-23_navarrocounty_tax-abatement-armadillo-solar.pdf)). This agreement covers the ORIGINAL combined project, not confirmed as split by queue number. `ch312.py resolve` and `ch313.py resolve` both returned negative — the agreement predates/was purged from the Comptroller's open-data tables; only found via the county's own document server
- CAD: not queried directly (Ch.312 Exhibit B parcel IDs stand in as the county-record equivalent)

## 5. Interconnection & contractual schedule

- **No IA found for 27INR0614 itself** — queue milestones confirm `iaSigned: null`. All 4 IA filings located under "Armadillo Solar Center" are captioned **GINR 21INR0421** (Phase 1), never 27INR0614
- POI per Phase 1's IA: "Revolution Switch at 138kV... adjacent to TSP's existing 69kV Navarro Sub on Main St in the town of Navarro" ([IA](sources/2026-07-23_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf)) — matches target's queue POI text "3387 Revolution 138kV" (same substation)
- Equipment (Phase 1, Exhibit C): originally 270× TMEIC PCS-840 inverters (204 MW net); Amendment 7 (2025) changed to 57× SMA SC4400-UP-US inverters (202.6 MW at generator terminals)

| IA document (Phase 1, 21INR0421 — NOT the target INR) | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-23_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf)) | 2021-02-02 | $4,086,825 → $9,081,832 (2021-2022 schedule) |
| Amendment 5 ([pdf](sources/unverified_2026-07-23_puct_35077-1926_amendment-no-5-to-the-standard-generation-interc.pdf)) | 2024-08-14 | $10,833,691 (2024-12-04) |
| Amendment 6 ([pdf](sources/unverified_2026-07-23_puct_35077-2216_amendment-no-6-to-the-standard-generation-interc.pdf)) | 2025-08-01 | unchanged |
| Amendment 7 ([pdf](sources/unverified_2026-07-23_puct_35077-2295_amendment-no-7-to-the-standard-generation-interc.pdf)) | 2025-10-31 | unchanged |

| Milestone (Phase 1) | Original IA 2021 | Amendment 7 2025 |
|---|---|---|
| In-Service | 2022-11-17 | 2026-04-16 |
| Trial Operation | 2022-11-27 | 2026-06-01 |
| Scheduled COD | 2022-12-31 | 2026-12-31 |

- Queue-history COD drift for 27INR0614 itself ([timeline.md](timeline.md)): 0 changes, 1 snapshot only (2026-06-01) — too new to show drift
- Not in EIA-860M ([eia_history.py](sources/../log.md)) — expected pre-IA

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-06 | undisturbed farmland across full combined site | [2024-06](imagery/grid_current/s2_2024-06-01.png) |
| 2025-01 | still undisturbed | [2025-01](imagery/grid_current/s2_2025-01-01.png) |
| 2025-08 | partly cloudy, grading ambiguous | [2025-08](imagery/grid_current/s2_2025-08-15.png) |
| 2025-11 | multiple large graded polygons, internal racking rows visible, both site clusters active | [2025-11](imagery/grid_current/s2_2025-11-01.png) |
| 2026-07 | graded footprint stable/expanded, racking rows persist | [2026-07](imagery/s2_2026-07-20_wide.png) |

- Verdict: **racking** — bulk earthwork visible by 2025-11 across the shared site; imagery cannot distinguish which cluster is Phase 1 vs Phase 2, and Phase 1's own contractual schedule (In-Service 2026-04-16) fully accounts for the observed activity without requiring Phase 2 to have started

## 7. COD assessment

- 27INR0614 has no signed IA — screening/FIS/IA/construction milestones all null except FIS requested 2026-06-26; this stage is normally 18-36 months from an IA, independent of the sibling's progress
- The co-located sibling (21INR0421, same SPV/EPC/POI) slipped its own COD by exactly 4 years across 6+ amendments (2022-12-31 → 2026-12-31); the original 2020 Ch.312 abatement target (2024-12-31) was also missed
- Applying a comparable slip pattern to Phase 2's claimed 2027-03-04 makes that date read as an early placeholder rather than a grounded schedule
- For: real, active developer (AES) and EPC (Hanwha Q Cells) with an ACTIVE TCEQ construction registration at the shared site; this is not a paper/speculative shell — the site is genuinely under construction, just for the sibling phase
- **Independent estimate: 2027-Q4 (low confidence), drift risk high** — will firm up once Phase 2's own IA is located

## 8. Could not determine

- Which of the two graded site polygons (visible in imagery and the 2021 project-area map) corresponds to Phase 2 vs Phase 1 specifically
- Whether Phase 2 has an executed IA under a name/number not yet surfaced by the PUCT docket-index name-match (only exact "Armadillo Solar" keys were tried)
- Financing status/close for either phase
- Exact CAD parcel-level detail for Phase 2's footprint (Ch.312 Exhibit B parcels are for the original combined 2020 filing, not phase-split)
