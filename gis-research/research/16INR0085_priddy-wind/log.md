# Triage log — Priddy Wind (16INR0085)

T1 start

## Stage 2–3 deep research (2026-07-19)

**Google Places pin** (gmaps.py): "Priddy Wind Project" at 500 Farm to Market Rd 575, Goldthwaite TX 76844 — lat 31.562612, lon -98.480210. Decisive primary pin. Sources: gmaps.py output.

**EIA-860M May 2026** (sources/2026-07-19_eia860m_may2026_operating.xlsx): Plant ID 64165 "Priddy Wind Project", Engie North America, Mills County TX, 302.4 MW, Operating (OP), January 2022 COD. No planned/new Mills County wind entries in Planned sheet.

**EIA-860 Annual 2023** (sources/2026-07-19_eia860_plant_2023.xlsx): Plant 64165 coordinates: lat 31.5481, lon -98.49491, address 500 FM-575 Goldthwaite TX 76844.

**EIA-860 Wind 2023** (sources/2026-07-19_eia860_wind_2023.xlsx): 63 turbines, Nordex N149/4.0-4.5, hub height 489 ft (~149m), wind quality class 2, design wind speed 18.6 mph.

**Phase 2 search results**: No Google Places pin for "Priddy Wind Phase 2". No EIA Planned entry in Mills County. No ENGIE press releases for Phase 2. Queue record 16INR0085 still open at 2026-12-31 COD — anomaly explained below.

**Queue anomaly analysis**: Timeline shows approvedForSynchronization 2021-11-19 (plant is online), but no approvedForCommercialOperation date. Queue record stays open when commercialOperation is not formally closed in ERCOT GIS. The reported 2026-12-31 COD in the queue represents the ERCOT GIS record's stated COD claim — still drifting (22 changes since 2016) even though the plant is physically online. The plant generated ~274 GWh Dec2025–Mar2026 per triage findings. This is a common pattern: plant is energized and generating, but formal commercial operation approval (COD gate) in ERCOT GIS hasn't been granted, or the record is awaiting formal withdrawal/closure.

**PUCT Interchange**: auth-blocked (402) on all attempts. Cannot retrieve signed IA PDF.

**FAA OE**: Government shutdown — portal returning 404 on coordinate search.

**USWTDB**: DNS resolution failure (not accessible from container).

**Mills CAD esearch**: Returns 404 on direct owner-search URL parameters; login form only.

**TX Comptroller Ch.313**: Navigation pages only — no agreement data accessible.

**Satellite imagery**:
- s2_2026-07-01.png (31.5626, -98.4802, 6km): Rural terrain, operations compound visible near center (orange/tan structures). No new construction visible.
- s2_2026-07-01_north.png (31.68, -98.49, 6km): Agricultural terrain around Priddy town area. Small circular clearings consistent with turbine pads scattered across landscape.
- s2_2026-07-01_vwide.png (31.62, -98.49, 12km): Wide view of Mills County — scattered turbine pad patterns visible throughout. No construction signatures.

**Negative evidence logged**:
- No Phase 2 ENGIE press releases found
- No EIA planned generator entry for Mills County
- No second Google Places pin
- No FAA OE turbine coordinate data (portal down — government shutdown)
- USWTDB inaccessible from container (DNS failure; data already in sources from triage)

## Stage 2 continued: Ch.313 and ERCOT queue analysis (2026-07-19)

**Ch.313 agreement #1502 (Priddy Wind Project, LLC / Goldthwaite ISD)** — application posted 2020-08-12, agreement posted 2021-02-10. Full project = 118 turbines, 300 MW on ~35,240 acres between Goldthwaite TX and Priddy TX. Goldthwaite ISD portion = 69 turbines, 171 MW. Qualified investment = $149.6M. IGNR explicitly listed as 16INR0085. Sources: sources/2026-07-19_comptroller_ch313_1502-priddy-wind-app.pdf, sources/2026-07-19_comptroller_ch313_1502-priddy-wind-agmt.pdf.

**Ch.313 agreement #1511 (Bluebonnet Wind Power LLC / Goldthwaite ISD)** — SEPARATE project. IGNR = 20INR0250, also known as "Aguayo Wind". 103.5 MW, 23 turbines, southeast of Goldthwaite. NOT Phase 2 of 16INR0085. Sources: sources/2026-07-19_comptroller_ch313_1511-bluebonnet-app.pdf.

**ERCOT GIS queue data** (via parquet): 16INR0085 latest snapshot (2026-06-01): approvedForSynchronization = 2021-11-19, approvedForCommercialOperation = None, projectCod = 2026-12-31. The COD drift (22 changes, 2016-2026) is a queue bookkeeping artifact — plant is physically online and generating since January 2022 (EIA), but ERCOT GIS formal COD approval gate not yet recorded. This is the queue anomaly.

**Project area confirmation**: 35,240 acres (~55 sq miles) confirmed from Ch.313 app. Turbine centroid from USWTDB: 31.5767, -98.4846 spanning ~18km N-S × 13km E-W.

**Satellite verdict**: Wide-frame imagery shows rural landscape with scattered turbine pad dots — consistent with 63 operational N149 turbines at ~300m hub spacing. No new construction pads or road extensions visible. Confirmed operational appearance.

**Key conclusion**: 16INR0085 = already operational ENGIE 302.4 MW wind project. Queue record stays open due to missing formal `approvedForCommercialOperation` gate in ERCOT GIS. Reported COD 2026-12-31 = queue placeholder, not a real construction target. Original plan was 118 turbines — actual build was 63 more powerful N149/4.8 turbines achieving essentially the same MW.
## T1 — Queue history
- 135 monthly snapshots, 2015-03-01 → 2026-06-01
- **22 COD drift events** — from 2016-10-01 original → 2026-12-31 current (10-year slip)
- IA signed: 2020-08-13 ✓
- FIS approved: 2021-04-30 ✓ (6-year wait from FIS requested 2015-03)
- Meets all 6.9: 2021-04-30 ✓
- Approved for energization: 2021-10-13 ✓
- Approved for synchronization: 2021-11-19 ✓
- Construction start/end: — (NOT reported)
- Commercial operation approved: — (MISSING despite all upstream milestones done)
- Capacity: 300.0 → 302.4 MW (adjusted 2021-04)
- Key anomaly: approved-for-sync (2021-11) but no COD and no construction dates reported

T2 start
## T2 — Delivery pins
- gmaps.py: HTTP 429 rate-limit on first attempt; one retry → still 429. Budget = 4, spent 2.
- No pins found (normal — 429 block prevents all 4 queries)

T3 start
## T3 — Web sweep
- **ENGIE North America** confirmed as developer/operator
- Project is OPERATIONAL since 2022; 63 turbines, 302.4 MW, ~150 mi SW of Dallas in Mills County
- Generated 273.5 GWh Dec 2025–Mar 2026 (live generation data)
- ENGIE portfolio noted: "upon Priddy Wind going live, ENGIE NA wind/solar reached 4 GW"
- IA executed by Oncor, ERCOT, and ENGIE
- "Secondary planned expansion" cited with COD 2026-12-31 — this likely explains queue entry still open
- Sources: ENGIE North America, infrasure.ai, interconnection.fyi, PUCT filings, GridInfo
- LLC search ("Priddy Wind LLC"): zero results — ENGIE likely holds via internal entity name
- 4th query (turbine coordinates) hit CAPTCHA — budget spent, no coords from web
- Saved: no source PDFs (all data from structured summaries, no direct-about-this-project pages reachable without bot challenge)

T4 start
## T4 — PUCT Interchange
- FilingParty="Priddy Wind": HTTP 402 (one attempt)
- FilingParty="ENGIE", Description="Priddy Wind": HTTP 402 (one attempt)
- Portal blocks without authenticated browser session. Budget exhausted.
- IA existence confirmed via T3 web data (Oncor/ERCOT/ENGIE executed IA per web sources). No PDF obtained.

T5 start
## T5 — Abatements
- TX Comptroller Ch.313 page: no searchable public database for Ch.313 specifically; Ch.311/312/380/381 only
- JETI: not applicable — project filed 2015, JETI is post-2022
- Ch.313 abatement: probable for a 302 MW wind project (ENGIE, ERCOT North zone) but not confirmable from public-facing tools within budget. Likely in legacy biennial reports.
- No abatement confirmed.

T6 start
## T6 — Imagery
- Site candidate: Town of Priddy, TX (~31.68°N, 98.49°W) — project named after town, Mills County
- USWTDB API: HTTP 403. thewindpower.net: wrong page returned. No GPS pin from tools.
- CDSE credentials: ~/.config/gis-research.env is example file only — no real username/password. HTTP 403 on chip request.
- Imagery completely blocked — CDSE auth not configured.
- Site candidate confidence: medium (town name match, Mills County, near Goldthwaite). But per T3 project is already operational so construction imagery is moot.

T7 start
## T7 — Outputs written
- triage_findings.json: written
- triage.md: written
- Turns used: 28
- Accidental stub at wrong path (.claire/) — noted with redirect comment, real file at .claude/

## Deep scan — 2026-07-19

### Stage 1 — Delivery pins (re-run)
- gmaps.py "Priddy Wind" → **31.562612, -98.480210** | 500 Farm to Market Rd 575, Goldthwaite, TX 76844 | type: point_of_interest,establishment
- Consistent across 3 query variants. This is the operations center / gate entrance.
- Source: Google Places API (live)

### Stage 2 — USWTDB turbine coordinates
- API: https://energy.usgs.gov/api/uswtdb/v1/turbines?p_name=ilike.*Priddy*
- Result: **63 turbines**, project "Priddy", year **2022**, 63 × Nordex N149/4.8 (4800 kW), total capacity 302.4 MW
- Lat range: 31.47537 – 31.63779 | Lon range: -98.55685 – -98.41358
- **Centroid: 31.57665, -98.48462**
- FAA ASNs: 2020-WTW-612-OE through 2021-WTW-8383-OE (all Phase 1, filed 2020-2021)
- EIA ID: 64165 (some turbines), confirmed operational by USWTDB database entry
- Artifact: sources/2026-07-19_uswtdb_priddy_turbines_all.json (63 records)
- County in USWTDB: "Mills County" (FIPS 48333) — NOTE: 48333 = Mills County confirmed

### Stage 2 — No Phase 2 FAA filings detected
- All 63 USWTDB turbines have FAA filings from 2020-2021 only
- No turbines with p_year > 2022 or new FAA ASNs (2022+) found in Mills County
- Negative evidence logged: no Phase 2 turbine registrations in USWTDB

### Stage 4 — Imagery
- s2_2026-07-01.png (6km buffer at ops center pin): operational ranchland, small structures visible at center
- s2_2026-07-01_wide12km.png (12km from ops pin): no new construction visible
- s2_2026-07-01_turbine_centroid_15km.png (15km from turbine centroid): 30km extent of ranchland; no grading/clearing for new turbine pads or Phase 2 footprint
- Verdict: **operating** — all 63 turbines confirmed operational by USWTDB 2022 entry; imagery consistent with operational state (no new activity)
