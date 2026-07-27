# Dossier — HyFuels Green Lake Solar (26INR0019)

Researched 2026-07-19 · site 28.7600, -96.8300 · verdict **real_early**

## 1. Verdict

- **real_early** — Ch.313 agreement signed 2022-11-14 with Calhoun County ISD, minimum $30M investment committed; developer BNB Renewable Energy Holdings LLC has 1,000+ MW of operating projects ([agreement](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-agmt.pdf))
- Construction: **no_activity**, first activity not yet observed; stated start Jan 2027 ([application Tab 4](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-app.pdf))
- Site: 28.7600, -96.8300 — bearing calc from Port Lavaca + map alignment, medium confidence ([vicinity map](https://www.google.com/maps/@28.76,-96.83,50000m/data=!3m1!1e3))
- COD: reported 2027-12-01 → independent **2028-Q2**, drift risk **high** (no IA, no FIS approval, 347 MW in 11 months post-groundbreak is aggressive)

## 2. Site identification

- Derivation: application states "~10 miles NW of Port Lavaca, TX"; 315° bearing gives 28.76N,-96.80W; parcel map Tab 11 shows site at Victoria/Calhoun county line ([vicinity map](imagery/ch313_map_page26.png), [parcel map](imagery/ch313_map_page27.png))
- **Stated project area: not specified** in application text; 400 MW ac / 994,280 panels implies ~2,000–3,000 acres; Tab 9 "Not applicable" (land not qualified property)
- Cross-checks: Port Lavaca centroid 28.617N,-96.633W; 10 mi NW ≈ 28.76N,-96.80W; parcel map road alignment suggests 28.76N,-96.83W; Clark Station (OSM): 28.616N,-96.711W (too far S/E for this project)
- Not obtainable: exact parcel coords (CAD portal JS-gated; no PUCT IA; Overpass 406); Dokmai 138kV substation coordinates (CEII / not in OSM)
- Imagery footprint: consistent with agricultural land, no construction (Feb 2026, 12km frame) ([frame](imagery/s2_2026-02-01_xwide.png))

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| HyFuels Green Lake Solar LLC | SPV (DE LLC, TX active since 2022-04) | [Form 772](sources/2026-07-19_comptroller_ch313_1925-hyfuels-form772-2023.pdf) p5 franchise search |
| HyFuels Holdings LLC | Manager/intermediate parent | [Agreement](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-agmt.pdf) Art X.1 — contact Orlando Puig |
| BNB Renewable Energy Holdings LLC | Ultimate developer/owner | [BNB website](sources/2026-07-19_bnbrenewables_homepage.html); [App Tab 5](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-app.pdf) p17 |
| Jonathan Nicholas | Managing Partner, BNB | [Form 772](sources/2026-07-19_comptroller_ch313_1925-hyfuels-form772-2023.pdf) p4 signatory |
| EPC | Unknown | Not identified; no press release found |
| Offtaker / PPA | Unknown | No announcement found |

- Financing: not closed; no press release; pre-IA stage — no financing expected yet
- BNB track record: Bull Creek Wind (181 MW, 2008), Long Draw Solar (225 MW, Borden Co), Lamesa Solar (102 MW), Mesquite Creek Wind (211 MW), Ivory Solar (50 MW) — all operating

## 4. Land & county records

- Tenure: **unknown** — Tab 9 "Not applicable" (land not qualified property, likely leased); existing property described as "houses, barns, Oil & Gas Wells" on parcels ([app Tab 10](sources/2026-07-19_comptroller_ch313_1925-hyfuels-green-lake-solar-app.pdf))
- Abatements: Ch.313 App 1925 (Solar), 1926 (Storage — "Green Lake LLC"), 1927 (Wind — "Green Lake Wind LLC") — all Calhoun County ISD, all signed 2022-12-20 ([app docs page](https://comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id=1925))
- Sibling 26INR0028 (HyFuels Calhoun Solar, 301.82 MW, Victoria Co) in ERCOT queue — possible campus extension
- CAD: 0 parcel hits — portal required JS session token; could not perform owner-name search (negative evidence)
- Commissioners court minutes: attempted but resolved to Calhoun Co Alabama site (negative evidence)

## 5. Interconnection & contractual schedule

- POI per queue: Dokmai 138kV Substation (bus #80090) — no IA on file (PUCT 402 error); FIS requested 2023-06-13, not yet approved as of 2026-06-01
- Equipment (if in IA exhibits): not available — no IA obtained

| IA document | Signed | Financial security posted |
|---|---|---|
| No PUCT IA found | — | — |

| Milestone | Ch.313 Agreement / Application 2022 |
|---|---|
| Qualifying Time Period start | 2026-01-01 |
| Qualifying Time Period end | 2027-12-31 |
| Construction start (stated) | 2027-01-01 |
| Commercial operation (stated) | 2027-12-31 |
| Tax Limitation Period start | 2028-01-01 |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2026-10-01 → 2027-12-01 (+14 months); in queue since 2023-06

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-12 | Undisturbed agricultural (coastal plain); no clearing | [xwide](imagery/s2_2025-12-01_xwide.png) |
| 2026-02 | Undisturbed agricultural (bare fallow fields, 12km frame); zero construction | [xwide](imagery/s2_2026-02-01_xwide.png) |
| 2026-06 | Heavy cloud cover; grid assessment inconclusive | [grid contact sheet](imagery/grid_contact_sheet.png) |

- Verdict: **no_activity** — consistent with Jan 2027 stated construction start; 10 m/px cannot confirm sub-acre site prep

## 7. COD assessment

- Reported 2027-12-01 is NOT grounded in a signed IA — it is the developer's stated schedule from Ch.313 Tab 4 (application narrative), reflected in the ERCOT queue
- FIS not yet approved 3+ years after request (2023-06-13); no IA = no transmission milestone clock; a 347 MW project needs IA + NTP before construction can begin
- Application construction schedule: Jan 2027 – Dec 2027. A 347 MW solar project realistically takes 12–18 months after groundbreak; earliest commercial operation mid-to-late 2028
- Ch.313 qualifying time period ends 2027-12-31 — strong tax incentive to maintain the schedule on paper; watch for further COD slip if FIS approval continues to lag
- Developer (BNB) has real completed projects and capital; project is not speculative paper. But early-stage pre-IA status means the COD is a placeholder, not a contractual commitment
- **Independent estimate: 2028-Q2, drift risk high** (conditional on FIS approval in 2026 and IA execution in early 2027)

## 8. Could not determine

- Exact site lat/lon (no IA, no CAD parcel geometry, no delivery pin; medium-confidence estimate only)
- Project acreage (not stated in Ch.313 application; Tab 9 "Not applicable")
- Land tenure (likely leased; not confirmed — CAD search blocked by JS requirement)
- EPC contractor identity
- PPA/offtaker
- Financing status
- Sibling project 1926 (storage) capacity and whether it has a separate ERCOT INR
- Dokmai 138kV substation coordinates
- FIS study results or expected approval date
