# Research log — HyFuels Green Lake Solar (26INR0019)

## Triage summary (2026-07-18)
- 37 queue snapshots 2023-06–2026-06; FIS requested 2023-06-13, NOT approved; no IA, no construction dates
- COD drift: 2026-10-01 → 2027-12-01 (1 slip, 14 months)
- Capacity: 120.6 → 347 MW (nearly 3×)
- Ch.313 App 1925 (Calhoun County ISD, signed 2022-12-20) confirmed; siblings 1926+1927
- Developer: BNB Renewables (jnicholas@bnbrenewables.com)
- CDSE auth failed in triage; site candidate 28.57N, -96.87W (low confidence)
- PUCT 402 in triage

## Deep scan start (2026-07-19)
Focus: App 1925 PDF, BNB Renewables identity, sibling scope, PUCT IA, Calhoun CAD, imagery

## S1 — LLC → parent chain
- BNB Renewables = BNB Renewable Energy Holdings LLC, New York NY 10007 (277 Broadway, 16th Fl)
  - Founded 2004; 1,000+ MW developed; projects incl. Bull Creek Wind, Long Draw Solar, Mesquite Creek Wind
  - Source: bnbrenewables.com homepage [sources/2026-07-19_bnbrenewables_homepage.html]
- HyFuels Holdings LLC = manager/parent of HyFuels Green Lake Solar LLC per agreement Art X.1
  - Same 277 Broadway address as BNB Renewables
  - Contact: Orlando Puig, Project Manager (opuig@bnbenewables.com)
  - Source: Ch.313 agreement p.23 [sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-agmt.pdf]
- Chain: HyFuels Green Lake Solar LLC → HyFuels Holdings LLC → BNB Renewable Energy Holdings LLC

## S2 — County records sweep
- Ch.313 App 1925 confirmed: HyFuels Green Lake Solar LLC + Calhoun County ISD, filed 2022-05-20, signed 2022-11-14
  - Project: 400 MW ac solar + battery storage, ~10 miles NW of Port Lavaca, Calhoun County
  - Construction anticipated: January 2027 – December 2027 (per Tab 4 application description)
  - Qualifying Time Period: Jan 1, 2026 – Dec 31, 2027 (per Agreement §2.3.C)
  - Tax Limitation Period: Jan 1, 2028 – Dec 31, 2037 (§2.3.D)
  - Minimum qualified investment: $30,000,000 (§2.5.A — statutory minimum for Calhoun County ISD subchapter C)
  - Application fee paid: $75,000
  - Jobs: 2 qualifying jobs (waiver granted per §313.025(f-1))
  - Sibling apps filed same day: 1926 (HyFuels Green Lake LLC) + 1927 (HyFuels Green Lake Wind LLC)
  - Source: [app PDF](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-app.pdf), [agmt PDF](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-agmt.pdf)
- Project area maps in Tab 11 of application show:
  - Vicinity map (p26): reinvestment zone (red polygon) near Victoria/Calhoun county line, NW of Port Lavaca near Clark Station area
  - Parcel map (p27): project area (blue polygon) in Calhoun County, abstracts labeled CI CO (×multiple), DLAC CO, J POINDEXTER, THOMAS INTER, PATRICK HUGHES — all in Calhoun County
  - Imagery saved: [imagery/ch313_map_page26.png], [imagery/ch313_map_page27.png]
- CAD search: esearch.calhouncad.org returned 404 for URL-based queries; portal requires JS session token (negative evidence logged)
- PUCT Interchange: HTTP 402 on all attempts (negative evidence from triage)

## S3 — Site pinpoint
- Application text: "approximately 10 miles northwest of the town of Port Lavaca, TX in Calhoun County"
- Port Lavaca: ~28.617N, -96.633W → 10 mi NW ≈ 28.76N, -96.80W
- Vicinity map (imagery/ch313_map_page26.png): red polygon near Victoria/Calhoun county line, NW of Port Lavaca, Clark Station area
- Parcel map (imagery/ch313_map_page27.png): project area (blue) on CI CO (Calhoun Improvement Co?) abstracts; PATRICK HUGHES, THOMAS INTER, J POINDEXTER parcels; diagonal road at base of project
- Clark Station, Calhoun County TX: 28.616N, -96.711W (OSM Nominatim)
- Best candidate: 28.76N, -96.83W — from bearing calculation + map alignment; medium confidence
- Google Places: HTTP 429 (negative evidence); no delivery pin found
- No PUCT IA found (402 error); no Overpass/OSM Dokmai substation found

## S4 — Satellite ground truth
- Feb 2026 xwide (28.74N, -96.87W, 6km): pure undisturbed agricultural land, bare fallow fields, zero construction activity [imagery/s2_2026-02-01_xwide.png]
- Feb 2026 xwide (28.76N, -96.80W, 6km): same — flat coastal plain agricultural, no clearing/grading [imagery/s2_2026-02-01_28.76_-96.80.png]  
- Jun 2026 grid (9 chips, 2km): heavy cloud cover, insufficient for assessment [imagery/grid_contact_sheet.png]
- VERDICT: no_activity — consistent with stated construction start Jan 2027

## NEGATIVE EVIDENCE LOG
- PUCT Interchange: HTTP 402 all attempts (triage + deep scan)
- Google Places: HTTP 429 (triage + deep scan, rate limited)
- Calhoun CAD esearch: 404 for URL-based queries (requires JS session token)
- Overpass API: 406 Not Acceptable
- Calhoun County TX website: minutes found but domain resolved to Calhoun Co ALABAMA
- Bing: no news/press releases for HyFuels Green Lake Solar
- Bing: no results for Dokmai 138kV substation location
- USGS GNIS: service temporarily unavailable


