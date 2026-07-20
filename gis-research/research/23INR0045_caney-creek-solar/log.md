# Triage log — Caney Creek Solar (23INR0045)

T1 start

## T1 — Queue history

queue_history.py: 65 snapshots (2021-02-01 → 2026-06-01), 3 COD changes.

COD drift:
- 2023-06-01 held 2021-02 → 2022-11 (original COD)
- 2024-06-01 held 2022-12 → 2023-04
- 2025-05-15 held 2023-05 → 2024-12
- 2027-06-21 held 2025-01 → 2026-06 (current)

Milestones achieved:
- Screening started: 2020-09-25
- Screening complete: 2020-12-16
- FIS requested: 2021-02-22
- IA signed: 2021-12-29
- Meets 6.9(1): 2021-12-13

Not achieved: FIS approved, Meets all 6.9, construction start/end, approved for energization/sync/COD.

Capacity: 102.6 MW → 121.97 MW (2021-03) → 121.04 MW (2025-10, current)

Key signals: IA signed Dec 2021 — project cleared first financing gate. COD has slipped 4 years total (2023→2027). No construction milestone in the queue data. FIS approval missing despite IA signed (unusual gap to note).

T2 start

## T2 — Delivery pins

gmaps.py: HTTP 429 (rate-limited) on all attempts — 1 initial + 1 retry. No pins found.
Result: 0 pins.

T3 start

## T3 — Web sweep

DDG search: "Caney Creek Solar Texas news" → multiple hits.

Developer confirmed: HEP Caney Creek Solar LLC / HEP Aquamarine Holdings LLC (Louisville, CO; TX foreign LLC registered 2020-09-11).
Financing: secured from Solareit (Virginia-based real estate company) per local opposition site.
Location detail: east of FM 47, south of I-20, Van Zandt County — 600+ acres.
Easements: six property owners leased easements to HEP Caney Creek Solar LLC for grid interconnection.
PUCT filing: Jan 2022 IA filing by Rayburn Country Electric Cooperative (control number 35077).
Local opposition group: savevzcounty.org tracks the project as "Active," build start Summer 2026.
Third-party aggregators (interconnection.fyi, ercotqueue.com, cleanview.co) confirm 121 MW, Jun 2027.

Saved: sources/savevzcounty_caney_creek.md

T4 start

## T4 — PUCT Interchange

Control number 35077 surfaced in T3 (Rayburn Country Electric Cooperative IA filing, Jan 2022).
All PUCT Interchange URL patterns returned HTTP 402 — portal requires session auth / subscription.
IA existence confirmed via T3 web sweep (queue milestone also shows iaSigned = 2021-12-29).
PDF content not retrievable; milestone schedule exhibit not obtained.

Result: IA found (confirmed via queue data + T3 reference), but PDF inaccessible during triage.
ia_found = true (queue milestone), PDF content = unavailable.

T5 start

## T5 — Abatements

TX Comptroller Ch.313 portal: dynamic site, not fetchable as static HTML — no table returned.
JETI registry: DDG search returned no results for Caney Creek Solar / HEP Caney Creek.
No Ch.313 application found; no JETI application found.
Normal for post-2022 project (Ch.313 expired Sep 2022; JETI launched 2023, filings sparse).

Result: abatement_found = false.

T6 start

## T6 — Imagery

Site candidate derived from T3: east of FM 47, south of I-20, Van Zandt County TX (~32.44N, -95.82W, medium confidence).
cdse.py: HTTP 401 Unauthorized on all chip requests — CDSE credentials not available in ~/.config/gis-research.env for this session.
No imagery obtained; contact sheet not produced.

Result: construction_visible = false (no imagery), construction verdict = unknown.

T7 start

## T7 — Write and stop

Wrote triage_findings.json and triage.md.
Turns used: ~28. STOP.
