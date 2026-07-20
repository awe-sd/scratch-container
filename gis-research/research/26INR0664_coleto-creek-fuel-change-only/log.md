# Research Log — Coleto Creek Fuel Change Only (26INR0664)

**Researched:** 2026-07-19  
**Analyst:** agent  
**Identity packet:** 655 MW Gas steam, Goliad County TX, POI "8162 Coleto Creek 138kV", CDR zone SOUTH, reported COD 2026-12-15

---

## Triage findings (inherited from prior run 2026-07-18)
- 14 queue snapshots (2025-05-01 → 2026-06-01); 0 COD drifts; stable 2026-12-15 COD
- Screening started 2025-04-21, screening complete 2025-07-19, FIS requested 2025-05-21
- FIS NOT approved, IA NOT signed, no milestones achieved beyond screening
- Site candidate: existing Coleto Creek Power Station ~28.72, -97.21 (domain knowledge)
- "Fuel Change Only" scope ambiguous: coal→gas conversion vs. administrative re-designation
- TCEQ NSR air permit: NOT CHECKED (priority #1)
- PUCT IA: NOT FOUND (priority #2)
- Owner/developer: unknown (priority #3)

## Stage 1 — LLC / parent chain

**FINDING:** Vistra Corp / Luminant is the developer.
- "Coleto Creek Power, LLC" is the SPV (matches ERCOT queue project name ~LLC pattern)
- Owner confirmed: Vistra Corp (via victoriaedc.com April 2025 article + TCEQ permit)
- Luminant Generation Company LLC = operating subsidiary (Renee.Collins@luminant.com cc'd on TCEQ correspondence)
- May 30, 2024 Vistra press release: plans to add up to 2,000 MW gas in ERCOT; Coleto Creek coal retiring 2027 per EPA, repowered as gas adding "up to 600 MW"
- September 2025: Coleto Creek repower described as "on-track" by Vistra
- TCEQ contact: Roderick Harger PE, Vistra Environmental Specialist Sr., Irving TX
- No sub-developer, no EPC announced publicly
- Source: victoria edc article (verbal description), energychoicematters.com story saved mentally
  ARTIFACT: sources/2026-07-19_tceq_titlev-pending-coleto-creek-37946-ac.pdf (TCEQ confirms Vistra/Coleto Creek Power LLC)

## Stage 2 — County records / permits

**FINDING: Title V permit renewal (Permit O25, Project 37946) filed 2025-03-27, accepted by TCEQ, status Administrative Complete (as of 2026-07-18)**
- This is a RENEWAL of the existing coal plant's FOP/SOP, NOT an NSR for new gas plant
- Company: Coleto Creek Power, LLC
- Facility: Coleto Creek Power Station, Fannin, Goliad County
- ORIS/Facility Code: 6178; RN: RN100226919; CN: CN605521988
- **Site coordinates from OP-1 form**: Lat 028°42'49" = **28.7136°N**, Lon 097°12'50" = **-97.2139°W**
- Address: FM 2987 and Coleto Creek Dr (gate entrance); Unit 1 Boiler at stated coords
- ARTIFACT: sources/2026-07-19_tceq_titlev-pending-coleto-creek-37946-ac.pdf (pages 31-36)

**NSR for gas conversion: NOT found in TCEQ pending NSR list (checked 2026-07-19)**
- Title V pending list searched — only coal plant renewal found, no NSR for new gas units
- NSR pending list searched — no Coleto Creek entry found
- This is SIGNIFICANT: no new source permit for the gas repower has been filed (or approved) as of 2026-07-19
- Log negative: TCEQ NSR pending list 2026-07-19 — searched "Coleto Creek", "Luminant" — Coleto Creek absent from NSR list

**FINDING: EPA Dec 5, 2025 approved Texas regional haze plans removing pollution control mandates at Coleto Creek (EPA-R06-OAR-2025-019)**
- Prior requirement for emissions controls eliminated; Vistra/Luminant can operate without new controls
- This WEAKENS (but doesn't eliminate) the EPA-compliance driver for the 2027 coal retirement
- Source: Yahoo search result snippets referencing South Texas News Dec 11, 2025 article

**TCEQ Title V pending list** saved: sources/2026-07-19_tceq_titlev-pending-list.html

## Stage 3 — Site pinpoint

Site candidate from TCEQ OP-1 form: **28.7136°N, -97.2139°W** (precision: seconds = ~30m accuracy, pointing to Unit 1 Boiler)
OSM Nominatim cross-check: 28.7221, -97.2149 (industrial landuse polygon, same complex, ~1 km)
TCEQ GIS map link: -97.213888, 28.713611 — consistent
Google Maps delivery pin: rate-limited (429), not obtained
Confidence: HIGH (derived from TCEQ regulatory filing, not domain guess)

## Stage 4 — Satellite imagery

CDSE credentials returned 401 Unauthorized. Satellite imagery NOT obtained.
This is an existing operating coal plant — current imagery would show the industrial facility, not a new construction site.
Log negative: CDSE chip attempt 28.7136, -97.2139, date 2026-07-01 — HTTP 401 Unauthorized.

## Stage 5 — Synthesis

Key findings:
1. Vistra Corp / Luminant own and operate the existing Coleto Creek Power Station (coal, ORIS 6178)
2. Vistra announced May 2024: coal retirement ~2027 (EPA compliance); gas repower adds "up to 600 MW" — confirmed "on-track" Sept 2025
3. TCEQ Title V renewal of existing coal permit filed Mar 2025 (Project 37946, Permit O25) — NOT an NSR for new gas units
4. No TCEQ NSR for gas repower filed as of 2026-07-19 (searched pending NSR list)
5. No IA signed; FIS not approved (queue data)
6. Transco FERC filing Mar 2026: gas supply pipeline planning underway (170,000 Dth/d to Luminant)
7. EPA Dec 2025: removed pollution control mandates — slightly weakens 2027 coal retirement urgency
8. Reported COD 2026-12-15 is physically impossible (coal still operating; no NSR; no IA)
9. Independent estimate: 2028-Q2; drift risk HIGH

Verdict: **real_early** — credible developer, real project, but far from construction-ready. COD claim is a placeholder.


