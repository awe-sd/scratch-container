# Research log — Coyote Ridge BESS (27INR0432)

## T1 start
queue_history.py: 18 monthly snapshots (2025-01-01 → 2026-06-01)
COD drift: 0 changes — 2027-10-06 held steady since 2025-01-01
Milestones: Screening started 2025-01-28, Screening complete 2025-04-17, FIS requested 2025-01-15
NO milestones beyond screening: FIS not approved, no IA, no 6.9, no construction dates
Still early-stage: FIS requested but not approved after 18 months.
T1 complete (2 tool calls used)

## T2 start
gmaps.py: HTTP 429 on first call; retried once → 429 again. API rate-limited. No pins found.
T2 complete — 0 pins (API blocked, budget exhausted)

## T3 start
Developer identified: Grenergy USA (Spanish renewables developer, US arm)
No press releases or official announcements found — only tracker databases reference the project
Sources: ercotqueue.com, infrasure.ai, cleanview.co, interconnection.fyi all list Grenergy USA as developer
grenergy.eu/en/markets/usa/ → 404; no direct project page found
LLC registration not found in web search (Texas SOS not scraped — deferred to deep scan if warranted)
T3 complete (5 calls used, budget exhausted)

## T4 start
PUCT Interchange: all attempts (search page, FilingParty, Description) → HTTP 402. Portal blocked.
No IA or PUCT filings retrievable via WebFetch. No IA found.
T4 complete — ia_found: false (portal blocked, budget exhausted at 3 calls)

## T5 start
TX Comptroller Ch.313 page: no searchable database accessible via WebFetch
JETI search: no results for Coyote Ridge or Grenergy in Brown County
No abatement found. Normal for post-2022 project (Ch.313 expired; JETI registry incomplete).
T5 complete — abatement_found: false (3 calls used)

## T6 start
POI "292 Holder 138 kV": no coordinates found in web search (DDG, infrasure.ai all return county-level only)
No pin from T2 (API blocked), no abatement map, no IA map
Best site estimate: "somewhere in Brown County" — below threshold for imagery
SKIPPING imagery per triage rules: no site candidate
T6 complete (4 calls used, budget 8)

## T7 start
triage_findings.json written
triage.md written
T7 complete — turns used: ~22
