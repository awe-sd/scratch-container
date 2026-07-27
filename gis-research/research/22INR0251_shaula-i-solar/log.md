# Log — Shaula I Solar (22INR0251)

## D0 — setup, 2026-07-21
- Read PLAYBOOK.md, DOSSIER_TEMPLATE.md, Hanson Solar reference dossier.
- Read sources/REFRESH_DIRECTIVE.md (pre-computed leads from prior triage/orchestration pass).
- No prior deep-scan artifacts existed for this INR (sources/ only had the directive, imagery/ empty,
  no findings.json) — starting D0 fresh despite the large run_stream_deep.jsonl (that file is this
  session's own live transcript, not a prior run).
- Checked sibling 22INR0267 Shaula II Solar dir: no findings.json/log.md yet (concurrent agent still
  running) — cannot cross-reference its results; noting the twin-phase attribution risk per directive.
- Wrote findings.json skeleton (all schema keys, nulls).

Identity packet facts (claims to verify):
- Shaula I Solar, 22INR0251, DeWitt County TX, 205.2 MW Solar PV, zone SOUTH.
- SPV lead: Shaula Energy Project, LLC (per directive; unverified).
- POI: tap 345kV 5133 Elm Creek - 5915 SO TEX ckt 1.
- Reported COD (claim): 2026-03-31 — already passed per directive, constructionStart empty.
- ginrStudyPhase: "SS Completed, FIS Started, IA" — FIS never completed despite signed IA (2022-02-16).

## D1 — IA / SPV resolution, 2026-07-21
- `puct.py match 22INR0251 --key "Shaula Energy Project"` → 4 filings in docket 35077, all image-only
  scanned PDFs (0 chars via pdftotext). TSP = **CPS Energy** (not Oncor/ETT as usual — DeWitt Co is
  in CPS's service territory near San Antonio).
  - 35077-1387 (2022-02-18): original IA, "Shaula Energy Project LLC" ↔ CPS Energy — **CONFIRMED ours**
    via exhibit.py scan/render: Exhibit C p32 "Name: Shaula I Solar (the 'Plant')", 205.2 MW AC, 63×
    3.257 MVA PV inverter arrays, POI = "approximately 63 miles east of the CPS Energy-owned Elm Creek
    345 kV Switchyard on the 345 kV Elm Creek to STP transmission circuit 2" — matches queue POI text
    exactly. Renamed CONFIRMED_*_shaula-i-solar-IA.pdf.
  - 35077-1413 (2022-05-05): same but "Shaula Energy Project II, LLC" — this is the SIBLING project's
    (22INR0267) IA, NOT ours. Renamed NOTOURS_*.
  - 35077-1554 (2023-02-13): First Amendment for Shaula Energy Project, LLC (ours) — CONFIRMED via
    Exhibit C repeating "Name: Shaula I Solar". Renamed CONFIRMED_*_shaula-i-solar-IA-amend1.pdf.
  - 35077-1555 (2023-02-13): First Amendment for Shaula Energy Project II, LLC — sibling's, NOTOURS_*.
  - `puct.py search "Shaula"` confirms exactly 4 filings total in docket 35077 — no second amendment,
    no other Shaula filings anywhere in PUCT Interchange.
- **Exhibit C1 (POI one-line diagram)**: generic interconnection-pole schematic, no site geo info —
  not useful for site pinpoint (as expected — it's an electrical detail, not a plot map). No parcel/
  boundary map exists in this IA (CPS Energy's standard IA template has no Attachment-C3-style site
  map, unlike Oncor/ETT templates) — confirmed by reading the full sheet index of both PDFs (10 sheets
  covering all 40 pages of the original + 3 sheets/11 pages of the amendment); no map/plat exhibit
  present anywhere. `site.map_artifacts` will be empty for this project — recorded as a genuine gap,
  not a miss.
- **SCHEDULE DRIFT (decisive, in the IA itself, no queue-history needed)**:
  - Original IA (2022-02): In-Service 2024-02-23, Trial Op 2024-03-07, **COD 2024-06-28**.
  - Amendment 1 (2023-02): In-Service 2024-11-21, Trial Op 2024-11-30, **COD 2025-10-30**.
  - Both dates are BEFORE the queue's claimed reported COD of 2026-03-31 — the queue's projectCod
    (2026-03-31) does not match either contractual schedule found in the signed documents. Either a
    second (unfiled/informal) slip pushed it further, or the queue's self-reported date has drifted
    independently of the IA. No IA amendment exists past 2023-02 (confirmed via puct.py search), so
    2025-10-30 is the last CONTRACTUALLY documented COD — and that date has already passed as of
    today (2026-07-21) with, per the identity packet, constructionStart still empty in the queue.
  - This is strong evidence the project has NOT reached commercial operation on its own contractual
    schedule, let alone the queue's claim.
- Financial security: $17,735,000 total (both tranches) posted per original IA Exhibit D; Amendment 1
  restates the same total ($9,174,000 + $8,561,000) but re-dates both tranches to 2022-02-11 (i.e. the
  amendment revised the IN-SERVICE schedule but security amount was unchanged — no escalation, unusual
  vs Hanson-style amendments where security rises).
- Cleaned up intermediate exhibit.py sheet-tile PNGs (kept sheet_index.md files) to reduce sources/
  bloat; kept the 8 decisive rendered page PNGs (Exhibit B/C/C1/D for both original + amendment).

## D1 continued — SPV/developer resolution, 2026-07-21
- `spv.py resolve 22INR0251` → no systematic candidate (EIA-860M has zero DeWitt Co rows, confirming
  REFRESH_DIRECTIVE's EIA-negative finding independently).
- `ch313.py resolve 22INR0251` (name + county "Cuero"/"DeWitt") → all NEGATIVE. The local
  ch313_agreements.json bulk file (740 rows fetched 2026-07-20) has NO row with district containing
  "witt" or "cuero" at all — i.e. the bulk snapshot itself is missing this agreement, not just a
  name-match miss. Confirmed by direct grep of data/reference/ch313_agreements.json rows.
- `ch312.py resolve` → negative (weak, expected — CAD-submitted annual gaps).
- `tceq.py resolve 22INR0251 --county DeWitt --keyword Shaula --storm` → **STRONG POSITIVE**, contradicts
  REFRESH_DIRECTIVE's "TCEQ negative" note (that was a plain resolve without --storm/--keyword). 3 active
  facilities: "CPS ENERGY SHAULA 345KV SWITCHYARD", "SHAULA ENERGY PROJECT", "SHAULA I AND II POI AND
  ACCESS ROAD PROJECT" — all ACTIVE. 3 construction-stormwater NOIs: TXR1529MC, TXR1541SY, TXR1565NR.
  Owner/customer legal names on these permits: **BP Alternative Energy North America Inc.**,
  **E-Z BEL CONSTRUCTION, LLC** (likely civil/road contractor), **Shaula Energy Project, LLC**.
  This is decisive: BP entity name ties directly to a real corporate parent, and the "POI AND ACCESS
  ROAD PROJECT" facility name confirms physical interconnection/access-road construction activity
  under TCEQ jurisdiction (i.e., dirt-moving-adjacent activity, though NOI existing ≠ construction
  complete — it's a permit, log accordingly).
- `search.py "Shaula Solar BP DeWitt County Texas"` → hit: conservativetexansforenergyinnovation.org
  article. **DECISIVE**: developer = **Lightsource bp** (UK joint venture, BP owns 50%), projects
  wholly owned by **BP Solar Holdings**. THREE separate LLCs confirmed: Shaula Energy Project (I),
  Shaula Energy Project II, Shaula Energy Project III — I is in Cuero ISD, II in Yoakum ISD (III also
  Cuero ISD per article, though our own docket search only surfaced I/II filings — III's INR is
  reportedly 23INR0009 per a search snippet, not this run's concern).
  Each project: 200 MW nominal (matches 205.2 MW nameplate AC), 530,000+ panels, $180M investment,
  300 construction jobs. Article's own COD table: Shaula I "Summer 2024", Shaula II "Dec 2024",
  Shaula III "June 2025" — Shaula I's article-stated COD (mid-2024) matches the ORIGINAL IA schedule
  (2024-06-28) almost exactly, NOT the Amendment-1 schedule (2025-10-30) and NOT the queue's claimed
  2026-03-31. Construction target start "early 2023" per article.
  Article also states Ch.313 caps: Shaula I capped at $20M taxable value/10yr — meaning a Ch.313
  AGREEMENT DOES EXIST for Shaula I despite our own bulk ch313_agreements.json missing it.
- `search.py "Cuero ISD Shaula solar tax abatement"` → found the actual Comptroller page:
  **comptroller.texas.gov/economy/local/ch313/agreement-docs-details.php?id=1714** — "Cuero ISD
  No. 1714, Shaula Energy Project, LLC" — this is the Ch.313 agreement our bulk snapshot missed
  (stale/incomplete fetch, not absence). Also found dewittcountytoday.com "Cuero ISD enrollment
  totals growing, Board approves solar reinvestment zones" (Shaula reinvestment zones). Two
  dewittcountytoday.com article URLs from the first search round 404'd on direct fetch (site may
  gate/paginate) — will retry via search snippets or cache.
  NEXT: fetch comptroller id=1714 page + linked PDFs (App/Agreement) for site/acreage/schedule data;
  fetch the ISD reinvestment-zone article.

## D1 continued — Ch.313 application recovered via Wayback, 2026-07-21
- Live comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id=1714
  returns "There is no record found" — CONFIRMED via direct curl (this record has been REMOVED/purged
  from the live site, same pattern as 22INR0455 Blue Sky Sol's Crockett CCCSD record). Our local bulk
  ch313_agreements.json (740 rows, fetched 2026-07-20) also lacks id 1713-1715 entirely — the purge
  predates our snapshot.
- Wayback CDX search (`web.archive.org/cdx/search/cdx?url=assets.comptroller.texas.gov/ch313/1714/*`)
  found 4 archived PDFs from 2024-06-20: agmt (2.5MB), app (6.2MB), appsupp1 (1.7MB), cert (2.1MB).
  Downloaded agmt+app+cert (all HTTP 200 via web.archive.org/web/<ts>/<url> passthrough; direct
  assets.comptroller.texas.gov fetch 403s — must go through the wayback proxy URL, not the raw asset
  URL, even for a "closest snapshot" lookup).
- **Ch.313 App (id=1714) Tab 4, p17 — CONFIRMED, DECISIVE**: "Shaula Energy Project, LLC is a 200 MW/AC
  solar electric generation facility that will be located in eastern DeWitt County in eastern Cuero
  Independent School District. The facility will feature 530,000 photovoltaic panels and 63 central
  inverters. Shaula Energy Project, LLC is wholly owned by BP Solar Holding, LLC and is being developed
  by Lightsource BP under a development services agreement." This directly confirms the news-article
  ownership chain from a primary regulatory filing, independent of the PR/news source.
  Artifact: sources/2026-07-21_wayback_ch313-1714-cuero-shaula-app_p17.png
- **SITE MAP — decisive, `site.map_artifacts`**: p25 of the App PDF is an Esri-basemap aerial map
  titled "Shaula Energy Project, LLC" showing a distinctive Z/lightning-bolt-shaped "Project Boundary"
  (red outline) + "Proposed Reinvestment Zone" (hatched) polygon, ~1.4-mile scale bar, north arrow.
  Terrain: mixed scrub/woodland with cleared agricultural patches, NOT open farmland — matches DeWitt
  County's post-oak savannah character (differs from the flat cropland typical of West Texas solar
  sites in other dossiers). This is THE site-derivation artifact for D2 — will match this exact
  polygon shape against a wide-area imagery search since no lat/lon or address is stated on the map
  itself. Artifact: sources/2026-07-21_wayback_ch313-1714-cuero-shaula-app_p25.png (4.5MB, saved).
  Other p26-28 map pages are duplicate compass/legend views of the same-shaped polygon at different
  zoom/crop — not saved as separate artifacts (redundant with p25, keeping ≤6-full-read budget for D2).
- **Exhibit A legal description (agmt p78)**: 17 parcels, 5 owner families (Barnes Jeremy; Berkman
  Linda A etal; CS Holdings Ltd; JMM Ranches Ltd; McMahan Jeff & Denise), sum = **2,767.11 acres**.
  NOTE: this is the full reinvestment-zone parcel extent per Ch.313 Exhibit A (whole parcels the
  owners hold within the zone), not necessarily the exact fenced project footprint (leased portion
  is typically smaller) — recorded as project_area with that caveat.
  Vicinity map (agmt p79) shows the reinvestment zone as a small irregular polygon east of Cuero,
  along the Hwy 766/Wolf Hollow corridor toward Yoakum, inside DeWitt County — NOT overlapping
  Gonzales county despite the map's wide DeWitt-boundary diamond shape.
- **TCEQ raw Socrata query (bypassing tceq.py's summary, direct API call) — DECISIVE SITE ADDRESS**:
  `data.texas.gov/resource/tzyg-j7q4.json` filtered county=DEWITT + program=STORM + name~SHAULA
  returns 3 rows with full physical-location fields:
  1. "CPS ENERGY SHAULA 345KV SWITCHYARD" — desc "1.43 mi SE of intersection of Wolf Hollow Rd CR110
     & Friar Rd CR100, west side of Wolf Hollow Rd"; contractor E-Z BEL CONSTRUCTION LLC; NOI
     TXR1565NR, began 2023-07-24, **now CANCELLED**.
  2. "SHAULA I AND II POI AND ACCESS ROAD PROJECT" — desc "10 miles west of Cuero, TX near Wolf
     Hollow Rd"; owner BP Alternative Energy North America Inc.; NOI TXR1529MC, began 2023-03-13,
     **now CANCELLED**.
  3. **"SHAULA ENERGY PROJECT"** — full street address **880 Wolf Hollow Rd, Cuero, TX 77954**;
     owner/SPV Shaula Energy Project, LLC (exact IA party name match); industry code 221114 SOLAR
     ELECTRIC POWER GENERATION; NOI TXR1541SY, began **2024-12-06**, **now CANCELLED**.
  All 3 NOIs are CANCELLED (not just inactive) — a stormwater NOI is cancelled either because
  construction finished (site stabilized, permit closed out normally) OR because the project was
  abandoned before/without breaking ground. Cannot distinguish from this record alone — imagery is
  needed to resolve which. The 2024-12-06 start (Shaula Energy Project's own NOI) postdates BOTH IA
  schedules (June 2024 / Oct 2025 COD) — if that date is a genuine construction start, it's LATE
  relative to the original schedule but could still support the Amendment-1 Oct-2025 COD; if it's
  actually already cancelled with no follow-on activity, that points toward stalled/abandoned.
  Geocoded 880 Wolf Hollow Rd via `gmaps.py places` → **29.084248, -97.105140** (street_address type,
  high-confidence geocode). Site method recorded: TCEQ NOI physical address (site.method).
- Wolf Hollow Rd (OSM) spans lat 29.019-29.094, confirming the address sits within the named road's
  extent, consistent with "10 miles west of Cuero" (Cuero is ~29.10, -97.29 — wait, checking: Cuero's
  actual coords are ~29.0938, -97.2900; 880 Wolf Hollow Rd at -97.1051 is ~11 mi EAST of Cuero center,
  not west — the NOI desc text may have the cardinal direction backwards, a known type of scrivener
  error in these filings; geocoded coordinate is the more reliable source). Also consistent with
  "eastern DeWitt County, eastern Cuero ISD" per the Ch.313 application Tab 4 text.
- D1 CLOSED. Moving to D2 site+imagery: cross-check 29.084248,-97.105140 against the Ch313 boundary
  map polygon shape via satellite imagery before finalizing site confidence.

## D2 — site+imagery, RESUMED 2026-07-21 (correcting prior interrupted run)
- Prior deep-scan attempt (run_meta_deep.json) hit error_max_turns (121 turns) with audit
  violations: 16 image reads (>6 cap), dossier.md missing. Its findings.json construction
  section claimed "imagery grid + xwide/xxwide chips (2.5/6/10km)" and an "8-date history
  2022-01 to 2026-01" as evidence for a no_activity verdict, but only ONE file
  (imagery/s2_2026-07-15_search.png) exists on disk. run_stream_deep.jsonl is THIS session's
  own transcript (confirmed by reading it), not the prior run's — the prior run's actual
  image reads are not recoverable. Treating the no_activity verdict as UNSUBSTANTIATED and
  redoing D2 from scratch rather than trusting it.
- Reviewed the one surviving chip (s2_2026-07-15_search.png, no lat/lon in filename/log —
  cannot confirm what coordinate it was centered on): ordinary mixed farmland/scrub, small
  cleared rectangular patches, farm buildings, no solar racking signature visible. Consistent
  with no_activity AT WHATEVER LOCATION IT SHOWS, but not tied to a confirmed site coordinate.
- s2aws.py chip at 29.084248,-97.105140 (geocoded 880 Wolf Hollow Rd), 3km buffer, 2026-07-20
  scene 2026-07-19: ordinary farmland, small buildings, NO match to the Ch313 boundary map's
  distinctive Z/lightning-bolt polygon shape (sources/..._app_p25.png) — no red-outline-shaped
  graded/cleared area, no racking rows.
- Built 3x3 grid (2.5km chips, 0.02deg lat / 0.03deg lon steps) around the same address,
  contact sheet imagery/grid_contact_sheet.png: none of the 9 tiles show the distinctive
  Z-shape polygon or any large-scale grading/racking signature. The TCEQ NOI street address
  may be a site OFFICE/GATE address, not centered on the actual generation footprint (per
  playbook: "the pin is usually the site gate, not the array centroid" — but even allowing
  for a 5km miss, the terrain type (post-oak savannah scrub/woodland with irregular clearings)
  seen in the grid IS consistent with the Ch313 map's terrain character, unlike a mismatch.
  DOWNGRADING site.confidence from med to low: address geocode alone is not sufficient without
  a shape-match; need the actual project boundary polygon (CAD parcel GIS or a wider grid).
- NEXT: try DeWitt CAD GIS parcel viewer with cad_id list (17840, 2917, 2916, 16418, 14411,
  2319, 17839, 17838, 19847, 2922, 17841, 14410, 2320, 5217, 17849, 17837, 19845) to get an
  authoritative parcel geometry fix instead of shape-matching by eye.

## D2 continued — CAD parcel geometry attempt, 2026-07-21
- dewittcad.com is a private paid lookup mirror (not official). Official CAD site
  www.dewittcad.org is ASP.NET SPA, no working REST/GIS endpoint found by guessing paths
  (/Property/View/<id>, /gis, /map all 404). TaxNetUSA interactive GIS map requires Pro
  membership for parcel-ID deep links (confirmed via WebFetch of taxnetusa.com/texas/dewitt).
  Regrid app.regrid.com requires interactive search, no anonymous parcel-ID URL works via
  WebFetch. NEGATIVE: no free authoritative parcel-geometry API found for DeWitt CAD IDs
  17840/2917/2916/16418/14411/2319/17839/17838/19847/2922/17841/14410/2320/5217/17849/
  17837/19845 within reasonable effort — abandoning this path, relying on imagery
  shape-match + OSM road geocoding instead.
- Nominatim geocode of "Wolf Hollow Road, DeWitt County, Texas": bounding box lat
  29.0192-29.0943, lon -97.1135 to -97.0939 — confirms 880 Wolf Hollow Rd (29.084248,
  -97.105140) sits right at the NW end of the named road extent, consistent placement.
  FM 766 (named in the Ch313 vicinity map corridor) is centered ~29.12-29.15, -97.30 near
  Cuero/Gonzales border — i.e. ~18km WEST of the Wolf Hollow address. The Ch313 vicinity
  map (agmt p79) shows the black reinvestment-zone polygon east of Cuero near the DeWitt/
  Cuero-ISD boundary, roughly 10-15mi ENE of Cuero town center — broadly consistent with
  the Wolf Hollow Rd address (Cuero center ~29.0938,-97.2900; Wolf Hollow site is ~17km
  ENE of that) even though FM766 itself runs well to the west. Treating the vicinity map
  as ROUGH placement confirmation (right quadrant of the county) not a precise fix.
- gmaps.py places on parcel owner names (JMM Ranches, CS Holdings) returned NO relevant
  hits in DeWitt County (unrelated national entities of the same name) — negative evidence,
  logged.
- gmaps.py places "Shaula Solar"/"Shaula Solar Cuero" — NO RESULTS. "Shaula Energy Project"
  → returned an unrelated "Peacock Solar Plant" in Taft TX (different county, not a match) —
  NO usable construction-site Google pin exists for this project. Negative evidence.
- 6km xwide chip at the geocoded address (2026-07-19 scene): reviewed — ordinary mixed
  scrub/farmland with scattered small clearings and ONE rectangular striped/hatched
  agricultural field (~pecan orchard or row-crop, not solar racking pattern — rows are
  too widely spaced and terrain-following, unlike uniform module blocks) in the SW quadrant
  of the frame. NO large graded polygon, NO Z-shaped clearing matching the Ch313 map, no
  substation-scale bright squares. Verdict at this candidate coordinate: no solar
  construction signature visible within 6km as of 2026-07-19.
- CONCLUSION for D2: site coordinate confidence remains LOW — TCEQ NOI street address
  is the best available fix (exact address, SPV-name-matched permit) but imagery does not
  show a shape-match to the Ch313 boundary map at that location or in a surrounding 3x3
  grid. Two explanations consistent with evidence: (a) address is right but project never
  broke ground (NOIs cancelled without construction, matches "abandoned" reading), or
  (b) address is a site office/mailing point offset from the actual Z-shaped parcel by
  several km. Recording site.confidence=low with both hypotheses; imagery supports
  NO ACTIVITY at the TCEQ address regardless of which hypothesis is true.

## D3/D4 — deterministic wrap-up + synthesis, 2026-07-21
- `queue_history.py 22INR0251`: 80 monthly snapshots (2019-11 -> 2026-06). DECISIVE gaps:
  FIS approved = NEVER (despite IA signed 2022-02-16 -- unusual sequencing, IA executed
  before FIS approval, but meetsSection691 achieved 2023-03-27); meetsAll6.9 = NEVER;
  constructionStart (reported) = NEVER; constructionEnd = NEVER. 6 reported-COD changes
  spanning 2022-01-31 up through the current 2026-03-31 -- a slip almost every year since
  2019, with the current claimed COD already 4 months in the past as of today (2026-07-21)
  and construction still not reported started in the queue's own milestone data. This is
  independent (queue-side) corroboration of the IA-schedule drift found in D1 and the
  no_activity imagery finding in D2 -- three independent signals now agree.
- `eia_history.py 22INR0251 --write`: NOT in EIA-860M TX slice at all. Negative evidence,
  consistent with spv.py's earlier finding and with a project that has not begun
  construction (EIA-860M generally picks up projects once under construction/near-term).
- SYNTHESIS: real_project_verdict = real_early. This is NOT a paper project -- it has a
  fully identified, credible corporate chain (Shaula Energy Project LLC -> wholly owned by
  BP Solar Holding LLC -> developed by Lightsource bp, a major utility-scale developer with
  5.4GW+ portfolio per its own Ch313 filing), a signed+amended IA with real financial
  security posted ($17.735M), a Ch.313 tax abatement agreement with Cuero ISD, and TCEQ
  permits filed under the SPV's own name at a specific address. But it is EARLY / STALLED:
  zero imagery evidence of ground-disturbance at the best-available site coordinate, all
  3 TCEQ stormwater NOIs cancelled without a visible construction signature, FIS never
  approved after 4+ years, construction start never reported in the queue's own milestone
  tracking, not in EIA-860M, and the contractual COD schedule has already slipped twice
  past its own IA amendment (Oct-2025) plus the queue's current claim (Mar-2026) with no
  third amendment on file. The sibling Shaula II project (22INR0267) shows an identical
  pattern per its own IA amendment (found during D1), suggesting a portfolio-wide slip/pause
  by the developer across all three Shaula-named projects, not an idiosyncratic single-
  project issue.
- Independent COD: given FIS still not approved, no construction, no EIA-860M presence,
  and the developer/BP corporate chain intact (financial capacity is not in question), the
  project is credible but has an extended runway ahead: at minimum FIS approval -> meets-all-
  6.9 -> construction start -> ~18-24mo build for a 205MW/2,767-acre solar site. Given zero
  visible groundwork today (2026-07-21), the earliest plausible independent COD is
  approximately 2028, with meaningful risk it slips further or is cancelled outright (as
  its own NOI cancellations without construction suggest is already underway). Recording
  independent COD as "~2028 or later (low confidence)" and drift_risk "high".

## D5 — wrap-up, 2026-07-21
- `queue_history.py 22INR0251` -> timeline.json/timeline.md (80 snapshots, 6 COD changes).
- `eia_history.py 22INR0251 --write` -> NOT in EIA-860M TX slice (negative evidence).
- `build_brief.py 22INR0251` -> brief.html (9KB, 1 image, 28 sources).
- `build_index.py` -> research/index.json + INDEX.md refreshed (173 projects).
- dossier.md written per DOSSIER_TEMPLATE.md. findings.json final pass complete, all schema
  keys populated (nulls only where genuinely unknown: land_tenure.status). Run closed.
