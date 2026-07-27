# Dossier — Chisme Solar (24INR0333)

Researched 2026-07-20 · site 31.5689, -98.8220 · verdict **real_early**

## 1. Verdict

- **real_early** — signed, financially-secured IA's Scheduled COD (Apr 13, 2027) exactly matches the queue claim ([IA Exhibit B](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf)); a Ch.312 abatement application and county-published fact sheet independently confirm site, acreage, and schedule ([fact sheet](sources/2026-07-20_millscountytx_chisme-fact-sheet.pdf))
- Construction: **under construction (≤50% complete), not visually verified** — EIA-860M's own status field flips from "not under construction" to "under construction" between the 2026-03 and 2026-04 snapshots ([eia_history.json](eia_history.json)); CDSE imagery and Google Maps Static API were both unavailable this run (account credits / API not enabled) so no visual confirmation was possible
- Site: 31.5689, -98.8220 — 3-source convergence (EIA-860M plant coords, "Gobblers Knob" named terrain feature, GIS-precision project-boundary maps in the county abatement filing), high confidence ([satellite view](https://www.google.com/maps/@31.5689,-98.8220,5000m/data=!3m1!1e3))
- COD: reported 2027-04-13 → independent **2027-Q2**, drift risk **medium** (contractually grounded by 3 sources but abatement rejected + no visual construction confirmation)

## 2. Site identification

- Derivation: POI text ("Gobbers Knob Switch" on Oncor's 345kV Brown Switch–Buckhorn Switch line, [IA Exhibit C](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf)) → cross-referenced to "Gobblers Knob," a named summit in Mills County (31.5640, -98.8192, [hometownlocator](https://texas.hometownlocator.com/maps/feature-map,ftc,1,fid,1358108,n,gobblers%20knob.cfm)) → matches the independent EIA-860M plant registration (31.56893, -98.82195, factsheet.json) within 0.6 km
- **Stated project area: 720 acres** per [company fact sheet](sources/2026-07-20_millscountytx_chisme-fact-sheet.pdf) ("sited on approximately 720 acres in a remote area away from residences"); imagery footprint consistent? **unverified** (no imagery obtained this run)
- Cross-checks (each linked): GIS-precision project-boundary polygon over topo + aerial basemaps in the [Mills County Ch.312 abatement application](sources/2026-07-20_millscountytx_red-river-abatement-application.pdf) (pp. 5-16) places the site in NW Mills County immediately east of the historic Camp Bowie tract, south of the Brown/Mills line, between Brownwood and Goldthwaite — agrees with the fact-sheet vicinity map and the EIA/Gobblers Knob coordinate cluster within ~1-2 km
- Not obtainable: exact Gobbers Knob Switch coordinates (redacted/blacked out in IA Exhibit C text as CEII); Sentinel-2/static-map imagery (CDSE 402 "insufficient credits," gmaps 403 "Maps Static API not activated" — both infra failures, not site issues)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Blue Heron Solar, LLC | SPV | party on [IA](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf), Exhibit C; applicant on [Ch.312 application](sources/2026-07-20_millscountytx_red-river-abatement-application.pdf) |
| Red River Clean Energy | developer/parent | IA Exhibit D notice/EFT addresses; explicitly named "parent company" in [Ch.312 application](sources/2026-07-20_millscountytx_red-river-abatement-application.pdf) item 2; matches EIA-860M entity name exactly (factsheet.json) |
| Concord New Energy | possible ultimate parent (unconfirmed) | IA Exhibit D billing email domain `accounting@concordnewenergy.com` under Blue Heron's own contact block — lead only, not corroborated independently |
| Open Doors Public Relations (Bill Pentak) | PR/spokesperson | contact on [fact sheet](sources/2026-07-20_millscountytx_chisme-fact-sheet.pdf); presented to Mills County court per [CitizenPortal](sources/2026-07-20_citizenportal_mills-county-rejects-blue-heron-abatement.html) |

- Financing: not disclosed; $15,842,206 Irrevocable Standby Letter of Credit posted to Oncor as interconnection security effective on/before Dec 6, 2024 ([IA Exhibit E](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf)) — a real financial commitment, not proof of full project financing

## 4. Land & county records

- Tenure: **leased/optioned** — Ch.312 application's own certification: "Blue Heron Solar, LLC does not currently own any property within the proposed Reinvestment Zone" ([application](sources/2026-07-20_millscountytx_red-river-abatement-application.pdf)); 5 private ranch owners named on the parcel listing (Clayton Ranches Ltd, Hardberger George Robert Trustee, Childress Charles Grady Sr ×4), ~3,612 ac total, abstracts 254/13/530/270/572/697, all situs N CR 531
- Abatements: **Chapter 312** (county-level) application filed 2025-10-27 requesting 10-yr 50% abatement (reduced to 35% before the vote); Mills County Commissioners' Court **rejected it 3-2 on 2025-12-29**, citing failure to clearly meet the $10M net-benefit guideline ([CitizenPortal](sources/2026-07-20_citizenportal_mills-county-rejects-blue-heron-abatement.html)); Ch.313/JETI (state) search returned negative — expected, as those are separate programs and this IA post-dates the Ch.313 sunset
- CAD: not separately searched (parcel IDs + acreage obtained directly from the abatement application's own parcel listing, sourced from Mills CAD)

## 5. Interconnection & contractual schedule

- POI per signed IA: "proposed Gobbers Knob Switch" on Oncor's 345 kV Brown Switch – Buckhorn Switch line, Brown County ([IA Exhibit C](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf)) — matches queue POI text exactly
- Equipment (Exhibit C): 39× Sungrow SG4400-UD solar inverters, 148.941 MW gross / 147 MW measured at 34.5kV collector; co-located BESS under companion INR 24INR0331 "Chisme Storage" (68×12 Sungrow SC210HX-US, 147.56 MW gross / 146 MW measured) sharing this same IA and POI

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-20_puct_35077-2003_standard-generation-interconnection-agreement-be.pdf)) | filed 2024-12-04 (NTP Dec 6, 2024) | $15,842,206 irrevocable standby LC |

| Milestone | Original IA (2024) |
|---|---|
| In-Service | 2026-12-03 |
| Trial Operation | 2026-12-13 |
| Scheduled COD | 2027-04-13 |

(No amendments on file — `puct.py match` returned a single confirmed filing.)
- Queue-history COD drift (from [timeline.md](timeline.md)): 3 changes pre-contract — 2025-07-01 → 2026-02-20 → 2026-10-07 → 2027-04-13; current COD unchanged since 2024-10-01 (21 months stable), now matching the signed IA exactly

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| n/a | **No Sentinel-2 imagery obtained** — CDSE openEO returned HTTP 402 "insufficient credits" on every retry (verified by direct API call, not a transient rate-limit); gmaps.py staticmap returned HTTP 403 "Maps Static API not activated." Both playbook imagery paths were unavailable this run. | — |
| n/a | Aerial basemap (undated, Esri World Imagery, embedded in the county abatement filing) shows the project-boundary polygon over rolling wooded/scrub ranchland bisected by an unpaved road; no visible clearing, grading, or structures — but this basemap's vintage is unknown and may predate the project. | [boundary+aerial](sources/2026-07-20_millscountytx_red-river-abatement-applica_sheet02.png) |
| 2026-03 → 2026-04 | EIA-860M status flips "(T) Not under construction" → "(U) Under construction, ≤50% complete" | [eia_history.json](eia_history.json) |

- Verdict: **under construction (≤50% complete)** per EIA-860M's own status field (independent federal self-report, not visual) — no satellite/aerial confirmation obtainable this run

## 7. COD assessment

- Reported COD (2027-04-13) is the exact Scheduled Commercial Operation Date in a signed, PUCT-filed IA — independently corroborated by EIA-860M (planned 2027-05) and the company's own fact sheet ("estimated startup Q2 2027"). Three separate sources converge on the same quarter.
- The queue's 3 prior COD slips (totaling ~21 months) all occurred before this IA was signed (Dec 2024) and before the current COD was even entered (stable since Oct 2024) — they reflect pre-contract uncertainty, not post-signing schedule risk.
- Risk: Mills County rejected the requested tax abatement (Dec 2025), adding cost without stopping the project; construction-start self-reports disagree by one quarter between the developer's two own documents; no imagery was obtainable to confirm physical progress toward the Dec 2026 In-Service Date, though EIA-860M's own status field independently confirms construction is underway.
- For: signed IA with posted $15.8M security, matching independent EIA-860M schedule, EIA status flip to "under construction" as of April 2026, detailed county-level economic filings (parcels, taxes, jobs) consistent with an active, funded development — not a paper/shell filing.
- **Independent estimate: 2027-Q2, drift risk medium** (grounded by contract + 2 independent corroborating sources, but no visual construction confirmation and one unresolved local funding friction point).

## 8. Could not determine

- Exact Gobbers Knob Switch / site centroid coordinates (CEII-redacted in the IA; no imagery tool available to georeference the boundary polygon precisely)
- Visual construction progress / exact completion percentage (CDSE out of processing credits — HTTP 402; gmaps Static API not enabled — HTTP 403; both playbook imagery paths down this run; EIA-860M confirms "under construction, ≤50%" but gives no finer resolution)
- Corporate structure above Red River Clean Energy (Concord New Energy link is a document-sourced lead — matching email domain — not independently confirmed via SOS/corporate registry)
- Whether land tenure is a lease or a purchase option (Ch.312 filing confirms non-ownership but not which)
- Full content of the Dec 29, 2025 commissioners' court discussion beyond the AI-summarized excerpt (source is paywalled past the summary)
