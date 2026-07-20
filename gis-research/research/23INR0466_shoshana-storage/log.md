# Triage Log — 23INR0466 Shoshana Storage

T1 start
T1 result: 50 snapshots (2022-05-01 → 2026-06-01). COD drifted 4 times: 2023-12-31 → 2024-06-01 → 2025-06-01 → 2026-08-28 → 2028-05-30 (current). Milestones: screening started 2022-03-30, screening complete 2022-06-26, FIS requested 2022-05-16. FIS NOT approved, IA NOT signed, NO construction milestones. Stalled at FIS stage 4+ years; capacity minor tweak (221.92→220.15→221.0 MW).

T2 result: gmaps.py 429 Too Many Requests on all calls; one retry also 429 — blocked. 0 pins found.

T3 result: Developer confirmed = ACCIONA (Spanish multinational). SPV = Shoshana Storage Project LLC. County tax abatement unanimously approved 2024-04-28 (5-year, 100%, ~$2M total). Matagorda Hospital District also held abatement hearing Nov 2024. No site address, no contractor, no construction dates in press. Sources saved to sources/t3_web_sweep.md.

T4 result: PUCT Interchange portal returns HTTP 402 on all URL attempts (FilingParty=Shoshana+Storage, Description variants, main search page). Portal blocked — no IA found. Note: milestone table confirms IA NOT signed, so absence is consistent.

T5 result: Ch.313 ended 2022 — not applicable (project entered queue May 2022, post-cutoff). JETI registry has no public searchable database. County Ch.312 abatement already found in T3 (Matagorda County Commissioners approved 2024-04-28, 5-year 100%; Hospital District hearing Nov 2024). No formal JETI application found. Abatement_found = TRUE (county Ch.312).

T6 result: SKIPPED — budget warning at 80% before grid could run. Site candidate: STP nuclear plant vicinity ~28.80N, -96.05W (POI = "Tap STP – Refuge ckt 27"). No imagery acquired. construction_visible = unknown.

T7 result: triage_findings.json + triage.md written. Turns used: ~22. deep_scan_recommended = true.

## Deep scan D1 (2026-07-19) — started

D1 result: STP nuclear plant at 28.79556°N, 96.04889°W (Wikipedia, confirmed decimal coords). POI "Tap STP – Refuge ckt 27" = tap on the STP-Refuge 345kV transmission circuit near STP. Battery storage site expected within ~1-5 km of STP substation area. Wadsworth TX is ~6 km NE of STP at 28.833N, 95.936W (unrelated).

D2 result: Bay City Tribune abatement article HTML fetched (247KB, paywall-gated but lead text visible). Confirms: 220 MW BESS, Acciona parent, 5-yr 100% county abatement approved Apr 2024, $2M to county. No site address or parcel number in visible text. Sources: 2026-07-19_baycitytribune_county-abatement.html

D3 result: MCHD abatement PDF fetched (533KB) — 2026-07-19_mchd_nov2024_abatement-hearing.pdf. Cannot extract text (poppler not installed). PDF size suggests it contains real content (meeting notice + likely abatement terms).

D4 result: PUCT Interchange portal returns 402 on direct URL and 404 on API endpoint — JavaScript-rendered only; IA NOT signed per queue milestones, consistent with no filing found.

D5 result: Overpass API 406/blocked for substation search. Refuge substation not in OSM (not found in any query). STP-Refuge ckt 27 is likely a CenterPoint Energy / ERCOT-registered circuit not in OSM.

D6 result: Google Maps still 429 — pins not accessible. Acciona website 403. Matagorda CAD portal: matagorda-cad.org appears to resolve (200 OK).

Site candidate refined: 28.79556°N, 96.04889°W (STP plant centroid). BESS will be within ~1-3 km of STP switchyard or the Refuge circuit tap point. Starting imagery at this coordinate.

## Deep scan D2 (2026-07-19) — parquet/queue cross-reference

D7 result: Queue parquet analysis → Refuge 345kV (ERCOT bus #42400) is a real existing substation in Matagorda County. Peyton Creek Wind II (20INR0155, 241 MW) connects there and was approved-for-synchronization 2025-02-05 — the substation is operational. Shoshana Storage (23INR0466) taps the same STP-Refuge 345kV ckt 27 circuit. This confirms POI infrastructure is real and installed.

D8 result: All other projects at Refuge 345kV = only 23INR0466 Shoshana Storage (no other BESS). Multiple projects tap the STP-Refuge circuit (STP = ERCOT bus 5915). The Refuge substation is distinct from Hillje, Blessing, and other Matagorda substations. No coordinates for Refuge substation found in OSM, Nominatim, or ArcGIS — it is not in public databases.

D9 result: CDSE auth failed (401 Unauthorized) after initial chips — credentials expired mid-session. Got 5 chips (3 at STP center/NE/NW at 2km, 1 xwide at 6km, 1 at south STP) before failure. No BESS pad visible in any chip; chip coverage focused on STP plant itself, not Refuge substation area (unknown coordinates).

D10 result: Google Maps Places API still 429 for entire session — no construction pins found.

D11 result: Bay City Tribune article (paywall) confirms: 220 MW BESS, Acciona parent, ~$2M county abatement, 30+ year lifespan. No site address in visible text.

D12 result: MCHD abatement PDF fetched (533KB) but PDF is compressed — only "Microsoft Word - MCHD Meeting Notice Oct 2024 - Tax Abatement Shoshana" extracted. Full text not readable without poppler. This is the meeting notice for the Hospital District abatement hearing, Nov 2024.

D13 result: Matagorda CAD propaccess.trueautomation.com (cid=235) — session timeout error; no owner search results accessible. 0 parcels found for Shoshana/Acciona.

D14 result: PUCT Interchange portal = JavaScript-rendered only, 402 blocked on all curl attempts. IA NOT signed per queue (confirmed). No PUCT filing found.

D15 result: TX Comptroller Ch.312 for Shoshana — not found. Ch.313 ended 2022 (project entered post-cutoff). Only abatement is county Ch.312 (approved Apr 2024, $2M over 5 yrs).

D16 result: Site candidate remains STP/Refuge 345kV corridor in Matagorda County. Without Refuge substation coordinates or Google Maps pins, precise lat/lon not determinable. Best estimate: ~28.80N, -96.05W (POI inference from STP plant location + Refuge circuit direction). Confidence: low.
