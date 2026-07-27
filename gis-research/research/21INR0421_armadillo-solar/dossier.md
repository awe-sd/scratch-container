# Dossier — Armadillo Solar (21INR0421)

Researched 2026-07-23 · site 32.0098, -96.3632 · verdict **real_active**

## 1. Verdict

- **real_active** — active ACTIVE TCEQ construction-stormwater permit (EPC named) plus a large graded/racking solar polygon visible in imagery, both at a site independently triangulated from county abatement records, news, and a Google Places pin ([storm NOI](sources/2026-07-23_tceq_armadillo-solar-stormwater-noi.json))
- Construction: **racking**, first activity **2024-10** (tentative) / clear by **2025-04** ([2025-04 frame](imagery/key/s2_2025-04-15.png), [2025-10 frame](imagery/key/s2_2025-10-15.png))
- Site: 32.0098, -96.3632 — imagery + TCEQ site description + news + Ch.312 boundary map cross-check, high confidence ([satellite view](https://www.google.com/maps/@32.0098,-96.3632,5000m/data=!3m1!1e3))
- COD: reported 2026-10-27 → independent **2026-Q4** (most likely ~2026-12-31), drift risk **low-medium** (queue is 2 months ahead of the generator's own signed IA date; construction is real and active)

## 2. Site identification

- Derivation: TCEQ ACTIVE stormwater NOI describes the site as "south of the intersection of SH-287 and SE County Road 2040, between the cities of Mildred and Navarro TX" ([storm NOI](sources/2026-07-23_tceq_armadillo-solar-stormwater-noi.json)); a Sentinel-2 chip centered on the midpoint reveals an unmistakable graded/racking solar polygon complex ([wide frame](imagery/grid/probe_2026-07.png)); centroid of the densest racking polygon = 32.0098, -96.3632
- **Stated project area: 2,300 acres** per Corsicana Daily Sun (2020-11-14) — AES.com separately states "~2,000 acres" ([AES page](sources/aes_project_page.md)); imagery footprint (an irregular multi-km-wide graded cluster) is consistent with a ~2,000-2,300 acre site
- Cross-checks (each linked): Google Places pin "Armadillo Solar", 5950 SE 2050, Corsicana TX (32.0084, -96.3743) ([gmaps.py places](sources/aes_project_page.md)) is 1.2 km from Navarro village / 3.0 km from Mildred village; Corsicana Daily Sun news text "~1 mile north of Mildred High School on Hwy 287"; Ch.312 [reinvestment-zone boundary map](sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-cente_p19.png) shows an irregular Z-shaped polygon spanning between labeled "Mildred" and "Navarro"/"Cheneyboro" — same shape family as the imagery footprint. All agree within ~3 km.
- **Rejected candidates (explicit negative evidence):** EIA860M plant coordinate (32.00014, -96.2027) is ~16-17 km from Mildred/Navarro — inconsistent with every other source, treated as an unsurveyed placeholder in AES's EIA filing; triage's address-geocode (9316 US-287, 31.9996, -96.2467) is ~12-13 km off — that address is near Kerens/Streetman, not the Mildred-Navarro corridor, and is now known to be wrong
- Not obtainable: exact Revolution Switch / POI structure coordinates (IA Exhibit C describes it only in text, no CEII map attached to the filed PDF)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Armadillo Solar Center, LLC | SPV / Generator | party on [original IA](sources/2026-07-19_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf) and all amendments; owner on [Ch.312 abatement](sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-center.pdf) |
| Ørsted Onshore North America, LLC | original developer (2020-2024) | Ch.312 agreement signature block: "By Its Sole Member, Ørsted Onshore DevCo, LLC, By Its Sole Member, Ørsted Onshore North America, LLC" ([p15](sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-center.pdf)); original IA notice email `BRERO@Orsted.com` |
| AES Corporation (AES Clean Energy) | current developer/owner (from ~2024) | [Amendment 5](sources/2026-07-19_puct_35077-1926_amendment-no-5-to-the-standard-generation-interc.pdf) notice address changed to AES's Louisville CO office, @aes.com emails; [AES project page](sources/aes_project_page.md); Corsicana Daily Sun 2025-04-30 "First Amendment to Tax Abatement agreement" filed post-takeover ([article](sources/2026-07-23_corsicanadailysun_commissioners-amend-abatement-agreement.html)) |
| Hanwha Q Cells EPC USA LLC | EPC contractor | named principal on ACTIVE TCEQ stormwater permit TXR1538TO alongside Armadillo Solar Center LLC, affiliation begin 2025-02-07 ([storm NOI](sources/2026-07-23_tceq_armadillo-solar-stormwater-noi.json)) |

- Financing: not disclosed in any source found; Ch.312 agreement states minimum investment of **$140,000,000** ([p4](sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-center.pdf)); Navco Chronicle cites "$300 million+" capital investment ([article](sources/2026-07-23_navcochronicle_armadillo-solar-signals-bright-future.html))

## 4. Land & county records

- Tenure: **leased (probable)** — Corsicana Daily Sun (2020-11-14) describes the reinvestment zone as "covering leased properties from six landowners" within Mildred ISD; no CAD parcel search performed (ran out of budget)
- Abatement: **Ch.312** (not Ch.313 — ch313.py's negative result was correct) tax abatement between Navarro County and Armadillo Solar Center, LLC, executed 2020-11-09 ([agreement](sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-center.pdf)): 175-200 MW PV, 10-year abatement period, PILOT $525/MW (county) + $367/MW (road & bridge), entirely within Mildred ISD; **First Amendment** approved by Commissioners Court 2025-04-30 to "update the terms of the ongoing project" post-AES-takeover ([article](sources/2026-07-23_corsicanadailysun_commissioners-amend-abatement-agreement.html))
- CAD: not searched (turn budget)

## 5. Interconnection & contractual schedule

- POI per signed IA: "the TSP's Revolution Switch at 138 kV... adjacent to TSP's existing 69kV Navarro Sub on Main St in the town of Navarro, Navarro County, Texas" ([IA](sources/2026-07-19_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf), Exhibit C) — requires re-terminating the Hillsboro-Navarro and Corsicana-Navarro 138kV lines into the new Revolution Switch
- Equipment: original IA = 270 inverters (TMEIC PCS-840, 226.8 MVA, 204 MW net); [Amendment 7](sources/2026-07-19_puct_35077-2295_amendment-no-7-to-the-standard-generation-interc.pdf) restates as 57× SMA SC4400-UP-US inverters, 231.85 MVA gross, dispatched 202.6 MW at generator terminals / 200.03 MW at the 34.5kV bus — **the IA has not been amended to reflect the queue's Feb-2026 capacity cut to 150.48 MW; a contract-vs-queue capacity mismatch remains open**

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1230_interconnection-agreement-between-oncor-electric.pdf)) | 2021-02-02 | $4,086,825 (by 2021-06-04) → $9,081,832 (by 2022-01-03) |
| Amendment No. 5 ([pdf](sources/2026-07-19_puct_35077-1926_amendment-no-5-to-the-standard-generation-interc.pdf)) | 2024-08-14 | $10,833,691 cumulative (by 2024-12-04, ~4 yrs after originally required) |
| Amendment No. 6 ([pdf](sources/2026-07-19_puct_35077-2216_amendment-no-6-to-the-standard-generation-interc.pdf)) | 2025-08-01 | unchanged ($10,833,691 — Exhibit E not amended) |
| Amendment No. 7 ([pdf](sources/2026-07-19_puct_35077-2295_amendment-no-7-to-the-standard-generation-interc.pdf)) | 2025-10-31 | unchanged ($10,833,691 — Exhibit E not amended) |

| Milestone | Original IA 2021 | Amend 5 (2024) | Amend 6 (2025-08) | Amend 7 (2025-10) |
|---|---|---|---|---|
| In-Service | 2022-11-17 | 2025-12-04 | 2026-04-16 | 2026-04-16 |
| Trial Operation | 2022-11-27 | 2026-07-01 | 2026-07-01 | 2026-06-01 |
| Scheduled COD | 2022-12-31 | **2026-12-31** | **2026-12-31** | **2026-12-31** |

- Queue-history COD drift (from [timeline.md](timeline.md)): **6 changes** — 2021-12-31 → 2022-12-31 → 2023-09-28 → 2024-10-15 → 2025-10-15 → 2026-12-31 → 2026-10-27; in reports since 2019-09-01 (82 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-01 | undisturbed farmland | [2024-01](imagery/key/s2_2024-01-15.png) |
| 2024-10 | faint rectangular disturbance (tentative early clearing) | [2024-10](imagery/key/s2_2024-10-15.png) |
| 2025-04 | clear graded/cleared patches, multiple distinct polygons | [2025-04](imagery/key/s2_2025-04-15.png) |
| 2025-10 | extensive graded footprint, internal road grid across most of frame | [2025-10](imagery/key/s2_2025-10-15.png) |
| 2026-03/06 | partly cloudy; visible portions show advancing footprint, clearer racking-row lines | [2026-03](imagery/key/s2_2026-03-15.png) |
| 2026-07 | full graded/racking complex confirmed, centered 32.0098,-96.3632 | [2026-07 wide](imagery/grid/probe_2026-07.png) |

- Verdict: **racking** — bulk earthwork essentially complete by 2025-10, matching Navco Chronicle's reported Spring-2025 construction start; 10 m Sentinel-2 resolution cannot confirm installed modules over bare graded soil

## 7. COD assessment

- Reported 2026-10-27 is **not** the contractual date — the generator's own most recent signed IA amendment (No. 7, 2025-10-31) sets Scheduled COD at **2026-12-31**, a figure unchanged since Amendment 5 (2024-08-14)
- Independent news (Navco Chronicle) corroborates "Winter 2026" — consistent with the IA, not the queue
- EIA-860M's own COD estimate for this plant *slipped* from 2026-07 to 2027-05 between the 2025-12 and 2026-01 monthly reports ([eia_history.json](eia_history.json)) — the opposite direction from the queue's tightening to 2026-10-27, a decisive divergence signal
- AES's public marketing page states "2027" — treated as an upper-bound/rounded figure, not the central estimate, given the more specific and more recently-signed IA and news dates
- Construction is real and visibly advancing (racking stage, ACTIVE TCEQ storm coverage, named EPC) — this is not a paper project, but the queue's specific day-level COD (2026-10-27) is unsupported by any primary document
- **Independent estimate: 2026-Q4 (most likely at or near the IA's 2026-12-31 date), drift risk low-medium**

## 8. Could not determine

- Exact Revolution Switch / POI structure coordinates (IA text-only, no map exhibit attached to the filed PDF)
- CAD parcel-level ownership (search not performed — turn budget)
- Financing details / lenders (no PR or SEC filing found specific to this project's debt/equity close)
- Resolution of the queue's Feb-2026 capacity cut (204→150.48 MW) against the IA, which as of the latest amendment (Nov 2025) still specifies ~200 MW — no Amendment 8 found
- Why ch312.py's registry search missed this abatement by name (the county's own PDF was used as primary evidence instead)
