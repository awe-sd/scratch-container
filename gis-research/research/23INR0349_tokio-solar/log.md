# Triage log — Tokio Solar (23INR0349)

## T1 start
queue_history.py ran: 50 snapshots (2022-05-01 → 2026-06-01)

**COD drift (3 changes):**
- 2024-10-31 (held 1 month: 2022-05)
- 2025-03-24 (held 1 month: 2022-07)
- 2025-08-25 (held ~25 months: 2022-08 → 2024-08)
- 2027-08-25 (current, held since 2024-09)

Total drift: ~3 years from original COD (2024-10-31 → 2027-08-25).

**Milestones achieved:** Screening started 2021-08-12, Screening complete 2021-11-01, FIS requested 2022-04-14, IA signed 2023-11-06, Meets 6.9(1) 2023-11-17.
**Not yet:** FIS approved, Meets all 6.9, construction start/end, energization, sync, COA.

**Capacity changes:** 175 → 177.64 → 175.72 → 170.45 MW (current). Minor trimming, settled.

**Milestone gap:** IA signed but FIS NOT approved — unusual (IA without FIS approval). Note for deep scan.

## T2 start
gmaps.py: HTTP 429 on both attempts (rate-limited). Per rules: one retry done → negative log.
**Pins found: 0** (tool blocked, not conclusive absence)

## T3 start
**Developer identified: Gransolar Texas Eight, LLC** (Irving TX; parent: Gransolar Group, Spain; 3.1 GW globally, 18 TX assets ~3,313 MW)
- LLC incorporated TX 2021-07-09; address 125 E John Carpenter Blvd Ste 1325, Irving TX 75062
- Only 1 ERCOT project on file (this one)
- PUC Control Number **35077** found — IA filed 2023-11-30 (Oncor + Gransolar Texas Eight)
- EIA Plant Code: 66397 ("Tokio")
- Build-chance estimate (ercotqueue.com): 26%
- No news articles found; project in pre-construction per aggregators
- cleanview.co behind login — skipped

Sources: DDG search results (ercotqueue.com, interconnection.fyi, infrasure.ai, cleanview.co, PUCT Interchange via web aggregators)

## T4 start
PUCT Interchange (interchange.puc.texas.gov) returning HTTP 402 on all URL patterns tried. Portal blocked; per rules: one retry done → negative log.
**IA confirmed exists (from T3 web sweep):** Control No. 35077, filed 2023-11-30, Oncor + Gransolar Texas Eight LLC. But PDF contents (milestone schedule) inaccessible via WebFetch.
**IA found: YES** (from external aggregators); schedule exhibit: NOT retrieved (portal blocked)

## T5 start
TX Comptroller Ch.313: no searchable online database accessible via WebFetch; Comptroller pages are nav-only.
DDG search for Tokio Solar/Gransolar + McLennan + Ch.313/JETI: no results.
**Abatement found: NO** (normal for post-2022 project; Ch.313 expired Dec 2022, JETI is replacement but no hit found)

## T6 start
Site candidate: Waco Atco substation vicinity — 31.41°N, 97.15°W (SE of Hewitt TX), LOW confidence.
- No pin from T2 (gmaps blocked), no confirmed address from web sweep
- POI "Tap 138kV 3592 Waco Atco - 170 Cotton Belt" → substation anchor only; actual site unknown
- Ran 1 chip: 31.41°N 97.15°W, 2026-07-01, 2km buffer
- Result: agricultural farmland (green/fallow fields), no solar infrastructure, no construction visible
- 1 full-size frame read used (1/3 budget)
- Cannot confirm this IS the project site — just the POI infrastructure area
**Construction visible: NO** (at low-confidence location)

## T7 start
Wrote triage_findings.json and triage.md.
**Turns used: ~22. Run complete.**

## D0 — findings.json skeleton written (2026-07-20)

## D1 — IA exhibit extraction

**IA on disk:** `sources/2026-07-19_puct_35077-1720_generation-interconnection-agreement-between-onc.pdf`
Filed 2023-11-30, PUCT Control 35077, Oncor + Gransolar Texas Eight LLC

**Exhibit B (Time Schedule) — p29:**
- Notice to proceed: November 8, 2025
- In-Service Date: **May 8, 2025**
- Trial Operation Date: **April 27, 2025**
- Scheduled COD: **August 25, 2025**
- TSP Metering Design Proposal to ERCOT: October 17, 2024
- Sunflower Switch grading/all-weather road: August 13, 2024
- Easements/deeds for Sunflower Switch: June 7, 2024

**Exhibit C (Interconnection Details) — p32:**
- Project name: Tokio Solar
- POI: Sunflower Switch in Waco West Sub – Temple Elm Creek Switch 138 kV Line, McLennan County TX
- **"The Sunflower Switch will be located approximately 16 miles SW of Waco, Texas off of Hwy US-84 W."**
- 59 Sungrow SG3425UD_MV inverters; 202.08 MVA nameplate; 177.64 MW dispatched
- Delivery voltage: 138 kV

**Key signal:** Original IA COD = 2025-08-25; queue COD = 2027-08-25 → exactly 2-year slip, no construction visible yet.

Rendered map/exhibit pages saved: sources/..._p29.png, p30.png, p31.png, p32.png, p41.png

## D1/D2 continuation (2026-07-20)

**Financial security (Exhibit E, IA p50-51):**
- $7,882,720 irrevocable standby letter of credit, due on or before 2023-11-08
- Confirms financial commitment posted

**EIA history (eia_history.py --write):**
- Plant 66397 'Tokio Solar', entity Gransolar Texas Eight LLC (name match)
- Reports: 2023-03-01 → 2026-05-01 (38 monthly snapshots)
- COD: 2025-08 → 2026-08 → 2027-08 (3 slips in EIA reporting)
- Capacity: 175.0 MW (2023-03 to 2024-12) → 170.4 MW (2025-01 onward)
- Status: "(P) Planned for installation, but regulatory approvals not initiated" — HELD ALL 38 MONTHS
- EIA coords: 31.42742, -97.31086 confirmed
- Written to eia_history.json

**CDSE imagery (D2):**
- Auth OK (token confirmed); openEO job submission fails with RemoteDisconnected — endpoint down
- Attempts at 31.4274, -97.3109 for 2026-07-01 and 2026-06-01: all failed
- Triage chip (31.41, -97.15 = wrong location near substation) shows agricultural farmland — not conclusive
- CDSE imagery: NOT OBTAINED for confirmed coords — log as negative evidence; construction verdict based on EIA status + absence of news

**D3 gap-fill:**
- McLennan CAD: JS-gated portal, no curl result for owner "Gransolar" — negative evidence logged
- Ch.313/JETI: no hit (expected — 2023 project, Ch.313 expired 2022)
- No JETI application found
- No news/permitting/construction announcements found
- No Google Places pin (gmaps returned no TX result for "Tokio Solar" or "Gransolar Texas")
- GEM wiki confirms coords 31.4274, -97.3109 (cites EIA-860M; status: announced)
- Developer identity: Gransolar Group (Spain) 100% owner per GEM; no Adapture transfer confirmed in primary sources

## Imagery gap-fill (2026-07-21)

**Provenance re-derivation (per task instructions to imagery-verify any EIA pin before trusting it):**
- `exhibit.py list`/`scan` re-run over both IA PDFs in sources/ (51pp each): no dedicated GPS map/site-plat exhibit exists — only Exhibit C text description and Attachment 1 (One Line Diagram, Sunflower Switch, taps to "Waco Atco" and "Cotton Belt" lines) and Attachment 2A (comms block diagram). Rendered/read p44 (One Line Diagram) and p45 (SCADA table) to confirm — no coordinates or map. So the map-exhibit rung is unavailable for this project; EIA-860M is the best rung.
- Checked the specific risk called out in the task — "EIA pins have been town centroids before" — against the literal name coincidence here: there IS a real hamlet named "Tokio, TX" in McLennan County. Geocoded it (Nominatim): 31.7585, -97.1558, ~14.5 mi **north** of Waco. The EIA plant coordinate (31.42742, -97.31086) is ~12.8 mi **southwest** of Waco — a completely different location/direction. Confirmed the EIA pin is NOT the Tokio-hamlet centroid; the project is simply named after a place it isn't located at (or the name predates/is unrelated to siting).
- Cross-validated the EIA pin against IA Exhibit C's text description ("Sunflower Switch ... approximately 16 miles SW of Waco, Texas off of Hwy US-84 W"): reverse-geocoded the EIA coord → sits ~5.8 mi from McGregor, TX center; Overpass confirms "West US Highway 84" runs within ~3 mi. Direction (SW of Waco) and rough distance (12.8 mi straight-line vs. "16 miles", plausible given US-84's diagonal routing vs. straight-line) both check out. Confidence raised **med → high**.
- Checked `data/eia_generator_tx.parquet` (latest reportDate 2026-05-01, county=='McLennan') for operating/UC neighbors: nearest is EDFR Bluebonnet (9.9 MW solar, operating since 2023-09) at 31.411854,-97.42367, ~6.8 mi from the Tokio anchor — well outside the 3.5 km imagery buffer, so no neighbor-attribution risk. Also noted a same-developer sibling, Braswell Solar (Gransolar Texas Nine LLC, plant 67772), ~7.7 mi away, also not-yet-built ("(L) Regulatory approvals pending").

**Imagery fetch:** `s2aws.py chips --lat 31.42742 --lon -97.31086 --dates 2024-07-01,2025-07-01,2026-01-15,2026-04-15,2026-07-15 --out-dir imagery/key --buffer-km 3.5 --window-days 20 --max-cloud 25` — all 5 dates returned real scenes (magic-byte PNG-verified): S2A 2024-07-19 (24.0% cloud), S2C 2025-07-17 (12.1%), S2B 2026-01-28 (22.7%), S2C 2026-05-03 (0.2%), S2C 2026-07-19 (0.9%).

**Read all 5 frames.** Framing is full-coverage with margin (7km-wide chip around a site that would be ~1000 acres / ~4 km² at most); no tile-seam clipping. All 5 show the same field/road/creek pattern (a paved N-S road, a wooded creek corridor through center, surrounding row-crop/pasture parcels) — 2024-07 and 2026-01 have partial cloud/cloud-shadow but the visible ground is consistently agricultural. **No solar array, grading, access-road grid, or laydown yard visible in any frame at any date.** Construction verdict stands: **no_activity**, first_activity_seen: null — consistent with EIA status held "(P) Planned, regulatory approvals not initiated" across all 38 reported months.

**Housekeeping:** moved a stray pre-existing wrong-location probe chip (`s2_center_2026-07-01.png`, sitting in the project root from a prior session, not the imagery/ dir) to /tmp scratch per convention.

findings.json updated: site.method/confidence (med→high, provenance re-derivation documented), construction.evidence/imagery_artifacts/latest_observation. brief.html rebuilt.
