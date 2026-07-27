# Triage log — 25INR0368 Echols Grove Solar

## T1 start
- Script: `queue_history.py 25INR0368` → 40 snapshots (2023-03-01 → 2026-06-01)
- COD drift: 5 changes (2025-12-09 → 2025-12-31 → 2026-04-15 → 2026-12-31 → 2027-10-13 → 2027-04-03)
- Milestones achieved: Screening started (2023-04-07), Screening complete (2023-07-05), FIS requested (2023-03-22), FIS approved (2026-06-18, first in 2024-07-01 report), IA signed (2024-07-06, first in 2025-07-01 report — ~12 month reporting lag), Meets 6.9(1) (2025-07-08)
- Milestones NOT achieved: Meets all 6.9, Construction start/end, Approved for energization/synchronization/commercial operation
- Capacity changes: 203.5 MW → 201.15 MW → 201.56 MW (minor trim)
- Note: FIS approved date (2026-06-18) is very recent; IA signed 2024-07-06 but first appeared 2025-07-01 — unusual reporting lag. Meets 6.9(1) but NOT all 6.9 → still has open conditions.

## T2 start
- gmaps.py: HTTP 429 on first call, 429 on retry → blocked. No pins found.
- T2 result: 0 delivery pins.

## T3 start
- DDG html.duckduckgo.com: CAPTCHA block on both queries (exact name; LLC name) — blocked on first attempt.
- Bing search "Echols Grove Solar Texas": returned unrelated IMDb results — no hits.
- Bing search "Echols Grove Solar LLC": returned unrelated results — no hits.
- Bing search "Echols Grove Solar" + "Lamar County": returned Chinese DJI content — no hits.
- SEC EDGAR full-text search API: HTTP 403 on all attempts.
- TX SOS SOSDirect: requires paid session ($1/search), not automatable.
- T3 result: No developer name, no news, no LLC registration found. Project appears to have no public web presence.

## T4 start
- ERCOT Interchange (interchange.ercot.com): DNS not found.
- PUCT Interchange (interchange.puc.texas.gov/search/filings/, /Documents/ListDocumentsByParty.aspx, /Search.aspx): HTTP 402 on all attempts — portal blocked/requires auth session.
- puc.texas.gov/interchange/search.aspx: HTTP 402.
- puc.texas.gov/industry/electric/rates/Interconnection/InterconnectionAgreements.aspx: HTTP 402.
- T4 result: IA status UNKNOWN — portal inaccessible. Queue data shows iaSigned=2024-07-06; IA exists but content unverified. Deep scan should attempt direct portal access or alternate UA.

## T5 start
- TX Comptroller Ch.313 database (mycpa.cpa.state.tx.us/ch313/): 404. Program expired 2022; new projects use JETI.
- comptroller.texas.gov/economy/local/ch313/: navigation only, no searchable data.
- comptroller.texas.gov/economy/local/ch312-313/jeti/agreements.php: redirects to overview page, no data.
- comptroller.texas.gov/economy/development/search-tools/sb1340/search.php: dynamic JS search form, not fetchable via WebFetch.
- Project entered queue 2023-03, so Ch.313 ineligible. JETI is the applicable program but requires a paid/authenticated session or dynamic browser.
- T5 result: No abatement found. Normal for post-2022 project. JETI check deferred to deep scan.

## T6 start
- Site candidate: Blossom, TX area (Lamar County) inferred from POI name "Lamar Blossom Switch" — confidence LOW (name inference only, no parcel/pin/IA map).
- Estimated center: ~33.658°N, -95.395°W (Blossom TX).
- cdse.py 3×3 chip grid attempted: HTTP 401/403 on all 9 calls — ~/.config/gis-research.env contains example placeholder credentials only.
- T6 result: No imagery obtained. Construction status UNKNOWN.

## T7 start
- triage_findings.json written
- triage.md written
- Turns used: ~28. All steps completed. Tool blockers: gmaps 429, DDG CAPTCHA, Bing no hits, PUCT 402, CDSE 401 (placeholder creds), JETI dynamic JS.
- T7 complete.

## D1 — IA documents

- **D1-start**: triage had 0 signals; factsheet shows 1 verified IA + 2 docket-join-table items + 2 EIA-860M candidates
- `puct.py match 25INR0368` → 2 CONFIRMED PDFs:
  - `sources/2026-07-20_puct_35077-2030_standard-generation-interconnection-agreement-be.pdf` (original IA, PUCT 35077-2030, filed 2025-01-02)
  - `sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-generation-interc.pdf` (Amendment No. 1, PUCT 35077-2335, filed 2025-12-17)
- Original IA (p6): "5th day of December 2024, between Oncor Electric Delivery Company LLC and **BT Ferguson Solar LLC**" — SPV confirmed
- Amendment No. 1 (p3): Renames all references "BT Ferguson Solar, LLC" → "**Echols Grove, LLC**"; removes Echols Creek Storage (25INR0369); signed 2025-12-07 by Ignacio Fuentes, Vice President
- Exhibit B Time Schedule (original p29): In-Service **Dec 3, 2026** · Trial Op **Jan 3, 2027** · Scheduled COD **Apr 3, 2027** · NTP deadline Dec 6, 2024
- Amendment Exhibit B (p4): Identical milestone dates — COD **Apr 3, 2027 unchanged**; NTP deadline Dec 9, 2025
- Exhibit C (Amendment p7): POI = "Click Creek Switch" (new switch to be built) on Oncor 138kV Hawk Hollow – Lamar Blossom Sub – Tenaska Switch line, Lamar County; switch location REDACTED (CEII). Equipment: 64× SUNGROW SG3600UD-MV inverters, 201.15 MW net
- One-line diagram (original p43): Shows "Echols Creek Solar GINR 25INR0368 201.15 MW" + "Echols Creek Storage GINR 25INR0369 100.57 MW" — storage removed in Amendment
- Exhibit E (original p49): LC effective on or before Dec 6, 2024; amount page not fully read
- Amendment Exhibit E (p22): LC effective on or before **Dec 9, 2025** — amount page text cut off (no dollar amount visible)
- **EIA match**: factsheet spv candidate "BT Ferguson Solar, LLC" plant="Echols Creek Solar" 201.2MW @ 33.61647,-95.45837 planned=2027-12 — name, MW, county all agree; adopted as site candidate
- `ch313.py resolve` + JETI: no hits (post-2022 project, expected)

## D2 — Site identification

- Google Places pin "Echols Grove Solar": **3018 U.S. Hwy 271 S, Paris, TX 75462** @ 33.611368, -95.445060 — delivery pin at project gate on US-271 south of Paris, Lamar County
- EIA-860M plant 68902 "Echols Creek Solar" (BT Ferguson Solar LLC): @ 33.61647, -95.45837 — 1.3 km from Places pin; name/MW/county match
- Both converge on US Hwy 271 S corridor ~5 km south of Paris TX: site candidate **33.611-33.616°N, -95.445-95.458°W**, confidence HIGH (two independent sources)
- Map artifacts: sources/2026-07-20_puct_35077-2030_standard-generation-interconnecti_p43.png (one-line diagram with project name), sources/2026-07-20_puct_35077-2335_amendment-no-1-to-the-standard-ge_p7.png (Exhibit C POI description)
- Imagery: CDSE openEO returned 402 Payment Required on all chip attempts (2026-07-20) — no Sentinel-2 imagery obtained; CDSE token valid but no compute credits

## D3 — Gap fill / secondary sources

- LC security amounts confirmed from IA PDFs: $8,596,091 (original, Dec 2024) → $11,711,125 (Amendment No. 1, Dec 2025) — 36% escalation, shows active Oncor work commitment
- EIA-860M plant 68902: planned COD **2028-12** for 12 consecutive months (Jun 2025 → May 2026); status "(L) Regulatory approvals pending. Not under construction" throughout
- EIA COD vs queue COD divergence: queue says 2027-04, EIA says 2028-12 — **8-month gap**, consistent not-under-construction status
- eia_history.py written to eia_history.json
- search.py: all queries failed on all backends (developer, project name, LLC, signatory)
- Developer identity: unknown — "Ignacio Fuentes, Vice President" signed Amendment for Echols Grove LLC; no web presence found
- Ch313/JETI: 0 hits (expected for post-2022 project)
- Lamar CAD: not queried (no functional HTTP path available)

## D5 wrap-up

- queue_history.py: 40 snapshots, 5 COD changes — already in timeline.json/timeline.md
- eia_history.py --plant-id 68902 --write: wrote eia_history.json
- build_brief.py: running

## D6 — Imagery fix + provenance re-derivation (2026-07-21)

- **Provenance check**: prior `site.method` cited two PUCT pages as `map_artifacts` (p43, Amendment p7). Re-read both: p43 ("Attachment 1 to Exhibit C One Line Diagram — Click Creek Switch") is a one-line electrical diagram — project name/GINR/MW only, no geography. Amendment Exhibit C p7 ("Point of Interconnection location") has its actual location paragraph **CEII-REDACTED** in the filed PDF (black bar after "The Click Creek Switch will be located"). `exhibit.py scan` over both IA PDFs found no other map/plat/survey pages (only false-positive keyword hits on Docusign envelope-ID boilerplate, p14/p39). **Conclusion: neither the map-exhibit rung nor the IA-Exhibit-C-text rung is actually available for this project** — the true rung was already the bottom two (documented Places pin + EIA-860M plant point), so imagery verification (task step 3/4) is the correct next move, not optional.
- **Banned-domain re-check**: `grep -riE "infrasure|futuregrid|cleanview|interconnection\.fyi|gridinfo|ercotqueue"` across findings.json, dossier.md, log.md, triage.md, triage_findings.json, factsheet.json/md, brief.html, timeline.json/md, and `ls sources/` — **0 hits**. No cleanup needed.
- **Imagery**: cdse.py still down (per task brief — capacity outage), used s2aws.py only, as instructed.
  - First pass at the EIA anchor (33.61647,-95.45837, buffer 3.5km) landed on Cox Field (Paris Municipal Airport, the runway "X" visible near frame-top) plus open pasture — no construction visible in any of the 5 initial frames by eye. A pixel-diff (2024-07-01 vs 2026-07-15, brightness delta, connected-component analysis) found one large, coherent, non-seasonal bright blob in the SE quadrant of the frame — its bounding box touched the bottom (south) frame edge, i.e. **cut off**, per the task's re-fetch trigger.
  - Re-centered on the disturbance centroid (33.593,-95.440) with buffer widened to 4.5km and refetched all 5 key dates — now fully framed with margin on all sides. Deleted the cut-off first-pass chips (never committed; they only ever lived under the same imagery/key path and were overwritten, not left behind).
  - Added one bracketing frame (`s2_2025-10-15.png`, actual acquisition 2025-11-03, 0% cloud) to pin down first-activity timing between the clean 2025-07-01 frame and the already-disturbed 2026-01-15 frame; a 2025-09-01 probe (actual acquisition 2025-09-17) was cloud-obscured directly over the site and is not usable (kept only in /tmp scratch, not copied into imagery/key).
  - All 6 imagery/key PNGs magic-byte verified (`\x89PNG\r\n\x1a\n` header).
- **Construction read (chronological)**:
  - 2024-07-01, 2025-07-01: clean pasture/agricultural fields at the disturbance location, no roads, no clearing. A stable, unrelated circular field feature (irrigation pivot or similar) at the frame's NE corner is unchanged in all 5 frames — confirms consistent geo-registration across dates.
  - 2025-10-15 (acq. 2025-11-03): curving light-tan access-road/track network first visible across the future footprint — first activity.
  - 2026-01-15 (acq. 2026-02-04): same track network, consistent/slightly firmer (whole scene in winter-dormant brown tones).
  - 2026-04-15 (acq. 2026-03-26): tan cleared area now shows an orthogonal cross-road pattern plus a small orange bare-soil laydown/staging pad to the NW.
  - 2026-07-15 (acq. 2026-07-19): most developed frame — dense cross-shaped main haul roads + fishbone lateral access roads across a ~2km x 1.5km footprint, the classic pre-racking civil-grading signature for utility-scale solar. No PV panel rows visible yet.
  - Neighbor check (`data/eia_generator_tx.parquet`, county=='Lamar', latest reportDate 2026-05-01): nearest operating solar neighbors are Eiffel Solar (240MW, operating, 6.5km W of the EIA anchor) and Chisum (10MW, operating, 6.5km NE) — both outside the imaging buffer and both visibly unchanged across all 5 dates, ruling out neighbor-plant misattribution. Rowdy Creek Solar (24INR0186, the other Lamar County queue project) is 23km N — not a confusion risk at this zoom.
- **Verdict change**: `real_early`/`pre_construction` → **`real_active`/`under_construction_early`**. This directly contradicts the EIA-860M self-reported status ("(L) Regulatory approvals pending. Not under construction," carried through the May 2026 snapshot) — same staleness pattern already flagged for the EIA-vs-queue COD divergence.
- findings.json updated (site.method/confidence, construction block, verdict, real_project_verdict, notes). Re-running `build_brief.py` next.
