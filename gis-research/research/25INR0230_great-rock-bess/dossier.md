# Dossier — Great Rock BESS (25INR0230)

Researched 2026-07-19 · site ~31.10, ~-96.183 (estimated) · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2024-08-23 (queue parquet milestone); developer BMES confirmed by [La Marque city doc snippet](sources/2026-07-19_bravesearch_la-marque-bess-list.txt); part of a 3.2 GW energy hub ("BM Great Rock") at same POI tap in the ERCOT queue
- Construction: **no_activity** (construction start reported 2026-10-20); [corridor imagery Jul 2026](imagery/s2_2026-07_limestone_area.png) shows undisturbed farmland along entire 345kV line route
- Site: ~31.10, ~-96.183 — **POI inference only, low confidence** (see §2); no parcel or delivery pin found
- COD: reported 2027-12-20 → independent **2028-Q2**, drift risk **high** (7 prior COD changes, no 6.9 milestones met, FIS not approved, BMES still holding)

## 2. Site identification

- Derivation: POI geometry inference only — "Tap 345kV 46020 Limestone - 967 Gibbon Creek Ckt 18" places site along the NRG Limestone plant (31.423, -96.251) ↔ Gibbons Creek (30.620, -96.082) 345kV corridor in Leon County; interpolated latitude range 31.05–31.20 ([queue source](sources/2026-07-19_ercot-queue_great-rock-hub.txt))
- No parcel records found in Leon CAD (multiple search attempts, site errors); no Google Maps delivery pin for "Great Rock BESS" or LLC variants
- The sibling gas project (30INR0091 BM Great Rock Energy Center) names the tap "LIMEST_POI_5" — a new 345kV substation to be built; Pecan Prairie Solar (21INR0371/0428, same corridor, Yellow Wolf bus) has delivery pins at 31.049–31.135, -96.217–96.263, suggesting this zone as the likely site footprint
- Cross-check: Pecan Prairie pins ↔ POI corridor geometry agree within ~5 km; not decisively locating the BESS pad
- **Not obtainable**: exact tap substation coordinates (CEII / no PUCT IA retrieved); no parcel situs

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Great Rock BESS, LLC | SPV | queue name; likely sub of BMES |
| Black Mountain Energy Storage (BMES) | developer | [La Marque doc](sources/2026-07-19_bravesearch_la-marque-bess-list.txt) ("Black Mountain Energy Storage II"); [BMES profile](sources/2026-07-19_energy-storage-news_bmes-profile.txt) |
| Unknown buyer | future owner/IPP | BMES's track record = develop-and-sell; no sale announced as of Jul 2026 |

- Financing: no project financing announced; BMES model is pre-construction development then sale ([BMES profile](sources/2026-07-19_energy-storage-news_bmes-profile.txt))
- TX SOS entity record for "Great Rock BESS, LLC": not retrieved (Comptroller COA search redirected, paid SOS portal required)

## 4. Land & county records

- Tenure: **unknown** — Leon CAD search returned errors; no parcel records for BMES/Great Rock BESS found
- Abatements: no Ch.313/JETI agreements found for Great Rock BESS or BMES in Leon County (Comptroller search, battery projects rarely pursue Ch.313 pre-construction)
- CAD: 0 hits (multiple attempts, site returned 404/500); expected for pre-construction BESS with no land acquisition yet confirmed
- **Project area**: not determinable — no abatement, IA, or CAD doc retrieved

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 345kV 46020 Limestone - 967 Gibbon Creek Ckt 18" — new substation tap "LIMEST_POI_5" per sibling project 30INR0091
- **IA signed 2024-08-23** per queue milestone ([timeline](timeline.md)) — IA document not retrieved (PUCT interchange requires JS; item number not known)
- FIS Approved: **NOT achieved** as of latest report (2026-06-01)
- 6.9 milestones: **neither 6.9(1) nor all 6.9 achieved**

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved) | 2024-08-23 | unknown — IA PDF not accessible |

| Milestone | Queue-reported |
|---|---|
| Construction start | 2026-10-20 |
| Construction end (COD) | 2027-12-20 |

- Queue-history COD drift ([timeline.md](timeline.md)): **7 changes**, first report 2022-10-01 → COD has moved from 2025-05 → 2024-07 → 2025-12 → 2026-04 → 2027-12 → 2026-12 → 2027-12-20 (current)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | NRG Limestone plant area: undisturbed; mine active; no BESS pads | [xwide](imagery/s2_2026-07_limestone_area.png) |
| 2026-07 | Corridor chips (3 pts, tight 2km): undisturbed farmland/forest | [corridor contact sheet](imagery/contact_corridor.png) |
| 2026-07 | Normangee/Pecan Prairie area: rural farmland, no construction | [3km chip](imagery/s2_2026-07_normangee_area.png) |

- Verdict: **no_activity** — consistent with reported construction start 2026-10-20; tap substation not yet visible

## 7. COD assessment

- Reported 2027-12-20 is the contractual construction-end date from the IA (queue milestone); NOT independently verified from IA document
- **7 COD changes in 45 monthly snapshots**: earliest was 2025-05, latest 2027-12-20 — pattern of persistent optimism followed by 12-18 month slips
- Critical gate not cleared: **FIS not approved** (the Full Interconnection Study, which must precede construction). No FIS approval = no final network upgrade scope = schedule uncertainty
- 6.9 milestones not met = project has not demonstrated readiness to proceed; financial security notice not provided
- BMES's business model is develop-then-sell: no buyer means no project financing, no EPC mobilization
- BESS construction is fast (12-18 months) IF financing closes, but financing requires a buyer and cleared IA milestones
- Scenario A (BMES sells in late 2026, FIS approves, construction starts Q4 2026): COD **late 2028** is achievable
- Scenario B (FIS delayed or no buyer in 2026): further slip to **2029** or withdrawal
- **Independent estimate: 2028-Q2, drift risk high** (base case assumes ≥1 further schedule slip)

## 8. Could not determine

- Exact site coordinates: CEII-redacted in PUCT filings; no parcel, delivery pin, or media-confirmed address
- Financial security amount in IA (IA PDF not retrieved from PUCT; PUCT JS-only interface)
- IA milestones/schedule (document not obtained)
- Whether BMES has a buyer in discussion or land secured (no press release found)
- TX SOS entity details for Great Rock BESS, LLC (paid SOSDirect required)
- Exact acreage/project area (no CAD/abatement/IA obtained)
