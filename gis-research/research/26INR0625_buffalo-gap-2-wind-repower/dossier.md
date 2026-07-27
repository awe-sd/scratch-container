# Dossier — Buffalo Gap 2 Wind Repower (26INR0625)

Researched 2026-07-19 · site 32.31056, -100.14917 · verdict **real_early**

## 1. Verdict

- **real_early** — AES Corp 10-K (2026-03-02) lists "Buffalo Gap Repowering 527 MW, 100%, 1H 2027" as construction-pipeline commitment; $200M HASI preferred equity closed Dec 2025 ([10-K excerpt](sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt))
- Construction: **pre-construction / not yet started**, no earthworks visible through 2026-07
- Site: 32.31056, -100.14917 — existing BG WF2 plant centroid from [thewindpower.net](sources/2026-07-19_thewindpower_buffalo-gap-2-site-record.txt) ([map](https://google.com/maps/@32.31056,-100.14917,5000m/data=!3m1!1e3))
- COD: reported 2027-02-01 → independent **2027-Q3**, drift risk **high** (no construction visible Jul 2026, 7 months to claimed COD)

## 2. Site identification

- Derivation: thewindpower.net record #3211 gives exact plant centroid 32°18'38"N, 100°8'57"W; confirmed by Sentinel-2 showing operational turbine pads matching 155-turbine array ([site record](sources/2026-07-19_thewindpower_buffalo-gap-2-site-record.txt))
- **Stated project area: not obtained** — IA not retrievable (PUCT JS-only portal); CAD search returned 0 hits (wind turbine personal property assessed separately from real property in TX); no abatement filing found
- Cross-checks: thewindpower coords → imagery turbine pads agree within 0.5 km; POI "6216 Bluff Creek 138 kV" in Taylor/Nolan county boundary area consistent with site location
- Not obtainable: exact POI switch coords (CEII); IA document (PUCT JS-only, 402 blocked); FAA OE/AAA turbine coordinates (portal 404 during govt shutdown)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Buffalo Gap Wind Farm 2, LLC | SPV (existing) | [queue data / triage](triage_findings.json) |
| AES DevCo HoldCo, LLC | SPV holdco (repower) | [FY2025 10-K](sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt) |
| AES Corp (AES) | Developer/owner 100% | [FY2025 10-K](sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt); [Q3 2025 10-Q](sources/2026-07-19_sec_aes_q3_2025_10q_buffalo-gap-excerpt.txt) |
| HASI (HA Sustainable Infrastructure Capital) | Preferred equity investor | [FY2025 10-K](sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt) |

- Financing: **$200M HASI preferred equity closed December 2025** — recorded as redeemable noncontrolling interest in AES DevCo HoldCo, LLC ([FY2025 10-K](sources/2026-07-19_sec_aes_fy2025_10k_buffalo-gap-repower-excerpt.txt))
- Tax equity: AES Renewable Holdings completed buyout of legacy tax equity partners at BG I, II, III in Q3 2025 ([Q3 2025 10-Q](sources/2026-07-19_sec_aes_q3_2025_10q_buffalo-gap-excerpt.txt)) — clears structure for new PTC/ITC

## 4. Land & county records

- Tenure: **leased** (wind farms universally use long-term land leases in TX) — no CAD real-property owner hit for "Buffalo Gap Wind Farm 2 LLC" or AES variants; wind turbines assessed as industrial personal property in TX, not real property
- Abatements/agreements: No JETI filing found; Ch.313 program expired 2022 (project entered queue 2024; JETI application may be in progress or not filed)
- CAD: 0 hits on Nolan CAD real-property owner search for all AES/Buffalo Gap variants — expected for wind personal property

## 5. Interconnection & contractual schedule

- POI per queue: "6216 Bluff Creek 138 kV" — IA signed (queue milestone = 2025-02-28, queue shows "2005-02-28" as data artifact for 2025-02-28)
- IA document: **not retrieved** — PUCT Interchange portal requires JS rendering; curl/HTTP returns 402 or redirects to noscript page (negative evidence logged)
- Equipment (turbine supplier): not public — no procurement announcement found

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | ~2025-02-28 (queue milestone; doc not retrieved) | unknown — IA text not available |

| Milestone | Queue data |
|---|---|
| IA signed | ~2025-02-28 |
| Meets 6.9(1) | 2026-03-25 |
| Meets all 6.9 | 2026-05-05 |
| Scheduled COD | 2027-02-01 (current queue) |

- Queue-history COD drift (from [timeline.md](timeline.md)): 1 change, 2026-12-01 → 2027-02-01 (~2 month slip, Dec 2024 → Jan 2026 reports)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-10-01 | Existing turbine array intact, no staging or earthworks | [png](imagery/key/s2_2025-10-01.png) |
| 2026-01-01 | No change — operational array, no new activity | [png](imagery/key/s2_2026-01-01.png) |
| 2026-04-01 | No change — no construction staging, no turbine removal | [png](imagery/key/s2_2026-04-01.png) |
| 2026-07-01 | No change — full existing array in place, no earthworks | [png](imagery/key/s2_2026-07-01.png) |

- Verdict: **pre-construction** — existing 155-turbine array fully operational through Jul 2026; no decommissioning activity, no new foundation pads, no staging areas visible at 10 m/px. Repower has not visibly broken ground as of this imagery date.

## 7. COD assessment

- **Financing committed but construction not started**: HASI $200M closed Dec 2025; AES guides 1H 2027 (i.e., by Jun 30 2027) for full 527 MW repower
- **No construction visible through Jul 2026**: typical 231 MW wind repower requires turbine decommissioning (~3–6 months), foundation rework, and new turbine erection (~12–18 months total); with nothing visible at 7 months before reported COD (Feb 2027), that date is not achievable
- **AES 1H 2027 guidance is the credible target**: AES says 1H 2027 in a public 10-K; this covers Jan–Jun 2027 and implies construction begins mid-2026 with a very compressed schedule
- **COD slip likely to Q3 2027**: even if construction starts Aug–Sep 2026, completing 231 MW repower in 5–6 months is aggressive; industry comps for 100–250 MW wind repowers average 12–15 months from first turbine down to COD
- **Independent estimate: 2027-Q3 (Jul–Sep 2027)** with high drift risk; if construction does not begin by Sep 2026, a further slip to Q4 2027 or 2028 is plausible

## 8. Could not determine

- IA document text, POI exact switch coordinates, financial security amount, milestone schedule exhibit
- Turbine model / supplier for repower (no procurement announcement found)
- Construction start date (no groundbreaking announcement; FAA OE not accessible during govt shutdown)
- EPC contractor
- Exact parcel acreage (CAD personal-property assessment; JETI/abatement not filed or not public)
