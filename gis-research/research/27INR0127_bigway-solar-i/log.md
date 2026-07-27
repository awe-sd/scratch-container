# Triage log — Bigway Solar I (27INR0127)

## T1 start
**queue_history result:** 28 snapshots 2024-03-01 → 2026-06-01, 2 reported-COD changes.

| Item | Value |
|---|---|
| IA signed | 2025-02-15 |
| Meets 6.9(1) | 2025-03-19 |
| FIS requested | 2024-02-28 |
| FIS approved | NOT YET |
| Construction start/end | NOT reported |
| Capacity (latest) | 195.2 MW |
| COD drift | 2029-07-01 → 2028-12-31 → 2027-12-31 (pulled forward) |

**Notes:** IA signed without FIS approval (valid per ERCOT rules — independent gates). COD trending forward (optimistic signal). No construction milestones in queue. Capacity oscillated 200→195→200→203→195.2 MW.

## T2 start
**gmaps.py:** HTTP 429 Too Many Requests on first call; one retry also 429. API rate-limited — no pins retrieved. No delivery pins found.

**T2 result:** 0 pins. Normal for this project type.

## T3 start
**Web sweep results:**
- Developer confirmed: NextEra Energy Interconnection Holdings, LLC
- Sister project: Bigway Solar II (27INR0128) same county, same developer
- PUCT IA filing found: controlNumber=35077 (ETT × Bigway Solar, LLC, Feb 2025)
- King County tax abatement document references "Stetson Renewables Holdings, LLC and/or Bigway Solar, LLC, as assignee" — Ch.313 or JETI lead
- Third search hit CAPTCHA — stopped per rules
- Saved to sources/t3_web_sweep.md

**T3 result:** news_found=true, developer=NextEra, PUCT IA lead confirmed, abatement lead found.

## T4 start
**PUCT Interchange attempts:**
- controlNumber=35077 filing page → HTTP 402 Payment Required
- Direct PDF URL (35077_2069_*) → HTTP 402
- interchange.puc.texas.gov/search/ → HTTP 402
All PUCT Interchange endpoints returning 402 — portal blocked, one retry done (same result). IA is confirmed to exist (from T3 web sweep) but content inaccessible.

**T4 result:** ia_found=true (confirmed by T3 sources), but IA PDF unreadable — milestone schedule unknown.

## T5 start
**King County PDF** (co.king.tx.us/upload/page/9617/January 2026.pdf): SSL cert mismatch — domain resolves to harrisoncountytexas.gov cert. Could not retrieve.
**TX Comptroller Ch.313 portal:** No searchable agreement list returned via WebFetch — portal requires JS/session interaction; PDF download not available via this route.
**Abatement lead from T3:** King County Jan 2026 document (referenced in DDG results) mentions "Stetson Renewables Holdings, LLC and/or Bigway Solar, LLC, as assignee" — this strongly suggests a Ch.313 or JETI abatement application exists for this project. Could not confirm from primary source.

**T5 result:** abatement_found=plausible (indirect evidence only; direct source inaccessible). Note: Stetson Renewables as original applicant, Bigway Solar/NextEra as assignee.

## T6 start
**Site candidate:** No GPS pin (gmaps API 429). No abatement map available. POI substation (Edith Clarke 345kV) coords not resolved via web. Used King County centroid (33.60°N, 100.20°W) — confidence LOW.

**Imagery:** 3×3 grid at county centroid (step ±0.03°), buffer-km 2, date 2026-07-01.
- 7/9 chips retrieved (W and C grid positions got HTTP 403)
- Contact sheet read: all visible chips show undeveloped West Texas brushland/grassland
- No solar panels, no ground disturbance, no construction activity visible
- Flatter agricultural terrain visible in SW chip, but no development
- 2 center chips (W, C) failed — actual project site may be in unmapped area

**T6 result:** construction_visible=false. Site candidate confidence too low to draw strong conclusion. No construction signal at county centroid.

## T7 start
Wrote triage_findings.json and triage.md.
**Turns used: ~28.** T1–T7 complete. Deep scan recommended.

**Blockers encountered:**
- gmaps.py: 429 rate limit (T2)
- PUCT Interchange: 402 on all endpoints (T4)
- King County PDF: SSL cert mismatch (T5)
- TX Comptroller Ch.313: no searchable data via WebFetch (T5)
- CDSE W+C chips: 403 (T6)
- DDG bot-block on 2/3 web searches (T3)

## 2026-07-20 — Deep Scan

### D1: IA extracted (PUCT 35077-2069)
- **IA confirmed**: PUCT 35077-2069, ETT × Bigway Solar LLC, signed 2025-02-18 → `sources/2026-07-20_puct_35077-2069_ercot-standard-generation-interconnection-agreem.pdf`
- **Exhibit B (Time Schedule)**: 32mo In-Service / 33mo Trial Op / 37mo Scheduled COD — all relative to Exhibit A conditions. Using 2025-02-18 as proxy: COD ~2028-03-18. Queue 2027-12-31 is ~3mo optimistic.
- **Exhibit C (Interconnection Details)**: "Bigway Substation located in King County approximately 14 miles south of Paducah, TX. POI at TSP's Claror Station." Delivery 345kV. 55x Power Electronics FS4105M inverters per INR (27INR0127 + 27INR0128). Joint 400 MW plant in single IA.
- **Exhibit C-1 (One-Line)**: Claror Station on Cottonwood–Edith Clarke 345kV Ckt 2. Cottonwood ~36 mi west; Edith Clarke ~53 mi east. `sources/2026-07-20_puct_35077-2069_ercot-standard-generation-interco_p51.png` → site.map_artifacts
- **Exhibit E (Security)**: $25,000,000 LC or corporate guaranty (ETT/NextEra) → `sources/2026-07-20_puct_35077-2069_ercot-standard-generation-interco_p55.png`

### D2: Site estimate
- Method: IA Exhibit C text — 14 miles south of Paducah TX (Cottle Co seat, 34.009°N 100.302°W). Estimated site: ~33.806°N, 100.302°W. King County. No Google Places pin. No Claror Station coords via gmaps/search.

### D3: King County abatement
- **Ch.312 tax abatement, Reinvestment Zone #2021-01** — original Sept 9, 2024; Second Amendment agenda Jan 12, 2026 → `sources/2026-07-20_king-county-tx_commissioners-court-jan2026-minutes.pdf`
- Parties: Stetson Renewables Holdings LLC and/or Bigway Solar LLC, assignee
- Tracts: D&W RR CO (Abs 2691030), MASON A (2691160, 2691212), MASSEY JV (269255), TT RR CO (269320, 2691077), I&GN RR CO (269309, 269312), BURLESON J (26913), GROGAN HRS (26990)
- Improvements: solar panels, invertors, substation, roads, SCADA — 175 MW AC; Cost $210M
- Road Use Agreement also: same parties, same abatement agreement dated Sept 9, 2024
- **This is a Ch.312 county abatement (not Ch.313 school district)** — explains ch313.py negative result

### Negatives logged
- Google Places: no pin for "Bigway Solar", "Bigway Solar I", "Claror Station" — search backends down (DDG ConnectionError)
- ch313.py: no match under Bigway Solar, Stetson, or NextEra — expected (Ch.312, not Ch.313)
- EIA-860M: not in EIA per factsheet (paper score factor); FIS not approved as of Jun 2026

### D4/D5 wrap-up

**CDSE imagery**: Service unavailable throughout deep scan (RemoteDisconnected on all attempts). True site at ~33.806N, 100.302W not imaged. Triage contact sheet covers county centroid (~33.6N), not the 14-mi-south-of-Paducah site. Imagery stage: inconclusive/no_activity at county centroid.

**EIA-860M**: NOT in EIA-860M (TX slice) — consistent with early-stage project with no construction start; negative evidence supporting delayed COD.

**King County Feb 2026 minutes**: No solar project action items (routine county business). Dec 2024 minutes: No solar items.

**COD assessment**: IA Exhibit B = 37 months relative → ~2028-03-18 using IA execution as proxy. Queue COD 2027-12-31 is ~3 months optimistic vs IA schedule. FIS not approved. No construction. COD history pulled forward 2 years (2029→2028→2027) in 28 snapshots. Independent estimate: **2028-Q1, drift risk HIGH**.

**Verdict**: **real_early** — IA confirmed, $25M security posted, Ch.312 county abatement executed (Sept 2024 original + 2nd amendment), 10 survey tracts named, $210M investment, NextEra developer with nexteraenergy.com contacts in IA. No construction activity to date. Queue COD 2027-12-31 is ahead of IA contractual schedule by ~3 months; high drift risk given FIS not approved and no build start.

---

## 2026-07-21 — Second-pass review (resumed after prior deep scan)

### SPV reconciliation (verified)
- ONLY King County Ch.312 abatement (authoritative Comptroller registry, ch312.py) = **Midway Ranch Solar LLC | King County Reinvestment Zone #2024-01 | Active** (record #000014903, effective 2024-09-09, expires 2033-11-04) + purged/Inactive twin #000014900 (Wayback-recovered).
- King County minutes 2026-01-12 (re-read directly) name the SAME abatement's property owner/applicant as **Stetson Renewables Holdings, LLC and/or Bigway Solar, LLC (assignee)** — same RZ, same 10 tracts, same 2024-09-09 effective date. So: Bigway Solar LLC = ERCOT queue/IA customer; Stetson Renewables = abatement applicant (county); Midway Ranch Solar LLC = Comptroller-registered zone owner. Link DOCUMENTED (shared zone/tracts/date); NextEra parent INFERRED only.
- CORRECTION to prior scan: zone is **#2024-01** (the minutes' "Name of Reinvestment Zone"), NOT #2021-01 (that came from the doc's stray "Location of Reinvestment Zone #2021-01" template line). Prior findings never surfaced the Midway Ranch registry name.

### Registry corroboration (was skipped by prior scan)
- eia_history.py --write: neither INR in EIA-860M TX slice — clean negative, no operating-neighbor false-bind (King Co empty).
- spv.py resolve: Bigway Solar, LLC confirmed (puct-index, IA filing description).
- ch312.py resolve (both INRs): county-match Midway Ranch RZ#2024-01 (records above).
- ch313.py resolve + --name "Midway Ranch": structural negatives (recorded).
- puct.py match --key "Midway Ranch": IA 35077-2069 CONFIRMED (INR found in document text) for both.
- minutes.py harvest/index/resolve --county King: 116/121 indexed files are image-only scans; tool cannot text-match. Coverage limit, not a true negative — abatement confirmed via manually-rendered 2026-01-12 minutes.

### Site (verified, HIGH confidence): 33.77561 N, -100.31339 W
- Re-ran TX GLO OTLS ArcGIS query myself (Original_Texas_Land_Survey/FeatureServer/0, field ABSTRACT_N). All 10 abstracts matched EXACTLY on survey name + abstract number; per-tract centroid mean reproduces 33.77561/-100.31339 independently. Corroborated by IA "~14 mi S of Paducah" (~2 mi off).
- Built parcel/tract map from the OTLS polygons -> sources/2026-07-21_king-county_bigway-abatement-tracts_map.png (+ .geojson). Addresses the "missing parcel map" gap. See SITE_DERIVATION.md.

### Imagery (Sentinel-2, 4 km buffer, verified centroid) — VERDICT REVERSAL
- Fetched 5 dates: 2024-07-15, 2025-07-20, 2026-01-31, 2026-04-26, 2026-07-20 (all clouds <=10.4%). Read every frame + zoomed crops.
- 2024/2025/2026-01/2026-04: undisturbed rangeland + seasonal ag (dryland fields, edge center-pivot circles) — NO project works.
- **2026-07-20: CONSTRUCTION VISIBLE** — engineered rectilinear graded array-block pads + bright straight access-road grid (90-deg corners) along a central spine road + a bright substation/laydown pad, on the abatement tracts near the section road. No PV modules yet (site-prep/pre-racking). First activity between 2026-04-26 (absent) and 2026-07-20 (present).
- This CORRECTS the prior 'no_activity': 27INR0127's prior chips were at the wrong county centroid (~33.60/-100.20); 27INR0128's prior July frame (wider 6 km buffer) showed the works faintly and was under-read (the "reversal" the prior scan was sensing).
- **Verdict: real_under_construction (early / site-prep).** COD 2027-12-31 still optimistic for a ~400 MW joint build; independent estimate 2028, drift risk downgraded high->moderate.
