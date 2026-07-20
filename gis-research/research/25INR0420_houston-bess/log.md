# Triage log — Houston BESS (25INR0420)

## T1 start
- queue_history.py ran: 40 snapshots (2023-03-01 → 2026-06-01)
- Milestones: Screening done 2023-07-03; FIS approved 2024-04-04; IA NOT signed; no construction milestones
- COD drift: 4 CODs — 2025-09-29 → 2026-06-15 → 2026-12-15 → 2027-08-01 (3 slips)
- Capacity: started 233.4 MW, settled at 227.9 MW from 2023-06-01
- T1 complete

## T2 start
- gmaps.py places: persistent HTTP 429 on all 3 queries (after backoff retry) — tool blocked
- No delivery pins found (tool failure, not a project signal)
- T2 complete: 0 pins

## T3 start
- DDG search "Houston BESS battery storage ERCOT": 1 result → infrasure.ai project page
- Developer: SMT Energy; SPV: SMT Houston IV
- Key finds: $135M financing Feb 2025; groundbreaking May 2025 (Irby Construction + CenterPoint)
- Project described as 160 MW / 320 MWh in press (vs 227.9 MW in queue — flag)
- news_found: YES (financing + groundbreaking press coverage)
- Saved: sources/infrasure_project_page.md
- T3 complete

## T4 start
- PUCT Interchange portal: HTTP 402 on all attempts — portal blocked, one retry done
- ia_found: NO (portal inaccessible; queue confirms IA not yet signed either)
- T4 complete: no IA recovered

## T5 start
- Ch.313: program expired 2023; post-2022 project — no application expected, normal miss
- JETI registry: no searchable public database found; tool limitation, not project signal
- abatement_found: NO (normal for a 2023 queue entry)
- T5 complete

## T6 start
- Site candidate: Lauder substation, 4711 Lauder Rd Houston TX; FCC coords 29.9109°N, 95.3213°W — method=POI infrastructure
- 3×3 chip grid at 2km buffer, 2026-06-01; 4/9 tiles returned (5 remote disconnects)
- Contact sheet read + 1 full-size frame (center tile, Lauder substation) read
- Center tile: dense suburban/industrial mix; no obvious pale gravel BESS container pad visible
- construction_visible: inconclusive — partial coverage (5 tiles missing), groundbreaking confirmed by press but not directly observable at this resolution/coverage
- T6 complete

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~28
- T7 complete — STOP

## Deep scan D1 (2026-07-19)
- Irby Construction project page confirms: SMT Houston IV BESS, 160 MW/320 MWh, EPC=Irby, groundbreaking April 2025 (vs May 13 in other sources), COD June 2026
- infrasure.ai confirms: IA NOT signed, facility study phase; COD per platform = Jun 14, 2026 vs queue 2027-08-01
- Lauder Substation OSM geom confirmed: centroid 29.9112, -95.3215 (CenterPoint 138kV/12kV)
- Rittenhouse Substation OSM: 29.8636, -95.3794 (CenterPoint 138kV/12.5kV)
- SMT Energy HQ confirmed: Boulder CO
- SMT Energy partners: FlexGen, SUSI Partners, KeyBank, GreenPrint, UBS, Goldman Sachs
- PUCT Interchange: 402 again — IA still unrecoverable via web
- gmaps 429 again — pin search still blocked
- Lauder tight 1km chip: dense suburban + industrial; no pale gravel BESS pad visible at substation
- Lauder 3km chip: dense urban — no open industrial land adjacent
- Rittenhouse 2km chip: dense residential; no BESS pad visible
- MW discrepancy: 227.9 MW (queue, initially 233.4) vs 160 MW/320 MWh (all press/financing/EPC) — project rescoped; queue MW was never updated after initial filing reduced to 227.9

## Deep scan D2 (2026-07-19) — site investigation
- POI is a TAP on the 138kV line between Lauder and Rittenhouse — not AT either substation
- The BESS pad will be located along this transmission line corridor, NOT at the substations
- Neither Lauder nor Rittenhouse chips show a BESS pad — consistent with POI being a line-tap
- Midpoint of Lauder–Rittenhouse corridor: ~29.887N, -95.350W (4 km SW of Lauder, 3 km NE of Rittenhouse)

## Deep scan synthesis (2026-07-19)
- dossier.md written
- findings.json written
- queue_history.py: 40 snapshots, 3 COD changes
- build_brief.py: brief.html (5KB, 3 images, 3 sources)
- build_index.py: 107 projects indexed
- VERDICT: real_active; COD 2027-Q2/Q3; drift risk HIGH
