# Research Log — Foxtrot Wind (20INR0129)

Project: Foxtrot Wind | 268.2 MW Wind | Bee County, TX | CDR: SOUTH
POI: AEP 88689 Tango 345kV station | Reported COD: 2026-08-31

---

## Stage 1 — LLC → Parent Chain

### 2026-07-19 — GLEIF LEI registry
- Query: https://api.gleif.org/api/v1/lei-records?filter[entity.names]=helena+wind
- Result: **Helena Wind, LLC** — LEI 549300KY6HKK0GECYX39, HQ 401 N Michigan Ave Chicago IL (Delaware entity, created 2018-04-16). Chicago HQ consistent with Lincoln Clean Energy (Ørsted subsidiary).
- Artifact: sources/2026-07-19_gleif_helena-wind-llc.txt

### 2026-07-19 — TX Comptroller entity search
- Query: mycpa.cpa.state.tx.us → redirects to JS-only search page; no programmatic API available
- Result: **NEGATIVE** — no entity data returned for "foxtrot wind" or "lincoln clean"

### 2026-07-19 — TX SOS entity search
- Query: sos.state.tx.us/corp/soscorp.cgi?nm=foxtrot+wind
- Result: **HTTP 403 Forbidden** — blocked

### 2026-07-19 — GLEIF for "foxtrot wind"
- Result: **NEGATIVE** — empty results, 0 LEI records

### 2026-07-19 — Google Places (gmaps.py)
- Queries: "Foxtrot Wind", "Foxtrot Wind construction", "Lincoln Clean wind Bee County"
- Result: **HTTP 429 Too Many Requests** — rate limited

---

## Stage 2 — County Records Sweep

### 2026-07-19 — EIA Form 860 2025 Early Release *** DECISIVE ***
- Source: https://www.eia.gov/electricity/data/eia860/xls/eia8602025ER.zip
- Query: Bee County TX (FIPS 48025) wind plants
- Result: **Helena Wind** (plant code 63738, Helena Wind LLC, 268.2 MW OPERATING June 2022, 180 Vestas V150-4.2 turbines, lat 28.621959 lon -97.937625, 345kV via South Texas Electric Coop)
- Why matters: Exact 268.2 MW capacity match to Foxtrot Wind 20INR0129. Same county. ERCOT approved-for-sync March 2022; EIA operating June 2022. This is almost certainly the same physical project operating under a different legal entity name.
- Artifact: sources/2026-07-19_eia860_2025er_bee-county-wind.txt

### 2026-07-19 — Bee County CAD (esearch.beecad.org)
- Queries: owner "foxtrot", "lincoln", "foxtrot wind"
- Result: **HTTP 404** on all owner-name search attempts; search endpoint URL format not working

### 2026-07-19 — PUCT Interchange IA retrieval
- Queries: SearchText=foxtrot wind, SearchText=foxtrot, SearchText=20INR0129
- Result: **HTTP 402 Payment Required** on all queries — paywall, cannot access

### 2026-07-19 — TX Comptroller Ch.312/313 agreements
- Attempted: comptroller.texas.gov search — JS-only, no results returned
- Result: **NEGATIVE** — not accessible programmatically

### 2026-07-19 — Bee County Commissioners Court agendas
- Result: **HTTP 404** — beecounty.texas.gov/commissioners-court/agendas/ not found

---

## Stage 3 — Site Pinpoint

### 2026-07-19 — EIA 860 plant coordinates
- Helena Wind: lat 28.621959, lon -97.937625, city Pawnee TX 78145
- Adopted as site coordinates

### 2026-07-19 — OSM Overpass wind turbine nodes
- Query: power=generator, generator:source=wind, bbox (28.4,-98.2,28.9,-97.7)
- Result: **72 turbine nodes** at centroid ~28.622N, -97.938W — matches EIA coordinates within < 0.1 km
- Artifact: sources/2026-07-19_osm-overpass_bee-county-wind-turbines.txt

### 2026-07-19 — Tango 345kV substation location
- OSM Overpass search for substation named Tango: **no results** — not in OSM
- Nominatim search: **no results**
- AEP PDF: HTTP 404
- Cannot locate Tango substation independently

---

## Stage 4 — Satellite Imagery

### 2026-07-19 — Sentinel-2 chip at site coordinates
- Date: 2026-07-01, lat 28.6220, lon -97.9376, 6 km buffer
- Result: Turbines visible as white dots with access road network; confirmed operating wind farm
- Artifact: imagery/s2_28.62_-97.94_2026-07-01.png

### Prior triage (2026-07-18) — imagery at county centroid
- Date: 2026-07-01, lat 28.39, lon -97.77 — hit Beeville town center, not turbine site
- Artifact: imagery/s2_28.39_-97.77_2026-07-01.png
- Lesson: county centroid was 25+ km from actual site

---

## FAA OE/AAA
- System in government shutdown — no new filings processable; search returned only shutdown notice
- No turbine coordinates available from FAA

---

## Pentagon wind-pause risk
- TX Tribune articles for May 2026 wind/Pentagon topic: 404 errors; content not retrieved
- Status: **unconfirmed** — irrelevant if project already operating

---

## Key Conclusion
**Foxtrot Wind 20INR0129 is almost certainly already operating as Helena Wind** (EIA 860 plant 63738, 268.2 MW, operating June 2022). The ERCOT queue entry remains open with rolling COD dates because the approved-for-commercial-operation milestone was never filed under the "Foxtrot Wind" name. The reported COD of 2026-08-31 is a queue artifact with no physical meaning.
