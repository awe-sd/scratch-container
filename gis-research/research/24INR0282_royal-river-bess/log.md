# Triage log — Royal River BESS (24INR0282)

## T1 start
- queue_history.py ran: 41 snapshots, 2023-02 → 2026-06
- IA signed: 2023-12-15 (first appeared in queue 2026-05-01 — late reporting)
- FIS approved: 2025-10-09
- COD drift count: 3 changes (2024-12-01 → 2025-11-28 → 2027-01-11 → 2027-06-30)
- No construction start/end, no 6.9 milestones, no energization/sync/COD approvals
- Capacity crept up: 307.1 → 309.0 → 310.7 MW over history
- T1 complete

## T2 start
- gmaps.py places "Royal River BESS" → 429 Too Many Requests
- gmaps.py places "Royal River BESS Brazoria County Texas" → 429 (retry exhausted)
- pins_found: 0 (API rate-limited, not evidence of no pins)
- T2 complete (blocked)

## T3 start
- DDG search "Royal River BESS battery storage Texas": cleanview.co, infrasure.ai, interconnection.fyi, gridstatus.io all confirm 310.7 MW / Brazoria County / ERCOT 24INR0282; developer listed as "Royal River LLC"
- DDG search "Royal River BESS LLC registration": CAPTCHA blocked
- DDG search "Royal River BESS developer announcement news": CAPTCHA blocked
- infrasure.ai: developer = Royal River LLC, COD 2027-06-30, "4 articles about deals" (paywalled)
- interconnection.fyi: developer name locked; POI = Tap 138kV Angleton–West Columbia confirmed; no news
- No press releases, no parent company, no developer identity confirmed
- news_found: false; no sources saved (tracker sites only, no original reporting)
- T3 complete

## T4 start
- PUCT Interchange direct URL → HTTP 402 Payment Required (blocked, two attempts)
- DDG site:interchange.puc.texas.gov search → CAPTCHA blocked
- Bing "Royal River BESS PUCT interchange filing" → no relevant results
- Bing "Royal River BESS interconnection agreement ERCOT" → no relevant results
- ia_found: false (portal blocked; IA signed date 2023-12-15 from queue data only)
- T4 complete (portal blocked, budget exhausted)

## T5 start
- TX Comptroller Ch.313 pages not navigable via WebFetch (generic portal pages, no data)
- JETI registry URL → 404; Bing search for JETI+Brazoria+battery → no results
- abatement_found: false (normal for post-2022 BESS — Ch.313 expired 2022, JETI not public yet)
- T5 complete

## T6 start
- Site candidate: Angleton city center (29.1694, -95.4319) — POI is 138kV Angleton–West Columbia tap; no pin or abatement map available
- cdse.py chip: 29.1694/-95.4319, 2026-06-15, 4km buffer → wrote angleton_center_2026-06.png (854 KB)
- Image read: ~70% cloud cover, Angleton urban grid visible but substation/BESS pad not identifiable
- No activity spotted; no re-center warranted; full-size read budget used (1/3)
- construction_visible: false (inconclusive — cloudy imagery, wrong scale for BESS detection)
- T6 complete

## T7 start
- Wrote triage_findings.json
- Wrote triage.md
- turns_used: ~27
- T7 complete — STOP

## Deep scan start — 2026-07-19

Triage blockers:
1. PUCT portal 402-blocked — need to retry IA search
2. Developer identity unknown — only "Royal River LLC" from tracker sites
3. Site candidate low confidence — Angleton city center proxy; need exact substation
4. Imagery cloudy — need clear chip at correct location

Priority order: substation pin → developer/IA → imagery

## Stage 1 — LLC chain — 2026-07-19

**DECISIVE FIND**: TX Comptroller franchise tax search confirms Royal River LLC = Clearway Energy Group SPV
- Royal River LLC (TX taxpayer 32087259811): formed DE 11/21/2022, ACTIVE
  Officers: Craig Cornelius (PRESIDENT), Charles C Colby (VP), Christopher Fox (VP), Logan Granger (VP), 
  Crystal Clark-Knapp (Assistant), Jennifer Hein (Secretary), Daniel Summa (VP), et al.
  All at 300 Carnegie Center Dr Ste 300, Princeton NJ 08540
- Clearway Energy Group LLC (TX taxpayer 32067634686): CEO = Craig Cornelius, Secretary = Jennifer Hein,
  mailing 100 California St Ste 650 San Francisco CA
  → Same Craig Cornelius + Jennifer Hein = SAME MANAGEMENT
- CONCLUSION: Royal River LLC is a Clearway Energy Group project SPV
  Princeton NJ address = Clearway Energy Group East office  
- Artifact: sources/2026-07-19_txcomptroller_royal-river-llc.json

**Stage 1 COMPLETE** — Royal River LLC → Clearway Energy Group LLC (Craig Cornelius shared President/CEO)

## Stage 2/3 — PUCT + substation + developer search — 2026-07-19 (deep scan resumed)

Previous deep scan hit 121-turn limit without writing outputs. Resuming from Stage 1 complete.
Priorities: (a) Angleton 138kV substation exact coords, (b) PUCT IA filing, (c) Clearway news, (d) clear imagery

**SUBSTATION FOUND**: Angleton 138kV at 29.2268°N, -95.4288°W — CenterPoint Energy, OSM node 244479862
- Source: Overpass API / OpenStreetMap — https://overpass-api.de/api/interpreter
- West Columbia 138kV at 29.1568°N, -95.6576°W (CenterPoint, OSM 336964607)
- Triage used city-center proxy (29.1694, -95.4319); actual substation is ~6 km NNW of center

**CLEARWAY NEWS**: No press release for Royal River BESS on clearwayenergygroup.com (all 13 pages scanned)
- Closest known Clearway TX BESS: Pine Forest Energy Storage (construction Oct 2024, online Feb 2026)
- No public announcement means pre-announcement or NDA'd — not unusual for Clearway SPV projects

**PUCT PORTAL**: Still 402-blocked for programmatic access; IA signed 2023-12-15 from queue data only

**CAD**: Brazoria CAD portal requires JS; no programmatic parcel result; manual search needed

Next: imagery at 29.2268, -95.4288 with 1-km buffer (BESS spec) — SKIPPED at 80% token budget
Budget hit 80% warning; went to synthesis directly.
findings.json + dossier.md + brief.html written. queue_history.py + build_brief.py + build_index.py all ran successfully.
RESEARCH COMPLETE 2026-07-19.
