# Triage log — 27INR0313 Spindletop Solar

**Date:** 2026-07-18  
**Triage agent:** automated first pass

---

T1 start
## T1 result — queue history
- 24 monthly snapshots (2024-07-01 → 2026-06-01)
- IA signed: 2025-12-29 (in 2025-12-01 report)
- Meets 6.9(1): 2026-03-25 (in 2026-03-01 report)
- FIS approved: NOT achieved
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- COD drift: 4 changes — 2027-04-01 → 2027-06-30 → 2027-08-28 → 2027-06-30 → 2027-12-29 (current)
- Total drift: +9 months from first reported COD
- Capacity: minor changes (286.3 → 286.04 → 286.4 MW)

T2 start
## T2 result — delivery pins
- gmaps.py places: HTTP 429 Too Many Requests on both attempts (exact name + county variant)
- Budget exhausted; no pins obtained
- Result: 0 pins found

T3 start
## T3 result — web sweep
- DDG HTML search: CAPTCHA block on all attempts, no results returned
- Bing HTML search: returned unrelated pages (Roblox dev forum, CT post office), no solar results
- Texas SOS: redirected, session-based form — not fetchable without interactive session
- No developer name, news, or LLC registration surfaced
- Result: news_found = false

T4 start
## T4 result — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all URL patterns (/, /Documents/search, /Search/Filings)
- No puct_search.py script available in research_tools
- Budget exhausted after ONE retry pattern — portal fully blocked
- Result: ia_found = false (cannot confirm via PUCT; IA signed date IS present in queue data from T1: 2025-12-29)

T5 start
## T5 result — abatements
- Texas Comptroller Ch.313 page: search tool is form-based JavaScript; not directly URL-fetchable; no results list exposed
- JETI registry: URL pattern not known; attempted ercot.com doc lookup → 404
- Note: project is post-2022 (INR starts 27 = likely filed ~2024); Ch.313 expired 12/31/2022; JETI is the successor but no known list URL
- Result: abatement_found = false (normal for post-2022 project)

T6 start
## T6 result — imagery
- No delivery pins from T2 (rate-limited)
- No IA document from T4 (PUCT 402-blocked) — no map/exhibit available
- No abatement application from T5 — no map available
- POI: "Tap Stryker [3109] - Lufkin [3117] 345 kV line" — Nacogdoches County
  - Lufkin substation (node 3117): Angelina County ~31.35°N, 94.73°W (general knowledge, not verified)
  - Stryker substation (node 3109): location unknown; web searches blocked/unproductive
- Site resolution: county-level only — no better candidate
- Decision: SKIP imagery per checklist rule ("somewhere in the county" → skip)
- Result: construction_visible = false (imagery not run)

T7 start
## T7 result — outputs written
- triage_findings.json: written
- triage.md: written (10 lines)
- Turns used: ~22
- All steps completed T1→T7. Stopping.

---
## Deep scan start — 2026-07-19

### D1 — PUCT Interchange search
- URL: interchange.puc.texas.gov/Search/Filings?q=Spindletop+Solar
- Result: HTTP 402 (blocked, same as triage)
- URL: interchange.puc.texas.gov/Documents/search?q=Spindletop+Solar
- Result: HTTP 402
- Still fully blocked

### D2 — TX Comptroller entity search
- mycpa.cpa.state.tx.us redirect to comptroller.texas.gov/taxes/franchise/account-status/search
- Form-based, no URL-parameter search available; API needs auth
- Result: no entity data retrieved

### D3 — TX SOS entity search
- direct.sos.state.tx.us — requires paid account
- Result: no data retrieved

### D4 — SEC EDGAR
- sec.gov/cgi-bin/browse-edgar?company=spindletop+solar — HTTP 403
- efts.sec.gov searches — HTTP 403/403
- Result: no filings found

### D5 — Nacogdoches CAD
- nacad.org — 401; nacogdochescad.com — DNS fail; nacogdochescad.org — DNS fail
- propaccess.trueautomation.com cid=155 — session expired
- Result: CAD portal not accessible

### D6 — ERCOT bus/node data
- Multiple ERCOT URLs for BusGPS.xlsx, node lists — all 404
- Result: Stryker (3109) coordinates not obtained from ERCOT

### D7 — OSM Overpass for Stryker substation
- Overpass query for power substations named Stryker in Texas — empty result (0 elements)
- Lufkin power query — HTTP 429 rate limited
- Result: Stryker substation NOT in OSM

### D8 — Chapter 313 Comptroller
- comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs.php
- Page truncated before Nacogdoches entries; no Spindletop Solar found in visible portion
- Note: Ch.313 expired 12/31/2022; project INR 27INR0313 filed ~2024 — JETI is successor
- JETI registry: no searchable list found online
- Result: No abatement found (expected for post-2022 project)

### D9 — Nacogdoches County government
- nacogdochesco.gov — 404; co.nacogdoches.tx.us — redirects to new site under construction
- No commissioners court agendas accessible

### D10 — Local parquet deep-extract (KEY FINDINGS)
- interconnectingFacility = "Banita Creek Solar LLC" — actual entity name behind Spindletop Solar project
- financialSecurityAndNoticeToProceedProvided = "Yes" — financial security POSTED, strong real-project signal
- approvalDateForSubmissionOfProofOfSiteControl = 2024-07-16 — site control proven
- ginrStudyPhase = "SS Completed, FIS Started, IA"
- FIS still not approved but IA signed — unusual, implies FIS may be in progress/waived
- Banita Creek = real waterway in Nacogdoches County → geographic anchor for imagery search
- Source: local parquet gis-research/data/ercot_generation_interconnect.parquet

### D11 — Nominatim geographic anchors
- Banita Creek Park/Hall: 31.608°N, 94.657°W (city of Nacogdoches proper)
  - "Banita Creek Solar LLC" likely named after this waterway in Nacogdoches city
- Stryker Creek Junction: 31.889°N, 95.030°W — hamlet in Cherokee County
  - ERCOT node "Stryker [3109]" is likely a substation near this community
- Lufkin substation (node 3117): city of Lufkin, Angelina County ~31.34°N, 94.73°W
- Tap geometry: 345 kV line from Cherokee County (Stryker) → Angelina County (Lufkin)
  runs through/near Nacogdoches County → project site likely somewhere on this corridor
- Source: Nominatim/OSM query 2026-07-19

### D12 — Stryker substation/node geographic anchor (KEY)
- Nominatim: "Stryker Creek Power Plant" at 31.9410°N, 94.9913°W — Cherokee County, TX
- This is almost certainly ERCOT node "Stryker [3109]" — existing gas plant at that location
- Lufkin substation (3117): near Lufkin city, Angelina County ~31.34°N, 94.73°W
- 345 kV line Stryker→Lufkin runs ~NW-SE through Cherokee/Nacogdoches/Angelina counties
- Project "taps" this line (not at endpoints) — so site is somewhere ON the line, in Nacogdoches County
- Corridor midpoint estimate: ~31.65°N, 94.85°W (between 31.94 and 31.34 lat, -94.99 and -94.73 lon)
- Source: Nominatim/OSM query 2026-07-19

### D13 — Initial imagery grid (3 chips)
- 31.65N, 94.85W: forest/ag, no construction (s2_search_31.65_-94.85_2026-07-01.png)
- 31.78N, 94.98W: forest/ag with cloud, no construction (s2_search_31.78_-94.98_2026-07-01.png)
- 31.55N, 94.72W: forest/ag, no construction (s2_search_31.55_-94.72_2026-07-01.png)
- None of these 3 chips show solar activity

### D14 — Corridor grid imagery (7 chips, contact sheet)
- All 7 chips along estimated Stryker-Lufkin corridor: undisturbed forest/ag, no solar activity
- Chips: 31.46,-94.75; 31.55,-94.72; 31.58,-94.80; 31.65,-94.85; 31.72,-94.87; 31.78,-94.98; 31.85,-94.93
- No grading, no racking, no substation construction visible in any frame
- Interpretation: site is EITHER (a) pre-construction (no earth disturbance yet) OR (b) not on this corridor
- Note: IA signed 2025-12-29, financial security posted — land is controlled, but construction not yet started
- Construction start not reported in queue data (confirms no_activity expected for now)
- contact_sheet_search.png built from all 7 chips

### D15 — Active Nacogdoches project landscape
- 5 active solar/storage projects in Nacogdoches County in latest snapshot
- Timberline Renewables LLC: 2 projects (solar 201 MW + storage 100.5 MW), COD 2029-04
- Sunlit Pines Energy Center LLC + BESS LLC: 2 projects (207 + 208 MW), COD 2028-09 — no IA, no security
- Banita Creek Solar LLC (our subject): 286.4 MW, COD 2027-12, IA SIGNED, security POSTED
- Aypa Power: linked by DDG to "Sunlit Pines Solar" (27INR0226) via Nacogdoches Chamber listing, but NOT confirmed for Banita Creek/Spindletop
- Note: cleanview.co source for Aypa-Sunlit Pines link is BANNED — cannot rely on that claim
- Timberline Renewables, LLC: appears in 2 Nacogdoches projects — may be a relevant developer to investigate
- Source: local parquet, DDG search 2026-07-19

### D16 — Developer identity: Parliament Energy (KEY)
- Developer = Parliament Energy (operating as Banita Creek Solar LLC)
- IA signed December 26, 2025 between ONCOR Electric Delivery and Banita Creek Solar LLC
- PUCT filing submitted January 23, 2026
- Paired with Spindletop Storage (27INR0314) — solar + storage hybrid
- Transmission provider: Oncor (not AEP) — this means site is in Oncor territory
- Source: DDG web search result (text snippet from ercotqueue.com/other source) 2026-07-19
- WARNING: ercotqueue.com is a banned source; Parliament Energy identity needs independent verification
- Action: verify via PUCT filing search and direct Parliament Energy web search

### D17 — Parliament Energy confirmed as developer (KEY PRIMARY SOURCE)
- parliamentenergy.com explicitly lists "Banita Creek Solar" in portfolio
- Parent chain: Banita Creek Solar LLC → Parliament Energy → EnCap Investments + Mercuria Energy
- Parliament Energy backed by EnCap (major PE firm, oil/gas + renewables) and Mercuria (commodity trading)
- Portfolio: Parliament Solar (Waller County TX, 640MWdc, COMPLETED early 2025), Tehuacana Creek Solar, Rowdy Creek Solar, Banita Creek Solar, Hollow Branch Solar
- Flagship Parliament Solar ~88k homes demonstrates Parliament is a real, operational developer
- Source: parliamentenergy.com homepage 2026-07-19

### D18 — Spindletop Storage (27INR0314) CANCELLED
- 27INR0314 Spindletop Storage (142.57 MW BESS) — CANCELLED 2026-03-23
- FIS approved (2025-12-05), IA signed (2025-12-26), financial security posted — then cancelled
- Cancellation may indicate: design change (removing BESS portion), or separate IA process
- The solar 27INR0313 remains ACTIVE — not cancelled
- Combined site control approval dates: solar 2024-07-16, storage 2024-07-24 (very close)
- Source: local parquet 2026-07-19

### D19 — Project origin and location (CRITICAL FINDS)
- Parliament Energy purchased Banita Creek Solar from Solar Proponent (original developer)
- Solar Proponent leased ~7,200 acres near Alazan and Lake Nacogdoches in 2023
- 7,200 acres = confirmed project area (MUCH larger than the solar footprint alone — land envelope)
- Site located near Alazan, Nacogdoches County, TX and Lake Nacogdoches
- Alazan is a small community in NW Nacogdoches County near Lake Nacogdoches
- Parliament Energy described as "Houston-based utility-scale solar developer"
- PUCT filing 3/6/2026: interconnection agreements for "Parliament Energy (Banita Creek/Middlebrook Creek) Item 2375"
- Companion project: "Middlebrook Solar" (separate from Spindletop Storage)
- Local opposition coalition formed; town hall held
- Construction status: "in construction phase" per YouTube reporting (date unknown)
- Source: DDG search result (Daily Sentinel, PUC filings, YouTube) 2026-07-19

### D20 — Site location anchor: Alazan / Lake Nacogdoches
- Alazan community: approx 31.68°N, 94.72°W (NW Nacogdoches County near Lake Nacogdoches)
- Lake Nacogdoches: reservoir in NW Nacogdoches County, approx 31.70°N, 94.73°W
- THIS is a much better imagery target than the transmission line corridor guesses
- New imagery search: center chips on Alazan/Lake Nacogdoches area

### D21 — Construction confirmed ACTIVE; YouTube primary source
- Parliament Energy official YouTube video: "Parliament Energy - Banita Creek Solar Farm - Nacogdoches County, Texas"
- Video describes project as "a 286-megawatt industrial solar farm ALREADY IN THE CONSTRUCTION PHASE"
- This is primary evidence of active construction (pre-COD)
- Daily Sentinel: "Coalition forms over planned solar farm projects" — confirms community opposition
- Acquisition timeline: Solar Proponent → Parliament Energy, purchased late 2025
- Land: Solar Proponent leased ~7,200 acres near Alazan and Lake Nacogdoches in 2023
- Alazan hamlet: 31.583°N, 94.786°W (SW Nacogdoches County)
- Lake Nacogdoches: 31.621°N, 94.822°W
- Previous imagery grid was WRONG quadrant — need chips near 31.58°N, 94.79°W
- Source: DDG search result (Daily Sentinel + Parliament YouTube) 2026-07-19

### D22 — CONSTRUCTION CONFIRMED via Sentinel-2 imagery (KEY ARTIFACT)
- Chip s2_site_31.595_-94.772_2026-07-01.png: EXTENSIVE clearing/grading visible
- Large interconnected tan-brown polygons across most of frame = active solar site preparation
- Access roads visible connecting cleared areas; irregular boundaries consistent with parcel-following clearing
- Activity extends to all frame edges → site much larger than 2km chip (consistent with ~4 sq mi / 2,560 acres)
- Stage: clearing/grading — NOT yet racking (no dark uniform module rows visible)
- Construction in progress as of ~July 2026
- Site centroid estimate: ~31.595°N, 94.772°W (activity fills the frame)
- Source: Sentinel-2 chip 2026-07-01 ±15d, 2.0 km buffer, s2_site_31.595_-94.772_2026-07-01.png

### D23 — Parliament Energy website (primary source)
- URL: parliamentenergy.com/banita-creek
- Capacity: 371 MWdc / 285 MWac
- Expected completion: Q4 2027 (consistent with reported COD 2027-12-29)
- Site size: ~4 sq miles (~2,560 acres)
- Construction: ~18 months (implies start ~mid-2026 for Q4 2027 COD, or earlier)
- Battery storage removed (ERCOT and Oncor formally notified) — explains 27INR0314 cancellation
- Transmission: Oncor
- Partners: EnCap Investments LP + Mercuria Energy (backers)
- 0.6M solar panels, 428 miles of trackers/cable, 16 tons steel
- $500M+ private investment; $41M+ projected property taxes
- Source: parliamentenergy.com/banita-creek 2026-07-19

### D24 — Parliament Energy financing ($747M) — strong real-project signal
- Parliament Energy secured USD 747M non-recourse senior secured financing (Credit Agricole CIB)
- Named deal: Tehuacana Creek Solar, Texas (separate from Banita Creek)
- Structure: non-recourse project financing confirms debt underwriting and commercial viability
- EnCap Energy Transition Fund II + Mercuria Energy Group are co-founders of Parliament Energy
- Parliament building 2.7 GWdc portfolio of CONTRACTED utility-scale solar assets
- Banita Creek Solar is part of this contracted portfolio
- Source: LinkedIn/Credit Agricole CIB PR (via DDG) 2026-07-19

### D25 — Site imagery confirmation (xwide, 2026-07-01)
- s2_site_xwide_2026-07-01.png (6km buffer): ACTIVE CONSTRUCTION confirmed
- Clearing/grading visible across ~3-4km E-W extent centered ~31.595°N, 94.772°W
- Lake Nacogdoches visible upper-left confirming geography
- Two lobes of cleared land visible — consistent with multi-parcel site spanning 2,560 acres
- Stage: clearing/grading (pre-racking) as of July 2026
- Site centroid confirmed: ~31.595°N, 94.77°W method: imagery + geographic anchors (Alazan, Lake Nacogdoches)


---
## Stage 5 — Synthesis complete 2026-07-19

### S1 — Dossier, findings.json written
- dossier.md: written following DOSSIER_TEMPLATE.md
- findings.json: written in Hanson-schema format (real_project_verdict, cod_assessment, contractual_schedule with milestones as list)
- Verdict: real_active, COD 2027-Q4, drift risk medium

### S2 — Wrap-up commands
- queue_history.py: timeline.json + timeline.md regenerated (24 snapshots, 4 COD changes)
- build_brief.py: brief.html written (7KB, 1 image, 1 source)
- build_index.py: index.json + INDEX.md refreshed (76 projects)
