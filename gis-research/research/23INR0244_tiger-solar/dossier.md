# Dossier — Tiger Solar (23INR0244)

Researched 2026-07-19 · site 32.5430, -99.6190 · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA on file at PUCT, $32.7M financial security required, dedicated 345-kV CCN filed and contested/decided; no construction visible yet ([CCN route map](sources/2026-07-19_puct_58405_ccn-route-map.jpg))
- Construction: **no_activity** confirmed, no NTP/construction dates in queue through Jun 2026
- Site: 32.5430, -99.6190 — dual cross-check (4.55-mi bearing from Fort Phantom Switchyard + 2.3 mi north of CR 195/US-277), medium-high confidence ([map](https://www.google.com/maps/@32.543,-99.619,5000m/data=!3m1!1e3))
- COD: reported 2027-06-30 → independent **2027-Q3**, drift risk **medium** (CCN contest adds transmission delay; 3 prior slips)

## 2. Site identification

- Derivation: two independent CCN descriptions converge — (a) "4.55-mile line from Phantom Hill Station (NW corner of CR 185 & CR 186)" [Fort Phantom Switchyard at 32.5826, -99.6823 confirmed via OSM Overpass]; (b) "collector station located along CR 195 approximately 2.3 miles north of intersection of CR 195 and US-277" ([CCN application](sources/2026-07-19_puct_58405-2_ccn-app-p1-100.pdf))
- **Stated project area: not recovered** — CCN route map shows footprint boundary; ~750-1,000 acres estimated at 3-4 ac/MW for 250 MW
- Cross-checks: Phantom Hill Station coords (OSM) → 4.55 mi at ~128° = (32.543, -99.619); CR 195/US-277 at ~32.510N + 2.3 mi north = 32.543N ✓; CCN aerial map ([route map](sources/2026-07-19_puct_58405_ccn-route-map.jpg)) confirms Proposed Substation in SE quadrant ~4.5 mi from Phantom Hill
- Not obtainable: exact POI coordinates (not explicitly stated), precise project boundary acreage, Google Places pin (API 429)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Vaca Del Sol, LLC | SPV/Generator | party on [IA](sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf), 700 Universe Blvd Juno Beach FL |
| NextEra Energy Resources, LLC | indirect parent of Vaca Del Sol | [CCN app](sources/2026-07-19_puct_58405-2_ccn-app-p1-100.pdf): "indirect, wholly owned subsidiary" |
| Lone Star Transmission, LLC | TSP (NextEra affiliate) | [IA](sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf) Exhibit D: same Juno Beach FL address |
| Unknown | EPC | not found — no construction news, no press releases |
| Unknown | PPA offtaker | not found |

- Financing: no project-finance PR found; parent NextEra Energy Resources is investment-grade; $32.7M security requirement in IA

## 4. Land & county records

- Tenure: **unknown** — Jones County CAD returned 0 hits for Vaca Del Sol / Tiger Solar (JS-rendered portal, no API access). CCN Attachment 2 names Waddell family landowners for the transmission ROW; solar array landowners not identified.
- Abatements: **none found** — JETI portal 404; no Ch.313 hit. Normal for post-2022 project (Ch.313 expired Dec 2022, JETI launched 2023 but Tiger Solar not found).
- CAD: 0 parcels under Vaca Del Sol, Tiger Solar, or NextEra in Jones County

## 5. Interconnection & contractual schedule

- POI per signed IA: Phantom Hill 345 kV substation, Jones County TX ([IA](sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf) Exhibit C); "4.55-mile 345 kV line from TSP's Phantom Hill 345 kV station to GIF Step Up Station"
- Equipment (Exhibit C): 72 × PE FS4105M inverters, 4.105 MVA each = **255 MW** total
- CCN: PUCT docket 58405, Lone Star Transmission CCN for dedicated 345-kV spur; ENGIE contested (SOAH hearing); SOAH Proposal for Decision issued May 2026, no-exceptions Jun 2026 — approval expected

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf)) | 2024-10-30 | $32,710,000 (Irrevocable Standby LC or Corporate Guaranty) |

| Milestone | IA Exhibit B (2024) |
|---|---|
| NTP Need Date | 2024-11-01 |
| TIF In-Service (Backfeed) | 2026-11-06 |
| Trial Operation (Synchronization) | 2026-11-14 |
| Scheduled COD | **2027-06-30** |

- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2023-12-01 → 2026-10-15 → 2028-03-15 → 2027-06-30 (current)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2023 (map background) | Undisturbed agricultural land at project footprint | [CCN route map](sources/2026-07-19_puct_58405_ccn-route-map.jpg) |
| 2026-06 (triage partial) | 2 of 9 chips retrieved; southern grid shows agriculture/lake, no construction | triage (CDSE 401 in deep scan) |

- Verdict: **no_activity** — no construction visible in any available imagery; CDSE unavailable in deep scan (401 auth error); CCN 2023 aerial confirms undisturbed fields at Tiger Solar footprint

## 7. COD assessment

- Contractual COD 2027-06-30 is confirmed in countersigned [IA Exhibit B](sources/2026-07-19_puct_35077-1966_tiger-solar-IA.pdf) — grounded in primary document
- CCN for dedicated 345-kV transmission spur was contested by ENGIE (PUCT docket 58405); SOAH decided in Lone Star's favor (Proposal for Decision May 2026, no-exceptions Jun 2026); CCN approval likely but adds ~1-2 month uncertainty to transmission construction start
- CCN transmission construction schedule: start May 2026, energize Oct 2026, complete Dec 2026 — must complete before IA TIF In-Service Date of Nov 6, 2026; timeline is tight and contingent on CCN order issuance
- No construction start date filed in ERCOT queue through Jun 2026 — as of research date there is no evidence site construction has begun; if NTP was not issued by Nov 2024 Need Date, all IA dates extend day-for-day
- Pattern: 3 prior COD slips (original 2023-12-01 has slipped ~3.5 years); most recent target has held ~2 years
- **Independent estimate: 2027-Q3, drift risk medium** — contractual dates are real, developer is credible, but transmission CCN contest + no visible site prep as of mid-2026 = moderate slip probability of 1-2 quarters

## 8. Could not determine

- Exact project boundary acreage (CCN footprint map has scale but not extracted)
- Land tenure (0 CAD hits; leased parcels likely)
- EPC contractor (no press releases or construction news found)
- PPA offtaker (no public announcement found)
- Whether NTP was issued to Lone Star by the Nov 1, 2024 Need Date (not in public filings)
- Current construction status at site (CDSE 401 in deep scan; no Google Maps pin)
