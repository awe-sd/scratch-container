# Dossier — Douie Solar (26INR0098)

Researched 2026-07-19 · site unknown (POI corridor only) · verdict **unclear**

## 1. Verdict

- **unclear** — IA signed and 6.9(1) met but zero public footprint: no LLC registration, no developer identity, no web presence, no CAD parcels, no construction visible in 6 imagery chips across the full POI corridor
- Construction: **no_activity**, first activity: not seen ([corridor contact sheet](imagery/contact_sheet_deep.png))
- Site: POI corridor only — lat ~31.43–31.65, lon ~-96.17 to -96.30 (Freestone County, between Seaway Teague substation and Jewett) — method: OSM 138kV corridor anchor, **low confidence**, no parcel pin found ([corridor view](https://www.google.com/maps/@31.55,-96.24,50000m/data=!3m1!1e3))
- COD: reported 2028-04-18 → independent **2029-Q2 or later** (if real), drift risk **high** (3 prior slips; no construction start; developer unknown)

## 2. Site identification

- Derivation: POI text "Tap 138 kV 3501 Sea way Teague - 3394 Jewett" → OSM nodes for Teague Main Substation (31.6473, -96.2968) and Jewett area (~31.37, -96.14); project taps this line somewhere in Freestone County — exact parcel unknown
- **Stated project area: unknown** — CAD portal (esearch.freestonecad.org) returned SSL error; Freestone CAD unreachable; TaxNetUSA search returned 0 results for "Douie Solar"
- Cross-checks: all inaccessible — no Places pin (429), no parcel deed, no abatement map, no IA exhibit retrieved
- Not obtainable: exact tap coordinates (PUCT Interchange JS-blocked; IA PDF not retrieved); exact parcel (CAD unreachable)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Douie Solar, LLC (assumed) | SPV | Queue record (INR only); 0 TX franchise results ([API](sources/2026-07-19_txcomptroller_ft_douie-solar-0-results.json)) |
| Developer | unknown | Zero web results ([Bing](sources/2026-07-19_bing_web-search-0-results.json)); 0 EDGAR hits ([EDGAR](sources/2026-07-19_edgar_douie-solar-0-results.json)) |
| EPC | unknown | No delivery pin, no news |
| Offtaker | unknown | No PPA announcement found |

- Financing: unknown — no announcement, no closing PR, not in EDGAR

## 4. Land & county records

- Tenure: **unknown** — CAD portal (SSL error); TaxNetUSA owner search = 0 results
- Abatements/agreements: none found — Ch.313 expired 2022 (not applicable); JETI registry search = 0 Freestone County entries; no commissioners-court minutes retrieved
- CAD: 0 parcels found (portal unreachable + TaxNetUSA 0-hit)

## 5. Interconnection & contractual schedule

- POI per queue record: "Tap 138 kV 3501 Sea way Teague - 3394 Jewett" — PUCT Interchange inaccessible (JS-only portal); IA PDF not retrieved
- Equipment: unknown

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved) | 2026-03-08 (queue data only) | unknown |

| Milestone | Queue data only |
|---|---|
| IA signed | 2026-03-08 |
| Meets 6.9(1) | 2026-04-13 |
| Scheduled COD | 2028-04-18 |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2026-06-01 → 2027-04-14 → 2027-09-30 → 2028-04-18; in reports since 2023-05 (38 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-15 | Teague area (31.628, -96.281) — undisturbed farmland | [png](imagery/s2_2026-06-15.png) |
| 2026-07-01 | Seaway tap (31.42, -96.25) — Limestone Power Plant (coal), not solar | [png](imagery/grid_seaway_tap.png) |
| 2026-07-01 | 31.50, -96.26 — undisturbed green farmland | [png](imagery/grid_31.500_-96.260.png) |
| 2026-07-01 | 31.55, -96.27 — undisturbed green farmland | [png](imagery/grid_31.550_-96.270.png) |
| 2026-07-01 | 31.60, -96.27 — undisturbed green farmland S of Teague substation | [png](imagery/grid_31.60_-96.27.png) |
| 2026-07-01 | 31.43, -96.17 — farmland + quarry (not solar grading) | [png](imagery/grid_31.43_-96.17.png) |

- Verdict: **no_activity** — 6 chips spanning the full ~25 km Seaway-Jewett 138 kV corridor in Freestone County; no cleared rectangles, no module arrays, no earthworks resembling a 900-acre solar site

## 7. COD assessment

- Reported 2028-04-18 is purely from the queue record — no signed IA schedule confirmed
- COD has drifted 3× already: originally 2026-06 (25 months away when filed), now 2028-04 — a pattern consistent with paper-project delay accumulation
- Zero construction activity visible across the entire known site corridor as of 2026-07 (16 months before reported COD) — a 221 MW solar project would require 12+ months of earthwork + racking visible by now to meet 2028-04
- Developer unknown, financing status unknown, EPC unknown — all commitment signals absent
- If real and construction starts by late 2026, earliest realistic COD is **2029-Q2**; each additional quarter of no-start adds a quarter of slip
- **Independent estimate: 2029-Q2 if real, drift risk high — project may be paper or stalled pre-commitment**

## 8. Could not determine

- Developer / parent company identity (zero public footprint)
- IA exhibit parties, financial security amounts, milestone schedule (PUCT portal JS-blocked)
- Parcel identity / acreage (Freestone CAD unreachable)
- Land tenure (leased vs purchased)
- Financing status or offtake
- Exact POI tap coordinates (CEII / portal inaccessible)
