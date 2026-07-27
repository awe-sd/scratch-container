# Dossier — Van Zandt Energy Storage (25INR0301)

Researched 2026-07-19 · site not located · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-03-03 (queue milestone + [PUCT filing reference](#5-interconnection--contractual-schedule)); FIS approved 2024-11-18 ([timeline](timeline.md))
- Construction: **pre-construction** — no construction milestones achieved; financial security not posted; no build evidence in imagery
- Site: not located — POI = Odessa EHV Switch 138 kV (bus 1027, Ector County, Oncor) confirmed via [TPIT](sources/2026-07-19_ercot_tpit_july2026.xlsx); substation coordinates could not be resolved (CEII + JS-walled portals)
- COD: reported 2027-05-15 → independent **2028-Q2**, drift risk **high** (NTP not posted; no developer track record; unexplained COD acceleration)

## 2. Site identification

- Derivation: no site located — imagery search around OSM Moss Substation proxy (31.81327°N, -102.49554°W) and surrounding Odessa locations returned dense residential urban fabric inconsistent with BESS siting
- **Stated project area: unknown** — IA PDF not retrieved; no CAD or abatement hit
- POI confirmed: "Odessa EHV Switch 138 kV" = ERCOT bus 1027, Ector County, Oncor ([TPIT](sources/2026-07-19_ercot_tpit_july2026.xlsx) projects 93466, 71182, 81240, 81383, 81175 all reference this bus)
- Not obtainable: precise substation coordinates (OSM Overpass 406; HIFLD API errors; ERCOT bus coordinates unavailable; CEII protection)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Van Zandt Energy Storage LLC | SPV | queue milestone data (iaSigned); PUCT filing reference (2025-03-31) |
| Rocky Mountain Energy Holdings, LLC | developer | TX Comptroller franchise tax (ZIP 55401 Minneapolis MN + 75201 Dallas TX) |
| — | EPC | not found |
| — | PPA offtaker | not found |

- Financing: no announcement found; financial security not yet posted ([queue](timeline.json): `financialSecurityAndNoticeToProceedProvided = "No"` as of Jun 2026)
- Developer has no public website (domain parked/for-sale); no press releases on PR Newswire or Business Wire; no LinkedIn project posts; no SEC EDGAR filings

## 4. Land & county records

- Tenure: **unknown** — no CAD owner-name search results (Ector CAD portal JS-walled); IA PDF not retrieved
- Abatements: none found — normal for post-2022 BESS entry (Ch.313 expired 2022; JETI registry showed no hit, expected at IA stage)
- CAD: 0 hits for Van Zandt Energy Storage, Rocky Mountain Energy Holdings (JS rendering required)

## 5. Interconnection & contractual schedule

- POI per queue data: "1027 Odessa EHV Switch 138 kV", Ector County, Oncor — confirmed as active 345/138 kV substation with multiple live TPIT upgrades ([xlsx](sources/2026-07-19_ercot_tpit_july2026.xlsx))
- PUCT filing reference: "Standard Generation Interconnection Agreement between Oncor Electric Delivery and Van Zandt Energy Storage LLC", filed 2025-03-31; **PDF not retrieved** (PUCT Interchange requires JavaScript)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-03-03 | unknown (IA PDF not retrieved) |

| Milestone | Original IA |
|---|---|
| In-Service | not obtained |
| Trial Operation | not obtained |
| Scheduled COD | not obtained |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2025-04-29 → 2026-09-25 → 2027-04-13 → 2028-04-13 → 2027-05-15; entered queue 2023-06-01 (37 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Dense urban residential at OSM Moss Sub proxy; BESS pad not found at any tried location | [1km chip](imagery/s2_2026-07-01_poi_1km.png) |
| 2026-07 | 3km chip around proxy — same urban fabric; no BESS signatures | [3km chip](imagery/s2_2026-07-01_poi_3km.png) |

- Verdict: **not_located** — imagery inconclusive because substation coordinates could not be verified; dense urban area is not where a BESS pad would be, suggesting proxy coordinates were wrong. No construction visible at any searched location.

## 7. COD assessment

- Reported 2027-05-15 COD requires NTP by approximately Nov 2026 at the latest (12-month BESS build); as of Jun 2026 financial security is NOT posted and NTP has not been given
- 26 months from IA signing (Mar 2025) to reported COD (May 2027) is technically achievable for a BESS, but only if NTP issues ~immediately
- The unexplained 11-month pull-forward (2028-04-13 → 2027-05-15 in the Mar-2026 update) coincided with no new milestone — the acceleration is a data anomaly, not evidence of progress
- Developer Rocky Mountain Energy Holdings has zero public track record, no financing announcement, no EPC named — profile consistent with a pre-development/speculative stage
- Independent estimate: **2028-Q2** (assumes NTP mid-2027 + 12-month BESS build); drift risk **high**

## 8. Could not determine

- Precise Odessa EHV Switch / site coordinates (CEII + portal JS walls)
- IA milestone schedule, financial security amount (PDF not retrieved)
- Developer identity beyond TX franchise-tax registrations (no website, no press, no EDGAR)
- Whether project has signed a PPA or begun permitting beyond the IA
- Site acreage / exact parcel (no IA exhibit, no CAD hit)
