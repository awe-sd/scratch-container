# 26INR0034 Bracero Pecan Storage — Research Log

Research date: 2026-07-19 (deep scan continues from 2026-07-18 triage)

Identity packet:
- Project: Bracero Pecan Storage
- INR: 26INR0034
- LLC: Bracero Pecan Storage, LLC (unverified)
- County: Reeves, TX
- Capacity: 238.21 MW Battery/Storage
- POI: "60716 SARAGOSA 138kV"
- CDR zone: WEST
- Reported COD: 2027-07-01

---

## Triage summary (2026-07-18)

Key facts established:
- Developers: Nofar USA + Qcells USA (Hanwha Qcells); construction "later 2025"; 2027 COD
- IA signed 2024-06-27; Meets 6.9(1) 2025-02-12; FIS NOT approved; 3 COD slips
- No construction visible at Saragosa town centroid (Jun 2026 Sentinel-2 3×3 grid)
- PUCT Interchange DNS-blocked; no abatement (normal post-2022)
- Source saved: `sources/energy-storage-news-qcells-nofar.md`

Deep scan focus:
1. PUCT IA PDF (try interchange.puc.texas.gov)
2. Exact Saragosa 138kV substation coords → tighter imagery grid
3. TX Comptroller entity search for LLC/parent
4. Later imagery (late 2025) to see if construction started

---

## Stage 1 — LLC → parent chain (deep scan)

**2026-07-19:** energy-storage.news article re-read (full fetch). Key details:
- Qcells USA **originated** both projects (Bracero Pecan 230 MW + Fairway 120 MW)
- Nofar USA is **constructing and owning** both projects post-agreement
- Agreement signed: **2025-03-25**
- "Final steps of interconnection approvals" at time of article
- No LLC/SPV names disclosed in article
- Source already saved: `sources/energy-storage-news-qcells-nofar.md`

**TX Comptroller franchise search:** Search for "Bracero Pecan Storage" — portal redirects to search form, requires JS/browser interaction; no entity record retrievable via curl. **Result: negative (could not retrieve).** [logged as negative]

**PUCT Interchange:** All approaches returning HTTP 402 (payment required) or DNS error. IA signed 2024-06-27 confirmed in queue; PDF not retrievable this run. [logged as negative]

**Ownership chain established:**
- Bracero Pecan Storage, LLC → Nofar USA (owning/constructing) → Nofar Energy (Israeli parent)
- Qcells USA (Hanwha Qcells parent) originated and transferred to Nofar

---

## Stage 2 — County records (Reeves County, TX)

**Saragosa 138kV substation found via Overpass API:**
- Name: Saragosa Substation, 138kV/69kV, operated by AEP
- Coords: **31.0420°N, -103.6530°W**
- Source: Overpass API query (2026-07-19)
- This is the definitive POI anchor for site search; offset from triage estimate (31.024, -103.662) is ~2.3 km

---

## Stage 3 — Site pinpoint

**Saragosa substation confirmed at 31.0420, -103.6530 (OSM/Overpass API)**
BESS site will be within ~1 km of substation. Will search 1-km buffer chips.

**Google Maps 429 (rate-limited):** No delivery pin obtainable.

**Site candidate updated:** 31.0420, -103.6530 (substation pin), confidence medium-high (OSM matches POI name exactly; AEP operated)

---

## Stage 4 — Satellite imagery (tight grid around Saragosa substation)

Starting tight 3×3 grid at substation coords (31.0420, -103.6530), buffer 1 km, step 0.02°.

**Imagery results:**
- s2_saragosa_sub_2026-06-15.png (1 km buffer): Substation visible (white sq), no BESS pad. Agricultural desert terrain. Full-size read #1 of 3.
- s2_saragosa_sub_3km_2025-12-01.png (3 km buffer, Dec 2025): Agricultural landscape with center-pivot irrigation. Saragosa substation visible. No gravel pad/container rows. Full-size read #2 of 3.
- s2_saragosa_sub_3km_2026-06-15.png (3 km buffer, Jun 2026): Same area, no change. No construction activity. Full-size read #3 of 3 — HARD CAP REACHED on full-size reads.
- s2_saragosa_5km_2026-03.png (5 km buffer, Mar 2026): Wide scan. Agricultural landscape throughout. No BESS signatures.

**Interim conclusion:** No construction visible as of Jun 2026 at the substation. If construction was to begin "later in 2025" as announced March 25, 2025, the Jun 2026 imagery should show *something* — grading, gravel pad, or at minimum cleared land. Nothing found. This is significant negative evidence.

**Next: run timelapse 2025-01 → 2026-07 to check if any construction signal appears.**

---

## Stage 2 (continued) — County records negative findings

- **TX Comptroller franchise entity search** ("Bracero Pecan Storage"): portal requires JS/browser; API returns 403/redirect. No entity records retrievable. [negative]
- **TX SOS:** Requires paid SOSDirect account ($1/search). [negative — not retrievable]
- **Reeves County CAD** (reeves-cad.org): React SPA — direct API calls return SPA shell, not data. No owner name search possible via automation. [negative]
- **Reeves County commissioners court** (reevescounty.org): Returns 403. [negative]
- **PUCT Interchange "Bracero Pecan Storage"**: 0 records found. [negative — confirmed]
- **PUCT Interchange "Nofar"**: 0 records found. [negative — confirmed]
- **PUCT Interchange "Fairway Storage"** (sister Oncor project): 0 records found. [negative — confirmed; AEP Texas IAs do NOT appear to be filed via PUCT Interchange, unlike Oncor]
- **SEC EDGAR "bracero pecan"**: 0 hits. [negative]
- **Reeves County abatement/Ch.313/JETI**: No hits (consistent with post-2022 BESS, Ch.313 closed 2023). [negative — expected]
- **TCEQ permit**: Not expected for BESS (no air emissions). [negative — expected]

---

## Stage 3 (continued) — Site pinpoint

**Best available pin:** 31.0420, -103.6530 (Saragosa substation per OSM/Overpass API)
- Method: POI name "SARAGOSA 138kV" → OSM power=substation tag, named "Saragosa", 138kV/69kV, AEP operated
- Confidence: medium-high (OSM data matches POI name and utility exactly; AEP Texas ERCOT West)
- BESS site will be within 0.5-1 km of this substation
- No delivery pin or parcel to confirm exact pad location within that radius

