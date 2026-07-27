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

## Deep scan D1 (2026-07-20 continuation) — IA schedule extraction
- PDF pages 27-28 (Exhibit B): NTP Need Date 2024-11-01; TIF In-Service (backfeed) later of 2026-10-16 or 24 months NTP; Trial Op (sync) later of 2026-10-30 or 2 weeks after TIF; COD later of 2027-07-01 or 2 months after TIF
- Financial security (Exhibit E): $27,750,000 Corporate Guaranty or ILOC
- TSP options: Section 4.1.A chosen (not liquidated-damages option)
- IA Exhibit D: Generator = Funston Solar, LLC c/o NextEra Energy Resources, LLC, 700 Universe Blvd, Juno Beach FL 33408 — developer chain confirmed
- IA Attachment C-3 (p47): Project Overview Map extracted → sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA_map_p47.png — shows project footprint N of village Funston, bounded approx CR 254 (N), CR 266 (S), FM-220 (W), CR 265 (E); Generator Step-Up Station on CR 260; New LST Footloose station to west connected by 1.38-mi 345kV line
- No amendments found to this IA

## Deep scan D2 (2026-07-20) — EIA history
- eia_history.py output: plant 67359 'Funston Solar', entity 'Funston Solar, LLC'
- EIA planned COD: 2025-12 (2024-03→2024-11); 2026-12 (2024-12→2026-05) — developer tracking 2026-12 in EIA vs 2027-07-01 in queue
- EIA status: P Planned (2024-03→2025-11); U Under construction ≤50% (2025-12→2026-02); V Under construction >50% (2026-03→2026-05)
- EIA capacity: 204.0 MW (2024-03→2025-01); 350.0 MW (2025-02→2026-05) — grew to near-final nameplate
- Coordinates: 32.78367, -99.72019 (Jones Co) — authoritative EIA position
- Wrote eia_history.json

## Deep scan D3 (2026-07-20) — spv.py, ch313.py
- spv.py resolve 29INR0015: EIA860m confirmed Funston Solar, LLC (name match); PUCT index confirms filing 35077-1965 2024-10-30
- ch313.py resolve 29INR0015: NEGATIVE — no Ch.313 or JETI match; expected for post-2022 solar project
- gmaps.py places "Funston Solar": NO RESULTS
- gmaps.py places "Funston Solar LLC Jones County": returned "Jones City Solar" at 32.822247,-99.986384 — unrelated project; no Funston Solar pin
- gmaps.py staticmap: HTTP 403 (Maps Static API not enabled)

## Deep scan D4 (2026-07-20) — timelapse attempt
- cdse.py timelapse 2024-01-01→2026-07-01: RemoteDisconnected (CDSE down)
- cdse.py chip 2025-01-01, 2025-07-01: RemoteDisconnected (CDSE down)
- Conclusion: Cannot bracket first_activity_seen; rely on EIA status transition U→V (≤50%→>50%) at 2026-03 as proxy

## Deep scan D5 (2026-07-20) — search attempts (all failed)
- search.py "Funston Solar NextEra Jones County Texas": SEARCH FAILED
- search.py "ESI Energy Funston Solar 351 MW Jones County Texas 2027": SEARCH FAILED
- search.py "\"Funston Solar\" Texas 2024 2025 2026": SEARCH FAILED
- search.py "Jones County Texas solar farm 2025 2026 construction Anson": SEARCH FAILED
- search.py "NextEra Energy solar Jones County Texas CR 267": SEARCH FAILED
- search.py Jones County CAD parcel lookup: SEARCH FAILED
- Result: All web searches blocked; CAD not retrieved; no news/PPA found
- Negative evidence count: 8 searches failed

## Imagery refresh (user-directed, 2026-07-21)
Site confirmed correct (EIA plant 67359 pin). Old chips cropped the complex's western
half; series refetched at 32.795,-99.745 (11x8km rectangular): 2025-03/07 fenced-only ->
2025-11 grading -> 2026-03 racking -> 2026-07-20 majority racked, eastern blocks paneled.
Verdict substantially_complete stands, now with a complete-frame 5-date progression.
