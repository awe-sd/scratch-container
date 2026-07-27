# Dossier — Indigo Solar (21INR0031)

Researched 2026-07-20 · site 32.628, -100.236 · verdict **real_early**

## 1. Verdict

- **real_early** — genuine IA paper trail with a real SPV transfer and $24.98M security posted ([2nd Amendment](sources/2026-07-20_puct_35077-1860_second-amendment-to-generation-interconnection-a.pdf)), but EIA-860M has logged "(P) regulatory approvals not initiated" for all 33 months on record ([eia_history.json](eia_history.json)) and no construction has started
- Construction: **no_activity** (imagery unavailable this run — see §6), no groundbreaking/EPC news found
- Site: 32.628, -100.236 — two independent fixes converge within 1.36 km: EIA-860M self-reported plant point, and geocode of the Fisher County abatement notice's "~6.5 miles south of Sylvester, TX" ([map](https://www.google.com/maps/@32.628,-100.236,5000m/data=!3m1!1e3)); medium-high confidence
- COD: reported 2027-09-17 → independent **2028-Q2**, drift risk **high** (no on-file IA amendment supports current claim; 4 prior slips; zero EIA-reported progress)

## 2. Site identification

- Derivation: EIA-860M plant coordinates (32.62806, -100.236) cross-checked against an independent geocode: Fisher County Ch.312 abatement notice states the site is "~6.5 miles south of the community of Sylvester" ([notice](sources/2026-07-20_fishercounty_notice-IS245-indigo-reinvestment-zone.pdf)); Sylvester, TX = 32.72194, -100.25056 (Wikipedia) → calculated point 32.6277, -100.2506, agreeing with the EIA point within 1.36 km
- **Stated project cost: $300,000,000** for ~150 MW AC solar + potential 180 MW AC/360 MWh BESS per the same abatement notice — acreage not stated in any document obtained; imagery footprint not verified (see §6)
- Cross-checks: IA Attachment C-3 "Project Overview Map" ([artifact](sources/ia_35077-2447_attC3_map_p42.png)) shows the boundary anchored on County Road 151 (N), FM 1085 (E), County Road 164, and Dry Creek (S), around a new "Lone Star Jordan Station" — consistent with the POI text (Claytonville–Phantom Hill 345 kV cut-in) but road-geometry was not independently pixel-matched to imagery this run
- Not obtainable: exact parcel/CAD tract; Google Places/Static Map pins (both gmaps.py endpoints unavailable — see §8)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| GGS Energy, LLC | original SPV (2020–2022) | Named Generator on [original IA](sources/2026-07-20_puct_35077-1161_ercot-standard-generation-interconnection-agreem.pdf), signed 2020-10-15 |
| Innovative Solar 245, LLC | current SPV | [First Amended & Restated IA](sources/2026-07-20_puct_35077-1483_first-amended-and-restated-ercot-standard-genera.pdf) (2022-09-15) transfers from GGS Energy; also applicant on [Fisher Co. abatement notice](sources/2026-07-20_fishercounty_notice-IS245-indigo-reinvestment-zone.pdf) |
| Innovative Solar Solutions (ISS) | developer (unverified corporate link) | Triage web sweep: PV Magazine names ISS as owner of a 690 MW TX portfolio including Indigo; GEM.wiki page blocked (HTTP 403, both triage and deep) |
| Lone Star Transmission, LLC (c/o NextEra Energy Transmission) | TSP counterparty | IA party; billing notices route to NextEra Energy Transmission, Juno Beach FL |

- Financing: not found — no press release, financing announcement, or EPC contractor identified this run (negative evidence, logged in [log.md](log.md))

## 4. Land & county records

- Tenure: **unknown** — CAD parcel-owner search not completed this run (time budget)
- Fisher County **Ch.312** tax-abatement public hearing (2024-12-09) names Innovative Solar 245, LLC as "applicant and property owner," $300M improvement cost, "IS 245 - Indigo LLC Reinvestment Zone" ([notice](sources/2026-07-20_fishercounty_notice-IS245-indigo-reinvestment-zone.pdf)) — vote outcome not confirmed (commissioners-court minutes not located)
- Ch.313/JETI: **0 hits** for "Indigo Solar" / "Innovative Solar 245" / Fisher County across 3 query variants ([ch313.py resolve](log.md)) — expected, since this project uses a county Ch.312 abatement rather than a school-district Ch.313/JETI value-limitation agreement
- CAD: not searched this run

## 5. Interconnection & contractual schedule

- POI per signed IA: new TSP-owned dead-end structure at "new Lone Star Jordan Station," formed by cutting in the existing Claytonville–Phantom Hill 345 kV circuit ([Exhibit C, 2nd Amendment](sources/2026-07-20_puct_35077-1860_second-amendment-to-generation-interconnection-a.pdf)) — matches queue POI text exactly
- Equipment (Exhibit C): Canadian Solar CS6U-335P panels + TMEIC PVH-L2700GR 2.5 MW inverters, 150 MWac

| IA document | Signed | Financial security |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-1161_ercot-standard-generation-interconnection-agreem.pdf)) | 2020-10-15 | not stated in this doc |
| First Amended & Restated ([pdf](sources/2026-07-20_puct_35077-1483_first-amended-and-restated-ercot-standard-genera.pdf)) | 2022-09-15 | $19,660,000 (Milestones 8/19/22, 11/1/22, 3/1/23) |
| Second Amendment ([pdf](sources/2026-07-20_puct_35077-1860_second-amendment-to-generation-interconnection-a.pdf)) | 2024-06-17/18 | $24,980,000 total ($19.66M + $5.32M due 12/31/24) |
| Third Amendment ([pdf](sources/unverified_2026-07-19_puct_35077-2036_third-amendment-to-generation-interconnection-ag.pdf)) | 2024-12-31 | $24,980,000 unchanged; Milestone II due date pushed to 2/11/25 |
| Fourth Amendment ([pdf](sources/unverified_2026-07-19_puct_35077-2087_fourth-amendment-to-generation-interconnection-a.pdf)) | 2025-02-19/03-10 | $24,980,000 unchanged; Milestone II due date pushed again to 4/11/25 |

| Milestone | Restated IA 2022 | 2nd Amendment 2024 |
|---|---|---|
| TIF In-Service | 2024-04-01 | 2026-05-15 |
| Trial Operation | 2024-10-11 | 2026-06-01 |
| Scheduled COD | 2024-12-31 | 2026-08-17 |

- The 3rd and 4th Amendments touched **only** Exhibit E (security) — twice pushing back the "Remaining Security" due date, never the schedule itself; no 5th Amendment found in the docket ([puct.py filings check](log.md))
- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2021-12 → 2023-10 → 2024-12 → 2026-08 → 2027-09 (current); the 2026-08-17 step exactly matches the 2nd Amendment's Exhibit B, cross-validating the extraction — but the current 2027-09-17 claim has **no matching IA amendment on file**
- A separate Standard GIA ([pdf](sources/2026-07-20_puct_35077-2447_standard-generator-interconnection-agreement-bet.pdf), filed 2026-04-03) covers co-located "Indigo Storage 1–4" (different INRs) between the same parties — confirms ongoing paperwork at the site, but not for this solar INR

## 6. Satellite timeline

- **Not obtained this run.** CDSE/openEO service failed on 8 attempts over ~50 minutes ("Remote end closed connection without response"), reproduced against a known-good reference site — a service-side outage, not a bad coordinate. gmaps.py Places (429, rate-limited) and Static Map (403, API not enabled on the key) were also unavailable. The 3 chips already on disk from the triage pass (`imagery/s2_2026-05-*.png`) are centered on a **superseded** candidate ~15 km away (Claytonville substation) and are not evidence for this site.
- Verdict: **no_activity (unconfirmed by imagery)** — based on absence of any construction signal in county/PUCT/news records rather than direct visual inspection; genuinely undetermined pending a retry

## 7. COD assessment

- Contractually, the only schedule on file (2nd Amendment, June 2024) sets COD at **2026-08-17** — the queue's current claim of 2027-09-17 is not backed by any amendment filed since (checked through 2026-07-20)
- EIA-860M (independent of the developer) has slipped its own planned COD four times — 2025-05 → 2026-05 → 2026-11 → 2027-05 (latest, May 2026 report) — and even EIA's own newest figure trails the queue's claim by 4 months
- EIA status has read **"(P) regulatory approvals not initiated"** for the entire 33-month reporting window with no change — the strongest available evidence of stalled progress
- The Generator has twice failed to meet its own posted financial-security deadline (12/31/24 → 2/11/25 → 4/11/25), requiring two amendments just to extend the date — a soft distress signal, though the $24.98M amount itself has been posted and never reduced
- No financing, EPC, or offtake announcement found; no construction visible in available (superseded-location) imagery; no confirmed groundbreaking
- Given 4 prior COD slips (avg. ~1.5–2 yrs each), zero construction start, and a current claim already ungrounded in its own paperwork: **independent estimate 2028-Q2, drift risk high**

## 8. Could not determine

- Satellite confirmation of construction stage at the corrected site (CDSE outage this run)
- Google Places/Static Map site imagery (both endpoints unavailable: 429 / 403)
- CAD parcel ownership / land tenure (leased vs. purchased)
- Outcome of the 2024-12-09 Fisher County Ch.312 abatement vote
- Corporate link from Innovative Solar 245, LLC to "Innovative Solar Solutions" parent (GEM.wiki blocked, TX SOS not queried)
- Whether a 5th IA Amendment exists that would explain the queue's 2027-09-17 COD (none found in docket 35077 as of 2026-07-20)
