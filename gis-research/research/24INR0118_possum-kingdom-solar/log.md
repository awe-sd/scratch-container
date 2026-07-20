# Triage log — Possum Kingdom Solar (24INR0118)

## T1 start
- queue_history.py: 50 monthly snapshots (2022-05 → 2026-06); 3 reported-COD changes
- COD drift: 2024-11-22 → 2026-05-08 → 2026-10-30 → 2027-10-29 (current)
- Key milestones: Screening complete 2021-11-29; FIS approved 2025-03-18; IA signed 2025-07-25; Meets 6.9(1) 2026-06-09
- Construction start reported 2025-05-01; construction end reported 2026-05-08 (but COD = 2027-10-29 — ~17-month gap)
- Capacity crept up: 260.0 → 261.36 → 262.22 MW
- Meets all 6.9: not yet; commercial operation not approved
- Note: IA signed 2025-07-25, appearing in queue first 2026-04-01 (likely late-reported)

## T2 start
- gmaps.py: HTTP 429 on all 4 queries (rate-limited); 0 pins found. Normal outcome.

## T3 start
- Bing: "Possum Kingdom Solar" + Texas → 0 project results (only opossum animal pages); DDG 403
- Bing: LLC + 24INR0118 → 0 project results
- opencorporates.com → CAPTCHA/403 blocked; 1 retry = also blocked
- No news, no press releases, no developer name surfaced
- T3 result: no web presence found

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all direct URL attempts (FilingParty= and Description= params)
- Bing site: search → CAPTCHA blocked; Bing general search → 0 results
- Queue data DOES show iaSigned = 2025-07-25 (first appeared 2026-04-01), so IA exists in ERCOT system
- IA PDF not retrievable via available web tools during triage
- T4 result: ia_found=true (ERCOT milestone confirms), PDF not downloaded

## T5 start
- TX Comptroller Ch.313 pages: general overview, no searchable list directly accessible
- Bing: Ch.313 / JETI / Jack County → 0 project results (all opossum results)
- Post-2022 project → missing Ch.313/JETI is expected (program expired Sept 2023)
- T5 result: abatement_found=false (normal for post-2022 entry)

## T6 start
- No pin from T2 (gmaps 429); no IA PDF map (PUCT 402); no abatement map
- Tried to resolve "Willow Creek Switch 345kV" POI → Bing returns unrelated results, no coordinates
- Best site estimate = "somewhere in Jack County" → checklist says SKIP imagery
- T6 result: no site candidate; imagery skipped

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~22
- Run complete

## Deep Scan — Stage 1: LLC → parent chain

### GIS xlsx re-read: LLC confirmed
- Source: local GIS xlsx (RPT.00015933…GIS_Report_Jun2026.xlsx, sheet "Project Details - Large Gen", row 395)
- **CRITICAL CORRECTION: LLC is "PK Solar, LLC" NOT "Possum Kingdom Solar, LLC"**
- Same LLC (PK Solar, LLC) also owns companion project 24INR0375 "Possum Kingdom BESS" (200.86 MW battery), same POI, same IA date 2025-07-30
- Combined project is ~263 MW solar + ~201 MW BESS; co-located at Willow Creek Switch in Jack County
- Artifact: local xlsx row, no saved file needed (authoritative source)

### Developer identity: NOT FOUND
- Bing searches for "PK Solar" Texas returned only Bollywood film / Pakistan results (CAPTCHA + irrelevant)
- Bing news: zero results for "Possum Kingdom Solar" or "PK Solar"
- Bing news for 24INR0375 / Possum Kingdom BESS: zero results
- pv-magazine, pv-tech, renewableenergyworld: blocked or no results
- SEC EDGAR full-text: 403 Forbidden
- TX Comptroller entity search: form-based, not accessible via GET/POST
- OpenCorporates: CAPTCHA-blocked
- TX SOS: paid portal ($1/search)
- **Conclusion: developer identity not determinable via web search; LLC name "PK Solar" is non-searchable**

### Co-POI context: Hecate Energy also at Willow Creek
- ERCOT queue shows 3 Hecate Energy "Dovetail Solar" projects (1-3) + Dovetail Storage all tapping bus 1421 Willow Creek in Jack County
- This confirms: (a) Willow Creek Switch is a real, accessible 345kV POI in Jack County; (b) the POI is capable of hosting multiple large projects
- Hecate Dovetail projects have no IA signed (FIS Started status) — they are earlier-stage than PK Solar

## Deep Scan — Stage 2: County records sweep

### PUCT Interchange: IA NOT retrieved
- All direct PUCT interchange.puc.texas.gov searches return HTTP 402 (requires authenticated session)
- ERCOT queue confirms iaSigned = 2025-07-25 (first appeared 2026-04-01, late-reported)
- IA document content (parties, schedule exhibit, POI map): unknown
- **Negative finding: IA PDF not retrievable with available tools**

### Jack County CAD: not accessible
- jackcad.org property search requires interactive form (no GET endpoint found)
- Attempts to search "PK Solar" as owner returned 404 errors
- **Negative finding: CAD parcels not retrieved**

### Ch.313/JETI abatement: not applicable
- Project entered queue 2022; Ch.313 expired Sept 2023; JETI post-2023
- No Ch.313 found (expected for post-2022 entry)

### Commissioners court: not accessible
- jackcounty.org returns 400; no online minutes portal found
- **Negative finding: no county government records retrieved**

## Deep Scan — Stage 3: Site pinpoint

### POI substations triangulated via OSM
- **Willow Creek Substation (bus 1421): 33.0562°N, 97.9103°W → Wise County** (reverse geocoded via Nominatim)
- **Jacksboro Substation (bus 1429): 33.2772°N, 98.1068°W → Jack County** (Nominatim)
- Willow Creek is at the Jack/Wise county border (east of Jack County centroid)
- Thomas Price (bus 11523) location NOT found via OSM or search
- The Willow Creek–Thomas Price 345kV line segment runs through Jack County
- Wise County Power Repower (20INR0286) also connects to "1421 Willow Creek 345kV" but is in Wise County — the switch straddles the county boundary area
- **Best estimate for project: eastern Jack County, roughly 33.0-33.2°N, 98.0-98.3°W — a ~30 km² search zone**
- gmaps.py: persistently 429 rate-limited (all attempts failed)
- Satellite imagery: CDSE 401 Unauthorized (credentials invalid/expired); Google Static Maps 403 (API not enabled)

### Site candidate: NOT resolved to parcel/pin
- No delivery pin, no parcel situs, no CAD record
- OSM substation coordinates give POI anchor but project site is a TAP on the line, not at the substation
- **Confidence: LOW — cannot report a lat/lon without derivation**

## Deep Scan — Stage 4: Satellite imagery
- CDSE credentials returning 401 Unauthorized — imagery unavailable
- Google Static Maps API: 403 Forbidden — unavailable
- **No imagery obtained**

## Negative evidence summary
- Zero web/news presence for "Possum Kingdom Solar" or "PK Solar" (strong signal for early-stage or private developer)
- No delivery pin found (gmaps rate-limited — inconclusive)
- No CAD parcel under LLC name (form-based portal inaccessible)
- No IA PDF retrieved (PUCT 402)
- No construction evidence (no imagery)
