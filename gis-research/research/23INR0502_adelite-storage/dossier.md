# Dossier — Adelite Storage (23INR0502)

Researched 2026-07-19 · site 30.6200, -97.2111 · verdict **real_early**

## 1. Verdict

- **real_early** — IA countersigned Aug 2024 by established developer (Acciona Energy USA); FIS approved May 2024; no construction milestones and no satellite activity at POI substation as of Jul 2026 ([contact sheet](imagery/contact_sheet_deep.png))
- Construction: **pre-construction (no_activity)**, first activity not yet observed
- Site: 30.6200, -97.2111 — Thorndale North Substation (Oncor 138kV, confirmed via [OSM Overpass](https://overpass-api.de/)), high confidence for POI; BESS pad location within ~1 km radius unresolved ([satellite view](https://www.google.com/maps/@30.6200,-97.2111,5000m/data=!3m1!1e3))
- COD: reported 2027-06-28 → independent **2027-Q4 to 2028-Q2**, drift risk **high** (no construction started, 11 months to reported COD, 5 prior slips totaling +3 yrs)

## 2. Site identification

- Derivation: POI description "Tap 138kV Thorndale North (bus #3659) – Rookie Switch (bus #3701)" + OSM Overpass query (bbox 30.5–30.75N, -97.35–-97.05W) confirmed Thorndale North Substation at 30.6200, -97.2111, operator Oncor, 138kV
- **Stated project area: unknown** — no IA exhibit, no abatement, no CAD parcel accessed; for 231 MW BESS expected 20–60 acres; imagery footprint: no pad visible yet
- Cross-checks: Thorndale village centroid (OSM node 151442177: 30.6139, -97.2061) matches substation location within 0.7 km; infrasure.ai confirms POI text verbatim; queue packet consistent
- Not obtainable: exact Rookie Switch coordinates (likely CEII); PUCT Interchange portal blocked (HTTP 402) — IA PDF not retrieved; precise BESS pad parcel

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Adelite Storage Project LLC | SPV | triage DDG search ([t3_web_sweep.md](sources/t3_web_sweep.md)); infrasure.ai |
| Acciona Energy USA Global, LLC | developer/owner | [infrasure.ai](https://infrasure.ai/plant/69004-adelite-storage-project-llc); triage DDG |
| (EPC) | EPC | not disclosed — no press release found |
| (offtaker/PPA) | offtaker | not disclosed |

- Financing: **not confirmed** — no FERC EQR wholesale contracts, no NTP or financial close press release found; Acciona is a well-capitalized developer (global IPP) but project-level financing not closed as of research date

## 4. Land & county records

- Tenure: **unknown** — Milam CAD portal (esearch.milamad.org) requires JavaScript; WebFetch returned no data. County clerk portal (milam.tx.publicsearch.us) same. 0 CAD hits for "Adelite" — expected for BESS (typically leased land, not purchased)
- Abatements/agreements: none found — JETI registry lists 11 agreements, none for Adelite/Acciona/Milam County ([JETI current agreements](https://comptroller.texas.gov/economy/development/prop-tax/jeti/current-agreements.php)); Ch.313 expired 2022; commissioners court minutes inaccessible
- CAD: 0 hits via WebFetch (portal requires JS); absence consistent with leased-land BESS

## 5. Interconnection & contractual schedule

- POI per IA: "Tap 138kV Thorndale North (bus #3659) – Rookie Switch (bus #3701)" — from queue identity packet; IA PDF not retrieved (PUCT Interchange HTTP 402 on all attempts)
- Equipment: not disclosed in any accessible source

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard Gen IA (PUCT Interchange, not retrieved) | 2024-08-27 | unknown — PDF inaccessible |

| Milestone | Queue report |
|---|---|
| IA signed | 2024-08-27 |
| Meets 6.9(1) | — (not achieved) |
| Meets all 6.9 | — (not achieved) |
| Construction start | — |
| Scheduled COD (reported) | 2027-06-28 |

- Queue-history COD drift ([timeline.md](timeline.md)): **5 changes** — 2024-06-01 → 2026-02-28 → 2026-06-30 → 2026-07-31 → 2027-04-15 → 2027-06-28; +3 years total slip since first report

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-07-01 | undisturbed farmland/pasture, full 3 km radius | [2025-07 3km](imagery/s2_2025-07-01_3km.png) |
| 2026-07-01 | unchanged — no pad, no grading, no containers | [2026-07 3km](imagery/s2_2026-07-01_3km.png) |
| 2026-07-01 | substation vicinity (0.5 km tight): undisturbed | [substation](imagery/s2_2026-07-01_substation.png) |

- Verdict: **no_activity** — identical land cover Jul 2025 vs Jul 2026; no BESS construction signature in any of 10 chips across 5 offset positions and two dates

## 7. COD assessment

- Reported COD 2027-06-28 is **~11 months** from research date (2026-07-19); a BESS build requires ~12–18 months from groundbreaking
- **No construction activity visible** in Jul 2026 imagery → to meet reported COD, NTP and mobilization must begin within weeks of research date
- COD drift history is extreme: 5 changes totaling +3 years; project has been in queue since 2022 without any construction milestones; Meets-6.9 criteria not yet achieved
- For: IA signed (Aug 2024), FIS approved (May 2024), Acciona is established developer with track record, 86% build-probability rating (ercotqueue.com, noted but banned source — not primary evidence)
- Against: no financing close, no EPC named, no NTP found, no construction begun, COD date structurally impossible without immediate start
- **Independent estimate: 2027-Q4 to 2028-Q2, drift risk HIGH** — the reported 2027-06-28 COD is not achievable from current pre-construction state without extraordinary pace; a slip to H2 2027 or early 2028 is the base case

## 8. Could not determine

- Exact BESS pad parcel/location within Thorndale North substation vicinity
- IA schedule exhibit and financial security amounts (PUCT Interchange blocked)
- EPC contractor identity
- PPA offtaker or financing close status
- Milam CAD parcel IDs or land tenure (portal requires JS)
- Rookie Switch exact coordinates (likely CEII-redacted)
