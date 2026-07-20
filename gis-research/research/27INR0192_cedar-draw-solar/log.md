
### Stage 2 findings (2026-07-19)

**TX Comptroller Ch.312 API query (api.comptroller.texas.gov/open-data/v1/tables/ch312-abatement):**
- Query: all records, 1,398 total, Scurry CAD matches: 4 (Dermott Wind, Fluvanna Wind, Midwest Solar, WL Plastics)
- Cedar Draw Solar LLC: NOT FOUND (expected — Apr 2024 hearing is newer than last Dec 2023 report submission)
- Ch312-abatement-zone API: same 4 Scurry entries, no Inadale Reinvestment Zone #1, no Cedar Draw
- NEGATIVE EVIDENCE: The 2024 county abatement has not yet been reported to TX Comptroller as of last data pull (Dec 2023)

**April 16, 2024 Scurry County agenda (retrieved via HTTP workaround):**
- Saved: sources/2026-07-19_scurry-agenda-apr16-2024.doc
- Text confirms: "2024 Inadale Reinvestment Zone #1 (Scurry)" — designation hearing for Exhibit A land parcel
- Named Texas Tax Code §312 as the statute
- NO direct "Cedar Draw Solar" company name in the agenda text (Exhibit A not embedded)
- Inadale is consistent with Scurry County geography for Cedar Draw Solar


### Stage 2 CAD results (2026-07-19)

**Scurry CAD owner search (esearch.scurrytex.com):**
- Queries: "Cedar Draw", "Cedar Draw Solar" — both returned NO RESULTS
- This is consistent with leased land (LLC as tenant, landowner holds parcels)
- NEGATIVE EVIDENCE: Cedar Draw Solar LLC does not own assessed property in Scurry CAD
- The /search/result endpoint confirmed no matches — saved HTML pages

**Delivery pin search (gmaps.py):**
- Both "Cedar Draw Solar" and "Cedar Draw Solar Scurry County Texas" returned HTTP 429 (rate limited)
- pins_found: 0 (consistent with triage T2)

**Google Maps Stage 3 attempt:** Rate limited; no pin obtained.


### Stage 3 — Site pinpoint (2026-07-19)

**Google Places pin:** Rate-limited (HTTP 429) for both "Cedar Draw Solar" and variant queries — 0 delivery pins found

**POI analysis:**
- POI: "60011 Nebula7A 345kV" — ETT 345kV tap station; bus 60011 is NEWER than Faraday (59905), MHOS (59911), Galvani (59912)
- ETT corridor context: Long Draw at 32.72,-101.63; Faraday at 32.65,-101.40; MHOS/Galvani in western Scurry
- Nebula is shared by Andromeda Storage II (26INR0517) and IIB (26INR0540) — all Scurry County WEST zone
- NOT yet in OpenStreetMap or any public geo source — likely planned/under-construction substation
- Inadale community: ~15 mi west of Snyder, near US-180/US-84 junction (est. 32.76, -101.34)
- Reinvestment zone (10,500 ac) centered on Inadale suggests site in that area
- CONCLUSION: No actionable lat/lon. SKIP imagery per playbook rule.

**Stage 4 — Satellite:** SKIPPED — no site coordinates meeting the ≥county-centroid threshold

### Stage 5 — Synthesis (2026-07-19) 

**Companion project:** 27INR0193 Cedar Draw BESS (225.7 MW, OTH) — same POI, same COD, same study phase (SS Complete, FIS Started, No IA)

**Developer identity:** NOT confirmed. No TX Comptroller entity found (JS-only search). No press release, no EDGAR filing, no news article naming a parent company. Web searches CAPTCHA-blocked. The LLC name "Cedar Draw Solar LLC" has zero public footprint.

**Queue assessment:** 
- 28 monthly snapshots, COD 2027-12-31 STABLE (0 drift)
- FIS requested 2024-03-01; FIS NOT APPROVED as of 2026-06-01
- No IA, no financial security, no construction milestones
- "SS Completed, FIS Started, No IA" — stuck since entry

**Overall verdict: unclear (leaning paper)**
- FOR real: county abatement process initiated (Inadale RZ#1, ~10,500 acres), companion BESS project shows paired planning
- AGAINST: no developer identity, no FIS approval in 28 months, no delivery pin, no press release, no financing announcement, no IA
- COD 2027-12-31 is implausible: minimum path from no-FIS to COD is ~3 years (FIS→IA→build)
- Independent COD: 2030-Q1 at earliest, HIGH drift risk; cancellation risk elevated

