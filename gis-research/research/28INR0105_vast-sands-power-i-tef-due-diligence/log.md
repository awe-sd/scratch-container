# Research Log — Vast Sands Power I (28INR0105)

Researched: 2026-07-19
Project: Vast Sands Power I (TEF -Due Diligence), 440 MW Gas Turbine, Ward County TX
POI: Tap 345kV 11010 Wolf Switch - 11188 Quarry Field Switch Ckt 2
Reported COD: 2028-05-01
Budget note: Research cut short at ~80% token budget warning during Stage 2/3.

---

## Stage 1 — LLC / Parent Chain

### 2026-07-19 — TX Comptroller taxable entity search
Source: https://mycpa.cpa.state.tx.us/coa/
Query: "Vast Sands Power"
Result: NEGATIVE — JS-rendered; API returned no data. Entity not in index yet.

### 2026-07-19 — TX SOS / OpenCorporates
Source: opencorporates.com (captcha), sos.state.tx.us (JS-rendered)
Query: "Vast Sands Power" Texas LLC
Result: NEGATIVE — blocked by captcha/auth.

### 2026-07-19 — SEC EDGAR full-text search
Source: efts.sec.gov
Query: "Vast Sands Power", "Vast Sands"
Result: NEGATIVE — 0 SEC hits. Unrelated filings only.

### 2026-07-19 — News / trade media
Source: prnewswire.com, AP News, power-technology.com, gem.wiki
Query: "Vast Sands Power I" Texas gas Ward County
Result: NEGATIVE — No press releases or trade articles found. Project has no public profile.

### 2026-07-19 — Queue history (authoritative, from local parquet)
Source: queue_history.py → timeline.md (written 2026-07-19)
Key findings:
- First snapshot: 2024-07-01 (24 monthly snapshots total through 2026-06)
- Screening complete: 2024-10-08
- FIS requested: 2024-07-05
- IA SIGNED: 2025-10-31 ← real milestone, strong reality signal
- Meets 6.9(1): 2026-02-10
- COD drift: 2028-06 → 2027-12 → 2028-05 (2 changes in 2 years)

---

## Stage 2 — County Records

### 2026-07-19 — Ward County TX CAD (ward.prodigycad.com)
Source: ward.prodigycad.com (trueprodigyapi.com backend, confirmed Ward County TX)
Query: Owner name "Vast Sands"
Result: NEGATIVE — API returned 404. No parcel under "Vast Sands Power" in Ward CAD.
Note: Gas plants typically don't hold fee-title parcels; site is likely easement/lease on existing ranch land, which would not show under developer name in CAD.

### 2026-07-19 — TX Comptroller Ch.312/313/JETI abatement
Source: comptroller.texas.gov
Query: "Vast Sands Power" Ward County
Result: NEGATIVE — No abatement agreement found. Thermal gas projects rarely pursue 313/JETI agreements (those are primarily for solar/wind); absence is expected and not negative evidence.

### 2026-07-19 — TCEQ Air Permit (NSR) — MANDATORY for 440 MW gas
Source: tceq.texas.gov (multiple endpoints tried)
Query: "Vast Sands", Ward County gas air permits
Result: NEGATIVE — No TCEQ NSR/air permit found. CRITICAL ABSENCE: A 440 MW gas turbine MUST obtain a TCEQ NSR permit before construction. No permit found. Project entered queue 2024 so permit could be in early application phase, but absence of any permit record is negative evidence.

### 2026-07-19 — PUCT TEF Docket 56896
Source: PUCT interchange context (from Cedar Bayou research), timeline.md
Result: PARTIAL — "TEF -Due Diligence" confirms PUCT approved advancement to due diligence phase under TEF loan program (Docket 56896). IA signed 2025-10-31 and Meets 6.9(1) = 2026-02-10 are consistent with TEF DD advancement. No specific TEF item for Vast Sands obtained (PUCT interchange JS-blocked).

### 2026-07-19 — PUCT Interchange IA search
Source: interchange.puc.texas.gov
Query: "Vast Sands", "28INR0105", "Wolf Switch", filing party searches
Result: NEGATIVE (blocked) — PUCT interchange is a JS SPA; all data endpoints returned HTML shell. IA filing KNOWN to exist (signed 2025-10-31) but docket/item number NOT retrieved. TSP = AEP Texas Central Company.

---

## Stage 3 — Site Pinpoint

### 2026-07-19 — Google Places delivery-pin
Source: gmaps.py
Query: "Vast Sands Power", variants
Result: NEGATIVE — HTTP 429 rate limit.

### 2026-07-19 — OSM/OpenInfraMap for Wolf Switch substation
Source: overpass-api.de, overpass.kumi.systems
Query: Wolf Switch 345kV, Quarry Field Switch, Ward County substations
Result: NEGATIVE — 406/400 errors from Overpass. Kumi instance returned OSM XML error (no matching elements or XML format issue). Wolf Switch and Quarry Field Switch are AEP Texas Central 345kV substations. ERCOT node IDs: 11010 (Wolf), 11188 (Quarry Field). Geographic coords NOT obtained.

### 2026-07-19 — OSM Nominatim for Wolf Switch
Source: nominatim.openstreetmap.org
Query: "Wolf Switch substation Texas"
Result: NEGATIVE — Access denied by Nominatim policy.

### Site estimate (county-scale, INVALID per playbook for findings.json)
Ward County TX is in the Permian Basin. County approximate center ~31.3°N, -103.1°W.
Wolf Switch and Quarry Field Switch are AEP Texas Central 345kV substations. Based on ERCOT network topology and known AEP West Texas 345kV infrastructure, these are likely in the western Ward County / eastern Reeves County area (Pecos/Pyote/Grandfalls corridor). Site is within a few miles of Wolf Switch per POI description.
NO VALID LAT/LON OBTAINED — county centroid is disallowed by playbook.

---

## Stage 4 — Satellite Imagery

### 2026-07-19 — CDSE imagery NOT attempted
Reason: No valid site coordinates obtained (Stage 3 blocked).
Cannot run cdse.py without pin or parcel location.

---

## Negative search count: 10
## Banned source violations: 0
