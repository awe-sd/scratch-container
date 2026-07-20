# Triage log — Danish Fields Solar (20INR0069)

T1 start

## T1 — queue history

Result: 95 monthly snapshots (2018-08-01 → 2026-06-01). Script succeeded.

Key findings:
- **IA signed**: 2020-02-24 (pre-dates FIS approval — unusual order)
- **FIS approved**: 2022-07-25
- **Meets all 6.9**: 2022-07-28
- **Approved for energization**: 2023-03-27
- **Approved for synchronization**: 2023-05-04
- **Construction start/end**: NOT REPORTED
- **Commercial operation approved**: NOT ACHIEVED
- **COD drift count**: 19 changes over 6+ years (2021-02-01 → 2026-08-29); currently 2026-08-29
- **Capacity**: 200 MW (2018) → 201 MW → 619.1 MW (2022) → 602.8 MW (current)

RED FLAG: Approved for energization AND synchronization in 2023 (≈online indicators) but no construction start/end reported and no commercial operation after 3+ years. COD 2026-08-29 is ~6 weeks out from today. Extreme COD drift (19 changes).

T2 start

## T2 — delivery pins

Result: NEGATIVE — Google Maps Places API returning 429 Too Many Requests on all queries (tried: "Danish Fields Solar", "Danish Fields Solar Wharton County Texas", "Danish Fields Solar LLC Texas"). One retry per query, all failed. No pins found.

T3 start

## T3 — web sweep

Result: NEGATIVE — DDG blocked by CAPTCHA (both queries). Bing returns no results for "Danish Fields Solar" OR "Danish Fields Solar LLC" OR "Danish Fields" solar Wharton — all queries return Danish-language/culture results, no project hits. TX Comptroller COA search redirected (requires interactive session). No developer name surfaced. No sources saved.

T4 start

## T4 — PUCT Interchange

SKIPPED — budget at 80%+ warning received mid-T3; skipping T4 and T5 to preserve budget for T7 output. Not attempted.

T5 start

## T5 — abatements

SKIPPED — budget constraint (same reason as T4).

T6 start

## T6 — imagery

SKIPPED — no site candidate pin available (gmaps 429, no web results). Without a coordinate better than "somewhere in Wharton County", checklist rules say SKIP.

T7 start

## T7 — output

triage_findings.json + triage.md written. Turns used: ~22. Budget warning hit at T3; T4/T5/T6 skipped to preserve T7 budget. Deep scan recommended.

---
## Deep Scan — 2026-07-19

### Stage 1 — LLC → parent chain

**PUCT Interchange search** (2026-07-19) — found 9 filings under "Danish Fields" including:
- Control 54647: Danish Fields Solar, LLC — PGC Registration application (2023-02-13)
- Control 57632: Danish Fields Solar, LLC — PGC Amendment (2025-01-31)
- Control 51568: CenterPoint Energy Houston Electric CCN for 345kV line in Wharton County (Danish Fields intervened)
- Control 55835/57630: Danish Fields Storage, LLC (companion battery)

**PGC Registration (54647-1)** confirms full parent chain:
- Danish Fields Solar, LLC → TotalEnergies DF Solar, LLC → TotalEnergies Renewables USA, LLC → TotalEnergies Delaware, Inc. → TotalEnergies Holdings USA, Inc. → TotalEnergies Gestion USA, SARL → **TotalEnergies SE** (100% ownership)
- Physical site: **11000 County Road 403, El Campo, TX 77437, Wharton and Matagorda County**
- TSP: CenterPoint Energy Houston Electric, LLC
- Contact: Nicolas Felix, Director of Operations, TotalEnergies, nicolas.felix@totalenergies.com
- Attorney: Todd Kimbrough, Balch & Bingham LLP, Austin TX
- Filed 2023-02-13; artifact: sources/2026-07-19_puct_54647-1_danish-fields-solar-pgc-registration.pdf

**PGC Amendment (57632-1)** (2025-01-31) adds new parent chain for tax equity:
- Danish Fields TE Partnership, LLC → AP Tosca Borrower, LLC → Tosca Holdco, LLC → Tosca Pledgor, LLC
- "AP" likely Ares Partners (tax equity partner); confirms financing structure in place
- Artifact: sources/2026-07-19_puct_57632-1_danish-fields-solar-pgc-amendment.pdf

**Original developer: SunChase Power LLC** (cofounded by David Groberg) developed the project through subsidiary Brazos Renewable Energy, LLC. TotalEnergies acquired Danish Fields in **2021** as part of 2.2 GW Texas portfolio purchased from SunChase Power.

### Stage 2 — County records

**PUCT 51568 Direct Testimony (item 50)** by David Groberg (SunChase/Total) filed 2021-05-03:
- Site: **5,000-acre solar farm in Wharton County** (stated explicitly)
- IA security: **$6,600,000 posted with CenterPoint** for Hillje Substation interconnect
- Standard interconnection agreement executed with CenterPoint
- **Property tax abatement agreement obtained** (ISD/county unnamed in testimony)
- Land: easements and exclusive purchase options secured; mineral accommodation agreements from 40+ mineral owners
- Artifact: sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf

**PUCT 51568 item 115**: Danish Fields Solar filed "Notice of Memorandum of Lease" 2021-10-25 — confirms **land is LEASED**, not purchased.

**TX CAD**: WCAD search not resolved (Williamson CAD returned instead of Wharton). Wharton CAD URL not found via direct fetch; CAD search for parcels not completed.

**TX Comptroller Ch.313**: Direct testimony mentions abatement obtained; specific ISD not named. Ch.313 database search returned no direct results (website non-responsive to structured queries). NEGATIVE: no abatement documents retrieved.

### Stage 3 — Site pinpoint

**Physical address confirmed**: 11000 County Road 403, El Campo, TX 77437 (Wharton and Matagorda Counties) — from PUCT PGC registration.
- Nominatim geocode of CR 403 / Wharton County: ~29.129, -96.243
- Hillje TX (POI community): 29.1489, -96.3433
- Initial S2 chip at 29.129, -96.243 (2026-06-15) shows **solar array visible in lower-left quadrant** of 6km frame
- Tighter chip at 29.110, -96.278 (2026-06-15) confirms **clear solar panel arrays** in upper-right, consistent with site
- Provisional site centroid: **29.126, -96.262** (imagery-derived, cross-check with address)
- Cross-check: CR 403 runs N-S through Wharton County south of El Campo; 5,000-acre site at ~29.12N, 96.26W is consistent

### Stage 4 — Satellite ground truth

**S2 chip 2026-06-15 (6km, CR403 center)**: clear solar installation visible; dark rectangular module blocks; partially cloudy frame. Confirms operating solar farm in range.

**S2 chip 2026-06-15 (tight 2km, 29.110/-96.278)**: solar panel arrays clearly visible in upper-right; active solar farm.

**S2 chip 2025-10-01 (3km, 29.126/-96.262)**: DECISIVE FRAME — multiple array sections with uniform dark panel blocks visible center-frame; substantial substation-like bright pad in center. At 10 m/px clearly shows an operating solar installation. Construction complete or substantially complete by Oct 2025.

**TotalEnergies Press Release (2024-09-30)**: "TotalEnergies has started commercial operations of Danish Fields and Cottonwood, two utility-scale solar farms with integrated battery storage located in southeast Texas... Danish Fields: 720 MWp, 1.4 million PV panels, 225 MWh battery storage, COD 2024-09-30."
- Offtake: 70% via long-term CPPAs (Saint-Gobain + others); 30% self-supply for TotalEnergies Gulf Coast industrial plants
- Battery: 225 MWh (Saft, TotalEnergies subsidiary)
- Artifact: sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html

**Key anomaly**: ERCOT queue (20INR0069) still shows `approvedForCommercialOperation = null` with COD 2026-08-29 in June 2026 snapshots. Project is physically operating since 2024-09-30. Queue entry may reflect administrative closure pending (or battery storage add-on 20INR0069 component).

Timelapse (2023-01 to 2026-07, monthly) job running — not yet complete at time of dossier write.

**Verdict: OPERATING** — plant commercially operational since 2024-09-30; imagery confirms solar arrays in place.
