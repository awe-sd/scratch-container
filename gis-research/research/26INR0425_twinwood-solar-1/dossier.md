# Dossier — Twinwood Solar 1 (26INR0425)

Researched 2026-07-19 · site ~29.80, -95.94 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-11-07 and 6.9(1) achieved 2026-05-26 confirm the project passed binding ERCOT queue milestones; FIS not yet approved, no construction visible in Jan–Jun 2026 imagery
- Construction: **no_activity**, first activity: not observed ([Jan 2026 grid](imagery/s2_2026-01-15_north.png))
- Site: ~29.80, -95.94 — geographic inference from OSM "Twinwood Parkway" (Fort Bend Co.) + Waller Co. queue county, **low confidence** ([map](https://www.google.com/maps/@29.80,-95.94,5000m/data=!3m1!1e3))
- COD: reported 2027-10-27 → independent **2028-Q3**, drift risk **high** (FIS not approved, no NTP, 16 mo to reported COD)

## 2. Site identification

- Derivation: OSM "Twinwood Parkway" runs at ~29.74–29.76°N, -95.93–95.96°W in Fort Bend County — project named for this locality. Queue county = Waller → array extends north across county line. Estimated centroid ~3 km north of parkway.
- **Stated project area:** not obtained — CAD portals JS-only; IA not retrieved (PUCT 402)
- Cross-checks: none independent — pin unavailable (gmaps 429), parcel unavailable (CAD JS-only), IA unavailable (PUCT 402)
- Not obtainable: exact TWINWD substation coordinates (CEII / PUCT blocked); parcel IDs; developer identity

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Twinwood Solar 1, LLC | SPV | queue data (iaSigned party) |
| Unknown | developer/parent | no web presence found; all searches blocked |
| CenterPoint Energy | TSP | HOUSTON zone + 138kV POI = CenterPoint territory |
| Unknown | EPC / PPA | not found |

- Financing: unknown — no press release, no PPA announcement found anywhere

## 4. Land & county records

- Tenure: **unknown** — no parcel data retrieved (Waller CAD and Fort Bend CAD JS-only portals)
- Abatements: none found (Ch.313 expired 2022; JETI search returned no Waller County entries) — normal for post-2022 project
- CAD: 0 parcels retrieved under any Twinwood variant

## 5. Interconnection & contractual schedule

- POI per queue data: "Tap 138kV 44750 FULSHR_S25_8 – 44860 TWINWD_S25_8" — new CenterPoint 138kV tap; TWINWD is the project's own collector substation (bus name = project name)
- IA signed 2025-11-07 per ERCOT queue; PUCT Interchange returned HTTP 402 on all access attempts — PDF not retrieved

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (CenterPoint / Twinwood Solar 1) | 2025-11-07 | unknown (PDF not retrieved) |

| Milestone | Queue data |
|---|---|
| IA signed | 2025-11-07 |
| Meets 6.9(1) | 2026-05-26 |
| FIS approved | — (not yet) |
| Meets all 6.9 | — |
| Reported COD | 2027-10-27 |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2027-05-01 → 2027-10-27 (Oct 2024); stable since

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-01 | Undisturbed farmland/pasture across Waller/Fort Bend border; no grading, no solar signature | [north](imagery/s2_2026-01-15_north.png), [se](imagery/s2_2026-01-15_se.png), [sw](imagery/s2_2026-01-15_sw.png), [nne](imagery/s2_2026-01-15_nne.png) |
| 2026-06 | Heavily clouded; where clear shows same undisturbed land | [center](imagery/s2_2026-06-01_center.png) |

- Verdict: **no_activity** — 5 chips covering ~15 km swath across estimated site area; no tan graded polygon, no module rows, no substation pad. Site not precisely confirmed (low-confidence pin) but a 358 MW / ~1,500-ac array would be unmistakable at 10 m/px if present.

## 7. COD assessment

- Reported COD 2027-10-27 requires NTP ~now and 16-month build — extremely tight given FIS not yet approved
- FIS approval typically precedes NTP; without FIS, developer cannot order long-lead equipment or break ground per standard IA terms
- 358 MW / ~1,500 acres of solar in SE Texas: 18–24 months civil + electrical is typical for a project of this size
- No construction visible in Jan or Jun 2026; at today (Jul 2026), the project has effectively zero months of construction under its belt
- 1 prior COD drift (May→Oct 2027); Meets 6.9(1) in May 2026 = queue progressing but FIS lag is the binding constraint
- **Independent estimate: 2028-Q3** (assumes FIS by Q4 2026, NTP Q1 2027, 18-month build); **drift risk: high**

## 8. Could not determine

- Developer / parent company identity (all searches blocked; no public presence)
- EPC contractor, PPA offtaker, financing status
- IA exhibit details: milestone dates, financial security amounts, equipment specs (PUCT 402)
- Parcel IDs and acreage (CAD portals JS-only)
- Exact site location (no parcel, no delivery pin, no IA confirmation)
- Whether FIS approval is imminent or delayed
