# Triage log — Funston Solar (29INR0015)

T1 start

## T1 — Queue history
- 27 snapshots, 2024-04-01 → 2026-06-01
- COD drift: 0 (stable at 2027-07-01 since first appearance)
- IA signed: 2024-10-23 ← strong signal
- FIS approved: 2025-12-17
- Meets 6.9(1): 2025-09-15; Meets all 6.9: 2026-01-28
- No construction start/end or energization dates
- Capacity settled 355.22 → 351.4 → 351.1 MW (minor trims, no major rescope)
- Result: Well-advanced milestones; IA exists; no construction date yet

T2 start

## T2 — Delivery pins
- gmaps.py: HTTP 429 (rate-limited) on both attempts
- No pin coordinates obtained
- Result: BLOCKED — 0 pins

T3 start

## T3 — Web sweep
- Developer: ESI Energy (NextEra Energy subsidiary); SPV: Funston Solar, LLC
- LLC registered in Texas 2024-11-07, Delaware-formed (foreign LLC), TX file 0805782517
- EIA plant code 67359; near Anson, Jones County
- One source lists Nov 2026 COD, another Jul 2027 — two data points, discrepant
- No news/press releases found; no named PPA or offtaker
- Saved: no pages saved (no direct project-article URLs retrieved to save)
- Result: Developer confirmed (NextEra/ESI Energy); news = none

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov returned HTTP 402 on all 3 attempts (portal blocked)
- Note: Queue history confirms iaSigned=2024-10-23 — IA exists in ERCOT system even if PUCT filing not retrievable
- Result: BLOCKED — IA confirmed via queue data, PUCT filing details not retrieved

T5 start

## T5 — Abatements
- Ch.313 expired 2022; project entered queue 2024-02 — ineligible by timing, no Ch.313 expected
- JETI: renewable energy projects explicitly ineligible per program rules
- No abatement found; normal for post-2022 solar project
- Side note: Jones County has other solar activity (ENGIE Anson 2, Lightsource bp Jones City Energy)
- Result: No abatement found (expected)

T6 start

## T6 — Imagery
- Site candidate: lat ~32.784, lon ~-99.670 (EIA data lat=32.784 partial, near Anson/Jones County)
  Confidence: low-medium (lat from FutureGrid/EIA reference, lon estimated from community name + POI)
- Retrieved 3/9 grid chips before CDSE 401 (auth token expired mid-grid): r1_c1, r1_c0, r1_cm1 (all at lat 32.814°)
- chip_r1_cm1 (32.814°N, -99.700°W, buf 2km): lower-left corner shows regular rectangular row pattern — possible panel rows, different from ag fields
- chip_r1_c0, chip_r1_c1: pure agricultural, no construction signal
- Center/south rows (32.784°, 32.754°) not retrieved — auth blocked
- Construction verdict: POSSIBLE signal at edge of coverage, not confirmed; center of site likely slightly south of chips retrieved
- Result: Partial imagery — possible construction signal at edge; deep scan should re-image with fresh auth

T7 start

## T7 — Output written
- triage_findings.json ✓
- triage.md ✓
- Turns used: ~28
- STOP

## Deep scan start — 2026-07-19

## D1 — Google Maps Places (delivery-pin trick)
- gmaps.py: HTTP 429 (rate-limited) on all 3 attempts: "Funston Solar", "Funston Solar LLC", "ESI Energy Funston Jones County"
- Result: BLOCKED — 0 pins; note negative evidence

## D2 — PUCT Interchange IA filing
- Found: PUCT Control No. 35077, Item 1965 — https://interchange.puc.texas.gov/Documents/35077_1965_1438562.PDF
- PDF downloaded: sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf (51 pages, 1.7 MB)
- TSP: Lone Star Transmission, LLC (NOT Oncor — LST is NextEra subsidiary covering Jones County)
- Signed: 2024-10-23
- Milestone schedule (Exhibit B):
  - NTP deadline: 2024-11-01
  - TIF In-Service (backfeed): Later of 2026-10-16 or +24 months from NTP
  - Trial Operation (sync): Later of 2026-10-30 or +2 weeks from TIF In-Service
  - COD: Later of 2027-07-01 or +2 months from TIF In-Service
- Financial security: $27,750,000 (Corp Guaranty or ILOC)
- POI: new "Footloose 345 kV" substation, 1.38-mile new 345 kV line from GIF to LST cut-in on West Shackelford–Phantom Hill Circuit 2
- Plant capacity in IA: 351.4 MW (102 inverters PE FS4105M)
- No amendments found
- Result: COD 2027-07-01 is THE contractual target exactly; $27.75M security is substantial and consistent with real project

## D3 — EIA Form 860 coordinates
- Plant 67359: lat=32.783669, lon=-99.720186
- Address: 3694 CR 267, Anson, TX 79501
- Confidence: HIGH (Form 860 direct record, authoritative)
- Corrects triage lon estimate (-99.720 vs -99.670 estimate)
- Community "Funston" (OSM) at 32.7515, -99.8001 is ~4 miles SW — plant is on CR 266/267 between Anson and Phantom Hill reservoir

## D4 — Imagery: Present chip (2026-07-01)
- Chip: imagery/s2_2026-07-01.png (3km buffer, EIA center 32.783669 / -99.720186)
- STRONG SIGNAL: upper-left quadrant of frame shows MULTIPLE DISTINCT RECTANGULAR BLOCKS with uniform dark row patterns — unmistakably installed solar PV modules
- Arrays appear in multiple sub-blocks separated by access roads, consistent with 350 MW project footprint
- Northern portion of array is in frame; appears to extend beyond image edge to north
- Site is in upper-left, slightly NW of EIA center — array centroid ~32.795-32.81°N
- Construction stage assessment: SUBSTANTIALLY COMPLETE — installed module blocks clearly visible
- Result: REAL ACTIVE project; 2027-07-01 COD plausible given near-complete appearance
- Next: timelapse from ~2yr back to bracket first_activity
