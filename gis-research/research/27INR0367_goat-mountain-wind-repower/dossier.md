# Dossier — Goat Mountain Wind-Repower (27INR0367)

Researched 2026-07-19 · site 31.93988, -100.82605 · verdict **real_active**

## 1. Verdict

- **real_active** — Clearway Energy Q1 2026 10-Q: ["The Goat Mountain wind facility commenced repowering activities in February 2026 and was taken offline."](sources/2026-05-08_clearway_10Q_Q12026.htm)
- Construction: **active_repowering**, commenced February 2026 (facility taken offline)
- Site: 31.93988, -100.82605 — Google Maps Places pin "Goat Mountain Wind LP | Silver, TX 76945" + Clearway 10-K confirms "Sterling City, Texas" ([map](https://google.com/maps/@31.93988,-100.82605,5000m/data=!3m1!1e3))
- COD: reported 2027-06-01 → independent **2027-Q3/Q4**, drift risk **med** (H2 2027 confirmed by Clearway but start vs. end of H2 unclear)

## 2. Site identification

- Derivation: Google Maps Places pin (delivered as "corporate_office,point_of_interest") + Clearway 10-K/10-Q text: "Sterling City, Texas." Confirmed by Sentinel-2 chip showing dense wind farm road/pad network at these coordinates.
- **Stated project area:** Not in IA (PUCT portal blocked). CAD parcels: no energy company ownership found (expected — wind projects lease land from ranchers).
- Cross-checks: gmaps pin → existing operating farm → Clearway text "Sterling City" → Sentinel-2 imagery shows wind farm → agree within <1 km
- Not obtainable: POI substation exact coordinates (CEII); IA PDF (PUCT Interchange returned 402); FAA OE/AAA turbine coordinates (JS-only portal)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Goat Wind LLC | SPV co-borrower | [Q1 2026 10-Q](sources/2026-05-08_clearway_10Q_Q12026.htm) |
| Goat Mountain Class B Holdco LLC | SPV co-borrower | [Q1 2026 10-Q](sources/2026-05-08_clearway_10Q_Q12026.htm) |
| Palisade Plains Development Partnership LLC | VIE owning facility | [Q1 2026 10-Q](sources/2026-05-08_clearway_10Q_Q12026.htm) |
| Clearway Energy Inc. (CWEN) | Parent / 99% Class B owner | [10-K 2025](sources/2026-02-24_clearway_10K_2025.htm) |
| Clearway Renew | EPC / dev services | [10-K 2025](sources/2026-02-24_clearway_10K_2025.htm) |
| Clearway Renewable O&M (RENOM) | O&M operator | [10-K 2025](sources/2026-02-24_clearway_10K_2025.htm) |
| Unnamed investment-grade counterparty (likely Google) | PPA offtaker | [10-K 2025](sources/2026-02-24_clearway_10K_2025.htm) |

- Financing: **$703M non-recourse construction loan closed 2026-02-27** (Goat Wind LLC + Goat Mountain Class B Holdco LLC as co-borrowers; SOFR+1.50%); $151M borrowed through 2026-03-31; converts to 5-yr term loan at substantial completion. Tax equity bridge also included. ([Q1 2026 10-Q](sources/2026-05-08_clearway_10Q_Q12026.htm))
- Total Clearway capex: **$200M** (of the $703M total project cost). ([10-K 2025](sources/2026-02-24_clearway_10K_2025.htm))
- Equipment deposit: $25M paid 2025-12-12 to Clearway Renew. ([10-K 2025](sources/2026-02-24_clearway_10K_2025.htm))

## 4. Land & county records

- Tenure: **leased** (inferred — no Clearway/Goat Wind LLC ownership in Sterling CAD; wind projects lease ranching land)
- Abatements/agreements: None — Ch.313 expired 2022; project entered queue Dec 2024 (post-deadline). JETI search: Sterling County not found in TX Comptroller JETI database. No Ch.312 found.
- CAD: Sterling CAD owner search — no records for "Clearway", "Cielo Wind", "Goat Mountain", "Goat Wind" (expected for lease structure)
- Original farm: Goat Mountain Wind LP, developed by Cielo Wind Power LP, early partner Edison Mission Group (first ERCOT project)

## 5. Interconnection & contractual schedule

- POI per queue: "76030 Gasconades Creek 345kV" (ERCOT queue data; IA PDF not retrieved — PUCT portal blocked)
- IA signed: **2026-02-20** per ERCOT queue milestone data ([timeline.md](timeline.md))

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (PUCT Interchange filing, not retrieved) | 2026-02-20 (per queue) | Unknown — portal blocked |

| Milestone | Queue data |
|---|---|
| IA signed | 2026-02-20 |
| Meets 6.9(1) | 2026-06-18 |
| Reported COD | 2027-06-01 |
| Clearway internal target | H2 2027 |

- Queue-history COD drift ([timeline.md](timeline.md)): 1 change — 2027-12-31 → 2027-06-01 (pulled in ~6 months, Mar 2025)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Dense existing wind farm road/pad network visible across 6 km frame; white circular turbine pads at ends of access road branches; central O&M/substation cluster; no obvious construction disturbance visible at 10 m/px | [png](imagery/s2_2026-07-01.png) |

- Verdict: **active_repowering** — 10-Q confirms facility taken offline Feb 2026; Sentinel-2 at 10 m/px cannot distinguish standing turbine vs. removed turbine vs. new installation. Timelapse ordered (openEO job pending). FAA OE/AAA portal JS-only, no turbine coordinates obtained.
- Note: timelapse (2025-01 to 2026-07) submitted as openEO batch job; frames pending at time of writing.

## 7. COD assessment

- **Contractual grounding:** Clearway Q1 2026 10-Q language is "second half of 2027" (H2 2027) — not June specifically. Construction loan matures at "substantial completion expected in H2 2027." Queue reports June 1, 2027 = start of H2 2027 — the aggressive end of this range.
- **Construction pace:** Repowering commenced Feb 2026; construction financing closed Feb 27, 2026; $151M drawn by end of Q1 2026. Equipment deposit paid Dec 2025 ($25M). This implies turbines were ordered in Q4 2025 / Q1 2026 — consistent with ~12-18 month delivery lead time targeting mid-to-late 2027 commissioning.
- **Repower advantage:** Existing road network, substation, and grid connection reduce civil work vs. greenfield. Original farm at this site (Cielo/Edison Mission) is fully permitted land. Repower builds are typically faster (12-18 months vs. 24-36 months).
- **Risk factors:** Wind repower at 303 MW requires phased turbine swap; new turbine procurement and ERCOT testing could push into Q4 2027 or early 2028 if any supply chain delays. $200M Clearway capex on $703M total project — large project with contractor coordination risk.
- **Independent COD estimate:** **2027-Q3 (Jul–Sep 2027)** most likely; could slip to Q4 2027. June 1, 2027 (queue claim) is achievable only if all turbines delivered and commissioned by end of May — possible but represents fastest-case execution.

## 8. Could not determine

- IA PDF and financial security amount (PUCT portal blocked — 402 error)
- FAA OE/AAA turbine coordinates for new turbines (portal JS-only, no results)
- PPA counterparty confirmed by primary source (SEC filings say "investment-grade counterparty"; Google attribution from secondary DealFlow.energy reporting only)
- Project area in acres (no abatement doc, CAD lease structure, IA not retrieved)
- Turbine model/count for repower (not in SEC filings reviewed)
- Timelapse frame confirming exact turbine removal start date (openEO job pending)
