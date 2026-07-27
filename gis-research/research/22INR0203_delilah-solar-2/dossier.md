# Dossier — Delilah Solar 2 (22INR0203)

Researched 2026-07-19 · site **not pinned** (see §8) · verdict **real_active**

## 1. Verdict

- **real_active** — ERCOT approved for synchronization 2025-01-13 ([timeline](timeline.md)); physical plant built and energized; awaiting commercial operation approval only
- Construction: **substantially_complete**, first activity date not determined (no imagery obtained)
- Site: lat/lon **not determined** — gmaps.py rate-limited (429), Lamar CAD search failed, PUCT IA not retrieved; county: Lamar TX, ~140 mi NE Dallas
- COD: reported 2026-09-30 → independent **2026-Q4**, drift risk **high** (11 prior slips; sync'd 18 months ago, still not COD'd)

## 2. Site identification

- Derivation: **not determined** — Google Places delivery-pin search returned HTTP 429 (rate-limited); Lamar CAD esearch returned 404 for "delilah solar" and "invenergy" owner searches; PUCT interchange returned 402
- **Stated project area:** unknown — no IA, no CAD parcels, no abatement docs retrieved
- POI "345 kV TTRSW 11688" not resolved to coordinates (CEII / not publicly mapped)
- Not obtainable this session: site lat/lon, exact parcel IDs, acreage

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Delilah Solar 2, LLC | SPV | ERCOT queue party; IA signed 2020-12-22 ([timeline](timeline.md)) |
| Invenergy LLC | developer/owner | [WEC PR Delilah I](sources/2026-07-19_prnewswire_wec-delilah-i-acquisition.html) — Invenergy developer of sibling Delilah I + same 5-phase portfolio |
| WEC Energy Group / WEC Infrastructure | likely investor (unconfirmed for Delilah 2) | [WEC PR Delilah I](sources/2026-07-19_prnewswire_wec-delilah-i-acquisition.html): 90% stake in Delilah I; no public announcement for Delilah 2 |
| offtaker | unknown | Delilah I: Honda 200 MW + Tesla 100 MW VPPAs; Samson I: AT&T — no offtaker announced for Delilah 2 |

- Financing: unknown for Delilah 2; Invenergy self-builds then sells down (confirmed for Delilah I and Samson I)

## 4. Land & county records

- Tenure: **unknown** — CAD owner search failed (404 at esearch.lamarcad.org); no parcel records found
- Abatements: Ch.313 agreements page did not list Lamar County solar entries; no JETI/Ch.312 records found
- CAD: 0 results (search portal error, not confirmed absence)

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "345 kV TTRSW 11688" — TSP not confirmed; likely Oncor (Lamar County is Oncor territory)
- PUCT interchange: returned HTTP 402 — no IA documents retrieved
- IA signed per queue: **2020-12-22** ([timeline](timeline.md))

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (not retrieved) | 2020-12-22 | unknown |

| Milestone | Queue record |
|---|---|
| IA signed | 2020-12-22 |
| Meets 6.9(1) | 2021-03-23 |
| Meets all 6.9 | 2022-08-12 |
| Approved for energization | 2024-10-29 |
| Approved for synchronization | **2025-01-13** |
| Commercial operation approved | not yet (as of 2026-06-01) |

- Queue-history COD drift ([timeline.md](timeline.md)): **11 changes**, 2022-12-31 → 2026-09-30; in reports since 2019-05 (86 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | No imagery obtained (site not pinned; gmaps rate-limited) | — |

- Verdict: **substantially_complete** inferred from milestone record (sync approved 2025-01); satellite stage unverified

## 7. COD assessment

- Approved for synchronization **2025-01-13** — strongest single indicator that the physical plant exists and is energized; this milestone cannot be obtained without a built plant
- 18+ months elapsed since sync approval with no commercial operation approved — suggests testing, interconnection punch-list, or commercial arrangements not yet closed
- 11 COD drifts across 7 years (2019→2026); chronic pattern of 6-12 month slips; reported 2026-09-30 is the 12th COD
- Sibling Delilah I (22INR0202) also experienced multi-year drift before reaching COD
- **No PUCT IA obtained** to verify contractual schedule or financial security; cannot confirm whether 2026-09-30 is the contractual date or just queue reporting
- **Independent estimate: 2026-Q4, drift risk high** — plant is built but COD completion has lagged sync by >18 months already; could slip to 2027-Q1

## 8. Could not determine

- Site lat/lon (gmaps.py rate-limited; Lamar CAD search portal returning 404; PUCT IA not retrieved)
- Project acreage (no abatement docs, no CAD parcels, no IA)
- PUCT IA documents (interchange returned HTTP 402)
- Financial security amounts
- EPC contractor (Invenergy self-builds per Delilah I pattern)
- PPA offtaker for Delilah 2
- WEC stake in Delilah 2 (not publicly announced as of 2026-07-19)
- TX Comptroller entity details for Delilah Solar 2, LLC (JS-rendered, no static fetch)
