# Triage log — Longfellow BESS II (24INR0455)

## T1 start
- 39 monthly snapshots (2023-04-01 → 2026-06-01)
- COD drifted 4 times: 2024-12-31 → 2025-12-01 → 2026-01-31 → 2026-08-31 → 2026-11-30 (current)
- Key milestones: Screening complete 2023-02-03, FIS approved 2025-12-17, IA signed 2025-04-15, Meets 6.9(1) 2025-04-29, Meets all 6.9 2026-01-29
- Construction start/end: NOT reported. No energization/sync/COD approvals yet.
- Milestone posture: fully through pre-construction gates (IA signed, all 6.9 met), but no construction-phase milestones logged.

## T2 start
- gmaps.py places: HTTP 429 on first call; HTTP 429 on one retry — API rate-limited, budget exhausted
- No delivery pins found (tool blocked, not a miss on the project)

## T3 start
- Developer identified: Century Gas Processing, LLC
- LLC registered: Longfellow BESS II, LLC incorporated 2025-12-17 in Texas (Dallas address), Tax ID 32103489251
- Related project: Longfellow BESS I (~430 MWh) has EPC contract with SolarMax; BESS II no equivalent announcement
- ercotqueue.com: IA+FIS complete, "build-chance 92%"
- No major press release for BESS II specifically
- Searches 3-4 returned CAPTCHA (budgeted out)
- Saved: sources/t3_web_sweep.md

## T4 start
- PUCT Interchange search: HTTP 402 on both attempts (portal blocked/requires auth)
- IA existence confirmed indirectly: queue timeline shows iaSigned=2025-04-15
- No IA PDF retrieved; deep scan should attempt Interchange with authenticated session
- ia_found: inferred YES (milestone date present) but document not retrieved

## T5 start
- TX Comptroller Ch.313: No searchable database found; program ended post-2022 — expected miss for this 2022 entry
- JETI registry (applications.php): page returned "Error Loading Page" — data unavailable
- JETI current-agreements: not fetched (budget reached after 4 calls)
- abatement_found: NO (normal for post-2022 BESS project; Ch.313 expired, JETI portal errored)

## T6 start
- POI: "38432 TNCENTRY2_1 138 KV" = TNMP Century Plant Substation
- Located via OSM way 503096012, node 4934385388
- Coordinates: 30.6076°N, 102.5813°W (Pecos TX area, Trans-Pecos West TX)
- Operator on OSM: Occidental Petroleum (OXY) — this is a 138kV industrial substation near Pecos
- Site candidate: medium confidence (POI substation match; BESS pad would be within ~1km)
- cdse.py chips: HTTP 401 Unauthorized on all 5 date requests — CDSE credentials not working
- construction_visible: UNKNOWN (imagery blocked)
- No contact sheet produced

## T7 start
- triage_findings.json: written
- triage.md: written
- Turns used: ~28
- STOP
