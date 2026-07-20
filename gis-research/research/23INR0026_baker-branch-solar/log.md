# Triage log — Baker Branch Solar (23INR0026)

## T1 start
- queue_history.py ran successfully; 76 snapshots (2020-03-01 → 2026-06-01)
- 13 reported-COD changes (heavy drift)
- COD trajectory: 2023-02-28 → ... → 2026-09-30 (slipped ~3.5 years from original)
- IA signed: 2022-02-14 ✓
- FIS approved: 2023-10-30 ✓
- Meets 6.9(1): 2023-10-03 ✓ / Meets all 6.9: 2023-10-30 ✓
- Approved for energization: 2024-04-01 ✓
- Approved for synchronization: 2024-04-10 ✓
- Construction start/end: NOT reported
- Commercial operation approved: NOT reported
- Capacity: 400 MW → 476.3 → 469.42 MW (settled)
- POI: tap 345kV 1692 Paris - 1690 Valley; CDR zone: NORTH
- VERDICT: Project has IA + full 6.9 + sync approval. COD drift is heavy but advanced milestone set. Reported COD 2026-09-30 is current as of 2026-06-01 snapshot.
## T1 done

## T2 start
- gmaps.py places "Baker Branch Solar" → HTTP 429 (rate limit)
- gmaps.py places "Baker Branch Solar Lamar County Texas" → HTTP 429 (one retry per rules)
- RESULT: No pins found. 0 pins. Blocked by rate limit after 1 retry.
## T2 done

## T3 start
- DDG: "Baker Branch Solar Texas news" → project is Mockingbird Solar Center (Ørsted), Brookston/Paris TX, Lamar County
- DDG: "Baker Branch Solar LLC" → entity not found as standalone; project attributed to Mockingbird Solar Center LLC across all tracker sites
- ercotqueue.com: "Currently Commissioned; build-chance 100%"
- Electrek Nov 22 2024: Mockingbird Solar Center ~468 MW commissioned Nov 22, 2024 — Ørsted's largest solar project globally at that time
- Ørsted Nov 2024 press release (403 blocked): confirmed commissioning celebration
- Baker Branch Substation = POI infrastructure (Dallas News Jan 2025)
- KEY FINDING: Project is ALREADY OPERATIONAL as of Nov 22, 2024. ERCOT queue still shows reported COD 2026-09-30 — queue has not been updated to reflect actual COD.
- Developer: Ørsted (via Mockingbird Solar Center, LLC)
- Saved source: sources/orsted_commissioning_nov2024.md
## T3 done

## T4 start
- PUCT Interchange portal: HTTP 402 on all endpoint attempts (payment/subscription wall)
- IA existence confirmed via queue: iaSigned = 2022-02-14 — IA definitely exists
- Could not download IA PDF or milestone schedule exhibit
- RESULT: IA confirmed via queue data; PUCT portal blocked for PDF retrieval
## T4 done

## T5 start
- TX Comptroller Ch.313 search: Mockingbird Solar Center, LLC found
  - App #1711: Chisum ISD, posted 2022-03-07, agreement 2022-10-27, first tax year 2025
  - App #1712: North Lamar ISD, same applicant/date
  - Annual reports 2023-2025 present (confirms project operational)
  - PDF: https://assets.comptroller.texas.gov/ch313/1711/1711-chisum-mockingbird-app.pdf
- JETI registry: not checked (post-2022 Ch.313 alternative; project used Ch.313 which closed 2023)
- RESULT: Abatement FOUND. Mockingbird Solar Center LLC = Baker Branch Solar (23INR0026)
## T5 done

## T6 start
- Site candidate: Brookston/Paris, Lamar County TX — from Electrek Nov 2024 article + Dallas News reference to Baker Branch Substation near Brookston
- Center estimate: 33.668°N, 95.702°W (Brookston area), confidence: high (news-confirmed)
- 3×3 grid chips at 2026-07-01, buffer-km 2, step ±0.03° — 4 of 9 chips downloaded
- Contact sheet read (4 frames): TOP-LEFT (center) + TOP-RIGHT (33.668,-95.732): LARGE SOLAR PANEL ARRAYS CLEARLY VISIBLE — dense rectangular blue/purple panel pattern covering extensive agricultural land
- BOTTOM frames (33.698 row): agricultural fields, no solar visible at this northward offset
- construction_visible = TRUE (arrays operational, not under construction — panels installed and complete)
- No baseline chip needed: project confirmed operational by news; visual confirms fully installed arrays
## T6 done

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- deep_scan_recommended: false (project operational)
## T7 done — TRIAGE COMPLETE
