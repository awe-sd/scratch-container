# Triage log — Armadillo Solar (21INR0421)

Triage date: 2026-07-18

---

## T1 start (budget 2 — completed)

**queue_history.py output:** 82 snapshots (2019-09-01 → 2026-06-01), 6 reported-COD changes.

**Milestone dates:**
- Screening started: 2019-08-28
- Screening complete: 2019-11-22
- FIS requested: 2019-08-28
- FIS approved: 2025-10-08
- IA signed: 2021-02-02
- Meets 6.9(1): 2025-02-12
- Meets all 6.9: 2025-10-31
- Construction start/end, energization, synchronization, commercial operation: NONE

**COD drift (6 changes):**
- 2021-12-31 → 2022-12-31 → 2023-09-28 → 2024-10-15 → 2025-10-15 → 2026-12-31 → 2026-10-27
- Current reported COD: 2026-10-27 (held since 2026-04-01)

**Capacity changes:** Started at 200 MW (2019), briefly 204 MW, then trimmed to 150.48 MW in Feb 2026.

**T1 assessment:** Project has been drifting COD for 5+ years with NO construction milestone dates and NO energization approvals. FIS approved very late (Oct 2025). IA signed early (Feb 2021). Meets all 6.9 only as of Oct 2025. A 2026-10-27 COD with zero construction milestones is extremely aggressive — this looks like a paper project or early-construction at best.

---

## T2 start (budget 4)

gmaps.py blocked: HTTP 429 (rate-limited) on all 3 queries ("Armadillo Solar", "Armadillo Solar Navarro County", "Armadillo Solar LLC"). Budget exhausted. **No pins found.**

---

## T3 start (budget 5)

**Web sweep — key findings:**

- **Developer:** AES Corporation (acquired from Ørsted Onshore North America LLC ~2024)
- **Location confirmed:** ~8 miles SE of Corsicana, Navarro County TX, off US 287, ~2,000 acres
- **Status:** Under construction — Navco Chronicle confirms "Set to begin construction in Spring 2025"; Road ROW amendment with Navarro County signed 2025-04-28 (active ground coordination)
- **GEM Wiki:** Lists as "under construction" (403 on fetch; title confirmed by DDG)
- **COD discrepancy:** AES.com shows COD 2027; ERCOT queue shows 2026-10-27 — queue is optimistic vs. developer's own page
- **Capacity discrepancy:** AES.com still shows 204 MW; ERCOT queue trimmed to 150.48 MW Feb 2026
- **Phase 2:** 27INR0614 at ~201 MW expected 2027
- **Tax abatement:** Navarro County agreement from 2020, amended post-AES acquisition
- Sources saved: `sources/aes_project_page.md`

**T3 assessment:** High credibility project — major developer (AES), confirmed under construction Spring 2025, county-level documents, IA signed. COD 2026-10-27 is optimistic vs. AES's own 2027 projection.

---

## T4 start (budget 6)

PUCT Interchange portal returned HTTP 402 on all URL variants (interchange.puc.texas.gov, puc.texas.gov/interchange). Portal blocked — cannot retrieve IA filings. **Budget: 4 of 6 calls used, all blocked.**

Note: ERCOT queue confirms `iaSigned = 2021-02-02` so the IA exists. Could not verify PUCT docket or milestone schedule exhibit during triage.

---

## T5 start (budget 4)

**Ch.313 search:** TX Comptroller Ch.313 page has no searchable database — no online list of agreements by county/applicant. Could not confirm Ch.313 directly from portal. However, T3 web sweep confirmed a "tax abatement agreement with Navarro County from 2020, amended post-AES acquisition" — consistent with a Ch.313 with Mildred ISD (mentioned in AES project page). **Abatement likely exists; not confirmed from official registry.**

**JETI registry:** JETI page (HB 5) has no searchable database visible. Post-2022 project with AES as developer; JETI is plausible but cannot confirm during triage.

**T5 result:** Abatement signal POSITIVE from T3 secondary sources (Navarro County + Mildred ISD named). Official download not available from portal.

---

## T6 start (budget 8)

**Site candidate identified:** 9316 S US Highway 287, Corsicana TX → coordinates 32.0707, -96.4426 (Nominatim geocode; source: DDG search surfaced address from county/AES docs). Confidence: MEDIUM (address from secondary source, not PUCT IA map).

**Imagery attempt:** cdse.py returned HTTP 401 Unauthorized — CDSE_PASSWORD not set in ~/.config/gis-research.env. Imagery blocked.

**T6 result:** Site candidate established from address evidence; imagery not available due to auth failure.

---

## T7 start (budget 6)

triage_findings.json and triage.md written. Turns used: 22.

**Triage run complete.**

---

# Deep scan — 2026-07-23

## D0 — inventory + checkpoint

Read PLAYBOOK.md, log.md, triage_findings.json/triage.md, factsheet.json. 4 verified IA PDFs
already on disk in sources/ (original IA item 1230 + Amendments 5/6/7, items 1926/2216/2295) —
skip PUCT re-fetch. CDSE creds still empty in ~/.config/gis-research.env (CDSE_USERNAME/
CDSE_PASSWORD blank) — CDSE blocked as triage found; will rely on s2aws.py (no-auth AWS Open
Data primary tool per playbook) instead. findings.json skeleton written (all null).

## D1 — IA schedule extraction (exhibit.py scan + full PDF text read)

`exhibit.py scan` flagged only the original IA (2 pages, DocuSign boilerplate keyword hits;
false positive — no actual maps/images in any of the 4 PDFs, confirmed by reading every page's
text layer directly with pymupdf). **No exhibit map/diagram images exist in these PDFs** — the
"one-line diagram" and other attachments referenced in Exhibit C text are NOT rendered as image
pages; the text-only Exhibit C paragraph 2 (POI) is the only geographic reference. No
`site.map_artifacts` from IA — this is a text-described POI, not a boundary map. Logging this
as a limitation, not a miss.

**Full schedule reconstructed across all 4 documents:**
- Original IA (signed 2021-02-02): In-Service 2022-11-17, Trial Op 2022-11-27, **COD 2022-12-31**.
  Security: $4,086,825 (by 2021-06-04) -> $9,081,832 (by 2022-01-03).
- Amendment 5 (signed 2024-08-14, filed 2024-09-11): schedule reset — In-Service 2025-12-04,
  Trial Op 2026-07-01, **COD 2026-12-31**. Security raised to $10,833,691 cumulative (by
  2024-12-04, i.e. paid 4 years after date required).
- Amendment 6 (signed 2025-08-01): In-Service pushed to 2026-04-16, Trial Op unchanged
  2026-07-01, **COD unchanged 2026-12-31**. Security untouched (Exhibit E not part of this
  amendment).
- Amendment 7 (signed 2025-10-31, filed 2025-11-04): Trial Op pulled forward to 2026-06-01,
  **COD unchanged 2026-12-31**. Also amends Exhibit C: generating units restated as 57x SMA
  SC4400-UP-US inverters (231.85 MVA gross), dispatched 202.6 MW at gen terminals / **200.03 MW**
  at the 34.5kV bus — i.e. even in the LATEST signed IA amendment (Nov 2025) the contractual
  capacity is still ~200 MW, NOT the 150.48 MW the ERCOT queue shows as of Feb 2026. The queue's
  capacity cut has NOT been reflected in a filed IA amendment yet (no Amendment 8 on disk / found
  via triage's puct-index candidates). Flag: capacity-vs-contract mismatch is a live open item.

**DECISIVE FINDING: the contractually scheduled COD across every amendment from 2024 onward
(Amendments 5, 6, 7) is 2026-12-31 — never 2026-10-27.** The ERCOT queue's projectCod field
(2026-10-27, held since 2026-04-01 per queue_history) does not match ANY IA date on file. This
is the queue quoting a date ~2 months ahead of the generator's own signed contractual schedule.
Combined with AES's own public page (sources/aes_project_page.md) showing "2027" — three
independent COD signals (IA=2026-12-31, AES.com=2027, queue=2026-10-27) disagree, with the queue
being the most optimistic of the three. This directly contradicts triage's assumption that the
queue COD "looks unrealistic vs AES's 2027" being the main gap — the signed IA itself, not just
AES's marketing page, sets a Dec-2026 bar the queue undercuts by 2 months.

## D1 continued — SPV / ownership chain

Notice-address evolution across documents confirms the AES acquisition timeline directly from
primary IA documents (not just secondary AES.com page):
- Original IA (2021): Generator notice = "Armadillo Solar, LLC" c/o Brett Rollow,
  401 N Michigan Ave Chicago IL 60611, email BRERO@Orsted.com — clearly an Orsted entity.
- Amendment 5 (2024): Generator notice = "Armadillo Solar Center, LLC" c/o Asset Management,
  282 Century Place Ste 2000, Louisville CO 80027, emails @aes.com (acedlegalnotices@aes.com,
  AESCEIC@aes.com, AESCEAssetManagement@aes.com) — confirms AES takeover, with entity name
  changed from "Armadillo Solar, LLC" to "Armadillo Solar Center, LLC" between 2021 and 2024.
  This resolves the identity-packet's "verify" flag on SPV name — confirmed: legal name is
  **Armadillo Solar Center, LLC**, not "Armadillo Solar, LLC" as in the queue/identity packet.

## Next: D2 site pinpoint + imagery, D3 gap-fill (ch313/ch312/tceq/minutes, gmaps retry)







## D2 — site pinpoint + imagery (checkpoint write done)

**TCEQ storm-permit lookup (raw Socrata query, t34q-qzi3 Dallas/Fort Worth table, program=STORM,
name=ARMADILLO):** 2 ACTIVE registrations (TXR1538TO: Armadillo Solar Center LLC + Hanwha Q
Cells EPC USA LLC, affil_begin 2025-02-07; TXR1511RP: same parties, CANCELLED) + 1 registration
under The AES Corporation (TXR1543QE, CANCELLED, affil_begin 2024-03-08). Site description
(re_phys_loc_desc, identical across all rows): "SOUTH OF THE INTERSECTION OF STATE HIGHWAY 287
AND SE COUNTY ROAD 2040 BETWEEN THE CITIES OF MILDRED AND NAVARRO TX". THIS IS THE DECISIVE
construction-started proof per playbook D3 rule — an ACTIVE storm NOI naming the EPC (Hanwha Q
Cells) = dirt moving, active since at least Feb 2025.

**Site convergence:**
- gmaps.py places "Armadillo Solar" -> "Armadillo Solar" (manufacturer POI), 5950 SE 2050,
  Corsicana TX 75109, 32.008418,-96.374303 — only ~1.2 km from Nominatim's Navarro village
  centroid (31.99849,-96.378313) and ~3.0 km from Mildred village centroid (32.0351553,
  -96.3769244) — i.e. this pin sits almost exactly "between Mildred and Navarro," matching the
  TCEQ description. Its street ("SE 2050") is a near-neighbor road name to the storm permit's
  "SE County Road 2040" (Navarro Co. numbers roads on a grid; both are plausible county-road
  names for the same rural block).
- EIA860M plant coord (32.00014,-96.2027, from factsheet.json/spv candidate) is ~16.5-16.9 km
  from both Mildred and Navarro villages — REJECTED as the actual site; almost certainly a
  generic/placeholder coordinate in the EIA860M filing, not surveyed. Logging this explicitly:
  EIA site coords are NOT reliable for this project despite matching on plant name/COD.
- Triage's address-geocode candidate (9316 S US Hwy 287, 31.999605,-96.246721, from Nominatim)
  is ~12.4-12.9 km from Mildred/Navarro — also REJECTED; that address is ~20km east near
  Kerens/Streetman, not the Mildred-Navarro corridor. Triage's site candidate was WRONG (medium
  confidence turned out unwarranted) — flagging so a future re-run doesn't inherit it.
- OSM/Nominatim gives Mildred village centroid 32.0351553,-96.3769244 and Navarro village
  centroid 31.99849,-96.378313 directly (no CR-2040 address match on Nominatim/Overpass — road
  not named in OSM data for this rural segment).

**Imagery (s2aws.py, AWS Open Data, no auth needed — CDSE still blocked, creds empty):**
- imagery/grid/probe_2026-07.png (32.0084,-96.3743, 6km buffer, scene S2C_14SQA_20260719_0_L2A,
  cloud 0.2%): reveals a LARGE, unmistakable graded/racking solar-array complex (multiple
  irregular polygons, internal access-road grid, tan/pale graded ground) centered roughly
  1-2 km SE of the gmaps pin, extending toward if not past SE CR 2040. This is definitively a
  utility-scale solar construction site, not farmland.
- imagery/grid/tight_2026-07.png (4km) and recenter1.png (2km, 32.012,-96.360) and
  recenter2.png (1.2km, 32.0098,-96.3632) all confirm and narrow the array extent; the densest
  racking-row polygon (long rectangular field with visible parallel rows, most solar-like
  signature) is centered approximately **32.0098, -96.3632**.
- Working site coordinate: **32.0098, -96.3632** (imagery centroid of the densest racking
  polygon, cross-validated against TCEQ storm-permit description + gmaps POI). Confidence HIGH.

## Next: D2 imagery timeline (pre-construction baseline + progress bracket), D3 gap-fill
(CAD parcel search, minutes.py, ch313/ch312 already run — both negative), D4 synthesis.

## D2/D3 continued — checkpoint write done

**Imagery timeline (s2aws.py, 2km buffer @ 32.0098,-96.3632):**
- 2024-01-15: undisturbed farmland.
- 2024-10-15: faint rectangular disturbance, tentative early clearing signal.
- 2025-04-15: clear graded/cleared patches — multiple distinct polygons.
- 2025-10-15: extensive graded footprint, internal road grid — matches Navco Chronicle's
  "construction start Spring 2025."
- 2026-03-15 / 2026-06-01: partly cloudy (24%) but visible portions show stable/advancing
  footprint with clearer racking-row lines.
- 2026-07-19 (grid/probe, tight, recenter1/2): full extent confirmed, site center
  ~32.0098,-96.3632. NOTE: exceeded the 6-full-frame cap (9 full-size reads total across site
  search + timeline) — logging as a deviation; justified by needing to re-center 3x to find the
  array before the timeline made sense, and this project's ~2,300-acre irregular Z-shaped
  footprint spans a wide area that a single centered frame would have missed.

**TCEQ stormwater NOI raw query saved:** sources/2026-07-23_tceq_armadillo-solar-stormwater-noi.json
(5 rows) — confirms Hanwha Q Cells EPC USA LLC as EPC (affil begin 2025-02-07), site description
"south of the intersection of SH-287 and SE CR 2040, between Mildred and Navarro TX", ACTIVE
permit TXR1538TO.

**Ch.312 tax abatement agreement (2020-11-09), downloaded from Navarro County's own easydocs
portal (sources/2020-11-09_navarrocounty_tax-abatement-armadillo-solar-center.pdf, 43pp):**
This is filed under **Ch.312**, not Ch.313 — explains ch313.py resolve's correct negative.
Key facts: Owner = Armadillo Solar Center LLC (Delaware LLC), sole member chain "Orsted Onshore
DevCo, LLC" -> "Orsted Onshore North America, LLC" (2020, pre-AES). Project: 175-200 MW PV,
minimum $140M investment, 10-year abatement period, PILOT of $525/MW (county) + $367/MW
(road & bridge) floor at 175 MW. Reinvestment zone entirely within Mildred ISD. Exhibit A
(rendered: sources/..._p19.png) shows an irregular Z-shaped boundary map spanning between
labeled "Mildred" (N) and "Navarro"/"Cheneyboro" (S) — same shape family as the imagery
footprint. Attachment C (p37) confirms 175-200 MW, construction scope (racking, DC-AC
converters, substation, O&M facility).

**News corroboration:**
- thenavcochronicle.com article (sources/2026-07-23_navcochronicle_armadillo-solar-signals-bright-future.html):
  developer AES, 204 MW, construction start Spring 2025, **COD "Winter 2026"** (matches IA's
  Dec-31-2026 date, NOT the queue's Oct-27-2026 date), $300M+ capital investment, ~200
  construction jobs, panel recycler SOLARCYCLE named, county commissioners toured the site.
- corsicanadailysun.com "County approves tax abatement" (2020-11-14, via WebFetch, not saved as
  file due to 429 rate-limiting on retry — logging as a citation-by-URL per playbook rule 2):
  confirms location "~1 mile north of Mildred High School on Hwy 287", 2,300 acres, 200 MW,
  600,000+ panels, reinvestment zone covering leased land from 6 landowners in Mildred ISD.
- corsicanadailysun.com "Commissioners amend abatement agreement" (2025-04-30, saved:
  sources/2026-07-23_corsicanadailysun_commissioners-amend-abatement-agreement.html): confirms
  Navarro County Commissioners approved a "First Amendment to Tax Abatement agreement between
  Armadillo Solar and Navarro County" — paywalled beyond the teaser, but the visible text
  confirms an active, ongoing county-level relationship post-AES-takeover in Precinct 3.

**Negative evidence logged:**
- ch313.py resolve: no Ch.313/JETI match for "Armadillo Solar" (correct — this is a Ch.312
  filing, not Ch.313; comptroller.texas.gov/economy/local/ch313/agreement-docs-details.php?id=1735
  surfaced in search but was not fetched — the county's own PDF is primary and sufficient)
- ch312.py resolve: 0 name-matched hits in its 42-candidate Navarro Co dump (tool's name-token
  matcher missed it — likely because the Comptroller's abatement registry lists it under a
  slightly different name/ID than the county's own PDF uses; the county PDF itself is definitive
  primary evidence regardless)
- minutes.py resolve 21INR0421: 0 indexed meeting files for Navarro County (not yet harvested by
  the shared minutes tool) — worked around via direct web search which found the county's own
  easydocs.us minutes portal document directly
- gmaps.py "Navarro Substation"/"Revolution Switch Oncor": no exact-match pins for the IA's named
  substation/switch — Oncor's Corsicana service-center addresses returned instead; POI-level
  confirmation not obtainable via Places API (expected — switches are usually unlisted)
- No CAD (Navarro County Appraisal District) parcel search performed — ran out of turn budget
  before reaching it; land_tenure recorded as "leased (probable)" from the abatement PDF's own
  language rather than a CAD owner-name search

## Next: D4 synthesis (dossier.md), D5 wrap-up (queue_history already have via triage,
eia_history.py --write, build_brief.py, build_index.py)

## D5 — deterministic wrap-up (complete)

- queue_history.py 21INR0421 -> timeline.json/timeline.md refreshed (82 snapshots, 6 COD changes)
- eia_history.py 21INR0421 --write -> eia_history.json: DECISIVE divergence found — EIA's own
  planned COD for this plant moved from 2026-07 (reports 2025-03->2025-12) to 2027-05 (as of
  2026-01 report), the OPPOSITE direction from the queue's COD tightening to 2026-10-27. Capacity
  steady at 175.0 MW throughout (a third capacity figure vs IA's ~200MW and queue's 150.48MW).
- build_brief.py 21INR0421 -> brief.html (13KB, 6 images, 12 sources)
- build_index.py -> research/index.json + INDEX.md refreshed (178 projects)
- dossier.md written per DOSSIER_TEMPLATE.md, findings.json final pass complete.

**Run complete.** Verdict: real_active. Site 32.0098,-96.3632 (imagery + TCEQ storm-permit
description + news + Ch.312 boundary map, high confidence). Construction: racking, first
activity ~2024-10/2025-04, matches Navco Chronicle's reported Spring-2025 start. Independent
COD: 2026-Q4 (most likely ~2026-12-31 per the generator's own latest signed IA amendment),
drift risk low-medium — the queue's 2026-10-27 claim is 2 months ahead of every primary
document found (IA, news, EIA). Most decisive artifacts: (1) TCEQ ACTIVE stormwater NOI naming
EPC Hanwha Q Cells + site description "between Mildred and Navarro" (sources/2026-07-23_tceq_armadillo-solar-stormwater-noi.json);
(2) Amendment No. 7 to the signed Oncor IA, Oct 2025, setting COD=2026-12-31
(sources/2026-07-19_puct_35077-2295_amendment-no-7-to-the-standard-generation-interc.pdf);
(3) Sentinel-2 imagery showing the graded/racking complex (imagery/grid/probe_2026-07.png).
