# Research log — Vial BESS (25INR0122)

## T1 start
**queue_history.py** — 39 snapshots (2023-04-01 → 2026-06-01)

Milestone dates:
- Screening started: 2022-07-05
- Screening complete: 2022-10-01
- FIS requested: 2023-03-29
- FIS approved: 2025-05-30
- IA signed: **2025-08-04**
- Meets 6.9(1): 2025-08-28
- Meets all 6.9: not achieved
- Construction start/end, energization, sync, commercial op: all null

COD drift (4 changes):
1. 2025-06-30 (held 2023-04 → 2023-05)
2. 2026-01-15 (2023-06)
3. 2026-07-15 (2023-07 → 2024-05)
4. 2027-04-20 (2024-06 → 2024-11)
5. 2027-09-15 (2024-12 → 2026-06, current)

Capacity: 135.12 → 141.39 → 135.18 MW (current)

**T1 result:** IA signed Aug 2025; no construction milestones; 4 COD slips (now 2027-09-15). Plausible but not confirmed.

## T2 start
gmaps.py places — HTTP 429 (rate-limited) on both attempts ("Vial BESS", "Vial BESS Hill County Texas"). Budget spent.
**T2 result:** no delivery pins — gmaps blocked.

## T3 start
DDG returning CAPTCHA on all queries. Bing searches for "Vial BESS", "Vial BESS LLC", "Vial Hill County Texas battery ERCOT" — all returned zero relevant results (word "vial" drowns signal). No news articles, press releases, developer identity, or corporate records surfaced.
**T3 result:** no web signal. Developer identity unknown. No sources saved.

## T4 start
PUCT Interchange (interchange.puc.texas.gov and puc.texas.gov/interchange) — HTTP 402 on all URL patterns. Portal blocked, not accessible via WebFetch. Tried FilingParty=Vial BESS and alternate root URLs.
**T4 result:** IA cannot be confirmed/retrieved via portal. Milestone data shows iaSigned=2025-08-04 from queue history (T1 is the only IA signal available).

## T5 start
TX Comptroller Ch.313 and JETI: comptroller.texas.gov pages return overview/navigation pages only — no searchable database accessible via WebFetch. No project-level data retrievable for Hill County. JETI link navigates to a program description page, not a registry.
Normal finding for a post-2022 BESS project — Ch.313 expired 2022; JETI is newer and registry may not be publicly accessible via web scrape.
**T5 result:** no abatement found (portal inaccessible, normal for this vintage).

## T6 start
POI: "Chatt(234) - Pecan Street(3352) 138kV". Searched OSM Overpass for Hill County substations — no "Pecan Street" named substation found (named subs in area: Abbott, Hillsboro, Sam Switching Station, Mertens). Bing search for ONCOR Pecan Street 138kV returned zero results. No pin from T2, no abatement map from T5 to use as site candidate.
Best known location: Hill County, TX (roughly 32.0, -97.1) — county-level only, no tighter candidate.
**T6 result:** no site candidate — imagery SKIPPED per rules.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. Deep scan recommended.
**T7 complete.**
