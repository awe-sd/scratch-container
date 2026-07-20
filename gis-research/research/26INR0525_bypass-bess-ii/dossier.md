# Dossier — Bypass BESS II (26INR0525)

Researched 2026-07-19 · site 29.4700, -95.6420 · verdict **real_early**

## 1. Verdict

- **real_early** — SGIA signed 2026-05-08, NTP date June 30, 2026; 65×PF4200 inverters named in Exhibit C; Aypa Power confirmed as operator via IA contacts ([IA](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf))
- Construction: **no_activity** (NTP just issued Jun 2026; pre-construction as of Apr–Jul 2026 imagery)
- Site: 29.4700, -95.6420 — IA POI address text ("due South of 2201 Y.U. Jones Rd, Richmond TX 77469") + OSM Y.U. Jones Rd geometry, high confidence ([satellite view](https://www.google.com/maps/@29.470,-95.642,5000m/data=!3m1!1e3))
- COD: reported 2028-04-30 → independent **2028-Q1**, drift risk **medium** (IA COD Jan 3, 2028; 3 prior COD slips; BESS build is fast once NTP clears)

## 2. Site identification

- Derivation: IA Exhibit C names BYP Substation "due South of 2201 Y.U. Jones Rd, Richmond, TX 77469"; OSM confirms Y.U. Jones Rd (aka Lockwood Bypass) at 29.474–29.476°N, -95.641–95.642°W, adjacent to W.A. Parish plant ([IA Exhibit C](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf))
- **Stated project area: not stated** — BESS compact, likely ≤30 acres; no abatement/CAD doc found; imagery footprint unverified (no pad visible yet)
- Cross-checks: IA POI address ↔ OSM road ↔ W.A. Parish WAP substation (29.4808°N, -95.6242°W, Overpass) — all consistent within ~1 km; triage candidate (29.4627N, 95.6602W) was 4 km off, superseded by IA text
- Not obtainable: exact BYP substation parcel (not yet in CAD; BESS land rights acquisition required by 11 months before In-Service date = ~Nov 2026)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Bypass BESS II LLC | SPV | party on [IA](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf) |
| Aypa Power Development LLC | developer/owner | [IA Exhibit D](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf) — EFT acct name |
| Aypa Power | operator | [IA Exhibit D](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf) — ic.ercot@aypa.com |
| Blackstone | ultimate parent | [triage T3 sources](sources/T3_web_sweep_notes.md) — confirmed for Bypass BESS I, same developer |

- Financing: **not yet announced** for II; Bypass BESS I (same developer, same county) closed $190M in 2023; no separate II financing PR found

## 4. Land & county records

- Tenure: **unknown** — IA requires land rights by ~Nov 2026 (11 months before TIF In-Service); no CAD parcels under LLC/Aypa found (JS-rendered site, not conclusive)
- Abatements/agreements: none found (post-Ch.313 sunset, no JETI filing identified — normal for 2026 entry)
- CAD: 0 hits under "Bypass BESS II" or "Aypa" in Fort Bend CAD (JS-rendered search, not fully conclusive)

## 5. Interconnection & contractual schedule

- POI per signed IA: "BYP Substation… due South of 2201 Y.U. Jones Rd, Richmond, TX 77469, Fort Bend County" at WAP (W.A. Parish) 345 kV ([IA Exhibit C](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf))
- Equipment: 65× Power Electronics FREEMAQ PF4200 BESS bi-directional inverters @ ~3.17 MW each = 205.86 MW, 345 kV delivery

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_35077-2482_centerpoint-bypass-bess-ii-sgia.pdf)) | 2026-05-08 | $100,000 LC (due by Jun 30, 2026 NTP date); CIAC = $0 |

| Milestone | SGIA 2026 |
|---|---|
| NTP / Construction Authorization | 2026-06-30 |
| TIF In-Service | 2027-10-01 (or 12 mo after NTP) |
| Trial Operation | 2027-12-15 |
| Scheduled COD | **2028-01-03** (or 3 mo after In-Service) |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2026-05 → 2026-06 → 2027-04 → 2028-04; capacity halved 416 → 206 MW in Feb 2026

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-04 | Undisturbed farmland south of Y.U. Jones Rd; W.A. Parish complex visible, no pad | [Apr 2026](imagery/key/s2_2026-04-01_byp_site_pre_construction.png) |
| 2026-07 | Same undisturbed farmland; NTP just issued Jun 30, 2026; no construction yet | [Jul 2026](imagery/key/s2_2026-07-01_byp_site_latest.png) |

- Verdict: **no_activity** — site is raw farmland at NTP date; BESS build has not commenced; consistent with contracted schedule (TIF In-Service Oct 2027, 15 months away)

## 7. COD assessment

- The contractual Scheduled COD in the signed SGIA is **January 3, 2028** (or 3 months after TIF In-Service Oct 1, 2027); the reported queue COD of 2028-04-30 adds ~4 months of float above the IA date — plausible buffer given BESS fast-build nature
- BESS builds of this size (~200 MW) typically take 12–18 months once equipment is on site; NTP issued Jun 2026, In-Service contracted Oct 2027 = ~16 months — typical
- Risk: 3 prior COD slips spanning 2 years (2026-05 → 2028-04); capacity was halved in Feb 2026 — scope reduction signals study/design re-work; project stabilized at 206 MW with signed IA
- For: IA signed and filed; NTP date concrete (Jun 30, 2026); BESS inverter model specified (PF4200) — procurement likely underway; low financial security ($100k) signals generator-side costs are modest (interconnection is CenterPoint's expense)
- Against: no financing announcement yet for II; no construction commenced; CDSE credential failure prevented imagery after Jul 2026
- **Independent estimate: 2028-Q1, drift risk medium** — contractual anchor is Jan 3, 2028; reported 2028-04-30 is within range; medium risk given 3 prior slips but IA now anchors schedule

## 8. Could not determine

- Financing status for Bypass BESS II specifically (no PR found; Bypass BESS I = $190M for reference)
- Exact BYP substation parcel geometry/acreage (not yet in Fort Bend CAD; expected pre-construction)
- BESS duration/energy capacity (MWh) — not stated in IA
- Offtake counterparty for II (triage T3 sources say "already secured" per aggregator coverage, but no named counterparty found)
- CDSE imagery post-Jul 2026 (credentials expired; construction status after NTP not observable)
