# Triage log — Elm Flats Solar SLF (26INR0130)

T1 start

## T1 — Queue history

37 snapshots (2023-06-01 → 2026-06-01). COD has drifted 3 times:
- 2026-01-31 (held 1 month), → 2026-07-01 (held ~14 mo), → 2026-12-01 (held ~10 mo), → 2027-09-30 (current, held since 2025-08)
- Total COD drift: ~20 months from original 2026-01-31
- IA signed: 2025-11-21 (first appeared in latest snapshot 2026-06-01) — very recent
- FIS approved: NOT achieved
- No construction milestones (start/end, energization, sync, COA all blank)
- Capacity: minor uptick from 125.58 → 125.84 MW (2026-02)

Verdict: Active, IA just signed Nov 2025, pre-construction. COD drift is significant but not alarming for a 125 MW solar project.

T2 start

## T2 — Delivery pins

gmaps.py returned HTTP 429 (rate-limited) on both attempts (exact name; name+county). Budget exhausted. No pins found.

T3 start

## T3 — Web sweep

Key findings:
- Developer: **Orca Falls Solar, LLC** (confirmed via PUCT IA filing; some trackers list "Elm Flats Solar, LLC" as alternate entity name)
- Paired project: storage component 26INR0131 (Elm Flats Storage SLF, ~50 MW battery) shares the same IA
- IA executed 2025-11-21 with Oncor Electric Delivery under PUC docket **35077**, item 2325 — filed Dec 2025
- ercotqueue.com rates build-chance 5% (low, but they also flag "no IA" which contradicts the actual PUCT filing — likely stale tracker)
- No press releases or developer parent company identified
- gem.wiki lists as "announced" (no construction)
- Saved source: PUCT docket reference (no file download yet — that's T4)

T4 start

## T4 — PUCT Interchange

PUCT interchange portal (interchange.puc.texas.gov) returned HTTP 402 on all attempts:
- Search by controlNumber=35077 → 402
- Search by controlNumber=35077&itemNumber=2325 → 402
- Direct PDF (35077_2325_1566464.PDF) → 402
Portal requires authentication; cannot retrieve IA PDF during triage.

IA is confirmed to exist (docket 35077, item 2325, filed ~Dec 2025, Oncor + Orca Falls Solar, LLC,
covering both Elm Flats Solar SLF & Elm Flats Storage SLF) via T3 web results.
IA parties/POI/schedule page not extracted — this is a deep-scan task.

T5 start

## T5 — Abatements

Ch. 313 program expired 2022 — project entered queue 2023-06, so Ch. 313 is not applicable.
JETI registry: gov.texas.gov/business/page/jeti returned 404. Comptroller Ch.313 search page
did not surface a county-level lookup tool. DDG search for JETI/abatement hit CAPTCHA.
No abatement found. Normal for a post-2022 project without a confirmed JETI filing.

T6 start

## T6 — Imagery

Site candidate: 32.1136, -96.3048 (from infrasure.ai EIA plant record, high confidence).
Downloaded 3 chips (2 km buffer, 2026-06-15 ±15d, cloud≤40%):
- s2_2026-06-15.png (center)
- s2_grid_32.0836_-96.3048_2026-06-15.png (south)
- s2_grid_32.1436_-96.3348_2026-06-15.png (north-west)
5 of 8 surrounding grid chips failed (CDSE 403/RemoteDisconnected during parallel batch — rate/auth issue).

Contact sheet read: all three frames show undisturbed agricultural/rural land — scattered crop fields,
wooded creek corridors, no solar panel arrays, no ground disturbance or construction patterns visible.
Construction verdict: NOT VISIBLE. Consistent with IA signed Nov 2025, no queue construction milestones.

No re-centering or baseline chip warranted (no activity to anchor on).

T7 start

## T7 — Write and stop

triage_findings.json and triage.md written. 28 turns used. Stopping.

---

# DEEP SCAN — 2026-07-20

## D0 — Inventory

Prior triage + partial deep artifacts already on disk: 1 IA PDF in sources/ (unextracted), 3 imagery
chips, contact_sheet.png, factsheet.json/md (paper_score 16 -> deep_candidate, priority 8.75).
findings.json did not exist yet — this run's D0 checkpoint created it fresh from triage+factsheet data.

## D1 — IA schedule extraction (exhibit.py)

`exhibit.py sheet` on the on-disk IA PDF (35077-2325, 53pp) — read via 4-page tile sheets, decisive pages:
- p8 (sheet02): signature page — Orca Falls Solar, LLC (Generator, signed by Peter Stein CDO) x Oncor
  Electric Delivery Company LLC (TSP, signed by Jim Greer EVP/COO), both dated 2025-11-21.
- p31 (sheet04): **Exhibit B Time Schedule** — In-Service Date(s) May 13, 2027; Scheduled Trial
  Operation Date May 30, 2027; Scheduled Commercial Operation Date **September 30, 2027** — EXACTLY
  matches queue-claimed COD. Also lists E&P DSA security schedule (Aug 20 2025 $4,017,301 -> Nov 21
  2025 $8,115,760, sheet14 p53).
- p33/34 (sheet09): **Exhibit C Interconnection Details** — POI = "Wheelock Lake Switch in TSP's
  Trinidad Switch - Corsicana Sub 138kV Transmission Line," Navarro County. 35 Sungrow
  SG4400UD-MV-US inverters, 146.3 MVA nameplate, dispatched 125.58MW@34.5kV / 127.155MW at gen
  terminals. Co-located: 26INR0131 Elm Flats Storage SLF (47x SMA SCS3450UP-US, 128.06MW/129.015MW).
- Attachment 1 one-line diagram (sheet12 p46): confirms queue POI text "3472 BRIAR_CRK_8 -
  3467 POWELL1_8" = same node — Wheelock Lake Switch sits on the 138kV line to Corsicana Sub "via
  Briar Creek POI" and to Trinidad Sub "via Powell Sub." POI naming reconciled, not a discrepancy.
- Exact Wheelock Lake Switch coordinates redacted (CEII) per Oncor's PUCT cover letter (sheet01 p2) —
  "Oncor Electric Delivery has redacted station location information, which contain CEII, located in
  Exhibit B and Exhibit C."
- No parcel/boundary map exhibit in the IA itself (Exhibit C is text + one-line diagram only, no site
  plan) — site evidence for D2 must come from Ch.313 instead.

## D1b — SPV / Ch.313 registry

`ch313.py resolve 26INR0130` -> 1 candidate: Ch.313 #1973, applicant "Elm Flats Solar, LLC," Kerens
ISD, applied 2022-05-25. Downloaded app + amend1 + agmt PDFs. `spv.py resolve` cross-check:
EIA-860M plant-name match "Elm Flats Solar" 125.0MW, entity **Birch Creek Development**,
@32.11358,-96.30476, planned 2026-06.

Ch.313 application (sources/2026-07-20_comptroller_ch313_1973-kerens-elm-app.pdf) cover letter +
signature page CONFIRM the chain: Christopher Norqual signs as "Authorized Representative, Elm
Flats Solar, LLC" with email **norqual@birchcreekdev.com** — ties the 2022 Ch.313 applicant directly
to the EIA-reporting entity Birch Creek Development. Also cc'd: Joe Arb, Consultant
(jarb@alluvialpower.com); Troy Reed, Manager, Ernst & Young LLP (EY prepared/filed the application).
Notarized in Los Angeles County, CA (Erica Sabiniano, notary) — Birch Creek Development is
CA-based or uses a CA-based signatory.

Land: Ch.313 Tab 9 "Description of Land" — "The applicant will lease approximately 1,500 acres of
land within Navarro County, Texas for the project." **Leased, not purchased.** Cover letter states
"~125 MWac... utility scale single axis tracker photovoltaic facility... surface area approximately
1,500 acres."

**Site map found**: Ch.313 Checklist Item #11 vicinity maps (app p39-41, sheet06-07) — Navarro CAD
web map shows the actual project boundary polygon (irregular quadrilateral, ~1 mi across) just east
of Powell / south of Kerens, in the Elm Flat area, Kerens ISD — NOT a county centroid, an actual
drawn project-boundary shape from the applicant's own filing. This is close to and consistent with
the EIA-860M candidate coordinate (32.11358, -96.30476) — corroboration from an independent source
(Ch.313 filing vicinity map vs EIA-860M plant registry), upgrading site confidence to medium-high.
No IA-exhibit map existed to cross-check further (IA Exhibit C has no site plan, CEII-redacted).

First Year of Qualifying Time Period: 2026. First Year of Limitation: 2028. Min qualified investment
$40,000,000. Only 1 new qualifying job committed (waiver requested/granted per Section 14.9/3a — job
creation requirement waived). This is a small-jobs, land-lease solar Ch.313 application, typical for
the fuel type — not itself a red flag.

Checkpoint: findings.json updated with llc_chain (Orca Falls Solar/Elm Flats Solar LLC/Birch Creek
Development/Joe Arb-Alluvial Power/EY/Oncor), project_area (1500 ac, Ch313 Tab 9), site map_artifacts,
contractual_schedule (IA Exhibit B milestones + security schedule).

## D1c — Ch.313 executed agreement + amendment

Read `..._agmt.pdf` (executed Agreement for Limitation on Appraised Value, Kerens ISD x Elm Flats
Solar LLC, application #1973) via exhibit.py sheets. Findings:
- Total investment estimate "in excess of $162 million" (Region 12 ESC financial impact summary,
  p2/sheet08). $40M value-limitation ceiling on M&O appraised value, years 2028-29 through 2037-38
  (10-yr limitation period, first year of qualifying period 2026). Projected total revenue to
  Kerens ISD $1,897,253 over the life of the agreement (= projected company tax savings, offsetting
  figures in the Region 12 summary table).
- Executed agreement itself dated **November 28, 2022** (DocuSign, Exhibit 2/3/4 pages) — pre-dates
  IA execution by 3 years. Exhibit 2 "Description and Location of Land" repeats the 1,500-acre lease
  language; Exhibit 3/4 list qualified-investment/property components (modules, tracking mounts,
  BESS, inverters on pads, substation, O&M facility) — consistent with a genuine utility-scale
  single-axis-tracker PV + co-located BESS design, matches IA equipment list (Sungrow inverters, SMA
  BESS) filed 3 years later.
- Amendment 001 (7/21/2022, pre-dates the main agreement) — routine attachment/wage-table update
  within the same application cycle, not a substantive change.
- This is now the 3rd independent document confirming ~125 MW solar + co-located BESS on ~1,500
  leased acres in Navarro County: Ch.313 app (2022) -> Ch.313 agreement (2022) -> IA (2025) — fully
  consistent story across a 3-year gap, no contradiction. Financial commitment (Ch.313 tax
  concession bound to $40M limitation, in force once qualifying investment is made) is a real cost
  to the school district only if the project is built — school district would not have executed this
  in 2022 without genuine developer intent, though of course this predates the recent 20-month queue
  COD drift and does not by itself prove current construction timing.

## D2 — Site + imagery (CDSE outage)

CDSE openEO backend unreachable this session — 5 consecutive `cdse.py chip` attempts (2km and 3km
buffer, various dates) all failed with `RemoteDisconnected` after establishing a valid cached token
(/tmp/.cdse_token_cache.json refreshed 17:07, so not a credentials/auth issue — backend-side).
gmaps.py places also 429'd (rate-limited), consistent with triage's earlier gmaps failures for this
same project. Logging as negative evidence / tool outage rather than retrying indefinitely.

Falling back to the 3 chips triage already pulled (2026-06-15, 2km buffer, centered + N/S grid
around the EIA/Ch313-corroborated site 32.1136,-96.3048): contact_sheet.png reviewed again — all
three frames show intact cropland/pasture, wooded creek corridors, scattered rural structures; NO
graded rectangles, NO racking rows, NO substation pad visible at or near the coordinate. Verdict
unchanged from triage: **no_activity**. Given IA execution was only 2025-11-21 (~8 months before
these chips) and In-Service Date isn't until 2027-05-13, this is expected, not a red flag.

## D3 — Gap-fill / web sweep

search.py: "Birch Creek Development Elm Flats Solar Navarro County" -> Birch Creek Energy (dev,
formerly branded "Birch Creek Development") general company hits, Crunchbase, birchcreekdev.com
"about" page; no Elm-Flats-specific news article. "Orca Falls Solar LLC" -> 0 relevant hits (generic
"Orca" solar companies unrelated). "Elm Flats Solar Navarro County construction" -> 0 relevant hits
(unrelated Lightsource bp/Enel/bigelmsolar.com results — bigelmsolar.com is a different, unrelated
"Big Elm Solar" project per its placeholder "coming soon" page, NOT this project — logged as
negative, do not conflate names). "Birch Creek Energy solar projects Texas" -> confirms Birch Creek
Energy (birchcreekdev.com) is a real, PGIM-backed ($65-76M invested), scaling solar IPP/developer
(PRNewswire coverage of expansion + Foundation Solar Partners acquisition) — general corporate
legitimacy confirmed, but no Elm-Flats-project-specific press found.
WebFetch birchcreekdev.com/about/ directly: confirms "36 utility-scale solar projects, 872 MW" but
lists no individual project names/locations — Elm Flats not named on their own site (normal for a
pre-construction project, not itself a red flag).
No press release, no PPA/offtake announcement, no EPC contractor identified for Elm Flats
specifically. Negative evidence logged.

## D4/D5 — Wrap-up

`queue_history.py 26INR0130` -> timeline.json/md refreshed (37 snapshots, 3 COD changes,
IA-signed date matches). `eia_history.py 26INR0130 --write` -> confirmed EIA status flip to
"(U) Under construction, <=50% complete" starting 2025-12-01 (was "(P) Planned" through 2025-11) —
this is the one open divergence vs our no-activity imagery read; recorded in cod_assessment
reasoning_evidence, not resolved (CDSE down all session). `build_brief.py 26INR0130` ->
brief.html regenerated after final findings.json edits. `build_index.py` -> index refreshed
(166 projects).

Verdict: **real_early**. Independent COD 2027-Q4 (vs reported 2027-09-30), drift risk medium.
Site 32.1136,-96.30476, medium-high confidence (EIA plant record + Ch.313 vicinity map
corroboration). dossier.md written per template. Deep scan complete.

