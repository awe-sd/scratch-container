# Dossier — Bastrop Peaking Generators (26INR0261)

Researched 2026-07-18 · site 30.14555, -97.54879 · verdict **real_early**

## 1. Verdict

- **real_early** — brownfield expansion at the operating **Bastrop Energy Center**; large fresh graded pad north of the existing plant in 2026-07 vs undisturbed farmland in 2024-01 ([2026-07](imagery/s2_2026-07.png), [2024-01](imagery/s2_2024-01.png)); ownership + air permit + TEF loan all documented
- Construction: **clearing/early-grading**, first activity between 2024-01 and 2026-07 (couldn't tighten — see §8)
- Site: 30.14555, -97.54879 — OSM industrial-landuse polygon of Bastrop Energy Center, imagery-confirmed, high confidence ([satellite view](https://www.google.com/maps/@30.14555,-97.54879,5000m/data=!3m1!1e3))
- COD: reported 2027-12-07 → independent **2029-Q1**, drift risk **high** (13 months from early-grading to 1104 MW COD is unrealistic)

## 2. Site identification

- Derivation: OSM Nominatim direct hit on "Bastrop Energy Center" (way 462642757), industrial landuse polygon at 30.14555, -97.54879 ([OSM data](sources/2026-07-18_osm_bastrop-energy-center.json)); Sentinel-2 xwide confirms existing plant + new graded pad at that centroid ([2026-07](imagery/s2_2026-07.png), [center crop](imagery/s2_2026-07_center_crop.png))
- **Stated project area: ~74 acres** for the OSM industrial polygon (490 m N-S × 616 m E-W); the new-plant graded pad north of the existing complex adds ~800 m of visible footprint. No IA/abatement acreage number obtained (see §8)
- Cross-checks (each linked): TEF NOI names site as "the existing Bastrop Energy Center site in Cedar Creek, TX" ([NOI](sources/2024-05-30_puct_56455-42_hull-street-tef-noi-app-194.pdf)); TCEQ RN101056851 registered at "125 Old Bastrop Rd, Cedar Creek" with MPH Bastrop Peakers as active operator ([TCEQ RE search](sources/2026-07-18_tceq_re-search-bastrop-energy-center.html)); distance to POI "L_GARFIE" (Austin Energy Garfield 345 kV, ~30.207, -97.633) ≈ 10.6 km — consistent with a tap line
- Not obtainable: exact new-plant tract boundary; Bastrop CAD parcel geometries (portal is JS-rendered, no scrape)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| MPH Bastrop Peakers, LLC | SPV / operator | [TEF filings](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf); active operator of TCEQ NSR 178585 ([permit page](sources/2026-07-18_tceq_air-permit-178585-mph-facility.html)) |
| Hull Street Energy, LLC (Bethesda MD) | parent developer | [TEF NOI 2024-05-30](sources/2024-05-30_puct_56455-42_hull-street-tef-noi-app-194.pdf) — "wholly-owned subsidiary", partner Mark Orman signed |
| Bastrop Energy Partners LP | existing plant owner/operator (CN600615470) | [TCEQ RE search](sources/2026-07-18_tceq_re-search-bastrop-energy-center.html) — co-listed at same RN |
| Texas Energy Fund (PUCT) | debt financing | Application **APP-00000194**; extension request ([56896-83](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf)) |

- Financing: TEF loan agreement executed; initial disbursement deadline **extended to 2026-12-31** on 2025-10-08 by CFO Craig Herlihy, citing "EPC availability, supply chain issues, and electrical interconnect timing" ([56896-83](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf)) — negative velocity signal

## 4. Land & county records

- Tenure: **unknown** — no CAD hit (portal is JS-rendered, no scrape); the site is a brownfield expansion co-located with existing Bastrop Energy Partners assets, so land tenure likely inherited rather than newly acquired ([TCEQ RE](sources/2026-07-18_tceq_re-search-bastrop-energy-center.html))
- Abatements: none surfaced (Ch.313 expired 2023; JETI queries returned generic pages this pass)
- CAD: 0 parcels scraped from esearch.bastropcad.org (JS-rendered XHR — see log D6)

## 5. Interconnection & contractual schedule

- POI per queue: "7048 L_GARFIE5_1Y 345kV" = tap at Austin Energy Garfield 345 kV switchyard (~10.6 km NW of site). IA PDF not obtained this pass (PUCT Interchange returned HTTP 402 in triage; no docket surfaced under "Bastrop Peaking" in deep-scan Case/Filing searches) — see §8
- Equipment: not obtained (no IA exhibits pulled)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA — not retrieved | 2025-12-19 (per queue) | not obtained |

| Milestone | Original IA | Amendment |
|---|---|---|
| In-Service | not obtained | — |
| Trial Operation | not obtained | — |
| Scheduled COD | not obtained | — |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2026-05-31 → 2027-03-31 → 2027-12-07 (18+ months of slip across 3 IA-window snapshots)
- Independent TEF milestone: initial disbursement deadline slipped Q4-2025 → **2026-12-31** ([extension request](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf))

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-01 | Existing plant only; area N of it is undisturbed pasture/farmland | [png](imagery/s2_2024-01.png) |
| 2026-07 | Existing plant + very large bright tan graded pad (~800 m across) immediately N/E of it; no turbine hall, cooling structures, or crane pad on the new area yet | [png](imagery/s2_2026-07.png), [center crop](imagery/s2_2026-07_center_crop.png) |

- Verdict: **clearing/early-grading** — bulk earthwork visibly begun on new footprint; zero vertical structures on the expansion pad; 10 m/px cannot resolve foundations. Cannot bracket first-activity month between 2024-01 and 2026-07 this pass (CDSE OAuth token locked out; timelapse retry produced no frames)

## 7. COD assessment

- Reported 2027-12-07 is a **queue field**, not verified against an IA exhibit this pass; NB the queue COD has already slipped from 2026-05-31 → 2027-03-31 → 2027-12-07 (18+ months) pre-construction
- MPH's own TEF filing on 2025-10-08 requested an initial-disbursement extension to 2026-12-31, citing "EPC availability, supply chain issues, and electrical interconnect timing" ([56896-83](sources/2025-10-08_puct_56896-83_mph-bastrop-peakers-extension-request.pdf)) — the developer itself did not expect first draw before end-2026, which is inconsistent with a Dec-2027 COD
- Observed pace: only bulk earthwork visible in 2026-07; no turbine hall, cooling, transformer, or laydown yet. A 1,104 MW gas peaker fleet typically needs 24-36 months from pad-ready to COD for turbine delivery (GE/Siemens/Mitsubishi frame lead times run 2-3 yrs currently), erection, commissioning, and Trial Operation
- Positive signals: IA signed 2025-12-19 (per queue); TCEQ NSR permit 178585 ACTIVE with MPH as operator since 2024-12-13; identified parent (Hull Street) is a real infrastructure fund; site is a brownfield with existing water/gas/interconnect infrastructure — none of these constrain the schedule to 2027-12
- **Independent estimate: 2029-Q1, drift risk high.** Baseline case: pad-ready by end-2026, turbine erection through 2028, commissioning 2028-Q4 → COD 2029-Q1. Meaningful downside risk (TEF disbursement, turbine delivery, gas/water/electrical tie-in coordination) into 2029-Q3+

## 8. Could not determine

- Signed IA PDF (PUCT Interchange HTTP 402 during triage; no matching docket surfaced in deep-scan Case/FilingParty searches) — cannot cite contractual In-Service/Trial-Op/COD dates, financial-security amount, or exhibit-C equipment list
- First-activity month between 2024-01 and 2026-07 (CDSE OAuth locked out; timelapse retry produced no frames)
- Bastrop CAD parcel geometries / tract boundaries (esearch portal JS-rendered)
- TX SOS registration detail for MPH Bastrop Peakers, LLC (free searches returned nothing; SOSDirect is paid)
- Static site map (`gmaps.py staticmap` returned HTTP 403 — API not enabled on the key)
- Turbine OEM / EPC identity (not disclosed in the TEF filings pulled)
