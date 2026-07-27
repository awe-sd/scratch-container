# Site derivation — Lamkin Solar 22INR0220 (user-directed 2nd pass, 2026-07-20)

Existing site coordinate (31.80352, -98.28654, from GIA Exhibit C's printed vicinity-map
DMS string) is corroborated, not replaced, by Ch.313 App #1785 (PUCT filing
`2026-07-20_comptroller_ch313-1785-app.pdf`), Tab 11 "Maps of Project":

- **p24 — Figure 1, "Comanche Solar Project School District Overview"**: county-wide map,
  red Project Boundary polygon shown just SW of the "Lamkin" label, inside the green
  Hamilton ISD outline — matches the queue/GIA site.
- **p25 — Figure 2, "Qualified Investment Area and Proposed Infrastructure"**: USGS
  topo extract, same polygon (blue dashed "Reinvestment Zone & Project Area", black-hatch
  "Qualified Investment Area"), green line = existing electric transmission crossing the
  NW lobe. Scale bar measured at ~9.06 ft/px; polygon bounding box ≈ 3.07 km E-W × 2.72 km
  N-S.
- **p26 — Figure 3, "Comanche Solar Project Reinvestment Zone"**: same polygon, relabeled
  (Reinvestment Zone == Project Area here, unlike some other projects where those differ).
- **p27 — a second, differently-sourced "Figure 1"** (Core Solar letterhead, aerial base,
  metric 0/250/500 m scale bar, dated 3/12/2001 — almost certainly a typo for 2021): same
  polygon over an aerial photo, showing a paved county road along the south edge curving
  down to cross a labeled **"Warren Creek"**, with natural terrain terracing inside the
  polygon (no development).

Independent corroboration (OSM/Overpass, `lz4.overpass-api.de`, 2026-07-20):
- **Lamkin** hamlet found 2.1 km from the coordinate (matches Figure 1's map label).
- A **69 kV power line** found ~1.6 km away — matches the GIA's own text: "Brazos Electric's
  69 kV Switching Station on FM 260, ~1 mile from Lamkin, TX."
- "Warren Creek" itself was **not found** in OSM within 12 km (nearest named waterways:
  Resley Creek, Leon River) — treated as an OSM rural-creek coverage gap, not a location
  contradiction, given the two independent corroborations above.
- A satellite chip's road-fork/terrain-terrace pattern visually matches Figure 1 (p27)'s
  aerial at the same scale.

=> Confidence upgraded to **high (independently corroborated)**. New AWS Open Data
Sentinel-2 chips (2022/2024/2025/2026) fetched at `--buffer-km 2.2 --buffer-y-km 2.6`
(kite-shaped polygon, taller than the default square) — replaces the prior CDSE-402 /
gmaps-blocked "unknown_imagery_blocked" construction verdict with a directly observed
`pre_construction` (no array, staging, or grading in any of the 4 years).
