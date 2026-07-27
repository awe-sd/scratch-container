# Dossier — Cradle Solar (23INR0150)

Researched 2026-07-20 (refresh) · site 29.28494, -95.43309 · verdict **real_active**

## 1. Verdict

- **real_active** — countersigned SGIA with $21.2M security ([IA](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interconnection-agreem.pdf)); ACTIVE construction-stormwater NOI filed 2024-10-03 naming EPC PCL Solar Constructors USA Inc. at the project site (TCEQ Central Registry, facility RN112058680, queried 2026-07-20) — the single strongest "dirt is moving" signal
- Construction: **construction_started_per_regulatory_filing**, first regulatory evidence **2024-10-03**; NOT visually confirmed — a ~6x6km satellite search around the site pin/POI (Mar 2026) shows no large-scale grading/racking yet (see §6)
- Site: 29.28494, -95.43309 — Google Places pin "Cradle Solar Plant", high confidence on identity, unconfirmed on exact array footprint ([satellite view](https://www.google.com/maps/@29.28494,-95.43309,5000m/data=!3m1!1e3))
- COD: reported 2027-09-17 → independent **2027-Q4**, drift risk **medium** (two independent self-reported sources — queue and EIA — now cluster in 2027; no IA amendment yet files the new date)

## 2. Site identification

- Derivation: Google Places pin "Cradle Solar Plant" (7HM8+XQ, Angleton TX 77515); TCEQ stormwater NOI site description "1 mile off of Highway 48 and left into frontage rd" matches County Road 48, Angleton TX 77515 — same ZIP, independent corroboration of the pin's neighborhood ([TCEQ query result, see log.md](log.md))
- **Stated project area: 1,600 acres** per the developer's own project website ([cradlesolartx.com](sources/2026-07-20_cradlesolartx_official-site.html)) — imagery footprint **not verified**: no matching graded polygon located within the searched window (see §6)
- Cross-checks: Places pin (29.28494,-95.43309) ↔ IA Exhibit C POI structure coords (29.29293,-95.41503) agree within 1.6 km ([Exhibit C](sources/ia_exhibit_c_coords_p46.png)); TCEQ NOI address ↔ Places pin ZIP agree
- Not obtainable: exact parcel boundary/acreage from CAD (Brazoria CAD's search portal is JS-rendered, not fetchable headlessly; consistent with leased land not appearing under the SPV name anyway); satellite confirmation of the array footprint itself

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Cradle Solar, LLC | SPV (IA party) | [SGIA](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interconnection-agreem.pdf); 6688 N Central Expy Ste 500 Dallas TX |
| Cradle Solar Energy, LLC | SPV (per developer site — name variant, same project) | [cradlesolartx.com](sources/2026-07-20_cradlesolartx_official-site.html) |
| Leeward Renewable Energy (LRE) | developer/owner, portfolio co. of OMERS Infrastructure | [cradlesolartx.com](sources/2026-07-20_cradlesolartx_official-site.html); [LRE project page](sources/2026-07-20_lreus_cradle-solar-project-page.html); email domain @LeewardEnergy.com on [IA Exhibit D](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interco_p55.png) |
| PCL Solar Constructors USA Inc. | EPC | owner/customer of record on TCEQ stormwater NOI RN112058680 (queried 2026-07-20) |
| Microsoft Corporation | PPA offtaker (~200 MW) | [PPA summary](sources/leeward_microsoft_ppa_summary.md) (~March 2024) |

- Financing: not confirmed closed via press release; Microsoft PPA (~Mar 2024) provides offtake foundation; $21.2M security posted to CenterPoint ([IA Exhibit E](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interco_p56.png))

## 4. Land & county records

- Tenure: **leased** — IA references "existing land lease with fee owner(s)" and TSP reimbursing generator for acquired land rights ([IA p52](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interco_p52.png))
- Abatements/agreements: none found — expected; Ch.313 closed to new applications Dec 2022, no JETI filing found
- CAD: not queried this refresh — Brazoria CAD's `esearch.brazoriacad.org` portal is JS-driven and does not return results to a headless fetch; expected 0 hits under the SPV name regardless, given leased tenure (per the Hanson Solar precedent)

## 5. Interconnection & contractual schedule

- POI per signed IA: "tap 345kV 42500 Dow - 43035 Oasis ckt 18"; SPEEDWAY Substation (TSP side); CRADLE Substation (customer-owned); 29°17'34.5606"N 95°24'54.1152"W ([Exhibit C](sources/ia_exhibit_c_coords_p46.png))
- Equipment (Exhibit C): 310 TMEIC PVU-L0840GR inverters (62 groups × 5, each with a 4.2 MVA step-up transformer); 225 MW planned terminal capacity

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-20_puct_35077-1580_ercot-standard-generation-interconnection-agreem.pdf)) | 2023-03-15 | $21,237,000 (LC or cash, Exhibit E) |

(No amendment exists in docket 35077 as of this refresh — `puct.py match` returns only the original filing.)

| Milestone | Original IA (2023) |
|---|---|
| Scheduled Start Date | 2023-03-30 |
| TIF In-Service | 2024-10-02 (or 18 mo after start) |
| Scheduled COD | 2025-01-02 (or 3 mo after TIF IS) |

- Queue-history COD drift ([timeline.md](timeline.md)): **4 changes** — 2023-08-31 → 2025-01-02 → 2025-12-31 → 2027-02-22 → 2027-09-17; 33 months past the original contractual COD, **not yet reflected in a signed IA amendment**

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-03-16 | Pin-area quiet — farmland/rural residential, no grading | [3km](imagery/s2_jan2025_3km.png) |
| 2026-03-13/18 | Pin area visually unchanged from 2025-03; wide 6km view shows no large graded polygon near pin/POI | [3km](imagery/s2_jan2026_3km.png), [6km wide](imagery/s2_wide6km_2026-03.png) |
| 2026-03-21 | 3x3 grid (2km chips) spanning the pin-to-POI corridor: subdivisions, tilled farmland, ranchland — no racking/grading signature anywhere in the ~6x6km window | [grid contact sheet](imagery/grid_contact_sheet.png) |
| 2026-05-29 | Tight 2km chip at pin: still quiet | [2km](imagery/s2_tight_lowcloud.png) |

- Verdict: **no_visible_activity_in_searched_window** — at 10 m/px, no grading/racking found around the Places pin or IA POI as of March 2026, despite an ACTIVE TCEQ construction-stormwater permit since Oct 2024. Two explanations not distinguished this session: (a) early sitework (access roads, clearing) too subtle for 10 m/px, or (b) the true ~1,600-acre footprint sits outside the searched 6x6km box. CDSE fleet contention (shared with other concurrent research agents) blocked further chips/timelapse this session — see log.md.

## 7. COD assessment

- TCEQ's active, dated, EPC-named stormwater permit is stronger evidence of "real, construction underway" than a satellite read; it is regulatory paper filed specifically because dirt-disturbing work is imminent or underway
- EIA-860M's own planned-COD (plant 65822, Cradle Solar / Infigen Asset Management LLC — corrected from a prior false bind to an unrelated plant) has independently slipped to **2027-05**, four months ahead of the queue's 2027-09-17 — two independently self-reported sources now roughly agree on a 2027 COD, which is meaningfully more grounded than either alone
- The 33-month slip from the original contractual COD (2025-01-02) is NOT yet re-papered in a signed IA amendment — the 2027-09-17 figure is a self-reported queue update, not a countersigned date
- The developer's own public site (cradlesolartx.com) shows a "Targeted Operational" year of 2026 — a full year ahead of both the queue and EIA dates — an unreconciled internal inconsistency, treated as marketing optimism rather than governing evidence
- Risk: no visual construction confirmation this session (imagery search inconclusive, not negative); EIA status history shows the plant regressing from "under construction" back to "not under construction" for 16 months (Dec 2024-Apr 2026) before vanishing from the newest snapshot — a genuinely ambiguous signal only resolved in Cradle's favor by the TCEQ permit
- **Independent estimate: 2027-Q4**, drift risk **medium** — grounded in the EIA/queue convergence around 2027, but unconfirmed by imagery and with a documented pattern of serial slips

## 8. Could not determine

- Satellite confirmation of the actual construction footprint (searched 6x6km window came up empty; footprint may be outside it, or too early-stage to read at 10m/px)
- Exact parcel IDs/acreage from Brazoria CAD (portal not fetchable headlessly)
- Financing-close date/press release
- Whether "Cradle Solar, LLC" (IA party) and "Cradle Solar Energy, LLC" (developer-site name) are the same legal entity or a renamed/restructured successor
- Reconciliation of the developer site's "2026 Targeted Operational" claim against the queue's 2027-09-17 and EIA's 2027-05 dates
- EIA-860M's reason for regressing Cradle Solar's status backward for 16 months, and for dropping the plant from the 2026-05 snapshot, while a TCEQ construction permit stayed active throughout
