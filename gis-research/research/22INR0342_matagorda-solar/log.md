# Triage log — Matagorda Solar (22INR0342)

## T1 start
- queue_history.py ran: 67 snapshots, 2020-12-01 → 2026-06-01
- COD drift: 4 changes (2023-06 → 2023-12 → 2025-12 → 2026-08 → 2027-08); current claim 2027-08-25
- MW: started 80.6, bumped to 101.0 at 2021-04
- Milestones: Screening started 2020-05, complete 2020-07, FIS requested 2020-11, FIS approved 2021-09, IA signed 2022-06-08, Meets 6.9(1) 2025-02-12
- Construction start/end: NOT reported; Meets all 6.9: NOT achieved; energization/sync/COA: NOT achieved
- T1 result: IA signed (2022-06), partial 6.9, no construction milestones, COD slipped 4 times over ~4 years

## T2 start
- gmaps.py: 429 Too Many Requests on all 4 attempts (exact name, name+county, name+LLC, name+solar) — rate-limited, one retry each = budget exhausted
- T2 result: 0 pins found (API blocked, not a project signal)

## T3 start
- DDG search 1 "Matagorda Solar Texas news": hits on cleanview.co, infrasure.ai (developer=Leeward Renewable Energy Development LLC), ercotqueue.com (SPV="Matagorda Solar Farm LLC", build-chance 86%), interconnection.fyi
- DDG search 2 "Matagorda Solar LLC registration": Utah-based foreign LLC registered TX 2021-01-25; SLC UT address (201 S Main St Suite 2000/2100); CT Corp registered agent; prior CEO Luigi Resta
- DDG search 3 "Leeward Matagorda construction/announcement": no press releases, no construction announcements found
- Sibling project note: Leeward also had 22INR0441 Milwaukee Solar (201.5 MW, same county) — WITHDRAWN
- Developer confirmed: Leeward Renewable Energy Development, LLC (Salt Lake City)
- No news/PR pages directly about this project to save beyond infrasure reference
- T3 result: developer identified (Leeward), no construction news, no announcement found

## T4 start
- PUCT Interchange portal (interchange.puc.texas.gov): HTTP 402 on root, FilingParty search, and description search — blocked, one retry per attempt = budget spent
- T4 result: IA exists (queue milestone confirmed 2022-06-08) but PUCT portal inaccessible; IA PDF not retrieved; schedule exhibit unknown
- NOTE: IA existence confirmed via ERCOT queue data, but PUCT filing content not accessible this run

## T5 start
- TX Comptroller Ch.313 page: no searchable database accessible via web; Ch.313 expired end-2022 so post-2022 projects ineligible anyway
- JETI registry: no searchable online database found; JETI is post-2022 replacement for Ch.313
- Project entered queue 2020, IA signed 2022 — could have filed Ch.313 before expiry; no confirmation found
- T5 result: no abatement confirmed (normal for this vintage + no accessible online db)

## T6 start
- POI: "5555 Shropshire 69kV" — searched DDG, Nominatim OSM, ERCOT network docs: Shropshire 69kV substation not found in any database
- Nominatim returns Shropshire Boulevard (Austin/Travis County) and Shropshire Lake Dam (McCulloch County) — neither near Matagorda County
- T2 pins: none (gmaps blocked); T4 IA map: not retrieved (portal blocked)
- Site candidate: only "somewhere in Matagorda County" — below threshold for imagery
- T6 result: SKIP imagery per checklist ("no site candidate")

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~22 of 35 budget
- T7 complete — STOP

## D0 start (deep scan, 2026-07-20)
- Read PLAYBOOK.md, DOSSIER_TEMPLATE.md, Hanson reference dossier+findings.json, triage
  artifacts, factsheet.json.
- **CAUTION — banned source in triage sources/**: `sources/infrasure_22INR0342.txt` was saved
  during triage from infrasure.ai (a banned queue-aggregator per PLAYBOOK rule 1). NOT usable
  as evidence in this deep scan; kept on disk only as a triage artifact, not cited.
- **False-match IA PDFs discovered in sources/**: the two `unverified_2026-07-19_puct_35077-2315_*`
  PDFs (from a prior `puct.py match` run) are actually the CenterPoint–Peyton Creek Wind Farm II,
  LLC SGIA + Amendment One (INR 20INR0155, filed 2025-11-24, Control No. 35077 Item 2315) — a
  DIFFERENT project, also in Matagorda County (wind, not solar), which is why the county-name
  match fired. Verified via pypdf full-text extract: 0 hits for "22INR0342", "Leeward",
  "Shropshire"; "Matagorda" appears only in "Peyton Creek Wind Farm II, Matagorda County, Texas".
  DO NOT cite these as Matagorda Solar's IA. Will re-run puct.py match fresh for this INR.
- factsheet.json confirms: IA signed 2022-06-08, fisApproved 2021-09-14, financial_security=Yes,
  paper_score 48 (deep_candidate, priority 7.66), SPV unresolved, EIA not_in_eia, 4 COD slips.
- findings.json skeleton written (all null/empty per schema).

## D1 — systematic ladder (2026-07-20)
- `puct.py match 22INR0342` fresh: only candidate by exact name key is 35077-2315 = SAME
  Peyton Creek Wind Farm II filing (INR-in-text check correctly returns UNCONFIRMED both
  times). Tried `--key "Matagorda Solar Farm"` too — identical single candidate. No IA for
  this project exists in the local docket index under any name key tried.
- `spv.py resolve 22INR0342`: no systematic candidate (dry — no EIA-860M hit, no docket-index
  non-TSP-party hit).
- `ch313.py resolve 22INR0342` (+ `--county Matagorda`, `--name Tidehaven`): NEGATIVE — no
  Ch.313/JETI applicant matches "Matagorda Solar", nor the Tidehaven ISD district filter.
  Manual scan of the full 740-row local table for Matagorda-adjacent solar Ch313 filings
  found only: Danish Fields Solar LLC (Tidehaven ISD, app 2020) and HIF USA LLC (Tidehaven
  ISD, app 2021) — neither name overlaps "Matagorda Solar"/"Leeward". Danish Fields'
  district match is coincidental (Tidehaven ISD spans multiple counties incl. Matagorda);
  not pursued further without a name/MW tie.
- `tceq.py resolve 22INR0342 --county Matagorda --keyword "Matagorda Solar" --storm`:
  13 facilities / 23 storm-water NOIs in Matagorda Co, NONE named Leeward/Matagorda Solar;
  owner list (16 names) has zero overlap with the developer or SPV — no construction-started
  proof via this route.
- Web search "Leeward Renewable Energy Matagorda Solar Texas" surfaced
  baycitytribune.com "Tidehaven looks to add to tax base" (2021-04-13,
  [artifact](sources/2026-07-20_baycitytribune_tidehaven-tax-base.html)): Leeward Ch.313
  application to Tidehaven ISD for a **200 MW / 2,000-acre / $157.5M** solar farm, construction
  targeted "first part of 2023". **This does NOT match 22INR0342 (101 MW)** — capacity and
  acreage are ~2x. Almost certainly describes the SIBLING project 22INR0441 "Milwaukee Solar"
  (201.5 MW, same county, same developer, per triage) which the triage log recorded as
  WITHDRAWN. Logged as negative evidence for 22INR0342 specifically; confirms Leeward was
  active in Matagorda Co. circa 2021 but the paper trail found so far belongs to the
  withdrawn sibling, not this project.
- Web search "gem.wiki Eldora solar farm" (from a broader search) — Matagorda County, 200 MW,
  owner Advanced Power AG / operator Eldora Energy, commissioning 2027 (planned). Different
  owner, different capacity — NOT a match for 22INR0342. Negative evidence, not pursued.
- No Ch.313/JETI, no TCEQ storm NOI, no docket filing anywhere ties an SPV/IA specifically to
  101 MW "Matagorda Solar" (22INR0342) as distinct from its 200 MW sibling. This is a material
  finding: the ONLY IA-adjacent paper for "Matagorda Solar/Leeward" in Matagorda Co. found so
  far belongs to a different, withdrawn project.
- Cross-checked sibling 22INR0441 "Milwaukee Solar" via `queue_history.py`: only 11 monthly
  snapshots (2021-03 → 2022-01), never signed IA, screening/FIS-requested only, then dropped
  from the queue — matches "withdrawn" note from triage. The 2021-04-13 Tidehaven ISD 200 MW /
  $157.5M Ch313 application ([artifact](sources/2026-07-20_baycitytribune_tidehaven-tax-base.html))
  is almost certainly this withdrawn Milwaukee Solar project, NOT 22INR0342 — confirms our
  101 MW target has a SEPARATE (and so far undiscovered) paper trail from its cancelled sibling.
- `gem.wiki/Eldora_solar_farm`: 200 MW Matagorda Co project, owner Advanced Power AG / operator
  Eldora Energy — different owner, different capacity. NOT a match. Negative evidence.
- `solarpowerworldonline.com` "Leeward completes 200-MW Texas solar project" (2024-04): page
  blocked by Cloudflare, could not retrieve; likely also about the 200 MW sibling given the
  MW figure — not pursued further (200≠101).
- **Shropshire 69kV substation still unlocatable** (D2 blocker carried over from triage):
  - `search.py` variants ("AEP Texas Shropshire switch/substation", "Shropshire switching
    station", exact "5555 Shropshire" quoted): no hits naming a real Shropshire substation/
    switch in Texas; recurring irrelevant PUCT doc (35077-175, fetched+checked, = old AEP FERC
    "Pharr/Markham Tie" tariff sheet, Matagorda mention is Markham Tie Line 1.5mi off Hwy 35 —
    NOT Shropshire, deleted from sources/ as off-target).
  - Nominatim `Shropshire, Texas` / `Shropshire, Matagorda County, Texas`: only hits are
    Shropshire Lake Dam (McCulloch Co.), Shropshire Blvd/Dr/St/Ct (Austin/San Antonio/Ft
    Worth/Keller) — none in or near Matagorda County.
  - `gmaps.py places` blocked again (HTTP 429, same as triage) — API still rate-limited from
    this container/key.
  - openinframap.org unreachable (curl empty response, code 000).
  - Matagorda CAD portal (esearch.matagorda-cad.org): JS-heavy True Automation-style portal
    requiring session tokens for any search — no simple GET query string works; not pursued
    further given diminishing returns (web-last rule).
  - `puct.py filings 35077 --party <TSP>` swept across AEP, CenterPoint, Oncor, LCRA, TNMP,
    Entergy: zero filings anywhere in docket 35077 mention "Matagorda", "Leeward", or
    "Shropshire" in the FilingDescription text (AEP alone has ~60 solar SGIA filings 2013-2026,
    none of them this project). This is decisive: **no signed IA for 22INR0342 exists in the
    local docket-35077 index under any TSP or name key**, despite the ERCOT queue's own
    `iaSigned=2022-06-08` milestone claim.
  - Cross-checked the permanent rung-0 join table (`_reference/puct_inr_join.json`, 1,743
    docket items with extracted INR strings) and the pre-computed `_reference/spv_candidates.csv`
    (772 rows) directly by grep/JSON-scan: **zero occurrences of "22INR0342" in either file.**
    This project has NEVER been matched to a docket filing by the systematic harvest, which
    has ingested every docket-35077 PDF since 2018 — strong independent corroboration that
    the queue's iaSigned claim has no discoverable paper trail.
  - Other Matagorda County solar leads surfaced and ruled out as NOT this project (different
    owner/capacity/name): Eldora Energy / Advanced Power AG (200 MW, gem.wiki), Midfield Solar
    and Storage LLC / Hanwha Q Cells ($260M, baycitytribune 2024-07-23), Apex Matagorda Energy
    Center (EPA doc, gas peaker not solar), Industrial Sun / LyondellBasell Matagorda Complex
    (50 MWac, industrial rooftop-scale, different sponsor).
  - Matagorda County EDC "Current Projects" page (mcedc.net, current as of Q1 2026): zero
    mentions of "solar" or "Leeward" at all — county's own public project list is silent on
    this project.
  - `gmaps.py places` retried twice more (direct project name, direct "Shropshire substation
    Texas") — still HTTP 429 both times. Fleet-wide API rate limit, not a project signal;
    genuinely inconclusive (not "no pins found", but "could not check").
  - ERCOT node/settlement-point search and UK "Shropshire" renewable-energy hits confirm: no
    real Texas infrastructure named "Shropshire" is discoverable through any public channel
    tried. Site location is UNRESOLVED for this run.

## D3/D4 — decision to stop chasing site, synthesize (2026-07-20)
- `eia_history.py 22INR0342` (dry + `--write`): confirms factsheet — NOT in EIA-860M TX slice.
  No eia_history.json written (tool only writes on a match).
- Exhausted the reasonable systematic ladder for both SPV/IA discovery and site location within
  budget. Per PLAYBOOK rule 4 (no county centroids), did NOT fabricate a placeholder lat/lon —
  no imagery pulled this run.
- Verdict lands as **unclear** rather than paper/real_active: the queue's own iaSigned +
  financial-security flags are non-trivial (posting security costs real money) and argue against
  pure vaporware, but the total absence of ANY independent corroboration (docket text, join
  table, SPV table, Ch313/JETI, TCEQ, EIA, news, site) after an exhaustive multi-tool sweep is
  itself a strong, decisive negative signal that a "real_active" verdict would not be honest.
- dossier.md, findings.json written per template/schema.

## D5 — deterministic wrap-up
- `queue_history.py 22INR0342` -> timeline.json/timeline.md (67 snapshots, 4 COD changes)
- `eia_history.py 22INR0342 --write` -> NOT in EIA-860M, no file written (expected, tool
  behavior for a non-match)
- `build_brief.py 22INR0342` -> brief.html (7 KB, 0 images, 4 sources) — re-run after final
  findings.json edit
- `build_index.py` -> research/index.json + INDEX.md refreshed (171 projects)
- STOP — deep scan complete.

## Second-pass user review (2026-07-20)

**User complaint:** missing parcel/images, ch313 missing.

- **Ch.313 was already checked in D1** (`ch313.py resolve 22INR0342` + `--county Matagorda` +
  `--name Tidehaven`): genuinely negative, with the two nearby district matches (Danish
  Fields Solar, HIF USA) individually ruled out by name. Not a gap -- the brief's "no Ch.313"
  is a checked negative, not a missed lookup.
- **Site/parcel remains genuinely unresolvable**: D1 already exhausted Nominatim, gmaps
  (rate-limited both triage+deep), openinframap, the Matagorda CAD JS portal, a full
  `puct.py filings --party` sweep across every TSP in docket 35077, the permanent
  docket<->INR join table, and the pre-computed SPV-candidates table -- 24 negative
  searches total. Per PLAYBOOK rule 4, no placeholder/county-centroid coordinate was used,
  so no imagery could be pulled (correctly) -- there is nothing to fix here without a real
  site lead, which none of the systematic tools produce for this INR.
- **Banned-source cleanup**: deleted `sources/infrasure_22INR0342.txt` (infrasure.ai,
  banned queue-aggregator per PLAYBOOK rule 1) -- it was never cited as evidence in
  findings.json/dossier.md, but the raw file should not have been left on disk. Brief
  rebuilt (3 sources, was 4).
- **New bounded check**: OpenCorporates has a "Matagorda Solar LLC" TX registration
  (us_tx/0803913885) -- NOT the same name as the "Matagorda Solar Farm LLC" SPV name
  surfaced via ercotqueue.com in triage. Detail page blocked by an anti-bot challenge;
  could not confirm registered agent/address to tie it to this INR specifically. Logged as
  an unconfirmed lead, not cited as evidence.
- Verdict remains **unclear** -- this is the correct, well-evidenced state for this project,
  not an artifact of a rushed or incomplete run.
