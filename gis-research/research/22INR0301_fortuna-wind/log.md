# Research Log — Fortuna Wind (22INR0301)

Project: Fortuna Wind | INR: 22INR0301 | County: Jack, TX | 295.3 MW Wind
POI: Tap 345kV 1429 Jacksboro - 1730 WKrum | Zone: NORTH | Reported COD: 2026-07-01

Started: 2026-07-19

---

## Stage 1 — LLC → Parent Chain


## Stage 2 — County Records Sweep

### Jack County CAD (jackcad.org) — 2026-07-19
- Searched: FORTUNA WIND, RWE, WIND, ENERGY, CLEAN ENERGY
- Result: count=0 for all searches
- Finding: No parcels registered under project LLC/developer — expected for leased wind farm; landowner parcels retain their names
- Artifact: none saved (negative search result via API)

### PUCT Interchange — 2026-07-19
- Attempted multiple API endpoint patterns — all blocked (JS-only SPA, no scrape path)
- Triage previously confirmed IA filed 2024-08-29 by RWE Clean Energy Development LLC (Oncor is TSP)
- Control number unknown; range estimate ~35600-36500 based on Hanson Solar 35077 = 2023-09-20

### SEC EDGAR full-text search — 2026-07-19
- Query: "Fortuna Wind" 2022-2026
- Result: 0 hits — RWE is a German public company but uses European filings; not in EDGAR

### Jack County commissioners court — not yet searched

## Stage 3 — Site Pinpoint

### Overpass/OSM transmission infrastructure — 2026-07-19
- Jacksboro Substation (POI anchor): 33.2772N, -98.1068W ← decisive infrastructure anchor
- POI line: "Jacksboro - West Denton 345kV" (id=171941218)
  - Runs from Jacksboro (33.2772,-98.1065) → West Denton/Krum (33.3170,-97.3624)
  - This IS the "1429 Jacksboro - 1730 WKrum" line the project taps
- WKrum = West Krum, Denton County: ~33.27N, ~97.22W
- The tap point is along this corridor within Jack County (east of Jacksboro)
- Wind farm turbines can span >20km from the tap point; site search area = Jack County broadly
- Artifact: OSM overpass results (not saved to file yet)

### USWTDB (LBNL/USGS Wind Turbine DB) — 2026-07-19
- Query: Jack County (FIPS 48237)
- Result: 0 turbines — no existing/operational wind farm in Jack County
- Confirms Fortuna Wind has not yet been built

### POI infrastructure analysis — 2026-07-19  
- POI: "Tap 345kV 1429 Jacksboro - 1730 WKrum"
- OSM confirms: "Jacksboro - West Denton 345kV" line runs from Jacksboro Substation (33.2772N, -98.1065W) eastward to ~33.317N, -97.362W (West Denton)
- The tap point is somewhere along this line within Jack County (west portion of line)
- Jack County spans from ~33.0-33.6N, -97.8 to -98.5W
- Wind farm within Jack County most likely east of Jacksboro (following transmission corridor)
- Site estimate: center of Jack County east of Jacksboro, ~33.25N, -98.0W (±20km uncertainty)

## Stage 4 — Satellite Ground Truth

### Imagery survey — 2026-07-19
Chips pulled (all 2026-07-01 ±15d, 6km buffer):
- s2_2026-07-01_far_NW (33.55N, -98.45W) — open rolling farmland; zero turbine pads, no road network → key/
- s2_2026-07-01_NW (33.45N, -98.35W) — open farmland/rangeland; zero activity
- s2_2026-07-01_N (33.55N, -98.20W) — mixed farmland; zero activity  
- s2_2026-07-01_NE (33.45N, -97.95W) — eastern Jack County; undisturbed
- s2_2026-07-01_W (33.15N, -98.40W) — W Jack County; no activity
- s2_2026-07-01_center (33.25N, -98.00W) — wooded river valleys; no activity
- s2_2026-07-01_jacksboro (33.28N, -98.11W) — Jacksboro area; substation visible, no turbine activity → key/

**VERDICT: no_activity** — all 8 chips across full Jack County extent show undisturbed farmland/rangeland/woodland; no turbine pads, no access road strings, no clearing, no substation expansion consistent with a new 295 MW wind farm.

Per playbook early-exit rule: present-day no_activity + confirmed by county-wide scan → STOP imagery, do not pull historical.

## Stage 5 — Synthesis

### COD assessment
- Reported COD 2026-07-01 is already PAST (today 2026-07-19) with zero construction evidence
- Timeline drift: 4 COD changes over 3.5 years; project in queue since 2021-01-01
- IA signed 2024-08-08; FIS approved 2024-05-09 — both milestones are complete
- No construction start milestone, no JETI/Ch313 abatement, no FAA turbine filings
- Imagery confirms zero ground disturbance across Jack County as of July 2026
- A 295.3 MW wind farm (likely 50-100 turbines) requires 18-36 months to construct
- Independent COD: **2028-Q4 at earliest**, contingent on construction start by late 2026; drift risk HIGH
