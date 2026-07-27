# Dossier — Caliche Mound Solar (23INR0056)

Researched 2026-07-20 · site 34.84993, -102.27918 · verdict **unclear**

## 1. Verdict

- **unclear** — signed IA is 11-15 months past its own contractual COD with zero imagery evidence of construction ([IA](sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf), [May 2026 chip](imagery/s2_2026-05-01.png))
- Construction: **no_activity** — undisturbed farmland/pasture across a 3x3 grid search, most recent clear imagery 2026-05-19 ([grid](imagery/grid_contact_sheet.png))
- Site: 34.84993, -102.27918 — POI text geolocation (road intersection + distance), medium confidence ([map](https://www.google.com/maps/@34.84993,-102.27918,5000m/data=!3m1!1e3))
- COD: reported 2027-10-26 → independent **2028-Q2 or later (low confidence)**, drift risk **high** (contractual COD already missed by ~1yr, no ground truth)

## 2. Site identification

- Derivation: IA Exhibit C states POI "Mule Deer Switch...located on CO Road 8, 2.6 miles east of US Highway 60," Deaf Smith County ([IA](sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf)) — found the US-60 × CR8 intersection via OSM/Overpass, walked 2.6 mi east along CR8's real road geometry
- **Stated project area: not obtainable** — no Ch.313/JETI/CAD/abatement document found this session; imagery footprint cannot be sanity-checked against a stated acreage
- Cross-checks: OSM shows real, named 345kV "Windmill Substation" and "Hereford Wind Substation" ~5.4-5.5 mi south of the candidate, confirming the AJ Swope–Windmill 345kV corridor exists in this area; no node named "Mule Deer" or "AJ Swope" (expected — Mule Deer is a new, not-yet-built switch)
- Not obtainable: exact Mule Deer Switch coordinates (no site-plan exhibit in the IA, only a schematic one-line electrical diagram); gmaps.py delivery-pin search HTTP 429'd this session, not retried

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| CIG DS1, LLC | SPV — actual signed "Generator" party | [IA](sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf) recital, signature page, notice/EFT addresses |
| Caliche Mound Solar, LLC | project-name alias (Oncor cover-letter usage only) | same IA, p2 cover letter vs. signature block |
| CIG Companies / CIG Capital | developer/owner | [CIG portfolio page](sources/2026-07-20_cigcap_solar-portfolio.html): "CIG DS1... 516 MW... Northern Texas... BBB [green bond]" |
| Danfoss | PPA offtaker (per third party, unconfirmed here) | power-technology.com CIG DS1 profile (WebFetch only, not independently re-fetched — 75MW/12yr PPA) |

- Financing: green bond rated BBB per CIG's own site; no independent rating-agency filing obtained ([CIG portfolio](sources/2026-07-20_cigcap_solar-portfolio.html))

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel search or deed record obtained this session
- Abatements/agreements: **none found** — Ch.313 and JETI registries return 0 hits under "Caliche Mound," "CIG," "Mule Deer," "Tierra/Tiera Blanco," and Deaf Smith County generally (`ch313.py resolve`, 5 separate queries)
- CAD: not searched this session (Deaf Smith CAD e-search portal was 404/account-gated per prior triage)

## 5. Interconnection & contractual schedule

- POI per signed IA: "located in Deaf Smith County, Texas, at the Mule Deer Switch in TSP's AJ Swope – Windmill 345 kV line...on CO Road 8, 2.6 miles east of US Highway 60" ([IA](sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf)) — matches queue POI text exactly
- Equipment (Exhibit C): 107× Power Electronics HEM FS4200M inverters, 4.05 MVA each, 433.35 MVA gross / 408.21 MW at generator terminals

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1688_interconnection-agreement-between-oncor-electric.pdf)) | 2023-10-10 | $12,995,303 irrevocable standby LC |

(No amendment exists — re-verified twice via `puct.py match`, by INR and by the "CIG DS1" legal-name key; both return only this single filing.)

| Milestone | Original IA 2023 |
|---|---|
| Notice to proceed (design/security) | 2023-10-10 |
| Notice to commence construction | 2024-04-17 |
| In-Service Date | 2025-04-17 |
| Trial Operation | 2025-04-28 |
| Scheduled Commercial Operation | **2025-08-28** |

- Queue-history COD drift (from [timeline.md](timeline.md)): the queue's own reported COD held at **2025-08-28 for 25 months (2023-02→2025-03)** — exactly matching the IA's Scheduled Commercial Operation Date, confirming the two were tracking the same real target. It then slipped twice post-hoc (2026-10-10, then 2027-10-15/26), both **after** the original date had already passed with no construction and **with no IA amendment on file** to authorize either change

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-05 (2026-05-09 scene, 0% cloud) | undisturbed center-pivot farmland + creek/drainage at candidate site, no infrastructure | [2026-05](imagery/s2_2026-05-01.png) |
| 2026-05 (2026-05-19 scene, 4.1% cloud) | 3×3 grid (~9×9 km) around candidate: dairy/feedyard, private airstrip, ranch structures — no racking/grading anywhere | [grid](imagery/grid_contact_sheet.png) |
| 2026-07 (2026-07-18 scene, 30.5% cloud) | heavily cloud-obscured; clear patches show undisturbed farmland | [2026-07](imagery/s2_2026-07-15_center.png) |

- Verdict: **no_activity** — no grading, racking, or substation-pad signature found in a ~9×9 km search around the POI-derived site as of the latest clear imagery (2026-05-19); site-fix uncertainty (medium confidence, no boundary map) means the true array footprint could sit outside the searched area

## 7. COD assessment

- The queue's own reported COD tracked the signed IA's Scheduled Commercial Operation Date (**2025-08-28**) exactly for 25 months (2023-02→2025-03, [timeline.md](timeline.md)) — confirming the project genuinely targeted that date. It has now missed it by ~11 months (as of 2026-07-20), with **zero imagery evidence of construction** as of the most recent clear pass (2026-05-19)
- Both post-hoc slips (to 2026-10-10, then to 2027-10-15/26) occurred **after** the original date had already passed with no ground truth, and **neither is backed by a filed IA amendment** — re-verified twice via `puct.py match`, by INR and by the "CIG DS1" legal name; unlike comparable projects (e.g. Hanson Solar) where every queue slip tracked a corresponding IA Amendment, these read as informal re-forecasts
- Corroborating signals from factsheet.json: 5 total COD slips since ~2020, `fisApproved` still null, absent from EIA-860M
- No Ch.313/JETI filing, no CAD record, no press, no construction-stormwater NOI, no financing announcement beyond CIG's own marketing page — a limited paper trail for a 406.6 MW project this far past its original target date
- **Independent estimate: cannot ground a confident date.** If construction has not begun by early 2027, 2027-10-26 is very unlikely on a normal 18-24 month solar build timeline; a realistic floor is **2028 or later**, with meaningful risk the project does not proceed in its current form — CIG's own site described it as still in "permitting stage" as of an October 2024 update

## 8. Could not determine

- Exact Mule Deer Switch coordinates (no site-plan/parcel exhibit in the IA; only a schematic one-line diagram)
- Land tenure (leased vs. purchased) — no CAD/deed record obtained
- Project area in acres — no Ch.313/JETI/abatement/CAD document found
- Definitive confirmation that "CIG DS1" (per CIG's own marketing) is the same asset as INR 23INR0056 beyond the IA's signature block and capacity-band consistency — no single source states the linkage in one sentence
- Whether the project is still actively being developed or has stalled — CIG's own materials (as fetched) predate this research date and describe it as "permitting stage" without a current status update
