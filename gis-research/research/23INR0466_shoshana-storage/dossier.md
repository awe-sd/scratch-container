# Dossier — Shoshana Storage (23INR0466)

Researched 2026-07-19 · site ~28.80, -96.05 (low confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — Acciona is a credible developer with confirmed local abatements; POI infrastructure (Refuge 345kV bus #42400) is operational ([queue cross-ref](findings.json)); but FIS not approved after 4+ years and no IA signed
- Construction: **no_activity** — zero construction milestones in queue; imagery around STP plant shows undisturbed farmland; Refuge substation location not imaged (coordinates unknown)
- Site: ~28.80, -96.05 — POI-proximity inference from STP nuclear plant + Refuge 345kV circuit, **low confidence** ([satellite view](https://www.google.com/maps/@28.800,-96.050,5000m/data=!3m1!1e3))
- COD: reported 2028-05-30 → independent **2029-Q2 to 2030-Q2**, drift risk **high** (FIS not approved, IA unsigned, 5 prior slips = 65 mo total)

## 2. Site identification

- Derivation: POI text "Tap STP – Refuge ckt 27" → ERCOT bus 42400 (Refuge 345kV), Matagorda County; STP plant at 28.79556N, 96.04889W ([Wikipedia](https://en.wikipedia.org/wiki/South_Texas_Project)); coordinate estimate is STP vicinity, ~1-5km from Refuge substation whose exact location is not in OSM or public GIS databases
- **Stated project area: not determinable** — MCHD PDF not readable (no poppler); no Ch.313 app; no CAD parcels; no IA
- Cross-checks: Peyton Creek Wind II (20INR0155) also connects to Refuge 345kV (ERCOT bus 42400) and was approved-for-synchronization 2025-02-05 — confirms substation is real and operational; no Google Maps pin found (429 rate-limited); no parcel address in press coverage
- Not obtainable: Exact Refuge substation coordinates (not in OSM/Nominatim/ArcGIS public layers; CEII equivalent); Peyton Creek Wind turbine locations (USGS WTDB blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Shoshana Storage Project LLC | SPV | [ERCOT queue](https://www.ercot.com/); [Bay City Tribune 2024-04-30](sources/2026-07-19_baycitytribune_county-abatement.html) |
| Acciona (ACCIONA Energía S.A.) | developer/owner | [Bay City Tribune](sources/2026-07-19_baycitytribune_county-abatement.html): "Shoshana Storage's parent company, Acciona" |
| EPC | unknown | — not named in any source found |
| offtaker/PPA | unknown | — not announced publicly |

- Financing: not closed — no press release, no project financing announcement found; consistent with pre-FIS stage (financing rarely closes before IA)

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found for Shoshana/Acciona at Matagorda County (propaccess.trueautomation.com cid=235); expected to be leased/optioned but not yet filed; CAD ownership transfers typically occur closer to construction start
- Abatements: **Matagorda County Ch.312** — 100% abatement, 5 years, ~$2M total to county; unanimously approved 2024-04-28 ([Bay City Tribune](sources/2026-07-19_baycitytribune_county-abatement.html)); **Matagorda Regional Medical Center Hospital District** — abatement hearing held November 2024 ([MCHD notice](sources/2026-07-19_mchd_nov2024_abatement-hearing.pdf))
- Ch.313/JETI: N/A — Ch.313 ended 2022; project entered queue post-cutoff; no JETI found

## 5. Interconnection & contractual schedule

- POI per queue: "Tap STP – Refuge ckt 27" — ERCOT bus 5915 (STP) to bus 42400 (Refuge 345kV), circuit 27 ([queue data](findings.json))
- FIS requested: 2022-05-16; **NOT approved** as of 2026-06-01 (50 snapshots, 4+ years stalled)
- IA: **not signed** — confirmed by queue milestone data

| IA document | Signed | Financial security posted |
|---|---|---|
| — | IA not signed | — |

| Milestone | Status |
|---|---|
| In-Service | not scheduled (IA unsigned) |
| Trial Operation | not scheduled |
| Scheduled COD | not scheduled |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2023-12 → 2024-06 → 2025-06 → 2026-08 → 2028-05; 65 months of cumulative slippage since initial entry

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | STP plant + 2km radius: nuclear complex, farmland, no BESS pad | [stp_center](imagery/s2_2026-07-01_stp_center.png) |
| 2026-07-01 | STP + 6km xwide: transmission corridors NW, heavy clouds south; no BESS | [xwide](imagery/s2_2026-07-01_stp_xwide.png) |
| 2026-07-01 | 2km NW of STP: farmland + transmission towers, no BESS pad | [stp_nw](imagery/s2_2026-07-01_stp_nw.png) |

- Verdict: **no_activity** — no BESS pad visible in any chip; note coverage limited to STP plant vicinity; Refuge substation location unknown and not imaged; CDSE auth expired mid-session preventing further coverage

## 7. COD assessment

- **2028-05-30 is highly aggressive**: requires FIS approval (~0-6 mo), IA negotiation and signing (~6-12 mo), financial security, equipment procurement, and 12-18 month BESS construction — all from today
- FIS has been stalled since May 2022 (4+ years); no public indication from ERCOT that study is completing; the study delay is the primary risk
- 5 prior COD slips totaling 65 months show a pattern of study-queue delay, not one-time adjustment
- Acciona has operating BESS portfolio in the US but no confirmed Texas BESS commissioned project yet (none found in press)
- Dual abatements (county + hospital district) signal real local commitment and investment by Acciona in the entitlement process
- **Independent estimate: 2029-Q2 to 2030-Q2, drift risk high** — assumes FIS approval in 2026-2027, IA signed 2027-2028, BESS build 12-18 months

## 8. Could not determine

- Exact site location/parcel (Refuge substation not in public GIS; no CAD parcels; no IA; no Google Maps pin)
- Project area in acres (no IA, no Ch.313, no accessible CAD data)
- EPC contractor (not named in any source)
- PPA/offtaker (not announced)
- Financial security amounts (IA not signed)
- Outcome of Hospital District abatement hearing (PDF text not extractable)
- FIS completion timeline (ERCOT study queue not publicly tracked at project level)
- TX SOS/Comptroller LLC details for Shoshana Storage Project LLC (JS-rendered, not accessible)
