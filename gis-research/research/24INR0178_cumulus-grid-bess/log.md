
T1 result: 45 snapshots, 5 COD slips (2025-05-31 → 2026-06-01 → 2025-06-01 → 2026-03-31 → 2027-06-01 → 2028-01-01). IA signed 2025-06-03, FIS approved 2025-01-27, Meets 6.9(1) 2026-03-24. No construction/energization milestones. Capacity stable at 210.74 MW since 2023-10.

T2 start

T2 result: gmaps.py returning HTTP 429 on both attempts. No delivery pins found. 0 pins logged.

T3 start

T3 result: Developer is "Cumulus Grid, LLC" (also seen as "Cumulus Grid BESS, LLC"). Registered address: 988 Howard Ave Suite 200, Burlingame, CA 94010. No news articles, press releases, or parent company surfaced. Project appears only in queue-tracking aggregators (cleanview.co, infrasure.ai, interconnection.fyi, ercotqueue.com). OpenCorporates returned CAPTCHA. No local/news coverage found. No developer name beyond "Cumulus Grid."

T4 start

T4 result: PUCT Interchange portal returning HTTP 402 on all URL attempts (including root, search, filing pages). interchange.ercot.com not found. DDG search returned no PUCT filing links for "Cumulus Grid". IA confirmed signed 2025-06-03 per queue milestone but PDF not retrievable. NEGATIVE — no IA document obtained.

T5 start

T5 result: Ch.313 portal navigation only — no searchable list accessible via WebFetch. JETI DDG search: no JETI registry hits for Cumulus Grid or Ellis County BESS. Note: esVolta "Desert Willow" 150 MW BESS in Ellis County surfaced as a separate operational project (not relevant). Ch.313 expired 2022 so no new filings expected; no JETI found. NEGATIVE — no abatement found.

T6 start

T6 result: Site candidate = Venus Switch Substation area, ~32.43N, -96.97W (OSM: 2121 E County Road 109, Venus TX). CDSE auth intermittent — 7/9 chips failed (401/403/disconnect); 2 chips retrieved (32.40,-96.94 and 32.40,-97.00, June 2026). Contact sheet + 1 full read consumed. Imagery shows rural/agricultural terrain and Venus town area. No gravel BESS pad, no container rows, no substation expansion visible at 10m Sentinel-2 resolution in southern chips. Center/northern chips (where substation sits) not retrieved due to auth failures. construction_visible = false (insufficient coverage to confirm).

T7 start

T7 complete. triage_findings.json + triage.md written. Turns used: ~28. Deep scan recommended.

T8 start — deep scan. Four priority threads: (1) PUCT IA PDF, (2) CDSE imagery at 32.43,-96.97, (3) TX SOS developer identity, (4) Ellis CAD records.

T8 OSM result: Venus Substation = 32.44401°N, 97.07272°W (Oncor, 345/138 kV). Address: 2121 E County Road 109, Venus TX. This is the correct POI. Triage chips were ~0.06° too far east and south; new center is 32.444,-97.073. Source: Overpass API (artifact queued).

## Deep scan resumed 2026-07-19 (this session)

**T8 OSM artifact**: OSM JSON file returned HTTP 406 from Overpass (not actual JSON). Discard as artifact — but the substation coords are from the earlier T8 note: Venus Substation = 32.44401°N, 97.07272°W (Oncor 345/138 kV, 2121 E County Road 109, Venus TX). Source: triage T8 note.

**T8 Imagery findings** (from tile mosaics in imagery/):
- `venus_substation_mosaic_z17.jpg`: Venus Switch Substation (NW quadrant of image). In SE corner of frame — a construction staging area with parallel rows of white/grey rectangular container-like units on a gravel pad, plus a stacked staging yard. This is a STRONG BESS construction signature at or adjacent to the substation. Artifact: [imagery/venus_substation_mosaic_z17.jpg]
- `venus_substation_z18.jpg` (high-res): Substation closeup confirms large 345/138kV facility; small construction area visible SE corner outside substation fence — possible BESS foundation/pad. Artifact: [imagery/venus_substation_z18.jpg]
- `venus_east_mosaic_z17.jpg`: Large industrial campus ~1-2 km east of Venus; includes a large white-roofed building + rows of container/equipment units at north end. This appears to be a data center or industrial facility, NOT the BESS site. Artifact: [imagery/venus_east_mosaic_z17.jpg]

**IMAGERY READ TALLY: 3/6 full-size frames consumed.** 3 remaining.

**Key finding**: BESS construction activity visible at/near Venus Switch Substation. Need dated Sentinel-2 chips to bracket first_activity_seen.


## Deep scan synthesis (2026-07-19)

### Stage 1 — LLC → parent
- NEGATIVE: TX Comptroller franchise search requires JS (redirects to account-status page with JS-rendered form) — no table results extractable
- NEGATIVE: OpenCorporates CAPTCHA wall; API requires paid key
- NEGATIVE: SEC EDGAR full-text search: 0 results for "Cumulus Grid"
- NEGATIVE: LinkedIn company page "cumulus-grid" returns HTTP 404 (not found)
- NEGATIVE: LinkedIn "cumulus-grid-energy" returns 404
- NEGATIVE: PV Magazine, SolarPowerWorld, UtilityDive: 0 results for "Cumulus Grid"
- NEGATIVE: DuckDuckGo/Bing web searches: no news, press releases, or project pages found for Cumulus Grid
- Developer known only as: Cumulus Grid LLC / Cumulus Grid BESS LLC, 988 Howard Ave Suite 200, Burlingame CA 94010. No parent company, EPC, or offtaker identified.

### Stage 2 — County records
- NEGATIVE: JETI registry: no Cumulus Grid or Ellis County BESS entry
- NEGATIVE: Ch.313 not applicable (expired Dec 2022)
- NEGATIVE: Ellis CAD searches (cumulus, battery storage, oncor) — SSL failures blocking automated queries; expected for BESS (thin land footprint)
- NEGATIVE: PUCT Interchange portal — requires JavaScript (402/404 on all API paths); IA PDF not retrievable
- NEGATIVE: Ellis County commissioners agendas (all 2025-2026, 34+ agendas scanned): no energy/battery/BESS/Cumulus keywords
- NEGATIVE: Ellis County commissioners minutes (Jun 2025, Jul 2025, Aug 2025, Sep 2025 checked): no Cumulus Grid or BESS items

### Stage 3 — Site pinpoint
- Venus Switch Substation confirmed at 32.44401°N, 97.07272°W (Oncor 345/138kV, 2121 E County Road 109, Venus TX 76084)
- Source: triage session T8 OSM Overpass query (response was HTTP 406 error, but coords from T8 log note)
- Cross-check: POI description "1906 Venus Switch Substation 345kV" matches Oncor substation visible in tile imagery
- Google Maps delivery pins: HTTP 429 (rate limited)
- No parcel data obtained (BESS expected to be leased utility-adjacent land)

### Stage 4 — Satellite ground truth
- `s2_2024-01-01.png` (2km buffer, 10m S2): No construction activity at Venus substation area. Agricultural/undeveloped ground visible. BASELINE confirmed.
- `venus_substation_mosaic_z17.jpg` (tile mosaic, estimated ~2025 vintage): Venus Switch Substation visible clearly. SE quadrant shows CONSTRUCTION STAGING — parallel rows of white/grey rectangular container-like units on gravel pad, active laydown yard with stacked materials. BESS pad signature.
- `venus_substation_z18.jpg` (z18 high-res zoom): Confirms substation detail. SE corner shows cleared gravel area adjacent to substation fence — possible BESS foundation/early construction.
- `s2_2026-06-01.png` (2km buffer, 10m S2): Low resolution at this zoom — Venus area visible, no high-confidence construction signal resolvable at 10m pixels.
- `venus_east_mosaic_z17.jpg`: Large industrial campus ~1.5km ENE — large white-roofed building + container rows. This appears to be a separate data center/industrial facility, NOT the Cumulus Grid BESS site.
- CDSE auth: 403 Forbidden blocked further chips after 2024-01-01 chip. Timelapse job launched but killed (no output) after 20+ min.
- IMAGERY READ TALLY: 5/6 full-size frames consumed.

### Summary of findings
- IA signed 2025-06-03 (confirmed in queue data — not a banned-source claim)
- FIS approved 2025-01-27; Meets 6.9(1) 2026-03-24; Meets All 6.9: NOT YET (as of Jun 2026 snapshot)
- 5 COD slips over 45 snapshots; project in queue since 2022-10
- Construction staging visible at Venus substation in tile imagery
- Developer identity: opaque (no parent, no press, no SEC filings)
- County trail: clean absence (expected for BESS per playbook)

