# Dossier — Monarch Creek Wind (21INR0263)

Researched 2026-07-19 · site 33.20938, -99.46218 · verdict **real_active**

## 1. Verdict

- **real_active** — 86 FAA OE/AAA turbine obstruction filings (2024-WTW-8086 through 8171, all "No Hazard") confirm exact turbine layout; active civil construction visible in 2026-06 imagery ([s2_2026-06-15](imagery/key/s2_2026-06-15_latest.png))
- Construction: **clearing/civil works**, first activity between Jan–Jun 2026 ([baseline](imagery/key/s2_2024-07-01_baseline.png) vs [latest](imagery/key/s2_2026-06-15_latest.png))
- Site: 33.20938, -99.46218 — FAA turbine centroid (86 filed positions), high confidence ([satellite view](https://www.google.com/maps/@33.20938,-99.46218,5000m/data=!3m1!1e3))
- COD: reported 2027-09-17 → independent **2027-Q4**, drift risk **high** (9 prior slips; civil pads only, no towers yet)

## 2. Site identification

- Derivation: centroid of 86 FAA OE/AAA turbine positions filed 2024-08-05 ([FAA filings](sources/2026-07-19_faa_oe_aaa_turbine-filings.json)); bounding box 33.18°–33.24°N, 99.40°–99.52°W — spans ~12 km E-W × ~6 km N-S
- **Stated project area: not extracted** — Ch.313 application states 58 × 6.0 MW turbines; FAA filed 66 primary + 20 alternate positions; imagery footprint consistent with a multi-km distributed wind layout
- Cross-checks: FAA county split (Throckmorton 49 / Haskell 37) consistent with Ch.313 siting near Throckmorton CISD; [2026-06 imagery](imagery/key/s2_2026-06-15_latest.png) shows pad network centered ~33.21°N, 99.46°W matching FAA centroid
- Not obtainable: exact Coody Crossing Switch 345kV coordinates (CEII); PUCT portal blocked (402)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Monarch Creek Wind, LLC | SPV | TX Comptroller reg #0804576895; formerly King Creek Wind Farm 3 LLC |
| EDF Renewables | Developer/owner | [Ch.313 application](https://comptroller.texas.gov/programs/property-tax/311-313/docs/1807/) names Matthew McCluskey (VP) and Todd Eagleston (PM) as EDF Renewables contacts |
| Unknown | EPC | No press release found |
| Unknown | PPA offtaker | No PPA announced |

- Financing: **not confirmed** — no press release or FERC EWG filing found indicating financing close. FERC EWG self-cert filed Feb 2025 (288 MW, ERCOT WEST, expected 2027) establishes power sales authorization.

## 4. Land & county records

- Tenure: **leased** (expected for wind — turbines on ranching/farmland)
- Abatements: Ch.313 #1807 with Throckmorton CISD ([Comptroller](https://comptroller.texas.gov/programs/property-tax/311-313/docs/1807/)) — original Dec 2022, amended Mar 2025 and Aug 2025. 58 × 6 MW turbines, qualifying period starts 2026-01-01, value limitation starts 2028-01-01.
- CAD: not searched (no parcel lookup needed — wind project on leased ranchland; owner names unknown)

## 5. Interconnection & contractual schedule

- POI per queue: "11419 Coody Crossing Switch 345kV" — Oncor TSP
- IA confirmed: PUCT Control No. 35077 (original Aug 2020 + items 1877, 2355); portal blocked (402) — milestone schedule dates not retrieved

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PUCT 35077 Item 1138) | 2020-08-24 | not retrieved (portal 402) |
| Amended & Restated SGIA (Item 1877) | unknown | not retrieved |
| Amendment No. 2 (Item 2355) | unknown | not retrieved |

| Milestone | Queue-reported |
|---|---|
| IA signed | 2020-08-24 |
| FIS approved | 2025-11-05 |
| Meets all 6.9 | 2026-01-26 |
| Scheduled COD (latest) | 2027-09-17 |

- Queue-history COD drift ([timeline.md](timeline.md)): **9 changes** — 2021-10-01 → 2027-09-17 (6-year total slip over 83 monthly snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-07 | Undisturbed rangeland across full project area | [baseline](imagery/key/s2_2024-07-01_baseline.png) |
| 2026-01 | Still undisturbed — no pads or roads | [2026-01](imagery/key/s2_2026-01-01.png) |
| 2026-06 | Active civil construction — graded turbine pads + access road network across ~12 km E-W footprint in both Throckmorton and Haskell portions | [latest](imagery/key/s2_2026-06-15_latest.png) |

- Verdict: **clearing/civil works** — pad network established ≥ 2026 Q2; no tower sections or nacelles visible at 10 m/px; construction commenced after Jan 2026

## 7. COD assessment

- Reported 2027-09-17 is NOT yet grounded by a retrievable signed IA schedule (PUCT blocked); it is the 10th COD the project has claimed in 6 years of 9 slips
- Observed pace: civil works started no earlier than Q1 2026, based on Jan 2026 baseline clear. Pad grid well-established by Jun 2026.
- Typical wind build timeline from civil works to COD: 12–18 months from first pads → 2027-Q1 at the absolute fastest, 2027-Q4 most likely
- Risk factors: 9 prior slips, no financing announcement, no construction start reported in queue data, PUCT IA schedule inaccessible, tower erection not yet visible
- Ch.313 value limitation starts Jan 2028 — economic incentive to achieve COD by end of 2027 but not a hard contractual constraint
- **Independent estimate: 2027-Q4, drift risk high** — plausible but tight; any delay in tower delivery or erection could push to 2028-Q1/Q2

## 8. Could not determine

- IA milestone schedule (Scheduled COD date, In-Service, Trial Operation) — PUCT Interchange blocked (402 error)
- Financial security amounts posted with Oncor
- EPC contractor identity
- PPA offtaker
- Financing close announcement
- Exact acreage under lease
- Whether 58-turbine Ch.313 layout or 66-primary-position FAA layout is the final build plan
