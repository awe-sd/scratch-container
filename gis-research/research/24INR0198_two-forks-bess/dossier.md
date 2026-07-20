# Dossier — Two Forks BESS (24INR0198)

Researched 2026-07-19 · site 33.5497, -97.1801 · verdict **unclear**

## 1. Verdict

- **unclear** — IA signed May 2024 and MW refined 5× over 4 years signal live development, but developer is entirely unidentifiable publicly; no construction visible; FIS never granted; 3 prior COD slips
- Construction: **pre-construction / unconfirmed**, first activity not observed ([contact sheet](imagery/contact_sheet.png))
- Site: 33.5497, -97.1801 — OSM 138kV substation nodes, medium confidence ([satellite view](https://www.google.com/maps/@33.5497,-97.1801,5000m/data=!3m1!1e3))
- COD: reported 2027-06-30 → independent **2028-Q2 to 2028-Q4**, drift risk **high** (no groundbreak, 3 prior slips, FIS absent)

## 2. Site identification

- Derivation: OSM Overpass returned two unnamed 138kV substation nodes at 33.5497209,-97.1801476 and 33.549617,-97.1795355 (~6 m apart, same compound) — best candidate for POI "684 SPRING 138kV" in Cooke County ([artifact](sources/2026-07-19_osm_spring-substation.json))
- **Stated project area: not obtainable** — no abatement/CAD/IA exhibit found; expected ~30-80 acres for 309.8 MW BESS
- Cross-checks: Rippey Solar (Adapture Renewables, 59 MW, EIA 62773, operational 2020-12) confirmed at 33.5527,-97.1786 at same substation compound ([artifact](sources/2026-07-19_osm_rippey-solar.json)); imagery confirms large pre-existing solar array at this location
- Imagery: the regular white grid in all frames (2024-07 through 2026-06) is **Rippey Solar**, not Two Forks BESS activity ([1km frame Jul 2026](imagery/s2_2026-07-01_1km.png))
- Not obtainable: exact Spring substation coordinates (PUCT 402-blocked); distinct BESS pad location (indistinguishable at 10 m/px from Rippey Solar compound)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Two Forks BESS, LLC (presumed) | SPV | queue data: "Two Forks LLC" per ercotqueue.com (aggregator, cited for name only) |
| Unknown | developer/owner | no press releases, no TX SOS free hit, no news |
| Unknown | EPC | not found |
| Unknown | offtaker | not found |

- Financing: unknown — no public announcements found

## 4. Land & county records

- Tenure: **unknown** — PUCT IA PDF not obtainable (402-blocked); CAD portal JS-rendered, owner search failed
- Abatements: none — expected for post-2022 BESS (Ch.313 expired; no JETI entry)
- CAD: 0 parcels confirmed — portal inaccessible without JS/browser session ([cookecad.org](https://www.cookecad.org/))

## 5. Interconnection & contractual schedule

- IA existence confirmed from queue data: iaSigned = 2024-05-03, meets6.9(1) = 2024-05-06 ([timeline.md](timeline.md))
- POI per signed IA: unknown — PUCT Interchange 402-blocked; schedule exhibit and parties page not obtained
- TSP: likely Oncor (CDR zone NORTH, Cooke County = Oncor service territory)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([not retrieved](sources/)) | 2024-05-03 | unknown — PUCT blocked |

| Milestone | Original IA |
|---|---|
| In-Service | unknown (IA PDF not obtained) |
| Trial Operation | unknown |
| Scheduled COD | unknown (reported 2027-06-30) |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2024-12 → 2025-12 → 2027-07 → 2027-06-30; in queue since 2022-10 (45 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-07 | Pre-existing Rippey Solar array visible; no BESS activity identified | [2024-07](imagery/s2_2024-07-01_2km.png) |
| 2025-01 | Same Rippey Solar footprint; no change consistent with BESS construction | [2025-01](imagery/s2_2025-01-01_2km.png) |
| 2025-07 | Same; no new compact pad visible near substation | [2025-07](imagery/s2_2025-07-01_2km.png) |
| 2026-04 | Same Rippey Solar; no distinct BESS pad at 2km resolution | [2026-04](imagery/s2_2026-04-01_2km.png) |
| 2026-06/07 | Rippey Solar stable; substation visible in 1km tight frame; no BESS container rows | [2026-07 1km](imagery/s2_2026-07-01_1km.png) |

- Verdict: **no_activity_confirmed** — all detected changes are Rippey Solar (pre-existing 2020). BESS pad, if any, is inside the substation compound and not separately resolvable at 10 m/px. Cannot exclude recent site prep.

## 7. COD assessment

- Reported 2027-06-30 **not grounded** in a readable IA schedule — PUCT Interchange is 402-blocked; the date comes only from the queue report itself
- BESS build is 12-18 months minimum; no construction start or groundbreak confirmed through July 2026
- For a 2027-06-30 COD, groundbreak would need to have occurred by ~Dec 2025 to Jan 2026 — possible but not confirmed in imagery (CDSE tight chip unavailable due to auth failure)
- FIS never granted (unusual but not disqualifying — IA was signed; ERCOT guide allows IA before FIS in some cases)
- Pattern of 3 slips over 4 years (18 months total drift to date) argues against the current target being firm
- MW refinements (300.0 → 309.8 MW, 5 steps) suggest active development rather than total abandonment
- **Independent estimate: 2028-Q2 to 2028-Q4**, drift risk **high** — no construction visible, no financing announcement, developer opaque

## 8. Could not determine

- Developer/owner identity (all public channels exhausted; PUCT Interchange is payment-blocked)
- Signed IA details: schedule milestones, financial security amounts, POI confirmation, parties
- Project area (acres) — no abatement, no CAD parcel, no IA exhibit
- Whether any site prep has occurred inside the substation compound (CDSE auth failure on tight chip)
- Whether FIS absence is a waiver, ongoing study, or a blocking risk
- Exact Spring/684 substation coordinates (no CEII-clear source found)
