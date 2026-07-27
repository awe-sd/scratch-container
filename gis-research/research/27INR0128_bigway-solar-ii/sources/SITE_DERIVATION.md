# Site derivation — Bigway Solar II (27INR0128) / shared campus with Bigway Solar I (27INR0127)

**Anchor: 33.77561 N, -100.31339 W — confidence HIGH.**
Northern King County, TX. Bigway Solar I and II are ONE physical shared-campus project
(one IA, one substation, one abatement, one construction site); the individual INRs
cannot be spatially separated from imagery and are NOT cross-attributed.

## Evidence chain (best → corroborating)

1. **Ch.312 abatement tracts (primary, geometry-grade).** King County Commissioners' Court
   minutes 2026-01-12 (Second Amendment to Tax Abatement Agreement) name 10 survey abstracts.
   The minutes' "Abstract Number" values carry the King County code 269 as a prefix:
   D&W RR CO A-1030 (2691030), MASON A A-1160 (2691160) & A-1212 (2691212),
   MASSEY J V A-255 (269255), TT RR CO A-320 (269320) & A-1077 (2691077),
   I&GN RR CO A-309 (269309) & A-312 (269312), BURLESON J A-13 (26913), GROGAN HRS J A-90 (26990).
   Artifact: sources/2026-07-20_king-county-tx_commissioners-court-jan2026-minutes.pdf (p2 tract table).

2. **TX GLO Original Texas Land Survey (OTLS) polygons.** ArcGIS FeatureServer
   services1.arcgis.com/7DRakJXKPEhwv0fM/.../Original_Texas_Land_Survey/FeatureServer/0
   (field ABSTRACT_N). All 10 abstracts matched EXACTLY on survey name + abstract number
   (verified & reproduced 2026-07-21). Per-tract centroid mean = **33.77561, -100.31339**;
   vertex bbox lon -100.3552..-100.2813, lat 33.7397..33.8109 (~6.8 km E-W × ~7.9 km N-S).
   Artifacts: sources/2026-07-21_king-county_bigway-abatement-tracts_otls.geojson +
   sources/2026-07-21_king-county_bigway-abatement-tracts_map.png (parcel/tract map).

3. **IA Exhibit C (corroborating).** ERCOT Standard Generation IA, PUCT control 35077 item
   2069: "Bigway Substation located in King County approximately 14 miles south of Paducah, TX."
   Paducah (Cottle Co seat) 34.009 N, -100.302 W; 14 mi S ≈ 33.806 N, -100.302 W — ~2 mi NNE of
   the OTLS centroid, i.e. inside the tract cluster. Independent agreement.

4. **Imagery confirmation.** Sentinel-2 (4 km buffer) at the anchor shows the graded
   construction footprint (access-road grid + array-block pads) sitting ON these exact
   abstract tracts as of 2026-07-20 — the tracts and the disturbed ground coincide.

## Prior work
27INR0128's earlier deep scan derived this same centroid (33.77561, -100.31339) from the
OTLS abstracts — independently reproduced here. Its two July/Jan 2026 key frames were at a
wider 6 km buffer and read as "no activity"; they are retained under
imagery/superseded_6km/. The construction works ARE faintly present in that wider July
frame — the tighter 4 km set now in key/ makes them unambiguous.
