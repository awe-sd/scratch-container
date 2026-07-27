# Triage log — JackGard BESS (26INR0215)

## T1 start
**queue_history result:** 35 snapshots (2023-08-01 → 2026-06-01), 5 COD changes.

Milestones achieved:
- Screening started: 2023-08-14
- Screening complete: 2023-11-02
- FIS requested: 2023-07-31
- FIS approved: 2024-11-15

Milestones NOT achieved: IA signed, meets 6.9(1), meets all 6.9, construction start/end, energization, sync, commercial operation.

COD drift:
- 2026-04-01 → 2026-09-14 → 2027-04-14 → 2027-09-15 → 2027-10-10 → 2028-04-17
- ~2 years of total slippage over 3 years in queue. Currently 2028-04-17.
- No IA yet — pre-IA project.

## T2 start
**gmaps.py:** HTTP 429 on first call; retried once — still 429. No pins found. Normal.

## T3 start
**Web sweep results:**
- infrasure.ai, cleanview.co, ercotqueue.com, interconnection.fyi: aggregator listings only; confirm 200.59 MW BESS, Jack County, NORTH zone, no-IA status. No standalone news/PR.
- KEY FIND: IA reportedly signed 2025-06-19 between Oncor Electric Delivery TSP LLC and Jackgard BESS LLC — PUCT filing Control No. 35077. (Queue snapshots through 2026-06-01 do NOT show iaSigned — discrepancy to resolve in T4.)
- LLC registered TX 2024-04-30, address 5900 Balcones Dr, Austin TX 78731. No identified parent company — appears project-specific SPV.
- No developer PR/news found for this specific project.

Sources saved: none (aggregator listings; PUCT filing target for T4).

## T4 start
**PUCT Interchange:** HTTP 402 on all three attempts (FilingParty search, Description search, direct Control No. 35077 PDF). Portal blocked. IA existence confirmed by T3 web sweep (Control No. 35077, Oncor + Jackgard BESS LLC, 2025-06-19) but document not accessible during triage. IA found = YES (external source), PDF contents = unknown.

## T5 start
**Ch.313 search:** Comptroller Ch.313 list not directly queryable — no dedicated search tool found; no hit for JackGard in surface content.
**JETI:** txjetifund.com unreachable (ENOTFOUND). DDG fallback search: no JETI application for JackGard specifically. Post-2022 project → JETI miss is normal.
**Ch.312 abatement lead:** "Jack County Energy Storage, LLC" obtained Ch.312 tax abatement; reinvestment zone approved Jack County Commissioners' Court 2025-06-09, ~$165M improvements. Separate "PK Solar / Jack County Energy" joint application also approved June 2025. Entity "Jack County Energy Storage, LLC" ≠ "JackGard BESS, LLC" by name — may be a related or companion project, or same project under alternate entity. NOT confirmed as JackGard. Also: Hecate Energy / Graford ISD has a Ch.313 BESS in Jack County (separate project).
**abatement_found = UNCERTAIN** — Ch.312 abatement exists in Jack County for energy storage; link to JackGard unconfirmed.

## T6 start
**Site candidate:** Jacksboro 345kV substation located ~5 mi NE of Jacksboro TX along SH-59. OSM node coords: 33.278°N, -98.107°W. Confidence: MEDIUM (POI substation confirmed, but BESS pad placement within ~1-km buffer unknown).
**Imagery attempt:** cdse.py chips at center coords, 3 recent dates (2026-04, 05, 06) — HTTP 401 Unauthorized on all. CDSE credentials expired/invalid. No contact sheet produced.
**imagery: BLOCKED (auth failure)**

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.
