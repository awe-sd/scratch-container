# Research log — Buda BESS (25INR0650)

## T1 start
queue_history.py → 15 snapshots (2025-04-01 → 2026-06-01), 4 COD changes.
- IA signed: 2025-02-26 (present from first snapshot)
- Approved for energization: 2026-05-05
- Approved for synchronization: 2026-06-02
- Commercial operation approved: NOT YET
- COD drift: 2025-12-01 → 2026-02-06 → 2026-04-08 → 2026-08-10 → 2026-09-11 (current)
- No construction start/end milestone dates reported
- Project is late-stage: sync approval in hand, awaiting commercial operation sign-off.

## T2 start
gmaps.py places — all 3 queries returned HTTP 429 (rate-limited). One retry attempted, still blocked. No delivery pins found. Normal for a small battery project.

## T3 start
DDG: CAPTCHA-blocked on both queries. Bing: no results for "Buda BESS", "Buda BESS LLC", or 25INR0650. TX SOS direct search URL returned 404. No developer name, no news, no LLC registration found. Very low web footprint — consistent with a small battery project with thin public record.

## T4 start
PUCT Interchange: all URL patterns returned HTTP 402 (session/auth required). Portal blocked. One retry attempted. IA existence is confirmed from queue history (iaSigned=2025-02-26) but the document itself is inaccessible via WebFetch. No filing party search possible.

## T5 start
TX Comptroller Ch.313 page: no searchable database returned via WebFetch (page is navigation only). Ch.313 sunset 2023, no new agreements possible for a 2025 project. JETI registry page similarly returned no data (navigation only, no embedded list). No abatement found — normal for a post-2022 9.9 MW battery project.

## T6 start
Site candidate: BUDA substation, Buda TX (Hays County) ≈ 30.085°N, -97.840°W (city-center estimate).
CDSE chip: 401 on first attempt, 403 on retry — credentials rejected. No imagery obtained. Construction verdict unknown.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~28. STOP.
