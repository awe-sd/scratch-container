# Triage log — 22INR0262 Sequoia II Solar

## T1 start
**Queue history (71 snapshots, 2020-08-01 → 2026-06-01)**
- COD drift: 4 changes. Started 2023-01-01 → 2025-05-31 → 2026-02-28 → 2026-07-31 → 2026-11-21 (current)
- IA signed: 2023-08-29
- FIS approved: 2026-03-16 (recent — took ~5.5 years from FIS request 2020-08-27)
- Meets 6.9(1): 2025-09-22; Meets all 6.9: 2026-04-28
- No construction start/end dates; no energization/sync/commercial-op approvals
- Capacity downsized: 550 → 556.25 → 425.02 → 417.47 MW (current)
- Status: IA signed, FIS approved, all 6.9 milestones met — pre-construction stage

## T2 start
**gmaps.py places** — 429 Too Many Requests on both attempts. 0 pins found. Normal, moving on.

## T3 start
**Web sweep** — DDG blocked (CAPTCHA). Bing returned no relevant results for "Sequoia II Solar" + Texas/Callahan/ERCOT/22INR0262 across 3 queries. No developer name, news, or LLC registration found. No sources saved. Normal for low-profile queue project.

## T4 start
**PUCT Interchange** — portal returns HTTP 402 on all direct URL attempts (3 tries). Bing search for PUCT + "Sequoia II Solar" returned no docket numbers or IA documents. No IA found via web access. Note: IA signed date IS present in ERCOT queue data (2023-08-29) confirming IA exists, but the PUCT filing itself is inaccessible via these methods during triage.

## T5 start
**TX Comptroller Ch.313 / JETI** — Comptroller site redirected to program overview page (no searchable data accessible via WebFetch). Bing search for JETI + Sequoia + Callahan returned no results. No abatement application found. Normal for post-2022 projects (Ch.313 expired; JETI registry not yet fully searchable).

## T6 start
**Imagery** — No pin from T2 (gmaps blocked). Reata 345kV substation coordinates not found via OSM/Bing/Overpass (all returned empty or timeout). Best candidate is county-level only (Callahan County centroid ~32.30N, 99.40W). Rule: "nothing better than somewhere in the county → SKIP imagery." Skipping. No site candidate.

## T7 start
Wrote triage_findings.json and triage.md. Turns used: ~22. STOP.

## Deep scan start — 2026-07-19

### D1: Developer identification
- **ENBRIDGE SOLAR SEQUOIA II LLC** = interconnecting entity per ERCOT GIS Report Jun 2026 xlsx
- Parent: **Enbridge Inc.** (Canadian pipeline/energy, NYSE: ENB)
- Enbridge renewables page confirms "Sequoia Solar Phase 2 – Callahan County, TX – 415 MWac (2026)"
- Source: local GIS xlsx (row 169, sheet "Project Details - Large Gen") + enbridge.com/about-us/renewable-energy
- NOTE: Also have "Sequoia I Solar" (earlier phase) — need to find that INR for cross-reference

### D2: Reata 345kV substation location
- Bus 68051, operator: Lone Star Transmission, LLC
- PUCT filing description: "along and east of CR 126, 1.10 miles north of FM 2945 in western Eastland County, TX"
- Derived coords: ~32.4034°N, -99.1097°W (1.1 mi north along CR 126 from FM 2945 intersection)
- NOTE: substation in Eastland County, not Callahan — project site likely straddles/adjacent
- Site will be within a few miles of this POI tap

### D3–D7: Deep-scan web research results (2026-07-19)

**D3: Enbridge renewables page (https://www.enbridge.com/about-us/renewable-energy)**
- Verbatim table row: "Sequoia Solar Phase 1 | Callahan County, TX | December 2025 | 400 | Enbridge Inc. (100%)"
- Verbatim table row: "Sequoia Solar Phase 2 | Callahan County, TX | 2026 | 415 | Enbridge Inc. (100%)"
- Both phases 100% Enbridge-owned. Combined gross = 815 MWac.
- Page note: combined solar net total = 2,347 MW across 18 solar assets; 2,710 MW gross total.
- Sequoia II COD listed as "2026" (no specific month given on the page).
- ERCOT queue shows current COD 2026-11-21 for 22INR0262. Phase 1 (Phase 1 INR not found in this session) targeted December 2025.
- No EPC contractor, offtake, or financing details disclosed on this page.

**D4: PUCT Interchange filing**
- interchange.puc.texas.gov returns HTTP 402 (payment required / access restricted) on all direct URL fetch attempts.
- Web searches for PUCT docket + "Enbridge Solar Sequoia" or "Sequoia II Solar" returned no docket numbers.
- IA existence is confirmed via ERCOT queue data (iaSigned = 2023-08-29) but the PUCT filing number could not be retrieved via WebFetch.
- RECOMMENDATION: Manual PUCT Interchange search at https://interchange.puc.texas.gov using company name "Enbridge Solar Sequoia II" or docket keyword "Sequoia" with date range 2023-08 to 2023-10 is required.

**D5: Callahan County CAD**
- esearch.callahancad.org — public owner-name search portal exists but URL parameter pattern for REST query is not publicly documented (form-based only, 404 on guessed URL patterns).
- GIS map available at gis.bisclient.com/callahancad/ but not scrapable.
- No parcel IDs, acreage, or situs addresses retrieved for "Sequoia" or "Enbridge" owners.
- RECOMMENDATION: Manual search at https://esearch.callahancad.org/ using Owner tab → name "Sequoia" will find parcels if title has transferred.

**D6: TX Comptroller franchise tax / TX SOS**
- comptroller.texas.gov/taxes/franchise/account-status/search — accepts entity name, but results require form POST (no direct URL query); returned empty on guessed GET params.
- apps.sos.state.tx.us — DNS not resolvable from this environment (ENOTFOUND).
- No franchise tax status or SOS registration data retrieved.
- RECOMMENDATION: Manual search at https://mycpa.cpa.state.tx.us/coa/ entity name "Enbridge Solar Sequoia II" or "Sequoia II Solar LLC" will confirm registered agent / formation date.

**D7: Press releases and news**
- Enbridge newsroom (enbridge.com/media-center/news) — no press releases found for "Sequoia Solar" across 2022, 2023, 2024, 2025 keyword searches.
- Enbridge DID issue a press release for the related project: "Clear Fork Solar – 600 MW Texas (Meta offtake)" dated July 22, 2025. No Sequoia-specific announcement found.
- Enbridge acquired Tri Global Energy (TGE) on 2022-09-29 for US$270M — TGE was the originator of many Texas solar developments in Enbridge's portfolio. Sequoia II was likely originated by TGE pre-acquisition.
- No construction updates, EPC contractor announcements, or groundbreaking news found for Sequoia II Solar.
- Solar Power World, Recharge News (paywalled), Business Wire (timeout) all returned no accessible results.
- RECOMMENDATION: Search PV Tech, Wood Mackenzie project database, or SNL/S&P for EPC details. TGE's historic project pipeline may name the EPC.

### D3: ERCOT queue — Reata POI neighbors
- 22INR0261 "Dorado Solar" (401 MW, Callahan, same Reata 345kV POI) approved for commercial operation 2026-04-28 — THIS IS LIKELY SEQUOIA PHASE 1 (Enbridge page shows "Sequoia Solar Phase 1 – Dec 2025 – 400 MWac")
- 21INR0325 "Sheep Creek Wind" (153 MW, Callahan, Reata POI) also now commercial 2024-10-01
- Phase 1 online means the substation is BUILT and ENERGIZED → Phase 2 (22INR0262) does NOT need to wait for substation construction
- This is a major real-project signal: infrastructure exists, developer track record proven on adjacent site

### D4: Enbridge.com confirmation
- Enbridge page: "Sequoia Solar Phase 1 | Callahan County, TX | December 2025 | 400 MWac | 100% Enbridge"
- Enbridge page: "Sequoia Solar Phase 2 | Callahan County, TX | 2026 | 415 MWac | 100% Enbridge"
- Developer chain: Sequoia II Solar LLC → Enbridge Solar Sequoia II LLC → Enbridge Inc. (via Tri Global Energy acquisition Sep 2022)
- Source: https://www.enbridge.com/about-us/renewable-energy
