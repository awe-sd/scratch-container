# Triage log — Possum Kingdom Solar (24INR0118)

## T1 start
- queue_history.py: 50 monthly snapshots (2022-05 → 2026-06); 3 reported-COD changes
- COD drift: 2024-11-22 → 2026-05-08 → 2026-10-30 → 2027-10-29 (current)
- Key milestones: Screening complete 2021-11-29; FIS approved 2025-03-18; IA signed 2025-07-25; Meets 6.9(1) 2026-06-09
- Construction start reported 2025-05-01; construction end reported 2026-05-08 (but COD = 2027-10-29 — ~17-month gap)
- Capacity crept up: 260.0 → 261.36 → 262.22 MW
- Meets all 6.9: not yet; commercial operation not approved
- Note: IA signed 2025-07-25, appearing in queue first 2026-04-01 (likely late-reported)

## T2 start
- gmaps.py: HTTP 429 on all 4 queries (rate-limited); 0 pins found. Normal outcome.

## T3 start
- Bing: "Possum Kingdom Solar" + Texas → 0 project results (only opossum animal pages); DDG 403
- Bing: LLC + 24INR0118 → 0 project results
- opencorporates.com → CAPTCHA/403 blocked; 1 retry = also blocked
- No news, no press releases, no developer name surfaced
- T3 result: no web presence found

## T4 start
- interchange.puc.texas.gov: HTTP 402 on all direct URL attempts (FilingParty= and Description= params)
- Bing site: search → CAPTCHA blocked; Bing general search → 0 results
- Queue data DOES show iaSigned = 2025-07-25 (first appeared 2026-04-01), so IA exists in ERCOT system
- IA PDF not retrievable via available web tools during triage
- T4 result: ia_found=true (ERCOT milestone confirms), PDF not downloaded

## T5 start
- TX Comptroller Ch.313 pages: general overview, no searchable list directly accessible
- Bing: Ch.313 / JETI / Jack County → 0 project results (all opossum results)
- Post-2022 project → missing Ch.313/JETI is expected (program expired Sept 2023)
- T5 result: abatement_found=false (normal for post-2022 entry)

## T6 start
- No pin from T2 (gmaps 429); no IA PDF map (PUCT 402); no abatement map
- Tried to resolve "Willow Creek Switch 345kV" POI → Bing returns unrelated results, no coordinates
- Best site estimate = "somewhere in Jack County" → checklist says SKIP imagery
- T6 result: no site candidate; imagery skipped

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~22
- Run complete

## Deep Scan — Stage 1: LLC → parent chain

### GIS xlsx re-read: LLC confirmed
- Source: local GIS xlsx (RPT.00015933…GIS_Report_Jun2026.xlsx, sheet "Project Details - Large Gen", row 395)
- **CRITICAL CORRECTION: LLC is "PK Solar, LLC" NOT "Possum Kingdom Solar, LLC"**
- Same LLC (PK Solar, LLC) also owns companion project 24INR0375 "Possum Kingdom BESS" (200.86 MW battery), same POI, same IA date 2025-07-30
- Combined project is ~263 MW solar + ~201 MW BESS; co-located at Willow Creek Switch in Jack County
- Artifact: local xlsx row, no saved file needed (authoritative source)

### Developer identity: NOT FOUND
- Bing searches for "PK Solar" Texas returned only Bollywood film / Pakistan results (CAPTCHA + irrelevant)
- Bing news: zero results for "Possum Kingdom Solar" or "PK Solar"
- Bing news for 24INR0375 / Possum Kingdom BESS: zero results
- pv-magazine, pv-tech, renewableenergyworld: blocked or no results
- SEC EDGAR full-text: 403 Forbidden
- TX Comptroller entity search: form-based, not accessible via GET/POST
- OpenCorporates: CAPTCHA-blocked
- TX SOS: paid portal ($1/search)
- **Conclusion: developer identity not determinable via web search; LLC name "PK Solar" is non-searchable**

### Co-POI context: Hecate Energy also at Willow Creek
- ERCOT queue shows 3 Hecate Energy "Dovetail Solar" projects (1-3) + Dovetail Storage all tapping bus 1421 Willow Creek in Jack County
- This confirms: (a) Willow Creek Switch is a real, accessible 345kV POI in Jack County; (b) the POI is capable of hosting multiple large projects
- Hecate Dovetail projects have no IA signed (FIS Started status) — they are earlier-stage than PK Solar

## Deep Scan — Stage 2: County records sweep

### PUCT Interchange: IA NOT retrieved
- All direct PUCT interchange.puc.texas.gov searches return HTTP 402 (requires authenticated session)
- ERCOT queue confirms iaSigned = 2025-07-25 (first appeared 2026-04-01, late-reported)
- IA document content (parties, schedule exhibit, POI map): unknown
- **Negative finding: IA PDF not retrievable with available tools**

### Jack County CAD: not accessible
- jackcad.org property search requires interactive form (no GET endpoint found)
- Attempts to search "PK Solar" as owner returned 404 errors
- **Negative finding: CAD parcels not retrieved**

### Ch.313/JETI abatement: not applicable
- Project entered queue 2022; Ch.313 expired Sept 2023; JETI post-2023
- No Ch.313 found (expected for post-2022 entry)

### Commissioners court: not accessible
- jackcounty.org returns 400; no online minutes portal found
- **Negative finding: no county government records retrieved**

## Deep Scan — Stage 3: Site pinpoint

### POI substations triangulated via OSM
- **Willow Creek Substation (bus 1421): 33.0562°N, 97.9103°W → Wise County** (reverse geocoded via Nominatim)
- **Jacksboro Substation (bus 1429): 33.2772°N, 98.1068°W → Jack County** (Nominatim)
- Willow Creek is at the Jack/Wise county border (east of Jack County centroid)
- Thomas Price (bus 11523) location NOT found via OSM or search
- The Willow Creek–Thomas Price 345kV line segment runs through Jack County
- Wise County Power Repower (20INR0286) also connects to "1421 Willow Creek 345kV" but is in Wise County — the switch straddles the county boundary area
- **Best estimate for project: eastern Jack County, roughly 33.0-33.2°N, 98.0-98.3°W — a ~30 km² search zone**
- gmaps.py: persistently 429 rate-limited (all attempts failed)
- Satellite imagery: CDSE 401 Unauthorized (credentials invalid/expired); Google Static Maps 403 (API not enabled)

### Site candidate: NOT resolved to parcel/pin
- No delivery pin, no parcel situs, no CAD record
- OSM substation coordinates give POI anchor but project site is a TAP on the line, not at the substation
- **Confidence: LOW — cannot report a lat/lon without derivation**

## Deep Scan — Stage 4: Satellite imagery
- CDSE credentials returning 401 Unauthorized — imagery unavailable
- Google Static Maps API: 403 Forbidden — unavailable
- **No imagery obtained**

## Negative evidence summary
- Zero web/news presence for "Possum Kingdom Solar" or "PK Solar" (strong signal for early-stage or private developer)
- No delivery pin found (gmaps rate-limited — inconclusive)
- No CAD parcel under LLC name (form-based portal inaccessible)
- No IA PDF retrieved (PUCT 402)
- No construction evidence (no imagery)

## 2026-07-21 — Rescan

### Banned-domain contamination check
- Grepped findings.json, dossier.md, log.md, triage.md, triage_findings.json, and all of
  sources/ for `infrasure|futuregrid|cleanview|interconnection\.fyi|gridinfo|ercotqueue|energyacuity`
  — zero hits in any of those files. The only hits were inside the raw transcript JSONL
  (`run_stream_deep.jsonl`), which is the PLAYBOOK TEXT itself (the rule listing the banned
  domains, echoed back as a tool_result), not an actual citation. **No cleanup needed —
  clean.**

### IA PDF already present (from prior run) — read in full
- `sources/2026-07-19_puct_35077-2239_standard-generation-interconnection-agreement-be.pdf`
  is a genuine 56-page executed IA (magic-byte verified `%PDF-1.7`, 1.8MB — not an S3 error
  body). `findings.json` had stale `ia_pdf_retrieved: false` from before this file landed —
  corrected.
- Full-text extraction (pymupdf) confirms INR-in-text: "PK Solar, LLC (Possum Kingdom Solar)
  (24INR0118)" — CONFIRMED per puct.py match criteria.
- Executed/dated **July 30, 2025** (not July 25 as ERCOT queue self-reports — 5-day
  discrepancy, using the document date as authoritative). Filed at PUCT 2025-08-26
  (Control 35077, Item 2239) per Oncor's Rule 25.195(h) cover letter.
- Oncor's cover letter explicitly discloses: "Oncor Electric Delivery has redacted station
  location information, which contain CEII, located in Exhibit C, and certain financial
  information, located in Exhibit D." — explains the blacked-out line in Exhibit C.
- `exhibit.py list` flagged p15/p43 (weak); manually found and rendered the real Exhibit C
  (p33-34, "Halsell Ranch Switch", REDACTED location sentence) and Attachment 1 one-line
  diagram (p47, confirms co-tenant switchyard layout: Possum Kingdom Solar 24INR0118 +
  Possum Kingdom BESS 24INR0375 share one switchyard at Halsell Ranch Switch).
- Financial security (Exhibit E): **$15,508,166** combined Irrevocable Standby Letter of
  Credit for both GINRs, effective on/before 2025-07-01.
- Time Schedule (Exhibit B, p30-31): NTP 2025-07-01; In-Service Date 2027-05-13; Trial
  Operation 2027-05-17; **Scheduled COD 2027-10-29** — matches the ERCOT queue's
  self-reported projectCod exactly (positive cross-check: not a stale/invented queue number).

### spv.py / registries
- `spv.py resolve 24INR0118`: only the puct-index candidate (PK Solar, LLC — already
  confirmed above). No EIA-860M hit.
- `ch313.py resolve 24INR0118`: negative on exact project-name match — BUT
  `ch313.py resolve --name "PK Solar"` found **agreement #1728**: "PK Solar, LLC f/k/a Novis
  Renewables, LLC", Graford ISD, applied 2022-03-14. **This overturns the task's assumption
  of a structural Ch.313 negative** — the project actually entered the pipeline in 2021-2022
  (screening_started 2021-09-13 lines up with the Ch.313 app's "applied 9/1/2021 to ERCOT"
  statement), well before the Sept-2023 sunset, not as a 2024 entrant.
- Downloaded and read the full Ch.313 packet: original application (43pp, magic-byte
  verified), original agreement (44pp), 2026 amendment application (5pp), 2026 amendment
  agreement (3pp) — all genuine PDFs, all saved to sources/ with ISO-dated names.
- Application Checklist Item #4 (p16) contains the money quote: "The applicant applied on
  9/1/2021 to ERCOT and has received the following GINR number: 24INR0118. This project may
  have been known by Possum Kingdom Solar in past media reports, investor presentations..."
  — this is a SECOND independent document (beyond the IA) that states the INR verbatim.
- Developer chain resolved: Novis Renewables, LLC (2022 applicant; Jonathan Koch, President;
  Grant Huber, Development Manager) → renamed **PK Solar, LLC**, now administered by
  **Nadara Development US, LLC / Nadara North America, Inc.** (Thomas Leahy, Authorized
  Signatory/CFO; John Lichtenberger, Chief Development Officer; Erin Michelle Lunsford),
  1 Bridge St Suite 11, Irvington, NY 10533 — matches the IA's notice address exactly.
  Amendment notarized 2025-12-16 in Westchester County, NY (consistent with Irvington HQ).
  Ch.313 agreement is STILL being actively amended as of 2026-03-05 — strong currency
  signal this is a live, managed project.
- Ch.313 Checklist Item #11 ("Maps") delivered actual MAP EXHIBITS — see
  `sources/SITE_DERIVATION.md` for the full site-resolution chain. Also gives project scope
  context: original 2022 concept was ~305 MWac / ~2,500 acres leased across Jack + Palo
  Pinto Counties (100% in Graford ISD, 65% Palo Pinto Co / 35% Jack Co) — since refined
  down to the built 262.22 MW / 68-inverter design in the 2025 IA.
- `ch312.py resolve 24INR0118` / `--name "PK Solar"` / `--county Jack` / `--county "Palo
  Pinto"`: all NEGATIVE (weak — CAD-submitted annual registry, incomplete coverage).
  Consistent with the project's incentive already being covered by Ch.313 (no double-filing
  expected).
- `eia_history.py 24INR0118 --write`: NOT in EIA-860M (TX slice) — negative, no plant/entity
  match by name or county+prime-mover+MW. Logged, no eia_history.json written (tool does not
  write on a pure miss).

### Site resolution — see sources/SITE_DERIVATION.md
- Full chain: Ch.313 map exhibit (reinvestment-zone map, landmark "Marluc Bella Vita Ranch")
  → WebFetch of the ranch's own site (lakegodstone.com) → address "4636 Halsell Ranch Road,
  Graford, TX 76449" → matches the IA Exhibit C's redacted switch name "Halsell Ranch
  Switch" → Overpass/OSM query for `name~"Halsell"` → "Halsell Ranch Road" (TIGER,
  tiger:county=Jack,TX) + "Halsell Ranch Cemetery" (**GNIS feature_id 1337264**) at
  **33.0318 N, -98.2947 W**. Three independent public records converge — no single rung
  was sufficient alone (IA coordinates redacted as CEII; Ch.313 map has no lat/lon
  graticule printed). Confidence: high, but NOT parcel-precise (~1km-radius anchor).
- Nominatim/Census geocoder attempts on the literal street address ("4636 Halsell Ranch
  Road...") returned zero matches (too rural for those geocoders) — Overpass/TIGER was the
  path that worked. Logged as a tool-choice finding for future rescans of rural sites.

### Imagery — s2aws.py chips at 33.0318, -98.2947 (3.5km buffer, 20-day window, max-cloud 25)
- All 5 requested dates returned a scene within the window and under the cloud cap
  (4.4%, 18.3%, 23.4%, 0.4%, 2.1%). No re-fetch needed — none cropped/seam-clipped/cloud-
  ruined at the anchor (2025-07-19's 18.3% cloud sat in the SE corner of frame, not over
  the anchor).
- 2024-07-12, 2025-07-19, 2026-02-02, 2026-05-03, 2026-07-07: all five frames show
  essentially IDENTICAL rangeland/ranch-track land use. **No grading, no panel rows, no
  laydown yard, no construction of any kind** at the resolved anchor through the latest
  clear acquisition (2026-07-07).
- Checked `data/eia_generator_tx.parquet` (latest reportDate 2026-05-01) for Jack/Palo
  Pinto County plants before attributing any array: found **Hecate Energy Longhorn Solar
  LLC** (entity: Repsol Renewables NA), 650 MW, **(OP) Operating**, at 33.04417 N,
  -98.34052 W — ~4.5 km WEST of the site anchor, just outside the narrow 7km chips.
  Fetched a dedicated probe chip there (scratch only, not saved to project imagery/) to
  confirm its distinctive panel-row grid IS visible at this Sentinel-2 resolution — this
  rules out both (a) missing real construction due to resolution limits, and (b)
  misattributing the neighbor's array to 24INR0118.
- Fetched one supplementary WIDE frame (6.5km buffer, centered 33.00/-98.31, latest date)
  covering the full mapped reinvestment zone from Marluc Bella Vita Ranch (north) down
  past FM 337 (south) in one image, specifically to rule out construction starting at an
  extremity outside the narrow chips' footprint. Longhorn Solar's grid is clearly visible
  in the western third of this wide frame (confirms imagery efficacy); the Possum Kingdom
  Solar zone (eastern two-thirds) shows no construction anywhere.
- **Construction verdict: NOT STARTED** as of 2026-07-07. Given IA Exhibit B's own NTP
  date (2025-07-01, over a year before this rescan) and In-Service Date (2027-05-13, ~10
  months away), this is a genuine schedule-risk finding, not a data gap — reinforces the
  existing high-drift-risk COD assessment (independent estimate nudged from 2028-Q3 to
  2028-Q2/Q3 given the imagery evidence).
- Also flags the ERCOT queue's own `construction_start_reported` (2025-05-01) /
  `construction_end_reported` (2026-05-08) milestone fields as unreliable for this
  project — both dates have passed with zero imagery evidence of activity.

### findings.json / dossier updates
- Rewrote `site`, `developer`, `interconnection.contractual_schedule`, `satellite`,
  `cod_assessment`, `could_not_determine`, `comparable_projects`; added new `tax_incentives`
  top-level section; added `site.map_artifacts`. Confidence raised low → medium-high.
  Verdict stays `real_early` (real, administratively active, financially secured — but
  construction not yet visible).
- Wrote `sources/SITE_DERIVATION.md` (full provenance chain, standalone).
