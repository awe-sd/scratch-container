# Triage log — Musgravite Solar (27INR0198)

## T1 start
- Script: `uv run gis-research/scripts/research_tools/queue_history.py 27INR0198`
- 28 monthly snapshots (2024-03-01 → 2026-06-01)
- COD drift count: 1 (2027-05-28 → 2027-11-01, shifted at 2025-10-01 snapshot)
- Milestone dates:
  - Screening started: 2024-03-22
  - Screening complete: 2024-06-19
  - FIS requested: 2024-03-06
  - FIS approved: 2025-10-06
  - IA signed: 2025-05-20 (first appeared in 2026-02-01 snapshot)
  - No 6.9 milestones, no construction start/end, no energization/sync/COD approvals
- **T1 result:** IA is signed (strong signal); project has cleared FIS. No construction milestone yet. 1 COD slip.

## T2 start
- gmaps.py: 429 Too Many Requests on all 4 queries (exact name; name+county; LLC name; name+solar). One retry attempted, still 429.
- **T2 result:** No pins found (rate-limited, not a project signal).

## T3 start
- Query 1: DDG "Musgravite Solar" Texas → developer identified: **BT Thompson Solar, LLC**; location pinned to LaRue, Henderson County TX; multiple tracker sites confirm 100.6 MW, 2027 COD
- Query 2: DDG "BT Thompson Solar" + "Musgravite" → no parent company, no press releases; only 1 project on file per ercotqueue.com
- Query 3: DDG "BT Thompson Solar" Texas LLC → TX SOS File #0805261272, filed 2023-10-11, address: 13612 Midway Rd Ste 200, Farmers Branch TX 75244; bizapedia blocked (security check, counted as 1 retry)
- No press releases or financing news found. No traditional news coverage.
- Sources saved: none (no unique project-specific pages beyond aggregator summaries)
- **T3 result:** Developer = BT Thompson Solar LLC (Farmers Branch TX), single-project developer, filed Oct 2023. No news/PR. Location claim: LaRue, Henderson County.

## T4 start
- PUCT Interchange search (FilingParty=Musgravite Solar): HTTP 402 Payment Required
- PUCT Interchange search (FilingParty=BT Thompson Solar): HTTP 402 Payment Required
- PUCT Interchange root: HTTP 402 Payment Required
- One retry attempted (BT Thompson name), still blocked.
- **T4 result:** Portal blocked (402), cannot confirm IA filing. IA is recorded as signed (2025-05-20) in the queue data, but no PUCT document retrieved.

## T5 start
- TX Comptroller Ch.313 page: no searchable database returned via WebFetch (page doesn't render data table)
- DDG search for Ch.313/JETI + Musgravite/BT Thompson + Henderson County: no results
- Note: Ch.313 expired 2022-12-31; project filed 2023-10-11, so post-cutoff — JETI (replacement) would be applicable. No JETI hit found.
- **T5 result:** No abatement found. Normal for a 2023-filed project (post-Ch.313 expiry); JETI miss is expected at this stage.

## T6 start
- Site candidate: LaRue, Henderson County TX (32.1169, -95.6747) — from T3 web sweep (futuregrid.io + cleanview.co cited LaRue as location)
- Ran 9-point 3×3 grid chips in parallel; 7 failed (CDSE RemoteDisconnected under parallel load); 2 auto-succeeded (top row NW+N). Re-ran center chip serially — succeeded.
- 3 chips available: (32.1169,-95.6747), (32.1469,-95.6747), (32.1469,-95.7047) — all 2026-06-01 ±15d, 2 km buffer
- Contact sheet read: ~50-70% cloud cover across all three chips. Visible ground = rural forest/agricultural patchwork. No solar arrays, no grading, no equipment staging visible in cloud-free windows.
- No activity spotted → no re-center or baseline chip needed (full-size reads saved for deep scan)
- **T6 result:** No construction visible. Cloud contamination limits confidence; imagery inconclusive but consistent with pre-construction. Site candidate confidence: LOW (LaRue is a town centroid, not a surveyed parcel location).

## T7 start
- Wrote triage_findings.json (ia_found=true, construction_visible=false, deep_scan_recommended=true)
- Wrote triage.md (10-line summary)
- **Turns used: ~28**
- DONE.
