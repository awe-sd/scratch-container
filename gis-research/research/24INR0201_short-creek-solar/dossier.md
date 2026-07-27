# Dossier — Short Creek Solar (24INR0201)

Researched 2026-07-18 (corrected 2026-07-18) · site 33.9850, -98.7950 · verdict **real_early**

**Correction notice (2026-07-18):** a human reviewer spotted apparent construction in the top-right corner of [imagery/s2_2026-07-15_xwide.png](imagery/s2_2026-07-15_xwide.png) (~lat 34.05, lon -98.78). The original no_activity verdict had only ever imaged a 2 km buffer around the site point below; it never looked at that corner. Re-investigation found genuine new land disturbance there — but a rigorous pixel-to-geo transform of the Ch313 boundary map (scale bar + OSM-anchored landmark) shows that disturbance lies **~3.1 km outside** the Short Creek Solar project boundary, not inside a second lobe of it as an intermediate draft of this correction mistakenly concluded. Final verdict: **no_activity confirmed** for 24INR0201, with the ruled-out candidate documented in §6/§8. Full trail in [log.md](log.md) "Correction pass 2026-07-18".

## 1. Verdict

- **real_early** — $20 M security posted, IA executed twice, Ch313 tax deal live with 3 yrs of Form 772 filings, developer is TotalEnergies via SPV "Wichita Solar I, LLC" ([IA](sources/2026-07-18_puct_35077-1963_aep-wichita-solar-IA.pdf), [Amend 1](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf), [Form 772 TY24](sources/form772_p1.png))
- Construction: **no_activity (re-confirmed 2026-07-18)** — bare farmland within the actual, rigorously georeferenced project boundary on all Sentinel-2 dates 2022-07 → 2026-07 ([latest frame](imagery/key/s2_swblock_2026-07-15.png)). A human-flagged candidate ~7.3 km NE of the site point does show real new land clearing, but pixel-geo transform of the Ch313 boundary map ([map](sources/appsupp1_p4.png)) places that location ~3.1 km outside the project boundary — real disturbance, wrong project. See §6.
- Site: 33.9850, -98.7950 — Ch313 boundary map matched to N. Fork Buffalo Creek Reservoir + US-287 alignment, high confidence — independently re-confirmed and tightened this pass via OSM landmark cross-checks and a full pixel-geo transform of the boundary map ([abatement map](sources/appsupp1_p4.png), [satellite view](https://www.google.com/maps/@33.9850,-98.7950,5000m/data=!3m1!1e3))
- COD: reported 2027-12-17 → independent **2028-Q3**, drift risk **high** (unchanged — contractual COD is 2028-06; imagery still bare within the confirmed project boundary)

## 2. Site identification

- Derivation: Ch313 supplement 001 Figure 2 ([map](sources/appsupp1_p4.png)) shows a "notched" Reinvestment Zone boundary — a large SW block plus a smaller notched lobe to its NE, connected by a narrower waist — with US-287 crossing the SW block's SW corner, FM 2384W on its west edge, and Lake Buffalo / North Fork Buffalo Creek running along its east side. Cross-referenced against the North Fork Buffalo Creek Reservoir at 33.9995, -98.7564 (gmaps places hit) and the US-287 alignment; boundary centroid → **33.985, -98.795**.
- **Independent OSM cross-check added this pass** (no image budget cost): US-287 way 21326169 (lat 33.9711-33.9864, lon -98.8172/-98.7695) crosses almost exactly at the SW corner; North Fork Buffalo Creek Reservoir (OSM way 203133874, lat 33.9853-34.0162, lon -98.7736/-98.7320) has its southern tip only **1.97 km** east of the site point at matching latitude — both independently corroborate the derivation. FM 2384 (OSM ways 202478860/862/866, lon -98.837/-98.831) runs N-S ~3.9 km west of the site point, consistent with "FM 2384W along the west edge" for a several-sq-mi polygon.
- **Rigorous pixel-geo transform added this pass**: the Ch313 boundary map was georeferenced using its own printed scale bar (measured at 107 px = 0.4 mi -> 166.2 px/km) anchored on the map's SW corner (pixel ~952,912), matched to the closest point on OSM US-287 way 21326169 to the site's longitude (33.9771, -98.7949, 0.88 km from that way's nearest vertex). Cross-validated on the west edge: the transform predicts the boundary's west edge at lon -98.825, vs. OSM's FM-2384 at lon -98.834 (~800 m gap, consistent with the map showing the boundary running alongside, not on top of, the road) — two independent landmarks agree. Under this north-up affine transform, the boundary's blue outline (detected by color threshold; pixel bbox x:491-1206, y:136-912 excluding the legend) spans **lat 33.977-34.019, lon -98.825 to -98.778** — a ~4.3 x 4.7 km "several sq mi" area, including its own internal NE lobe (the notch, topping out at ~34.019), consistent with the Ch313 description. **Important distinction**: the corner-candidate disturbance (§6/§8) at lat 34.0475 sits ~3 km north of even this internal NE lobe's own northern tip (34.019) — it is not "the NE lobe," it is a separate feature further north still, outside the boundary entirely.
- Cross-checks (each linked): IA Exhibit C text "Short Creek Substation... located in Wichita County approximately eight (8) miles east of Electra, Texas" ([IA p37](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf)) — Electra is at (34.026, -99.014), site is ~13 km ESE = ~8 miles. IA Exhibit C-1 one-line ([rendered](sources/wichita_ia_p57_exhibitC1_oneline.png)) shows POI at AEP Poisson Station on 345 kV line running 23 mi W to Riley and 5 mi E to Fisher Road — matches identity-packet POI "Tap 345kV 6101 Riley - 1425 Fisher Road Switch Ckt 1". OSM 345 kV substation way 1122931096 at (33.9294, -98.8316) is a plausible Poisson location, ~7 km SW of the project boundary — consistent with the ~0.1 mile GIF distance shown in Exhibit C-1 being conceptual.
- Not obtainable: exact Poisson Station coordinates (CEII); a surveyed (rather than pixel-measured) project boundary; Wichita CAD parcel geometry (portal blocked).

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Wichita Solar I, LLC | SPV | party on [IA](sources/2026-07-18_puct_35077-1963_aep-wichita-solar-IA.pdf), [Amend 1](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf) and [Ch313 app 1837](sources/2026-07-18_comptroller_ch313_1837-electra-wichita-app.pdf); ERCOT queue name "Short Creek" is the substation name |
| TotalEnergies Renewables USA | developer/owner of SPV | Generator notice emails in [Amend 1 Exhibit D](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf) all @totalenergies.com (Romo, Newcombe); [Form 772 TY24](sources/form772_p1.png) signatory Randy Jenks / randy.jenks@totalenergies.com, "Director of Engineering and Project Execution" |
| Core Solar, LLC | original developer (pre-acquisition) | "CORE SOLAR" logo on [Ch313 supp1 Fig 1 map](sources/appsupp1_p3.png) and [Fig 2 map](sources/appsupp1_p4.png), dated Aug/Jul 2022 — before TotalEnergies acquired Core Solar in Jan 2023 |
| EPC / offtaker | unknown | no PR / permit filings surfaced — expected for a project 17+ months from planned COD |

- Financing: **$20,000,000 financial security posted with AEP Texas** per [Amend 1 Exhibit E](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf) (LC or corporate guaranty); Ch313 value limitation cap **$40,000,000** with Electra ISD, agreement executed and active.

## 4. Land & county records

- Tenure: **unknown** — Ch313 supp1 shows a Project Boundary polygon and Reinvestment Zone ([map](sources/appsupp1_p4.png)) but does not label lease vs purchase, and the Wichita CAD portal (propaccess.trueautomation.com cid=112) returned a session-timeout fallback to every scripted request. Base rate for a Texas solar project of this size is leased ranch/farmland with landowner names still on the tax roll, likely here.
- Abatements: **Ch313 agreement 1837 with Electra ISD is executed and current** ([Comptroller docket index](sources/2026-07-18_comptroller_ch313_1837_electra-wichita-solar-index.html)) — $40 M value limitation, applicant Wichita Solar I LLC, Renewable Energy Electric Generation, **Form 772 annual compliance reports filed 3 years running (2023, 2024, 2025)**. QTP1 = 2026-2027, QTP2 = 2027-2028, Year 1 of Value Limitation Period = 2028-2029.
- CAD: portal not scriptable in this container; owner-name search under "Wichita Solar" / "TotalEnergies" / "Core Solar" could not be executed.

## 5. Interconnection & contractual schedule

- POI per signed IA: "Substation Name: Short Creek... located in Wichita County approximately eight (8) miles east of Electra, Texas. Once the facilities are completed and energized, the Point of Interconnection will be located at TSP's first dead-end structure outside the fence of TSP's **Poisson Station**" on a 345 kV tap of the Riley – Fisher Road 345 kV line ([Amend 1 p37](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf), [Exhibit C-1](sources/wichita_ia_p57_exhibitC1_oneline.png)) — matches identity-packet POI text exactly.
- Equipment (Amend 1 Exhibit C): nominal **830.16 MW at inverter terminals** = Gen Ph 1 Solar (24INR0201) 162x SUNGROW SG 4400 inverters @ 4.18 MW each = **677.16 MW** + Gen Ph 2 Storage (27INR0029) SMA 4600-S2-US inverters. Original IA was solar-only: 171x SMA SC4400 UP-US @ 3.6 MW = 615.6 MW. Queue-report 627.81 MW sits between these two figures.

| Milestone | Original IA 2024 | Amendment 1 (2026) |
|---|---|---|
| In-Service Date | ~2028-10-02 (48 mo) | **~2028-04-02** (42 mo) |
| Trial Operation | ~2028-11-02 (49 mo) | **~2028-05-02** (43 mo) |
| Scheduled COD — Solar (Gen Ph 1, 24INR0201) | ~2028-12-02 (50 mo) | **~2028-06-02** (44 mo) |
| Scheduled COD — Storage (Gen Ph 2, 27INR0029) | N/A | **~2030-06-02** (56 mo) |
| Scheduled COD — BTM Load | N/A | ~2028-04-02 (42 mo) |

(Months measured from Original Agreement execution 2024-10-02; PUCT Control No. 35077, items 1963 and 2471; original signed 2024-10-02, amendment executed 2026-04-14.)
- Security posted: **$20,000,000** ([Amend 1 Exhibit E](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf))
- Queue-history COD drift (from [timeline.md](timeline.md)): 3 values across 45 monthly snapshots — 2027-12-01 (2022-10 → 2024-09; pre-IA), **2029-03-02 (2024-10 → 2025-05; matches original IA COD ~2028-12 loosely, held for 8 months right after IA execution)**, then **back to 2027-12-17 (2025-06 → 2026-06)** — the current queue value is ~9 months earlier than the amended-IA contractual date, i.e. queue reflects a developer-optimistic COD, not the signed schedule.

## 6. Satellite timeline

**Site (33.985, -98.795) and its confirmed project boundary — unchanged, still bare:**

| Date | Observation | Frame |
|---|---|---|
| 2022-07 | pre-project baseline: farmland, creek pattern intact | [png](imagery/key/s2_swblock_2022-07-15.png) |
| 2024-07 | just before IA signing (Oct 2024) — unchanged farmland | [png](imagery/s2_project_2024-07.png) |
| 2025-07 | post-IA, pre-amendment — unchanged | [png](imagery/s2_project_2025-07.png) |
| 2025-11 | 6 months before amendment — unchanged | [png](imagery/s2_project_2025-11.png) |
| 2026-03 | just before amendment — unchanged | [png](imagery/s2_project_2026-03.png) |
| 2026-06 | 2 months after amendment (partly cloudy) — no new activity | [png](imagery/s2_project_2026-06.png) |
| 2026-07 | present — still farmland, no visible grading or pad | [png](imagery/key/s2_swblock_2026-07-15.png) |

- **Verdict: no_activity, re-confirmed 2026-07-18.** Creek pattern, field boundaries, and road grid are visually identical between 2022-07 and 2026-07 within the project boundary. 10 m resolution can't detect survey stakes but would show any real solar-scale grading, which is absent.

**Corner-candidate investigation (2026-07-18 correction pass):** a human reviewer flagged what looked like construction in the top-right corner of [imagery/s2_2026-07-15_xwide.png](imagery/s2_2026-07-15_xwide.png) (~lat 34.05, lon -98.78). Investigation found genuine new land disturbance at **lat 34.0475, lon -98.7712** — [imagery/key/s2_cornercandidate_2022-07-15.png](imagery/key/s2_cornercandidate_2022-07-15.png) (2022: natural brush/pasture, dark plow-row texture, no clearing) vs [imagery/key/s2_cornercandidate_2026-07-15.png](imagery/key/s2_cornercandidate_2026-07-15.png) (2026: a cleared, notched-boundary graded area — bare tan soil, interior dirt tracks, several small bright structures, a small dark pond not present in 2022; zoom [png](imagery/s2_cornercandidate_2022vs2026_zoom.png)). **This is real change, but it is not the Short Creek Solar project.** A rigorous pixel-to-geo transform of the Ch313 boundary map (§2) places the project boundary's northern edge at lat ~34.019 — the disturbed area is ~3.1 km further north, outside the boundary. Likely cause is unconfirmed from imagery alone (possibly an oil-lease pad/tank battery — small dot features consistent with the oil-field disturbance noted throughout this county — or unrelated ranch development), but it is not attributable to 24INR0201.
- Negative-sweep of the rest of the human-flagged region (3 km buffer, 2026-07-15): [imagery/search/pA_2026-07-15.png](imagery/search/pA_2026-07-15.png) (34.05,-98.775, the original corner candidate), [pB](imagery/search/pB_2026-07-15.png) (34.05,-98.81), [pC](imagery/search/pC_2026-07-15.png) (34.02,-98.78), [pD](imagery/search/pD_2026-07-15.png) (34.02,-98.81), [pE_recheck](imagery/search/pE_recheck_2026-07-15.png) (33.985,-98.795) — all show only ordinary contour-plowed farmland, oil-lease pads/tanks, and creek/pond features. No construction signature was found anywhere within the actual (georeferenced) project boundary.

## 7. COD assessment

- Reported queue COD **2027-12-17** is not corroborated by the primary evidence: the contractual Scheduled COD in the currently-executed First Amended and Restated IA (signed 2026-04-14, [PUCT 35077-2471](sources/2026-07-18_puct_35077-2471_aep-wichita-solar-IA-amend1.pdf)) is **~2028-06-02** for Gen Phase 1 (Solar) — roughly six months later than the queue claim.
- Physical infeasibility of 2027-12: the project site is completely undeveloped as of 2026-07-15 within the actual, rigorously georeferenced project boundary (§2, §6); reaching Dec 2027 CO on a ~625-830 MW project from a bare-land start in ~17 months would require simultaneously starting mass grading, substation civils, and racking — well outside industry norm and inconsistent with a Ch313 that lists 250 construction FTEs starting in the 2027-2028 school year.
- **Corner-candidate investigation (2026-07-18)**: a human reviewer flagged apparent construction ~7.3 km NE of the site; real land disturbance was found there, but a rigorous pixel-geo transform of the Ch313 boundary map showed it lies ~3.1 km outside the project boundary (§6). It does not change this assessment — no construction evidence exists within the confirmed project footprint.
- Contractual 2028-06 is credible given typical build cadence on flat Texas ranchland: mobilization 2027-Q1, grading through 2027-Q4, racking + modules 2028-Q1-Q2, commissioning into In-Service 2028-04 / COD 2028-06.
- Risk: amended IA already pulled Solar COD in by 6 months (from 2028-12 to 2028-06) while adding storage & BTM scope — this is aggressive; one further slip on either the interconnection facilities side (AEP Poisson buildout) or the equipment side (Sungrow inverter delivery) would push COD to late 2028 or Q1 2029. Amended IA rule that any 12+ month extension triggers a paid-for re-study caps single-step drift but doesn't rule out serial 6-month adjustments.
- For: $20M security posted and retained through the amendment; TotalEnergies parent (investment-grade, real 4 GW US pipeline via Core Solar acquisition Jan 2023); Ch313 with Electra ISD executed and 3 years of compliance reports; amendment ADDS scope (co-located battery + BTM load) — developers don't do that on paper projects.
- **Independent estimate: 2028-Q3, drift risk high** — real project on a credible contractual path, but the queue-reported COD is ~9 months earlier than the signed contract and cannot be reconciled with bare-earth imagery within the confirmed project boundary 17 months out.

## 8. Could not determine

- **Corner-candidate check (added 2026-07-18 correction pass):** a human reviewer flagged apparent construction ~7.3 km NE of the site point (34.05,-98.78 approx.) in the xwide frame. Real new land disturbance was confirmed there (34.0475,-98.7712, +/-~0.3-0.5 km from manual pixel measurement) between 2022-07 and 2026-07, but a rigorous pixel-to-geo transform of the Ch313 boundary map (§2, anchored on the map's scale bar + an OSM-matched point on US-287) shows the project boundary's northern edge is at lat ~34.019 — **the disturbed area is ~3.1 km outside the project boundary** and is not attributable to 24INR0201. Its actual cause (oil-lease pad, unrelated ranch/agricultural development, or something else) was not determined — out of scope once it was established to be a different site. This confirms, rather than changes, the no_activity verdict for Short Creek Solar.
- Exact AEP Poisson Station coordinates (CEII-redacted); OSM has a plausible unnamed 345 kV substation at (33.9294, -98.8316) that fits.
- Wichita CAD parcel search under LLC / TotalEnergies / Core Solar names — portal (Harris Govern / True Automation cid=112) rejected all scripted requests in this container.
- Lease-vs-purchase status of the underlying land (blocked by CAD access + no explicit label in Ch313 supp1).
- EPC identity, PPA offtaker, financing close details — none surfaced via press-release fetch (all queried outlets returned 403/CAPTCHA); consistent with the project being 17+ months from targeted COD and not yet mobilized.
- TotalEnergies-Core Solar acquisition press release (Jan 2023) — original URL rolled off TotalEnergies news index and Wayback direct-URL lookups empty. Parent-chain relies on primary IA + Form 772 email domains and Ch313 map logos, not on the acquisition PR.
