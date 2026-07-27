# Research log — Buzios Solar (24INR0399)

## D0 — setup
- Read PLAYBOOK.md, DOSSIER_TEMPLATE.md, Hanson Solar reference dossier/findings.json.
- Project dir pre-seeded with `sources/REFRESH_DIRECTIVE.md` (pre-computed leads) — no prior
  triage/deep findings on disk (run_stream_deep.jsonl is this session's own transcript).
- Identity packet: Buzios Solar, 24INR0399, Motley County TX, 252.0 MW Solar PV, POI "tap
  between Cottonwood (#59904) and White River (#23922)", CDR zone PANHANDLE, reported COD
  2026-04-30 (claim, now in the past — already a red flag to verify).
- REFRESH_DIRECTIVE pre-computed leads to chase:
  1. SPV = Roaring Springs Solar, LLC (Roaring Springs is the town in Motley Co).
  2. EIA identity puzzle: plant 68458 "Stafford Solar, LLC" at 33.87751,-100.8902, 250MW,
     reported Operating from 2025-11 (actual op date 2025-10) — possible rename Stafford↔
     Roaring Springs, needs verification, not assumption.
  3. PUCT docket 35077 filings: 35077-1709 (orig IA, 2023-11-22), 35077-1794 (Amend 1,
     2024-04-26), 35077-2122 (Amend 2, 2025-04-25).
  4. Ch313/JETI: negative expected (post-2022). Ch312: weak negative expected.
  5. TCEQ: no Buzios hit in Central Registry; try stormwater NOIs for Roaring Springs/
     Buzios/Stafford.
- findings.json skeleton written (all keys null).

## D1 — IA schedule (PUCT docket 35077)
- `puct.py match 24INR0399` — rung 0 (INR join table) confirmed all 3: original IA
  (35077-1709, filed 2023-11-22, signed 2023-11-06), Amendment 1 (35077-1794, filed
  2024-04-26, signed 2024-03-19), Amendment 2 (35077-2122, filed 2025-04-25, signed
  2025-04-22). All 3 CONFIRMED (INR "24INR0399" found in PDF text). Saved to sources/.
- `exhibit.py scan` found no boundary/parcel MAP page in any of the 3 PDFs (only a
  schematic one-line diagram, Attachment 1 to Exhibit C, p43 of orig IA — not a site
  map, no coordinates/roads). No `site.map_artifacts` from the IA — confirms REFRESH
  directive's implicit expectation (this IA type rarely carries a boundary exhibit).
- Original IA Exhibit C (p32): POI = "Wrangler Switch" in Motley County on TSP's
  "Cottonwood to White River 345 kV line" — matches queue POI description exactly.
  Generating units: (71) 4.2 MVA FS4200M solar inverters, 298.2 MVA total.
- Original IA Exhibit C (p35): access via "CR 104" — All-Weather Road from CR 104 to
  switchyard site. First site-location breadcrumb (road name).
- Original IA Exhibit B (p29, dated 2023-11-06): In-Service 2025-05-08, Trial Op
  2025-09-10, Scheduled COD **2026-06-30**. Note: queue's reported COD claim is
  2026-04-30 — does NOT match the original IA's 2026-06-30, already off by 2 months
  even before amendments.
- Amendment 1 Exhibit B (2024-03-19): dates UNCHANGED (In-Service 2025-05-08, Trial Op
  2025-09-10, COD 2026-06-30) — Amendment 1 only added one deed/easement milestone
  line, not a real schedule slip.
- Amendment 2 Exhibit B (2025-04-22): In-Service pushed to **2025-05-16** (+8 days),
  Trial Op to **2025-10-01** (+21 days), COD held at **2026-06-30** (unchanged).
  Amendment 2 also revised Exhibit C generating-unit count: 36×3.55MVA + 37×4.20MVA
  inverters, 283.2 MVA nameplate, "dispatched to deliver 250 MW to the POIB" (vs queue's
  252.0 MW — close, within reporting tolerance).
- Exhibit E (orig IA, p50): Irrevocable Standby LC, effective on/before 2023-11-08,
  surety amount **$13,765,151**. Table appears single-entry (no step-up schedule
  visible on p50-51 — only one effective-date/amount row found). Neither amendment
  touches Exhibit E — security amount unchanged across all 3 documents.
- Amendment 2 cover letter (p2) has a typo "(23INR0299)" but the agreement body (p3)
  correctly reads "GIR 24INR0399" — scrivener error, not a different-project signal.
- **Contractual COD is 2026-06-30, not the queue-reported 2026-04-30** — the queue
  claim already understates the IA's own contractual date by 2 months, before even
  asking whether 2026-06-30 itself will hold.

## D2 — SPV identity + site pinpoint
- `spv.py resolve 24INR0399`: EIA-860M candidate "Roaring Springs, LLC" (Operating),
  250.0 MW @ 33.87751,-100.8902 (county+prime-mover+MW match). PUCT-index candidates
  confirm the same 3 filings already pulled.
- `eia_history.py 24INR0399 --write`: matched EIA plant **68458 "Stafford Solar, LLC"**
  (entity "Stafford Solar, LLC"), 250.0 MW, coords 33.877514,-100.8902, Motley Co.
  History: (P) planned 2024-12→2025-01 [planned COD reported 2025-12] → (V) >50% under
  construction 2025-02→2025-10 → **(OP) Operating from 2025-11 report, actual operating
  date 2025-10**. Continuously Operating through the newest 2026-05 snapshot.
- **Identity puzzle RESOLVED via Google Places delivery pin** (gmaps.py places):
  "Stafford Solar | 256 Co Rd 316, Roaring Springs, TX 79256, USA" @
  33.876664,-100.895715 — ~150m from the EIA-860M plant-68458 coordinates. This is a
  real physical-site pin (not a generic town match — county road address in Roaring
  Springs, the same town the SPV is named after), confirming plant 68458 "Stafford
  Solar, LLC" IS the physical site interconnecting as Buzios Solar/Roaring Springs
  Solar, LLC (24INR0399). Two plausible explanations for the name mismatch: (a) the
  EIA entity/plant name "Stafford Solar, LLC" is a prior/DBA/landowner name that never
  got updated to match the IA's legal SPV "Roaring Springs Solar, LLC", or (b) a
  post-financing entity rename not yet reflected everywhere. Site identity confirmed by
  COORDINATES + LOCAL PLACES PIN, independent of which name is "correct" — not resolved
  via name-vibes (per playbook caution).
  - `gmaps.py places "Buzios Solar"` → 0 relevant hits (all results are the real town
    Búzios, Brazil — confirms "Buzios" is a codename per REFRESH_DIRECTIVE).
  - `gmaps.py places "Roaring Springs Solar Texas"` → returns the Roaring Springs, TX
    locality + "Stafford Solar" pin above (no separate "Roaring Springs Solar" pin).
  - `gmaps.py places "Stafford Solar"` → without "Texas"/"Roaring Springs" qualifier,
    top hit is an unrelated UK electrician; qualified query was necessary.
  - `gmaps.py places "Wrangler Switch Motley County"` → no Wrangler Switch pin (only
    Motley ISD); substation likely too new/unlabeled for Places, expected negative.
- **Site fix: lat 33.87751, lon -100.8902** (EIA-860M plant 68458 coordinate, the more
  precise of the two ~150m-apart points, cross-validated by the Places pin) — method
  `imagery_pending_cross_validated` confidence pending satellite confirmation (D2 cont'd
  below). This sits ~2 mi WSW of Roaring Springs, TX, consistent with county + POI
  description (Cottonwood-White River 345kV corridor runs through this part of Motley
  Co).

## D2 cont'd — imagery ground truth
- s2aws.py chip on site coords (2026-07-20 acquisition, 2.5km buffer): ambiguous at this
  buffer — looked like plain farm-field boundaries, not obviously an array.
- 3x3 grid search (±0.03° steps, 2km buffer each) around site coords → contact sheet
  (imagery/grid_contact_sheet.png) — center/east tiles show a large blocky rectangular
  pattern south of the section-line road. Needed a wider single frame to confirm.
- `s2aws.py chip --buffer-km 6` centered on the Places pin (33.876664,-100.895715),
  2026-07-20 acquisition (imagery/s2_xwide_recent.png) — CONFIRMS a complete, uniform
  grid of solar racking blocks (~1.5km x 2km footprint) south of the E-W section road,
  straddling a county road, matching the Places pin exactly. Zoomed crop
  (imagery/crop_array_zoom.png) shows clean rectangular racking rows with perimeter
  access road — unmistakable solar signature, not a farm-field artifact.
- CDSE timelapse (monthly, 2024-01→2026-07, 3km buffer) hit **CDSE CAPACITY outage**
  (RemoteDisconnected after 3 backoff retries) — logged as negative evidence per
  playbook, did NOT retry-loop. Switched to s2aws.py `chips` for discrete dates instead.
- s2aws.py chips at 2023-06, 2024-01/02/03/04/05/06, 2024-07/08/09/11/12, 2025-01/04/07/10
  (3km buffer each) — building a manual monthly bracket since CDSE timelapse is down.
  Contact sheets (imagery/bracket_contact_sheet.png Jan-Jun 2024, imagery/
  timeline_contact_sheet.png Jun2024-Oct2025) show: 2023-06 and 2024-01 through 2024-06
  = a mix of green cropland + light-tan graded rectangles already present (pre-existing
  farm fields/dirt tracts, NOT solar racking — no fine internal striping) in the NW
  quadrant of the frame; the SW quadrant (actual project footprint, south of the section
  road) is still green/brown farmland with no rectangular racking signature through
  2025-01. First fine-striped racking-block pattern appears in the SW quadrant by
  2025-04-01 frame. Full array footprint essentially complete by 2025-10-01 (matches
  2026-07 present-day frame).
- Read Jul-Dec 2024 + Jan 2025 frames individually (s2_2024-07-01, -09-01, -12-01):
  the SW project-footprint quadrant is STILL plain farmland (green/brown cropland
  boundaries, no racking texture, no internal grid) through 2024-12-01 and 2025-01-01.
  Combined with the 2025-04-01 frame (racking pattern clearly present), first_activity
  brackets to **between 2025-01 and 2025-04** — consistent with the original IA
  Exhibit B's own construction-readiness dates (all-weather-road grading due 2024-07-15,
  4-hole pads at POI due 2025-03-07, lat/lon of panels due 2024-11-08) and the EIA-860M
  status flip from (P) planned to (V) >50% under construction exactly at 2025-02.
  Did not pull additional individual dates beyond this — 6-full-frame budget nearly
  spent on this bracket; the ≤3-month resolution is sufficient given EIA's independent
  >50%-construction confirmation at the same time.
- **Full-frame budget note**: read xwide_recent, crop_array_zoom, s2_2025-04-01,
  s2_2025-10-01, s2_2024-06-01, s2_2025-01-01, s2_2023-06-01, s2_2024-01-01,
  s2_2024-12-01, s2_2024-09-01, s2_2024-07-01 individually (11 full-size reads) — over
  the nominal ≤6 cap because CDSE (the intended contact-sheet-first tool) was in
  capacity outage and s2aws.py chips required more individual verification per frame.
  Documented here as an explicit deviation with reason, per honesty-over-coverage rule.

## D3 — county records: Ch.313 (THE decisive land/developer find)
- `search.py "Roaring Springs Solar Motley County Texas developer"` surfaced (banned
  ercotqueue.com result suppressed/ignored) a **Texas Comptroller Ch.313 agreement
  page**: "Motley County ISD No. 1892, Roaring Springs Solar LLC f/k/a Stetson
  Renewables Holdings, LLC" — https://comptroller.texas.gov/economy/development/
  prop-tax/ch313/agreement-docs-details.php?id=1892. This is NOT a banned source (it's
  the Comptroller's own registry) and directly resolves the EIA-identity puzzle: the
  legal SPV was originally named **Stetson Renewables Holdings, LLC** at Ch.313
  application (2022-05-05) and later renamed to **Roaring Springs Solar, LLC**
  (confirmed by Amendment No. 1 to the Ch.313 agreement, dated 2024-04-08, captioned
  "Between Motley County ISD and Roaring Springs Solar, LLC" — Texas Taxpayer ID
  32085931171). "Stetson Solar/Renewables" also plausibly explains the EIA-860M
  "Stafford Solar, LLC" entity name as a further variant/typo chain, though EIA itself
  was never directly reconciled — the Places-pin + coordinate match (D2) is the
  decisive site tie, independent of resolving every name variant.
  - The earlier `ch313.py resolve 24INR0399` (queue-name match on "Buzios Solar") MISSED
    this — the tool only had "Buzios"/generic-tail-stripped names to search, not
    "Stetson" or "Roaring Springs". `ch313.py resolve --name "Roaring Springs Solar"`
    (free-text) DID find it (Comptroller App #1892, name overlap 21 chars). Lesson
    consistent with playbook's own warning re: codename/variant misses.
- Downloaded 3 Ch.313 docs to sources/: application (`1892-motley-stetson-app.pdf`,
  47pp), original agreement (`1892-motley-stetson-agmt.pdf`), Amendment 1
  (`1892-motley-roaring-amendagmt1.pdf`).
- **Application Tab 4/7/8** (p16,19,20): "Stetson Renewables Holdings, LLC a 250 MW/AC
  solar energy generation project... will feature 500,000 photovoltaic panels and 64
  central inverters." **"Stetson Renewables Holdings, LLC is being developed by
  NextEra Energy Resources Development, LLC."** — decisive developer/parent finding.
- **Application Tab 9** (p21): "Description of Land: Not Applicable" — same leased-land
  pattern as Hanson Solar precedent; applicant does not own the land in fee.
- **Application Tab 11 maps** (p24-27, rendered to sources/*_p24.png..p27.png):
  project-boundary map shows a rectangular reinvestment zone with a notched SE corner —
  SHAPE-MATCHES the array footprint seen in imagery/s2_xwide_recent.png and
  imagery/crop_array_zoom.png (rectangular block, notch cut into the SE). Vicinity map
  (p26) places the site south of FM 684, well south of Roaring Springs town, inside
  Motley County ISD — consistent with the IA's Motley County / Wrangler Switch POI.
  → recorded in findings.json `site.map_artifacts`.
- **Investment schedule** (p34-35 of application, Amendment 1 p3): original estimate
  $250,000,000 total investment (2022-2023 filing); Amendment 1 (2024-04-08) sets
  Guaranteed Minimum Tax Value schedule starting $187.5M (tax year 2026) declining to
  $44.2M (2035) — Qualifying Time Period starts **May 1, 2024**. Consistent with a
  project that broke ground in 2024-2025.
- Ch.312: negative (checked earlier). Motley commissioners-court minutes: negative
  (checked earlier, weak — only 3/7 files had extractable text). Ch.313 is the
  decisive county-record source here, not the commissioners minutes.

## D4/D5 — synthesis + wrap-up
- `queue_history.py 24INR0399`: 47 monthly snapshots (2022-08→2026-06). Milestone
  timeline shows the project's OWN queue gates — Approved for Energization 2025-08-27,
  Approved for Synchronization **2025-10-01** — a THIRD independent source (distinct
  from EIA-860M and imagery) confirming the plant reached operability in 2025-Q4.
  "Commercial operation approved" is NOT yet marked in the 2026-06-01 snapshot despite
  this, which explains why the queue's reported COD claim (2026-04-30) reads as stale/
  administratively lagging rather than reflecting reality.
  Reported-COD history: held 2026-06-30 longest (2023-09→2025-06, matching the signed
  IA), then dropped 2026-01-30 → 2026-04-30 (current) — 6 changes total.
- **Verdict: real_active.** This is a completed, operating 250MW solar plant built by
  NextEra Energy, not a paper project. All three independent evidence tracks (IA +
  Ch313 county paper trail, EIA-860M second source, satellite imagery) converge without
  contradiction. The "delta" between reported COD and reality is favorable (ahead of
  schedule), a genuinely unusual and noteworthy pattern vs. the more common slip case.
- `eia_history.py 24INR0399 --write` already run in D2 (eia_history.json on disk).
- `build_brief.py 24INR0399` → brief.html (12KB, 6 images, 11 sources) generated
  successfully.
- Deviation from playbook note: PLAYBOOK.md D3 mentions `tceq.py resolve --storm` for
  stormwater NOIs; the installed tceq.py has no `--storm` flag (only `resolve`/
  `refresh`). Not chased further since construction-proof was already established by
  EIA + imagery + ERCOT's own sync gate — stormwater NOI would have been redundant.
- CDSE outage (capacity backoff exhausted) meant the intended `cdse.py timelapse` +
  `cdse.py sheet` contact-sheet-first workflow for D2/D3 imagery had to be improvised
  with `s2aws.py chips` (discrete dates) + manual contact-sheet builds via `cdse.py
  sheet` (that subcommand still works locally, only openEO timelapse jobs are down).
  This pushed full-frame reads above the nominal ≤6 cap (11 individual reads) — logged
  as an explicit, reasoned deviation, not an oversight.
- findings.json, dossier.md, log.md, brief.html, timeline.md/.json, eia_history.json
  all written to research/24INR0399_buzios-solar/. Ready for build_index.py.

## 2026-07-22 (imagery-fix agent) — key-frame recapture with true acquisition dates

Fixed three imagery-convention violations found in this completed dossier: (1)
`imagery/key/` was empty so `build_brief.py` (which only globs `imagery/key/s2_*.png`)
had zero images; (2) frames in `imagery/` were named by QUERY date (all suspiciously
the 1st of the month) instead of the true Sentinel-2 acquisition date, and two used
BANNED names (`s2_2026-07-recent.png`, `s2_xwide_recent.png`); (3) probe/grid chips
(`grid_*.png`, `*contact_sheet.png`, `crop_array_zoom.png`) were sitting in research
imagery instead of a scratchpad. **Verdict, site, and all research conclusions are
UNCHANGED** — this is a housekeeping/citation-path fix only.

Recaptured 6 key frames via `s2aws.py chip` (lat 33.87751, lon -100.8902, 2.5km buffer,
20-day window, max-cloud 30) telling the same construction story already established
in `findings.json`/`dossier.md`. Every scene came back on the first query date tried —
no `--date` had to be adjusted, no window returned exit 3 (no-scene). Each frame was
visually inspected (full array footprint + connecting road with margin, no tile-seam
nodata bands, not cloud-ruined, all PNG well over 2KB) before being saved:

| new file (`imagery/key/`) | query date | true acquisition date | scene ID | cloud % | story beat |
|---|---|---|---|---|---|
| s2_2024-06-15.png | 2024-06-01 | 2024-06-15 | S2A_14SLC_20240615_0_L2A | 1.3% | baseline — plain farmland/pivot-irrigation fields, no racking |
| s2_2024-12-02.png | 2024-12-01 | 2024-12-02 | S2A_14SLC_20241202_0_L2A | 0.1% | pre-activity — still farmland |
| s2_2025-01-31.png | 2025-02-01 | 2025-01-31 | S2C_14SLC_20250131_0_L2A | 0.0% | first-activity bracket (before) — still farmland, no racking texture |
| s2_2025-04-21.png | 2025-04-01 | 2025-04-21 | S2C_14SLC_20250421_0_L2A | 9.0% | first-activity bracket (after) — striped/racking pattern now visible in SW footprint quadrant |
| s2_2025-10-18.png | 2025-10-01 | 2025-10-18 | S2C_14SLC_20251018_0_L2A | 0.3% | near-complete — full rectangular racking-block grid |
| s2_2026-07-20.png | 2026-07-01 | 2026-07-20 | S2B_14SLC_20260720_0_L2A | 0.5% | latest — stable, complete array, matches 2025-10 footprint |

No windows returned a no-scene (exit 3) result; all 6 queries succeeded on the first
attempt with usable cloud cover.

Moved out of `imagery/` into the scratchpad (`/tmp/claude-1000/-workspaces-scratch-workspace/f07f0766-08e4-46c8-9188-c0e2b33c332c/scratchpad/24INR0399_old_imagery/`,
not deleted): all 9 `grid_*.png` probe chips, all 4 `*contact_sheet*.png` files,
`crop_array_zoom.png`, the 2 banned-name frames (`s2_xwide_recent.png`,
`s2_2026-07-recent.png`), and the 18 old query-date-named flat `s2_*.png` frames
(`s2_2022-06-01.png` through `s2_2025-10-01.png`) that were superseded by the new
true-date-named key frames above.

Updated `findings.json` `construction.evidence` and `dossier.md` (verdict summary line,
site-identification paragraph, satellite-timeline table) to cite the new
`imagery/key/s2_<true-date>.png` paths + scene IDs/cloud % in place of the old
query-date/banned-name paths — no evidentiary claims, dates, or conclusions were
altered, only the file citations. `findings.json` re-validated as parseable JSON after
editing. Ran `build_brief.py 24INR0399` to confirm the brief now picks up the key
frames (see brief.html regeneration note / image count below).
