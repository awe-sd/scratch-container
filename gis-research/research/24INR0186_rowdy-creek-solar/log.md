# Triage log — Rowdy Creek Solar (24INR0186)

T1 start
- queue_history.py ran: 54 snapshots, 5 COD-drift changes
- IA signed: 2025-05-02 ✓; Meets 6.9(1): 2025-07-29 ✓; FIS approved: not yet; no construction dates
- COD drift: 2024-06-01 → 2024-12-31 → 2025-05-31 → 2026-03-10 → 2027-04-01 → 2027-12-29 (current)
- Capacity halved mid-2024: ~715 MW → 351.78 MW (July 2024 snapshot)
- IA signed — project has real financial commitment; 2027-12-29 COD is plausible but heavily drifted
T1 end

T2 start
- gmaps.py blocked: HTTP 429 on all attempts (rate-limited); 1 retry attempted per rule 5
- No delivery pins obtained — normal result, not a signal
T2 end

T3 start
- DDG: CAPTCHA blocked on both queries (no retry — rule 5)
- Bing: 3 queries for "Rowdy Creek Solar", "Rowdy Creek Solar" + Texas, "Rowdy Creek Solar" + ERCOT — zero results; search defaults to word definitions
- No developer name, LLC registration, or news surfaced
- Project has essentially no public web footprint
T3 end

T4 start
- PUCT Interchange: HTTP 402 on all endpoints (FilingParty, description, base search) — portal blocked
- No IA PDF or milestone-schedule exhibit retrievable during triage
- IA signed 2025-05-02 per queue record — IA exists but content not accessible here
T4 end

T5 start
- TX Comptroller Ch.313: search portal not directly queryable via WebFetch (no data returned from overview pages)
- Bing search for Lamar County solar + Ch.313/JETI: no results
- JETI registry: not directly checked (JETI replaced Ch.313 post-2022; project entered queue Jan 2022)
- No abatement found — normal: Ch.313 expired Dec 2022; JETI eligible but no filing surfaced
T5 end

T6 start
- No pin from T2; no abatement/IA map from T4/T5
- POI "Woodfin Switch (#1465) 345kV" — substation location search: 2 Bing queries returned no coordinates
- Best site estimate = "somewhere in Lamar County" — below threshold for imagery
- SKIPPING imagery per checklist rule: no site candidate
T6 end

T7 start
- triage_findings.json written
- triage.md written
- Total turns used: ~22
T7 end

## Deep Scan — 2026-07-19

### Stage 1 — LLC → parent chain
DS-1 start
- Searching TX Comptroller taxable entity search for "Rowdy Creek Solar"
- Parallel: PUCT Interchange retry for IA filing
- Parallel: TX SOS / EDGAR for developer chain

DS-1 findings:
- Developer: Parliament Energy (parliamentenergy.com) — confirmed Rowdy Creek Solar in portfolio
  Source: parliamentenergy.com homepage + /rowdy-creek page
- Parent chain: Parliament Energy Holdings LLC → EnCap Investments L.P. (Energy Transition Fund II) + Mercuria Energy Group (co-backer)
- Project specs per Parliament Energy website: 455 MWdc / 350 MWac, Q4 2027 COD, Lamar County TX
- Project area: **6 sq miles (~3,840 acres)**, 0.8M panels, 525 mi trackers — from parliamentenergy.com/rowdy-creek
- Parliament Energy track record: Parliament Solar 640 MWdc completed early 2025 (Texas); Tehuacana Creek Solar $747M non-recourse financing closed June 2026
- EnCap's total portfolio: "2.7 GWdc portfolio of contracted utility-scale solar assets"
- PUCT Interchange: HTTP 402 on all attempts (both triage and deep scan) — portal remains blocked
- TX Comptroller taxable entity: search form only (JS-rendered, not queryable via WebFetch)
- TX SOS SOSDirect: paid ($1/search), cannot access
- EDGAR: HTTP 403
DS-1 end

### Stage 2 — County records / PUCT IA
DS-2 start
IA FOUND and downloaded: sources/2026-07-19_puct_35077-2148_oncor-rowdy-creek-solar-IA.pdf (1.6 MB, 52 pp)
Signed: May 2, 2025; filed with PUCT May 30, 2025; Control No. 35077, Item 2148

Exhibit B — Time Schedule:
- In-Service Date: April 15, 2027
- Trial Operation: May 3, 2027
- Scheduled COD: July 18, 2027  ← NOTE: diverges from queue 2027-12-29 (suggests amendment may exist)
- Notice-to-proceed deadline: May 5, 2025

Exhibit C — Interconnection Details:
- POI: Woodfin Switching Station (Woodfin Switch), in Paris Switch – Valley Switch 345 kV line
- Location: "Lamar County, Texas... west of Paris, TX" (CEII: station coordinates redacted)
- Solar: 96 × Power Electronics HEM FS4200M inverters, 388.8 MVA total, 351.78 MW net (24INR0186)
- BESS: 48 × Power Electronics PCSM FP4200M inverters, 194.4 MVA, 175.89 MW net (24INR0187)
- County road: creek crossing to be improved by Generator (road name redacted)
- TSP builds Woodfin Switch (new greenfield); Generator grades the site

Exhibit D — Contacts:
- Generator: Rowdy Creek Solar LLC, Attn: Geoffrey Dewhurst, 9651 Katy Freeway, Houston TX 77024
  Email: Dewhurst@parliamentenergy.us  ← confirms Parliament Energy is developer
- O&M operator: NovaSource Control Room (NSCR), Phone: (877) 375-7662, NSCR-Ops@novasourcepower.com
- TSP: Oncor Electric Delivery, Robert Holt, 777 Main St Suite 707, Fort Worth TX 76102

Exhibit E — Security: Irrevocable Standby LC required by May 5, 2025; amount not shown in extractable text (redacted per letter p.2)

Developer chain confirmed: Rowdy Creek Solar LLC → Parliament Energy (parliamentenergy.us) → EnCap Investments LP (Energy Transition Fund II) + Mercuria Energy Group

CAD (Lamar County esearch.lamarcad.org): search forms not queryable via WebFetch (JS-rendered, 404 on parameter URLs); 0 parcels returned
JETI: TX Comptroller not queryable via WebFetch
DS-2 end (partial — need amendment search, CAD alternative, site pin)

DS-2 additional findings (abatement):
- Tax Abatement Agreement (Ch.312): Lamar County + Rowdy Creek Solar LLC (Delaware LLC)
  Signed: May 30, 2023 by Jeffrey Sabins, CDO, Solar Proponent LLC (Sole Member of Rowdy Creek Solar LLC)
  Source: sources/2026-07-19_lamarcounty_rowdy-creek-solar-PILOT-2023-05-22.pdf
- COD deadline in abatement: July 31, 2027 (cancellation remedy if missed)
- Project scope: ~500 MW AC solar + ~500 MWh storage; minimum 450 MW AC solar
- Abatement: 100% county property tax abated for 10 years (replaced by PILOT payments)
- PILOT: $1,576/MW AC/yr solar + $620/MWh storage; one-time $30,000 fee
- Tenure: LEASED (landowner agreements noted; "Solar Proponent LLC" as sole member)
- County roads used: CR 35200, 35620, 34050, 35010, 35020, 35080, 35100, 35030
- CR 35200 locates near Sumner, TX (33.74°N, 95.67°W) — west-central Lamar County, ~20 mi WSW of Paris
- Consistent with IA: "west of Paris, TX" + Paris Switch – Valley Switch 345kV line
- Attachment C (site legal description): referenced but images too small to read metes-and-bounds

### Stage 3 — Site pinpoint
DS-3 start
- Best estimate: Sumner TX area, 33.74N, 95.67W (from CR 35200 abatement road list + "west of Paris" IA description)
- gmaps.py: HTTP 429 — rate blocked, no pins returned
- Woodfin Switch: not in OSM; site is WEST of Paris per IA (Paris Switch - Valley Switch line, new tap)
- Paris Switch is near Paris TX (Lamar County); Valley Switch location unknown
- Site is ~20 mi WSW of Paris TX; Woodfin Switch is new greenfield substation built by Generator on project land
DS-3 (partial)

### Stage 4 — Satellite imagery
DS-4: CDSE credentials not configured (example placeholder only) — imagery run not possible.
GEM Wiki (Global Energy Monitor, July 2026): project listed as "pre-construction" as of ~6 days ago.
Stage 4 verdict: pre-construction / no_activity confirmed by third-party tracker; imagery not independently verified.
NEGATIVE EVIDENCE: no construction news, no delivery pins, no EPC announcements; GEM pre-construction tag July 2026.

### Stage 5 — Synthesis
Key tension: IA contractual COD = July 18, 2027 but queue shows 2027-12-29 (5.5-mo gap).
Two explanations: (a) an IA amendment bumped COD to Q4 2027 (not retrievable from PUCT — 402 blocked), or (b) the queue drifted post-IA. Given 5 prior slips, likely the queue reflects developer's revised internal target.
NTP deadline per IA was May 5, 2025. If NTP was given, grading should have started by late 2025. No evidence of grading. GEM pre-construction as of July 2026 = ~14 months past NTP deadline with no visible construction → HIGH slip risk.
Independent estimate: 2028-Q2, drift risk HIGH.
DS-5 end
