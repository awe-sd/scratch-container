# Research Log — Sowers Storage (22INR0552)

Researched 2026-07-19 | Kaufman County, TX | 208.89 MW Battery/Storage | POI: 6894 Rose Hill_RC Sub 138 kV | CDR Zone: NORTH | Reported COD: 2027-07-01

---

## Stage 1 — LLC → parent chain


### 2026-07-19 — Web search for LLC/developer
- Query: "Sowers Storage" battery Texas, "Sowers Storage LLC" Kaufman County, etc.
- **FOUND:** Developer = **Belltown Power Texas**; LLC likely = **BT Sowers Storage, LLC** (consistent BT-prefix naming pattern across Belltown's ERCOT portfolio)
- Belltown Power: UK/US renewable developer, Farmers Branch TX HQ (13612 Midway Rd Suite 200), >11 GW developed capacity
- Key deal: ENGIE acquired ~6 GW (33 projects, solar+BESS) from Belltown Oct 2022; Sowers Storage likely in that portfolio
- PUCT referenced: Control 35077 (items 1409 + 1543) - NEEDS VERIFICATION (agent may have cross-referenced Oncor/Hanson number in error)
- TSP: Rayburn Country Electric Cooperative, Inc.
- IA signed date claimed: 2022-04-22 (amendment 2023-01-20) - NEEDS VERIFICATION vs PUCT docs
- Site candidate from POI "Rose Hill_RC Sub": ~32.6736, -96.3358 near Terrell TX (Kaufman County) - unverified
- No press releases or construction news found for Sowers Storage
- Source: web agent search (no saved artifact - negative result for press releases)

### 2026-07-19 — TX Comptroller COA search
- Query: name="Sowers Storage" via mycpa.cpa.state.tx.us
- RESULT: Portal redirects to search page; requires form POST - could not retrieve programmatically. Negative result (no cached entity data).


### 2026-07-19 — Queue history run
- queue_history.py output: 59 snapshots (2021-08-01 → 2026-06-01), 9 COD changes, 2022-12-31 → 2027-07-01
- FIS: NEVER approved. IA signed 2022-04-22. Meets 6.9(1) 2022-12-05. No "meets all 6.9" milestone.
- No construction start/end/energization/sync/COD approved dates.
- Capacity fluctuated: 203.0 → 200.83 → 206.1 → 204.96 → 203.9 → 208.89 MW (ongoing restudy activity)
- DECISIVE: 9 slips, 4.5yr total drift, pre-FIS, no construction evidence. High-drift risk.

### 2026-07-19 — PUCT Interchange search
- URL: interchange.puc.texas.gov/search/filings/?company=sowers+storage and company=BT+Sowers+Storage
- RESULT: Both returned HTTP 402 Payment Required. No documents retrieved.
- Negative result logged.

### 2026-07-19 — Kaufman CAD search
- kaufmancad.org/property-search → 404. esearch.kaufmancad.org → DNS not found.
- Negative result: Kaufman CAD portal unavailable via automated fetch.

### 2026-07-19 — Google Places (gmaps.py)
- Queries: "Sowers Storage battery", "BT Sowers Storage"
- RESULT: HTTP 429 Too Many Requests (rate limited). No pin data retrieved.
- Negative result logged.

### 2026-07-19 — Sentinel-2 imagery at estimated Rose Hill coords
- Chip 1: 32.700N, 96.350W, 2km buffer (s2_2026-07-01_b.png) — shows large industrial complex (warehouse/logistics, probably existing Terrell TX industrial). NOT a BESS signature — no parallel container rows on gravel pad near substation.
- Chip 2: 32.740N, 96.310W, 2km buffer (s2_2026-07-01_rosehillN.png) — peri-urban Terrell TX area, no BESS visible.
- 1km tight chip at 32.705, 96.337 failed (connection reset).
- Verdict from available imagery: no_activity / no BESS signature found in searched area. Possible site not covered by estimated coords.
- NOTE: Rose Hill RC Sub coords need confirmation — site was NOT found in 2-chip scan. Confidence LOW on lat/lon.

## Stage 3 — Site pinpoint summary
- POI "Rose Hill_RC Sub 138 kV" = Rayburn Country EC substation, Kaufman County
- Estimated area: northeast Terrell TX, ~32.73N, 96.32W — UNVERIFIED
- Google Places pin: FAILED (rate limit). No delivery pin obtained.
- No parcel/CAD data retrieved. No news photos or groundbreaking reports found.
- Confidence: LOW. Lat/lon from POI name only, not verified by parcel/pin/imagery.

## Stage 4 — Satellite ground truth summary
- Searched 2km buffers around 32.700/-96.350 and 32.740/-96.310
- No BESS signature (gravel pad + container rows) found at either location
- Verdict: no_activity (within searched area). Cannot confirm site not found = undeveloped; just means estimated coords may be wrong.
