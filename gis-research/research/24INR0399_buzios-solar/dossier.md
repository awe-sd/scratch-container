# Dossier — Buzios Solar (24INR0399)

Researched 2026-07-22 · site 33.87751, -100.8902 · verdict **real_active**

## 1. Verdict

- **real_active** — site is already built and operating: satellite footprint exactly shape-matches the [Ch313 boundary map](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app_p25.png); EIA-860M reports the plant (OP) Operating since 2025-10
- Construction: **operating**, first activity bracketed **2025-01 to 2025-04** ([2025-04 frame](imagery/key/s2_2025-04-21.png))
- Site: 33.87751, -100.8902 — EIA-860M coords cross-validated by Google Places pin + Ch313 map shape-match, high confidence ([satellite view](https://www.google.com/maps/@33.87751,-100.8902,5000m/data=!3m1!1e3))
- COD: reported 2026-04-30 → independent **2025-Q4** (commercial operation already achieved), drift risk **low** (favorable/ahead-of-claim, not a slip)

## 2. Site identification

- Derivation: EIA-860M plant 68458 coordinates (33.877514,-100.8902) matched a Google Places delivery pin "Stafford Solar, 256 Co Rd 316, Roaring Springs, TX" ~150m away ([gmaps.py places](imagery/key/s2_2026-07-20.png)); wide satellite chip confirms a complete solar array at this location whose boundary shape matches the [Ch313 Tab 11 project map](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app_p25.png) exactly (notched SE corner in both)
- Project area: acreage not explicitly stated in any document found (Ch313 Tab 9 "Description of Land: Not Applicable" — leased land, no CAD listing); imagery footprint (~1.5km × 2km) is consistent with a 250 MW/AC array
- Cross-checks (all agree): EIA coords ↔ Places pin (150m) ↔ Ch313 boundary-map shape ↔ IA POI text "Wrangler Switch...Cottonwood to White River 345 kV line" in Motley County ([IA](sources/2026-07-22_puct_35077-1709_generation-interconnection-agreement-between-onc.pdf) p32) ↔ Ch313 vicinity map places it south of FM 684, Motley County ISD
- Not obtainable: exact Wrangler Switch substation coordinates (no separate Places pin; not in any downloaded exhibit)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Roaring Springs Solar, LLC (f/k/a Stetson Renewables Holdings, LLC) | SPV | party on [IA](sources/2026-07-22_puct_35077-1709_generation-interconnection-agreement-between-onc.pdf); [Ch313 App #1892](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app.pdf) filed as Stetson, renamed per [Amendment 1](sources/2026-07-22_comptroller_ch313_1892-motley-roaring-amendagmt1.pdf) |
| NextEra Energy Resources Development, LLC | developer/parent | Ch313 application Tab 4/7/8: "Stetson Renewables Holdings, LLC is being developed by NextEra Energy Resources Development, LLC" ([app](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app.pdf) p16) |
| Stafford Solar, LLC | EIA-860M reporting entity, same physical plant | plant 68458, same coords as project site (name lineage to Stetson/Roaring Springs not directly documented, tied by coordinates only) |

- Financing: not found in any document reviewed — no PR/financing announcement surfaced; project appears financed and built without a public financing press cycle (typical for a large-utility developer like NextEra funding from balance sheet)

## 4. Land & county records

- Tenure: **leased** — Ch313 application Tab 9 "Description of Land: Not Applicable" ([app](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app.pdf) p21), same pattern as other leased-ranchland solar projects
- Ch313 agreement with Motley County ISD, applied 2022-05-05 as Stetson Renewables Holdings, LLC ([app](sources/2026-07-22_comptroller_ch313_1892-motley-stetson-app.pdf)); Amendment No. 1 (2024-04-08) renamed the Applicant to Roaring Springs Solar, LLC and set Guaranteed Minimum Tax Value schedule $187.5M (2026) declining to $44.2M (2035) ([amendment](sources/2026-07-22_comptroller_ch313_1892-motley-roaring-amendagmt1.pdf))
- Estimated total investment $250,000,000 (application Schedule, tax years 2022-2023)
- Ch312: no hit (weak negative, CAD-submission gaps expected). CAD: no parcel search run (leased land, no owner-name lead pursued)
- Motley County commissioners-court minutes: harvested 7 PDFs (4 image-only, 3 text-extractable) via `minutes.py`; 0 mentions of "Buzios"/"Roaring Springs" in extractable text — weak negative, most of the record is scanned images

## 5. Interconnection & contractual schedule

- POI per signed IA: "The Point of Interconnection is located in Motley County, Texas, at the Wrangler Switch in TSP's Cottonwood to White River 345 kV line" ([IA](sources/2026-07-22_puct_35077-1709_generation-interconnection-agreement-between-onc.pdf) Exhibit C, p32) — matches queue POI exactly
- Equipment (Exhibit C, amended by Amendment 2): 36×3.55 MVA + 37×4.20 MVA Power Electronics solar inverters, 283.2 MVA nameplate, dispatched to deliver 250 MW ([Amend 2](sources/2026-07-22_puct_35077-2122_amendment-no-2-to-the-standard-generation-interc.pdf))

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-22_puct_35077-1709_generation-interconnection-agreement-between-onc.pdf)) | 2023-11-06 | $13,765,151 irrevocable LC, effective 2023-11-08 |
| Amendment 1 ([pdf](sources/2026-07-22_puct_35077-1794_amendment-no-1-to-the-generation-interconnection.pdf)) | 2024-03-19 | unchanged — $13,765,151 |
| Amendment 2 ([pdf](sources/2026-07-22_puct_35077-2122_amendment-no-2-to-the-standard-generation-interc.pdf)) | 2025-04-22 | unchanged — $13,765,151 |

| Milestone | Original IA 2023 | Amendment 2 2025 |
|---|---|---|
| In-Service | 2025-05-08 | 2025-05-16 |
| Trial Operation | 2025-09-10 | 2025-10-01 |
| Scheduled COD | 2026-06-30 | 2026-06-30 (unchanged) |

- Queue-history COD drift ([timeline.md](timeline.md)): 6 reported-COD changes across 47 snapshots since 2022-08; longest hold was 2026-06-30 (2023-09 → 2025-06, matching the IA), then dropped to 2026-01-30 and finally the current 2026-04-30 — the 2026-06-01 snapshot had not yet caught up to the project's real-world completion
- ERCOT's own queue milestones ([timeline.md](timeline.md)): Approved for Energization 2025-08-27, Approved for Synchronization 2025-10-01 — Commercial-Operation-Approved not yet marked in the 2026-06-01 snapshot despite the plant operating since 2025-10 per EIA

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-06 to 2025-01 | undisturbed farmland/cropland, no racking texture in project footprint | [2024-06](imagery/key/s2_2024-06-15.png), [2024-12](imagery/key/s2_2024-12-02.png), [2025-01](imagery/key/s2_2025-01-31.png) |
| 2025-04 | racking/grading pattern clearly visible — construction well underway | [2025-04](imagery/key/s2_2025-04-21.png) |
| 2025-10 | array visually complete, matches present-day footprint | [2025-10](imagery/key/s2_2025-10-18.png) |
| 2026-07 | stable, complete panel-block grid with internal access roads | [2026-07](imagery/key/s2_2026-07-20.png) |

- Verdict: **operating** — full array built, matches EIA's independently reported (OP) Operating status since 2025-10 and ERCOT's own Approved-for-Synchronization gate (2025-10-01); first-activity window bracketed to Jan-Apr 2025 by absence/presence across monthly frames, consistent with the IA's own pad-installation deadline (2025-03-07) and EIA's (P)→(V) status flip at 2025-02

## 7. COD assessment

- The plant is very likely ALREADY commercially operating as of Oct 2025 — three independent sources converge on this: satellite imagery (complete array), EIA-860M (OP status, actual operating date 2025-10, continuous through 2026-05), and ERCOT's own queue milestones (Approved for Synchronization 2025-10-01)
- Both paper COD dates — the IA's contractual 2026-06-30 and the queue's reported claim of 2026-04-30 — appear to be administrative artifacts that the ERCOT report has not yet reconciled against real-world completion; this is a case of the queue lagging reality, not the reverse
- Risk: the only unresolved item is why the 2026-06-01 queue snapshot still shows the project active with an unmet future COD instead of "Commercial Operation Approved" — likely a reporting/administrative lag rather than a technical issue, since imagery + EIA + ERCOT's own sync gate all agree
- **Independent estimate: 2025-Q4 (commercial operation effectively already achieved), drift risk low** — favorable drift (ahead of both paper dates), not a delay risk

## 8. Could not determine

- Exact date the project will be (or was) marked "Commercial Operation Approved" in ERCOT's own report — the 2026-06-01 snapshot had not yet recorded it despite Approved-for-Synchronization since 2025-10
- Precise project acreage (no document stated it directly; leased land, no CAD parcel trail)
- The exact name-change chain connecting EIA-860M's "Stafford Solar, LLC" to "Stetson Renewables Holdings, LLC" / "Roaring Springs Solar, LLC" — tied together by coordinates and Places pin, not by a document stating the rename explicitly
- Any public financing announcement or PPA offtaker (none surfaced; NextEra likely self-financed, no press search hit)
- Exact Wrangler Switch substation coordinates (no Places pin, no exhibit map with coordinates)
