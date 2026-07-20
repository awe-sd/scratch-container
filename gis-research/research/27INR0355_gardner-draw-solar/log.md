# Triage log — 27INR0355 Gardner Draw Solar

Triage date: 2026-07-18

---

T1 start
## T1 — Queue history
- 22 snapshots: 2024-09-01 → 2026-06-01
- COD drift: 0 — stable at 2027-12-31 throughout
- Milestones: Screening started 2024-10-01, Screening complete 2024-12-30, FIS requested 2024-09-25, **IA signed 2025-08-07** — FIS approved NOT achieved
- Capacity bumps: 200 MW → 300 MW (2025-10) → 309.5 MW (2026-05)
- No construction milestones

## T2 — Delivery pins
- gmaps.py 429 Too Many Requests on both attempts (exact name, name+county) — budget exhausted
- No pins found

## T3 — Web sweep
- DDG: CAPTCHA block on both attempts (exact name, LLC name) — 1 retry exhausted
- Bing "Gardner Draw Solar" Texas: no relevant results
- Bing "Gardner Draw" solar Glasscock Texas: no relevant results
- No developer name, press release, or news found
- No pages saved to sources/

## T4 — PUCT Interchange
- interchange.puc.texas.gov: HTTP 402 on all paths (/, /search, /Documents/Search.aspx)
- Portal blocked — all 3 attempts exhausted budget
- No IA confirmation or PDF retrieved
- Note: queue data shows iaSigned = 2025-08-07 (milestone achieved per ERCOT GIS report) but IA document not accessible via PUCT

## T5 — Abatements
- TX Comptroller Ch.313: page navigation only, no searchable data accessible via WebFetch; Ch.313 expired 2022 so a 2024-filed project would not have one
- JETI registry: navigation page only, no agreement list accessible
- Budget exhausted (4 fetches)
- No abatement found — NORMAL for post-2022 project

## T6 — Imagery
- Site candidate: Glasscock County center (31.870N, 101.520W) based on POI = Sand Bluff 345kV (59902); confirmed Glasscock is correct county via parquet
- CDSE chips: HTTP 401 Unauthorized on all 9 grid attempts — credentials not available in this environment
- No contact sheet produced, no construction imagery obtained
- construction_visible: null

## T7 — Write and stop
- triage_findings.json written
- triage.md written
- Turns used: ~26
- STOP

---

# Deep scan log — 27INR0355 Gardner Draw Solar

Deep scan date: 2026-07-19

## D1 — Developer identified via GIS xlsx
- Queried local xlsx: gis-research/data/RPT.00015933.0000000000000000.20260701.151514224.GIS_Report_Jun2026.xlsx
- Row for 27INR0355 → col3 (entity) = **"RWE Clean Energy Development, LLC"** — developer confirmed
- Companion project 27INR0371 (Feather Dalea BESS, 200 MW) = same RWE entity, same Sand Bluff 345kV (59902) POI, Glasscock County, COD 2027-07-02 — co-located BESS
- Other Sand Bluff projects: 26INR0452 (Cannibal Draw Solar, 149.5 MW, 2028-04), 26INR0453 (Cannibal Draw Storage, 98.6 MW), 27INR0076 (Bob Creek Wind NextEra 240 MW Sterling Co), 27INR0383 (Windjammer 244 MW), 30INR0080 (Indigo Quill Gas 370 MW RWE)
- **Artifact:** extracted from local xlsx file (no saved source — data already on disk)
- Significance: RWE is a major developer, this is a real project, not a paper speculator

## D2 — Sand Bluff substation location confirmed
- OSM Overpass query: way[power=substation][name~"Sand Bluff",i] in bbox 31.5,-102.0,32.5,-100.5
- Result: Sand Bluff Substation lat=32.0035397, lon=-101.2732002, operator="Wind Energy Transmission Texas", 345kV
- This is in Sterling County (Glasscock border is just to the west at ~lon -101.33)
- Gardner Draw Solar (Glasscock County) will be W or SW of the substation, within ~5-10 km of the county line
- Confidence: HIGH — OSM source consistent with queue POI "59902 Sand Bluff 345kV"

## D3 — PUCT Interchange still 402
- All interchange.puc.texas.gov URLs continue returning HTTP 402
- IA document not retrievable — IA date only confirmed via ERCOT queue milestone

## D4 — RWE press/news
- Americas.rwe.com/press: navigation page only, no indexed press releases
- RWE.com press: no Gardner Draw Solar press release found
- No news coverage found (project too new/unpublicized)

## D5 — TX Comptroller / JETI
- JETI current agreements: no Glasscock County entries — only 10 ISDs listed, none in Glasscock
- Ch.312/SB1340 search: API errors loading data
- No abatement agreements found — expected for 2024-filed project (Ch.313 expired 2022)

## D6 — Glasscock County CAD
- glasscockad.org: DNS not resolving
- co.glasscock.tx.us: found, but no property search portal linked; archived minutes only 2020-2021
- No CAD parcel search available online; no parcels found under Gardner Draw Solar / RWE

## D7 — CDSE imagery
- Credentials still 401 (example env file only, no real creds configured)
- Existing imagery chip (triage): county centroid 31.87/-101.52 = undisturbed farmland/ranchland with oil/gas pads — this is 17 km west of Sand Bluff Sub; likely wrong location
- Correct target: ~32.00N, -101.33-101.40W (Glasscock side of Sand Bluff, ~2-5 km west of substation)
- Cannot run imagery — 401 blocks all CDSE calls
