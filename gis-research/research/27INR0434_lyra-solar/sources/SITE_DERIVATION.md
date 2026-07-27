# Site derivation — Lyra Solar (27INR0434)

Second-pass review, 2026-07-21. Supersedes the 2026-07-19 deep-scan site
(`32.7222, -101.6385`, "OSM Overpass companion BESS" inference, confidence medium),
which pointed at the **existing** Long Draw/Borden County BESS complex, **not** Lyra's
array. This review pulled the Lyra CCN docket (PUCT 59183) and derived the anchor from
the project's own location map.

## Provenance chain (best rung first)

1. **MAP EXHIBIT — CCN 59183 EA Appendix A, Figure 1-1 (Project Location Map) + Figure 2-1
   (Property Owners, on aerial).** WETT's application to amend its CCN for the "Muleshoe to
   Lyra Solar and Lyra BESS 345 kV Transmission Lines" (filed 2026-01-07). Figure 1-1/2-1
   show the **Proposed Lyra Solar and Lyra BESS Collector Stations just NORTH of US-180,
   ~7 mi west of Gail, on the "Juno DC, LLC" parcel.** The WETT Muleshoe Switching Station
   (the POI, #59922) is ~8 mi SOUTH; the collector station (= the generation site) is a
   distinct location connected to it by the new ~8-mi 345 kV line.
   - Artifacts: `2026-07-21_puct_59183-2_ccn-figure1-1_project-location-map.png`,
     `2026-07-21_puct_59183-2_ccn-figure2-1_property-owners-aerial.png`
   - EA §3.6.1: "PSA is located within rural land west of the city of Gail… ranches and
     other private properties." Landowners at/near the collector: **Juno DC, LLC**, Coleman
     Ranches Ltd, R M Livestock LTD, Muleshoe Ranch Ltd, Moorfaith Holdings LLC, AMNWC Real
     Estate/Clayton/Gregory/Wilson, Kent Youngblood Trust, Ophelia Blackard.
2. **IA text — PUCT 35077-2185** (`…lyra-solar-IA.pdf`, was `unverified_…2185…`, now
   verified: parties WETT + SE DC DevCo LLC, project "Lyra Solar Project", Borden County,
   Sungrow SG4400UD-MV-US inverters, POI "Muleshoe 345kV switching station… adjacent to the
   Generator's station fence"). POI ≈ switching station, not the array.
3. **Imagery** (verifies): collector site bare in 2024/2025; new graded ground appears 2026.

**Adopted anchor: `32.770, -101.555`** (Lyra/Lyra-BESS Collector Stations, N of US-180).
Method = `ccn_59183_figure_1-1_2-1_map`. Confidence **medium-high** (map-derived; eyeball
georeference against Gail 32.769,-101.443 and Long Draw Switching Station 32.721,-101.633,
±~1 km). This is a point on the collector-station complex; the panel footprint will spread
S/E across the ranch parcels within the CCN study area.

## Filing docs retrieved this pass
- **IA 35077-2185** (verified). Exhibit B schedule: In-Service 2027-05-15, Trial Op
  2027-06-15, **Scheduled COD 2027-11-15** (note: queue `projectCod` = 2027-09-15 — a
  ~2-month discrepancy; the IA date is the contractual one). Security (Attachment 1 to
  Exhibit B): **$18,000,000** due at execution (no later than 2025-07-16) for initial
  engineering/CCN prep/long-lead procurement/ROW; Limited NTP at CCN filing/award
  (2026-01-15 milestone); Full NTP TBD on Facility Study results.
- **CCN 59183** (docket live, pulled 2026-07-21): item -2 application + 310-pp EA
  (`…59183-2_filing.pdf` = pp 1-100 text; high-res figure appendix pp 101-300 pruned after
  rendering Fig 1-1/2-1 — re-fetch via `puct.py fetch 59183 2`); item -24 Kenda Pollio
  routing testimony (`…59183-24_filing.pdf`). Status: SOAH **paper hearing** (Order No. 5,
  2026-03-19); CCN not yet granted.

## Tax incentives
- **Ch.313 / JETI: NEGATIVE** (structural — Lyra entered the queue in 2025, after the
  Ch.313 sunset of Dec 2022; JETI table has no match for Lyra Solar / SE DC DevCo / SB Energy).
- **Ch.312: no abatement attributable to Lyra.** Four active Borden County Ch.312 reinvestment
  zones exist but all belong to **other/existing** projects — none names Lyra/Antila/SE DC
  DevCo, and none links a harvested PDF (all `pdf=None`, so no abatement map to render):

| Ch.312 # | Zone | Owner | Submitted | Expires | Relates to |
|---|---|---|---|---|---|
| 000003676 | BNB Oxbow Solar Reinvestment Zone | Oxbow Ranch | 2023-12-15 | 2028-04-22 | early "BNB" solar zone — NOT the SB Energy trio |
| 000004302 | Borden County BNB Long Draw Solar | Youngblood/Coleman/Miller Ranch | 2023-12-15 | 2030-12-31 | existing ENGIE Long Draw Solar |
| 000004303 | Borden County IP Juno Reinvestment Zone | Coleman Ranch | 2023-12-15 | 2030-12-31 | existing Intersect Power Juno Solar |
| 000015389 | Dairy Bank | Borden County Battery Storage System LLC | 2025-07-24 | 2034-12-31 | existing Borden County BESS |

  (A Ch.312 miss is only *weak* negative evidence — CAD-submitted annually with gaps; the SB
  Energy projects could file a zone later.)
- **EIA-860M: NOT present** (negative; normal for a pre-construction project; operating-
  neighbor guard held — no false match to ENGIE/IP Juno).

---
# Borden County generation cluster — attribution table
*(ERCOT queue fileDate 2026-06-01; EIA-860M reportDate 2026-05-01. This table is identical
in the Antila `SITE_DERIVATION.md`. Do not attribute existing arrays to the new projects.)*

## THE "JUNO" NAME TRAP (root of the prior conflation)
Three distinct developers operate in this county. The name "Juno" spans two of them:
- **Intersect Power** owns the **existing** "Juno Solar Project" (op 2021).
- **SB Energy** codenames its **new** projects "Juno Solar 3" (= Juno 3 Solar) and "Juno
  Solar 4" (= Lyra Solar).
The 2026-07-19 Lyra deep scan conflated these — it read the existing ENGIE/Intersect arrays
as evidence and inferred **ENGIE** as Lyra's parent. **Corrected here: Lyra's IA
(35077-2185) names SE DC DevCo, LLC = SB Energy.**

## Existing / operating plants — NEVER attribute to Lyra / Antila / Juno 3
| Plant | Entity (parent) | Fuel | MW | EIA | Status | Lat, Lon |
|---|---|---|---|---|---|---|
| ENGIE Long Draw Solar | GDF Suez North America (**ENGIE**) | Solar | 225 | 62845 | Operating 2020 | 32.7414, -101.6218 |
| Juno Solar Project | IP Juno, LLC (**Intersect Power**) | Solar | 305.6 | 63328 | Operating 2021 | 32.7729, -101.3910 |
| Borden County BESS | Borden County Battery Energy Storage System LLC | Battery | 150 | 66804 | Operating 2024 | 32.7223, -101.6385 |
| Stephens Ranch Wind | Stephens Ranch Wind Energy LLC | Wind | 376 | 57983 | Operating 2014-15 | 32.9264, -101.6478 |
| Bull Creek / Post / Gopher Creek Wind | various | Wind | 84-180 | 56956/56457/61417 | Operating | ~32.88-32.93 (N county) |

## New SB Energy campaign (SE DC DevCo, LLC; TSP = WETT) — all PRE-CONSTRUCTION
| Project | INR | Queue facility name | Fuel | MW | POI | IA (PUCT 35077) | CCN | COD queue / IA |
|---|---|---|---|---|---|---|---|---|
| Juno 3 Solar | 26INR0621 | Juno Solar 3 | Solar | 500 | Buck Canyon #59916 | -2184 (2025-07-07) | 59199 | 2027-11-30 / — |
| **Lyra Solar** | **27INR0434** | Juno Solar 4 | Solar | 500 | Muleshoe #59922 | **-2185** (2025-07-07) | **59183** | 2027-09-15 / 2027-11-15 |
| Lyra Storage (BESS) | 26INR0636 | JUNO BESS I | Battery | 500 | Muleshoe #59922 | -2225 (2025-08-18) | 59183 | 2026-11-12 / — |
| Antila Solar | 27INR0500 | Antila Solar LLC | Solar | 500 | Buck Canyon #59916 | -2227 (2025-08-18) | 59199 | 2027-11-30 / 2027-11-15 |

Campaign structure (one filing campaign, paired lead+contingent IAs):
- **Muleshoe pair** (POI #59922, CCN 59183): Lyra Solar = lead IA ($18M initial security) +
  Lyra Storage (JUNO BESS I).
- **Buck Canyon pair** (POI #59916, CCN 59199): Juno 3 Solar = lead IA + Antila Solar
  ($100k, "contingent on the Juno Solar 3 Agreement").
- **Collector stations for all four are co-located just N of US-180, W of Gail
  (~32.77, -101.556)** — per CCN 59183 Fig 1-1/2-1 (Lyra/BESS) and CCN 59199 Fig 1-1
  (Juno 3/Antila). Lyra's site == Antila's site == Juno 3's site to within georeference slack (~1-2 km).

## Other queued Borden projects (context; not SB Energy, coords not in queue)
Draco Solar (27INR0499, 500 MW, taps Long Draw–Faraday/Galvani), Uva Creek Solar
(26INR0359, 302 MW, Grape Creek Solar LLC / EIA "Red River Clean Energy" 68739 @
32.6798,-101.5044), Gail Mountain Solar (28INR0176, 244 MW, EIA 69506 @ 32.7146,-101.5274),
Caesar Solar+Storage (29INR0131/0132, Buck Canyon), Tumbleweed Solar+Storage (27INR0086/87,
Hecate, Faraday, INACTIVE), Magnet Solar+Storage (28INR0297/98, HyFuels, Faraday), Borden
Dino Solar+BESS (27INR0480/81, Faraday), Enfinity Post Oak/White Oak (EG White Oak LLC),
Iron Belt storage (EIA 67059 @ 32.5557,-101.6601, planned).

## Imagery attribution (this project's chips: `imagery/key/`, 8 dates)
5.0 km buffer around 32.770,-101.555 (S2 tile 14SKB). Every visible array is attributed:
- **West edge (~-101.60/-101.61):** dark panel-row block = **existing operating solar
  (ENGIE Long Draw, EIA 62845, op 2020, and/or adjacent existing sites)** — unchanged across
  all frames, NOT Lyra.
- **Frame center, N of US-180 (= the collector-station complex), time series:**
  2024-07-18, 2025-07-20 (cloud 0.0%), 2025-11-02, 2026-02-03 = **bare rangeland / fallow
  field, no disturbance**; **2026-03-29** = cleared/plowed rectangle emerging; **2026-05-31**
  (cloud 0.0%) = bright graded pad established, expanding; **2026-07-03 / 2026-07-20** = ~1 km
  bright graded/cleared area. Monotonic growth (Mar→May→Jul, same location, hard geometric
  edges) rules out a seasonal field → **collector-complex site clearing/grading, onset ~Q2
  2026**, ahead of the CCN transmission TIF window (Aug 2026–Apr 2027).
- **CALIBRATION:** the bright feature reads as bare/graded **soil or gravel pad** — **no PV
  panels are yet visible** (panels read *dark*, like the existing block at the W edge). The
  pad is as consistent with the WETT collector-station/switchyard footprint as with generator
  solar site prep; and it cannot be separated from the co-located Juno 3/Antila collector work
  at Sentinel-2 resolution.
- 2024-07-18 & 2026-02-03 chips are swath-edge clipped (SE, S2A orbit) but west + center are
  clean; the clean 2025-07-20 chip is the pre-construction reference frame.
