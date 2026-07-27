# Dossier — Shaula II Solar (22INR0267)

Researched 2026-07-21 · site ~29.115, -97.13 · verdict **unclear**

## 1. Verdict

- **unclear** — real, legally-executed project (signed IA + executed Ch313 agreement) that has missed its own contractual COD with zero visible construction and no financing/groundbreaking announcement ([Ch313 findings](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf), [IA Amendment](sources/2026-07-21_puct_35077-1555_filing.pdf))
- Construction: **no_activity**, first activity never observed ([2026-07 frame](imagery/s2_2026-07-15_friarrd.png))
- Site: ~29.115, -97.13 — Ch313 boundary map + named-road geocode (Friar Rd, Cattle Guard Rd), medium confidence ([map](https://www.google.com/maps/@29.115,-97.13,5000m/data=!3m1!1e3))
- COD: reported 2026-05-30 → independent **indeterminate, high drift risk** (contractual date already passed, no build evidence)

## 2. Site identification

- Derivation: Ch313 Application #1715 Tab 11 vicinity map shows two non-contiguous reinvestment-zone polygons over roads labeled "Friar Rd" and "Cattle Guard Rd" ([aerial](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-find_p29.png), [road map](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-find_p30.png)); `gmaps.py places` geocodes Friar Rd to 29.0963,-97.1595 and Cattle Guard Rd to 29.1442,-97.0988 (both DeWitt Co) — centroid estimate ~29.115,-97.13
- **Stated project area: 1,491.3 acres** per Ch313 Yoakum ISD Resolution Exhibit A, 9 itemized DCAD parcels ([exhibit](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf) p147) — imagery footprint consistent? unverified, no development visible to shape-match against
- Cross-checks: Tab 4 "located in eastern DeWitt County in western Yoakum ISD" ([app](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf) p21) agrees with road geocodes; IA POI "~63 mi east of CPS Energy Elm Creek 345kV Switchyard" is consistent with a DeWitt Co site but the exact tap point is not resolvable from IA text alone
- Not obtainable: parcel-level boundary-to-imagery shape match (no graded footprint exists yet to match against); exact POI tap coordinates (not in IA exhibits, generic C1 diagram)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Shaula Energy Project II, LLC | SPV | party on [IA](sources/2026-07-21_puct_35077-1413_filing.pdf) and [Ch313 app](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf) |
| BP Solar Holding, LLC | sole member / owner | IA signature page ([Amend 1](sources/2026-07-21_puct_35077-1555_filing.pdf) p4); Ch313 Tab 4 "wholly owned by BP Solar Holding, LLC" |
| Lightsource bp | developer | Ch313 Tab 4: "being developed by Lightsource BP under a development services agreement...5.4 GW of developed solar" |

- Financing: **no financial close, groundbreaking, or construction announcement found** for Shaula I or II in any Lightsource bp/BP press search — contrast with Starr Solar/Second Division Solar and Elm Branch/Briar Creek, which each got explicit newsroom announcements at close (search.py queries logged in [log.md](log.md)). BP took full ownership of Lightsource bp Oct 2024, then announced a renewables-capex cut (~$5B/yr → $1.5-2B/yr) in Feb 2025 under shareholder pressure — a corporate headwind coinciding with Shaula II's construction-NTP window

## 4. Land & county records

- Tenure: **leased** — Ch313 Tab 9 "Description of Land: Not Applicable" ([app](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf) p26); reinvestment-zone parcels titled to 9 separate ranch families (Boothe, Dowlearn/Fort/Lucas/Nash/Park "Chicolete Ranch", Granberry, Doolittle), not to Shaula/BP
- **Ch313 agreement EXECUTED**: Yoakum ISD Board Resolution, approved 2022-11-17, signed by Board President Glen Kusak + Secretary Darlene Renken ([findings doc](sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf) p6); Comptroller approved the agreement 2022-10-20; supplemental payments >$1.765M owed 2026-2034. This CORRECTS the initial REFRESH_DIRECTIVE note of "Ch.313/JETI: negative" — that was a gap in the local static-table tool (keyed on "Yoakum"/school district, missed by name-search), not a true absence; live search.py found the primary document directly
- CAD: not independently queried (DeWitt CAD has no online owner-name search tool available); parcel/owner list obtained instead from the Ch313 exhibit itself (see §2)
- DeWitt County commissioners-court minutes: harvested + indexed (82 files, 75 image-only/no-OCR — real coverage only 7 files) — no mention of "Shaula"/"Lightsource" in the searchable subset (weak negative, most of the archive is unsearchable scans)

## 5. Interconnection & contractual schedule

- POI per signed IA: "approximately 63 miles east of the CPS Energy-owned Elm Creek 345 kV Switchyard on the 345 kV Elm Creek to STP transmission circuit 1" ([IA](sources/2026-07-21_puct_35077-1413_filing.pdf), [Amend 1](sources/2026-07-21_puct_35077-1555_filing.pdf)) — matches queue POI text exactly
- Equipment (Exhibit C): ~63× 3.257 MVA PV inverter arrays, 205.2 MW AC — matches queue MW exactly; matches Ch313's "530,000 photovoltaic panels and 63 central inverters"; GIF-to-TIF tie line ≤1 mile

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-21_puct_35077-1413_filing.pdf)) | 2022-04-27 | $2,046,000 (design/procurement) + $889,000 (construction) = $2,935,000 |
| First Amendment ([pdf](sources/2026-07-21_puct_35077-1555_filing.pdf)) | 2022-11-16 | $2,935,000 — unchanged from original |

| Milestone | Original IA (2022) | Amendment 1 (2022) |
|---|---|---|
| In-Service | 2024-10-25 | 2025-04-25 |
| Trial Operation | 2024-11-12 | 2025-05-30 |
| Scheduled COD | 2024-12-24 | **2026-05-30** |

- TSP is CPS Energy (San Antonio muni), not a standard IOU — this is why `puct.py`'s INR-join rung-0 missed it; found via `puct.py filings --match "Shaula"` instead. Schedule is contractually tied 1:1 to sibling Shaula I Energy Project (22INR0251) — delays to either extend both
- Queue-history COD drift (from [timeline.md](timeline.md)): **6 reported-COD changes** across 79 monthly snapshots (2019-12→2026-06); COD has sat at 2026-05-30 since 2023-04 — unchanged for 3+ years even as the date approached and then passed. **FIS never approved, `meets_all_6.9` never achieved, construction start never reported** despite the IA being signed over 4 years ago

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-12 (cloud 54%) | too cloud-covered to judge | [2024-12](imagery/s2_2024-12-01_friarrd.png) |
| 2026-07 (scene 2026-07-19) | undisturbed pasture/ranchland at both named-road geocode and the larger SE reinvestment-zone polygon; no clearing, grading, or racking signature anywhere in an ~8 km window | [Friar Rd](imagery/s2_2026-07-15_friarrd.png), [SE parcel](imagery/s2_2026-07-15_se-parcel.png) |

- Verdict: **no_activity** — as of the most recent available scene (2026-07-19), ~14 months after the amended In-Service Date and ~2 months after the amended Commercial Operation Date have both already passed, the site shows zero construction; imagery cannot rule out a build starting outside the two chipped windows if the true parcel centroid differs from the road-geocode estimate

## 7. COD assessment

- Reported 2026-05-30 is the exact contractual Commercial Operation date from the countersigned [IA Amendment No. 1](sources/2026-07-21_puct_35077-1555_filing.pdf) (signed 2022-11-16) — legally grounded, but **that date has now passed** (today 2026-07-21) with no visible construction and no financing announcement
- One prior schedule slip (~17 months, original→amendment) occurred pre-construction in 2022, before any site work was contractually due — normal for early-stage IA negotiation, not itself alarming
- The project cleared real legal/financial gates a genuine paper filing usually skips: executed Ch313 value-limitation agreement with a real school district (Yoakum ISD, 2022), $2.9M security posted per IA, itemized 9-parcel legal description with real DCAD PIDs — this is NOT boilerplate
- But four independent signals now point toward stall/abandonment risk: (1) FIS never completed in ~4 years despite signed IA; (2) EIA-860M has zero record this project ever existed; (3) no Lightsource bp/BP press release ever announced Shaula financing or construction, unlike every other Lightsource bp Texas project found in search; (4) BP's Feb-2025 renewables-capex retreat directly overlaps the window Shaula II needed construction notice-to-proceed
- **Independent estimate: indeterminate — cannot assign a credible COD.** The contractual date is void (passed, unmet) and there is no independent evidence (construction, financing, EIA reporting) to project a new one. Drift risk: **high** — the project may resume, be re-amended, or quietly lapse; nothing observed here distinguishes those outcomes

## 8. Could not determine

- Whether Shaula I's status (dependency trigger in both IA exhibits) is itself active, stalled, or cancelled — would directly explain Shaula II's schedule
- Live TX Comptroller franchise-tax status for Shaula Energy Project II, LLC in 2026 (only a 2022 "ACTIVE" snapshot was available, embedded in the Ch313 exhibit; the live search portal requires JS/session interaction not reachable via `curl`)
- DeWitt CAD owner-name parcel confirmation (no public search tool found; parcel list taken from the Ch313 exhibit itself, not independently cross-checked against a live CAD lookup)
- A precise parcel-level site centroid — current estimate is a named-road geocode, not a boundary-matched coordinate, since no development footprint exists yet to shape-match
- Whether a newer (post-2022) IA amendment exists that further changed the schedule — `puct.py filings --match "Shaula"` returned only the 4 filings found (2 per phase); a 2nd amendment may not yet be docketed or may not exist
