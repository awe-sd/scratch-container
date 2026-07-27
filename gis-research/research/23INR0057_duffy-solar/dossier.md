# Dossier — Duffy Solar (23INR0057)

Researched 2026-07-20 · site 28.85275, -96.0865 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA chain (SGIA + 2 amendments, all confirmed) resolves to Linea Energy's project vehicle, with a Google 500 MW PPA ([PR](sources/2026-07-20_lineaenergy_official-500mw-ppa-announcement.html)); no broad grading/racking at the solar array yet
- Construction: **BESS pad stable, solar array not graded**, pad visible from ≥2026-01 through the latest clear look 2026-03 ([Jan](imagery/key/s2_2026-01-15.png), [Feb](imagery/key/s2_2026-02-24.png), [Mar](imagery/key/s2_2026-03-21.png), [Mar wide](imagery/key/s2_2026-03-21_wide4km.png))
- Site: 28.85275, -96.0865 — signed [Amendment Two](sources/2026-07-20_puct_35077-2516_amendment-two-to-ercot-standard-generation-inter.pdf) Exhibit C POI, cross-checked 0.21 km against EIA-860M's independent Duffy BESS coordinate, high confidence ([satellite view](https://www.google.com/maps/@28.85275,-96.0865,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 (queue, stale) → signed IA says **2028-10-31**; developer PR says "late 2027" → independent **2028-Q4**, drift risk **medium** (secured offtake, but 3-way COD disagreement)

## 2. Site identification

- Derivation: [Amendment Two](sources/2026-07-20_puct_35077-2516_amendment-two-to-ercot-standard-generation-inter.pdf) Exhibit C: POI "located approximately at 28.85275, -96.0865, Matagorda County, Texas"
- **Stated project area: 3,526 acres** per [Linea Energy PR](sources/2026-07-20_lineaenergy_official-500mw-ppa-announcement.html) (independently corroborated at "~3,500 acres" by [Bay City Tribune](sources/2026-07-20_baycitytribune_duffy-solar-community-event.html)) — imagery footprint unverified (no full-array grading visible yet to compare against)
- Cross-checks: EIA-860M Duffy BESS plant coordinate (28.854592,-96.08606) agrees within 0.21 km; original 2023 SGIA POI (28.874002,-96.066461) was ~3.1 km NE — moved when the plant was rescoped; both fall inside the WAP-STP 345kV corridor named in the queue POI text
- Not obtainable: Matagorda CAD parcel geometry (matagordacad.org is a "coming soon" placeholder, not a live portal)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Duffy Project Co LLC (f/k/a VDA Solar Texas 1, LLC) | SPV | party on all 3 [IA documents](sources/2026-07-20_puct_35077-2516_amendment-two-to-ercot-standard-generation-inter.pdf); TX Comptroller franchise-tax record (taxpayerId 32073592530, mailing ZIP 94104) |
| Linea Energy (sponsored by EnCap Investments L.P.) | developer/owner | [official PR](sources/2026-07-20_lineaenergy_official-500mw-ppa-announcement.html), San Francisco — ZIP 94104 matches the LLC's Comptroller mailing address |
| IEA Constructors, LLC | EPC (confirmed for co-located BESS only) | active TCEQ storm NOIs TXR1501WK/TXR1593WQ for "Duffy Energy Storage" |
| Google | PPA offtaker | 15-yr, 500 MW PPA, [PR](sources/2026-07-20_lineaenergy_official-500mw-ppa-announcement.html); independently reported by [Bay City Tribune](sources/2026-07-20_baycitytribune_duffy-solar-community-event.html) |

- Financing: offtake secured (Google PPA); no separate debt-close/financing announcement found for the solar array

## 4. Land & county records

- Tenure: **unknown** — not stated in any IA document or in PR/news coverage
- Abatements/agreements: none found — Ch.313 expired 2022 for this INR; no JETI application located
- CAD: 0 hits — matagordacad.org is a "coming soon" placeholder (confirmed dead, not a fetch error)

## 5. Interconnection & contractual schedule

- POI per Amendment Two: "approximately at 28.85275, -96.0865, Matagorda County, Texas," 345 kV delivery voltage — matches queue POI text ("Tap 345kV WAP to STP CKT39")
- Equipment: original SGIA specified 170× Sungrow SG3600UDMV inverters (540 MW); Amendment Two replaces with 135× Power Electronics HEM FS4200M inverters (502.46 MW) — a full equipment re-spec, not just a capacity trim

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_35077-2191_ercot-standard-generation-interconnection-agreem.pdf)) | 2023-04-12 | $24,346,000 Security Estimate, irrevocable LC option |
| Amendment One ([pdf](sources/2026-07-19_puct_35077-2301_amendment-one-to-ercot-standard-generation-inter.pdf)) | 2025-10-22 (dated 2025-09-19) | $100,000 CIAC — LC security language dropped from amended exhibits |
| Amendment Two ([pdf](sources/2026-07-20_puct_35077-2516_amendment-two-to-ercot-standard-generation-inter.pdf)) | 2026-07-01, eff. 2026-07-03 | $100,000 CIAC, unchanged |

| Milestone | Original SGIA 2023 | Amendment One 2025 | Amendment Two 2026 |
|---|---|---|---|
| Generator name | VDA Solar Texas 1, LLC | Duffy Project Co LLC (f/k/a VDA) | Duffy Project Co LLC |
| TIF In-Service | later of 2025-05-07 or +24mo | later of 2027-08-15 or +4mo | later of 2027-08-15 or +4mo (unchanged) |
| Scheduled COD | later of 2025-08-06 or +3mo | later of 2027-12-31 or +4mo | **later of 2028-10-31 or +4mo** |

- Queue-history COD drift ([timeline.md](timeline.md)): 3 changes — 2023-06-01 → 2025-05-31 → 2026-11-01 → 2027-12-31; 54 months total slip; in reports since 2021-02 (65 snapshots). The signed Amendment Two above is a **4th, more current** slip the queue has not yet reflected.

## 6. Satellite timeline

Imagery refreshed 2026-07-23 (2026-only, cloud-free set; off-site probes archived). All frames are tight 2 km chips centered on the exact Amendment Two POI unless noted.

| Date | Cloud | Observation | Frame |
|---|---|---|---|
| 2026-01-15 | 0.1% | Small pad/structure with access-road stubs at POI; farmland undisturbed (winter-fallow) | [Jan](imagery/key/s2_2026-01-15.png) |
| 2026-02-24 | 0.6% | Pad unchanged; pristine frame; no grading/racking | [Feb](imagery/key/s2_2026-02-24.png) |
| 2026-03-21 | 2.0% | Pad unchanged; site clear (minor puffs); no array activity | [Mar](imagery/key/s2_2026-03-21.png) |
| 2026-03-21 | 2.0% | **4 km wide context** — whole POI area still farmland, no large graded array footprint anywhere | [Mar wide](imagery/key/s2_2026-03-21_wide4km.png) |
| 2026-06-29 | 6.3%* | Cleanest recent frame — clouds sit off the POI so the site is clear; pad unchanged, no array grading | [Jun](imagery/key/s2_2026-06-29.png) |
| 2026-07-19 | 39.9%* | **Newest scene in existence** — heavy cloud lower/bottom-right but the BESS pad at center is clear; pad unchanged, no array grading | [Jul](imagery/key/s2_2026-07-19.png) |

*whole-tile cloud; the site itself is clear/readable in both frames.

- **Why nothing more recent:** 2026-07-19 is the newest Sentinel-2 scene that exists at all. The satellite last passed on 2026-07-19 (4 days before this update) and revisits ~every 5 days, so no fresher scene is published yet (next pass ~2026-07-24). July 07-04 (24.6%) and 07-09 (19.1%) have cloud directly over the POI and are archived.
- Verdict: **BESS pad present and stable; solar array not yet graded** — the pad matches the EIA/TCEQ-confirmed Duffy BESS location (0.21 km away), not a 3,526-acre array footprint. Consistent with (does not contradict) the developer's stated Q3-2026 solar construction start.

## 7. COD assessment

- Signed [Amendment Two](sources/2026-07-20_puct_35077-2516_amendment-two-to-ercot-standard-generation-inter.pdf) (effective 3 weeks before this research) sets the legal scheduled COD at 2028-10-31 — the most authoritative date on file, and already 10 months past the queue's still-reported 2027-12-31
- Developer PR/news claim an even earlier "late 2027" target — a 3-way disagreement (queue / signed IA / developer messaging) that is itself the most decisive drift signal here
- TIF In-Service prerequisite date (2027-04-15) is unchanged between Amendment One and Two — the COD slip is a back-end schedule reset, not a missed early milestone
- Offtake is secured (Google PPA) and the co-located BESS is independently confirmed under active construction, both de-risking factors relative to a project with no offtake or paper trail
- **Independent estimate: 2028-Q4, drift risk medium** — anchored to the signed IA's own most recent schedule; a "late 2027" actual COD would be a positive surprise, not further slippage

## 8. Could not determine

- Land tenure (lease vs. purchase) — absent from IA documents and PR/news
- EPC for the solar array specifically (IEA Constructors confirmed only for the co-located BESS)
- Non-PPA financing/debt-close status for the solar array
- Whether FIS has been waived or remains outstanding (queue snapshot: requested 2021-02, never shown approved)
- Solar-array grading progress after 2026-07-09 (partial cloud cover that date) — recommend a follow-up chip in Q4 2026
