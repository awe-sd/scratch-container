# Project Research Playbook

How to research one ERCOT queue project. Execute stages IN ORDER. Evidence first, opinion last.
Full design: `docs/superpowers/specs/2026-07-17-project-research-agent-design.md`.

## Inputs you get (identity packet)

Project name, INR, LLC name, county, MW, fuel/tech, POI description, zone — and the reported
COD **as a claim to verify, never as evidence**. You do NOT get milestone data. Do not go
looking for it: your job is independent ground truth.

## Hard rules

1. **BANNED SOURCES** — these republish the ERCOT GIS report; citing them as evidence is an
   automatic fail: interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, any
   "interconnection queue tracker". You may not use them even for orientation.
2. **Artifacts or it didn't happen.** Every claim in findings.json must reference a saved file
   in `sources/` or a URL + verbatim quote. Save documents with `curl` as
   `sources/<YYYY-MM-DD>_<source>_<desc>.<ext>`.
3. **Log negative evidence.** Every search that returns nothing goes in `log.md`:
   source, exact query, date, result. "Nothing found" is a finding.
4. **No county centroids.** A lat/lon without a derivation method (parcel, Places pin,
   imagery feature, news photo, POI infrastructure) is invalid.
5. Write ONLY inside your assigned project directory.

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
- **PUCT Interchange filings search** (https://interchange.puc.texas.gov/search/filings/):
  search by project LLC / project name. Interconnection agreements between the transmission
  provider (Oncor, AEP, LCRA, …) and the project LLC are filed here — free primary documents
  naming parties, POI, and sometimes schedule exhibits. (This is the signed IA itself —
  primary evidence, unlike queue aggregators.)
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
- READ the images yourself (you are multimodal): mottled farmland → graded rectangles =
  clearing; regular dark rows = racking/modules; substation square near POI = late stage.
- `uv run gis-research/scripts/research_tools/gmaps.py staticmap --lat <lat> --lon <lon>
  --out imagery/map_site.png` — site-highlighted map image for the dossier.
- Output: dated chip series + verdict: no_activity | clearing | racking | substantially_complete | operating.

## Stage 5 — Synthesis (only now)

Write `dossier.md` + `findings.json` (schema in the spec §5). Verdict real/paper, construction
stage, independent COD (month precision) + drift risk vs the reported-COD claim. Every
sentence traceable to stages 1-4 artifacts. Unknowns stay unknown — honesty over coverage.
