# Dossier — Palo Verde Wind (27INR0132)

Researched 2026-07-19 · site ~28.099, -97.437 · verdict **real_early**

## 1. Verdict

- **real_early** — signed LGIA (ERCOT SGIA) between AEP Texas and RWE Clean Energy Development, LLC dated 2025-12-19 with $32M financial security; 67 Vestas V136 turbines specified ([IA](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf))
- Construction: **no_activity** — 14 Sentinel-2 chips across ~200 km² search grid (Jul 2026) show undisturbed ranchland ([search grid](imagery/search/contact_sheet2.png))
- Site: ~28.099, -97.437 — IA Exhibit C: "approximately 6 miles NE of Sinton, TX"; medium confidence ([map](https://www.google.com/maps/@28.099,-97.437,25000m/data=!3m1!1e3))
- COD: reported 2027-09-02 → independent **2028-Q4 to 2029-Q3**, drift risk **high** (no construction, FIS pending, contractual max 2029-Q3)

## 2. Site identification

- Derivation: IA Exhibit C states "San Patricio County approximately six (6) miles northeast of Sinton, Texas" → ~28.099°N, -97.437°W computed NE bearing from Sinton (28.038°N, -97.507°W) ([IA Exhibit C](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf))
- **Stated project area: not determinable** — no abatement, no CAD parcels retrieved; typical 297 MW wind lease = 15,000–25,000 acres; imagery footprint unverifiable pre-construction
- Cross-checks: Lon C Hill 345kV substation (OSM-verified, 27.844°N, -97.616°W) = one endpoint of POI transmission line; Steel Dynamics Sinton 345kV node (OSM, 28.057°N, -97.446°W) likely near new Canopy tap; both consistent with ~6 mi NE of Sinton bearing
- Not obtainable: exact turbine pad coordinates (FAA OE portal down — government shutdown); exact Canopy 345kV Station location (new build, not in OSM or public GIS)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Palo Verde Wind, LLC (unverified) | likely SPV | identity packet; not confirmed in IA |
| RWE Clean Energy Development, LLC | developer / IA party | [IA](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf); address 1401 E 6th St Suite 400, Austin TX 78702 |
| RWE AG | ultimate parent (implied) | public knowledge; not independently verified here |
| AEP Texas Inc. | TSP / transmission provider | [IA](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf) |

- Financing: not closed — no press releases or financing announcements found; consistent with early stage

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found for San Patricio County (portal not accessible); no abatement/easement filings retrieved
- Abatements/agreements: none found; post-2022 JETI era; no county commissioner minutes surfaced; normal for 2027-COD wind project in early development
- CAD: 0 hits — San Patricio County CAD portal not accessible in this research session

## 5. Interconnection & contractual schedule

- POI per signed IA: "Canopy 345kV Station (new AEP tap); dead-end structure outside fence, on Grissom–Lon C Hill 345kV line; approximately 6 miles NE of Sinton, TX" ([IA Exhibit C & C-1](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf))
- Equipment (Exhibit C): **67 Vestas V136 turbines at 4.44 MW each**, nominal 297.5 MW at 34.5kV bus, 296.7 MW at POI; delivery voltage 345kV

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-01-15_puct35077_palo-verde-wind-IA.pdf)) | 2025-12-19 | $32,000,000 total: $20M initial (within 10 biz days of TSP execution) + $12M (within 1 year of execution date) |

| Milestone | Original IA |
|---|---|
| In-Service Date | 36 months from first security installment |
| Trial Operation | 37 months from first security installment |
| Scheduled COD | **43 months from first security installment** |

- First security estimate: ~2026-01 (IA executed 2025-12-19; 10-business-day clock)
- Contractual COD maximum: ~2029-Q3 (43 months from Jan 2026)
- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2027-09-02 held across all 27 snapshots (2024-04 → 2026-06)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Undisturbed agricultural/ranch land across full search grid; no pads, no roads, no grading | [search grid](imagery/search/contact_sheet2.png) |

- Verdict: **no_activity** — 14 chips covering ~200 km² show zero construction signal; consistent with IA signed 7 months prior and no reported construction start milestone

## 7. COD assessment

- Reported COD 2027-09-02 is **not contractually grounded** — the signed IA pegs COD at 43 months from first security posting (est. ~2029-Q3); the reported date is 24 months earlier than that maximum
- No physical construction activity as of Jul 2026; to meet Sep 2027, turbine mobilization would need to begin by approximately Q3 2026 for a 297 MW / 67-turbine project — no evidence of imminent start
- FIS not approved as of Jun 2026 snapshot (atypical given IA signed; grid deliverability remains an open risk)
- RWE is an active ERCOT developer with strong track record (Papalote Creek Wind Farm nearby); financial capacity to accelerate not in doubt; but schedule evidence does not support 2027 target
- **Independent estimate: 2028-Q4 (optimistic, RWE executes fast post-mobilization) to 2029-Q3 (contractual max), base case 2029-Q2**
- Drift risk HIGH: no construction, FIS pending, reported COD 2 years inside contractual maximum

## 8. Could not determine

- Exact turbine-pad coordinates (FAA OE/AAA portal down — government shutdown in effect)
- San Patricio County CAD parcel records (portal not accessible)
- Project area in acres (no abatement or IA exhibit with acreage)
- LLC SPV name behind RWE (IA counterparty is RWE Clean Energy Development LLC directly; Palo Verde Wind, LLC not confirmed)
- Financing status / PPA offtaker (no public announcements found)
- Canopy 345kV Station exact coordinates (new AEP build, not in OSM or HIFLD)
- TX SOS / Comptroller entity record (JS-only portal, could not scrape)
