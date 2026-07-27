# Triage log — Dundee East A Wind (27INR0005)

T1 start

## T1 — Queue history
- 43 snapshots: 2022-12-01 → 2026-06-01
- COD drift: 1 change — 2027-07-31 (held 2022-12 → 2025-09) → 2027-12-31 (2025-10 → current)
- Capacity drift: 307.23 MW → 523.73 MW → 524.0 MW (Oct 2025 upsize, +70%)
- Milestones achieved: Screening started 2023-01-03, Screening complete 2023-03-30, FIS requested 2022-12-22, IA signed 2025-02-21, Meets 6.9(1) 2025-04-03
- FIS approved: not achieved. Construction start/end, energization, sync, COD: not achieved
- Summary: IA is signed (Feb 2025), passed first 6.9 gate (Apr 2025). FIS still not approved — unusual. Major capacity upsize Oct 2025.

T2 start

## T2 — Delivery pins
- gmaps.py places: HTTP 429 on all 3 queries (rate-limited / quota exhausted). One retry attempted, still 429.
- No pins found.
- NEGATIVE: no delivery pins.

T3 start

## T3 — Web sweep
- No press releases, news, or official developer pages found for "Dundee East A Wind" or "Dundee East A Wind LLC".
- Sibling project "Dundee East B Wind" (27INR0011, 261 MW) lists developer as **Felix 2, LLC** (from ercotqueue.com / infrasure.ai).
- "Felix 2, LLC" / "Felix Energy" search returned no results — name likely an SPV; parent unknown.
- Queue aggregator pages confirm 524 MW, Baylor County, 2027 COD — these are derived from ERCOT GIS, not independent reporting.
- Withdrawn placeholder 27INR0598 (523.73 MW) is the old-capacity slot that was superseded after the Oct 2025 upsize.
- No pages saved to sources/ (no direct-project content beyond queue aggregators).
- Developer inference: likely same developer as Dundee East B (Felix 2, LLC or its parent). Not confirmed for project A.

T4 start

## T4 — PUCT Interchange
- PUCT Interchange portal (interchange.puc.texas.gov) returned HTTP 402 on all direct URL attempts. One retry attempted — same result. Portal blocked; cannot enumerate filings.
- DDG search for PUCT docket numbers found none — only queue aggregator data.
- NOTE: IA is confirmed signed (2025-02-21) in queue data; IA PDF likely exists in PUCT but inaccessible this run.
- NEGATIVE: No IA PDF retrieved. Deep scan should attempt PUCT with a session-capable browser or alternative access method.

T5 start

## T5 — Abatements
- TX Comptroller Ch.313 search page not directly queryable via WebFetch (returns overview, not search results).
- DDG search: no Ch.313 or JETI filings found for Baylor County wind or "Dundee East".
- Post-2022 projects use JETI rather than Ch.313; JETI registry not accessible via DDG.
- NEGATIVE: No abatement found. Normal for a project with 2022+ queue entry (pre-JETI Ch.313 expired).
- Side note from T5 search: one source referred to developer as Felix 2, LLC for Dundee East A (also labeled "Dundee South A Wind" in that aggregator) — developer attribution for project A more likely confirmed.

T6 start

## T6 — Imagery
- Site candidate: Riley Substation (345 kV, AEP) at ~34.085°N, -99.145°W in Wilbarger County (adjacent to Baylor County).  
  Method: POI substation coordinates from DDG/Mapcarta. Confidence: medium (substation known, wind array extent unknown).
- cdse.py chip: HTTP 401 Unauthorized on all 9 calls — CDSE credentials missing or expired in ~/.config/gis-research.env.
- One retry was implicit (all 9 jobs failed the same way). No imagery obtained.
- NEGATIVE: No satellite chips produced. No construction assessment possible.

T7 start

## T7 — Final outputs
- triage_findings.json written
- triage.md written (10 lines)
- Turns used: ~28
- Tool blocks encountered: gmaps 429 (T2), PUCT 402 (T4), CDSE 401 (T6)
- All three tool failures logged as negative per rules; no re-engineering attempted.
- STOP.

## Deep scan start — 2026-07-19

### D1 — AES Corp developer confirmation
- AES Corp Exhibit 21.1 (10-K FY2024, filed 2025-04-11, accession 0000874761-25-000029): lists Felix 1, LLC; Felix 2, LLC; Felix 3, LLC; Felix DevCo Holdings, LLC; Felix DevCo, LLC — all Delaware subsidiaries
- Also present in AES 10-K FY2025 (filed 2026-03-02, accession 0000874761-26-000063) Exhibit 21.1
- Dundee East A Wind not separately listed (expected: development-stage project, held under Felix DevCo)
- STRONG INFERENCE: AES Corp is developer/owner of Dundee East A Wind via Felix DevCo chain
- Artifact: AES Exhibit 21.1 URL https://www.sec.gov/Archives/edgar/data/874761/000087476125000029/aes1231202410-kaexhibit211.htm
- No Dundee East directly named in EDGAR filings as of 2026-07-19 (0 hits)

### D2 — Initial imagery (Riley Substation POI, 34.085°N -99.145°W)
- s2_2026-06-15.png: 6 km buffer chip, 2026-06-15
- OBSERVATION: Large industrial complex with evaporation ponds visible (left/west side of frame) — likely oil/gas facility, NOT wind construction
- OBSERVATION: Large graded rectangular pad (lower center-right) — fresh tan soil, geometric edges, apparent structures/equipment — possible substation construction or industrial facility
- NO turbine pads or wind access road strings visible in this chip
- CRITICAL: Riley Substation is adjacent to industrial area; the graded rectangle may be unrelated (oil field)
- Next: grid search further into Baylor County (east/SE of this location) to find turbine pad strings

### D3 — ERCOT parquet data: InterconnectingFacility confirmed
- `interconnectingFacility` = "Felix 2, LLC" for ALL 43 snapshots (2022-12 to 2026-06)
- `financialSecurityAndNoticeToProceedProvided` = "Yes" first seen 2025-09-01 snapshot → continues through 2026-06-01
- Name changed: "Dundee South A Wind" → "Dundee East A Wind" in Oct 2025 (same time as MW upsize 307→523.73)
- Both sibling projects (27INR0005 A and 27INR0011 B) list `interconnectingFacility = Felix 2, LLC`, same COD 2027-12-31, same IA signing date 2025-02-21
- Financial security YES = notice to proceed given. Very strong commitment signal.

### D4 — AES Corp parent chain
- AES Corp (NYSE: AES, CIK 0000874761) Exhibit 21.1 (10-K FY2024, filed 2025-04-11) lists:
  "Felix 1, LLC (Delaware), Felix 2, LLC (Delaware), Felix 3, LLC (Delaware), Felix DevCo Holdings, LLC (Delaware), Felix DevCo, LLC (Delaware)"
- CONFIRMED: Felix 2, LLC is an AES Corp subsidiary (Delaware)
- Ownership chain: Felix 2, LLC → [Felix DevCo Holdings, LLC?] → AES Corp
- AES 10-K FY2025 note: Felix DevCo, LLC was originally a JV with Air Products for green hydrogen in TX; AES acquired 100% in Nov 2024 for $34M. This is DIFFERENT from Felix 2, LLC (the wind project SPV).
- Same name family (Felix 1/2/3 and Felix DevCo are all AES subsidiaries) — Felix 2, LLC is the interconnecting entity/SPV for Dundee East A Wind
- NEGATIVE: Dundee East A Wind not mentioned by name in AES 10-K FY2025 body text (expected — development stage project not material enough for disclosure)
- Artifact: sources/2025-04-11_AES_10K_EX211_felix_entities.txt, sources/2026-03-02_AES_10K_felix_acquisition_note.txt

### D5 — Imagery assessment (grid search)
- Original 6km chip at 34.085°N -99.145°W (2026-06-15): Large graded rectangle visible (lower-center-right of frame) — further examination showed this is near oil/gas infrastructure at Riley Substation area
- 3x3 grid across Baylor County (33.50-33.80°N, -99.10 to -99.30°W): All farmland/brush, oil/gas well pads (circular with dirt road spokes), NO wind turbine construction
- 5 chips in eastern Baylor/western Archer County (33.55-33.75°N, -98.90 to -99.00°W): No wind activity
- CDSE rate-limited: >50% of chip requests failed with 401/403 after initial successful batch
- Assessment: NO wind turbine pads or access road strings visible in any of the chips examined
- The graded rectangle SE of Riley Substation is more likely an oil/gas processing facility or new substation construction — cannot definitively attribute to Dundee East wind
- NEGATIVE: No wind construction visible as of June 2026 chips
- Site candidate: Riley Substation (34.085°N, -99.145°W) confirmed as POI; turbine array extent unknown

### D6 — Focused imagery (graded facility identification)
- 3km chip at 34.055°N, -99.125°W (2026-06-15): CONFIRMED large graded rectangular facility in upper-left corner of frame (approx 34.065-34.075°N, -99.135 to -99.150°W)
- The facility has multiple geometric cleared areas with fresh soil/gravel - this is the Riley Substation area (345 kV AEP)
- This is NOT a wind turbine pad cluster — it appears to be an existing substation and/or new gen-tie substation construction activity
- 1.5km tight chip at 34.03°N, -99.08°W: Oil/gas well pads with spoke road networks — NOT wind construction
- 3km chip at 34.05°N, -99.09°W: Shows cleared circular/oval area (oil/gas well pad) in lower-center
- IMAGERY VERDICT: No wind turbine pads confirmed visible in the June 2026 chips across the Baylor County search area
- However, wind turbines span 10-20km from POI; my search grid may not cover the full project area in Baylor County
- CDSE rate-limited (403 quota) after ~15 successful chips — cannot extend grid further this session
- Based on ground-level evidence available: construction stage = NO CONSTRUCTION VISIBLE
- Confidence: medium-low (grid only covers ~60% of likely turbine placement area)

### D7 — Key site coordinates (best estimate)
- Riley Substation POI: ~34.085°N, -99.145°W (from OpenInfraMap/DDG for Wilbarger County)
- Turbine placement area (Baylor County, Baylor Co seats Seymour ~33.594°N -99.260°W): likely spans 33.5-33.9°N
- The project is listed as Baylor County (not Wilbarger), suggesting the wind array is in Baylor Co proper, south/SE of Riley Substation
- Best site estimate: 33.7°N, -99.2°W (Baylor County centroid, NOT a parcel-derived coordinate)
- LIMIT: Cannot confirm with a parcel/POI/delivery-pin derived coordinate; this is a county-level estimate only
