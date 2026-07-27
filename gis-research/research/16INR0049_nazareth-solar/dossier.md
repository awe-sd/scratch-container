# Dossier — Nazareth Solar (16INR0049)

Researched 2026-07-20 · site 34.48840, -101.97284 · verdict **real_early**

## 1. Verdict

- **real_early** — Vesper Energy project with signed IA (2026-03-05 amendment), $236M financing closed Jan 2025, Ch.313 abatement / Tulia ISD, Google Places construction pin at 1291 Co Rd 2 Tulia TX 79088 ([EIA record](sources/eia_history.json))
- Construction: **not yet started as of May 2026** — EIA-860M status "(T) Regulatory approvals received. Not under construction" continuous 2025-06 → 2026-05 ([eia_history.json](eia_history.json))
- Site: 34.48840, -101.97284 — Google Places pin ([gmaps result](#)) + EIA plant 67575 coords 34.49,-101.97 agree within 0.002° — **Swisher County** (queue says Castro County: incorrect)
- COD: reported 2027-08-31 → independent **2028-Q2**, drift risk **med** (construction not confirmed started; 15 prior slips; ~18-month build from NTP)

## 2. Site identification

- Derivation: Google Places "Nazareth Solar" → 1291 Co Rd 2, Tulia TX 79088 (manufacturer/establishment pin); EIA-860M plant 67575 independently coordinates 34.49,-101.97 (Swisher Co)
- **Stated project area: ~2,000 acres** per [Ch.313 App #1592](sources/2026-07-20_comptroller_ch313-1592_nazareth-app.pdf) (Tulia ISD, 2021-04-26) — imagery footprint not verified (CDSE blocked this session)
- Cross-checks: Places pin (34.4884,-101.9728) ↔ EIA coords (34.49,-101.97) agree <0.5 km; IA Exhibit C: "Ozark Trail Switch in Swisher County" — all consistent
- **Queue county error**: queue lists Castro County; IA + Ch.313 + EIA all say Swisher County. Site is ~50 km east of Nazareth TX (Castro Co), near Tulia TX (Swisher Co).
- Not obtainable: exact POI switch coords (CEII-redacted in Exhibit C)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| TX Nazareth Solar Project, LLC | SPV (legal name in IA) | [IA 35077-1643](sources/2026-07-20_puct_35077-1643_interconnection-agreement-between-oncor-electric.pdf) |
| Hornet Solar LLC f/k/a TX Nazareth Solar, LLC | SPV (renamed) | [Ch.313 #1592](sources/2026-07-20_comptroller_ch313-1592_nazareth-app.pdf) |
| Vesper Energy Development LLC | Developer/parent | [Ch.313 #1592](sources/2026-07-20_comptroller_ch313-1592_nazareth-app.pdf) p.6; IA Exhibit D |
| Generate Capital | Financier (~$236M, Jan 2025) | [infrasure_project_page.md](sources/infrasure_project_page.md) |

- Financing: ~$236M tax equity/debt closed January 2025 per Infrasure.ai; Bank of America listed as Generator bank in IA Exhibit D

## 4. Land & county records

- Tenure: **leased** — Ch.313 App p.8: "long-term lease option agreements with area landowners"; land not classified as qualified property (lessee)
- Abatements: Ch.313 App #1592 / Tulia ISD ([app](sources/2026-07-20_comptroller_ch313-1592_nazareth-app.pdf)) — filed 2021-04-26; ~2,000 ac Swisher County; first limitation year 2024; entity chain TX Nazareth Solar → Hornet Solar II → Hornet Solar
- Ch.313 App #1784 / Nazareth ISD: **NOT this project** — triage incorrectly linked it; that is a separate Castro County project (Castro Solar One LLC)
- CAD: Swisher County CAD not searched (no portal access this session); 0 parcels confirmed

## 5. Interconnection & contractual schedule

- POI per signed IA: "Ozark Trail Switch in Swisher County, Texas, at the south circuit of the Ogallala Switch–Tule Canyon Switch 345 kV double circuit transmission line" ([IA](sources/2026-07-20_puct_35077-1643_interconnection-agreement-between-oncor-electric.pdf), [Amend 1](sources/2026-07-20_puct_35077-2431_amendment-no-1-to-the-standard-generation-interc.pdf))
- Equipment (Amendment 1 Exhibit C): 54 × Sungrow SG4400UD inverters, 203 MW net at POI (upgraded from 65 × SG3600UD in original IA)
- Co-tenancy: Hornet Solar II LLC (separate project, same Ozark Trail Switch — [PUCT 35077-1929](sources/2026-07-20_puct_35077-1929_interconnection-agreement-between-oncor-and-horn.pdf))

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-1643_interconnection-agreement-between-oncor-electric.pdf)) | 2023-06-06 | $4,174,433 LC (due 2023-06-12) |
| Amendment No. 1 ([pdf](sources/2026-07-20_puct_35077-2431_amendment-no-1-to-the-standard-generation-interc.pdf)) | 2026-03-05 | LC structure carried forward; new amount not stated in amendment |

| Milestone | Original IA (2023) | Amendment 1 (2026) |
|---|---|---|
| In-Service | 2024-12-17 | 2027-04-01 |
| Trial Operation | 2024-12-27 | 2027-04-11 |
| Scheduled COD | 2025-04-26 | 2027-08-31 |

- Queue-history COD drift ([timeline.md](timeline.md)): 15 changes, 2016-07-01 original → 2027-08-31 current
- Amendment 1 construction notice deadline: August 15, 2025 — presumably met (financing closed Jan 2025), but EIA reports not-under-construction through May 2026

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-01 | Cropland at **wrong location** (34.51,-102.11, Castro County) — no solar activity | [contact_sheet.png](imagery/contact_sheet.png) |
| 2026-07-20 | CDSE blocked for correct Swisher County location (rate limit) — no chips obtained | — |

- Verdict: **no imagery at correct site** — construction status from EIA only (not under construction May 2026)

## 7. COD assessment

- Amendment 1 SCOD is 2027-08-31, contractually grounded and matches queue exactly — queue is tracking the amended IA
- EIA reports not-under-construction through May 2026; in-service date of April 2027 requires construction start by ~Oct 2026 for an 18-month build
- If NTP was given mid-2026 (6-9 months after financing close), COD would land mid-2028 — 1 quarter slip from current queue date
- 15-change drift history with a mean of ~12-18 month slips at each step creates baseline med-risk
- Equipment upgrade in Amendment 1 (SG3600UD → SG4400UD) suggests active redesign as recently as Q1 2026, consistent with construction not yet started
- Queue COD has been more stable since financing closed: only moved from 2025-12→2027-08 in the March 2026 amendment; no further drift in the 4 months since
- **Independent estimate: 2028-Q2** (range 2027-Q4 if construction started and accelerated; 2028-Q4 if further delay)

## 8. Could not determine

- Swisher County CAD parcels / exact tract descriptions
- Exact project boundary / location of Ozark Trail Switch (CEII)
- Whether NTP was formally issued after the August 2025 contractual deadline
- Satellite ground truth at the Swisher County site (CDSE blocked)
- Financial security amount in Amendment 1 (redacted/not stated)
- PPA counterparty / offtaker
