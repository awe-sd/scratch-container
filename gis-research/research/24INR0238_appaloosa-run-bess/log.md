# Triage log — 24INR0238 Appaloosa Run BESS

T1 start
## T1 — Queue history
- 52 snapshots (2022-03-01 → 2026-06-01)
- Milestones: Screening started 2022-03-07, Screening complete 2022-06-02, FIS requested 2022-03-01
- NO FIS approved, NO IA signed, NO construction milestones, NO 6.9 gates
- COD drift: 2024-08-30 (held 2022-03 → 2024-01) → 2026-08-30 (held 2024-02 → 2026-06) — 1 drift, 2-year slip
- Capacity changes: 200.5 MW (2022-03 → 2024-06) → 100.0 MW (2024-07 → 2025-01) → 103.0 MW (2025-02 → 2026-06)
  - Significant downsize: halved from 200.5 → ~103 MW
- Red flags: No FIS approval, No IA, COD already slipped 2 years, capacity halved

T2 start
## T2 — Delivery pins
- gmaps.py: HTTP 429 on both attempts (rate-limited). Budget spent.
- No pins found. Normal for BESS projects.

T3 start
## T3 — Web sweep
- DDG mostly CAPTCHAed; one live result from first query via ercotqueue.com aggregator
- Developer name surfaced: "Appaloosa Run Storage, LLC" (from ercotqueue.com result snippet)
- Sources mention: ercotqueue.com, infrasure.ai, cleanview.co, interconnection.fyi — all trackers, no primary press
- Build probability cited: ~4% (infrasure.ai/interconnection.fyi aggregator estimate — no IA)
- No news articles, press releases, or official developer announcements found
- LLC registration search: CAPTCHA blocked
- ercotqueue.com project page: fetched but returned minimal content
- No pages directly about this project saved to sources/ (nothing primary found)

T4 start
## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all endpoints (FilingParty search, Description search, root)
- Portal blocked — one retry attempted, still 402. No IA found.

T5 start
## T5 — Abatements
- TX Comptroller Ch.313 page: no filterable agreement data accessible via WebFetch — page keeps returning overview/index content, not agreement list
- JETI registry: same — overview page only, no project-level data accessible
- No abatement found for Appaloosa Run BESS / Upton County
- Normal: post-2022 battery project; Ch.313 expired 2022; JETI is new and sparse
- Result: no abatement found (expected)

T6 start
## T6 — Imagery
- Site candidate search: POI = "New Palouse 138kV (#60278)", Upton County TX
- Nominatim: no results for "New Palouse Upton County Texas"
- DDG searches for substation #60278 / New Palouse: all CAPTCHAed or empty
- OpenStreetMap substation query for Upton County: empty
- No pin from T2, no abatement map, no IA map
- Best estimate: "somewhere in Upton County" — below threshold for imagery run
- SKIPPING imagery per checklist rule ("no site candidate")

T7 start
## T7 — Output written
- triage_findings.json: written
- triage.md: written
- Turns used: ~28
- All negative: paper project, no deep scan recommended
