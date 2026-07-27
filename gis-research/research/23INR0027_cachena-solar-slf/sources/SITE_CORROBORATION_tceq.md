> **CORRECTED 2026-07-21.** This doc originally read the TCEQ address below as merely
> "corroborating" the EIA-860M point (29.26357,-97.78055) -- but that EIA point is the
> Nixon, TX town centroid (an administrative artifact), not the plant, and the address
> was never actually geocoded. Geocoded now (two independent services, Esri ArcGIS +
> Google Places, agree to ~0.5 mi): **29.2579,-97.8057** — see `findings.json` `site` for
> the adopted point and full cross-checks. This address is the PRIMARY site anchor, not a
> mere corroboration of the (wrong) EIA point. The 2026-07-20 deep pass separately (and
> wrongly) adopted a DIFFERENT point, 29.456,-97.750 = Hoke Solar's (23INR0231) footprint
> in Gonzales County — see `findings.json` `retraction` for that chain.

# Site corroboration — Cachena Solar SLF / Enbridge Clear Fork (2026-07-20)

No Ch.313 exists (checked: "Cachena", "Clear Fork", Wilson-county ISDs — program
expired 2022-12; project took FID without value limitation; no JETI either). The
LOCATION + CONSTRUCTION proof comes from TCEQ construction-stormwater NOIs instead
(artifact: 2026-07-20_tceq_stormwater_nois_clearfork_cachena.json):
- CLEAR FORK CREEK SOLAR, STORM TXR1512VO, owner Hanwha Q Cells EPC USA LLC (EPC!),
  ACTIVE since 2025-08-15 — site: 10046 US HIGHWAY 87 EAST, Wilson Co
- CLEAR FORK CREEK SOLAR SUBSTATION, TXR1573TG, same EPC, from 2025-01-13
- CACHENA SOLAR POI, TXR1599VD, owner Dorazio Enterprises ("CPS ENERGY SOLAR POI"),
  ACTIVE since 2025-07-09
=> [SUPERSEDED 2026-07-21] originally claimed this "corroborates findings site
29.26357,-97.78055" and "PROVES construction start (EPC stormwater coverage = dirt
moving)". Both overstated: 29.26357,-97.78055 is the Nixon town centroid, not a
verified plant point, and an ACTIVE stormwater-NOI registration proves a construction
PERMIT exists, not that Sentinel-2-visible earthwork has happened -- a 2026-07-21
imagery sweep at the now-geocoded true address point (29.2579,-97.8057, this address's
own coordinates) found no visible grading through 2026-07-09 (see findings.json
`construction`). The address itself IS a solid site anchor (two independent geocoders
agree); the inferences drawn from it here were not.
Timeline: substation Jan-25 → POI Jul-25 → main array Aug-25 (permit dates only).
