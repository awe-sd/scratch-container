# Triage log — Quantum Storage (26INR0310)

## T1 start
- queue_history.py ran: 29 snapshots, 2024-02-01 → 2026-06-01
- COD drift: 3 changes (2026-03-31 → 2026-06-30 → 2026-06-01 → 2026-07-21)
- Key milestones: Screening complete 2024-06-19, FIS approved 2025-06-16, IA signed 2023-10-26, Meets 6.9 2025-08-04, Approved for energization 2026-03-26, Approved for synchronization 2026-04-10
- Construction start/end: NOT reported (both null)
- Capacity stable at ~321 MW (minor fluctuations)
- Note: IA signed date (2023-10-26) appeared in queue first at 2024-12-01 — possibly backdated or late entry
- Note: "Commercial operation approved" = null, despite COD claim of 2026-07-21 (3 days from now)

## T2 result
- gmaps.py: HTTP 429 on all calls (rate-limited), retry also 429 — API unavailable
- No pins found

## T3 result
- DDG: CAPTCHA blocked on all queries
- Bing: "Quantum Storage" returns no relevant project results — only quantum physics / unrelated companies
- Bing: "Quantum Storage LLC" returns no entity registration hits
- TX Comptroller redirect encountered (budget exhausted before retry)
- No developer name, no news/PR, no LLC entity identified
- Project appears to have no public web footprint

## T4 result
- PUCT Interchange: HTTP 402 on all endpoints (interchange.puc.texas.gov, puc.texas.gov/agency) — portal blocked
- Retry also 402 — no IA found, no filings retrieved
- Note: IA signed milestone IS in queue data (2023-10-26), so IA exists but PDF not retrieved

## T5 result
- TX Comptroller Ch.313: page returned navigation only, no data — Ch.313 closed to new applicants post-2022
- JETI registry: page returned navigation only, no searchable data accessible
- No abatement found — normal for post-2022 BESS project without JETI entry
- Note: no JETI entry found is expected but not confirmable without working search access

## T6 start
- No delivery pin from T2; no IA map from T4
- Best site candidate: POI = "60089 Kilby Switching Station 345kV" in Haskell County, TX
- Will attempt to locate Kilby Switching Station coordinates via web search, then run imagery

## T6 result
- Budget exhausted (8 calls) on substation location research — no imagery run
- "Kilby Switching Station" not found by that name in OSM or Bing/ERCOT web search
- 345kV substations in Haskell County area from Overpass API:
  * Clear Crossing Substation: 33.0014, -99.6055 (345kV)
  * Baker Ranch Substation: 33.3699, -99.5891 (345/34.5kV)
  * Gauss Substation: 33.4789, -99.6616 (345kV)
  * Foxtail Switching Station: 33.6463, -99.4208 (345kV)
- "Kilby" name may be ERCOT internal naming not reflected in OSM
- Site candidate confidence: LOW (substation identified, name unconfirmed)
- No imagery = construction_visible unknown

## T7 result
- triage_findings.json written
- triage.md written
- Turns used: ~26
- T7 complete — triage done

## D1 — Developer identity confirmed
- **Developer: Intersect Power** (140 New Montgomery St 11th Fl, San Francisco CA 94105)
- Haskell CAD owner records (taxYear=0): IP QUANTUM BESS LLC + IP QUANTUM II BESS LLC
  - IP QUANTUM BESS LLC: "BESS FACILITY-320 MWAC", "COD JAN 1 2026 PAINT CREEK ISD", $173.5M market value
  - IP QUANTUM II BESS LLC: "BESS FACILITY-320 MGAC", "COD JAN 1 2026 HASKELL ISD", $175.4M market value
  - Total BESS market value on tax rolls: ~$349M
- Solar co-located project (21INR0207):
  - IP QUANTUM I LLC: "200 MGW SOLAR PROJECT", "CWIP 2026 PAINT CREEK", $85.1M
  - IP QUANTUM II LLC: "200 MGW SOLAR PROJECT SPLIT", CWIP 2026 Haskell ISD 53% + Paint Creek 47%
- Lease name "COD JAN 1 2026" = CAD assessment date, likely effective date; ERCOT approvedForCommercialOperation still null as of 2026-06-01 snapshot
- Paint Creek ISD = confirms location in Paint Creek area of Haskell County
- Intersect Power address: 140 New Montgomery St, San Francisco = confirmed (searchable on LinkedIn/web)

## D2 — Site location via Paint Creek ISD
- "Paint Creek ISD" in lease names = school district serving north-central Haskell County
- Paint Creek is a community in northeastern Haskell County near coords ~33.35N, -99.45W
- TPIT confirmed Kilby SS is on Clear Crossing to Pendulo 345kV line, in Haskell County
- Proceeding to run imagery around Paint Creek area and Kilby SS location


## D3 — Intersect Power Quantum press release confirmation
- Google/Intersect June 2026 press release: "Quantum begins operations this month (June 2026)"
- Full name: "Quantum Clean Energy Project", 640 MW solar + 1.3 GWh battery storage, Haskell County TX
- Announced November 2025 as first Google/Intersect co-located site
- Google data center at same site "recently began construction" (as of June 2026)
- Acquisition of Intersect by Alphabet/Google closed March 2026
- Source: https://www.intersect.com/news/google-and-intersect-deepen-texas-roots-with-new-data-center-and-energy-investments-in-gray-and-roberts-counties
- Key discrepancy: PR says "begins operations June 2026" but ERCOT queue shows approvedForCommercialOperation=null as of 2026-06-01 snapshot AND COD still listed as 2026-07-21
- CAD lease name "COD JAN 1 2026" may refer to tax assessment effective date, not actual COD
- Combined ERCOT queue: 21INR0207 (321.66 MW solar) + 26INR0310 (321.75 MW BESS) ≈ 643 MW solar + ~320 MW (4hr = 1.28 GWh ≈ 1.3 GWh) BESS

## D4 — Site confirmed via imagery (from prior deep scan run)
- Imagery at 33.000, -99.612 (3km buffer, 2026-07-01): large operating solar array fully visible
- Module rows clearly distinct; appears substantially complete/operating
- Substation/O&M building visible (light-colored); gravel pad with structures (BESS candidates)
- Site center estimated: ~33.000, -99.612 (±0.005 deg) — method: imagery centroid
- Paint Creek ISD school at 33.0634, -99.6747 = ~7km NNW of site center
- Wide 5km chip confirms no other solar/BESS development in this area


## S1 — Synthesis run (2026-07-19, main agent)

### S1-a: Press release confirmed
- WebFetch intersect.com/news/google-and-intersect-deepen... → confirmed "Quantum will begin operations this month" (June 2026)
- Full name: Quantum Clean Energy Project, 640 MW solar + 1.3 GWh storage, Haskell County TX
- Source saved: sources/2026-07-19_intersect_quantum-operations-PR.html
- Decisive: developer statement of operations in June 2026

### S1-b: PUCT still blocked
- interchange.puc.texas.gov all endpoints return 402 — IA PDF not retrieved
- Financial security amount unknown; IA signed date from queue = 2023-10-26

### S1-c: Imagery reviewed
- s2_2026-07-01_solar_3km.png: large fully-built solar array + substation compound visible; operating
- s2_2026-07-01_substation_1km.png: white O&M building, gravel pad with rectangular BESS-consistent structures
- Verdict: operating

### S1-d: TPIT confirmed
- ERCOT TPIT 80508: "Kilby: Construct New 345kV Station — Interconnect Quantum Solar — IN-SERVICE 2026-01-27"
- Transmission owner ETT; node IDs 60089 = POI match

### S1-e: Synthesis outputs written
- findings.json: verdict real_active, COD 2026-Q3, drift risk low
- dossier.md: all sections complete
- Map not generated (Google Maps Static API not enabled)
