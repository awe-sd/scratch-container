# Triage log — 28INR0390 Horsepower BESS

## T1 start
- Script: queue_history.py 28INR0390
- 7 snapshots: 2025-12-01 → 2026-06-01
- COD drift: 0 (held at 2028-01-31 the entire window)
- Milestones achieved:
  - Screening started: 2025-12-17
  - Screening complete: 2026-02-23
  - FIS requested: 2025-11-24
- Milestones NOT achieved: FIS approved, IA signed, 6.9(1), all 6.9, construction, energization, sync, COA
- Assessment: early-stage; screening done, FIS pending approval. No IA yet.

## T2 start
- gmaps.py: HTTP 429 on both attempts (rate-limited). Logging negative — no pins found.
- Pins found: 0

## T3 start
- DDG: CAPTCHA blocked (1 attempt).
- Bing: "Horsepower BESS" Texas — no results
- Bing: "Horsepower BESS LLC" OR "28INR0390" — no results
- Bing: "Howard Substation" Bexar battery storage ERCOT — no results
- No developer name surfaced. No news, PR, or registration found.
- news_found: false

## T4 start
- PUCT Interchange direct URL: HTTP 402 on both FilingParty and Description endpoints (portal requires session/auth).
- Bing search "Horsepower BESS" PUCT / IA: CAPTCHA blocked then no results.
- No IA found via accessible channels.
- ia_found: false

## T5 start
- TX Comptroller Ch.313 page: no searchable data accessible via URL (page is overview only).
- Bing: no JETI or Ch.313 records for Horsepower BESS / 28INR0390 in Bexar County.
- Expected: Ch.313 expired 2022; JETI possible but no developer footprint visible.
- abatement_found: false

## T6 start
- Best site candidate: "POI is 138 kV Howard Substation (Bus# 5230)" — need substation coords.
- OSM Overpass: no "Howard" substation in Bexar County area (all 138kV substations listed, none named Howard).
- Bing searches for Howard substation + CPS Energy + San Antonio: no location data returned.
- Nominatim: empty for "Howard substation San Antonio" and "Howard substation Bexar County".
- Best available = "somewhere in Bexar County" — checklist says SKIP imagery in this case.
- Imagery skipped. construction_visible: false (not assessed). no site candidate.

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28
- deep_scan_recommended: false
- All steps T1-T7 complete
