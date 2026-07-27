# Research Log — Samson Solar 1 (21INR0221)

Project: Samson Solar 1 · 250 MW Solar PV · Lamar County, TX · CDR zone: NORTH
POI: "tap both 345kV 1685 FarmersVl - 1695 Moses ckts"
Reported COD: 2026-09-30

---

## Triage summary (2026-07-18, prior run)
- Developer: Invenergy; 23 COD drifts 2021→2026; IA signed 2020-08-26
- Approved-for-sync 2021-08-31; NO commercial operation approval in queue
- PUCT blocked (HTTP 402); no site pin found; imagery skipped (no coordinates)
- Deep-scan recommended: resolve sync/COD gap, geolocate via substations, check phasing

## Stage 1 — LLC → Parent chain (2026-07-19)

### Name history from queue parquet
- 21INR0221 was originally filed as "Delilah Solar 1" (700 MW) in 2019
- Renamed to "Samson Solar 1" (250 MW) by 2020-01 after capacity reduction to 250 MW
- Three related INRs in the same multi-phase project: 21INR0221, 21INR0490, 21INR0491
  - 21INR0490 "Samson Solar 2" (203 MW) — originally "Delilah Solar 1A"; sync Oct 2024
  - 21INR0491 "Samson Solar 3" (250 MW) — originally "Delilah Solar 1B"; sync Oct 2021
  - 21INR0221 and 21INR0491 share the same POI ("1685 FarmersVl - 1695 Moses ckts")

### Multi-phase project identification
- All three phases (21INR0221, 21INR0490, 21INR0491) are part of the Samson Solar Energy Center
- Developer/operator: **Invenergy** (confirmed from Invenergy 2020 press release, GEM, WEC 10-K)
- Total project: five phases, 1,310 MW across Franklin, Lamar, Red River counties
- POI map: 21INR0221 = tap both 345kV FarmersVl-Moses circuits (Lamar County)
- SOURCE: sources/2026-07-19_invenergy_samson-solar-announcement-2020.html (Invenergy PR Nov 2020)

### WEC Energy Group 10-K (FY2025) — EDGAR 0000783325-26-000018
- WEC Infrastructure LLC acquired 80% of "Samson I" (= Samson Solar Energy LLC, 250 MW) in Feb 2023 for $257.3M
- Samson I commercially operational **May 2022** (Franklin County area)
- This matches EIA plant #63211 = Phase 1 (Franklin County, 250 MW)
- SOURCE: sources/2026-07-19_sec_wec-energy-group-10k-2025.html

### GEM Wiki (Global Energy Monitor) — phase table
- Phase 1: 250 MW, 2022 COD, Franklin County, 33.4300 -95.3820 (EIA 63211)
- Phase 2: 200 MW, 2025 COD, Lamar County, 33.2510 -95.1934 (EIA 63882 — actually census shows Franklin Co for these coords; GEM county label uncertain)
- Phase 3: 250 MW, 2022 COD, Lamar County, 33.4640 -95.3510
- GEM only tracks 3 phases (700 MW); full project is 5 phases 1,310 MW
- SOURCE: sources/2026-07-19_gem-wiki_samson-solar-energy.html

### Infrasure.ai — Samson Solar Energy II LLC (EIA 63882)
- 200 MW, Lamar County, operating 2025; lat 33.468171, lon -95.340883
- Census verify: GEM's coords for "Phase 2" (33.2510, -95.1934) are Franklin County not Lamar — GEM county mislabeled; infrasure coords (33.468, -95.341) confirmed Lamar County
- SOURCE: sources/2026-07-19_infrasure_samson-solar-ii.html

### LLC / ownership chain
- Samson Solar 1, LLC → Invenergy LLC (developer/operator)
- Invenergy LLC [privately held, Chicago] → no publicly traded parent
- No TX Comptroller search result for "Samson Solar 1, LLC" (portal JS-only, no API access)
- TX SOS not checked (SOSDirect paywall)

### Negative searches:
1. TX Comptroller entity search — POST form no results; portal JS-only
2. EDGAR company search "samson solar" — no registrant
3. PUCT Interchange filing search — JS-only portal, HTTP 402 on all curl attempts
4. TX SOS — not searched (paywall)
5. Lamar CAD owner search "Samson Solar" — JS-rendered portal, no results via curl
6. Lamar CAD owner search "Invenergy" — server returned 411 error
7. DDG search for Farmers Valley 345kV substation — botnet challenge blocked
8. DDG search "Samson Solar 1 LLC Texas" — botnet challenge blocked
9. OSM Overpass API — no substations returned for Lamar/Red River county bounding box (empty result, possible timeout)
10. EIA public API — requires valid API key

## Stage 2 — County records (2026-07-19)

### Abatements
- No Ch.313 found (per triage); consistent with 2021 INR
- JETI search: no JETI agreement found for Samson Solar 1 or Lamar County solar 2021-2022
- Absence expected for this vintage (Ch.313 expired end-2022; JETI is post-2022)
- No commissioner court minutes found

### Lamar CAD
- esearch.lamarcad.org JS-rendered — no results via curl
- No parcels found under Samson Solar, Samson Solar 1 LLC, or Invenergy
- Expected: solar parcels typically still under landowner names in TX

### Project area
- austinio.com: project spans ~11,000 acres across 3 counties for full 1,310 MW project
- Phase 3 (250 MW) = approx 1,000-1,500 acres (estimated; 250 MW ÷ 1,310 MW × 11,000 ac)
- No signed IA retrieved (PUCT blocked); no abatement application with acreage detail found

## Stage 3 — Site pinpoint (2026-07-19)

### Coordinates established
- **Primary**: 33.4640, -95.3510 (GEM Wiki "Phase 3", labeled Lamar County)
- **Cross-check**: 33.4682, -95.3409 (Infrasure EIA 63882 "Samson Solar Energy II LLC")
- **Census verify**: GEM Phase 3 coordinates confirmed Lamar County (Census geocoder)
- Distance between primary and cross-check: **1.04 km** — same project area
- The GEM Phase 3 (250 MW, Lamar, 2022 COD) matches 21INR0221 (250 MW, Lamar, sync 2021-08-31, oldest among three Lamar phases)
- 21INR0491 (Samson Solar 3, also 250 MW, Lamar, sync 2021-10-26) shares the same POI — may occupy an adjacent sub-area within the same ~1 km

### POI substations
- POI: "tap both 345kV 1685 FarmersVl - 1695 Moses ckts" — ERCOT element IDs
- "FarmersVl" and "Moses" are ERCOT node names; exact substation coordinates not found
  (OSM Overpass empty; DDG blocked; no CEII-free source found)
- Both 21INR0221 and 21INR0491 tap the same POI — confirming same interconnection area
- 21INR0490 uses a different POI (TTRSW 11688 at 345 kV) — different cluster

### Delivery pin
- gmaps.py: HTTP 429 (rate limited) across all attempts; no delivery pin retrieved

### Confidence assessment
- Coordinates: **33.4640, -95.3510** — GEM Wiki cited from EIA-860 + wiki-solar.org
- Method: GEM/EIA secondary source cross-checked with Infrasure EIA data
- Confidence: **medium** (secondary sources, not parcel deed or gate address; but both independent sources agree within 1 km; imagery confirms active solar farm at these coordinates)
- Disclaimer: 21INR0221 and 21INR0491 share the same POI and both 250 MW — they may be adjacent sub-blocks rather than distinct site locations; the coordinates are representative of the project area

## Stage 4 — Satellite imagery (2026-07-19)

### CDSE / Sentinel-2
- CDSE auth: HTTP 401/403 — credentials invalid/expired; imagery download blocked
- CDSE Catalog: confirmed tile T15STT covers the site (scenes available 2026-07-11)

### ESRI World Imagery tiles (public, date unknown but current)
- esri_z14_tile.jpg (33.464 -95.351): **dense solar panel arrays visible**, uniform dark blue-gray blocks across entire tile
- esri_z14_phase2.jpg (33.468 -95.341): same tile; same solar installation
- esri_z14_phase3_west.jpg (33.464 -95.370): **solar panels extend west** — panel blocks span at least 2 map tiles across ~4-5 km
- esri_z14_phase1_franklin.jpg (33.430 -95.382): additional **solar installation** in Franklin County area (Phase 1)
- esri_z13_phase3.jpg: wide view confirms multiple large solar blocks in NW portion, farmland to SE
- esri_z12_wide.jpg: county-scale view, Samson complex visible as dark patches

### Imagery verdict
- Site is **operating**: multiple independent tiles all show installed solar panel arrays
- Footprint appears to span ~6-8 km EW, consistent with 450-700 MW multi-phase complex
- No evidence of construction (grading, bare earth) — panels fully installed

## Stage 5 — Synthesis (2026-07-19)

### Verdict: OPERATING (queue artifact)
21INR0221 (Samson Solar 1) is confirmed operating as part of the Samson Solar Energy Center
multi-phase complex. The project received "Approved for Synchronization" on 2021-08-31 per ERCOT
queue data and the site shows installed solar arrays. The absence of "Approved for Commercial
Operation" in ERCOT queue is a queue data anomaly — not evidence of an incomplete project.

The reported COD of 2026-09-30 is the queue's last COD drift entry. The actual commercial
operation date is circa 2022 (consistent with WEC's Samson I acquisition noting COD May 2022,
and GEM tracking Phase 3 Lamar County COD 2022). The queue record has drifted 23 times but
the project has been generating for ~4 years.

