# Research log — Aldrin 345 BESS (25INR0425)

## Triage log (2026-07-18)

T1 start
- queue_history: 38 snapshots (2023-05-01 → 2026-06-01), 2 COD changes
- COD drift: 2025-07-15 → 2027-12-01 → 2028-03-01 (slipped ~2.7 years total)
- IA signed: 2024-06-15 (present — positive signal)
- FIS approved: 2025-04-21
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- No energization / sync / commercial operation milestones
T1 done

T2 start
- gmaps.py places "Aldrin 345 BESS": 429 Too Many Requests on first call, 429 on retry → blocked
- gmaps.py places "Aldrin 345 BESS Brazoria": not attempted (budget exhausted by block)
- pins_found: 0
T2 done

T3 start
- DDG search "Aldrin 345 BESS battery storage Brazoria Texas": developer identified as Aldrin Energy Storage LLC
- Parent company: Vesper Energy (footer copyright on aldrinenergystorage.com)
- Address: 1722 Routh Street Suite 900, Dallas TX 75201 (same as Vesper Energy Dallas office)
- Website claims 550 MW (vs 362 MW in queue) and "end of 2025" COD (both outdated/discrepant)
- Website: site is "less than 12 acres privately owned land" adjacent to existing substation
- No press releases or news articles found specifically about this project
- Third-party trackers (ercotqueue.com, interconnection.fyi, cleanview.co, infrasure.ai) all data-aggregate from ERCOT — no original reporting
- saved sources/aldrin_energy_storage_website.md
T3 done

T4 start
- interchange.puc.texas.gov: HTTP 402 on all endpoints (portal + document search) — blocked
- No IA PDF retrieved
- Note: queue timeline shows IA signed 2024-06-15; IA exists but could not be accessed
T4 done — blocked portal, negative result

T5 start
- TX Comptroller Ch.313: no searchable database accessible via WebFetch; portal returns generic content
- JETI: no registry accessible via WebFetch
- Note: post-2022 BESS projects unlikely to have Ch.313 (program expired 2022); JETI is the replacement but registry not publicly searchable
- abatement_found: false — normal for this project vintage
T5 done

T6 start
- Site candidate: Meadow 345kV substation (CenterPoint Energy), centroid 29.4603, -95.2580 (Brazoria County)
  - Derived from OSM way 583408103; confidence HIGH (POI named in IA description)
- cdse.py chips 2026-06-01 + 2023-06-01 at 29.4603/-95.2580 --buffer-km 2: HTTP 403 Forbidden on both
  - Cause: ~/.config/gis-research.env is example file only, no real CDSE credentials
- imagery: blocked — no chips downloaded, no contact sheet, no visual evidence
- construction_visible: unknown
T6 done

T7 start
- wrote triage_findings.json
- wrote triage.md
- turns used: ~27
T7 done — triage complete

---

## Deep scan log (2026-07-19)

D1 — PUCT Interchange IA PDF attempt
- interchange.puc.texas.gov/search/filings/?q=aldrin+345+bess: HTTP 402 (same as triage)
- interchange.puc.texas.gov/search/?q=aldrin+energy: HTTP 402
- interchange.puc.texas.gov/documents/<id>: HTTP 402 on multiple endpoints
- All PUCT interchange URLs blocked — system requires paid subscription
- NEGATIVE: IA PDF text not retrievable; existence confirmed by queue milestone only
- Artifact: none obtainable; logging as hard negative

D2 — Vesper Energy parent chain + financing
- aldrinenergystorage.com: confirms Vesper Energy parent (copyright footer); 550 MW claim, "end of 2025" target COD (stale)
- Website confirms site is <12 acres on privately owned land adjacent to existing substation in Brazoria County
- vesperenergy.com/news: 9 news items found (Jun 2026 → Dec 2024). NO mentions of Aldrin, BESS, battery storage, Texas battery projects, or Brazoria County
- vesperenergy.com/projects: lists 5 projects: Gaucho Solar (PA), Hornet Solar (TX solar, operational Apr 2025), Juniper Creek Storage (CA), Bradford Solar (PA), Axton Solar (VA). NO Aldrin or Texas BESS project listed
- Ownership chain confirmed: Aldrin Energy Storage LLC → Vesper Energy → Magnetar Capital (acquired 2020 from Lendlease Energy Development) + GCM Grosvenor (equity stake 2023)
- Nazareth Solar ($236M financing Jun 2026): Vesper's most recent financing. No Aldrin mentioned
- Vesper Energy has no press release, news item, or project listing for Aldrin 345 BESS
- Sources saved: sources/2026-07-19_vesperenergy_news_page.md, sources/2026-07-19_vesperenergy_projects_page.md

D3 — OSM/POI site verification
- Overpass query confirmed Meadow Substation (way 583408103):
  - Center: 29.4602°N, 95.2580°W
  - Operator: CenterPoint Energy
  - Type: transmission substation
  - Voltage: 345kV / 138kV
- Adjacent substation: North Alvin Substation (way 174401064, TNMP, 138kV, 29.4590°N, 95.2575°W)
- Location context: Meadow Substation is in the Alvin, TX area of Brazoria County (not near major population centers)
- Site area <12 acres — consistent with BESS adjacent to existing substation
- Sources saved: sources/2026-07-19_osm_meadow_substation.md

D4 — TX Comptroller entity search
- mycpa.cpa.state.tx.us/coa: redirects to comptroller.texas.gov/taxes/franchise/account-status/search (live form, not direct-query API)
- SOSDirect: paid portal ($1/search), not accessible
- TX SOS entity details for "Aldrin Energy Storage LLC": NOT retrievable via WebFetch
- NEGATIVE: Comptroller entity detail not retrieved; Vesper Energy parent chain confirmed from website evidence only

D5 — County records sweep
- Brazoria CAD (esearch.brazoriacad.org): JavaScript form-based, URL parameter searches return 404; direct owner-name search not programmatically accessible
- Ch.313/JETI: Chapter 313 expired 2022; JETI (HB5) registry searchable but no Brazoria County battery storage agreements found in comptroller portals reached
- Alvin ISD: website accessed, no JETI/313 agreements found for energy storage projects
- Brazoria County commissioners court minutes: page returned empty content
- NEGATIVE: No CAD parcels, no abatement/JETI agreements found. Expected for BESS on small owned parcel

D6 — Satellite imagery
- CDSE credentials (gis-research.env): example file only — real credentials required; cdse.py returns HTTP 403 on token request
- gmaps.py staticmap: Maps Static API not enabled for the configured key (HTTP 403)
- gmaps.py places: HTTP 429 rate limit on all calls
- NO satellite imagery obtained for this project
- NEGATIVE: construction_visible = unknown; no visual evidence of any stage

D7 — Additional developer/financing search
- SEC Form D searches: HTTP 403 blocked
- Bloomberg Law: 0 stories found for "Vesper Energy Aldrin"
- PRNewswire: no Vesper Energy releases found mentioning Aldrin/BESS
- GCM Grosvenor news: no releases mentioning Vesper Energy or Aldrin
- LinkedIn: authentication required
- CenterPoint Energy press releases: 404 on most URL variants
- No third-party news, financing announcements, EPC mobilization, or community engagement evidence found

D8 — Sibling project check (25INR0421 Aldrin 138 BESS)
- INR 25INR0421 is "Aldrin 138 BESS" — same developer, presumably same substation at 138kV level
- Both 25INR0425 (345kV, 362 MW) and 25INR0421 (138kV) appear in queue directory listing
- This indicates Vesper submitted two interconnection requests at the same Meadow substation, one at each voltage level — suggests iterating on configuration, may reflect uncertainty about final design
- The 550 MW website claim vs 362 MW queue figure may reflect this two-project portfolio or a design evolution

D9 — PUCT/CenterPoint IA via alternate routes
- puc.texas.gov/industry/electric/gen/interconnection/largegen.aspx: HTTP 402
- puc.texas.gov/industry/electric/filings/search.aspx: HTTP 402
- CenterPoint Energy website for large generators: HTTP 404
- All PUCT routes blocked; IA contents remain unverified
