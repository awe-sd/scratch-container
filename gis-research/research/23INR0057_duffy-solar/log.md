# Triage log — 23INR0057 Duffy Solar

T1 start
T1 result: 65 snapshots. IA signed 2023-04-12. Meets 6.9(1) 2023-05-24. COD drifted 3×: 2023-06-01 → 2025-05-31 → 2026-11-01 → 2027-12-31. Capacity: 550.8→545.21→502.46 MW. No FIS approved, no construction milestones, no energization/sync. Project has IA — real development signal.

T2 start
T2 result: gmaps.py returned HTTP 429 on both attempts (rate-limited). Budget exhausted. No pins found — normal for triage.

T3 start
T3 result: DDG blocked (CAPTCHA). Bing: no results for "Duffy Solar" + Matagorda/ERCOT/Texas. No developer name, no news, no LLC registration surfaced. Project name too common (singer "Duffy" noise). No pages saved to sources/.

T4 start
T4 result: interchange.puc.texas.gov returns HTTP 402 for all endpoints (session/auth required). Bing site: search returned no indexed results for "Duffy Solar". No IA PDF retrieved. Note: queue data shows iaSigned=2023-04-12, so an IA exists in ERCOT's records — PUCT filing would need authenticated portal access. No PDF downloaded.

T5 start
T5 result: TX Comptroller Ch.313 database not directly accessible (no downloadable list found at known endpoints, 404 on agreements.php). Bing + Comptroller searches CAPTCHA-blocked or returned no hits for "Duffy Solar" + Matagorda Ch.313. No JETI hits. Note: Ch.313 closed to new applications after 2022 (statute expired), so post-2022 projects like this one (INR 2023) normally use JETI or no abatement — miss is expected. No abatement application found.

T6 start
T6 result: SKIPPED — no site candidate. T2 gmaps blocked (429), T4 PUCT blocked (402), T5 no abatement. POI description gives 345kV WAP→STP corridor in Matagorda County (PTI# 5915-44000 CKT39) but tap point is unlocated along potentially 20+ mile line — not better than "somewhere in county." No imagery acquired.

T7 start
T7 result: triage_findings.json + triage.md written. Turns used: ~23. Deep scan recommended. Key blockers this pass: gmaps 429, PUCT 402, DDG/Bing CAPTCHA.
TRIAGE COMPLETE.

## Deep Scan

DS1: Stage 1 — LLC/developer search
- TX Comptroller COA search for "Duffy Solar": JS-rendered results, not accessible via curl/WebFetch
- EDGAR: HTTP 403 blocked
- OpenCorporates: CAPTCHA blocked
- Nominatim: Wadsworth village located at 28.8327°N, 95.9358°W — POI anchor for WAP substation vicinity
- Stage 1 result: Developer identity NOT established. No LLC registration found via available tools.

DS2: Stage 2 — County records
- PUCT Interchange: HTTP 402 (session auth required) — IA PDF not retrieved
- Matagorda CAD: SSL cert error on matagordacad.org; property search portal unreachable
- Matagorda County commissioners court minutes: PDFs available at matagordatx.gov but are scanned images (CCITTFax), no text layer, no OCR tooling available
- Ch.313/JETI Comptroller database: no direct API or downloadable dataset accessible; Ch.313 expired 2022 (post-2022 projects use JETI); no JETI record found for Duffy Solar
- Stage 2 result: No parcel data, no abatement agreement, no IA PDF retrieved.
- NEGATIVE: No county paper trail found via available tools.

DS3: POI analysis — inferring site location
- POI "Tap 345kV WAP to STP CKT39 (PTI# 5915-44000 CKT 39)" = tap on WAP→STP 345kV circuit 39
- WAP = Wadsworth Area Project substation, near Wadsworth village: 28.8327°N, 95.9358°W
- STP = South Texas Project nuclear plant / switchyard area (~28.80°N, -96.05°W)
- The WAP-STP 345kV line runs roughly E-W through Matagorda County farmland
- Site will be within a few miles of this corridor; starting search at ~28.83°N, 96.00°W (midpoint)

DS4: OSM infrastructure lookup
- Wadsworth Substation (AEP) confirmed at 28.7851°N, 95.9380°W (OSM node)
- STP Switchyard cluster at ~28.799°N, 96.051°W
- CenterPoint 345kV line (2 circuits, id=1060258405) confirmed: runs E-W from 28.8279,-95.8591 to 28.8018,-96.0498 (66 nodes, ~18 km)
  → This is the WAP-STP 345kV CKT39 corridor
- Corridor runs approximately through lat 28.80-28.83, lon -95.86 to -96.05
- Search center for imagery: ~28.812°N, 95.960°W (midpoint)
- No "Duffy" geographic features found in OSM (Matagorda County area)
- NEGATIVE: No companion project LLC or developer name found in SEC EDGAR (0 hits), press releases (0 hits), or pv-magazine

DS5: Developer identity / LLC parent
- TX Comptroller COA: JS-rendered, no direct API result for "Duffy Solar"
- TX SOS SOSDirect: paid ($1/search), not accessible
- SEC EDGAR full-text search: 0 hits for "Duffy Solar"
- PR Newswire: 0 hits for "Duffy Solar"
- NEGATIVE: Developer identity NOT established via available tools. Project has unusually low web presence.

DS6: County records
- Matagorda County CAD (matagordacad.org): SSL cert error, unreachable
- Matagorda County commissioners court minutes: scanned image PDFs (no text layer), OCR not available
- Ch.313/JETI: Ch.313 expired 2022 (no new applications post-2022); no JETI record found
- NEGATIVE: No county paper trail via available tools.

## Stage 3 — Site pinpoint

Starting imagery search along WAP-STP 345kV corridor (~28.81°N, -95.96°W midpoint)
- WAP-STP CenterPoint 345kV corridor confirmed via OSM (id=1060258405): 28.8279,-95.8591 to 28.8018,-96.0498
- No "Duffy" place name in Matagorda County (Nominatim). No delivery pin (gmaps 429/daily quota).
- Site search area: bbox 28.78-28.90, -96.10 to -95.85 (6 grid chips + 3 search chips)

## Stage 4 — Satellite ground truth

Imagery survey across WAP-STP corridor in Matagorda County (March 2026 = clearest available):
- grid_28.80_-95.90_2026-03: undisturbed agricultural land, creek meanders, NO solar
- grid_28.80_-96.00_2026-03: Colorado River visible, farmland on both sides, NO solar
- grid_28.85_-95.90_2026-03: flat coastal plain, mixed pasture/cropland, NO solar
- grid_28.88_-95.90_2026-03: irrigated rice fields, dark ponds/paddies, NO solar
- grid_28.90_-95.85_2026-03: open grassland and cropland, NO solar
- grid_29.00_-95.85_2026-03: green pasture with river, NO solar
- search_28.83_-95.95_2026-06 + search_28.81_-96.00_2026-07: heavy cloud cover, underlying farmland
- s2_2026-07-01_mid (28.812,-95.960): heavy cloud cover, mixed agricultural landscape with NO solar

IMAGERY VERDICT: NO CONSTRUCTION ACTIVITY observed anywhere along WAP-STP 345kV corridor
in March/June/July 2026. Entire 6-grid search area (~18×10 km) shows undisturbed farmland.
A 500 MW solar farm (≥2,000 acres) would be unmistakable at 10 m/px — it is absent.

Note: Could not confirm exact tap point as CEII. Site could theoretically be elsewhere along 
the corridor beyond the grid search, but standard interpretation: no activity visible = 
no construction underway in July 2026, 18 months before claimed COD.

## Stage 5 — Synthesis notes

Key facts:
- IA signed 2023-04-12 (real development signal — this is not a zero-effort paper project)
- No FIS approved (gap — FIS requested Feb 2021, still unapproved as of latest snapshot)
- Meets 6.9(1) achieved 2023-05-24 (passed first completion gate)
- 4 COD slips: 2023-06 → 2025-05 → 2026-11 → 2027-12 (18-month pace of slippage, exactly one slip/year)
- Capacity trimmed 545→502 MW Oct-2024 (often signals scope adjustment, not cancellation)
- No developer ID, no public web presence, no abatement, no news
- No construction visible anywhere in the WAP-STP corridor in 2026-03 imagery
- Project in queue 65 months (since Feb 2021) with IA but no civil/construction milestones

Assessment:
- Real project: IA signed, milestone 6.9(1) met, capacity resized — not paper filing behavior
- BUT: no construction in March 2026 with COD claim Dec 2027 = 21 months to complete 500 MW
  → This schedule is extremely aggressive: 500 MW requires ~18-24 months civil+install
  → No site prep visible → COD 2027-12 is NOT achievable unless broke ground very recently
  → Independent COD estimate: 2029-Q1 at earliest (18-month slip from 2027-12 continuing pattern)
- Drift risk: HIGH — 4 prior slips, no construction visible, FIS still not approved

## Re-run 2026-07-20 (1M budget, user-ordered) — decisive IA/SPV update

RD1: puct.py match with --key "Duffy Project Co" fetched Amendment Two (35077-2516, filed
2026-07-01, effective 2026-07-03) — CONFIRMED (INR in text). Also re-confirmed original SGIA
(35077-2191) and Amendment One (35077-2301).

RD2: Read all 3 IA documents in full (pypdf extract, no OCR needed — all text layers present).
KEY FINDING: Amendment Two Exhibit B sets scheduled Commercial Operation Date = "later of
10/31/2028 or 4 months after TIF In-Service Date" — this SUPERSEDES Amendment One's 2027-12-31
(which is what the ERCOT queue snapshot still reports). The IA amendment itself is 10 months
ahead of what the queue currently shows. This is primary-document COD drift evidence, not an
imagery inference — decisive.

RD3: Amendment Two Exhibit C gives POI = "approximately at 28.85275, -96.0865, Matagorda
County, Texas" — 345kV delivery voltage, matches queue POI text. This is DIFFERENT from the
original 2023 SGIA's POI (28.874002, -96.066461) by ~3.1 km SW — the tap point moved when the
project was rescoped. Prior deep-run's satellite grid (imagery/grid_*.png, centered 28.80-29.00N,
-95.85 to -96.10W) covers this general area but was not tightly centered on either exact POI —
construction verdict from that pass should be treated as unverified near-site, not a confirmed
no-activity at the correct coordinate.

RD4: Equipment/ownership changes tracked across the 3 documents:
- Generator name: "VDA Solar Texas 1, LLC" (original 2023-04-12 signing) -> "Duffy Project Co
  LLC (f/k/a VDA Solar Texas 1, LLC)" (Amendment One, filed 2025-11-10, signed 2025-10-22) ->
  "Duffy Project Co LLC" (Amendment Two, 2026-07-01). Rename/acquisition happened sometime
  between original signing and Oct-2025.
- Inverter vendor: 170x Sungrow SG3600UDMV (540 MW, original) -> 135x Power Electronics HEM
  FS4200M (502.46 MW, Amendment Two) — a full equipment re-spec, not just a capacity trim.
- Financial security: original Exhibit E used a $24.346M Security Estimate / irrevocable LC
  mechanism; Amendments One & Two instead cite only a flat $100,000 CIAC (contribution in aid
  of construction) in Exhibit C — the large-security LC language appears to have been dropped
  in the amended exhibits (could not find a replacement Exhibit E dollar figure in Amendment
  One or Two text — logged as a gap, not assumed zero).
- TSP confirmed as CenterPoint Energy Houston Electric, LLC (not AEP as triage/prior-run notes
  guessed from OSM line ownership).

RD5: findings.json updated with contractual_schedule.documents (3 entries), corrected site
coords (Amendment Two POI), corrected interconnection.tsp, cod_assessment revised to cite the
IA amendment sequence as primary evidence. Verdict raised to confidence "high" given 3 CONFIRMED
signed contracts in hand.

Next: re-chip satellite imagery tightly centered on 28.85275,-96.0865 (Amendment Two POI) before
finalizing construction-stage verdict; run storm/tceq NOI check for VDA/Duffy Project Co
variants per REFRESH_DIRECTIVE lead 2; attempt TX SOS/CAD owner search for both LLC names;
run deterministic wrap-up (queue_history, eia_history, build_brief, build_index).

RD6: CDSE openEO backend returned RemoteDisconnected on every attempt this session (direct
sync-endpoint tests, `chips` CLI with retry/backoff, and a background retry after clearing
the token cache) — token minting itself succeeded (get_token() returned a valid ~2.4KB JWT)
and the base openEO root endpoint (GET /openeo/1.2/) returned HTTP 200, so this is a backend
capacity/availability issue on the /result sync endpoint, not a credentials problem. The
tool's own capacity-backoff logic (15s/45s/120s) exhausted and printed "CDSE CAPACITY:
RemoteDisconnected after retries — do NOT loop; log as negative evidence and move on" —
followed that instruction. NO satellite imagery obtained at the corrected POI this run.
Existing March-2026 imagery in imagery/ remains uncentered on the true site and should not
be used to support a construction verdict at the solar array specifically.

RD7: TX Comptroller franchise-tax JSON API (https://comptroller.texas.gov/data-search/
franchise-tax?name=Duffy%20Project%20Co) returned a clean hit: "DUFFY PROJECT CO LLC",
taxpayerId 32073592530, mailing ZIP 94104 — decisive because this is San Francisco, matching
Linea Energy's HQ, found independently of any press release. (The old triage/deep-run notes
that "TX Comptroller COA JS-rendered, not accessible via curl" were about the COA franchise-
tax-status *search page*; the underlying data-search API is a plain JSON GET and works fine.)

RD8: search.py "\"Duffy Solar\" Matagorda solar project MW" broke the case wide open —
5 hits, 3 banned queue-trackers auto-suppressed:
- Linea Energy official PR (2026-05, San Francisco): Google signed 15-yr 500MW PPA off the
  "3,526-acre Duffy Solar Project" in Matagorda County; Linea Energy sponsored by EnCap
  Investments L.P. / EnCap Energy Transition; "construction to begin Q3 2026", co-located with
  "235 MWac Duffy BESS project, which is currently under construction."
  -> sources/2026-07-20_lineaenergy_official-500mw-ppa-announcement.html
- Bay City Tribune (2026-06-23, independent local news, NOT a Linea channel): confirms same
  500MW/3,500-acre/Google-PPA facts, ADDS "commercial operations targeted for late 2027" and
  describes a community lunch-and-learn (2026-06-29) — the project has an active, visible
  local community-relations program, a strong "real" signal.
  -> sources/2026-07-20_baycitytribune_duffy-solar-community-event.html
- 3 syndications of the same PR (poweralliance.org, datacenterdynamics.com [403, saved partial],
  esgtoday.com [403, saved partial]) — corroborating but derivative.
Note the "\"VDA Solar Texas\"" and "\"Duffy Project Co LLC\" Texas" queries (tried first)
returned pure noise — the decisive query had to include "Matagorda" + "solar project MW", i.e.
searching by SPV legal name alone missed it; the queue/public project name + county was the
key that worked.

RD9: developer PR/news public messaging ("Q3 2026 construction start", "late 2027 COD") is
LESS conservative than the developer's OWN signed Amendment Two (effective 2026-07-03, 3 weeks
before the Bay City Tribune article) which sets legal COD at 2028-10-31. Logged as a 3-way
COD disagreement (queue 2027-12-31 / signed IA 2028-10-31 / developer PR "late 2027") rather
than picked apart — independent estimate in findings.json weights the signed contract.

findings.json fully updated: developer (Linea Energy/EnCap parent, Google offtake), project_area
(3,526 ac, sourced), construction (reframed — BESS confirmed active, solar array unverified by
imagery this run, PR says Q3-2026 start), cod_assessment (2028-Q4 independent estimate, medium
drift risk, 3-way COD disagreement documented), unknowns list narrowed to genuine remaining gaps.

Next: attempt Matagorda CAD parcel search under "Duffy Project Co" / "Linea Energy" owner
names; retry CDSE chip once more if time allows; run deterministic wrap-up (queue_history,
eia_history already run, build_brief, build_index); write dossier.md.

RD10: CDSE recovered after the earlier RemoteDisconnected run (transient, self-resolved).
Pulled 2 tight (2km buffer) single-scene chips EXACTLY centered on the Amendment Two POI
(28.85275,-96.0865): 2026-01-15 (0.1% cloud, clean) and 2026-07-09 (19.1% cloud, partial).
Read both full-size (image reads 1-2 of the 6-cap this run). BOTH show the same small
light-toned pad/structure with short access-road stubs near chip center, essentially
unchanged Jan->Jul 2026 -- consistent with the EIA/TCEQ-confirmed Duffy BESS pad (0.21 km
away), not a 3,526-acre solar array (which would show large graded rectangles spanning
multiple km, not a small pad in a 4km-square chip). Surrounding farmland in both frames is
undisturbed -- no grading/racking signature for the SOLAR portion specifically. This is
consistent with (does not contradict) Linea's own "construction begins Q3 2026" PR claim.
Copied both to imagery/key/ as the decisive site frames. This also gives an independent
coordinate cross-check: EIA-860M's Duffy BESS plant coordinate (28.854592,-96.08606) sits
0.21 km from the IA's own POI — two unrelated primary sources agree tightly. Site confidence
raised to "high". findings.json construction/imagery/site sections updated accordingly.

## Summary of this re-run's net changes vs the prior (violation) run
- SPV/developer chain: UNKNOWN -> FULLY RESOLVED (Linea Energy/EnCap -> Duffy Project Co LLC,
  f/k/a VDA Solar Texas 1, LLC; Google 500MW/15yr PPA offtake)
- Site: uncentered corridor guess -> exact POI (28.85275,-96.0865) from signed Amendment Two,
  cross-validated against independent EIA-860M coordinate (0.21 km agreement)
- Contractual schedule: 0 IA documents in old findings -> 3 CONFIRMED documents with full
  milestone/security/equipment history
- COD assessment: single-source (queue only, "2029-Q1 high risk") -> three-way cross-check
  (queue 2027-12-31 stale / signed IA 2028-10-31 / developer PR "late 2027"), independent
  estimate 2028-Q4, drift risk downgraded high->medium given secured offtake + amendment cadence
- Construction: "no_activity" (wrong coordinates) -> BESS pad confirmed stable, solar array
  no grading yet, consistent with a Q3-2026 stated start
- Verdict confidence: medium -> high

## Second-pass user review (2026-07-20)

**User question:** "looks like there is clearing, where is the project, images have too many
clouds, get more recent to check if clearing is recent."

- **Location** (unchanged, already high confidence): 28.85275, -96.0865, Matagorda County --
  IA Amendment Two's own POI coordinate, independently corroborated by EIA-860M's "Duffy
  BESS" plant record 0.21 km away. Sits on the Wadsworth-STP 345kV corridor.
- **Freshest available AWS Open Data scene**: 2026-07-19 (yesterday) -- fetched at both 2km
  (tight) and 6km (wide) buffers. Still cloud-affected (Gulf Coast humidity; no cleaner scene
  exists in the archive yet for this location/season) but the pad itself is visible in the
  clear portion of the tight chip.
- **"Clearing" assessment**: direct Jan-2026 vs Jul-2026 comparison at the exact POI shows the
  small BESS pad is UNCHANGED (present already Jan 2026) -- the brown/green patchwork the user
  is likely reading as clearing is ordinary seasonal farmland (winter-fallow brown, summer-crop
  green), not solar grading. No broad clearing/grading signature is visible in either the 2km
  or 6km buffer as of the newest (2026-07-19) scene. Verdict unchanged: BESS pad
  present/stable, solar array construction not yet visually evident.

## 2026-07-23 — imagery refresh (user request: 2026-only, no cloudy, drop off-site)
- User asked for more site frames, only 2026, no cloudy images, and to remove frames not
  showing the site. Site anchor = Amendment Two POI 28.85275,-96.0865.
- Fetched via s2aws.py (AWS Open Data COGs; named by TRUE acquisition date parsed from stdout,
  not query date). New clean 2 km chips at the exact POI: 2026-02-24 (0.6% cloud),
  2026-03-21 (2.0%); plus a 4 km wide-context frame 2026-03-21 (2.0%). Kept the existing clean
  2026-01-15 (0.1%). April/May 2026 returned NO scene under 10% cloud; June/July are all
  cloud-obscured (coastal-humid summer) -- best summer scenes are 2026-06-29 (6.3%) and
  2026-07-19 (~40%), which per the no-cloudy request are archived, not kept.
- FINAL clean key set (imagery/key/): s2_2026-01-15, s2_2026-02-24, s2_2026-03-21,
  s2_2026-03-21_wide4km.
- Moved (NOT hard-deleted -- imagery is gitignored, so a move keeps it recoverable) to
  scratchpad/duffy_old_imagery/: 6 off-site grid_* probes, 4 search_* probes, contact_grid.png,
  2 superseded site_* duplicates, and the cloudy summer frames (s2_2026-07-09, s2_2026-07-19,
  s2_2026-07-01_mid, s2_2026-06-29).
- Updated findings.json (construction.notes, imagery.frames, imagery_artifacts, site.notes),
  dossier.md (§1 verdict line, §6 satellite timeline table), rebuilt brief.html (4 images).
  Verdict, site coordinate, and all conclusions UNCHANGED: BESS pad present/stable, solar array
  not yet graded through the latest clear look (2026-03-21).
- IA energization dates (user question) confirmed against the PDFs: the SGIA has no discrete
  "energization date" -- ERCOT authorizes energization ~30 days after the TIF is modeled/energized
  (Amendment Two p12). Controlling contractual schedule (Amendment Two, eff. 2026-07-03):
  Prerequisite Items due 2027-04-15; TIF In-Service = later of 2027-08-15 or +4mo; Scheduled COD
  = later of 2028-10-31 or +4mo. Supersedes queue's stale 2027-12-31 and original 2023 SGIA
  (In-Service 2025-05-07 / COD 2025-08-06).

## 2026-07-23 (follow-up) — added most-recent usable frame
- User asked why there were no more-recent frames. Root cause: newest Sentinel-2 scene in
  existence is 2026-07-19 (~40% cloud, site cloud-covered); satellite last passed 07-19,
  ~5-day revisit, next pass ~07-24 not yet published -- so nothing fresher exists yet, and all
  July scenes (07-04 24.6%, 07-09 19.1%, 07-19 40%) have cloud over the POI.
- Added imagery/key/s2_2026-06-29.png (6.3% whole-tile, but the site itself is clear) as the
  most-recent USABLE frame. Pad unchanged, no array grading. Updated findings.json +
  dossier.md §6, rebuilt brief.html.

## 2026-07-23 (follow-up 2) — added newest July frame per user request
- User wanted the most recent July frame regardless of cloud. Added imagery/key/s2_2026-07-19.png
  (S2C_14RQS_20260719, 39.9% whole-tile) -- newest scene in existence. Heavy cloud is
  lower/bottom-right; BESS pad at center is clear. Pad unchanged, no array grading.
- Key set now 6 frames: 2026-01-15, 02-24, 03-21, 03-21_wide4km, 06-29, 07-19.
  Rebuilt brief.html. Archived (cloud over POI): 07-04, 07-09.
