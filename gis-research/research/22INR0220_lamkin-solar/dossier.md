# Dossier — Lamkin Solar (22INR0220)

Researched 2026-07-20 · site 31.80352, -98.28654 · verdict **real_early**

## 1. Verdict

- **real_early** — signed 2025 GIA names the exact project, POI, and a Scheduled Commercial Operation Date identical to the queue's claim ([GIA](sources/2026-07-20_puct_35077-2140_standard-generation-interconnection-agreement-be.pdf))
- Construction: **unknown (imagery blocked)** — no satellite/map evidence obtainable this run; queue itself reports no construction-start milestone yet
- Site: 31.80352, -98.28654 — GIA's own engineering vicinity map states these coordinates for the "Proposed POI", high confidence ([vicinity map](sources/2026-07-20_puct_35077-2140_standard-generation-interconnecti_p36.png), [satellite view](https://www.google.com/maps/@31.80352,-98.28654,5000m/data=!3m1!1e3))
- COD: reported 2027-08-08 → independent **2027-Q3**, drift risk **medium** (contractually fixed, but NTP/build start unverified)

## 2. Site identification

- Derivation: GIA Exhibit C/vicinity map prints exact DMS coordinates (31°48'12.68"N, 98°17'11.53"W) for the "Proposed Lamkin Switching Station" / POI ([one-line diagram](sources/2026-07-20_puct_35077-2140_standard-generation-interconnecti_p35.png), [vicinity map](sources/2026-07-20_puct_35077-2140_standard-generation-interconnecti_p36.png))
- **Stated project area: 1,026.88 acres** per Ch.313 App #1785 Tab 9/16 land description ([app PDF](sources/2026-07-20_comptroller_ch313-1785-app.pdf)) — imagery footprint consistent? unverified (no imagery obtainable)
- Cross-checks: Ch.313 Figure 1 "ISD Overview" map places the project boundary just SW of Lamkin, TX inside Hamilton ISD ([map](sources/2026-07-20_comptroller_ch313-1785-app_p24.png)) — visually consistent with the GIA vicinity map's pin; POI text "~1 mile from Lamkin, Texas" on FM 260 agrees
- Not obtainable: satellite/imagery confirmation (CDSE 402 credit exhaustion; Google Places 429; Google Static Maps 403 — all account-level, see log.md)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Comanche Solar, LLC | SPV | party on [GIA](sources/2026-07-20_puct_35077-2140_standard-generation-interconnection-agreement-be.pdf) + [Ch313 app](sources/2026-07-20_comptroller_ch313-1785-app.pdf) (Texas Taxpayer ID #32070105377) |
| CORE Solar (CORE Solar LLC, Austin TX) | developer | [job-waiver letter](sources/2026-07-20_comptroller_ch313-1785-app.pdf) on CORE Solar letterhead, signed Greg Nelson (President); [2021 county-hearing coverage](sources/2026-07-20_thecomanchechief_no-motion-comanche-solar-reinvestment-zone.html) names CORE Solar reps Randy Jenkins & Julius Horvath |
| Brazos Electric Power Cooperative | TSP / interconnecting utility | counterparty on [GIA](sources/2026-07-20_puct_35077-2140_standard-generation-interconnection-agreement-be.pdf) |
| JKS Cattle & Land, LLC | landowner (lessor) | 5 parcels, [Ch313 Tab 9/16](sources/2026-07-20_comptroller_ch313-1785-app.pdf); 2 independently confirmed on [Comanche CAD](sources/2026-07-20_comanchecad_parcel-11186-jks-cattle-land.html) |

- Financing: no financing/PPA announcement found; project stage is pre-construction with only interconnection + tax-abatement paper trail

## 4. Land & county records

- Tenure: **leased** — all 5 parcels (1,026.88 ac total) owned by JKS Cattle & Land, LLC, not Comanche Solar LLC ([Ch313 app](sources/2026-07-20_comptroller_ch313-1785-app.pdf)); 2 of 5 independently cross-checked on Comanche CAD ([parcel 11186](sources/2026-07-20_comanchecad_parcel-11186-jks-cattle-land.html), [parcel 11134](sources/2026-07-20_comanchecad_parcel-11134-jks-cattle-land.html)), both Owner ID 58262, mailing 115 Ada Ct, Granbury TX
- Ch.313 App #1785 with Hamilton ISD: applied 2022-05-09, agreement executed 2023-01-12, Hamilton ISD Board Findings dated 2022-11-28 ([agmt](sources/2026-07-20_comptroller_ch313-1785-agmt.pdf)); ~100 MWac, ~254,700 panels, ~28 inverters per Tab 7/8 ([amend1](sources/2026-07-20_comptroller_ch313-1785-appamend1.pdf))
- Comanche County itself declined (no motion made) to create a Ch.312 reinvestment zone in a 2021-07-19 public hearing — county-level abatement did not happen, but this did not block the project; the separate ISD-level Ch.313 abatement proceeded independently ([news](sources/2026-07-20_thecomanchechief_no-motion-comanche-solar-reinvestment-zone.html))
- CAD: 2/5 parcels independently confirmed under "JKS Cattle & Land, LLC" — consistent, no discrepancies found

## 5. Interconnection & contractual schedule

- POI per signed GIA: "Point of Interconnection...located in Comanche County, Texas, at Brazos Electric's 69 kV Switching Station...on FM 260, approximately 1 mile from Lamkin, Texas" ([GIA Exhibit C](sources/2026-07-20_puct_35077-2140_standard-generation-interconnection-agreement-be.pdf))
- Equipment (Exhibit C): 101.5 MW nominal total plant, 28 inverters at 3.625 MW each

| IA document | Signed | Financial security posted |
|---|---|---|
| Original GIA ([pdf](sources/2026-07-20_puct_35077-2140_standard-generation-interconnection-agreement-be.pdf)) | March 2025 (filed 2025-05-19) | $9.5M irrevocable standby letter of credit, effective within 2 business days of execution |

| Milestone | Original GIA 2025 |
|---|---|
| In-Service | Later of 1100 days from NTP-with-security, or 03/31/2027 |
| Trial Operation | To be determined |
| Scheduled COD | 08/08/2027 |

- Queue-history COD drift (from [timeline.md](timeline.md)): 3 historical changes (2022→2023→2025→2027), but **0 changes since the GIA was signed** — COD has held at 2027-08-08 for 17 straight monthly snapshots (2025-02 → 2026-06)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | No imagery obtained | — |

- Verdict: **unknown (imagery blocked)** — CDSE openEO returned HTTP 402 (account credits exhausted); Google Places returned HTTP 429; Google Static Maps returned HTTP 403 (API not enabled). All three are account/environment-level failures, not evidence about the site itself.

## 7. COD assessment

- Reported 2027-08-08 is the exact **Scheduled Commercial Operation Date** in the countersigned GIA (PUCT 35077-2140) — this is the strongest possible grounding: a primary contractual document, not a queue self-report
- The date has been stable in the ERCOT queue for 17 consecutive monthly snapshots since the GIA was signed, with zero drift post-signing
- Risk: the In-Service Date is pegged to "1100 days from Generator's notice to proceed with construction," not a fixed calendar date — if NTP is delayed, In-Service (and by extension COD) could slip; Trial Operation date is explicitly "to be determined" even in the signed agreement
- No construction-start milestone yet reported in the ERCOT queue (as of 2026-06-01, ~13 months before reported COD) and the project is not yet in EIA-860M — expected for a solar project at this stage but leaves no independently observed schedule cushion
- Could not verify actual ground conditions (imagery blocked) to confirm whether NTP/construction has already begun
- **Independent estimate: 2027-Q3, drift risk medium** — grounded in a real signed contract with matching dates, but the 1100-day NTP-contingent clause and lack of any observed construction milestone or imagery leave real schedule risk

## 8. Could not determine

- Whether construction has physically started (CDSE imagery: HTTP 402 credits exhausted; Google Places: HTTP 429; Google Static Maps: HTTP 403 — all blocked this run)
- Exact date Generator provided notice-to-proceed-with-construction (governs the 1100-day In-Service Date clause)
- Confirmed identity of the individual(s) behind "JKS Cattle & Land, LLC" (plausibly tied to James Shelton, the landowner named in 2021 county-hearing news coverage, but not independently verified via TX SOS/Comptroller entity search this run)
- Financing status / PPA offtaker (no announcements found; may simply not have been publicized yet at this pre-construction stage)
