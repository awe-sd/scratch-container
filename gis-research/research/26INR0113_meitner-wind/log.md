# Deep research log — 26INR0113 Meitner Wind

## Triage carryover
- 36 snapshots (2023-07 → 2026-06). IA signed 2024-04-19; FIS not achieved; no construction milestones.
- Capacity 836.5 → 709 MW (2025-03). COD drifted 2× (2026-09-17 → 2027-12-20 → 2028-05-24).
- Developer: **Intersect Power / IP Meitner, LLC** (Delaware LLC, Pampa TX office).
- Meitner Wind + Meitner Solar share 345/34.5 kV substation; export via new ~14-mi 345 kV
  double-circuit line to Gray Substation (LS Power). Data-center pivot: up to 840 MW BTM.
- Triage site candidate: east of Pampa (~35.54°N, -100.90°W, low confidence).

## Deep-scan findings (2026-07-18)

### FAA OE/AAA
- FAA OE portal on GOVERNMENT SHUTDOWN — search endpoint returns admin banner only, no
  structure data. Wind turbine coords not retrievable this run. Negative evidence logged.

### PUCT Interchange — 10 filings under Control No. 35077
- Meitner Wind + Meitner Solar IAs share **Cross Texas Transmission LLC**'s standing informational
  docket (Subst. R. §25.195(e)). CTT = LS Power grid company. Search
  `FilingDescription=Meitner` → 10 filings, retrieved all 5 Wind PDFs:
  - **Original IA** filed 2024-05-17 (item 1825, executed **2024-04-19**), 58 pp
    → [sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf).
  - **Amend 1** filed 2025-02-05 (item 2061, executed **2025-02-04**)
    → [sources/2026-07-18_puct_35077-2061_ctt-meitner-wind-IA-amend1.pdf](sources/2026-07-18_puct_35077-2061_ctt-meitner-wind-IA-amend1.pdf).
  - **Amend 2** filed 2025-07-02 (item 2179, executed **2025-06-12**) — adds Large Load 840 MW BTM
    → [sources/2026-07-18_puct_35077-2179_ctt-meitner-wind-IA-amend2.pdf](sources/2026-07-18_puct_35077-2179_ctt-meitner-wind-IA-amend2.pdf).
  - **Amend 3** filed 2026-02-11 (item 2406, executed **2026-01-30**)
    → [sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf](sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf).
  - **Amend 4 & 5** filed 2026-06-04 (item 2497, executed **2026-05-28**) — adds Phase 2 420 MW
    → [sources/2026-07-18_puct_35077-2497_ctt-meitner-IA-amend4-5.pdf](sources/2026-07-18_puct_35077-2497_ctt-meitner-IA-amend4-5.pdf).
- Also on the docket (Solar side, not downloaded to save budget): items 1754, 2060, 2180, 2407 —
  same amendment cadence for IP Meitner Solar (25INR0080).

### POI & equipment (Original IA pp 41-51)
- **POI**: "in Gray County, near **Laketon, Texas**, at TSP's Ghost Town Substation" — new
  345 kV CTT switchyard. Meitner Wind + Solar shared substation is ~10 mi from Ghost Town per
  Amend 4/5 Exhibit C-1 One-Line Diagram. Ghost Town connects to existing Gray Substation
  (35.408, -100.820) via new ~14-mi bundled double-circuit 345 kV line.
- **Turbines**: 186 × **Vestas V163 4.5 MW** = 836.5 MW nameplate (matches 2023-07→2025-02
  queue snapshots). Capacity 836.5 → 709 MW in 2025-03 = removal of ~28 turbines (~157 units
  remaining). Turbine downsizing coincides with data-center Large Load addition and shared
  substation optimization.
- **Interconnection Option 4.1.A** (TSP-designed and constructed TIF).

### Contractual schedule progression (Exhibit B, all filings)
| Doc | Signed | In-Service | Trial | COD | Large Load ISD |
|---|---|---|---|---|---|
| Orig IA | 2024-04-19 | 2026-12-30 | 2027-01-30 | 2027-12-30 | — |
| Amend 1 | 2025-02-04 | 2027-04-30 | 2027-05-30 | 2028-04-30 | — |
| Amend 2 | 2025-06-12 | (unchanged) | (unchanged) | (unchanged) | 2027-10-26 |
| Amend 3 | 2026-01-30 | 2027-10-26 | 2027-11-26 | 2028-04-30 | 2027-10-26 |
| Amend 4 | 2026-05-28 | 2027-10-26 | 2027-11-26 | 2028-04-30 | Ph1 2027-10-26, Ph2 2028-10-01 |
- Reported queue COD 2028-05-24 tracks IA COD 2028-04-30 (~1 mo pad).
- Amend 3 clause 4: "All deadlines set forth in Exhibits B and E that pre-date the effective date
  of this Third Amendment are deemed to have been satisfied" — meaning by 2026-01-30 the
  Generator had cleared the 2025-04-30, 2025-09-01, 2026-01-10 milestones (site drawings,
  notice to proceed, substation parcel deed).
- Amend 4 clause 3 (2026-05-28): substation parcel deed already conveyed; TX ROW target 2026-11-01;
  new notice-to-proceed 2026-01-28 (retro).

### Financial security (Exhibit E)
- IA-required Security total: **$92.7M → $97.3M** (Amend 1 raised it). Wind-side security is borne
  by the Solar IA (shared TIF); Wind requires no separate security unless Solar defaults.
- Solar-side schedule (mirrored in Wind Amend 3 Exhibit E for cure-triggered assumption):
  $1.7M (2024-02-14) → $2.9M (2024-05-15) → $4.25M (2025-01-31) → $5.6M (2025-04-30) →
  $8.1M (2025-07-21) → $15.6M (2025-09-02) → $43.9M (2026-01-31) → $51.4M (2026-07-01) →
  **$97.3M (2026-08-31)**. Monotonic escalation through mid-2025 aligns with amendments —
  money is moving.

### Gray County tax abatement (executed **2025-10-31**)
Sources:
- [Tax Abatement Agreement — Data Center](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf) — 29 pp scan.
- [Road Use, Local Plans & Fire Safety Agreement](sources/2026-07-18_gray-county_road-use-ip-meitner.pdf) — 13 pp scan.
- [Notice of Meeting — 2025-08-01 public hearing](sources/2026-07-18_gray-county_notice-datacenter-abatement-2025-09.pdf).

Facts (from p-image reads):
- Reinvestment Zone designated **2023-11-15** by Gray County Commissioners' Court under
  Chapter 312.
- Property (Exhibit A, abate p 21): **3 tracts = 1,744.24 total ac** in Block M-2, BS&F Survey:
  - Parcel 1: **480.0 ac**, Section 118 (S/2 + NW/4), Property ID **13519**.
  - Parcel 2: **624.24 ac**, Section 142, Property ID **13542**.
  - Parcel 3: **638.0 ac**, Section 143, Property ID **13548**.
- Improvements: up to 3 phases of datacenter buildings (Phase 1 ~$1B, ~$3B total).
- Phase 1 abatement expires 10 yrs from Commencement Date; Commencement Date for Phase 1
  must occur **by January 1, 2029** (one-time extension to 2030 with County approval).
- **Construction start goal: on or before April 1, 2026. Completion goal: December 31, 2028.**
- Prior 2024-03-07 Hydrogen Abatement is terminated upon execution of all three phases.
- Executed by IP Meitner CCO **Simon Ross** (2025-10-31) + County Judge **Chris Porter** &
  four commissioners (2025-10-27). Notary/clerk **Dee Dee Laramore**.
- IP Meitner registered address: **120 W Kingsmill Ave, Suite 120, Pampa, TX 79065**.

Exhibit B (map, abate p 22, saved as
[imagery/exhibit_b_datacenter_map_full.png](imagery/exhibit_b_datacenter_map_full.png)):
- Aerial with data-center project boundary (red L-shape), Reinvestment Zone (dark hatched),
  Gray County N boundary (blue line at top = ~35.6191°N / Gray-Roberts line).
- Scale bar reads "1.25" (miles); the Reinvestment Zone spans ~5-8 mi east-west.
- Terrain: center-pivot irrigated farms south/central, canyon-cut ranchland north near county line.
- The red datacenter tract sits ~mid-map, just south of the Gray-Roberts line.

### Gray CAD portal
- esearch.graycad.org returning HTTP 500 for all property URLs (Property/View, PropertyDetail,
  print, map). Site is down or the endpoint has moved. Property lookups by ID (13519/13542/13548)
  not retrievable. Legal descriptions in the tax abatement (Section 118/142/143 of Block M-2 BS&F
  Survey) are the working ground truth.

### Site pinpoint
- Ghost Town Substation is being built by CTT — NOT yet in OSM. Nearest known 345 kV substations
  (OSM): **Gray Substation (LS Power) 35.4078, -100.8199** (existing) and **Miami Wind Substation
  (Invenergy) 35.6202, -100.5414** (Roberts County, ~3 mi north of Gray line).
- POI text: "near Laketon TX". Laketon GNIS = **35.5437, -100.6329** (OSM Nominatim).
- Gray-Sub → Laketon ≈ 22 km ≈ 13.7 mi (matches "~14 mile" line in one-line diagram).
- Datacenter Property (from Exhibit B) sits ~just south of Gray-Roberts county line (35.62°N).
  Section 118/142/143 of Block M-2 BS&F Survey. Based on the map's characteristic pivot pattern
  in the lower-center and the position of the red L-shape ~5 mi south of the county line, the
  datacenter site is roughly at **35.58°N, -100.48°W** (Gray County NE corner, near
  Grandview / county line east of Miami TX).
- **Wind field extent**: 186→157 Vestas V163 (163 m rotor, ~4.5-6D spacing = ~800 m minimum)
  spans well beyond the Reinvestment Zone. Wind pads likely extend south + west of the
  datacenter across ~15-25 km of Gray County.

### Sentinel-2 imagery attempts (T7)
- Chip 1 at Laketon anchor 35.5437, -100.6329 (2026-07-05, 6 km buffer, cloud≤25%) →
  [imagery/s2_laketon_present.png](imagery/s2_laketon_present.png). Ag/ranchland, N-S road grid,
  center-pivot circles NW; ~SE has rugged breaks. NO turbine pads or substation construction
  visible — the site is elsewhere, or Ghost Town is unbuilt.
- Chip 2 at east-of-Laketon switchyard candidate 35.55, -100.48 (2026-07-05) →
  [imagery/s2_east_swyd_candidate.png](imagery/s2_east_swyd_candidate.png). Center-pivot cluster
  in the middle-right (matches the pivot pattern in Exhibit B), rugged canyons SW, small settlement
  visible right-center. Consistent with the datacenter area but no visible construction footprint
  yet.
- Chip 3 at 35.45, -100.55 (S of Laketon) → [imagery/s2_gray_south.png](imagery/s2_gray_south.png).
  Rugged rangeland, sparse pivots. Unlikely to host turbines here at this density.
- CDSE credentials then invalidated (HTTP 403 on token refresh) — further chips blocked. Google
  Places API 429'd across 4+ retries; Static Map API 403 (not enabled on key).
- **Present-first verdict**: **no_activity visible from S2**. No pad-scale features, no substation
  earthworks, no widened access roads. The Amend 3 milestone list says substation parcel
  deed was to be conveyed by 2026-06-01 and the notice-to-proceed given 2026-01-28 — so the
  TIF (Ghost Town) is only weeks-old in the ground, and Vestas V163 pads (~50 m ≈ 5 px at 10 m
  resolution) are below or at the visibility threshold. Expected: physical works begin H2-2026.

### Ownership chain (from IA + abatement)
- **Meitner Wind, LLC → IP Meitner, LLC → Intersect Power → Google (per Bing snippet
  2025-12-22 announcement, closed 2026-03).** IP Meitner is Delaware LLC. Contact person on
  IA Exhibit D: **Christian Fiene**, christian@intersectpower.com,
  9450 SW Gemini Dr PMB #68743, Beaverton OR 97008 (Intersect Power HQ).
- Signatory CCO **Simon Ross** on Wind IA amendments + datacenter abatement.
- Cross Texas Transmission LLC (an LS Power Grid company) = TSP.

### Missing / could-not-determine
- Exact FAA-verified turbine coordinates (portal on shutdown).
- Exact Ghost Town Substation lat/lon (new-build, not in OSM).
- Precise wind-field extent — the 3-tract abatement covers only the datacenter, not the wind
  layout; there's no public map of Meitner Wind turbine positions.
- Gray CAD parcel geometry lookup (portal HTTP 500).
