# Dossier — Meitner Wind (26INR0113)

Researched 2026-07-18 · site 35.5800, -100.4800 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA + 4 amendments through 2026-05-28 with escalating shared-TIF security ($92.7M → $97.3M) and a fully-executed Gray County tax-abatement package (2025-10-31) for the co-located datacenter that anchors this wind project's off-take ([abatement](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf), [Wind IA Amend 4](sources/2026-07-18_puct_35077-2497_ctt-meitner-IA-amend4-5.pdf))
- Construction: **no_activity visible** in the S2 chips retrieved ([east-of-Laketon chip](imagery/s2_east_swyd_candidate.png)); TIF notice-to-proceed only issued 2026-01-28 per [Amend 3](sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf)
- Site: 35.5800, -100.4800 — IA POI text + abatement Exhibit B map, medium confidence ([map](https://www.google.com/maps/@35.58,-100.48,5000m/data=!3m1!1e3))
- COD: reported 2028-05-24 → independent **2028-Q3**, drift risk **medium** (2 prior slips; TIF barely started)

## 2. Site identification

- Derivation: IA Exhibit C p42 places the POI "in Gray County, near **Laketon, Texas**, at TSP's Ghost Town Substation"; Amend 4 Exhibit C-1 one-line diagram shows the Meitner Wind+Solar shared switchyard ~10 mi from Ghost Town Station, which sits on a new ~14 mi 345 kV double-circuit line to Gray Substation ([Orig IA](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf), [Amend 4](sources/2026-07-18_puct_35077-2497_ctt-meitner-IA-amend4-5.pdf))
- **Stated project area: 1,744.24 acres** (datacenter only) per abatement Exhibit A — 3 tracts (Section 118/142/143 Block M-2 BS&F, Property IDs 13519/13542/13548) ([abatement](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf)) — imagery footprint consistent? **unverified** (S2 shows only unaltered ranchland; TIF works too recent to see)
- Cross-checks: Laketon GNIS 35.5437,-100.6329 (OSM); Gray Sub 35.4078,-100.8199 (OSM ‑ LS Power); Gray-Sub → Laketon = 22 km = 13.7 mi (matches "~14 mi" IA line length); [datacenter Exhibit B aerial](imagery/exhibit_b_datacenter_map_full.png) shows a stepped L-shaped red tract just south of the Gray-Roberts county line (map's blue upper border = 35.6191°N) — all agree within ~10 km of the derived centroid
- Not obtainable: Ghost Town Substation coords (new-build, not in OSM); exact turbine coords (FAA OE portal on government shutdown); Gray CAD parcel geometry (portal HTTP 500 across 5 URL patterns)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Meitner Wind, LLC | SPV per queue | queue identity packet; signatures on 5 IA filings name IP Meitner as Generator, not a separate Wind LLC |
| IP Meitner, LLC (Delaware) | generator of record | party on all 5 [IA filings](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf) + [abatement](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf); mailing 120 W Kingsmill Ave Ste 120, Pampa TX 79065 |
| Intersect Power | developer/parent | signatory Simon Ross (IP Meitner CCO) on all Wind IA amendments + datacenter abatement; operational contact via intersectpower.com email + Beaverton OR HQ ([Orig IA Ex D](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf)); [newprojectmedia coverage](sources/newprojectmedia_data_center_pivot.md) |
| Google (Alphabet) | acquirer of Intersect | acquisition announced 2025-12-22, closed 2026-03 (per intersect.com pipeline redirect + industry press) |
| Cross Texas Transmission LLC (LS Power) | TSP | party on all 5 IA filings; LS Power address on Amend 4 cover letter |

- Financing: no separate financing announcement located for Meitner Wind; the shared-TIF Security ($97.3M) is IA-required and posted per Meitner Solar schedule ([Amend 3 Ex E](sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf)). Google acquisition puts Alphabet balance-sheet behind development.

## 4. Land & county records

- Tenure: **mixed purchased/leased/easement** — [abatement recital](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf) defines "Real Estate Rights" as "ownership, lease, and/or easement rights or options"; Wind IA Amend 3 records substation-parcel deed conveyance target 2026-06-01 and Transmission-Line ROW target 2026-11-01 ([Amend 3 Ex B](sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf))
- Abatements/agreements: [Gray County Tax Abatement (Ch.312) — Data Center](sources/2026-07-18_gray-county_tax-abatement-ip-meitner.pdf) executed 2025-10-31; Meitner Reinvestment Zone designated 2023-11-15; 10-yr abatement per phase; Phase-1 Commencement Date deadline **2029-01-01** (one extension to 2030); construction start goal **2026-04-01**, completion goal **2028-12-31**; Phase 1 ~$1B, total ~$3B; supersedes 2024-03-07 hydrogen abatement. Also [Road Use / Fire Safety Training Agreement](sources/2026-07-18_gray-county_road-use-ip-meitner.pdf) executed 2025-10-31.
- CAD: esearch.graycad.org returned HTTP 500 for all endpoints; parcel geometry could not be pulled. Property IDs 13519/13542/13548 recorded from abatement Exhibit A for later lookup.

## 5. Interconnection & contractual schedule

- POI per signed IA: "in Gray County, near Laketon, Texas, at TSP's Ghost Town Substation ... 345 kV" ([Orig IA p42](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf), consistent across all amendments)
- Equipment (Orig IA Exhibit C): 186 × Vestas V163 4.5 MW = 836.5 MW nameplate (queue dropped to 709 MW in 2025-03 — ~28 turbines removed). Shared 345/34.5 kV project switchyard co-locates Meitner Wind + [Meitner Solar 25INR0080]; export via new 14-mi 345 kV double-circuit line CTT builds from Ghost Town to Gray Substation. Amend 2 (2025-06-12) adds 840 MW BTM Large Load; Amend 4 (2026-05-28) adds Phase 2 420 MW BTM.

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-18_puct_35077-1825_ctt-meitner-wind-IA.pdf)) | 2024-04-19 | $92.7M total required (shared-TIF, borne by Meitner Solar IA) |
| Amendment 1 ([pdf](sources/2026-07-18_puct_35077-2061_ctt-meitner-wind-IA-amend1.pdf)) | 2025-02-04 | raised to **$97.3M** total; 6-tranche schedule ending 2026-05-27 |
| Amendment 2 ([pdf](sources/2026-07-18_puct_35077-2179_ctt-meitner-wind-IA-amend2.pdf)) | 2025-06-12 | $97.3M unchanged; Large Load 840 MW BTM added |
| Amendment 3 ([pdf](sources/2026-07-18_puct_35077-2406_ctt-meitner-wind-IA-amend3.pdf)) | 2026-01-30 | $97.3M restructured to 9 installments ending **2026-08-31**; clause 4 deems all pre-Amend-3 milestones satisfied |
| Amendments 4 & 5 ([pdf](sources/2026-07-18_puct_35077-2497_ctt-meitner-IA-amend4-5.pdf)) | 2026-05-28 | $97.3M; Phase 2 420 MW BTM added; Security Effective Date fixed to 2024-02-14 |

| Milestone | Orig 2024 | Amend 1 2025 | Amend 3 2026 | Amend 4 2026 |
|---|---|---|---|---|
| In-Service | 2026-12-30 | 2027-04-30 | 2027-10-26 | 2027-10-26 |
| Trial Operation | 2027-01-30 | 2027-05-30 | 2027-11-26 | 2027-11-26 |
| Scheduled COD | 2027-12-30 | 2028-04-30 | 2028-04-30 | 2028-04-30 |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2026-09-17 → 2027-12-20 → 2028-05-24 (across 36 monthly snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-05 | Laketon anchor: unaltered ranch/farm, center-pivot ag, no substation earthworks | [png](imagery/s2_laketon_present.png) |
| 2026-07-05 | East-of-Laketon (35.55,-100.48): pivot cluster matches abatement Exhibit B texture, no visible construction | [png](imagery/s2_east_swyd_candidate.png) |
| 2026-07-05 | South of Laketon (35.45,-100.55): pure rangeland, no activity | [png](imagery/s2_gray_south.png) |
| — | Abatement Exhibit B aerial (undated, ≤2025): red L-shape datacenter tract inside dark-hatched Reinvestment Zone just S of the Gray-Roberts county line | [map](imagery/exhibit_b_datacenter_map_full.png) |

- Verdict: **no_activity visible** — TIF notice-to-proceed only 2026-01-28 (Amend 3); Ghost Town Substation not yet in OSM; V163 pads (~50 m) at 10 m/px are at the visibility floor. CDSE credentials invalidated after 3 chips prevented running the full contact-sheet grid or a monthly timelapse — this verdict is bounded to the three chips actually retrieved and could be updated when tooling recovers.

## 7. COD assessment

- Reported 2028-05-24 pads the **contractual Scheduled COD of 2028-04-30** by ~1 month — grounded but grounded ≠ achievable
- 4 IA amendments in 25 months (Orig COD 2027-12-30 → 2028-04-30 held through Amends 1-4); queue-history drift 2 additional times → project has already re-anchored ~5 months and shows a pattern of 4-9 month slips
- TIF critical path is barely started: Ghost Town substation is a new-build with parcel deed only due 2026-06-01, transmission-line ROW deed only due 2026-11-01, and no visible earthworks in July-2026 Sentinel-2 — the ~28 months to COD is tight against typical wind-farm timelines (12-18 mo civil + electrical + testing after major TIF completion)
- Datacenter drives the wind: Amend 2 adds 840 MW BTM Large Load ISD 2027-10-26; Amend 4 adds Phase 2 420 MW ISD 2028-10-01. Datacenter abatement construction-start goal 2026-04-01 and completion goal 2028-12-31 are aligned; Phase 1 abatement Commencement Date deadline 2029-01-01 leaves ~4 months slack past the Wind COD. If DC Phase 1 slips past that deadline, Wind loses its BTM load rationale and could revise capacity again.
- Positive signals: $97.3M shared-TIF security escalating on schedule ($15.6M target 2025-09-02 → $43.9M 2026-01-31 → $97.3M 2026-08-31); Google acquisition of Intersect Power (Dec-2025 / Mar-2026 close) puts Alphabet balance-sheet behind the campus; abatement + Road Use agreement executed 2025-10-31; 4 IA amendments show active TSP-Generator coordination, not paper-project neglect.
- **Independent estimate: 2028-Q3, drift risk medium** (contractual 2028-04-30 + typical +3-4 month slip on a wind project not-yet-under-construction).

## 8. Could not determine

- Exact Ghost Town Substation lat/lon (new-build, absent from OSM; CEII redacted in filings)
- Exact turbine positions and their bounding polygon (FAA OE portal on shutdown; no public developer map of Meitner Wind layout)
- Gray CAD parcel geometry (esearch.graycad.org HTTP 500 across every URL pattern tried)
- Whether V163 count is now 157 or has been adjusted again since Amend 4 (the 709 MW / 4.5 MW math points to 157.5)
- Independent confirmation of Intersect Power → Google closing status past Bing snippet
