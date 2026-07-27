# Triage log — Cachena Solar SLF (23INR0027)

T1 start

## T1 — Queue history

- 71 snapshots (2020-08-01 → 2026-06-01)
- 6 COD drifts: 2023-06-01 → 2023-12-31 → 2024-06-01 → 2024-12-31 → 2025-12-31 → 2026-12-31 → **2027-04-29** (current)
- Milestones: Screening complete 2020-07-13 | FIS requested 2020-08-17 | **IA signed 2021-11-23** | Meets 6.9(1) 2021-11-29 | **FIS approved 2026-06-17** (very recent)
- Notable: IA was signed BEFORE FIS approval (unusual order); FIS only approved ~1 month ago
- Capacity drift: 400 → 408.94 → 440 → 600 → 601.31 → **602.02 MW**
- No construction milestones (start/end/energization/sync/COD) — none achieved
- Result: mature queue entrant (2020), serious milestones, no construction activity on record

T2 start

## T2 — Delivery pins

- gmaps.py: HTTP 429 on first call; one retry also 429 → BLOCKED (per rules: 1 retry, then negative log)
- pins_found: 0 (API rate-limited, not searched successfully)

T3 start

## T3 — Web sweep

- Developer identified: **Clear Fork Creek Solar LLC** (TX entity #0803498583, reg. address El Dorado Hills CA 95762)
- No parent company surfaced; Jeff Sabins listed as CDO (CorporationWiki)
- **Wilson County Commissioners approved 10-year tax abatement July 14, 2025** — county-level, not Ch.313
- Project described as ~6,100 acres along US-87 (Precinct 4), includes BESS component reference
- No press releases, financing news, construction updates, or PPA announcements found
- No dedicated project page saved (no pages directly about this project beyond queue trackers)
- news_found: false (only queue aggregators, no primary reporting)

T4 start

## T4 — PUCT Interchange

- interchange.ercot.com: ENOTFOUND (DNS, not a real host)
- interchange.puc.texas.gov: HTTP 402 on all attempts — blocked/session required
- DDG site:interchange.puc.texas.gov search: CAPTCHA blocked
- IA signed date from T1: 2021-11-23 — IA IS confirmed in queue data but PDF not retrieved
- ia_found: TRUE (via queue milestone; PDF inaccessible this pass)
- DRIFT: queue history shows IA signed 2021-11-23 but FIS only approved 2026-06-17 — unusual gap

T5 start

## T5 — Abatements

- TX Comptroller Ch.313 search: no direct Ch.313 hit found; search tools inaccessible or returned no results
- JETI registry: not checked directly (DDG CAPTCHA blocked all subsequent queries)
- From T3 web sweep: **Wilson County Commissioners approved 10-year tax abatement July 14, 2025** — county-level (Ch.312 or commissioners' agreement, not necessarily Ch.313/JETI)
- Ch.313 expired for new applications post-2022; JETI is replacement — expected miss for post-2022 filing
- abatement_found: TRUE (county-level 10-year, July 2025 — type not confirmed but county commissioner approval is strong signal)
- No application PDF downloaded (not accessible this pass)

T6 start

## T6 — Imagery

- Site candidate: Wilson County / US-87 corridor near Floresville (~29.13°N, -98.16°W) — low confidence (from T3 description: "~6,100 acres along US-87 Precinct 4")
- 3×3 chip grid attempted (center 29.13/-98.16, step ±0.03°, buffer-km 2, date 2026-07-01 ±15d)
- CDSE RemoteDisconnected on 7/9 chips; 2/9 returned successfully
- Contact sheet generated with 2 frames
- Visual review of contact sheet: left chip (29.10,-98.13) shows agricultural farmland, road intersection, small structures — NO solar panel rows, no grading, no construction visible; right chip (29.16,-98.19) rendered black (no data)
- construction_visible: FALSE (limited coverage, no signal in available chips)
- Imagery inconclusive due to partial CDSE failure and low-confidence site location
- No baseline chip run (no clear construction signal to anchor re-center on)

T7 start

## T7 — Outputs written

- triage_findings.json ✓
- triage.md ✓
- Turns used: ~28
- STOP

---

# Deep scan log — 2026-07-20

## D0 — Skeleton written

- findings.json skeleton created
- Triage noted: 2 verified IA PDFs on disk (sources/2026-07-19_puct_35077-1594_cps-clear-fork-creek-solar-ia-amends1-3.pdf and sources/2026-07-19_puct_56006-351_cachena-solar-bundled-tx.pdf)
- EIA candidate: Clear Fork Creek Solar and BESS SLF 600 MW at 29.26357,-97.78055, planned 2027-03, under construction <=50%
- EIA coords (29.26357,-97.78055) are DIFFERENT from triage site candidate (29.13,-98.16) — EIA candidate is ~17 km NE of triage guess; this is the primary site fix candidate
- Deep scan focus threads: IA schedule extract, developer parent chain, Wilson CAD parcels, imagery at EIA coords

## D1 — IA Schedule extraction (2026-07-20)

### PUCT 35077-1594: Amendments 1-3 to Generation Interconnection Agreement
- Filed 2023-04-21 by CPS Energy; parties = CPS Energy + **Clear Fork Creek Solar LLC** (Delaware LLC)
- CDO signatory: Jeffrey Sabins (signed all 3 amendments)
- POI: 18.5 miles East of Elm Creek station on 345kV Elm Creek-STP circuit 2

| Document | Signed | Capacity | In-Service | Trial Op | COD | Security |
|---|---|---|---|---|---|---|
| Original IA | 2021-11-23 | ~440 MW | — | — | — | $13.1M total LoC |
| Amendment 1 | 2022-03-28 | 440 MW | 2024-04-15 | 2024-04-22 | 2024-05-31 | $13.1M unchanged |
| Amendment 2 | 2022-10-14 | 600 MW | 2024-10-03 | 2024-10-15 | 2024-12-31 | $13.1M unchanged |
| Amendment 3 | 2023-04-10 | 600 MW | 2025-11-07 | 2025-11-28 | 2025-12-31 | $13.1M + delay pmt $40,571 |

- Amendment 3 COD was **Dec 31, 2025 — MISSED**. No Amendment 4+ found in PUCT (puct.py match with "Clear Fork Creek Solar" returned only the 35077-1594 filing)

### PUCT 56006-351: CPS MTCPR November 2024
- Project T-0313/S-0966 "Cachena, Wilson" = TSP switchyard for this project
- Start: 2026-08-03 | Finish: 2027-01-31 | % Complete: **0% as of Nov 2024**
- CPS Energy cost: $3.7M for 345kV switchyard loop-in
- **CRITICAL**: TSP switchyard not started as of Nov 2024, won't finish until Jan 2027 at earliest

## D2 — Site pinpoint (2026-07-20)

- EIA-860M: plant "Clear Fork Creek Solar and BESS SLF" 600MW @ **29.26357,-97.78055**, planned COD 2027-03, status "under construction <=50%"
- IA confirms: POI ~18.5 miles east of Elm Creek 345kV station; Wilson County — consistent with EIA coords
- gmaps.py "Cachena Solar": NO RESULTS
- gmaps.py "Clear Fork Creek Solar Wilson County": NO RESULTS
- CDSE: all chips RemoteDisconnected (2026-07-20 server outage) — no satellite imagery obtained this session
- Enbridge project map (2026-07-19_enbridge_clear-fork-solar-map.png): shows Clear Fork solar in SE Texas, Wilson County, SE of San Antonio — consistent with EIA coords
- Triage site guess (29.13,-98.16) replaced by EIA 29.26357,-97.78055; ~17 km difference
- Site confidence: **medium** (EIA coords + IA POI consistent; no independent parcel/CAD verification this session)

## D3 — Gap-fill: Developer/ownership/abatement (2026-07-20)

### Enbridge FID press release (2026-07-19_enbridge_pr_clear-fork-solar-fid.html)
- **Enbridge Inc.** announced FID on "Clear Fork" 600 MW solar on July 22, 2025
- Located "near San Antonio" in Wilson County
- In-service expected **"summer of 2027"**
- **Meta Platforms, Inc.** signed long-term contract for 100% of renewable output
- Project cost: **US$900 million**
- "Construction is underway" as of FID announcement

### Enbridge project updates (2026-07-19_enbridge_clear-fork-solar-project-updates.html)
- November 2021: Enbridge completed original interconnection agreements with CPS Energy and ERCOT
- **August 2025: Started early construction activities, including site preparation and clearing**
- **Q4 2025: Construction began**

### Enbridge FAQ (2026-07-19_enbridge_clear-fork-solar-faq.html)
- **4,600 acres** of privately owned land (vs. triage estimate ~6,100 — FAQ preferred)
- Full output to Meta Platforms; $900M capital cost

### Registry results
- ch313.py: NO HIT for "Cachena Solar SLF" — expected (Ch.313 expired 2022; post-2022 Enbridge projects use county agreements)
- spv.py: confirmed EIA-860M candidate at 29.26357,-97.78055
- search.py: all backends failed (SEARCH FAILED) — negative evidence logged

### Abatement
- Wilson County Commissioners approved 10-year tax abatement July 14, 2025 (county-level Ch.312; no JETI/Ch.313)

## D4 — COD assessment (2026-07-20)

- Three corroborating sources: Enbridge "summer 2027", EIA-860M "2027-03", queue "2027-04-29"
- TSP switchyard (T-0313) not started as of Nov 2024; scheduled finish Jan 31, 2027 — on critical path
- Construction active (site prep Aug 2025, full construction Q4 2025)
- 6 prior COD slips (2023-06 original → 2027-04 current); Amendment 3 COD Dec 2025 already missed
- Independent COD estimate: **2027-Q3** (mid-summer as Enbridge stated, vs queue Apr 29)
- Drift risk: **medium** — $900M committed, Meta PPA, active construction, but TSP critical path + historical pattern

## D5 — Wrap-up tools pending
- queue_history.py: already run at D0 (timeline.md exists)
- eia_history.py --write: pending
- build_brief.py: pending
- build_index.py: pending

---

# Retraction + re-derivation — 2026-07-21

## R0 — Why this pass exists

Orchestrator flagged (deterministic cross-check, not this project's own analysis) that
the site adopted in the 2026-07-20 deep pass, 29.456,-97.750 ("high" confidence,
"grading since 2026-01/02"), is **wrong**. That footprint belongs to **Hoke Solar**
(23INR0231, f/k/a Brush Country Solar), a 95.29 MW project in **Gonzales** County on a
**138kV** tap (LCRA Deer Creek-Nixon), not this project's 602MW/4,600-acre array on the
**345kV** Elm Creek-STP circuit in **Wilson** County. Evidence: FCC census geocode of that
point = Gonzales County; the only OSM transmission line within 2km is 138kV; the ~550-acre
footprint scale fits Hoke's 95MW not Cachena's 602MW; and Hoke's own Ch.313 boundary map
(scale-bar georeference, `research/23INR0231_hoke-solar/sources/SITE_DERIVATION.md`) lands
dead-center on that same footprint.

## R1 — How the error happened (read the transcript, not just the artifact)

The 2026-07-20 pass's own logic was: (1) correctly catch that the EIA-860M coordinate
(29.26357,-97.78055) is the Nixon, TX town centroid, not the plant; (2) re-derive via a
15km AWS Open Data sweep "due east" of Elm Creek substation per the IA's "18.5 mi East"
language; (3) find a large graded multi-block site ~15mi out and adopt it, backed by a
"visually confirmed construction matching developer's own timeline" claim.

That timeline claim was **circular**, not independent confirmation. Re-read both
`sources/2026-07-19_enbridge_clear-fork-solar-project-updates.html` and the FAQ this
pass (2026-07-21): Enbridge's own public page states ONLY that site prep began Aug 2025
and construction began Q4 2025 — **it names no location whatsoever**. The prior pass
found *a* real construction site (Hoke's) at a plausible bearing/distance whose
observed grading dates (first visible Feb 2026) happened to postdate Enbridge's Aug/Q4
2025 announcement, and treated that date-order coincidence as proof of identity, without
checking county, interconnection voltage, or an independent boundary map — the same
category of unverified-coordinate mistake as the EIA-town-centroid bug it had just caught
one step earlier in the same pass.

SITE_CORROBORATION_tceq.md (2026-07-20) separately found a real, useful lead — a TCEQ
stormwater-NOI physical address, "10046 US Highway 87 East", Wilson County, shared by
three related "Clear Fork Creek Solar" registrations — but mis-used it as mere
corroboration of the wrong (Nixon-centroid) EIA point instead of geocoding it as an
independent site fix in its own right. That is fixed this pass (R2 below).

## R2 — Re-derivation

**Registry rungs checked first** (per playbook: boundary maps beat imagery):
- `ch313.py resolve 23INR0027`: NEGATIVE — no Ch.313 agreement or JETI application for
  "Cachena Solar SLF" (program expired 2022, project took FID without value-limitation
  filing; matches 2026-07-20 finding, re-confirmed).
- `ch312.py resolve 23INR0027`: 2 Wilson County candidates, both "City of La Vernia
  Crossing Reinvestment Zone" — an unrelated commercial development, not Clear Fork
  Creek Solar. No boundary map available from this rung.
- `grep -i "clear fork"` / `"cachena"` across `data/reference/ch312_abatements_detail.csv`
  and `ch313_agreements.json`: no hits.
- No abatement-registry boundary map exists for this project — confirmed dead end,
  proceed to the TCEQ-address + imagery rungs.

**TCEQ address geocode** (the actual re-derivation): the three stormwater-NOI
registrations sharing "10046 US Highway 87 East / US Hwy 87 E", Wilson County
(`sources/2026-07-20_tceq_stormwater_nois_clearfork_cachena.json`) — "CLEAR FORK CREEK
SOLAR" (main array, EPC Hanwha Q Cells EPC USA LLC, active since 2025-08-15), "CLEAR
FORK CREEK SOLAR SUBSTATION" (same EPC, since 2025-01-13), "CACHENA SOLAR POI" (owner
Dorazio Enterprises, since 2025-07-09) — were geocoded with two independent services:
- Esri/ArcGIS World Geocoder: score 100, StreetAddress match → **29.257169,-97.809055**
  ("Nixon, TX 78140")
- Google Places API (text search "10046 US Highway 87 East Nixon TX"): street_address
  type → **29.258670,-97.802252** ("Stockdale, TX 78160")

Independent agreement to ~0.5 mi. Adopted point = average = **29.2579,-97.8057**.

Distance check: straight-line from Elm Creek substation (29.4673,-97.99988) to this
point = **18.57 mi**, within 0.4% of the IA's stated "approximately 18.5 miles East"
POI language (bearing is ESE, not literally due-east, but the IA text is a narrative
approximation, not a bearing spec — same caveat the 2026-07-20 pass correctly applied
to its own now-retracted point).

The EIA-860M point (29.26357,-97.78055, Nixon town centroid — an administrative
artifact, not the plant) sits ~1.5 mi from this new address point: same neighborhood,
loosely corroborating, but explicitly NOT used as the site fix (that was the original
sin of the 2026-07-20 pass).

**Site confidence: medium** — two independent geocoders converging on the project's own
registered construction address is real, checkable evidence, stronger than a town
centroid or an uncross-checked "due east" imagery sweep, but it is a documentary
address anchor, not an imagery- or parcel-confirmed array boundary.

## R3 — Imagery: delete wrong frames, sweep the true site

Deleted the 7 imagery/key/ frames from the retracted pass (all centered on Hoke's
footprint): s2_2024-06-01, s2_2025-06-01, s2_2025-10-01, s2_2025-11-01, s2_2026-01-15,
s2_2026-03-15, s2_2026-06-15.

Fetched a fresh series at the true-site address anchor (29.2579,-97.8057):
- Wide-area sweeps to rule out a nearby offset: 6km buffer, 14km x 24km undistorted
  tile, 15km buffer, and an 18km x 24km tile shifted north toward Clear Fork Creek
  (the waterway the project is named for) — roughly 24km x 24km total coverage,
  best-available low-cloud scene 2026-07-09 (4.3% cloud). Only large disturbed-earth
  feature found: an irregular ~1km blob with haul roads and standing-water ponds south
  of the address point, consistent with a pre-existing aggregate/caliche quarry (wrong
  shape and wrong scale for a 4,600-acre solar array).
- Tight 3km-buffer time series at the address point itself, 5 usable dates: 2024-06-09
  (19.2% cloud, partial), 2025-06-17 (0.5%), 2025-11-26 (5.2%), 2026-05-03 (0.1%),
  2026-07-09 (4.3%) — a 6th candidate (2026-02-12, 18% cloud) was too cloud-obscured
  to be useful and was dropped. All 5 kept frames show unbroken agricultural/ranch
  land with center-pivot irrigation; a small tank/utility yard along US-87 is visible
  and UNCHANGED in every frame including the 2024 baseline (pre-existing, not new
  construction). **No grading, racking rows, or large-scale earthwork visible in any
  frame through 2026-07-09.**
- All 5 new frames verified: valid PNG magic bytes, all >400KB, each individually
  inspected (not just file-listed) before being written to imagery/key/.

## R4 — Verdict / construction outcome

- `real_active` is NOT supported — no imagery-confirmed construction exists at the
  best-available true-site anchor, and the only "confirmed construction" the prior pass
  cited was another project's (Hoke's) footprint.
- `real_early` adopted: the paper trail remains strong and independent of the site
  question — signed IA (2021-11-23), $13.1M financial security posted, FID announced
  (Jul 22, 2025), Meta Platforms 100% long-term PPA, and TCEQ stormwater-NOI permits
  ACTIVE since Jan/Jul/Aug 2025 naming a real EPC (Hanwha Q Cells). These permits prove
  regulatory/contractual reality, not Sentinel-2-visible dirt-moving — an honest
  distinction this pass keeps separate going forward.
- COD drift risk nudged from "med" to "med-high": the visual construction-progress
  cross-check that would normally corroborate an on-track build is currently
  unavailable (paper trail says permits are active; imagery can't confirm the
  earthwork it implies).

## R5 — Companion project (23INR0077 Cachena Storage SLF)

Checked `research/23INR0077_cachena-storage-slf/` — only triage-stage files exist
(no findings.json/dossier.md/imagery — deep scan never ran for the storage companion).
Added a retraction note to its triage.md/log.md pointing at this project's corrected
site rather than rewriting a nonexistent findings.json. No imagery to fix (none exists).

## R6 — Outputs

- findings.json: site/construction/verdict/eia sections rewritten, `retraction` block
  added, confidence downgraded to medium at the site level
- imagery/key/: 7 wrong frames deleted, 5 new frames fetched and inspected
- SITE_CORROBORATION_wide_sweep.md, SITE_CORROBORATION_tceq.md: retraction/correction
  banners added, false conclusions struck through with corrected notes (originals kept
  for provenance)
- dossier.md: synced to the corrected site/verdict/construction (see dossier.md diff)
- build_brief.py 23INR0027: re-run, confirm exit 0
- Banned-domain grep: run across findings/dossier/log/brief/sources (transcripts
  exempt) — see final report

## 2026-07-21 (orchestrator) — Ch.312 abatement: primary document recovered
User asked to chase the "commissioners approved 10-year abatement 2025-07-14" note against the
ch312 scrape. Registry: conclusively absent (all Wilson rows = La Vernia city commercial; zero
Enbridge/Clear Fork/Cachena hits across live+reports+purged+detail CSV) — CAD annual-submission
lag for a 2025-07 approval. Went to the primary record instead: Wilson County posts agendas as
PDFs (census custom-pdf platform); fetched 07-14-2025 Agenda.pdf → item 6 is the abatement:
Clear Fork Creek Solar LLC, 600MW PV, $800M, ~6,100-ac reinvestment zone N+S of Hwy 87 Pct 4,
21 named CAD parcels w/ owners (see sources/2025-07-14_wilson-county_agenda_item6_extraction.md).
Zone location corroborates the re-derived Hwy-87 address anchor. Vote outcome still needs the
minutes (page 403s from container) — documented gap. Parcel IDs = future CAD-boundary lead.

## 2026-07-21 (orchestrator) — zone-wide imagery per agenda location description
Used the agenda's zone description (~6,100 ac N+S of Hwy 87, Pct 4) to size a 12x10km frame
pair at the address anchor: s2_2026-07-19_zone12x10km.png vs s2_2024-07-04_zone12x10km.png
(both 14RPT, fetched via s2aws, inspected). Result: entire corridor is agriculture; no ground
activity through 2026-07-19. Nixon visible ~4.5km ENE — original EIA Nixon-centroid pin was
only ~4km off (the 2026-07-20 'corrected' pin was the 20km error). Verdict real_early stands.
