# Dossier — Fagus Solar Park 2 SLF (25INR0672)

Researched 2026-07-22 · site 34.35099, -100.0493 · verdict **real_active**

## 1. Verdict

- **real_active** — this is Phase 2 of a 3-phase, co-located solar project at ETT's Fagus Substation; the shared EIA-860M plant record has reported status **(OP) Operating since the 2026-04 report, actual operating date 2025-12** ([eia_history.json](eia_history.json))
- Construction: **substantially_complete**, first ambiguous activity **2024-06** ([frame](imagery/key/s2_2024-06-25.png)), clear array by **2025-01** ([frame](imagery/key/s2_2025-01-01.png))
- Site: 34.35099, -100.0493 — EIA-860M plant coords, cross-validated by Google Places "MISAE SOLAR PROJECT" pin (~1 km) and POI-distance match to the "Tesla Substation" pin (~2.6 mi, matches IA's "~3 miles" line length), high confidence ([satellite view](https://www.google.com/maps/@34.35099,-100.0493,5000m/data=!3m1!1e3))
- COD: reported 2026-05-20 → independent **2025-Q4**, drift risk **low** (EIA says plant already operating; queue date is administratively stale, not a real slip)

## 2. Site identification

- Derivation: EIA-860M plant 67123 "Fagus Solar Park" (entity Excel Advantage Services, LLC) coordinates ([eia_history.json](eia_history.json)), cross-checked against Google Places "MISAE SOLAR PROJECT" pin at 385 FM1033, Childress TX (34.346201, -100.058146, ~1.0 km away, inside the built array) and imagery shape-match at the anchor
- No project area figure specific to Phase 2 exists; **stated combined-project area: 3,800 acres** per a 2018 developer YouTube post quoted in the Ch313 certificate ([Ch313 App 1613 cert](sources/2026-07-22_comptroller_ch313-1613-childress-excel-cert.pdf)) — covers all 3 phases together, imagery footprint at the anchor is consistent with a multi-hundred-MW array of that scale, unverified per-phase
- Cross-checks (each linked): EIA coords ↔ [Places pin](sources/) (~1.0 km) ↔ POI-distance to [Tesla Substation pin](sources/) (2.6 mi vs IA's stated "~3 miles", [Exhibit C-1](sources/2026-07-22_puct_35077-2433_seventh-amended-and-restated-erco_p60.png)) ↔ IA Exhibit C text ("Fagus Substation…approximately eight (8) miles southeast of Childress, Texas") — all agree
- Not obtainable: a distinct Phase-2-only sub-boundary — all 3 phases share one substation/collector system per Exhibit C-1, and 10 m Sentinel-2 resolution cannot separate them on the ground; no CAD parcel search performed this session

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Excel Advantage Services, LLC dba Misae Solar Park II | SPV / Designated Interconnection Agent, all 3 phases | Party on [IA 7th A&R](sources/2026-07-22_puct_35077-2433_seventh-amended-and-restated-ercot-standard-gene.pdf); Applicant on [Ch313 App 1613](sources/2026-07-22_comptroller_ch313-1613-childress-excel-cert.pdf) |
| Dr. Miguel A. Oneto / Latinoamericana de Energia (LAE) | original developer/sponsor | Ch313 cert quotes 2018 developer YouTube post ("Engineered by Miguel A. Oneto and LAE American Energy"); matches [IA 4th A&R](sources/unverified_2026-07-22_puct_35077-1658_fourth-amended-and-restated-ercot-standard-gener.pdf) recital naming "Latinoamericana de Energia" as original #20INR0091 sponsor |
| Greenalia Solar Power Misae III, LLC | co-principal for Phase 3 ONLY (not this INR) | Added via [Ch313 Amendment 2](sources/2026-07-22_comptroller_ch313-1613-childress-excel-amendagmt2.pdf) (~2024-06); added as Phase-3 co-tenant in [IA 7th A&R](sources/2026-07-22_puct_35077-2433_seventh-amended-and-restated-ercot-standard-gene.pdf) |
| M. A. Mortenson Company | EPC candidate | Owner-of-record on ACTIVE TCEQ stormwater NOI for "MISEA SOLAR PARK II" / "TESLA II…TO FAGUS TRANSMISSION LINE" (`tceq.py resolve --storm`) |
| Solv Energy, LLC | EPC candidate | Co-listed owner on the same ACTIVE TCEQ NOIs as Mortenson |

- Financing: not independently confirmed; Ch313 App 1613 cites Proposed Total/Qualified Investment **$395,300,000** and Limitation Amount $20,000,000 for the combined project ([cert](sources/2026-07-22_comptroller_ch313-1613-childress-excel-cert.pdf))

## 4. Land & county records

- Tenure: **unknown** — no lease/purchase language found in the IA amendments or Ch313 documents reviewed; no CAD parcel search performed this session (time-budget tradeoff)
- Ch313: **App No. 1613, Childress ISD**, original agreement 2022-02-11, Amendment 1 (2022-08-15), Amendment 2 (~2024-06, adds Greenalia as joint Applicant) ([cert](sources/2026-07-22_comptroller_ch313-1613-childress-excel-cert.pdf), [amend2](sources/2026-07-22_comptroller_ch313-1613-childress-excel-amendagmt2.pdf)) — filed under the ISD, so `ch313.py`'s name-key matcher missed it; found via web search instead
- Ch.312: one county-only candidate (#000004312, "Childress Solar Park LLC", zone 2017-01) **ruled OUT** — verified via `puct.py match --key` as a separate, older (2018) docket 35077-850, unrelated project
- CAD: not queried this session — recorded as could-not-determine, not a negative finding

## 5. Interconnection & contractual schedule

- POI per signed IA: "Generator's Fagus Substation…located in Childress County approximately eight (8) miles southeast of Childress, Texas. …Point of Interconnection will be located at TSP's [ETT's] first dead-end structure outside the Substation fence that terminates TSP's 345 kV transmission line from TSP's **Tesla Station**" ([7th A&R Exhibit C, p.42](sources/2026-07-22_puct_35077-2433_seventh-amended-and-restated-ercot-standard-gene.pdf)) — matches queue POI text "60501 Tesla 345 kV" exactly
- Equipment (Exhibit C): Generation Phase 2 (25INR0672) = 50 units × 3.3729 MW Sungrow SG3600UD-MV inverters = 168.64 MW nameplate (queue reports 166.57 MW — AC-rating rounding)
- TSP is **Electric Transmission Texas, LLC (ETT/AEP)**, not Oncor — REFRESH_DIRECTIVE did not specify

| IA document | Signed | Financial security posted |
|---|---|---|
| Fourth A&R ([pdf](sources/unverified_2026-07-22_puct_35077-1658_fourth-amended-and-restated-ercot-standard-gener.pdf)) — still single-phase, #20INR0091 only | 2023-08-17 | not itemized (pre-split) |
| Fifth A&R ([pdf](sources/2026-07-22_puct_35077-1923_fifth-amended-and-restated-ercot-standard-genera.pdf)) — **splits into Phase 1/2/3**, creates #25INR0672 | 2024-08-29 | $18,000,000 total (all 3 phases) |
| Sixth A&R ([pdf](sources/2026-07-22_puct_35077-2001_sixth-amended-and-restated-ercot-standard-genera.pdf)) | 2024-11-21 | $18,000,000 — unchanged |
| Seventh A&R ([pdf](sources/2026-07-22_puct_35077-2433_seventh-amended-and-restated-ercot-standard-gene.pdf)) — adds Greenalia as Phase-3 principal | 2026-03-12 | **$19,500,000** — increased |

(All schedules computed from the Original Agreement execution date **2019-02-21**; security totals are NOT broken out per phase in any exhibit.)

| Milestone (Generation Phase 2 / 25INR0672) | Fifth A&R (2024-08) | Sixth A&R (2024-11) | Seventh A&R (2026-03, current) |
|---|---|---|---|
| Scheduled Trial Operation | 2025-05-21 | 2025-08-21 | 2025-07-21 |
| Scheduled Commercial Operation | 2025-10-21 | 2025-12-21 | 2026-03-21 |

- Queue-history COD drift (from [timeline.md](timeline.md)): **7 changes** across 25 monthly snapshots (2024-06→2026-06) — 2025-12-01 → 2026-02-11 → 2026-02-10 → 2025-09-26 → 2025-10-03 → 2026-03-15 → 2026-05-14 → 2026-05-20 (current); queue already shows approved-for-energization (2025-05-29) and approved-for-synchronization (2025-07-07) achieved, but commercial-operation-approved still blank

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2023-01/11 | undisturbed cropland at anchor; unrelated older solar array visible ~2 km west | [2023-11](imagery/key/s2_2023-11-03.png) |
| 2024-06 | first faint field/grading pattern at anchor — ambiguous, ~1 month after phase-split IA filing window | [2024-06](imagery/key/s2_2024-06-25.png) |
| 2025-01 | clear graded/racked rectangular block array with access roads and pad structures | [2025-01](imagery/key/s2_2025-01-01.png) |
| 2025-06 | same footprint, darker/more uniform texture (partly cloudy) | [2025-06](imagery/key/s2_2025-06-25.png) |
| 2026-05 | large, fully built-out dark uniform block array; adjacent substation/switchyard complex visible | [2026-05](imagery/key/s2_2026-05-16.png) |

- Verdict: **substantially_complete** — consistent with EIA's independent claim of Operating status since 2025-12; imagery cannot distinguish which phase (1 vs 2) contributes which block, as all 3 phases share one substation per the IA's own one-line diagram

## 7. COD assessment

- Reported COD (2026-05-20, current queue snapshot) is a moving target — 7 revisions across 25 monthly reports; the underlying contractual Scheduled COD in the current signed IA (Seventh A&R) is **2026-03-21**, itself already 5 amendments removed from the original 2025-10-21 date
- EIA-860M (the shared plant record covering both phases) independently reports status **(OP) Operating since the 2026-04 report, with an actual operating date of 2025-12** — ahead of even the contractual 2026-03-21 date
- Satellite imagery corroborates a substantially-complete, stable array footprint by 2026-05, consistent with a plant that has been generating since late 2025
- Risk: EIA does not separate the two phases — "operating" could reflect Phase 1 (166.42 MW, in queue since 2018) carrying most of the reported capacity while Phase 2 (this INR, 166.57 MW) trails; no imagery or document evidence distinguishes the phases structurally, and equal unit counts (50 units each) offer no basis to suspect an asymmetric build
- **Independent estimate: 2025-Q4 (per EIA operating date), drift risk low** — the project is not lagging; if anything the queue's still-open status and 2026-05-20 COD figure are administratively stale relative to EIA's operating report

## 8. Could not determine

- Per-phase (Phase 1 vs Phase 2) split of the shared EIA plant's operating/capacity status — EIA reports one combined plant record for all 3 phases
- Land tenure (leased vs purchased) — not stated in any document reviewed; no CAD parcel search run this session
- Exact per-phase financial security amount — all IA Exhibit E figures are combined totals across all 3 phases
- Confirmed EPC (Mortenson vs Solv Energy vs a joint venture) — both appear as owner-of-record on the same active TCEQ stormwater NOIs with roles undifferentiated
- Whether "Misae Solar Park I" (the CIP/IKEA-owned complex referenced in a 2020 PV Magazine article quoted in the Ch313 cert) is geographically adjacent or entirely separate — Applicant explicitly denied any connection to a nearby App 1197 project, but the "Misae I" reference itself was not independently traced
