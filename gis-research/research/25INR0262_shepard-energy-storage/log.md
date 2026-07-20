# Triage log — Shepard Energy Storage (25INR0262)

## T1 start
queue_history.py: 43 snapshots (2022-12-01 → 2026-06-01), 5 COD changes.
- IA signed: 2024-01-17 (strong signal — contracted)
- FIS approved: 2026-03-19 (recent)
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: NOT achieved
- Construction start/end: NOT reported
- COD drift: 2025-07-09 → 2027-07-01 (~2 yr slip in 3 years)
- Capacity drift: 263.2 → 256.79 MW (minor trim, not unusual)
- Current COD 2027-07-01 — held since 2025-03-01 (stable for 16 months)

## T2 start
gmaps.py: HTTP 429 on first call, 429 on retry — rate-limited. No pins found (budget exhausted).
pins_found: 0

## T3 start
DDG search 1: Project has a website, "directly next to an electrical substation," <15 acres, one tracker rates build probability 92%. Developer confirmed as Vesper Energy (1722 Routh St Suite 900, Dallas TX 75201; also 125 E John Carpenter Fwy Suite 525, Irving TX 75062). Multiple Vesper sister LLCs at same Irving address (Aldrin Energy Storage, Swanson Energy Storage — naming pattern: Shepard/Aldrin/Swanson = astronaut names).
DDG search 2: LLC formed 2022-11-10 as Delaware foreign entity, TX SOS file 0804803481, "In Existence."
news_found: true (project website exists; no press releases or formal news)
developer: Vesper Energy Development LLC

## T4 start
interchange.puc.texas.gov: HTTP 402 on all endpoints (FilingParty=Shepard+Energy+Storage, FilingParty=Vesper+Energy, root). Portal requires session auth — blocked after 1 retry. IA known to exist (queue shows iaSigned=2024-01-17) but PDF not retrieved.
ia_found: false (exists per queue but PDF unavailable)

## T5 start
TX Comptroller Ch.313 page: no searchable database accessible via WebFetch; CAPTCHA block on abatement DDG query.
Post-2022 battery projects rarely have Ch.313 (program sunset 2023); no JETI result found.
abatement_found: false (normal for post-2022 BESS)

## T6 start
Site candidate identified via Nominatim: Hidden Lakes neighborhood, League City, Galveston County — 29.500°N, -95.028°W (residential area matching POI description "Hidden Lakes" substation adjacent). Method: OSM geocode of POI name fragment.
cdse.py chip: HTTP 403 on CDSE auth token endpoint — credentials not configured in this environment.
construction_visible: false (imagery blocked)

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~28. STOP.

---

## Deep scan — 2026-07-19

### D1 — Developer chain
Vesper Energy confirmed as developer via shepardenergystorage.com (©2025 Vesper Energy, 1722 Routh St Suite 900, Dallas TX 75201; contact 409-761-1765). 
- Founded 2015 as Lendlease Energy Development → acquired by Magnetar Capital 2020, rebranded as Vesper Energy → GCM Grosvenor joined as equity owner 2023.
- TX SOS file 0804803481 (Shepard Energy Storage LLC) confirmed from triage; SOSDirect requires paid account, not accessible.
- Vesper portfolio: 49+ projects, 11,000+ MW pipeline; Texas BESS projects NOT listed on vesperenergy.com/projects (only Hornet Solar TX is featured, plus PA/VA projects).
- Phone area code 409 = SE Texas (Galveston/Beaumont region) confirms geographic affiliation.
source: sources/2026-07-19_shepardenergystorage.com_homepage.html (14 KB, retrieved 2026-07-19)
source: sources/2026-07-19_shepardenergystorage.com_faqs.html (21 KB, retrieved 2026-07-19)
source: vesperenergy.com/about — Magnetar Capital + GCM Grosvenor ownership chain confirmed

### D2 — Project website facts
Project website states: "proposed 250-megawatt BESS in Galveston County, Texas, on less than 15 acres of privately owned land, directly next to an electrical substation and major electrical corridor."
- Expected operational "by end of 2025" (outdated on the page — queue shows current COD 2027-07-01).
- Substation has "existing capacity available without requiring additional grid upgrades" (from FAQ).
- ~50 construction jobs, ~2 long-term maintenance jobs.
- No specific site address, no substation name disclosed on website.
source: sources/2026-07-19_shepardenergystorage.com_faqs.html

### D3 — PUCT Interchange
HTTP 402 on all PUCT interchange endpoints. IA known to exist (queue iaSigned=2024-01-17). PDF not retrievable without session auth. Negative evidence logged.

### D4 — CAD / county records
Galveston CAD (esearch.galvestoncad.org) accessible but owner-search endpoint returns 404. No parcel records retrieved for "Shepard Energy" or "Vesper Energy."
TCEQ Central Registry: search page loaded but no facility records for Vesper Energy / Shepard Energy in Galveston County. Battery storage does not require NSR air permit — absence expected.
No Ch.312/313/JETI abatements found (program sunset 2023, BESS ineligible).
Galveston County commissioners court website: domain inaccessible (403/DNS errors).

### D5 — Site pinpoint attempt
OSM Overpass: "Hidden Lakes" not found as named substation in OSM across full TX bounding box. P.H. Robinson Switching Station confirmed at 29.4878, -94.9826 (CenterPoint Energy).
No POI named "Hidden Lakes Substation" found in any public database.
Nominatim: 0 results for "Hidden Lakes substation League City Texas."
POI descriptor "#38900 Hidden Lakes - #42015 PHR 138 KV" = ERCOT bus numbers; bus 38900 is the Hidden Lakes 138kV bus, bus 42015 is the P.H. Robinson bus. ERCOT CEII — exact coordinates not in public data.
Project website confirms: site is <15 acres directly adjacent to an electrical substation. Hidden Lakes subdivision near League City is the candidate area.
Revised candidate: 29.512, -95.010 (Hidden Lakes subdivision center). PHR is 4.5 km SE at 29.488, -94.983. A 138kV line corridor connecting them is consistent with the geographic setup.
gmaps.py: rate-limited (429) on all attempts.

### D6 — Satellite imagery
Wide frame (6km, 2026-07-01 ±15d): heavy cloud cover over League City — not useful.
Wide frame (6km, 2026-03-01): clear — shows dense suburban League City. Curved cul-de-sacs of Hidden Lakes visible in center. No BESS pad/gravel visible in the 6km frame.
Tight chip (2km, 29.494/-95.003): shows semi-rural fringe south of Hidden Lakes. Some earthwork/brownfield in lower-left but not near any substation. No BESS activity.
Tight chip (2km, 29.490/-94.985): shows PHR vicinity area (transmission corridor, south of residential). Diagonal highway. No BESS pad visible.
Tight chip (2km, 29.510/-95.005): shows east edge of Hidden Lakes near Galveston Bay (TX-96). No substation or BESS pad visible.
CONCLUSION: No BESS construction activity detected in any imagery within reasonable range of Hidden Lakes. Given the site is <15 acres (compact BESS), it could be tucked adjacent to a substation not yet visible or it is truly pre-groundbreak.
Imagery verdict: no_activity / pre-construction.

### D7 — Construction permits / news
No construction permits found in Galveston County system (inaccessible). No press releases or news about Shepard Energy Storage from Vesper, Magnetar, or GCM Grosvenor. No groundbreaking announcements. DuckDuckGo/Bing search blocked by CAPTCHA/irrelevant results.
Project website timeline "expected operational end of 2025" is outdated — consistent with the COD having slipped to 2027-07-01.
Negative evidence: no construction start date in queue (as of 2026-06-01 snapshot).

### D8 — Synopsis
- REAL project: Vesper Energy (Magnetar/GCM backed), IA signed 2024-01-17, FIS approved 2026-03-19, financial security posted ("Yes" in queue), project website live, <15 acres BESS adjacent to CenterPoint Hidden Lakes substation.
- NOT yet under construction as of 2026-06-01 queue snapshot. No imagery evidence of construction through 2026-03.
- COD 2027-07-01: 12 months away. 12-18 month BESS build; needs groundbreak immediately to hit this date. 
- Prior drift history (2025-07 → 2027-07 = 2yr slip total) raises medium risk. But milestones cleared: IA+FIS+financial security all done.
- Independent estimate: 2027-Q3 to 2028-Q1 depending on groundbreak date. 2027-07-01 is achievable but tight.
