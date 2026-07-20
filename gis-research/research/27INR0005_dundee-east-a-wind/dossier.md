# Dossier — Dundee East A Wind (27INR0005)

Researched 2026-07-19 · site 34.085°N, -99.145°W (POI) · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Feb 2025, financial security/NTP posted Sept 2025, AES Corp subsidiary confirmed; no construction visible June 2026
- Construction: **no_activity**, first activity: not observed ([grid](imagery/contact_sheet_grid.png))
- Site: 34.085°N, -99.145°W — Riley Substation #6101 POI, Wilbarger Co. adjacent to Baylor Co. ([map](https://google.com/maps/@34.085,-99.145,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 → independent **2028-Q4**, drift risk **high** (FIS unapproved post +70% upsize, no construction start)

## 2. Site identification

- Derivation: POI substation text in ERCOT GIS field `poiLocation` = "345 kV Riley Substation (#6101); AEP" → located to Wilbarger County, adjacent to Baylor ([timeline](timeline.md))
- **Stated project area: unknown** — no abatement, IA PDF, or CAD parcel data obtained
- Cross-checks: POI substation confirmed in imagery as large industrial complex at 34.085°N, -99.145°W; Baylor County seat Seymour is ~55km south (~33.59°N) suggesting turbine array could span large area south of POI
- Not obtainable: exact turbine coordinates (FAA OE/AAA portal 404); parcel/lease boundaries (Baylor CAD inaccessible); IA exhibit maps (PUCT 402/JS-only); Google Maps delivery pin (429)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Felix 2, LLC (Delaware) | SPV / interconnecting entity | [ERCOT GIS parquet](timeline.md) — `interconnectingFacility` all 43 snapshots |
| AES Corp (NYSE: AES) | Developer / parent | [10-K FY2024 Exhibit 21.1](sources/2025-04-11_AES_10K_EX211_felix_entities.txt) — Felix 2 LLC listed as AES subsidiary |
| Felix DevCo, LLC | Sibling AES entity (green H₂, not this project) | [10-K FY2025 Note 26](sources/2026-03-02_AES_10K_felix_acquisition_note.txt) — separate JV acquired from Air Products Nov 2024 |
| Unknown | EPC | Not found |
| Unknown | PPA offtaker | Not found |

- Financing: not found; no press releases or debt filings located

## 4. Land & county records

- Tenure: **unknown** — Baylor CAD inaccessible (HTTP 403); TX SOS requires paid account
- Abatements: none found — expected for 2022+ project (post-Ch.313 era, JETI not found)
- CAD: 0 hits obtainable — NEGATIVE: no parcel data

## 5. Interconnection & contractual schedule

- POI per queue: "345 kV Riley Substation (#6101); AEP" — IA PDF not retrieved (PUCT 402)
- Equipment: unknown

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PDF not retrieved) | 2025-02-21 | Sept 2025 (Yes, first seen 2025-09-01 snapshot) |

(Security amount unknown — IA PDF inaccessible)

| Milestone | Queue record |
|---|---|
| IA signed | 2025-02-21 |
| Meets 6.9(1) | 2025-04-03 |
| FIS approved | — (never) |
| Construction start | — |
| Reported COD | 2027-12-31 |

- Queue-history COD drift ([timeline.md](timeline.md)): 1 change — 2027-07-31 → 2027-12-31 (Oct 2025, coincident with +70% MW upsize)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-15 | Riley Substation area: existing industrial complex + substation grading, no turbine pads | [s2_2026-06-15.png](imagery/s2_2026-06-15.png) |
| 2026-06-15 | 9-tile Baylor County grid (33.50-33.80°N): undisturbed farmland, oil/gas well pads only | [contact_sheet_grid.png](imagery/contact_sheet_grid.png) |
| 2026-06-15 | Eastern Baylor/Archer County grid (−98.90W): undisturbed, no wind activity | [contact_sheet_east.png](imagery/contact_sheet_east.png) |

- Verdict: **no_activity** — no wind turbine pads, access road strings, or graded turbine foundations visible in June 2026 across ~14 chips covering primary Baylor County area. Grid may not cover full 524 MW extent (typically 10-20 km spread); CDSE quota exhausted before complete coverage.

## 7. COD assessment

- IA signed Feb 2025, NTP/financial security posted Sept 2025 (confirmed by parquet field `financialSecurityAndNoticeToProceedProvided = Yes`)
- No construction start reported in queue as of June 2026 (15 months post-IA signing)
- 524 MW wind project requires 18-24 months from mobilization to COD; earliest construction start ~Q3 2026 implies COD no earlier than Q1-Q3 2028
- **Critical risk**: +70% capacity upsize (307→524 MW, Oct 2025) triggered without FIS approval — almost certainly requires restudy; FIS still not approved as of June 2026 is a blocking constraint
- Sibling 27INR0011 (Dundee East B, 261 MW, same IA date/COD) has identical constraint profile; cluster must advance together or stagger
- Independent estimate: **2028-Q4** (assumes FIS resolved H1 2026, construction start Q4 2026, 18-month build)
- Drift risk **HIGH**: FIS unapproved, no construction start, major capacity change likely triggering restudy

## 8. Could not determine

- Exact turbine locations (FAA OE/AAA portal offline; no delivery pins)
- IA financial security amounts (PUCT PDF inaccessible)
- IA contractual milestone schedule (PUCT inaccessible)
- Land lease parcels / project acreage (Baylor CAD inaccessible, TX SOS requires payment)
- EPC contractor, PPA counterparty, financing details
- Whether FIS restudy has been requested or resolved post Oct 2025 upsize
- Whether any turbine orders have been placed
