# Triage log — Blue Sky Sol (22INR0455)

## T1 start
- queue_history.py output: 67 snapshots, 5 reported-COD changes
- IA signed: 2022-02-01
- Meets 6.9(1): 2022-02-07
- Meets all 6.9: 2023-07-31
- Construction start/end: none
- COD drift (5 changes):
  - 2022-12-15 (held 2020-12-01 → 2021-12-01)
  - 2023-11-24 (held 2022-01-01 → 2023-01-01)
  - 2024-06-15 (held 2023-02-01 → 2023-08-01)
  - 2025-02-15 (held 2023-09-01 → 2024-12-01)
  - 2027-04-23 (held 2025-01-01 → 2026-02-01)
  - 2027-12-31 (held 2026-03-01 → 2026-06-01) ← current
- Project is ~5.5 years in queue; no construction milestones achieved; IA and full 6.9 met

## T2 start
- gmaps.py: HTTP 429 on both attempts (rate-limited); 0 pins found

## T3 start
- DDG: CAPTCHA-blocked on both queries
- Bing: no results for "Blue Sky Sol" + ERCOT/Texas/Crockett County
- TX Comptroller COA: redirected (session-based search, not fetchable)
- No developer name, no news, no press releases surfaced
- news_found: false

## T4 start
- PUCT Interchange: HTTP 402 on all endpoints (FilingParty=, Description=, root) — portal blocked
- No IA filing found via PUCT; queue data already confirms iaSigned=2022-02-01 (milestone achieved)
- ia_found: false (no IA document retrieved, milestone date confirmed via queue only)

## T5 start
- TX Comptroller Ch.313: database not directly fetchable (form/session-based); no Crockett County solar hits confirmed
- JETI registry: page not queryable via WebFetch; project entered queue 2020, so pre-JETI era (Ch.313 deadline was Dec 2022)
- abatement_found: false (inconclusive — databases blocked, not confirmed absent)

## T6 start
- Site candidate: no pin (T2 blocked), no IA map (T4 blocked), no Friends Ranch substation coords found via web
- "Friends Ranch 138kV" substation not locatable from web; Crockett County is ~3,000 sq miles — too large for useful imagery
- SKIP imagery per checklist rule: no site candidate better than "somewhere in county"
- construction_visible: null

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~22
- STOP

## D1 — IA schedule extraction (2026-07-20)
- 3 verified IA PDFs already on disk (triage-era puct.py match pull): 35077-1379 (Original, exec 2022-02-01), 35077-2277 (First A&R, exec 2025-09-17, filed 2025-10-10), 35077-2358 (Second A&R, exec 2025-12-11, filed 2026-01-09). All 3 explicitly quote "generation interconnection request #22INR0455" and name "Blue Sky Solar LLC" as Generator — CONFIRMED, not just probable.
- Exhibit B (Time Schedule) in all 3 is stated as "N months from the date conditions under 4.2/4.3 satisfied" rather than a fixed date; the amendment text carries over "As of the Execution Date of the Original Agreement, Generator hereby provides such written authorization" — i.e. the conditions-satisfied anchor is the Original Agreement's 2022-02-01 execution date, not the amendment's own execution date. Month-counts: Original 24/24/25mo -> ISD/TOD/COD 2024-02 / 2024-02 / 2024-03; First A&R 59/60/62mo -> 2027-01 / 2027-02 / 2027-04; Second A&R 68/69/71mo -> 2027-10 / 2027-11 / 2028-01.
- Exhibit C (Interconnection Details) identical across all 3 versions: "Generator's Blue Sky Substation ... located in Crockett County approximately Five and one Half (5.5) miles east of Ozona, Texas." POI = TSP's first dead-end structure outside Friend Ranch Station fence, terminating a 138kV line from the Blue Sky Substation. 101.2 MW via 29x GE LV5+-1569 solar inverters @ 3.48959 MW each.
- Exhibit C-1 (One-Line Drawing, Second A&R p58, rendered to sources/2026-07-19_puct_35077-2358_second-amended-and-restated-ercot_p58.png) shows "~3.6 mile, 138kV" generator-owned line from Blue Sky Substation to Friend Ranch Station POI — conceptual/not to scale, no lat/lon, but confirms line length order-of-magnitude (~3.6 mi separation between substation and POI).
- Exhibit E (Security): all 3 documents state identical $2,200,000 LC/guaranty — the amendments deferred schedule ~4x total (2024-03 orig COD -> 2028-01 latest contractual COD) WITHOUT any financial-security increase. Contrast with Hanson Solar (23INR0086) where LC rose $11.3M->$13.4M with its one amendment — here security is flat despite far larger slippage, a soft paper-project signal (no incremental capital commitment tracking the repeated deferrals).
- NOTE: contractual COD in latest signed IA (2028-01, i.e. 71mo from 2022-02-01) does NOT match queue-reported COD (2027-12-31). Off by ~1 month — negligible, effectively the same target, likely reporting/rounding difference between exact month-count and queue's date field.
- p70 of Second A&R (image-only per exhibit.py scan) = blank "Marked Tariff Record" divider page, not a map — logged as negative finding, no site map exists in these IA exhibits beyond the conceptual one-line drawing.

## D2 — Site pinpoint in progress (2026-07-20)
- gmaps.py places: HTTP 429 (rate-limited) on 2 attempts, same as triage — negative evidence, tool exhausted for this run.
- OpenGridMap transnet-models csv_nodes.csv (GitHub, not a queue-tracker/banned source): only match for "Friend*" is "Friendswood Substation" near Houston (CenterPoint) — false positive, not this site. No node near Ozona/Crockett Co in that dataset.
- search.py "\"Friends Ranch\" substation Crockett County Texas" surfaced hometownlocator.com listing "Friend Ranch (in Crockett County, TX)" as a named GNIS locale — confirms the place name is real and matches IA Exhibit C's "Friend Ranch Station" naming, but the site itself (individual coordinates) wasn't retrievable — hometownlocator page had no coordinate data in fetched text; USGS GNIS gaz-service and legacy apex endpoints both returned 503/403 (service down), logged as negative/blocked.
- Site estimate anchor: IA Exhibit C states verbatim (all 3 signed IA versions) "Generator's Blue Sky Substation... located in Crockett County approximately Five and one Half (5.5) miles east of Ozona, Texas." Ozona, TX town coordinates confirmed via search.py (travelmath/latitude.to): 30.7053N, -101.2025W. Computed estimate 5.5mi due east: 30.7096, -101.1108 (bearing assumption: due east, since IA gives no bearing detail beyond "east"; this is a coarse estimate pending imagery confirmation, NOT a county centroid — anchored to a named town + stated distance from a primary legal document).
- Pulling Sentinel-2 6km-buffer wide chip at this estimate (2026-06-01) to orient before tight grid search.
- cdse.py chip call (2026-06-01, 6km buffer) failed: "RemoteDisconnected — capacity backoff" x3, tool self-aborted with "CDSE CAPACITY: do NOT loop; log as negative evidence and move on." Negative evidence logged; will retry once later in the run, not looped.

## D3 — Gap-fill: SPV/registries (2026-07-20)
- spv.py resolve: no EIA-860M hit (confirms triage's not_in_eia), only puct-index hits already on disk (3 IA filings, all already downloaded). No independent developer/parent name surfaced via spv.py.
- ch313.py resolve 22INR0455 / --name "Blue Sky Solar" / --name "Blue Sky": all NEGATIVE against the local cached ch313_agreements.json (740 rows, fetched 2026-07-19).
- BUT: manually inspected the local JSON — app_no sequence has a GAP at 1821 (1820 and 1822 present, 1821 absent) — the local cache is missing this one row. search.py "comptroller ch313 1821 Blue Sky Solar Crockett" confirms it exists on the live Comptroller site: "Crockett County Consolidated Csd No. 1821, Blue Sky Solar, LLC" (agreement-docs-details.php?id=1821), with PDFs at assets.comptroller.texas.gov/ch313/1821/1821-crockett-blue-agmt.pdf (agreement) and .../1821-crockett-blue-appamend1.pdf (application amendment 1). This is a REAL Ch.313 tax-abatement filing for this project — ch313.py's local cache is stale/incomplete, not a true negative. Direct curl + WebFetch both got HTTP 403 on assets.comptroller.texas.gov PDFs (bot-blocked); comptroller agreement-docs-details.php?id=1821 via WebFetch returned "no record found" (likely JS-rendered page, not fetchable via simple HTML fetch). Will retry PDF fetch with alternate method.
- tceq.py resolve --county Crockett --storm: no "Blue Sky" hit among Crockett Co storm-water NOIs; only 4 unrelated active AIR facilities (oil/gas SWD, pipeline, battery storage, legacy gas plant) — none are Blue Sky Solar. Construction-started proof via TCEQ storm-water = NEGATIVE (no active NOI found for this project).
- search.py "Blue Sky Solar LLC Crockett County Texas construction": surfaced North American Clean Energy article — "UKA North America Executes 15-Year PPA with Google for Blue Sky Solar Project in ERCOT West" — first non-filing evidence of a real developer (UKA North America) and offtaker (Google). Need to fetch full article next.
- Ch.313 app #1821 agreement/appamend1 PDFs at assets.comptroller.texas.gov: confirmed HTTP 403 via curl (2 UA variants), WebFetch, AND ch313.py's own throttled `get()` helper — genuinely blocked at the CDN/WAF level for this asset path (not a client misconfiguration). Comptroller detail page (agreement-docs-details.php?id=1821) via WebFetch returned "no record found" (JS-rendered SPA, not scrapeable via simple fetch). STOPPING further retry attempts per playbook discipline; treating existence-but-inaccessible as: Ch.313 filing CONFIRMED to exist (via search-engine index metadata: title "BLUE SKY SOLAR, LLC TEXAS TAXPAYER ID #..." + "App# 1821-Crockett County CCSD-Blue Sky Solar, LLC" for the amendment) but full text NOT independently obtained — a genuine gap, logged as such in findings.json rather than fabricated.
- Fetched nacleanenergy.com article directly via curl (browser UA) after WebFetch got 403 — saved sources/2026-07-20_nacleanenergy_uka-google-blue-sky-solar-ppa.html. KEY FACTS (published 2026-02-23): "UKA North America, the U.S. subsidiary of UKA Group, has executed a 15-year power purchase agreement (PPA) with Google for the Blue Sky Solar Project, a 100 MWac utility-scale solar facility located in Crockett County, Texas." Project "is in late-stage development and is planned to come online in late 2027" — matches queue COD 2027-12-31 and latest signed IA contractual COD (2028-01) closely. Creates 150-200 construction jobs; transaction facilitated by LevelTen (PPA broker, corroborates real deal, not vaporware).
- Fetched energycentral.com M&A article (curl, browser UA) — sources/2026-07-20_energycentral_uka-blue-sky-sale-2023.html. Dated ~May 2023 (article says "Interested parties have until June 16, 2023"). KEY FACTS: "UKA Group's North American subsidiary seeks to sell its 101.2 MW Blue Sky solar project in Texas" via Fractal Advisory; "located in Crockett County, within Crockett County Consolidated Common School District" (ties directly to the Ch.313 app #1821 filer "Crockett County Consolidated Csd"); "will host 240,732 photovoltaic panels and 29 central inverters" (29 inverters matches IA Exhibit C exactly: "29 General Electric/LV5+-1569 Solar Inverters"); "currently in the ready-to-build stage, with commercial operation expected by mid-2024" (2023 snapshot — badly missed, consistent with the queue's own COD slip history); cites "UKA Group's regulatory filings with the Texas Comptroller of Public Accounts" for a "$85mn" total investment figure — independent confirmation the Ch.313 filing is real and substantive, not just a name match.
- SYNTHESIS: UKA Group (German developer, ~60 grid-connected assets, ~14GW pipeline per the article) = the parent/developer behind Blue Sky Solar LLC, confirmed by 2 independent trade-press sources 3 years apart (2023 sale attempt "ready-to-build" -> 2026 Google PPA "late-stage development"). The project appears to have NOT sold in 2023 (still branded "UKA's Blue Sky" in the 2026 PPA announcement) — UKA retained and continued developing it themselves rather than selling. This is the single most decisive reality-signal found: a signed 15-yr PPA with Google, brokered via LevelTen, announced 2026-02-23.

## D2/D3 — CDSE imagery: hard blocker (2026-07-20)
- 2 separate cdse.py chip attempts (2026-06-01, 6km buffer, lat/lon estimate) both failed with "RemoteDisconnected — capacity backoff 15s/45s/120s" then self-aborted per the tool's own guidance ("do NOT loop"). Observed via `ps aux` that OTHER concurrent sessions in this container are also running CDSE capacity-probe loops against different projects (e.g. 23INR0056) — this is a fleet-wide CDSE outage/capacity issue right now, not specific to this project or this lat/lon. STOPPING retries per playbook + tool guidance; no satellite imagery obtained this run. Construction-stage verdict below is based on documentary evidence only (IA + news + Ch313 lead), NOT independently confirmed by imagery — flagged as a limit in the dossier.
- Crockett CAD (crockettcad.com and crockettcad.org): both are session/JS-based property-search portals (True Automation-style), not scrapeable via curl/WebFetch without a browser — consistent with playbook's expectation that some CAD portals block automated fetches. No owner-name parcel search performed; logged as inconclusive, not a true negative.

## Checkpoint (2026-07-20) — findings.json updated
- gmaps.py places: still HTTP 429 on retry — logged, moving on. Will attempt gmaps.py staticmap for dossier illustration only (does not require Places API success).
- Final CDSE retry (after ~15min gap): still RemoteDisconnected x3, self-aborted. Confirmed genuine outage, not transient — stopping imagery attempts for this run.
- gmaps.py staticmap: HTTP 403 "Maps Static API is not enabled for this key" — infra/API-key config issue (not a data finding), separate from the Places 429s. No site map image producible this run via gmaps tooling.

## D5 — Deterministic wrap-up (2026-07-20)
- queue_history.py: confirmed 67 snapshots, 5 reported-COD changes (unchanged from triage; timeline.md refreshed).
- eia_history.py --write: "NOT in EIA-860M (TX slice)" — confirms triage's not_in_eia; consistent with a project that per the IA's own timeline has never reached In-Service Date (EIA-860M generally tracks constructing/operating units).
- build_brief.py 22INR0455: wrote brief.html (10 KB, 0 images, 9 sources) — 0 images reflects the no-imagery-this-run limitation, honestly propagated.
- build_index.py: refreshed research/index.json + INDEX.md (171 projects).
- Final findings.json validated as well-formed JSON. Dossier + log + findings all consistent: real_early verdict, site medium-confidence text-derived estimate, COD 2028-Q2/high drift risk.
- STOP — D0-D5 complete.

## Second-pass user review (2026-07-20)
- OSM/Overpass: "Friend Ranch Substation" found by exact name (138kV/69kV), 3.55mi due east
  of Ozona -- matches IA Exhibit C's POI text and, combined with the ~3.6mi generator gen-tie
  (Exhibit C-1), corroborates the existing 5.5mi-east-of-Ozona site estimate. Confidence
  upgraded medium -> high.
- AWS Open Data chips (s2aws.py) fetched 2022/2024/2025/2026 at the site: unchanged rural
  I-10 frontage scene, no solar array in any year. Frame partially clipped by a Sentinel-2
  tile edge (14RKU) -- known single-scene limitation, visible portion is clean.

## Ch.313 recovery + boundary-framed imagery (user-flagged, 2026-07-21)

- User flagged the ch313 PDFs as corrupted: the two 111-byte files were S3 AccessDenied
  XML bodies saved with .pdf names (failed-download artifacts, now deleted).
- Root cause found: the app-1821 filenames the prior run guessed were CORRECT, but the
  live Comptroller CDN has since PURGED the /ch313/1821/ folder (the sibling /1785/
  fetches fine today). All five documents recovered from the Wayback Machine
  (agreement 7.1MB, application 9.0MB, appamend1 1.4MB, cert 1.2MB, 2023 SLA report
  2.4MB) -> sources/2026-07-21_wayback_ch313-*.pdf.
- The recovered application carries the Tab-11 PROJECT BOUNDARY map (p22 rendered):
  boundary north of I-10, SW tip at the substation pad ~5.5mi E of Ozona -- consistent
  with IA Exhibit C text and the OSM-verified Friend Ranch Substation. Site fix moved
  from the substation-end estimate to the boundary-bbox center (30.744,-101.065).
- Imagery reframed per user request ("current image is cropping out the complete plant
  site"): 4-date series re-fetched at the boundary center (11x8km frames); one 2026-07-20
  scene rejected for tile-seam clipping (14RLV edge), replaced by the full-frame
  2026-07-10 wide chip. Whole boundary interior: rangeland + oil-lease pads only, no
  construction in any year. Verdict unchanged (real_early, unclear_no_construction_visible).
