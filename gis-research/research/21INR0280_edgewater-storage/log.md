# Triage log — 21INR0280 Edgewater Storage

T1 start
- queue_history.py ran OK: 87 snapshots, 4 reported-COD changes
- FIS requested 2019-03-24; screening complete 2019-07-04
- NO FIS approved, NO IA signed, NO 6.9 milestones, NO construction dates
- COD drift: 2021-06-28 → 2022-04-15 → 2023-04-15 → 2024-11-01 → 2028-02-29 (current)
- 4 COD slips total; project has been in queue since ~2019; still at early FIS stage
- Capacity: 47.12 MW (2019) → 50.6 MW (2021) → 50.0 MW (2023, current)
- Assessment: project is behind — no IA, no 6.9 approvals after 7 years; COD claim 2028-02-29 is very aggressive given zero milestones cleared

T2 start
- gmaps.py places: 429 Too Many Requests on both attempts (project name; project name + county)
- BLOCKED — 429 rate limit, one retry used, moving on
- pins_found: 0 (inconclusive — API rate-limited, not confirmed absence)

T3 start
- Search 1 (project name + ERCOT): LLC name confirmed = "Edgewater Battery Storage LLC"; Delaware-registered; no IA; third-party trackers give "build-chance 5%"
- Search 2 (Ellis County): Same — confirms no IA, no news or press releases found
- Search 3 (LLC registration): Delaware LLC; no TX filing details, no named principals surfaced
- Search 4 (developer/parent): CAPTCHA block — budget used
- news_found: false; no developer parent identified; Delaware-registered SPV with no known parent
- Sources: ercotqueue.com, infrasure.ai, interconnection.fyi, gridstatus.io, cleanview.co (aggregators, not primary)

T4 start
- interchange.puc.texas.gov: HTTP 402 on all URL patterns tried — site requires session/auth, not accessible via WebFetch
- DDG site: search blocked by CAPTCHA
- ia_found: false (portal inaccessible, not confirmed absence — queue data already shows IA = null)
- No IA PDF retrieved; no milestone-schedule exhibit

T5 start
- TX Comptroller Ch.313 page: no direct county-filter search; JETI not in searchable DB on main page
- Ch.313 applications pages returned only program overview content, not application data
- Budget used without reaching actual data — portal structure requires JS/session navigation
- abatement_found: false (normal for post-2022 battery project; Ch.313 expired end of 2022; JETI not searchable via WebFetch)

T6 start
