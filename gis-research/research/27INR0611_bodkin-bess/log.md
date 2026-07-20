# Triage log — Bodkin BESS (27INR0611)

## T1 start
- queue_history.py ran OK; 4 snapshots (2026-03-01 → 2026-06-01)
- Milestones achieved: Screening started 2026-04-02, Screening complete 2026-06-30, FIS requested 2026-03-23
- No FIS approved, no IA signed, no construction milestones
- COD drift: 2027-06-16 (held 2026-03 → 2026-04) → 2027-12-01 (held 2026-05 → 2026-06); 1 drift event
- Status: very early stage (pre-IA, pre-FIS-approval); only 4 months in queue

## T2 start
- gmaps.py: 429 Too Many Requests on first call; retry also 429 — logged negative per rules
- Fallback web search: no map pins or coordinates found for "Bodkin BESS"; county-level only
- LLC name "Bodkin BESS, LLC" confirmed; TX Tax ID 32103362250, incorporated 2025-12-09
- pins_found: 0

## T3 start
- DDG: CAPTCHA-blocked after 1 try; no retry per rules
- Bing searches (3): all returned results about Netflix show "Bodkin" — no project hit
- TX Comptroller lookup: redirected to search landing page (no direct entity lookup available)
- No news, press releases, or developer identity found
- LLC name "Bodkin BESS, LLC" is the only confirmed entity; parent developer unknown
- news_found: false

## T4 start
- interchange.ercot.com: DNS not found (ENOTFOUND)
- ercot.com/services/rq/ie/index.html: 404
- bing search site:ercot.com: CAPTCHA blocked
- interchange.puc.texas.gov: 402 Payment Required (all URL variants)
- No IA filing found; portal blocked; cannot confirm IA
- ia_found: false

## T5 start
- TX Comptroller Ch.313 page: general overview only; no direct county-level query available via WebFetch
- Bing search for JETI/Ch.313 + Bodkin BESS: no hit (Netflix TV show noise)
- No abatement found — expected for post-2022 project (Ch.313 expired 2022, JETI not widely used yet)
- abatement_found: false

## T6 start
- Site candidate: Danbury TX town center (29.2283°N, 95.3449°W) from Nominatim; POI is "Danbury Dab DANBUR_POI_8" 138kV substation, likely near/in Danbury TX (Brazoria Co.)
- cdse.py chip: 401 Unauthorized on token endpoint (CDSE credentials in ~/.config/gis-research.env not authenticating); all 9 grid chips failed
- One retry done; per rules: logging negative, no engineering around blocked portal
- construction_visible: false (imagery not obtainable)

## T7 start
- triage_findings.json written
- triage.md written (10-line table)
- Turns used: ~28
- STOP
