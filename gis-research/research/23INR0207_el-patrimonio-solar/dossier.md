# Dossier — El Patrimonio Solar (23INR0207)

Researched 2026-07-20 · site 29.2405, -98.51006 (unverified candidate) · verdict **real_active**

## 1. Verdict

- **real_active** — groundbreaking held, $200M debt financing closed, EPC/offtaker named and quoted by name in CPS Energy's own press release ([CPS Energy PR](sources/2026-07-20_cpsenergy_el-patrimonio-groundbreaking.html))
- Construction: **claimed active (unverified visually)** — developer states construction began 2025 ([Ashtrom project page](sources/2026-07-20_ashtrom_el-patrimonio-project-page.html), [Construction Review](sources/2026-07-20_constructionreview_200m-financing.html)); no satellite confirmation obtained this run
- Site: 29.2405, -98.51006 — EIA-860M candidate coordinate, **no independent derivation method**, low confidence ([EIA-860M via eia_history.py](eia_history.json))
- COD: reported 2027-04-29 → independent **2027-Q2**, drift risk **low** (signed IA + developer's own "2H2027" language bracket this)

## 2. Site identification

- Derivation: none obtained. IA Exhibits C/C1 are text + one-line diagrams, not a boundary map — no `site.map_artifacts` exist in this docket ([Exhibit C1](sources/unverified_2026-07-20_puct_35077-1734_interconnection-agreem_p35.png) is a schematic POI diagram, not a site plat)
- **Stated project area: 867 acres** per Ashtrom's own project page ([artifact](sources/2026-07-20_ashtrom_el-patrimonio-project-page.html)), corroborated verbatim by Construction Review's fact sheet — imagery footprint consistent? **unverified** (no imagery obtained)
- Cross-checks: EIA-860M plant coordinate (29.2405, -98.51006) is ~12.7 mi S / bearing 184° from downtown San Antonio — consistent with news description "southwest of San Antonio" ([Construction Review](sources/2026-07-20_constructionreview_200m-financing.html)), but this is a single unconfirmed source, not an independent cross-check
- Not obtainable this run: exact parcel/address (BCAD owner-name search needs an interactive query beyond `search.py`'s reach); Google Places pin (`gmaps.py` HTTP 429 on 2 attempts — API-side quota, not a project signal); satellite imagery (CDSE HTTP 402 "insufficient credits," account-wide, confirmed via direct API test — not a code bug); Trumbo substation's own coordinates (no OSM/OpenInfraMap hit found; Overpass API blocked at container egress)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Heritage Solar, LLC | SPV / IA signatory | Named party + "El Patrimonio Solar" in Exhibit C of all 3 IAs ([original IA](sources/confirmed_2026-07-20_puct_35077-1734_interconnection-agreement-by-and-between-heritag.pdf)) |
| Ashtrom Renewable Energy | developer/owner | [CPS Energy PR](sources/2026-07-20_cpsenergy_el-patrimonio-groundbreaking.html); [own project page](sources/2026-07-20_ashtrom_el-patrimonio-project-page.html) lists project under "Activity in USA" |
| Ashtrom Group (TASE: ASHG) | ultimate parent | [Construction Review fact sheet](sources/2026-07-20_constructionreview_200m-financing.html) |
| OnPeak Power | original developer (sold 2021) | [Construction Review fact sheet](sources/2026-07-20_constructionreview_200m-financing.html) |
| SOLV Energy (Nasdaq: MWH) | EPC | CEO George Hershman quoted in [CPS Energy PR](sources/2026-07-20_cpsenergy_el-patrimonio-groundbreaking.html) |
| CPS Energy | offtaker (20-yr PPA, ~70% of output) + interconnecting utility | [CPS Energy PR](sources/2026-07-20_cpsenergy_el-patrimonio-groundbreaking.html); counterparty on all 3 IAs |
| BHI (Bank Hapoalim US) | lender, $200M debt facility | [Construction Review](sources/2026-07-20_constructionreview_200m-financing.html) |

- Financing: $200M bank debt facility with BHI closed **March 2026**, plus a separate 10-year Production Tax Credit monetization deal with an unnamed major US institution (Aa3/Moody's) ([Ashtrom project page](sources/2026-07-20_ashtrom_el-patrimonio-project-page.html))

## 4. Land & county records

- Tenure: **unknown** — no CAD owner-name parcel search completed (Bexar CAD requires an interactive query; `search.py` surfaced only the portal homepage, [bcad.org](sources/) not fetched)
- Abatements/agreements: **none found** — Ch.313/JETI registry hit list empty per triage/factsheet; expected, since Ch.313 expired in 2022 and this is a post-2023 IA
- CAD: not queried this run (out of scope without interactive portal access)

## 5. Interconnection & contractual schedule

- POI per signed IA (identical text, all 3 documents): "approximately 2.60 miles North from the existing CPS Energy substation (Trumbo)" ([original IA](sources/confirmed_2026-07-20_puct_35077-1734_interconnection-agreement-by-and-between-heritag.pdf)) — matches queue POI "138kV 5429 Trumbo - 5260 Leon Creek" exactly
- Equipment: original/Amendment 1 = 37× Sungrow SG4400UD-MV inverters @ 4.4 MVA (150.0 MW gross); Second Amendment reconfigured to 38× Sungrow SG4400UD-MV @ 4.158 MW (150 MW gross, same nameplate) ([2nd Amendment Exhibit C](sources/unverified_2026-07-20_puct_35077-2511_second-amendment-to-ge_p4.png))

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/confirmed_2026-07-20_puct_35077-1734_interconnection-agreement-by-and-between-heritag.pdf)) | 2023-12-11 | $4.36M → $13.04M → $16.28M cumulative (tiered by NTP stage) |
| First Amendment ([pdf](sources/confirmed_2026-07-20_puct_35077-2083_first-amendment-to-generation-interconnection-ag.pdf)) | 2025-03-05 | Same tiered amounts, effective dates pushed later (final tier eff. 2026-05-01) |
| Second Amendment ([pdf](sources/confirmed_2026-07-20_puct_35077-2511_second-amendment-to-generation-interconnection-a.pdf)) | 2026-06-10/22 | Unchanged — Exhibit C (equipment) only |

| Milestone | Original IA 2023 | Amendment 1 2025 |
|---|---|---|
| In-Service | 2026-05-01 | 2026-12-04 |
| Trial Operation | 2026-05-26 | 2026-12-29 |
| Scheduled COD | 2026-08-09 | **2027-03-30** |

- Queue-history COD drift (from [timeline.md](timeline.md)): **3 changes** — 2024-05-18 → 2024-08-30 → 2026-09-23 → 2027-04-29 (current); in reports since 2021-11-01 (56 snapshots)
- EIA-860M second source ([eia_history.json](eia_history.json)): planned COD **2027-07**, status "(L) Regulatory approvals pending. Not under construction" through 2026-05-01 reports — lags the developer's own construction-start claim (known EIA reporting-lag pattern)

## 6. Satellite timeline

- **Not obtained.** CDSE returned HTTP 402 "insufficient credits" on every imagery request this run (confirmed via direct API call to the openEO `/result` endpoint — token auth and metadata GETs succeed, only the paid processing call is blocked). This is an account-wide credit exhaustion, not specific to this project. No dated frames exist in `imagery/`.
- Construction stage is therefore asserted from documentary sources only (§1, §3) — not visually verified.

## 7. COD assessment

- Latest signed contractual COD (First Amendment, filed 2025-03-11) = **2027-03-30**; the Second Amendment (2026-06-22) touched only equipment specs (Exhibit C), leaving the schedule (Exhibit B) unchanged
- Queue's current claim (2027-04-29) sits ~1 month after the signed contractual date — internally consistent, not a red flag
- Developer's own public materials independently say "second half of 2027" (Construction Review fact sheet) / "Operational facility 2027" (Ashtrom's own page) — slightly later than the IA date but same year and window
- One prior slip occurred pre-construction (original IA COD 2026-08-09 → Amendment 1 COD 2027-03-30, ~7 months) but that is already reflected in the current queue claim, not a new risk
- For: $200M debt financing closed, PTC monetization deal signed, EPC (SOLV Energy) and offtaker (CPS Energy, 20-yr PPA) named and quoted by name, groundbreaking ceremony held, no schedule change in the 14+ months since the First Amendment
- **Independent estimate: 2027-Q2, drift risk low**

## 8. Could not determine

- Exact site coordinates/parcel — no IA boundary map exists in this docket (CPS Energy's IA carries only a POI one-line diagram, no site plat); Bexar CAD owner-name search not completed; Google Places blocked by HTTP 429 (both triage and deep attempts)
- Any visual construction confirmation — CDSE satellite imagery blocked account-wide (HTTP 402, insufficient credits)
- Land tenure (leased vs. purchased) — no CAD or abatement documents available to establish this
- Exact relationship (if any) between IA signatory "Oren Nussbaum" and Ashtrom Group Chairperson Rami Nussbaum (same surname, not confirmed as related)
- Trumbo substation's own coordinates (no OSM/OpenInfraMap listing found; Overpass API blocked at this container's egress)
