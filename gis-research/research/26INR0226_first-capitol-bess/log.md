# Triage log — First Capitol BESS (26INR0226)

## T1 start
**queue_history.py** → 34 snapshots (2023-09-01 → 2026-06-01), 5 COD changes (6 distinct values):

| COD | Held from | Until |
|---|---|---|
| 2026-05-31 | 2023-09-01 | 2023-10-01 |
| 2026-04-15 | 2023-11-01 | 2024-03-01 |
| 2025-12-31 | 2024-04-01 | 2025-01-01 |
| 2026-05-01 | 2025-02-01 | 2025-07-01 |
| 2027-05-01 | 2025-08-01 | 2026-04-01 |
| 2027-11-01 | 2026-05-01 | 2026-06-01 |

Key milestones: Screening complete 2023-12-14; IA signed 2025-05-15; Meets 6.9(1) 2025-02-12.
FIS approved = NONE. Construction start/end = NONE. COD slipped ~18 months total.
MW bumped 256.2 → 257.48 in 2025-02.

## T2 start
gmaps.py places "First Capitol BESS" → HTTP 429 Too Many Requests. One retry also 429.
gmaps.py places "First Capitol BESS Brazoria County" → HTTP 429. Budget exhausted.
**T2 result: 0 pins found (rate-limited, not necessarily no results).**

## T3 start
DDG search "First Capitol BESS" → CAPTCHA block. Bing searches (3 queries):
- "First Capitol BESS" Texas battery → 0 relevant results
- "First Capitol BESS" OR "26INR0226" → 0 relevant results
- "First Capitol" BESS Brazoria/West Columbia/Sweeny → 0 relevant results
No developer name, no news/PR, no LLC registration hit surfaced.
**T3 result: 0 relevant web results. No developer identified.**

## T4 start
PUCT Interchange all URL patterns → HTTP 402 Payment Required (3 attempts). Portal blocked.
**T4 result: IA status UNKNOWN — portal inaccessible. Note: queue shows iaSigned=2025-05-15, so IA exists in ERCOT records. Could not retrieve PDF.**

## T5 start
TX Comptroller Ch.313 page: no searchable database. Ch.313 expired 2022; 26INR entered queue 2023 → not eligible.
JETI page: no searchable registry found. Post-2022 project; JETI absence is normal.
Brazoria County CAD not checked (T5 budget exhausted on Comptroller pages).
**T5 result: no abatement found. Expected for this project vintage.**

## T6 start
Site candidate: West Columbia Main 138kV substation. POI is "Tap 138kV West Columbia Main (39500)".
West Columbia, TX city center ~29.144, -95.645 from Nominatim.
3×3 chip grid attempt (lat ±0.03°, lon ±0.03°, --buffer-km 2, 2026-06-15) → HTTP 401 Unauthorized (CDSE creds absent).
**T6 result: imagery not retrieved. CDSE auth failure. Site candidate: 29.144, -95.645 (West Columbia substation area), confidence=low.**

## T7 start
Wrote triage_findings.json + triage.md. Turns used: ~28. Run complete.

## Deep scan started 2026-07-19

### Stage 1 — LLC / Developer
- TX Comptroller franchise tax search: redirects, JS-rendered; no result retrieved for "First Capitol BESS"
- SEC EDGAR search: HTTP 403
- LinkedIn: auth wall, no results
- Web searches (DDG, Bing): previously blocked in triage — no developer name found
- **Result: developer identity unknown**

### Stage 2 — County records
- Brazoria CAD portal (esearch.brazoriacad.org): 404 on search URL; portal.brazoriacad.org is login-required
- BIS Consultants CAD backend: no accessible owner-search API found
- TX Ch.313/JETI: not applicable (project entered queue 2023, after 2022 expiry)
- TCEQ: BESS project, no air permit expected
- PUCT Interchange: fully JS-rendered, no curl-accessible API; "First Capitol BESS" as filing party: no results accessible
- **Result: 0 county parcels found; no abatement; IA not retrieved via portal**

### Stage 3 — Site pinpoint
- POI: "Tap 138kV West Columbia Main (39500) - Sweeny Cogen (110505)"
- Sweeny Cogeneration (OSM): 29.0728, -95.7446 → Old Ocean, Brazoria County [Phillips 66 complex]
- West Columbia city center (Nominatim): 29.1439, -95.6452
- POI description = tap on 138kV line BETWEEN West Columbia Main substation and Sweeny Cogen
- West Columbia Main 138kV substation location: NOT in OSM under that name; likely along TX-36 corridor between West Columbia and Old Ocean
- Estimated BESS location: near West Columbia Main substation, ~29.12–29.15, ~95.65–95.69
- **Site pinpoint: low confidence; no Google Places pin; no CAD parcel**

### Stage 4 — Imagery
- 2026-06-15, 2km chip around West Columbia (29.144,-95.645): heavily clouded, town center only visible
- 2025-09 4km chip (29.11,-95.68): partly cloudy; no BESS pad visible in clear areas
- 2025-12 4km chip (29.11,-95.68): mostly clear; shows West Columbia (upper right), agricultural fields center; no industrial BESS pad visible
- Sweeny Cogen 2km chip: large Phillips 66 refinery complex clearly visible; no new construction adjacent
- **Construction stage: no_activity based on Dec 2025 imagery (but site not precisely located)**

## Synthesis complete 2026-07-19

**Verdict: real_early** — IA signed 2025-05-15 is confirmed in ERCOT queue milestones; 6.9(1) passed 2025-02-12. Project cleared real contractual gates. However:
- No construction visible in Dec 2025 Sentinel-2 imagery at estimated location
- Developer entirely unknown (0 hits across all sources)
- PUCT IA PDF not retrieved (portal JS-rendered)
- 5 prior COD slips in 34 snapshots (net +17 months)

**Independent COD: 2028-Q2, drift risk HIGH**

Wrap-up: queue_history.py done (timeline.md already existed); build_brief.py → brief.html (7KB); build_index.py → 83 projects indexed.
