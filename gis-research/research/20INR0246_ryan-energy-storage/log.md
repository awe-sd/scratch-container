# Triage log — Ryan Energy Storage (20INR0246)

## T1 start
- Script: `queue_history.py 20INR0246` → 90 snapshots, 5 reported-COD changes
- IA signed: 2021-02-18 ✓
- FIS approved: 2025-09-16 (late — 6 years after FIS requested 2019-03-15)
- Meets 6.9(1): 2022-08-03; Meets all 6.9: 2026-01-27
- Construction start/end: not reported
- COD drift: 2020-08-31 → 2022-04-01 → 2023-01-09 → 2024-10-21 → 2027-03-31 → 2026-12-12 (5 changes; currently 2026-12-12)
  - Notable: was 2027-03-31 for ~12 months (2024-07 to 2025-06), then pulled in to 2026-12-12
- Capacity grew: 47.12 → 50.0 → 51.6 MW
- T1 done.

## T2 start
- gmaps.py places "Ryan Energy Storage" → HTTP 429 (rate-limited)
- Retry: gmaps.py places "Ryan Energy Storage Coryell County Texas" → HTTP 429 again
- T2 result: 0 pins found (API rate-limited, budget exhausted). Normal for storage project.
- T2 done.

## T3 start
- Bing search "Ryan Energy Storage LLC Texas battery storage ERCOT" → no relevant results (Ryan's World, Ryan Homes noise)
- Bing search "Ryan Energy Storage" + "Coryell" OR "20INR0246" → no results
- Bing search site:sos.texas.gov → CAPTCHA blocked (one allowed retry hit earlier 429 on gmaps); treating as blocked
- Bing search "TNPancake" + "Ryan" + storage + Coryell → no results
- No developer name, LLC registration, or news found
- T3 done.

## T4 start
- interchange.puc.texas.gov → HTTP 402 Payment Required on all URL patterns (search, documents, root)
- Bing search for PUCT filings → CAPTCHA blocked
- Cannot access PUCT Interchange directly; IA confirmed from queue timeline (iaSigned = 2021-02-18) but PDF not retrievable
- T4 done: IA existence confirmed via queue data; PDF not retrieved (portal blocked).

## T5 start
- Bing search Ch.313/JETI "Ryan Energy Storage" Coryell → no results
- comptroller.texas.gov/economy/local/ch313/ → navigation page only, no searchable data accessible
- Project entered queue 2019/2020; Ch.313 expired 2022; JETI launched post-2022 — no abatement expected or found
- T5 done: no abatement found (normal for post-2022 or small 51.6 MW storage project).

## T6 start
- Site candidate: Pancake community, Coryell County, TX — coordinates 31.618°N, 97.800°W (Wikipedia); TNPancake substation expected near community
- Confidence: medium (named community matches POI "TNPancake", no pin or IA map to confirm)
- cdse.py chip (current date 2026-06-01, buffer 2km) → HTTP 401 Unauthorized (CDSE token auth failure)
- Retry with direct chip call → same 401
- CDSE credentials not valid; imagery skipped per blocked-portal rule
- T6 done: no imagery obtained; site candidate is Pancake, TX area (lat=31.618, lon=-97.800).

## T7 start
- Wrote triage_findings.json and triage.md
- Turns used: ~28
- T7 done. Stopping.
