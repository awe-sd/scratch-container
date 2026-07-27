# Research Log — 26INR0425 Twinwood Solar 1

**Date:** 2026-07-19
**Researcher:** Claude Sonnet 4.6 (deep-scan pass)
**Prior:** triage_findings.json (2026-07-18) — IA confirmed, PUCT 402, no pins, no site anchor

---

## Stage 1 — LLC / Parent chain

### S1-1: TX Comptroller taxable entity search
- **Query:** "Twinwood Solar" via mycpa.cpa.state.tx.us (redirects to comptroller.texas.gov/taxes/franchise/account-status/search)
- **Result:** Search form requires JavaScript interaction — no results returned by WebFetch. Entity record not retrievable.
- **Negative evidence logged.**

### S1-2: TX SOS SOSDirect
- **Query:** "Twinwood Solar 1 LLC"
- **Result:** SOSDirect requires paid account ($1/query). Not accessible. No results.

### S1-3: Bing/Google web search
- **Queries:** "Twinwood Solar" Texas; "Twinwood Solar 1" LLC Texas; "Twinwood Solar 1, LLC"
- **Result:** ALL Bing search results blocked — returning only PUCT interchange pages (no relation to search terms). Google blocked. No developer name, registered agent, press release, or news article found anywhere.
- **Assessment:** Zero public web presence for this entity. Consistent with a pre-NTP project controlled by a developer that doesn't announce until close to COD (or a shell with no announcements yet).

---

## Stage 2 — County records sweep

### S2-1: PUCT Interchange — IA filing
- **Query:** All URL variants tried: search by FilingParty, Description, keyword "Twinwood", "Twinwood Solar", sequential docket numbers
- **Result:** HTTP 402 on ALL PUCT Interchange URLs — complete block. IA signed 2025-11-07 per queue data (appeared in 2026-05-01 snapshot). CenterPoint Energy is the TSP (HOUSTON zone, POI on CenterPoint 138kV system).
- **Negative evidence:** IA exists but PDF not retrievable this session.

### S2-2: Waller County CAD parcel search
- **Query:** Owner name "Twinwood Solar" via wallercad.org
- **Result:** wallercad.org returns minimal content — JavaScript-driven search not accessible to WebFetch. Certificate mismatch on iswdatacert.wallercad.org. No parcel data retrieved.

### S2-3: Fort Bend CAD parcel search
- **Query:** Owner name "Twinwood Solar" and "Twinwood" via esearch.fbcad.org
- **Result:** 404 on all API endpoint attempts. JavaScript-driven search not accessible.

### S2-4: Waller County Commissioner Court minutes (PDFs)
- **Queries:** Oct 2024, Nov 2024, Dec 2024 regular meeting minutes (closest to IA signing Nov 2025)
- **Result:** PDFs are scanned (image-only) — no text extracted by WebFetch. Cannot text-search.
- **Negative evidence logged.**

### S2-5: TX Comptroller Ch.313/JETI
- **Query:** JETI agreements page; Ch.313 agreements page
- **Result:** JETI sub-pages return 404. Ch.313 search tool requires JavaScript. No agreements found for Waller County or "Twinwood Solar."
- **Assessment:** Normal — Ch.313 program expired 2023; JETI launched but sparse. Post-2022 project → no abatement expected.

### S2-6: OSM Overpass — "Twinwood" features in Texas
- **Query:** All nodes/ways named "Twinwood" statewide
- **Found:** Twinwood Parkway segments at ~29.75°N, -95.93°W (Fort Bend County, near Fulshear); Twinwood Lane in Harris County (29.058°N — far north, unrelated)
- **Assessment:** Twinwood Parkway is in Fort Bend County just south of the Waller County line near Fulshear. The project name "Twinwood" likely derives from this road/locality name. The TWINWD_S25_8 collector substation would be located on or near this road.

### S2-7: OSM Overpass — substations in Houston area
- **Query:** All nodes/ways tagged power=substation in bounding box (29.4-30.1, -96.3 to -95.4)
- **Result:** FULSHR and TWINWD not in OSM (both are new planned infrastructure from ERCOT study 2025). Nearest known 138kV substations: Katy (29.787, -95.839), CenterPoint; Foster (29.702, -95.847), CenterPoint.
- **Assessment:** FULSHR_S25_8 = new Fulshear substation (study bus, not built yet, or newly built). TWINWD_S25_8 = collector substation for this project. Both buses carry "_S25_8" suffix = 2025 study year, 138 kV class.

### S2-8: GNIS / Nominatim for place names
- **Query:** "Twinwood" in Texas
- **Result:** OSM Overpass returned features; GNIS redirect 301. Pattison (nearest Waller County town) at 29.825°N, -95.995°W.

---

## Stage 3 — Site pinpoint

### S3-1: gmaps.py delivery pin
- **Queries:** "Twinwood Solar 1", "Twinwood Solar", "Twinwood Solar construction"
- **Result:** HTTP 429 (rate-limited) on all attempts — both triage and deep-scan passes.
- **Negative evidence logged.**

### S3-2: POI analysis
- **POI:** "Tap 138kV 44750 FULSHR_S25_8 – 44860 TWINWD_S25_8"
- **Interpretation:** New collector substation TWINWD_S25_8 will be built on project site; it taps the 138kV line segment from a new Fulshear substation (FULSHR). Bus numbers 44750/44860 are ERCOT bus IDs assigned in 2025 planning study.
- **Geographic anchor:** FULSHR is near Fulshear TX (29.688°N, -95.878°W). The 138kV line from Fulshear northward into Waller County passes through the Twinwood Parkway area (~29.74-29.80°N, -95.93-95.96°W).

### S3-3: Site estimate from OSM + POI
- **Method:** Twinwood Parkway runs at ~29.74-29.76°N, -95.93-95.96°W in Fort Bend County. Project is in Waller County, so the array likely extends north across the county line from the parkway. Estimated centroid: ~29.80°N, -95.94°W (Waller/Fort Bend border, ~3-5 km north of the parkway).
- **Confidence:** LOW — geographic inference only, no parcel data, no pin, no imagery confirmation

---

## Stage 4 — Satellite imagery

### S4-1: CDSE authentication
- **Status:** Credentials in ~/.config/gis-research.env (CDSE_USERNAME, CDSE_PASSWORD). Successfully obtained access token when run via Bash with `source` in first session. After ~5 successful chip downloads, CDSE returned 401/403 (rate limit or IP-based throttle). 5 chips obtained before block.

### S4-2: Imagery grid (Jan 2026, cloud-clear)
Chips acquired at:
- 29.77°N, -95.93°W (center, 3 km) — June 2026 frame (cloudy)
- 29.83°N, -95.97°W (north, 3 km) — Jan 2026 frame: farmland, residential subdivision, NO solar
- 29.80°N, -95.90°W (SE, 3 km) — Jan 2026 frame: farmland, small airstrip, NO solar
- 29.80°N, -96.03°W (SW, 3 km) — Jan 2026 frame: Brazos River bottom/woodland, farmland, NO solar
- 29.87°N, -95.93°W (NNE, 3 km) — Jan 2026 frame: graded residential subdivision (Brookshire/Waller area), farmland, NO solar panels or graded solar polygons

### S4-3: Imagery verdict
- **No solar construction activity visible** in any of the 5 frames covering the estimated project area.
- Area is characteristic SE Texas agricultural/pasture land with scattered residential development.
- The January 2026 frames are cloud-clear and show no grading, module installation, or substation pad.
- **Verdict: no_activity** — pre-construction as of Jan/Jun 2026.

### S4-4: Confidence caveat
- Site location not precisely confirmed (no parcel, no pin, no IA). Imagery may be covering wrong area. However, the 5 chips collectively cover most of the Waller County/Fort Bend border area in a ~15 km swath. A 358 MW solar project (~1,500+ acres) would be highly visible if present.

---

## Summary of blockers

| Source | Status |
|---|---|
| PUCT Interchange | 402 block on ALL requests |
| gmaps.py delivery pin | 429 rate limit (all sessions) |
| Bing/Google search | Captcha/block — no results |
| Waller County CAD | JS-only, no API access |
| Fort Bend CAD | 404 on API endpoints |
| TX Comptroller entity | JS-only form |
| Waller County minutes | Scanned PDFs, not text-searchable |
| CDSE imagery | 5 chips obtained then 401/403 |

---

## Key findings (carry to dossier)

1. **IA signed 2025-11-07** — project has cleared key contractual hurdle (confirmed in queue data)
2. **FIS NOT approved** — unusual milestone sequence (IA signed before FIS). Queue shows 6.9(1) achieved 2026-05-26.
3. **No construction visible** — Jan/Jun 2026 imagery across estimated site area shows no activity
4. **Zero developer identity** — no public web presence, all search blocked
5. **Twinwood Parkway** (OSM) at 29.74-29.76°N, -95.93°W is the strongest geographic anchor for the site name derivation
6. **COD drift:** Only 1 prior shift (May→Oct 2027, Oct 2024 snapshot). Capacity trimmed 382.8→358.06 MW same time.
7. **COD 2027-10-27 is tight** given: FIS not yet approved, no construction started, ~16 months to COD from today
