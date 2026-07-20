# Research log — Ariji BESS (25INR0143)

## T1 start
- queue_history.py ran: 37 snapshots (2023-06-01 → 2026-06-01)
- Milestones: screening complete 2022-12-13, FIS approved 2025-03-03, IA signed 2025-08-01, Meets 6.9(1) 2026-03-24
- COD drift: 2026-04-21 → 2026-09-14 → 2027-06-28 (2 drifts)
- No construction milestones reported yet
- Capacity stable at 100.32 MW since 2023-08

## T2 start
- gmaps.py places: HTTP 429 on both attempts (rate-limited). No pins found. Logging negative.

## T3 start
- "Ariji BESS" DDG sweep: hits on InfraSure, interconnection.fyi, FutureGrid, Cleanview (all queue trackers, no original news)
- Developer confirmed: Ariji BESS, LLC; contact: Hyohuan Lee, 13501 Katy Freeway Suite 3200, Houston TX 77079
- IA confirmed: PUCT Docket #35077, Oncor TSP, signed 2025-08-01 (matches timeline)
- Chapter 381 Economic Development Agreement found: Howard County (note: Ch.381, not Ch.313)
- No major news/PR articles found for this project
- LLC registration search: CAPTCHA blocked, no data

## T4 start
- PUCT Interchange docket search (FilingParty=Ariji BESS): HTTP 402 (auth required)
- PUCT Docket 35077 direct URL: HTTP 402 (auth required)
- IA existence confirmed by T3 web results (signed 2025-08-01, Oncor TSP); PDF not retrieved
- Deep scan should attempt PUCT Interchange session auth for Docket 35077 to get milestone schedule exhibit

## T5 start
- TX Comptroller Ch.313 list: page returned overview only, no searchable list retrieved
- JETI registry page: same issue, no list
- Howard County Ch.380/381 PDF (assets.comptroller.texas.gov/dat/ch380/0011284/0011284-Howard.pdf): file too large to fetch (>10MB)
- T3 results confirmed a Ch.381 (not Ch.313) Economic Development Incentive Agreement in Howard County for this project
- Ch.313 program ended 2022; post-2022 project using Ch.381 is normal — no JETI application found (expected for 100 MW BESS)
- Deep scan: attempt to download the Ch.381 agreement PDF directly or via alternate means

## T6 start
- Site candidate: ~32.25°N, -101.48°W (Big Spring TX, Howard County seat; POI "BIGSPRIG_8" = Big Spring substation; no precise pin available)
- cdse.py chip: HTTP 401/403 — CDSE credentials not loaded in this session. All 9 grid chips failed.
- No imagery retrieved. Construction verdict: unknown.
- Deep scan: fix CDSE credentials, then run 3x3 grid around Big Spring substation (~32.25, -101.48)

## T7 start
- triage_findings.json written
- triage.md written
- Total turns used: ~22
- STOP
