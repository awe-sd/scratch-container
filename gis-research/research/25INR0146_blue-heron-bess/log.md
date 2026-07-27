# Triage log — Blue Heron BESS (25INR0146)

## T1 start
Queue history: 39 snapshots (2023-04-01 → 2026-06-01).
- Screening started 2022-10-24, screening complete 2023-01-20 — DONE
- FIS requested 2023-04-10 — but NOT approved (no date)
- IA signed: NO
- All 6.9 milestones: NO — project is pre-IA
- Reported COD has drifted 4× (2025-12-31 → 2026-04-21 → 2026-09-14 → 2027-09-13 → 2028-03-31)
- Current capacity: 201.13 MW (stable since 2025-09)
- COD drift: slipping ~6 months each cycle; 5 distinct CODs over 3 years
- No construction start/end dates; no energization or commercial op approval

T1 complete.

## T2 start
gmaps.py: HTTP 429 on first attempt; retry also 429 — API rate-limited. No pins found.
Pins found: 0 (API blocked, not a search miss).

T2 complete.

## T3 start
DDG HTML: HTTP 403 blocked.
Bing search 1 ("Blue Heron BESS" Texas battery): no results — only generic color-of-blue pages.
Bing search 2 ("Blue Heron BESS LLC" energy storage): no results.
Bing search 3 (ERCOT + Reeves + 25INR0146): no results.
Bing search 4 (SEC/FERC/PUC site-restricted): CAPTCHA blocked.
No developer name, no news, no LLC registration found.
T3 complete.

## T4 start
PUCT Interchange (interchange.puc.texas.gov): HTTP 402 on all endpoints (FilingParty search, description search, root). Portal blocked — not a session issue.
No IA found. No alternate name surfaced in T3 to try.
T4 complete.

## T5 start
TX Comptroller Ch.313: URL returned overview page, not searchable data; xlsx direct link returned file description only (can't parse binary). No Ch.313 for Blue Heron found.
JETI registry: jeti.comptroller.texas.gov DNS not found; comptroller JETI page is navigation-only.
2025-filed project — JETI miss is normal (Ch.313 expired 2023, JETI program; no applications found).
T5 complete.

## T6 start
Site candidate: Riverton, TX area (~31.10°N, 103.70°W, Reeves County) — derived from POI description "Tap 138kV MANSON (1094) - Riverton (11083)". Confidence: low (Riverton is a tiny community; substation is nearby but exact coords unknown).
CDSE imagery: HTTP 403 on both attempts (2026-06-15, 2026-05-01 with wider windows). Authentication failing — CDSE session likely expired. No contact sheet produced.
Imagery: not available this run.
T6 complete.

## T7 start
Wrote triage_findings.json and triage.md.
Turns used: ~28. All steps completed. Three tool blockers (gmaps 429, PUCT 402, CDSE 403).
T7 complete. STOP.
