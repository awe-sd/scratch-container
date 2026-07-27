# Triage log — BRP Ampato BESS (23INR0074)

## T1 start
- queue_history.py run: 71 snapshots, 2 COD changes
- COD drift: 2023-03-31 → 2024-12-01 → 2027-12-01 (drifted twice, now 4 years past original)
- FIS requested 2020-08-24; FIS approved: NEVER. IA signed: NEVER. No construction milestones.
- Only milestones hit: Screening started (2020-08-04), Screening complete (2020-10-28), FIS requested (2020-08-24)
- Capacity stable at 121.56 MW since 2020-09
- Result: project is stuck pre-FIS-approval since entry in 2020 — 6 years, 0 post-screening progress

## T2 start
- gmaps.py places: HTTP 429 on "BRP Ampato BESS" and "BRP Ampato BESS Crane County" — rate-limited, 1 retry used, blocked
- No pins found
- Result: 0 delivery pins

## T3 start
- Search 1 "BRP Ampato BESS battery storage Texas": 5 tracker hits (cleanview, infrasure, ercotqueue, interconnection.fyi, gridstatus) — all aggregators of ERCOT data, no independent reporting
- Search 2 "BRP Ampato LLC registration": LLC confirmed — Delaware foreign LLC, registered TX 2020-07-21, active; Dallas/Houston/Dover DE addresses; no parent company identified
- Search 3 "BRP Ampato" OR "BRP Energy" announcements: zero results
- ercotqueue.com flags 4% build-chance; 1 project on file, 0 commissioned
- No news articles, press releases, or developer identity beyond LLC name
- Result: news_found = false; LLC confirmed as BRP Ampato BESS, LLC; no developer track record

## T4 start
- PUCT Interchange (interchange.puc.texas.gov): HTTP 402 on all attempts (3 URLs tried) — portal blocked
- DDG site:puc.texas.gov search: no results for "BRP Ampato BESS"
- IA found: false
- Result: no IA, no PUCT documents retrieved

## T5 start
- TX Comptroller Ch.313 page: no direct searchable database found; no Crane County results
- DDG search for Ch.313/JETI + Crane County BESS: no results
- Result: abatement_found = false (normal — post-2022 project with no IA)

## T6 start
- Site candidate: center of Crane, TX (31.397, -102.350) — no pin, no IA map, POI "NS Crane Switch 138kV" implies proximity to Crane city substation; confidence low
- Ran 3×3 chip grid (center 31.397,-102.350, step ±0.03°, buffer-km 2, date 2026-07-01)
- 7/9 chips: HTTP 401/403 (CDSE auth failure — credential issue in ~/.config/gis-research.env)
- 2/9 chips succeeded: 31.367,-102.320 and 31.367,-102.350 (south fringe only)
- Contact sheet read: both frames = bare West Texas scrubland, road grid, small settlement edge; 1 small bright white object (farm structure, not BESS pad); no construction-scale disturbance visible
- Coverage: south fringe only; center/north (most likely area) not imaged
- Result: construction_visible = false; site candidate unconfirmed; imagery inconclusive due to auth failures

## T7 start
- Wrote triage_findings.json and triage.md
- All signals negative; deep scan not recommended
- Turns used: ~28
- Blockers this run: gmaps.py 429, PUCT Interchange 402, CDSE 401/403 on 7/9 chips
