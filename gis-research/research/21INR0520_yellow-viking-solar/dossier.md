# Dossier — Yellow Viking Solar (21INR0520)

Researched 2026-07-20 · site 32.317, -97.629 · verdict **real_early**

## 1. Verdict

- **real_early** — $689M construction-to-term financing closed Feb 2026 ([BusinessWire](sources/lydian_financing_businesswire.md)); IA Amendment 3 signed 2026-07-02 ([Amend 3](sources/2026-07-19_puct_35077-2523_amendment-no-3-to-the-standard-generation-interc.pdf)); project contractually active
- Construction: **pre-construction**, NTP deadline 2025-07-01 is 12 months past with no ERCOT construction-start milestone
- Site: 32.317, -97.629 — EIA-860M plant 67222 coords + IA Exhibit C anchor (FM 2174 SE Hood County); not confirmed by imagery ([map](https://www.google.com/maps/@32.317,-97.629,5000m/data=!3m1!1e3))
- COD: reported 2027-07-13 → independent **2027-Q4**, drift risk **high** (no construction start, 12-mo NTP overrun)

## 2. Site identification

- Derivation: EIA-860M plant 67222 "Yellow Vikings" matched to Lydian Energy by county+prime-mover+MW ([eia_history.json](eia_history.json)); corroborated by IA Exhibit C: "Nautilus Switch, FM 2174, ~25 miles west of Cleburne, Hood County TX" ([IA Exhibit C](sources/2026-07-19_puct_35077-1523_interconnection-agreement-between_p30.png))
- **Stated project area: 4,078 acres** per GEM wiki search snippet (gem.wiki/Yellow_Vikings_solar_farm, 403 on direct fetch) — imagery not obtained to verify footprint
- Cross-checks: EIA coords 32.31664, -97.62889 (Somervell Co label); IA text: Hood County; GEM wiki: SE Hood County; Somervell County abatement also exists → site straddles Hood/Somervell county line, consistent with all three sources
- Not obtainable: exact parcel boundaries (CAD 0 hits under LLC/developer; landowner names unknown); imagery (CDSE HTTP 402 credit exhaustion on 2026-07-20)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Yellow Viking Development One, LLC | SPV | party on [IA](sources/2026-07-19_puct_35077-1523_interconnection-agreement-between-oncor-electric.pdf) + all amendments |
| Lydian Energy | developer/owner | [financing PR](sources/lydian_financing_businesswire.md); EIA entity name |
| Excelsior Energy Capital | Lydian backer | [energy-storage.news](https://www.energy-storage.news/lydian-energy-secures-us689-million-for-three-us-bess-and-solar-projects/) |
| European Energy (Denmark) | prior developer | [triage.md](triage.md); PM Knud Erik Andersen |
| CIBC + MUFG | lenders | [financing PR](sources/lydian_financing_businesswire.md) |
| unnamed investment-grade | PPA (100 MW) | [financing PR](sources/lydian_financing_businesswire.md) |

- Financing: $689M construction-to-term + tax credit bridge + co-investment bridge + LC facility closed **2026-02-17**; Yellow Viking is one of three projects in the deal (with Faraday BESS/Utah and AC Ranch 1 Solar/NM)

## 4. Land & county records

- Tenure: **leased** (inferred — 0 CAD hits under LLC or developer in Hood or Somervell CAD; expected for ranchland lease portfolio)
- Abatements: Hood County abatement voted "no longer active" **Feb 2025** ([hcnews.com snippet](https://www.hcnews.com/stories/countys-tax-abatement-agreement-with-yellow-viking-solar-farm-no-longer-active,65733)); Somervell County abatement amendment hearing **Feb 12 2024** (extension requested; SCS Salon site down for upgrade — outcome not confirmed)
- CAD: 0 parcels under Yellow Viking / Lydian / European Energy in Hood or Somervell CAD

## 5. Interconnection & contractual schedule

- POI per signed IA: "Hood County, Nautilus Switch in Comanche Peak – Timberview Switch 345kV line, FM 2174, ~25 miles west of Cleburne TX" ([IA Exhibit C](sources/2026-07-19_puct_35077-1523_interconnection-agreement-between_p30.png))
- Equipment (Amend 3): 45 × SMA inverters, 4.312 MVA each = 194.04 MVA / **172.80 MW** dispatched

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1523_interconnection-agreement-between-oncor-electric.pdf)) | 2022-10-25 | $4,724,586 LC by 2022-10-18 |
| Amendment No. 1 ([pdf](sources/2026-07-19_puct_35077-2154_amendment-no-1-to-the-standard-generation-interc.pdf)) | filed 2025-06-13 | Steps up to $13,784,627 by 2025-07-01 |
| Amendment No. 2 ([pdf](sources/2026-07-19_puct_35077-2493_amendment-no-2-to-the-standard-generation-interc.pdf)) | filed 2026-05-27 | Unchanged |
| Amendment No. 3 ([pdf](sources/2026-07-19_puct_35077-2523_amendment-no-3-to-the-standard-generation-interc.pdf)) | 2026-07-02 | Unchanged |

| Milestone | Original IA | Amendment 1/2/3 |
|---|---|---|
| In-Service | 2024-04-18 | **2027-05-13** |
| Trial Operation | 2024-05-01 | **2027-05-28** |
| Scheduled COD | 2024-07-26 | **2027-07-13** |
| NTP (construction) | 2023-08-18 | **2025-07-01** |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2022-12-26 → 2024-07-26 → 2026-11-07 → 2027-07-13; in reports since 2020-10 (69 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-20 | Not obtained — CDSE HTTP 402 (credit exhaustion) | — |

- Verdict: **pre-construction** — EIA reports "(L) Regulatory approvals pending. Not under construction" as of 2026-05-01; consistent with 0 ERCOT construction milestones

## 7. COD assessment

- Contractual COD **2027-07-13** confirmed across three consecutive amendments, including Amend 3 signed 2026-07-02 — schedule is grounded and actively maintained
- However, NTP construction deadline was **2025-07-01** (12 months ago); no ERCOT construction-start milestone; EIA still shows "(L) not under construction" as of May 2026
- EIA COD history: 2026-11 (early reports) → 2026-10 → **2027-10** (latest) — 1 quarter beyond contractual, suggesting EIA independently expects a modest slip
- For: $13.8M LC posted (full step-up), $689M financing closed, Amend 3 actively modifying equipment specs — project is not abandoned
- Against: 41% capacity downsize (289→171 MW) in 2025; Hood County abatement terminated Feb 2025; FIS never approved (unusual for a 2022 IA); 4.5 years total COD drift across 3 slips
- In-Service deadline 2027-05-13 is only **10 months away** from today — essentially no margin for a project not yet under construction
- **Independent estimate: 2027-Q4, drift risk high** — COD 2027-07-13 requires construction start and full completion in ≤10 months; if NTP issued recently (summer 2026), a Q4 2027 COD is achievable but tight; a further slip to 2028 is the base-case risk

## 8. Could not determine

- Whether construction NTP was actually issued on/after 2025-07-01 (no public announcement found)
- EPC contractor identity
- PPA offtaker identity
- Reason for Hood County abatement termination (hcnews.com 403)
- Outcome of Somervell County abatement amendment hearing (scsalon.org 404)
- FIS approval status (missing — unusual for a 2022 IA project)
- Site imagery (CDSE credits exhausted)
- Exact parcel boundaries (CAD under landowner names)
