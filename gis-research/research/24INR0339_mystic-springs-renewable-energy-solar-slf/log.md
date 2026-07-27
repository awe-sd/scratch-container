# Research Log — Mystic Springs Renewable Energy Solar SLF (24INR0339)

Started: 2026-07-19

## Identity packet
- Project: Mystic Springs Renewable Energy Solar SLF
- INR: 24INR0339
- LLC: Mystic Springs Renewable Energy Solar SLF, LLC (to verify)
- County: Kaufman, Texas
- Capacity: 258.83 MW Solar PV
- POI: Tap 345 kV Royse Switch (2478) – Poetry Switch (2485)
- CDR zone: NORTH
- Reported COD (claim): 2028-03-31

## Stage 1 — LLC → parent chain


## Stage 1 — LLC → parent chain

### 2026-07-19 — TX Comptroller taxable entity search
- Source: mycpa.cpa.state.tx.us/coa/
- Query: "Mystic Springs Renewable Energy Solar"
- Result: REDIRECT to comptroller.texas.gov/taxes/franchise/account-status/search — could not retrieve results from redirect target
- Logged as negative

### 2026-07-19 — Web search (subagent)
- Query: "Mystic Springs Renewable Energy Solar SLF" developer Kaufman Texas + variants
- Result: **FOUND developer** — Vesper Energy Development LLC (EIA Form 860 2024/2025, Utility ID 64545, address 20495 N Hwy 34 Terrell TX 75161)
- Vesper parent chain: Magnetar Capital (owner since Nov 2020), GCM Grosvenor (equity 2023), DBJ (equity)
- Paired storage project: 24INR0340 Mystic Springs Renewable Energy Storage SLF (same developer/POI, no IA signed)
- No press releases, EPC, PPA, or county filings found publicly

### 2026-07-19 — PUCT interchange search
- Source: interchange.puc.texas.gov
- Query: "Mystic Spring Renewable" company/project
- Result: HTTP 402 Payment Required — blocked, no IA document retrieved
- Logged as negative

## Stage 2 — County records

### 2026-07-19 — Kaufman CAD parcel search
- Not completed — budget exhaustion before reaching portal
- Logged as incomplete/negative

### 2026-07-19 — TX Comptroller Ch.312/313/JETI registry
- Not searched — budget exhaustion
- Logged as incomplete/negative

### 2026-07-19 — Kaufman County commissioners court minutes
- Not searched — budget exhaustion
- Logged as incomplete/negative

## Stage 3 — Site pinpoint

### 2026-07-19 — Google Places delivery pin
- Tool: gmaps.py places
- Queries: "Mystic Springs Renewable Energy Solar", "Mystic Springs Solar Kaufman County Texas"
- Result: HTTP 429 Too Many Requests (rate limited)
- Logged as negative

### 2026-07-19 — OpenInfraMap POI lookup
- Queried openinframap.org for Royse Switch / Poetry Switch 345kV infrastructure
- Result: No structured data returned from web fetch
- Logged as negative

### 2026-07-19 — Nominatim geocoding
- EIA address 20495 N Hwy 34 Terrell TX: no direct result
- Terrell TX: 32.7360, -96.2753
- Poetry TX (POI endpoint): 32.8257, -96.2458
- Royse City: 32.9761, -96.3313
- DERIVED ESTIMATE: site on TX-34 corridor between Terrell (~32.736) and Poetry (~32.826), estimated ~32.800, -96.255 (low confidence, ~5 km uncertainty)

## Stage 4 — Satellite

### 2026-07-19 — Sentinel-2 chip
- Not run — budget exhaustion before cdse.py chip command executed
- Logged as incomplete/negative

## Stage 5 — Wrap-up

### 2026-07-19 — queue_history.py 24INR0339
- Result: timeline.md written — 43 snapshots 2022-12 to 2026-06; 4 COD changes; IA signed 2025-10-30; no financial security/NtP
- ARTIFACT: timeline.md

### 2026-07-19 — build_brief.py and build_index.py
- Not run — budget exhaustion; running now in wrap-up
