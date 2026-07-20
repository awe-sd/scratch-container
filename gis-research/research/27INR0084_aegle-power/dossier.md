# Dossier — Aegle Power (27INR0084)

Researched 2026-07-18 · site 26.21636, -97.62806 · verdict **paper**

## 1. Verdict

- **paper** — TEF loan denied 2024-09-04 for failing due-diligence after CEO's 2017 embezzlement conviction surfaced and NextEra was listed as co-sponsor without consent ([PUCT release](sources/2026-07-18_puct_TEF_denial_pressrelease.pdf), [Utility Dive](sources/2026-07-18_utilitydive_puct-aegle.html))
- Construction: **no_activity** — site remains agricultural fields 13 yr after the 2013 planned construction start ([2020 chip](imagery/s2_2020-01_tight.png), [2026-07 chip](imagery/s2_2026-07_tight.png))
- Site: 26.21636, -97.62806 — 24684 FM 1595, Harlingen, from TCEQ PI-1 lat/long in the 2012 permit application, high confidence ([EPA GHG permit p.7](sources/2026-07-18_epa_lapaloma_ghg_permit_app.pdf), [map](https://www.google.com/maps/@26.2164,-97.6281,5000m/data=!3m1!1e3))
- COD: reported 2027-07-30 → independent **cancelled / no credible COD**, drift risk **N/A** (project is paper)

## 2. Site identification

- Derivation: exact lat 26°12'58.9"N lon 97°37'41.02"W and street address "24684 FM 1595, Harlingen 78550" on Form PI-1 of the [2012 TCEQ/EPA air permit application](sources/2026-07-18_epa_lapaloma_ghg_permit_app.pdf); GEM Wiki gives 26.216361, -97.62806 sourced to EIA-860M ([gem.wiki](sources/2026-07-18_gemwiki_lapaloma-energy-center.html))
- **Stated project area: not disclosed** in the 2012 permit (plot plan shows a rectangular property ~0.4 mi × 0.15 mi, but no acreage cited); [PR Newswire 2013](sources/2026-07-18_prnewswire_new-harlingen-power-plant-original-announcement.html) locates the plant in "Harlingen Industrial Park"
- Cross-checks agree: TCEQ address + EIA-860M coords + Ch313/JETI absent + PR Newswire text all place the plant at the same FM 1595 tract in Harlingen
- Not obtainable: no current TCEQ NSR permit under Aegle Power confirmed for 1,536 MW; the 2013 permit was for 637–735 MW (roughly half)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Aegle Power, LLC (TX SOS 0804910188, filed 2023-02-02, Austin) | Current SPV / queue applicant | [PUCT release](sources/2026-07-18_puct_TEF_denial_pressrelease.pdf); [t3 web sweep](sources/t3_web_sweep.md) |
| Kathleen Smith | Managing Partner/CEO of Aegle; pled guilty 2017 to embezzling from Chase Power (SDTX US Attorney) | [Utility Dive](sources/2026-07-18_utilitydive_puct-aegle.html) |
| La Paloma Energy Center, LLC (TX SOS 5108003, Plano) — Gary Neus EVP | 2012–2015 permit holder; owner Coronado Power Ventures LLC | [EPA GHG permit p.7](sources/2026-07-18_epa_lapaloma_ghg_permit_app.pdf); [GEM Wiki ownership tree](sources/2026-07-18_gemwiki_lapaloma-energy-center.html) |
| Coronado Power Ventures LLC + Bechtel (EPC: Becon Construction) | 2013 original announced developer / EPC | [PR Newswire 2013-05](sources/2026-07-18_prnewswire_new-harlingen-power-plant-original-announcement.html); [Business Facilities](sources/2026-07-18_businessfacilities_harlingen-plant.html) |
| NextEra Energy | Listed as co-sponsor by Aegle **without consent** on TEF App-162 | [PUCT release](sources/2026-07-18_puct_TEF_denial_pressrelease.pdf); [Utility Dive](sources/2026-07-18_utilitydive_puct-aegle.html) |

- Financing: **TEF loan denied 2024-09-04, denial "not subject to motions for rehearing or appeal"** ([PUCT](sources/2026-07-18_puct_TEF_denial_pressrelease.pdf)); no offtaker; no financial security posted with ERCOT (queue field "No" through latest snapshot 2026-06-01)
- Legislative fallout: 6-member advisory panel referred findings to Senate Finance; Oct-8 2024 hearing focused on Deloitte's initial vetting; PUCT sought a min. 10% reduction in the Deloitte contract for advancing the application ([Texas Electricity Ratings](sources/2026-07-18_texaselectricity_senate_investigation.html), [Power Mag](sources/2026-07-18_powermag_major_project_rejected.html))

## 4. Land & county records

- Tenure: **unknown** — no Cameron CAD parcel lookup performed under Aegle/Coronado (portal search blocked in triage); the 2012 permit lists property ownership by tract but the file's plot plan (p.15) shows a bounded rectangle of open farmland
- Abatements/agreements: **none found** for Aegle Power or La Paloma Energy Center in Cameron County (triage confirmed no Ch313/JETI — expected for a 2023-incorporated LLC and consistent with the plant never being built)
- CAD: not searched by owner name in this deep scan; Cameron CAD portal returned no results in triage

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "(#79501) Kingfisher 345 kV". Kingfisher is a NEW Sharyland substation ~20 mi ESE of the plant site, near San Benito, on Casey Rd; facilities-in-service Spring 2026 per [AEP fact sheet](sources/2026-07-18_aep_LaPalma-Kingfisher_factsheet.pdf) and [Final Order 1-18-2023](sources/2026-07-18_aep_LaPalma-Kingfisher_Final_Order.pdf). (Note: not to be confused with AEP's "La Palma" substation near San Benito — different site, different spelling.)
- Equipment (2012 EPA GHG permit exhibits): 2× F-class CCGT — GE 7FA (~183 MW each), Siemens SGT6-5000F(4) (~205 MW), or SGT6-5000F(5) (~232 MW) — plus one 271 MW shared steam turbine. Total 637–735 MW gross, **roughly half the 1,536.4 MW currently claimed by Aegle**.
- **No signed Interconnection Agreement found.** Queue field `iaSigned` is null across all 24 monthly snapshots. PUCT Interchange portal returned HTTP 402 in triage; no IA filing surfaced in Brave search.

| IA document | Signed | Financial security posted |
|---|---|---|
| — (no IA on file) | never | **No** ([financial_security_latest](timeline.json)) |

| Milestone | Original design 2012–13 | Current (Aegle 2024 claim) |
|---|---|---|
| Construction start | 2013-06-01 | not stated |
| Scheduled COD | 2015-10-01 | 2027-07-30 |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2027-07-30 held from 2024-07-01 through 2026-06-01. Stability here is not a positive signal: with zero milestone progression it just means nobody has bothered to update the date.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2020-01 | agricultural fields; some fallow, some planted; no industrial features | [png](imagery/s2_2020-01_tight.png) |
| 2026-07 | still agricultural fields; some cloud but tract clearly bare farmland; airport visible to west, San Benito east | [wide](imagery/s2_2026-07-01.png), [tight](imagery/s2_2026-07_tight.png) |

- Verdict: **no_activity** — 13 years after the 2013 planned construction start, and 11 years past the original 2015 COD, no earthwork, laydown, cranes, turbine hall, cooling structures, or substation pad exist. Sentinel-2 10 m resolution is more than sufficient to detect any CCGT construction; a gas plant of this size is an industrial site occupying ~40+ acres of gravel/concrete/steel.

## 7. COD assessment

- The 2027-07-30 reported COD is a queue field with no contractual grounding — no signed IA, no financial security, FIS unapproved after 24 months, TEF loan denied and unappealable.
- Historical baseline: the same site was permitted in 2012, planned construction 2013, planned COD 2015 — none of it happened. GEM Wiki lists the historical 1,282 MW unit as "Shelved" and a companion 771 MW unit as "Cancelled" (source EIA-860M).
- Aegle's current 1,536 MW claim is nearly DOUBLE the 637–735 MW that was originally permitted. Any credible restart would require a new/amended TCEQ NSR permit — no such permit found under the Aegle name.
- CEO Kathleen Smith's 2017 embezzlement conviction and the fraud-adjacent misuse of NextEra's name on the TEF filing make a lender-backed FID essentially impossible.
- **Independent estimate: no credible COD — treat as paper. Do not include in reasonable-case capacity forecasts.**

## 8. Could not determine

- Exact Cameron CAD parcel ownership at the FM 1595 tract (portal search blocked in triage; not re-attempted)
- Whether a current TCEQ NSR air permit exists under Aegle Power (TCEQ database access was not available in this scan; the 2012–13 permit was under La Paloma Energy Center LLC, which was for 637–735 MW not 1,536 MW)
- Details of the PUCT TEF App-162 filing beyond the public denial press release (PUCT Interchange returned HTTP 402)
- Whether Aegle has commissioned turbine long-lead orders (none surfaced in press releases — a strong reality signal for gas CCGT is absent)
