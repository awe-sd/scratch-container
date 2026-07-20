# Triage log — Lupinus Solar 1 (24INR0150)

T1 start

## T1 — Queue history
- 50 snapshots: 2022-05-01 → 2026-06-01
- COD drift (3 changes): 2024-12-30 → 2025-12-31 → 2026-09-21 → 2027-09-13 (current)
- IA signed: 2025-06-26 (first in 2025-07-01 report)
- Meets 6.9(1): 2025-08-05
- FIS requested 2022-05-11; FIS approval: NOT achieved
- Construction start/end: NOT reported
- Capacity: 164.86 MW (2022-05 → 2025-11) → 162.31 MW (2025-12 → present)
- Status: IA signed, 6.9(1) met, but no FIS approval, no construction milestones

T2 start

## T2 — Delivery pins
- gmaps.py: HTTP 429 (rate-limited) on all 2 attempts; tool blocked for triage
- No pins obtained. Normal result.

T3 start

## T3 — Web sweep
- Developer: Sunraycer Renewables (Crayhill Capital portfolio company)
- SPV: Lupinus Solar, LLC; early-stage developer: Diode Ventures
- $901M project financing closed 2026-05-14 (MUFG, Ally Bank, Nomura, Nord/LB, SocGen)
- Portfolio: Eagle Springs + Lupinus 1 + Lupinus 2 (479.5 MWac solar + 236.5 MWac BESS)
- Google PPAs backing Lupinus projects
- Groundbreaking: 2026-03-17 (construction confirmed underway)
- Eagle Springs targets late 2026 COD; Lupinus sites targeting 2027
- Sources saved to sources/web_sweep_summary.md
- gem.wiki: 403 blocked; DuckDuckGo CAPTCHA on two queries; 3 aggregator sites returned rich data

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all direct fetch attempts (portal requires session/auth)
- DDG search for PUCT docket "Lupinus Solar": no docket number surfaced
- IA existence CONFIRMED via T1 (iaSigned = 2025-06-26) + T3 (press coverage); PDF not retrieved
- No milestone schedule exhibit obtained; deep scan should attempt authenticated PUCT access

T5 start

## T5 — Abatements
- TX Comptroller Ch.313: portal returned overview pages only; no searchable table accessible via WebFetch; no Franklin County solar entry found
- JETI: DDG search returned no JETI applications for Lupinus/Sunraycer/Franklin County
- Normal for post-2022 project (Ch.313 expired 2022); JETI miss expected at triage without direct portal access
- Deep scan: try authenticated Comptroller ch313 data export + JETI portal directly

T6 start

## T6 — Imagery
- Site candidate assessment: no pin from T2 (gmaps blocked), no coords from aggregators (cleanview/interconnection.fyi), OpenInfraMap rendered no data, no groundbreaking press release with location
- Best available: "Franklin County, TX" — county-level only; no specific parcel or intersection
- Per checklist: no site candidate better than county → SKIP imagery
- Note: construction IS confirmed (groundbreaking 2026-03-17, financing closed). Deep scan should resolve site location first (county permit records, Texas Railroad Commission, or ERCOT GIS node map) then run imagery.

T7 start

## T7 — Final outputs
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP
