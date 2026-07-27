# Triage log — Bypass BESS II (26INR0525)

## T1 start
- 20 snapshots: 2024-11-01 → 2026-06-01
- Screening started 2024-11-19; complete 2025-02-18
- FIS requested 2024-10-23; FIS NOT approved
- IA NOT signed; no construction milestones
- COD drift: 3 changes — 2026-05-01 → 2026-06-01 → 2027-04-30 → 2028-04-30 (pushed ~2 years)
- Capacity cut: 415.97 MW → 205.86 MW in Feb 2026 (halved)
- Status: pre-IA, FIS pending — very early stage

## T2 start
- gmaps.py places "Bypass BESS II" → 429 Too Many Requests (retried once, same result)
- gmaps.py places budget exhausted; no pins found
- Result: 0 delivery pins

## T3 start
- "Bypass BESS" (original) confirmed: Aypa Power (Blackstone), Fort Bend County, 200MW/400MWh, $190M financing closed, offtake secured
- "Bypass BESS II" (26INR0525): cleanview.co + ess-news.com confirm 206MW BESS, Fort Bend, 2028 COD, offtake "already secured"
- Developer for II: strongly implied Aypa Power (same county, same specs as I)
- LLC "Bypass BESS II LLC" not found in web search; original used "Bypass BESS LLC"
- No press release specific to II found; coverage thin (aggregator sites only)
- Notes saved to sources/T3_web_sweep_notes.md

## T4 start
- PUCT Interchange direct access: 402 (blocked)
- DDG search found: SGIA filed 2026-05-08, PUCT docket 35077, item 2482; parties CenterPoint Energy Houston Electric LLC + Bypass BESS II LLC
- Amendment One also filed (same docket)
- Bypass BESS II LLC name CONFIRMED as SPV/LLC
- PDF at interchange.puc.texas.gov/Documents/35077_2482_1639863.PDF → 402 blocked
- Milestone schedule / POI detail not extractable from triage
- ia_found = TRUE

## T5 start
- TX Comptroller Ch.313 search: no direct county-filter tool found on landing page
- DDG search for Ch.313/JETI + "Bypass BESS" + Fort Bend → no results
- abatement_found = FALSE (normal: Ch.313 sunset 2022; JETI for projects after that; 2026 entry unlikely to have applied)

## T6 start
- Site candidate: W.A. Parish 345kV substation, ~29.4627°N 95.6602°W (POI description match, near Richmond TX)
- cdse.py chip: 403 Forbidden on CDSE token endpoint (credentials present in env but rejected)
- Retried once, same result — CDSE auth broken this session
- construction_visible = null (imagery blocked)
- Deep scan: CDSE credentials should be fixed/rotated before imagery step

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28

## Deep scan — Stage 1 (Developer/LLC chain)
- IA Exhibit D confirms: Bypass BESS II LLC, 11801 Domain Blvd Suite 525, Austin TX 78758; email @aypa.com → Aypa Power is developer
- Bank account for EFT: "Aypa Power Development LLC" at Keybank (ABA 041001039, Acct 359681685319) — parent company name confirmed
- Aypa Power is a Blackstone portfolio company (confirmed from public knowledge + triage T3 sources)
- Aypa news page (2026-07-19) does NOT list a Bypass BESS II financing announcement — II is in early/pre-construction stage with no separate PR found
- LLC chain: Bypass BESS II LLC → Aypa Power Development LLC → Aypa Power → Blackstone (partially confirmed; direct Blackstone link not in IA)
- Artifact: sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf (pages 66-67, Exhibit D)

## Deep scan — Stage 2 (PUCT IA / contractual schedule)
- PUCT docket 35077 item 2482 PDF retrieved via curl (2.5 MB, 100 pages)
- IA signed 2026-05-08 by CenterPoint Energy Houston Electric, LLC + Bypass BESS II LLC
- Exhibit B (Time Schedule):
  - NTP and Construction Authorization Date: **June 30, 2026**
  - TIF In-Service Date: **October 1, 2027** (or 12 months after NTP)
  - Scheduled Trial Operation Date: **December 15, 2027**
  - Scheduled Commercial Operation Date: **January 3, 2028** (or 3 months after TIF In-Service)
- Exhibit C (Interconnection Details):
  - POI: BYP Substation, "due South of 2201 Y.U. Jones Rd, Richmond, TX 77469, Fort Bend County"
  - TSP facility: W.A. Parish (WAP) Substation
  - 65× Power Electronics FREEMAQ PF4200 BESS inverters = 205.86 MW at 345 kV
  - Delivery voltage: 345 kV
- Exhibit E (Security): Financial Security = **$100,000** LC; CIAC = $0
- Artifact: sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf

## Deep scan — Stage 2 (Fort Bend CAD)
- esearch.fbcad.org owner-name search for "bypass" and "aypa" — page is JS-rendered, returned blank page; no parcels found
- Expected for pre-construction BESS: generator likely leasing land, LLC may not appear in CAD yet
- CAD: 0 hits under Bypass BESS II LLC or Aypa Power (JS-rendered site; not a conclusive absence)

## Deep scan — Stage 3 (Site pinpoint)
- POI text from IA Exhibit C: BYP Substation "due South of 2201 Y.U. Jones Rd, Richmond, TX 77469"
- OSM Overpass query: "Y U Jones Road" (also tagged "Lockwood Bypass") confirmed at 29.474-29.476°N, -95.641-95.642°W, adjacent to W.A. Parish plant
- W.A. Parish Substation 345kV confirmed at 29.4808°N, -95.6242°W via Overpass
- BYP Substation location estimated: ~29.470°N, -95.642°W (due south of Y.U. Jones Rd junction at Parish)
- Cross-check: triage candidate 29.4627N, 95.6602W (medium confidence) was ~4 km NNW of IA-derived location — IA text supersedes; revised to 29.470°N, -95.642°W
- Method: IA POI address text + OSM road geometry
- Confidence: HIGH (IA text is primary document; road geometry verified via Overpass)

## Deep scan — Stage 4 (Imagery)
- CDSE credentials became invalid (401) after first session — only 2-3 chips obtained before expiry
- Images obtained (all 2km or 1.5km buffer):
  - s2_2026-07-01_byp_site.png: July 2026, some cloud; shows Y.U. Jones Rd + Parish complex + open farmland south of road; no construction activity
  - s2_2026-04-01_byp_site.png: April 2026, clearer; confirms undisturbed farmland south of Y.U. Jones Rd — no BESS pad, no grading
- Verdict: **no_activity** as of April-July 2026 — consistent with IA NTP date June 30, 2026; construction not yet commenced
- Artifact: imagery/key/s2_2026-04-01_byp_site_pre_construction.png, imagery/key/s2_2026-07-01_byp_site_latest.png
