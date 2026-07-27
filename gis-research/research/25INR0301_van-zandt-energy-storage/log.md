# Triage log — 25INR0301 Van Zandt Energy Storage

## T1 start
- Script: queue_history.py → 37 snapshots (2023-06-01 → 2026-06-01)
- FIS approved: 2024-11-18
- IA signed: 2025-03-03 (first appeared 2026-03-01 report)
- Construction milestones: NONE achieved
- COD drift: 4 changes — 2025-04-29 → 2026-09-25 → 2027-04-13 → 2028-04-13 → 2027-05-15 (current)
- Capacity: 251.5 → 256.58 → 256.0 MW (current)
- Zone: WEST; County: Ector, TX; POI: 1027 Odessa EHV Switch 138 kV

## T2 start
- gmaps.py: HTTP 429 on first call, 429 on retry → no pins found (rate-limited)
- Queries attempted: "Van Zandt Energy Storage", "Van Zandt Energy Storage Ector County"
- Result: 0 pins

## T3 start
- Developer identified: Rocky Mountain Energy Holdings, LLC
- SPV confirmed: Van Zandt Energy Storage LLC
- PUCT filing found: PUC control no. 35077 (IA with Oncor Electric Delivery, filed 2025-03-31)
- Sources: ercotqueue.com (86% build-chance, IA+FIS complete), infrasure.ai, interconnection.fyi, cleanview.co
- No developer press release or portfolio info found
- TX SOS registration not surfaced via DDG

## T4 start
- PUCT Interchange portal: HTTP 402 on all endpoint attempts (filing/35077, search by party, search by description)
- Control 35077 confirmed by DDG T3 result: "Standard Generation Interconnection Agreement between Oncor Electric Delivery and Van Zandt Energy Storage LLC, filed 2025-03-31"
- IA existence confirmed via T1 queue data (iaSigned = 2025-03-03) and T3 web source
- Unable to retrieve IA PDF or milestone schedule exhibit — blocked by portal auth
- Result: IA confirmed via queue + web, PDF not retrieved

## T5 start
- TX Comptroller Ch.313 search: JS-rendered, not accessible via WebFetch (returns blank form only)
- JETI registry: 404 at gov.texas.gov/business/page/jeti
- DDG abatement search: CAPTCHA block, no results
- 25INR0301 entered queue 2023-06 (post-2022 Ch.313 expiry) — no Ch.313 expected
- JETI is early-stage; no hit is normal for a project that just signed IA in 2025
- Result: no abatement found (normal)

## T6 start
- POI: "1027 Odessa EHV Switch 138 kV" — substation coordinates not resolved
- Sources tried: OSM Nominatim, Oncor website, ERCOT bus/node files (404), OpenInfraMap (JS wall), DDG (CAPTCHA)
- Only available proxy: Odessa city center (~31.845N, 102.367W) — too coarse for 10-80 acre battery pad
- Decision: SKIP imagery per checklist rule ("nothing better than somewhere in the county")
- site_candidate: null

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP

## Deep scan start — 2026-07-19 (first run — hit max turns without writing deliverables)

### Stage 1 — LLC/developer parent chain
- TX Comptroller franchise tax API found TWO entries for Rocky Mountain Energy Holdings, LLC:
  - taxpayerId 32092185100, ZIP 55401 (Minneapolis, MN)
  - taxpayerId 32095432582, ZIP 75201 (Dallas, TX)
- TX Comptroller franchise tax API found Van Zandt Energy Storage LLC:
  - taxpayerId 32092196594, ZIP 80302 (Boulder, CO)
  - taxpayerId 32099675848, ZIP 80302 (Boulder, CO) — likely registered twice
- Boulder CO 80302 = downtown Boulder; suggests developer is a Boulder-based company
- Minneapolis 55401 = downtown Minneapolis; a known clean energy hub (Xcel HQ, many developers)
- No website found for Rocky Mountain Energy Holdings (domain parked/for sale)
- No press releases found via PR Newswire or Business Wire
- No SEC EDGAR filings found (403 on API)
- Colorado SOS search blocked (403)
- TX SOS is paid-access only (SOSDirect)

### Stage 2 — County records sweep
- Ector CAD (ectorcad.org): Owner name search requires JS rendering; WebFetch returns empty results for both "Rocky Mountain Energy Holdings" and "Van Zandt Energy Storage"
- PUCT Interchange portal: Returns HTTP 402 on all document/search endpoints (authentication required)
- PUCT control 35077 = "Standard Generation Interconnection Agreement between Oncor Electric Delivery and Van Zandt Energy Storage LLC, filed 2025-03-31" — CONFIRMED via queue data (iaSigned=2025-03-03) and triage web sources; PDF not retrievable
- No JETI or Ch.313 abatement found (post-2022 entry, expected for BESS at this stage)

### Stage 2 — TPIT (Transmission Project Information Tracking)
- Downloaded ERCOT TPIT 2026-07-17 (560KB xlsx from ercot.com/gridinfo/planning)
- CONFIRMED: Odessa EHV Switch = bus 1027 (138kV), Ector County, Oncor
  - TPIT project 93466: "Rebuild Odessa EHV – Reiter 138 kV Double Circuit Line", Ector County, bus 1027
  - TPIT project 71182: "Reiter 345/138 kV Switch [at] Odessa EHV → Wolf/Moss", Ector County, planned 2026-12-01
  - TPIT project 81240: "Consavvy – Odessa EHV 345 kV Double Circuit Line Rebuild", Midland→Ector County
  - TPIT project 81383: "Edwards Tap – Sandhills Tap 138 kV Line Rebuild" [from] Odessa EHV → Wolf (In-Service 2025-07-24)
  - RTP entry: "2022-FW14 Odessa EHV Switch – Rexall – General Tire Switch – Southwestern Portland Tap – Edwards Tap – Judkins – Sandhills Tap – Wolf Switching Station 138-kV Line Upgrade, Oncor 2024"
- Alder 138kV Switch establishment (TPIT 91945) in Van Zandt county – DIFFERENT Van Zandt! Not the same as this project.
- OSM: No "Odessa EHV Switch" named node found; likely = "Moss Substation" (31.81327, -102.49554, Oncor 345/138/13.2kV)
  - Moss Substation is the only Oncor 345+138kV facility in Ector County visible in OSM
  - TPIT project 71182 "from Odessa EHV to Wolf/Moss" implies they may be co-located or the new 345/138kV Reiter switch is being built AT or adjacent to Moss
  - Alternative: Odessa EHV is at a different location not in OSM; the site could be within ~5km of Moss


### Stage 3 — Site pinpoint (second run, 2026-07-19)
- Google Maps Places API: HTTP 403 error (API key rate-limited or disabled)
- Tried OSM Overpass for Ector County substations: HTTP 406 (all mirrors)
- HIFLD Electric Substations API: "Invalid URL" errors (wrong service endpoint)
- FERC eLibrary: JS wall (no results)
- ERCOT bus coordinate files: 404 (not public)
- Best proxy: OSM Moss Substation at 31.81327°N, -102.49554°W
  - This is at middle of dense residential Odessa — wrong location for BESS
- HIFLD, FERC OASIS, Nominatim, EIA 860/861: all blocked or returned no Odessa EHV data
- CONCLUSION: site not locatable; proxy rejected per playbook "no county centroid" rule
  (Moss Sub may not be Odessa EHV Switch; TPIT shows these are distinct facilities)

### Stage 4 — Imagery
- Chip 1: 1km around OSM Moss Sub (31.81327, -102.49554) — dense residential Odessa
  Artifact: imagery/s2_2026-07-01_poi_1km.png
- Chip 2: 3km around OSM Moss Sub — still dense residential; no BESS signatures
  Artifact: imagery/s2_2026-07-01_poi_3km.png  
- Chip 3: SW Odessa (31.820, -102.420) — I-20 corridor; residential + sparse industrial
  Artifact: imagery/s2_2026-07-01_sw_odessa_3km.png
- Chip 4: West Odessa (31.850, -102.490) — residential urban core
  Artifact: imagery/s2_2026-07-01_westodessa_3km.png
- VERDICT: imagery inconclusive — substation not located, chips show wrong area
- NO BESS pad found at any tried location

### Stage 5 — Synthesis (2026-07-19)
- findings.json written: verdict=real_early, COD=2028-Q2, drift=high
- dossier.md written following DOSSIER_TEMPLATE.md
- Key rationale: IA confirmed, financial security not posted (Jun 2026), no developer track
  record, no construction evidence — real but pre-NTP
- PUCT IA PDF: blocked (JS wall on all PUCT Interchange endpoints)
- Developer: Rocky Mountain Energy Holdings (TX franchise tax ZIP 55401 + 75201)
  SPV: Van Zandt Energy Storage LLC (TX franchise tax ZIP 80302 Boulder CO)
- TPIT XLSX saved as source artifact confirming Odessa EHV = bus 1027, 138kV, Ector/Oncor
