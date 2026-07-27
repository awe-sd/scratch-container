# Research Log — 21INR0324 Board Creek Wind (Limestone Wind)

## 2026-07-19 — Triage session (prior run)

See triage.md. Key findings: ERCOT "Board Creek Wind" = ENGIE "Limestone Wind", 301 MW, Navarro Co TX, COD end-2022. PUCT 402-blocked; TX Comptroller JS-blocked.

## 2026-07-20 — Deep scan session

### D0 — Skeleton + triage review

- Triage confirmed project is ENGIE's "Limestone Wind" — queue name ≠ public name.
- Factsheet signals: `eia_operating_date`, `verified_ia_on_disk`, `fis_approved`, `financial_security_posted` — all four reality signals present.
- EIA status already shown as Operating in factsheet. Queue COD 2026-07-01 is stale.
- IA PDF already on disk: `sources/2026-07-19_puct_35077-1306_interconnection-agreement-between-oncor-electric.pdf`
- Findings.json skeleton written.

### D1 — IA schedule extraction

**PUCT 35077-1306 confirmed (INR in document)**
- SPV: Limestone Wind Project, LLC (Delaware LLC)
- TSP: Oncor Electric Delivery Company LLC
- Signed: 2021-08-19
- Equipment: 99 × GE 3.03-140 turbines, 3.367 MVA each, 333.30 MVA gross, dispatched 301 MW
- Delivery voltage: 345 kV
- POI: Outlaw Switch, Navarro County, ~6 mi SE of Richland TX; within Navarro Switch – Limestone SES 345 kV double-circuit line

**Schedule (Exhibit B):**
- In-Service Date: 2022-05-19
- Scheduled Trial Operation: 2022-09-23
- Scheduled COD: 2022-11-04

**Security (Exhibit E):** Irrevocable Standby Letter of Credit form specified; dollar amount not visible in PDF text extraction.

**No amendments found** — PUCT docket 35077 has only item 1306 matching this project. No amendment filings.

`puct.py match` also retrieved a second-download confirmation (already on disk, re-downloaded same file).

### D1 — EIA history

`eia_history.py 21INR0324 --write` output:
- EIA plant 65306 "Limestone Wind Project" entity "Limestone Wind Project, LLC"
- Capacity: 299.2 MW throughout
- Status history:
  - 2022-04 to 2022-07: Under construction ≤50%
  - 2022-08: Under construction >50%
  - 2022-09: Construction complete, not yet in commercial operation
  - 2023-01 to 2026-05: **Operating**
- Operating date reported: **2022-12**
- Planned COD: 2022-12 (reported Apr–Sep 2022), then null (already operating)
- EIA coordinates: 31.85346, -96.62446

**Key finding:** EIA shows operating since 2022-12. Queue COD 2026-07-01 is confirmed stale — ERCOT never closed out this entry with `approvedForCommercialOperation`.

### D2 — Site identification

**PUCT PGC Registration (53424-1, filed 2022-03-29):**
- Legal name: Limestone Wind Project, LLC; trade name: Limestone Wind
- Physical address: **803 SW County Road 4260, Dawson TX 76639, Navarro County**
- Parent chain: ENGIE IR Holdings, LLC (100%) → ENGIE North America Inc. (ultimate parent)
- ONCOR North zone, 299.2 MW

**OSM Overpass query (Navarro Co wind turbines):**
- 88 turbine elements tagged `name=Limestone Wind` (88 of 99 per IA; 11 possibly unmapped/slightly different tags)
- Centroid: **31.82707, -96.66834**; lat range 31.77–31.88 (~12 km N-S spread)
- Named substation: **"Limestone Wind Substation"** at 31.8534454, -96.6219567
- EIA plant coords (31.85346, -96.62446) agree within 100 m of substation
- OSM data saved: `sources/2026-07-20_osm_overpass_limestone-wind-turbines.json`

**Address crosscheck:** Dawson TX (Navarro Co) at 31.894, -96.715; 803 SW CR 4260 would be ~5 km W of the Limestone Wind Substation — consistent with a large 99-turbine wind farm spanning that area.

**CDSE satellite imagery:** CDSE identity endpoint (identity.dataspace.copernicus.eu) returning RemoteDisconnected on all attempts — likely service outage 2026-07-20. No chips obtained.

### D3 — Gap-fill

**FAA OE/AAA (faa.py resolve 21INR0324):** Negative — no Navarro County TX wind turbine cases in local cache. Live FAA sources blocked 2026-07. Deep-link recorded for future access.

**SPV resolution (spv.py resolve 21INR0324):** EIA-860M hit — "Limestone Wind Project, LLC", Operating, 299.2 MW @ 31.85346,-96.62446.

**PUCT search "Limestone Wind":** Additional dockets found:
- 53424: PGC Registration (2022-03-29, approved 2022-04-18)
- 53650: REC Generator Certification application
- 55749, 59131: PGC renewal registrations (even-numbered years)
- 53385: Emergency Operations Plan filing

**Search.py:** All backends failed (AgentCore pending + DDG/OAuth also failing) — negative evidence logged.

**ENGIE website:** bot-blocked (Imperva challenge); press release page returned empty. Triage data used.

### D4 — Verdict and COD assessment

**Verdict: real_active / operating**

Evidence cascade:
1. EIA-860M: Operating since 2022-12 (plant 65306) — strongest single signal
2. ERCOT: Approved for synchronization 2022-10-06; approved for energization 2022-09-19
3. 88 turbines in OSM tagged "Limestone Wind" — field-surveyed real infrastructure
4. ENGIE press release: "COD end-2022" with three named VPPA offtakers (LyondellBasell, Stanley Black & Decker, Whirlpool)
5. PUCT PGC registration 2022-03-30 → approved 2022-04-18 (just before energization/sync)
6. IA signed 2021-08-19, scheduled COD 2022-11-04 — achieved on schedule

**Queue COD 2026-07-01 is stale:** ERCOT GIS has no `approvedForCommercialOperation` date, which causes the queue entry to continue showing a COD. The 22 reported COD slips in the queue are pre-construction delays (original 2021-10-15 → final achieved ~2022-12), not post-sync stall.

**Independent COD: 2022-Q4** (most likely November–December 2022; EIA reports 2022-12; IA scheduled 2022-11-04).

**Drift risk: none** — project is already operating.

### Negative evidence log

| Source | Query/Attempt | Result |
|---|---|---|
| CDSE (Sentinel-2) | chip @ 31.85346,-96.62446 and 31.82707,-96.66834 | RemoteDisconnected — service outage |
| FAA OE/AAA | faa.py resolve 21INR0324 (Navarro Co) | No local cache hit; live blocked 2026-07 |
| search.py | 4 queries on Limestone Wind / ENGIE / COD | All backends failed |
| ENGIE website | engie-na.com/limestone/ | Imperva bot-block |
| ENGIE press release | engie-na.com/...650-mw... | Empty response |
| TX Comptroller | mycpa.cpa.state.tx.us | JS-only SPA; API 403 |
| TX SOS | SOSDirect | Interactive login required |
| Navarro CAD | parcel search by owner | Not attempted (JS-blocked in prior triage) |
| OSM Overpass (substation save) | Limestone Wind Substation way query | 504 Gateway Timeout on second query |
