# Dossier — Spindletop Solar (27INR0313)

Researched 2026-07-19 · site 31.595, -94.772 · verdict **real_active**

## 1. Verdict

- **real_active** — Sentinel-2 July 2026 shows massive active clearing/grading (~2,560 acres) centered near Alazan/Lake Nacogdoches, matching Parliament Energy's own stated "4 square miles" footprint ([xwide key frame](imagery/key/s2_site_xwide_2026-07-01.png)); developer's website confirms "construction phase" ([parliament energy](sources/2026-07-19_parliamentenergy_banita-creek.html))
- Construction: **clearing/grading** (pre-racking), first activity date not yet bracketed (only one date imaged)
- Site: 31.595, -94.772 — imagery feature centroid + geographic anchors (Alazan hamlet, Lake Nacogdoches), medium confidence (±0.5 km) ([satellite view](https://www.google.com/maps/@31.595,-94.772,5000m/data=!3m1!1e3))
- COD: reported 2027-12-29 → independent **2027-Q4**, drift risk **medium** (active construction, FIS re-opened, 4× prior drifts)

## 2. Site identification

- Derivation: Parliament Energy website states "4 square miles" in Nacogdoches County; original developer Solar Proponent "leased ~7,200 acres near Alazan and Lake Nacogdoches" in 2023 (log.md D19); Sentinel-2 chip 31.595, -94.772 shows clearing/grading activity filling the 2 km frame with parcel-following boundaries ([site chip](imagery/s2_site_31.595_-94.772_2026-07-01.png))
- **Stated project area: ~2,560 acres (4 sq miles)** per Parliament Energy website ([html](sources/2026-07-19_parliamentenergy_banita-creek.html)); land lease ~7,200 acres total envelope — imagery footprint consistent: clearing spans ~3-4 km E-W in the xwide frame
- Cross-checks: Alazan hamlet (31.583°N, 94.786°W, OSM) + Lake Nacogdoches (upper-left in [xwide frame](imagery/key/s2_site_xwide_2026-07-01.png)) + clearing footprint center; agree within ~1.5 km; no Places pin obtained (rate-limited during triage)
- Not obtainable: exact Oncor POI switch coordinates (Stryker [3109] tap point); IA not retrieved from PUCT (portal 402-blocked); CAD parcels not accessible

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Banita Creek Solar LLC | SPV | ERCOT parquet `interconnectingFacility` field (log.md D10) |
| Parliament Energy | developer/owner | [parliamentenergy.com/banita-creek](sources/2026-07-19_parliamentenergy_banita-creek.html) |
| EnCap Investments LP + Mercuria Energy | co-founding backers | [parliamentenergy.com](sources/2026-07-19_parliamentenergy_banita-creek.html) FAQ section |
| Solar Proponent | original developer (sold to Parliament ~late 2025) | log.md D19 (Daily Sentinel via DDG) |

- Financing: Parliament Energy closed USD 747M non-recourse project financing for its Tehuacana Creek Solar project via Credit Agricole CIB (log.md D24, LinkedIn/CA CIB); Banita Creek is part of the "2.7 GWdc contracted portfolio" — no deal-specific financing announcement found yet for Banita Creek itself; financial security posted in ERCOT system (ERCOT parquet: `financialSecurityAndNoticeToProceedProvided = "Yes"`)

## 4. Land & county records

- Tenure: **leased** — Solar Proponent secured ~7,200-acre lease near Alazan and Lake Nacogdoches in 2023 (log.md D19); Parliament Energy acquired from Solar Proponent ~late 2025
- Abatements/agreements: post-2022 project → Ch.313 expired (ineligible); JETI registry not accessible online; no abatement found (expected)
- CAD: Nacogdoches CAD portal returned 401/DNS failure — no parcel search completed; parcels likely held under landowner names, not LLC (consistent with leased land)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Tap Stryker [3109] - Lufkin [3117] 345 kV line", Nacogdoches County (queue data); TSP = Oncor (parliament website FAQ); Stryker [3109] = Stryker Creek Power Plant area ~31.94°N, 94.99°W Cherokee County; Lufkin [3117] = Lufkin, Angelina County
- Note: PUCT portal (interchange.puc.texas.gov) returned HTTP 402 throughout this research — IA document not retrieved directly; signed date 2025-12-29 from ERCOT queue data
- Equipment: not obtainable (IA not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PUCT docket, unfetched) | 2025-12-29 | "Yes" per ERCOT parquet (amount unknown) |

| Milestone | IA 2025 (reported) | Amendment |
|---|---|---|
| In-Service | unknown | — |
| Trial Operation | unknown | — |
| Scheduled COD | 2027-12-29 (queue data) | — |

- FIS status anomaly: queue data shows "SS Completed, FIS Completed, IA" in 2025-12 through 2026-04, then reverted to "SS Completed, FIS Started, IA" in 2026-05 and 2026-06 — FIS re-opened or under revision; this is a risk factor ([timeline.md](timeline.md))
- Queue-history COD drift: **4 changes** — 2027-04-01 → 2027-06-30 → 2027-08-28 → 2027-06-30 → 2027-12-29; +9 months total from first reported COD ([timeline.md](timeline.md))

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Active clearing/grading, multiple cleared polygons with access roads, site fills 2 km chip | [site chip](imagery/s2_site_31.595_-94.772_2026-07-01.png) |
| 2026-07-01 (xwide) | Two-lobe clearing footprint ~3-4 km E-W; Lake Nacogdoches upper-left confirms geography | [xwide key](imagery/key/s2_site_xwide_2026-07-01.png) |

- Verdict: **clearing/grading** — bulk earthwork active July 2026; no uniform dark module rows visible yet (pre-racking); 10 m resolution cannot confirm equipment installation detail; first-activity date not yet bracketed (timelapse not run — only one date chip available at this location)

## 7. COD assessment

- Reported 2027-12-29 is the COD per queue; developer's website confirms "Q4 2027" expected completion ([html](sources/2026-07-19_parliamentenergy_banita-creek.html)) — both align but neither is a contractual schedule (IA not retrieved)
- Developer states "~18-month construction period" on website; site is in early clearing/grading as of July 2026; 18 months from ~mid-2026 start = Q4 2027 COD — math is internally consistent
- Risk factors: (1) FIS re-opened in the queue May/June 2026 — implies possible design change or restudied equipment; could cause IA amendment and schedule reset; (2) 4× prior COD drifts totaling +9 months; (3) no racking visible July 2026, so module/electrical phase not yet started
- For: financial security posted, construction active on the ground, credible developer (Parliament Energy operates flagship Parliament Solar ~640 MWdc, completed early 2025), major PE backers (EnCap + Mercuria), "4 sq mi" footprint matching imagery
- **Independent estimate: 2027-Q4, drift risk medium** — COD target is supported by observed pace and developer's own public statement; FIS re-opening is the primary risk that could push to 2028-Q1 or Q2

## 8. Could not determine

- Contractual In-Service / Trial Operation dates (IA not retrieved; PUCT portal blocked)
- Financial security amount (IA not retrieved)
- Exact site centroid to sub-km precision (no CAD parcels, no Places pin)
- First-activity date / construction start bracket (only one imagery date pulled; timelapse not run)
- PPA offtaker identity
- EPC contractor identity
- Exact Stryker [3109] tap-point coordinates (CEII likely; Stryker Creek area approx only)
