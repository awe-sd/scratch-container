# Dossier — Cachena Solar SLF (23INR0027)

Researched 2026-07-20 · corrected 2026-07-21 · site 29.2579, -97.8057 · verdict **real_early**

> **2026-07-21 retraction.** Two prior site fixes were wrong: the original EIA-860M
> point (29.26357,-97.78055) is the Nixon, TX town centroid, not the plant; a later
> "corrected" point (29.456,-97.750, since deleted from this doc) was actually **Hoke
> Solar's (23INR0231)** footprint in Gonzales County, on an unrelated 138kV tap. Full
> chain in `findings.json` `retraction` and `log.md` (2026-07-21 section). The site
> below is re-derived from the project's own TCEQ stormwater-NOI address, and the
> verdict is downgraded from `real_active` to `real_early` since no construction is
> visually confirmable at the corrected site.

## 1. Verdict

- **real_early** — Enbridge FID July 22, 2025 ([PR](sources/2026-07-19_enbridge_pr_clear-fork-solar-fid.html)); $900M committed; Meta Platforms 100% PPA signed; financial security posted — paper trail is strong
- Construction: **not visually confirmed** — TCEQ stormwater NOIs (main array + substation) ACTIVE since Jan/Aug 2025 naming EPC Hanwha Q Cells, but a 2026-07-21 Sentinel-2 sweep (~24km x 24km) around the corrected site found no visible grading through 2026-07-09 ([findings.json](findings.json) `construction`)
- Site: **29.2579, -97.8057** — geocoded from the project's TCEQ stormwater-NOI address ("10046 US Highway 87 East", Wilson County) by two independent services (Esri ArcGIS + Google Places, agree to ~0.5 mi); confidence **medium** (documentary address anchor, not imagery/parcel-confirmed)
- COD: reported 2027-04-29 → independent **2027-Q3**, drift risk **med-high** (TSP switchyard on critical path; visual construction cross-check unavailable this pass)

## 2. Site identification

- **RE-DERIVED 2026-07-21**: TCEQ Central Registry construction-stormwater NOIs (`sources/2026-07-20_tceq_stormwater_nois_clearfork_cachena.json`) show THREE related registrations sharing the address "10046 US Highway 87 East", Wilson County — "CLEAR FORK CREEK SOLAR" (main array, EPC Hanwha Q Cells, active since 2025-08-15), "CLEAR FORK CREEK SOLAR SUBSTATION" (same EPC, since 2025-01-13), "CACHENA SOLAR POI" (owner Dorazio Enterprises, since 2025-07-09). Geocoded independently: Esri/ArcGIS World Geocoder (score 100) → 29.257169,-97.809055; Google Places API → 29.258670,-97.802252. Adopted point = average, **29.2579,-97.8057**.
- **Stated project area: 4,600 acres** per Enbridge FAQ ([FAQ](sources/2026-07-19_enbridge_clear-fork-solar-faq.html)) — imagery footprint still unconfirmed (see construction, below)
- Cross-checks:
  - Distance from Elm Creek 345kV substation (29.4673,-97.99988) to the new site = 18.57 mi, within 0.4% of the IA's stated "approximately 18.5 miles East" ([IA Amend 1-3](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf))
  - EIA-860M coords 29.26357,-97.78055 ([factsheet](factsheet.json)) — this is the Nixon, TX town centroid (administrative artifact, NOT the plant), but sits ~1.5 mi from the new address point (same neighborhood, loose corroboration only)
  - Enbridge map shows Clear Fork solar SE of San Antonio in Wilson County ([map](sources/2026-07-19_enbridge_clear-fork-solar-map.png)) — project-level only, no precision
  - CPS MTCPR: project "Cachena, Wilson" explicitly placed in Wilson County ([MTCPR](sources/2026-07-19_puct_56006-351_cachena-solar-bundled-tx.pdf))
  - Ch.312 resolve (2026-07-21): 2 Wilson County candidates, both unrelated ("City of La Vernia Crossing Reinvestment Zone") — no boundary map available from abatement registries
  - Ch.313/JETI resolve (2026-07-21): NEGATIVE — no agreement/application for this project (program expired 2022)
- Not obtainable: exact parcel APNs / CAD boundary (no Ch.312/313/JETI record); imagery-confirmed array perimeter (see construction)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Clear Fork Creek Solar LLC (Delaware) | SPV / IA signatory | [IA Amend 1-3](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf) |
| Enbridge Inc. (TSX/NYSE: ENB) | Developer / owner | [FID PR](sources/2026-07-19_enbridge_pr_clear-fork-solar-fid.html) |
| Jeffrey Sabins | CDO, Clear Fork Creek Solar LLC | [IA signatures](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf) |
| Meta Platforms, Inc. | Offtaker (100% long-term PPA) | [FID PR](sources/2026-07-19_enbridge_pr_clear-fork-solar-fid.html) |
| CPS Energy | TSP (CPS service territory, San Antonio) | [IA](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf) |

- Financing: FID July 22, 2025; US$900M estimated capital cost; Enbridge balance-sheet funded under low-risk commercial model ([FID PR](sources/2026-07-19_enbridge_pr_clear-fork-solar-fid.html))

## 4. Land & county records

- Tenure: **privately owned / leased** — "4,600 acres of privately owned land" ([FAQ](sources/2026-07-19_enbridge_clear-fork-solar-faq.html))
- Abatements: Wilson County Commissioners approved 10-year tax abatement **July 14, 2025** (county-level; Ch.312 likely) — no Ch.313/JETI hit (ch313.py negative; expected for post-2022 project)
- CAD: Wilson County Appraisal District not queried successfully (search backends offline 2026-07-20)

## 5. Interconnection & contractual schedule

- POI per signed IA: "approximately 18.5 miles (East) from the existing CPS Energy station (Elm Creek) on the CPS Energy owned 345 kV Elm Creek to STP transmission circuit 2" ([IA Amend 1-3](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf))
- Equipment (Amendment 2+): Three (3) 345/34.5 kV transformers × 204 PV inverter arrays × 2.933 MW = 600 MW gross
- Queue name "Cachena Solar SLF" ≠ IA name "Clear Fork Creek Solar LLC" — same project confirmed by Wilson County + MW + CPS as TSP

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf)) | 2021-11-23 | $7,414,000 (D&P) + $5,692,000 (construction) = **$13,106,000** LC |
| Amendment 1 ([pdf](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf)) | 2022-03-28 | $13,106,000 unchanged |
| Amendment 2 ([pdf](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf)) | 2022-10-14 | $13,106,000 unchanged; capacity → 600 MW |
| Amendment 3 ([pdf](sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf)) | 2023-04-10 | $13,106,000 + delay payment $40,571 (Exhibit F) |

| Milestone | Amend 1 (2022) | Amend 2 (2022) | Amend 3 (2023) | Status |
|---|---|---|---|---|
| In-Service | 2024-04-15 | 2024-10-03 | 2025-11-07 | **MISSED** |
| Trial Operation | 2024-04-22 | 2024-10-15 | 2025-11-28 | **MISSED** |
| Scheduled COD | 2024-05-31 | 2024-12-31 | 2025-12-31 | **MISSED** |

- Queue-history COD drift ([timeline.md](timeline.md)): 6 changes, 2023-06-01 → 2027-04-29 (every contractual deadline missed)
- CPS TSP switchyard (T-0313/S-0966 "Cachena"): start 2026-08-03, finish **2027-01-31**, 0% complete as of Nov 2024 ([MTCPR](sources/2026-07-19_puct_56006-351_cachena-solar-bundled-tx.pdf)) — TSP work on critical path

## 6. Satellite timeline

**2026-07-21 correction**: the previously-shown 6-date "grading_active" timeline (2024-06
through 2026-06, ~6 rectangular blocks by 2026-06-29) was observed at 29.456,-97.750 —
Hoke Solar's (23INR0231) footprint, not this project's. Those frames have been deleted.
Fresh imagery fetched at the corrected site (29.2579,-97.8057), 3km buffer:

| Date (acquired) | Cloud | Observation | Frame |
|---|---|---|---|
| 2024-06-09 | 19.2% (partial) | Agricultural/ranch land, no clearing (visible portions) | [frame](imagery/key/s2_2024-06-09.png) |
| 2025-06-17 | 0.5% | Agricultural land, center-pivot irrigation, pre-existing tank/utility yard on US-87 | [frame](imagery/key/s2_2025-06-17.png) |
| 2025-11-26 | 5.2% | Same — no clearing | [frame](imagery/key/s2_2025-11-26.png) |
| 2026-05-03 | 0.1% | Same — no clearing | [frame](imagery/key/s2_2026-05-03.png) |
| 2026-07-09 (latest) | 4.3% | Same — no clearing; tank/utility yard unchanged since 2024 (pre-existing, not new construction) | [frame](imagery/key/s2_2026-07-09.png) |

A wider ~24km x 24km sweep around the address point found no large-scale (thousands-of-
acres) clearing anywhere nearby — the only sizeable disturbed-earth feature is an
irregular ~1km quarry-like blob, wrong shape/scale for this project.

- Verdict: **not visually confirmed** — TCEQ stormwater NOIs (main array + substation)
  are ACTIVE since Jan/Aug 2025 naming EPC Hanwha Q Cells (a real, checkable permit
  fact), but that is a permit-issued fact, not proof of Sentinel-2-visible earthwork.
  EIA-860M status "under construction, ≤50%" is a coarse, self-reported category and
  does not independently resolve this.

## 7. COD assessment

- Enbridge guided "summer of 2027" at FID (July 2025): this is the developer's own public forward-looking statement, post-FID ([FID PR](sources/2026-07-19_enbridge_pr_clear-fork-solar-fid.html))
- EIA-860M independently reports planned 2027-03 ([factsheet](factsheet.json)) — consistent
- TSP switchyard (CPS T-0313) is on the interconnection critical path: CPS's own schedule has it finishing Jan 31, 2027 at best, starting Aug 3, 2026 ([MTCPR](sources/2026-07-19_puct_56006-351_cachena-solar-bundled-tx.pdf))
- Queue COD 2027-04-29 is within range but TSP finish Jan 2027 + commissioning (typically 2-3 months) → earliest realistic COD ~Q2-Q3 2027
- 6 prior slips; Amendment 3 COD Dec 2025 missed by >6 months before construction started
- Independent estimate: **2027-Q3** (Enbridge "summer 2027" language; TSP critical path suggests Q2 tight, Q3 more likely)
- Drift risk: **med-high** (raised from "medium" 2026-07-21) — $900M committed capital, blue-chip PPA (Meta), Enbridge financial strength, and active EPC-named stormwater permits are all real positives, but the visual construction-progress cross-check that would normally corroborate an on-track build is currently unavailable (see satellite timeline) — TSP schedule-slip risk and historical pattern (6 prior slips) also weigh in

## 8. Could not determine

- Exact parcel APNs / Wilson County CAD parcel boundaries (no Ch.312/313/JETI record; CAD portals JS-gated)
- Whether Sentinel-2-visible earthwork exists somewhere outside the ~12km search radius around the address anchor (open question, not resolved this pass)
- EPC contractor's full scope (Hanwha Q Cells EPC USA LLC named on stormwater NOIs only)
- Whether Amendment 4 to IA exists post-April 2023 (PUCT search returned only 35077-1594; one additional recent filing not found)
- Enbridge project page map coordinates (promotional map only, no lat/lon precision)
