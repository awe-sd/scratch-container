# Dossier — Hastings Park BESS (26INR0551)

Researched 2026-07-19 · site 29.48324, -95.25257 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed with TNMP ([PUCT 35077/2222](#5-interconnection--contractual-schedule), 2025-08-14); substation confirmed via OSM; but no financial security / NTP as of Jun 2026 and no construction visible in any imagery frame
- Construction: **no_activity**, first activity date unknown ([Dec 2025 frame](imagery/key/s2_2025-12-01.png))
- Site: 29.48324, -95.25257 — OSM polygon centroid for TNMP Hastings Substation, high confidence ([satellite view](https://www.google.com/maps/@29.48324,-95.25257,5000m/data=!3m1!1e3))
- COD: reported 2027-09-15 → independent **2028-Q3**, drift risk **high** (no NTP 10 mo post-IA; 12-18 mo BESS build still ahead)

## 2. Site identification

- Derivation: OSM way 338758521 — TNMP Hastings Substation, 5-node polygon centroid ([OSM](https://www.openstreetmap.org/way/338758521))
- **Stated project area: not obtainable** — no CAD parcel, no IA exhibit, no abatement application retrieved; imagery footprint unverified (no construction yet)
- Cross-checks:
  - OSM tags: `name=Hastings Substation`, `operator=Texas-New Mexico Power`, `voltage=138000;12500` — matches queue POI "39010 138kV HASTINGS" exactly
  - Triage Mapcarta estimate (29.48325, -95.253) agrees within 50 m
  - [Tight 500m chip](imagery/key/s2_2026-04-01_tight.png) shows substation compound at expected position
- Not obtainable: street address of substation (TNMP portal 404); exact BESS siting within yard (pre-construction)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Brazos Roots BESS, LLC | SPV / developer | PUCT 35077/2222 party (DDG-confirmed); TX foreign LLC reg. 2025-01-01, Tax ID 32099702915 |
| Unknown parent | parent company | No press releases, LinkedIn, SEC filings, or corporate registry data found — all portals CAPTCHA/auth-blocked |
| Unknown | EPC | None identified |
| Unknown | PPA offtaker | None identified |

- Financing: no financing announcement found; no project equity or debt closing

## 4. Land & county records

- Tenure: **unknown** — likely utility-owned or leased land adjacent to TNMP Hastings substation; no CAD parcels found under any project/developer name
- Abatements: none found; Ch.313 expired 2022; JETI portal not queryable; absence normal for compact BESS at utility yard
- CAD: 0 parcels — Brazoria CAD portal JavaScript-driven, direct search URLs return 404; expected for BESS on utility land

## 5. Interconnection & contractual schedule

- POI per PUCT filing: TNMP "39010 138kV HASTINGS" substation, Brazoria County (queue data); IA content NOT retrieved (PUCT Interchange returns 402 on all document URL patterns)
- Equipment: unknown (IA exhibits not accessed)

| IA document | Signed | Financial security posted |
|---|---|---|
| SGIA (PUCT 35077/2222) ([filing confirmed](https://html.duckduckgo.com/html/?q=%22Brazos+Roots+BESS%22+interconnection+TNMP)) | 2025-08-13 | **None** as of 2026-06-01 |

| Milestone | Queue data | IA exhibit |
|---|---|---|
| IA signed | 2025-08-13 | not retrieved |
| Financial security / NTP | **No** (as of Jun 2026) | not retrieved |
| Scheduled COD (reported) | 2027-09-15 | not retrieved |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2026-12-31 → 2027-09-15 (~9 months slip)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-12 | Undisturbed scrubland adjacent to TNMP substation; no pad/containers | [png](imagery/key/s2_2025-12-01.png) |
| 2026-04 | Same scene — no change, no clearing or grading visible | [png](imagery/key/s2_2026-04-01.png) |
| 2026-04 tight | 500m chip: substation compound only; undeveloped land on all sides | [png](imagery/key/s2_2026-04-01_tight.png) |
| 2026-07 | Partial cloud cover; consistent with prior frames where clear | [xwide](imagery/s2_2026-07-01_xwide.png) |

- Verdict: **no_activity** — all frames undisturbed; no BESS gravel pad or container rows at any date through Apr 2026

## 7. COD assessment

- Reported 2027-09-15 is **not contractually grounded** — IA content not retrieved; no schedule exhibit accessed
- **Critical blocker:** `financialSecurityAndNoticeToProceedProvided = No` in Jun 2026 queue data — 10 months post-IA signing with no NTP is a hard delay signal
- BESS build cadence: 12-18 months from NTP; optimistic NTP in Q3 2026 → COD Q3 2027–Q1 2028; more realistic NTP in Q4 2026–Q1 2027 → COD **2028-Q3** or later
- No developer PR, no EPC, no PPA, no financing announcement — zero market-facing commitment signals
- One prior slip (9 months) already on record; project has never passed financial close
- **Independent estimate: 2028-Q3, drift risk high**

## 8. Could not determine

- IA content, milestone exhibit dates, financial security amount (PUCT Interchange 402-blocked throughout)
- Parent company / investor behind Brazos Roots BESS LLC (all corporate portals CAPTCHA/auth-blocked)
- EPC contractor and PPA offtaker (no press coverage found)
- Exact project acreage (no IA exhibits, no CAD parcels, no abatement application)
- Whether NTP has been issued after June 2026 (most recent queue snapshot)
