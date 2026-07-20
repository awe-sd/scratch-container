# Triage log — Bar Candela Solar SLF (24INR0269)

## T1 start
queue_history.py: 43 monthly snapshots (2022-12-01 → 2026-06-01)
- Screening started: 2022-03-21 | Screening complete: 2022-06-13
- FIS requested: 2022-12-06 | FIS approved: 2024-02-09
- IA signed: 2025-05-06
- No construction milestones achieved (start/end/energization/sync/COA all null)
- COD drift: 2026-01-31 → 2026-06-30 → 2027-12-31 (2 slips, currently 2027-12-31)
- Capacity: 198.0 MW briefly (Dec 2022), then 200.3 MW through 2026-06-01
- IA signed 2025-05-06 — project is post-IA, pre-construction per reported milestones

## T2 start
gmaps.py places: HTTP 429 Too Many Requests on both "Bar Candela Solar SLF" and "Bar Candela Solar Freestone County Texas" — API rate-limited. Budget exhausted. No pins found (not meaningful — API blocked, not absence of site).

## T3 start
DDG web sweep:
- Developer confirmed: Candela Renewables (Brian Kunz CEO, Nik Novograd CFO)
- SPV name per DDG: "Bar Candela Solar Project LLC" (vs. identity-packet "Bar Candela Solar SLF, LLC" — need to verify)
- IA signing party: Oncor (consistent with NORTH zone)
- PUCT Interchange control number 35077, item 2149 found in DDG results — IA filing
- Freestone County Times article URL (Jan 2022 commissioners presentation) returns 404
- ercotqueue.com page loaded but returned no parseable content
- candelarenewables.com: confirms developer, no project-specific location or coordinates published
- news_found: true (developer + PUCT IA reference confirmed via DDG)

## T4 start
PUCT Interchange: all endpoints (search UI, direct PDF, control number query) return HTTP 402 — session/cookie required. Cannot fetch IA document directly.
IA reference from T3: Control 35077, Item 2149 — IA signed 2025-05-06 per queue data; Oncor counterparty per DDG.
ia_found: true (existence confirmed via queue milestone + DDG result), but IA document content NOT retrieved (blocked). Schedule exhibit not examined.

## T5 start
TX Comptroller Ch.313: no Freestone County solar entries found; "Bar Candela" / "Candela" not in list. Ch.313 sunsetted end of 2022 — project entered queue Mar 2022, likely did not complete Ch.313 application before sunset.
JETI registry: no publicly searchable list available; no hits found.
abatement_found: false — normal for post-2022 solar project without completed Ch.313.

## T6 start
Site candidate: Long Lake body of water at ~31.92°N, 96.06°W, Freestone County — used as POI infrastructure proxy (Long Lake Sub = Bus 3280 in POI description). Confidence LOW — geographic name match only, no address confirmed.
cdse.py chips: HTTP 401/403 on all 9 chip requests — CDSE credentials absent or expired in this session (~/.config/gis-research.env missing/invalid). No imagery obtained.
construction_visible: unknown (imagery blocked)

## T7 start
triage_findings.json written. triage.md written. Turns used: ~22. STOP.
Blockers this run: gmaps 429 (T2), PUCT 402 (T4), CDSE 401 (T6) — all three tool classes rate-limited or credential-expired.
