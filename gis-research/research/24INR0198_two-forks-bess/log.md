# Triage log — Two Forks BESS (24INR0198)

## T1 start
**queue_history.py** — 45 snapshots (2022-10-01 → 2026-06-01)

Milestones:
- Screening started: 2022-01-28
- Screening complete: 2022-04-26
- FIS requested: 2022-10-13
- FIS approved: — (never)
- IA signed: **2024-05-03** (present in queue since 2024-05-01 snapshot)
- Meets 6.9(1): 2024-05-06
- Meets all 6.9: — (not yet)
- Construction start/end: — (none reported)
- Approved for energization/sync/COD: — (none)

COD drift (3 slips):
- 2024-12-01 → 2025-12-04 → 2027-07-01 → 2027-06-30 (current)

MW changes: 300.0 → 307.2 → 309.0 → 309.7 → 309.8 (fine-tuning, still active)

**Assessment:** IA signed ~14 months ago, FIS never granted (unusual but not disqualifying for storage). Three COD slips over 4 years; current 2027-06-30 target is 12 months out. No construction milestones yet.

## T2 start
gmaps.py returned HTTP 429 on both attempts (rate-limited). **No pins found.** Normal for unpermitted BESS.

## T3 start
DDG search for "Two Forks BESS": aggregator hits only (interconnection.fyi, ercotqueue.com, infrasure.ai, cleanview.co). All confirm 309.8 MW BESS, Cooke County, ERCOT North, POI "684 SPRING 138kV", COD 2027.
- Developer name listed as "Two Forks LLC" on ercotqueue.com (build-chance 26%); full developer contact paywalled on interconnection.fyi
- DDG search for "Two Forks BESS LLC" Texas: no results
- No press releases or news articles found about this project
- No developer company name surfaces publicly

**No sources saved** — aggregator pages only, no project-specific news.

## T4 start
PUCT Interchange: HTTP 402 on both direct URL attempts — portal blocked (session/auth required). Cannot fetch FilingParty search.
ERCOT MIS GIS report URL: SSL handshake failure.
**IA PDF not retrieved.** IA existence confirmed from T1 queue data (iaSigned=2024-05-03); schedule exhibit/parties page unknown.

## T5 start
TX Comptroller Ch.313 portal (comptroller.texas.gov/economy/local/ch313/): no searchable data returned — page returns overview only, no county-filtered list reachable via URL params.
JETI registry: not attempted separately — Ch.313 expired post-2022; post-2022 BESS projects rarely have JETI entries.
**No abatement found.** Normal for a 2022-entry BESS project.

## T6 start
Site candidate: OSM Overpass returned 25 138kV substations in Cooke County bounding box. Two generation-type 138kV substations at ~33.5497,-97.1801 (cluster) selected as best candidate for "684 Spring" POI — no named substations in OSM for this area.
cdse.py chip at 33.5497,-97.1801 --buffer-km 2: HTTP 403 on both attempts (CDSE auth failure). **Imagery not retrieved.** Construction unknown.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~28. Run complete.


## Deep scan start — 2026-07-19

### D1 POI confirmation via Overpass
OSM Overpass query (wider Cooke County bbox 33.3-33.9N, 97.7-96.5W) returned 86 substation elements.
Two unnamed 138kV nodes at 33.5497209,-97.1801476 and 33.549617,-97.1795355 — 6m apart, almost certainly the same compound.
This is the triage candidate and independently confirms POI "684 SPRING 138kV" at ~33.5497,-97.1801.
No named "Spring" substation in OSM, but coordinates match the triage OSM inference.
Confidence: MEDIUM — confirmed as 138kV substation, not yet confirmed as "Spring".

### D2 Portal access attempts
- PUCT Interchange (https://interchange.puc.texas.gov/search/filings/?FilingPartyTxt=Two+Forks+BESS): HTTP 402 — payment-blocked. IA confirmed signed 2024-05-03 from queue data; cannot retrieve PDF.
- TX Comptroller COA: JS-rendered, search results not loadable via direct fetch. No results confirmed.
- SEC EDGAR: HTTP 403 on all endpoints.
- gmaps.py: HTTP 429 (rate-limited) — no pins found.


### D3 Critical OSM finding — Rippey Solar at POI
OSM Overpass returned "Rippey Solar plant" (plant:source=solar) at 33.5527775, -97.1785918 — 
only ~340m from the POI substation cluster (33.5497, -97.1801).
The rectangular white grid in all imagery frames (2024-2026) is almost certainly the Rippey Solar 
farm, NOT Two Forks BESS activity.
Two Forks BESS would be a compact BESS pad, likely ADJACENT to or sharing the Spring substation — 
need to look for a small gravel pad + container rows near the substation, not the large solar grid.
This means TWO projects share or use the Spring 138kV substation: Rippey Solar (existing) + Two Forks BESS (proposed/future).

### D4 Imagery interpretation revised
Contact sheet frames 2024-07-01 to 2026-06-15: the regular white-gridded panel array is Rippey Solar.
No separate BESS pad is discernible at 2km resolution from these frames.
Need a TIGHTER 0.5km chip centered on the substation to look for BESS pad construction.

### D5 Rippey Solar ownership confirmed
OSM: Rippey Solar = 59 MW solar plant, operator "Adapture Renewables, Inc.", EIA ID 62773, 
operational since 2020-12. Center 33.5527775,-97.1785918.
This is PRE-EXISTING at the Spring 138kV substation — grid in all imagery is Rippey Solar, NOT Two Forks BESS.
Two Forks BESS would be a SEPARATE compact BESS pad adjacent to this facility.
Key question: is Adapture Renewables also the Two Forks BESS developer? (co-location pattern)

### D6 Adapture Renewables — not the Two Forks developer
Adapture portfolio lists "BT Cooke Solar" (Gainesville TX, 81.4 MW, 2020) = same project as 
Rippey Solar in OSM (different name for same facility?). Their TX BESS projects are 
"Farmersville BESS" and "Junction BESS" — no "Two Forks BESS" listed.
Adapture is probably NOT the Two Forks BESS developer.
Two Forks BESS is a co-locating/neighboring project by an unidentified developer.

### D7 Developer identity — zero public trace
Exhaustive search: no press releases (PRNewswire, GlobeNewsWire, BusinessWire, AccessWire), 
no news articles (pv-tech, rechargenews, utilitydive, renewablesnow), no LinkedIn company page,
no SEC EDGAR registrations for "Two Forks BESS" or "Two Forks LLC" or similar.
TX SOS SOSDirect requires paid account; TX Comptroller COA is JS-rendered and returned no results.
PUCT Interchange 402-blocked (payment wall). IA confirmed signed 2024-05-03 from queue data only.
Developer is completely opaque publicly — either ultra-stealth or the LLC has a non-obvious name.

### D8 Imagery summary (CDSE rate-limited, 401 errors on later attempts)
Successfully obtained: s2_2026-06-15_xwide (3km), s2_2026-07-01_1km (1km), s2_2025-07-01_2km, 
s2_2025-01-01_2km, s2_2024-07-01_2km, s2_2026-04-01_2km.
All frames show Rippey Solar (pre-existing 59 MW solar, Adapture Renewables, operational since 2020-12).
No distinct BESS pad visible — the compact pad, if present, would be within/adjacent to the 
Rippey Solar substation compound. At 10m/px with 2km buffer, a 30-50 acre BESS pad near an 
existing solar substation is not distinguishable from the existing infrastructure.
Tight 0.8km chip was not obtainable (CDSE auth failed on all retry attempts after initial success).
No construction activity visible that could be attributed to Two Forks BESS specifically.

### D9 Rippey Solar = BT Cooke Solar?
Adapture website lists "BT Cooke Solar" (81.4 MW, Gainesville TX, 2020). 
OSM lists "Rippey Solar" (59 MW, operator=Adapture, start_date=2020-12, EIA ID 62773).
Same location, same operator, same start year — likely the same facility with different public names,
or the 81.4 MW is DC while 59 MW is AC nameplate. Either way: pre-existing, not Two Forks BESS.
