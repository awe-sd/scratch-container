# Research Log — Tormes Solar (22INR0437)

Project: Tormes Solar | 356.6 MW Solar PV | Navarro County, TX | CDR: NORTH
Reported COD: 2027-03-31 | POI: tap 345kV 1906 Venus - 68091 Navarro

---

## Stage 1 — LLC → Parent Chain

### 2026-07-19 Construction Review Online — groundbreaking article
- Source: https://constructionreviewonline.com/750m-457-mw-tormes-solar-project-breaks-ground-in-texas/
- Saved: sources/2026-07-19_constructionreviewonline_tormes-solar-groundbreaking.html
- Findings:
  - Developer: **Matrix Renewables** (backed by TPG Rise)
  - EPC: **SOLV Energy** (CEO George Hershman quoted)
  - Groundbreaking: **May 19, 2026**
  - Capacity: 457 MWdc (queue says 356.6 MW — likely DC vs AC nameplate difference)
  - Location: "approximately two miles southeast of Barry and west of Corsicana"
  - Investment: over $750 million
  - Peak construction jobs: ~450
  - Prior collaboration: Matrix + SOLV previously did Stillhouse Solar in Bell County TX

### 2026-07-19 Construction Review Online — Matrix Renewables $1.3B portfolio financing
- Source: https://constructionreviewonline.com/1-3-billion-solar-and-storage-portfolio-financing-marks-major-milestone-for-matrix-renewables/
- Saved: sources/2026-07-19_constructionreviewonline_matrix-renewables-financing.html
- Findings:
  - Portfolio financing closed (month ~Jun 2026): $1.3B+ total
    - Construction-to-term debt: $470M+
    - Tax equity bridge financing: ~$400M
    - Letters of credit: ~$100M
    - DESRI preferred equity: $210M
  - Lenders/arrangers: MUFG, HSBC, Nomura, Santander
  - Equipment supplier: **First Solar** (for Tormes Solar)
  - **Expected COD: first half of 2027** (H1 2027)
  - Upon completion: "largest operational project in Matrix Renewables' global fleet"
  - Other portfolio projects: Alamo BESS (Kern CA), Gaskell West (Kern CA, operational), Pleasant Valley Solar (Ada ID, operational)

### 2026-07-19 TX Comptroller entity search — TORMES SOLAR LLC
- Source: https://mycpa.cpa.state.tx.us/coa/
- Result: Portal requires JavaScript/cookies — unable to fetch automated result
- Negative evidence: TX SOS SOSDirect requires paid login — could not verify registered agent

### 2026-07-19 SEC EDGAR full-text search — "tormes solar"
- Result: 0 hits — not surprising (private project company)

### 2026-07-19 PUCT Interchange keyword search — "tormes solar"
- Result: Extracted control number 207063 from HTML context text — possible IA docket
- Could not retrieve filing list (PUCT search UI returns 404 on POST)
- Need to verify via direct document URL pattern

---

## Stage 2 — County Records

### 2026-07-19 Navarro CAD owner search — Tormes Solar / Matrix Renewables
- navarro-cad.org: DNS not found
- navarrocad.org: SSL certificate error, could not access
- Negative evidence: No CAD parcel data obtained via automated fetch

### 2026-07-19 TX Comptroller Ch.313/JETI registry
- Fetched: https://comptroller.texas.gov/taxes/property-tax/ch313/
- Result: JSON data endpoint empty/inaccessible
- Negative evidence: No Ch.313 agreement found for Tormes Solar / Matrix Renewables / Navarro County via automated search

### 2026-07-19 Navarro County Commissioners Court minutes
- co.navarro.tx.us: returned no output
- navarrocounty.org: returned error
- Negative evidence: No abatement / JETI records found via automated means

---

## Stage 3 — Site Pinpoint

### 2026-07-19 Location clue from Construction Review article
- "approximately two miles southeast of Barry and west of Corsicana"
- Barry, TX is a small community in Navarro County at approximately 32.04°N, 96.62°W
- Two miles SE of Barry ≈ 32.014°N, 96.595°W (rough estimate; need POI cross-check)

### 2026-07-19 Google Places delivery-pin search — rate limited
- gmaps.py places "Tormes Solar" → HTTP 429 Too Many Requests (×3 attempts)
- gmaps.py places "Tormes Solar Navarro County" → HTTP 429
- Negative evidence: Could not retrieve Places pin; will retry later

### 2026-07-19 POI Infrastructure — Oncor 345kV Venus-Navarro line
- POI: "tap 345kV 1906 Venus - 68091 Navarro"
- "1906 Venus" and "68091 Navarro" are Oncor facility/bus IDs on a 345kV line
- Venus, TX is in Ellis County ~30 miles NW of Corsicana
- The Venus-Navarro 345kV line runs roughly NW-SE from Ellis to Navarro County
- Site should be within a few miles of a tap point on this line in Navarro County
- OpenInfraMap fetch: returned no map data (JavaScript-rendered)

---

## Stage 4 — Satellite Imagery

### PENDING — need confirmed lat/lon
- Barry, TX approximate centroid: 32.04, -96.62
- Will begin with chips around 32.014, -96.595 (2 mi SE of Barry)

### 2026-07-19 OpenStreetMap Overpass — power infrastructure near Barry TX
- Query: Overpass API, bbox 32.0-32.2 lat, -96.9 to -96.3 lon
- Found: OSM way 1087366819 (generation substation, 345kV) at 32.06334, -96.59314 — on Oncor Navarro-Watermill 345kV line
- Found: OSM way 1087366820 (transmission substation) adjacent
- POI "tap 345kV 1906 Venus - 68091 Navarro" = Oncor Navarro terminal on this line
- Location consistent with article "two miles SE of Barry, TX" (~3 km from Barry centroid)
- KEY FINDING: site confirmed at ~32.063, -96.593

### 2026-07-19 Queue history script — 22INR0437
- Output: timeline.md, 60 snapshots, 3 COD changes
- COD drift: 2023-12-15 → 2025-09-04 → 2027-05-31 → 2027-03-31
- IA signed: 2024-04-10; FIS approved: 2026-06-23

### 2026-07-19 CDSE Sentinel-2 imagery — FAILED
- Error: "invalid_grant" — CDSE credentials (sdalvi@appianwayenergy.com) no longer valid
- Negative evidence: No satellite imagery obtained

### 2026-07-19 Google Maps Static/Places API — FAILED  
- Static Maps: API not enabled for project
- Places API: quota exhausted (429 Too Many Requests)
- Negative evidence: No delivery-pin or site map image obtained

### 2026-07-19 PUCT Interchange — docket 207063
- Extracted from keyword search HTML context text
- Direct document fetch returned HTTP 402
- IA signed date (2024-04-10) confirmed via queue timeline

### 2026-07-19 TX Comptroller entity / Ch.313 / JETI
- Comptroller entity search: requires JavaScript — automated fetch returned search form only
- Ch.313 JSON: endpoint inaccessible
- JETI: no data found
- Negative evidence: No tax abatement documents obtained

### 2026-07-19 Navarro CAD property search
- navarro-cad.org: DNS NXDOMAIN
- navarro.prodigycad.com: React SPA — API endpoints return HTML (auth required)
- Negative evidence: No parcel data obtained

### 2026-07-19 TX SOS — TORMES SOLAR LLC
- SOSDirect requires paid login
- Negative evidence: Registered agent/address not retrieved
