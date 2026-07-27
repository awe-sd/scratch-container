# Dossier — Wander Waters BESS (27INR0207)

Researched 2026-07-19 · site 34.2929, -99.3679 · verdict **real_early**

## 1. Verdict

- **real_early** — FIS approved 2025-11-14 at a real 345kV substation (Jim Treece, Wilbarger County); IA not signed; no developer identified; no construction activity ([July 2026 chip](imagery/key/s2_2026-07-01_tight.png))
- Construction: **no_activity** — undisturbed farmland at POI substation site as of 2026-07
- Site: 34.2929, -99.3679 — Jim Treece 345kV substation (AEP Texas), derived from EIA-860 + Google Places cross-check on co-tenant Blue Summit Wind Farm, medium confidence ([satellite view](https://www.google.com/maps/@34.2929,-99.3679,5000m/data=!3m1!1e3))
- COD: reported 2027-10-31 → independent **2028-Q4**, drift risk **high** (IA unsigned, developer unknown, no groundbreak)

## 2. Site identification

- Derivation: ERCOT GIS parquet query identified all projects at "JIMTREEC7A 345kV" → Blue Summit Wind (18INR0072, 25INR0492) also at "Jim Treece 345kV." EIA-860 2024 gives Blue Summit Wind LLC at 34.292913, -99.367734; Google Places "Blue Summit Wind Farm" pin = 34.292859, -99.367948 (17301 County Rd 97 N, Vernon TX 76384). ([EIA artifact](sources/2026-07-19_eia860-2024_wilbarger-county-plants.json))
- **Stated project area: not determinable** — no IA, abatement, or CAD parcel obtained; 303.5 MW BESS would require ~20-50 acres adjacent to substation
- Cross-checks: EIA-860 lat/lon ↔ Google Places pin agree within 50m; both in Wilbarger County consistent with ERCOT queue county field; no parcel situs obtained
- Not obtainable: exact JIMTREEC7A switch coordinates (CEII), land tenure, IA exhibit maps

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Wander Waters BESS, LLC | SPV (presumed) | ERCOT queue name; no other source found |
| Unknown | developer/owner | Zero web footprint; no TX SOS, no press releases |
| Unknown | EPC | Not identified |
| Unknown | PPA/offtaker | Not identified |

- Financing: unknown — no evidence of project financing, PPA, or corporate backing found

## 4. Land & county records

- Tenure: **unknown** — Wilbarger CAD owner-name search for "Wander Waters" returned 0 results ([negative search](sources/2026-07-19_puct_search-result-negative.txt)); BESS expected to have leased land adjacent to substation; no lease identified
- Abatements/agreements: No Ch313 (expired Dec 2022, not applicable to 2024 project); JETI Act search returned no hits for Wilbarger County battery storage; no commissioners court minutes accessed (county website unreachable)
- CAD: 0 parcels under any variant of Wander Waters in Wilbarger County — expected for pre-IA project that hasn't yet executed site lease

## 5. Interconnection & contractual schedule

- POI per queue data: "61001 JIMTREEC7A 345kV" = Jim Treece substation, AEP Texas (utility node prefix 61001), Wilbarger County
- PUCT Interchange search: portal requires JavaScript; all search attempts returned HTTP 402 or 404. **IA not confirmed absent — portal blocked.** ([negative note](sources/2026-07-19_puct_search-result-negative.txt))

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA obtained | — | — |

| Milestone | Queue record |
|---|---|
| FIS approved | 2025-11-14 |
| IA signed | Not achieved (as of 2026-06-01) |
| Scheduled COD | 2027-10-31 (reported) |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2027-10-31 stable across all 28 snapshots (2024-03 → 2026-06). Stability reflects the filed claim never being updated, not evidence of schedule confidence.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Undisturbed agricultural farmland at Jim Treece substation site; existing Blue Summit compound visible; no graded pad | [tight](imagery/key/s2_2026-07-01_tight.png) · [wide](imagery/key/s2_2026-07-01_xwide.png) |

- Verdict: **no_activity** — no construction groundbreak visible at POI substation as of 2026-07. Consistent with pre-IA milestone stage. A 303.5 MW BESS pad (20-50 acres of gravel + container rows) would be clearly visible at 10m resolution.

## 7. COD assessment

- Reported 2027-10-31 is an **unsupported claim**: no signed IA, no developer identified, no construction initiated
- Minimum viable path: IA signed Q3-Q4 2026 → groundbreak Q1-Q2 2027 → COD mid-to-late 2028 (assuming no permitting delays, fast equipment delivery, fast grid study closeout)
- FIS was approved 2025-11-14, but AEP Texas IA execution can take 6-18 months post-FIS under complex study conditions; as of June 2026 it has been 7+ months without IA signing
- Risk factors: unknown developer (no financial strength visible), BESS supply chain lead times (18-24 months for large orders), no evidence of site control or permits
- No positive evidence of capital formation, land secured, EPC contracted, or equipment ordered
- **Independent estimate: 2028-Q4, drift risk high** — reported COD requires IA signing within weeks and immediate site mobilization; both appear unlikely given evidence profile

## 8. Could not determine

- Developer/parent company behind Wander Waters BESS, LLC (zero public footprint)
- Land tenure (CAD search negative; no IA or lease identified)
- Signed IA or financial security amount (PUCT portal JS-blocked)
- JETI Act abatement status (no hits in public registries)
- Exact site boundary or acreage (no engineering drawings or IA exhibits available)
- Whether Wilbarger County commissioners court has approved any agreements (minutes inaccessible)
