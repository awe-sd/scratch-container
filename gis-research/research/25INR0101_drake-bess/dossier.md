# Dossier — Drake BESS (25INR0101)

Researched 2026-07-19 · site ~33.0151, -96.5388 (low confidence — city centroid) · verdict **real_active**

## 1. Verdict

- **real_active** — Project confirmed under construction Dec 2025 per [Peregrine press release](sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html); $317M financing closed Nov 2025 ([financing PR](sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html))
- Construction: **active**, underway by 2025-Q3 (confirmed Dec 2025 in press release)
- Site: ~33.015, -96.539 — city centroid only, low confidence; exact Wylie Switch 138kV substation coords not resolved ([map area](https://www.google.com/maps/@33.015,-96.539,5000m/data=!3m1!1e3))
- COD: reported 2027-01-29 → independent **2026-Q4**, drift risk **high** (FERC filing states June 2026 operations; ERCOT queue lags)

## 2. Site identification

- Derivation: Wylie TX city centroid (Nominatim fallback); GP&L transmission territory + Collin County + "30 miles NE of Dallas" consistent with Wylie area
- **Stated project area: unknown** — Collin CAD Cloudflare-blocked; no IA exhibit with acreage retrieved; expected 20-60 acres for 250 MW / 500 MWh BESS
- Cross-checks: [FERC EWG filing](sources/2026-07-19_puct_54974_ia.pdf) confirms Collin County TX; PR confirms "30 miles NE of Dallas" (≈ Wylie, ~26 mi)
- Not obtainable: Wylie Switch 138kV precise coordinates (OSM no hit; GP&L website JS-blocked; gmaps 429); Collin CAD owner search (Cloudflare-blocked); exact site address

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Drake BESS LLC | queue registrant SPV | ERCOT GIS queue |
| Mallard Energy Storage LLC (DE) | project company / EWG | [FERC EWG filing](sources/2026-07-19_puct_54974_ia.pdf) |
| Peregrine Energy Solutions LLC | developer / owner (Boulder CO) | [Dec PR](sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html) |
| AB CarVal (~$20B AUM) | equity investor since Apr 2022 founding | [financing PR](sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html) |
| Bildmore Clean Energy | preferred equity | [financing PR](sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html) |
| First Citizens Bank + Societe Generale | coord lead arrangers ($317M) | [financing PR](sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html) |
| WHC Energy Services LLC (Surerus Murphy) | EPC contractor | [Dec PR](sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html) |
| Wärtsilä | technology (Quantum2 BESS) | [Dec PR](sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html) |
| Fortune 500 (unnamed) | tolling agreement offtake | [Dec PR](sources/2026-07-19_peregrine_mallard-wartsila-pr-dec2025.html) |

- Financing: $317M project financing closed **Nov 2025** — preferred equity + senior debt, full project package ([financing PR](sources/2026-07-19_peregrine_mallard-317m-financing-nov2025.html))

## 4. Land & county records

- Tenure: **unknown** — Collin CAD blocked (Cloudflare); no abatement filings found (expected: post-Ch.313 expiry, JETI not awarded)
- CAD: 0 results retrievable (esearch.collincad.org Cloudflare-blocked; owner search for Mallard Energy Storage / Peregrine Energy not completed)
- No Ch.313/JETI/abatement found — consistent with 2022 queue entry (post-313 expiry, JETI not yet common for BESS in Collin County)

## 5. Interconnection & contractual schedule

- POI per queue: "#833 Wylie Switch 138kV", Collin County ([timeline](timeline.md))
- Transmission provider: City of Garland TX d/b/a Garland Power & Light (GP&L) per [FERC EWG filing](sources/2026-07-19_puct_54974_ia.pdf)
- Project builds its own gen-tie substation: "newly constructed substation owned by the Facility" connecting to GP&L Wylie Switch at GP&L's first terminating structure outside the fence
- FERC EWG states expected operations: **June 2026**

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard Generator Interconnection Agreement (Mallard / GP&L) | 2025-05-06 | unknown — IA PDF not retrieved |

| Milestone | FERC EWG (Dec 2025) |
|---|---|
| Commencement of operations | June 2026 |
| ERCOT reported COD | 2027-01-29 |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes**, 2025-02-17 → 2027-01-29; all pre-financing slips

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Dense suburban Wylie; no BESS gravel pad visible from city centroid | [wide chip](imagery/s2_2026-07-01.png) |
| 2026-07-01 | 1km chip at city center: urban — no industrial pad | [center chip](imagery/s2_2026-07-01_wylie_center.png) |

- Verdict: **no_confirmed_visual** — site coordinates remain city centroid; project confirmed under construction by documentary evidence (Dec 2025 PR) but gravel pad / container rows not visible from centroid coordinates. CDSE transient connection failure prevented tight chips around substation area.

## 7. COD assessment

- FERC EWG self-cert (Dec 2025) states "expected to commence operations in June 2026" — 7 months earlier than ERCOT queue's 2027-01-29 COD
- Financing closed Nov 2025 with full senior debt + preferred equity; EPC (WHC) mobilized; Wärtsilä Quantum2 ordered — all major risk milestones cleared
- Wärtsilä Quantum2 is containerized BESS; 250 MW / 500 MWh typically 12-18 months from mobilization; construction commenced ~mid-2025
- 5× COD drift history was entirely pre-IA and pre-financing; post-financing COD convergence is normal pattern
- ERCOT queue COD (2027-01-29) likely has not been updated to reflect actual schedule; municipal utility (GP&L) interconnections can lag ERCOT reporting
- **Independent estimate: 2026-Q4, drift risk high** — most likely commercial operation is 2026-Q3/Q4 based on FERC filing and construction start; ERCOT queue COD will likely be revised forward by ~1 year

## 8. Could not determine

- Exact site address / parcel (Collin CAD Cloudflare-blocked, gmaps 429)
- Precise Wylie Switch 138kV substation coordinates (OSM no hit, GP&L JS-blocked)
- Satellite construction verification (CDSE connection failure at tight chip stage; city centroid too imprecise)
- IA milestone schedule exhibit (EWG filing retrieved, not the IA itself; IA PDF not downloadable via PUCT)
- Financial security amounts in IA
- Fortune 500 offtaker identity
