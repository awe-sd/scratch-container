# Dossier — Rock Rose BESS (26INR0201)

Researched 2026-07-19 · site 29.4743, -95.6229 · verdict **real_early**

## 1. Verdict

- **real_early** — fully-developed pre-NTP asset with signed IA and all 6.9 milestones met; no construction yet visible ([April 2026 frame](imagery/key/s2_2026-04-01_whaley_xwide.png))
- Construction: **no_activity** — no gravel pad or container rows adjacent to Whaley 345kV as of 2026-04
- Site: 29.4743, -95.6229 — OSM unnamed 345kV substation east of W.A. Parish, identified as Whaley 345kV via queue POI, medium confidence ([satellite view](https://www.google.com/maps/@29.4743,-95.6229,5000m/data=!3m1!1e3))
- COD: reported 2027-03-19 → independent **2027-Q4**, drift risk **high** (NTP not confirmed; Q1 2027 window likely missed)

## 2. Site identification

- Derivation: OSM Overpass query returned unnamed 345kV substation at 29.4743°N, -95.6229°W immediately adjacent to W.A. Parish generating station; ERCOT queue POI "44070 Whaley 345 kV" + nearby Whaley Corner hamlet (OSM node 29.4461°N, -95.6741°W) confirm name ([OSM source](sources/2026-07-19_osm_whaley-substation.md))
- **Stated project area: not found** — no IA retrieved (PUCT blocked), no CAD parcels, no abatement app found
- Cross-checks: OSM substation location ↔ POI description "Whaley 345 kV" ↔ W.A. Parish known anchor (29.4808°N, -95.6242°W per OSM) — consistent within 0.1 km. BESS would be sited within ~1 km of this anchor.
- Not obtainable: exact parcel/lease boundary; PUCT IA POI confirmation (portal blocked); Google Maps delivery pin (API rate-limited throughout)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Rock Rose Energy Storage LLC | SPV | [Advanced Power PR](sources/2026-07-19_advanced-power_rock-rose-sale-pr.md) |
| Advanced Power | original developer | [Advanced Power PR](sources/2026-07-19_advanced-power_rock-rose-sale-pr.md) |
| Greenflash Infrastructure (unconfirmed) | buyer Oct 2025 | [triage source](sources/advanced_power_sale.md) — buyer unnamed in official press release |
| PEI Global Partners | financial advisor (sale) | [Advanced Power PR](sources/2026-07-19_advanced-power_rock-rose-sale-pr.md) |

- Financing: project sold pre-NTP Oct 2025 as "fully developed"; no construction financing or lender announced as of research date ([PR](sources/2026-07-19_advanced-power_rock-rose-sale-pr.md))

## 4. Land & county records

- Tenure: **unknown** — no Fort Bend CAD parcels found under Rock Rose Energy Storage (portal JS-only; owner-name URL patterns all 404); expected for pre-NTP BESS on leased agricultural/industrial land
- Abatements: JETI (post-2022 vehicle) — TX Comptroller portal JS-only, no public search; Fort Bend commissioners court URL patterns inaccessible. **Could not confirm or rule out**
- CAD: 0 hits (access-limited, not conclusive)

## 5. Interconnection & contractual schedule

- POI per queue: "44070 Whaley 345 kV" — CenterPoint transmission, adjacent to W.A. Parish
- IA document: **NOT retrieved** — PUCT Interchange returns HTTP 402 on all query patterns. IA existence confirmed only by queue milestone (iaSigned 2024-06-15)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([not retrieved](sources/)) | 2024-06-15 | Unknown — PUCT blocked |

| Milestone | Queue record |
|---|---|
| IA signed | 2024-06-15 |
| Meets 6.9(1) | 2025-11-13 |
| Meets all 6.9 | 2026-05-26 |
| Construction start | — (not reported) |
| Scheduled COD | 2027-03-19 (reported claim) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2026-07-02 → 2026-12-15 → 2027-03-19; in reports since 2023-09 (34 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-01 | Undisturbed farmland/industrial surrounds at Whaley 345kV; no pad | [jan 2026](imagery/key/s2_2026-01-01_whaley.png) |
| 2026-04 | Clear frame — Whaley 345kV switching yard visible; surrounding fields undisturbed; no gravel pad or container rows | [apr 2026](imagery/key/s2_2026-04-01_whaley_xwide.png) |
| 2026-07 | Cloudy — no useful observation | (not usable) |

- Verdict: **no_activity** — no ground disturbance near POI substation as of April 2026; consistent with pre-NTP status at time of sale

## 7. COD assessment

- Reported COD 2027-03-19 was already the third schedule in the queue; project has drifted ~8 months total
- Project was sold as "fully developed / pre-NTP" in Oct 2025 ([PR](sources/2026-07-19_advanced-power_rock-rose-sale-pr.md)); a BESS build requires ~12-18 months from NTP
- April 2026 imagery shows no_activity → NTP has not yet been issued (or was issued very recently, post-April 2026)
- To hit 2027-03-19, NTP was needed by ~Q3 2025 (18-month build) or Q1 2026 (12-month sprint); April 2026 no-activity makes Q1 2027 COD implausible
- Risk factors: new owner (Greenflash, unconfirmed), no public NTP or construction financing announcement, 2 prior slips
- **Independent estimate: 2027-Q4, drift risk high** — BESS-speed build from ~mid-2026 NTP; ~12 months minimum

## 8. Could not determine

- Exact site parcel boundary or acreage (CAD inaccessible, no IA retrieved)
- PUCT IA text, schedule exhibits, financial security amounts (PUCT Interchange HTTP 402)
- Buyer identity in IA (Greenflash Infrastructure unconfirmed; unnamed in official PR)
- JETI abatement application (portal not publicly searchable)
- Whether NTP was issued post-April 2026 (would pull COD earlier, toward 2027-Q3)
- EPC contractor
