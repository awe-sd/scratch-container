# Triage log — Bigway Solar II (27INR0128)

T1 start
## T1 — Queue history
- 28 snapshots: 2024-03-01 → 2026-06-01
- COD drift (2 changes): 2029-07-01 → 2028-12-31 → 2027-12-31 (net FORWARD pull by ~1.5 yr)
- Milestones achieved: Screening started 2023-12-20, Screening complete 2024-03-15, FIS requested 2024-02-28, **IA signed 2025-02-15**, Meets 6.9(1) 2025-03-19
- FIS approved: NOT achieved; Meets all 6.9: NOT achieved; No construction dates
- Capacity: started 250.83 MW → 205 → 200 → 203 → **206 MW** (current); capacity trimmed ~18% from entry
- Notable: IA signed without FIS approved — milestone ordering anomaly per CLAUDE.md note
T1 done

T2 start
## T2 — Delivery pins
- gmaps.py returned HTTP 429 (rate-limited) on both attempts ("Bigway Solar II", "Bigway Solar II King County Texas")
- One retry attempted per rules; still blocked
- No pins found — BLOCKED portal, budget exhausted
T2 done

T3 start
## T3 — Web sweep
- Developer confirmed: **NextEra Energy** (NextEra Energy Interconnection Holdings, LLC)
- IA filed under entity "Bigway Solar, LLC" (covers Phases I & II)
- Companion project: Bigway Solar I (27INR0127), ~195 MW, same county
- PUCT control number found: **35077**, item 2069 — SGIA between Electric Transmission Texas LLC and Bigway Solar LLC
- Tax abatement: King County Jan 2026 agenda — Second Amendment to Tax Abatement Agreement, involves **Stetson Renewables Holdings** and Bigway Solar LLC (parent entity for NextEra dev co?)
- No news articles or press releases found; tracker sites (cleanview.co, interconnection.fyi, ercotqueue.com) confirm project data
- Sources saved: sources/web_sweep.md
T3 done

T4 start
## T4 — PUCT Interchange
- Control number 35077 identified from T3 web sweep
- All PUCT Interchange URLs returned HTTP 402 (Payment Required / session auth required)
- Tried: search by controlNumber, direct PDF URL, search by filingParty — all blocked
- One retry attempted; portal remains blocked — logging negative, budget exhausted
- KNOWN: IA exists (confirmed from T1 milestone: iaSigned 2025-02-15; T3: SGIA between ETT LLC and Bigway Solar LLC)
- IA schedule exhibit NOT retrieved — flag for deep scan
T4 done

T5 start
## T5 — Abatements
- Ch.313 expired 2022; project entered queue Dec 2023 → no Ch.313 expected, none found
- JETI registry search: no results for "Bigway Solar" + King County
- King County Jan 2026 agenda PDF (co.king.tx.us) referenced in T3: SSL cert mismatch error, could not retrieve
- BUT: T3 confirmed existence of "Second Amendment to Tax Abatement Agreement" between King County and Stetson Renewables Holdings / Bigway Solar LLC (Jan 2026 agenda)
- Abatement LIKELY EXISTS (Ch.312 or county-level) but application PDF not retrieved — flag for deep scan
T5 done

T6 start
## T6 — Imagery
- No pin from T2 (gmaps blocked)
- No abatement/IA map retrieved (PUCT 402, King County PDF SSL error)
- POI: "Tap 345KV #59904 Cottonwood - #60500 Edith Clarke Ckt #2" — tried to locate substation via web search; DDG returned CAPTCHA, Bing returned zero relevant results
- Best candidate is "somewhere in King County TX" — no specific site coordinate
- Per checklist: SKIP imagery, log "no site candidate"
- construction_visible: unknown
T6 done

T7 start
## T7 — Output
- triage_findings.json written
- triage.md written
- Turns used: ~18
- Deep scan: RECOMMENDED
T7 done

## T8 — King County Jan 2026 Commissioners' Court Agenda (DEEP SCAN)
- Source: https://www.co.king.tx.us/upload/page/9617/January%202026.pdf
- Artifact: sources/2026-07-19_king-county_jan2026_agenda.pdf
- Filed for record: NOV 25, 2025; meeting date: January 12, 2026
- **Confirms Second Amendment to Tax Abatement Agreement** between King County and Stetson Renewables Holdings, LLC and/or Bigway Solar, LLC as assignee
- Original abatement date: September 9, 2024 (from Road Use Agreement item)
- Reinvestment Zone #2021-01 (pre-dates 2023 queue entry — likely shared with Bigway Solar I / predecessor concept)
- **Applicant: Stetson Renewables Holdings, LLC** (Bigway Solar LLC = assignee)
- **Capacity: 175 MW AC** (vs 206 MW in queue = DC rating difference, consistent)
- **Estimated Cost of Improvements: $210,000,000**
- Improvements: Solar panels, invertors, substation, roads, collection system, SCADA
- Agenda Item 2: Road Use Agreement (Stetson/Bigway Solar) — active construction-prep paper trail
- Legal description tracts (survey/abstract numbers in King County):
  - D&W RR CO Block 2 Survey 2 Abs 2691030
  - MASON,A Block T Survey 12 Abs 2691160
  - MASON,A Block T Survey 12 Abs 2691212
  - MASSEY,JV Survey 1 Abs 269255
  - TT RR CO Survey 15 Abs 269320
  - TT RR CO Survey 16 Abs 2691077
  - I&GN RR CO Survey 17 Abs 269309
  - I&GN RR CO Survey 2 Abs 269312
  - BURLESON,J Abs 26913
  - GROGAN,HRS Abs 26990
- **Why it matters**: abatement confirms real project with investment commitment, tract descriptions anchor site geographically, Road Use Agreement = active pre-construction
echo "log updated"
## T9 — Site pinpoint via OTLS survey abstracts (Stage 3)
- Source: Texas GLO Original Texas Land Survey, ArcGIS FeatureServer
- Method: Queried all 10 abstract numbers from King County Jan 2026 abatement agenda; all 10 matched in northern King County TX
- Results: centroids from 33.74543 to 33.80676 lat, -100.34429 to -100.29146 lon
- **OVERALL CENTROID: 33.77561, -100.31339**
- Total area from OTLS polygons: ~7,681 acres (full leased ranchland, not panel footprint)
- Abatement capacity: 175 MW AC; queue: 206 MW — consistent with Phase II sizing (DC/AC ~1.18 or Phase II is 206 MW AC separately)
- **Why it matters**: tracts confirm exact location in northern King County; centroid anchors imagery

## T10 — Delivery pins (Stage 3 gmaps)
- HTTP 429 again on all three attempts (Bigway Solar, Bigway Solar II, Bigway Solar King County Texas)
- Negative evidence: no Google Places pins found; pin method unavailable
- Site already anchored by OTLS abstracts (T9) — no pin needed for imagery

## T11 — Satellite imagery Stage 4 (present-first)
- Frame 1: s2_2026-07-15.png — 6km buffer, centroid 33.77561,-100.31339
  - Observation: undisturbed ranchland + irrigated pivot fields. No graded polygons, no cleared pads, no access roads, no dark module arrays. Full footprint of abatement tracts visible as unmodified range/crop land.
- Frame 2: s2_2026-01-15.png — same centroid, 6 months back
  - Observation: identical character. No preconstruction or clearing activity anywhere in 6km view.
- Per PLAYBOOK early-exit: two consecutive no-activity reads → verdict **no_activity**; stop imagery scan.
- Key frames copied to imagery/key/
- Static map: Google Maps Static API 403 (API not enabled) — logged negative
- **Why it matters**: CRITICAL finding — no ground disturbs in early 2026, abatement Second Amendment dated Jan 2026 and Road Use Agreement → pre-construction permitting stage, not construction. COD 2027-12-31 requires construction to start imminently (≤18 months away from today).

## T12 — Stage 1 LLC/parent chain (additional attempts)
- OpenCorporates search for "Bigway Solar" TX: 0 results
- OpenCorporates search for "Stetson Renewables Holdings" TX: 0 results
- TX Comptroller COA search: requires JS execution; API requires auth — blocked
- TX SOS SOSDirect: $1/search paywall
- SEC EDGAR full-text "Bigway Solar": 0 hits
- SEC EDGAR full-text "Stetson Renewables": 0 hits
- BusinessWire search for Stetson Renewables: timeout
- NextEra newsroom search: no mention of Bigway Solar
- LinkedIn Stetson Renewables: 219KB JS wall (no text data)
- Parent chain: Triage T3 established "NextEra Energy Interconnection Holdings" as the developer from PUCT filing research; Stetson Renewables Holdings confirmed as applicant in King County abatement agenda. Chain = Bigway Solar LLC (SPV) → Stetson Renewables Holdings LLC (applicant/developer) → NextEra Energy Interconnection Holdings LLC — unverified at primary source, derived from triage T3 web research and abatement applicant name.
- No PPA / EPC / financing PR found (project is pre-construction)

## T13 — Stage 2 PUCT IA schedule (deep scan attempt)
- Control 35077, item 2069 confirmed in triage T3
- PUCT Interchange consistently returns 402 on all URL formats
- Doc number guessing (1250000–1450000 range) all 404
- The Hanson IA URL pattern (35077_1682_1337695.PDF) confirmed; Bigway would be 35077_2069_?????.PDF — doc ID not determinable without the search portal
- IA schedule UNCONFIRMED at primary source — rely on queue milestone: iaSigned 2025-02-15
- NOTE: FIS NOT approved as of 2026-06-01 (latest queue snapshot) — this is a constraint on final POI design

## T14 — Summary: evidence gathered
REAL signals: IA signed, Ch.312 abatement (2nd amendment Jan 2026), Road Use Agreement Jan 2026, OTLS tracts located, $210M estimated cost
EARLY signals: NO construction visible July 2026, NO July/Jan activity in imagery, FIS not approved
COD pull-forward (2029→2027) unusual — suggests developer confidence, not schedule certainty

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
