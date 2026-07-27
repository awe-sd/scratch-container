# Dossier — Ulysses Solar (21INR0253)

Researched 2026-07-20 · site 31.72623, -100.2771 · verdict **real_active**

## 1. Verdict

- **real_active** — developer's own project page (Akuo) states status "in construction," up to 400 workers on site ([project page](sources/2026-07-20_akuoenergy_tennyson-project-page.html)); two 15-yr PPAs signed 2025-06 ([Sasol](sources/2026-07-20_akuoenergy_sasol-vppa-press-release.html), [Imerys](sources/2026-07-20_akuoenergy_imerys-ppa-press-release.html))
- Construction: **unconfirmed by imagery this run** (CDSE credits exhausted, see §6) — non-imagery sources say "in construction"/EIA "≤50% complete"
- Site: 31.72623, -100.2771 — POI-network triangulation cross-validated against EIA-860M, high confidence ([satellite view](https://www.google.com/maps/@31.72623,-100.2771,5000m/data=!3m1!1e3))
- COD: reported 2027-03-02 → independent **2027-Q2**, drift risk **medium** (floating IA schedule, EIA says 2026-12)

## 2. Site identification

- Derivation: IA Exhibit C-1 one-line diagram ([rendered](sources/2026-07-19_puct_35077-1501_ercot-standard-generation-interco_p53.png)) names AEP's Odysseus Station ~35 mi from "Bluff Creek Station" and ~15 mi from "Red Creek Station"; IA Exhibit C text: Ulysses Substation "~19 miles northeast of San Angelo." Matched those named stations in OpenGridMap's `transnet-models` OSM-derived transmission-node dataset → San Angelo Red Creek Substation (AEP, 345/138kV) at 31.5290977, -100.3212098.
- **Stated project area: 1,200+ acres** per BNB's own project page ([source](sources/2026-07-20_bnbrenewables_tennyson-solar-project-page.html)) — imagery footprint consistent? unverified (no imagery obtained this run)
- Cross-checks (each linked): factsheet's independent EIA-860M plant coordinate (31.72623,-100.2771) is 13.9 mi from Red Creek Substation (IA said ~15 mi) and 20.4 mi at bearing 027° from San Angelo (IA said ~19 mi NE) — two independent geometric derivations agree within ~1–1.5 mi
- Not obtainable: exact substation/POI coordinates (not published; Exhibit C-1 is schematic/not-to-scale), CAD parcel boundary (no parcel search run this pass)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| BNB Tennyson Solar LLC | SPV | Generator party on [original IA](sources/2026-07-19_puct_35077-1501_ercot-standard-generation-interconnection-agreem.pdf) & [Amendment 1](sources/2026-07-19_puct_35077-2283_first-amended-and-restated-ercot-standard-genera.pdf) |
| BNB Renewable Energy | original developer | named filer in IA recital; [own project page](sources/2026-07-20_bnbrenewables_tennyson-solar-project-page.html) |
| Akuo Energy USA | current owner/developer | BNB page states sold to Akuo 2021; [Akuo's own project page](sources/2026-07-20_akuoenergy_tennyson-project-page.html) |
| Ardian (PE) | parent financial sponsor | acquired 100% of Akuo Group, completed 2025-07-04 (akuoenergy.com press release; [secondary confirmation](sources/2026-07-20_pvtech_akuo-tennyson-imerys-ppa.html)) |
| Sasol | offtaker (VPPA) | 91 MW, 15-yr, ~250 GWh/yr ([PR](sources/2026-07-20_akuoenergy_sasol-vppa-press-release.html)) |
| Imerys | offtaker (PPA) | 57 MW, 15-yr, ~153 GWh/yr, announced 2025-06-20 ([PR](sources/2026-07-20_akuoenergy_imerys-ppa-press-release.html), [pv-tech](sources/2026-07-20_pvtech_akuo-tennyson-imerys-ppa.html)) |

- Financing: no dedicated project-financing-close PR found; parent Akuo Group's acquisition by PE firm Ardian (2025-07-04) is the closest financing signal — Ardian "committed to providing the financial resources" for Akuo's build-out ([pv-tech](sources/2026-07-20_pvtech_akuo-tennyson-imerys-ppa.html))

## 4. Land & county records

- Tenure: **leased** — Akuo's project page states land is "long-term leased," no competing land uses ([source](sources/2026-07-20_akuoenergy_tennyson-project-page.html))
- Abatements/agreements: **none found** — `ch313.py resolve` returned no Ch.313 or JETI match under "Ulysses Solar," "BNB Tennyson Solar," or Coke County keys
- CAD: not searched this pass (leased ranchland typically shows 0 hits under LLC name, per Hanson precedent; not run given time budget)

## 5. Interconnection & contractual schedule

- POI per signed IA: Odysseus Station, first dead-end structure outside station fence, Coke County ([IA](sources/2026-07-19_puct_35077-1501_ercot-standard-generation-interconnection-agreem.pdf))
- Equipment: original IA specified 39× Power Electronics FS4200M-HEM GEN3 (163.8 MW nominal); Amendment 1 changed to 37× Sungrow SG4400UD-MV (150 MW at POI / 151.2 MW at 34.5kV bus) — matches queue's 150.0→151.2 MW bump (2025-05)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1501_ercot-standard-generation-interconnection-agreem.pdf)) | 2022-10-03 | $19,000,000 |
| Amendment 1 ([pdf](sources/2026-07-19_puct_35077-2283_first-amended-and-restated-ercot-standard-genera.pdf)) | 2025-10-01 | $28,500,000 — increased |

| Milestone | Original IA 2022 | Amendment 1 (2025) |
|---|---|---|
| In-Service | 24 mo. from conditions-satisfied trigger | 24 mo. (unchanged) |
| Trial Operation | 25 mo. from trigger | 30 mo. (+5 mo.) |
| Scheduled COD | 26 mo. from trigger | 35 mo. (+9 mo.) |

- Both IAs use a **floating** schedule (months from the date Sec. 4.2/4.3 conditions are satisfied) — neither document states that trigger's calendar date, so contractual COD cannot be read directly off the IA text
- Queue-history COD drift (from [timeline.md](timeline.md)): **7 changes**, 2021-11-01 → 2027-03-02; current value stable for 9 straight monthly snapshots (2025-10-01 → 2026-06-01), longest hold in the project's 86-snapshot history, coinciding with Amendment 1's execution date

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | **No imagery obtained.** `cdse.py chip` failed repeatedly; root-caused via raw `curl` to the openEO endpoint → **HTTP 402 Payment Required**, "insufficient credits" (shared CDSE account exhausted, likely by 4+ concurrent research-agent sessions in this container). Not a per-request/backoff-fixable error. | — |

- Verdict: **cannot independently confirm construction stage or pace via imagery this run.** Relying instead on non-imagery evidence: Akuo's own page states "in construction" (≤400 workers on site); EIA-860M status "Under construction, ≤50% complete" sustained 5 months (Jan–May 2026)

## 7. COD assessment

- Reported 2027-03-02 has held 9 consecutive monthly snapshots — the longest stable period in the project's history — beginning exactly at Amendment 1's execution date (2025-10-01), suggesting it reflects the amended (not yet re-slipped) schedule
- EIA-860M second source reports an **earlier** planned COD (2026-12) sustained across all 5 available months, alongside "Under construction, ≤50% complete" — independent confirmation of active build, though the ≤50% band implies meaningful work remains as of 2026-05
- For: two 15-yr investment-grade-adjacent offtake contracts (Sasol, Imerys) signed mid-2025; PE-backed parent (Ardian) completed acquisition of Akuo Group 2025-07; security posting more than doubled to $28.5M with Amendment 1 — all consistent with active late-stage development, not a stalled/paper filing
- Risk: 7 prior COD slips (~64 months cumulative drift since original 2021-11 claim); IA's floating schedule trigger date is unknown, so the contractual COD cannot be pinned exactly; no visual confirmation of construction pace this run
- **Independent estimate: 2027-Q2, drift risk medium** — splits between EIA's earlier date and the queue's newly-stabilized figure, weighted toward the queue given the more recent security increase and PPA-backed financing

## 8. Could not determine

- Construction stage/pace via satellite imagery — CDSE account credit-exhausted (HTTP 402), a hard blocker this run, not project-specific
- Exact IA schedule trigger date (Sec. 4.2/4.3 conditions-satisfied) — floating schedule, undocumented in either IA
- CAD parcel records / underlying landowner names — not searched this pass
- Dedicated project-financing-close announcement (only the parent-level Ardian/Akuo acquisition was found)
- Global Energy Monitor's Tennyson Solar page — fetch returned HTTP 403
