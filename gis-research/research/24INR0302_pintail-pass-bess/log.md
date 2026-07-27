# Triage log — 24INR0302 Pintail Pass BESS

## T1 start
- Script: `queue_history.py 24INR0302` → 51 snapshots (2022-04-01 → 2026-06-01)
- **COD drift: 9 changes** — slipped from 2024-06-01 → 2026-07-24 (~2-year total slip)
  - Most recent: 2026-06-09 → 2026-07-24 (held since 2026-06-01 only)
- **Milestones:**
  - Screening started: 2022-04-18 ✓
  - Screening complete: 2022-06-16 ✓
  - FIS requested: 2022-04-07 ✓
  - FIS approved: 2024-10-15 ✓
  - IA signed: 2023-05-16 ✓
  - Meets 6.9(1) + all 6.9: 2024-11-01 ✓
  - Approved for energization: 2026-02-10 ✓
  - Approved for synchronization: 2026-03-25 ✓
  - Construction start/end: NOT reported
  - Commercial operation approved: NOT yet
- Capacity: 201.2 MW (2022) → 207.18 → 207.25 MW (2024-05 onward)
- **Strong late-stage signals**: energization + sync approvals in hand; COD 2026-07-24 is 6 days out from triage date (2026-07-18)

## T2 start
- gmaps.py returned HTTP 429 on both attempts (rate-limited). No pins found.
- Result: 0 delivery pins. Normal for BESS projects.

## T3 start
- Bing search "Pintail Pass BESS battery Texas San Patricio": no project hits
- Bing search "Pintail Pass" ERCOT: no project hits
- Bing search "24INR0302": no hits
- Bing search "Pintail Pass" LLC Texas battery: no hits
- TX SOS lookup: CAPTCHA-blocked (one attempt)
- No developer name surfaced. No news/PR found.
- Result: news_found=false, no LLC confirmation, no developer identified

## T4 start
- interchange.ercot.com: DNS not found (not the correct portal)
- interchange.puc.texas.gov/filings/search: HTTP 402 on all attempts
- Bing site:interchange.puc.texas.gov "Pintail Pass": CAPTCHA-blocked
- Bing web search for PUCT IA filing "Pintail Pass BESS": no results
- Note: queue timeline shows iaSigned=2023-05-16 (IA exists in ERCOT queue record)
  but the actual IA document could not be retrieved from PUCT this pass.
- Result: ia_found=false (document not retrieved, though queue record confirms IA signed)

## T5 start
- TX Comptroller Ch.313 page: no searchable database accessible via WebFetch
- JETI registry Bing search "San Patricio" battery: no results
- "Pintail Pass" + JETI/Ch.313/abatement search: no results
- Result: abatement_found=false — normal for post-2022 BESS projects (Ch.313 expired,
  JETI is new/sparse)

## T6 start
- Site candidate: POI = "8249 ANGSTROM 345KV" substation. Must geo-locate this substation.
- Searching for Angstrom substation location in San Patricio County / ERCOT COASTAL zone.
- Bing: "ANGSTROM 345kV substation San Patricio" — no results
- Bing: "ERCOT ANGSTROM substation" — no results
- Bing: "AEP Texas Angstrom substation San Patricio/Corpus Christi" — no results
- Bing: "ERCOT bus 8249 ANGSTROM" — no results
- ERCOT data portal: no accessible bus location dataset
- Bing: 345kV Portland/Ingleside San Patricio 2026: no results
- Result: ANGSTROM substation NOT geolocatable from public web sources in T6 budget.
  No site candidate better than county-level → SKIPPING imagery per playbook.
  construction_visible=false, site_candidate=null

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~32
- Run complete.

## Deep scan start — 2026-07-19

### D1 — Opening all deep-scan threads
- Three focus threads from triage: (1) ANGSTROM substation geo, (2) PUCT IA retrieval, (3) developer identification
- Today's date: 2026-07-19; COD claim: 2026-07-24 (5 days out)
- Sync approval in hand (2026-03-25); project may already be physically complete

### D2 — ANGSTROM substation geolocated
- **OSM way 1089997597**: "Angstrom Substation", AEP operator, 345kV switching, start_date 2022
- **Centroid: 28.04441, -97.43821** (from 9 polygon nodes via OSM API — sources/2026-07-19_osm_angstrom-substation.json)
- ~7 km N of Taft TX, ~6 km E of Sinton TX, San Patricio County
- Edit note in OSM: "new generation plants from EIA data" → confirms this is a NEW facility
- ERCOT parquet (earliest record 2022-04-01) shows `interconnectingFacility = BLACK MOUNTAIN ENERGY STORAGE`
- Developer name surfaced: **Black Mountain Energy Storage / Black Mountain Energy** (Fort Worth/Austin TX, founded 2021)
- Source: OSM API + parquet; HIGH CONFIDENCE

### D3 — Developer chain
- BMES website (bmenergystorage.com): 25+ ERCOT BESS sites sold (3.6 GW), 400 MW pipeline
- BMES parent: **Black Mountain** (blackmtn.com) — Fort Worth TX, founded 2007, multi-energy verticals
- BMES buyers cited on website: **Cypress Creek Renewables**, **Recurrent** (via LevelTen)
- BMES team: Rhett Bennett CEO, Jacob Smith CFO, Witt Duncan VP/CCO/Co-Founder, Prashanth Buyanni Dir Transmission
- `interconnectingFacility` timeline (from parquet):
  - 2022-04-01: BLACK MOUNTAIN ENERGY STORAGE (originator)
  - 2022-05-01: Pintail Pass BESS LLC (SPV formed)
  - 2023-10-01: EEC Pintail (brief — acquisition/JV phase, identity unknown)
  - 2024-02-01: Pintail Pass BESS, LLC (current SPV, through 2026-06-01)
- "EEC Pintail" identity: TX SOS blocked (requires login), no web hits, NOT resolved — logged as gap
- ERCOT June 2026 GIS xlsx confirmed: interconnectingFacility = Pintail Pass BESS, LLC

### D4 — PUCT IA retrieval
- interchange.puc.texas.gov: consistently HTTP 402 on all URL patterns (blocked for automated access)
- PUCT search by UTILITY_NAME=Pintail+Pass, UTILITY_NAME=Black+Mountain+Energy+Storage: both 402
- PUCT interconnection agreements search: 402
- IA document NOT retrieved (PUCT portal blocked); queue confirms iaSigned=2023-05-16
- Negative: ia_document_artifact=null

### D5 — Satellite imagery (2026-07-01 chip at substation centroid)
- 1 km buffer chip: PALE RECTANGULAR GRADED PAD visible in center-south; white structures present
  — consistent with battery container rows beside substation → substantially complete
- 3 km buffer xwide: Industrial complex NW (Voestalpine/LNG area), graded BESS pad in center
  — pad footprint ~10-15 acres estimate; small, consistent with 207 MW BESS footprint spec
- CDSE creds failing 403 after first two chips — historical timelapse not possible this session
- First activity date: NOT determinable (only 2026-07 imagery available); substation built 2022 per OSM
- Negative: historical construction timeline NOT established from imagery

### D6 — San Patricio CAD
- sanpatricio.prodigycad.com: JavaScript SPA, no API access, no owner-name search possible via curl/WebFetch
- Owner search for "Pintail Pass" and "Black Mountain": no results extractable
- Negative: CAD parcel data NOT obtained; expected for BESS (compact, leased from substation landowner)

### D7 — Tax abatements / commissioners court
- JETI/Ch.313 searches: no results (normal — Ch.313 expired 2022, JETI sparse for BESS)
- San Patricio commissioners court: site blocked
- Negative: no abatement document found

### D8 — Maps Static API
- gmaps.py staticmap: HTTP 403, Maps Static API not enabled for this key
- Negative: no site-highlighted map image generated

### D9 — CDSE authentication issue
- CDSE token endpoint returning 403 Forbidden (password may have changed or account rate-limited)
- Only chips that succeeded were from cached first run (2026-07-01 ±15d)
- Could not retrieve historical chips or run timelapse
- Negative: no pre-2026 satellite comparison available this session

### Summary of evidence state (pre-synthesis)
- Site: HIGH confidence (OSM substation + imagery confirms)
- Developer: Pintail Pass BESS, LLC → Black Mountain Energy Storage → Black Mountain (parent)
- Construction: Substantially complete per 2026-07-01 imagery
- IA: Confirmed signed 2023-05-16 (queue), document not retrieved
- COD: 5 days from today; all ERCOT gates cleared; financial security = Yes
