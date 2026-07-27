# Research Log — Hacienda Storage (23INR0485)

Researcher: Claude agent  
Date: 2026-07-19  
Project: Hacienda Storage | 205.8 MW Battery | Galveston County, TX | COD claim: 2027-12-01

---

## Stage 1 — LLC / Parent chain

### 2026-07-19 — Research initiated
- Starting TX Comptroller entity search for "Hacienda Storage, LLC"
- Starting PUCT interchange search for "Hacienda Storage"
- Starting web search for developer identity


---

## EXTERNAL SOURCE SWEEP — 2026-07-19

### PUCT Interchange filings search (3 search terms)

All three PUCT Interchange search URLs returned **HTTP 402 Payment Required**:
- `https://interchange.puc.texas.gov/search/filings/?SearchText=Hacienda+Storage` → 402
- `https://interchange.puc.texas.gov/search/filings/?SearchText=Galveston+Energy+Storage` → 402
- `https://interchange.puc.texas.gov/search/filings/?SearchText=BT+Hacienda` → 402
- `https://interchange.puc.texas.gov/Apps/Filings/Search.aspx` → 402

**Result: ia_found = false (blocked — not confirmed absent). Requires manual browser search.**
Recommended: browser-navigate to `https://interchange.puc.texas.gov/Apps/Filings/Search.aspx`, search "Hacienda Storage", "Galveston Energy Storage", "BT Hacienda".

---

### Galveston County Appraisal District (GCAD) parcel search

Searched for owners: "Galveston Energy Storage", "Hacienda Storage", "BT Hacienda", "Belltown Power"

All GCAD portal URLs were unreachable:
- `https://www.galcad.org/` → DNS ENOTFOUND
- `https://galcad.org/property-search` → DNS ENOTFOUND
- `https://esearch.galcad.org/Property/Search` → DNS ENOTFOUND
- `https://galcad.harrisgovern.io/` → ECONNREFUSED
- `https://propaccess.trueautomation.com/clientdb/?cid=17` → HTTP 504 Gateway Timeout

**Result: parcel_found = false (all portals unreachable). Requires manual browser access.**
Recommended: `https://propaccess.trueautomation.com/clientdb/?cid=17` or `https://galcad.harrisgovern.io`, owner search "Galveston Energy Storage" and "Belltown Power".

---

### Galveston County Commissioner's Court minutes

All galvestoncountytx.gov URLs returned **HTTP 403 Forbidden** (server blocks all automated requests):
- `https://www.galvestoncountytx.gov/commissioners-court/minutes` → 403
- `https://www.galvestoncountytx.gov/commissioners-court/agendas-minutes` → 403
- `https://www.galvestoncountytx.gov/` → 403

**Result: minutes_found = false (site blocks automated fetch). Requires manual browser search.**
Recommended: browser search for "Hacienda" or "Galveston Energy Storage" in court meeting archives.

---

### TX Comptroller Ch.312/313/JETI registry

Comptroller site pages confirmed accessible. Local Development Agreement Database confirmed at:
`https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`
(covers Ch. 312, 380, 381 agreements; JETI not included in this search tool)

Searches attempted:
- Entity = "Galveston Energy Storage": page loads (HTTP 200) but database is JavaScript-rendered — GET parameters do not trigger server-side query; no results in static HTML.
- Entity = "Hacienda Storage": same — form visible, no results rendered statically.
- Galveston County all agreements via results.php endpoint → HTTP error "problem loading the data."
- Ch. 313 (Value Limitation): no dedicated search tool; contact `chapter313@cpa.texas.gov` for lookup.
- JETI page: informational only, no searchable agreement database.

**Result: abatement_found = false (JS-rendered search; requires browser). No agreements confirmed or denied.**
Recommended: browser to `https://comptroller.texas.gov/economy/development/search-tools/sb1340/search.php`, enter entity "Galveston Energy Storage"; email `chapter313@cpa.texas.gov` for Ch.313 lookup.

---

### Attwater 138kV substation — location research

POI in queue data: "38745 Attwater 138kV" (5-digit prefix = ERCOT substation ID)

Substation directory sources tried:
- `https://www.puc.texas.gov/industry/electric/ucap/SubstationList.aspx` → HTTP 402
- `https://www.ercot.com/gis/maps` → HTTP 404
- `https://www.ercot.com/services/rq/re/noie` → HTTP 404
- ERCOT GIS Report xlsx (multiple date paths) → HTTP 404

**Result: substation_location_confirmed = false (no accessible directory). Requires ERCOT GIS viewer.**

Contextual inference: "Attwater" in the coastal Galveston County context may reference the Attwater Prairie Chicken NWR corridor (western Galveston County / Austin County border area, near Sealy/Brookshire, ~50 miles NW of Galveston Island). A 138kV substation at that voltage class would serve the coastal industrial/agricultural corridor. However, the project is in Galveston County proper, so the substation is likely in the League City / Santa Fe / Hitchcock / Texas City area or the inland western Galveston County corridor. No confirmed coordinates.

Recommended: ERCOT Transmission portal `https://transmission.ercot.com/` → map search for substation 38745; or ERCOT Network Operations GIS data.

---

### External source sweep summary

| Source | Status | Finding |
|--------|--------|---------|
| PUCT Interchange ("Hacienda Storage") | BLOCKED (402) | No result — not confirmed absent |
| PUCT Interchange ("Galveston Energy Storage") | BLOCKED (402) | No result — not confirmed absent |
| PUCT Interchange ("BT Hacienda") | BLOCKED (402) | No result — not confirmed absent |
| GCAD parcel search | UNREACHABLE (DNS/timeout) | No result — not confirmed absent |
| Galveston Co. Commissioner's Court minutes | BLOCKED (403) | No result — not confirmed absent |
| TX Comptroller Ch.312 Dev Agreement DB | JS-ONLY (no static results) | No result — not confirmed absent |
| TX Comptroller Ch.313 | Email-only lookup | Not searched — requires `chapter313@cpa.texas.gov` |
| TX Comptroller JETI | No searchable DB | Not searchable via this method |
| Attwater 138kV substation location | NOT FOUND (all ERCOT URLs 404/402) | Location not confirmed |

All five assigned research areas returned negative results due to access/environment limitations (HTTP 402/403, DNS failures, JS-only forms). **No affirmative findings obtained in this sweep. No records confirmed absent — all require manual browser access.**

---

## Stage 1 Results — 2026-07-19

### LLC / Developer chain
- SPV entity: Galveston Energy Storage LLC (TX Taxpayer No. 32082837199, filed 2022-01-24)
  - Address: 13612 Midway Rd Ste 200, Farmers Branch TX 75244
  - Status: Active
  - Source: Texas Comptroller Open Data API
- Also: BT Hacienda Storage LLC (same date, same address - BT = Belltown Power Texas naming pattern)
- Parent developer: Belltown Power Texas
  - Website: belltownpower.com/us
  - Claims 11 GW+ delivered, 4.5 GW+ pipeline
  - ENGIE acquired 6 GW from Belltown Power (Oct 2022) - unclear if Hacienda included
- NEGATIVE: No press releases naming "Hacienda Storage" specifically
- NEGATIVE: No EPC or PPA offtaker found
- NEGATIVE: No signed IA - project in Facility Study phase (significant risk)
- COD already slipped: original ~Jun 2026, now Dec 2027
- Build probability rated "low (5%)" by at least one source

---

## Stage 2 — Attwater 138kV Substation Location Research — 2026-07-19

### Task
Locate the physical lat/lon of "Attwater 138kV" substation (ERCOT POI ID 38745, Galveston County TX), which is the POI for Hacienda Storage (23INR0485, 205.8 MW BESS, Belltown Power / Galveston Energy Storage LLC).

### GIS Report confirmation
From local file `data/RPT.00015933.0000000000000000.20260701.151514224.GIS_Report_Jun2026.xlsx`, sheet "Project Details - Large Gen", row 352:
- **INR**: 23INR0485
- **Project Name**: Hacienda Storage
- **GIM Study Phase**: SS Completed, FIS Started, No IA
- **Interconnecting Entity**: Galveston Energy Storage LLC
- **POI Location**: `38745 Attwater 138kV`
- **County**: Galveston
- **CDR Reporting Zone**: HOUSTON
- **Projected COD**: 2027-12-01
- **Fuel/Tech**: OTH / BA (Battery)
- **Capacity**: 205.8 MW
- FIS Requested: 2022-08-06; FIS Approved: 2022-04-04 (pre-request date anomaly)
- No IA signed.

### Sources searched (all negative or inconclusive)

| Source | URL | Result |
|--------|-----|--------|
| OSM Nominatim — "Attwater substation Texas" | nominatim.openstreetmap.org | Empty array (no results) |
| OSM Nominatim — "Attwater 138kV Texas" | nominatim.openstreetmap.org | Found: "Attwater, East Houston, Houston, Harris County, TX 77028" — this is a neighborhood/street, NOT a substation |
| OSM Nominatim — "Attwater substation Galveston Texas" | nominatim.openstreetmap.org | Empty array |
| Overpass API — power substations named Attwater near Galveston | overpass-api.de | HTTP 400 (query syntax rejected; URL encoding issues) |
| ERCOT gridmktinfo/gridplanningdata | ercot.com | HTTP 404 |
| ERCOT GIS maps | ercot.com/gis/maps | HTTP 404 |
| ERCOT network model substation list (xlsx) | ercot.com/files/docs/ | HTTP 404 |
| ERCOT MIS report 13455 (network model) | mis.ercot.com | HTTP 400/SSL failure |
| ERCOT MIS report 13060 | mis.ercot.com | SSL handshake failure |
| PUCT substation list | puc.texas.gov/industry/electric/ucap/SubstationList.aspx | HTTP 402 |
| OpenInfraMap | openinframap.org | JS-rendered map; no text data extractable |
| CenterPoint Energy substation list | centerpointenergy.com | HTTP 404 |
| Belltown Power website | belltownpower.com | Redirect to mybelltown.com (UK ISP); no US project pages found |

### OSM Nominatim note
The one non-empty result for "Attwater 138kV Texas" returned:
- Name: "Attwater"
- Lat: **29.8160850**, Lon: **-95.2844635**
- Display: "Attwater, East Houston, Houston, Harris County, Texas, 77028, United States"

This is the **Attwater Street neighborhood in northeast Houston / East Houston**, not a substation. It is 29.8°N, 95.28°W — north of Galveston County. Worth noting as this may be where the transmission line corridor originates — a 138kV line from a Houston-area substation named "Attwater" extending south into Galveston County is one hypothesis.

### Physical geography reasoning
- "Attwater 138kV" at 138kV voltage class is a transmission-level substation owned by CenterPoint Energy (the incumbent T&D utility in Galveston County).
- The name "Attwater" in this area references: (1) the Attwater's Prairie Chicken (endangered species in coastal prairie TX), (2) Attwater Road / communities in the western Gulf Coast corridor.
- Galveston County extends significantly inland (north) to ~30.0°N. The county includes Texas City, Hitchcock, Santa Fe, League City, Friendswood, Dickinson, La Marque.
- A battery storage project (not needing a remote/rural site for wind/solar resources) could sit at or near the substation itself.
- The triage run previously estimated site candidate ~29.42N, 94.99W (low confidence, from aggregator trackers which are banned sources per the playbook).

### Conclusion
**Not confirmed.** No authoritative lat/lon found. The OSM "Attwater" result at 29.816°N, 95.284°W is a Houston neighborhood, not the substation. The actual Attwater 138kV substation location in Galveston County TX remains unconfirmed from automated sources.

### Recommended manual follow-up
1. **ERCOT Transmission Operations portal** (`https://transmission.ercot.com/`): Map view → search substation "38745" or "Attwater". Requires browser.
2. **CenterPoint Energy transmission map** or substation inventory: CenterPoint owns 138kV T&D in Harris/Galveston Counties. Contact CenterPoint or search their PUCT filing exhibits for substation coordinates.
3. **PUCT TCOS/TCEQ permit filings**: CenterPoint files annual TCOS updates with substation locations. PUCT Interchange search for "Attwater" (requires browser due to 402 block on WebFetch).
4. **Google Maps / Satellite**: Search "Attwater substation" or "CenterPoint Energy Attwater" in Galveston County.
5. **Army Corps Galveston file SWG-2022-00547** (from prior triage): jurisdictional determination issued; the AJD document may contain site map coordinates.

