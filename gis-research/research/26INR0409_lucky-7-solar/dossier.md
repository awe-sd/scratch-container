# Dossier — Lucky 7 Solar (26INR0409)

Researched 2026-07-20 · site 33.078, -95.712 · verdict **real_active**

## 1. Verdict

- **real_active** — ACTIVE TCEQ construction-stormwater NOI ([TXR1503YB](sources/2026-07-20_tceq_storm-noi-TXR1503YB-lucky7solarfarm.json), coverage since 2026-04-27) at a named Brashear, TX address, corroborated by EIA-860M "[under construction, ≤50% complete](eia_history.json)" and a graded polygon visible in [Sentinel-2 imagery](imagery/s2_2026-07-01_wide.png)
- Construction: **clearing**, first activity **2026-04-27** (TCEQ NOI coverage-begin date; no pre-construction imagery baseline obtained — CDSE fleet capacity exhausted, see §8)
- Site: 33.078, -95.712 — imagery feature match near EIA-860M coords (33.082, -95.721), cross-checked against IA POI text and TCEQ site address, medium confidence ([satellite view](https://www.google.com/maps/@33.078,-95.712,5000m/data=!3m1!1e3))
- COD: reported 2027-09-20 → independent **2027-Q3**, drift risk **low** (stable 14 months, 3 independent sources agree)

## 2. Site identification

- Derivation: EIA-860M plant coordinates (33.082, -95.721) used as search center; a Sentinel-2 chip ([wide frame](imagery/s2_2026-07-01_wide.png), scene 2026-07-11) shows an irregular graded/cleared polygon ~1 km ESE at 33.078, -95.712, with internal light-toned access-road striping
- **Stated project area: not obtained** — no acreage figure found in any source (no Ch.313/JETI filing, no CAD parcel search performed); imagery footprint (~1-1.5 km across, roughly 250-350 acres by eye) is plausible for a 100 MW AC solar site but unconfirmed against a document figure
- Cross-checks (each linked): IA POI text — "Point of Interconnection is located in Hopkins County, Texas, at the **Brashear Switch**" ([IA Exhibit C](sources/2026-07-19_puct_35077-2241_standard-generation-interconnection-agreement-be.pdf), p31); TCEQ storm-NOI physical address — **2854 Farm Road 3389, Brashear, TX 75420** ([NOI](sources/2026-07-20_tceq_storm-noi-TXR1503YB-lucky7solarfarm.json)); queue POI text "Tap 345kV 2621 Sandy Ranch Switch - 2464 CASH SWITCH" matches the IA's "Sandy Ranch Switch – Cash Switch 345kV line" naming exactly — all three agree on the Brashear/Cash-Switch-corridor area
- Not obtainable: exact Brashear Switch tie-point coordinates (redacted as CEII in IA Exhibit C); no parcel/boundary map exhibit exists yet — the IA's site-plan/KMZ deliverable is not due to Oncor until 2026-11-05 (Exhibit B), so `site.map_artifacts` is empty by contract-timing, not by omission

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Lucky 7 Solar Farm LLC | SPV | Generator party on [IA](sources/2026-07-19_puct_35077-2241_standard-generation-interconnection-agreement-be.pdf), PUCT 35077-2241 |
| OCI Energy | original developer / seller | IA Exhibit D address (San Antonio, ocienergy.com email); [Sidley Austin PR](sources/2026-07-20_sidley_oci-sale-lucky7-sabanci.html) 2025-08-18 |
| Sabanci Renewables (Sabanci Holding, Türkiye) | current developer/owner | [Sidley PR](sources/2026-07-20_sidley_oci-sale-lucky7-sabanci.html); [developer project page](sources/2026-07-20_sabanciclimatetech_lucky7-project-profile.html) |
| Signal Energy, LLC | EPC | [TCEQ NOI](sources/2026-07-20_tceq_storm-noi-TXR1503YB-lucky7solarfarm.json); [construction press](sources/2026-07-20_constructionreviewonline_sabanci-lucky7-pepper.html) 2026-01-27; developer page |
| Waaree Solar Americas | module supplier | construction press + developer page (bifacial, hail-resistant modules) |

- Financing: no debt/equity-close PR found; [pv-magazine 2026-03-02](sources/2026-07-20_pvmagazine_sabanci-empact-286mw-portfolio.html) reports a tax-equity/ITC-compliance engagement with Empact Technologies covering the 286 MW Lucky 7 + Pepper portfolio — a financing-adjacent signal, not a closed debt facility
- PPA: developer's own project page lists PPA status as **"under exclusivity"** (not yet executed)

## 4. Land & county records

- Tenure: **unknown** — no parcel/site-plan document on file; IA's KMZ/panel-coordinate deliverable is not due until 2026-11-05
- Abatements/agreements: **0 hits** — `ch313.py resolve --county Hopkins --name` tried against "Lucky 7", "Sabanci", and "Signal Energy" (3 searches), all negative. Consistent with a 2024-era project that did not pursue a Ch.313/JETI value-limitation
- CAD: Hopkins County Appraisal District (hopkinscad.org) search page is a JS/AJAX front-end that returns an empty shell to a plain HTTP GET — not queried; no parcel data obtained

## 5. Interconnection & contractual schedule

- POI per signed IA: "...located in Hopkins County, Texas, at the **Brashear Switch** in TSP's Sandy Ranch Switch - Cash Switch 345 kV transmission line" ([IA](sources/2026-07-19_puct_35077-2241_standard-generation-interconnection-agreement-be.pdf), Exhibit C)
- Equipment (Exhibit C): 29× Power Electronics FS4010 solar inverters, 4.01 MVA each, gross 116.29 MVA, dispatched 101.8 MW at generator terminals / 100.8 MW at 34.5kV bus. Note: the developer's own project page lists inverter vendor as **SMA** — a discrepancy vs. the IA's Power Electronics spec, possibly a post-acquisition equipment change (unresolved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-2241_standard-generation-interconnection-agreement-be.pdf)) | 2025-08-12/13 | $19,290,074 Irrevocable Standby LC, effective on/before 2025-09-19 |

(No amendments on file — `puct.py match` returned exactly one docket filing, 35077-2241, confirmed via INR-in-text.)

| Milestone | Original IA 2025 |
|---|---|
| In-Service | 2027-05-13 |
| Trial Operation | 2027-05-23 |
| Scheduled COD | 2027-09-20 |

- Queue-history COD drift (from [timeline.md](timeline.md)): **2 changes** — placeholder 2026-07-01 (Mar 2024 only) → 2027-09-04 (Apr 2024–Apr 2025) → 2027-09-20 (May 2025–Jun 2026, current, 14 straight snapshots, matches the signed IA exactly)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-11 | Irregular graded/tan polygon, ~1-1.5 km across, internal access-road striping visible; no dark uniform module-block signature yet | [wide frame](imagery/s2_2026-07-01_wide.png), [tight frame](imagery/grid/s2_c0_0.png) |

- Verdict: **clearing** — TCEQ NOI (coverage since 2026-04-27) is the dated first-activity evidence; no pre-construction baseline frame was obtained (CDSE fleet-wide processing capacity was exhausted by concurrent deep-scan workers during this run — 2 further chip/timelapse attempts failed after retries and were not looped, per tool guidance)

## 7. COD assessment

- Reported 2027-09-20 is the exact Scheduled Commercial Operation date in the signed IA — contractually grounded, single document, no amendments
- Three independent sources agree within one month of each other: IA (2027-09-20), EIA-860M planned COD (2027-10), developer's own page (Q3 2027) — unusually strong convergence for this stage
- EIA-860M's "under construction, ≤50% complete" status (as of 2026-05-01) plus the active TCEQ storm NOI (since 2026-04-27) independently confirm the project is past paper-stage and mid-civil-works, ~14 months ahead of the contractual COD — a normal construction lead time for 100 MW solar
- Risk factors: PPA still "under exclusivity" (not fully executed) per the developer's own page; panel layout/KMZ not finalized (not due to TSP until 2026-11-05); an unresolved inverter-vendor discrepancy (IA: Power Electronics vs. developer page: SMA) suggests some post-acquisition scope churn, though not schedule-threatening on its own
- **Independent estimate: 2027-Q3, drift risk low**

## 8. Could not determine

- Exact Brashear Switch tie-point coordinates (CEII-redacted in IA Exhibit C)
- Stated project acreage (no Ch.313/JETI filing; CAD not queried — JS/AJAX portal)
- Parcel ownership / land tenure (leased vs. purchased) — no site-plan/KMZ exhibit exists yet (not due until 2026-11-05); Hopkins CAD not queried (JS-driven search, not scriptable via plain HTTP)
- A pre-construction imagery baseline to bracket first_activity_seen precisely — CDSE fleet processing capacity was saturated by concurrent deep-scan workers throughout this run; first_activity_seen is sourced from the TCEQ NOI date, not an imagery bracket
- Closed financing/debt details (only a tax-equity/ITC-compliance engagement found, not a financial close)
- Resolution of the IA-vs-developer-page inverter vendor discrepancy (Power Electronics FS4010 vs. SMA)
