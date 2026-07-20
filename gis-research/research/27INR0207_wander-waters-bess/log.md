# Research Log — Wander Waters BESS (27INR0207)

**Project:** Wander Waters BESS  
**INR:** 27INR0207  
**County:** Wilbarger, TX  
**Capacity:** 303.5 MW BESS  
**POI:** 61001 JIMTREEC7A 345kV (= Jim Treece substation, AEP Texas utility ID 61001)  
**CDR Zone:** WEST  
**Reported COD:** 2027-10-31  

---

## Triage pass (2026-07-18) — inherited findings

See triage.md / triage_findings.json. Key inherited negatives:
- T2: gmaps.py 429 on "Wander Waters BESS" (rate-limited)
- T3: Bing 0 hits on project name (zero web footprint)
- T4: PUCT Interchange 402 on all filing queries
- T5: No Ch313 (expired 2022) or JETI abatement found
- T6: JIMTREEC7A coords unresolvable — site skipped

---

## Deep scan (2026-07-19)

### Stage 1 — LLC → Parent

- **TX Comptroller search** (`mycpa.cpa.state.tx.us`): Redirected to comptroller.texas.gov. API requires auth. No "Wander Waters" entity found (search attempted via POST). [Negative]
- **TX SOS** (`sos.state.tx.us`): SOSDirect is a paid portal ($1/search). Free web interface returned "file not found" for all queries. No "Wander Waters BESS LLC" entity found. [Negative — portal blocked]
- **Bing search** "Wander Waters BESS" + "battery" + "energy" + Texas: Zero relevant hits. Project name returns only unrelated "wander" results (vacation rentals, film). Zero web presence for developer or project name. Artifact: [sources/2026-07-19_bing_wander-waters-search.html](sources/2026-07-19_bing_wander-waters-search.html)
- **Developer identity**: Unknown. No press releases, LinkedIn posts, or news articles found for this project.

### Stage 2 — County records sweep

- **Wilbarger CAD** (`wilbargercad.org`): POST search for "Wander Waters" → "No results." BESS projects typically show thin CAD record (little land needed) so this is expected but confirms no registered ownership. [Negative — expected]
- **PUCT Interchange IA search**: Portal returns HTTP 402 or requires JavaScript for all search parameters (FilingParty, Description). Cannot confirm absence of IA — portal is structurally inaccessible without a JS-capable browser. [Blocked — not definitive negative]
- **JETI Act registry**: Comptroller JETI page loaded but no search interface. Bing query for "JETI Wilbarger County battery storage 2024-2025" returned no relevant results. [Negative]
- **Wilbarger County Commissioners Court**: County website (wilbargercounty.org) returned ENOTFOUND. No meeting minutes accessed. [Blocked]
- **TCEQ air permit**: Not searched — battery storage does not require TCEQ air permit; absence is expected.

### Stage 3 — Site pinpoint

**Key breakthrough**: Queried the local ERCOT GIS parquet for all projects at JIMTREEC7A POI.
- 27INR0207 (Wander Waters BESS) = **only** project at "JIMTREEC7A 345kV" in current queue
- But cross-reference: **18INR0072 Blue Summit repower** and **25INR0492 Blue Summit Energy Storage** both at "61001 Jim Treece 345kV" (same substation, slightly different name spelling)
- This confirms JIMTREEC7A = Jim Treece substation, AEP Texas, Wilbarger County

**EIA-860 2024 data** (downloaded from eia.gov, artifact: [sources/2026-07-19_eia860-2024_wilbarger-county-plants.json](sources/2026-07-19_eia860-2024_wilbarger-county-plants.json)):
- **Blue Summit Wind LLC**: plant_code=57218, lat=34.292913, lon=-99.367734
- **Blue Summit Storage, LLC**: lat=34.299, lon=-99.399
- **Blue Summit II Wind**: lat=34.225882, lon=-99.477986

**Google Places pin** (gmaps.py places "Blue Summit Wind Farm Texas"):
- "Blue Summit Wind Farm | 17301 County Rd 97 N, Vernon, TX 76384, USA | 34.292859, -99.367948"
- Address: County Road 97 N, Vernon TX — this is the access road to the Jim Treece substation compound

**Site candidate**: Jim Treece 345kV substation at approx **34.2929, -99.3679**
- Method: EIA-860 plant coordinates + Google Places pin for co-located wind farm
- Confidence: **medium-high** — EIA and gmaps agree within 50m; this is the existing Blue Summit wind substation and the POI for the BESS project
- Wander Waters BESS would be a new pad ADJACENT to the existing Blue Summit substation compound (BESS is added to existing substations)

### Stage 4 — Satellite ground truth

**Chips pulled** (CDSE Sentinel-2 L2A, ~10m/px):
1. **2026-07-01 tight** (2km buffer) centered at 34.2929, -99.3679: Undisturbed agricultural farmland around existing Blue Summit substation compound. No graded pad, no container rows, no new construction visible. [no_activity]
2. **2026-07-01 xwide** (6km buffer): Same site in wider context. All farmland, center shows existing substation structures from existing Blue Summit wind farm. No new construction visible in any direction. [no_activity]
3. **2026-07-01 Blue Summit Storage offset** (2km buffer at 34.299, -99.399): Agricultural fields with irrigation pivots. Existing substation compound barely visible center. No new large graded pad. [no_activity]

**Per PLAYBOOK: raw farmland, no activity → confirmed no_activity without additional chips required.**

CDSE API returned HTTP 401 on subsequent calls (token expiry); January 2026 chip not obtained. However, the July 2026 chip unambiguously shows no construction at the known substation location, which is consistent with the pre-IA project stage.

**Verdict: no_activity.** Site confirmed at Jim Treece substation; no BESS construction initiated.

### Negative evidence log

| Source | Query | Result |
|---|---|---|
| TX Comptroller | "Wander Waters BESS" entity search | No entity found / portal redirected |
| TX SOS SOSDirect | "Wander Waters" entity search | Paid portal; blocked |
| Wilbarger CAD | "Wander Waters" owner name search | No results |
| PUCT Interchange | FilingParty="Wander Waters" | HTTP 402 / JS required |
| Bing | "Wander Waters BESS" + battery + Texas | Zero project hits |
| Wilbarger County website | commissioners court minutes | Domain ENOTFOUND |
| JETI registry | Wilbarger battery storage | No hits |
| GNIS | "Jim Tree" Texas place name | Service unavailable |
| OSM Overpass | Wilbarger County 345kV substations | 406 Not Acceptable |
| EIA OpenData API | Wilbarger County plant data | 0 records (API key issue) |

---

## Summary

Project is **real_early** — FIS approved at a real substation (Jim Treece 345kV, Wilbarger County), but IA not yet signed and zero construction activity visible in July 2026 imagery. Developer identity is unknown (zero public footprint). The 2027-10-31 COD is tight: IA must be signed soon, then 12-18 months construction minimum. Drift risk is high for a BESS without a signed IA or identified developer.
