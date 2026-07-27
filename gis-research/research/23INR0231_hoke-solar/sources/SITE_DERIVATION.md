# Site derivation — Hoke Solar (23INR0231 / f/k/a Brush Country Solar)

**Goal:** derive a lat/lon anchor for the project's solar array footprint from the
Ch.313 application's own boundary maps, since no parcel/GPS pin exists in any
document on disk and gmaps.py is quota-blocked (429, persistent since triage).

## 1. Identify which map is which (boundary vs. reinvestment zone vs. district)

Three project-authored maps were on disk (Enel Green Power, 2021, NAD83 StatePlane
TX South Central FIPS 4204 Feet):

| Page | Title | Scale | What it shows |
|---|---|---|---|
| `..._app_p29.png` | "Brush Country Solar - Vicinity Map" | 1:150,000 | Whole Nixon-Smiley CISD (green outline) in its 9-county regional context (Seguin/Luling/Gonzales/Yoakum/Cuero); a small **orange box legended "Brush Country Solar Project Boundary and Proposed Reinvestment Zone"** sits in the CISD's narrow NW arm, near FM 80, just south of the Guadalupe/Gonzales county line. |
| `..._app_p37.png` | "Brush Country Solar - Reinvestement Zone Within Vicinity" | 1:90,000 | Tighter crop of the same CISD, same orange box, now with local roads/creeks/the "Leesville" place label visible. **Same legend** ("Project Boundary and Proposed Reinvestment Zone") — i.e. the app treats project boundary and reinvestment zone as **one and the same box** on both maps; there is no separate, tighter "just the array" polygon anywhere in the application. |
| `..._agmt_p82/p83.png` | Ch.313 Agreement Exhibit A "Legal Description" / Exhibit B "Survey Map" of the "Brush Country Solar Reinvestment Zone" | — | Exhibit B (p83) is the **same** Reinvestment-Zone-Within-Vicinity map as app p37 (rotated to portrait), not a tighter survey plat. Exhibit A (p82) is a **parcel table**, not a map — see finding below. |

**Conclusion:** the orange box on p29/p37/agmt-p83 IS the project boundary (== the
reinvestment zone, per the applicant's own legend — these ch313 filings do not
distinguish a smaller array footprint from the zone). No tighter polygon exists in
any source on disk. IA Exhibit C3 (`..._p59.png`, satellite screenshot) shows a
**different, smaller feature**: the POI substation pad, ~2-3 mi SE of this box,
independently confirmed below.

### Bonus (not used for geocoding, logged for provenance)
Exhibit A (agmt p82) gives the **underlying ranch tract** the reinvestment zone sits
on: Owner **QSTS RANCH PARTNERSHIP LTD**, Parcel ID **1715**, legal description
"34 J DE LA BAUME QUEIN SABE RANCH", 4,185.19 acres total (the box carves ~1,300
acres of lease/easement out of this larger ranch per app p22/24). QSTS Ranch
Partnership, Ltd. is a real Texas LP (OpenCorporates: registered San Antonio, TX,
since 1996) — a landowner, not the SPV. Gonzales CAD (gonzalescad.org) and Regrid
both gate their parcel-lookup/GIS behind JS/login that WebFetch cannot execute, so
this could not be converted into an independent parcel-centroid lat/lon within
budget; noted as a lead for anyone with interactive CAD access.

## 2. Georeferencing method (map-internal scale-bar math + OSM anchor, per playbook rule 4)

gmaps.py is 429-quota-blocked. OSM Overpass (`lz4.overpass-api.de`) worked for point
lookups but 504/timed out twice on heavier polygon/relation queries (county
boundary relation, substation search) even after a 10s wait + one retry each — per
convention, those were treated as misses and the derivation fell back to the
prescribed map-internal scale-bar method, using Overpass only for the lighter
point/way lookups that did succeed.

**Scale-bar math (independent of eyeballing the printed ticks):** both PNGs were
rendered by `exhibit.py` at its default 170 DPI; both are exactly 6120x4080 px =
36x24 in (ARCH-D landscape) — confirms 170 DPI directly (6120/170 = 36.0). At a
printed scale of 1:N, 1 inch = N/63,360 miles, so:
- p37 (1:90,000): 170 / (90,000/63,360) = **119.68 px/mile**
- p29 (1:150,000): 170 / (150,000/63,360) = **71.8 px/mile**
Both match the visually-read tick spacing on each map's own scale bar (~120 px/mi
and ~71.7 px/mi respectively) — cross-validated, not just assumed.

**Orange-box pixel centroid** (color-threshold connected-component detection,
`r>200,100<g<190,b<60`, legend swatch masked out by x/y crop before labeling):
- p37: bbox x 2103-2238, y 987-1161; area centroid (accounting for the notch cut
  from the bottom-right corner) = **(2166.0, 1068.0)**.
- p29: single component, bbox x 1658-1744, y 2123-2232; centroid =
  **(1701.7, 2176.4)** — matches the prior (dead) run's independently-eyeballed
  (1700.5, 2177.5) almost exactly, cross-validating the detection.

**Anchor 1 — Leesville, TX** (OSM Overpass node 151462694, place=hamlet):
`29.4069038, -97.7449990` (confirms the prior run's Nominatim value to 5 decimal
places, now independently re-derived via Overpass per the task's required method).
Pixel position on p37 ≈ (2200, 1445) — the basemap's "Leesville" label is drawn
straddling the through-road (OSM "TX 80"/local road) at that row; road+label
placement together fix the point to this pixel, ±~100 px (~0.1 mi) of subjective
uncertainty in exactly where under the text the point sits.

Vector from Leesville to box centroid (p37): dx = 2166-2200 = **-34 px** (west),
dy = 1068-1445 = **-377 px** (north, image-y-up = north).
In miles: -0.284 mi east/west, +3.150 mi north (at 119.68 px/mi).
In degrees (69.0 mi/deg lat; 60.11 mi/deg lon at cos(29.42 deg)=0.8712):
dlat=+0.04565, dlon=-0.004727.
**Box (via p37/Leesville) = 29.4526, -97.7497.**

**Anchor 2 — Nixon, TX** (OSM Overpass node 151811162, place=town):
`29.2696579, -97.7625132`. Pixel position on p29 ≈ (1670, 3085) (label centroid,
same subjective-placement caveat, larger here since Nixon is a built-up polygon not
a point).
Vector to box centroid (p29): dx=+31.7 px (east), dy=-908.6 px (north), i.e.
+0.442 mi east, +12.655 mi north (at 71.8 px/mi) -> dlat=+0.18341, dlon=+0.007345.
**Box (via p29/Nixon) = 29.4531, -97.7552.**

**Cross-check:** the two fully independent map pages (different scale, different
anchor town, different OSM lookups) agree on **latitude to within 0.0005 deg
(~100 ft)** and on **longitude to within 0.0055 deg (~0.33 mi)** — the longitude
spread is expected given the Nixon baseline is ~4x longer than the Leesville
baseline (any small angular/measurement error amplifies over distance). Qualitative
OSM cross-check: County Road 102 (Overpass way 15252431, lat 29.4369-29.4991, lon
-97.7387/-97.7402) sits ~0.6 mi east of the derived box at a matching latitude band
— consistent with the visual gap on both maps between the box's east edge and CR102.
The LCRA 138kV line (way 15250175, vertices ~29.4217-29.4315 N / -97.7391 to
-97.7405 W) sits ~1.4-2.1 mi south of the box at a similar longitude — consistent
with the IA's own narrative that the POI/substation sits south-southeast of the
generation site.

**ADOPTED ANCHOR (average of the two independent derivations):**
**lat = 29.453, lon = -97.751**
**Confidence: medium** — two independently-derived, cross-validated map-based
fixes agree to ~0.3 mi; no ground-truth pin (gmaps blocked) or CAD parcel centroid
obtained. A 3.5 km imagery buffer comfortably covers both the ~2 km box extent and
the ~0.3-0.5 mi cross-check spread.

## 3. Distinct feature: the POI substation (NOT the array)

IA Exhibit C3 (`..._puct_35077-1562..._p59.png`, Google Earth screenshot, explicitly
labeled "23INR0231 & 23INR0232 Brush Country LLC (aka Rocinante) Generation
Interconnection at LCRA TSC's Leesville Substation") shows the **POI substation
pad**, not the generation site: a fenced yard immediately west of a paved road
(Google's on-image label "102" — a **local road**, not the same feature as County
Road 102 identified above by number-coincidence only; no Overpass name/ref match
was found for a "FM 102" in this area, so this is presumably an unofficial/legacy
county designation not carried in OSM) at its crossing with a NE-SW stream. This
POI sits ~2-3 mi SSE of the derived project-boundary box, matching the original
(dead) run's qualitative read and the ch313 app's own text ("Brush Country Solar
anticipates interconnecting to the existing LCRA 138-kV Nixon to Deer Creek
Transmission line").

## 5. Imagery confirmation (supersedes the map-only estimate)

The `s2aws.py` chip centered on the adopted map anchor (29.453,-97.751, 3.5km buffer)
shows no disturbance in 2024/2025, then a large graded/racking-row construction
footprint appearing by 2026-01 sitting almost exactly at frame center, growing through
2026-07. This independently confirms the map derivation was correct. The array
footprint's own pixel bbox was measured directly off the clearest (2026-07-15, acq.
2026-07-09) chip (~x:280-460, y:205-390 of the 700x700px/10m-per-px chip) and converted
to lat/lon: **29.4577, -97.7489** (offset +200m E, +525m N of the chip center) — within
~0.5 km of the map-only estimate. `findings.json` `site.lat/lon` uses this
imagery-measured point with **high** confidence, superseding the medium-confidence
map-only fix above (which stands as the independent corroborating derivation).

## 6. Map artifacts used

- `sources/2026-07-20_comptroller_ch313-1618-nixon-brush-app_p29.png` — vicinity
  map, district-wide context, orange box = project boundary/reinvestment zone.
- `sources/2026-07-20_comptroller_ch313-1618-nixon-brush-app_p37.png` — reinvestment
  zone within vicinity, tighter/higher-scale render of the same box (primary
  derivation source).
- `sources/2026-07-20_comptroller_ch313-1618-nixon-brush-agmt_p82.png` — Exhibit A,
  legal description / parcel table (QSTS Ranch Partnership Ltd, Parcel 1715).
- `sources/2026-07-20_comptroller_ch313-1618-nixon-brush-agmt_p83.png` — Exhibit B,
  survey map (same box, portrait rotation of app p37 — confirms no tighter polygon
  exists in the agreement package either).
- `sources/2026-07-20_puct_35077-1562_ercot-standard-generation-interco_p59.png` —
  IA Exhibit C3, POI substation location (distinct feature, not the array).
