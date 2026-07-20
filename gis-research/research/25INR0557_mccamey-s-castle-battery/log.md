# Triage log — McCamey's Castle Battery (25INR0557)

T1 start
## T1 — Queue history
- 33 snapshots (2023-10-01 → 2026-06-01), 2 COD changes
- IA signed: 2025-03-20 ✓
- Construction start (reported): 2026-05-28 ✓ (very recent; first appeared 2025-10-01)
- Construction end (reported): 2027-03-31
- FIS approved: NOT achieved
- Meets all 6.9: NOT achieved
- COD drift: 2025-12-15 → 2027-03-31 → 2028-03-30 (~2.25 yr total slip)
- Reported COD: 2028-03-30 (current claim)

T2 start
## T2 — Delivery pins
- gmaps.py: HTTP 429 on all 3 queries (rate-limited); one retry attempted, still 429
- No pins found; logging as blocked
- pins_found: 0

T3 start
## T3 — Web sweep
- Developer name: **Castle Storage, LLC** (consistent across 3 sources; NOT "McCamey's Castle Battery LLC")
- No press releases or official developer announcements found
- ercotqueue.com status: "currently Construction" with "build-chance 91%"
- Parent company: unknown / not identified
- No other Castle Storage projects found in sweep
- Sources: infrasure.ai, cleanview.co, interconnection.fyi, ercotqueue.com — all third-party trackers, no primary sources
- news_found: false (no direct developer PR/news)

T4 start
## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all attempts (root + search endpoints)
- One retry attempted, still 402 — logging as blocked
- IA signed 2025-03-20 per queue data but PDF not retrieved
- ia_found: false (portal blocked)

T5 start
## T5 — Abatements
- TX Comptroller Ch. 313: program sunset post-2022; no searchable database accessible
- JETI registry: no county-level search available through public pages
- abatement_found: false (normal for post-2022 battery project)

T6 start
## T6 — Imagery
- Site candidate: 31.13, -102.19 (McCamey TX, near Robbins Switch 138kV — approximate)
- 3x3 grid attempted; 8/9 chips failed CDSE auth (401/403 — cred issue)
- 1 chip retrieved: s2_31.13_-102.19_2026-06-01.png
- Observation: large pale graded rectangular pad visible upper-center frame; no container rows or BESS signatures; possibly site prep or unrelated grading
- construction_visible: false (inconclusive; insufficient coverage)
- No baseline chip attempted (insufficient coverage to justify)

T7 start
## T7 — Outputs written
- triage_findings.json ✓
- triage.md ✓
- Turns used: ~28

## Deep scan — 2026-07-19

### D1 — Queue data deep dive
- Full 35-row history extracted from parquet
- Key anomaly: inActiveDate briefly appeared 2025-11-01 snapshot (2025-11-18 10:42:15 timestamp) then cleared by 2025-12-01 — project was temporarily marked inactive, then reinstated. This is a significant project health signal.
- COD drift: 2025-12-15 → 2027-03-31 (changed 2025-10-01 with constructionStart first appearing) → 2028-03-30 (changed 2026-04-01)
- FIS still not approved; meetsAllSection69 never achieved. ginrStudyPhase stuck at "SS Completed, FIS Started, IA"
- constructionStart 2026-05-28 first appeared in Oct-2025 snapshot (before construction date itself)
- constructionEnd (reported) 2027-03-31 but current COD is 2028-03-30 (+12 months beyond reported construction end)

### D2 — POI / Substation identification
- "76597 Robbins Switch 138kV" = ERCOT bus 76597 named "Robbins Switch," 138kV
- No OSM substation named "Robbins" within 100km of McCamey
- OSM data shows these 138kV substations near McCamey: McCamey Sub (31.1372, -102.2033, AEP), North McCamey (31.1535-1551, -102.2233-2268, LCRA/AEP 345/138kV), Castle Gap (31.1157, -102.2951, AEP 138kV)
- "Robbins Switch 138kV" not in OSM → likely a new switching station being constructed for this project, or ERCOT network model name for an existing AEP switching bus
- Bus 76000 = North McCamey 345kV; 76597 = Robbins Switch 138kV (a 138kV bus in the same numeric family, suggests same substation complex)
- Best POI candidate: near McCamey AEP substation area or a tap point off the 138kV line between McCamey and North McCamey subs
- Site lat/lon estimate: ~31.137, -102.203 (McCamey Substation, AEP) or a tap point nearby
- Upton County CAD: 0 hits for "Castle Storage" or "McCamey Castle" as of 2025 — no parcels registered yet (consistent with BESS needing minimal land and being early in permitting)

### D3 — Developer identity
- LLC name from GIS data: "Castle Storage, LLC"
- No TX Comptroller / SOS results accessible (API redirect; SOSDirect requires fee)
- SEC EDGAR: consistently 403 blocked
- LinkedIn: "Castle Storage" returns only a self-storage company in Iowa — wrong entity
- No press releases, developer website, or public announcements found
- Only 3rd-party trackers (banned sources) reference the developer
- Castle Storage LLC = unknown parent; may be a newly-formed SPV with no public footprint

### D4 — County records
- Upton CAD: 0 hits for "Castle Storage" (2025 tax year) — no parcels registered
- "McCamey Castle" CAD search: 0 hits
- Chapter 313 program sunset 2022 — not applicable
- JETI: no application found (normal for 2023-vintage project)
- Commissioners court: website not accessible

### D5 — PUCT Interchange
- All attempts to PUCT Interchange returned HTTP 402 — consistently blocked
- IA signed 2025-03-20 per ERCOT GIS data — real document exists but not retrieved

### D6 — Imagery
- CDSE auth: 401/403 on all chip attempts — credentials expired/invalid
- Existing triage chip: 31.13, -102.19, 2026-06-01: large pale graded rectangular pad visible upper-center; no BESS container rows confirmed
- Grid chips: g_31.12_-102.22 = McCamey town center (no industrial activity); g_31.16_-102.22 = scrubland; g_31.12_-102.16 = scrubland; g_31.12_-102.10 = badlands
- The pale graded pad in the triage chip at upper-center (~31.15, -102.19) could be: (a) existing industrial pad (oil/gas), (b) early site prep for BESS
- Cannot confirm BESS installation without fresh imagery at proper POI location

### D7 — Synthesis context
- McCamey Substation (AEP 138kV, 31.1372, -102.2033) is likely closest to POI "Robbins Switch 138kV"
- North McCamey substations (31.153-155, -102.222-227) also candidates — the "76000 North McCamey 345kV" bus family is large
- Castle Gap (31.1157, -102.2951) is further west
- Site should be within 1-2km of McCamey AEP substation or a switching station tap on the 138kV corridor
