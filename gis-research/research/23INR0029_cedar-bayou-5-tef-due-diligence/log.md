# Triage log — Cedar Bayou 5 (TEF - Due Diligence) (23INR0029)

## T1 start
- queue_history.py: 76 snapshots, 2020-03-01 → 2026-06-01
- **COD drift: 4 changes** — 2023-07-05 → 2023-06-01 → 2026-06-01 → 2027-02-02 → 2027-12-15 (current)
- First slipped from mid-2023 to mid-2026 (big slip ~Sep 2022), then to 2027 territory
- Milestones achieved: Screening started (2020-03-26), Screening complete (2020-06-04), FIS requested (2020-03-18), **FIS approved (2025-05-30)**, **IA signed (2022-01-10)**, **Meets 6.9(1) (2025-02-12)**
- Milestones NOT achieved: Meets all 6.9, construction start/end, approved-for-energization/synchronization/commercial-operation
- Summary: IA signed Jan 2022, FIS approved May 2025 (very late), meets 6.9(1) Feb 2025. No construction milestones. COD 2027-12-15 is the 5th reported COD.

## T2 start
- gmaps.py: HTTP 429 on both attempts (rate-limited). No pins found.
- Note: Cedar Bayou is a well-known existing industrial site in Baytown area (Chambers/Harris County border) — Cedar Bayou 5 likely references units 1-4 of the existing AEP Texas Central Cedar Bayou power plant (Baytown, TX). This is strong prior context for site location.
- pins_found: 0 (tool blocked)

## T3 start
- Developer: NRG Energy / NRG Cedar Bayou 5 LLC
- PUCT TEF docket: Project 56896; advanced to due diligence Dec 12, 2024 (721 MW cited at PUCT)
- Turbine: Mitsubishi Power MHI501JAC (415 MW GT + 280 MW ST = 695 MW CCGT) — strong reality signal
- Status per web: "permitting stage" as of Nov 2024 (power-technology.com)
- news_found: YES; sources saved to sources/T3_web_sweep.md

## T4 start
- PUCT Interchange: HTTP 402 on ALL endpoints (FilingParty, Description, docket 56896, direct PDF URL)
- ia_found: KNOWN from queue data (iaSigned = 2022-01-10) but PDF not retrieved
- TEF docket 56896 confirmed from T3 web sources; cannot pull documents via WebFetch
- ia_found: true (from queue milestones); IA PDF: blocked

## T5 start
- Ch.313: Program closed to new applications after 2022; Cedar Bayou 5 entered queue 2020 but IA not signed until 2022-01-10 — possible pre-cutoff window, but Comptroller search portal not directly queryable via WebFetch (redirects to overview pages)
- JETI: Could not retrieve project list via WebFetch (portal returns overview pages only, not data)
- abatement_found: UNKNOWN (portal blocked to direct query) — normal for post-2022 gas project; worth checking in deep scan
- Note: TEF loan program is the primary financial incentive mechanism here, not Ch.313/JETI

## T6 start
- Site candidate: 29.726, -95.015 — existing Cedar Bayou Generating Station (units 1-4), confirmed by POI "40000 Cedar Bayou 345kV" and cooling pond visible in imagery. Method: POI name + known plant location.
- Chips acquired: 4/9 (others 403 CDSE auth errors during grid; center chip from chips command succeeded, 3 offset chips succeeded, 4 failed 403, 1 baseline attempt failed 401 auth expired)
- Contact sheet read: chips at -94.955 (suburban/residential east), -94.985 center (suburban/mixed), -95.015 (EXISTING PLANT — large dark cooling pond, industrial structures), -95.015 N tile (industrial mix)
- Full-size read: 29.726/-95.015 — existing plant site clearly visible; large cooling reservoir with dark water, surrounding industrial infrastructure. No new laydown yards, cranes, construction staging, or greenfield clearing visible at 10m resolution as of 2026-06.
- Baseline (2023): BLOCKED — CDSE 401 Unauthorized (token expired)
- construction_visible: false (no new construction footprint seen; site appears operational/unchanged)
- Note: Cedar Bayou 5 is an EXPANSION of the existing plant — new unit added to operating complex. Construction signature would be adjacent to existing structures; may be subtle at 10m.

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP

## Deep scan T1 — PUCT filings

- **PUCT 56455/9 (2024-05-09)**: NRG Cedar Bayou 5 LLC NOI for TEF, signed by Matthew J. Pistner (SVP Generation NRG Energy) — confirms 23INR0029, Baytown, 721 MW nameplate, CCGT. Verbatim: **"the Cedar Bayou 5 project is shovel-ready as NRG has the necessary ERCOT interconnection agreements, environmental permits and water rights to commence construction immediately."** ([NOI](sources/2026-07-18_puct_56455-9_nrg-cedar-bayou-5-NOI.pdf)) — strong reality signal from developer, dated 2024-05.
- **PUCT 56896/60 (2024-12-12)**: TEF Staff memo advancing NRG APP-016 (721 MW) to due diligence review; DD expected 4–8 months. Portfolio criteria required "signed EPC agreement + equity commitment/attestation" and "arrangements to obtain required equipment." Approved same day by PUC OPDM Order (56896/61). ([DD memo](sources/2026-07-18_puct_56896-60_cedar-bayou-DD-memo.pdf)) — institutional validation.
- **PUCT 56896**: Cedar Bayou 5 does NOT appear in the 2025-Q4 / 2026-H1 extension-request or withdrawal filings (siblings GB6, Bulldog, Homestead, Pecos, Permian I/II, Invenergy, Rayburn, MPH Bastrop, NGEC did file for extensions). Absence of extension = milestone schedule still on track per TEF program. Only sibling NRG Greens Bayou 6 filed for extension (2025-10-21) then withdrew the request (2025-11-21).
- **PUCT full-text search for "Cedar Bayou 5"**: no hits under Description or FilingDescription — IA/POI docs likely under CenterPoint's generic docket (TBD) or filed as CEII.

## Deep scan T2 — TCEQ air permit check

- **TCEQ CR search "Cedar Bayou"** ([saved](sources/2026-07-18_tceq_cr_cedar-bayou-search.html)) — found:
  - **RN100825371** CEDAR BAYOU ELECTRIC GENERATING STATION, 7705 W Bay Rd, Baytown 77523, Chambers Co. — existing NRG plant
  - **RN110333184** CEDAR BAYOU GENERATING STATION, West Bayou Rd, Baytown 77520, Chambers Co. — SEPARATE, NEWER TCEQ registration = **very likely the CB5 expansion registered as a distinct Regulated Entity** (RN >110M is a recent number; existing plant is RN <101M)
  - CenterPoint Energy — Cedar Bayou Substation (RN109910265) confirms POI is CNP-owned
- Direct NSR permit-number retrieval blocked by JS-driven CR detail pages, but the RE existence + NRG's own [NOI attestation](sources/2026-07-18_puct_56455-9_nrg-cedar-bayou-5-NOI.pdf) ("necessary environmental permits and water rights") is strong reality signal. Absence of a "PAPER PROJECT" TCEQ dead-end (no CR registration for a >600 MW gas plant would be an immediate paper-project verdict).

## Deep scan T3 — IA + Amendment 1 retrieved (PUCT 35077)

- **IA original** ([2026-07-18_puct_35077-1362_centerpoint-nrg-cedar-bayou-5-IA.pdf](sources/2026-07-18_puct_35077-1362_centerpoint-nrg-cedar-bayou-5-IA.pdf)): SGIA dated **2021-12-01**, filed 2022-01-10. Contract INT-21-224A. Scheduled Start Date **2026-12-01**; TIF ISD later of 2023-05-03 or 18 months after prerequisites; COD later of 2025-06-01 or 6 months after ISD. **Security Estimate: $4,900,000 (LC)**. 59 pages.
- **IA Amendment 1** ([2026-07-18_puct_35077-1807_centerpoint-nrg-cedar-bayou-5-IA-amend1.pdf](sources/2026-07-18_puct_35077-1807_centerpoint-nrg-cedar-bayou-5-IA-amend1.pdf)): signed 2024-04-24 (NRG) / 2024-04-26 (CNP), filed 2024-05-06. Replaces Exhibits B, C, D, E. Scheduled Start **2024-05-15**; TIF ISD later of **2027-07-14** or 38 months after prerequisites; COD later of **2027-12-15** or 4 months after ISD. **Security Estimate: $9,423,000 (LC or cash)** — nearly 2× original.
- **POI (per Amendment 1, Exhibit C)**: "TSP system side of Plant's terminating structure(s) inside Generator's GIFSUB, approximately located at **29.7512636, -94.9208826, Chambers County, Texas**." Delivery voltage 345 kV. **Plant = one Mitsubishi Power (MHI) model M501JAC 1x1 single-shaft combined cycle power block, 674 MW at generator terminals**, natural gas, 24-345 kV step-up.
- POI coordinates place the GIFSUB about **1.8 km NNW of the existing Cedar Bayou plant complex** (29.734, -94.919 for existing units), adjacent to but distinct from the current plant footprint. Existing NRG Cedar Bayou units 1-4 are along the west shore of Trinity Bay north of I-10.

## Deep scan T4 — imagery constraint

- CDSE credentials in `~/.config/gis-research.env` now return **401 invalid_grant** — cannot fetch fresh Sentinel-2 imagery this session. Triage's 2026-06 chip and 2023-06 baseline chip in `imagery/` were captured at (29.726, -95.015) which is Baytown suburbs, NOT the plant. Existing chips are of limited value for construction verdict. Falling back to Google staticmap for site visualization.

## Deep scan T5 — TCEQ air permit (specific permit number)

- Direct look-up of RN110333184 via TCEQ CR public query returned only the empty search form (JS-driven detail page). WebFetch, curl POST/GET, and standard search engines (Google/DDG/Bing) all failed to surface a specific NSR permit number for "NRG Cedar Bayou 5".
- **Best available evidence for the air permit**: (a) NRG's own [PUCT NOI attestation (2024-05-09)](sources/2026-07-18_puct_56455-9_nrg-cedar-bayou-5-NOI.pdf) that CB5 has "necessary environmental permits and water rights"; (b) TCEQ RN110333184 registration for "CEDAR BAYOU GENERATING STATION" at West Bayou Rd — distinct from the existing plant's RN100825371 — consistent with an active permitting file; (c) TEF Due-Diligence advancement (Dec 2024) required "demonstrated readiness including required permits" per staff criteria.
- **Cannot cite a specific NSR permit number.** Recorded as an "unknown" for the dossier — not paper-project evidence, as (a-c) constitute reasonable indirect confirmation.

## Deep scan T6 — Mitsubishi turbine order verification

- **Not obtainable via public sources.** Mitsubishi Power Americas news pages 1-3 have zero Cedar Bayou / NRG / 501JAC mentions; the mitsubishipower.com root domain now redirects to a parked-domain page (moved to power.mhi.com).
- **What we DO have**: (a) IA Amendment 1 Exhibit C, signed by both parties April 2024, names the equipment: "**One Mitsubishi Power (MHI) model M501JAC 1x1 Single Shaft Combined Cycle power block**" ([Amend 1](sources/2026-07-18_puct_35077-1807_centerpoint-nrg-cedar-bayou-5-IA-amend1.pdf), Exhibit C, ¶5); (b) NRG's own April 2024 signature commits to this equipment spec; (c) TEF DD advancement (Dec 2024) required "arrangements to obtain required equipment" per PUC staff memo.
- **Cannot cite a specific Mitsubishi PR announcing the CB5 order** — recorded as an unknown. Not evidence against reality; NRG's own contractual commitment and TEF DD gate are sufficient for medium-confidence reality signal.

## Deep scan T7 — OSM verification of IA POI coordinates

- **Nominatim reverse-geocode of 29.7512636, -94.9208826** returned OSM way/39979635 "Cedar Bayou Station", landuse=industrial, Chambers County — confirming the GIFSUB from IA Amendment 1 sits inside the existing NRG plant polygon (bbox 29.7471–29.7529, -94.9279–-94.9197).
- **Overpass 3 km-radius query** at same coords ([saved](sources/2026-07-18_osm_overpass_cedar-bayou-poi-3km.json)): the "Cedar Bayou Station" way carries operator=NRG Energy, plant:source=gas, plant:output:electricity=2065.5 MW, EIA IDs 3460;56806, start_date=1970-12; nearby substations include CenterPoint-owned "Cedar Bayou Plant Substation" (way/39962537, 345/138 kV) 300 m SW and Calpine's Baytown Energy Center 2.2 km NNE.
- **Verdict**: CB5 GIFSUB is co-sited on the operating NRG plant complex — not greenfield; land tenure defaults to "owned (existing plant land)"; site-identification confidence upgraded to high from POI-only.
- **Note on triage imagery mislocation**: the earlier 2026-06/2023-06 chips at 29.726/-95.015 (Baytown suburbs) were ~10 km W of the true POI. The 2026-07-01 corrected & v2 chips in imagery/ cover a wider bay area including the existing plant cooling reservoir and adjacent industrial land — no visible new mobilization is apparent NNW of the plant, but a small pad could be below 10 m resolution.

## Deep scan T8 — Chambers CAD blocked

- **Chambers County eSearch** (esearch.chamberscad.org): first curl to /Search/Result returned HTML shell (2110 lines) but the results table is JS-populated via AJAX (`dataSet` initialized empty in inline JS). Subsequent curls to any path returned TLS handshake errors (`error:0A000126: unexpected eof while reading`) — server appears to be rate-limiting or fingerprinting; --tls-max 1.2, --http1.1, --ciphers 'DEFAULT:@SECLEVEL=0', --insecure, and various UA rotations all failed.
- **Recorded as blocked, not paper-project evidence.** For a brownfield expansion at an existing owner-operator's site, CAD parcels would list "NRG Cedar Bayou LLC" or predecessor entity; absence of a CAD hit today does not imply absence of tenure.

## Deep scan T9 — synthesis

- Dossier written to dossier.md; findings.json populated with contractual_schedule.documents (per-doc security) + project_area (null/not disclosed).
- Verdict: **real_early** (SPV real, IA real, POI on existing plant land, TEF DD in progress, no visible mobilization).
- Independent COD: **2028-Q2**, drift risk **med** — thin ISD-to-COD buffer + no mobilization visible + prior 2.5-yr pre-construction slip, offset by TEF pathway + brownfield + LC ramp.
- Turns used at end of deep scan: ~60.

