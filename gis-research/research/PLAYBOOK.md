# Project Research Playbook

How to research one ERCOT queue project. Execute stages IN ORDER. Evidence first, opinion last.
Full design: `docs/superpowers/specs/2026-07-17-project-research-agent-design.md`.

## Inputs you get (identity packet)

Project name, INR, LLC name, county, MW, fuel/tech, POI description, zone — and the reported
COD **as a claim to verify, never as evidence**. You do NOT get milestone data. Do not go
looking for it: your job is independent ground truth.

## Hard rules

1. **BANNED SOURCES** — these republish the ERCOT GIS report; citing them as evidence is an
   automatic fail: interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, infrasure.ai, futuregrid.io, any
   "interconnection queue tracker". You may not use them even for orientation.
2. **Artifacts or it didn't happen.** Every claim in findings.json must reference a saved file
   in `sources/` or a URL + verbatim quote. Save documents with `curl` as
   `sources/<YYYY-MM-DD>_<source>_<desc>.<ext>`.
3. **Log negative evidence.** Every search that returns nothing goes in `log.md`:
   source, exact query, date, result. "Nothing found" is a finding.
3b. **Write as you go.** Append every significant find to `log.md` THE MOMENT you make it
   (fact + artifact path + 1-line why it matters). Your context may be compacted at any
   time — anything not on disk is lost. Never hold findings "for the dossier later".
4. **No county centroids.** A lat/lon without a derivation method (parcel, Places pin,
   imagery feature, news photo, POI infrastructure) is invalid.
4b. **Save the map you derived the site from.** Whenever a filing document contains a
   parcel/boundary/improvements map (Ch.313 exhibit, IA exhibit, TCEQ permit map, CAD
   parcel) that you used — or could use — to locate the site, extract that page to
   `sources/<doc>_map_pNN.png` and list every such image in findings.json under
   `site.map_artifacts: ["sources/..."]`. The human brief renders these beside the
   satellite frames so a reviewer can verify the fix; this matters MOST when construction
   has not started or the parcel is unverified — the map is then the only site evidence.
5. Write ONLY inside your assigned project directory.

## Deep scan v2 — stages (each stage ENDS with a findings.json checkpoint write)

D0 CHECKPOINT ZERO: write findings.json skeleton (every schema key, null values)
   BEFORE any research. Read factsheet.json/md + triage_findings.json + inventory
   sources/ — IA PDFs are usually already there (verified_* naming; never cite
   unverified_* without eyeballing the parties page).
D1 IA SCHEDULE: extract the milestone-schedule exhibit from each IA document on disk
   (In-Service / Trial Op / COD dates, financial security) → contractual_schedule
   (one row per document — amendments change amounts). If no IA on disk, run the
   systematic ladder (below) once — do not loop.
   MANDATORY: `uv run gis-research/scripts/research_tools/exhibit.py scan <proj_dir>`
   — every agreement PDF's map/exhibit pages get rendered (`exhibit.py render <pdf>
   -p N,M`) and READ before you form any site hypothesis. Attachment C-3 / Exhibit B
   style maps carry the site with road names; guessing a location while such a map
   sits in sources/ is an automatic quality failure. Record rendered pages in
   `site.map_artifacts`. DOWNLOAD every linked agreement document (application,
   agreement, FINDINGS) — a URL in a note is not an artifact. For a big or scanned
   PDF, do NOT Read it page-by-page: `exhibit.py sheet <pdf>` tiles 4 pages/image +
   writes an .md index — read the index, then only the tiles you need (~4x fewer
   tokens).
D2 SITE + IMAGERY: fix coordinates (factsheet EIA coords are a candidate, not truth);
   cdse.py chips, ≤6 image reads total; save boundary-map pages → site.map_artifacts.
D3 GAP-FILL: county records/news for what the factsheet couldn't answer — local tools
   first (spv.py, ch313/faa/tceq, search.py), web last.
D4 NARRATIVE: independent COD + drift verdict + confidence; write dossier.md.
D5 DETERMINISTIC WRAP-UP (in order): queue_history.py <INR> → eia_history.py <INR>
   --write → build_brief.py <dir> → build_index.py. Then a final findings.json pass.

The detail sections below (Stage 1–5, retained for reference) are what D1–D5 draw on:
the systematic IA ladder + registry tools + fuel paper trails (Stage 2), site pinpoint
techniques (Stage 3), CDSE imagery discipline (Stage 4), and the dossier + wrap-up
specifics (Stage 5).

## Stage 1 — LLC → parent chain

The LLC is a shell; find who's behind it.
- TX Comptroller **taxable entity search** (free): https://mycpa.cpa.state.tx.us/coa/ —
  registered agent, officers, mailing address. Shared mailing address/agent across projects
  = same developer.
- TX SOS filings if surfaced via web search; press releases, developer project pages,
  LinkedIn posts (project name + "solar" + county), PPA announcements.
- Output: chain like `Hanson Solar, LLC → <DevCo> → <Parent>` with evidence per hop.

## Stage 2 — County records sweep

County is known. Work it hard — this is where real projects leave paper.
- **CAD (county appraisal district) parcel search by owner name** = the LLC and variants.
  Find the county's CAD portal (search "<county> county appraisal district property search").
  Owner-name search → parcel IDs, acreage, situs, land value. Save result pages.
- **Tax abatements**: TX Comptroller Ch.312/313/JETI registries; county commissioners-court
  minutes/agendas (search "<county> commissioners court minutes <project/LLC name>").
  Abatement agreements bury exact tract descriptions, investment amounts, construction
  schedules — read the PDFs, don't skim titles.
- School-district (ISD) Ch.313/JETI agreements name the project precisely (comptroller site).
- TCEQ permits only if fuel type needs them (solar usually none — absence is expected,
  not evidence of paper project).
- **PUCT Interchange — use `puct.py match`, never raw WebFetch** (the portal rate-limits
  ad-hoc fetches to HTTP 402). The signed IA is primary evidence: parties, POI, financial
  security, and the milestone-schedule exhibit (In-Service / Trial Op / COD dates).
  Background: ALL TSPs (Oncor, ETT, CenterPoint, AEP, LCRA, TNMP, …) file executed IAs as
  informational filings in ONE central docket — control 35077 (Subst. R. §25.195(e));
  `FilingParty=<project>` always returns 0 (the filing party is the TSP). The queue's
  iaSigned date is self-reported and often stale — never use dates as a join key.
  THE SYSTEMATIC LADDER (stop at the first rung that yields CONFIRMED/PROBABLE):
  1. `uv run gis-research/scripts/research_tools/puct.py match <INR> --dir <sources/>`
     — automatically checks the INR join table first (rung 0 — exact match, from
     `inr_harvest.py`'s docket↔INR index) before falling back to name keys — local
     docket index, exact name keys (queue + triage spv_name/developer), verification
     by INR-in-PDF (CONFIRMED) or county+MW-in-PDF (PROBABLE). Files it can't verify
     get an `unverified_` prefix — never cite those without eyeballing the
     parties/POI page yourself.
  2. SPV discovery, then re-match: FIRST `spv.py resolve <INR>` (systematic: EIA-860M
     entity/coords/status + PUCT docket-index parties — local + instant; the bulk table
     research/_reference/spv_candidates.csv has pre-computed candidates); if that is dry,
     run the FUEL-SPECIFIC REGISTRY TOOL (same conventions as puct.py; `resolve` is
     read-only and agent-safe; every candidate is a LEAD, never a conclusion):
       - wind  → `uv run gis-research/scripts/research_tools/faa.py resolve <INR>` —
         OE/AAA per-turbine cases: sponsor (= SPV), ASN block, filing year, turbine
         centroid. NOTE live FAA sources blocked as of 2026-07 (private Socrata + govt
         shutdown) — runs off cached pulls; a miss prints deep-links, log the negative.
       - solar/storage → `uv run gis-research/scripts/research_tools/ch313.py resolve
         <INR>` (also `--name "<text>"` / `--county <name>`) — Ch.313 (pre-2023) or JETI
         (2024+) value-limitation applicant = the legal SPV + application PDFs. Lists key
         on SCHOOL DISTRICT, not county — name match is primary.
       - gas/thermal → `uv run gis-research/scripts/research_tools/tceq.py resolve <INR>`
         (or `--county <name> --keyword <text>`) — TCEQ air-permit (AIRNSR) facility +
         owner legal names in the county. Same-named facility may be a co-located
         PREDECESSOR (different owner); permit# and owner are not paired.
     Still dry: TX SOS / Comptroller taxable-entity search / county records / news.
     Then `puct.py match <INR> --key "<SPV legal name>" --dir <sources/>`.
     Record the SPV in findings regardless — codename projects ("Operation Sunshine") and
     variant spellings (queue "Shepard" = filed "Sheppard") are the #1 miss cause.
  3. Last resort, judgment call: `puct.py filings 35077 --party <TSP fragment>` or a
     bounded window listing, and eyeball descriptions for the SPV. Treat any hit like a
     rung-2 candidate: fetch, then verify against INR/county/MW before citing.
  Amendments matter: security amounts and schedules change — fetch ALL amendments
  (match downloads every candidate filing), record per-document in `contractual_schedule`.
- **Project area**: abatement applications, IA exhibits, and CAD parcels state acreage —
  capture it in findings.json as `project_area` `{acres, source, artifact}`. The reviewer
  uses it to sanity-check the imagery footprint against the docs.
- **Fuel-specific paper trails** (a missing MANDATORY doc is strong paper-project evidence):
  gas/thermal MUST have a TCEQ air permit (NSR) — `tceq.py resolve <INR>` — plus water
  supply; "(TEF …)" in the project name = Texas Energy Fund loan → check the PUCT TEF
  docket. Wind: FAA OE/AAA obstruction filings carry exact turbine coordinates —
  decisive, `faa.py resolve <INR>` early. Battery: thin county trail (little land) —
  lean on the IA, substation work, and developer PRs. Solar: `ch313.py resolve <INR>`
  (Ch.313/JETI applicant + application PDFs) + CAD as written above.
- Output: parcels + acreage + any abatement/permit docs saved to `sources/`.

## Stage 3 — Site pinpoint

Converge on lat/lon from independent angles; state your method + confidence.
- **Delivery-pin trick (do this FIRST — cheap, often decisive):**
  `uv run gis-research/scripts/research_tools/gmaps.py places "<project name>"` and variants
  ("<name> construction", "<name> site", "<LLC name>", "<EPC name> <project>"). Construction
  sites register Google pins so delivery drivers can find the gate. A pin with an FM road
  address in the right county is gold.
- POI description names real infrastructure (switches/lines). Cross-reference OpenInfraMap
  (openinframap.org) / news for switch locations; the site is within a few miles of its POI tap.
- Parcel situs/geometry from Stage 2.
- News/groundbreaking photos, drone footage captions.
- Cross-check: pin ↔ parcel ↔ POI should agree. Disagreement = investigate, don't average.
- Output: lat/lon (5 decimals), method, confidence, cross-check notes.

## Stage 4 — Satellite ground truth

- `uv run gis-research/scripts/research_tools/cdse.py chip --lat <lat> --lon <lon>
  --date <YYYY-MM-DD> --out imagery/s2_<date>.png` — Sentinel-2 true color, ~3 km box.
- **Search TIGHT, present WIDE (search rule):** wide frames dilute the signal — a solar
  site is unmistakable at 2-3 km buffer and nearly invisible at 12 km. To SEARCH: grid of
  small chips (`--buffer-km 2`), stepping ±0.03° around the estimated location; build ONE
  contact sheet of the grid and read THAT to find the site. The xwide (6 km) view is for
  the final `imagery/key/` reviewer frames ONLY, after the site is found.
- **Look around before concluding:** the pin is usually the site GATE or office, not the
  array centroid — a 600 MW site spans ~10 km. Activity at a frame edge/corner → RE-CENTER
  and re-chip. Nothing at the estimate → widen the grid before concluding no_activity.
  Never judge a big project from one centered frame.
- **Hard cap: read ≤6 full-size frames per project.** Everything else is judged from
  contact sheets. Every full-size image you read is re-read from cache every turn after —
  image bloat is the #1 cost driver.
- **Present-first, early-exit (efficiency rule):**
  1. Pull TODAY's chip first.
  2. Raw farmland, no activity → pull ONE chip ~6 months back to confirm, then STOP.
     Verdict `no_activity`; do not scan history looking for nothing.
  3. Activity visible (clearing/racking/complete) → ONE `timelapse` job to bracket
     `first_activity_seen`:
     `uv run gis-research/scripts/research_tools/cdse.py timelapse --lat <lat> --lon <lon>
      --start <~2y back> --end <today> --out-dir imagery/ --cadence month`
     (single openEO job → dated monthly frames + timelapse.gif; far cheaper than per-date chips)
  4. Construction ACTIVE now (not yet complete) → also `timelapse --cadence dekad` over the
     last ~2-3 months (10-day frames) — progress velocity feeds the COD estimate.
  Cloud filter is per-scene, so some frames stay partly cloudy — judge from the clear ones.
- **Context economy:** don't read every frame individually. Build a contact sheet
  (`cdse.py sheet --dir imagery/ --out imagery/contact_sheet.png`) = one image containing all
  dated thumbnails; read THAT to spot the transition, then read only the 2-4 decisive frames
  full-size. All imagery defaults to the 6 km "xwide" view (~1200px, 10 m/px).
- Fetch several specific dates concurrently with `cdse.py chips --dates d1,d2,… --out-dir
  imagery/key/` — put the 3-5 frames a human should see (pre / first-activity / latest) in
  `imagery/key/`; brief.html embeds them. GIF is not used in the human brief.
- READ the images yourself (you are multimodal): mottled farmland → graded rectangles =
  clearing; regular dark rows = racking/modules; substation square near POI = late stage.
- **Fuel-specific signatures at 10 m/px:**
  - Solar: sharp-edged tan graded polygons → uniform dark blue-gray module blocks;
    100 MW ≈ 500-900 acres — big, unmistakable when present.
  - Battery: COMPACT — 10-80 acres even at 1 GW. Pale gravel pad + parallel container
    rows beside a substation. Search 1-km-buffer chips around the POI substation; a
    county-scale grid will scan right past it. Build is fast (~12-18 months) — bare
    ground today can still make a near COD.
  - Wind: no single polygon — strings of small turbine pads + new access roads across
    tens of km. Grid wide, look for pad strings/road networks; FAA filings give coords.
  - Thermal (gas): one industrial site — laydown yard, cranes, turbine hall, cooling
    structures; multi-year build, usually near pipelines / existing industry.
- `uv run gis-research/scripts/research_tools/gmaps.py staticmap --lat <lat> --lon <lon>
  --out imagery/map_site.png` — site-highlighted map image for the dossier.
- Output: dated chip series + verdict: no_activity | clearing | racking | substantially_complete | operating.

## Stage 5 — Synthesis (only now)

Write `dossier.md` + `findings.json` (schema in the spec §5). Verdict real/paper, construction
stage, independent COD (month precision) + drift risk vs the reported-COD claim.
findings.json must also carry `project_area` `{acres, source, artifact}` and
`contractual_schedule.documents` — one entry per IA document
`{doc, signed, financial_security, artifact}`; security amounts often rise with amendments,
so record them per document, never as one number. Every
sentence traceable to stages 1-4 artifacts. Unknowns stay unknown — honesty over coverage.

**Dossier: follow `research/DOSSIER_TEMPLATE.md` EXACTLY** (section order, tables, style).
Reference example: `research/23INR0086_hanson-solar/dossier.md`. Core rules: ≤ ~60 lines,
bullets not prose, EVERY claim inline-linked to a `sources/` artifact or URL, no methodology
narration (log.md has that), one honest "could not determine" section at the end.

**Deterministic wrap-up (run these, don't hand-write their outputs):**
1. `uv run gis-research/scripts/research_tools/queue_history.py <INR>` — full milestone/COD-drift
   timeline from the local parquet (all monthly reports since 2014). Read `timeline.md`; cite the
   COD-drift history in your assessment.
2. `uv run gis-research/scripts/research_tools/eia_history.py <INR> --write` — the EIA-860M
   second source: what the entity reports to EIA monthly (planned COD / status / capacity),
   independent of the developer's queue claims. Divergence between the two histories is
   decisive COD-drift evidence — cite it. "NOT in EIA-860M" is negative evidence; log it.
3. `uv run gis-research/scripts/research_tools/build_brief.py <INR>` — one-page brief.html
   (renders the EIA second-source tables automatically when eia_history.json exists).
4. `uv run gis-research/scripts/research_tools/build_index.py` — refresh the research index.
