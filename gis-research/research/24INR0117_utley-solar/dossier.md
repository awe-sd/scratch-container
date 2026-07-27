# Dossier — Utley Solar (24INR0117)

Researched 2026-07-19 · site ~31.813, -96.148 (low confidence) · verdict **unclear**

## 1. Verdict

- **unclear** — IA signed Dec 2025 is a real milestone, but FIS never approved after 4+ years, financial security never posted, developer has zero public web presence, and no independent ground evidence (parcels, permits, press, imagery at correct site) was found
- Construction: **no_activity** — no solar activity visible in any chip; note: site not conclusively imaged (CDSE auth failed for revised candidate area)
- Site: ~31.813, -96.148 — POI-infrastructure method, low confidence ([map](https://www.google.com/maps/@31.813,-96.148,10000m/data=!3m1!1e3)); actual solar field parcel location unknown
- COD: reported 2028-05-11 → independent **2029-Q2**, drift risk **high** (5 slips, 49-mo total; FIS missing; no financial security)

## 2. Site identification

- Derivation: POI "Tap 345kV 3381 Big Brown Switch - 3391 Jewett" → Big Brown W switch coordinates **31.813367°, -96.147730°** recovered from co-project 29INR0298 POI text in [ERCOT GIS parquet](sources/2026-07-19_ercot_parquet_bigbrown-context.json); site is on agricultural land somewhere along this 345kV corridor in southern Freestone Co.
- **Stated project area: not obtained** — no abatement application, IA, or CAD parcel retrieved; 221.78 MW solar PV implies ~800–1,200 acres typical footprint
- Cross-checks: none independent — no Google Maps pin (429), no parcel situs (Freestone CAD maintenance), no news/photo coords
- Not obtainable: exact tap point coordinates (CEII); IA schedule exhibit (PUCT Interchange HTTP 402 on all attempts); developer identity (primary)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Utley Solar, LLC | SPV (inferred) | queue listing in [ERCOT GIS parquet](sources/2026-07-19_ercot_parquet_utley-solar-history.json) |
| Palmera Solar Development LLC | developer (unverified) | aggregator-sourced only; zero primary web presence confirmed by exhaustive search |
| (parent) | unknown | — |
| (EPC) | unknown | — |
| (offtaker) | unknown | no PPA announcement found |

- Financing: unknown — no announcement, no closing PR, no SEC filings found

## 4. Land & county records

- Tenure: **unknown** — Freestone County CAD in server maintenance throughout; no owner-name search possible
- Abatements/agreements: none found — Ch.313 expired 2022 (post-2022 project); JETI portal JS-driven, inaccessible; county commissioners court website DNS errors; Bing searches returned no results
- CAD: 0 parcels — site in maintenance

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "Tap 345kV 3381 Big Brown Switch - 3391 Jewett" ([parquet](sources/2026-07-19_ercot_parquet_utley-solar-history.json)) — IA signed 2025-12-18
- IA PDF: **not retrieved** — PUCT Interchange returned HTTP 402 on all URL patterns; no schedule exhibit, no POI confirmation, no financial security amount

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (not retrieved) | 2025-12-18 | **No** — financialSecurityAndNoticeToProceedProvided = "No" in all 52 queue snapshots |

| Milestone | Queue data (parquet) |
|---|---|
| IA signed | 2025-12-18 |
| FIS approved | — (never; 4+ years unresolved) |
| Financial security | — (never posted) |
| Scheduled COD (queue) | 2028-05-11 |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2024-04-15 → 2025-02-14 → 2025-04-15 → 2027-09-30 → 2028-05-11 (49-month total drift)

## 6. Satellite timeline

| Date | Location | Observation | Frame |
|---|---|---|---|
| 2026-07-01 | 31.822, -96.058 (Big Brown plant) | Decommissioned lignite plant; no solar activity | [png](imagery/s2_2026-07-01_center.png) |
| 2026-07-01 | 31.84–31.87, -96.28–96.31 (orig. candidate) | Rural wooded/agricultural; no solar activity | [png](imagery/s2_lat31.84_lon-96.28.png) |
| 2026-07-01 | 31.670, -96.110 (S of Big Brown) | Rural wooded land; no solar activity | [png](imagery/grid/s2_31.670_-96.110.png) |

- Verdict: **no_activity** — no grading, racking, or panel signatures in any chip. Caveat: CDSE auth failed for revised candidate area (31.813, -96.148 corridor); absence of activity is not conclusive for the correct site.

## 7. COD assessment

- Reported 2028-05-11 is 29 months after IA signing (Dec 2025) — tight but arithmetically possible
- FIS unapproved after 4+ years is anomalous; normally FIS precedes IA. Suggests either waived path or processing anomaly — IA without FIS creates sequence risk
- Financial security never posted in 52 snapshots: developer has not committed capital; NTP not issued. No construction can legally begin without NTP
- 4 prior COD slips totaling 49 months; the project has been in the queue since 2021 with no construction milestone ever achieved
- Developer (Palmera Solar) has no public profile: no press releases, no project pages, no filings found in exhaustive search — cannot assess developer capability or financial standing
- For 2028-05 COD: construction would need to begin by ~Q1 2027 at latest (~18-month build). No site preparation observed; financial security not posted; this is feasible only if land secured, permits active, and construction mobilizes in H2 2026
- **Independent estimate: 2029-Q2, drift risk high** — the structural gaps (no FIS, no financial security, anonymous developer, 49-month drift history) make on-time delivery to the reported 2028 COD unlikely; another 12-month slip is the base case

## 8. Could not determine

- Developer parent company (Palmera Solar has zero public web presence)
- IA schedule exhibit and financial security amount (PUCT Interchange HTTP 402)
- Exact site coordinates and parcel (Freestone CAD in maintenance; no delivery pin)
- Whether FIS unapproved status is a processing anomaly or a real technical impediment
- PPA counterparty, EPC contractor, or project financing status
- Imagery of the correct site area (~31.813, -96.148 corridor) — CDSE auth failed after initial cached chip
