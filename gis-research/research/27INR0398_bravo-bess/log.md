# Triage log — Bravo BESS (27INR0398)

## T1 start
- queue_history.py run: 20 snapshots (2024-11-01 → 2026-06-01)
- COD drift: 1 change (2027-12-08 → 2027-12-12, 4-day shift)
- Milestones achieved: Screening started 2024-11-26, Screening complete 2025-02-18, FIS requested 2024-11-21
- Milestones NOT achieved: FIS approved, IA signed, 6.9(1), all 6.9, construction start/end, energization, sync, COA
- Assessment: Early-stage project. FIS study in progress (requested but not approved). No IA yet.

## T2 start
- gmaps.py blocked: HTTP 429 on both attempts (rate-limited). No pins found.
- T2 result: 0 pins.

## T3 start
- DDG search "Bravo BESS battery Texas": found LLC name confirmed as "Bravo BESS LLC"; also found separate "18-Bravo BESS" in Hunt County (407MW, different project) and a Zapata County listing (200MWac)
- TX SOS data: Bravo BESS LLC, foreign LLC (Delaware), incorporated 2024-09-24, file #0805720787, registered at 1501 S Mopac Expy Ste 220 Austin TX 78476, agent: Capitol Corporate Services, Inc.
- Related entity: "OCI San Antonio Bravo BESS LLC" (same date, same type) — strong signal OCI is parent/developer
- Zapata County abatement notice: $88M improvements for electricity storage (NOTE: this is Zapata County, NOT Webb County — different sub-project)
- No press releases or news specifically about the 27INR0398 Webb County project
- DDG captcha/rate-limit hit on OCI follow-up searches; no further developer info obtained
- T3 result: developer = OCI (likely OCI Solar Power LLC or similar, San Antonio HQ); news_found = false for this specific project; abatement in Zapata County but not Webb County

## T4 start
- PUCT interchange.puc.texas.gov: HTTP 402 on all URL patterns tried (FilingParty=Bravo BESS, description=27INR0398). Portal blocked — no puct_interchange.py script available.
- No IA found in T4. Expected at this stage: FIS not yet approved, so IA would not exist yet.
- T4 result: ia_found = false (consistent with queue milestone status).

## T5 start
- TX Comptroller Ch.313: portal pages returned generic overview only, no Webb County BESS entries found
- JETI registry: same result — portal redirected to overview page
- DDG search for Webb County Ch.313/JETI: CAPTCHA block, no results
- Note: Zapata County abatement for Bravo BESS LLC ($88M) found in T3 — that is a different sub-project
- Ch.313 expired 2022; Webb County project INR'd 2024 — normal for no abatement to exist
- T5 result: abatement_found = false for Webb County (as expected for post-2022 project)

## T6 start
- Site candidate identified from T3/web: CENIZO substation center ~27.3276°N, 99.4116°W (ETT-operated 345kV substation, ~5mi SE of Rio Bravo / ~16mi S of Laredo on Hwy 83, Webb County). OSM way 451971746 confirmed polygon bounds.
- cdse.py chip attempt: HTTP 403 on CDSE token request — CDSE_PASSWORD not set in ~/.config/gis-research.env (example file only, no real credentials configured)
- One retry attempted — same result. Imagery skipped per rule.
- T6 result: site_candidate = confirmed from OSM; construction_visible = unknown (no imagery obtained)

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~22
- STOP

## Deep scan — 2026-07-19

### D1 — Imagery
- CDSE chip 2026-07-01, 6km buffer: CENIZO substation clearly visible as white rectangle center-frame; surrounding land is undisturbed South Texas brushland. No grading, no gravel pad, no container rows. sources/2026-07-01_s2_cenizo_6km.png
- CDSE chip 2026-07-01, 2km buffer: tighter view confirms CENIZO substation building only; zero construction activity. imagery/s2_2026-07-01_2km.png (FULL IMAGE READ #1)
- CDSE chip 2026-01-01, 2km buffer: same undisturbed landscape (seasonal color variation only). imagery/s2_2026-01-01_2km.png (FULL IMAGE READ #2)
- Imagery verdict: no_activity. Per playbook: two chips confirm no activity → stop scanning history.

### D2 — Developer parent chain
- OCI Solar Power rebranded to OCI Energy in July 2024 (sources: ocienergy.com)
- Parent chain confirmed: OCI Holdings (Korean global conglomerate, 60+ yr history) → OCI Enterprises Inc. (US holding) → OCI Energy (San Antonio, TX, est. 2012)
- OCI Energy is an active developer with substantial Texas solar/BESS pipeline: Alamo City BESS (120MW/480MWh) broke ground May 2026; $130M tax equity June 2026; ING construction financing Sep 2025 (separate project)
- OCI Energy project page lists "Bravo" 200 MW battery in Zapata County (NOT Webb County) under development. This matches the triage finding of "Zapata County Bravo BESS abatement $88M"
- Webb County / Laredo: no mention on OCI Energy website. 27INR0398 is listed as Webb County in ERCOT queue but CENIZO substation is confirmed in Webb County by census geocoder and OSM.
- Discrepancy: OCI's own website says Bravo is Zapata County; ERCOT queue says Webb County. The substation (Cenizo, 27.3276N 99.4116W) IS in Webb County. Possible explanation: the battery site may be planned for Zapata side of the county line while connecting to the Webb County substation, OR OCI's website is imprecise.

### D3 — PUCT Interchange
- PUCT interchange.puc.texas.gov: requires JavaScript rendering; query for 27INR0398 and "Bravo BESS" both returned 402 Payment Required via direct fetch. No IA accessible.
- Queue milestone data confirms: FIS approved = NOT YET, IA signed = NOT YET. Pre-IA stage consistent with PUCT non-filing.

### D4 — County records
- Webb County CAD (webbcad.org): domain forwarded to GoDaddy parked page — not operational
- Webb County CAD (webbcad.com via apps): SSL cert error. Cannot search owner-name.
- JETI registry: no hits for Bravo BESS or OCI Energy in Webb County (expected: Ch.313 expired 2022; JETI new program; no application found)
- Zapata County: triage found $88M abatement notice but OCI website confirms "Bravo" is listed as Zapata County BESS. This is likely the companion sub-project (Webb County INR = 27INR0398; there may be a separate Zapata INR).

### D5 — Google Maps Places
- gmaps.py: HTTP 429 rate-limited on all attempts. No delivery pins found.
- Static Maps API: 403 (not enabled for this key). No site map image.

### D6 — OSM infrastructure
- Cenizo Substation confirmed: OSM way 451971746, center 27.3276°N 99.4116°W, voltage 345000, Webb County
- TIEMPO substation: no OSM results found for any TIEMPO power infrastructure in South Texas
- CENIZO → TIEMPO tap line: POI description "Tap 345kV 80220 CENIZO7A - 80224 TIEMPO7A" suggests two substations on ETT 345kV line. TIEMPO likely nearby but not in OSM.

### D7 — OCI financial activity
- Sep 2025: OCI Energy + ING finalized construction financing for "a major battery project in Texas" (unnamed in accessible press releases)
- Jun 2026: OCI Energy closed $130M tax equity with Greenprint Capital for Alamo City BESS (Bexar County)
- This confirms OCI Energy has active BESS financing/construction activity — but the ING-financed Sep 2025 project could be the Bravo BESS (Zapata or Webb county) given timing
