# Dossier — Pecan Prairie South (21INR0371)

Researched 2026-07-20 · site 31.05001, -96.221 (medium confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — confirmed SPV (CG Leon County LLC) just added as co-Generator to a signed IA on 2026-04-09, and $27.9M combined security is already fully posted as of 2025-03-28 ([7th Amendment](sources/2026-07-20_puct_35077-2483_filing.pdf)) — real contractual/financial commitment, but pre-construction (no imagery this session)
- Construction: **unknown** — CDSE imagery unavailable this session (fleet-wide CDSE account HTTP 402 "insufficient credits", confirmed via manual token+curl replication); no satellite ground truth obtained
- Site: 31.05001, -96.221 — EIA-860M plant coords (stable 2022-2026) cross-checked by PUCT PGC registration physical address "9396 FM 3, South Normangee, TX 77871" ([PGC reg](sources/2026-07-20_puct_59753-1_filing.pdf)), medium confidence
- COD: reported 2027-05-01 → independent **2027-Q3**, drift risk **medium** (binding IA says 09/30/2027, 5 months later than queue claim)

## 2. Site identification

- Derivation: EIA-860M plant 64981 lat/lon, identical across every monthly EIA snapshot 2022-04→2026-05 ([eia_history.json](eia_history.json)); independently consistent with the physical unit address on the PUCT Power Generation Company registration ([PGC form](sources/2026-07-20_puct_59753-1_filing.pdf), Part E table: "9396 FM 3, South Normangee, TX 77871", Leon Co, 132.98 MW Solar)
- **Stated project area: not determined this session** — the only acreage figure found (69.535 ac, Property ID 613681) is one landowner's parcel *inside* a 2019 Ch.313 reinvestment zone, not the project's own footprint
- Cross-checks: EIA plant coords + PGC address agree (same South Normangee locale). A THIRD candidate — the Ch.313 application's 2019 reinvestment-zone map ([map](sources/2026-07-20_comptroller_ch313_1703-normangee-cg-app_p26.png)) — shows a different site ~15-20 km NW near Marquez/Robertson Co line; judged a stale pre-shrink footprint (map dated 2019-12-04, project was 300 MW then vs. 130-133 MW now) rather than the current site, but NOT independently disproven
- Not obtainable this session: satellite imagery (CDSE credits exhausted), Google Places delivery pin (HTTP 429 rate-limited), exact parcel of the SPV itself

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| CG Leon County LLC | SPV | [PGC registration](sources/2026-07-20_puct_59753-1_filing.pdf); party on [7th IA Amendment](sources/2026-07-20_puct_35077-2483_filing.pdf) |
| Repsol Renewables North America, Inc. | corporate parent | Named as sole parent on the same PGC registration form |
| CG Leon County II LLC | co-located sibling SPV (different INR, 21INR0428, "Pecan Prairie North") | Same [7th IA Amendment](sources/2026-07-20_puct_35077-2483_filing.pdf); jointly/severally liable for shared security |
| ConnectGen (predecessor) | original developer, pre-Repsol acquisition | Carried from triage (KBTX article) — not independently re-verified this session |

- Financing: not independently verified this session; $27.9M interconnection security (LC/cash) posted jointly by South+North as of 2025-03-28 ([Exhibit E](sources/2026-07-20_puct_35077-2483_filing.pdf)) is a strong reality signal but is TSP-facing collateral, not project financing

## 4. Land & county records

- Tenure: **unknown** — not determined this session
- Abatements/agreements: Ch.313 Agreement #1703, applicant "CG Leon County, LLC", Normangee ISD, applied 2020-02-17 ([app PDF](sources/2026-07-20_comptroller_ch313_1703-normangee-cg-app.pdf), [agreement](sources/2026-07-20_comptroller_ch313_1703-normangee-cg-agmt.pdf)). Sibling Ch.313 #1702 "CG Leon County II, LLC" under Leon ISD is the North project — do not conflate.
- CAD: one incidental hit (GHCJ Ranches LLC, 69.535 ac, Property ID 613681, HWY 3 Normangee) found inside the Ch.313 reinvestment zone map, not a systematic owner-name CAD search of the SPV itself (not run this session)

## 5. Interconnection & contractual schedule

- POI per IA: shared CTT station between "To Limestone" and "To Gibbons Creek" 345kV lines, feeding "To Pecan Prairie North 320MW" and "To Pecan Prairie South 130MW" ([Exhibit C3](sources/2026-07-20_puct_35077-2483_filing_p10.png) — rendered page, not yet copied to a persistent named file); consistent with queue POI text "CTT Yellow Wolf, bus # 79007" though the station name is not spelled out as "Yellow Wolf" in any IA text reviewed
- Equipment (Exhibit C, South-specific): 130 MW at Point of Interconnection (36 × 4.2 MVA = 151.2 MVA), Power Electronics Inverters PE FS4200M

| IA document | Signed | Financial security |
|---|---|---|
| Original SGIA, CTT + CG Leon County II LLC (joint North/South facilities) ([pdf](sources/2026-07-20_puct_35077-1242_filing.pdf)) | 2021-02-26 | not itemized per-project in original |
| 7th Amendment — adds CG Leon County LLC (South) as co-Generator ([pdf](sources/2026-07-20_puct_35077-2483_filing.pdf)) | 2026-04-09 (filed 2026-05-12) | $27,900,000 total, fully posted 2025-03-28, joint & several between South + North |

| Milestone | South-specific (7th Amendment Exhibit B) |
|---|---|
| In-Service Date | 04/15/2025 (marked "Achieved") |
| Trial Operation | 10/21/2026 |
| Scheduled COD | **09/30/2027** |

- Queue-history COD drift ([timeline.md](timeline.md)): 9 changes, 2021 original → 2027-05-01 current, in queue since 2019 (83 snapshots)
- EIA-860M second source ([eia_history.json](eia_history.json)): planned COD moved 2023-07 → 2025-05 → 2025-12 → 2026-03 → **2027-03** across 2022-2026 reports; status held at "(L) Regulatory approvals pending. Not under construction" for all 5 years of EIA history through 2026-05 — EIA has NOT yet recognized construction start, in tension with the IA's own "In-Service Date Achieved" marking

## 6. Satellite timeline

- **Not obtained this session.** CDSE (Copernicus Data Space Ecosystem) returned HTTP 402 "insufficient credits" on the openEO processing endpoint — confirmed via manual token retrieval + curl replication, not a credentials or network issue. This is a fleet-wide blocker, not specific to this project.

## 7. COD assessment

- Reported COD 2027-05-01 (queue) vs. 09/30/2027 (signed 7th IA Amendment, executed 2026-04-09) — the binding contractual document is 5 months LATER than the queue's self-reported claim, an active divergence as of this research date
- EIA-860M's own planned-COD series (2027-03 latest) sits between the two, and its persistent "not under construction" status for 5 straight years is a caution flag despite the IA's "In-Service Date Achieved" language for the South milestone schedule — that Achieved marking likely reflects the SHARED facility's original 2021 in-service date being satisfied by the North project, not South-specific construction completion
- 9 COD slips since 2019 entry (300 MW → 132.98 MW capacity shrink over that time) is a long history of schedule slippage, but the 2026 admission of South as a formal IA party plus $27.9M security already posted are recent, concrete, money-backed commitments — this is not a paper project
- No satellite or imagery ground truth this session to confirm/deny physical construction progress
- **Independent estimate: 2027-Q3, drift risk medium** — weighted toward the signed IA's 09/30/2027 date as the primary document, but EIA's continued "not under construction" status keeps risk from being "low"

## 8. Could not determine

- Satellite/imagery construction stage (CDSE account out of processing credits fleet-wide)
- Google Places delivery-pin cross-check (HTTP 429 rate-limited on all attempts)
- Project area/acreage specific to the current 130 MW South footprint (only an incidental landowner parcel found)
- Land tenure (leased vs. purchased)
- Exact meaning of "CTT Yellow Wolf, bus # 79007" POI name — IA exhibits describe the POI topologically (Limestone/Gibbons Creek lines) but do not spell out "Yellow Wolf" as a station name
- Whether the 2019 Ch.313 reinvestment-zone map (near Marquez/Robertson Co line) represents a stale pre-shrink footprint or an alternate real site — flagged for next pass, not resolved
- Independent SPV↔ConnectGen/Repsol corporate-chain verification (carried from triage, not re-confirmed this session beyond the PGC registration's own parent-company disclosure)
