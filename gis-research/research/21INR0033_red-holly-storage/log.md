T1 result: 91 snapshots (2018-12-01 → 2026-06-01). IA signed 2020-10-19. No FIS approved, no construction milestone dates. COD drift: 2021-07-01 → 2023-08-01 → 2024-05-31 → 2026-05-30 → 2027-06-01 → 2028-05-30 (5 slips, ~7yr total). Current COD 2028-05-30 held since 2024-11-01.

T2 start
T2 result: gmaps.py returning 429 (rate limited) on both attempts. No pins found. Normal — battery storage sites rarely have Google Places listings.

T3 start
T3 result: DDG returned CAPTCHA pages (blocked). Bing returned no relevant results for "Red Holly Storage" + Texas/battery/ERCOT/LLC, and "Red Holly" + Dawson County + energy. No developer name, press release, or news found. No pages saved to sources/.

T4 start
T4 result: PUCT interchange.puc.texas.gov returns 402 (blocked, likely requires session/auth). Bing site: search and direct PUCT+IA searches returned CAPTCHA or unrelated results. No IA PDF found. Note: queue timeline shows iaSigned=2020-10-19 — IA exists but not located via web this pass.

T5 start
T5 result: TX Comptroller Ch.313 page has no searchable database (confirms no public-facing Ch.313 search tool online). JETI page also has no public search tool. Bing search for Red Holly Storage + Dawson County + abatement/Ch.313/JETI returned no results. No abatement found. Normal for post-2022 battery projects.

T6 start
- POI: "tap 345kV 59900 Longdraw - 79641 Farmland". Attempted nominatim, Bing, OpenInfraMap, and ERCOT bus-number searches for both substation names — all blocked (CAPTCHA) or returned empty. gmaps still 429.
- No site candidate better than county centroid (Lamesa, TX ~32.73, -101.95). Battery site requires 1-km chip; county-only too coarse.
- T6 result: SKIP imagery — no site candidate. Log: "no site candidate".

T7 start
- Wrote triage_findings.json and triage.md.
- Turns used: ~22. Deep scan NOT recommended.
- T7 complete.
