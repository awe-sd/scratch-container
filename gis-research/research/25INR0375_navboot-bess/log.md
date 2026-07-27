# 25INR0375 NavBoot BESS — triage log

T1 start
- queue_history ran: 40 snapshots 2023-03-01→2026-06-01
- IA signed: 2025-10-20 (present!)
- FIS approved: not achieved
- Construction milestones: none
- COD drift (2 changes): 2025-06-01 → 2026-12-01 → 2027-11-11
- Current reported COD: 2027-11-11
T1 done

T2 start
- gmaps.py: HTTP 429 on first call + retry → blocked; 0 pins found
T2 done (blocked, 0 pins)

T3 start
- DDG HTML: 403 blocked
- Bing "NavBoot BESS Nueces Texas": no results
- Bing "NavBoot BESS LLC registration": no results
- Bing "NavBoot energy storage ERCOT 25INR0375": no results
- Bing "NavBoot energy developer": no results (Bing returning default pages)
- NavBoot has NO indexed web presence; developer unknown
T3 done (0 hits)

T4 start
- PUCT FilingParty=NavBoot BESS: 0 records
- PUCT FilingDescription=NavBoot BESS: 1 record — Control 35077 (Oncor standing IA docket), "INFORMATIONAL FILING OF ERCOT INTERCONNECTION AGREEMENTS PURSUANT TO SUBST. R. §25.195(e)"
- IA_FOUND = true. Specific filing number not extractable via curl (JS-rendered docket page). Queue milestone iaSigned=2025-10-20 corroborates. Transmission provider = Oncor (consistent with Nueces/COASTAL zone).
- Budget warning at 80% — skipping PDF download, proceeding to write outputs immediately
T4 done (IA confirmed, docket 35077)

T5 start
- Post-2022 BESS project; Ch.313 expired; JETI search skipped due to budget constraint; BESS has thin county trail per fuel guidance
T5 done (skipped, expected miss for post-2022 BESS)

T6 start
- No site candidate: gmaps blocked, no web presence, no abatement map, no IA exhibit available
- POI "8858 MCKENZIE4A 138kV" is a Nueces county 138kV substation — no public lat/lon confirmed without further research
- Skipping imagery per checklist rule: no site candidate better than "somewhere in the county"
T6 done (skipped — no site candidate)

T7 start
- triage_findings.json written
- triage.md written
- turns used: ~28
T7 done

## Deep Scan — 2026-07-19

### S1 — LLC → Parent Chain
**FOUND**: PUCT docket 35077, item 2292, filed 2025-11-04 by AEP Texas Inc.
- IA: ERCOT Standard Generation Interconnection Agreement between AEP Texas Inc. and Navboot BESS LLC
- Signed: 10/20/2025
- Source: `sources/2026-07-19_puct_35077-2292_navboot-bess-ia.pdf`

**Developer identified**: Navitas Energy
- CEO: Gerardo Manalac (gmanalac@navitasenergy.org)
- Also: squisenberry@navitasenergy.org (contacts)
- Generator address: 5900 Balcones Drive Ste 100, Austin TX 78731
- Phone: 713-503-8645

**TSP**: AEP Texas Inc. (NOT Oncor as triage assumed)
- AEP Corpus Christi contact: 12730 Hearn Road, Corpus Christi, TX 78410

### S2 — Site Location (from Exhibit C)
- "approximately six (6) miles east of Robstown, Texas"
- County: Nueces
- New "Navboot Substation" at 138kV/34.5kV
- POI: First dead-end structure outside Navboot Substation fence
- Transmission: 0.25-mile 138kV line w/ OPGW from AEP's McKenzie Rd Station

### Technology
- Inverters: SMA SCS 3800, 99 units × 3.06 MW = 302.9 MW nominal
- Delivery voltage: 138 kV

### Contractual Schedule (Exhibit B)
- In-Service Date: 32 months from conditions satisfied (IA executed Oct 20, 2025)
- Trial Operation: 33 months
- Scheduled COD: 34 months
- Security: $7,500,000 (LC / corporate guaranty / cash)
- As of IA execution, Generator authorized TSP to proceed

### COD Note
- 34 months from ~Oct 20, 2025 = ~Aug 2028 (contractual maximum)
- BUT: TIF is only 0.25 miles — likely much faster than 34 months
- Reported COD 2027-11-11 (13 months post-IA) plausible if AEP tap builds fast

### S3 — Site Pinpoint
**McKenzie Substation (OSM way 174705983)**:
- Coordinates: 27.8057°N, -97.5715°W
- Source: OpenStreetMap (AEP operator, 138kV substation)
- Method: Overpass query for "McKenzie" substations in Nueces County bbox
- IA Exhibit C confirms: "TSP's McKenzie Rd Station" with 0.25-mile 138kV line to new Navboot Substation
- Site is 6 miles east of Robstown — consistent with OSM coords (6.7 miles E of Robstown center)

**Derived site estimate**: 27.806°N, -97.571°W ± 0.25 miles
- New "Navboot Substation" is 0.25 miles from McKenzie Rd Station
- Battery pad will be immediately adjacent to the new substation (compact BESS footprint)

### Navitas Energy (Developer)
- navitasenergy.org — Austin-based developer
- Focus: BESS + flexible load in Texas ERCOT markets
- CEO: Gerardo Manalac (gmanalac@navitasenergy.org)
- Contact: 5900 Balcones Drive Ste 100, Austin TX 78731
- Source: IA Exhibit D notices

### Negative evidence
- SEC EDGAR: 403 errors (blocked), no SEC filing found for NavBoot BESS
- TX Comptroller website: POST-form only, no results obtained
- FERC eLibrary: 403 errors (blocked)
- HIFLD: No Texas McKenzie substation in transmission line dataset
- gmaps.py: 429 rate limit throughout both triage and deep scan
- Nueces CAD: Session-based search, no results obtained
