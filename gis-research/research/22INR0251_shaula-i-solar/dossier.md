# Dossier — Shaula I Solar (22INR0251)

Researched 2026-07-21 · site 29.084248, -97.105140 (low confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — credible SPV/developer chain (BP Solar Holding / Lightsource bp) with a signed+amended IA and Ch.313 abatement, but FIS never approved, construction never reported, not in EIA-860M ([timeline.md](timeline.md))
- Construction: **no_activity**, no first activity date — no ground-disturbance signature at the best-available site coordinate ([xwide frame](imagery/key/s2_2026-07-19_xwide.png))
- Site: 29.084248, -97.105140 — TCEQ stormwater-NOI physical address geocode, **low confidence** (no independent parcel/shape-match obtained) ([map](https://www.google.com/maps/@29.084248,-97.105140,5000m/data=!3m1!1e3))
- COD: reported 2026-03-31 (already passed) → independent **~2028 or later**, drift risk **high** (FIS never approved, no construction)

## 2. Site identification

- Derivation: TCEQ construction-stormwater NOI "SHAULA ENERGY PROJECT" (owner = Shaula Energy Project, LLC, exact IA-party match) lists physical address **880 Wolf Hollow Rd, Cuero, TX 77954**, geocoded via `gmaps.py places` (street_address type) ([TCEQ Socrata record](https://data.texas.gov/resource/tzyg-j7q4.json), queried directly)
- **Stated project area: 2,767.11 acres** per Ch.313 Agreement Exhibit A legal description (17 parcels) ([artifact](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-agmt_p78.png)) — imagery footprint consistent? **unverified**: no shape-match found to the Ch.313 Improvements Map's distinctive Z-shaped boundary ([map](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-app_p25.png)) at the geocoded address or in a surrounding 3×3 grid ([contact sheet](imagery/grid_contact_sheet.png))
- Cross-checks: OSM Nominatim confirms the address sits at the correct end of the named road (Wolf Hollow Rd extent lat 29.019–29.094) and in the right general quadrant of the county (east of Cuero, near Yoakum) per the Ch.313 vicinity map ([map](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-agmt_p79.png)) — a quadrant-level agreement only, not a shape-match
- Not obtainable: DeWitt CAD parcel geometry for the 17 Exhibit-A cad_ids (no free REST/GIS endpoint found — dewittcad.org is a JS SPA, TaxNetUSA/Regrid require paid or interactive access); no Google Places construction pin exists for "Shaula Solar" / "Shaula Energy Project" / any parcel-owner name

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Shaula Energy Project, LLC | SPV | party on signed IA ([IA](sources/CONFIRMED_2026-07-21_puct_35077-1387_shaula-i-solar-IA.pdf)) |
| BP Solar Holding, LLC | owner | "wholly owned by BP Solar Holding, LLC" ([Ch313 app Tab 4, p17](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-app_p17.png)) |
| Lightsource bp | developer | "developed by Lightsource BP under a development services agreement", 5.4 GW portfolio (same Ch313 app p17); BP owns 50% of the JV per [conservativetexansforenergyinnovation.org](https://conservativetexansforenergyinnovation.org) |
| BP Alternative Energy North America Inc. | permit owner | named owner/customer on TCEQ NOI TXR1529MC ("SHAULA I AND II POI AND ACCESS ROAD PROJECT") |
| E-Z BEL CONSTRUCTION, LLC | civil contractor | contractor on TCEQ NOI TXR1565NR (switchyard NOI) |

- Financing: not found (no press release / financing PR located in this run) — logged as negative evidence, not confirmed absent

## 4. Land & county records

- Tenure: **unknown** — 17 parcels across 5 owner families (Barnes, Berkman, CS Holdings, JMM Ranches, McMahan) in Ch.313 Exhibit A ([artifact](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-agmt_p78.png)); lease vs. purchase not stated (standard for Ch.313 filings)
- Ch.313 agreement: Cuero ISD No. 1714, "Shaula Energy Project, LLC" — purged from the live Comptroller site (`agreement-docs-details.php?id=1714` returns "no record found"), recovered via Wayback CDX (4 archived PDFs, 2024-06-20 snapshot) ([app](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-app.pdf), [agmt](sources/2026-07-21_wayback_ch313-1714-cuero-shaula-agmt.pdf)); value-limitation cap $20M taxable value/10yr per news reporting
- CAD: 17 parcels identified by cad_id/owner from the Ch.313 Exhibit A legal description (not an independent CAD search — no working DeWitt CAD portal found this run)

## 5. Interconnection & contractual schedule

- POI per signed IA: "approximately 63 miles east of the CPS Energy-owned Elm Creek 345 kV Switchyard on the 345 kV Elm Creek to STP transmission circuit 2" ([IA Exhibit C, p32](sources/CONFIRMED_2026-07-21_puct_35077-1387_shaula-i-solar-IA.pdf)) — matches queue POI text exactly. TSP = **CPS Energy** (not the usual Oncor/ETT/CenterPoint)
- Equipment (Exhibit C): 63 × 3.257 MVA PV inverter arrays, 205.2 MW AC

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/CONFIRMED_2026-07-21_puct_35077-1387_shaula-i-solar-IA.pdf)) | 2022-02-18 | $17,735,000 total ($9,174,000 eff. 2022-02-18 + $8,561,000 eff. 2022-09-02) |
| Amendment 1 ([pdf](sources/CONFIRMED_2026-07-21_puct_35077-1554_shaula-i-solar-IA-amend1.pdf)) | 2023-02-13 | $17,735,000 total, unchanged — both tranches re-dated eff. 2022-02-11 (schedule-only amendment) |

| Milestone | Original IA 2022 | Amendment 1 2023 |
|---|---|---|
| In-Service | 2024-02-23 | 2024-11-21 |
| Trial Operation | 2024-03-07 | 2024-11-30 |
| Scheduled COD | 2024-06-28 | **2025-10-30** |

- No second amendment exists in PUCT docket 35077 (`puct.py search "Shaula"` — exactly 4 filings total, 2 ours + 2 sibling project's) — 2025-10-30 is the last contractually documented COD, and it has already passed
- Queue-history COD drift ([timeline.md](timeline.md)): **6 changes**, 2022-01-31 → 2026-03-31 (current, also already passed); in reports since 2019-11-01 (80 monthly snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-19 | ordinary mixed scrub/farmland at TCEQ NOI address; one striped row-crop/orchard field (not racking); no graded polygon, no Z-shaped clearing matching Ch313 boundary map, no substation-scale bright squares | [xwide](imagery/key/s2_2026-07-19_xwide.png) |
| 2026-07-19 | 3×3 grid (2.5 km chips) around the same address — no tile shows the Ch313 boundary shape or a construction signature | [contact sheet](imagery/grid_contact_sheet.png) |

- Verdict: **no_activity** at the TCEQ NOI coordinate as of 2026-07-19; site-coordinate confidence is low (see §2/§8), so a shifted true site a few km away is not fully ruled out

## 7. COD assessment

- Contractual grounding: last signed schedule (Amendment 1, 2023-02) set COD 2025-10-30 — already past with no third amendment on file
- FIS never approved in 4.5+ years since IA signing ([timeline.md](timeline.md)); `meetsAllSection69` never achieved; constructionStart/End never reported in 80 monthly snapshots
- Not in EIA-860M (TX slice) — consistent with pre-construction status
- All 3 TCEQ stormwater NOIs (incl. one filed directly under the SPV's own name, started 2024-12-06) are now CANCELLED with no imagery evidence of either completed or started construction — cancellation-without-groundbreak is the more consistent reading given §6
- For: developer/parent (Lightsource bp / BP Solar Holding) is a large, credible operator (5.4 GW+ portfolio) — financial capacity is not the constraint; this reads as a schedule/interconnection stall, not a shell
- **Independent estimate: ~2028 or later (low confidence), drift risk high** — no construction start, no FIS approval, and a queue-claimed COD (2026-03-31) already 4 months past with zero visible groundwork

## 8. Could not determine

- Precise site coordinate / shape-match to the Ch.313 boundary map (no free DeWitt CAD parcel-geometry source found; TCEQ address may be a site-office/access-road point rather than the array centroid)
- Whether the 3 cancelled TCEQ NOIs reflect completed-and-stabilized work or abandonment before groundbreak — the record alone does not distinguish, and imagery favors abandonment
- Financing status / any developer press release for Shaula I specifically
- Land tenure (lease vs. purchase) for the 17 Exhibit-A parcels
- Reason for the sequencing anomaly (IA signed before FIS approval) and whether the developer's identical pattern on sibling project Shaula II (22INR0267) reflects a portfolio-wide pause
