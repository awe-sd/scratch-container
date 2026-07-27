# Triage log — Chisme Solar (24INR0333)

## T1 start
queue_history.py ran: 42 snapshots, 3 COD changes (not counting current).
COD drift: 2025-07-01 → 2026-02-20 → 2026-10-07 → 2027-04-13 (current). Three slips, ~21 months total drift from first COD.
Milestones: Screening complete 2023-04-14, FIS approved 2026-06-23, Meets 6.9(1) 2025-09-16.
IA NOT signed. No construction dates reported. Capacity settled at 147.0 MW since 2023-11.

## T2 start
gmaps.py: 429 Too Many Requests on first attempt + retry. No pins obtained. 0 pins found — normal.

## T3 start
Developer confirmed: Blue Heron Solar, LLC (not "Chisme Solar LLC"). Project full name: Chisme Solar & Storage (incl. ~146 MW BESS). Straddles Brown + Mills County. PUCT control #35077 found — IA filing with Oncor. Low build-chance (5%) noted on one tracker. gem.wiki 403. Sources saved to sources/t3_web_sweep.md.

## T4 start
PUCT Interchange portal: 402 on controlNumber=35077 and FilingParty=Blue+Heron+Solar. Portal blocked — cannot retrieve IA PDF. PUCT #35077 exists per T3 web search (IA with Oncor confirmed from secondary sources). No PDF downloaded. IA found=TRUE (via secondary source reference), content not retrieved.

## T5 start
Ch.313: portal not directly searchable by county; Ch.313 expired for new apps Dec 2022 — project entered queue Jan 2023, so no Ch.313 expected. JETI registry not publicly searchable (no direct search tool). No abatement found — normal for post-2022 project.

## T6 start
Site search: DDG 403, Bing returned no results for Chisme Solar location. No pin from T2 (gmaps 429). No IA PDF (PUCT 402). No precise coordinates for Brown Switch/Buckhorn Switch substations found. Best candidate is "somewhere in Brown/Mills County" — does not meet threshold for imagery. SKIP imagery per rules: no site candidate.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. Run complete.

# DEEP SCAN — 2026-07-20

## D1 start
puct.py match 24INR0333: rung-0 INR-join hit, CONFIRMED (INR found in doc text). Filing
35077-2003, 12/4/2024, Standard Generation Interconnection Agreement between Oncor Electric
Delivery Company LLC and Blue Heron Solar, LLC (Chisme). Saved:
sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf
(51 pages). This is the signed IA — triage's PUCT-portal-blocked note is now resolved.

## D1 — Exhibit B/C read (sheet08, pp26-29)
DECISIVE: signed IA Exhibit "B" Time Schedule (pp26-27):
- Notice-to-proceed date: Dec 6, 2024
- In-Service Date: **Dec 3, 2026**
- Scheduled Trial Operation Date: Dec 13, 2026
- Scheduled Commercial Operation Date: **April 13, 2027** — EXACT MATCH to queue-claimed COD
  (2027-04-13). Contradicts triage's "not plausible" call — reported COD is not a stale/
  optimistic queue self-report, it's the literal contractual date in a signed (Dec 2024),
  PUCT-filed IA. Queue milestone `iaSigned` shows null/— but the IA plainly exists and is
  signed — the queue milestone column is stale, not the underlying fact.
Exhibit "C" Interconnection Details (pp27-29):
- Name: Blue Heron Solar, LLC (confirms triage SPV find, now CONFIRMED not just secondary-
  sourced)
- POI: "proposed Gobbers Knob Switch" on TSP's 345kV Brown Switch–Buckhorn Switch line —
  matches queue POI text exactly ("Tap 345 kV 1444 BROWN SWITCH - 3424 BUCKHORN SWITCH")
- Delivery voltage 345 kV
- Generating units: Chisme Solar 24INR0333 = 39x Sungrow SG4400-UD inverters, 148.941 MW
  gross / 147 MW measured at 34.5kV collector (matches queue capacity exactly)
- Companion project: "Chisme Storage" 24INR0331 = 68x12 Sungrow SC210HX-US storage
  inverters, 147.56 MW gross / 146 MW measured — SEPARATE INR confirmed (answers triage's
  open question about the BESS component: it is filed as its own INR, not folded into
  24INR0333, and shares this same IA/POI).
Exact POI coordinates redacted (blacked out) in Exhibit C text — "(See attached one-line
diagram)" — need to check later exhibit pages for a site/route drawing.

## D1 — Exhibit D/E read (sheet13, pp46-48)
Exhibit "D" Notice/EFT info (p46) confirms ownership chain:
- Generator legal name: Blue Heron Solar, LLC
- Notice address: "Attn: Manager, Red River Clean Energy / 11801 Domain Blvd, 3rd Floor,
  Austin, TX 78758"; billing "Attn: Accounting, Red River Clean Energy / 107 Spring Street,
  Seattle, WA 98104"; emails mluo@redrivercleanenergy.com,
  accounting@concordnewenergy.com — ties Blue Heron Solar LLC to developer "Red River Clean
  Energy" AND to "Concord New Energy" (accounting domain) — matches EIA-860M entity name
  "Red River Clean Energy" from factsheet.json exactly. Two names in one filing (Red River
  Clean Energy address/email + Concord New Energy accounting email) suggests Red River
  Clean Energy is Concord New Energy's US development platform/subsidiary — needs a web
  check but is a strong, document-sourced lead, not speculation.
- EFT: Generator bank = Bank of America, Seattle WA; account holder "Red River Clean
  Energy, LLC" — confirms Red River Clean Energy as the operating parent (not just a
  mailing contact).
Exhibit "E" Security Arrangement Details (p47-48): Irrevocable Standby Letter of Credit,
effective on/before **Dec 6, 2024** = **$15,842,206**. Single tranche listed (no
amendments/escalation schedule visible in this original IA — this is a first/only IA, no
amendment on file per puct.py match single-result).

## D2 start — site pinpoint
gmaps.py places "Gobbers Knob Switch" and "Chisme Solar": both 429 Too Many Requests
(same failure as triage T2) — tool remains rate-limited, could not retry further without
burning turns.
search.py "Gobbers Knob Switch Brown County Texas": top hit = hometownlocator.com
"Gobblers Knob" — a named summit/physical feature in MILLS County (not Brown), FID
1358108, coordinates lat 31.5640442, lon -98.8192066 (near Zephyr, TX; Mullin-Priddy CCD).
CROSS-CHECK: this is within ~0.6 km of the independent EIA-860M plant coordinate candidate
(31.56893, -98.82195, factsheet.json plant 68078). The IA's proposed "Gobbers Knob Switch"
name is evidently derived from this real, pre-existing terrain feature — two independent
sources (EIA-860M plant registration + USGS/hometownlocator named-feature gazetteer)
converge on the same ~0.6 km patch of ground. This resolves the Brown/Mills county-line
ambiguity: the POI switch site sits right at the Brown/Mills line, consistent with queue
county=Brown and triage's "straddles Brown+Mills" finding.
SITE CANDIDATE: 31.5689, -98.8220 (EIA-860M, prioritized as it's the plant coordinate not
a terrain-name proxy) — corroborated by Gobblers Knob named feature 0.6 km away. Method:
poi_name_cross_reference + eia860m_plant_coords. Confidence: medium (no parcel/imagery
confirmation yet — proceeding to satellite check).

## D2 — imagery BLOCKED: CDSE account out of processing credits
cdse.py chip repeatedly failed with `RemoteDisconnected` (5 retries over ~2.5 min, various
backoff). Root-caused by hand: direct curl POST to openeo.dataspace.copernicus.eu/openeo/1.2/result
with the same cached bearer token returns **HTTP 402 Payment Required** — "You do not have
sufficient credits to perform this request" (marketplace-portal.dataspace.copernicus.eu/
pages/pricing). Token itself is valid (not expired, decodes fine). This is an account-level
quota exhaustion, not a per-request auth/rate-limit issue like the known 403 rate-limiting
bug — cdse.py's urllib error handling apparently doesn't surface the 402 body cleanly under
`uv run` (shows as RemoteDisconnected instead), but the raw HTTP response is unambiguous.
IMPACT: no Sentinel-2 imagery obtainable this run. Cannot verify construction stage visually
for this project. Flagging for the operator — same shared CDSE credential is used
fleet-wide, so this likely blocks EVERY concurrent deep-scan needing imagery right now, not
just this project. Proceeding with non-satellite site verification (POI cross-reference
already done above) and noting construction stage as unconfirmed/not obtainable in
findings.json rather than guessing.
gmaps.py staticmap also failed: HTTP 403 "Maps Static API is not activated on your API
project" — a distinct, separate infra gap (API not enabled, not credits/rate-limit). Both
of the playbook's two imagery/mapping tool paths (cdse.py, gmaps.py) are unavailable this
run for different reasons (CDSE=credits, gmaps=API not enabled + earlier 429s). No
satellite or static-map imagery obtained for this project — logging as infrastructure
failure, not as "no_activity" site finding.

## D3 — registry sweep
spv.py resolve 24INR0333: confirms same two candidates already verified via IA (EIA-860m
Red River Clean Energy, puct-index Blue Heron Solar) — no new leads, both already CONFIRMED
via document read, not just resolver output.
ch313.py resolve 24INR0333 / --name "Blue Heron" / --name "Red River Clean" / --county Brown:
ALL NEGATIVE — no Ch.313 agreement or JETI application for Chisme Solar, Blue Heron Solar,
or Red River Clean Energy under any name variant. Expected: IA executed Dec 2024, well
after Ch.313 sunset (Dec 2022) and this JETI dataset (38 rows, likely incomplete coverage)
has no hit either. Consistent with triage's earlier "no abatement expected" call.
ch313.py resolve --county Mills: 1 unrelated hit "Markum Solar Farm, LLC" (Valley Mills ISD,
applied 2021) — different project, different applicant name, no INR/name overlap with
Chisme. Logged as checked-and-ruled-out, not a Chisme lead.

## D3 — Mills County government docs (primary source, NOT a banned aggregator)
search.py "Blue Heron Solar LLC Chisme Brown County Texas" surfaced millscountytx.gov
(official county government site) hosting a Chisme fact sheet + a "Red River Abatement
Application" PDF dated 2025-10-27. First download attempt (page/9267 path from search
snippet) 404'd — page IDs had moved. Re-searched "millscountytx.gov Red River Abatement
Chisme" and found the SAME docs under page/0102: both downloaded successfully as valid
PDFs (verified %PDF magic bytes + multi-MB size, per the Tormes-lesson artifact-validation
rule):
- sources/2026-07-20_millscountytx_chisme-fact-sheet.pdf (2.9 MB)
- sources/2026-07-20_millscountytx_red-river-abatement-application.pdf (3.0 MB)
This directly answers triage's open item #3 (Mills County fact sheet for site coords) and
adds a NEW abatement lead the triage never found (ch313.py's negative result above is for
Ch.313/JETI specifically — this is a separate COUNTY (Ch.312-style local) tax abatement
application, filed with Mills County directly, not the state Comptroller registries).

## D3 — Chisme fact sheet read (DECISIVE — company-published, developer's own doc)
sources/2026-07-20_millscountytx_chisme-fact-sheet.pdf (rendered via exhibit.py sheet,
sheet01.png):
- **Site: ~720 acres** in "a remote area away from residences" — sited on the FORMER CAMP
  BOWIE SITE ("project will help remediate the land by removing unexploded ordnance from
  the former Camp Bowie site") — historically significant WWII Army training camp land near
  Brownwood/Goldthwaite, explains "remote/away from residences" framing and unexploded-
  ordnance remediation as a real, specific site detail (not boilerplate).
- Vicinity map: shows Mills County, pin near "Elkins Rd" between Brownwood (Brown Co) and
  Goldthwaite, near Hwy 183/377 junction — CONSISTENT with the Brown/Mills county-line
  candidate site (31.5689, -98.822, ~ 6 km from this map's approximate pin location) and
  with the Gobblers Knob feature cross-check. Map explicitly says "representative...not
  drawn to scale" — cannot extract precise coordinates from it, but it corroborates the
  county-line siting and rules out a materially different location.
- Capacity: 147 MW (AC) solar + 146 MW (AC) battery — matches queue/IA exactly.
- **Construction schedule (company's own, most authoritative non-IA source): start of
  construction ~Q3 2025; estimated startup Q2 2027** — this is ~1 quarter later than the
  signed IA's Scheduled COD (2027-04-13 = Q2 2027, consistent) but construction START
  (Q3 2025) is new information not in the IA (IA's earliest listed date obligations run
  from Dec 2024 NTP through late 2026).
- Economic: ~$265M direct investment; avg $1.086M/yr total tax revenue ($700.3k/yr school
  district, $385.7k/yr county); up to 250 construction jobs; ~27,000 TX homes powered.
- Confirms "Red River Clean Energy" as a "joint venture subsidiary of a multinational
  renewable energy developer... 4 GW of operating assets worldwide... headquartered in
  Austin, Texas" with "a pipeline of projects in the Lone Star State totaling 4 GW" — does
  NOT name the multinational parent explicitly on this page, so "Concord New Energy" as
  ultimate parent remains a lead (from IA billing-email domain) corroborated but not
  confirmed by this doc; contact is a PR firm (Bill Pentak, Open Doors Public Relations),
  standard for a legitimate active development, not a red flag.
This is the map_artifacts candidate per PLAYBOOK rule 4b (company-published site-vicinity
map) — saved as sources/2026-07-20_millscountytx_chisme-fact-sheet_sheet01.png.

## D3 — Abatement application pp1-8 read: DECISIVE parcel + GIS boundary maps
sheet01 (pp1-4, application form): confirms "Blue Heron Solar, LLC, whose parent company is
Red River Clean Energy / Mike Luo" (item 2) — parent relationship now stated explicitly in
a signed county filing, not just inferred from IA notice addresses. "Parcel Listing" table
(p4) names FIVE distinct private landowners across ~3,612 acres total (Clayton Ranches Ltd
1777.989ac, Hardberger George Robert Trustee 1588ac, Childress Charles Grady Sr x4 parcels
75.88+154.615+7.14+8.26ac), all situs "N CR 531" or "390 N CR 531" — Blue Heron is listed
as "Project Sponsor" not "Property Owner" (separate field says "SEE ATTACHED PARCEL
LISTING"), consistent with a lease/option over rancher-owned tracts rather than SPV
ownership. Fiscal section: $267,000,000 added to tax rolls, $1,568,000 direct sales tax,
$972,900 annual opex budget, requested abatement 50% nominal / 34% effective rate.
Application's own construction dates: Construction Start Q4 2025, Construction Complete
Q2 2027, Operations Commence Q2 2027 (filed 2025-10-27 — ONE quarter later start than the
company fact sheet's "Q3 2025," both self-reported, logging the discrepancy not resolving
it).

sheet02 (pp5-8, "SEE MAPS ATTACHED"): FOUR maps titled "Blue Heron Solar, LLC" with a red
"Project Boundary" polygon overlaid on a blue "Mills County" outline:
  1. County-wide view: project boundary sits in NW Mills County, between Brownwood (Brown
     Co, west) and Goldthwaite (Mills Co seat, east), just south of the Brown/Mills line.
  2. Mid-zoom (5 mi scale): shows "Camp Bowie" (labeled gray polygon, the historic WWII Army
     training camp / bombing range) immediately WEST of the project boundary near Zephyr,
     TX — confirms the fact sheet's "former Camp Bowie site... unexploded ordnance"
     language refers to this specific mapped area, not marketing boilerplate.
  3. Detail zoom (0.7 mi scale, topo basemap): precise arrow/quadrilateral-shaped project
     boundary polygon, ~narrow notch on the NE edge — a distinctive, identifiable shape.
  4. SAME boundary overlaid on an ESRI AERIAL/SATELLITE basemap (0.7 mi scale) — shows the
     exact polygon over real terrain: rolling wooded/scrub land bisected by a light-colored
     unpaved road, a small stream at the SE corner, no visible development, clearing, or
     structures inside the boundary as of this basemap's (undated, likely Esri World
     Imagery, NOT dated Sentinel-2) vintage.
THIS (map #4) is the primary site.map_artifacts source — an aerial image with the exact
parcel/project boundary overlaid, superior to the fact sheet's low-res vicinity sketch.
Saved as sources/2026-07-20_millscountytx_red-river-abatement-applica_sheet02.png (all 4
panels; the project boundary + aerial panel is the bottom-right quadrant of this tile).
CROSS-CHECK: this boundary's approximate centroid (visually, between Camp Bowie and
Zephyr, south of the Brown/Mills line, near a CR 531/FM road) is consistent with — same
county-line, same "Zephyr/Camp Bowie" neighborhood — the EIA-860M coordinate (31.5689,
-98.822) and the Gobblers Knob named-feature coordinate (31.5640, -98.8192) already
established in D2. Three independent sources (EIA-860M plant registration, USGS-derived
gazetteer feature, and now a GIS-precision county abatement filing map) converge on the
same ~1-2 km neighborhood. Confidence upgraded to HIGH given this convergence, even though
exact polygon-to-lat/lon georeferencing was not performed (no imagery tool available to
verify pixel-for-pixel — see D2 limits).

## D3 — Abatement application pp9-16 (sheet03/04) read
sheet03 (pp9-12): cover letter from K.E. Andrews (tax consultant, Rockwall TX; Mike Fry,
Senior Director Energy Services) to Mills County Commissioners' Court, dated 2025-10-24 —
CONFIRMS this is a **Texas Property Tax Code Chapter 312** application (county-level
abatement), explaining why ch313.py's negative result is correct and expected: Ch.313/JETI
(state Comptroller value-limitation, checked by ch313.py) is a DIFFERENT program than
Ch.312 (county-level, filed directly with Mills County, not centrally registered/
scrapeable). Confirms parent "Red River Clean Energy" again; applicant contact Mike Luo
(mluo@redrivercleanenergy.com), consultant contact Mike Fry (mfry@keatax.com). Certifies
"Blue Heron Solar, LLC does not currently own any property within the proposed
Reinvestment Zone" — EXPLICIT confirmation of lease/option structure (not owned by SPV),
resolving the land_tenure ambiguity from the parcel-listing table. Terms: 10-year 50%
abatement (structured as 100% abatement + PILOT of $517,852/yr, $5,178,518 over 10 yrs).
Improvements list: standard utility-scale solar+BESS component list (substation,
transmission line, inverters/transformers, racking, BESS, SCADA, etc.) — nothing anomalous.
sheet04 (pp13-16): repeats the parcel table + THREE cleaner "Map of Reinvestment Zone"
panels (topo, aerial, county-wide) at higher legibility than sheet02's four-up — same
project-boundary polygon, same location (NW Mills Co, south of Brown/Mills line, between
Brownwood and Goldthwaite). No new information, just a clean confirmatory repeat —
strengthens confidence the boundary is genuine (not a rendering artifact of one map) since
it appears consistently across two independently-generated map sets in the same filing.

## D3 — Abatement OUTCOME: REJECTED by Mills County Commissioners' Court, 2025-12-29
search.py "Mills County Commissioners Court Blue Heron Solar abatement approved" surfaced
citizenportal.ai (a government-meeting summary/transcript service, NOT a banned
queue-tracker — distinct category, allowed): "Mills County court rejects tax abatement for
Blue Heron solar project in 3-2 vote," published 2025-12-30, describing the Dec 29, 2025
Commissioners' Court meeting. Saved:
sources/2026-07-20_citizenportal_mills-county-rejects-blue-heron-abatement.html
KEY FACTS (from article body, AI-summarized from the meeting video per the site's own
disclaimer — treat as secondary/summarized, corroborated by our own primary-doc read of
the application terms which match exactly):
- Applicant had already REDUCED the request from the original 50% (per the Oct 2025
  application we read) down to 35% before the vote — a concession attempt.
- County guidelines required a net economic benefit of $10M over the abatement period;
  legal discussion centered on whether the proposal met that bar.
- Presiding judge moved for ZERO abatement; seconded by Commissioner Depp; passed 3-2.
- Project rep (Bill Pentak/Pentec — same PR contact as on the fact sheet, "Open Doors
  Public Relations" / presenting for Red River Clean Energy/Blue Heron) told the court the
  $267M project would generate "$17,400,000 in tax revenues for Mills County" and that
  company would pay 100% [of taxable value — cut off by paywall].
IMPLICATION FOR VERDICT: the county rejected the requested INCENTIVE (PILOT/abatement),
NOT the project itself — Blue Heron's project proceeds subject to standard ad valorem
taxation instead of the reduced PILOT rate. This is a real, documented local political/
regulatory friction point (adds cost, could theoretically factor into financing economics)
but is NOT evidence the project is being cancelled or is paper — if anything, the
presentation to the court (attorneys, financial projections, reduced counter-offer) is
itself evidence of active, funded, ongoing development. Logging as a genuine risk/schedule
factor for the COD assessment, not as a red flag on realness.

# WRAP-UP — D5 deterministic tools

## queue_history.py 24INR0333
Confirms same 42 snapshots / 3 COD changes already known from triage — no drift since.

## eia_history.py 24INR0333 --write — DECISIVE independent construction confirmation
EIA plant 68078 "Chisme Solar and Storage," entity Red River Clean Energy (name match).
Reports 2024-10-01 -> 2026-05-01 (19 monthly snapshots). KEY FINDING:
- **Status transition**: "(T) Regulatory approvals received. Not under construction"
  (2024-10 through 2026-03) -> **"(U) Under construction, less than or equal to 50 percent
  complete" (2026-04, 2026-05)**. This is an INDEPENDENT, non-visual confirmation that
  physical construction is underway as of April 2026 — substitutes for the imagery
  verification that CDSE/gmaps outages prevented this run. Sourced from the entity's own
  monthly EIA-860M filing, a federal reporting obligation with penalties for
  misrepresentation — stronger evidence than a marketing fact sheet.
- EIA capacity: flat 293.0 MW for the entire history — matches 147 (solar) + 146
  (storage) combined exactly, confirming EIA is tracking the co-located solar+storage
  facility as one plant record.
- Planned COD: 2027-04 (2024-10 through 2026-04) -> 2027-05 (2026-05, most recent) — a
  ONE-MONTH slip in the latest snapshot, negligible, still lands in the same quarter
  (2027-Q2) as the signed IA's 2027-04-13 date.
- Coordinates 31.56893,-98.82195 (Brown Co) — same as factsheet.json, already used as the
  site candidate.
This closes the construction-verdict gap left by the imagery outage: independent evidence
(EIA-860M self-report, backed by federal reporting obligation) now supports "under
construction, <=50% complete" as of 2026-04/05, distinct from mere developer PR framing.

## build_brief.py / build_index.py
build_brief.py 24INR0333: wrote brief.html (15 KB, 0 images [no imagery this run], 28
sources cited). build_index.py: refreshed research/index.json + INDEX.md (162 projects).
Both ran clean, no errors.

## RUN COMPLETE
findings.json, dossier.md, log.md, brief.html all written and internally consistent.
Verdict: real_early. Independent COD 2027-Q2 (matches signed IA + EIA-860M + company fact
sheet, 3-way convergence). Drift risk medium (grounded but two unresolved risk factors:
rejected abatement, no visual construction confirmation). Site 31.5689,-98.8220, high
confidence via 3-source convergence, no imagery obtained (CDSE 402 credits exhausted,
gmaps 403 API not enabled — both logged as infra failures for the operator to fix).
Turns used: this deep-scan session started fresh (no prior deep run existed); triage was
already complete on disk. All PLAYBOOK stages D0-D5 executed in order.

## D1 — Remaining exhibit sheets checked (sheet09-12), NO parcel/boundary map found
Attachment 1 to Exhibit C (sheet11, p41) = ONE LINE DIAGRAM "Gobbers Knob Switch" — purely
schematic (breakers/buses), explicitly labeled "for illustration only, not for design/
construction/operations." Names "Generator Switchyard (Chisme Project)" but has NO
geographic coordinates or parcel boundary. Attachment 2/2A/3 (sheet12, pp42-45) = SCADA
table + communications block diagram + protection requirements — also non-geographic.
CONCLUSION: this signed IA contains no site/parcel map exhibit (unlike Hanson's Ch313
Improvements Map) — `site.map_artifacts` stays empty for this doc; site must be pinpointed
via POI infrastructure name ("Gobbers Knob Switch" — a NEW/proposed switch, not yet on
OpenInfraMap presumably) + gmaps + EIA-860M coords candidate + imagery, per Stage 3.

# IMAGERY FIX + CLEANUP — 2026-07-21

## Banned-domain cleanup
Grepped findings.json, dossier.md, log.md, triage.md, triage_findings.json, brief.html for
infrasure|futuregrid|cleanview|interconnection.fyi|gridinfo|ercotqueue|energyacuity — ZERO
hits in any of those six curated files (prior authors had already anonymized the "low
build-chance" tracker mention to "one tracker" / "a third-party tracker" without naming the
domain). ONE hit found in `sources/t3_web_sweep.md` (a T3-stage working note, itself
authored in-house, not a file fetched FROM a banned domain): a bullet read "build-chance:
noted as low (5%) on ercotqueue.com". Removed that bullet line (the domain-name citation)
from t3_web_sweep.md — the rest of the file's content (developer/LLC confirmation, PUCT
lead) is unaffected and was not banned-sourced. brief.html links to t3_web_sweep.md as one
of its 28 cited sources but does not itself repeat the banned-domain string. No sources/
files needed deletion (no PDF/HTML was actually fetched from a banned domain this project).
Also confirmed banned-domain mentions appear in raw agent transcripts
(run_stream_triage.jsonl — a DDG search result snippet quoting infrasure.ai/
interconnection.fyi/ercotqueue.com verbatim) but those are unedited tool-call logs, not
curated findings/citations, and are out of scope for this cleanup pass.

## Site provenance rung — established
Per the map-exhibit > IA-Exhibit-C-text > imagery-verified-EIA > documented-Places-pin
hierarchy: IA Exhibit C's POI coordinates are redacted/blacked-out in the signed IA text
(confirmed in D1 above), so rung 2 is unavailable. The abatement application's project-
boundary map (rung 1) was never formally georeferenced to lat/lon (no GIS overlay tool
available). The EIA-860M plant coordinate (31.568929,-98.82195, rung 3) was the best
available anchor but was UNVERIFIED against imagery as of the last run (CDSE was down).
This run closes that gap: fetched Sentinel-2 imagery at the exact EIA coordinate via
s2aws.py (CDSE-independent, AWS Open Data) and confirmed a construction footprint sits
there, whose outline shape matches the rung-1 map exhibit's polygon feature-for-feature.
Effective rung achieved: imagery-verified EIA (rung 3), strongly corroborated by an
(unformalized) shape match to the rung-1 map exhibit. Coordinate unchanged
(31.568929,-98.82195 full precision, was rounded to 31.5689,-98.822 previously).

## Imagery fetch + tool quirk found
`s2aws.py chips --lat 31.56893 --lon -98.82195 --dates 2024-07-01,2025-07-01,2026-01-15,
2026-04-15,2026-07-15 --buffer-km 3.5 --window-days 20 --max-cloud 25` ran clean (5/5
chips written, valid PNG magic bytes). On READ-verification (task step 4), the 2024-07-01
and 2025-07-01 chips had a partial-black bottom strip (~15% of frame height) — a tile-edge/
swath-boundary nodata artifact, NOT cloud: this site sits almost exactly on the MGRS
14S/14R latitude-band boundary (tiles 14SNA vs 14RNV), and the particular 14SNA granules
the tool auto-selected had incomplete swath coverage at the buffer's southern edge. The
2026-01-15 chip was cloud/haze-ruined (near-white, unusable) despite the STAC item
reporting only 9.6% cloud_cover (metadata is a whole-tile average; this buffer's sub-region
was worse). Root-caused a real bug in s2aws.py while investigating: its STAC query
requests `sort: eo:cloud_cover asc` but the earth-search.aws.element84.com endpoint
appears to ignore/not-honor that sort param — direct queries showed results actually
returned in date-descending order (filtered by the cloud threshold), so `items[0]` is "most
recent scene under the cloud cap," not "lowest-cloud scene in the window" as the tool's own
docstring claims. Not fixing the shared tool this run (out of scope for a single-project
imagery pass; flagging for the operator) — worked around it by using single `chip` calls
with a 1-day window targeting specific dates/tiles identified via manual STAC queries
(sanctioned use of the same tool, no scraping):
- 2024-07-01 -> replaced with 2024-07-07 (S2B_14RNV_20240707_0_L2A, 18.9% cloud, RNV tile,
  no seam)
- 2025-07-01 -> replaced with 2025-07-17 (S2C_14RNV_20250717_0_L2A, 8.6% cloud, RNV tile,
  no seam)
- 2026-01-15 -> replaced with 2026-01-03 (S2C_14RNV_20260103_0_L2A, 0.0% cloud, RNV tile) —
  bonus: winter leaf-off imagery makes the project's perimeter road/clearing MUCH more
  legible than the originally-targeted mid-Jan date would have been anyway
- 2026-04-15 -> kept as-fetched (S2C_14RNV_20260503_0_L2A, 0.0% cloud, already clean)
- 2026-07-15 -> swapped for a cleaner nearby scene, 2026-06-27 (S2B_14RNV_20260627_1_L2A,
  3.1% cloud vs. the original 2026-07-02 pick's 13.4% cloud with a distracting cloud-shadow
  blob over part of the frame) — same construction-progress checkpoint, better legibility
No probe/wrong-location chips were generated in research/24INR0333_chisme-solar/imagery/ —
all test fetches for the swapped dates were written to /tmp scratch and only the accepted
final PNGs were copied into imagery/key/. All 5 final PNGs re-verified as valid PNG magic
bytes after the swap.

## Per-date imagery read (see findings.json construction.evidence for the citable version)
- 2024-07-07: undisturbed rangeland/woodland + ranch roads, no project boundary or
  clearing visible anywhere in frame. Clean pre-construction baseline.
- 2025-07-17: same — still no clearing/grading anywhere in the project footprint. Company
  fact sheet's "construction start ~Q3 2025" is NOT visually corroborated by this date;
  either genuinely not yet started, or below-resolution preliminary work only.
- 2026-01-03: FIRST frame showing the project. Leaf-off winter contrast reveals the
  distinctive arrow/quadrilateral perimeter access road (exact shape match to the Ch.312
  abatement app's boundary map) with the central-to-southern interior already cleared/bare
  soil (tan); the NE arm of the polygon is still dark/vegetated (not yet touched). Confirms
  ground-breaking occurred in the ~5.5-month gap since the last clean baseline.
- 2026-05-03: full site graded — complete perimeter + dense internal access-road grid
  subdividing the site into blocks, plus a light-toned staging/laydown area in the NW
  corner (probable substation/O&M pad). Matches the EIA-860M "(U) Under construction"
  status-flip month exactly.
- 2026-06-27: interior grading now covers nearly the whole polygon; NW staging area larger
  with visible light-colored objects (equipment/materials). Civil works essentially
  complete. No individual panel/racking rows resolvable at Sentinel-2's 10m pixel size —
  cannot confirm or rule out array-installation progress from this imagery alone.

## Neighbor check (data/eia_generator_tx.parquet, latest reportDate 2026-05-01)
Brown County rows: Chisme Solar and Storage (68078, exact coordinate match, "(U) Under
construction"); IP Radian LLC (64859, 320MW operating solar+BESS, 31.5481,-99.1872,
~31km W of Chisme); Wetzel BESS (67555, RIC Development, "(P) Planned, regulatory approvals
not initiated", 31.7070,-98.8575, ~15km N of Chisme). Neither neighbor falls inside the
3.5km imagery buffer used above — no risk this run of misattributing a neighbor's
development to Chisme.

## findings.json updated
site.lat/lon set to full EIA precision (31.568929,-98.82195, was rounded 31.5689,-98.822);
site.method/confidence updated with the imagery-verification + provenance-rung language
above. construction.verdict -> under_construction_confirmed_visually (was
under_construction_unverified_visually). construction.first_activity_seen -> "≤2026-01-03"
(imagery-bounded, was "2026-04-01" which had come from the EIA status-flip month, not from
visual evidence). construction.imagery_artifacts added (5 paths). construction.evidence
appended with the imagery findings, boundary-shape cross-check, and neighbor cross-check;
prior CDSE/gmaps outage bullets kept for the historical record but reframed as resolved
via s2aws.py.
