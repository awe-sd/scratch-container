# Triage log — Cosper Solar (25INR0281)

## T1 start
- 37 snapshots (2023-06-01 → 2026-06-01)
- COD drift: 2025-12-30 → 2026-09-15 → 2027-04-18 → 2027-11-12 (3 changes, ~2yr total slip)
- IA signed: 2025-07-31 (first in 2025-08-01 report)
- FIS approved: 2024-11-01
- Meets 6.9(1): 2025-08-18
- Meets all 6.9: not yet; construction start/end not reported; no energization/sync/COA
- Assessment: real project, IA signed ~1yr ago, pre-construction phase

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts (exact name; name+county). Budget exhausted.
- pins_found: 0 (blocked, not confirmed absent)

## T3 start
- Developer: Gransolar Texas Twenty LLC (SPV); parent = Gransolar Group (Spain), ~48 US projects, ~6.7 GW pipeline
- LLC status: "Forfeited" per tx state records (may be stale/data artifact — common for SPVs)
- PUCT IA filing confirmed: Standard GIA between Oncor and Gransolar Texas Twenty LLC
- KWTX Nov 2023: developer did NOT attend Bell County commissioners court — potential community opposition signal
- EIA completion date: 10/31/2027; ercotqueue.com build-chance: 86%
- news_found: true; saved → sources/t3_web_sweep.md

## T4 start
- PUCT case 35077 confirmed (via DDG): IA filed 2025-07-31 (Item 2238), First Amendment filed 2025-08-26 (Item 2246)
- Both party names confirmed: Oncor Electric Delivery Company LLC + Gransolar Texas Twenty, LLC (Cosper Solar)
- Direct PDF fetch blocked: interchange.puc.texas.gov returns 402 on all URLs — cannot retrieve schedule exhibit
- ia_found: TRUE (case number + filing dates confirmed via DDG); schedule exhibit contents unknown
- Deep scan note: amendment filed ~4 weeks after IA — worth fetching to see if schedule changed

## T5 start
- Ch.313: no results (Cosper Solar / Gransolar Texas Twenty / Bell County) — normal, Ch.313 expired 2022
- JETI: no results — normal for projects in this vintage without confirmed local ISD agreement
- abatement_found: false

## T6 start
- Site candidate: Ding Dong substation area (30.9874, -97.7667) — derived from POI "Tap 138kV 115 Ding Dong - 3630 Copperas Cove Tu"; confidence LOW (infrastructure-derived, no pin or abatement map)
- 3×3 chip grid attempted, 4/9 fetched (403 blocked center + entire south row)
- Contact sheet read: 4 frames cover Killeen/Copperas Cove suburban corridor — no solar panel arrays visible, no construction activity
- construction_visible: false (caveat: center tile blocked; field may be south of grid)
- Budget exhausted; no full-frame reads needed (no activity to zoom in on)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28 of 35 budget

## END
