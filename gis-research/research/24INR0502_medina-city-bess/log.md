# Triage log — Medina City BESS (24INR0502)

## T1 start
- queue_history.py ran successfully: 5 snapshots (2025-08-01 → 2026-06-01)
- IA signed: 2023-01-18 (present from first snapshot 2025-08-01)
- COD drift: 2 changes — initial 2026-03-02, then slipped to 2026-10-16, then 2026-10-15
- No construction milestones achieved (start, end, energization, sync, commercial op all null)
- Screening and FIS milestones also null — unusual that IA is signed without FIS approved
- T1 result: IA exists (strong signal), COD drifted ~7 months, no construction milestones confirmed

## T2 start
- gmaps.py: 429 Too Many Requests on both attempts (exact name, name+county) — rate-limited, budget exhausted
- T2 result: no delivery pins found (rate-limited, not absence of site)

## T3 start
- Developer identified: Regis Medina LLC (part of "Regis" group: Regis Leakey LLC, Regis Medina LLC, Regis Medina Lake LLC, Regis Utopia LLC)
- EWG self-certification filed with PUCT: February 2025
- PUCT Complaint Docket 57986 (filed 2025-04-21): Regis entities vs. Bandera Electric Cooperative — alleges co-op "refuses to honor the Interconnection Agreements" for all 4 Regis projects; active/unresolved
- No press releases or news articles specific to project construction
- Source: DDG web search results (infrasure.ai, interconnection.fyi, PUCT Interchange references)
- T3 result: developer identified, significant dispute signal — Bandera Electric Co-op blocking IA enforcement; EWG cert filed

## T4 start
- PUCT Interchange portal returned HTTP 402 on all 3 attempts (docket search, filing party search, direct docket 57986)
- Portal is blocked in this environment — cannot retrieve IA PDFs directly
- Note: T3 web sweep confirmed IA signed 2023-01-18 (queue data) and that a complaint exists about co-op refusing to honor IAs (Docket 57986)
- T4 result: IA existence confirmed via queue data + complaint filing; PDF content unavailable (portal blocked)

## T5 start
- TX Comptroller Ch.313 portal: no application data visible for Bandera County — budget consumed (3 attempts, all returned nav pages not data)
- Ch.313 program expired 2022 for new applications — not expected for a 2022-entry project
- JETI registry (gov.texas.gov/business/page/jeti): HTTP 404
- T5 result: no abatements found — normal for post-2022 BESS project; JETI portal unavailable

## T6 start
- Site candidate: MEDINA substation POI — approx 29.803°N, -99.253°W (Medina, TX, Bandera County)
- Attempted 3×3 grid of chips (buffer-km 2, step ±0.03°) via cdse.py
- CDSE auth: HTTP 401/403 on all 9 chip attempts — ~/.config/gis-research.env contains only example placeholder, no real credentials
- Cannot retry auth credential issue during triage
- T6 result: imagery blocked (no CDSE credentials); no construction verdict possible from imagery

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~24
- T7 complete; stopping
