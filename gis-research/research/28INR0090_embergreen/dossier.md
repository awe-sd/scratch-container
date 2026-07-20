# Dossier — EmberGreen (28INR0090)

Researched 2026-07-18 · site 29.3695, -96.0912 · verdict **real_early**

## 1. Verdict

- **real_early** — TCEQ **EGU Standard Permit 178642 issued 2024-12-20** for two simple-cycle gas CTGs at "Ray Road, County Road 229, Wharton, TX 77488" ([notification letter](sources/2026-07-18_tceq_notification-letter_178642.pdf), [technical review](sources/2026-07-18_tceq_technical-review_178642.pdf)); no IA, no construction, no confirmed turbine 18 mo from reported COD.
- Construction: **no_activity** — agricultural land 6 mo before reported COD ([2026-06-01 chip](imagery/key/s2_2026-06-01_rayroad.png))
- Site: 29.3695, -96.0912 — TCEQ permit address → OSM road intersection, medium-high confidence ([map](https://www.google.com/maps/@29.3695,-96.0912,5000m/data=!3m1!1e3))
- COD: reported 2028-01-01 → independent **2031-Q1+**, drift risk **high** (no IA, no turbine order, no construction)

## 2. Site identification

- Derivation: TCEQ permit specifies "**Ray Road, County Road 229, Wharton, Texas 77488**" ([tech review](sources/2026-07-18_tceq_technical-review_178642.pdf) p.1); OSM Nominatim geocoded Ray Road to 29.3706, -96.0921 and CR 229 seg to 29.3689, -96.0904 — intersection at ~29.3695, -96.0912
- **Stated project area:** not disclosed in TCEQ EGU Standard Permit (Standard Permit path omits acreage); no Ch313/JETI or IA available to cross-check. Imagery footprint check: unverified (site undisturbed)
- Cross-checks: TCEQ permit address, OSM Ray Rd + CR 229 geometry, GEM Wiki "approximate 29.28, -96.22" (imprecise, ~13 km SW) — TCEQ address takes precedence
- Not obtainable: exact parcel geometry (Wharton CAD SPA has no scrapable API surface); Caney-Hungerford 138 kV switch coords (CEII redaction pattern)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| EmberGreen Energy Center LLC | SPV | [TCEQ permit letter to Raj Suri, CEO, 4410 Dusty Meadow Ln, Sugar Land TX](sources/2026-07-18_tceq_notification-letter_178642.pdf); TX foreign LLC filed 2026-02-04 (triage) |
| EmberClear Corp | developer/parent | [GEM Wiki EmberGreen page](https://www.gem.wiki/EmberGreen_power_plant) (operator + owner + parent = EmberClear); [Power Technology 2024-08](sources/power_technology_emberclear.md) |
| — | EPC | none announced |
| — | turbine OEM | **none announced**; Aug 2024 press said "discussions ongoing with leading manufacturer" ([Power Technology](sources/power_technology_emberclear.md)) |
| ConocoPhillips + Matterhorn pipeline | gas supply | [Power Technology 2024-08](sources/power_technology_emberclear.md) |

- Financing: **Texas Energy Fund $432M loan application** filed (In-ERCOT Generation Loans Program, NOI APP 00000130) per [Power Technology 2024-08](sources/power_technology_emberclear.md); TEF docket number & due-diligence status not verifiable via PUCT Interchange (triage's "56455" is confirmed to be a different applicant "Sky2 TEF NOI", not EmberGreen — see log T27)

## 4. Land & county records

- Tenure: **unknown** — no Wharton CAD parcel data extractable (React SPA, no server-rendered HTML)
- Abatements/agreements: none found — Ch313 sunset 2022; no JETI/ISD agreement surfaced; commissioners-court minutes not searched (portal blocked)
- CAD: parcels-under-LLC search not runnable; the LLC filed TX foreign only in Feb 2026 (16 months AFTER TCEQ permit issued), so any parcels are likely still held under option/purchase agreement rather than titled to the SPV

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 138kV 48050 Caney - 44150 Hungerford" — no signed IA on file with ERCOT (`iaSigned` null through 2026-06-01 snapshot; [timeline.md](timeline.md))
- Equipment (per TCEQ permit): **2× simple-cycle natural-gas CTGs, combined nominal 900 MW**, SCR + CEMS for NOx/CO; permit total emissions 212.56 tpy NOx, 248.04 tpy CO ([emissions table](sources/2026-07-18_tceq_notification-letter_178642.pdf) p.3)
- **900 MW permit vs 1036 MW queue** — capacity bumped in queue Aug 2025 without matching TCEQ permit amendment; a larger unit may require permit revision

| IA document | Signed | Financial security posted |
|---|---|---|
| No IA on file | — | — |

- Milestones: no IA schedule to compare. ERCOT milestones: FIS requested 2024-12-18, FIS approved 2026-04-21, iaSigned null ([timeline.md](timeline.md))
- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2028-01-01 held stable across all 18 snapshots since Jan 2025 (pre-IA project, no reason to drift yet)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-01 | agricultural land, small rural roads, no clearing / no laydown / no pad, US-59 visible NE | [png](imagery/key/s2_2026-06-01_rayroad.png) |
| 2026-06-15 | (triage chip, 3.5 km NE of actual site at Hungerford CDP): rural + highway, no activity | [png](imagery/s2_2026-06-15.png) |

- Verdict: **no_activity** — pre-construction 6 months before reported COD. Thermal builds take 24-36 mo; construction should be visibly underway by now for a Jan 2028 COD. Baseline pre-permit chip (2024-10) not retrievable — CDSE token 401/403 during synthesis window.

## 7. COD assessment

- Reported 2028-01-01 has **zero queue-history drift** (18 stable snapshots) — but this is not achievement evidence; it's a placeholder attached to a pre-IA project with no downstream milestones to force a slip
- Blockers to 2028-01-01: (1) no signed IA (~9-15 mo to negotiate + amend after FIS); (2) no confirmed turbine order (heavy-frame CTG lead time 3-5 yr from firm PO); (3) no visible construction 18 mo out; (4) 900→1036 MW capacity bump not yet in TCEQ permit
- The TCEQ Standard Permit + specific greenfield address + engineered emissions controls + developer with two prior US plants (Birdsboro PA operating, Lincoln Land IL announced) confirms this is a **real, engineered project**, not a shell — but the timeline is fictional
- **Independent estimate: 2031-Q1 at earliest, drift risk HIGH.** A reasonable build path: IA signed 2027, turbine PO 2027, construction start 2028, in-service ~2030-2031

## 8. Could not determine

- Exact PUCT TEF docket number for EmberGreen NOI (Interchange requires known control#; party-name reverse lookup unsupported; triage's "56455" is a different applicant)
- Wharton CAD parcels tied to EmberGreen / EmberClear (esearch.whartoncad.net React SPA has no server-rendered listings)
- Turbine OEM identity / order status (no public announcement post Aug 2024)
- Current status of Lincoln Land Energy Centre IL (developer website "under maintenance")
- Baseline pre-permit satellite chip at Ray Rd/CR 229 (CDSE OAuth token repeatedly 401/403)
- Exact project acreage (Standard Permit path omits it; no IA/abatement doc to cite)
