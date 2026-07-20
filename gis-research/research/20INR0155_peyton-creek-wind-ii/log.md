# Research Log — Peyton Creek Wind II (20INR0155)

Project: Peyton Creek Wind II · 241.2 MW Wind · Matagorda County, TX
CDR Zone: COASTAL · POI: 42400 Refuge 345kV · Reported COD: 2026-07-01
Research started: 2026-07-19

---

## Stage 1 — LLC → Parent Chain


## 2026-07-19 — Stage 1 findings

**Ch.313 App 1307**: Peyton Creek Wind Farm, LLC / Bay City ISD. Original agreement 2019-08-07.
- Signed as `c/o EC&R Development, LLC` (E.ON Climate & Renewables). Contact: paul.bowman@eon.com
- Artifact: sources/2026-07-19_comptroller_ch313_1307-peyton-creek-wind-farm-agmt.pdf (page 23)
- By 2022-2025, mailing address: 353 N Clark St #30 Chicago IL 60654 — Invenergy HQ.
  Strongly suggests E.ON sold the project to Invenergy (E.ON sold NA renewables to RWE 2020,
  then possibly Invenergy acquired from RWE or from E.ON pre-sale).
- IMPORTANT: the Ch.313 is for "Peyton Creek Wind Farm" (the original project), but the INR
  20INR0155 is "Peyton Creek Wind II". Different projects but same site/developer. Need PUCT IA
  for the Wind II entity specifically.

## 2026-07-19 — Queue history findings (timeline.md)

IA signed: 2023-02-27. FIS approved: 2024-06-25. Approved for energization: 2024-12-30.
Approved for synchronization: 2025-02-05. Commercial operation NOT yet approved.
10 COD changes: 2020-12 → 2026-07-01 (latest).
This project is likely ONLINE or near-COD. ApprSync = 2025-02-05, ~17 months ago.

## 2026-07-19 — Stage 3 site pinpoint — START

Google Places search for "Peyton Creek Wind II": HTTP 429 rate limit. Trying other methods.


## 2026-07-19 — CDSE credentials failure

Source: cdse.py Sentinel-2 imagery tool
Query: authentication to dataspace.copernicus.eu
Date: 2026-07-19
Result: 401 Unauthorized - "Invalid user credentials". CDSE password expired/invalid.
Cannot pull Sentinel-2 imagery this session.

## 2026-07-19 — Site pinpoint from OSM

OSM Overpass query: wind turbines bbox (28.5,-96.2,29.3,-95.4), generator:source=wind
Result: 48 turbines named "Peyton Creek Wind Farm", operator "RWE Renewables", start_date "2020"
  Nordex AW125/3150 (Acciona AW125/3000), 3.15 MW each
  Lat: 28.84203 to 28.89482
  Lon: -95.91056 to -95.85258
  Center: ~28.872, -95.875
OSM relation 13509567: plant:output:electricity = 151.2 MW, ref:US:EIA = 62417
This is Wind I. Wind II (241.2 MW, 20INR0155) not yet in OSM.

## 2026-07-19 — Ownership chain clarification

Original developer: EC&R Development, LLC (E.ON Climate & Renewables)
  → per Ch.313 agreement 2019, contact: paul.bowman@eon.com
  → Ch.313 map labeled "E.ON Climate & Renewables NA"
E.ON → RWE swap (2020): E.ON transferred renewables to RWE in asset swap
  → OSM operator = "RWE Renewables" (Wind I)
  → 2025 Form 772 mailing address: 353 N Clark St #30 Chicago IL 60654
  This address = Invenergy HQ (confirmed separately). 
  INFERENCE: Invenergy acquired Wind II from RWE (or directly from E.ON/EC&R pre-swap).
  This is UNCONFIRMED - the Ch.313 is for Wind I (Peyton Creek Wind Farm LLC), not Wind II.
  Note: triage file (cleanview-banned source) says "developer: RWE". Queue data doesn't confirm.


## 2026-07-19 — RWE portfolio page

Source: americas.rwe.com/wind-power/wind-projects (fetched 2026-07-19)
Result: RWE lists "Peyton Creek" (Wind I, 151 MW, 48 Nordex turbines) as OPERATING.
"Peyton Creek Wind II" NOT listed in RWE portfolio. This strongly suggests Wind II has a DIFFERENT owner.
The 353 N Clark St Chicago address in Form 772 is for Wind I LLC only - not necessarily related to Wind II.

## 2026-07-19 — Key observation on queue timeline

IA signed 2023-02-27 → approved for sync 2025-02-05 (24 months build time). 
Current COD in queue: 2026-07-01 (passed 18 days ago).
"Commercial operation NOT yet approved" in ERCOT data as of June 2026 snapshot.
But: approved for sync Feb 2025 = physically energized + testing.
COD=2026-07-01 may indicate it JUST reached commercial operation.
The gap between sync approval (2025-02) and COD (2026-07) is 17 months - unusual.
Could indicate: partial COD (some turbines), commissioning delays, or offtake completion.


## 2026-07-19 — Stage 3: site pinpoint

Method: OSM Overpass query for wind turbines in Matagorda County area.
Wind I (Peyton Creek Wind Farm, RWE Renewables): 48 turbines at 28.842-28.895, -95.852 to -95.983.
Center of Wind I cluster: 28.867, -95.893.
Wind II (20INR0155, 241.2 MW) NOT yet in OSM. No separate turbine pads found in OSM.
Best estimate: adjacent to Wind I, expanding west/southwest. Center ~28.860, -95.940.
Confidence: MED — derived from Wind I centroid + adjacency reasoning, NOT direct observation.

Source: Overpass API query, 2026-07-19 (85 wind turbines total; 48 named Peyton Creek Wind Farm)

## 2026-07-19 — Negative searches

1. Google Places "Peyton Creek Wind II" — HTTP 429 daily quota exhausted
2. CDSE Sentinel-2 imagery — 401 invalid credentials
3. PUCT Interchange search — JS-only interface, no results returned
4. FAA OE/AAA search — government system returning 3-byte response
5. JETI registry (Matagorda) — no matching entries
6. TX Comptroller Ch.313 (Wind II) — no separate agreement found for Wind II
7. SEC EDGAR "Peyton Creek Wind II" — 0 hits
8. EIA plant lookup (plant 62417 = Wind I) — API returns empty
9. Matagorda CAD — website "coming soon"
10. RWE Americas portfolio — Wind I (151 MW) listed; Wind II absent → different owner

