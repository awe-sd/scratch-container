# Deep-scan Log — 28INR0089 EmberYork

## Triage carryover (from triage.md, 2026-07-18)

- ERCOT queue milestones: SS 2024-08-29 · FIS 2025-07-14 · IA signed 2025-12-12. COD 2028-01-01 stable, 0 drifts (19 snapshots).
- TEF loan DENIED — PUCT docket 56896. EYEC filed response 2025-04-16.
- IA in PUCT docket 35077 (CenterPoint Standard Gen IA, ~Dec 2025). PDF not yet retrieved.
- TCEQ air permit records show cover letter dID=8484637 — permit stage unknown at triage.
- Site candidate 132 Machala Rd, Sealy TX → 29.724109, -96.13698. 3×3 contact sheet (2026-07-01 ±20d, 2 km buffer): center = raw agricultural land. Pre-existing industrial sites ~3 km east/SE are UNRELATED (grid_05, grid_06, grid_08).

## Deep-scan turn log

### T1 — TEF denial docket 56896 (items 71/72/73)
- Pulled full 79-row PUCT xlsx export for docket 56896 → identified items 71 (denial), 72 (unrelated Lonestar), 73 (EYEC response).
- Downloaded 3 PDFs to sources/.
- **[2025-04-15 Order Denying Loan Application, item 71](sources/2025-04-15_puct_56896-71_order-denying-loan-app.pdf)** — 1-page order: "Application 131 submitted under sponsor name **EmberClear Management, Jupiter Island Capital**" has "failed to meet due diligence requirements", executive director denies, "**not subject to motions for rehearing or appeal**". Signed Connie Corona.
- **[2025-04-16 EYEC response, item 73](sources/2025-04-16_puct_56896-73_emberyork-response-to-denial.pdf)** — 1-page letterhead "EmberYork Energy Center LLC, 800 Town & Country Blvd Suite 500, Houston TX 77024". Signed by **Raj Suri (CEO EmberClear)**, **Peter Perri (Managing Partner Jupiter Island Capital)**, **Jon Cody (Managing Director Whitehall & Company)**. Contests denial, claims milestones met, urges reconsideration. Specific claims:
  - **"Receipt of the Final Air Permit (Standard Permit #1778571) on December 17, 2024"** — CONFIRMS TCEQ air permit issued (mandatory-doc box checked)
  - "Receipt of the Generation Interconnection Agreement (SGIA) in April 2025" — draft/preliminary IA in April; ERCOT queue records signed date 2025-12-12 (likely an executed/updated version)
  - "Selection of an EPC contractor and negotiation of a binding EPC agreement" — EPC not yet binding
  - "Ongoing negotiations with gas turbine suppliers, with binding proposals in progress" — **turbines NOT yet ordered** (paper signal; multi-year lead time)
  - "Loan Term Sheet C negotiated by Paul Hastings"
  - "First-round equity commitment letter and KYC documentation from a large power asset owner backed by a parent company with an 'A' credit rating"
- Item 72 (2025-04-15) = unrelated denial (Frontier / Lonestar Industrial Park LLC). Kept in sources/ but not linked in dossier.
- **Why it matters:** confirms hard denial with no cure path; EYEC still relying on unnamed A-rated equity partner and unordered turbines as of April 2025 — 8 months later (Dec 2025) IA signed. But no turbine order = no long-lead construction possible in 2026 = COD 2028 essentially impossible.

### T2 — Signed SGIA in PUCT docket 35077, item 2322 (filed 2025-12-11)
- Found via `FilingDescription=Ember` filter on 35077 export. Item 2322: "ERCOT STANDARD GENERATION INTERCONNECTION AGREEMENT BETWEEN CENTERPOINT ENERGY HOUSTON ELECTRIC, LLC AND EMBERYORK ENERGY CENTER WITH SGIA AMENDMENT PROVISIONS", filed by CenterPoint 2025-12-11.
- Downloaded 3 PDFs: [cover](sources/2025-12-11_puct_35077-2322_centerpoint-emberyork-IA-cover.pdf), [IA main body](sources/2025-12-11_puct_35077-2322_centerpoint-emberyork-IA.pdf) (100pp), [exhibits/attachments 62MB](sources/2025-12-11_puct_35077-2322_centerpoint-emberyork-IA-exhibits.pdf) (not fully parsed, contains drawings/H exhibits).
- **[Signed SGIA](sources/2025-12-11_puct_35077-2322_centerpoint-emberyork-IA.pdf)**, effective **2025-12-01**, DocuSign envelope 562A048A-DADE-49CE-885A-D4FD8CA9520D. Signed by Raj Suri (President, EmberYork) and Jesus Soto Jr (EVP & COO, CenterPoint).
- **POI (Exhibit C p.54)**: "TSP system side of Plant's terminating structure(s) located inside Generator's GIFSUB Substation located at approximately **29.724109 N -96.1369804 W**, in Austin County, Texas." — This matches the Machala Rd site EXACTLY (triage geocode was 29.724109, -96.13698). Delivery voltage 138 kV.
- **Plant (Exhibit C p.54)**: "2 natural gas-fired generators, total output 900 MW … Two **GE Frame 7HA** simple cycle gas fired turbine and **GE H84 generator** rated at approximately 583 MW [each]" — turbine OEM = **General Electric**, model **7HA.02** (implied by 583 MW rating), specific model numbers.
- **Facilities Study**: "Full Interconnection Study Report dated **February 12, 2025**" (Amendment Provisions Section 1.6).
- **Contractual schedule (Exhibit B, p.52)**:
  - Scheduled Start Date (Prerequisite Items — NTP, Security, CIAC due): **2026-12-12**
  - TIF In-Service Date: later of **2028-10-12** or 36 months after Prerequisite Items
  - Scheduled Commercial Operation Date: later of **2029-01-12** or 3 months after TIF In-Service
- **CRITICAL DRIFT**: ERCOT queue reports COD 2028-01-01, but the **signed IA schedules COD 2029-01-12** — a full year later. Reported COD is stale/misaligned with the executed agreement.
- **Financial security (Exhibit E, p.69)**: **Security Estimate = $99,157,000 (LC)**, due by 2026-12-12. Very large — reflects 138 kV interconnection cost for a 900 MW machine. Not yet posted (queue latest `financialSecurityAndNoticeToProceedProvided`="No" as of 2026-06-01).
- **CIAC (Exhibit C p.63)**: "Generator does not desire any enhancements … no CIAC required."
- **Access from Machala Rd (Exhibit C p.64)**: "access road(s) from public road Machala Rd to the TIFSB" — confirms the site is on Machala Rd, Austin County.
- **Why it matters:** confirms REAL contractual commitment — a real developer would not sign a $99M LC obligation for a paper project. Site coords exact. Turbines identified (GE 7HA — 3-year OEM lead time typical). But the signed schedule says 2029-Q1 COD, not 2028-Q1; ERCOT queue COD is stale. And the LC is not yet posted; if EYEC fails to post $99M by 2026-12-12, CenterPoint may terminate under Section 2.1.

### T3 — TCEQ air permit (dID=8484637)
- Downloaded TCEQ document dID=8484637 direct (via `GET_FILE`). 43 pages, filed **2024-12-12** by Trinity Consultants on behalf of EmberYork Energy Center LLC. [Application PDF](sources/2024-12_tceq_dID8484637_air-permit.pdf).
- **Standard Permit 6005 (SPEGU) registration application** for "two Simple Cycle Natural gas-fired combustion turbine generators (CTG)" at 132 Machala Road, Sealy TX 77474.
- Fee: $900 registration + $500 expedited (total $1,400) submitted via ePay. Expedited fee explains the 5-day turnaround to the EYEC-claimed permit-issue date of 2024-12-17.
- **TCEQ Core Data Form (p.42) coordinates**: 29°43'19.27" N, 96°08'21.48" W = **29.72202°N, -96.13930°W** — within ~300m of the IA POI (29.724109, -96.13698). Same site.
- Site classified minor for PSD/NSR (attainment area), major for Title V.
- Signed by Raj Suri (President & CEO EmberYork), Frank Wilson (VP Construction EmberClear).
- **Note:** The document is the APPLICATION, not the issued Standard Permit registration confirmation letter. EYEC's 2025-04-16 PUCT letter [claims permit #1778571 issued 2024-12-17](sources/2025-04-16_puct_56896-73_emberyork-response-to-denial.pdf); Standard Permit 6005 registrations are self-implementing on TCEQ acknowledgement, so the 5-day turnaround with expedited fee is plausible but I did not independently retrieve the confirmation letter (TCEQ Records Online search is JS-rendered and non-scrapable via curl).
- **Why it matters:** MANDATORY thermal-project doc box is CHECKED — the site has both an air permit application on file and a specific standard-permit registration number cited under oath in a PUCT filing. This alone rules out "paper project" verdict.

### T4 — Austin CAD owner search (2026 roll) — 0 developer parcels
- Endpoint `esearch.austincad.org/Search/SearchResults?keywords=OwnerName:<X>` — 6 owner-name variants (EmberYork, EmberClear, Ember, Jupiter Island, GIFSUB) ALL returned `totalResults:0`. Address search `PropertyAddress:Machala` also 0 (indexed by street). `StreetName:Machala` returned 15 parcels — no developer-owned. Saved [here](sources/2026-07-18_austincad_owner-search-empty.json).
- 132 Machala Rd (the address in the TCEQ application) is prop #16375, owner **ROSNIAK JOAN MARIE ET AL**, appraised $210,876 — a small residential/rural parcel. The site polygon per IA extends well beyond one parcel, so ROSNIAK is at best one adjacent landowner, not the full ~200 acre plant footprint.
- **Why it matters:** Land is NOT yet in the developer's name in the 2026 tax roll (roll cutoff Jan 1, 2026). Any option/lease is either off-record or held under a nominee. For a 900 MW thermal site targeting COD 2028, no recorded ownership 24 months before COD is a paper-project signal — but not fatal by itself (leases often precede recording).

### T5 — Google Places rate-limited (429), skipped
- Places API returned HTTP 429 on all queries. Skipped — site coords already come from the signed IA Exhibit C (29.724109, -96.1369804) as EXACT primary evidence; a Places pin would add no new information.

### T6 — Comptroller JETI (Ch.403 / HB5) — sister project EmberGreen J0028 filed, EmberYork NOT
- Queried Comptroller open-data API `api.comptroller.texas.gov/open-data/v1/tables/jeti` (list of all 38 JETI applications/agreements to date, JSON).
- **EmberYork: 0 entries** — no J-number for EmberYork Energy Center or Sealy ISD.
- **EmberGreen (sister 900 MW project, Wharton County): J0028** — Applicant "EmberGreen Energy Center LLC" (same officers Raj Suri + Peter Perri, same address 800 Town & Center Blvd Suite 500 Houston 77026), Wharton ISD, Fossil Fuel Electric Power Generation NAICS 221112. Application filed 2026-03-10; Comptroller Recommendation Packet issued 2026-04-15 (approved). Fetched [rec packet](sources/2026-04-15_comptroller_J0028_embergreen-wharton-jeti-recpkt.pdf) (148pp, 23MB).
- Attachment A summary (p.3): **Projected commencement of construction 2026, projected completion 2029, first year of incentive period 2030**, last year 2039. 75% M&O limitation. Performance bond $3,591,115. Estimated M&O tax benefit $35.9M.
- Also fetched [current JETI agreements page](sources/2026-07-18_comptroller_jeti_current-agreements.html) — confirms Sealy ISD has one JETI agreement (SIKA plastics J0011), NOT EmberYork.
- **Why it matters:** EmberClear absolutely knows the JETI path (they used it for the twin project). The absence of a matching Sealy ISD JETI filing for EmberYork means either (a) Sealy ISD declined to partner or (b) EmberYork strategy is not requesting it — either way, one lever of local financial support is unused. Also, the JETI-filed EmberGreen construction schedule (2026-2029, incentive from 2030) confirms EmberClear's *own* internal build timeline is 2029, not the 2028 shown in the ERCOT queue — aligned with the EmberYork IA's 2029-01-12 scheduled COD.

### T7 — Imagery re-confirm at IA POI coord (29.724109, -96.13698)
- Present-day center chip from triage grid (`grid_29.724109_-96.13698.png`, 2026-07-01 ±20d, 3km buffer) = undisturbed farmland with scattered rural residences, county roads, small water feature; NO industrial pad, laydown, cranes, or turbine-hall footprint. Copied to `imagery/key/s2_2026-07-01_center.png` for the brief.
- CDSE creds expired in this session (`~/.config/gis-research.env` is the example placeholder) — could not fetch a fresh 6-months-back "pre" chip. Given the site is undisturbed today, a pre chip would show the same undisturbed land. Verdict `no_activity` is safe on current evidence alone.
- No `gmaps.py staticmap` — API key project has Maps Static API disabled (HTTP 403). Site link uses Google Maps satellite URL in the dossier instead.
- **Why it matters:** as of 2026-07-01, ~30 months before the IA-scheduled COD (2029-01-12) and 18 months before the reported-COD-claim (2028-01-01), the site remains in its pre-development state. For a 900 MW simple-cycle plant (multi-year build, laydown-yard-first), reaching COD by 2028-01-01 from this base is not physically feasible.

### T8 — Austin County CAD abatement / commissioners court
- Web/Bing/DDG SERPs blocked (bot detection). No Austin County commissioners court agenda hits for EmberClear / EmberYork through the searches attempted. Recording as negative evidence: **no discovered Austin County Ch.312 abatement or commissioners-court resolution** for this project as of 2026-07-18. Combined with the JETI absence, EmberYork has no visible local tax-incentive package.


