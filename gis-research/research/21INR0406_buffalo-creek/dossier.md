# Dossier — Buffalo Creek (21INR0406)

Researched 2026-07-19 · site ~29.330, -95.840 (low-medium confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — solar installation visible in [Sentinel-2 June 2021](imagery/key/s2_2021-06_first_activity.png) and [June 2026](imagery/key/s2_2026-06_present.png) chips at ~29.33°N 95.84°W in Fort Bend County; ERCOT approved-for-sync Jan 2022 confirms physical grid connection
- Construction: **substantially_complete**, first activity visible 2021-06 ([frame](imagery/key/s2_2021-06_first_activity.png))
- Site: ~29.330, -95.840 — imagery candidate on 345kV corridor SW of W.A. Parish, low-medium confidence ([map](https://google.com/maps/@29.330,-95.840,5000m/data=!3m1!1e3))
- COD: reported 2026-08-31 → independent **2026-Q4 to 2027-Q2**, drift risk **high** (19 drifts, 4.5 yr stall post-sync)

## 2. Site identification

- Derivation: Sentinel-2 chips at 29.33°N 95.84°W show dark module rows + white access road grid consistent with utility-scale solar; location ~12 km SW of W.A. Parish 345kV substation ([OSM confirmed at 29.4808, -95.6242](https://www.openstreetmap.org/#map=14/29.4808/-95.6242)) along the 345kV line toward Bailey switch
- **Stated project area: not determined** — PUCT IA not accessible (HTTP 402), Ch.313/JETI not found, CAD JS-gated — imagery footprint not sanity-checkable
- Cross-checks: W.A. Parish 345kV at 29.4808/-95.6242 (OSM); Fighting Jays (EIA 29.358/-95.746) separate chip showed no solar June 2026; candidate installation ≠ any EIA 860M registered plant ([EIA 860M May 2026](https://www.eia.gov/electricity/data/eia860m/))
- Not obtainable: Bailey switch exact coordinates (not in OSM, PUCT inaccessible), precise parcel boundaries

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Buffalo Creek, LLC (presumed) | SPV | ERCOT queue only; unverified |
| Unknown developer | developer | no web presence, no press release, no Ch.313/JETI found |
| Unknown EPC | EPC | not determined |
| Unknown offtaker | PPA | not determined |

- Financing: unknown — no PPA announcement, no financing PR found

## 4. Land & county records

- Tenure: **unknown** — FBCAD JS-gated (no owner-name results loadable via fetch)
- Abatements/agreements: **none found** — Ch.313 2023 supplemental PDF: no Fort Bend County entries; JETI current agreements: no solar/Fort Bend entries
- CAD: 0 hits retrievable (JS-gated portal; curl returns only HTML shell)

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "tap 345kV 44000 WA Parish – 44040 BAILEY"; W.A. Parish 345kV confirmed at 29.4808, -95.6242 (OSM); Bailey bus not in OSM
- Equipment: unknown — IA not retrievable (PUCT 402)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2020-04-16 | unknown (PUCT 402) |

| Milestone | ERCOT queue |
|---|---|
| IA signed | 2020-04-16 |
| Approved for energization | 2021-12-08 |
| Approved for synchronization | 2022-01-06 |
| Commercial operation | NOT ACHIEVED as of 2026-06-01 |

- Queue-history COD drift (from [timeline.md](timeline.md)): **19 drifts**, 2021-12-31 → 2026-08-31

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2021-06 | Solar array rows + access road grid visible at ~29.33°N 95.84°W — early installation stage | [png](imagery/key/s2_2021-06_first_activity.png) |
| 2025-12 | Same installation visible, substantially complete appearance | [png](imagery/s2_2025-12-01.png) |
| 2026-06 | Dark module rows present; cloud-partial but consistent with operating array | [png](imagery/key/s2_2026-06_present.png) |

- Verdict: **substantially_complete** — physical installation visible since mid-2021; not yet in EIA 860M as of May 2026 (not operationally registered); note: site candidate is low-medium confidence, imagery may partially overlap Fighting Jays or another nearby project

## 7. COD assessment

- Approved-for-sync Jan 2022 = ERCOT confirmed physical grid connection. No commercial operation 4.5 years later is highly anomalous; typical cause: grid studies, performance testing failure, equipment defect, or contractual/offtake issue
- Not in EIA 860M Operating or Planned (May 2026) — plant has not filed operational registration with EIA; unprecedented for a project that got approved-for-sync 4.5 years ago
- 19 consecutive short-term COD slips: each 1-6 months, consistent with a project "almost ready" that keeps failing the final gate. Pattern suggests a persistent blocking issue rather than construction delay
- 2026-08-31 (6 weeks away): implausible given zero construction milestone progress reported, not in EIA 860M, and no web presence; COD reporting appears pro-forma monthly extension
- Independent estimate: **2026-Q4 to 2027-Q2** — if the blocking issue resolves, the physical installation is largely done; if systemic (financing/offtake collapse), could slip to 2027 or later

## 8. Could not determine

- Developer / parent company identity (no web presence, TX SOS paywall, PUCT 402)
- Exact site parcel and acreage (CAD JS-gated, IA not obtainable)
- Reason for 4.5-year stall post-sync-approval (no public filings found)
- Financial security amounts from IA (PUCT 402)
- EPC contractor
- Offtaker / PPA status
- Precise site coordinates (gmaps 429 throughout; site candidate from imagery only)
