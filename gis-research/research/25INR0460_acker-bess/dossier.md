# Dossier — Acker BESS (25INR0460)

Researched 2026-07-19 · site 34.5197, -102.0387 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-04-21 with Oncor (PUCT Docket 35077); developer Navitas Energy is active in ERCOT storage backed by [Leyline Renewable Capital](sources/2026-07-19_prnewswire_leyline-navitas-energy-launch.html); but Financial Security/NtP = No as of June 2026 and zero construction visible
- Construction: **pre-construction**, no activity seen in any frame
- Site: 34.5197, -102.0387 — OSM Overpass confirmed Ogallala Substation (way 453589277, operator Sharyland Utilities, 345 kV), high confidence ([satellite view](https://www.google.com/maps/@34.5197,-102.0387,5000m/data=!3m1!1e3))
- COD: reported 2028-04-17 → independent **2028-Q4 to 2029-Q2**, drift risk **high** (no NtP, 3 prior slips, no financing/EPC public)

## 2. Site identification

- Derivation: OSM Overpass API (node/way 453589277) returns `name=Ogallala Substation`, `power=substation`, `voltage=345000`, `operator=Sharyland Utilities`, Castro County TX. Sentinel-2 chips at these coords show the substation structure matching the POI.
- **Stated project area: unknown** — no abatement filing, IA exhibits inaccessible (PUCT 402), CAD requires browser session. At 301 MW BESS, expected ~15–60 acres beside substation.
- Cross-checks: triage estimate (34.51, -102.07) agrees within 0.3 km; Sentinel-2 confirms substation structure at confirmed coords; POI text "23912 Ogallala 345 kV" matches OSM node name exactly
- Not obtainable: IA Exhibit C (CEII status unknown; PUCT paywalled); exact acreage

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Ogallala BESS LLC | ERCOT Interconnecting Entity (SPV queue name) | ERCOT GIS Report Jun 2026 row 734 |
| Acker BESS LLC | TX-registered SPV / PUCT IA counterparty | TX SOS 0805263391; PUCT Docket 35077 item 2136 |
| Navitas Energy LLC | Developer / sole member of Acker BESS LLC | TX SOS 0804234630; [Leyline PR](sources/2026-07-19_prnewswire_leyline-navitas-energy-launch.html) |
| Leyline Renewable Capital | Growth capital backer | [PR Oct 2022](sources/2026-07-19_prnewswire_leyline-navitas-energy-launch.html) — 500–1000 MW ERCOT storage target |

- Financing: No project-level financing announcement; Leyline provided portfolio-level growth capital (non-dilutive) announced Oct 2022 ([PR](sources/2026-07-19_prnewswire_leyline-navitas-energy-launch.html)). No EPC named. No PPA announced.

## 4. Land & county records

- Tenure: **unknown** — no CAD parcels found under Acker BESS / Navitas / Ogallala BESS (browser-session required at esearch.castrocad.org; programmatic search blocked)
- Abatements: None — Ch.313 expired end-2022; no JETI application found. Normal for post-2022 BESS.
- TCEQ: No permits — battery storage has no combustion emissions (none required, absence expected)

## 5. Interconnection & contractual schedule

- POI per signed IA: "23912 Ogallala 345 kV" — Oncor TSP (PUCT Docket 35077, signed 2025-04-21; doc 35077_2136_1499463.PDF — portal 402, not retrieved)
- Financial Security / NtP: **No** per ERCOT GIS June 2026 — construction not yet authorized 14+ months post-IA

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-04-21 | Not yet (GIS June 2026: Financial Security/NtP = No) |

*IA milestone schedule exhibits not retrievable (PUCT Interchange paywalled; HTTP 402 on all paths).*

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2025-12-01 → 2026-09-15 → 2027-09-14 → 2028-04-17; 28 months total drift; in reports since 2023-05 (38 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-03 | Undisturbed ag fields, substation unchanged | [key/s2_2025-03-15_tight.png](imagery/key/s2_2025-03-15_tight.png) |
| 2025-06 to 2025-12 | Pure ag, center-pivot circles, no change | original triage frames |
| 2026-02 to 2026-06 | Same — no site prep, no gravel, no containers | [s2_tight_2026-06-15.png](imagery/s2_tight_2026-06-15.png) |
| 2026-06 (xwide) | 4 km² frame: substation + farm fields, zero BESS footprint | [key/s2_2026-06-15_xwide.png](imagery/key/s2_2026-06-15_xwide.png) |

- Verdict: **no_activity** — 11 frames across 15 months at confirmed substation coords, all show pure agricultural landscape; Sentinel-2 10 m resolution would clearly detect any gravel pad or container rows if present

## 7. COD assessment

- Reported 2028-04-17 is ungrounded operationally: Financial Security / NtP not posted as of June 2026, 14+ months after IA signing
- 3 prior COD slips totaling 28 months (2025-12 → 2028-04) indicate structural delay tendency; every prior COD was missed
- Navitas is a small developer (single-founder, ~Austin office) with no announced project-level financing or EPC — these typically precede NtP by 6-12 months
- Even optimistic case (NtP by Q3 2026, fast-track build): BESS construction 12-18 months → earliest realistic COD ~2027-Q4; but no evidence NtP is imminent
- Conservative case (financing + EPC signed H1 2027, build starts Q3 2027): COD 2028-Q4 to 2029-Q1
- **Independent estimate: 2028-Q4 to 2029-Q2, drift risk high**

## 8. Could not determine

- IA milestone schedule (PUCT Interchange paywalled — HTTP 402 on all paths)
- Financial security amount and structure
- Project acreage (no abatement, IA exhibits unavailable, CAD browser-only)
- EPC contractor and PPA offtaker (none publicly announced)
- Whether "Ogallala BESS LLC" and "Acker BESS LLC" are the same legal entity or co-registered SPVs
- NtP issuance / construction start (if any post June 2026)
