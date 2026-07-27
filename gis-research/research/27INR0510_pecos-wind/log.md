# Triage Log — 27INR0510 Pecos Wind

T1 start
- 12 snapshots (2025-07-01 → 2026-06-01)
- Screening complete: 2025-09-30; IA signed: 2026-03-18 (NO FIS step recorded)
- 1 COD slip: 2027-03-28 → 2027-09-30 (change appeared 2025-12-01)
- Capacity changes: 257.73 MW → 191.0 MW (Sep 2025) → 193.8 MW (Mar 2026)
- No construction milestones started

T2 start
- gmaps.py 429 on both attempts — API rate-limited; no pins retrieved
- T2 result: 0 pins found (API blocked)

T3 start
- Developer identified: Midnight Energy Center, LLC (single-project shop per ercotqueue.com)
- SPV: Pecos Wind LLC — Texas Domestic LLC filed 2018-06-13, file #0803047415, 3500 Potomac Ave Dallas TX 75205; registered agent James T Lopez c/o ESI 8111 LBJ Frwy #985 Dallas TX 75251
- Prior entity: RES Pecos Wind LLC — franchise tax ended (defunct)
- No construction news or PR found; no developer announcements
- Source saved: interconnection.fyi confirms 193.8 MW, ERCOT WEST, COD 2027-09-30
- T3 result: developer named, LLC confirmed, no news

T4 start
- interchange.puc.texas.gov returned HTTP 402 on all three queries (FilingParty=Pecos Wind, FilingParty=Midnight Energy Center, Description=Pecos Wind) — portal blocked/auth required
- T4 result: PUCT Interchange inaccessible; IA existence confirmed from queue data (iaSigned=2026-03-18) but PDF not retrieved

T5 start
- TX Comptroller Ch.313 page did not return searchable data — portal structure only; project queued 2025, post-Ch.313 sunset (2022), so 313 not expected
- JETI page similarly did not expose records; project is small independent developer, JETI unlikely
- T5 result: no abatement found (normal for post-2022 wind project)

T6 start
- Solstice sub: 30.9483, -103.3617; Bakersfield sub: 30.9759, -102.2891 (from OSM Overpass)
- POI taps the line between them — corridor is ~100 km; midpoint ~30.96, -102.82
- No FAA OE filings retrieved (portal 404); no pins; no abatement map
- Site candidate confidence LOW — cannot constrain to ±10km without turbine filings
- Per checklist: "no site candidate better than somewhere in the county" — SKIP imagery
- T6 result: no imagery run; site candidate low-confidence only

T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~22; budget warning hit at T6 imagery step — imagery skipped per rules (no site candidate)
- T7 complete
