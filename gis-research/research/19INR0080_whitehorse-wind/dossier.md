# Dossier — Whitehorse Wind (19INR0080)

Researched 2026-07-19 · site anchor 32.6281, -100.5456 · verdict **paper**

## 1. Verdict

- **paper** — 8 Sentinel-2 tiles across Fisher County (2026-07) + 1 historical frame (2020-01) show zero wind infrastructure; project was "approved for synchronization" Dec 2019 but never broke ground ([2026 contact sheet](imagery/contact_north.png), [2020 frame](imagery/s2_2020_north_hist.png))
- Construction: **no_activity**, first activity **never**
- Site: 32.6281, -100.5456 (POI anchor only) — Claytonville Substation per [OSM Overpass query](https://overpass-api.de/); name matches queue POI "68001 Clayton 345kV"; actual turbine field unknown (none built) ([satellite view](https://www.google.com/maps/@32.6281,-100.5456,5000m/data=!3m1!1e3))
- COD: reported 2026-12-31 → independent **none defensible**, drift risk **extreme** (14 slips / 8 yrs; zero construction)

## 2. Site identification

- Derivation: OSM substation name "Claytonville" at 32.6281, -100.5456 (345kV/138kV) matches queue POI "68001 Clayton 345kV" ([OSM query](https://overpass-api.de/api/interpreter?data=[out:json];(way[power=substation](32.4,-101.1,33.2,-99.5););out+center;))
- **Stated project area: unknown** — no IA retrieved, no abatement agreement found
- Cross-checks: POI text → Claytonville Substation (OSM); no further cross-checks (no pin, no parcel, no news)
- Not obtainable: actual turbine layout (nothing built); exact POI switch coordinates (PUCT CEII + portal blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Whitehorse Wind, LLC | SPV (assumed) | Queue data only — not verified via registry |
| Unknown | developer | Zero public footprint; TX Comptroller/SOS/SEC/OpenCorporates all blocked or 0 results |

- Financing: unknown — no press releases, no financing announcements, no SEC filings found

## 4. Land & county records

- Tenure: **unknown** — Fisher CAD owner-name search returned no results for "whitehorse"; all dynamic results
- Abatements/agreements: none found — TX Comptroller Ch.313 portal returns navigation page only; Rotan ISD / Hamlin ISD searches yielded 0 results
- CAD: 0 parcels under any variant of project/LLC name

## 5. Interconnection & contractual schedule

- POI per queue: "68001 Clayton 345kV" — corresponds to Claytonville Substation, Fisher/Nolan county border
- Equipment: unknown (IA not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PDF not retrieved) | 2018-12-05 | Unknown (queue shows financialSecurity = "Yes") |

| Milestone | Queue record | Notes |
|---|---|---|
| FIS approved | 2019-01-22 | |
| Approved for energization | 2019-12-12 | |
| Approved for synchronization | 2019-12-27 | ~7 years ago; COD never followed |
| Construction start | — | Never set |
| Commercial operation | — | Never set |

- Queue-history COD drift ([timeline.md](timeline.md)): **14 changes** — 2019-10-01 → 2026-12-31 over 8 years

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2020-01 | Undisturbed rangeland at time of "approved-for-sync"; no pads, no roads | [png](imagery/s2_2020_north_hist.png) |
| 2026-07 | Same undisturbed landscape, 8-tile county-wide grid; no wind infrastructure | [contact sheet](imagery/contact_north.png) |

- Verdict: **no_activity** — project never commenced construction; imagery 6 years apart shows no change

## 7. COD assessment

- Reported COD 2026-12-31 is the 14th revision of a COD that was first 2019-10-01; the project has been slipping continuously since before the original date
- Satellite imagery in both 2020 (approved-for-sync year) and 2026 confirms zero ground disturbance — no turbine pads, no access roads, no laydown areas anywhere in Fisher County
- A 418.9 MW wind farm takes 18–30 months to build once construction starts; with 5 months remaining to the reported COD and zero site activity, the 2026-12-31 target is impossible
- Financial security is "Yes" per queue data, meaning the project has not defaulted its ERCOT deposits — it is deliberately held dormant, not abandoned outright
- **No independent COD estimate is defensible.** The project has not started. If construction were to begin today (impossible given permitting/procurement timelines), earliest possible COD would be ~2029 at the soonest.

## 8. Could not determine

- Developer / parent company (TX Comptroller/SOS/SEC/OpenCorporates all blocked or returned 0 results)
- IA PDF and milestone schedule (PUCT interchange HTTP 402 on all queries)
- Financial security amount (IA not retrieved)
- FAA OE/AAA turbine filings (government shutdown — system offline)
- Ch.313/JETI abatement status (Comptroller portal inaccessible)
- Exact turbine layout location (nothing built; FAA OE unavailable)
