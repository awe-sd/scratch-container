# Dossier — Sky Global West Houston (26INR0519)

Researched 2026-07-19 · site 29.74120, -96.15770 · verdict **real_active**

## 1. Verdict

- **real_active** — TCEQ NSR air permit #176331 EFFECTIVE at [978 FM 3013 Rd, Sealy TX](sources/2026-07-19_tceq_airperm_sky-global-nsr-results.html); industrial construction compound visible in [2026-07 imagery](imagery/s2_2026-07-01_tight.png) vs [2023 baseline](imagery/s2_2023-06-01_tight.png)
- Construction: **construction_active**, first activity ≤2023 ([2023 tight frame](imagery/s2_2023-06-01_tight.png))
- Site: 29.74120, -96.15770 — TCEQ facility address → OSM geocode, high confidence ([satellite view](https://www.google.com/maps/@29.7412,-96.1577,5000m/data=!3m1!1e3))
- COD: reported 2027-06-01 → independent **2027-Q2**, drift risk **high** (tight IC-engine build window; one prior slip)

## 2. Site identification

- Derivation: TCEQ NSR permit RN111020285 address "978 FM 3013 Rd, Sealy, Austin County TX" → OSM Nominatim geocode 29.7412, -96.1577 ([TCEQ results](sources/2026-07-19_tceq_airperm_sky-global-nsr-results.html))
- **Stated project area: not obtained** — Austin CAD JS-blocked; PUCT IA not retrieved; imagery shows compact industrial pad ~5-15 acres, consistent with IC engine plant
- Cross-checks: POI "Gebhardt–Wallis 138kV circuit 65" — Wallis TX ~9 km SW, consistent for a 138kV tap; [Sky Global Power One](sources/2026-07-19_eia_860m_may2026_sky-global-power-one.txt) at 29.5503°N, -96.5378°W (Colorado County, 40 km SW) confirms developer pattern of Austin/Colorado County corridor
- Not obtainable: exact POI substation coordinates; Austin CAD parcel IDs; PUCT IA PDF (402 payment required)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Sky Global Power Two LLC | SPV/operator | [TCEQ NSR permit CN605770015](sources/2026-07-19_tceq_airperm_sky-global-nsr-results.html) |
| Sky Global Partners LLC | developer (est. 2007) | triage web sweep; [prior project EIA record](sources/2026-07-19_eia_860m_may2026_sky-global-power-one.txt) |
| Sky Global Power One Pledgor LLC | sister entity / track-record | [EIA 860M 59938](sources/2026-07-19_eia_860m_may2026_sky-global-power-one.txt) — 6×IC, 50 MW, operating since 2016 |

- Financing: unknown — no press release or financing announcement found
- EPC: unknown — no construction contractor identified

## 4. Land & county records

- Tenure: **unknown** — Austin CAD parcel search JS-blocked; no owner-name result obtained
- Abatements: none found (post-2022 project; Ch.313 expired Dec 2022; no JETI hit)
- CAD: 0 parcels retrieved (JS-dependent portal, WebFetch non-functional)
- TCEQ facility address confirms site in Austin County, Sealy area, Rule 6005 (engines/turbines) ([source](sources/2026-07-19_tceq_airperm_sky-global-nsr-results.html))

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "tap 138kV 44700 Gebhardt - 44740 Wallis circuit 65"
- IA signed: **2025-03-25** (per [ERCOT queue timeline](timeline.md)); PDF not retrieved (PUCT Interchange 402)

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (ERCOT queue milestone only) | 2025-03-25 | unknown — PDF not retrieved |

| Milestone | Queue record |
|---|---|
| FIS approved | 2025-03-12 |
| IA signed | 2025-03-25 |
| Scheduled COD | 2027-06-01 (latest) |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2026-12-15 → 2027-06-01 (6-month slip, first reported 2024-08)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2023-06 | Small industrial pad at site, earlier configuration | [tight](imagery/s2_2023-06-01_tight.png) |
| 2026-07 | Larger industrial compound, prominent rectangular building/structure, graded pad | [tight](imagery/s2_2026-07-01_tight.png) |

- Verdict: **construction_active** — site shows significant industrial development 2023→2026; large rectangular structure (engine hall candidate) visible in 2026 not present at same scale in 2023. Timelapse (monthly 2024-2026) submitted but timed out — exact first-activity month not bracketed. 10 m Sentinel-2 cannot distinguish equipment stage (engine installation vs civil).

## 7. COD assessment

- TCEQ NSR permit obtained May 2024, IA signed March 2025 — real regulatory and contractual milestones achieved
- Construction visible by 2026-07; IC engine plant (16 engines, ~325 MW) requires substantial civil + electrical work after engine delivery
- IC engine lead time typically 12-18 months after order; no procurement announcement found — if ordered post-IA (Q2 2025), delivery ~Q3/Q4 2026, commissioning Q2 2027 is tight but possible
- One prior COD slip of 6 months (2026-12 → 2027-06); project has been in queue since mid-2024 with design changes
- For: active NSR permit, signed IA, construction active, developer track record (Power One 2016)
- Against: schedule tight, no financing announcement, no EPC named, timelapse unavailable to confirm construction pace
- **Independent estimate: 2027-Q2, drift risk high** — aligned with reported COD but material risk of Q3/Q4 slip

## 8. Could not determine

- PUCT IA PDF (milestone schedule, financial security amounts) — portal returned 402
- Austin CAD parcel IDs and acreage
- Exact engine type / manufacturer (design changed from GE LM6000 to IC engines; likely INNIO Jenbacher or Wärtsilä based on Power One precedent)
- EPC contractor identity
- Financing status / PPA offtaker
- Construction timelapse (monthly 2024-2026) — job timed out
- TX Comptroller / SOS entity details for Sky Global Power Two LLC
