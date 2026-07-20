# Triage log — 22INR0504 Barton Branch IA

T1 start
## T1 — Queue history
- 64 snapshots (2021-03-01 → 2026-06-01)
- COD drift count: 8 changes; started 2022-02-01, current 2026-10-01
- Key milestone dates: Screening complete 2021-05-28, FIS approved 2025-06-16, IA signed 2025-06-18
- Meets 6.9(1) and all 6.9: both 2025-08-01
- No construction start/end dates; no energization/sync approvals
- Capacity: 101.63 MW → 200.0 MW (2023-06) → 203.62 MW (2025-06); roughly doubled
- COD has bounced widely; 2026-10-01 current claim with IA now in place

T2 start
## T2 — Delivery pins
- GMaps API returned 429 (rate-limited) on first and retry calls; no pins obtained.
- 0 pins found. Normal for a battery project without a named facility.

T3 start
## T3 — Web sweep
- DDG: 403 blocked on both queries.
- Bing: returned garbage/unrelated results for "Barton Branch IA" + battery storage Texas, "Barton Branch IA LLC", and alternate search.
- SEC EDGAR site search: CAPTCHA blocked.
- Texas Comptroller redirected to franchise account status page (dynamic form, no static lookup).
- No developer name surfaced; no news, press releases, or registrations found.
- Result: 0 useful web hits; no developer ID.

T4 start
## T4 — PUCT Interchange
- interchange.puc.texas.gov: returned HTTP 402 on ALL attempts (FilingParty=Barton+Branch+IA, Description=Barton+Branch+IA, root URL, search endpoint).
- Queue data confirms IA signed 2025-06-18; the filing exists but is inaccessible via WebFetch.
- ia_found: false (file not retrieved); queue confirms execution date.

T5 start
## T5 — Abatements
- TX Comptroller Ch.313: site redirected to generic overview pages; no Robertson County entries accessible.
- JETI applications page: returned "problem loading data" error.
- JETI current agreements: 11 active agreements listed, none for Robertson County or "Barton Branch".
- Ch.313 program closed to new applications Sep 2022; 22INR0504 filed after cutoff — no abatement expected.
- abatement_found: false. Normal for this project's vintage.

T6 start
## T6 — Imagery
- Site candidate: Oak Grove Power Plant area (~31.18, -96.49), Robertson County.
  Oak Grove is known major power plant in county; POI "TNP One" (Tenaska Power Plant #1)
  likely sits nearby; no confirmed substation coords found.
- CDSE chip generation: 401/403 auth errors on all 9 grid chips — CDSE creds not valid in this env.
- contact_sheet: not produced.
- construction_visible: unknown — no imagery obtained.

T7 start
## T7 — Final output
- triage_findings.json written
- triage.md written
- Turns used: ~28
- Blockers this run: GMaps 429, DDG/Bing noise, PUCT 402, CDSE 401/403
