# GIS-research — external data sources

What each research tool fetches, and from where. All web access is throttled/cached per the
tool; agents must use these tools rather than scraping directly. Generated 2026-07-24.

## Registry / incentive resolvers

| Data | Tool | Host(s) | Endpoint / notes |
|---|---|---|---|
| **Ch.313** school-district abatements | `ch313.py` | `comptroller.texas.gov`, `api.comptroller.texas.gov` | Static 740-row set + JETI API `api.comptroller.texas.gov/open-data/v1/tables/jeti`; detail page `comptroller.texas.gov/economy/development/prop-tax/jeti/application-details.php?id=`. Keys on **school district**, not county. |
| **JETI** (post-313 incentive) | `ch313.py` | `api.comptroller.texas.gov` | `/open-data/v1/tables/jeti` — same call as Ch.313. |
| **Ch.312** county/city abatements | `ch312.py` | `comptroller.texas.gov`, `api.comptroller.texas.gov`, `assets.comptroller.texas.gov`, `web.archive.org` | `.../search-tools/ch312/abatements-simple.php`, `/open-data/v1/tables/`, `assets.comptroller.texas.gov/dat/ch312/…`; `web.archive.org/cdx` fallback for stale/removed rows. ~1,400 rows; the post-2022 abatement rung. |
| **TCEQ stormwater / air (NSR) filings** | `tceq.py` | `data.texas.gov` | Socrata SoQL `data.texas.gov/resource/{id}.json`; stormwater datasets `5eqq-7nad`, `9iad-hrn8`; 5 regional Central-Registry tables, county-routed. |
| **County clerk / commissioner agendas & minutes** | `minutes.py` | *(no fixed host)* | No hardcoded portal — each TX county publishes differently, so it resolves per-county via `search.py`. |

## Interconnection / ownership

| Data | Tool | Host(s) | Notes |
|---|---|---|---|
| **PUCT Interchange** (executed IAs, docket 35077) | `puct.py` | `interchange.puc.texas.gov` | Throttled 2s, backoff on the portal's 402 rate-limit. Search by **FilingDescription** in control **35077**. |
| **Docket↔INR join** | `inr_harvest.py` | `interchange.puc.texas.gov` (via puct.py) | Downloads docket-35077 PDFs once → extracts INR strings → `research/_reference/puct_inr_join.json`. |
| **SPV / developer candidates** | `spv.py` | *(local only)* | EIA-860M xlsx + local PUCT docket index; no live scraping. |
| **EIA-860M history** | `eia_history.py` | *(local only)* | Reads `data/eia_generator_tx.parquet` (AW.dbo tables); no live scraping. |
| **FAA obstruction cases** (wind) | `faa.py` | `datahub.transportation.gov`, `oeaaa.faa.gov` | Both live sources blocked as of 2026-07 (Socrata private + oeaaa shutdown) — runs off cached pulls, self-heals on `refresh`. |

## Imagery

| Data | Tool | Host(s) | Notes |
|---|---|---|---|
| **Sentinel-2 chips** (primary) | `s2aws.py` | `earth-search.aws.element84.com` + `s3://sentinel-cogs` | STAC search + public COGs; no auth, no quota. |
| **Sentinel-2 composites / timelapse** | `cdse.py` | `identity.dataspace.copernicus.eu`, `openeo.dataspace.copernicus.eu` | Copernicus openEO; free-tier 2-concurrent/12-per-min; shared token cache. |
| **Google Maps / Places** | `gmaps.py` | `maps.googleapis.com`, `places.googleapis.com` | Static/geocode + place lookups; API key from `~/.config/gis-research.env`. |

## Web search

| Data | Tool | Host(s) | Notes |
|---|---|---|---|
| **General web search** (the ONLY search entrypoint) | `search.py` | AgentCore Gateway (if configured) → OAuth bridge → `html.duckduckgo.com` | 7-day cache, 3s throttle, 120/h fleet cap. **Banned:** queue-tracker/aggregator domains (interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, infrasure.ai, futuregrid.io) — suppressed at the tool layer. |

## Summary of distinct external hosts

- `comptroller.texas.gov` / `api.comptroller.texas.gov` / `assets.comptroller.texas.gov` — Ch.313, Ch.312, JETI
- `data.texas.gov` — TCEQ (Socrata)
- `interchange.puc.texas.gov` — PUCT IAs
- `datahub.transportation.gov` / `oeaaa.faa.gov` — FAA (currently blocked, cache-only)
- `earth-search.aws.element84.com` + `s3://sentinel-cogs` — Sentinel-2 (AWS)
- `identity.dataspace.copernicus.eu` / `openeo.dataspace.copernicus.eu` — Copernicus
- `maps.googleapis.com` / `places.googleapis.com` — Google
- `html.duckduckgo.com` — search fallback
- `web.archive.org` — Ch.312 archival fallback
