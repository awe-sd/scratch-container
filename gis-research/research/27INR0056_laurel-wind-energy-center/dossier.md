# Dossier — Laurel Wind Energy Center (27INR0056)

Researched 2026-07-19 · site 30.891, -102.298 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Oct 2024, Meets 6.9(1) Sep 2025; developer (Nova Clean Energy) confirmed via [BNB→Nova portfolio acquisition Apr 2024](https://www.pv-tech.org/?s=nova+clean+energy); no construction activity in satellite imagery as of Jul 2026
- Construction: **no_activity**, first activity not yet visible ([Jul 2026 chip](imagery/s2_2026-07-01.png))
- Site: 30.891, -102.298 — POI town anchor only, low confidence ([satellite view](https://www.google.com/maps/@30.891,-102.298,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 → independent **2028-Q2**, drift risk **high** (3 prior drifts, no construction started, ~40% capacity downsize in 2025)

## 2. Site identification

- Derivation: POI description "Solstice to Bakersfield (Bus# 60404–76002) 345kV Ckt 2 line tap" anchors to Bakersfield TX (~30.891°N, 102.298°W); turbines would be on mesas within ~15-30 km
- **Stated project area: unknown** — no abatement app, IA, or CAD doc retrieved; imagery footprint unverifiable
- Cross-checks: POI town anchor only; no independent parcel, Places pin, or FAA OE coordinate available
- Not obtainable: exact POI substation coordinates (CEII); FAA OE/AAA search portal returned 404; PUCT IA portal blocked (402)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Laurel Energy Center LLC | SPV (likely) | [infrasure.ai](sources/infrasure_project_page.md) — unverified; queue uses "Laurel Wind Energy Center LLC" |
| Nova Clean Energy | Developer/owner | [pv-tech Apr 2024](https://www.pv-tech.org/?s=nova+clean+energy): acquired 1 GW TX solar+wind from BNB Renewable Energy |
| Wanzek Construction (MasTec) | EPC | [infrasure.ai](sources/infrasure_project_page.md) — commercial intel, unverified |
| CPS Energy | PPA offtaker | [infrasure.ai](sources/infrasure_project_page.md) — commercial intel, unverified |

- Financing: No primary close announcement found; lenders cited by infrasure.ai (DNB, CIBC, NAB, DZ Bank) may be conflated with related Clearway project

## 4. Land & county records

- Tenure: **unknown** — expected leased (standard for TX wind); no lease docs found
- Abatements/agreements: post-2022 Ch.313 ineligible; JETI registry not publicly searchable; absence normal
- CAD: 0 hits in [Pecos CAD](https://www.pecoscad.org/Home/Search) for "laurel", "laurel wind", "nova clean", "wind energy", "wanzek" (2026-07-19) — consistent with leased ranchland (parcels stay under landowner names)

## 5. Interconnection & contractual schedule

- POI per queue: "Solstice to Bakersfield (Bus# 60404–76002) 345kV Ckt 2 line tap"
- IA PDF: **not retrieved** — PUCT Interchange portal blocked (HTTP 402, JS-only) in this environment

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-10-25 | unknown — PDF not retrieved |

| Milestone | Queue date |
|---|---|
| IA signed | 2024-10-25 |
| Meets 6.9(1) | 2025-09-15 |
| Meets all 6.9 | not yet |
| Construction start | not reported |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2027-01-31 → 2027-03-28 → 2027-12-31

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Undisturbed desert mesa + Bakersfield town; no turbine pads, grading, or road strings | [s2_2026-07-01.png](imagery/s2_2026-07-01.png) |
| 2026-07 | Grid S (~13 km S of anchor): undisturbed arroyo/mesa terrain | [grid_S.png](imagery/grid_S.png) |
| 2026-07 | Grid NW (~13 km NW of anchor): undisturbed desert canyon | [grid_NW.png](imagery/grid_NW.png) |

- Verdict: **no_activity** — all 3 retrieved chips show undisturbed terrain; 5 planned chips not retrieved (CDSE token expired); site anchor confidence low

## 7. COD assessment

- Reported 2027-12-31 has COD-drifted 3× (from 2027-01-31 originally); no contractual IA milestone schedule obtained
- As of Jul 2026: **no construction started** — no activity in satellite imagery near anchor, no FAA OE filings, no CAD parcel activity
- 307 MW wind with Wanzek EPC typically requires 18-24 months construction; with no groundbreaking visible by Jul 2026, a Dec 2027 COD requires immediate mobilization
- Capacity downsize ~502→307 MW in Aug–Sep 2025 may reflect a layout revision, partial abandonment, or split — reduces project risk but COD date did not reset
- Positive signals: IA signed Oct 2024, Meets 6.9(1) achieved Sep 2025; CPS Energy offtake (if confirmed) would drive urgency
- **Independent estimate: 2028-Q2, drift risk high**

## 8. Could not determine

- Exact turbine coordinates (FAA OE portal blocked/broken)
- PUCT IA milestone schedule and financial security amounts (portal blocked)
- CPS Energy PPA — primary source not found (commercial intel only)
- Wanzek EPC contract — primary source not found
- Project area in acres
- Nova Clean Energy financing close
- SPV exact legal name and TX SOS registration
- 5 of 8 planned imagery grid chips (CDSE token expired mid-session)
