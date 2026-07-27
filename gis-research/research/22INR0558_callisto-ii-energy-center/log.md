# Triage Log — 22INR0558 Callisto II Energy Center

T1 start
## T1 result
- 57 snapshots (2021-10 → 2026-06), 6 reported-COD changes
- COD drift: Dec-2022 → Dec-2023 → Jun-2024 → Dec-2025 → Jul-2026 → Jul-20-2026 → Oct-2026 (current, held since 2026-05)
- Capacity halved: ~406 MW → 203.2 MW in May 2025
- IA signed 2023-12-11; FIS approved 2025-08-21; Meets all 6.9 milestones 2025-09-11
- No construction start/end or energization milestones visible
- POI: 47150 HO Clarke 138kV; zone HOUSTON; Harris County

T2 start
## T2 result
- gmaps.py returned HTTP 429 on both attempts (rate-limited). Budget exhausted.
- No delivery pins found. Normal outcome.

T3 start
## T3 result
- DDG: bot CAPTCHA, no results
- Bing searches (4 queries): "Callisto II Energy Center battery Texas", LLC + Harris County, 22INR0558 + ERCOT, HO Clarke substation + battery storage
- All queries returned zero relevant hits — no news, no developer PR, no company mentions
- No developer name surfaced to drive alternate searches
- No pages saved to sources/ (nothing found)

T4 start
## T4 result
- PUCT Interchange: found docket 59062 — PGC registration (not IA filing)
- Filing party: Callisto II Energy Center LLC
- Filed: 2025-12-04 (PGC registration / compliance update)
- Developer/parent: Jupiter Power LLC (1108 Lavaca St, Suite 110-349, Austin TX 78701)
- Email domain: @jupiterpower.io; contact David Hernandez (VP Ops), Caitlin Smith (VP Policy)
- Affiliates: Crossett Power Management LLC (PGC), Swoose LLC (PGC), Triple Butte LLC (PGC)
- PHYSICAL SITE ADDRESS: 12100 Hiram Clarke Rd, Houston, TX 77045, Harris County
  (Note: confirms POI "HO Clarke 138kV" — "Hiram Clarke" road variant)
- CenterPoint Energy as Interconnecting TSP; 200 MW Battery Storage; ERCOT/Texas RE
- IA already logged as signed 2023-12-11 (from queue data) — no IA PDF in PUCT Interchange
- Saved PDF: sources/PUCT_59062_PGC_registration.pdf

T5 start
## T5 result
- TX Comptroller Ch.313: portal returned generic pages on all 3 attempts — no searchable data accessible
- JETI registry: texasjetisystem.com not resolvable (DNS failure)
- Ch.313 expired 2022 — normal miss for a 2022-vintage project; JETI is the replacement but unreachable
- No abatement found (expected for post-2022 battery project)

T6 start
## T6 result
- Site candidate: 12100 Hiram Clarke Rd, Houston TX 77045 (from PGC registration PDF — HIGH confidence)
- Geocoded: lat=29.6502, lon=-95.4466
- CDSE chip/chips: HTTP 401 Unauthorized on token grant — credential failure at gis-research.env
- One retry attempted (single chip); same 401. Budget exhausted.
- No imagery obtained. Cannot assess construction status from satellite.
- Imagery blocked note: CDSE credentials need refresh; deep scan should retry.

T7 start
## T7 result
- Written: triage_findings.json, triage.md
- Turns used: ~25
- STOP
