# Research log — Operation Sunshine Storage (26INR0357)
County: Concho, TX | 409.8 MW Battery/Storage | POI: 7077 Amos Creek 345kV | COD claim: 2028-03-12
Researched: 2026-07-19

## Stage 1 — LLC → parent chain

**2026-07-19** Duck Creek Storage LLC (TX file 0805304599, Fort Worth, filed 2023-11-14) confirmed as registered developer entity. Sister entity Duck Creek Solar LLC (TX file 0805092573, filed 2023-06-07) operates the companion solar project 26INR0255. Both at ~1300 S University Dr, Fort Worth TX 76107. Sources: `sources/t3_web_sweep.md`

**2026-07-19** SPV confirmed as **Concho Duck Creek Storage, LLC** — named in Concho County public meeting notice Jul 8 2025 item 3: "Public Meeting on proposed Concho Duck Creek Storage, LLC Tax Abatement Agreement." Source: `sources/2025-07-08_concho-cc_public-meeting-notice_p1.png` (copied from sister-project research, same primary document).

**2026-07-19** **Concord New Energy Group Limited** identified as likely developer/parent/acquirer — named in Concho County Commissioner Court agenda June 9 2026, Item 6: "Consider/Discuss/Approve Road Use Agreement for Concho Pearl Solar, LLC, Don Battenfelder with Concord New Energy Group Limited." Concho Pearl Solar is a co-located project at the same site cluster. Source: `sources/2026-06-09_concho-cc_agenda.pdf`. Concord New Energy is a HK-listed clean energy developer (HKEX:182) active in ERCOT utility-scale solar and storage. This is the best available parent-chain indicator; no direct press release linking Duck Creek Storage to Concord confirmed.

**2026-07-19** Energy Capital Partners listed as "possible parent" in infrasure.ai — unconfirmed; may be stale or incorrect given Concord New Energy now appearing in county records for the same site cluster.

## Stage 2 — County records sweep

**2026-07-19** Ch.312 tax abatement public hearing held **July 8, 2025** for Concho Duck Creek Storage, LLC. Public meeting notice confirmed this is a separate line item from companion solar projects. Source: `sources/2025-07-08_concho-cc_public-meeting-notice_p1.png`. NEGATIVE: No approval agenda item found in any 2025–2026 Concho County Commissioner Court agenda through Jul 14 2026. Abatement status: PENDING or approved in executive session (not public).

**2026-07-19** Scanned all Concho County CC agendas Jan–Jul 2026 (17 PDFs). No Duck Creek Storage abatement approval found in any public agenda item. The Ch.312 public hearing process was completed July 2025; approval may have happened in closed/executive session or was not separately captioned.

**2026-07-19** EPC: **Primoris Renewable Energy** — named in Jan 13 2026 agenda item 9: "Bore Regulations on Utility Right of Way Permit by Brian Cooper with Primoris Renewable Energy." This is a shared EPC servicing both solar and storage components. Source: `sources/2026-01-13_concho-cc_agenda_p1.png`.

**2026-07-19** Land tenure: "Concho Solar 1, LLC Easement and Right-of-Way use with the Frank and Katy Smith Living Trust UDT" — Jan 13 2026 agenda item 8. This is the solar SPV but the same land parcel cluster used for the combined solar+storage project. Source: `sources/2026-01-13_concho-cc_agenda_p1.png`.

**2026-07-19** CAD parcel search: `esearch.conchocad.org` — owner search for "Duck Creek" and "Operation Sunshine" returned 404 errors (portal may require JS). No parcel IDs obtained.

**2026-07-19** JETI/Ch.313: Comptroller.texas.gov JETI page does not expose searchable database; no Concho County battery storage JETI found.

**2026-07-19** PUCT Interchange: ALL queries returned HTTP 402 (subscription required). IA document text not retrieved. Control number 35077 referenced in web search results for Amos Creek substation documents but not accessible.

## Stage 3 — Site pinpoint

**2026-07-19** Amos Creek Road, Concho County, TX locates at 31.4956°N, 99.7062°W per Nominatim/OSM (road type, Concho County). The POI substation "7077 Amos Creek 345kV" is a NEW substation on LCRA TSC line T424 — confirmed via web search citing PUCT Control 35077 document description: "new substation built along existing LCRA TSC 345-kV transmission line T424 in Concho County, TX." No GPS coordinates for the substation itself found (CEII protected). Amos Creek Road provides the best public coordinate anchor.

**2026-07-19** Google Maps Places API: rate-limited (HTTP 429) throughout session; no delivery pin obtained.

**2026-07-19** Overpass API (OSM): multiple instances returned 406 Not Acceptable; Amos Creek substation not in OSM (CEII infrastructure).

**2026-07-19** Site estimate: 31.4956°N, 99.7062°W (Amos Creek Road, Concho County), confidence LOW — road reference only; substation may be 2–5 km from this point along the T424 line.

**2026-07-19** NEGATIVE: No Google Maps delivery pin, no parcel GIS, no FAA filings (battery, not wind), no news/aerial photos with site location.

## Stage 4 — Satellite ground truth

**2026-07-19** CDSE token auth failed: `invalid_grant` / `Invalid user credentials` — Copernicus satellite imagery unavailable this session. No Sentinel-2 chips obtained. Construction stage not verified from imagery.

**2026-07-19** NEGATIVE: No imagery from any source. Stage 4 is entirely absent for this project.

## Stage 5 — Synthesis

**2026-07-19** Findings.json, dossier.md, and brief.html generated. Verdict: **real_active**. Construction: **early civil** (inferred from EPC bore permit Jan 2026, land access secured; no visual confirmation). COD: reported 2028-03-12 → independent **2028-Q2**, drift risk **medium**.

Key evidence trail:
- IA signed 2025-08-27 (ERCOT queue)
- Ch.312 public hearing Jul 2025 (county notice)
- EPC Primoris bore permit Jan 2026 (CC agenda)
- Land access secured Jan 2026 (CC agenda)
- Concord New Energy road use agreement Jun 2026 (CC agenda) — developer presence confirmed at site cluster
- COD drifted twice (2026-07 → 2026-09 → 2028-03); FIS not yet approved as of 2026-06 queue
