# Dossier — Samson Solar 1 (21INR0221)

Researched 2026-07-19 · site 33.4640, -95.3510 · verdict **operating**

## 1. Verdict

- **operating** — satellite imagery shows fully installed solar panel arrays at site; ERCOT `approvedForSynchronization` 2021-08-31; site is Phase 3 of the operating [Samson Solar Energy Center](https://samsonsolarenergycenter.com) ([GEM Wiki](sources/2026-07-19_gem-wiki_samson-solar-energy.html))
- Construction: **operating** (site fully installed, ~4 years operational), first sync signal **2021-08-31** ([ERCOT queue](sources/timeline.md))
- Site: 33.4640, -95.3510 — GEM Wiki EIA-860 Phase 3 (Lamar County, 250 MW), cross-checked Infrasure EIA 63882 (1.04 km) ([satellite view](https://www.google.com/maps/@33.4640,-95.3510,5000m/data=!3m1!1e3))
- COD: reported 2026-09-30 → independent **~2022 (already operating)**, drift risk **low** (queue record not reconciled with actual commercial operation; ~4 years of operation not captured)

## 2. Site identification

- Derivation: GEM Wiki "Phase 3" coords (33.4640, -95.3510) from EIA-860 data; census-geocoder confirms Lamar County ([GEM](sources/2026-07-19_gem-wiki_samson-solar-energy.html))
- **Stated project area: ~1,500-2,000 acres (estimated)** — full project 11,000 acres / 1,310 MW × 250 MW; no signed IA or abatement with exact acreage retrieved ([project site](sources/2026-07-19_austinio_samson-solar-energy-center.html)) — imagery footprint broadly consistent
- Cross-checks: Infrasure EIA 63882 coords (33.468, -95.341) 1.04 km from GEM — same project area ([Infrasure](sources/2026-07-19_infrasure_samson-solar-ii.html)); imagery confirms dense solar panels across multiple z=14 tiles at both locations ([z14 tile](imagery/key/esri_z14_site_present.jpg), [z13 wide](imagery/key/esri_z13_phase3_wide.jpg))
- Not obtainable: exact FarmersVl/Moses 345kV substation coords (CEII); gate address; parcel IDs (CAD JS-only portal)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Samson Solar 1, LLC | SPV | ERCOT queue (IA party, signed 2020-08-26) |
| Invenergy LLC | developer/operator | [Nov 2020 PR](sources/2026-07-19_invenergy_samson-solar-announcement-2020.html); [GEM Wiki](sources/2026-07-19_gem-wiki_samson-solar-energy.html) |
| WEC Infrastructure LLC | co-investor in Phase 1 (Franklin Co) | [WEC 10-K 2025](sources/2026-07-19_sec_wec-energy-group-10k-2025.html): 90% of Samson I (250 MW Franklin), COD May 2022 |
| AT&T, Google, McDonald's, Honda, Home Depot | PPA offtakers (combined 1,010 MW across project) | [Invenergy PR](sources/2026-07-19_invenergy_samson-solar-announcement-2020.html) |

- Financing: non-recourse project; no Phase 3-specific financing announcement found. Full project = $1.6B capital investment ([Invenergy PR](sources/2026-07-19_invenergy_samson-solar-announcement-2020.html))

## 4. Land & county records

- Tenure: **leased** (implied) — Invenergy PR: "$250M in landowner payments over life of project"; no owned-land evidence; leased ranchland typical
- Abatements/agreements: **none found** — Ch.313 expired end-2022; JETI search negative; consistent with pre-JETI project vintage (IA 2020); no ISD agreement retrieved
- CAD: 0 parcels under Samson Solar / Samson Solar 1 LLC / Invenergy (CAD portal JS-only, no curl access; expect leased-land result anyway)

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "tap both 345kV 1685 FarmersVl - 1695 Moses ckts" (Lamar County, NORTH zone)
- Same POI shared with 21INR0491 (Samson Solar 3, 250 MW) — both phases tap the same FarmersVl-Moses 345kV circuits
- IA: signed 2020-08-26 per queue; PUCT Interchange portal blocked (HTTP 402) — IA PDF NOT RETRIEVED

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (Oncor / Samson Solar 1 LLC) | 2020-08-26 | Unknown — PUCT blocked |

| Milestone | IA schedule |
|---|---|
| IA signed | 2020-08-26 |
| Meets 6.9(1) | 2020-08-26 |
| Meets all 6.9 | 2020-10-15 |
| Approved for energization | 2021-06-30 |
| Approved for synchronization | **2021-08-31** |
| Commercial operation approved | **NEVER (queue artifact)** |

- Queue-history COD drift ([timeline.md](timeline.md)): **23 changes** — 2021-12-31 → 2026-09-30; project has been generating since ~2022; drifts reflect queue record not reconciled

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 (current) | Dense solar panels fully installed across multiple km; no bare ground | [z14 present](imagery/key/esri_z14_site_present.jpg) |
| 2026-07 wide | Multi-block solar complex visible, west extent confirmed | [z14 west](imagery/key/esri_z14_site_west.jpg) |
| 2026-07 z13 | Wide view: solar blocks NW portion, farmland SE | [z13 wide](imagery/key/esri_z13_phase3_wide.jpg) |

- Verdict: **operating** — panel arrays fully installed; visual consistent with 250 MW+ installation (multiple km footprint). Note: imagery is ESRI World Imagery tiles (undated); Sentinel-2 chips not available (CDSE credentials expired). No historical progression images retrieved.

## 7. COD assessment

- Reported 2026-09-30 is a **queue artifact** — the last in a sequence of 23 COD drifts over 5 years; the project reached commercial operation circa 2022 per GEM Wiki and WEC 10-K timelines
- ERCOT `approvedForSynchronization` date (2021-08-31) is the last recorded milestone; no `approvedForCommercialOperation` ever entered, which is anomalous for an operating plant
- All three Samson phases in Lamar County (21INR0221, 21INR0490, 21INR0491) share this pattern — none have formal COD in queue; systemic record-keeping issue, not a construction failure
- Satellite imagery confirms installed operating arrays at the referenced coordinates
- No construction-stage activity visible anywhere in the project area
- **Independent estimate: already operating since ~2022; reported COD 2026-09-30 is not a future event**

## 8. Could not determine

- Exact site coordinates for 21INR0221 vs 21INR0491 specifically (both 250 MW, same POI, same county, ~1 km from each other; may be adjacent sub-blocks)
- Exact gate/parcel address (gmaps rate-limited; CAD blocked)
- IA financial security amounts (PUCT Interchange blocked)
- Construction start date (not reported in ERCOT queue)
- WEC Energy investment stake in 21INR0221 specifically (WEC confirmed as investor in Phase 1 Franklin Co; Phase 3 Lamar Co ownership not confirmed separately)
- TX SOS entity details for Samson Solar 1, LLC (SOSDirect paywall; Comptroller JS-only)
