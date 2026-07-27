# Dossier — Bluegill BESS (25INR0434)

Researched 2026-07-19 · site 29.9497, -95.0891 · verdict **real_early**

## 1. Verdict

- **real_early** — plat submitted to Houston Planning Commission ([Facebook post](sources/2026-07-19_facebook_huffman-tx-developments-plat-post.md)) confirms site and LLC; but no IA, no FIS approval, no construction visible
- Construction: **pre_construction**, no activity in Apr 2026 ([tight chip](imagery/key/s2_2026-04_tight_key.png))
- Site: 29.9497, -95.0891 — road intersection estimate for NWC FM-2100 / Old Atascocita Rd, Huffman TX, medium confidence ([satellite view](https://www.google.com/maps/@29.9497,-95.0891,5000m/data=!3m1!1e3))
- COD: reported 2027-10-31 → independent **2029-Q4**, drift risk **high** (no IA, no milestones, no construction)

## 2. Site identification

- Derivation: Facebook "Huffman Texas Developments" group post — "Bluegill Bess, LLC has submitted this plat to the Houston Planning Commission, it's a 25 acre tract on the northwest corner of FM-2100 Rd and Atascocita Rd" ([post](sources/2026-07-19_facebook_huffman-tx-developments-plat-post.md))
- **Stated project area: ~25 acres (plat) / 28.82 acres (parcel)** per [Facebook plat post](sources/2026-07-19_facebook_huffman-tx-developments-plat-post.md) and [LoopNet listing APN 1461570010002](sources/2026-07-19_loopnet_nwc-fm2100-atascocita-listing.md) — imagery footprint consistent (appropriate size for 251 MW BESS; compact 10-30 ac pad expected)
- Cross-checks: plat post (NWC FM-2100/Atascocita) agrees with LoopNet parcel (NWC FM-2100/Old Atascocita Rd, APN 1461570010002); POI tap on 138kV Atascocita–East Gate line is consistent with site location ~7 km east of Atascocita substation
- Not obtainable: exact parcel corners/centroid (HCAD blocked), CenterPoint East Gate substation coordinates (not in public sources), POI tap coordinates (likely CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Bluegill BESS, LLC (TX #0805105887) | SPV | [Facebook plat post](sources/2026-07-19_facebook_huffman-tx-developments-plat-post.md); [triage T3 web sweep](sources/t3_web_sweep.md) |
| Eolian, L.P. (Burlingame CA; GIP/BlackRock portfolio) | developer candidate | [Padua financing PR](sources/2026-07-19_eolian_padua-financing-pr.md); LLC address inference only — not confirmed |
| EPC | unknown | — |
| Offtaker | unknown | — |

- Financing: none identified — no IA, no financial security posted ([queue timeline](timeline.json))

## 4. Land & county records

- Tenure: **unknown** — listing was for-sale industrial land; plat submitted suggests purchase or option acquired
- Plat: submitted to Houston Planning Commission for 25-acre tract, NWC FM-2100 / Atascocita Rd ([post](sources/2026-07-19_facebook_huffman-tx-developments-plat-post.md))
- CAD: APN 1461570010002 identified via LoopNet ([listing](sources/2026-07-19_loopnet_nwc-fm2100-atascocita-listing.md)); current owner not verified — HCAD direct lookup blocked (404/403)
- Abatements: Ch.313 expired Dec 2022 (project ineligible). JETI database not machine-readable. No abatement record found.

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 138 kV 40130 Atascocita - 40690 East Gate" — CenterPoint Energy service territory, Harris County
- IA: **NOT SIGNED** — PUCT Interchange returned HTTP 402 on all URL patterns throughout research; IA existence unknown
- Financial security posted: **No** (queue data)

| IA document | Signed | Financial security posted |
|---|---|---|
| — (no IA found) | — | — |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2025-07-31 → 2026-10-01 → 2027-10-31; study phase stuck at "SS Completed, FIS Started, No IA" since Sep 2023 (22 months)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-04 | No BESS pad, no gravel staging, no container rows — undisturbed mixed land | [png](imagery/key/s2_2026-04_tight_key.png) |
| 2026-05 | Wide view (6 km buffer): FM-2100 corridor, no activity | [png](imagery/key/s2_2026-05_wide_key.png) |

- Verdict: **pre_construction** — bare land as of Apr 2026; no construction signatures at 2 km buffer around estimated site

## 7. COD assessment

- Reported 2027-10-31 is NOT grounded in a signed IA or any contractual document
- With 15 months remaining to Oct 2027: impossible to complete FIS approval, sign IA, post financial security, and build 251 MW BESS from bare ground (typical 12-18 month build timeline alone)
- FIS started May 2023 but not approved in 26+ months — study likely awaiting CenterPoint capacity confirmation or developer action
- Capacity halved Jun 2024 (501.9 → 251 MW) — likely a risk-reduction or scope change, not a sign of progress
- Prior drift: 2 slips totaling +24 months from original 2025-07-31 target
- **Independent estimate: 2029-Q4**, assuming FIS approval 2026, IA signed late 2026, construction start 2027, 18-month build. High drift risk — project may cancel or slip further without milestones.

## 8. Could not determine

- IA filing (PUCT Interchange portal blocked — HTTP 402 throughout)
- Current HCAD owner of APN 1461570010002 (lookup blocked — 404/403)
- Developer identity confirmed (TX SOS paid access required; Eolian link is address inference only)
- JETI tax abatement (database not machine-readable)
- Exact site coordinates (estimated from road intersection only, ±500 m uncertainty)
- CenterPoint East Gate substation location (not in public sources)
- Offtaker, EPC, financing status
