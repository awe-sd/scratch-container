# Dossier — Royal River BESS (24INR0282)

Researched 2026-07-19 · site 29.22680, -95.42880 · verdict **real_early**

## 1. Verdict

- **real_early** — Clearway Energy Group SPV confirmed ([TX SOS officers](sources/2026-07-19_txcomptroller_royal-river-llc.json)); IA signed 2023-12-15 + FIS approved 2025-10-09; no construction yet visible
- Construction: **pre_construction**, first activity not observed
- Site: 29.22680, -95.42880 — CenterPoint Angleton 138kV substation (OSM Overpass API), medium confidence ([map](https://google.com/maps/@29.2268,-95.4288,5000m/data=!3m1!1e3))
- COD: reported 2027-06-30 → independent **2027-Q3**, drift risk **high** (3 prior drifts, no groundbreaking)

## 2. Site identification

- Derivation: OSM Overpass API — CenterPoint Energy Angleton 138kV substation, node 244479862; BESS expected on adjacent parcel within ~1 km of substation
- **Stated project area: not obtained** — CAD portal JS-blocked, IA exhibit not retrieved; imagery footprint unverified
- Cross-checks: POI "Tap 138kV 42110 Angleton – 43381 West Columbia" consistent with CenterPoint substation at 29.2268, -95.4288; West Columbia terminus at 29.1568, -95.6576 (OSM 336964607)
- Not obtainable: exact BESS pad lat/lon (no IA exhibit, CAD portal blocked); both triage Sentinel-2 chips used wrong proxy location (city center) and were ~70% cloud-covered

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Royal River LLC | SPV | [TX SOS — TX taxpayer 32087259811](sources/2026-07-19_txcomptroller_royal-river-llc.json) |
| Clearway Energy Group LLC | Developer/owner | [TX SOS — Craig Cornelius + Jennifer Hein shared officers](sources/2026-07-19_txcomptroller_clearway-energy-group-llc.json) |
| EPC contractor | unknown | Not found — no press release |
| Offtaker | unknown | No PPA announcement found |

- Financing: unknown — no press release; Clearway's comparable Pine Forest BESS (~85 MW, TX) closed financing Oct 2024 and came online Feb 2026

## 4. Land & county records

- Tenure: **unknown** — Brazoria CAD portal requires JavaScript; automated owner search returned 404; no parcel found
- Abatements/agreements: none found (expected — Ch.313 expired 2022; JETI not yet public)
- CAD: 0 hits (portal not machine-readable; manual search at https://esearch.brazoriacad.org/ for "Royal River" recommended)

## 5. Interconnection & contractual schedule

- POI per queue data: "Tap 138kV 42110 Angleton - 43381 West Columbia" (IA document not retrieved — PUCT Interchange portal 402-blocked)
- Equipment: not in IA (not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2023-12-15 (queue data) | not obtained |

| Milestone | Queue data |
|---|---|
| IA signed | 2023-12-15 |
| FIS approved | 2025-10-09 |
| Meets 6.9(1) | — |
| Meets all 6.9 | — |
| Construction start (reported) | — |
| In-Service | — |

- Queue-history COD drift ([timeline.md](timeline.md)): 3 changes, 2024-12-01 → 2025-11-28 → 2027-01-11 → 2027-06-30 (total slip ~30 months from original)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-15 | ~70% cloud-covered; city center proxy; no BESS pad visible | [png](imagery/angleton_center_2026-06.png) |
| 2026-07 approx | ~70% cloud-covered; city center proxy; no activity | [png](imagery/angleton_center_2026-07.png) |

- Verdict: **no_confirmed_activity** — both chips are at wrong location (29.1694, -95.4319 city center vs 29.2268, -95.4288 actual substation) and cloud-covered; correct-location imagery not obtained

## 7. COD assessment

- IA signed 2023-12-15 + FIS approved 2025-10-09 = project cleared two hard gates; developer is active (Clearway operates multiple TX projects)
- 3 prior COD drifts totaling ~30 months of slippage from original 2024-12-01 claim; current 2027-06-30 is 4th reported COD
- No construction start in ERCOT queue; no press release; no site activity confirmed — as of 2026-07-19, likely in permitting/procurement phase
- BESS build time ~12-18 months: a 2026-Q4 / 2027-Q1 groundbreaking could still make a late-2027 COD; absence of activity through mid-2026 puts 2027-Q3 as base independent estimate
- Drift risk HIGH: pattern of slippage + no public construction signal; 2027-Q4 or 2028-Q1 are realistic downside scenarios

## 8. Could not determine

- Exact BESS site parcel / lat-lon (CAD blocked; no IA exhibit; correct-location imagery not taken)
- Financial security amount posted under IA
- EPC contractor and offtaker
- Any construction start date or groundbreaking announcement
- PUCT Interchange IA document (402-blocked in all attempts across two run sessions)
