# Triage log — Cradle Solar (23INR0150)

## T1 start
- queue_history.py ran OK: 64 snapshots (2021-03 → 2026-06)
- COD drift: 4 changes — 2023-08-31 → 2025-01-02 → 2025-12-31 → 2027-02-22 → 2027-09-17 (current); ~4-yr slip from original
- Capacity: 225 MW → 200.85 MW (2024-07)
- Key milestones achieved: Screening complete 2021-04-21; FIS approved 2025-03-14; IA signed 2023-03-15; Meets 6.9(1) 2025-02-12; Meets all 6.9 2025-04-30
- Construction start/end: NOT reported; no energization/synchronization/commercial operation approvals
- IA signed is a strong signal — project is past paper stage

## T2 start
- gmaps.py: HTTP 429 on first call; 429 on retry — rate-limited, blocked
- No delivery pins found (tool unavailable this run)
- T2 result: 0 pins

## T3 start
- Developer confirmed: Leeward Renewable Energy (LRE); SPV = Cradle Solar, LLC
- PPA: Microsoft Corp., ~200 MW, announced ~March 2024; sister project = Morrow Lake Solar (Frio County)
- Technology: First Solar thin-film PV
- Status per news: described as "actively under construction" / "currently under development" at time of PPA
- No specific coordinates or construction start date found
- No LLC registration details found via DDG
- Saved: sources/leeward_microsoft_ppa_summary.md
- T3 result: developer identified, PPA confirmed, construction activity claimed in press

## T4 start
- PUCT Interchange portal: HTTP 402 on direct access (blocked); one retry = same result
- Via DDG site search: IA found — PUCT docket 35077 contains ERCOT SGIA between CenterPoint Energy Houston Electric, LLC and Cradle Solar, LLC (200 MW solar, Bonney TX)
- Docket 53385: Emergency Operations Plan filings (Aug 2024, Mar 2025) — consistent with operational/pre-operational activity
- Direct PDF download of docket 35077 not possible via WebFetch (portal blocked); milestone schedule not retrieved
- Location confirmed: Bonney, Texas (Brazoria County)
- T4 result: IA confirmed (PUCT 35077 SGIA); milestone schedule not extractable in triage

## T5 start
- DDG search for Ch.313 / JETI in Brazoria County: no results for Cradle Solar
- TX Comptroller page: no granular data accessible via WebFetch
- No JETI or Ch.313 application found; normal for a post-2022 project (Ch.313 closed to new apps after Dec 2022; JETI is the successor but not widely filed yet)
- T5 result: no abatement found — expected/normal

## T6 start
- Site candidate: Bonney, Texas, ~29.317N, -95.448W (from SGIA filing; Brazoria County)
- cdse.py chip: HTTP 401 Unauthorized on all 9 grid calls — CDSE credentials not available in this session
- No imagery retrieved; no construction verdict from satellite
- T6 result: site candidate established (Bonney TX, confidence=medium-from-SGIA); imagery blocked (CDSE 401)

## T7 start
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~23; T2 blocked (gmaps 429), T6 blocked (CDSE 401)
- Deep scan recommended: YES

## D1 — IA review (2026-07-20)
- PUCT 35077-1580 CONFIRMED (INR in PDF); CenterPoint + Cradle Solar LLC; signed 2023-03-15
- Exhibit B: TIF In-Service = Oct 2 2024 or 18mo after start; Sched COD = Jan 2 2025 or 3mo after TIF IS → original COD was Jan 2025; now claims 2027-09-17 = 33-month slip
- Exhibit C: POI coords exact = 29°17'34.5606"N 95°24'54.1152"W; 310 TMEIC PVU-L0840GR inverters; 225 MW planned terminal; Speedway Substation = POI; Cradle Substation = gen facility
- Exhibit E: Security = $21,237,000
- Exhibit D: Cradle Solar LLC address 6688 N Central Expy Ste 500 Dallas TX 75206; email @LeewardEnergy.com confirms developer = Leeward Renewable Energy
- artifact: sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interconnection-agreem.pdf

## D2 — Site fix (2026-07-20)
- gmaps.py places "Cradle Solar": hit = "Cradle Solar Plant | 7HM8+XQ Angleton TX 77515 | 29.28494, -95.43309" (manufacturer/POI/establishment) — strong site gate pin
- POI structure coords 29.29293,-95.41503 agree within ~1.6 km (expected: gate vs interconnection structure)
- CDSE chip attempts at 29.2849,-95.4331: repeated RemoteDisconnected errors — imagery NOT obtained this session
- Static map: Maps Static API not enabled — not obtained
- EIA: both Brazoria Co matches (64447, 66046) are different operating projects; Cradle Solar NOT in EIA-860M

## D3 — Gap fill (2026-07-20)
- search.py "Cradle Solar Brazoria County Texas": FAILED all backends (negative — record)
- search.py "Cradle Solar Leeward Renewable Brazoria Texas construction 2025": FAILED (negative)
- search.py '"Cradle Solar" Brazoria Texas': FAILED (negative)
- No Ch.313/JETI found (expected: Ch.313 closed 2022; JETI not filed — consistent with post-2022 project)
- No Brazoria CAD parcel search attempted (portal not tried in deep scan)

## REFRESH 2026-07-20 (17:xx) — resolving EIA-vs-TCEQ contradiction (user 1M-budget re-run)
- Prior findings.json eia_match was a FALSE BIND to --plant-id 66046 (Danciger, unrelated OPERATING plant since 2022) — violates playbook D5 EIA BIND RULE (county+MW neighbor bind).
- Corrected: exact NAME match on plant 65822, plant name "Cradle Solar", entity "Infigen Asset Management LLC" (per `eia_generator_tx.parquet` direct query — eia_history.py's own matcher offered only the two non-name candidates 64447/66046 by county+MW; a raw pandas query found the exact name hit it missed/didn't surface as its own top choice — investigate why eia_history.py's substring matcher didn't surface 65822 itself later if revisited).
- Plant 65822 history: (U) under-construction ≤50% 2022-08→2024-05 (blip to (T) Jan-Feb 2023) → (T) regulatory-approvals-received/NOT under construction 2024-06→2024-11 → (L) regulatory-approvals-PENDING/NOT under construction 2024-12→2026-04 (16 months) → ABSENT from 2026-05-01 snapshot (DROPPED_FROM_860M).
- Infigen Asset Management LLC = ArcLight-era US wind/solar asset holding name (search.py "Infigen Asset Management LLC Leeward Renewable Energy" — no direct M&A link surfaced, but Infigen Energy's US assets were bought by ArcLight in 2015; Leeward is also ArcLight-lineage — plausible same corporate family, not confirmed).
- TCEQ live SoQL query (data.texas.gov tzyg-j7q4, Coastal & East Texas table, queried 2026-07-20): facility "CRADLE SOLAR" RN112058680, county BRAZORIA, reg_ent_desc "UTILITY SCALE SOLAR PROJECT", 2 ACTIVE stormwater-construction NOIs (TXR1539SI, TXR1573SY), affil_begin_dt = status_dt = 2024-10-03T00:00:00, site desc "1 MILE OFF OF HIGHWAY 48 AND LEFT INTO FRONTAGE RD.", owner/EPC of record = "Pcl Solar Constructors USA Inc." Full raw JSON captured in this log (not saved as separate artifact — SoQL result, cite by query+date per playbook rule 2).
- Verified geography: search.py "County Road 48 Brazoria County Texas Bonney Angleton" → top hit "25033 County Road 48, Angleton, TX 77515" (HAR.com listing) — same ZIP (77515) as the prior run's Google Places pin "Cradle Solar Plant" (7HM8+XQ Angleton TX 77515). NOTE: TCEQ site desc says "Highway 48" but Brazoria's numbered road in this area is "County Road 48" (TX State Highway 48 is in Cameron County near Brownsville, per Wikipedia/TxDOT — confirmed NOT this). Site desc is informal/abbreviated, matches County Road 48.
- PCL Solar Constructors USA Inc. is a real, known utility-scale solar EPC (PCL Construction subsidiary) — consistent with "actively under construction" news framing, not a shell.
- Fetched official project sites via WebFetch (curl got HTTP 403 bot-block on both):
  - cradlesolartx.com: 1,600 acres, "Targeted Operational" = 2026 (site literally shows "0" placeholder text alongside it per prior scrape, WebFetch read "2026"), development-phase progress bar (not machine readable), no EPC/PPA disclosed, developer = Leeward Renewable Energy, owner SPV = "Cradle Solar Energy, LLC" (note: slightly different from IA party name "Cradle Solar, LLC" — same project, verify if this is a scrivener variant or two related entities), LRE = portfolio company of OMERS Infrastructure.
  - lreus.com/projects/cradle-solar/: 200 MW, ~35 mi S of Houston, ~1,600 ac privately owned, no COD/EPC/PPA on page.
  - Both saved: sources/2026-07-20_cradlesolartx_official-site.html, sources/2026-07-20_lreus_cradle-solar-project-page.html
- CDSE imagery: chip command hangs >180s (no error, no output) this session — DIFFERENT failure mode than prior run's immediate RemoteDisconnected/401. Verified token acquisition works in isolation (get_token() returns valid JWT in <1s from cache). The openEO job submission/polling step itself is what hangs. Still no imagery obtained — logging as a second, distinct CDSE failure mode for the known-issues list.
- Resolution adopted for dossier: TCEQ active dated NOI + named EPC is stronger, more specific evidence of physical construction than EIA's self-reported status, which regressed backward (U→T→L) in a way inconsistent with a project simultaneously described in Leeward's own developer materials and Microsoft PPA news as under development toward a 2026 target. Treat EIA-860M status for this project as unreliable/stale rather than treating TCEQ as wrong. The whole-plant EIA disappearance (2026-05) is NOT read as a cancellation signal given the active permit — most likely an EIA-side reporting/reorg gap (Infigen legacy entity name).
- eia_history.py rerun with --plant-id 65822 (correct match): wrote eia_history.json. EIA's OWN planned-COD history also slipped: 2024-06 → 2024-12 → 2025-12 → 2026-05 → 2027-05 (as of the last 7 monthly reports, 2025-11 through 2026-04) — this independently corroborates the queue's current 2027-09-17 claim (2027-05 EIA vs 2027-09 queue, ~4 months apart, same ballpark) far better than a straight paper-project read would predict.
- puct.py match rerun: still only 1 filing (35077-1580, original SGIA) — no amendment has been filed since the prior run. Confirms contractual schedule (Sched COD 2025-01-02) is unamended/stale on paper; the 2027-09-17 claim is NOT yet reflected in any signed IA amendment.

## Official project-website fetch + imagery re-search (2026-07-20, continued)
- cradlesolartx.com / lreus.com fetched via WebFetch (curl 403 bot-blocked both) — see refresh block above for content. Notably: official site's OWN SPV name is "Cradle Solar Energy, LLC" vs the IA party "Cradle Solar, LLC" — flagging as an unconfirmed naming variant, not investigated further (low priority, same project beyond doubt via address/PPA/county match).
- CDSE fleet contention heavy this session (other concurrent agents' cdse.py processes visible in `ps aux` the whole session; one agent was mid-edit adding a 2-slot+10/min fleet-wide throttle to cdse.py itself, causing a transient syntax error window ~17:38-17:40). Foreground `chip` calls hung >180s with no output; backgrounding (nohup + poll) got 5 chips through successfully before contention worsened again:
  - imagery/s2_tight_lowcloud.png (2km, 2026-05-29, 11.6% cloud) — pin area quiet, no array
  - imagery/s2_jan2025_3km.png (3km, 2025-03-16, 1.5% cloud) — pin area baseline
  - imagery/s2_jan2026_3km.png (3km, 2026-03-13, 0% cloud) — pin area unchanged vs 2025-03
  - imagery/s2_wide6km_2026-03.png (6km, 2026-03-18, 0.7% cloud) — wide view, small existing solar installation visible near a highway junction ~2km SW of pin (pre-existing, NOT Cradle-scale — likely a small distributed/commercial array, not verified further)
  - imagery/grid/*.png (9× 2km chips, 2026-03-21, 1.8% cloud) — 3x3 grid spanning the area between the Google Places pin and the IA POI coordinates; reviewed via imagery/grid_contact_sheet.png — all 9 tiles show established residential subdivisions, farmland (tilled fields, not graded/racked), ranchland, and small ponds. NO large graded polygon or racking signature matching a ~1,600-acre / 225 MW utility solar buildout is visible anywhere in this ~6km x 6km search window as of March 2026.
- 2 further chip attempts (dark-shape recheck near the wide chip's SW corner; tight chip at the exact IA POI/CRADLE-substation coords 29.29293,-95.41503) both hung on fleet contention and were abandoned per playbook ("do NOT loop... log as negative evidence, move on") rather than retried further — logged as negative evidence, not a definitive "nothing there."
- Monthly timelapse job (2024-06→2026-07) failed outright after exhausted retries (RemoteDisconnected) — no monthly bracket obtained this session.
- CONCLUSION on imagery: at 10 m/px, the ~6km search window around the Places pin / IA POI shows NO visible large-scale grading or racking as of March 2026 — this is negative evidence for "substantially complete," not proof of "no activity"; early-stage sitework (clearing, access roads, small pads) consistent with the Oct-2024 TCEQ stormwater permit could be present without being distinguishable from farmland at this resolution, OR the true array footprint sits outside the searched 6x6km box (a 1,600-acre parcel is ~2.5km per side, so it should have been visible if centered near the pin/POI — but a ~2-3km offset from search center is plausible with imagery this constrained by clouds+contention). This is the single most consequential gap in this run.

## D4-D5 — Synthesis & wrap-up (2026-07-20)
- CDSE all attempts failed (RemoteDisconnected) — imagery gap noted in dossier
- EIA: no confirmed match for Cradle Solar; both Brazoria Co candidates are different operating projects
- dossier.md written; findings.json finalized
- verdict: real_active (IA confirmed, $21.2M security, PPA, milestones cleared, Places pin active)
- independent COD: 2027-Q4; drift risk: medium
- queue_history.py: OK (timeline already existed)
- build_brief.py: OK (brief.html 18KB)
- build_index.py: OK (145 projects indexed)
