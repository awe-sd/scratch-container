# Research Log — Little Ridge Storage (25INR0238)

Researched 2026-07-19 | Analyst: deep-research agent

## Identity packet
- Project: Little Ridge Storage
- INR: 25INR0238
- LLC: Little Ridge Storage, LLC (to verify)
- County: Collin, Texas
- Capacity: 252.0 MW
- Fuel/tech: Battery/Storage
- POI: Tap 138kV Swindell (812) - Olinger (818)
- CDR zone: NORTH
- Reported COD (CLAIM): 2027-09-01

---

## Stage 1 — LLC / parent chain


### 2026-07-19 — MAJOR FINDING: Site location from OSM

OSM Nominatim query for "Olinger Texas" returns:
- **Ray Olinger Power Station** at lat **33.0691813**, lon **-96.4509452**
- Address: "Ray Olinger Power Station, **Little Ridge**, Collin County, Texas"
- OSM bounding box: 33.0669-33.0706°N, -96.4540 to -96.4480°W
- OSM type: landuse/industrial, osm_id: 864993515

**The hamlet is named "Little Ridge"** — project name directly derived from this locality.
POI "Olinger (818)" = Olinger substation at/near Ray Olinger Power Station.

This gives high-confidence site lat/lon: **33.0691, -96.4510** (Collin County, NORTH zone) ✓

Source: Nominatim API — artifact: will save curl output to sources/

Also noted: Swindell Drive exists in Celina, Collin County (33.2885, -96.7566) — 
but the primary Swindell substation (812) is more likely near the transmission line 
connecting to the Ray Olinger/Olinger (818) substation.

### 2026-07-19 — Developer name: TX BESS B LLC

Yahoo search snippets from infrasure.ai and ercotqueue.com (BANNED sources — cannot cite directly)
both identify developer as "TX BESS B LLC". Need independent verification.
NEGATIVE: No TX Comptroller results (form redirects, API 403).
NEGATIVE: SOS Direct is paid — cannot access.
NEGATIVE: Bizapedia returned CAPTCHA.
TODO: Try corporateregistrationtx.com or other free TX entity lookup.


---

## Stage 2 — County records sweep

### Collin CAD
- NEGATIVE: collincad.org returns HTTP 403 on API queries. Could not perform owner-name search.
- NEGATIVE: No direct CAD parcel data obtained for "Little Ridge Storage" or "TX BESS B LLC".
- Expected for BESS: compact footprint (likely leased substation land) — thin CAD trail.

### TX Comptroller abatement / Ch.312/JETI
- NEGATIVE: Comptroller SB1340 database form does not return results via WebFetch (JS-rendered).
- NEGATIVE: No Ch.312 or JETI agreements surfaced in web searches for "Little Ridge Storage" or "TX BESS" in Collin County.
- Expected for new BESS: Ch.313 expired; JETI/Ch.403 potential but no application found.

### PUCT Interchange (interconnection agreements)
- CONFIRMED: **IA not signed** — queue milestone data shows IA signed date is blank (per timeline.md).
- NEGATIVE: PUCT interchange.puc.texas.gov returns HTTP 402 on direct docket queries.
- Web search surfaced docket numbers 59475 and 59315, but these are UNRELATED Oncor CCN proceedings.
- No Little Ridge Storage PUCT filing found independently.

### Commissioner Court minutes
- NEGATIVE: eagenda.collincountytx.gov returns 403. 
- NEGATIVE: No Collin County commissioner court references to Little Ridge Storage, TX BESS B, or battery storage projects in area near Nevada TX.

---

## Stage 3 — Site pinpoint

### Primary derivation: OSM Nominatim (decisive)
- Query "Olinger Texas" → returns OSM way 864993515: "Ray Olinger Power Station, **Little Ridge**, Collin County, Texas"
- Center: **lat=33.0691, lon=-96.4510**, bounding box 33.0669-33.0706 / -96.4540 to -96.4480
- The hamlet is literally named "Little Ridge" — project name derived from this locality.
- Operator: City of Garland (GP&L), 401 MW gas peaker, EIA ref #3576
- POI "Tap 138kV Swindell (812) - Olinger (818)" → "Olinger" = the 138kV substation at/adjacent to this plant.
- Artifact: sources/2026-07-19_osm-nominatim_olinger-substation-location.json

### Adjacent 138kV substation
- Overpass API: unnamed 138kV transmission substation at **lat=33.0681, lon=-96.4515**, 0.1km from Ray Olinger Power Station.
- This is almost certainly the "Olinger (818)" tap point.
- BESS site would be on or immediately adjacent to this substation.
- Artifact: sources/2026-07-19_osm-overpass_substations-near-olinger.json

### Delivery pin search: NEGATIVE
- GMaps places API returned HTTP 429 (rate limited) on all queries.
- No "Little Ridge Storage" construction delivery pin found.

### Cross-check
- POI county (Collin) ✓, POI zone (NORTH) ✓, hamlet name "Little Ridge" ✓
- Confidence: **HIGH** — OSM toponymy match is decisive.

---

## Stage 4 — Satellite ground truth

### Imagery obtained
- s2_2025-10-01_2km.png: Oct 2025, clear, 2km buffer centered on Ray Olinger plant
- s2_2026-04-01_2km.png: Apr 2026, clear, 2km buffer
- s2_2026-07-01_1km.png: Jul 2026, partially cloudy, 1km buffer  
- s2_2026-07-01_2km.png: Jul 2026, partially cloudy, 2km buffer
- contact_sheet.png: all 4 frames in one strip

### Observation
- **ALL FRAMES: NO CONSTRUCTION ACTIVITY VISIBLE.**
- Ray Olinger Power Station and its existing industrial footprint visible throughout.
- Adjacent 138kV substation area shows no new gravel pad, no container rows, no clearing activity.
- Surrounding land = undisturbed farmland, residential (Nevada TX), Lake Lavon shoreline.
- No BESS signature (pale gravel + parallel container rows) anywhere in 2km radius.
- VERDICT: **no_activity** — confirmed across 9 months of imagery (Oct 2025 → Jul 2026)

### Present-first rule: PASSED
- Jul 2026 = no activity → pulled Oct 2025 to confirm → both clear = no_activity confirmed.
- No timelapse needed (PLAYBOOK rule: bare farmland → pull ONE chip ~6mo back → stop).


---

## Stage 5 — Synthesis (2026-07-19)

### Negative evidence summary
- TX Comptroller entity search: API 403 / form redirect — could not verify LLC
- TX SOS (SOSDirect): paid, could not access
- Bizapedia: CAPTCHA blocked
- PUCT Interchange: 402 Payment Required on direct docket queries
- GMaps Places API: 429 Too Many Requests (rate limited throughout)
- Collin CAD: 403 Forbidden
- Collin County eAgenda: 403 Forbidden
- Comptroller SB1340 abatement DB: JS-rendered, no results via WebFetch
- PUCT dockets 59475/59315 (from Yahoo search): unrelated Oncor CCN proceedings — FALSE HIT

### Key affirmative findings
1. OSM hamlet "Little Ridge" at Ray Olinger Power Station confirms site at 33.0691, -96.4510 (sources/2026-07-19_osm-nominatim_olinger-substation-location.json)
2. Adjacent 138kV substation 0.1km away = likely Olinger (818) tap (sources/2026-07-19_osm-overpass_substations-near-olinger.json)
3. Queue timeline confirms: FIS never approved, IA never signed, 27-month COD drift (timeline.md)
4. Satellite: no_activity across Oct 2025 – Jul 2026 (imagery/contact_sheet.png)

### Wrap-up tools run
- queue_history.py ✓ → timeline.md
- build_brief.py ✓ → brief.html
- build_index.py ✓ → index refreshed (92 projects)

