# Triage log — Hoyte Solar (23INR0235)

## T1 start
- queue_history.py ran: 63 snapshots, 5 reported-COD changes
- COD drift: 2023-12-31 → 2024-06-01 → 2025-09-30 → 2026-03-31 → 2026-12-15 → 2027-04-15 (current)
- Key milestones: IA signed 2022-10-14, FIS approved 2026-03-16, Meets all 6.9 2026-05-01
- Construction start reported 2025-08-11 (first appeared in 2026-04 snapshot)
- Capacity: 203.97 MW → 206.22 → 206.75 MW (stable since 2024-05)
- T1 result: Active project, IA signed, construction start claimed, COD 2027-04-15

## T2 start
- T2 result: gmaps.py returned 429 Too Many Requests on both attempts; pins_found=0 (API rate-limited, not a negative signal about project existence)

## T3 start
- T3 results:
  - Developer entity: Milano Solar, LLC (SPV name differs from "Hoyte Solar, LLC" in identity packet)
  - PUCT: Second Amendment to Standard SGIA (Oncor/Milano Solar) filed ~April-May 2026
  - ercotqueue.com: status "Construction; build-chance 91%"
  - infrasure.ai, cleanview.co, interconnection.fyi all confirm active 206-207 MW solar, Milam County
  - Ferrovial newsroom referenced ~$355M investment for a 250 MW Milam County facility (possibly related/adjacent)
  - Second DDG search: CAPTCHA blocked; one retry exhausted → negative
  - Third search: 403 → negative
  - news_found=true (IA amendment, Ferrovial ref); developer name = Milano Solar LLC

## T4 start
- T4 result: PUCT Interchange returning HTTP 402 on all URL patterns attempted (FilingParty search, Documents search, root). Portal blocked — ia_found=false from direct access. Note: T3 web sweep found a reference to a "Second Amendment to SGIA (Oncor/Milano Solar) filed April-May 2026" via third-party trackers, which strongly implies an IA exists, but could not confirm or download directly. Logging ia_found=true (inferred from secondary source); deep scan should chase the actual PUCT docket.

## T5 start
- T5 result: TX Comptroller Ch.313 pages returned only navigation/overview content — actual agreement DB not accessible via WebFetch (likely JS-rendered). JETI registry not successfully reached. abatement_found=false. Note: post-2022 projects normally use JETI not Ch.313; a JETI miss is normal for this vintage. Deep scan should try direct JETI portal if needed.

## T6 start
- T6 result: no site candidate found — gmaps returned no pins (429), web sweep found no coordinates or parcel data, "Cannon Switch" substation location not found in web results. Best available: "somewhere in Milam County" (center ~30.79N, 96.98W). Per checklist rule: SKIP imagery, log "no site candidate". construction_visible=false/unknown.

## T7 start
- T7 result: triage_findings.json + triage.md written. deep_scan_recommended=true. Turns used: ~22.

## Deep scan start — 2026-07-19

### Stage 1: LLC → parent chain
- Confirmed from local parquet: `interconnectingFacility = "Milano Solar LLC"` for 23INR0235. This is the SPV on the ERCOT IA, confirming triage finding. "Hoyte Solar" = project name; "Milano Solar, LLC" = legal entity name. [parquet]
- financialSecurityAndNoticeToProceedProvided = "Yes" confirmed; NTP issued.
- All 6.9 milestones met 2026-05-01; FIS approved 2026-03-16; IA signed 2022-10-14.
- TX Comptroller entity search: CPA API returns 403/Forbidden; SOSDirect requires paid account. Developer identity above "Milano Solar LLC" not yet established.
- PUCT Interchange portal returns HTTP 402 on all access attempts; full JS rendering blocks curl. Could not pull IA document or control number directly.
- Triage noted Second Amendment to SGIA (Oncor/Milano Solar) filed Apr-May 2026 per third-party tracker. Treating as plausible — IA exists (IA signed date in queue = 2022-10-14).
- Ferrovial newsroom search: no reference to Milano Solar or Milam County solar found. The "Ferrovial $355M / 250 MW Milam County" triage reference could not be confirmed from Ferrovial's own newsroom.

### Stage 2: County records
- Milam CAD esearch.milamad.org: owner name search is JS-rendered; curl returns only page shell. Could not retrieve Milano Solar parcel records.
- Milam County public records (milam.tx.publicsearch.us): React-rendered; no API access.
- TX Comptroller Ch.313/JETI pages: all JS-rendered; no downloadable agreement list found.
- TPIT (ERCOT Transmission Planning Info Tracking, Jul 2026): **KEY FINDING** — Bus 3707 = Cannon Switch 138kV, Milam County, Oncor (confirmed). [sources/2026-07-19_ercot_tpit_cannon-switch.xlsx]
  - TPIT row 99344: Rebuild Minerva(3683)-Cannon(3707) 138kV line, 10.2 miles, Milam County, planned 2028 (Tier 1 project)
  - TPIT row 110022: Rebuild Cannon(3707)-Dos Rios(3725)-Robertson(32) 138kV line, 19.2 miles, Milam/Robertson counties, planned 2029 (Tier 1)
  - TPIT row 81551: New Dos Rios 138kV Switch (bus 3725) between Cannon and Robertson, planned 2029
  - Implication: Cannon Switch is an EXISTING junction switch in Milam County on the Oncor 138kV network, being REBUILT/upgraded to accommodate new generation. 

### Stage 3: Site pinpoint
- gmaps.py returning HTTP 429 (rate-limited from triage day); no Places pins obtained.
- Cannon Switch coordinates NOT in public sources directly.
- OSM Nominatim: "Cannon Switch" returns 0 results; "Cannon Texas" shows only Grayson/Cass/Mason counties (not Milam).
- Milam County geographic context: Minerva TX hamlet at 30.7582, -96.9880; Milano TX at 30.7106, -96.8647.
- Estimated Cannon Switch location: ~30.78N, -96.80W (10.2 miles bearing ~80° east of Minerva toward Robertson County line) — ESTIMATE from TPIT topology, NOT a primary coordinate source.
- Confidence: LOW for exact pin; will search in ~30.75-30.85N, ~96.70-96.90W grid.

### Stage 1 continued — Developer ID (KEY FINDING)
- **SEC EDGAR search confirmed: Milano Solar, LLC is a subsidiary of Ferrovial SE** (Spanish infrastructure conglomerate, NYSE: FER). Chain: Milano Solar, LLC → Ferrovial Energy US, LLC → Ferrovial SE. [sources/2026-07-19_sec_ferrovial_20F_subsidiary-list.html]
- Ferrovial acquired Milano Solar, LLC on **June 30, 2025** for **USD 19 million** via Ferrovial Energy US, LLC. Stated purpose: "development, construction, financing, operation, and maintenance of a 250 MW solar photovoltaic facility, located in Milam County, Texas, expected to operate for 40 years." [sources/2026-07-19_sec_ferrovial_6K_june2025_milano-solar-acquisition.html]
- Project described in 20-F as "newly launched" — had no staff/business activity at acquisition → SPV purchased from original developer (name unknown). [sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html]
- Bank guarantees as of 12/31/2025: EUR 32M for Milano Solar project (20-F). [sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html]
- Note: Ferrovial reports 250 MW capacity; ERCOT queue shows 206.75 MW. This discrepancy is common (nameplate vs grid capacity).
- IAI 2025 report also confirms Milano Solar in US energy portfolio. [sources/2026-07-19_sec_ferrovial_IAI2025_milano-solar.html]

### Stage 2 continued — County records
- Milam County CAD: esearch.milamad.org returns 404 for all search URL patterns (JS-rendered; not accessible via curl). 0 owner-name records found.
- Milam County Commissioners Court agendas 2022-2026: No visible reference to "Milano Solar" or "Hoyte Solar" in agenda titles via BoardBook and milam website. Riot Rockdale (data center) was the primary recent energy agenda item.
- TX Comptroller Ch.313/JETI: portals JS-rendered; no direct agreement data accessible.
- Milam County has active solar pipeline: Jan 2026 commissioners minutes reference "Tehuancana Creek Solar LLC" utility easement in Pct 3 — confirms county is solar-active.

### Stage 3 — Site pinpoint
- OSM Nominatim: "Hoyte" community exists at **30.7849N, -96.9155W** in Milam County TX (confirmed primary). Project named after this community.
- "Milano" community: 30.7106N, -96.8647W — possible alternate site reference.
- Cannon Switch (3707) location: estimated ~30.78-30.75N, ~96.82W based on TPIT topology (Minerva-Cannon 138kV, 10.2 miles, Milam County). NOT in OSM; exact coords CEII-restricted.
- Existing imagery chip (s2_2026-07-10_center.png, centered ~30.78, -96.80): white grid structure visible at lower-left, estimated ~30.748N, -96.838W — likely construction activity.
- CDSE sync endpoint experiencing remote disconnections since this session started; unable to get new chips. Existing chip covers Cannon Switch area NOT the Hoyte community area.
- No Places pin for Hoyte Solar or Milano Solar (GMaps API 429 + REQUEST_DENIED).
- Site candidate: **30.748N, -96.838W** (from imagery feature in existing chip) OR **30.785N, -96.916W** (Hoyte community). Confidence: LOW — need more imagery.

### Ferrovial 20-F December 31 2025 — Construction Status (KEY FINDING)
- Ferrovial 20-F (annual report, Dec 31 2025): **"In the United States, the Energy Division has two solar photovoltaic plants under construction in Texas (Leon and Milano), with a combined generation capacity of 500 MW, that are expected start operations in 2026 and in 2027 respectively."** — Milano = 2027 COD consistent with queue. [sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html]
- Ferrovial June 2025 6-K: As of June 30 2025 (acquisition date), Ferrovial "in the process of negotiating and closing PPAs, financing and construction contracts including the sourcing of main equipment." → NO PPA/financing/EPC at acquisition. [sources/2026-07-19_sec_ferrovial_6K_june2025_milano-solar-acquisition.html]
- Sequence: Jun 2025 = acquired, negotiating → Q3 2025 = construction start (queue: 2025-08-11) → Dec 2025 = "under construction" (20-F confirmed).
- EUR 174M PP&E additions in 2025 Energy division = "fundamentally due to acquisition of Milano Solar." EUR 32M bank guarantees issued for Milano Solar in 2025.
- PP&E value (EUR 174M vs $19M SPV price) implies substantial tangible asset value embedded in the SPV (site rights, IA, permits). 
- No EPC contractor named in SEC filings.

## Deep scan resumed — 2026-07-20 (new run after max-turns failure)

### D0: findings.json skeleton written

### D1: IA schedule extraction
- **Original IA** (filed 2022-11-09, signed 2022-10-14): COD June 1, 2024; In-Service Apr 18, 2024; Trial Op May 1, 2024. Security: $3,662,558 (by Oct 14 2022) → $8,142,020 (by Jul 7 2023). Equipment: 61× Power Electronics HEMK FS3430K inverters. [sources/2026-07-19_puct_35077-1514_interconnection-agreement-between-oncor-electric.pdf]
- **Amendment 1** (filed 2026-04-20, signed 2023-11-16): COD Sept 30, 2025; In-Service May 8, 2025; Trial Op May 18, 2025. Security: $3,662,558 → $9,793,633. [sources/2026-07-19_puct_35077-2462_amendment-no-1-to-the-standard-generator-interco.pdf]
- **Amendment 2** (filed 2026-06-17, signed 2026-05-27): **COD April 15, 2027; In-Service Dec 12, 2025 (past); Trial Op Dec 16, 2026.** Equipment updated to 54× Sungrow SG4400UD inverters. No security exhibit in Amendment 2 (Exhibit E not replaced). [sources/2026-07-19_puct_35077-2503_amendment-no-2-to-the-standard-generation-interc.pdf]
- POI confirmed: Cannon Switch 138kV, ~5 miles north of Milano, Milam County. TSP = Oncor.
- Developer contact on orig IA: Dan King (dan@electerra.dev) → original developer was Electerra (Austin TX). Sold to Ferrovial Energy US LLC for $19M on June 30, 2025.

### D2: Site / imagery
- One chip exists: imagery/s2_2026-07-10_center.png (centered approx 30.78, -96.80). Contains: lower-left = bright white road grid + cleared/graded area (active construction site); lower-center = dark parallel rows (modules or racking). CDSE endpoint down for new chips.
- POI stated as "~5 miles north of Milano" = ~30.783N, -96.865W (estimate). Hoyte community at 30.785N, -96.916W.
- Imagery shows activity consistent with active solar construction. At least two areas visible in single chip.
- CDSE remote disconnect: no new chips obtained. Single existing chip covers ~6km box.

### D3: Gap-fill
- ch313.py: No Ch.313 or JETI agreement found for Hoyte Solar or Milano Solar — negative evidence. This is expected for a 2023-vintage project where the JETI portal was not fully populated. [artifact: ch313.py output]
- SPV resolved: Milano Solar, LLC (PUCT filings) = confirmed SPV. Parent = Ferrovial SE via Ferrovial Energy US LLC (confirmed from SEC 20-F subsidiary list). [sources/2026-07-19_sec_ferrovial_20F_subsidiary-list.html]
- EIA 860M: No exact match. Ambiguous candidates in county (Two Rivers Solar 214MW at 30.869,-96.736 is plausible, planned 2027-08; Yaupon Solar 200MW at 31.044,-96.851 less likely). "P - Planned for installation" status for all candidates. No DROPPED_FROM_860M signal.
- Queue: 5 COD slips (2023-12 → 2024-06 → 2025-09 → 2026-03 → 2026-12 → 2027-04). Construction start 2025-08-11 first appeared Apr-2026 snapshot. [timeline.md]
- Ferrovial 20-F Dec 2025: "Milano" plant under construction in Texas, expected to operate in 2027 — consistent with queue COD. EUR 174M PP&E additions in Energy division "fundamentally due to Milano Solar acquisition." EUR 32M bank guarantees issued. [sources/2026-07-19_sec_ferrovial_20F_annual2025_milano-solar.html]
- Ferrovial 6-K Jun 2025: At acquisition, "in the process of negotiating and closing PPAs, financing and construction contracts." By Dec 2025 annual report: "under construction." [sources/2026-07-19_sec_ferrovial_6K_june2025_milano-solar-acquisition.html]
- Abatements: No Ch.313/JETI agreement found. Normal for 2023 vintage. County commissioners no explicit Milano Solar reference found.

### D4: Analysis
- Verdict: real_active — Ferrovial confirmation, Amendment 2 signed May 2026, construction ongoing per imagery and SEC filings.
- Site: estimated 30.783N, -96.865W (5 miles N of Milano per IA) with LOW-MEDIUM confidence (no CAD, no Places pin, no GPS coords from IA, imagery not recentered). Activity in existing chip consistent with construction.
- Independent COD: 2027-Q2 (contractual Apr 15 2027 per Amendment 2, construction active per imagery/Ferrovial, but 5 prior slips and still in Trial Op phase with Dec 2026 target).
- Drift risk: medium — Ferrovial is institutional backer with EUR 32M guarantees, but In-Service was Dec 2025 (already missed), Trial Op due Dec 2026, COD Apr 2027 = tight.
