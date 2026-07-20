# Triage log — Corralitos Wind 2 (24INR0506)

T1 start
**T1 — queue history**
- 42 monthly snapshots (2023-01 → 2026-06)
- Screening started: 2023-01-30; Screening complete: 2023-04-28
- FIS requested: 2023-01-19; FIS approved: NOT ACHIEVED
- IA signed: 2025-06-19 (appeared in 2025-06-01 report)
- Meets 6.9(1), Meets all 6.9: NOT ACHIEVED
- Construction start/end: NOT REPORTED
- COD drift: 2024-12-31 → 2027-12-31 (held 2023-01 through 2024-11, then slipped 3 years; 1 COD change)
- Notable: IA signed without FIS approved — unusual, matches the data model note that milestones are independent gates

T2 start
**T2 — delivery pins**
- gmaps.py returning HTTP 429 (rate-limited) on all 3 queries (exact name, name+county, LLC name)
- One retry attempted, still blocked
- Result: 0 pins found (blocked portal, not a project miss)

T3 start
**T3 — web sweep**
- Developer identified: Vaquero Wind Energy, LLC (Delaware-registered)
- Sister project confirmed: Corralitos Wind 1 (196 MW), Cascabel Wind 2 (~198 MW) — all Zapata County; Vaquero has 4 active ERCOT projects, 0 commissioned
- No project-specific news, press releases, or permit announcements found for Corralitos Wind 2
- cleanview.co confirms 195 MW, ERCO, Planned status, COD Dec 2027 — saved to sources/
- No Texas SOS or detailed LLC ownership chain surfaced

T4 start
**T4 — PUCT Interchange**
- PUCT portal interchange.puc.texas.gov returns HTTP 402 on all direct URL attempts — blocked, no workaround during triage
- DDG search surfaced: PUCT case **35077** — Standard Generation Interconnection Agreement covering BOTH Corralitos Wind 1 (#24INR0505) and Corralitos Wind 2 (#24INR0506)
- Filing party: **Las Crestas Wind Energy, LLC** (also refs Bordas Renewable Energy, LLC) — DIFFERENT from Vaquero Wind Energy (T3); discrepancy flagged for deep scan
- Document ref found: 35077_2172_1510941 — could not retrieve PDF (portal 402)
- IA confirmed FOUND (also consistent with queue data: iaSigned 2025-06-19)
- Milestone schedule exhibit: NOT retrieved (portal blocked)
- DRIFT NOTE: T3 surfaced Vaquero Wind Energy as developer; T4 surfaces Las Crestas Wind Energy as IA counterparty — these may be related SPVs or one may be wrong

T5 start
**T5 — abatements**
- TX Comptroller Ch.313 portal not returning searchable data via WebFetch (redirects to general overview, no direct DB access)
- DDG CAPTCHA'd on all Zapata County + 313/JETI queries
- Project INR is 24INR0506 — entered queue 2024, post-2022; Ch.313 program expired 2022; JETI miss is NORMAL for this vintage
- No abatement found — expected for post-2022 projects; not a negative signal

T6 start
**T6 — imagery**
- Site estimate attempts: FAA OE portal (shutdown notice), gmaps.py (429), DDG CAPTCHA, USGS USWTDB (403), cleanview.co (county only), interconnection.fyi (county only)
- POI description: tap on 345kV line CENIZO7C-DELSOL7C (new ETT Tiempo substation) — gives corridor knowledge but not coordinates
- No abatement map, no IA map retrieved (portal blocked T4)
- Sister project Corralitos Wind 1 (24INR0505) also only at county level in all open sources
- Result: NO SITE CANDIDATE better than "somewhere in Zapata County" — imagery SKIPPED per checklist rule
- Note for deep scan: FAA OE/AAA obstruction filings likely to have exact turbine coordinates when not in shutdown; PUCT case 35077 IA document may contain a project map

T7 start
**T7 — outputs written**
- triage_findings.json: written
- triage.md: written (10 lines)
- Turns used: ~30; deep scan recommended: YES
- Key threads for deep scan: PUCT 35077 PDF, FAA OE filings, entity discrepancy (Vaquero vs Las Crestas), FIS gap
