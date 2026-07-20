
T1 result:
- 39 snapshots (2023-04-01 to 2026-06-01), 4 COD-drift events
- COD history: 2024-12-31 → 2025-12-01 → 2026-01-31 → 2026-08-31 → 2026-11-30 (current) — ~2-year total slip
- Milestones achieved: screening started 2022-11-07, screening complete 2023-02-03, FIS requested 2023-04-12, FIS approved 2025-12-17, IA signed 2025-04-15, meets 6.9(1) 2025-04-29, meets all 6.9 2026-01-29
- No construction start/end, no energization/sync/COA dates
- Strong milestone chain through IA + 6.9 complete (2026-01-29): not a paper project

T2 start

T2 result:
- gmaps.py returning 429 Too Many Requests on both attempts (rate-limited)
- No pins obtained; 0 pins logged
- No site coordinates from this step

T3 start

T3 result:
- EPC contractor: SolarMax Renewable Energy Provider Inc., $127.3M contract, also holds 8% equity in LLC
- Capacity confirmed: 430 MWh / 54.99 MW, Pecos County TX, ERCOT
- Target completion per press release: June 30, 2026 (queue COD 2026-11-30 — 5-month gap)
- SEC filing found (SolarMax EX-99.2) but 403 on direct fetch
- LLC ultimate owner not identified; SolarMax is EPC+minority equity
- Saved source summary to sources/t3_web_sweep.md
- SEC EDGAR API consistently 403 after one retry — moving on

T4 start

T4 result:
- interchange.puc.texas.gov: HTTP 402 on all URL patterns (same as all prior projects — portal requires authenticated session)
- Tried: /filingSearch, /Documents/search, /search/filings/ — all 402
- One retry attempted; no path forward without authenticated session
- IA existence confirmed from queue data (iaSigned: 2025-04-15) but PDF not retrieved
- No schedule exhibit or parties page extracted

T5 start

T5 result:
- Ch.313 expired 2022 — post-2022 project like this would use JETI (2023+)
- TX Comptroller CoA entity search: session-based, redirects — could not search "Longfellow BESS I"
- JETI registry applicants page: no direct data table accessible via WebFetch (page is JS-rendered)
- Ch.313 Pecos County search: no data returned (same issue)
- No abatement found — normal for a 2024 project (JETI possible but not accessible this run)
- Missing JETI is not strong negative signal for a 54.99 MW BESS (smaller projects often skip)

T6 start
