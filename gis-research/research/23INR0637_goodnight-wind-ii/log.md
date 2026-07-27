# Research Log — Goodnight Wind II (23INR0637)

Project: Goodnight Wind II | 259.2 MW Wind | Armstrong County, TX | POI: tap 345kV 23900 Alibates - 23914 Tule Canyon CKT2 | CDR: PANHANDLE | Reported COD: 2027-06-06

---

## 2026-07-19 Session

### Stage 1 — LLC → parent chain


#### Stage 1 findings (2026-07-19)

**LLC → Parent chain:**
- FGE Power LLC (Austin, TX; founder Emerson G. Farrell) = original developer
- 100% sale announced 2026-07-18 2022 to Omega Energia (São Paulo, Brazil; CEO Antonio Bastos Filho)
- Omega Energia later rebranded as Serena Energia (domain omegaenergia.com.br → srna.co)
- All three Goodnight phases are in Armstrong County; Goodnight I = 265.5MW, II = 265.5MW (~259.2 MW in GIS), III = 200+ MW
- Vestas V136-4.5MW turbines; EPC: IEA (Infrastructure and Energy Alternatives)
- Source: PR Newswire press release https://www.prnewswire.com/news-releases/fge-power-announces-sale-of-fge-goodnight-wind-farm-project-to-omega-energia-301588378.html
- FGE Power portfolio page: https://www.fgepower.com/portfolio lists all three Goodnight phases, Armstrong County

**Negative searches Stage 1:**
- TX Comptroller taxable entity form: JS form, cannot submit programmatically — NEGATIVE
- TX SOSDirect: requires login — NEGATIVE
- LinkedIn: requires authentication — NEGATIVE
- ERCOT NOM files for Alibates/Tule Canyon node confirmation: 404/403 — NEGATIVE

ARTIFACT NEEDED: Save PR Newswire press release


---

## 2026-07-19 Deep-Scan Session

### Stage 1 — LLC chain (continued from triage)

**Ownership chain confirmed:**
- FGE Goodnight II, LLC (Texas taxpayer ID 32064194957) = SPV
  - Source: Ch.313 Amendment 3 cover letter, March 25, 2026 ([amend3](sources/2026-07-19_comptroller_ch313_1507-fge-goodnight-ii-amend3.pdf))
- Developer: FGE Power LLC (Austin, TX; Emerson G. Farrell, Founder/Chairman)
  - Source: PR Newswire 2022-07-18 ([pr](sources/2026-07-19_prnewswire_fge-goodnight-sale-to-omega.html))
- Current owner: Omega Energia (São Paulo, Brazil; CEO Antonio Bastos Filho) → rebranded as Serena Energia (srna.co)
  - 100% ownership acquired July 18, 2022
  - Contact in amendment: Giulia Ribeiro (Legal & Structuring, Serena), Andrea Sztajn (CFO, Serena)
- EPC contractor named for Phase I: IEA (Infrastructure and Energy Alternatives) — Phase II EPC not explicitly stated in PR
- Turbines: Vestas V136-4.5MW (named for Phase I; Phase II turbine not confirmed from this source)
- Signed by FGE Goodnight II, LLC rep on Amendment 3: signature not legible but title blank

### Stage 2 — County & regulatory records

**Ch.313 Amendment 3 (Comptroller App 1507, signed 2026-03-24):**
- Parties: Claude ISD + FGE Goodnight II, LLC
- Key change: Tax Limitation Period START pushed to January 1, 2028 (from prior earlier date)
- Tax Limitation Period: Jan 1, 2028 → Dec 31, 2037 (10 years)
- Final Termination Date: Dec 31, 2042
- This implies commercial operations begin in 2027 (limitation starts first complete year AFTER commercial ops)
- Original agreement: Dec 10, 2020; Amendment 1: March 20, 2023; Amendment 2: Oct 21, 2024; Amendment 3: March 24, 2026
- Artifact: [amend3](sources/2026-07-19_comptroller_ch313_1507-fge-goodnight-ii-amend3.pdf)
- NOTE: Original agreement PDF returned 403 Access Denied — original 2020 terms not readable

**Negative searches:**
- Armstrong CAD owner search for "Goodnight" and "FGE" — search portal returned 404 on direct URL attempts; dynamic site requires JS-driven form
- PUCT Interchange search returned 402 — IA not retrieved
- FAA OE/AAA portal: government shutdown notice — new Part 77 filings suspended; search portal returned 404

### Stage 3 — Site identification

**EIA Form 860M (May 2026) — DECISIVE:**
- Plant: Goodnight Wind II, Plant ID 69403
- Entity: FGE Goodnight II, LLC (Entity ID 67462)
- Lat: **34.937162**, Lon: **-101.4339**
- Status: **(U) Under construction, ≤ 50% complete**
- Planned Operation: May 2027
- Capacity: 265.5 MW nameplate
- Technology: Onshore Wind Turbine
- Source: EIA 860M May 2026 (https://www.eia.gov/electricity/data/eia860m/xls/may_generator2026.xlsx)

**Sister plant Goodnight I (Phase I) for cross-check:**
- Plant ID 59246, Entity 65226 (FGE Goodnight I, LLC)
- Lat: 35.093889, Lon: -101.3261
- Operating since April 2024 (COD achieved)
- ~17 km north-northeast of Phase II site

**Confidence: HIGH** — EIA 860M is a primary regulatory filing by the project owner


### Stage 4 — Satellite imagery

**Chip 1: Phase II site (EIA coord), 2026-06-15 ±15d, 6km buffer**
- File: imagery/s2_2026-06-15.png
- Observation: Site straddles the Palo Duro Canyon escarpment. Northern half shows flat agricultural plateau (correct terrain for wind turbines). No obvious construction pads visible in this frame — the EIA coordinate (34.937, -101.434) is at the canyon edge; turbine array likely extends further north.
- Note: This is the EIA-reported centroid; wind farm footprint extends across wider area.

**Chip 2: Phase I (operating) comparison, 2026-06-15 ±15d, 6km buffer**  
- File: imagery/s2_phaseI_2026-06-15.png
- Observation: Clear wind farm road network visible — characteristic thin white access roads branching across farmland in lower-center and right portions of frame. Town of Claude (Armstrong County seat) visible upper-left. This confirms what Phase II construction activity should look like once visible.

**Additional imagery attempts:**
- Phase II plateau (34.98, -101.45): CDSE authentication failed (HTTP 401) — token expired during session
- CDSE credentials test: HTTP 401 "Invalid user credentials" — password may have changed

**Imagery verdict:** EIA 860M says "Under construction, ≤50% complete" (May 2026). The CDSE failure prevented a fresh plateau chip, but Phase II is south-southwest of Phase I — turbine arrays from both phases likely form a contiguous or nearby wind complex.

**Negative searches:**
- FAA OE/AAA portal: government shutdown notice active; Part 77 filings suspended; search portal 404
- GMaps Places/Delivery pin (Goodnight Wind II): HTTP 429 (rate limit) during deep-scan
- GMaps Static map: Maps Static API not enabled for this key (403)


### Stage 5 — Synthesis artifacts written
- findings.json: written 2026-07-19
- dossier.md: written 2026-07-19
- brief.html: generated by build_brief.py (6KB)
- timeline.md: regenerated (38 snapshots, 7 COD changes)
- index.json / INDEX.md: refreshed (87 projects)

