# Triage log — Tokio Solar (23INR0349)

## T1 start
queue_history.py ran: 50 snapshots (2022-05-01 → 2026-06-01)

**COD drift (3 changes):**
- 2024-10-31 (held 1 month: 2022-05)
- 2025-03-24 (held 1 month: 2022-07)
- 2025-08-25 (held ~25 months: 2022-08 → 2024-08)
- 2027-08-25 (current, held since 2024-09)

Total drift: ~3 years from original COD (2024-10-31 → 2027-08-25).

**Milestones achieved:** Screening started 2021-08-12, Screening complete 2021-11-01, FIS requested 2022-04-14, IA signed 2023-11-06, Meets 6.9(1) 2023-11-17.
**Not yet:** FIS approved, Meets all 6.9, construction start/end, energization, sync, COA.

**Capacity changes:** 175 → 177.64 → 175.72 → 170.45 MW (current). Minor trimming, settled.

**Milestone gap:** IA signed but FIS NOT approved — unusual (IA without FIS approval). Note for deep scan.

## T2 start
gmaps.py: HTTP 429 on both attempts (rate-limited). Per rules: one retry done → negative log.
**Pins found: 0** (tool blocked, not conclusive absence)

## T3 start
**Developer identified: Gransolar Texas Eight, LLC** (Irving TX; parent: Gransolar Group, Spain; 3.1 GW globally, 18 TX assets ~3,313 MW)
- LLC incorporated TX 2021-07-09; address 125 E John Carpenter Blvd Ste 1325, Irving TX 75062
- Only 1 ERCOT project on file (this one)
- PUC Control Number **35077** found — IA filed 2023-11-30 (Oncor + Gransolar Texas Eight)
- EIA Plant Code: 66397 ("Tokio")
- Build-chance estimate (ercotqueue.com): 26%
- No news articles found; project in pre-construction per aggregators
- cleanview.co behind login — skipped

Sources: DDG search results (ercotqueue.com, interconnection.fyi, infrasure.ai, cleanview.co, PUCT Interchange via web aggregators)

## T4 start
PUCT Interchange (interchange.puc.texas.gov) returning HTTP 402 on all URL patterns tried. Portal blocked; per rules: one retry done → negative log.
**IA confirmed exists (from T3 web sweep):** Control No. 35077, filed 2023-11-30, Oncor + Gransolar Texas Eight LLC. But PDF contents (milestone schedule) inaccessible via WebFetch.
**IA found: YES** (from external aggregators); schedule exhibit: NOT retrieved (portal blocked)

## T5 start
TX Comptroller Ch.313: no searchable online database accessible via WebFetch; Comptroller pages are nav-only.
DDG search for Tokio Solar/Gransolar + McLennan + Ch.313/JETI: no results.
**Abatement found: NO** (normal for post-2022 project; Ch.313 expired Dec 2022, JETI is replacement but no hit found)

## T6 start
Site candidate: Waco Atco substation vicinity — 31.41°N, 97.15°W (SE of Hewitt TX), LOW confidence.
- No pin from T2 (gmaps blocked), no confirmed address from web sweep
- POI "Tap 138kV 3592 Waco Atco - 170 Cotton Belt" → substation anchor only; actual site unknown
- Ran 1 chip: 31.41°N 97.15°W, 2026-07-01, 2km buffer
- Result: agricultural farmland (green/fallow fields), no solar infrastructure, no construction visible
- 1 full-size frame read used (1/3 budget)
- Cannot confirm this IS the project site — just the POI infrastructure area
**Construction visible: NO** (at low-confidence location)

## T7 start
Wrote triage_findings.json and triage.md.
**Turns used: ~22. Run complete.**
