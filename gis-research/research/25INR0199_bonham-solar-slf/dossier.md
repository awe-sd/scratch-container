# Dossier — Bonham Solar SLF (25INR0199)

Researched 2026-07-20, imagery/site refresh 2026-07-21 · site 31.60, -96.53 (imagery-corroborated) · verdict **real_active**

## 1. Verdict

- **real_active** — signed IA with $26.06M LC posted ([IA](sources/2026-07-20_puct_35077-1915_standard-generation-interconnection-agreement-be.pdf)); Sentinel-2 imagery (2026-07-21 refresh) confirms active switchyard/site construction underway, and the queue has already slipped past its own contractual COD with no amendment on file
- Construction: **under construction** — clear step-change from unbroken pasture (2024-07, 2025-07) to graded ground + new structure (2026-01) to a continuing build-out with internal access tracks (2026-07); see §6. First activity brackets to 2025-07/2026-01, landing almost exactly on the IA's own Baines Creek Switch grading deadline (2025-08-15). Not confirmed as a finished/energized array — Sentinel-2's 10m/px resolution can't resolve individual panel rows.
- Site: 31.60, -96.53 — IA Exhibit C text (named switch + line topology) cross-confirmed against the ERCOT queue's own `poiLocation` field (exact match) and now imagery-corroborated by the construction step-change at this anchor; medium confidence ([map](https://www.google.com/maps/@31.60,-96.53,10000m/data=!3m1!1e3))
- COD: reported 2027-04-06 → independent **2027-Q2 (provisional)**, drift risk **high** (already past signed contractual COD, no amendment; imagery shows construction real but visibly incomplete as of 2026-07-19, ~1 month before the original 2026-08-31 contractual COD)

## 2. Site identification

- Derivation: IA Exhibit C Attachment 1 one-line diagram ([p45](sources/2026-07-20_puct_35077-1915_standard-generation-interconnecti_p45.png)) names a new TSP switch **"Baines Creek Switch"**, tapping a 138kV line between "Ranchland Switch" and "Phifer Creek Switch". Exhibit C main text (p33-36) separately describes the work as looping the *existing* Groesbeck Main Substation – Mexia Main Substation 138kV line into Baines Creek Switch. Web search independently confirms Baines Creek is a real named creek/trail at Fort Parker State Park (31.60361, -96.55083), near Mexia/Groesbeck in Limestone Co. — corroborating the switch name is tied to real geography, not a codename. **No map/site-plan exhibit exists anywhere in this IA** (confirmed via full-document review, 2026-07-21) — Attachment 1 is an electrical one-line diagram only, explicitly labeled "not for design/construction/operations."
- Stated project area: **not obtainable** — no abatement/CAD document found (see §4)
- Cross-checks: queue `poiLocation` field for 25INR0199 reads verbatim **"TAP 138 kV MEXIA_2_1_8 3632 - GROES_SE1_8 3634"** — an exact, independent match to the Exhibit C text naming the Groesbeck Main–Mexia Main line ✓. "Ranchland Switch" and "Phifer Creek Switch" could not be independently geolocated (web search noise: ranch-for-sale listings, Phifer Cemetery).
- **Neighbor check (2026-07-21)**: nearest EIA-860M-registered solar (Mexia Solar Project, operating) is 11.79km away — outside the imagery buffer. A second queue project, Fiji Solar (25INR0128), taps the identical Groesbeck Main–Mexia line segment but has zero IA on file and is still "FIS Started, No IA" (pre-construction) — ruled out as the source of observed construction. Leighton Solar SLF (24INR0298), the county's other SLF-family sibling, sits ~20km west at its own separately-derived site (31.53, -96.73) — geographically distinct. 26INR0619 "Bonham Storage SLF" shares the same interconnecting entity (J&J Solar Ranch LLC) and POI — a co-located BESS addition at the same site, not a different location.
- Not obtainable: exact parcel/polygon (no map exhibit exists, no CAD access, no Places pin this session — quota-blocked)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| J&J Solar Ranch, LLC | SPV | Generator party on [IA](sources/2026-07-20_puct_35077-1915_standard-generation-interconnection-agreement-be.pdf); alias "XE Bonham Solar 1" on filing cover + one-line diagram |
| X-Elio | developer (probable, not press-confirmed) | IA Exhibit D notice contacts use @x-elio.com emails at X-Elio's Washington DC address; "XE" alias matches X-Elio naming pattern — but zero press/website hits for "Bonham Solar" specifically |

- Financing: not found — no press release, PR Newswire item, or developer announcement for this project under any name (contrast with X-Elio's own promoted project, "Liberty Solar" in Dayton TX/BASF, which has multiple PRs)

## 4. Land & county records

- Tenure: **unknown** — Limestone CAD owner-name parcel search unreachable this session (esearch.limestonecad.com timed out for both search form and results endpoint)
- Abatements/agreements: **none found** — `ch313.py resolve` returned negative for Ch.313 and JETI under all name variants; Limestone County commissioners-court records show no "Bonham Solar" hits
- CAD: 0 parcels checked (portal unreachable)

## 5. Interconnection & contractual schedule

- POI per signed IA: new "Baines Creek Switch" (138kV), Generator connects directly to TSP switchyard — no Generator Transmission Line ([IA Exhibit C](sources/2026-07-20_puct_35077-1915_standard-generation-interconnecti_p45.png))
- Equipment (Exhibit C): 138kV plant switchyard — 1 circuit breaker (3000/5 C800 multi-ratio CTs), air-break switches, PT/CCVT, protective relaying, SCADA RTU, fault recorder, PMU, 48-fiber optic cable

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard SGIA ([pdf](sources/2026-07-20_puct_35077-1915_standard-generation-interconnection-agreement-be.pdf)) | 2024-08-06/07 | $26,061,887.00 LC, effective by 2024-09-27 |

(Single document — no amendment found in the docket join table or via `puct.py match`, despite the queue COD having since slipped past this IA's own Scheduled COD.)

| Milestone | Original IA 2024 |
|---|---|
| Notice to Proceed | 2024-09-27 |
| In-Service | 2026-04-23 |
| Trial Operation | 2026-05-03 |
| Scheduled COD | **2026-08-31** |

- Queue-history COD drift (from [timeline.md](timeline.md)): **3 changes** — 2025-02-18 → 2026-04-27 → 2026-08-31 → 2027-04-06. The queue tracked the IA's own 2026-08-31 date for 18 months (2024-05 → 2025-11), then slipped again in Dec 2025 to the current 2027-04-06 claim, with no corresponding amendment filed.

## 6. Satellite timeline

- 2026-07-21 refresh: obtained via `s2aws.py` (AWS Open Data Sentinel-2, no-quota; CDSE remains down — see prior-session note below) at the anchor, 3.5km buffer, 5 dates:
  - **2024-07-01** (scene 2024-07-14, 1.2% cloud): unbroken green pasture, no clearing
  - **2025-07-01** (scene 2025-07-24, 0.0% cloud): still unbroken pasture, no clearing
  - **2026-01-15** (scene 2026-01-15, 0.0% cloud): **step change** — bare/graded ground inside a road-bounded parcel + a new small structure at the road junction, both absent prior
  - **2026-04-15** (scene 2026-03-21, 0.0% cloud): same cleared footprint persists, structure unchanged
  - **2026-07-15** (scene 2026-07-19, 0.2% cloud): cleared footprint shows internal grid-pattern access tracks + mixed bare/re-vegetated ground; structure still present (plausibly the Baines Creek Switch control house per the IA's own equipment list) — read as active build-out in progress, not a confirmed finished/energized array
  - A separate tan borrow-pit/quarry ~1km NE of the anchor is unchanged across all 5 dates — confirmed pre-existing, unrelated to this project
- First activity brackets to **2025-07/2026-01** — lands almost exactly on the IA's Baines Creek Switch grading-complete deadline (2025-08-15)
- Verdict: **under construction**, confirmed via imagery. Prior session (2026-07-20) had all three imagery/pin tool paths blocked (CDSE 402 credit exhaustion, Google Places 429 quota, Static Maps 403 not-activated) — resolved this session via the no-quota `s2aws.py` path per operator direction (cdse.py itself remains down)

## 7. COD assessment

- The only contractual COD on record is the signed IA's **2026-08-31** — no amendment exists to support the queue's current 2027-04-06 claim
- The queue tracked the IA date for a stable 18-month window before slipping again in Dec 2025 — this is a real post-commitment slip (unlike the earlier pre-IA screening-stage estimate change), a meaningful negative signal
- FIS was only approved 2026-06-26 (very recent, per triage) while Meets-6.9(1) achieved 2025-05-09 — regulatory process continuing but not yet complete
- Construction now confirmed via imagery (§6): active switchyard/site build-out since ~2025-07/2026-01, but visibly still in progress (not a confirmed finished/energized array) as of 2026-07-19 — corroborates rather than resolves the slip: the site is real and moving, but was not visibly complete by the original 2026-08-31 contractual COD
- For: signed IA, $26M LC posted and (per IA schedule) not yet reported drawn/defaulted, real named switch infrastructure being built (Baines Creek Switch, Phifer Creek Switch Station) tied to verifiable local geography, AND now imagery-confirmed active construction
- Against: unexplained post-signing slip with no amendment, no press/financing news, no abatement filing, land tenure unknown, developer identity unconfirmed by press, construction still visibly incomplete near/past the original contractual COD
- **Independent estimate: 2027-Q2 (provisional), drift risk HIGH** — now with direct imagery support in addition to the contractual-only reasoning

## 8. Could not determine

- Exact completion state of the array (panel rows are below Sentinel-2's 10m/px resolution; imagery confirms active construction but not a finished/energized plant)
- Exact site parcel/polygon and project area in acres (CAD portal unreachable; no abatement filing to cross-check; no map exhibit exists in the IA)
- Land tenure (leased vs. purchased)
- Independent press/financing confirmation that X-Elio is the developer (circumstantial IA-contact-domain evidence only)
- Why the IA's 2026-08-31 Scheduled COD was abandoned without a filed amendment
- TX SOS/Comptroller registered-agent detail for J&J Solar Ranch, LLC (OpenCorporates/Bizapedia both blocked by bot-detection)
