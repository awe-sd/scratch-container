# Triage log — Anson BAT (22INR0457)

## T1 start
- queue_history.py ran: 52 snapshots (2022-03-01 → 2026-06-01)
- COD drift: 6 changes — 2023-12-29 → 2024-12-28 → 2025-12-31 → 2026-05-29 → 2026-08-01 → 2026-09-01 → 2027-12-01 (current)
- Milestones achieved: screening started 2020-12-03, screening complete 2021-02-19, FIS requested 2022-02-23, **IA signed 2024-08-15**, FIS approved 2025-03-19, Meets 6.9(1) 2025-02-12
- No construction start/end, no energization/sync/COA dates
- Capacity stable at 153.55 MW as of 2025-07-01
- T1 result: project is post-IA, post-FIS-approval, pre-construction. 3+ year COD slip; currently targeting 2027-12-01.

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts ("Anson BAT", "Anson BAT LLC Jones County") — rate-limited, tool budget exhausted
- T2 result: 0 pins found (tool blocked, not a signal about project)

## T3 start
- DDG search "Anson BAT battery storage Texas": developer identified as ENGIE / "Anson II Storage LLC"; project linked to ENGIE's Anson 2 solar project (200 MW, Jones County); Meta 200 MW EAPA deal noted for the solar plant
- DDG "Anson II Storage LLC Texas": registered as foreign LLC in Texas 2022-08-26; no ENGIE attribution in those results
- DDG "Anson 2 solar storage ENGIE": solar component confirmed ~200 MW, expected operations late 2025; no battery component mentioned explicitly
- No press releases specifically about the battery project; no construction announcements
- T3 result: developer = ENGIE North America (Anson II Storage LLC); co-located with Anson 2 solar; news_found = true (developer/co-project confirmed)

## T4 start
- PUCT Interchange portal returns 402 (session auth required); direct URL attempts blocked
- DDG search surfaced: PUCT case 35077, item 1981 — Standard Generation Interconnection Agreement filed 2024-11-13
  - TSP: Lone Star Transmission, LLC; Generator: Anson II Storage LLC
  - Confirms 150.6 MW battery, Jones County, 22INR0457, proposed COD 2027-12-01
  - "slight deviations from standard form" noted
  - PDF at interchange.puc.texas.gov also 402-blocked; milestone schedule exhibit not retrievable
- T4 result: ia_found = true (PUCT 35077, filed Nov 2024); schedule exhibit blocked/CEII-unclear — deep scan should pull PDF directly

## T5 start
- Comptroller Ch.313 page returned generic content; no direct project search available
- DDG search found: "Jones City Energy Storage, LLC" filed tax abatement (likely Ch.312 county) in Jones County, discussed at Commissioners Court 2025-10-10 for a battery energy storage system
- Also found: ENGIE "Anson Solar Center" Phase I/II in Jones County — $250K road-use payment + Phase II abatement negotiations ongoing (Oct 25 vote)
- No JETI application found (post-2022 project; absence is normal)
- T5 result: abatement_found = true (county-level Ch.312 type for "Jones City Energy Storage LLC", likely same site); ENGIE presence confirmed; deep scan should pull the abatement docs to confirm LLC = Anson II Storage, and get JETI status

## T6 start
- Site candidate: 32.5618°N, -99.6887°W (from DDG — water quality DB entry for "LK Fort Phantom Hill Power Plant"); confidence LOW — near lake, may not be at the 345 kV substation tap
- Ran chips at --buffer-km 2 for 2026-05-01, 2026-06-01, 2026-07-01; generated contact sheet
- Contact sheet read: imagery shows Fort Phantom Hill lake shoreline + agricultural fields; no substation infrastructure or battery container rows visible; June chip has cloud cover; no construction signal
- T6 result: construction_visible = false; site candidate confidence low (lake proxy coordinates, not confirmed substation location); deep scan should geolocate Phantom Hill 345 kV substation precisely and re-run tighter chip

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~28
- STOP
