# Triage log — Graphic Packaging Gas (26INR0111)

## T1 start

**Queue history** — 30 snapshots (2024-01-01 → 2026-06-01), 3 COD changes.

| Milestone | Date |
|---|---|
| Screening started | 2024-01-11 |
| Screening complete | 2024-03-19 |
| FIS requested | 2024-01-05 |
| FIS approved | 2024-12-03 (first appeared 2026-06-01 report — backdated fill) |
| IA signed | — |
| All others | — |

COD drift: 2026-01-01 → 2026-04-07 → 2026-07-11 → **2027-02-15** (3 slips, ~13 months total)

No IA. No construction milestones. FIS approved but no IA — still early gate.

## T2 start

gmaps.py — HTTP 429 on first attempt, 429 on retry. API rate-limited. No pins found.
No delivery pin from gmaps. T2 budget exhausted.

## T3 start

DDG: CAPTCHA on both queries (no retry per rules).
Bing: 3 queries — no results for "Graphic Packaging Gas", "Graphic Packaging Gas LLC", or "Graphic Packaging McLennan cogeneration". Bing returned generic unrelated results.
Hypothesis: Graphic Packaging International (GPI) is a major paperboard/packaging company; this is likely a behind-the-meter cogeneration project at their Waco mill, but no web confirmation found.
No news, no LLC registration hits, no developer identified. T3 = negative.

## T4 start

PUCT Interchange: HTTP 402 on all endpoints (FilingParty search, Description search, Default page). Site requires authentication. Budget exhausted after 4 attempts (1 retry). No IA found, portal blocked.

## T5 start

TX Comptroller Ch.313: Page returned navigation links only, no searchable agreement data accessible via WebFetch (no direct county-filtered list). JETI registry page similarly navigation-only, no applicant database exposed. No abatement found. Normal for a post-2022 project (Ch.313 expired; JETI is new and sparse). T5 = negative.

## T6 start

No delivery pin from T2. No IA map or abatement. Searched "Castleman Substation" and "Peppervine Switch" (ERCOT POI facility IDs 3544/3446) — no web hits giving coordinates. Graphic Packaging International locations page has no Texas facilities listed.
Site candidate = only "somewhere in McLennan County" (county centroid ~31.55, -97.15). Per checklist: no site candidate better than county → SKIP imagery. T6 = no imagery run.

## T7 start

triage_findings.json and triage.md written. Deep scan not recommended. Turns used: ~25. Run complete.
