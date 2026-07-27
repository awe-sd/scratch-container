# Triage log — 18INR0031 Maryneal Wind

## T1 start
- queue_history.py ran: 113 snapshots (2017-02-01 → 2026-06-01)
- COD drift count: 23 changes (heavy drift — 2018-12-01 original → 2026-08-31 current)
- IA signed: 2020-01-31 ✓
- Approved for energization: 2021-01-08 ✓
- Approved for synchronization: 2021-04-23 ✓
- Commercial operation approved: NOT achieved
- Construction start/end: NOT reported in queue DB
- Capacity: 150 → 180 → 182.4 MW (stabilized 2019-03)
- NOTE: Sync approved 2021-04 but COD still pushed to 2026-08 — 5+ years of post-sync drift is anomalous

## T2 start
- gmaps.py 429 on all 4 queries (exact name; name+county; name+wind+town; LLC name) — blocked after 1 retry per checklist rule
- T2 result: 0 pins, tool unavailable

## T3 start
- DDG search "Maryneal Wind LLC Texas wind farm" returned strong hits
- KEY FINDING: Project is ALREADY OPERATIONAL per multiple sources:
  - ercotqueue.com: "Currently Commissioned"
  - power-technology.com: "commissioned in July 2021"
  - cleanview.co: "Operating 182 MW wind farm"
  - Deriva Energy project page: 38 × Nordex Acciona 4.8 MW; Sprint/T-Mobile 12yr VPPA
  - Developer: Deriva Energy (formerly Duke Energy Sustainable Solutions)
  - EPC: Wanzek Construction
- Saved: sources/deriva_energy_maryneal.md
- No developer name search needed (developer = Deriva Energy confirmed)
- T3 result: news_found = true; project confirmed operational July 2021

## T4 start
- PUCT Interchange: 402 Payment Required on both filing_party and description searches — blocked, 1 retry done
- T4 result: ia_found = false (portal blocked, not confirmed absent)

## T5 start
- TX Comptroller Ch.313 pages are index/overview only — no queryable database accessible via WebFetch
- JETI: project commissioned 2021, pre-JETI era — abatement search not applicable
- T5 result: abatement_found = false (portal not queryable, but normal for pre-2022 projects)

## T6 start
- Site candidate: Maryneal, TX ~32.22°N, 100.46°W (town namesake, Nolan County) — confidence MEDIUM
- CDSE chip calls returned 401/403 — credentials unavailable in this environment
- T6 result: construction_visible = false (imagery unavailable); note project already confirmed operational via T3

## T7 start
- triage_findings.json written
- triage.md written
- T7 complete. Total turns used: 22. STOP.
