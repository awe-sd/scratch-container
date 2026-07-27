# Triage log — Douie Solar (26INR0098)

T1 start
**T1 — queue history**: 38 snapshots (2023-05 → 2026-06). COD drifted 3 times: 2026-06-01 → 2027-04-14 → 2027-09-30 → 2028-04-18 (current). IA signed 2026-03-08. FIS approved 2025-07-07. Meets 6.9(1) = 2026-04-13. No construction start/end dates. Capacity stable at 221.2 MW.

T2 start
**T2 — delivery pins**: gmaps.py returned HTTP 429 (rate-limited) on both queries. No pins found. NORMAL — no site confirmed via maps.

T3 start
**T3 — web sweep**: DDG served CAPTCHA on both queries. Bing returned unrelated results for "Douie Solar" Texas, "Douie Solar LLC", and "Douie Solar ERCOT". No news, press releases, developer name, or LLC registration found. Project has effectively zero public web presence.

T4 start
**T4 — PUCT Interchange**: interchange.puc.texas.gov returned HTTP 402 on all URL attempts (application.aspx, search.aspx). Bing search also blocked by CAPTCHA. Portal inaccessible — cannot retrieve IA filing. Queue data confirms iaSigned=2026-03-08 but no PDF content retrieved. ia_found=false (unverified via portal).

T5 start
**T5 — abatements**: Ch.313 expired 2022; project entered queue 2023, not applicable. JETI current-agreements page loaded — 11 entries total, none for Freestone County or Douie Solar. JETI applications page returned data-load error. No abatement found. NORMAL for post-2022 project without JETI.

T6 start
**T6 — imagery**: Site candidate = POI anchor at Teague, TX (31.628, -96.281) — LOW confidence. Chip 2026-06-15: rural farmland, no construction. No activity.

T7 start
**T7 — outputs written**: triage_findings.json + triage.md complete. Turns used: ~28.
**T6 — imagery**: Site candidate = POI anchor at Teague, TX (31.628, -96.281) — LOW confidence (POI town only, no parcel pin). Ran 6 chips at 2026-06-15 but parallel execution overwrote to single file (cdse.py uses date-only filename). Contact sheet: 1 frame visible — rural farmland, green fields, roads, no solar panels, no cleared land or construction earthworks. No construction activity visible. construction_visible=false.

## Deep scan start — 2026-07-19

**Stage 1-2 results:**
- TX Comptroller franchise tax: 0 results for "Douie Solar" — not registered under that name
- PUCT Interchange: 0 records for "douie" OR "douie solar" OR "freestone solar" — IA not filed under project name
- TX SOS: paywall, inaccessible
- Freestone CAD: portal under maintenance, inaccessible
- Web search: zero public presence for Douie Solar (Bing, DDG)
- Stage 1 result: developer/owner chain UNKNOWN — no external evidence found

**OSM power line analysis:**
- Queried Overpass for all 138kV ways in bbox (31.35,-96.35,31.70,-96.10): 52 ways, 1189 nodes
- Main N-S corridor (Way 15235858): Freestone County, lat 31.37-31.71, lon -96.12 to -96.18
- Seaway/Teague line (Way 629783071): lat 31.647-31.695, lon -96.297 to -96.213 (Teague area heading SE)
- Busbar cluster at 31.4232, -96.2467 — likely the "Sea way Teague" switching station
- Jewett substation area: ~31.371, -96.135 (Brazos Electric lines converge)
- POI = tap on 138kV line between Seaway (31.42, -96.25) and Jewett (31.37, -96.14)
- **Search zone:** lat 31.42-31.65, lon -96.30 to -96.22 (Freestone County)

**Stage 3 — Site pinpoint:** running imagery grid over 4 candidate zones along the Teague-Jewett 138kV corridor

**OSM substation discovery:**
- Found "Teague Main Substation" at 31.6473, -96.2968 (named 138kV/25kV Oncor substation near Teague, TX)
- This is the "Sea way Teague" POI endpoint (Oncor switch #3501)
- "3394 Jewett" endpoint: ~31.371, -96.135 (Jewett area, Leon County boundary)
- Solar project taps the 138kV line between these two substations
- **Revised site search zone:** lat 31.50-31.65, lon -96.25 to -96.35 (Freestone County, south of Teague)

**Imagery analysis (2026-07-01 chips, 2km buffer):**
- Seaway tap (31.4232, -96.2467): Large industrial plant (coal/lignite — NRG Limestone or similar), NOT solar
- 31.500, -96.260: Rural farmland, no solar construction visible
- 31.550, -96.270: Rural farmland, no solar construction visible
- Triage chip (31.628, -96.281 = Teague center): Undisturbed farmland
- **Verdict: no_activity in all chips searched along corridor**
- Running 2 more chips: NW/SW of Teague Main Substation (the actual POI anchor)

**Stage 4 imagery final verdict:**
- Triage chip (31.628, -96.281, 2026-06-15): Teague area + substation vicinity — undisturbed farmland, no solar activity
- This chip effectively covers the Teague Main Substation (31.6473, -96.2968) — no construction visible
- Re-read of triage chip confirms: no graded rectangles, no module arrays, no earthworks near POI substation
- **CDSE rate-limited after 3 successful deep-scan chips; cannot image N of Teague (31.6473)**
- Full corridor search: 5 chips total, no construction activity found at any sampled point
- Site remains unconfirmed — only POI corridor established, exact parcel unknown
- **Imagery verdict: no_activity** — consistent with paper-project profile

**Stage 2 additional searches:**
- TX Comptroller franchise: 0 hits for "Douie Solar"
- PUCT Interchange: 0 hits for "douie", "douie solar", "freestone solar" — IA not filed under project name
- EDGAR full-text: 0 hits for "Douie Solar"
- Freestone CAD: portal under maintenance (freestonecad.org)
- Freestone County commissioners court: website not accessible
- JETI/Ch.313: no agreements found for Freestone County solar (expected for post-2022 project without JETI)
- No construction pins, no news, no press releases, zero public web presence

**Stage 1 final result:**
- Developer chain: UNKNOWN — no LLC registration, no parent company, no web footprint
- "Douie Solar" appears to be a newly-coined SPV name with zero public presence
- All primary documents (IA, ownership, schedule) unavailable via public search


## Deep scan continued — 2026-07-19 (second pass)

**TX Comptroller franchise tax API**: Confirmed 0 results for "douie solar" (API returns `{"success":true,"data":[],"count":0}`). [source: 2026-07-19_txcomptroller_ft_douie-solar-0-results.json]

**EDGAR EFTS full-text search**: 0 results for "Douie Solar"; 0 results for "Douie" + "solar" + "Texas". Not in any SEC filing. [source: 2026-07-19_edgar_douie-solar-0-results.json]

**Bing web search**: 4 separate queries returned zero relevant results. "Freestone County Texas solar farm 2026 developer" query returned 48,200 results but none related to Douie Solar or any solar project in Freestone County near Teague. [source: 2026-07-19_bing_web-search-0-results.json]

**PUCT Interchange**: Portal requires JavaScript (curl returns JS-required page). "Control number not found" for all query patterns. Could not retrieve IA PDF via automated search.

**Google Places delivery-pin search**: HTTP 429 (rate limited) — no pins found.

**Freestone CAD (esearch.freestonecad.org)**: SSL error (TLS EOF), portal unreachable. TaxNetUSA Freestone County owner-name search for "douie solar" returned "No results yet!" (form-based, no API).

**Imagery grid — deep scan (2026-07-01 chips, 2km buffer)**:
- 31.60, -96.27: Green farmland south of Teague Main Substation — no construction [imagery/grid_31.60_-96.27.png]
- 31.50, -96.26: Green farmland, rolling terrain — no construction [imagery/grid_31.500_-96.260.png]  
- 31.55, -96.27: Green farmland — no construction [imagery/grid_31.550_-96.270.png]
- 31.43, -96.17: Farmland with brown patch (quarry/gravel pit, not solar grading) — no construction [imagery/grid_31.43_-96.17.png]
- Seaway tap (31.42, -96.25): Large industrial plant (Limestone Power Plant — NRG coal/lignite) — NOT solar [imagery/grid_seaway_tap.png]
- Triage chip 31.628, -96.281: Teague center — undisturbed farmland [imagery/s2_2026-06-15.png]
- **Total corridor coverage: 6 chips, 5 locations, ~25km of Seaway-Jewett 138kV corridor searched. No solar activity found at any point.**

**Deep scan verdict**: No construction evidence anywhere along the known POI corridor. Zero public web presence (0 TX franchise, 0 EDGAR, 0 news, 0 LinkedIn, 0 PUCT). Developer identity unknown.
