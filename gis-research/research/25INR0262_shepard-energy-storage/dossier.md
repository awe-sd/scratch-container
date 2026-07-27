# Dossier — Shepard Energy Storage (25INR0262)

Researched 2026-07-19 · site 29.512, -95.010 · verdict **real_early**

## 1. Verdict

- **real_early** — IA signed Jan 2024, FIS approved Mar 2026, financial security posted; project website live confirming <15 ac BESS adjacent to CenterPoint 138kV substation in Hidden Lakes area ([project website](sources/2026-07-19_shepardenergystorage.com_homepage.html))
- Construction: **no_activity** — no groundbreak detected in Sentinel-2 imagery through 2026-03; no construction start date in queue as of 2026-06-01
- Site: 29.512, -95.010 — Hidden Lakes subdivision, League City/Galveston County; triangulated from POI "#38900 Hidden Lakes - #42015 PHR 138 KV"; P.H. Robinson confirmed at 29.4878/-94.9826 ([OSM](https://www.openstreetmap.org/#map=14/29.5/-95.01))
- COD: reported 2027-07-01 → independent **2027-Q3 to 2028-Q1**, drift risk **med** (no groundbreak confirmed, ~2yr prior slip)

## 2. Site identification

- Derivation: POI text names ERCOT bus 38900 "Hidden Lakes" and bus 42015 "PHR 138 KV"; P.H. Robinson Switching Station (CenterPoint, 29.4878/-94.9826) anchors the eastern end; Hidden Lakes substation is ~4.5 km NW in the Hidden Lakes residential area, League City. Project website confirms "<15 acres directly next to an electrical substation and major electrical corridor" ([FAQ](sources/2026-07-19_shepardenergystorage.com_faqs.html))
- **Stated project area: <15 acres** per project website ([homepage](sources/2026-07-19_shepardenergystorage.com_homepage.html)) — compact BESS consistent with 256 MW; imagery footprint **unverified** (site not located at parcel level)
- Cross-checks: POI bus name "Hidden Lakes" → Hidden Lakes neighborhood, League City, Galveston County ✓ (all three sources agree); no OSM-named "Hidden Lakes Substation" found; ERCOT bus coordinate is CEII
- Not obtainable: exact substation parcel coordinates (ERCOT CEII), CAD parcel ID (esearch.galvestoncad.org endpoint down)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Shepard Energy Storage LLC | SPV | [TX SOS 0804803481](https://direct.sos.state.tx.us) |
| Vesper Energy Development LLC | Developer/owner | [project website](sources/2026-07-19_shepardenergystorage.com_homepage.html) |
| Magnetar Capital | PE owner (since 2020) | [vesperenergy.com/about](https://vesperenergy.com/about) |
| GCM Grosvenor | Equity co-owner (since 2023) | [vesperenergy.com/about](https://vesperenergy.com/about) |
| EPC contractor | unknown | — |
| Offtaker/PPA | unknown | — |

- Financing: Institutional-quality backer (Magnetar + GCM Grosvenor); no public financing announcement found

## 4. Land & county records

- Tenure: **leased** — "privately owned land" per project website; <15 acres
- Abatements/agreements: none found — Ch.312/313 program sunset 2023; BESS ineligible for JETI; absence expected
- CAD: 0 parcels found — esearch.galvestoncad.org owner-search endpoint returned 404; Galveston County commissioners court website inaccessible
- TCEQ: no facility permits — battery storage does not require NSR air permit; absence expected

## 5. Interconnection & contractual schedule

- POI per queue: `# 38900 Hidden Lakes - # 42015 PHR 138 KV` — 138kV tap between Hidden Lakes substation and P.H. Robinson Switching Station
- IA PDF: not retrieved — PUCT Interchange returns HTTP 402 on all endpoints
- Financial security: posted ("Yes" per queue as of 2026-06-01)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA | 2024-01-17 | Amount unknown — PDF not retrieved |

| Milestone | Queue record |
|---|---|
| IA signed | 2024-01-17 |
| Meets 6.9(1) | 2025-02-12 |
| FIS approved | 2026-03-19 |
| Meets all 6.9 | not achieved |
| Construction start | not reported |

- Queue-history COD drift (from [timeline.md](timeline.md)): 6 values, 2025-07-09 → 2027-07-01 (~2yr total slip); stable at 2027-07-01 since 2025-03-01 (16 months)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-03 | Dense suburban/residential League City; no BESS pad, no gravel clearing, no container rows anywhere near Hidden Lakes area | [6km wide](imagery/s2_2026-03-01.png) |
| 2026-03 | Tight chip around POI midpoint (29.494/-95.003): semi-rural fringe south of Hidden Lakes, minor earthwork in lower corner unrelated to BESS | [2km chip](imagery/s2_tight_phr_mid.png) |
| 2026-03 | Tight chip PHR vicinity (29.490/-94.985): highway corridor, no BESS pad | [2km chip](imagery/s2_tight_phr.png) |
| 2026-07 | Heavy cloud cover — not useful for site check | [6km wide](imagery/s2_2026-07-01.png) |

- Verdict: **no_activity** — no construction visible through 2026-03; cloud cover in July 2026 prevents confirmation for the most recent period. Site <15 ac — could be tucked immediately adjacent to substation outside searched area, but 6 chips found no signal

## 7. COD assessment

- All major contractual gates cleared: IA signed (Jan 2024), FIS approved (Mar 2026), financial security posted, 6.9(1) met (Feb 2025) — project is contractually committed
- **No construction start** as of the 2026-06-01 queue snapshot; 12-18 month BESS build means groundbreak no later than Q3-2026 is required to hit 2027-07-01
- Historical pattern: COD slipped ~2yr from original (2025-07 → 2027-07) across 6 changes; now stable 16 months — suggests developer confidence but not proven
- Developer is institutional (Magnetar Capital / GCM Grosvenor backed) — low abandonment risk, but construction delays remain possible
- Independent estimate: **2027-Q3** (optimistic, if groundbreak started Jul 2026) to **2028-Q1** (realistic, if groundbreak slips to Q4-2026)
- Risk factor: "Meets all 6.9" not yet achieved — this is required before commercial operation; adds residual uncertainty

## 8. Could not determine

- Exact site address / parcel ID (ERCOT bus 38900 coords are CEII; CAD portal down)
- IA PDF / contractual schedule exhibits / financial security amount (PUCT blocked)
- EPC contractor, battery OEM, offtaker/PPA
- Whether groundbreak has occurred post-2026-03 (July imagery clouded out)
- Galveston County building permit number
