# Triage log — 27INR0261 Tipperary Solar

T1 start
## T1 results
- 25 snapshots (2024-06-01 → 2026-06-01)
- COD drift: 2027-09-30 (held 2024-06 to 2025-01) → 2028-03-15 (held 2025-02 to 2026-06). 1 slip ~6 months.
- Milestones: Screening started 2024-06-13, Screening complete 2024-09-10, FIS requested 2024-05-17
- FIS approval, IA signed, all 6.9 gates, construction start/end: ALL missing (—)
- Early-stage project: no IA, no construction milestones. FIS requested but not yet approved.

T2 start
## T2 results
- gmaps.py: HTTP 429 (rate-limited) on all 3 attempts. Per rules: one retry consumed, no pins found.
- 0 delivery pins found.

T3 start
## T3 results
- DDG: CAPTCHA-blocked (both queries). One retry consumed.
- Bing: 3 queries for "Tipperary Solar Texas ERCOT", "Tipperary Solar LLC Schleicher County", "Tipperary Solar developer energy solar" — all returned zero relevant results. Only Ireland geography results.
- No developer name surfaced. No news, press releases, or company registration found.
- news_found: false

T4 start
## T4 results
- interchange.puc.texas.gov: HTTP 402 on all direct queries (FilingParty, Description, root). Portal blocked.
- Bing site-search for PUCT filings: Bing CAPTCHA, no results.
- ia_found: false. No IA or related PUCT filing found.

T5 start
## T5 results
- TX Comptroller Ch.313 page loaded but no filterable database accessible via URL parameter — page shows nav only.
- JETI registry Bing search: no relevant results for Schleicher County solar.
- abatement_found: false. Normal for a 2027-era project (post-2022 Ch.313 expiry; JETI applications not yet visible if any).

T6 start
## T6 results
- POI: "6498 Live Oak AEP 69kV" — attempted 2 Bing searches for substation coords; no location data returned.
- No pin (T2), no IA map (T4), no abatement map (T5). Site estimate = "somewhere in Schleicher County."
- Per rules: no site candidate better than county-level → SKIP imagery. construction_visible: false by default.

T7 start
## T7 results
- triage_findings.json written
- triage.md written
- Turns used: ~22. Deep scan NOT recommended.
