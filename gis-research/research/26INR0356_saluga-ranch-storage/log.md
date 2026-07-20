# Triage log — Saluga Ranch Storage (26INR0356)

## T1 start
- queue_history.py: 30 snapshots, 2024-01-01 → 2026-06-01
- Screening started 2024-02-02; Screening complete 2024-04-29
- FIS requested 2024-01-08; FIS approved: NOT ACHIEVED
- IA signed: NOT ACHIEVED; all 6.9 milestones: NOT ACHIEVED
- COD drift: 2026-07-31 → 2027-08-25 (slipped ~13 months, 1 change)
- Capacity bump: 105.98 MW → 125.4 MW (as of 2025-02-01)
- No construction dates, no energization/sync/COA milestones
- Status: early-stage (screening done, FIS pending, no IA)

## T2 start
- gmaps.py: HTTP 429 on first call; retry also 429 — portal blocked, budget spent
- No delivery pins found (normal for pre-construction battery project)

## T3 start
- DDG: CAPTCHA block — no results
- Bing "Saluga Ranch Storage" + "Texas battery": no results (unrelated content)
- Bing "Saluga Ranch Storage LLC" OR "26INR0356": no results
- Bing "Saluga Ranch" Dimmit County energy storage: no results
- No developer name, press release, or LLC registration found
- No sources/ files to save

## T4 start
- PUCT Interchange FilingParty search: HTTP 402 (portal blocked)
- PUCT Interchange Description search: HTTP 402 (retry also blocked)
- No IA found

## T5 start
- TX Comptroller Ch.313 page: no searchable DB returned in content
- JETI domain (jeti.comptroller.texas.gov): ENOTFOUND — domain not resolving
- Bing JETI Dimmit County battery storage: no results
- No abatement found; normal for post-2022 battery project (Ch.313 expired 2022)
- Ch.313 expired Dec 2022; JETI portal inaccessible — normal miss

## T6 start
- Site candidate: Asherton city center ~28.44°N, 99.76°W (POI substation = Asherton 8283, 138kV)
  — city-center used as proxy; confidence LOW (no pin, no IA map, no abatement map)
- cdse.py 3×3 grid (lats 28.41/28.44/28.47, lons -99.79/-99.76/-99.73), buffer-km 2, date 2026-06-01
- All 9 chips: HTTP 401/403 — CDSE credentials not valid in this environment
- No imagery obtained; construction verdict: UNKNOWN

## T7 start
- Wrote triage_findings.json and triage.md
- All signals negative; deep scan not recommended
- Turns used: ~24; T6 imagery and T4 PUCT both blocked by auth/portal issues
- STOP
