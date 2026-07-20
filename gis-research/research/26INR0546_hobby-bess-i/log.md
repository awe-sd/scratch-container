# Research Log — Hobby BESS I (26INR0546)

Date: 2026-07-19 | Researcher: deep-agent

## Identity packet
- Project: Hobby BESS I
- INR: 26INR0546
- LLC guess: Hobby BESS I, LLC
- County: Harris, Texas
- Capacity: 602.56 MW
- Fuel/tech: Battery/Storage
- POI: "Double Tap 138kV 42680 Garden Villas – 48250 Hall & 42680 Garden Villas – 48013 Chocolate Bayou"
- CDR zone: HOUSTON
- Reported COD: 2027-10-15

---

## Stage 1 — LLC → parent chain

### 2026-07-19 | Queue history retrieved — CRITICAL
- timeline.md written: 23 snapshots (2024-08 → 2026-06)
- **IA NOT SIGNED** (null in all snapshots) — strong paper-project signal
- FIS approved 2026-01-20; no IA 6 months later
- COD drifted once: 2026-07-31 → 2027-10-15 (+15 months)
- First reported 2024-08-01; screening complete 2024-12-03

### 2026-07-19 | TX Comptroller search — BLOCKED
- Direct API redirects to new portal; form POST returns empty (AJAX-based)
- Entity "Hobby BESS I LLC" — not found via direct API queries
- Need to try: TX SOS, DDG search for "Airport Storage II LLC"

### 2026-07-19 | Web search — "Airport Storage II LLC" lead
- DDG search surfaced "Airport Storage II LLC" as developer (from queue aggregators — banned as primary, but lead to chase)
- Cannot use queue aggregator results as evidence; need independent confirmation
- Bing searches for "Hobby BESS" returned no independent developer info
- PUCT Interchange search for "Hobby BESS" and "Airport Storage": returned "Control number not found" — NO SIGNED IA FILED

### 2026-07-19 | PUCT Interchange — NEGATIVE
- Search: FilingParty=Hobby BESS → "Control number not found"
- Search: FilingParty=Airport Storage → "Control number not found"
- **No interconnection agreement has been filed at PUCT** — confirms IA not signed

### 2026-07-19 | SEC EDGAR — NEGATIVE
- Full-text search "Airport Storage II": 0 hits (2020-2026)
- Full-text search "Hobby BESS I": 0 hits
- Full-text search "Hobby BESS": 0 hits
- No publicly registered entity, no project bond/financing documents at SEC

### 2026-07-19 | Developer ID — PARTIAL
- DDG result cited "Airport Storage II LLC" as developer (from banned aggregator — not usable as evidence)
- No independent confirmation found via Bing, EDGAR, PUCT, or TX Comptroller
- "Airport Storage" name consistent with near-Hobby-Airport location branding
- Developer identity: unconfirmed / unknown (no primary source found)

## Stage 4 — Satellite imagery

### 2026-07-19 | Imagery summary (budget-limited)
- s2_2026-07-01_gv_1km.png / tight_gv.png: 1km buffer around Garden Villas sub (29.6510, -95.3144) — dense residential, canal, no BESS pad
- s2_2026-07-01_gv_2km.png: 2km buffer — same pattern, wider suburban Houston, some commercial bottom-right, NO pale gravel pad + container rows
- s2_2026-07-01_cb_1km.png: Chocolate Bayou area — residential/commercial, no BESS activity
- Triage contact sheet showed same pattern across all chips
- **Verdict: no_activity** — no construction signatures anywhere near Garden Villas or Chocolate Bayou substations

## Stage 2/3 — County records & site pinpoint

### 2026-07-19 | POI geography — DECISIVE
- **Garden Villas substation found: 29.6510, -95.3144** (OSM via Overpass)
- Voltage: 138kV/69kV/12kV — confirmed 138kV matches POI
- Located in SE Houston, Harris County, ~2 miles west of Hobby Airport
- CenterPoint facility IDs: 42680=Garden Villas, 48250=Hall, 48013=Chocolate Bayou
- "Double Tap 138kV" = BESS connects at same 138kV bus via two separate circuits
- BESS site should be within ~1 km of Garden Villas substation at 29.6510, -95.3144
- Saved: sources/2026-07-19_openstreetmap_garden-villas-substation.json


