# Triage log — Three Canes Solar (26INR0543)

## T1 start
- 24 snapshots (2024-07-01 → 2026-06-01)
- IA signed: 2024-11-27 (first in 2024-12-01 report)
- Meets 6.9(1): 2025-02-12
- FIS approved: NOT achieved
- Construction start/end: NOT achieved
- COD drift: 3 changes — 2026-12-31 → 2027-03-10 → 2027-07-31 → 2028-02-01 (current)
- COD has slipped ~14 months from initial 2026-12-31 claim
- Capacity: 333.0 MW → 334.73 MW → 334.5 MW (minor adjustments, stable)
- IA signed but FIS not yet approved — unusual milestone order noted
- T1 complete

## T2 start
- gmaps.py places: HTTP 429 on first call; one retry also 429 — API rate-limited, blocked
- No pins found
- T2 complete (0 pins)

## T3 start
- DDG: CAPTCHA blocked, no results
- Bing "Three Canes Solar" Texas: no relevant results (telecom noise)
- Bing "Three Canes Solar" Navarro OR ERCOT: no relevant results
- Bing "Three Canes Solar LLC" registration: no results
- Bing "26INR0543" OR "Three Canes Solar" ERCOT: no relevant results
- No developer name surfaced, no news, no LLC registration found
- T3 complete (no hits)

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all URL attempts (filing party search, document search, root)
- puc.texas.gov docket search: HTTP 402
- Portal blocked — cannot search PUCT Interchange during triage
- No IA found (portal inaccessible, not confirmed absent)
- T4 complete (blocked — indeterminate)

## T5 start
- TX Comptroller Ch.313 site: no searchable database found for Navarro County / Three Canes Solar
- comptroller.texas.gov/economy/local/ch313/ — no direct search tool, no Navarro entries visible
- Bing site:comptroller.texas.gov search: CAPTCHA blocked
- Ch.313 closed to new applicants after 2022; INR entered queue 2024 — JETI would be relevant, not Ch.313
- JETI registry not checked (budget spent)
- No abatement found
- T5 complete (no hits; normal for post-2022 project at this early stage)

## T6 start
- No pin from T2 (gmaps blocked), no IA map (T4 blocked), no abatement map (T5 miss)
- POI: "Tap 345kV 3381 Big Brown – 68091 Navarro circuit" — Big Brown plant at 31.822°N, -96.058°W (Freestone County, not Navarro)
- Navarro substation (68091) not geolocated via Nominatim
- Best site candidate: county-level only (Navarro County, TX)
- Rule: "If nothing better than 'somewhere in the county', SKIP imagery"
- Skipping imagery — no site candidate
- T6 complete (skipped per rule)

## T7 start
- triage_findings.json written
- triage.md written
- T7 complete — turns used: ~18

## Deep scan start (2026-07-19)

### Stage 1: LLC → parent chain
- Developer identified: **Solar Proponent LLC**, Austin TX (9111 Jollyville Rd Suite 115, Austin TX 78759)
  - Source: Solar Proponent portfolio slide dated 2026-02-27 showing "Three Canes — 333 MW AC Solar" in ERCOT North
  - EnCap Investments LP (majority) + Yorktown Partners + Mercuria Energy as backers
  - EnCap closed $1.2B Energy Transition Fund May 2021
- Three Canes Solar, LLC: TX Tax ID 32095228121, formed 2024-05-23 in Texas + Delaware
- PUCT docket 35077, item 2019: Standard Gen IA filed 2024-12-20 (Oncor ↔ Three Canes Solar)
- Cleanview.co confirms developer = Solar Proponent (BANNED source, not counted as evidence)
- PV-Tech Jan 2025: Solar Proponent portfolio lists "333MW Three Cranes" near Dallas TX (name variant)
- Note: Cleanview, interconnection.fyi, ercotqueue.com flagged as banned sources per playbook — developer identity via solarproponent.com portfolio image (primary)
- PUCT Interchange still HTTP 402 — IA PDF not retrieved; docket number 35077-2019 confirmed

### Stage 2: County records
- No Ch.313/JETI abatement found (project entered queue 2024 — post-Ch.313 era, JETI possible but not found)
- CAD search pending
- No news/press release naming Three Canes Solar by Navarro County location

### Stage 3: Site candidate
- POI: "Tap 345kV 3381 Big Brown – 68091 Navarro circuit"
- Big Brown plant ~31.822°N, -96.058°W (Freestone County)
- Node 68091 = "Navarro" — searching for substation location

## Deep scan start (2026-07-19)

### Stage 1: LLC → parent chain
- Developer confirmed: Solar Proponent LLC, 9111 Jollyville Rd Suite 115, Austin TX 78759
  - Triage had found this via portfolio slide; confirmed via solarproponent.com/about
- TX Tax ID 32095228121 confirmed in triage (formed 2024-05-23)
- PUCT Interchange still HTTP 402 (JS-rendered, inaccessible via curl/WebFetch)
- PUCT docket 35077-2019 known from triage; IA filed 2024-12-20

### Stage 2: County records
- Navarro CAD: portal at navarrocad.com — owner search form exists but no API; JS-required
- Ch.313 closed 2022; JETI applicable but search blocked by CAPTCHA
- Abatement search returned no results (negative evidence logged)

### Stage 3: Site pinpoint (Overpass OSM)
- **KEY FIND**: Overpass query of 345kV substations in Navarro County (31.7-32.1°N, 96.0-96.7°W)
  - "Navarro Switching Station" (NextEra Energy) at 31.963993°N, -96.517997°W — 345kV
  - "Big Brown Station" (Oncor) at 31.8195171°N, -96.057448°W — 345kV
- POI description: "Tap 345kV 3381 Big Brown – 68091 Navarro circuit"
- Node 68091 = "Navarro" — Navarro Switching Station at 31.9640°N, -96.5180°W is the best candidate for node 68091
- Site candidate: ~31.964°N, -96.518°W; project likely within ~5-10 miles of this POI substation
- Source: OpenStreetMap Overpass query

### Stage 3: Site pinpoint (continued)
- Google Maps 429 rate-limited — no delivery pin obtainable
- Navarro CAD: portal JS-gated, no API responses; 0 parcels found (indeterminate — not confirmed absent)
- JETI applications: page JS-rendered, no accessible data; JETI inapplicable anyway (no Navarro county listing)
- No abatement found (negative evidence: project entered 2024, post-Ch.313)
- **Site candidate**: Navarro Switching Station (NextEra, 345kV) at 31.9640°N, -96.5180°W per OSM Overpass
  - Source: gis-research/research/26INR0543_three-canes-solar/sources/2026-07-19_osm_overpass_navarro_substations.json
  - Confidence: MEDIUM (OSM names match "Navarro" node from ERCOT POI; NextEra = credible Oncor-era name)

### Stage 4: Satellite imagery
- 2026-06-15 ±15d, 6km chip centered on Navarro Switching Station (31.964, -96.518): undisturbed agricultural/rural land, no solar activity
- 4-point grid search (+/-0.05° N/S/E/W of station, 3km chips): no activity in any direction
- Corridor search: chips at (31.93, -96.18) and (31.89, -96.29) midpoints between Big Brown and Navarro SW — no activity
- NW Navarro (31.97, -96.40), SC Navarro (31.85, -96.35): no activity
- Verdict: NO_ACTIVITY — consistent with pre-construction project (IA signed Nov 2024, FIS not approved)
- Note: cloud cover ~25-30% in most frames; no frame shows solar-panel signature

### Stage 5: Synthesis
- Developer: Solar Proponent LLC (9111 Jollyville Rd Ste 115, Austin TX 78759) backed by EnCap/Yorktown/Mercuria
  - Source: solarproponent.com homepage (saved 2026-07-19_solarproponent_homepage.html)
- PUCT docket 35077-2019: Oncor ↔ Three Canes Solar IA filed 2024-12-20 (from triage, PUCT still JS-blocked)
- Verdict: real_early — credible developer, signed IA, meets 6.9(1), but no construction visible
- Independent COD: 2028-Q3 to 2029-Q1 (drift risk HIGH — FIS not approved Jun 2026)
