# Triage log — Zeus Spade Wind (26INR0386)

## T1 start
- queue_history.py ran: 15 monthly snapshots (2025-04-01 → 2026-06-01)
- Milestones: Screening started 2024-03-29, Screening complete 2024-06-25, FIS requested 2025-01-07
- No FIS approved, no IA signed, no 6.9 milestones
- Reported construction start 2025-08-01, construction end 2026-10-20 (THESE ARE QUEUE CLAIMS, not evidence)
- COD 2027-03-20 held steady across all 15 snapshots — zero drift
- COD plausibility: FIS not yet approved as of June 2026; COD 2027-03 is very aggressive for a project with no IA
## T1 result: project in early FIS stage; construction claims appear aspirational; stable COD with no IA is a red flag

## T2 start
- gmaps.py places: 429 Too Many Requests on all 3 attempts (project name, name+county, LLC+city)
- T2 result: NO pins found — gmaps API rate-limited, not a signal about project existence

## T3 start
- DDG search "Zeus Spade Wind Texas wind project": returned results from cleanview.co, interconnection.fyi, ercotqueue.com
- KEY FINDING: Developer identified as "Spade Wind, LLC" (not "Zeus Spade Wind, LLC" as assumed)
- Companion project: 26INR0387 Zeus Spade BESS, 446 MW battery, Mitchell County — suggests coordinated development
- ercotqueue.com status claim: "Construction; build-chance 95%" (third-party assessment)
- Federal wind permitting pause (Trump DoD review) noted — may affect this project
- DDG CAPTCHA on subsequent queries — no developer parent company identified, no press releases found
- Saved source: sources/ercotqueue_26INR0386.md
## T3 result: Developer = Spade Wind LLC; companion BESS project; no parent company confirmed; federal permit pause is a risk flag

## T4 start
- PUCT Interchange portal (interchange.puc.texas.gov): 402 Payment Required on all URL attempts — portal blocked/requires auth
- DDG search for PUCT filings "Spade Wind" OR "Zeus Spade" interconnection: no PUCT docket numbers returned
- IA milestone NOT achieved per queue data (iaSigned = null as of 2026-06-01)
- T4 result: NO Interconnection Agreement found; portal blocked; consistent with queue milestone data showing no IA signed

## T5 start
- TX Comptroller Ch.313 pages: no searchable database available via web; portal does not expose filterable 313 list
- JETI registry (jeti.house.texas.gov): domain not found (DNS failure)
- DDG search "Spade Wind" Mitchell County tax abatement / Ch.313 / JETI: no results
- Note: Ch.313 program expired 2022-12-31; post-2022 projects use JETI (Chapter 403); JETI DNS failure means registry may have moved
- 26INR0386 entered queue 2024 (post-313 expiry) — Ch.313 not applicable; JETI possible but not confirmed
- T5 result: NO abatement found; consistent with post-2022 project; JETI status unknown (DNS failure)

## T6 start
- Site candidate: POI = "Tap 345 kV 1030 Morgan Creek to 76030 Gasconades Creek"; Morgan Creek substation ~5 miles SW of Colorado City, TX
- Estimated center: 32.35°N, -100.95°W (low-confidence, POI-infrastructure based)
- 3×3 grid chips at ±0.03° step, buffer-km 2, date 2026-07-01: all 9 chips acquired after sequential retry
- Contact sheet built: 9 frames covering ~18×18 km around Morgan Creek / Colorado City area
- IMAGERY ASSESSMENT: Undisturbed West Texas ranchland + Colorado City Lake reservoir visible; NO turbine pads, NO new access road networks, NO disturbed/graded ground; zero construction signal
- T6 result: NO construction activity visible as of July 2026; consistent with no IA and no FIS approval

## T7 start
- Wrote triage_findings.json
- Wrote triage.md (10 lines)
- Turns used: ~28
- STOP

## Deep scan T1 — FAA OE portal
- oeaaa.faa.gov/oeaaa/external/searchAction.jsp?action=showSearchArchivesForm: 301 → /oeaaa/oe3a/main/#/home returns 503 "OEAAA Maintenance Notification — unexpected service interruption"
- FAA OE search unavailable during this run. Log as negative evidence: cannot retrieve exact turbine coords from FAA today.
- Fallback: USGS US Wind Turbine Database (uswtdb) for any built turbines; also SkyVector obstruction database + Google/DDG for study numbers.

## Deep scan T2 — USGS US Wind Turbine Database (uswtdb)
- energy.usgs.gov/api/uswtdb/v1/turbines?t_state=eq.TX&t_county=eq.Mitchell%20County → 206 turbines in Mitchell County, all pre-existing (Roscoe 2008 x104, Loraine 2010 x68, Loraine II 2011 x32, Champion 2008 x1, Inadale/Roscoe IV 2009 x1).
- ZERO turbines under "Spade Wind" or "Zeus Spade Wind" — CONFIRMED no turbines installed as of USGS DB (latest imagery date 2025-05-19 on some entries).
- Saved: sources/mitchell_uswtdb.json (206 built turbines, none Spade/Zeus)

## Deep scan T3 — TX Comptroller franchise entities (data.texas.gov "Active Franchise Taxpayers" dataset 9cir-efmm)
Found (saved: sources/2026-07-18_tx-comptroller_spade-entities.json):
- SPADE WIND, LLC — SOS 0804549070, chartered 2022-05-02, 500 W 2nd St, Austin TX 78701 — matches ERCOT queue LLC name per ercotqueue.com
- SPADE WIND I, LLC — SOS 0804549043, chartered 2022-05-02, same address
- SPADE WIND II, LLC — SOS 0804549049, chartered 2022-05-02, same address
- SPADE WIND III, LLC — SOS 0804549059, chartered 2022-05-02, same address
- SPADE BESS I / II / III, LLC — SOS 0805987213/218/221, chartered 2025-04-07, 500 W 2nd St Ste 1900, Austin TX 78701 — companion battery SPVs for 26INR0387
- NO "Zeus Spade Wind, LLC" — identity packet name is not the registered SPV; project SPV is "Spade Wind, LLC" (or numbered variants)
- Note: "Zeus" prefix appears only in the ERCOT queue project name and companion INR0387 name — a project family label, not an SPV name
- Suite 1900 address at 500 W 2nd Street matches a known Austin renewables developer office building

## Deep scan T4 — Suite 1900 tenants (developer identification)
Queried Comptroller for all entities at 500 W 2nd St Ste 1900, Austin TX 78701 (50-row page):
- **ZEUS RENEWABLE ENERGY DEVELOPMENT, LLC** — SOS 0804545xxx, chartered 2022-04-27 → 5 DAYS BEFORE Spade Wind LLCs (2022-05-02)
- **PARENT developer identified: Zeus Renewable Energy Development, LLC**
- The "Zeus" ERCOT project-name prefix (Zeus Spade Wind, Zeus Spade BESS) matches this parent
- Sibling project SPVs also at Suite 1900 (all chartered 2022-05-02, indicating a coordinated portfolio spin-up):
  - Mitchell Solar I / II / III / LLC (same Mitchell County → likely another queue project)
  - Armstrong Solar (I/II/LLC) — East TX (Armstrong County)
  - Houston County Solar (I/II/LLC)
  - Rusk Solar (I/II/LLC)
- Other suite-1900 devcos: Peak 10 Energy Management LLC (2023), FGE Peaker Portfolio / Robertson / Tyler / Athens (2024) — separate developers, shared office
- Saved: sources/2026-07-18_tx-comptroller_suite-1900-tenants.json

## Deep scan T5 — Zeus Renewable Energy Development web presence
- Standard domain patterns (zeusrenewables.com, zeusrenewableenergy.com, zeus-re.com, zeusrenewable.com): all NXDOMAIN
- SEC EDGAR full-text search "Spade Wind": 0 hits — not a public/registered filer
- Bing/DDG searches CAPTCHA'd or returning generic "spades" results
- LinkedIn public page: 404
- CorporationWiki: 403 (bot-blocked)
- Conclusion: Zeus Renewable Energy Development LLC has NO discoverable public web presence — likely a private, low-profile developer or a project-holding shell for another parent
- Portfolio in TX (all Suite 1900, chartered 2022-05-02, no public web): Mitchell Solar I/II/III, Armstrong Solar I/II, Houston County Solar I, Rusk Solar I — pattern of "county-name + resource" naming with numbered SPVs = signature of an early-stage speculative developer or a portfolio held for later monetization

## Deep scan T6 — Mitchell County CAD 2025 appraisal roll (33,459 parcels, downloaded direct)
- Searched entire 2025 roll for owners: SPADE WIND, SPADE BESS, ZEUS RENEWABLE, 500 W 2ND (Austin), any renewable/wind LLC at Austin address
- **ZERO parcels owned by Spade Wind LLC / Spade BESS LLC / Zeus Renewable Energy Development LLC**
- Only "Zeus" match: ZEUS PETROLEUM INC (mineral rights, Bellaire TX, unrelated oil-and-gas holder)
- Only "Spade" match: SPADES 5 LLC (Lubbock, farmland — NOT the wind SPV)
- Existing wind farms in county: RWE-Champion, RWE-Inadale, RWE-Roscoe, Loraine Windpark Phase 3 — these are OTHER developers' operating turbines (matches USGS uswtdb: 206 turbines built 2008-2011)
- **Implication:** Zeus/Spade Wind has NOT PURCHASED any Mitchell County land as of 2025 certified roll (dated 2025-08). Land is either (a) still under lease-option contracts (not titled to the SPV), or (b) does not exist yet. This is typical for a pre-IA wind project but is negative evidence for construction claims of "start 2025-08-01".
- Saved: sources/2026-07-18_mitchell-cad_2025-appraisal-roll.xlsx (6.3 MB, full county roll for reproducibility)

## Deep scan T7 — TX Comptroller JETI abatement registry
- Executed JETI agreements (comptroller.texas.gov/economy/development/prop-tax/jeti/current-agreements.php):
  - 11 agreements total (J0001-J0017 with gaps); none in Mitchell County, Colorado ISD, or Loraine ISD; no Spade/Zeus/Zeus Renewable applicant
  - Note: JETI excludes RENEWABLE POWER (per HB 5 statute — jet fuel, petrochem, semiconductor, biotech, but NOT wind/solar/battery). This project is INELIGIBLE for JETI abatement.
- JETI applications page: "We experienced a problem loading the data for this page" — could not retrieve pending applications
- Ch.313 expired 2022-12-31; 26INR0386 entered queue 2024 (too late for 313)
- Local abatement path (Ch.312) still available via county commissioners court — but Mitchell County site does not host agendas/minutes online
- No path to a county tax abatement for a post-2023 wind project other than local Ch.312 or PILOT — absence of a JETI application is expected, not a red flag

## Deep scan T8 — PUCT Interchange Filings Search (interchange.puc.texas.gov)
Direct search with browser UA succeeded (previous 402 was UA-blocked). Queried by Filing Party Name and Filing Description:
- FilingParty="Spade Wind": **0 record(s) found**
- FilingParty="Zeus Renewable": **0 record(s) found**
- FilingParty="Zeus Spade": **0 record(s) found**
- FilingParty="Spade BESS": **0 record(s) found**
- FilingDescription="Zeus Spade": **0 record(s) found**
- **No signed Interconnection Agreement filed with PUCT for this project by any variant of the party name.** Fully consistent with `iaSigned = null` in ERCOT queue milestone data.
- For a wind project reporting COD 2027-03-20, a signed IA at PUCT is a MANDATORY primary document — its absence at ~9 months to COD is a decisive paper-project signal.
- Saved: sources/2026-07-18_puct-interchange_spade-wind-0-records.html

## Deep scan T9 — Site imagery re-check
- FAA OE portal unavailable (T1) so no turbine-specific coords to re-center on. Wind sites span 20-30 km so widening from the initial grid is worthwhile.
- Attempted xwide (6 km buffer) reviewer chip at Morgan Creek POI center (32.3546, -100.9505) — CDSE auth failed (HTTP 401) on multiple retries. Existing triage imagery (9-chip grid, buffer 2 km, ±0.03° step at 32.32-32.38 x -100.92 to -100.98) covers ~18 km x 18 km around POI — enough of the POI vicinity to detect any turbine construction or pad-string; wind pads and access roads are conspicuous at 10 m/px against West Texas ranchland.
- Reviewer look at contact_sheet_2026-07.png (already produced during triage):
  - All 9 frames show undisturbed West Texas ranchland with existing farm/ranch fields, Colorado City Lake (E frames), one existing gray pad SW (visible in tile 32.32,-100.92 — appears to be an EXISTING industrial/oil-and-gas site, not new construction; no new access roads spoking from it)
  - NO new access-road networks, NO gray/tan graded turbine pads, NO substation construction
  - Reservoir + one industrial pad + ranchland only
- Verdict confirmed: **no_activity** — construction claim "start 2025-08-01" is not visible ~11 months later
- Moved triage frames to imagery/: contact sheet + center frame for the dossier

## Deep scan T10 — Synthesis
- Wrote findings.json + dossier.md
- Static Maps API 403 (not enabled) — no site_map.png in imagery/. Using Google Maps satellite URL as inline link instead.
- Running wrap-up: queue_history, build_brief, build_index
