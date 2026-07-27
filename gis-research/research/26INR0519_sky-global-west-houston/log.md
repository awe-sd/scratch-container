# Research log — Sky Global West Houston (26INR0519)

## Triage (prior session 2026-07-18)
**queue_history.py** — 25 snapshots (2024-06-01 → 2026-06-01), 1 COD change.
- Screening started: 2024-07-01 | Screening complete: 2024-10-04 | FIS approved: 2025-03-12
- **IA signed: 2025-03-25** ← strong signal
- COD drift: 2026-12-15 → 2027-06-01 (1 change)
- Developer: Sky Global Partners LLC (est. 2007); SPV: Sky Global Power Two LLC
- Technology: revised from 6×GE LM6000 to 16 IC engines (~331 MW)
- Prior project: Sky Global Power One (51 MW Jenbacher IC, commissioned 2016)
- TCEQ AQSEGU filings confirmed (multiple technical reviews + NSR void requests)
- deep_scan_recommended: true

## Deep scan (2026-07-19)

### D1 — Queue timeline
queue_history.py output saved to timeline.md and timeline.json. 25 snapshots, 1 COD change (2026-12-15 → 2027-06-01). IA signed 2025-03-25.

### D2 — EIA 860M (Sky Global Power One pinpoint)
Downloaded EIA Form 860M May 2026 from https://www.eia.gov/electricity/data/eia860m/xls/may_generator2026.xlsx
**Sky Global Power One** found in Operating sheet:
- Plant code 59938, Operator: Sky Global Power One Pledgor LLC
- County: **Colorado** (not Austin), State: TX
- Location: **29.550278°N, -96.53778°W**
- Units: 6× IC engine, 8.4 MW each, in-service 2016
- Confirms developer has operating track record; Power Two likely adjacent
Source: [EIA 860M](sources/2026-07-19_eia_860m_may2026_sky-global-power-one.txt)

### D3 — TCEQ NSR permit search (CRITICAL)
Successful POST to https://www2.tceq.texas.gov/airperm/index.cfm (fuseaction=airpermits.validate_search_criteria)
**Sky Global Power Two LLC (CN605770015, RN111020285)** — full permit history:
- Permits 160870, 166721, 170951 all CANCELLED after NSR VOID filings (design changes 2020-2024)
- **CURRENT ACTIVE: Permit 176331 (STDPMT, EFFECTIVE)**, Project 373915
  - Type: INITIAL (Standard Permit New Registration), Rule 6005
  - Received: 2024-05-13, Complete/issued: **2024-05-24**, Expiry: 2034-05-24
  - Address: **978 FM 3013 Rd, Sealy, Austin County TX**
- This is an EFFECTIVE NSR air permit — MANDATORY permit for gas reciprocating → obtained. Strong real-project signal.
- Design history: multiple void+reissue cycles confirm design evolution from GE LM6000 to IC engines
Source: [TCEQ NSR results HTML](sources/2026-07-19_tceq_airperm_sky-global-nsr-results.html)

### D4 — Site pinpoint via TCEQ + OSM geocode
978 FM 3013 Rd, Sealy TX geocoded via Nominatim OSM:
**29.7412°N, -96.1577°W** (OSM place/house match, FM 3013 road confirmed in Austin County)
Method: TCEQ facility address → OSM geocode. Confidence: high (permit address is authoritative)
Cross-check: POI "tap 138kV 44700 Gebhardt - 44740 Wallis circuit 65" — Wallis TX is ~9 km SW of this coordinate, consistent with a 138kV tap distance.

### D5 — Satellite imagery (Stage 4)
Present-first approach:
- 2026-07-01 6km chip (s2_2026-07-01.png): industrial compound visible lower-left, rectangular structure with graded pad
- 2026-07-01 2km tight (s2_2026-07-01_tight.png): clear industrial complex at site, large rectangular pale building/structure visible at center-left
- 2023-06-01 2km tight (s2_2023-06-01_tight.png): smaller/different footprint at same location — activity visible 2023
Comparison: 2026 frame shows larger, more developed industrial footprint than 2023. A new large rectangular structure (turbine hall / engine building) appears in 2026 that was not present (or much smaller) in 2023.
Timelapse job submitted (monthly 2024-2026) but timed out before completion — frames not available.
Construction verdict: **construction_active** — significant industrial development visible at site address.

### D6 — PUCT Interchange
Direct portal HTTP 402 (payment wall) — IA PDF not retrieved.
IA confirmed signed 2025-03-25 from ERCOT queue data.

### D7 — Austin CAD parcel
esearch.austincad.org returned search interface only (no results via WebFetch — likely requires JS).
Parcel data not retrieved; site address confirmed via TCEQ permit record.

### D8 — gmaps.py
HTTP 429 rate-limited on all attempts. No Google pins retrieved.

### Negative evidence log
- PUCT Interchange portal: 402 payment required — IA PDF not directly accessible
- Austin CAD: JS-dependent search, no WebFetch result
- gmaps.py: 429 rate limit on all queries
- DDG searches: all returned CAPTCHA pages
- TCEQ CRPUB customer search: POST redirected to homepage (wrong endpoint)
- Timelapse: job submitted but timed out (300s)
