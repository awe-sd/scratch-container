# Research Log — Trailblazer Solar (27INR0578)

Research started: 2026-07-19
Project: 323.02 MW Solar PV, Nolan County TX, POI: #11420 Sweetwater East Switch 345 kV, CDR: WEST, COD claim: 2027-12-12

---

## Stage 1 — LLC / parent chain

## Queue history (queue_history.py)
- First snapshot: 2026-03-01. Only 4 monthly snapshots (2026-03 through 2026-06).
- Screening started: 2026-03-18; completed: 2026-06-15
- FIS requested: 2026-03-11; NOT approved yet
- IA NOT signed; no construction start/end; no milestones beyond screening
- COD stable at 2027-12-12 since first appearance — zero drift
- IMPLICATION: Very new queue entrant. No IA signed, no FIS approved. COD 2027-12-12 is 18 months from now (Jul 2026). Achieving that COD with no IA signed is extremely tight.
- Artifact: timeline.md (generated)

## Stage 1 — LLC / parent chain

- TX Comptroller entity search: mycpa.cpa.state.tx.us redirects to generic form; cannot query via WebFetch (no POST form submission). NEGATIVE.
- Web searches (Bing x10+): "Trailblazer Solar" Texas returns NO matches — only Chevrolet Trailblazer, Salesforce, Trailblazer Mortgage. Zero developer attribution found.
- PR Newswire search: No results for "Trailblazer Solar"
- SEC EDGAR search: 403 forbidden
- "Sweetwater East Switch" AEP search: No results found
- PUCT Interchange: 402 Payment Required (requires login portal)
- NEGATIVE: Could not identify LLC parent, developer, EPC, or offtaker.

## Stage 2 — County records

- Nolancad.org / nolancad.net: DNS not found — CAD portal offline or different domain
- Ch.313 database: comptroller.texas.gov only shows navigation; no searchable agreements DB found via WebFetch
- Sweetwater ISD / Blackwell ISD: no results for solar agreements found
- TCEQ: not applicable (solar — absence expected)
- NEGATIVE: Could not find any county records, CAD parcels, or tax abatements

## Stage 3 — Site pinpoint

- Google Places: HTTP 429 rate limit errors (repeated)
- Known: POI = "#11420 Sweetwater East Switch 345 kV" in AEP Texas West territory; Nolan County. Sweetwater TX ≈ 32.47°N, 100.41°W
- "Sweetwater East" would be east of Sweetwater city; searching for substation location


## Stage 3 — Site pinpoint

- Google Places: ALL queries rate-limited (HTTP 429); no delivery pins found
- Sweetwater TX coordinates: 32.4710°N, 100.4059°W (OSM Nominatim confirmed)
- "Sweetwater East Switch 345 kV" — no public coordinates found via web search, OSM, AEP Texas, or ERCOT sources
- Estimate: ~7-15 mi east of Sweetwater along I-20 corridor = ~32.44°N, 100.20-100.30°W (low confidence — POI-named only, no artifact)
- AEP Texas website: no accessible maps showing substation locations
- Overpass API: HTTP 406 errors; could not retrieve OSM substation data
- NEGATIVE: No confirmed lat/lon for project site. Method = POI-named estimate only.

## Stage 4 — Satellite imagery

- Pulled 3 current chips (2026-07-01 ±15d) covering the estimated site area:
  - s2_2026-07-01_sweetwater.png — centered on Sweetwater city (32.47°N, 100.41°W): undisturbed ranchland/farmland, no solar signature
  - s2_2026-07-01_center.png — east of Sweetwater (32.44°N, 100.30°W): undisturbed ranchland, industrial area NW corner (appears to be Sweetwater industrial/gypsum), no solar signature
  - s2_2026-07-01_northeast.png — northeast of Sweetwater (32.50°N, 100.22°W): undisturbed rangeland along I-20 corridor, no solar signature
- VERDICT: no_activity across all chips in the estimated site area
- EARLY-EXIT applied: no construction activity visible; consistent with queue state (no IA signed, 4 months in queue)
- NOTE: Exact site location unknown — cannot confirm 0 activity at the actual site, only across ~18 km radius from Sweetwater city center. The no_activity verdict is qualified by location uncertainty.

## Stage 5 — Summary

- Queue state: Screening done, FIS requested but NOT approved, IA NOT signed. 4 snapshots only (Mar-Jun 2026).
- No developer identified anywhere (web, PR, SEC, places). Extremely new project.
- No county records (CAD, abatement, Ch.313/312) found.
- No construction activity visible in imagery across estimated site area.


## CloudBurst AI / CB Sweetwater finding

- Sweetwater Reporter article dated 2026-06-25: "CloudBurst AI Data Center Moving Forward in Sweetwater After Commissioners' Vote"
  - Entity: CB Sweetwater, LLC (or its subsidiary), collectively "Cloud Burst"
  - Project: 300 MW AI-ready data center campus; Nolan County tax abatement
  - Reinvestment zone with improvements >$5.25 million
  - Source: saved to sources/2026-07-19_sweetwaterreporter_cloudburst-ai-data-center-commissioners.html
  - PAYWALL: article is paywalled beyond intro paragraph; limited data extracted
- Triage (from prior run) reported: "Trailblazer Infrastructure LLC" as developer, different from "CB Sweetwater LLC"
- Possible interpretations: (a) CB Sweetwater = subsidiary of Trailblazer Infrastructure; (b) separate entity; (c) triage agent misidentified
- NO direct link between "Trailblazer Solar LLC" and "CB Sweetwater LLC" / "CloudBurst AI" confirmed in any source
- WORKING HYPOTHESIS: Trailblazer Solar LLC is the solar SPV associated with the CloudBurst/CB Sweetwater data center development; solar filed ERCOT queue March 2026 (same month period as data center planning); co-location or behind-the-meter power supply structure
- Cannot confirm without IA or corporate filings connecting the two entities

