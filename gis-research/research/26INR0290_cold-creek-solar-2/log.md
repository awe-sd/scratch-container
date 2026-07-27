# Research Log — Cold Creek Solar 2 (26INR0290)

Started: 2026-07-19

## Identity packet
- INR: 26INR0290
- Project: Cold Creek Solar 2
- LLC: Cold Creek Solar 2, LLC (to verify)
- County: Schleicher, Texas
- MW: 431.87 MW Solar PV
- POI: Tap 345kV line Big Hill (#76003) - Twin Buttes (#76009)
- Zone: CDR WEST
- Reported COD: 2028-05-28

---

## Stage 1 — LLC → parent chain

### 2026-07-19 — Web research session

**ERCOT queue `interconnectingFacility` field** (from `ercotGenerationInterconnect` table, latest snapshot):
- 26INR0290 (Cold Creek Solar 2): `Cold Creek Solar LLC`
- 26INR0291 (Cold Creek Storage 2): `Cold Creek Solar LLC` (same LLC for both)

**Sibling/predecessor projects found in queue history:**
- 24INR0263 "Cold Creek  Solar" — Schleicher Co, 455 MW, first seen 2022-04-01, **cancelled 2025-02-18**. Same `interconnectingFacility`: `Cold Creek Solar LLC`. Same POI: Big Hill Substation 345kV (#76003).
- 24INR0266 "Cold Creek Storage" — Schleicher Co, cancelled 2025-02-18 same day.
- 26INR0290/26INR0291 are the replacement pair, entered queue 2023-11-01/2023-12-01.

**TX Comptroller franchise tax search** (https://comptroller.texas.gov/data-search/franchise-tax):
- `COLD CREEK SOLAR LLC` — taxpayerID 32083120132, SOS file 0804438674
  - Formed: Delaware, effective TX registration 2022-02-07
  - Mailing: **1999 Bryan St Ste 900, Dallas TX 75201**
  - Registered agent: C T Corporation System, 1999 Bryan St Ste 900, Dallas TX 75201
  - Officer (2026 report): **Evan Speece, Treasurer**, 1601 Elm St Ste 4360, Dallas TX 75201
- `COLD CREEK SOLAR AND STORAGE LLC` — taxpayerID 32099707765, SOS file 0805991598
  - Formed: Delaware, effective TX registration 2025-04-14 (day before IA signed 2025-04-23)
  - Mailing: 1999 Bryan St Ste 990, Dallas TX 75201
  - No officers listed yet

**Developer identity — CLEARWAY ENERGY GROUP:**
- Evan Speece appears in Clearway Energy LLC / Clearway Energy Operating LLC SEC 8-K filings from 2020 (as "Senior Management Personnel" for Clearway Energy Operating LLC as Assignee in a MIPA).
  - SEC accession: 0001104659-20-048786 (filed 2020-04-20, Clearway Energy LLC CIK 0001637757)
- `CLEARWAY ASSET SERVICES LLC` (TX Comptroller 32067889454) has mailing address **1999 Bryan St Ste 900 Dallas TX 75201** — same address as Cold Creek Solar LLC.
- `CLEARWAY ENERGY GROUP LLC` (TX Comptroller 32067634686) uses same registered agent (C T Corp at 1999 Bryan St Ste 900 Dallas).
- Parent chain: **Cold Creek Solar LLC → Clearway Energy Group LLC** (Princeton NJ / San Francisco CA parent, NYSE: CWEN via Clearway Energy Inc.)

**No press releases, EPC announcements, or PPA announcements found** — extensive search of SEC EDGAR full-text, prnewswire, businesswire, pv-tech, solar power world, utility dive returned nothing for "Cold Creek Solar 2" or "Cold Creek Solar" in Texas. Project has no public web footprint as of 2026-07-19.

**Sources:**
- TX Comptroller API: https://comptroller.texas.gov/data-search/franchise-tax?name=cold+creek+solar (2026-07-19)
- TX Comptroller detail: https://comptroller.texas.gov/data-search/franchise-tax/32083120132 (2026-07-19)
- EDGAR EFTS: efts.sec.gov search for "Evan Speece" → 6 hits, all Clearway Energy LLC/Inc (2020)
- EDGAR filing: https://www.sec.gov/Archives/edgar/data/1637757/000110465920048786/tm2016404d1_ex10-2.htm


### 2026-07-19 — TX Comptroller entity search
- Source: TX Comptroller franchise tax search
- Query: "Cold Creek Solar"
- Result: Cold Creek Solar LLC (TID 32083120132, SOS 0804438674) — DE corp, TX registered 2022-02-07, 1999 Bryan St Ste 900 Dallas TX 75201, registered agent C T Corp. Officer: Evan Speece (Treasurer), 1601 Elm St Ste 4360 Dallas TX 75201
- Cold Creek Solar and Storage LLC (SOS 0805991598) — DE corp, TX registered 2025-04-14, 1999 Bryan St Ste 990 Dallas TX 75201
- Why it matters: Same mailing address (1999 Bryan St Dallas) = Clearway Energy Group. Evan Speece confirmed Clearway Energy Operating LLC officer via SEC EDGAR.

### 2026-07-19 — Developer chain resolved
- Clearway Energy Group LLC: private, backed by GIP (Global Infrastructure Partners)
- Chain: Cold Creek Solar 2, LLC → Clearway Energy Group LLC → GIP
- Cold Creek Solar and Storage LLC registered 2025-04-14 (one week before IA signed 2025-04-23) — likely the combined solar+storage entity for 26INR0290+26INR0291

### 2026-07-19 — Predecessor projects
- 24INR0263 "Cold Creek Solar" (455 MW, same POI Big Hill #76003, same county) — first queue 2022-04-01, CANCELLED 2025-02-18. COD drifted 2024-06-01 → 2026-12-31. FIS requested, no IA.
- 24INR0266 "Cold Creek Storage" — also cancelled 2025-02-18.
- 26INR0290/26INR0291 are the re-filed replacement pair.
- Why it matters: Clearway has real commitment — re-filed after cancellation, registered new LLC, appears to have signed IA. But predecessor cancellation is a risk flag.

### 2026-07-19 — No press releases found
- Search: "Cold Creek Solar 2 Texas", "Cold Creek Solar 2 LLC", PRNewswire/BusinessWire/pv-mag/UtilityDive
- Result: Zero press coverage. No EPC, no PPA, no groundbreaking announcements.
- Negative evidence logged.

## Stage 2 — County records sweep

echo "log appended"
### 2026-07-19 — BUDGET EXHAUSTED — emergency write
- Stages completed: Stage 1 (LLC→parent chain)
- Stages NOT completed: Stage 2 (county records), Stage 3 (site pinpoint), Stage 4 (satellite), Stage 5 (wrap-up)
- findings.json and dossier.md written with available evidence + honest "incomplete" flags
- Wrap-up commands (queue_history.py, build_brief.py, build_index.py) NOT run
