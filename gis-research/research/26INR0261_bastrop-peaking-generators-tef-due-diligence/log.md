# Triage Log — 26INR0261 Bastrop Peaking Generators (TEF-Due Diligence)

Triage date: 2026-07-18

## T1 start

**Result:** 27 snapshots (2024-04-01 → 2026-06-01). COD drifted twice: 2026-05-31 → 2027-03-31 → 2027-12-07 (current). MW grew from 476 → 1104 in Aug 2024. IA signed 2025-12-19. FIS requested 2024-03-15, not yet approved. No construction start reported. IA presence is meaningful signal.

## T2 start

**Result:** gmaps.py blocked — HTTP 429 on both attempts (rate-limited). No pins found. Normal miss for a new gas project without a public facility address.

## T3 start

**Result:** DDG blocked (CAPTCHA). Bing returned only generic Bastrop TX results for all 3 queries ("Bastrop Peaking Generators" + TEF, + ERCOT, + LLC). No developer name, news, or LLC registration surfaced. No sources saved.

## T4 start

**Result:** PUCT Interchange returning HTTP 402 on all 3 URL attempts (portal blocked). Bing site-search and docket keyword search also blocked (CAPTCHA). No IA PDF retrieved. Note: queue data shows `iaSigned = 2025-12-19` so an IA DOES exist in ERCOT records — it just could not be pulled from PUCT portal this pass. TEF docket not found.

## T5 start

**Result:** TX Comptroller Ch.313 and JETI pages returned generic overview pages (no application-level data accessible via URL params). Bing search for Bastrop + Ch.313/JETI + gas turbine returned only generic Bastrop county results. No abatement found. Normal for a 2026-vintage project — Ch.313 expired 2023, JETI is the successor but filings are sparse.

## T6 start

**Result:** SKIPPED — no site candidate. No pin (gmaps blocked), no abatement map, no IA PDF. POI "7048 L_GARFIE5_1Y 345kV" points to Garfield 345kV bus (Travis/Bastrop border area) but does not bound the plant site to better than county-wide. Imagery without a tighter center would waste budget on empty land. Deep scan should find the IA map or TCEQ permit address to anchor imagery.

## T7 start

**Result:** triage_findings.json + triage.md written. Turns used: ~22. STOP.

---

# Deep scan — 2026-07-18

## D1 PUCT filings

Case-style/FilingParty/Description searches for "Bastrop Peaking" all 0 hits.
Broad "Bastrop" 2024+ returned 16 dockets — all water/CCN, zero energy/interconnection.
"Bastrop" filings across docket 56896 (TEF In-ERCOT loan reports/filings): **1 hit** —
Item 83, 2025-10-08, filer **MPH Bastrop Peakers, LLC**, "Notice of Request for Extension
of Initial Disbursement Deadline". Saved as
[sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf).
Extension request pushes initial disbursement to **Dec 31, 2026**, citing "EPC availability,
supply chain issues, and electrical interconnect timing". CFO Craig Herlihy signed. Project APP-00000194.

## D2 TEF NOI (docket 56455)

Item 42, 2024-05-30 — **Hull Street Energy, LLC** (Bethesda, MD) filed the NOI as parent
of wholly-owned subsidiary **MPH Bastrop Peakers, LLC**. Saved as
[sources/2024-05-30_puct_56455-42_hull-street-tef-noi-app-194.pdf](sources/2024-05-30_puct_56455-42_hull-street-tef-noi-app-194.pdf).
**Decisive:** "1,080 MW peaking facility **at the existing Bastrop Energy Center site
in Cedar Creek, TX**." Signer: Mark Orman, Partner, Hull Street Energy.
Attorney: Randall Osteen. → project is a BROWNFIELD EXPANSION at an already-operating
gas plant. That resolves the "TEF-Due Diligence" name and the SPV mystery in one shot.
Note: NOI capacity 1,080 MW vs queue capacity 1,104 MW — a ~2% design uplift consistent
with detailed engineering, not a scope change.

## D3 Site pinpoint

OSM Nominatim direct hit: `Bastrop Energy Center` industrial landuse polygon (osm way
462642757), center 30.14555, -97.54879 — 490m N-S × 616m E-W ≈ **74 acres**.
Saved as [sources/2026-07-18_osm_bastrop-energy-center.json](sources/2026-07-18_osm_bastrop-energy-center.json).
Distance to POI "L_GARFIE" (Austin Energy Garfield 345kV, ~30.207,-97.633): **~10.6 km** —
consistent with a tap line from a switchyard 10 km NW.

## D4 TCEQ Central Registry — air permits at Bastrop Energy Center

RN101056851 = Bastrop Energy Center + MPH Facility co-listed at address
**125 OLD BASTROP RD, CEDAR CREEK** ([search results](sources/2026-07-18_tceq_re-search-bastrop-energy-center.html)).
Customers: Bastrop Energy Partners LP (Owner/Operator, CN600615470), Direct Energy Resources,
**MPH BASTROP PEAKERS LLC (OPERATOR since 12/13/2024, CN606334142)** — MPH mailing address
matches Hull Street's Bethesda MD suite (4747→4757 Bethesda Ave Ste 1220; 4757 is TCEQ's).
Active air program permits at this RN include NSR permit **178585** (page:
[sources/2026-07-18_tceq_air-permit-178585-mph-facility.html](sources/2026-07-18_tceq_air-permit-178585-mph-facility.html)),
described as "Air New Source Permit 178585 · For: MPH FACILITY (RN101056851) · Permit
Status: ACTIVE · Held by: MPH BASTROP PEAKERS LLC (CN606334142) · OPERATOR Since 12/13/2024".
Full list of active air permits at this RE: 41941 (existing), 178585 (MPH), 113103, 164269,
164270 (registrations), plus PSDTX948, PSDTX1658, GHGPSDTX247 (federal PSDs) and Title V
operating permit 2109. Mandatory-permit gap CLOSED: MPH has an active NSR permit.

## D5 Imagery (Sentinel-2 6 km xwide, 2026-07-01 ±15d)

Wide frame [s2_2026-07.png](imagery/s2_2026-07.png): center of frame shows a large bright
tan **graded pad** (~800m wide) immediately north/east of the existing plant complex,
consistent with clearing/grading for the peaker addition. Center crop
[s2_2026-07_center_crop.png](imagery/s2_2026-07_center_crop.png) (~3 km) confirms:
existing plant compact industrial buildings visible mid-frame; a very large bright tan
rectangular graded area sits just north — this is the new-plant footprint under
preparation. No turbine hall / cooling structure / crane pad visible yet on the new area.
Additional CDSE calls returned HTTP 401/403 (token rate-limit lockout on the CDSE OpenEO
password grant); cannot bracket first-activity month or run present dekad cadence this pass.
Judgment: **clearing/early-grading** stage as of 2026-07.

## D6 CAD parcel search

Bastrop CAD esearch (https://esearch.bastropcad.org) queries for "MPH Bastrop", "Bastrop
Energy Partners", "125 Old Bastrop" returned pages but data is JS-rendered off an internal
XHR — no parcel rows scraped. Not chasing further; TCEQ+OSM already fix the site.

## D7 Baseline chip 2024-01

Pulled Sentinel-2 xwide chip centered at 30.14555, -97.54879 for 2024-01-15 ±30d
([imagery/s2_2024-01.png](imagery/s2_2024-01.png)). Existing Bastrop Energy Center
industrial buildings visible mid-frame; the area immediately north/east where the
2026-07 bright graded pad appears is undisturbed farmland/pasture in 2024-01. Confirms
the graded pad is a NEW feature between 2024-01 and 2026-07 (i.e. first activity fell
somewhere in that 30-month window; couldn't tighten further this pass — timelapse job
retried under the same CDSE OAuth token and produced no output).

## D8 Static site map

`gmaps.py staticmap` returned HTTP 403 ("Maps Static API is not activated on this
key"). Skipping; dossier uses OSM industrial-landuse polygon + Sentinel-2 frames for
site depiction.

## Stage 5 synthesis 2026-07-18

Wrote dossier.md + findings.json. Ran queue_history.py (regenerated timeline),
build_brief.py, build_index.py. Verdict: **real_early** — signed IA, active NSR air
permit, TEF loan agreement with disbursement extension, and freshly graded pad at the
existing brownfield site. COD claim 2027-12-07 not achievable — 13 months from
early-grading to full 1104 MW commercial ops is well short of the 24-36 months a
greenfield-scale peaker expansion needs. Independent estimate: 2029-Q1, drift risk
high.
