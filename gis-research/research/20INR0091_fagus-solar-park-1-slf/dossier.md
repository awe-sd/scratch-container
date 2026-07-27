# Dossier — Fagus Solar Park 1 SLF (20INR0091)

Researched 2026-07-22 · site 34.35099, -100.0493 · verdict **real_active**

## 1. Verdict

- **real_active** — plant reports EIA-860M status **(OP) Operating**, actual operating date **2025-12** ([eia_history.json](eia_history.json)); satellite confirms fully built solar arrays at the coordinates ([frame](imagery/key/s2_2026-06-10.png))
- Construction: **substantially_complete/operating**, first activity not bracketed (already operating at first useful imagery pull) ([frame](imagery/key/s2_2026-06-10.png))
- Site: 34.35099, -100.0493 — EIA-860M coords cross-validated against a Google Places delivery pin (0.97 km away) and IA text ("~8 mi SE of Childress"), high confidence ([map](https://www.google.com/maps/@34.35099,-100.0493,5000m/data=!3m1!1e3))
- COD: reported 2026-05-20 → independent **2025-Q4** (EIA actual-ops date), drift risk **low** (plant is real & already generating; queue/IA dates are paperwork lag)

## 2. Site identification

- Derivation: EIA-860M plant coordinates (plant 67123 'Fagus Solar Park', entity Excel Advantage Services LLC) ([eia_history.json](eia_history.json)) cross-validated by imagery showing complete solar arrays at that point ([frame](imagery/key/s2_2026-06-10.png))
- Stated project area: **3,970 acres** per PR Newswire financing announcement for "Misae Solar Park II" (our combined Phase 1+2) ([PR](sources/2026-07-22_prnewswire_mufg-nomura-388m-greenalia-misae-ii-financing.html)) — Greenalia's own site states ~1,000 ha (~2,471 ac) for the same project ([Greenalia](sources/2026-07-22_greenalia_misae-ii-financing-official.html)), a gross-parcel-vs-footprint discrepancy, not resolved; imagery footprint (multiple large polygons spanning several km) is consistent with either figure — unverified precisely
- Cross-checks (each linked): Google Places pin "MISAE SOLAR PROJECT", 385 FM1033, Childress TX ([gmaps.py places](log.md)) 0.97 km from EIA coords; IA Exhibit C text "Fagus Substation... approximately eight (8) miles southeast of Childress, Texas" ([IA](sources/2026-07-22_puct_35077-2433_seventh-amended-restated-ercot-standard-gia.pdf) p.42) — bearing/distance computed from Childress city center agrees within 2 mi / 5° across all three site candidates (see log.md); TCEQ stormwater NOI facility "TESLA II TESLA TO FAGUS TRANSMISSION LINE" confirms the same substation-tie naming
- Not obtainable: a phase-level footprint boundary — Exhibit C-1 is an electrical one-line diagram only (no site plan), so which specific polygon in imagery is Phase 1 (ours) vs. Phase 2 (sibling 25INR0672) vs. neighboring unrelated Misae-family projects cannot be visually distinguished at 10 m/px

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Excel Advantage Services, LLC dba Misae Solar Park II | SPV / Designated Interconnection Agent | party on all 7 IA amendments ([7th Amend](sources/2026-07-22_puct_35077-2433_seventh-amended-restated-ercot-standard-gia.pdf)) |
| Greenalia S.A. (Spain) | developer/parent (probable) | [financing PR](sources/2026-07-22_prnewswire_mufg-nomura-388m-greenalia-misae-ii-financing.html), [Greenalia official](sources/2026-07-22_greenalia_misae-ii-financing-official.html) — "inaugural"/"first" US project |
| M.A. Mortenson Co. / SolvEnergy, LLC | EPC candidates | TCEQ stormwater NOI owner names on Misae/Fagus-line permits (log.md D3) |
| Toyota (subsidiaries) | PPA offtaker | [Greenalia official](sources/2026-07-22_greenalia_misae-ii-financing-official.html) |
| MUFG Bank + Nomura Securities (+ Barclays Ireland, green loan) | lenders | [financing PR](sources/2026-07-22_prnewswire_mufg-nomura-388m-greenalia-misae-ii-financing.html) |

- Financing: **$388M** closed ($295M construction-to-term loan + $93M LC facility; MUFG Administrative Agent) per PR Newswire; Greenalia states €383M total incl. $122.7M green loan ([Greenalia](sources/2026-07-22_greenalia_misae-ii-financing-official.html)) — construction reported **72% complete as of 2025-03-25**

## 4. Land & county records

- Tenure: **unknown** — no Ch313/JETI filing exists to state it (see below), no CAD search performed
- Abatements/agreements: **Ch.313/JETI — confirmed NEGATIVE** across 4 key variants (`Fagus`, `Misae`, `Excel Advantage`, county `Childress`) ([ch313.py resolve](log.md)); Ch.312 has only an unrelated county-only candidate ("Childress Solar Park LLC", a different plant) — this project has **no Texas property-tax abatement paper trail**, unusual for a 330+ MW project but not disqualifying (financing/EPC/EIA/imagery evidence is independently overwhelming)
- CAD: not searched (deprioritized — abatement route already exhausted and negative; other evidence sufficient for verdict)

## 5. Interconnection & contractual schedule

- POI per signed IA: "Fagus Substation... located in Childress County approximately eight (8) miles southeast of Childress, Texas... Point of Interconnection... terminates TSP's 345 kV transmission line from TSP's Tesla Station" ([7th Amend](sources/2026-07-22_puct_35077-2433_seventh-amended-restated-ercot-standard-gia.pdf) Exhibit C) — matches queue POI "60501 Tesla 345kV" exactly
- **This is a shared 3-phase IA**: Generation Phase 1 = our INR 20INR0091 (168.64 MW), Phase 2 = sibling 25INR0672 (168.64 MW, same SPV), Phase 3 = 26INR0524 (171.98 MW, transferred to Greenalia Solar Power Misae III, LLC — a *different* owner, in the 6th Amendment) — all three tie into one Fagus Substation ([one-line drawing](sources/2026-07-22_puct_35077-2433_seventh-amended-restated-ercot-st_p60.png))
- Equipment: Phase 1 = 50× Sungrow SG3600UD-MV inverters, 168.64 MW nominal

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-22_puct_35077-922_ercot-standard-interconnection-agreement-between.pdf)) | 2019-02-21 | not itemized in text extracted |
| 6th Amend (adds 3-phase structure, transfers Phase 3) ([pdf](sources/2026-07-22_puct_35077-2001_sixth-amended-and-restated-ercot-standard-genera.pdf)) | 2024-11-21 | $18,000,000 |
| 7th Amend (current) ([pdf](sources/2026-07-22_puct_35077-2433_seventh-amended-restated-ercot-standard-gia.pdf)) | 2026-03-12 | $19,500,000 — rose with re-schedule |

| Milestone (Phase 1 / our INR) | 6th Amend (2024) | 7th Amend (2026, current) |
|---|---|---|
| Trial Operation | 2025-03-21 (73mo) | 2025-08-21 (78mo) |
| Scheduled COD | 2025-05-21 (75mo) | 2026-03-21 (85mo) |

(Months are counted from the Original Agreement execution date, 2019-02-21, per Exhibit B's fixed formula.)

- Queue-history COD drift (from [timeline.md](timeline.md)): **11 changes** since 2018-05, current value 2026-05-20 held since 2026-05; queue's own milestone data shows **Approved for energization 2025-05-29** and **Approved for synchronization 2025-08-04** — both late-stage ERCOT grid gates cleared mid-2025, consistent with EIA's 2025-12 actual-operating claim

## 6. Satellite timeline

Construction-history frames (2023 → 2025) below are copied in from sibling INR 25INR0672's verified key series, added 2026-07-22 (imagery-fix pass) — both INRs are phases of the SAME shared EIA plant (67123 "Fagus Solar Park") at the SAME physical site/substation (Exhibit C-1 one-line diagram, §5 above), so the pre-2026 construction history applies to this project too even though it wasn't separately re-shot at the time of the original scan. Imagery still cannot distinguish which polygon belongs to Phase 1 (ours) vs. Phase 2 (sibling) — see §8.

| Date | Observation | Frame |
|---|---|---|
| 2023-01/11 | undisturbed cropland at anchor; unrelated older solar array visible ~2 km west | [2023-01-27](imagery/key/s2_2023-01-27.png) |
| 2024-06 | first faint field/grading pattern at anchor — ambiguous | [2024-06-25](imagery/key/s2_2024-06-25.png) |
| 2025-01 | clear graded/racked rectangular block array with access roads and pad structures | [2025-01-01](imagery/key/s2_2025-01-01.png) |
| 2025-06 | same footprint, darker/more uniform texture (partly cloudy) | [2025-06-25](imagery/key/s2_2025-06-25.png) |
| 2026-05 | large, fully built-out dark uniform block array; adjacent substation/switchyard complex visible | [2026-05-16](imagery/key/s2_2026-05-16.png) |
| 2026-06-10 | Multiple large, complete, uniform dark solar-panel-row polygons with access roads at and around site coords — fully built, not bare earth (this project's own original frame) | [s2_2026-06-10](imagery/key/s2_2026-06-10.png) |

- Verdict: **substantially_complete/operating** — no historical bracket pulled per playbook's present-first rule, since the site is already built at first observation and EIA independently dates first operation to 2025-12; resolution cannot distinguish which polygon is specifically Phase 1 vs. neighboring phases/projects. The imported 2023→2026-05 series (shared with sibling 25INR0672) corroborates the same construction arc independently.

## 7. COD assessment

- Queue's reported COD claim (2026-05-20) and even the just-signed 7th Amendment's contractual COD (2026-03-21) both trail EIA's independently reported actual-operating date of **2025-12** — the physical plant appears ahead of the paperwork, the reverse of the usual "paper project slipping" pattern
- Developer's own financing PR (2025-03) stated 72% construction complete and an "expected COD Q3 2025" target — a year-old developer target that landed close to EIA's claimed Dec-2025 actual date
- Queue milestone data (sync-approved 2025-08, energization-approved 2025-05) independently corroborates a mid-to-late-2025 completion window
- Risk/open question: the ~5-month gap between EIA's Dec-2025 "operating" date and the queue's May-2026 COD claim is not explained by any single document — possibly partial/phased energization (3 phases sharing one substation), a synchronization-vs-commercial-operation distinction, or simple field lag in the queue's `projectCod` value
- **Independent estimate: 2025-Q4 (per EIA actual-operating date), drift risk low** — the plant is real, financed, built, and (per the best independent evidence available) already generating; the remaining COD uncertainty is administrative, not existential

## 8. Could not determine

- Which specific imagery polygon corresponds to Phase 1 (our INR) vs. Phase 2 (sibling) vs. neighboring unrelated Misae-family solar projects — no site plan/plat was found in any IA exhibit (Exhibit C-1 is an electrical one-line only)
- Exact reason for the ~5-month gap between EIA's Dec-2025 operating date and the queue's May-2026 COD claim
- Land tenure (leased vs. purchased) — no Ch313/JETI filing exists to state it, and CAD parcel search was not performed
- Precise corporate linkage document between Excel Advantage Services, LLC and Greenalia S.A. (affiliation is high-confidence from shared branding/capacity/location, not from a single filed document)
- A single confirmed EPC — TCEQ NOI permits name both Mortenson and SolvEnergy as owner/customer, unclear if one, both, or sequential
