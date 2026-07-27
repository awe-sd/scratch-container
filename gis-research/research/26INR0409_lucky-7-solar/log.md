# Triage log — Lucky 7 Solar (26INR0409)

T1 start
- queue_history: 28 snapshots 2024-03-01 → 2026-06-01; 2 COD changes
- COD drift: 2026-07-01 → 2027-09-04 → 2027-09-20 (current)
- Milestones: screening complete 2024-06-19, FIS approved 2025-08-08, IA signed 2025-08-13
- No construction start/end, no energization/synchronization/COD approved
- Capacity ~stable 100.6–101.35 MW
- T1 complete (2 tool calls)

T2 start
- gmaps.py: persistent 429 Too Many Requests across all 4 queries — API rate-limited, T2 budget exhausted (3 attempts + 1 retry = budget spent)
- pins_found: 0 (blocked)
- T2 complete (4 tool calls used)

T3 start
- DDG: 403 blocked on both queries
- Bing: "Lucky 7 Solar Texas Hopkins County", "Lucky 7 Solar LLC ERCOT", "Lucky 7 Solar Sulphur Springs" — all returned zero relevant results
- No news, no developer name, no LLC registration info found
- news_found: false
- T3 complete (5 tool calls used)

T4 start
- PUCT Interchange interchange.puc.texas.gov: 402 on all direct API queries (FilingParty, description); Bing site: search returned CAPTCHA block
- ia_found: false (portal blocked, not confirmed negative — IA signed date 2025-08-13 in queue data confirms IA exists, just not retrieved here)
- T4 complete (6 tool calls used, budget exhausted)

T5 start
- TX Comptroller Ch.313: portal returned overview page only (no county-filtered data accessible via WebFetch); Bing search returned no results for "Lucky 7 Solar" + Ch.313
- JETI registry: Bing search returned no relevant results for Lucky 7 Solar or Hopkins County solar JETI
- Note: project entered queue 2024-03-01 (post-2022), so Ch.313 not applicable; JETI miss is normal for a project this early-stage
- abatement_found: false (normal)
- T5 complete (4 tool calls used)

T6 start
- Site candidate: POI references "2464 CASH SWITCH" — Cash is a small community in Hopkins County (~33.28°N, 95.73°W); confidence LOW (infrastructure inference only, no pin)
- cdse.py chips: 401 Unauthorized — ~/.config/gis-research.env contains only example/placeholder credentials, not real CDSE creds
- Imagery blocked — CDSE auth not configured
- construction_visible: false (no imagery retrieved)
- T6 complete (3 tool calls used)

T7 start
- triage_findings.json written
- triage.md written
- T7 complete
- Total turns used: ~22

## Deep scan D0-D1 — 2026-07-20

D0: findings.json skeleton written (all keys null).

D1: `exhibit.py scan` on the on-disk IA PDF (sources/2026-07-19_puct_35077-2241_...pdf, PUCT 35077-2241)
flagged pp14,30,31,40 as exhibit candidates; ran `exhibit.py sheet` → 13 tile sheets + index. Read
sheets 01,02,04,08,10,12,13 (7 of 13 — under the 6-full-frame satellite cap, these are doc tiles not
sat frames).

KEY FACTS FROM IA (PUCT Control 35077, filing 2241, filed 2025-08-26, Oncor cover letter):
- Filing cover letter (sheet01, p3) explicitly confirms: "Standard Generation Interconnection Agreement
  between Oncor Electric Delivery Company LLC and Lucky 7 Solar Farm, LLC (26INR0409), dated August 13,
  2025" — **rung-0 exact INR match, CONFIRMED tier**.
- SPV legal name: **Lucky 7 Solar Farm LLC**. Signed by Sabah Bayatli, President, 8/12/2025; address
  "8000 IH-10 West, Suite 201, San Antonio, TX 78230"; email sbayatli@ocienergy.com (sheet10, Exhibit D).
  → developer is **OCI Energy** (San Antonio-based solar developer) — this is a NEW finding not in
  triage (triage said "no LLC/developer identity found").
- Oncor signed by Jim Greer, EVP and COO, 8/13/2025.
- POI (Exhibit C, sheet08 p31): "Point of Interconnection is located in Hopkins County, Texas, at the
  **Brashear Switch** in TSP's Sandy Ranch Switch - Cash Switch 345kV transmission line." Exact switch
  coords redacted as CEII (black bar). Brashear is a real named place in Hopkins Co, TX — upgrades triage's
  low-confidence "Cash community" guess to a MUCH stronger lead: search around Brashear, TX first.
- Generating units (Exhibit C item 4, sheet08 p31): 29 solar inverters, Power Electronics FS4010, 4.01 MVA
  each, gross 116.29 MVA, dispatched 101.8 MW at generator terminals / 100.8 MW at 34.5kV bus — matches
  queue capacityMw 101.35 MW closely.
- Exhibit B Time Schedule (sheet08/10, pp28-29):
  - NTP/security date: Sept 19, 2025
  - In-Service Date: **May 13, 2027**
  - Scheduled Trial Operation: **May 23, 2027**
  - **Scheduled Commercial Operation: September 20, 2027** — matches queue COD claim EXACTLY.
  - Generator to notify TSP of lat/lon+KMZ of solar panel units by Nov 5, 2026 — panel layout not yet
    finalized as of signing (early-stage indicator).
  - Access road + Brashear Switch grading/drainage design complete by Apr 13 2026, construction complete
    Aug 14 2026 — i.e. per contract, dirt/grading work is NOT expected to start until ~2026 mid-year.
- Exhibit E Security (sheet10, p49): Irrevocable Standby LC required **$19,290,074**, effective on/before
  Sept 19, 2025. Single tranche, no amendments on file (only 1 IA doc, no amendment filings found in
  sources/).
- Exhibit C switchyard equipment list (sheet10 p37) confirms "Brashear Switch" again as the substation
  name; relay panel list also references "Cash Switch line" and "Sandy Ranch Switch line" as the two
  345kV lines meeting at Brashear — consistent with queue POI text "Tap 345kV 2621 Sandy Ranch Switch -
  2464 CASH SWITCH".
- No parcel/boundary map exhibit found in this IA (Attachment 1 to Exhibit C, the one-line diagram
  referenced in item 6a, was not captured as an image — text-only SCADA/comms diagrams only, sheet12).
  No site plan / KMZ attached (not due until Nov 2026 per Exhibit B) → **no map_artifacts available from
  IA at this stage**; site must be derived from POI text (Brashear Switch) + EIA coords, not a parcel map.
- Only ONE IA document on disk (original, no amendments) — contractual_schedule will have 1 document row.

## D2/D3 — 2026-07-20 (site + construction proof)

- gmaps.py places: 429 Too Many Requests on all 3 queries ("Lucky 7 Solar", "...construction Brashear",
  "Brashear Switch Hopkins County") — same rate-limit as triage. Negative evidence, moved on.
- cdse.py chip/chips subcommands hit `_openeo_result` — during this run another fleet worker hot-patched
  cdse.py to add a fleet-wide processing lock + backoff (comment cites Hoyte 23INR0235 2026-07-20 capacity
  incident); chip call now queues behind other agents' jobs (submitted, running in background).
- **tceq.py resolve --county Hopkins --keyword "Lucky 7" --storm → HIT.** ACTIVE construction-stormwater
  NOI (TXR1503YB), regulated entity "LUCKY 7 SOLAR FARM", physical address **2854 FARM ROAD 3389, BRASHEAR,
  TX 75420-6021**. Principal/EPC: **Signal Energy, LLC** (CN602963365). Affiliation begin date
  **2026-04-27**, status ACTIVE as of query. This is THE construction-started proof (Cachena/Clear Fork
  pattern) — dirt-moving authorized/underway since 2026-04-27, ~4 months before this research date
  (2026-07-20). Full record saved via direct SoQL query to data.texas.gov dataset tzyg-j7q4 (Coastal & East
  Texas Central Registry) — not yet saved as a file artifact; will save JSON to sources/.
  Address is in BRASHEAR, TX — confirms/tightens the IA POI text ("Brashear Switch") independently. This
  is a strong, INDEPENDENT (non-IA) confirmation of both site (Brashear) and construction timing.
- Site candidate lat/lon: EIA-860M plant coords 33.082, -95.721 (~1.8 km from Brashear townsite center per
  gazetteer estimate) — treating as best available numeric coordinate pending imagery confirmation; the
  storm-NOI address (2854 FM 3389, Brashear) is the independent cross-check anchor once geocoded.
- Saved TCEQ storm-NOI JSON record as sources/2026-07-20_tceq_storm-noi-TXR1503YB-lucky7solarfarm.json.
- **search.py "Signal Energy Lucky 7 Solar Hopkins County Texas" → 5 hits, ALL non-banned, HIGH VALUE:**
  resolves the full ownership chain, something triage completely missed ("no LLC/developer identity found").
  1. Sidley Austin press release (2025-08-18): "Sidley Represents OCI in Sale of Texas Utility-Scale Solar
     Project 'Lucky 7' to Sabanci Renewables" — OCI Energy (original developer) SOLD Project Lucky 7 Solar
     (100 MWac/130 MWdc, Hopkins County TX) to **Sabanci Renewables**; project "will now move forward to
     construction and operation under the leadership of Sabanci Renewables." Saved:
     sources/2026-07-20_sidley_oci-sale-lucky7-sabanci.html. Sale closed ~1 day before the IA was executed
     (IA signed 8/12-13/2025) — explains why the IA signatory (Sabah Bayatli, OCI) still appears as
     President even though beneficial ownership had just transferred/was transferring.
  2. constructionreviewonline.com (2026-01-27): "Sabanci Advances 256 MW Lucky 7 and Pepper Solar
     Projects" — Sabanci Renewables (US subsidiary of Turkish conglomerate Sabanci Holding) selected
     **Signal Energy as EPC** for Lucky 7 (Hopkins Co, ~130 MW DC) + Pepper Solar (McLennan Co, ~126 MW DC).
     Module supplier: Waaree Solar Americas (bifacial hail-resistant, 288 MWp for both sites). Target
     COD: **2027** (matches queue). Sabanci's US portfolio context: Cutlass II operational (272 MW),
     Oriana Solar under construction (232 MW); goal 3 GW in US by 2030. Saved:
     sources/2026-07-20_constructionreviewonline_sabanci-lucky7-pepper.html.
     **This EPC/date lines up exactly with the TCEQ storm NOI** (Signal Energy, coverage begin 2026-04-27,
     ~3 months after EPC selection) — independent corroboration across 2 unrelated sources.
  3. sabanciclimatetech.com project profile page + pv-magazine-usa.com (2026-03-02, "Sabanci Renewables
     taps Empact to de-risk 286 MW Texas solar portfolio") also saved for further detail (not yet read).
- Updated llc_chain: added Sabanci Renewables (current owner/developer post-sale) and Signal Energy
  (EPC, confirmed 2 ways: TCEQ NOI + construction press).
- **sabanciclimatetech.com project profile (the DEVELOPER'S OWN project page for Lucky 7) — extremely
  decisive, saved sources/2026-07-20_sabanciclimatetech_lucky7-project-profile.html:**
  - "Final Notice to Proceed" (FNTP): **12 Dec 2025**
  - COD: **Q3 2027** — matches queue claim 2027-09-20 exactly (Q3)
  - Capacity: 130 MW DC / 100 MW AC — matches queue 101.35 MW / IA 100.8 MW AC closely
  - Site Control: **Completed**
  - QSE: TNSK
  - Modules: Waaree (confirms construction-review article)
  - EPC: Signal Energy (3rd independent confirmation: TCEQ NOI + press + developer's own page)
  - Inverters: **SMA** — NOTE: this differs from the IA Exhibit C spec ("Power Electronics FS4010"
    solar inverters) signed 2025-08-13; may reflect an equipment change after Sabanci's acquisition, or
    one source is stale. Flagging as a minor unresolved discrepancy, not fatal to the real-project case.
  - Trackers: Game Change
  - PPA: "Under exclusivity" — not yet signed as of page-read date
  - Milestone table confirms "Interconnection Agreement Has been signed with Oncor"
  - Community-impact section: project created 300+ construction jobs, 3 permanent jobs, powers ~20,000
    homes — consistent with a project the developer considers active/under construction, not paper.
  This single artifact independently corroborates: capacity, COD quarter, EPC, module/tracker vendors,
  FNTP date, and site control status — from the CURRENT OWNER's own investor-facing page, not a 3rd party
  aggregator. Combined with the ACTIVE TCEQ storm NOI (construction authorized 2026-04-27, ~4.5 months
  after FNTP), this is about as strong a "real_active" case as this system's evidence ladder can produce
  without a parcel map or satellite confirmation.
- Hopkins County Appraisal District (hopkinscad.org) results page is a JS/DataTables front-end over an
  AJAX API, not a query-param search — a raw curl of `/results/?q=lucky+7` returns the empty page shell,
  no rows. Not pursued further (would need to reverse-engineer the AJAX endpoint); no CAD parcel lookup
  performed. Logged as negative evidence / not attempted rather than a 0-hit search.
- cdse.py chip (33.078,-95.712, 3km buffer, 2026-07-01) succeeded after fleet-lock queueing:
  imagery/s2_2026-07-01_wide.png — AWS COG scene 2026-07-11, cloud 9%. Shows an irregular tan/graded
  polygon ~1-1.5 km across straddling the road grid, with internal light-colored access-road striping —
  visually consistent with solar-site clearing/grading (PLAYBOOK signature), NOT yet the uniform dark
  module-block signature of installed racking. Also pulled a tight 2km chip (imagery/grid/s2_c0_0.png)
  centered on the EIA coords, same scene, same footprint visible in the SE quadrant of that frame.
  Site refined from EIA point (33.082,-95.721) to the graded-polygon centroid (~33.078,-95.712), ~1km ESE
  — consistent with "EIA coords are a candidate, not truth" per playbook D2.
  Monthly timelapse (2024-07 to 2026-07, 2.5km buffer) launched to bracket first_activity_seen against
  the TCEQ NOI's 2026-04-27 coverage-begin date — FAILED after 3 retries (RemoteDisconnected, CDSE fleet
  capacity exhausted; many other concurrent deep-scan workers observed hitting cdse.py at the same time
  via `ps aux`). Per cdse.py's explicit "do NOT loop" exit instruction, not retried; logging as negative
  evidence. Trying one cheap single-chip baseline instead (2025-06-01, pre-FNTP) rather than a full
  timelapse job.
- Baseline chip (2025-06-01, 3km buffer) ALSO failed — timed out at 280s under the same fleet-wide CDSE
  processing-lock contention (many other deep-scan workers' cdse.py calls visible via `ps aux` at the
  same time). Stopping imagery pursuit here: 2 full-size frames already read (imagery/grid/s2_c0_0.png,
  imagery/s2_2026-07-01_wide.png), within the ≤6-frame cap, both showing the same graded polygon on the
  2026-07-11 scene. No pre-construction baseline frame obtained, so first_activity_seen in findings.json
  is sourced from the TCEQ NOI date (2026-04-27), NOT from an imagery bracket -- this is stated explicitly
  as a limit in the dossier. Moving to synthesis; imagery evidence is sufficient (construction-stage
  visual + 2 independent non-imagery confirmations: TCEQ NOI, EIA-860M "under construction ≤50%") without
  further CDSE calls given fleet-wide capacity exhaustion.
