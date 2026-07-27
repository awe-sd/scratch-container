# Triage log — Miranda Solar Project (24INR0161)

## T1 start

**queue_history.py** — 49 snapshots (2022-06 → 2026-06). 3 reported-COD changes.

COD drift:
- 2024-05-31 (original, held Jun-Jun 2022 = 1 snapshot)
- 2024-12-01 (Jul 2022 → Mar 2024)
- 2026-08-30 (Apr 2024 → Mar 2025)
- 2027-12-06 (Apr 2025 → Jun 2026, current) — 3+ years slippage from original

Milestones hit: screening started 2021-11-03, screening complete 2022-01-07, FIS requested 2022-06-22, FIS approved 2024-09-03, **IA signed 2024-07-16** (IA before FIS approved — independent gate, noted).
No construction milestones. No energization/COD.

Capacity: was 261.42 MW → reduced to 202.0 MW as of May 2026.

**T1 result:** IA signed July 2024 (strong signal). COD drifted 3+ years. No construction milestones yet.

## T2 start

gmaps.py returned HTTP 429 on first call and one retry. All 4 query slots blocked. **T2 result: 0 pins found.**

## T3 start

DDG sweep results:
- Miranda Solar Project LLC: TX filing Oct 15, 2021; address 580 Westlake Park Blvd Ste 515, Houston TX 77079 (from opencorporates snippet). Status: active.
- Miranda Solar Project Holding Inc: separate foreign profit corp, TX registered Feb 06, 2024. Likely parent/financing vehicle.
- Cleanview/interconnection.fyi/infrasure confirm ERCOT-24INR0161, 202 MW, McMullen, expected 2027 — all derived from queue data.
- No press releases, no news articles, no developer parent company identified.
- opencorporates and bizapedia both blocked (CAPTCHA/security check).

**T3 result:** LLC confirmed active (Houston address). Holding Inc filed Feb 2024 (financing signal). No developer parent identified. No news found.

## T4 start

PUCT Interchange returned HTTP 402 (subscription-gated) on all URL attempts. One DDG fallback search for IA/PUCT filings also returned no results (CAPTCHA wall).
Queue data confirms IA signed 2024-07-16 — IA document exists in ERCOT system but PUCT filing text is not accessible via public web in this triage.

**T4 result:** IA confirmed via queue milestone (signed Jul 2024). PUCT Interchange blocked. PDF not retrieved.

## T5 start

TX Comptroller Ch.313 page does not have a direct filterable search for McMullen County via WebFetch; JETI DDG search returned no results (CAPTCHA block). Ch.313 expired in 2022 — post-2022 filings do not qualify. No JETI application found in open web search.

**T5 result:** No abatement found. Normal for a project entering queue in late 2021/early 2022 — Ch.313 window was closing. JETI not confirmed either way but no evidence found.

## T6 start

Site candidate: Fowlerton corridor (28.46°N, -98.78°W), McMullen/La Salle border — based on POI "Tap 345kV 5709 Fowlerton - 5901 San Miguel Ckt 1". Confidence: low (POI infrastructure only, no pin or IA map).
cdse.py chip returned HTTP 401 (Unauthorized) on all 9 grid attempts — CDSE credentials not available in ~/.config/gis-research.env.

**T6 result:** Imagery blocked (credential failure). No contact sheet. Construction: unknown.

## T7 start

triage_findings.json and triage.md written. Turns used: ~28. Run complete.

**Tools blocked this triage:** gmaps.py (429), PUCT Interchange (402), CDSE imagery (401), opencorporates/bizapedia (CAPTCHA). Core queue data and IA milestone confirmed from internal data.

---

## Deep scan D0 — 2026-07-20

findings.json skeleton written. Proceeding to D1 (IA schedule).

## D1 — PUCT IA match + D3 — Site pin FOUND

**KEY FIND:** Google Places "Miranda Site Entrance" — C5CW+W9, Fowlerton, TX 78021 — lat 28.422311, lon -98.804099 — in McMullen County, right county, Fowlerton area matching POI "Tap 345kV 5709 Fowlerton". This is a strong site-entrance candidate. Pursuing immediately.

2026-07-20: puct.py match 24INR0161 — 0 hits (keys: Miranda Solar Project, Miranda Solar, Miranda). INR not in join table (24INR0161 absent from 1,743-entry puct_inr_join.json). TSP may be AEP (South Texas zone, SOUTH CDR), not Oncor — different name keys likely.
2026-07-20: ch313.py resolve — no Ch.313 or JETI match. Normal for post-2022 solar.
2026-07-20: spv.py resolve — no candidates.
2026-07-20: exhibit.py scan — no PDFs in sources/.
2026-07-20: search.py "Miranda Solar Project McMullen County Texas interconnection" — FAILED all backends.
2026-07-20: gmaps.py places "Miranda Solar McMullen County Texas" — **HIT: "Miranda Site Entrance" 28.422311, -98.804099, Fowlerton TX 78021** (type: manufacturer,point_of_interest,establishment). This is the site entrance pin.

## D1–D3 extended negative evidence (deep scan)

2026-07-20: puct.py index refresh → 2530 filings. Searched AEP Texas Inc. 2024-2026 (96 items) — no Miranda anywhere. Full 2024-2026 solar IAs (~464 items) — no Miranda. IA not yet filed with PUCT or SPV name differs from queue name.
2026-07-20: search.py "Miranda Solar Project Holding Texas renewable developer" — FAILED.
2026-07-20: search.py "580 Westlake Park Blvd Houston solar developer Miranda" — FAILED.
2026-07-20: CDSE chip (multiple attempts) — RemoteDisconnected on openEO /result endpoint. Auth OK. Platform processing outage. No imagery retrieved.
2026-07-20: TX Comptroller franchise search "Miranda Solar" — JS-gated, no results renderable.
2026-07-20: McMullen CAD (esearch.mcmullencad.org) — found portal, JS-gated owner search, no parcel data.
2026-07-20: McMullen County commissioners court agendas 2024-2025 (9 PDFs sampled) — all scanned images, no text extractable. Cannot confirm Miranda mentions.
2026-07-20: PUCT items 1879 (Bracero Pecan), 1880 (S&S Renewables) — fetched, not Miranda.
2026-07-20: Overpass API 345kV infrastructure query — HTTP 406 error. No transmission map data.
2026-07-20: opencorporates.com Miranda Solar — CAPTCHA block.
2026-07-20: SEC EDGAR / Comptroller direct search — blocked by hook (not relevant channel).

## D4-D5 — Synthesis and wrap-up
