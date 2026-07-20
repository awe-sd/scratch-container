# Triage log — 25INR0394 Orchard Ray BESS

T1 start
- 38 snapshots (2023-05-01 → 2026-06-01)
- Milestones: Screening started 2023-06-07, Screening complete 2023-09-01, FIS requested 2023-05-31
- FIS approved: NO. IA signed: NO. No construction dates. No energization/sync/COD approvals.
- COD drift (3 changes): 2025-05-01 → 2027-05-01 → 2028-09-01 → 2027-05-01
- Current reported COD: 2027-05-01. Slipped ~2 years from original; bounced back from 2028-09-01.
T1 done

T2 start
- gmaps.py: HTTP 429 on all queries (rate-limited); pins_found=0
T2 done (blocked)

T3 start
- Web sweep: developer = Pettus BESS LLC (not "Orchard Ray BESS LLC"); confirmed on infrasure.ai, interconnection.fyi, ercotqueue.com
- ercotqueue.com notes no IA; build probability 5%
- No news, press releases, parent company, or permit filings found
T3 done

T4 start
- PUCT Interchange: HTTP 402 on both FilingParty queries (Pettus BESS, Orchard Ray BESS); blocked, no retry
- IA not found via PUCT
T4 done (blocked)

T5 start
- TX Comptroller Ch.313: no agreements found for Bee County / Orchard Ray / Pettus BESS
- JETI registry: no hits for Bee County battery storage
- Normal for post-2022 project (Ch.313 expired; JETI not yet populated for this project)
T5 done (no hits — normal)

T6 start
- Site candidate: Tuleta 138kV substation ~1 mi south of Pettus TX; estimated coords ~28.620, -97.800 (OSM/Nominatim)
- cdse.py chips: HTTP 401/403 on all 9 grid cells (CDSE creds not available); imagery failed
T6 done (creds blocked — no imagery)

T7 start
- triage_findings.json + triage.md written
- Turns used: ~22
T7 done — triage complete
