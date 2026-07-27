# Triage log — Helion BESS (27INR0624)

T1 start
- Queue history: 2 snapshots (2026-05-01 → 2026-06-01)
- COD 2027-09-16, 0 drift events (stable)
- Milestones: screening started 2026-05-15, FIS requested 2026-05-14
- No screening complete, FIS approved, IA signed, or later milestones
- Assessment: very early stage — roughly 2 months in queue

T2 start
- gmaps.py: HTTP 429 Too Many Requests on all queries (rate-limited)
- No pins found
- Result: 0 delivery pins

T3 start
- DDG search "Helion BESS Texas battery storage": only aggregator mirrors (cleanview.co, interconnection.fyi) — no news or developer info
- DDG search "Helion BESS LLC" registration: no results
- DDG search "Helion BESS" news/announcement: no results
- TX SOS business search (mycpa URL): 404
- interconnection.fyi/project/ercot-27inr0624: confirms 100 MW / Scurry / Sep 2027, but developer identity behind paywall
- No developer name, parent company, or press coverage found
- Result: news_found=false; no developer alias for T4 alternate search

T4 start
- PUCT Interchange portal: HTTP 402 on all attempts (session-auth required)
- No IA filings accessible during triage
- Result: ia_found=false

T5 start
- TX Comptroller Ch.313 page: navigation only, no searchable data accessible via fetch
- JETI registry page: navigation only, no searchable data accessible via fetch
- Ch.313 program expired Dec 2022 — project entered queue May 2026, so no Ch.313 expected
- JETI: no entries found for Scurry County battery storage; normal for 2-month-old project
- Result: abatement_found=false

T6 start
- Site candidate: POI "59912 GALVANI 345" → GALVANI is a new 345kV substation in Scurry County near Snyder TX (~32.73N, -100.90W), referenced in PUCT case 57477 (2023 filing for solar POI)
- Generated 3x3 chip grid (±0.03° step, buffer-km 2) around 32.73/-100.90: CDSE returned HTTP 401/403 (auth failure)
- No imagery retrieved; construction_visible=false (unknown, not false negative)
- Site confidence: LOW (POI substation county + town, no pin)

T7 start
- Wrote triage_findings.json and triage.md
- deep_scan_recommended: false (project only 2 months old, no IA, no milestones)
- Turns used: ~24
- DONE
