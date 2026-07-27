# Site derivation — Possum Kingdom Solar (24INR0118)

Rescan 2026-07-21. Resolved anchor: **33.0318 N, -98.2947 W** (Jack County, TX, near the
Palo Pinto County line, ~7 mi NNW of Graford). Confidence: **high** (three independent
public records converge; not a single-rung determination).

## Why no single rung was enough

1. **IA Exhibit C (redacted).** The executed Standard Generation Interconnection Agreement
   (`2026-07-19_puct_35077-2239_standard-generation-interconnection-agreement-be.pdf`, p.33)
   names the POI: "the Point of Interconnection is located in Jack County, Texas, at the
   **Halsell Ranch Switch** within the TSP's Thomas Price Switch - Willow Creek Switch 345 kV
   transmission line... The Halsell Ranch Switch will be located [REDACTED]". Oncor's PUCT
   cover letter (p.3) confirms the redaction: "Oncor Electric Delivery has redacted station
   location information, which contain CEII, located in Exhibit C". So we get an authoritative
   PLACE NAME ("Halsell Ranch") but no coordinates.

2. **Ch.313 map exhibit (the map rung).** Comptroller agreement #1728 (Graford ISD,
   applicant PK Solar LLC f/k/a Novis Renewables LLC) Checklist Item #11 includes real maps:
   - `2026-07-21_comptroller-ch313-1728_map-project-boundary-p25.png` — the solar-panel
     footprint polygon ("Project Boundary" / "Solar Panels" legend) on satellite imagery.
   - `2026-07-21_comptroller-ch313-1728_map-vicinity-p26.png` — regional vicinity map;
     the "Proposed Reinvestment Zone" sits just NW of Graford, TX.
   - `2026-07-21_comptroller-ch313-1728_map-reinvestment-zone-p27.png` — same polygon,
     zoomed in, with a labeled landmark pin at its northern end: **"Marluc Bella Vita
     Ranch"**.

3. **Landmark → address → road name (the bridge).** WebFetch of the ranch/lodge's own
   booking site (lakegodstone.com — Marluc Bella Vita Ranch operates "Lake Godstone")
   returns its street address: **"4636 Halsell Ranch Road, Graford, TX 76449"**. The road
   name independently matches the IA's redacted switch name ("Halsell Ranch Switch") —
   two unrelated documents (an interconnection agreement and a tax-abatement map) both
   point at the same place name, filed years apart, by different parties (Oncor vs.
   Novis Renewables/EY).

4. **GNIS/TIGER cross-reference (the anchor).** Overpass query for `name~"Halsell"` in a
   bbox around Jack/Palo Pinto counties returns:
   - Way "Halsell Ranch Road" (2 segments, `tiger:county=Jack, TX`), spanning
     33.030–33.046 N / -98.331 to -98.271 W.
   - Node "Halsell Ranch Cemetery", **GNIS feature_id 1337264** (a federally-documented
     named place, USGS Geographic Names Information System), at **33.0318 N, -98.2947 W**.

   The cemetery centroid sits inside the Halsell Ranch Road corridor and inside the
   Ch.313 mapped reinvestment-zone polygon's footprint — used as the site anchor.

## Cross-checks

- Ch.313 filing states the (2022-vintage, ~2,500-acre) reinvestment zone is 65% Palo
  Pinto County / 35% Jack County. The resolved anchor sits near the Jack/Palo Pinto
  line, consistent with that split.
- Prior (2026-07-19) POI triangulation via OSM reverse-geocoding of Willow Creek Switch
  (33.0562 N, -97.9103 W) and Jacksboro substation (33.2772 N, -98.1068 W) bracketed
  "eastern Jack County, 33.0–33.3 N, 98.0–98.4 W" — the new anchor falls inside that
  zone, near its western edge.
- Sentinel-2 imagery at the anchor (see `imagery/key/` and `imagery/wide/`) shows
  rangeland consistent with the Ch.313 map's undeveloped-in-2022 baseline, with the
  Longhorn Solar operating plant (Repsol Renewables NA, 650 MW) visible ~4.5 km west as
  a positive control that the imagery source resolves construction when present.

## What this is NOT

Not a parcel-precise or surveyed pin. `site.lat/lon` in findings.json is a
~1 km-radius place-name anchor corroborated three independent ways, not the switch's
surveyed coordinates (those remain CEII-redacted) and not a parcel boundary.
