# Dossier — Elm Flats Solar SLF (26INR0130)

Researched 2026-07-20 · site 32.1136, -96.3048 · verdict **real_early**

## 1. Verdict

- **real_early** — executed IA schedule COD (Sept 30, 2027) matches the queue claim exactly ([IA Exhibit B](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf)); 3+ years of consistent developer intent (Ch.313 filed 2022, IA executed 2025) but zero visible construction as of the latest imagery
- Construction: **no_activity** as of 2026-06-15 ([contact sheet](contact_sheet.png)); could not re-check with fresher imagery — CDSE backend down all session
- Site: 32.1136, -96.30476 — EIA-860M plant record, corroborated by Ch.313 vicinity map showing the actual project boundary polygon near Powell/Elm Flat ([map](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app_sheet07.png)), medium-high confidence ([satellite view](https://www.google.com/maps/@32.1136,-96.3048,5000m/data=!3m1!1e3))
- COD: reported 2027-09-30 → independent **2027-Q4**, drift risk **medium** (contractually grounded but tight runway, EIA/imagery status conflict unresolved)

## 2. Site identification

- Derivation: EIA-860M plant-name match (Elm Flats Solar, 32.11358,-96.30476) cross-corroborated by an independent source — the Ch.313 application's own vicinity map (Checklist Item #11), which draws the actual project-boundary polygon east of Powell / south of Kerens in the "Elm Flat" area, Navarro County ([vicinity map](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app_sheet07.png))
- **Stated project area: 1,500 acres** per Ch.313 application Tab 9 and executed Agreement Exhibit 2 ([app](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app.pdf), [agreement](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-agmt.pdf)) — imagery footprint unverified (no ground disturbance visible yet to compare against)
- Cross-checks: EIA-860M coords ↔ Ch.313 vicinity map agree (both place the project in the Elm Flat / Powell area east of Corsicana); IA POI "Wheelock Lake Switch" reconciles with queue POI text "3472 BRIAR_CRK_8 – 3467 POWELL1_8" via the IA's own one-line diagram, which shows Wheelock Lake Switch on the 138kV line to Corsicana Sub "via Briar Creek POI" and to Trinidad Sub "via Powell Sub" ([one-line diagram](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf), Attachment 1 to Exhibit C)
- Not obtainable: exact Wheelock Lake Switch / substation coordinates (redacted as CEII in the IA per Oncor's PUCT cover letter); no parcel-level CAD search performed this run

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Orca Falls Solar, LLC | SPV / IA Generator (current) | [IA](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf) signature page, signed by Peter Stein, Chief Development Officer |
| Elm Flats Solar, LLC | original SPV (2022 Ch.313 applicant) | [Ch.313 app](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app.pdf), [agreement](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-agmt.pdf) |
| Birch Creek Development (Birch Creek Energy) | developer | Chris Norqual signs Ch.313 app as "Authorized Representative, Elm Flats Solar, LLC" from norqual@birchcreekdev.com; matches EIA-860M reporting entity "Birch Creek Development" for the same plant/coords |
| Oncor Electric Delivery Company LLC | TSP | [IA](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf) signature page, signed by Jim Greer, EVP and COO |
| Ernst & Young LLP / Alluvial Power (Joe Arb) | Ch.313 consultants | cc'd on Ch.313 application cover letter |

- Financing: no financing close, PPA, or EPC announcement found (search.py + WebFetch birchcreekdev.com/about — 872MW/36-project portfolio claimed, Elm Flats not named); Birch Creek Energy independently confirmed as a real, PGIM-backed ($65-76M) solar developer via PRNewswire coverage — general corporate legitimacy, no project-specific financing confirmed

## 4. Land & county records

- Tenure: **leased** — Ch.313 Tab 9 / Agreement Exhibit 2: "The applicant will lease approximately 1,500 acres of land within Navarro County, Texas for the project" ([app](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app.pdf))
- Ch.313 value-limitation agreement executed by Kerens ISD Nov 28, 2022 ([agreement](sources/2026-07-20_comptroller_ch313_1973-kerens-elm-agmt.pdf)) — total investment "in excess of $162 million," $40M M&O appraised-value limitation 2028-29 through 2037-38, projected $1,897,253 total revenue to Kerens ISD over the agreement life (Region 12 ESC financial impact analysis)
- CAD: no parcel search performed this run (not reached before budget/tool constraints)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Point of Interconnection is located in Navarro County, Texas, at the Wheelock Lake Switch in TSP's Trinidad Switch – Corsicana Sub 138 kV Transmission Line" ([IA](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf), Exhibit C item 2)
- Equipment (Exhibit C item 4): 35× Sungrow SG4400UD-MV-US solar inverters, 146.3 MVA nameplate, dispatched 125.58 MW at 34.5kV bus / 127.155 MW at generator terminals; co-located 26INR0131 Elm Flats Storage SLF (47× SMA SCS3450UP-US BESS inverters, 128.06/129.015 MW)

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard Generation Interconnection Agreement ([pdf](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf)) | 2025-11-21 | $4,017,301 (E&P DSA, eff. 2025-08-20) → $8,115,760 (eff. on/before 2025-11-21) |

| Milestone | Original IA 2025 |
|---|---|
| In-Service Date | 2027-05-13 |
| Trial Operation | 2027-05-30 |
| Scheduled COD | 2027-09-30 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** before IA execution — 2026-01-31 → 2026-07-01 → 2026-12-01 → 2027-09-30 (current, held since 2025-08, stable through every snapshot since IA signing)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-15 | undisturbed cropland/pasture, wooded creek corridors, no grading/racking/substation pad visible | [contact sheet](contact_sheet.png) |

- Verdict: **no_activity** — could not obtain fresher imagery this session; CDSE openEO backend was unreachable for the entire deep-scan run (7 retries across ~2 hours, `RemoteDisconnected`, valid cached auth token so not a credentials issue)

## 7. COD assessment

- Reported 2027-09-30 is the exact **Scheduled Commercial Operation Date** in the countersigned [IA](sources/2026-07-19_puct_35077-2325_standard-generation-interconnection-agreement-be.pdf) — contractually grounded, not a bare queue self-report
- Prior COD instability (3 slips, ~20 months cumulative) all predates IA execution; the schedule has held steady since signing — a meaningfully different reliability signal than an unsigned project
- Financial security is real and escalating on-schedule ($4.0M → $8.1M in 2025) — inconsistent with a pure paper/optionality project
- Ch.313 tax agreement (2022) shows 3+ years of continuous developer commitment (Birch Creek Development/Elm Flats Solar LLC → Orca Falls Solar LLC) converging with the 2025 IA — same underlying project, not two unrelated filings
- Risk: EIA-860M flipped to "(U) Under construction, ≤50% complete" starting 2025-12-01, but our only available imagery (2026-06-15) shows no visible activity — an unresolved divergence that could mean either an overly loose EIA self-report or activity we simply couldn't see with the imagery on hand
- Only ~11 months of pre-construction runway remain to the contractual In-Service Date (2027-05-13) with zero confirmed grading, which is tight for a ~126 MW single-axis-tracker array even though typical builds run 12-18 months
- **Independent estimate: 2027-Q4, drift risk medium**

## 8. Could not determine

- Fresh satellite imagery past 2026-06-15 (CDSE backend down entire session — 7 failed retries)
- Whether EIA's "(U) Under construction" status (since 2025-12) reflects genuine physical construction or an administrative/financial-security-triggered self-report
- Exact Wheelock Lake Switch coordinates (CEII-redacted in the IA)
- CAD parcel-level ownership/situs (not reached this run)
- Financing close, EPC contractor, or PPA offtaker (no press or filing found)
- Delivery-pin corroboration (gmaps.py 429-rate-limited both in triage and this run)
