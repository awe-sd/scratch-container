# Triage log — Concho Pearl Solar (25INR0174)

T1 start

## T1 — queue history
- 43 snapshots (2022-12-01 → 2026-06-01)
- Milestones: Screening started 2022-12-07, Screening complete 2023-03-06, FIS requested 2022-11-30
- **IA signed: 2024-07-22** (notable: IA without FIS approved)
- FIS approved: NOT achieved
- Construction milestones: none
- COD drift (3 changes): 2025-07-01 → 2026-07-01 → 2027-10-14 → 2028-01-09 (~2.5 yr total slip)
- Capacity settled at 171.9 MW (from initial 174.2)

T2 start

## T2 — delivery pins
- gmaps.py returned HTTP 429 (rate-limited) on first and second attempt
- Per budget rules: 1 retry used, result negative. No pins obtained via gmaps.py.
- No coordinates from this step.

T3 start

## T3 — web sweep
- Developer confirmed: Concord New Energy Group (0182.HK), wholly-owned subsidiary Concho Pearl Solar, LLC
- SPV incorporated TX 07/22/2022; registered address 107 Spring St, Seattle WA 98104
- **EPC signed 2026-01-14** with The Ryan Company, Inc., ~$156M; completion target Oct 2027
- Project specs: 172 MW AC solar + 432 MWh BESS
- Tax abatement public hearing: Concho County Commissioners Court, 2025-11-13 (Ch. 312)
- Road use agreement also referenced — active local coordination
- EIA record: 334.3 MW combined facility
- news_found: YES; developer_name: Concord New Energy Group
- Saved: sources/web_sweep_summary.md

T4 start

## T4 — PUCT Interchange
- PUCT Interchange portal returned HTTP 402 (blocked) on all direct URL attempts
- DDG search found: **PUCT Control Number 35077, Item 1888**
  - "ERCOT Standard Generation Interconnection Agreement between LCRA Transmission Services Corporation and Concho Pearl Solar, LLC"
  - 2 documents filed; submitted pursuant to Substantive Rule 25.195(e)
- Also surfaced: Concho Pearl **Storage** (25INR0175, 162.4 MW) shares same POI and IA date (2024-07-22) — linked project
- Proposed completion (per IA context): Oct 13-14, 2027
- PDF download blocked (402). ia_found: YES, content extracted: NO
- Deep-scan note: IA exists at 35077/1888 — retry with authenticated session or check ERCOT GIS portal

T5 start

## T5 — abatements
- Ch.313 expired end of 2022 — not applicable for this post-2022 project
- **Ch.312 county-level abatement public hearing: Concho County Commissioners Court, 2025-11-13** (found in T3)
  - Proposed abatement under Texas Tax Code Ch.312; road use agreement also noted
- JETI registry: no results found for Concho Pearl Solar
- TX Comptroller Ch.313 database: no records (expected — project entered queue 2022, program already expired)
- abatement_found: YES (Ch.312 hearing confirmed, PDF not retrieved during triage)

T6 start

## T6 — imagery
- Site candidate: Amos Creek substation area, Concho County, near Paint Rock TX
  - Coords: 31.5174, -99.8065 (method: POI infrastructure lookup, confidence: medium)
- 3×3 grid attempted (9 chips, lat ±0.03°, buffer-km 2, date 2026-07-01)
- CDSE returned HTTP 401 Unauthorized on all 9 calls (creds not loaded / expired in this env)
- Imagery: NOT obtained
- construction_visible: UNKNOWN
- Deep-scan note: retry imagery with valid CDSE creds; POI-based coords are medium-confidence

T7 start

## T7 — write and stop
- Written: triage_findings.json, triage.md, sources/web_sweep_summary.md
- Turns used: ~25
- deep_scan_recommended: YES
