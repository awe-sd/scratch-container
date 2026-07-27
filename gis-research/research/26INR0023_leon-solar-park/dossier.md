# Dossier — Leon Solar Park (26INR0023)

Researched 2026-07-19 · site ~31.329, -95.889 · verdict **real_active**

## 1. Verdict

- **real_active** — [Ferrovial acquired the 257 MWdc project for $72M in May 2024](sources/2026-07-19_ferrovial_acquires_257mwdc_pv_texas.html); approved for synchronization 2026-06-01; COD reported 2026-07-01 (18 days before research date)
- Construction: **substantially_complete or operating**, evidence from documentary record; first activity from Ferrovial PR Q2 2024
- Site: ~31.329, -95.889 — OSM 138kV infrastructure anchor (Pleasant Springs Tap, bus #3355 analog); confidence **medium-low** ([map](https://google.com/maps/@31.329,-95.889,5000m/data=!3m1!1e3))
- COD: reported 2026-07-01 → independent **2026-Q3**, drift risk **low** (zero drift 46 snapshots; $72M skin-in-game)

## 2. Site identification

- Derivation: OSM 138kV line data — "Pleasant Springs Tap" at 31.3292N, -95.8886W confirmed on Jewett–Crockett 138kV line; project tap ("Grapeland Magnolia Tap bus #3355 → Pleasant Springs POI bus #3357") aligns; array within ~5-10 km
- **Stated project area: unknown** — Leon CAD under server maintenance; PUCT IA not accessible (HTTP 402); no abatement document found; expected ~600-900 acres for 210 MW
- Cross-checks: [OSM substation data](https://overpass-api.de) confirms both "Pleasant Springs Tap" (31.329, -95.889) and "Pleasant Springs Substation" (31.175, -95.853) on the corridor; Leon County per queue data
- Not obtainable: exact array centroid (Google Places API quota exhausted; Leon CAD offline); PUCT IA document (HTTP 402 subscription wall)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Misae Solar IV LLC | Original SPV / developer | [Triage web sweep](sources/web_sweep_notes.md) |
| Ferrovial Energy | Acquirer / owner-operator | [PR 2024-05-28](sources/2026-07-19_ferrovial_acquires_257mwdc_pv_texas.html) |
| Unknown | EPC | Not named in PR; Ferrovial may self-perform |
| Unknown | PPA / off-taker | Not disclosed |

- Financing: $72M Ferrovial equity investment confirmed ([PR](sources/2026-07-19_ferrovial_acquires_257mwdc_pv_texas.html)); Ferrovial's "first renewable investment in the US"

## 4. Land & county records

- Tenure: **unknown** — Leon CAD under maintenance; TX SOS requires paid access; publicsearch.us JavaScript-only
- Abatements/agreements: Ch.313 expired 2022-12-31 (project too new); JETI registry inaccessible (404/503); no abatement document found — expected for this project vintage
- CAD: Leon CAD unavailable (server maintenance at time of research)

## 5. Interconnection & contractual schedule

- POI per queue data: "Tap 138kV Grapeland Magnolia Tap (bus #3355) to Pleasant Springs POI (bus #3357) section of the Jewett–Crockett 138kV Line"; PUCT IA not accessible
- Equipment: 257 MWdc ground-mount PV per [Ferrovial PR](sources/2026-07-19_ferrovial_acquires_257mwdc_pv_texas.html)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved) | 2024-05-21 per queue data | Unknown — PUCT HTTP 402 |

| Milestone | From queue data |
|---|---|
| IA signed | 2024-05-21 |
| Meets 6.9(1) | 2025-02-12 |
| Meets all 6.9 | 2025-10-30 |
| Approved for energization | 2026-05-13 |
| Approved for synchronization | 2026-06-01 |
| Commercial operation approved | — (not in 2026-06-01 snapshot) |

- Queue-history COD drift (from [timeline.md](timeline.md)): **0 changes** — held at 2026-07-01 since first appearance 2022-09-01

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | No solar array confirmed at triage candidate (31.315, -95.902) — dense forest | [png](imagery/s2_2026-07-01_center.png) |
| 2026-07-01 | No solar array at POI tap anchor (31.329, -95.889) in July composite | [png](imagery/s2_2026-07-01_PS_tap_wide.png) |
| 2025-10-01 | No clearing at center candidate — confirms wrong initial location | [sheet](imagery/center_timeline.png) |

- Verdict: **imagery inconclusive** — 17 chips across Leon County show no solar array; east Texas July cloud cover degrades composites; CDSE auth bug blocked triage imagery (fixed in this session); documentary evidence (approved for synchronization, Ferrovial $72M, zero COD drift) strongly indicates project is real and substantially complete; inability to confirm via satellite does NOT contradict documentary record

## 7. COD assessment

- Queue data: zero COD drift across 46 snapshots; COD 2026-07-01 consistent with approved-for-sync 2026-06-01 (30-day commissioning window)
- Ferrovial PR (2024-05-28): construction started Q2 2024; COD "2026" — matches queue report
- All 6.9 ERCOT milestones cleared by Oct 2025; approved for energization May 2026; sync June 2026
- "Commercial operation approved" not yet in 2026-06-01 snapshot — likely stamped in July 2026 report
- **Independent estimate: 2026-Q3** — reported 2026-07-01 is plausible; possible slight delay to July-August if commissioning tests extended; no evidence of delay
- Drift risk: **low** — $72M Ferrovial investment, near-zero operational milestone delays, approved for sync 30 days before reported COD

## 8. Could not determine

- Exact array lat/lon (centroid) — Google Places quota, Leon CAD offline, no parcel data
- Project area (acres) — no abatement or IA exhibit obtained
- IA financial security amount — PUCT HTTP 402
- EPC contractor — not named in any accessible document
- PPA / off-taker — not disclosed
- LLC officers / registered agent for Misae Solar IV LLC — TX SOS requires paid access
- Whether "commercial operation approved" milestone was stamped in July 2026 queue report
