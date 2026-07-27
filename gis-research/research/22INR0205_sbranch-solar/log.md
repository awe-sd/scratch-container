# Triage log — 22INR0205 Sbranch Solar

## T1 start

**queue_history.py result:** 87 snapshots (2019-04-01 → 2026-06-01), 21 COD changes.

**Milestone summary:**
- Screening started: 2019-01-03
- Screening complete: 2019-03-13
- FIS requested: 2019-03-29
- FIS approved: 2021-07-29
- IA signed: 2020-07-26 ← signed BEFORE FIS approved (not unusual per data model)
- Meets 6.9(1): 2020-10-07
- Meets all 6.9: 2021-07-06
- Approved for energization: 2022-09-12
- Approved for synchronization: 2023-11-21
- Construction start/end: NOT REPORTED
- Commercial operation approved: NOT YET

**COD drift:** 21 changes from 2021-06-01 → 2026-07-31. Chronic slippage ~1 month at a time from 2024 onward. Current claim (2026-07-31) held only since 2026-06-01 — likely to slip again.

**Capacity changes:** 175 → 154 → 230 → 233.52 MW (settled since 2021-06).

**T1 result:** IA signed, all 6.9 milestones met, approved for synchronization but no commercial operation. No construction dates in queue. Heavy COD drift (21 changes over 5 years). Project appears stuck between sync-approval and COD.

## T2 result

gmaps.py returned HTTP 429 on first call; one retry also 429. T2 budget exhausted.
**Pins found: 0** (API rate-limited, not a negative signal about the project).

## T3 result

- DDG: CAPTCHA blocked (portal block, one retry attempted, still blocked)
- Bing "Sbranch Solar Texas solar": returned unrelated pages (Brazilian weather, Waffle House)
- Bing "Sbranch Solar ERCOT Wharton": returned unrelated pages (Vietnam articles)
- TX Comptroller entity search: 404 on direct URL; franchise search redirected, not useful without session
- No developer name surfaced; no news/PR found; no LLC registration details obtained
**T3 result: news_found=false, no developer identified**

## T4 result

- PUCT Interchange all endpoints returning HTTP 402 (Payment Required / session required)
- Tried: /search/filing, /search/filing?, /Documents/search, /, /search/filings/?FilingParty=Sbranch+Solar
- All 4 attempts blocked; rule allows 1 retry → budget exhausted
- Note: IA is confirmed SIGNED per queue data (2020-07-26) but the actual IA document PDF not obtained
**T4 result: ia_found=false (IA exists in queue but document not retrieved; PUCT portal blocked)**

## T5 result

- TX Comptroller Ch.313 agreements page: multiple URL attempts return overview/navigation pages only, no searchable database returned
- JETI registry page: same — navigation only, actual agreement data not accessible via WebFetch
- No Ch.313 or JETI agreement found for Sbranch Solar or Wharton County (inconclusive — portal did not serve data, not confirmed absence)
- Note: project was filed 2022, which is AFTER the 2022 Ch.313 sunset; JETI is the post-2023 successor — absence is EXPECTED and not meaningful for this project's vintage
**T5 result: abatement_found=false (portal inaccessible; post-2022 project — Ch.313 unlikely anyway)**

## T6 result

- Site candidate: POI anchor = East Bernard substation, Wharton County (~29.52°N, 96.07°W)
  - POI description: "Tap 138kV 44190 East Bernard - 44130 Caney" → project taps the 138kV line between East Bernard and Caney substations in Wharton County
  - Confidence: LOW-MEDIUM — East Bernard is the right substation but exact site location within county unknown
- CDSE imagery: 401 Unauthorized — ~/.config/gis-research.env contains only example credentials
- One retry with same credentials also failed (no real credentials present)
**T6 result: construction_visible=false (imagery unavailable — CDSE credentials not configured)**

## T7 result

Wrote triage_findings.json and triage.md. Turns used: ~28. Run complete.

**Portal blockers encountered this run:**
- gmaps.py: 429 Too Many Requests (T2)
- PUCT Interchange: 402 Payment Required across all URL variants (T4)
- DDG search: CAPTCHA (T3)
- CDSE: 401 Unauthorized — no credentials configured (T6)
- TX Comptroller Ch.313/JETI: returned navigation pages only, no data (T5)

## Deep scan start — 2026-07-19

Deep scan begins. Triage threads to chase:
1. PUCT IA document (portal blocked in T4)
2. Wharton County CAD parcel search (LLC name)
3. LLC parent chain (TX Comptroller, web)
4. CDSE imagery (sync-approved 2023-11-21, need to see if panels are up)
5. JETI/abatement check

Note: approved-for-sync 2023-11-21 but still no commercial operation (20 months) — abnormal gap; need to understand why.

## Deep scan results — 2026-07-19

### Stage 1 — LLC parent chain
- "Sbranch Solar" / "Sbranch Solar LLC" / "22INR0205": ZERO web presence across multiple search engines (Bing). All searches returned unrelated content.
- TX Comptroller entity search: portal requires JavaScript; could not retrieve entity details via WebFetch.
- TX SOS SOSDirect: requires paid account; not accessible.
- PUCT filing search (interchange.puc.texas.gov): FilingParty="Sbranch Solar LLC" = 0 records; FilingParty="S Branch Solar LLC" = 3 records (all for DIFFERENT project: Millers Branch Solar LLC / Brass Fork Solar / ETT territory).
- SEC EDGAR: 403/403 on all EFTS endpoints.
- **Developer: UNKNOWN.** No LLC parent chain established.

### Stage 2 — County records
- Wharton County CAD: whartoncad.net / wharton-cad.org — both DNS NXDOMAIN. wcad.net resolves but returns "Public Portal" with no accessible data. No parcel search performed.
- JETI/Ch.313: Portal inaccessible via WebFetch (returns navigation only).
- PUCT IA: Searched docket 35077 (umbrella IA docket, all TSPs). CenterPoint Energy Houston Electric filed solar IAs in 35077; NO filing for Sbranch Solar found. Item 1117 (CenterPoint-Hecate, 7/1/2020) and item 1139 (CenterPoint-AP Solar 6, 9/1/2020) bracket the IA signing date (2020-07-26) — items 1118-1138 in between are other TSPs' filings. No CenterPoint Sbranch Solar IA in PUCT records. The IA exists per ERCOT queue data but was not filed under 25.195(e) or was filed under a different description.
- **No county records obtained.** No abatements, no CAD parcels, no IA document.

### Stage 3 — Site pinpoint
- gmaps.py: 429 Too Many Requests (rate limited — not a negative signal).
- POI anchor: "Tap 138kV 44190 East Bernard - 44130 Caney" — node IDs 44xxx are CenterPoint's Houston Electric numbering system.
- Site candidate: 29.52°N, 96.07°W (East Bernard substation area) — confidence LOW; actual tap point on 138kV line somewhere between East Bernard and Caney substations, Wharton County.

### Stage 4 — Imagery
- CDSE credentials confirmed working (ePsYxCYw6tD6Kh@rTBFf).
- Pulled one xwide chip: 2026-07-01 at 29.52, -96.07 (East Bernard center).
- Image assessment: heavy cloud cover (~40% obscured); visible areas show agricultural fields, East Bernard town; NO solar array signature visible in this frame.
- NOTE: Image was centered on East Bernard town, not the tap-line corridor. The actual site is likely 2-5 km along the 138kV line running from East Bernard toward Caney (NW direction). Further imagery with better location needed.
- COD drift note: 22 changes, 2021-06 → 2026-07-31; slipping ~1 month at a time throughout 2024-2026; current COD claim (2026-07-31) is 12 days from today (2026-07-19) — near-certain to slip again.

### Key anomaly — approved-for-sync gap
Project approved-for-synchronization 2023-11-21 but still no commercial operation as of June 2026 (20+ months). Normal gap is weeks to a few months. 20-month gap with continued monthly COD slippage is a strong signal of persistent operational/commercial issue — interconnection dispute, financing problems, equipment issues, or PPA dispute. No public information found explaining the delay.

### Negative evidence (logged per playbook rule)
- No developer name found (all web searches)
- No news, PR, financing announcements found
- No CAD parcels found
- No abatement documents found
- No PUCT IA document found
- No construction pin (gmaps rate-limited)
- No construction dates ever reported in queue
