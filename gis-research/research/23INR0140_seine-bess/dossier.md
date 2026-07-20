# Dossier — Seine BESS (23INR0140)

Researched 2026-07-19 · site 33.9443, -99.7741 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Dec 2024 (only project in 13-project BRP portfolio with a signed IA), reinvestment zone created May 2026 ([Foard County public hearing](sources/2026-05-11_foard-county_public-hearing-agenda.pdf)), Ch.312 abatement in active negotiation; no construction started
- Construction: **pre-construction_probable** — no imagery acquired; no queue construction-start milestone; abatement not yet executed as of 2026-06-22
- Site: 33.9443, -99.7741 — Edith Clarke 345kV substation (OSM) + Foard County "~4 mi SW of Crowell" ([public hearing notice](sources/2026-05-11_foard-county_public-hearing-agenda.pdf)), high confidence ([satellite view](https://www.google.com/maps/@33.9443,-99.7741,1500m/data=!3m1!1e3))
- COD: reported 2027-10-01 → independent **2028-Q4**, drift risk **high** (no construction start, abatement unsigned, 4 prior slips)

## 2. Site identification

- Derivation: OSM Overpass API returned Edith Clarke Substation at 33.9443°N, -99.7741°W (AEP, 345kV, FM Road 2003, zip 79227); Foard County reinvestment zone notice states site "approximately 4 miles southwest of the city of Crowell" — matches substation location within 0.4 km ([public hearing](sources/2026-05-11_foard-county_public-hearing-agenda.pdf))
- **Stated project area: 162.831 acres** per Foard County reinvestment zone creation notice ([public hearing](sources/2026-05-11_foard-county_public-hearing-agenda.pdf)) — imagery footprint: unverified (no satellite obtained)
- Cross-checks: POI "60500 Edith Clarke 345kV" (ERCOT queue) = OSM substation node = county "4 mi SW Crowell" — all three agree within 0.5 km
- Pease River Solar (28INR0476, same developer, Foard County) has POI "Tap 345kV 6101 RILEY7A – 60505 EDITHCLA7B" — EDITHCLA bus ID confirms same substation
- Not obtainable: exact parcel IDs (Foard CAD portal not machine-readable); PUCT IA PDF (402 blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| BRP Seine Bess, LLC | SPV | [Foard County public hearing May 11, 2026](sources/2026-05-11_foard-county_public-hearing-agenda.pdf); [PUCT docket 35077](https://interchange.puc.texas.gov/Documents/35077_1999_1446261.PDF) (confirmed via DDG, PDF 402 blocked) |
| BRP [developer] | portfolio developer | 13 BESS projects in ERCOT queue all named "BRP [name] BESS" — same SPV shell pattern; parent identity unresolved (TX SOS paid, web blocked by Bombardier noise) |
| ETT (Electric Transmission Texas) | transmission provider / IA counterparty | PUCT docket 35077 IA filing confirmed |
| EPC | unknown | — |
| Offtaker | unknown | — |

- Financing: no evidence of closed financing; abatement not yet executed as of June 22, 2026 ([Foard County minutes](sources/2026-06-22_foard-county_regular-meeting-minutes.pdf))

## 4. Land & county records

- Tenure: **unknown** (likely leased — no CAD hits; 162-acre reinvestment zone boundary consistent with BESS pad footprint on leased ag land)
- Reinvestment zone: "Foard County Reinvestment Zone-BRP Seine BESS" created via public hearing May 11, 2026; covers ~162.831 acres ~4 mi SW of Crowell ([agenda](sources/2026-05-11_foard-county_public-hearing-agenda.pdf))
- Ch.312 abatement: anticipated, negotiations ongoing — Underwood Law Firm (Bryan Guymon, Lubbock TX) representing county; "No Action Taken" on abatement as of June 22, 2026 ([June 22 minutes](sources/2026-06-22_foard-county_regular-meeting-minutes.pdf))
- CAD: 0 parcels returned under BRP/Seine — portal machine-read failures; parcel owner names under underlying landowner not identified

## 5. Interconnection & contractual schedule

- POI per queue (IA confirmed filed): "60500 Edith Clarke 345kV" ([PUCT docket 35077](https://interchange.puc.texas.gov/Documents/35077_1999_1446261.PDF))
- Equipment: unknown — IA PDF inaccessible (PUCT Interchange returns 402)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA, PUCT docket 35077 doc 35077_1999_1446261 ([PDF blocked](https://interchange.puc.texas.gov/Documents/35077_1999_1446261.PDF)) | 2024-12-01 | unknown — PDF inaccessible |

| Milestone | Status |
|---|---|
| In-Service | not in IA exhibits (PDF blocked) |
| Trial Operation | not in IA exhibits (PDF blocked) |
| Scheduled COD | reported 2027-10-01 (queue); IA exhibit not confirmed |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2023-10 → 2024-12 → 2027-12 → 2027-10; originally filed 2020-11 (68 snapshots)
- FIS approved: **not achieved** despite FIS requested 2020-11 (6-year gap — anomalous; may be waived under ERCOT process or outstanding)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-19 | no imagery acquired — CDSE 401 (example credentials), gmaps 403/429 | — |

- Verdict: **no_imagery** — site confirmed at Edith Clarke substation (33.9443, -99.7741) but satellite verification not possible with available credentials; no construction activity confirmed or denied

## 7. COD assessment

- Reported 2027-10-01 requires construction mobilization by approximately Q3 2026 and completion by Q3 2027 — consistent with a 12-month BESS build only if ground-break is imminent
- Ch.312 abatement not yet executed as of June 22, 2026 — developers typically do not mobilize before local tax agreement is signed; Underwood Law Firm still negotiating
- No construction start milestone in 68 monthly queue snapshots; no EPC or financing announcement found
- 4 prior COD slips totaling ~4 years since original 2023-10 date; pattern shows developer has consistently over-promised schedule
- Seine BESS is the most-advanced project in a 13-project BRP portfolio (only one with IA) — developer has real institutional capacity and site commitment, but execution pace is slow
- FIS approved absent: unusual — if FIS is still pending rather than waived, it must be resolved before energization regardless of IA status
- **Independent estimate: 2028-Q4** — assumes construction mobilization after abatement execution (~Q3-Q4 2026) + 18-month BESS build; risk heavily skewed right

## 8. Could not determine

- BRP parent company identity (TX SOS paid-only, PUCT 402, web searches blocked by Bombardier noise)
- IA milestone schedule exhibit (PUCT Interchange 402 on all document fetches)
- Financial security amount posted with ETT under IA
- FIS approved status — waived vs. outstanding unknown
- CAD parcel owner names and land tenure confirmation
- Satellite construction status (CDSE credentials absent; gmaps API not enabled)
- Ch.312 abatement final execution date and terms
