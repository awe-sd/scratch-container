# Triage log — Lyford Energy (24INR0534)

## T1 start
- queue_history.py ran OK: 32 snapshots 2023-11-01 → 2026-06-01
- Milestones: Screening started 2023-03-08, Screening complete 2023-06-05, FIS requested 2023-10-24 (first appeared 2025-04-01 snapshot); all other milestones absent
- COD drift count: 1 change — 2025-09-15 (held 2023-11 → 2025-04) → 2027-09-02 (held 2025-05 → 2026-06)
- Stage: FIS requested, not yet approved. No IA.

## T2 start
- gmaps.py: HTTP 429 on first call; retry on second call also 429. Budget spent.
- Pins found: 0 (API rate-limited, not a content miss)

## T3 start
- DDG search "Lyford Energy battery storage Texas ERCOT": 3 hits — Infrasure, Interconnection.fyi, Cleanview — all aggregator/tracker sites, no developer identity
- DDG search "Lyford Energy LLC" Texas registration: 0 results
- DDG search "Lyford Energy" Willacy/Raymondville: 1 hit — Raymondville Chronicle 2024-12-31: Willacy County public hearing on tax abatement with "Lyford Energy Storage LLC" (Dec 30, 2024)
- SPV confirmed as Lyford Energy Storage LLC (slightly different from queue entry "Lyford Energy")
- No developer parent company identified; no news/press release found
- Source saved: sources/raymondville_chronicle_20241231.md

## T4 start
- interchange.puc.texas.gov: all paths return HTTP 402 (portal blocked, not a content miss)
- DDG site:puc.texas.gov search: returned CAPTCHA, no results
- IA found: NO (portal blocked; cannot rule out IA existence)
- Budget spent, moving on

## T5 start
- TX Comptroller Ch.313 list: program expired 2022; no search tool for agreements found
- JETI applications page: returned "Error Loading Page" — no data extractable
- Local abatement (Ch.312): Raymondville Chronicle item (T3) indicates Willacy County public hearing on tax abatement with Lyford Energy Storage LLC, Dec 2024 — this is likely a Ch.312 county abatement, not JETI/313
- Abatement found: INDIRECT signal only (county hearing, not a filed/approved application document in hand)
- Budget spent

## T6 start
- Site candidate: POI "5745 E Raymondville 138kV" → Raymondville No.2 Substation (AEP, 138kV), ~1 mile east of FM 186/Hwy 77 Bypass intersection
- Estimated coords: 26.482°N, 97.758°W (Raymondville city center offset east)
- CDSE chips attempted: 9 (3×3 grid); 6 failed with RemoteDisconnected; 3 succeeded (center + SW/NW of left column)
- Contact sheet: 3 chips covering agricultural/rural area around Raymondville — field patchwork, farm structures, no gravel pad, no container rows, no visible battery construction
- Construction visible: NO (within coverage; note 6/9 chips missing so east column not covered)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- STOP
