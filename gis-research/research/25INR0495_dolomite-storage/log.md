# Triage log — 25INR0495 Dolomite Storage

## T1 start
- queue_history.py ran: 34 snapshots 2023-09-01 → 2026-06-01
- COD: 2026-12-01, ZERO drift (held entire history)
- Screening started: 2023-09-08; Screening complete: 2023-12-04
- FIS requested: 2023-08-22 (pre-dates screening — normal for early filers)
- FIS approved: — (not yet)
- IA signed: — (not yet)
- All construction/energization/synchronization milestones: —
- Milestone posture: pre-FIS, no IA. Very early stage.

## T2 start
- gmaps.py: HTTP 429 (rate-limited) on both attempts — 0 pins found. Normal.

## T3 start
- Search 1 (DDG: "Dolomite Storage ERCOT battery Ellis County Texas"): surfaced tracker entries only. Developer identified as "BT Wilson Storage, LLC" (not "Dolomite Storage LLC"). No news/PR. Build-chance cited as ~5% on one tracker.
- Search 2 (DDG: "Dolomite Storage LLC Texas battery"): confirms BT Wilson Storage, LLC as developer. No LLC registration info, no parent company identified.
- Search 3 (DDG: "BT Wilson Storage"): CAPTCHA block — negative. 1 retry spent, moving on.
- T3 summary: Developer name = BT Wilson Storage, LLC. No news, no press releases, no parent company. Tracker entries only.

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all endpoint attempts (3 tries). Portal blocked.
- DDG search for PUCT/IA filings: CAPTCHA block — negative.
- T4 result: No IA found. Consistent with milestone data (iaSigned = —). Budget spent.

## T5 start
- TX Comptroller Ch.313: no searchable database found via portal; no Ellis County battery storage entries surfaced.
- JETI registry search: no results for Dolomite Storage or BT Wilson Storage in Ellis County.
- T5 result: No abatement found. Normal for post-2022 project (Ch.313 expired 2022, JETI too new/sparse).

## T6 start
- Site candidate: Rockett, TX ~32.47°N, 96.76°W (POI = "218 Rockett 69kV" per queue). Near Waxahachie, Ellis County.
- cdse.py chip: HTTP 401 Unauthorized on all 9 grid attempts — ~/.config/gis-research.env is the example template, no real CDSE credentials.
- T6 result: No imagery obtained. Site candidate identified from POI name. Construction status: unknown.

## T7 start
- Wrote triage_findings.json and triage.md.
- Turns used: ~28. T7 complete. Stopping.
