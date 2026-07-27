# Dossier — Renegade Project / Dawn Solar (20INR0255)

Researched 2026-07-20 · site 34.915, -102.834 · verdict **real_early**

## 1. Verdict

- **real_early** — $9,088,142 irrevocable LC posted to Oncor by Aug 2021 ([IA Exhibit E](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf)); Ch.313 executed 2020-11-23 with Hereford ISD ([agreement](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf)); BPF lists as ["in progress"](sources/2026-07-19_blueplanetfunding_dawn-solar-project-page.html)
- Construction: **reported_started** 2026-03-01 per queue; EIA-860M as of 2026-05-01 still "Not under construction" — lag or overstatement unknown
- Site: 34.915, -102.834 — IA Exhibit C "3.9 miles from FM 809" + Google Places CR12/FM809 pin, medium confidence ([vicinity map](sources/ia_wallaby_switch_vicinity_map_p46.png))
- COD: reported 2027-12-16 → independent **2028-Q2**, drift risk **high** (11 queue slips + 5 EIA COD slips; EIA/queue divergence)

## 2. Site identification

- Derivation: IA Exhibit C places Wallaby Switch "south side of County Road 12, approximately 3.9 miles from FM 809, Deaf Smith County" ([IA](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf)); Google Places pin "809 Co Rd 12" = 34.9155, -102.9032; 3.9 mi east → **34.915, -102.834**. Array extends NW per Ch.313 land description (CR12=east side, Hwy 60=south).
- **Stated project area: ~3,100 acres** per 16-tract sum Ch.313 Exhibit 2 ([agreement](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf)) — imagery unverified at correct site
- Cross-checks: IA vicinity map confirms Wallaby Switch on CR12, western Deaf Smith County ([map](sources/ia_wallaby_switch_vicinity_map_p46.png)); Ch.313 land surveys (Block K-14, Block 3 AB&M) consistent with CR12/FM809 area; EIA-860M coords 34.913, -102.2706 **rejected** (30+ mi east of IA-described site)
- Not obtainable: exact Wallaby Switch GPS (CEII); Deaf Smith CAD parcel boundaries (browser-only)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Renegade Renewables, LLC d/b/a Dawn Solar | SPV | [Ch.313 agreement](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf) |
| Blue Planet Funding (Kevin Adler CEO, Allen Funk COO) | Developer/investor | [BPF project page](sources/2026-07-19_blueplanetfunding_dawn-solar-project-page.html); Funk = Ch.313 signatory |
| BPF Acquisition Co Series 11, LLC | EFT / LC payee | [IA Exhibit E](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf) |
| Sean Purdy / Everett Jones LLC | Managing member | [Ch.313 agreement](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf), Sunbury PA |
| Mortenson Construction | EPC (2018 design) | Ch.313 App 1422 Exhibit 3 title block "Trace 2 - Dawn Solar" |
| — | PPA offtaker | Not found |

- Financing: no public announcement; "Series 11" entity implies fund tranche; no NTP close or debt financing press release found

## 4. Land & county records

- Tenure: **leased (likely)** — 16-tract metes-and-bounds with life estates and homestead exceptions typical of farmland lease ([Exhibit 2](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf))
- Ch.313 App 1422 with Hereford ISD executed 2020-11-23; tax limitation 2022–2031; $30M qualified investment; reinvestment zone created 2018-12-11 by Deaf Smith County Commissioners Court ([agreement](sources/2026-07-19_comptroller_ch313_1422_renegade_agreement.pdf))
- CAD: Deaf Smith CAD portal browser-only; parcel IDs not retrieved

## 5. Interconnection & contractual schedule

- POI: "Wallaby Switch in TSP's Windmill Switch – AJ Swope Switch 345 kV line, Deaf Smith County" ([IA Exhibit C](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf))
- Equipment: 690 TMEIC PVU-L0840GR inverters, 515.66 MW net; 1,950,994 PV modules; single-axis trackers; 138 blocks; 34.5 kV collection; 345 kV POI
- TSP: **Oncor Electric Delivery Company, LLC** (original FSA with Sharyland Utilities L.P., transitioned to Oncor)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf)) | 2021-01-04 | $4,089,664 by 2021-01-08 · **$9,088,142 by 2021-08-13** (irrevocable standby LC to Oncor) |

| Milestone | Original IA |
|---|---|
| In-Service | 2022-04-21 |
| Trial Operation | 2022-04-21 |
| Scheduled COD | **2022-06-01** |

- Queue-history COD drift ([timeline.md](timeline.md)): **11 changes** — 2021-12-21 → **2027-12-16**; 5.5-yr slip from IA original COD

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06 | Imagery not captured at revised site (CDSE RemoteDisconnected); prior chip at Hereford center (wrong location) showed undisturbed farmland | [wrong-loc chip](imagery/s2_hereford_center_2026-06.png) |

- Verdict: **imagery_not_captured** — CDSE endpoint unavailable; site at 34.915, -102.834 not imaged

## 7. COD assessment

- **IA original COD was 2022-06-01** — queue now 2027-12-16 = 5.5-year slip since IA signing ([IA Exhibit B](sources/2026-07-20_puct_35077-1207_interconnection-agreement-between-oncor-electric.pdf))
- **EIA-860M divergence (key risk signal)**: EIA plant 65310 logged 5 COD slips (2023-12→2024-12→2025-03→2025-06→2026-06→2026-12) and status "Not under construction" through 2026-05-01 — 2 months after queue's claimed 2026-03-01 construction start; EIA ≠ queue ([eia_history.json](eia_history.json))
- **For project**: $9.1M irrevocable LC to Oncor confirmed paid; Meets 6.9(1) 2024-04-30; active BPF project page; land secured (Ch.313 since 2018)
- **Against**: FIS never approved (requested 2019); no PPA announced; no financing press release; BPF page lists 683 MW vs queue's 515 MW (unexplained scope gap); EPC unconfirmed for current build
- Historical slip velocity ~1.4yr/yr on queue; adding 2 quarters of buffer to queue's 2027-12-16 → **2028-Q2** independent estimate

## 8. Could not determine

- Whether construction physically started (EIA lag + no imagery)
- EPC for current build (Mortenson 2018 design only)
- PPA counterparty / offtaker
- FIS approval (requested 2019, absent from all 89 queue snapshots)
- IA amendments (one filing found; no amendments in INR join table)
- Exact site GPS (IA gives road-distance anchor; CAD parcel coords not retrieved)
- 683 MW vs 515 MW discrepancy (BPF page vs queue)
