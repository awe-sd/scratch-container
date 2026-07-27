# Research Log — Hanson Solar (23INR0086)

---
## TRIAGE PASS — 2026-07-18

T1 start
- `queue_history.py` + `timeline.md` read. COD drift: 3 changes (2024-05-31 → 2025-10-21 → 2027-01-28 → 2027-04-17). Current COD 2027-04-17 stable 26 months. Milestones: IA signed 2023-09-20, Meets 6.9(1) 2025-02-12, FIS approved 2026-03-26 (recent). Meets all 6.9 = NOT YET. No construction-end or approval milestones in queue data.
T1 done (2 tool calls).

T2 start
- Prior research (log below) already covered gmaps places. Results: pin "TIC Hanson solar" at 31.692543,-99.548231 (Valera TX, Coleman County). 1 confirmed pin, EPC = TIC/Kiewit registered under this name.
T2 done (0 new tool calls — referenced prior results).

T3 start
- Prior research covered web sweep. Developer = Cypress Creek Renewables (CCR); SPV = Hanson Solar LLC. Offtake = Meta. Financing closed Nov 2025; construction mobilized 2025; COD target mid-2027. Sources saved in sources/. news_found = true.
T3 done (0 new tool calls — referenced prior results).

T4 start
- Prior research found PUCT Interchange Control 35077: original IA (35077-1682, filed 2023-10-13) + Amendment No. 1 (35077-1899, filed 2024-08-15). Amendment schedule: In-Service 2026-12-03, Trial Op 2026-12-17, COD 2027-04-17. Exactly matches reported COD. ia_found = true.
T4 done (0 new tool calls — referenced prior results).

T5 start
- Prior research: TX Comptroller Ch313 agreement ID 1698, executed 2022-11-14, 396 MW, Panther Creek CISD, Coleman County. Annual Form 772 reports filed 2023–2025. abatement_found = true.
T5 done (0 new tool calls — referenced prior results).

T6 start
- Prior research: site center at 31.6950, -99.5315 (imagery feature match + IA text + Places pin cross-validation). Sentinel-2 timelapse 2024-07→2026-07: first activity 2025-04 (substation pad); site-wide grading complete ~2025-09; panel/racking installation ambiguous-but-plausible from 2026-03. As of 2026-07 reads as late-stage civil / early electrical. construction_visible = true.
T6 done (0 new tool calls — referenced prior results).

T7 start — writing triage_findings.json + triage.md.
T7 done. triage_findings.json + triage.md written. Turns used: 10. STOP.

---
## PRIOR DEEP-RESEARCH RECORD (2026-07-17)

Date convention: all entries 2026-07-17 unless noted.

## Stage 3 (done first per playbook advice — delivery pin trick)

- Source: gmaps.py places, query: "Hanson Solar" → NO MATCH (returned "Hansen Solar Energy", Charlottetown PE Canada — unrelated business, name collision). Outcome: negative.
- Source: gmaps.py places, query: "Hanson Solar LLC" → HIT: "TIC Hanson solar" | 6725 FM503, Valera, TX 76884, USA | 31.692543,-99.548231 | tags: point_of_interest,service,establishment. Outcome: POSITIVE — construction-site delivery pin.
- Source: gmaps.py places, query: "Hanson Solar Coleman County Texas" → same HIT (TIC Hanson solar, Valera TX). Outcome: confirms.
- Source: gmaps.py places, query: "Hanson Solar Project construction" → same HIT. Outcome: confirms.
- Source: gmaps.py places, query: "Hanson Solar Farm" → same HIT. Outcome: confirms.
- Source: gmaps.py places, query: "TIC Hanson Solar" → same HIT. Outcome: confirms; pin name itself is "TIC Hanson solar" implying EPC contractor TIC (The Industrial Company) has registered a site pin under this name.
- Source: gmaps.py places, query: "Hanson Solar Valera Texas" → same HIT.
- Source: gmaps.py places, query: "Hanson Solar substation" → NO MATCH (returned unrelated Hansen Solar Energy Canada result again). Outcome: negative.

Valera, TX is an unincorporated community in Coleman County, TX — consistent with the identity packet's county field. This is a strong independent (non-queue-tracker) confirmation the project is real and under active development, since EPCs register Google Maps pins for delivery/site logistics during active construction, not for paper-stage projects.

## Stage 1 — Web search: LLC / developer identity

- WebSearch: `"Hanson Solar" LLC Coleman County Texas` → HIT. Multiple independent (non-banned) sources: colemancountytexas.com business directory, TX Comptroller Ch313 PDF (assets.comptroller.texas.gov/ch313/1698/1698-panther-hanson-appsupp1.pdf), colemantoday.com news, ktxs.com news, pv-magazine-usa.com, prnewswire.com, energytech.com, solarpowerworldonline.com, energymonitor.ai. (Also surfaced banned aggregator cleanview.co in result list — NOT clicked/cited, noted only as excluded.)
  - Developer: **Cypress Creek Renewables (CCR)** — Hanson Solar, LLC is CCR's project-specific SPV.
  - Offtake: Meta (Facebook parent) — environmental-attribute/PPA-style deal for the project, publicized March 2025 (pv-magazine-usa.com) and financing-close Nov 2025 (prnewswire.com).
  - Capacity variously reported 396 MW (AC, matches Ch313 filing) / 505 MWdc.
- WebSearch: `TIC "The Industrial Company" solar Coleman County Texas EPC` → HIT. TIC – The Industrial Company (subsidiary of Kiewit Corporation) confirmed as EPC contractor. Matches the Google Places pin name "TIC Hanson solar".
- WebSearch: `"Hanson Solar" Brown Central Bluff 345kV interconnection` → surfaced only banned aggregators (interconnection.fyi, cleanview.co) for the specific POI phrase — NOT used. Confirmed 345 kV / Brown-Central Bluff details independently via the PUCT interconnection agreement instead (see below).

### Saved sources (sources/):
- 2026-07-17_prnewswire_cypress-creek-hanson-solar-financing.html — PR Newswire, Nov 2025: financing close, EPC = TIC (Kiewit subsidiary), "construction was mobilized earlier this year" (2025), "reach commercial operation in mid-2027", debt from MUFG/SMBC, preferred equity from unnamed global credit manager.
- 2026-07-17_comptroller_ch313_hanson-solar-panther-creek-cisd.pdf — Ch313 Tab 7/8 attachment: 396 MW, ~1,240,504 PV modules, 104 inverters, Coleman County.
- 2026-07-17_comptroller_ch313_1698-hanson-app-main.pdf — full 42-page Ch313 application (filed 2022) incl. maps (Tab 11): shows "Leased land border" (land tenure = LEASED, not owned), project boundary map near Valera/Panther Creek CISD south of Coleman, substation location, and Tab 4 saying original 2022 timeline anticipated "construction ... Q1 2027 with completion by December 31, 2027" (this original schedule was later ACCELERATED — see PUCT IA below, which shows the executed schedule was actually earlier then slipped back).
- 2026-07-17_colemantoday_meta-linked-solar-valera.html — local news: 3,000 acres near Valera, 1.24M panels, 104 inverters + BESS, 345 kV line to ERCOT, "expected to break ground later this year" (article contemporaneous with 2025).
- 2026-07-17_colemancountytexas_business-directory-hanson-solar.html, 2026-07-17_ktxs_hanson-solar-tax-revenue.html — corroborating local coverage.
- 2026-07-17_ticus_markets-power.html, 2026-07-17_pvmagazine_meta-signs-more-texas-solar.html — Cloudflare-blocked on curl (saved as evidence of blocked fetch attempt; content obtained instead via WebFetch/WebSearch snippets above).
- hanson_map_p23.png, hanson_map_p24.png, hanson_map_p26.png etc. — rendered page images from the Ch313 application PDF (Tab 11 Improvements Map / Vicinity Map, Tab 12 waiver letter), extracted via PyMuPDF since poppler-utils unavailable in container.

### TX Comptroller Ch313 agreement docket (WebFetch, comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id=1698):
- Application filed 02/24/2022 (school board accepted 01/18/2022); amendments/supplements through 06/2022; **agreement executed 11/14/2022**.
- **Annual Form 772 eligibility reports filed 2023, 2024, 2025** (most recent filings dated 01/08/2026, 02/06/2026) — a project that is paper-only does not generate multi-year real compliance-reporting history with a school district; this is independent evidence of an ongoing, monitored real project.

## Stage 1/3 — PUCT Interchange interconnection-agreement filings (primary, non-aggregator source; added to playbook mid-task)

- Source: https://interchange.puc.texas.gov/ — form-based filing search (`/search/search/` GET endpoint; fields `FilingParty`, `Description` (case style), `FilingDescription`).
- Query: `FilingParty=Hanson Solar` → 0 records. Query: `FilingParty=Hanson` → 29 records (unrelated telecom "Hanson dba Sanderson Communications" and various). Query: `Description=Hanson Solar` (case style) → 0 records (IAs aren't docketed as their own case; they're informational filings under a standing docket).
- Query: `FilingDescription=Hanson Solar` → **1 record: Control Number 35077** — "INFORMATIONAL FILING OF ERCOT INTERCONNECTION AGREEMENTS PURSUANT TO SUBST. R. §25.195(e)" (Oncor's standing docket for filing all its ERCOT IAs). 2 filings under Hanson Solar within it.
- Filing 35077-1682 (filed 10/13/2023 by ONCOR ELECTRIC DELIVERY COMPANY LLC): "Interconnection agreement between Oncor Electric Delivery Company LLC and Hanson Solar, LLC" — the **original executed IA**, dated September 20, 2023, covering GINR **23INR0086 (Hanson Solar) & 24INR0057 (Hanson Storage)**. References a Facilities Study Agreement executed 10/6/2021 between the parties (project has been in TSP-level development since at least 2021).
  - Saved: sources/2026-07-17_puct_35077-1682_oncor-hanson-solar-IA.pdf (51 pp; downloaded directly from interchange.puc.texas.gov/Documents/35077_1682_1337695.PDF).
  - Exhibit B (original, 2023): In-Service Date May 8, 2025; Trial Operation May 20, 2025; **Scheduled Commercial Operation Date October 21, 2025**.
  - Exhibit C (Interconnection Details): "Point of Interconnection is located in Coleman County, Texas, at the **Fisk Switch** within TSP's **Brown Switch – Central Bluff Switch 345 kV Transmission line**... The Fisk Switch will be located **approximately 12 miles southwest of Coleman, TX directly west of CR 362**." Generating units: Solar — 104x SMA SC 4400UP-US inverters, nameplate 457.6 MVA dispatched at 396 MW; co-located Storage — 79x Tesla Megapack inverters, nameplate 118.5 MVA dispatched at 101.39 MW.
- Filing 35077-1899 (filed 8/15/2024 by Oncor): "Amendment No. 1 to the Standard Generation Interconnection Agreement ... (Fisk Switch) (Hanson Solar & Hanson Storage)", executed June/July 2024 (DocuSign).
  - Saved: sources/2026-07-17_puct_35077-1899_oncor-hanson-solar-IA-amend1.pdf (10 pp).
  - Replaces Exhibit B: In-Service Date **December 3, 2026**; Trial Operation **December 17, 2026**; **Scheduled Commercial Operation Date April 17, 2027**.
  - **This EXACTLY matches the reported/claimed COD given in the identity packet (2027-04-17)** — independently confirmed from the primary, signed TSP interconnection-agreement amendment, not from any queue tracker.
  - Note: this is the SECOND schedule in the IA's history — the original Sept-2023 IA had COD Oct 21, 2025, an ~18-month slip to the amended April 2027 date executed less than a year later. One slip already baked in before construction start; relevant to drift-risk assessment even though the current contractual date is corroborated.
  - Letter of credit security amounts: $11.3M effective 11/8/2023, rising to $13.4M by 12/3/2025 — real financial security posted with the TSP, another real-project signal.


## Stage 4 — Satellite ground truth (Sentinel-2, cdse.py)

### Site framing note (important correction mid-task)
- Initial narrow chips (buffer 1.6km) centered on the Google Places delivery pin (31.692543,-99.548231) showed only bare/natural farmland at all dates 2023-01 through 2025-11 — this was MISLEADING: a wide chip (buffer-km 6) revealed the actual ~3,000-acre project footprint sits centered roughly 1.5-2km NE of the delivery-pin coordinate, matching the Ch313 "Improvements Map" polygon shape almost exactly (irregular L-shaped boundary with a notch at the north end where the Improvements Map marks the substation).
- Refined site center used for all subsequent imagery: **lat 31.6950, lon -99.5315** (derived by pixel-matching the visible cleared/graded polygon in a wide Sentinel-2 chip against the Ch313 Tab-11 Improvements Map boundary shape — method = imagery feature, cross-validated against: (a) Places pin ~2km SW, (b) PUCT IA text "Fisk Switch ~12mi SW of Coleman, TX, directly west of CR 362", (c) OSM hamlet "Fisk" node at 31.6710,-99.4892 ~3.4mi ENE. All four independent references cluster within a ~3.5 km radius south of Coleman near Valera/Fisk — cross-check consistent, no material disagreement).
- Saved: imagery/s2_2026-07-10_xwide.png (12km box) and imagery/crop_project_area.png (2x zoom crop) — the frame used to confirm the boundary-shape match.

### Timelapse (single openEO job, `cdse.py timelapse`, lat 31.6950 lon -99.5315, buffer-km 3):
- Monthly series 2024-07-01 → 2026-07-01 (25 frames) + imagery/timelapse.gif — saved as imagery/s2_YYYY-MM-01.png.
- Dekad series 2026-04-15 → 2026-07-17 requested for fine-grained recent progress (construction confirmed active) — see below.

### Frame-by-frame read (substation-pad crop at polygon's north notch, pixel box (380,150)-(600,350)):
- 2024-07-01, 2024-11-01, 2025-01-01, 2025-02-01, 2025-03-01: all show undisturbed natural terrain / pre-existing small farm field only. NO construction activity visible.
- **2025-04-01: first clear construction signal** — a bright, reflective, L-shaped graded pad appears exactly at the substation location marked on the Ch313 Improvements Map. This is the tightest bracket available: activity absent 2025-03-01, present 2025-04-01.
- 2025-06-01 (full-frame): clearing/grading has expanded to cover roughly the southeastern half to two-thirds of the project polygon (large light-tan graded area, internal parcel roads visible).
- 2025-09-01: grading now extends across nearly the entire polygon footprint, including the northern portion that was still natural in June.
- 2025-12-01: internal grid/road pattern sharper; small green patches appearing (likely new ground cover/seeding on completed grading).
- 2026-03-01: darker, more uniform rectangular patches appear within the graded area (candidate early racking/panel rows, though at 10m Sentinel-2 resolution this cannot be distinguished with full confidence from bare damp soil or shadow).
- 2026-07-01 / 2026-07-10 (most recent): graded/bare-earth footprint now covers essentially the whole ~3,000-acre boundary; multiple small light-colored structures visible (plausible inverter/transformer pads); some larger dark uniform blocks in the south-central section are the best candidate for installed racking/panels, but not confirmed at this resolution. No unambiguous full-field panel signature (the uniform blue-gray block appearance expected of a completed utility-scale solar farm) is yet visible — site reads as **late-stage civil works / early electrical installation**, not "substantially complete" or "operating."

### Verdict (Stage 4): **clearing → racking (transitioning)**, first_activity_seen = **2025-03/2025-04** (substation pad), site-wide grading essentially complete by ~2025-09, panel/racking installation ambiguous-but-plausible from ~2026-03 onward. Consistent with a Dec-2026 In-Service Date / April-2027 COD trajectory — construction pace so far tracks the amended IA schedule, not a project standing still.

## Stage 2 — CAD parcel sweep (Coleman CAD, colemancad.net)

- Site form action `/Home/Search?SearchOption=basic&Keyword=...`; underlying results endpoint `/Home/SearchTable...` returns JSON with a `count` field.
- Query Keyword=`Hanson Solar` → **count:0**. Query Keyword=`Hanson` → count:0. Query Keyword=`Cypress Creek` → count:0. Query Keyword=`Cypress Creek Renewables` → count:0.
- Outcome: **no parcels in Coleman CAD under the LLC or developer name** — this is the EXPECTED result for a leased-land project (confirmed leased via Ch313 Improvements Map "Leased land border" label and Tab 9 "Not Applicable" = applicant does not own the land). Underlying ranch parcels remain on the tax roll under original landowner names, which were not identifiable from the packet and were not guessed/fabricated.
- WebSearch: `Coleman County commissioners court minutes Hanson Solar` → surfaced a 2020-dated colemantoday.com article "County Commissioners to Hear Solar Farm Proposal" — NOT used/cited, since article date (~2020) predates Hanson Solar's earliest documented activity (Facilities Study Agreement Oct 2021, Ch313 application Jan 2022) and cannot be confirmed as the same project; flagged as an ambiguous lead, not evidence.

## Stage 1 (follow-up) — TX Comptroller taxable entity search / SOS
- mycpa.cpa.state.tx.us/coa/ redirects to comptroller.texas.gov/taxes/franchise/account-status/search, a JS-driven tool not scriptable via curl/WebFetch in this environment.
- WebSearch: `"Hanson Solar, LLC" Texas registered agent OR "series" OR opencorporates` → no OpenCorporates or free SOS record surfaced for this specific entity (TX SOS filings require a paid SOSDirect account for full-text/entity lookup — out of scope for free-tool research). LLC→parent chain instead established via convergent press/primary-source evidence: PR Newswire + Cypress Creek's own site + Ch313 filings all state Cypress Creek Renewables (CCR) is the developer/owner/operator and Hanson Solar, LLC is CCR's project SPV.

## Additional corroborating sources saved
- 2026-07-17_constructionreviewonline_hanson-solar-construction-start.html — "Construction and commissioning are scheduled from 2026 to H1 2027, with commercial operation targeted for around mid-2027" (secondary paraphrase of the Nov 2025 CCR release; treated as lower-weight than the primary PUCT IA schedule, which is more precise and is the evidentiary basis used in findings.json).
- 2026-07-17_cypresscreekenergy_hanson-solar-financing-official.html — attempted fetch of Cypress Creek's own press release page; returned HTTP 403 (Cloudflare) — saved as evidence of blocked attempt only, not used as a cited source (content already corroborated via the PR Newswire syndication of the same release).

## Negative-search tally (for findings.json)
1. gmaps places "Hanson Solar" → wrong business (Hansen Solar Energy, Canada)
2. gmaps places "Hanson Solar substation" → same wrong business
3. WebSearch "Hanson Solar" Brown Central Bluff 345kV interconnection → only banned aggregators surfaced, none usable
4. PUCT FilingParty=Hanson Solar → 0 records
5. PUCT Description(case style)=Hanson Solar → 0 records
6. PUCT Description=Hanson Solar (exact re-check) → 0 records
7. Coleman CAD Keyword=Hanson Solar → 0 records
8. Coleman CAD Keyword=Hanson → 0 records
9. Coleman CAD Keyword=Cypress Creek → 0 records
10. Coleman CAD Keyword=Cypress Creek Renewables → 0 records
11. Overpass "Fisk" broad bbox query → HTTP 504 timeout (retried narrower, succeeded)
12. WebSearch "Hanson Solar, LLC" Texas registered agent / OpenCorporates → no entity-specific record found
Total negative searches logged: 12. Banned-source violations: 0 (interconnection.fyi and cleanview.co surfaced in generic result lists multiple times; never opened/cited/used as evidence).

---
## D5 WRAP-UP — 2026-07-20

- queue_history.py 23INR0086 → timeline.md refreshed (64 snapshots, 3 COD changes confirmed)
- eia_history.py 23INR0086 --write → eia_history.json refreshed; EIA plant 67657 'Hanson' / Cypress Creek Renewables; planned COD shifted 2026-09→2027-07 (Sep 2025); status still '(L) Regulatory approvals pending' through 2026-05 (EIA reporting lag behind physical construction)
- build_brief.py → brief.html regenerated (12 KB, 4 images, 33 sources)
- build_index.py → index refreshed (130 projects)
- findings.json updated to full schema: added project_area (3,000 acres), site.map_artifacts, contractual_schedule.documents (per-doc security amounts)
- EIA divergence noted: queue COD 2027-04-17, EIA says 2027-07 (+1 quarter) — minor, within noise, not a red flag
- No new sources fetched; all prior deep-scan artifacts intact
