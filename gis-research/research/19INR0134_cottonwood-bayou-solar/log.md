# Triage log — Cottonwood Bayou Solar (19INR0134)

## T1 start
- queue_history.py ran OK; 101 snapshots, 24 COD changes
- Milestones: IA signed 2019-11-13, FIS approved 2023-04-27, meetsAllSection69 2023-04-27
- Approved for energization: 2024-05-01; approved for synchronization: 2024-05-29
- Commercial operation approved: NOT YET
- Capacity expanded from 150 MW → 351.4 MW in Nov 2022
- COD drift: 24 changes; original 2020-11-01 → now 2026-08-29 (~6 year slip)
- Recent COD churn: monthly slips from mid-2024 to present; still slipping
- T1 done (2 tool calls used)

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts (1 retry used); no pins retrieved
- T2 done (2 tool calls, budget spent at limit)

## T3 start
- DDG: CAPTCHA blocked (1 attempt, 1 retry limit used)
- Bing: "Cottonwood Bayou Solar" — no project-relevant results (generic tree/quilt hits)
- Bing: "19INR0134" OR "Cottonwood Bayou Solar LLC" — no results
- Bing: "Cottonwood Bayou" solar Brazoria Texas — no results
- No developer name surfaced; no news/PR found
- T3 done (5 tool calls, budget spent)

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all direct URL attempts (all 3 tries returned 402)
- Bing site:interchange.puc.texas.gov: CAPTCHA blocked
- Bing PUCT/IA keyword search: no results
- IA not confirmed; portal blocked — negative result logged
- Note: milestone data shows iaSigned = 2019-11-13 in queue data, so IA likely exists as a filed document
- T4 done (5 tool calls, budget reached)

## T5 start
- TX Comptroller Ch.313 page: no downloadable database found; Ch.313 program ended 2022 (pre-cutoff)
- Bing Ch.313/JETI search: no results for Cottonwood Bayou Solar
- No abatement record found; normal for a 2019-vintage project (Ch.313 eligible era) if not applied
- T5 done (4 tool calls, budget spent)

## T6 start
- Site candidate: Liverpool TX area (29.30°N, 95.28°W) — POI names Liverpool substation (138kV)
- cdse.py 3×3 grid attempted: all 9 chips failed with HTTP 401/403 (CDSE token endpoint returning Forbidden/Unauthorized)
- Single retry attempted (the parallel grid was the retry pass); credentials appear invalid/expired
- No imagery retrieved; construction verdict: unknown
- T6 done (1 tool call used, credential block logged, no retry remaining)

## T7 start
- triage_findings.json written
- triage.md written
- T7 done. Total turns used: ~28. STOP.

## Deep scan — 2026-07-19

### D1 — Developer identification (DECISIVE)
- SEC EDGAR EFTS full-text search: "Cottonwood Bayou Solar" → 6 hits, all TotalEnergies SE (CIK 0000879764)
- **TotalEnergies 6-K filed 2024-01-02** (exhibit 99.15): "TotalEnergies has signed a second contract with LyondellBasell... to supply...green electricity sourced from its utility-scale Cottonwood Bayou and Brazoria Solar farms in Texas... Through the 12-year CPPA signed in 2022, LyondellBasell will offtake 150 MWac (195 MW) from TotalEnergies' Cottonwood Bayou Solar plant, a project located south of Houston, with a capacity of 455 MW and a commercial start-up planned for end of 2024."
- Saved to: sources/2024-01-02_totalenergies_6k_lyondellbasell_cppa.htm
- TotalEnergies 2025 20-F (FY2024): XBRL lists subsidiaries: Cottonwood Bayou Storage LLC (100%), Cottonwood Solar Cash Equity HoldCo LLC (100%), Cottonwood Solar Class B HoldCo LLC (50%). Also mentions "50% stake...operator of...Cottonwood [Solar]." This confirms full corporate structure in place.
- **Parent chain: Cottonwood Bayou Solar LLC → TotalEnergies SE (via Cottonwood Solar Cash Equity HoldCo LLC)**
- **Offtaker: LyondellBasell (12-yr CPPA signed 2022, 150 MWac/195 MW from Cottonwood Bayou)**
- Artifact: sources/2024-01-02_totalenergies_6k_lyondellbasell_cppa.htm

### D2 — Substation locations (OSM/Overpass)
- Liverpool Substation: 29.2791, -95.2949 (CenterPoint Energy, 138kV/12.5kV, ref "LV")
- Petson Substation: 29.2530, -95.2203 (138kV)
- Both confirmed in OSM via Overpass API query
- Distance between substations: ~9.4 km; project is a "tap" on the line between them
- Midpoint estimate for site: ~29.266, -95.258

### D3 — Site location — initial imagery
- test_chip.png (6 km buffer, 29.30, -95.28, 2026-07-01): No obvious solar installation at original POI centroid estimate; cloudy, green farmland
- grid_center_2km.png (2 km buffer, 29.307, -95.285): Green farmland/vegetation near Liverpool TX; no modules or graded pads visible
- CDSE token rate-limited when running parallel chips; sequential chips needed
- Liverpool-Petson midpoint chips not yet obtained (token cooldown)

### D4 — OSM solar plant polygons (DECISIVE site confirmation)
- Overpass query: solar plants in 29.20-29.31N, -95.32 to -95.20 → 18 elements
- **17 unnamed solar plant polygons clustered at 29.227-29.267N, -95.242 to -95.277** — directly between Liverpool and Petson 138kV substations as described in POI
- Centroid: 29.2512, -95.2589
- Lat range 0.04°, Lon range 0.035° → rough area ~3,700+ acres, consistent with 455 MW project
- Saved: sources/2026-07-19_osm_overpass_solar_plants_brazoria.json

### D5 — Satellite imagery (construction confirmed)
- cluster_2024-01.png (Jan 2024, 4km @ 29.2512,-95.2589): Large-scale ground clearing and grading, tan rectangular parcels — ACTIVE CONSTRUCTION visible
- cluster_centroid_4km.png (Jun 2026, 4km @ 29.2512,-95.2589): Brownish/tan rectangular blocks in same footprint; cloudy but consistent with installed modules. Pattern distinct from surrounding agricultural land.
- ERCOT milestone: energization approved 2024-05-01, sync approved 2024-05-29 — construction completed before May 2024
- Construction stage: **substantially_complete or operating** (energization granted May 2024)

### D6 — Developer/corporate chain
- TotalEnergies SE: 100% owner via Cottonwood Solar Cash Equity HoldCo, LLC; sold 50% stake in Dec 2024 (portfolio with Danish Fields + Hill Solar I) but remains operator
- Cottonwood Solar Class B HoldCo, LLC: 50% equity interest (investor)
- Cottonwood Bayou Storage, LLC: 100% owned (battery storage component)
- LyondellBasell: 12-year CPPA signed 2022 for 150 MWac (195 MW)

### D7 — COD drift assessment
- Dec 2023: TotalEnergies announces commercial start-up planned for "end of 2024"
- ERCOT energization: May 2024 — but COD keeps slipping (now Aug 2026)
- 25 COD changes since 2018; continuous monthly slipping since mid-2024 through mid-2026
- TotalEnergies' Brazoria Solar (neighbor project) had COD "end of 2025" — check if similarly delayed
- No commercial operation approval in ERCOT queue data as of June 2026
- Pattern: project is physically built (energization approved May 2024) but COD milestone not yet cleared — likely commissioning/ERCOT testing/contractual issues

### D8 — Timelapse analysis (contact sheet)
- Timelapse 2022-01 to 2026-06 (54 monthly frames), midpoint 29.266,-95.258
- 2022: Large brown agricultural/rice field parcels — baseline farmland
- 2023-Q1 (Jan-Mar): First rectangular cleared/graded areas distinct from farm patterns
- 2023-Q2 to Q4 (Apr-Dec): Active construction, graded rectangular parcels expanding
- 2024-Q1 to Q2: Dark uniform rectangular blocks = installed PV modules
- 2024-Q3 to 2026-Q2: Consistent dark panel signature — project built and stable
- **First activity: ~2023-01; substantially complete: ~2024-02 to 2024-04**
- Contact sheet: imagery/contact_sheet.png

### D9 — Ch.313/JETI and BCAD searches
- No Ch.313 record found for Cottonwood Bayou Solar in TX Comptroller search (blocked/not found)
- BCAD portal blocked (JS-dependent); no parcel lookup completed
- Negative results logged per hard rule

## Stage 5 wrap-up — 2026-07-19
- findings.json written
- dossier.md written
- queue_history.py: 101 snapshots, 24 COD changes → timeline.md regenerated
- build_brief.py: brief.html written (4 images, 3 sources)
- build_index.py: 41 projects indexed
- Verdict: real_active | Stage: substantially_complete | COD: 2026-Q3/Q4 | Drift risk: HIGH
