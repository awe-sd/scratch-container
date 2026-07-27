# Triage log — 23INR0231 Hoke Solar

**Project:** Hoke Solar | **INR:** 23INR0231 | **County:** Gonzales, TX | **Capacity:** 95.29 MW Solar PV
**POI:** tap 138kV 7595 Deer Creek – 7621 Nixon | **CDR zone:** SOUTH | **Claimed COD:** 2027-05-08

---

T1 start
**Result:** 63 snapshots. 8 COD slips (2023-07-01 → 2027-05-08, ~4 yr total drift). IA signed 2022-04-25. Meets 6.9(1) 2025-09-08. No construction start/end, energization, sync, or COA milestones. Capacity stable 95 MW, bumped to 95.29 in 2024-08. FIS never approved (unusual — IA signed without it).

T2 start
**Result:** gmaps.py → 429 Too Many Requests on both attempts (budget exhausted). No pins found. 0 delivery pins.

T3 start
**Result:** Developer = Nexus Renewable Power, LLC. EPC = AUI Partners (auipartners.com/hoke/ confirmed contract). Expanded scope: 123 MWdc + 132 MWh BESS. AUI page says "completion 2026". Cole Schotz (law firm) Facebook post: EPC agreement signed, "construction in the coming weeks." LLC name "Hoke Solar, LLC" not confirmed — developer entity is Nexus. DDG blocked 3/5 searches with CAPTCHA. Saved to sources/T3_web_sweep.md. news_found=true.

T4 start
**Result:** PUCT Interchange returning HTTP 402 on all attempts (blocked portal, budget exhausted). IA search not completed. ia_found=false (portal blocked, not confirmed absent).

T5 start
**Result:** Ch.313 not applicable — program expired 2022, IA signed 2022-04-25 (post-cutoff). JETI registry not directly accessible via WebFetch (Comptroller site portal-style, no simple list URL). No abatement/JETI hit found in budget. abatement_found=false (normal for this vintage).

T6 start
**Site candidate:** Nixon TX (29.27, -97.77) — POI is "tap 138kV 7595 Deer Creek – 7621 Nixon"; Nixon is the named substation. Confidence: medium (infrastructure-based, no pin).
**Imagery attempt:** CDSE token endpoint returning HTTP 401 Unauthorized on all 9 chip attempts (grid) + 1 retry. Auth credentials not loaded from ~/.config/gis-research.env. Blocked portal — budget exhausted. construction_visible=unknown.

T7 start
**Result:** triage_findings.json + triage.md written. Turns used: 22. Run complete.
deep_scan_recommended=true. Key blockers this run: gmaps 429, PUCT 402, CDSE 401.

---
## DEEP SCAN — 2026-07-20

D1: PUCT IA — `puct.py match 23INR0231` rung-0 INR-join hit, CONFIRMED (INR text match):
  35077-1562, LCRA TSC ↔ Generator, signed doc saved sources/2026-07-20_puct_35077-1562_ercot-standard-generation-interconnection-agreem.pdf (63pp). Note: this is the pre-name-change filing description ("LCRA...Generator") — party name inside PDF still TBD-check.

D1: ch313.py resolve → 1 candidate, Ch.313 #1618 "Hoke Solar Project, LLC f/k/a Brush Country Solar Project, LLC", Nixon-Smiley CISD, applied 2021-06-30.
  DECISIVE — confirms SPV legal name AND developer: application filed by **Enel Green Power North America, Inc.** (confidentiality letter, sources/..._app_p30.png, signed by Robert Pena Jr., Development, dated 2021-06-14, on Enel Green Power letterhead, 100 Brickstone Square Andover MA).
  Downloaded: -app.pdf (main application), -appsupp1.pdf, -agmt.pdf (signed agreement w/ Nixon-Smiley CISD, has image-only Exhibit A/B legal description + survey map pp79-88).
  Tab 7/8 (app pp22,24): scope = 100 MWac solar + 30 MWac (permanent) battery storage; ~1,300 acres under lease/easement in Gonzales County within Nixon-Smiley CISD. NOTE: 30 MWac battery in ch313 app vs triage's "132 MWh BESS" AUI page figure — different vintage/metric (MWac power vs MWh energy), not necessarily contradictory.
  Tab 8 confirms POI: "Brush Country Solar anticipates interconnecting to the existing LCRA 138-kV Nixon to Deer Creek Transmission line" — MATCHES queue POI "tap 138kV 7595 Deer Creek - 7621 Nixon" exactly. TSP = LCRA (matches IA party LCRA TSC).
  Vicinity map (app p29, "Brush Country Solar - Vicinity Map"): project boundary+reinvestment zone (orange box) plotted NW of Nixon, TX, straddling FM 80, just south of the Gonzales/Guadalupe county line, near "Leesville" label. Reinvestment Zone Within Vicinity (app p37) confirms same box, ~2-3 mi south of the Gonzales/Guadalupe line, near Gonzales CR 104 / FM 1681 area (map has no gridlines/scale ticks for a precise pin — used for orientation only, will cross-check with gmaps/OSM in D2).

D1 continued: PUCT amendment search — `puct.py match --key "Brush Country"` surfaced 3 filings total (35077-1562 original IA, -1640 First Amendment, -2357 Second Amendment). Both amendments UNCONFIRMED by tool (INR not in text — amendments only restate Exhibit B/E, no INR) but manually verified: signer emails stephen.pike@enel.com / James.Matlock@LCRA.ORG on Second Amendment (Adobe Sign audit trail), and both cover pages explicitly reference "Brush Country Solar Project, LLC" + Agreement dated 2022-04-25 matching the confirmed original IA — treating as CONFIRMED by chain-of-custody.
  First Amendment (signed 2023-06-08, effective per audit trail): COD pushed 2024-11-01 -> 2024-12-31; security raised $10.8M -> $13.5M (total, +$7.3M construction tranche replacing the +$4.6M in the original).
  Second Amendment (signed 2024-12-16): COD pushed again 2024-12-31 -> **2026-08-14**; Exhibit B only (no new security table, so $13.5M carries).
  GAP: queue's current claimed COD 2027-05-08 is ~9 months AFTER the last signed contractual COD (2026-08-14, Dec-2024 amendment) with no Third Amendment on file at PUCT as of search — the 2027-05-08 figure is a queue self-report not yet backed by a re-executed IA. This is the single most decisive COD-drift fact.
  Adobe Sign metadata on both amendments: internal doc name "Rocinante Solar BESS Brush_Country_SGIA" — confirms "Rocinante" = Enel's internal codename for this co-located solar+BESS pair (23INR0231/23INR0232).

D2: gmaps.py places — retried 2x (Leesville Substation variants) still HTTP 429 (quota-exhausted, not a transient fleet throttle — same failure since triage). NEGATIVE EVIDENCE, moving to alternate geocoding (Wikipedia/OSM for Leesville TX place coords, then visual cross-check against IA Exhibit C3 + ch313 vicinity map).

D2: Site pixel-geolocation — gmaps.py fully blocked (429 quota exhausted across triage+deep). Derived coordinates via manual pixel-scale conversion of the ch313 Vicinity Map (app p29, Enel-authored, scale 1:150,000 w/ printed mile scale bar): measured scale-bar tick spacing (~71.7 px/mile), located orange project-boundary-box centroid pixel (1700.5, 2177.5 in the 6120x4080 PNG) via color-threshold detection, and the 'Leesville' label pixel (~1727,2393) as an anchor cross-checked against OSM Nominatim Leesville TX centroid (29.4069,-97.7450). Result: project boundary box center ≈ **29.45N, -97.775W** (~3.1 mi N, ~1.8 mi W of Leesville).
  Cross-check: OSM Overpass power-line query confirms an LCRA 138kV line (way 15250175) running NNE through this exact area, with vertices at 29.4217,-97.7405 / 29.4315,-97.7391 — within ~2 mi of the derived box, consistent with the IA's POI description (Leesville Substation tapping this same 138kV line near FM 102) sitting just SE of the generation site. Two independent developer-authored maps (vicinity map p29 + reinvestment-zone-within-vicinity map p37) show the same box position.
  CONFIDENCE: medium — pixel-scale derivation from a developer map has no ground-truth pin/parcel corroboration (gmaps blocked, no CAD lookup yet); calling this a map-derivation fix per playbook rule 4 (not a county centroid — derived from the project's own boundary map + scale bar).

---
## DEEP SCAN RESUMED / COMPLETED — 2026-07-21

Prior run died mid-derivation (findings.json had verdict=null, site=null). Resumed from
disk artifacts; deleted the dead run's `imagery/` (search-grid junk from a wrong center).

**Site derivation, finished.** Re-derived from scratch with a cleaner method (full chain
in `sources/SITE_DERIVATION.md`). Identified which ch313 map is which: app p29 (Vicinity
Map, 1:150,000) and p37 (Reinvestment Zone Within Vicinity, 1:90,000) both legend the SAME
orange box as "Project Boundary and Proposed Reinvestment Zone" — Enel's own filing does
not distinguish a tighter array footprint from the reinvestment zone; agmt Exhibit B (p83)
confirms this (same box, portrait rotation, no tighter survey plat). Exhibit A (agmt p82)
turned up a bonus fact not used for geocoding: the underlying ranch tract is owned by QSTS
RANCH PARTNERSHIP LTD, Parcel ID 1715, "34 J De La Baume Quein Sabe Ranch," 4,185.19 ac
(real TX LP per OpenCorporates, San Antonio). Tried to convert this into an independent
parcel-centroid via gonzalescad.org and Regrid; both gate GIS/search behind JS/login that
WebFetch can't execute — logged as a negative, not pursued further.

Georeferencing: box pixel centroid found via color-threshold connected-component
detection (deterministic, not eyeballed): p37 (2166,1068)px of 6120x4080. Scale computed
from paper math (170dpi render x 1:90,000 printed scale = 119.68 px/mile), not read off
the printed ticks by eye — cross-checked against the visually-read tick spacing and it
matched. Anchored to Leesville, TX, independently re-confirmed via OSM Overpass (node
151462694, 29.4069038,-97.7449990 — matches the prior run's Nominatim value to 5 decimals).
Result: 29.4526,-97.7497. Fully independent second derivation on p29 (different scale
71.8px/mi, different anchor — Nixon TX via Overpass node 151811162) gave 29.4531,-97.7552.
The two agree to ~100ft on latitude, ~0.3mi on longitude — adopted their average
(29.453,-97.751) as the map-only estimate, medium confidence. Overpass 504'd twice on
heavier queries (county-boundary relation; Gonzales-area substation search) — each was
retried once after a 10s wait per convention; the boundary query still failed (treated as
a miss, not pursued further since it was only a nice-to-have cross-check), the substation
query succeeded on retry and confirmed no OSM node exists for the LCRA Leesville
Substation (only Nixon Substation, Nash Creek Substation, and an unrelated SunHub solar
plant ~9mi N — none of which is this project).

**Imagery.** `s2aws.py chips --lat 29.453 --lon -97.751 --buffer-km 3.5` for
2024-07-01/2025-07-01/2026-01-15/2026-04-15/2026-07-15 — all 5 scenes came back clean on
the first try (0-4.3% cloud), no re-fetches needed. Read every frame:
- 2024-07 (acq. 2024-07-02) and 2025-07 (acq. 2025-07-16): clean ranchland/brush baseline,
  no disturbance anywhere near the derived site.
- 2026-01 (acq. 2026-02-04): a large bare/graded rectangular footprint has appeared,
  sitting almost exactly at the chip's center — first direct visual confirmation the
  map-derived point was correct.
- 2026-04 (acq. 2026-05-03): the same footprint now shows a regular parallel row-banding
  pattern (racking/foundation corridors) across most of its area, plus small staging pads.
- 2026-07 (acq. 2026-07-09, some cloud/shadow at the frame edges but the site itself is
  clear): footprint has grown further, additional white structures near the access road
  (likely inverter/BESS skid pads), row-banding still visible across the bulk of it. At
  10m Sentinel-2 resolution individual panels can't be resolved, so calling this
  "actively constructing" (graded + racking rows + pads), not confirmed panel install.
- Measured the array footprint's own pixel bbox directly off the clearest (2026-07) frame
  (~x:280-460, y:205-390 of the 700x700px/10m-per-px chip) and converted its centroid to
  lat/lon: **29.4577,-97.7489** — within ~0.5km of the map-only estimate, confirming the
  derivation and superseding it with a HIGH-confidence, imagery-measured point.
- Checked `data/eia_generator_tx.parquet` (latest reportDate 2026-05-01) for Gonzales
  County solar before attributing the array: only two small out-of-service Guadalupe-
  Blanco-River-Authority hydro units exist in-county — zero solar — so there's no risk of
  misattributing a neighboring EIA-tracked plant's construction to this site.

**Wrap-up tools run:** `eia_history.py 23INR0231 --write` → still NOT_IN_EIA (negative,
matches factsheet, expected — no eia_history.json written since the tool only writes on a
resolved match). `ch312.py resolve 23INR0231` (+ name variants) → negative (weak; Ch.312
CAD-submitted annual cycle, doesn't rule out an abatement, but Ch.313 already gives a much
stronger confirmed incentive signal for this project). `queue_history.py` timeline was
already on disk from the dead run (63 monthly snapshots, 8 COD slips) — reused, not rerun.

**Verdict: real_active.** Signed IA (2022) + two amendments with escalating financial
security ($6.2M -> $10.8M -> $13.5M) + an EXECUTED (not just applied-for) Ch.313 agreement
with Nixon-Smiley CISD, predating the program's 2022 sunset + an EPC contract with AUI
Partners (triage T3 web sweep) + now directly confirmed by imagery: real graded
construction with racking rows advancing from bare ground (mid-2025) to a large
part-built footprint (mid-2026) at the exact derived location. cod_assessment: the
Second Amendment's own in-service date (2026-04-16) has already passed with the site
still mid-construction and no Third Amendment on file — the contract's own schedule has
already slipped once — so the queue's un-contracted 2027-05-08 self-report is judged the
more credible near-term estimate (independent call: Q1-Q2 2027), drift_risk moderate.

**Remaining gaps:** no ground-truth GPS pin (gmaps.py still 429-blocked) or CAD parcel
centroid (Gonzales CAD/Regrid GIS both JS/login-gated); imagery can't confirm whether
panels are physically mounted yet vs. racking-only at 10m resolution; no Third Amendment
found at PUCT as of this run to formalize a post-2026-08-14 COD.

## 2026-07-21 (orchestrator) — footprint ownership cross-check vs Cachena Solar SLF
The construction footprint at 29.4577,-97.7489 was ALSO claimed by Cachena Solar SLF
(23INR0027) in its 2026-07-20 re-check (site 29.456,-97.750, ~220m away). Resolved in
Hoke's favor on three deterministic checks: FCC census county = Gonzales (Hoke's queue
county; Cachena is Wilson); only line within 2km on OSM is 138kV (Hoke POI = tap 138kV
Deer Creek-Nixon; Cachena = tap 345kV Elm Creek-Old Hickory); footprint ~550 ac fits
95.29MW, not 602MW. Cachena's site/construction attribution is being retracted and
re-derived in its own dir. Hoke verdict unchanged: real_active.
