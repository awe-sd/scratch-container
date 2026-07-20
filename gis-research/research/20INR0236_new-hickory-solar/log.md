# Triage Log — 20INR0236 New Hickory Solar

T1 start
## T1 result
- 83 snapshots (2019-08-01 → 2026-06-01)
- COD drift: 12 changes. First COD 2021-05-21, current 2026-10-26 (~5.5yr slip)
- IA signed: 2020-06-30 ✓
- FIS approved: 2024-06-30 ✓ (very late relative to IA)
- Meets 6.9(1): 2021-04-12 ✓
- Meets all 6.9: 2025-07-31 ✓ (cleared last interconnection gate Jul 2025 — recent)
- Construction start/end/energization/sync/COA: all blank
- Capacity bounced: 250 → 206 → 225.7 → 206 → 209.15 MW (current)

T2 start
## T2 result
- gmaps.py → HTTP 429 (rate-limited) on both attempts; one retry done per rules
- pins_found: 0 (tool unavailable, not a confirmed miss)

T3 start
## T3 result
- DDG: CAPTCHA blocked; one retry used
- Bing x4 queries: "New Hickory Solar" Texas; LLC; Jackson County; + major developer names
- All returned generic news homepages — zero project-specific results
- Developer name: unknown; LLC: unconfirmed
- news_found: false

T4 start
## T4 result
- PUCT Interchange: all endpoints return HTTP 402 (blocked/unaccessible from this container)
- Bing site:interchange.puc.texas.gov search: CAPTCHA blocked
- FERC eLibrary: DNS not found / empty response
- IA status: queue data confirms iaSigned=2020-06-30 (milestone achieved), but IA document not retrieved
- ia_found: false (document not confirmed; milestone date is queue data, not document)

T5 start
## T5 result
- TX Comptroller Ch.313 pages: landing page only, no data tables accessible via WebFetch
- Bing search for JETI/Ch.313 + New Hickory Solar + Jackson County: no hits
- abatement_found: false
- Note: Ch.313 expired 2022; project entered queue 2019-2020, so pre-2022 window exists — worth checking in deep scan

T6 start
## T6 result
- No pin from T2 (tool blocked), no abatement map from T5, no IA map from T4
- Attempted POI substation lookup: "OLD_HCKRY_5 bus 5323 345 kV" — no coordinates found via OSM/Bing/web
- No site candidate better than "somewhere in Jackson County" — SKIP imagery per rules
- construction_visible: false (imagery not run)
- site_candidate: null

T7 start
## T7 result
- triage_findings.json written
- triage.md written
- Turns used: ~22
- Deep scan recommended: YES

## Deep Scan — 2026-07-19

### DS1: Ch.313 Agreement Found
- TX Comptroller Ch.313 app #1460: New Hickory Solar LLC f/k/a Old Hickory Solar LLC, Edna ISD, Jackson County
- Application date: 01/06/2020; first full tax year: 2026
- Source: https://comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id=1460
- Artifact: sources/2026-07-19_comptroller_ch313_1460_application.pdf (12.3 MB, 49 pages)
- Artifact: sources/2026-07-19_comptroller_ch313_1460_agreement.pdf (13.6 MB, 159 pages, mostly scanned)
- Artifact: sources/2026-07-19_comptroller_ch313_1460_amended_agreement_1.pdf (591 KB, 4 pages, text extractable)
- Artifact: sources/2026-07-19_comptroller_ch313_1460_form772_2024.pdf
- Artifact: sources/2026-07-19_comptroller_ch313_1460_form772_2025.pdf
- Artifact: sources/2026-07-19_comptroller_ch313_1460_biennial_2022.xlsx

### DS2: Developer Chain Established
- Original developer: Pattern Energy Group 2 LP (1088 Sansome St, San Francisco CA — patternenergy.com)
- Contact in 2022 biennial: Cole Johnson, CEO/Bridgelind Investments (777 Main St Suite 2800, Fort Worth TX 76102)
- Current contact (Amendment No.1, Oct 2025): Daniel Shlomi, Authorized Representative, NEW HICKORY SOLAR LLC, 280 Park Ave FL 27E, New York NY 10017 → email: dshlomi@crayhill.com
- Crayhill Capital Management is a New York-based infrastructure investment firm
- TX SOS file: 0804475641; entity registered in Delaware; name change from Old Hickory Solar LLC → New Hickory Solar LLC effective 04/09/2024

### DS3: Application Key Facts
- Original name: Old Hickory Solar LLC → renamed New Hickory Solar LLC (April 2024)
- 206 MWac, Jackson County, TX, ERCOT queue 20INR0236 (confirmed in application)
- Land: lease (option to lease as of Dec 2019); no parcel descriptions (Tab 9 = "Not Applicable")
- Total projected investment: $175.1M (per application Schedule A1/A2)
- Construction timeline per original application: start Q1 2021, COD June 2022
- Amendment No.1 (Oct 2025): construction commencement updated to Q4 2022; start of commercial operations updated to Q1 2026; limitation period: 2026-01-01 to 2035-12-31
- 2022 biennial report: $0 qualified investment through end of 2021 (no construction by 2021 year-end)
- 2022 biennial: COD projected Q4 2022 (missed; now at Oct 2026 per queue)

### DS4: Site Location Still Needed
- No parcel IDs found in application (Tab 9 "Not Applicable")
- Project is in Jackson County, Edna ISD
- Map on application page 24 shows site layout; map on page 23 is vicinity map in Jackson County
- Substation OLD_HCKRY_5 bus 5323 345 kV is the POI — other projects using same line are in Wilson/DeWitt counties
- Next: try to geolocate via Pattern Energy project listing, or imagery grid over Jackson County

### DS5: Site Location — NOT PINPOINTED
- Google Maps Places: 429 rate-limited (both triage and deep scan)
- Overpass: 429 rate-limited for Jackson County substation query
- Nominatim: no results for "Old Hickory" in Texas
- OLD_HCKRY_5 bus 5323 not in OSM; ERCOT bus lists are CEII-restricted
- Jackson County CAD API returned 0 results for "solar" (API works but no owner record found under "solar" — may be registered under different entity name or lease/exempt)
- Ch.313 application Tab 9 = "Not Applicable" (no land description/parcels)
- Application map page 23 (vicinity map) and page 24 (site layout) are images; text-extractable layer shows description text only
- Site: Jackson County, Edna ISD, near OLD_HCKRY_5 345kV bus — county-level precision only
- No imagery run (no confirmed coordinates)
- NEGATIVE: no parcel IDs, no Google pin, no OSM substation, no news/groundbreaking photo

### DS6: Construction Status Assessment
- 2023 CDR (actual data): 2021 $20.4M invested; 2022 same; 2023 $175.1M (full investment)
- 2022 CAD market value: $19.4M (equipment beginning to be placed)
- 2024 CAD market value: $114.1M — THIS IS AN ACTUAL APPRAISAL (not projected) per CDR format
- $114M CAD assessed value for a 209 MW solar plant is consistent with a completed facility
- Amendment No.1 (Oct 2025): "construction commencement updated to Q4 2022; start of commercial operations updated to Q1 2026"
- ERCOT queue (Jun 2026): construction start/end/energization/sync/COA all blank — discrepancy
- Interpretation: Project may be built but is stuck in ERCOT commissioning/testing queue; or construction delayed past Q4 2022 as reported; CAD value jump most consistent with modules installed
- Pattern Energy sold to Canada Pension Plan/CDPQ in 2020; project passed through Bridgelind Investments (Fort Worth) by 2022, then to Crayhill Capital (New York) by 2023
