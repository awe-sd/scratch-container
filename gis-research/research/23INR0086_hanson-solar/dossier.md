# Dossier — Hanson Solar (23INR0086)

Researched 2026-07-17 · site 31.6950, -99.5315 · verdict **real_active**

## 1. Verdict

- **real_active** — ~3,000-ac graded polygon in imagery pixel-matches the project's own [Ch313 Improvements Map](sources/hanson_map_p23.png); financing closed, EPC mobilized ([PR Newswire 2025-11-19](sources/2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html))
- Construction: **racking** (transitioning), first activity **2025-04** ([substation pad frame](imagery/s2_2025-04-01.png))
- Site: 31.6950, -99.5315 — imagery shape-match, high confidence ([satellite view](https://www.google.com/maps/@31.6950,-99.5315,5000m/data=!3m1!1e3))
- COD: reported 2027-04-17 → independent **2027-Q2**, drift risk **medium** (final stage unverified; one prior 18-mo slip)

## 2. Site identification

- Derivation: wide S2 chip ([xwide frame](imagery/s2_2026-07-10_xwide.png)) shows an L-shaped, notched graded polygon matching the boundary on CCR's own [Improvements Map](sources/hanson_map_p23.png), incl. the substation notch
- Cross-checks agree within ~3.5 km: Google Places pin "TIC Hanson solar", 6725 FM503 Valera TX (31.6925, -99.5483); IA POI text "Fisk Switch ~12 mi SW of Coleman, west of CR 362" ([IA](sources/2026-07-17_puct_35077-1682_oncor-hanson-solar-IA.pdf)); OSM "Fisk" node (31.6710, -99.4892); [Ch313 vicinity map](sources/hanson_map_p22.png)
- Not obtainable: exact Fisk Switch coordinates (Exhibit C redacted as CEII in PUCT filing)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Hanson Solar, LLC | SPV | party on [IA](sources/2026-07-17_puct_35077-1682_oncor-hanson-solar-IA.pdf) + [Ch313 app](sources/2026-07-17_comptroller_ch313_1698-hanson-app-main.pdf) |
| Cypress Creek Renewables | developer/owner/operator | [financing PR](sources/2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html); their name on [Improvements Map](sources/hanson_map_p23.png) |
| TIC (Kiewit) | EPC | Places pin named "TIC Hanson solar"; [PR](sources/2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html) |
| Meta | PPA offtaker | [pv-magazine 2025-03](sources/2026-07-17_pvmagazine_meta-signs-more-texas-solar.html), [PR](sources/2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html) |

- Financing: non-recourse project financing closed **Nov 2025** naming lenders + EPC ([PR](sources/2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html), [CCR official](sources/2026-07-17_cypresscreekenergy_hanson-solar-financing-official.html))

## 4. Land & county records

- Tenure: **leased** — "Leased land border" labeled on [Improvements Map](sources/hanson_map_p23.png); Ch313 Tab 9 "Description of Land" = "Not Applicable" ([app](sources/2026-07-17_comptroller_ch313_1698-hanson-app-main.pdf))
- Ch313 agreement with Panther Creek CISD executed Nov 2022, 3 yrs of Form 772 compliance reports ([agreement](sources/2026-07-17_comptroller_ch313_hanson-solar-panther-creek-cisd.pdf))
- CAD: 0 parcels under Hanson Solar / Hanson / Cypress Creek (4 owner-name searches) — expected for leased ranchland; landowner names unidentified

## 5. Interconnection & contractual schedule

- POI per signed IA: "Fisk Switch within TSP's Brown Switch – Central Bluff Switch 345 kV line", Coleman County ([IA 2023-09-20](sources/2026-07-17_puct_35077-1682_oncor-hanson-solar-IA.pdf)) — matches queue POI exactly
- Equipment (Exhibit C): 104× SMA SC4400UP-US (457.6 MVA, 396 MW solar) + co-located BESS 79× Tesla Megapack (101.4 MW, companion INR 24INR0057 "Hanson Storage")

| Milestone | Original IA 2023 | Amendment 1 (2024) |
|---|---|---|
| In-Service | 2025-05-08 | **2026-12-03** |
| Trial Operation | 2025-05-20 | **2026-12-17** |
| Scheduled COD | 2025-10-21 | **2027-04-17** |

([Amendment 1](sources/2026-07-17_puct_35077-1899_oncor-hanson-solar-IA-amend1.pdf), PUCT Control No. 35077)
- Security: LCs with Oncor $11.3M (Nov 2023) → $13.4M (Dec 2025) ([Amend 1](sources/2026-07-17_puct_35077-1899_oncor-hanson-solar-IA-amend1.pdf))
- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2024-05 → 2025-10 → 2027-01 → 2027-04; in reports since 2021-03 (64 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| ≤2025-03 | undisturbed farmland, full footprint | [2025-03](imagery/key/s2_2025-03-01.png) |
| 2025-04 | substation pad appears at mapped location (tight bracket vs 03-01) | [2025-04](imagery/key/s2_2025-04-15.png) |
| 2025-06 | grading over ~⅔ of polygon | [2025-06](imagery/s2_2025-06-01.png) |
| 2025-09 | grading essentially full footprint | [2025-09](imagery/key/s2_2025-09-01.png) |
| 2026-03+ | road grid sharp; darker uniform rectangles = candidate racking | [2026-03](imagery/s2_2026-03-01.png) |
| 2026-07 | stable graded footprint, small pads visible; no full panel-field signature yet | [2026-07](imagery/key/s2_2026-07-10.png) |

- Verdict: **racking** — bulk earthwork done ~2025-09, equipment-stage signals from 2026-03; 10 m resolution cannot confirm installed modules

## 7. COD assessment

- Reported 2027-04-17 is the **contractual** Scheduled COD in the countersigned [IA Amendment 1](sources/2026-07-17_puct_35077-1899_oncor-hanson-solar-IA-amend1.pdf) — grounded, but grounded ≠ achievable
- Observed pace tracks the amended schedule: civil works complete ~14 months before the 2026-12-03 In-Service date; site active continuously in dekad frames through 2026-07-11
- Risk: one prior slip of ~18 months (2025-10 → 2027-04) pre-construction; final electrical/panel stage not visually verified with ~5 months to In-Service
- For: financing closed, EPC on site, offtake signed, LCs increasing on schedule
- **Independent estimate: 2027-Q2, drift risk medium**

## 8. Could not determine

- Exact Fisk Switch / substation tie-point coordinates (CEII-redacted)
- Underlying ranch-owner names on leased parcels (0 CAD hits under LLC/developer, as expected)
- Definitive racking/module confirmation (Sentinel-2 10 m ceiling)
- TX SOS corporate detail for the LLC (free searches empty; SOSDirect is paid)
