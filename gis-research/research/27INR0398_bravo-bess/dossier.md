# Dossier — Bravo BESS (27INR0398)

Researched 2026-07-19 · site 27.32760, -99.41160 · verdict **real_early**

## 1. Verdict

- **real_early** — credible developer (OCI Energy, active BESS financier) with confirmed substation POI, but FIS pending 19+ months, no IA, no site activity ([imagery](imagery/key/s2_2026-07_2km_cenizo.png))
- Construction: **no_activity**, first activity not yet observed
- Site: 27.32760, -99.41160 — POI substation lookup (Cenizo 345kV OSM way 451971746, Census-confirmed Webb County) ([map](https://google.com/maps/@27.3276,-99.4116,5000m/data=!3m1!1e3))
- COD: reported 2027-12-12 → independent **2029-Q1**, drift risk **high** (FIS stalled 19+ months, no IA)

## 2. Site identification

- Derivation: ERCOT POI "Tap 345kV 80220 CENIZO7A - 80224 TIEMPO7A" → Cenizo Substation confirmed OSM way 451971746 at 27.3276°N 99.4116°W; Census geocoder confirms Webb County (Laredo South-El Cenizo CCD) ([OSM](https://www.openstreetmap.org/way/451971746))
- **Stated project area: unknown** — no IA, no abatement doc, no CAD parcel accessible; imagery footprint unverifiable (expected 10-40 ac for 207 MW BESS)
- Cross-checks: POI substation → OSM coordinates → Census geocoder all agree. OCI Energy website lists "Bravo" as Zapata County — discrepancy likely county-line ambiguity; substation is definitively Webb County.
- Not obtainable: TIEMPO substation exact coords (not in OSM; CEII); parcel boundaries (Webb CAD portal non-operational)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Bravo BESS LLC | SPV | [TX SOS #0805720787](sources/2026-07-19_ocienergy_ownership_summary.txt) — Delaware foreign LLC, inc. 2024-09-24, Austin TX office |
| OCI San Antonio Bravo BESS LLC | Related SPV | [TX SOS](sources/2026-07-19_ocienergy_ownership_summary.txt) — same date/type/address, likely co-borrower or companion entity |
| OCI Energy (San Antonio TX) | Developer/owner | [ocienergy.com/projects](sources/2026-07-19_ocienergy_projects_summary.txt) — lists Bravo 200 MW BESS under development |
| OCI Enterprises Inc. → OCI Holdings (Korea) | Parent chain | [ocienergy.com/about](sources/2026-07-19_ocienergy_ownership_summary.txt) |

- Financing: OCI Energy secured ING construction financing Sep 2025 for unnamed TX BESS project; $130M Greenprint Capital tax equity Jun 2026 for Alamo City BESS (different project). Bravo BESS financing not separately confirmed. ([source](sources/2026-07-19_ocienergy_ownership_summary.txt))

## 4. Land & county records

- Tenure: **unknown** — no deed/lease found; Webb CAD portal non-operational (webbad.com → GoDaddy parked; SSL cert error on alternate URL)
- Abatements: No Ch.312/313 or JETI found for Webb County. Note: OCI's website places "Bravo" in Zapata County; Zapata County $88M abatement reported in triage (distinct sub-project or same project with imprecise county). Ch.313 expired 2022 — absence of abatement expected for 2024-vintage project.
- CAD: 0 records obtainable (portal inaccessible)

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 345kV 80220 CENIZO7A - 80224 TIEMPO7A" — Cenizo Substation confirmed (ETT-operated, 345 kV, Webb County). TIEMPO substation not located in OSM.
- IA: **not signed** — FIS not yet approved; no PUCT interchange filing expected at this stage.

| IA document | Signed | Financial security posted |
|---|---|---|
| None found | — | — |

| Milestone | Status |
|---|---|
| Screening started | 2024-11-26 |
| Screening complete | 2025-02-18 |
| FIS requested | 2024-11-21 |
| FIS approved | — (pending 19+ months as of Jun 2026) |
| IA signed | — |

- Queue-history COD drift (from [timeline.md](timeline.md)): 1 change, 2027-12-08 → 2027-12-12 (4-day shift Jan 2025). Stable since then but no post-screening gates achieved.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-01 | Cenizo Substation only; undisturbed brushland, no construction | [png](imagery/key/s2_2026-01_2km_cenizo.png) |
| 2026-07 | Same; no grading, pad, or container rows within 2 km of substation | [png](imagery/key/s2_2026-07_2km_cenizo.png) |

- Verdict: **no_activity** — two frames across 6 months confirm zero ground disturbance near the POI substation; build not started. Resolution (10 m/px) can confirm absence of a 10-40 ac gravel pad unambiguously.

## 7. COD assessment

- **FIS still pending** (19+ months since request Nov 2024): without FIS approval there can be no IA. This is the single largest schedule gate. No FIS approval timeline is public.
- **Minimum-path COD logic**: FIS approval (unknown, plausibly 6-12 more months given ERCOT congestion study queue) + IA execution + land/permit work (3-6 months) + BESS procurement/construction (12-18 months) = 21-36 months from today → Q2-2028 best case, Q1-2029 base case.
- **Reported COD 2027-12-12**: implies IA execution by ~mid-2026 and construction start by ~Jan 2027. IA has not been executed as of Jun 2026; this timeline is no longer achievable.
- **OCI Energy is real**: active developer with financed/under-construction BESS pipeline (Alamo City broke ground May 2026). Bravo is on their public project page. Not a paper project — but not close to breaking ground.
- **Drift risk high**: project has cleared only triage-level gates (screening); every remaining gate represents potential delay. South Texas grid is not congested at 345kV level so FIS may not be a major bottleneck, but ERCOT study queues remain slow.
- **Independent COD estimate: 2029-Q1** (±2 quarters)

## 8. Could not determine

- FIS approval status/timing (ERCOT internal study)
- PUCT IA filing (none exists yet; portal requires JS rendering)
- Land parcel / acreage (Webb CAD inaccessible; no abatement doc)
- Exact TIEMPO substation coordinates (not in OSM; CEII)
- Whether OCI's ING Sep 2025 construction financing covers Bravo BESS specifically
- Offtaker / PPA counterparty
- EPC contractor
