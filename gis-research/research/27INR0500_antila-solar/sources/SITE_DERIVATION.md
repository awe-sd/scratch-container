# Site derivation — Antila Solar (27INR0500)

Second-pass review, 2026-07-21. **Corrects the prior site anchor.** The 2026-07-20 deep
scan used `32.7672, -101.6508` (method `ccn_map_and_places_pin`), but that longitude came
from a Google Places pin that geocoded to "O'Donnell TX" and lands ~8.6 km too far WEST —
at the Buck Canyon / Long Draw switching-station area, **not** the solar collector/array.
Deriving the anchor from the CCN 59199 location map instead moves it ~8.6 km east.

## Provenance chain (best rung first)

1. **MAP EXHIBIT — CCN 59199 EA Appendix A, Figure 1-1 (Project Location Map).** WETT's
   application to amend its CCN for the "Buck Canyon to Juno Solar 3 and Antila Solar 345 kV
   Transmission Lines" (filed 2026-01-29). Shows the **Proposed Juno Solar 3 and Antila Solar
   Collector Stations just NORTH of US-180, ~7 mi west of Gail** — the same location as the
   Lyra collector stations (co-located SB Energy complex). Buck Canyon Station (WETT, the POI
   #59916) and Long Draw Switching Station are ~8 mi SW.
   - Artifacts: `2026-07-20_puct_59199-2_ccn-figure1-1_project-location-map_hires.png`
     (re-rendered high-res this pass), `2026-07-20_puct_59199-ccn-figure1-1_project-location-map.png`
     (prior low-res).
   - Cross-reference: the **Lyra CCN 59183 Figure 2-1 (property owners on aerial)**
     (`research/27INR0434_lyra-solar/sources/2026-07-21_puct_59183-2_ccn-figure2-1_property-owners-aerial.png`)
     covers this exact ground and shows the collector complex on the "Juno DC, LLC" parcel.
2. **IA text — PUCT 35077-2227** (`…antila-solar-IA.pdf`, already verified 2026-07-20:
   WETT + SE DC DevCo LLC, "Antila Solar Project", Buck Canyon 345 kV POI, 200× Sungrow
   SG3600UD-MV inverters; schedule "contingent on the Juno Solar 3 Agreement").
3. **Imagery** (verifies): collector site bare in 2024/2025; new graded ground appears 2026.

**Adopted anchor: `32.772, -101.559`** (Juno 3 / Antila Collector Stations, N of US-180).
Method = `ccn_59199_figure_1-1_map`. Confidence **medium-high** (map-derived; eyeball
georeference against Gail 32.769,-101.443 and Long Draw 32.721,-101.633, ±~1 km). Anchor is
within georeference slack (~1-2 km) of Lyra's (32.770,-101.555) and of Juno 3's — the three new solar arrays share
one collector-station area.

## Filing docs (verified)
- **IA 35077-2227** (verified). Exhibit B: Trial Op 2027-06-15, **Scheduled COD 2027-11-15**
  (queue `projectCod` = 2027-11-30). Interconnection option 4.1.A/B: full NTP + **$100,000**
  security within 10 business days of TSP execution; expressly **contingent on the Juno
  Solar 3 Agreement** (35077-2184, same parties, same day) — Juno 3 carries the pair's lead
  security, Antila rides on it.
- **CCN 59199** (on disk from prior pass): WETT application + EA + Kenda Pollio testimony.
  TIF construction window Aug 2026–Apr 2027, energize May 2027. SOAH contested case active
  April 2026; CCN not yet granted. (87 MB image-only figure appendix pruned after rendering
  Fig 1-1; re-fetch via `puct.py fetch 59199 2`.)
- Sibling-IA primary sources also on disk (unverified_35077-2184 = Juno Solar 3, -2185 = Lyra
  Solar, -2225 = Lyra BESS) — proof the whole campaign is SE DC DevCo / SB Energy.

## Tax incentives
- **Ch.313 / JETI: NEGATIVE** (structural — 2025 queue entry, post Ch.313 Dec-2022 sunset;
  no JETI match for Antila / SE DC DevCo / SB Energy).
- **Ch.312: no abatement attributable to Antila.** Same four Borden County zones as in the
  cluster table below — all belong to other/existing projects, none names Antila/SE DC DevCo,
  none links a harvested PDF (`pdf=None`). Weak negative (CAD-submitted annually).
- **EIA-860M: NOT present** (negative; normal pre-construction; operating-neighbor guard held).

---
# Borden County generation cluster — attribution table
*(ERCOT queue fileDate 2026-06-01; EIA-860M reportDate 2026-05-01. Identical to the Lyra
`SITE_DERIVATION.md`. Do not attribute existing arrays to the new projects.)*

## THE "JUNO" NAME TRAP
Three distinct developers; the name "Juno" spans two:
- **Intersect Power** owns the **existing** "Juno Solar Project" (op 2021).
- **SB Energy** codenames its **new** projects "Juno Solar 3" (= Juno 3 Solar) and "Juno
  Solar 4" (= Lyra Solar).
Confirmed by primary source: IAs 35077-2184/2185/2225/2227 all name **SE DC DevCo, LLC = SB
Energy** (3 Lagoon Dr Suite 280, Redwood City CA; @sbenergy.com), TSP = WETT.

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
| Lyra Solar | 27INR0434 | Juno Solar 4 | Solar | 500 | Muleshoe #59922 | -2185 (2025-07-07) | 59183 | 2027-09-15 / 2027-11-15 |
| Lyra Storage (BESS) | 26INR0636 | JUNO BESS I | Battery | 500 | Muleshoe #59922 | -2225 (2025-08-18) | 59183 | 2026-11-12 / — |
| **Antila Solar** | **27INR0500** | Antila Solar LLC | Solar | 500 | Buck Canyon #59916 | **-2227** (2025-08-18) | **59199** | 2027-11-30 / 2027-11-15 |

Campaign structure (paired lead+contingent IAs):
- **Muleshoe pair** (POI #59922, CCN 59183): Lyra Solar = lead IA ($18M) + Lyra Storage.
- **Buck Canyon pair** (POI #59916, CCN 59199): Juno 3 Solar = lead IA + Antila Solar
  ($100k, "contingent on the Juno Solar 3 Agreement").
- **Collector stations for all four co-located just N of US-180, W of Gail (~32.77,
  -101.556).** Antila's site == Lyra's site == Juno 3's site to within georeference slack (~1-2 km).

## Other queued Borden projects (context; not SB Energy, coords not in queue)
Draco Solar (27INR0499, 500 MW), Uva Creek Solar (26INR0359, 302 MW, EIA 68739 @
32.6798,-101.5044), Gail Mountain Solar (28INR0176, 244 MW, EIA 69506 @ 32.7146,-101.5274),
Caesar Solar+Storage (29INR0131/0132, Buck Canyon), Tumbleweed Solar+Storage (27INR0086/87,
Hecate, INACTIVE), Magnet Solar+Storage (28INR0297/98, HyFuels), Borden Dino Solar+BESS
(27INR0480/81), Enfinity Post Oak/White Oak (EG White Oak LLC), Iron Belt storage (EIA
67059 @ 32.5557,-101.6601, planned).

## Imagery attribution (this project's chips: `imagery/key/`, 3 dates)
5.0 km buffer around 32.772,-101.559 (S2 tile 14SKB; same scenes as Lyra, anchor within
georeference slack).
- **West edge (~-101.60/-101.61):** dark panel-row block = **existing operating solar (ENGIE
  Long Draw, EIA 62845, op 2020, and/or adjacent existing sites)** — NOT Antila.
- **Frame center, N of US-180 (= collector-station complex):** 2024-07-18 & 2025-07-20 (cloud
  0.0%) = **bare rangeland, no disturbance**. 2026-07-20 = **NEW bright ~1 km graded/cleared
  area** absent in 2025. The denser **co-located Lyra time series** (same scene) dates the
  onset: clearing 2026-03-29 → graded pad expanding 2026-05-31 → 2026-07.
- **CALIBRATION:** the bright feature reads as bare/graded **soil or gravel pad** — **no PV
  panels yet visible** (panels read *dark*). As consistent with the WETT collector-
  station/switchyard footprint as with generator site prep; Antila / Juno 3 / Lyra collectors
  co-located, not separable at S2 resolution.
- 2026 chip has cloud+shadow in the NE corner; the collector site (center) is clear.
