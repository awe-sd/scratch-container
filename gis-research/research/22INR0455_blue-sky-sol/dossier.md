# Dossier — Blue Sky Sol (22INR0455)

Researched 2026-07-20 · site 30.7096, -101.1108 · verdict **real_early**

## 1. Verdict

- **real_early** — signed/twice-amended IA with intact financial security, a real Ch.313 tax-abatement filing, and a genuine 15-year PPA with Google announced 2026-02-23 ([article](sources/2026-07-20_nacleanenergy_uka-google-blue-sky-solar-ppa.html)); but "late-stage development," not under construction
- Construction: **unclear_no_imagery** — CDSE Sentinel-2 was down fleet-wide this run (RemoteDisconnected, all attempts); no queue-reported construction start/end in 67 monthly snapshots ([timeline.md](timeline.md)); no active TCEQ storm-water NOI
- Site: 30.7096, -101.1108 — IA Exhibit C text ("approximately Five and one Half (5.5) miles east of Ozona, Texas") + confirmed Ozona town coordinates, medium confidence ([IA](sources/2026-07-19_puct_35077-1379_ercot-standard-generation-interconnection-agreem.pdf); [map](https://www.google.com/maps/@30.7096,-101.1108,5000m/data=!3m1!1e3))
- COD: reported 2027-12-31 → independent **2028-Q2**, drift risk **high** (never met a self-set COD; latest IA already implies 2028-01)

## 2. Site identification

- Derivation: all 3 signed IA versions state identically (Exhibit C, Sec.2): "Generator's Blue Sky Substation...will be located in Crockett County approximately Five and one Half (5.5) miles east of Ozona, Texas" ([Original IA](sources/2026-07-19_puct_35077-1379_ercot-standard-generation-interconnection-agreem.pdf)). Ozona town center confirmed at 30.7053, -101.2025 (travelmath/latitude.to via search.py); estimate computed due east at that distance.
- **Stated project area: not obtained** — no acreage figure in any artifact; energycentral.com 2023 gives 240,732 PV panels + 29 central inverters + $85mn investment but no acres ([article](sources/2026-07-20_energycentral_uka-blue-sky-sale-2023.html)) — imagery footprint consistent? unverified (no imagery this run)
- Cross-checks: IA Exhibit C-1 one-line drawing ([diagram](sources/2026-07-19_puct_35077-2358_second-amended-and-restated-ercot_p58.png)) shows Blue Sky Substation connected to Friend Ranch Station by "~3.6 mile, 138 kV" generator-owned line — consistent order-of-magnitude with the Ozona-relative estimate, but conceptual/not-to-scale, no independent geo-fix. USGS GNIS confirms "Friend Ranch" as a real named Crockett County locale (hometownlocator.com), but GNIS coordinate lookup itself was unreachable (503) this run.
- Not obtainable: exact Blue Sky Substation / Friend Ranch Station coordinates (no GNIS access, no CAD parcel, no satellite imagery, Google Places 429-blocked all attempts)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Blue Sky Solar LLC | SPV | Generator party on [IA](sources/2026-07-19_puct_35077-1379_ercot-standard-generation-interconnection-agreem.pdf); INR #22INR0455 quoted verbatim in recitals of all 3 IA versions |
| UKA North America (subsidiary of UKA Group, Germany) | developer/owner | [PPA announcement](sources/2026-07-20_nacleanenergy_uka-google-blue-sky-solar-ppa.html) 2026-02-23; [2023 sale-process article](sources/2026-07-20_energycentral_uka-blue-sky-sale-2023.html) — 29-inverter count matches IA exactly, confirming same project |
| Google | offtaker (PPA) | 15-yr PPA executed, brokered by LevelTen ([PR](sources/2026-07-20_nacleanenergy_uka-google-blue-sky-solar-ppa.html)) |

- Financing: no project-financing-close announcement found; the Google PPA (2026-02-23) is the only capital-markets-relevant signal — a PPA precedes, not confirms, financial close ([article](sources/2026-07-20_nacleanenergy_uka-google-blue-sky-solar-ppa.html))

## 4. Land & county records

- Tenure: **unknown** — Crockett CAD portals (crockettcad.com, crockettcad.org) are session/JS-based, not scrapeable this run; no owner-name parcel search completed
- Ch.313 agreement: **exists** — Crockett County Consolidated CSD, applicant "Blue Sky Solar, LLC," app #1821 (comptroller.texas.gov/economy/development/prop-tax/ch313/agreement-docs-details.php?id=1821, confirmed via search index) — agreement + amendment-1 application PDFs both blocked HTTP 403 at assets.comptroller.texas.gov (confirmed via curl, WebFetch, and ch313.py's own request helper — genuine source-side block, not read); local ch313_agreements.json cache (740 rows) has a gap at app_no 1821, explaining ch313.py's false negative
- CAD: 0 parcels searched (portal not scrapeable) — inconclusive, not evidence either way

## 5. Interconnection & contractual schedule

- POI per signed IA: "TSP's first dead-end structure outside the fence of TSP's Friend Ranch Station...that terminates Generator's 138 kV transmission line from the [Blue Sky] Substation" ([Original IA](sources/2026-07-19_puct_35077-1379_ercot-standard-generation-interconnection-agreem.pdf)) — matches queue POI "Friends Ranch 138kV" exactly (minor spelling variant)
- Equipment (Exhibit C, all 3 versions): Maximum 101.2 MW via 29× General Electric LV5+-1569 solar inverters, 3.48959 MW each

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1379_ercot-standard-generation-interconnection-agreem.pdf)) | 2022-02-01 | $2,200,000 LC/guaranty |
| First A&R ([pdf](sources/2026-07-19_puct_35077-2277_ercot-standard-generation-interconnection-agreem.pdf)) | 2025-09-17 | $2,200,000 — unchanged |
| Second A&R ([pdf](sources/2026-07-19_puct_35077-2358_second-amended-and-restated-ercot-standard-gener.pdf)) | 2025-12-11 | $2,200,000 — unchanged |

(Security flat across two amendments and ~46 months of slippage — unlike comparable projects where security rises with each amendment.)

| Milestone | Original IA (2022) | First A&R (2025) | Second A&R (2026) |
|---|---|---|---|
| In-Service | 2024-02 (24mo) | 2027-01 (59mo) | 2027-10 (68mo) |
| Trial Operation | 2024-02 (24mo) | 2027-02 (60mo) | 2027-11 (69mo) |
| Scheduled COD | 2024-03 (25mo) | 2027-04 (62mo) | **2028-01 (71mo)** |

(All 3 exhibits state N-months-from-conditions-satisfied, anchored to the Original Agreement's 2022-02-01 execution date per each amendment's carryover text; months computed from that anchor.)
- Queue-history COD drift (from [timeline.md](timeline.md)): **5 changes** — 2022-12 → 2023-11 → 2024-06 → 2025-02 → 2027-04 → 2027-12 (current); the IA amendments add 2 more contractual slips not fully reflected in the queue's own reported date

## 6. Satellite timeline

- **No imagery obtained this run** — CDSE (Sentinel-2 / Copernicus Data Space) returned `RemoteDisconnected` capacity errors on every attempt (2 separate tries, ~15 min apart); confirmed via process inspection that other concurrent research sessions in this container hit the identical failure against unrelated projects — a fleet-wide outage, not specific to this site or coordinate.
- Verdict: **unclear_no_imagery** — construction stage cannot be visually confirmed or ruled out; all evidence below is documentary only

## 7. COD assessment

- Latest signed IA (Second A&R, exec 2025-12-11) sets contractual COD at 2028-01 — already past the queue's own reported 2027-12-31, and is the 3rd distinct contractual COD after two amendments (2024-03 → 2027-04 → 2028-01)
- Independent trade press (nacleanenergy.com, 2026-02-23) calls the project "late-stage development" with a vaguer "late 2027" target — already a quarter looser than the project's own latest signed paperwork
- No construction-start evidence from any independent channel: no TCEQ storm-water NOI, no queue construction milestone in 67 snapshots, no imagery (CDSE down)
- Financial security frozen at $2.2M through 46 months of slippage — a soft signal that capital commitment has not scaled with the repeated deferrals, though the PPA + Ch.313 filing + intact IA argue this is a real, funded-enough-to-persist project rather than paper
- Track record: 5 queue-reported COD slips plus IA-only visible slips = a project that has never once hit a COD it set for itself
- **Independent estimate: 2028-Q2, drift risk high** — anchored to the latest contractual date (2028-01) plus one quarter of buffer consistent with the project's unbroken slip history

## 8. Could not determine

- Site coordinates beyond a text-distance estimate — no satellite imagery, no CAD parcel, no Google Places pin (429-blocked), no GNIS coordinate (503 down) this run
- Land tenure (leased vs. purchased) — Crockett CAD portals not scrapeable; Ch.313 application PDF (would likely state this) blocked 403 at source
- Project acreage/footprint size
- Full Ch.313 agreement/application text (app #1821 exists, confirmed via search index, but PDF inaccessible — genuine source-side block, not a skipped step)
- Whether the 2023 UKA sale process (Fractal Advisory) concluded in a sale or UKA retained the project (2026 PPA is still branded as UKA's, suggesting retention, but no explicit confirmation found)
