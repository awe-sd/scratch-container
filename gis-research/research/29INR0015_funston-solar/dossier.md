# Dossier — Funston Solar (29INR0015)

Researched 2026-07-20 · site 32.78367, -99.72019 · verdict **real_active**

## 1. Verdict

- **real_active** — Sentinel-2 Jul 2026 shows multiple large dark-panel array blocks unmistakably installed; EIA-860M status "under construction >50%" since 2026-03 ([imagery](imagery/s2_2026-07-01.png))
- Construction: **substantially_complete**, first activity bracket: EIA status ≤50% 2025-12, >50% 2026-03 (exact date unresolved — CDSE down)
- Site: 32.78367, -99.72019 — EIA Form 860 direct record (plant 67359, address 3694 CR 267, Anson TX 79501), corroborated by IA Attachment C-3 project footprint map ([map](https://google.com/maps/@32.78367,-99.72019,5000m/data=!3m1!1e3))
- COD: reported 2027-07-01 → independent **2027-Q1**, drift risk **low** (near-complete array, tier-1 developer, 0 slips)

## 2. Site identification

- Derivation: EIA Form 860 (plant 67359) lat 32.78367 / lon -99.72019, address 3694 CR 267, Anson TX 79501 — authoritative federal registration ([eia_history.json](eia_history.json))
- **Stated project area: not quantified in acres** in IA; IA footprint map shows ~4 km N-S × 3 km E-W between CR 254 (N), CR 266 (S), FM-220 (W), CR 265 (E) ≈ 3,000–4,000 acres for 351 MW — imagery footprint consistent with northern array block visible in Jul 2026 chip
- Cross-checks: EIA coords ↔ IA Attachment C-3 footprint boundary ↔ Sentinel-2 array location — all agree within <1 km ([map p47](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA_map_p47.png))
- Not obtainable: CAD parcel list (Jones County CAD portal search blocked); exact POI switch coordinates (CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Funston Solar, LLC | SPV / Generator | [IA parties page](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf); EIA-860M plant 67359 |
| NextEra Energy Resources, LLC | Developer / parent | [IA Exhibit D](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf) — admin notices c/o NEER, 700 Universe Blvd, Juno Beach FL 33408; ROCC ops mailbox @nexteraenergy.com |
| Lone Star Transmission, LLC | TSP (NextEra Energy Transmission subsidiary) | [IA parties](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf) — files all Jones County IAs |

- Financing: $27,750,000 security posted (Corporate Guaranty or ILOC per [IA Exhibit E](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf)); no PPA or tax equity structure found (search down)

## 4. Land & county records

- Tenure: **leased** (presumed) — IA Exhibit C states generator must "acquire, on behalf of LST, easement or similar rights from the landowner(s)"; NextEra standard practice is lease/easement ([IA Exhibit C](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf))
- Abatements/agreements: **None** — Ch.313 program expired 2022; JETI ineligible for solar; project entered queue Feb 2024 (post-cutoff). Consistent with all post-2022 solar projects. ([ch313.py resolve](log.md))
- CAD: Jones County CAD parcel search **not retrieved** — web search backend down; no owner-name parcel data obtained

## 5. Interconnection & contractual schedule

- POI per signed IA: new "Footloose 345 kV" substation; 1.38-mile new 345 kV line from Footloose to Generator Step-Up Station; cut-in on existing West Shackelford–Phantom Hill Circuit 2 ([IA Exhibit C](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf))
- Equipment: 102 × PE FS4105M inverters @ 4.105 MVA = 351.4 MW nameplate (IA Exhibit C)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA — PUCT 35077-1965 ([pdf](sources/2026-07-19_puct_35077-1965_lst-funston-solar-IA.pdf)) | 2024-10-23 | $27,750,000 Corp Guaranty or ILOC |

_(No amendments found)_

| Milestone | Original IA (Oct 2024) |
|---|---|
| NTP Need Date | 2024-11-01 |
| TIF In-Service (Backfeed) | Later of **2026-10-16** or 24 months after NTP |
| Trial Operation (Sync) | Later of **2026-10-30** or 2 weeks after TIF |
| Scheduled COD | Later of **2027-07-01** or 2 months after TIF |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — 2027-07-01 held across all 27 monthly snapshots since 2024-04-01

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-12 | EIA status transitions: "Under construction ≤50%" (per EIA-860M; CDSE chip not retrieved) | [eia_history.json](eia_history.json) |
| 2026-03 | EIA status: "Under construction >50%" — majority of array physically installed | [eia_history.json](eia_history.json) |
| 2026-07-01 | **Multiple large dark-panel rectangular array blocks clearly visible** — substantially complete; access roads between sub-blocks; extends NW of EIA center | [s2_2026-07-01.png](imagery/s2_2026-07-01.png) |

- Verdict: **substantially_complete** — installed module blocks unmistakable at 10 m/px; substation structure consistent with near-complete site; commissioning/testing phase likely underway

## 7. COD assessment

- Contractual COD 2027-07-01 is the binding queue date and the IA-committed date; no amendments or slips recorded
- EIA-860M planned COD has been **2026-12** since Dec 2024 — developer is internally targeting Q4 2026, 6 months ahead of queue commitment; consistent with finishing construction and testing before winter
- Array is substantially complete per Jul 2026 imagery; TIF in-service date contractually 2026-10-16 — if LST delivers on time, grid connection complete Oct 2026, trial operation Oct/Nov 2026
- Sequential steps remaining: TIF commissioning (Oct 2026) → Trial Operation (Oct–Dec 2026) → COD declaration; typical trial operation is 1–2 months
- **Independent estimate: 2027-Q1** — Q4 2026 (EIA target) possible if trial operation proceeds smoothly; Q1 2027 is the more conservative base case; 2027-Q2 is the contractual ceiling
- Drift risk **low**: tier-1 developer (NextEra), all milestones cleared, array visually near-complete, 0 historical slips, $27.75M security at stake

## 8. Could not determine

- CAD parcel IDs and exact acreage (Jones County CAD blocked; web search down)
- First construction activity date (CDSE imagery service down during timelapse; EIA ≤50% 2025-12 is proxy)
- PPA offtaker and tax equity structure (no press releases found; search down)
- Exact Google Maps delivery pin for construction gate (gmaps returned unrelated project; staticmap API not enabled)
