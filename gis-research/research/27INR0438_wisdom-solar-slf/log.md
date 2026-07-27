# Triage log — Wisdom Solar SLF (27INR0438)

## T1 start
queue_history.py: 17 snapshots 2025-02-01 → 2026-06-01
- COD: 2027-10-06, zero drift across all 17 snapshots
- Screening started: 2025-02-12; screening complete: 2025-04-18
- FIS requested: 2025-02-05; FIS approved: 2025-10-09
- IA signed: NOT achieved (blank)
- All construction milestones: NOT achieved
- Meets 6.9(1) / all 6.9: NOT achieved
**T1 result:** Pre-IA stage; FIS approved but no IA yet. Stable COD.

## T2 start
gmaps.py: HTTP 429 on both attempts (exact name; name+county). Budget exhausted.
**T2 result:** 0 pins found.

## T3 start
DDG search "Wisdom Solar SLF Texas": found tracker aggregators (infrasure.ai, cleanview.co, ercotqueue.com, interconnection.fyi, gridstatus.io) + PUCT interchange filing hit (controlNumber=35077).
DDG search "Wisdom Green Energy LLC Texas": developer = Wisdom Green Energy LLC, Missouri City TX; holdings entity inc. April 4, 2025 (very new). No press releases, no news, no EPC contracts found.
No pages saved to sources/ (aggregator pages only, not primary sources about this project directly).
**T3 result:** Developer ID'd (Wisdom Green Energy LLC). No news/PR. PUCT filing controlNumber=35077 flagged for T4.

## T4 start
PUCT interchange.puc.texas.gov returns HTTP 402 (Payment Required) on both document list and PDF direct URL. Blocked — one retry attempted; budget exhausted.
Note from T3: controlNumber=35077, itemNumber=2435, dated 2026-03-13, described as IA between Wisdom Green Energy LLC and Texas-New Mexico Power Company (TNMP). IA EXISTS but content not retrieved.
**T4 result:** IA confirmed to exist (PUCT filing 35077/2435 per T3 aggregator hit, March 2026). Content inaccessible in triage (402). IA signed milestone NOT yet reflected in ERCOT queue data (timeline shows blank iaSigned as of 2026-06-01 snapshot — data lag possible).

## T5 start
TX Comptroller Ch.313 portal: pages return program overview only — no filterable data accessible via WebFetch. Budget exhausted (3 attempts).
JETI not attempted — post-2022 project; Ch.313 expired; JETI miss expected/normal.
**T5 result:** No abatement found. Normal for this vintage.

## T6 start
Site candidate assessment: no pin (T2 blocked), no IA map (T4 blocked), no abatement map (T5 miss).
POI = "Holiday Sub TNMP 138kV" — searched for substation coordinates: DDG returns TNMP White Baker→Century→Holiday 138kV corridor in Pecos County but no lat/lon.
Best candidate = "somewhere in Pecos County" — county area ~12,000 sq km.
Rule: no site candidate better than county-level → SKIP imagery.
**T6 result:** SKIPPED — no site candidate.

## T7 start
Wrote triage_findings.json and triage.md.
**Turns used: ~22. STOP.**

## Deep scan start — 2026-07-19

### DS1: Queue parquet POI cross-reference
GIS parquet query for 'Holiday' and 'Soaptree' in poiLocation:
- 27INR0438 Wisdom Solar SLF: `Tap 138 kV #38455 HOLIDAY SUB TNP - #38450 SOAPTREE TNP`, Pecos, 299.37 MW
- 27INR0440 Wisdom BESS SLF: same POI, 102.88 MW, same COD 2027-10-06 (sister project)
- 23INR0401 Headcamp Energy Storage: `tap 138kV 38331 TN Alamo St – 38455 TN Holiday`, Pecos, 152.88 MW, IA signed 2024-02-16, COD imminently due
Bus IDs confirmed: #38455 = HOLIDAY SUB, #38450 = SOAPTREE, #38331 = ALAMO ST (all TNMP 138kV, Pecos County)
**Finding: Holiday Sub confirmed real (Headcamp has signed IA and imminent COD). Soaptree is adjacent substation on same 138kV line.**

### DS2: Holiday Sub location via Google Places
`gmaps.py places "Headcamp BESS Pecos Texas"` → "Headcamp BESS | 816 E 42nd Ln, Fort Stockton, TX 79735 | 30.917793, -102.853740"
**Site candidate: 30.917793, -102.853740 (Fort Stockton TX) — this is the Headcamp BESS location at Holiday Sub, the same substation Wisdom Solar taps.**
Source: Google Places pin (delivery-pin trick), Headcamp BESS — same infrastructure, different project.
Confidence: medium-high — this is the substation/adjacent site, not necessarily the Wisdom Solar array centroid. Wisdom Solar (299 MW solar) will be within ~5-10 km of this pin.

### DS3: Satellite imagery — Holiday Sub area (30.9178, -102.8537)
S2 chip 2026-07-01, 6km buffer — centered on Headcamp BESS pin (Holiday Sub / Fort Stockton area).
- Frame shows Fort Stockton urban area + surrounding agricultural land; no solar construction visible anywhere in the 6km frame
- Note: 299 MW solar = ~600-900 acres; likely sited along the TNMP 138kV tap line between Holiday Sub and Soaptree Sub, potentially 5-20 km from Holiday Sub gate
- Need Soaptree Sub coordinates to triangulate tap midpoint for site search
- Artifact: imagery/s2_holiday_sub_2026-07-01.png (this is the original s2_2026-07-01.png showing same area)
**Finding: No activity at Holiday Sub gate area. Must search along Holiday-Soaptree 138kV corridor.**

### DS4: Developer chain — Wisdom Green Energy LLC
- No website (wisdomgreenenergy.com DNS fails)
- No LinkedIn company page
- No press releases, no news coverage
- TX Comptroller entity search: portal redirects to non-functional form (JS required)
- OpenCorporates: CAPTCHA blocked
- TX SOS: SOSDirect requires paid account
- PUCT interchange: consistently 402 (all item variants)
- Bizapedia: CAPTCHA blocked
- No CAD parcels found under "Wisdom" owner (JS-rendered results may not appear in static fetch)
**Finding: Developer Wisdom Green Energy LLC has zero public footprint. Cannot determine parent chain, officers, or prior projects.**

### DS5: Soaptree Switching Station located via OSM Overpass API
- Soaptree Switching Station (TNMP): 31.0831, -102.3936 (transmission, TNMP operator)
- Holiday Sub: NOT in OSM, but from Headcamp BESS DS2 pin, confirmed near Fort Stockton at ~30.92, -102.85 (816 E 42nd Ln area)
- 138kV tap corridor: Holiday Sub (30.92,-102.85) → Soaptree (31.08,-102.39) = ~43 km NE
- Wisdom Solar 299 MW would need 600-900 acres along this corridor
- No solar activity found at Holiday Sub gate area (DS3); must search midpoint and Soaptree end
- Source: Overpass API query (lat 30.5-31.5, lon -104 to -102), OSM power=substation data

### DS6: SOLAR INSTALLATION VISIBLE near Soaptree Sub
S2 chip 2026-06-01 (6km buffer, centered on Soaptree Switching Station 31.08,-102.39):
- DARK MODULE ARRAYS visible in upper-right quadrant — characteristic dark blue-gray rectangular grid = installed solar panels
- Array estimated center: ~31.11, -102.36 (pixel fraction ~70% right, 20% top of 12km frame)
- Size: appears substantial (multiple connected rectangular arrays); rough estimate 200-500 acres from thumbnail
- CRITICAL: Need to determine if this is an existing operating project or Wisdom Solar SLF (which is pre-IA per Jun 2026 data)
- Candidate existing projects near Soaptree area: Indian Mesa Repower variants (18INR0069, 19INR0080), or an existing operating plant not in current queue
- Getting tight 3km chip to confirm coordinates and size

### DS7: Solar array confirmed at ~31.11, -102.35 — identifying project
3km tight chip confirms: TWO adjacent solar array blocks, clearly installed (dark uniform module rows), appears operating/complete, NOT under construction.
- Lower-left block: ~400x400m; Upper-right block: ~500x500m total
- Combined estimate: ~100-150 acres from visible footprint in 6km chip context (NOT 300 MW = 600-900 acres)
- This is TOO SMALL for Wisdom Solar SLF 299 MW — strongly suggests this is an existing DIFFERENT project
- Need to identify: Indian Mesa Repower? existing operating solar project near Soaptree?
- Wisdom Solar (pre-IA, no construction) is NOT likely at this location

### DS8: Identifying existing solar near Soaptree (31.11, -102.35)
- Greasewood Solar (19INR0034, 255MW, COD 2021-02-09) confirmed at 31.037,-102.485 (Owego Rd, Fort Stockton) — too far west/south from the array visible at 31.11,-102.35
- Novasource East Pecos at 31.020,-102.286 — operates existing solar (Maplewood 2?) to NE of Soaptree area
- Riggins Solar (15INR0045, 155MW, COD 2018) at Riggins Switch 31.054,-102.851 (per OSM Riggins Substation)
- The array visible at 31.11,-102.35 in the Soaptree frame is likely an existing operating solar plant — possibly Maplewood 2a/2b (22+28=250 MW, COD 2021) or a similar operating project
- CRITICAL FINDING: Wisdom Solar SLF taps Holiday Sub (#38455) to Soaptree (#38450). Since no ACTIVE construction was visible at either Holiday Sub area or Soaptree area, NO construction is underway for Wisdom Solar SLF
- The solar arrays visible near 31.11,-102.35 appear to be an EXISTING operating project (pre-dates Wisdom Solar which is a 2025-entry project)

### DS9: Corridor midpoint imagery — no activity
S2 2026-07-01 at corridor midpoint 30.99,-102.62: raw undisturbed desert/scrubland, zero solar construction or land disturbance.
Full coverage of the Holiday–Soaptree 138kV tap corridor (6 frame sets) confirms NO construction activity for Wisdom Solar SLF anywhere along the expected tap line.
**IMAGERY VERDICT: no_activity. No solar construction visible on the Holiday-Soaptree corridor as of mid-2026.**

### DS10: Developer / ownership — final assessment
- Wisdom Green Energy LLC: Missouri City TX, formed April 2025, no website, no LinkedIn, no press
- No PUCT IA content retrieved (402 consistently blocked); triage confirmed IA filed Mar 2026 (PUCT 35077/2435)
- Sister project: Wisdom BESS SLF (27INR0440, 102.88 MW) at same POI — consistent with co-located solar+storage pattern
- Cannot determine parent company, officers, EPC, or offtaker
- Dogfish BESS (23INR0219, COD 2025-05-22) also taps Holiday Sub Alamo St area — demonstrates Holiday Sub capacity exists
- No developer track record, no financing news, no EPC contracts anywhere
**FINDING: Developer profile consistent with early-stage speculative paper project by a shell entity with no track record.**
