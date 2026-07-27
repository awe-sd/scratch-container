# Research log — Shaula II Solar (22INR0267)

## D0 — setup
- Read PLAYBOOK.md, DOSSIER_TEMPLATE.md, Hanson example dossier.
- Read `sources/REFRESH_DIRECTIVE.md` — pre-computed leads: EIA-860M negative (zero DeWitt Co
  rows, no "Shaula" match), Ch.313/JETI negative, Ch.312 weak negative, TCEQ Central Registry
  negative (only unrelated DCP pipeline facility in DeWitt). PUCT rung-0 (INR join) is empty but
  `puct.py search "Shaula"` reportedly shows 4 filings in docket 35077.
- No `factsheet.json`/`triage_findings.json` present in this dir — starting cold, deep mode only.
- Twin-phase cluster: 22INR0251 Shaula I Solar is the sibling (same county, POI, MW) — must
  attribute imagery/filings to the correct phase, not double count. Cachena Solar SLF (23INR0027,
  Wilson Co) taps the same Elm Creek 345kV family further north — do not cross-attribute.
- findings.json skeleton written (all nulls).

## D1 — IA schedule
- `puct.py search "Shaula"` → docket 35077, 4 filings total (2 for Shaula I, 2 for Shaula II).
- `puct.py filings 35077 --match "Shaula"` → TSP is **CPS Energy** (San Antonio muni), NOT a
  standard ERCOT TSP list name. Shaula II filings: 35077-1413 (original IA, filed 2022-05-05,
  signed 2022-04-27) and 35077-1555 (First Amendment, filed 2023-02-13, signed 2022-11-16).
  Both downloaded to sources/ (39pp + 10pp PDFs). `exhibit.py scan` found no true boundary/site
  maps — Exhibit C1 (p35/36 of original) is a generic POI wiring diagram (no coords/roads),
  Exhibit C2 is a one-line electrical diagram labeled "SHAULA SOLAR" / "CPS ENERGY" — rendered
  but NOT useful for site pinpoint, no map_artifacts recorded from these.
- **SPV parent resolved directly from IA signature page**: "SHAULA ENERGY PROJECT II, LLC / By:
  BP Solar Holding LLC, its sole member" signed by Javier Fuentes, VP, 11/10/2022
  (sources/2026-07-21_puct_35077-1555_filing.pdf p4). BP Solar Holding LLC = BP plc's US solar
  development arm (Lightsource bp is BP's separate JV; "BP Solar Holding LLC" appears to be a
  direct BP subsidiary — needs a web check to confirm which BP solar platform this maps to).
- Exhibit C (Interconnection Details), IA original + amendment, IDENTICAL wording both filings:
  "Name: Shaula Solar II"; POI = "approximately 63 miles east of the CPS Energy-owned Elm Creek
  345 kV Switchyard on the 345 kV Elm Creek to STP transmission circuit [2 in orig / 1 in amend]";
  "approximately sixty-three (63) 3.257 MVA PV inverter arrays... 205.2 MW of AC power" — MATCHES
  queue MW and POI description exactly (ckt 1 in the amendment matches the queue's "ckt 1").
  Total transmission line GIF→TIF ≤ 1 mile (short tie line — site is close to the POI tap).
- **Exhibit B time schedule — decisive COD find**:
  - Original IA (2022): In-Service 2024-10-25, Trial Op 2024-11-12, **Commercial Operation
    2024-12-24**.
  - First Amendment (signed 2022-11-16, ~7 months after original): In-Service 2025-04-25,
    Trial Op 2025-05-30, **Commercial Operation 2026-05-30** — exactly the queue's reported
    COD claim (2026-05-30). One prior slip of ~17 months, made EARLY (before construction
    milestones), not a late-stage slip.
  - Both exhibits state schedule is EXPLICITLY DEPENDENT on "the Shaula I Energy Project" —
    delays to Shaula I extend Shaula II's dates 1:1; if Shaula I is canceled the agreement
    would be amended. This ties the two phases' COD credibility together contractually.
  - Financial security (Exhibit D, both filings): $2,046,000 (design/procurement) +
    $889,000 (construction) = **$2,935,000 total** — small for 205 MW (Hanson's 396 MW project
    carried $11-13M in LCs), consistent with a muni-TSP interconnection (CPS Energy, not an
    investor-owned TSP) rather than paper-project weakness per se.
  - Site work clause (Exhibit C, amendment): Generator owed CPS Energy boundary
    survey/topo CADD files, easement maps by 2024-01-12 — a real requirement, not evidence
    those were delivered (no CPS/CAD confirmation obtained here).
- Per REFRESH_DIRECTIVE: EIA-860M negative (no Shaula/DeWitt Co rows), Ch313/JETI negative,
  TCEQ Central Registry negative — noted, not re-run (per playbook: don't re-loop dry rungs).

## D2 — site pinpoint
- `gmaps.py places` — NO RESULTS for "Shaula Solar", "Shaula Solar II construction DeWitt County
  Texas", "Shaula Energy Project", "BP Solar Holding DeWitt County", "Elm Creek Switchyard DeWitt
  County Texas". No delivery pin exists for this project (negative evidence, logged).
- `search.py "Shaula Solar DeWitt County Texas BP"` → dewittcountytoday.com hits (5 banned
  queue-tracker results suppressed by search.py itself, confirming the blocklist works). Both
  target URLs 404 on the live site; Wayback has a snapshot for one:
  https://web.archive.org/web/20250722042246/https://www.dewittcountytoday.com/news/solar-proposal-plans-target-dewitt-county
  (saved sources/2026-07-21_wayback_dewittcountytoday_solar-proposal-plans.html). The
  "county-approves-road-use-agreement" article has NO wayback snapshot (negative evidence).
- **DECISIVE local-news find** (Cuero Record via DeWitt County Today, published 2022-02-22,
  reporting a Cuero ISD board meeting held 2022-02-17): "Light Source BP...introducing their
  mission about a specific solar project in southern Dewitt county...it does look like southern
  Cuero ISD might become the solar capital of South Texas...Two, 200 Mega-Watt, projects with a
  180 million dollar total investment were presented and discussed. Shaula Energy plans to start
  construction March 2023." Board moved to accept a Ch313 application to submit to the
  Comptroller. This: (a) identifies the developer as **Lightsource bp** (confirms/names the "BP
  Solar Holding LLC" IA signatory as the Lightsource bp JV, not a generic BP entity), (b)
  confirms BOTH Shaula I and Shaula II are ~200 MW each (matches 205.2 MW), (c) narrows the site
  to **southern DeWitt County, Cuero ISD** territory, (d) gives a construction-start TARGET of
  March 2023 (never independently confirmed — see imagery below), (e) explains why Ch313 registry
  came back negative in REFRESH_DIRECTIVE: the application was only "accepted to review and
  submit" in Feb 2022 -- may never have been finalized/executed, or was filed under a different
  legal name the ch313.py static table didn't catch.
- Next: run `ch313.py resolve --name "Shaula" --county "DeWitt"` and `--name "Cuero"` to check
  for an application filed under the ISD; POI cross-check via OpenInfraMap for Elm Creek-STP
  345kV circuit routing through southern DeWitt Co.

## D3 — gap-fill (county/registry re-checks with new leads)
- `ch313.py resolve --name "Shaula"|"Lightsource"|"Cuero"` and `--county "DeWitt"` — ALL
  NEGATIVE. The Feb-2022 Cuero ISD board vote was only to "accept an application to review and
  submit to the comptroller" — never appears in the Comptroller's own 740-row Ch313 table or
  38-row JETI table under any name tried. Strong signal the Ch313 filing was never finalized/
  executed (or Cuero ISD's board never took final action), consistent with the FIS-never-completed
  status in REFRESH_DIRECTIVE.
- `ch312.py resolve 22INR0267` — NEGATIVE (weak, registry gaps possible).
- `minutes.py harvest --county "DeWitt"` (83 new PDFs) + `index --county "DeWitt"` (82 scanned,
  75 image-only/no-OCR, 7 with real text) + `resolve 22INR0267` / `--name "Shaula"` / `--name
  "Lightsource"` — ALL NEGATIVE. Real text coverage is only 7/82 files, so this is a WEAK
  negative, not proof no abatement/RUA discussion occurred — most Commissioners Court minutes on
  this county's portal are scanned images.
- `tceq.py resolve --county "DeWitt" --keyword "Shaula"` — NEGATIVE (only unrelated DCP Operating
  Company pipeline facility in DeWitt Co). `spv.py resolve 22INR0267` — dry, matches
  REFRESH_DIRECTIVE.
- **MAJOR FIND via search.py**: query "Shaula Energy Project II LLC stormwater TCEQ" surfaced a
  Comptroller asset URL `assets.comptroller.texas.gov/ch313/1715/1715-yoakum-shaula-findings.pdf`
  — Ch313 Application #1715, **Yoakum ISD** (not Cuero ISD — DeWitt straddles two districts, and
  the ch313.py static table search on "Yoakum"/"Shaula"/"Cuero" all missed this; a real gap in
  that tool's 740-row table, not proof of non-existence). Live URL returns S3 AccessDenied but
  Wayback has a full 154-page snapshot (2024-07-06) — fetched successfully.
  saved: sources/2026-07-21_wayback_comptroller_ch313-1715-yoakum-shaula-findings.pdf (5.9MB).
  **This is the executed, board-approved Ch313 agreement** (Yoakum ISD Board Resolution dated
  2022-11-17, signed by Board President Glen Kusak + Secretary Darlene Renken, p6 of the Findings
  doc) — contradicts REFRESH_DIRECTIVE's "Ch.313/JETI: negative" note, which was a tool-table gap,
  not a true negative. Corrected: Ch313 agreement EXISTS and was executed for Shaula II.
- Tab 4 (Detailed Description of Project): "Shaula Energy Project II, LLC is a 200 MW/AC solar
  electric generation facility that will be located in eastern DeWitt County in western Yoakum
  Independent School District. The facility will feature 530,000 photovoltaic panels and 63
  central inverters" (matches IA's 63 inverter arrays exactly) — "wholly owned by BP Solar
  Holding, LLC and is being developed by Lightsource BP under a development services agreement.
  With 5.4 GW of developed solar energy generation capacity, Lightsource BP is one of the world's
  leading renewable energy companies" (p21). Confirms/upgrades the developer lead from the 2022
  news article to a primary-document statement.
  Tab 9 "Description of Land: Not Applicable" (p26/p73) — same leased-land pattern as Hanson
  Solar precedent (23INR0086).
- **exhibit.py list/render** on the 154pp PDF found the vicinity/boundary maps at p28-32 (Tab 11:
  Maps) — rendered p6 (signature page), p28 (Tab 11 cover "Please See Attached"), p29 (aerial
  imagery, "Shaula Energy Project II, LLC" boundary in red over TWO non-contiguous polygons — a
  smaller NW parcel + larger SE parcel, both hatched "Proposed Reinvestment Zone-Shaula II"), p30
  (same boundary over an OSM-style road map, roads labeled **"Friar Rd"** and **"Cattle Guard
  Rd"**) — DECISIVE site-location artifact, recorded in site.map_artifacts.
  `gmaps.py places` geocodes: Friar Rd -> 29.096301,-97.159462; Cattle Guard Rd ->
  29.144234,-97.098752 (both DeWitt Co, TX) — consistent with "eastern DeWitt County" from Tab 4.
  Estimated project centroid (between the two named roads, matching the map's road layout):
  **~29.115, -97.13** (medium confidence — derived from named-road geocode + relative map
  position, NOT parcel-level precision; needs an imagery pass to refine against the actual
  boundary shape in p29/p30).
- **Tab 9 legal-description exhibit (Yoakum ISD Resolution Exhibit A, p147)**: 9 DCAD parcels,
  total **1,491.3 acres** — PIDs 1663/1664 (J W BOOTHE, 28.58+1.16ac), 5632 (W T DOWLEARN
  CHICOLETE RANCH, 55.5ac), 6430 (T C FORT CHICOLETE RANCH, 64ac), 7754 (M H GRANBERRY, 178.53ac),
  10694 (B W LUCAS CHICOLETE RANCH, 160ac), 13051 (JESSE E NASH CHICOLETE RANCH, 757.53ac), 14337
  (K C A PARK CHICOLETE RANCH, 65.3ac), 47659 (B DOOLITTLE, 180.725ac). All under "Chicolete
  Ranch"-family abstracts — consistent with the leased-ranchland pattern. This is a REAL, itemized
  parcel list with DCAD PIDs — strong evidence of a genuine site-specific filing, not boilerplate.
  project_area recorded as 1,491.3 ac (source: this exhibit).
- `gmaps.py staticmap` FAILS with HTTP 403 "Maps Static API not activated on this key" — tool
  limitation, not a project finding; noted so future runs don't retry it blind.
- `s2aws.py chip --lat 29.0963 --lon -97.1595` (Friar Rd geocode, 4km buffer, 2026-07-19 scene,
  cloud 29.6%) — imagery/s2_2026-07-15_friarrd.png: raw ranchland/pasture, NO clearing/grading/
  racking signature visible; matches the boundary-map road layout (Friar Rd running N-S through
  frame) but shows undisturbed vegetation. `chip --lat 29.09 --lon -97.14` (5km, covering the
  larger SE reinvestment-zone polygon) — imagery/s2_2026-07-15_se-parcel.png: also undisturbed,
  no solar signature anywhere in an ~8km wide window centered on the estimated site.
  `chip --lat 29.0963 --lon -97.1595 --date 2024-12-01` — too cloud-covered (54%) to judge, not
  used as evidence either way.
  **VERDICT: no_activity as of 2026-07-19** (scene date), ~14 months after the IA's amended
  In-Service Date (2025-04-25) and ~2 months after the amended Commercial Operation date
  (2026-05-30) already passed with zero visible construction.
- `search.py` sweep for Lightsource bp financing/construction announcements naming Shaula:
  "348 million financing" (2024-02) = **Starr Solar (163MW, Starr Co) + Second Division Solar
  (125MW, Brazoria Co)** — NOT Shaula. "380 million financing... 316 megawatts" (2021) = **Elm
  Branch + Briar Creek** — NOT Shaula, and predates Shaula's 2022 IA anyway. No search variant
  ("Shaula financing", "Shaula groundbreaking", "Shaula construction", "lightsourcebp.com
  Shaula") returns ANY financing/construction/groundbreaking announcement for Shaula I or II.
  Lightsource bp's own newsroom has never announced Shaula reaching financial close — a strong
  negative for a project whose contractual COD has already passed.
- **BP/Lightsource corporate headwind** (context, not site-specific): pv-tech.org 2025-02-27 —
  BP took full ownership of Lightsource bp in Oct 2024, then announced Feb 2025 a "reset"
  cutting renewables capex by $5B/yr (to $1.5-2B) under shareholder (Elliott Management)
  pressure, raising oil/gas capex $10B/yr instead. No Shaula-specific mention, but this is the
  parent's financial posture during the exact window Shaula II's amended schedule required
  design/procurement notice-to-proceed and security escalation (per the IA's Exhibit B/D dates).
  (sources: search.py results only, no HTML saved — WebFetch summary; log the query+URLs as the
  artifact per playbook rule 2.)

## D4/D5 — synthesis + wrap-up
- `search.py "Shaula Energy Project II LLC opencorporates Texas"` confirmed OpenCorporates listings
  exist for "Shaula Energy Project, LLC" and "Shaula Energy Project III, LLC" (siblings) but did not
  surface a live Comptroller taxable-entity status for 2026 — the only status snapshot obtained is
  from the 2022 Ch313 Exhibit J (ACTIVE, good standing, as of 2022-08-02). Live portal search
  (`mycpa.cpa.state.tx.us`) requires JS/session interaction, not reachable via plain curl POST —
  logged as a tool limitation, not re-attempted.
- `queue_history.py 22INR0267` → timeline.md: 79 monthly snapshots (2019-12 to 2026-06). DECISIVE:
  FIS never approved, meets_all_6.9 never achieved, construction start/end never reported despite
  IA signed 2022-04-27 (~4 years ago). Reported COD changed 6 times across the full history but has
  been frozen at 2026-05-30 since 2023-04 — unchanged for over 3 years, through and past its own
  due date.
- `eia_history.py 22INR0267 --write` → NOT in EIA-860M TX slice (confirms REFRESH_DIRECTIVE).
- `build_brief.py 22INR0267` → brief.html (10KB, 5 images, 16 sources). `build_index.py` → refreshed
  research/INDEX.md (173 projects).
- dossier.md written per DOSSIER_TEMPLATE.md; findings.json final pass done — verdict recorded as
  **unclear** (not paper, not real_active/real_early): the project cleared real legal/contractual
  gates (executed Ch313 agreement with a real ISD, signed IA, financial security posted, itemized
  9-parcel legal description) that a pure paper filing usually skips, but shows zero construction
  evidence, zero financing/groundbreaking announcements, and has now missed its own contractual COD
  by ~2 months with no observable activity. The determining unknown is Shaula I's status (both IA
  schedules are contractually 1:1 linked) — out of scope for this project's directory.
