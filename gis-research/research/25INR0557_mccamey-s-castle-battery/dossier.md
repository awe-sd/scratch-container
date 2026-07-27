# Dossier — McCamey's Castle Battery (25INR0557)

Researched 2026-07-19 · site ~31.137, -102.203 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed 2025-03-20 ([GIS source](sources/2026-07-01_ercot-gis-report_25inr0557.json)); constructionStart reported 2026-05-28; imagery inconclusive
- Construction: **pre-construction or very early**, no BESS container rows confirmed ([triage chip](imagery/s2_31.13_-102.19_2026-06-01.png))
- Site: ~31.137, -102.203 — POI proximity to McCamey AEP 138kV substation (OSM Overpass 2026-07-19), confidence low-medium ([map](https://google.com/maps/@31.137,-102.203,5000m/data=!3m1!1e3))
- COD: reported 2028-03-30 → independent **2028-Q2 to 2029-Q1**, drift risk **high** (2 prior slips, FIS not approved, brief inActiveDate anomaly)

## 2. Site identification

- Derivation: Bus 76597 "Robbins Switch 138kV" not in OSM or any public registry; nearest confirmed 138kV AEP facility is McCamey Substation (31.1372, -102.2033; OSM way data, Overpass query 2026-07-19). Site within ~2km of that point.
- **Stated project area: unknown** — IA not retrieved (PUCT 402); CAD 0 hits; no abatement found
- Cross-checks: triage chip at 31.13, -102.19 shows large graded pad upper-center, consistent with industrial prep; no BESS-specific confirmation
- Not obtainable: exact bus 76597 coordinates (CEII / not public); IA POI schedule exhibit (PUCT blocked); CDSE imagery (auth failure)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Castle Storage, LLC | SPV / interconnecting entity | [GIS report](sources/2026-07-01_ercot-gis-report_25inr0557.json) |
| Unknown parent | developer/owner | no TX SOS, SEC, press, or LinkedIn match found |

- Financing: unknown — no Form D, PPA announcement, or debt filing found; LLC has no public footprint

## 4. Land & county records

- Tenure: **unknown** — 0 CAD parcel hits for Castle Storage or McCamey Castle (Upton CAD, 2025 tax year); IA not retrieved
- Abatements/agreements: none found (Ch.313 sunset 2022; JETI: no application found; ISD: not found)
- CAD: 0 hits — BESS typically needs 40-80 acres, which would appear in CAD once a lease/easement is filed; absence may simply reflect early stage

## 5. Interconnection & contractual schedule

- POI per ERCOT GIS: "76597 Robbins Switch 138 kV" ([GIS source](sources/2026-07-01_ercot-gis-report_25inr0557.json)) — bus 76597 not in public substation registries; AEP operates 138kV infrastructure near McCamey
- Equipment: unknown (IA not retrieved)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2025-03-20 | unknown (PUCT 402-blocked; PDF not retrieved) |

| Milestone | ERCOT GIS (latest) |
|---|---|
| IA Signed | 2025-03-20 |
| FIS Approved | not yet |
| Meets all 6.9 | not yet |
| Construction Start (reported) | 2026-05-28 |
| Construction End (reported) | 2027-03-31 |
| Projected COD | 2028-03-30 |

- Queue-history COD drift (from [timeline.md](timeline.md)): 2 changes over 33 snapshots; 2025-12-15 → 2027-03-31 → 2028-03-30 (+27 months total)
- **Notable anomaly**: inActiveDate briefly appeared in the 2025-11-01 snapshot (timestamp 2025-11-18 10:42:15), then cleared by 2025-12-01 — suggests a data correction or brief project status wobble

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-06-01 | Large pale graded rectangular pad visible ~upper-center; no BESS container rows; inconclusive | [png](imagery/s2_31.13_-102.19_2026-06-01.png) |

- Verdict: **inconclusive** — single chip at approximate location; CDSE auth failed preventing grid scan of confirmed POI coordinates; cannot distinguish site prep from existing oil/gas industrial pad at 10m/px

## 7. COD assessment

- IA signed March 2025 establishes project is real; constructionStart date of 2026-05-28 is "declared" in ERCOT data, not independently verified
- FIS still not approved and meetsAllSection69 not met — these are real risks; interconnection studies incomplete could force schedule revision
- Two prior COD slips (+2.25 years) in 33 months; pattern suggests developer overestimates pace
- Reported constructionEnd 2027-03-31 vs projected COD 2028-03-30 = 12-month buffer already built in by developer
- Castle Storage LLC has no public financing or EPC announcements — unknown capital depth
- inActiveDate briefly set 2025-11-18 may indicate a near-withdrawal or administrative issue; cleared quickly
- BESS is fast to build once funded (~12-18 months); bare ground today could still make a late-2028 COD
- **Independent estimate: 2028-Q2 to 2029-Q1** — baseline from ~12-month build starting H2-2026 (allowing for study completion), risk-skewed later given FIS and milestone lags; call **2028-Q4** as point estimate

## 8. Could not determine

- Castle Storage LLC parent company / backers / capitalization (TX SOS fee-gated; SEC 403-blocked; no press)
- Signed IA schedule exhibits and financial security amount (PUCT 402-blocked consistently)
- Exact Robbins Switch 138kV substation coordinates (not in OSM, not public)
- Project area in acres (IA not retrieved; no CAD parcel; no abatement)
- Active construction confirmation (CDSE auth failure; no Google imagery access)
- PPA status
