# Research Log — Crowded Star Solar (20INR0241)

Jones County, TX · 218.79 MW Solar PV · CDR zone WEST · Reported COD 2026-08-17
POI: tap 345kV 68001 Claytonville – 68004 Phantom Hill c2 (New Substation: Open Sky 68014)

---

## 2026-07-19 — Session start

### Stage 1 — LLC → parent chain

### 2026-07-19 — Queue timeline review (CRITICAL)

**FINDING: approvedForSynchronization = 2026-05-28** — project is already synchronized to the grid as of May 2026. This is near-operating status per ERCOT. Also approvedForEnergization = 2026-04-22. Commercial operation approval still pending as of June 2026 snapshot.

Key milestones:
- IA signed: 2023-07-27
- FIS approved: 2024-11-05
- Meets all 6.9: 2025-07-24
- Approved for energization: 2026-04-22
- Approved for synchronization: 2026-05-28
- Commercial operation approved: not yet (as of 2026-06 snapshot)

COD drift: 13 changes over 86 snapshots, starting from 2021-07-02, now at 2026-08-17. Capacity reduced from 400 MW to 218.79 MW.

This project is REAL and almost certainly already operating or in final commissioning. Verdict will be real_active at minimum.

Source: queue_history.py output → timeline.md (deterministic from local parquet)

### Stage 1 — LLC → parent chain

- SEC EDGAR full-text search for "Crowded Star Solar": 0 results (negative evidence). Logged 2026-07-19.
- TX Comptroller franchise search: AJAX-based, no direct URL query. Will need alternate approach.


### Stage 1 continued — LLC/parent search negative evidence

- SEC EDGAR full-text: 0 results for "Crowded Star Solar" (2026-07-19)
- SEC EDGAR full-text: 0 results for "Crowded Star" (2026-07-19)
- TX Comptroller franchise entity search: portal uses AJAX, no direct query URL available; tried multiple URL patterns, none worked (2026-07-19)
- TX Comptroller Ch313 agreement search: URL pattern changed/redirected; tried multiple data URLs (2026-07-19)
- Jones County commissioners court minutes (2020-2023): ~25 PDFs searched, no match for "crowded", "solar", "energy", "renewable", "312", "313", "abatement" in any minute (2026-07-19)
- Google Places API: quota exhausted (429 RATE_LIMIT_EXCEEDED) for today (2026-07-19)
- Google News search for "Crowded Star Solar": not found (2026-07-19)
- PR Newswire search: no results for Crowded Star Solar (2026-07-19)

### Stage 2 — County records negative evidence so far

Jones County CAD search: portal loads but requires JS for actual search — couldn't query by owner name programmatically (2026-07-19)


### Stage 3 — Site pinpoint

**Method: POI infrastructure proximity**
- Phantom Hill hamlet OSM: 32.6434, -99.6778 (Jones County)
- POI describes tap on 345kV line "68001 Claytonville – 68004 Phantom Hill c2"
- OSM 345kV line runs approximately 32.52–32.63°N, 99.54–99.82°W (unnamed Oncor line)
- Site lat/lon estimated as 32.643, -99.678 (Phantom Hill area) — LOW confidence
- Google Places quota exhausted (429) — no delivery pin obtained (negative, 2026-07-19)
- OSM Nominatim "Crowded Star Solar": 0 results (negative, 2026-07-19)
- OSM Nominatim "Open Sky substation": 0 results (negative, 2026-07-19)

### Stage 4 — Satellite imagery

Chips requested for Phantom Hill area (lat 32.643, lon -99.678) and nearby southern location (lat 32.600, lon -99.640) for 2026-07-01. Awaiting download.

### CRITICAL FINDING (Stage 2/5)

Queue timeline confirms:
- approvedForEnergization = 2026-04-22 → PHYSICAL PLANT EXISTS, ENERGIZED
- approvedForSynchronization = 2026-05-28 → SYNCHRONIZED TO ERCOT GRID
- commercialOperationApproved = NOT SET (as of 2026-06-01 snapshot)

This is definitively a REAL project, now in final commissioning. Verdict: real_active.

### Stage 1 — additional negative evidence

- TX Comptroller franchise entity search: AJAX-only portal, no direct URL query possible (2026-07-19)
- Jones County commissioners court minutes (2020-2023): ~25 PDFs — no solar/abatement mentions
- Parent/developer identity: NOT DETERMINED


### Stage 4 — Imagery interpretation

- s2_2026-07-01.png (lat 32.643, lon -99.678, 3km buffer): Shows agricultural fields, some circular irrigation, riparian area. NO solar array signature. Site coordinates likely off.
- s2_2026-07-01_south.png (lat 32.600, lon -99.640, 3km buffer): Shows Fort Phantom Lake (NW corner), agricultural fields. NO solar array. 
- CONCLUSION: Estimated coordinates do not match actual project site. The ERCOT energization/synchronization milestones remain the definitive evidence of construction completion — imagery only needed for location confirmation, which failed due to coordinate uncertainty.

