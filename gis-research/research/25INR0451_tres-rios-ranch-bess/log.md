# Triage log — 25INR0451 Tres Rios Ranch BESS

T1 start

## T1 — Queue history
- 38 snapshots, 2023-05-01 → 2026-06-01
- IA signed: 2025-12-30 (first in 2026-01 report) ✓
- FIS approved: never achieved
- COD drift: 2025-12-31 → 2027-12-31 (slipped ~2 years, changed 2024-08-01, held since)
- Capacity: 242 MW → 0 MW (2023-07) → 290 MW (2024-08) — re-entered at higher capacity
- No construction milestones (start/end/energization/sync/COA all blank)
- IA signed without FIS approved — per CLAUDE.md milestones are independent gates, this is possible

T2 start

## T2 — Delivery pins
- gmaps.py: HTTP 429 (rate-limited) on first call; second call also 429 — budget exhausted, no pins
- No coordinates from gmaps

T3 start

## T3 — Web sweep
- DDG: CAPTCHA block (1 retry, negative)
- Bing: "Tres Rios Ranch BESS" — no hits
- Bing: "Tres Rios Ranch BESS LLC" OR "25INR0451" — no hits
- Bing: "Tres Rios Ranch" + BESS + Upton Texas — no hits
- Bing: "76008 Twelvemile" 345kV — no hits (76008 returns ZIP code results only)
- No developer name, no LLC confirmation, no news/PR found
- sources/ empty

T4 start

## T4 — PUCT Interchange
- interchange.puc.texas.gov returning HTTP 402 on ALL endpoints (not CAPTCHA — portal requires payment/auth subscription)
- Tried: /search/filing, /search/filings/, /Documents/search, homepage — all 402
- Budget exhausted after second attempt per rules
- No IA document retrieved; IA existence confirmed from T1 queue data (iaSigned=2025-12-30) but full text not obtained

T5 start

## T5 — Abatements
- Ch.313: TX Comptroller site did not return agreement-level data from standard URLs (page served generic landing page; no county filter worked via WebFetch)
- JETI registry: texas-jeti.com DNS not found; comptroller.texas.gov/economy/development/prop-tax/jeti/applications.php returned a data-loading error
- No Ch.313 or JETI entry confirmed for Tres Rios Ranch BESS in Upton County
- Note: Per PLAYBOOK, post-2022 projects without JETI is normal — Ch.313 program expired 2022; JETI is the successor. Absence is not disqualifying.

T6 start

## T6 — Imagery
- No pin from T2 (gmaps rate-limited); no IA map from T4 (PUCT blocked)
- Attempted to locate "76008 Twelvemile 345kV" substation: Bing searches returned nothing; Overpass API 429; USGS geonames 503; openinframap no substation data returned
- Cannot resolve POI substation to coordinates within budget
- Site candidate = "somewhere in Upton County" only — per checklist rules, SKIPPING imagery
- No contact sheet run; no imagery evidence

T7 start

## T7 — Outputs written
- triage_findings.json: written
- triage.md: written
- Turns used: ~28 of 35 budget

TRIAGE COMPLETE

## Deep scan — Stage 1-2 begins

### Stage 1: LLC/developer search
- TX Comptroller COA search API: 403/redirect, form-only; no entity data returned
- TX SOS SOSDirect: paid service ($1/search), not available
- Web searches (Bing/DDG): "Tres Rios Ranch BESS LLC" — zero hits across all search engines
- No developer identity established; no news, no PRs, no LinkedIn presence

### Stage 2: PUCT Interchange
- All PUCT interchange endpoints returning HTTP 402 (payment required)
- IA existence confirmed from queue data (iaSigned = 2025-12-30) but full IA text not retrieved
- Could not extract: IA parties, POI description text, financial security amount, schedule exhibits

### Stage 2: County records / Abatements
- Upton County CAD: multiple portal attempts (upton.cad.state.tx.us, uptoncad.org, trueautomation cid=163/195) — all DNS errors or session errors; no parcel search possible
- JETI/Ch.313: post-2022 project, Ch.313 expired 2022; JETI absence not disqualifying

### Stage 3: Substation location research (critical for satellite imagery)
- ERCOT TPIT xlsx downloaded (DocID 1250353235 — HTML auth error, downloaded separately)
- ERCOT TPIT (July 2026) confirms:
  - TPIT 6719A: "Twelvemile Substation Addition — Cuts into first circuit" | Status: IN-SERVICE | ISD: 2025-05-30 | TSP: LCRATSC | Counties: Pecos + Crockett | Buses: 7053, 76008, 76015
  - TPIT 6719B: "Twelvemile Substation Addition — Cuts into second circuit" | Status: Planned | ISD: ~2025-06 | Same TSP/counties/buses
  - TPIT 20RPG018: "Upgrade Bakersfield to Schneeman Draw" — upgrades substation equipment at Bakersfield, Cedar Canyon, **Twelvemile**, Noelke, Single Tree, and Schneeman Draw on the STEC 345-kV double circuit line
- Bus 76008 = Twelvemile 345kV = the POI for project 25INR0451 ✓
- Sources: ERCOT TPIT XLSX (DocID 1250353235) sharedStrings.xml

### Stage 3: Geographic triangulation
- Bakersfield, Pecos Co TX: 30.8913,-102.2979 (confirmed via Nominatim)
- AEP Texas North Co. 345kV line: 30.9762,-102.2891 (near Bakersfield) → 31.0472,-100.5431 (Schleicher Co.)
- Line routes through: Pecos Co → Crockett Co → Schleicher Co (reverse geocoded 4 points)
- TPIT confirms Twelvemile substation counties = Pecos + Crockett
- North McCamey substation at 31.1536,-102.2232 = Upton County (confirmed via reverse geocode)
- Sharyland/AEP N-S 345kV from North McCamey goes up through Upton Co to Ector/Midland
- CONCLUSION: Twelvemile 345kV (bus 76008) is on the E-W Bakersfield→Schneeman Draw line in Pecos/Crockett Co.
  The Tres Rios Ranch BESS is in Upton County (per queue) and likely connects via gen-tie south to Twelvemile
  OR the Twelvemile sub is near the Upton/Crockett county line (line passes at ~30.97-31.05 lat)
- Estimated Twelvemile location: ~31.0, -101.6 to -101.8 (southern Crockett County, ~20-30 km south of Upton County southern boundary)

### Stage 3: Delivery pins
- gmaps.py returned 429 on all attempts (rate-limited)
- Nominatim: no results for "Tres Rios Ranch" in TX or Upton County
- OSM: no node named "Twelvemile" substation in Texas

### Stage 4: Satellite imagery
- SKIPPED — no credible site pin established for the BESS in Upton County
- Cannot run imagery without a concrete lat/lon; county-centroid search expressly prohibited by PLAYBOOK
- Twelvemile substation (POI) in Pecos/Crockett is confirmed in-service as of 2025-05-30 per TPIT 6719A
  but BESS pad is expected in Upton County (different location, ~20-30 km north)

### Verdict decision
- IA signed 2025-12-30: confirmed (queue milestone data)
- Twelvemile POI substation: in-service as of 2025-05-30 per ERCOT TPIT (6719A) — POI infrastructure REAL
- Developer: UNKNOWN — zero public footprint
- Site: no pin, no parcel, no satellite
- FIS not approved despite IA signed — possible anomaly or FIS waived
- COD reported 2027-12-31: 24 months from IA signing; BESS builds 12-18 months — feasible if procurement started at IA
- Verdict: **real_early** — IA signed + POI substation confirmed in-service; no construction evidence found; developer unknown
- Independent COD: 2028-Q1, drift risk: medium (tight schedule, no procurement evidence, developer unknown)

