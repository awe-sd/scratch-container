# Research log — Rock Rose BESS (26INR0201)

## Triage (2026-07-18, prior session)

**Queue history**: 34 snapshots 2023-09-01 → 2026-06-01. 2 reported-COD changes (slipped from 2026-07-02 → 2026-12-15 → 2027-03-19). Capacity minor fluctuations, settled 208.5 MW.
Key milestones: Screening complete 2023-12-14, FIS approved 2026-03-18, IA signed 2024-06-15, Meets all 6.9 2026-05-26. No construction start/end dates. COD drifted ~8 months total since entry.

**gmaps.py**: HTTP 429 on both attempts (rate-limited). No pins. pins_found=0.

**Developer**: Advanced Power (original); sold to undisclosed buyer ~Oct 2025, pre-NTP. Later web sources identify buyer as Greenflash Infrastructure (Houston-based).
LLC name confirmed: "Rock Rose Energy Storage LLC".
Source saved: sources/advanced_power_sale.md
news_found=true.

**PUCT Interchange**: HTTP 402 on all URL patterns (root, FilingParty, query params). Blocked portal. ia_found=false.

**TX Comptroller Ch.313/JETI**: No searchable database accessible. abatement_found=false.

**Site candidate**: W.A. Parish / Whaley 345kV area, Fort Bend County, near Thompsons TX (~29.47N, -95.77W). Based on W.A. Parish proximity to Whaley 345kV line. Low-medium confidence.
CDSE: HTTP 401 — credentials not configured. No imagery.

## Deep scan (2026-07-19)

### Stage 1 — LLC / developer chain

**Advanced Power PR** (2026-07-19): Confirmed LLC = Rock Rose Energy Storage LLC. Advanced Power sold to undisclosed buyer Oct 9, 2025. "Fully developed" status. Financial advisor PEI Global Partners. No EPC or address in release. Source: sources/2026-07-19_advanced-power_rock-rose-sale-pr.md

**Greenflash Infrastructure**: No website (domain parked). No PUCT, SEC, or LinkedIn filings found. Buyer identity CANNOT be independently confirmed beyond triage-source reference. Negative: greenflashinfrastructure.com → domain parked.

**TX Comptroller**: Direct search redirects to form-only JS interface; no entity data returned. Negative evidence logged.

**PUCT Interchange**: Blocked HTTP 402 on all patterns: company=Rock+Rose, company=Rock+Rose+Energy+Storage, keyword=interconnection. IA document not retrieved. **ia_found=false (portal blocked)**. IA existence confirmed by queue milestone: iaSigned 2024-06-15.

### Stage 2 — County records

**Fort Bend CAD (fbcad.org / esearch.fbcad.org)**: URL pattern for owner-name search not determinable from static fetch (BIS platform, JS-driven). Negative: no parcel results returned for "Rock Rose" or "Rock Rose Energy". Expected for pre-NTP BESS — land likely leased from landowner; LLC may not appear as grantee until construction phase.

**TX Comptroller JETI registry**: No public search available — portal is JS-only. Negative: abatement_found=false (not confirmed absent, access-limited).

**Fort Bend County commissioners court**: URL patterns for agenda search not found. Negative: no agenda items confirmed.

**SEC EDGAR**: HTTP 403 on all EDGAR EFTS search patterns. Negative.

**PEI Global Partners**: Portfolio page lists unrelated transactions (Pathway Power, Calon Energy, etc.) — no Rock Rose mention. Negative.

### Stage 3 — Site pinpoint

**Delivery-pin trick (gmaps.py)**: HTTP 429 rate limit throughout session. No pins obtained.

**OSM Overpass query**: Fort Bend County 345kV substations found. Key result: unnamed 345kV substation at 29.4743°N, -95.6229°W immediately adjacent to W.A. Parish generating station. Identified as Whaley 345kV substation based on: (a) POI description "44070 Whaley 345 kV", (b) proximity to W.A. Parish which is the dominant 345kV node in this area, (c) Whaley Corner hamlet at 29.4461°N, -95.6741°W (OSM node). Source: sources/2026-07-19_osm_whaley-substation.md

**W.A. Parish coordinates**: OSM + general knowledge: ~29.4808°N, -95.6242°W. The Whaley 345kV substation is adjacent at 29.4743°N, -95.6229°W.

**Site location**: BESS would connect directly to Whaley 345kV. Site is likely within ~1 km of that substation. No delivery pin to confirm exact parcel.

### Stage 4 — Satellite ground truth

**CDSE imagery — Whaley 345kV area (29.4743N, 95.6229W)**:

- s2_2026-04-01_whaley (2km buffer): Clear April 2026 frame. W.A. Parish prominent upper-left. Whaley 345kV switching yard visible center — pale fenced compound. Surrounding land: open farmland to south and east. **No gravel pad, no container rows visible adjacent to substation.**
- s2_2026-01-01_whaley (2km buffer): Clear January 2026 frame. Same observation — undisturbed farmland/industrial surrounds around substation.
- s2_2026-07-15_whaley (2km buffer): Cloudy. No useful observation.
- Several 1km tight chips at candidate locations: no BESS infrastructure found.

**Verdict**: no_activity — no construction visible adjacent to Whaley 345kV substation as of April 2026. Consistent with pre-NTP status at time of sale (Oct 2025) and no reported construction start in queue.

**Note on imagery coverage**: Triage candidate at 29.47N, 95.77W (Thompsons area) was checked and shows residential/agricultural land with no BESS activity. The true POI anchor is 29.4743N, 95.6229W (Whaley 345kV substation east of Parish).

### Negative evidence summary (Stage 2 specific searches)

| Source | Query | Result |
|---|---|---|
| PUCT Interchange | company=Rock+Rose | HTTP 402 |
| PUCT Interchange | company=Rock+Rose+Energy+Storage | HTTP 402 |
| Fort Bend CAD (esearch.fbcad.org) | owner=Rock+Rose | HTTP 404 / no results |
| TX Comptroller JETI | Rock Rose Energy Storage | JS-only portal, no search |
| Fort Bend commissioners court | Rock Rose, battery storage | URL 404 |
| Greenflash Infrastructure website | portfolio | Domain parked |
| SEC EDGAR EFTS | Rock Rose Energy Storage | HTTP 403 |
| SEC EDGAR EFTS | Greenflash Infrastructure | HTTP 403 |
| OSM | Whaley substation, Texas | No match by name; identified by location |
| ERCOT NTP Substation List | Various URL patterns | All HTTP 404 |
| gmaps.py places | Rock Rose BESS / Energy Storage | HTTP 429 throughout |
