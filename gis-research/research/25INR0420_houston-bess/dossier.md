# Dossier — Houston BESS (25INR0420)

Researched 2026-07-19 · site 29.9112, -95.3215 (Lauder Substation) · verdict **real_active**

## 1. Verdict

- **real_active** — $135M construction financing closed Feb 2025; [Irby Construction project page](sources/2026-07-19_irby_smt-houston-iv-project.md) confirms 160 MW/320 MWh groundbreaking April/May 2025
- Construction: **active**, first activity ≥ Apr 2025 (imagery inconclusive — urban BESS compact)
- Site: 29.9112, -95.3215 — Lauder 138kV substation (OSM geometry), medium confidence ([map](https://google.com/maps/@29.9112,-95.3215,1500m/data=!3m1!1e3)); exact pad location unknown along the Lauder–Rittenhouse line tap
- COD: reported 2027-08-01 → independent **2027-Q2/Q3**, drift risk **high** (IA not signed, 3 prior slips; project rescoped to 160 MW vs 227.9 MW in queue)

## 2. Site identification

- Derivation: POI text "Tap 138kV LAUDER (#46002) – RITTENHOUSE (#46282) ckt 95" → Lauder Substation OSM geom centroid 29.9112, -95.3215; Rittenhouse Substation at 29.8636, -95.3794 ([OSM Overpass](https://overpass-api.de/))
- **Stated project area: not found** — no abatement, CAD parcel, or IA recovered; BESS signature 10–40 acres expected
- Cross-checks: Lauder Substation OSM confirmed CenterPoint 138kV/12kV, ref "LA"; Rittenhouse confirmed CenterPoint 138kV/12.5kV, ref "RU" — consistent with POI
- Not obtainable: exact tap/pad coordinates (CEII); HCAD owner-name search blocked (403); PUCT Interchange blocked (402)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Houston BESS, LLC (queue applicant per identity packet) | SPV/queue holder | ERCOT queue filing |
| SMT Houston IV (or SMT Houston IV BESS) | Operating entity / project name | [Irby project page](sources/2026-07-19_irby_smt-houston-iv-project.md) |
| SMT Energy (Boulder, CO) | Developer/owner | [smtenergy.com](https://www.smtenergy.com/); [infrasure](sources/2026-07-19_infrasure_project_page_deep.md) |
| Irby Construction | EPC | [Irby project page](sources/2026-07-19_irby_smt-houston-iv-project.md) |
| CenterPoint Energy | Transmission host + partner | [Irby project page](sources/2026-07-19_irby_smt-houston-iv-project.md) |
| FlexGen | BESS platform / SCADA (inferred from SMT Energy partnership) | [smtenergy.com partner listing](https://www.smtenergy.com) |
| KeyBank, SUSI Partners, UBS, Goldman Sachs | Financiers | [smtenergy.com partner listing](https://www.smtenergy.com) |

- Financing: **$135M construction financing closed Feb 26, 2025** ([infrasure](sources/2026-07-19_infrasure_project_page_deep.md))

## 4. Land & county records

- Tenure: **unknown** — no HCAD parcels recovered (search blocked); urban BESS likely on leased/acquired industrial parcel adjacent to CenterPoint infrastructure
- Abatements/agreements: **none found** — Ch.313 program expired 2023; JETI not searched (no public portal); Harris County is dense urban, no agricultural abatement expected
- CAD: 0 hits (HCAD search returned 403); negative result logged

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 138 kV LAUDER (#46002) – RITTENHOUSE (#46282) ckt 95" — no signed IA recovered
- IA status: **NOT SIGNED** as of latest queue snapshot 2026-06-01 and confirmed by infrasure.ai (Facility Study phase, 40 months in queue); PUCT Interchange blocked (402) throughout
- Equipment: 160 MW / 320 MWh per financing/EPC sources; queue shows 227.9 MW (never updated from initial filing)

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA recovered | — | — |

| Milestone | Queue report |
|---|---|
| Screening complete | 2023-07-03 |
| FIS approved | 2024-04-04 |
| IA signed | — (not signed) |
| In-Service / Trial Op / COD | — |

- Queue-history COD drift (from [timeline.md](timeline.md)): 3 changes — 2025-09-29 → 2026-06-15 → 2026-12-15 → 2027-08-01

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-01 | Pre-construction baseline — dense suburban/industrial at Lauder; no gravel pad | [png](imagery/s2_2025-01-01_lauder_pre.png) |
| 2026-06 | Same character — no distinct pale gravel BESS pad detected in 1km tight chip | [png](imagery/key/s2_2026-06-01_lauder_tight_1km.png) |
| 2026-07 | No change from Jun 2026 | [png](imagery/key/s2_2026-07_lauder_tight.png) |

- Verdict: **no_activity_confirmed_at_orbit** — dense urban area; BESS footprint (10–40 acres) is below reliable detection in this suburban mosaic at Sentinel-2 10m/px. Corridor search from Lauder (29.91, -95.32) to Rittenhouse (29.86, -95.38) covered 9 tiles; no industrial gravel pad identified. Absence is indeterminate for urban BESS — does NOT contradict active construction confirmed by press.

## 7. COD assessment

- Contractual grounding: **IA not signed** after 40 months in queue, despite confirmed groundbreaking May 2025 — abnormal; project may be using a bilateral agreement with CenterPoint (distribution-side) rather than ERCOT transmission IA, or IA is executed outside PUCT Interchange visibility
- Irby COD target was June 2026; infrasure shows Jun 14, 2026 revised target; queue latest = 2027-08-01 — implies June 2026 target was missed (today is July 2026)
- Observed pace: groundbreaking Apr/May 2025 with 14-month construction schedule to Jun 2026 = plausible for 160 MW BESS; however Jun 2026 COD has now passed without queue update to "approved"
- COD slips: 3 prior slips totaling ~23 months of drift from original 2025-09 target
- MW discrepancy: queue 227.9 MW vs. financed 160 MW — project was rescoped downward; queue never updated; suggests developer flexibility and possible further schedule adjustments
- **Independent COD estimate: 2027-Q2/Q3** — Jun 2026 target almost certainly slipped (no approval in queue as of Jun-2026 snapshot); 2027-08-01 queue COD plausible if IA execution completes; net drift of ~2 quarters from current claim is the base case
- Drift risk: **HIGH** — IA absent + pattern of serial slips + MW rescoping + target already missed

## 8. Could not determine

- Exact BESS pad coordinates or street address (CEII; HCAD blocked; no press release with address)
- Whether IA is executed via a non-PUCT bilateral (could explain no PUCT filing)
- Queue MW vs. actual MW — no amended queue filing visible; 227.9 vs. 160 MW gap unexplained
- PPA / offtaker — no evidence found
- HCAD parcel ownership (search blocked)
- Whether Jun 2026 COD was actually achieved and queue not yet updated, or truly missed
