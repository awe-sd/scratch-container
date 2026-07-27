# Dossier — First Capitol BESS (26INR0226)

Researched 2026-07-19 · site ~29.144, -95.645 (low confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-05-15 confirmed in ERCOT queue milestones (iaSigned field) + 6.9(1) passed 2025-02-12; project cleared contractual gate but no ground-level construction visible
- Construction: **no_activity**, first activity not yet seen ([Dec 2025 chip](imagery/s2_midpoint_2025-12-01.png))
- Site: ~29.144, -95.645 — POI inference only (West Columbia Main 138kV sub location unknown), low confidence ([satellite view](https://www.google.com/maps/@29.144,-95.645,5000m/data=!3m1!1e3))
- COD: reported 2027-11-01 → independent **2028-Q2**, drift risk **high** (5 prior slips, no construction visible, developer unknown)

## 2. Site identification

- Derivation: POI = "Tap 138kV West Columbia Main (39500) - Sweeny Cogen (110505)"; Sweeny Cogen confirmed at 29.0728, -95.7446 via [OSM Nominatim](https://nominatim.openstreetmap.org/search?q=Sweeny+Cogeneration+Texas) (Phillips 66 complex, Old Ocean, Brazoria Co.); BESS must tap the West Columbia Main 138kV sub, estimated near West Columbia (29.144, -95.645) on TX-36 corridor
- **Stated project area: unknown** — no abatement doc, no CAD parcel, no IA exhibit retrieved; BESS at 257 MW expected ~15-40 acres
- Cross-checks: Sweeny Cogen ([OSM](https://nominatim.openstreetmap.org/search?q=Sweeny+Cogeneration+Texas)); no Google Places pin (rate-limited); no CAD parcel match
- Not obtainable: Exact West Columbia Main substation coordinates (not in OSM, HIFLD Brazoria County query returned 0 substations); IA PDF not retrieved (PUCT Interchange JS-rendered)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| First Capitol BESS, LLC | SPV (presumed) | Party name in ERCOT queue |
| Unknown | Developer | 0 hits in web search, TX Comptroller, SEC, LinkedIn |
| Unknown | EPC | Not identified |
| Unknown | Offtaker/PPA | Not identified |

- Financing: unknown — no press release or financing announcement found anywhere

## 4. Land & county records

- Tenure: **unknown** — Brazoria CAD portal JS-rendered/login-required; no owner-name search completed; battery projects use minimal land (~15-40 ac) typically leased
- Abatements/agreements: none — Ch.313 expired 2022; project entered queue 2023; JETI not found
- CAD: 0 parcel hits (portal inaccessible; battery projects on leased land often absent under LLC name anyway)

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "Tap 138kV West Columbia Main (39500) - Sweeny Cogen (110505)", Brazoria Co. — consistent with CenterPoint Energy Houston Electric territory (COASTAL zone)
- FIS status: requested 2023-09-22, approved = **null** despite IA signed — atypical; may be data lag or waiver

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (PDF not retrieved) | 2025-05-15 | Unknown — PUCT portal inaccessible |

| Milestone | Original IA |
|---|---|
| In-Service | Not retrieved |
| Trial Operation | Not retrieved |
| Scheduled COD | Not retrieved |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2026-05-31 → 2026-04-15 → 2025-12-31 → 2026-05-01 → 2027-05-01 → 2027-11-01 (net +17 months since Sep 2023 entry)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-09 | Partly cloudy; clear areas show agricultural fields, no BESS pad | [Sep 2025](imagery/s2_midpoint_2025-09-01.png) |
| 2025-12 | Mostly clear 4km chip; West Columbia visible upper-right; no gravel pad or container rows | [Dec 2025](imagery/s2_midpoint_2025-12-01.png) |
| 2026-06 | Cloudy; Sweeny Cogen refinery complex visible (no BESS); West Columbia area clouded | [Jun 2026](imagery/s2_midpoint_2026-06-15.png) |

- Verdict: **no_activity** — no pale gravel pad or parallel container rows visible at estimated POI location through Dec 2025; caveat: site pinpoint is low-confidence (West Columbia Main substation coordinates unconfirmed)

## 7. COD assessment

- Reported 2027-11-01 is **not contractually grounded** in retrieved documents — IA PDF not accessible; milestone dates unknown
- 5 prior COD slips (net +17 months) establish a pattern of persistent delay; project has drifted in every year since 2023 entry
- No construction visible as of Dec 2025 — BESS build window of 12-18 months means groundbreaking must occur by ~mid-2026 to meet Nov 2027 COD; no evidence this has happened
- Developer entirely unknown — no financing, EPC, PPA, or press release found; "dark" developer profile consistent with speculative or early-stage project
- FIS approved = null is anomalous for a project with IA signed; adds technical uncertainty
- **Independent estimate: 2028-Q2, drift risk high** — reflecting one further ~6-month slip from reported date given lack of visible construction start and unknown financing/developer state; could slip further if developer is not capitalized

## 8. Could not determine

- Developer identity (zero results across all searched sources)
- IA contractual milestones (PUCT Interchange JS-rendered; PDF not downloaded)
- Financial security amount and IA schedule exhibits
- Exact West Columbia Main 138kV substation coordinates (not in OSM, HIFLD, or Nominatim)
- Site acreage (no abatement, no CAD, no IA exhibit)
- FIS approval anomaly explanation (null despite IA signed)
- Any financing, EPC, or offtake commitment
