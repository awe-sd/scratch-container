# Dossier — Northington Solar (25INR0319)

Researched 2026-07-20 · site not independently geocoded (text-only) · verdict **real_early**

## 1. Verdict

- **real_early** — signed IA with $11M financial security posted ([IA](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interconnection-agreem.pdf)); developer confirmed as Matrix Renewables via the signature block, no construction/financing signal yet
- Construction: **unknown** — no satellite imagery obtainable this session (CDSE credits exhausted, confirmed via direct 402 response); queue reports no construction start/end date
- Site: not independently geocoded — IA Exhibit C states Generator's own "Northington" substation is "approximately three (3) miles east of Louise, Texas" ([p35](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p35.png)); confidence **low**
- COD: reported 2027-11-30 → independent **2027-Q3** (contractual), drift risk **medium** (self-reported slip has no amendment backing it)

## 2. Site identification

- Derivation: text-only from signed IA. Exhibit C ([p35](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p35.png)): Generator's "Northington Substation" is in Wharton County "approximately three (3) miles east of Louise, Texas." POI is at TSP's first dead-end structure outside AEP's "Ursidae Station" fence.
- Cross-check: Exhibit C-1 one-line drawing ([p53](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p53.png)) places Ursidae Station ~8.9 mi from the El Campo (#8102) tap and ~4.3 mi from the Pulsar (#8192) tap along the same 138 kV line — textually consistent with the queue's own POI ("El Campo (#8102) - Pulsar (#8192) Line"), but this is a document-internal consistency check, not an independent geocode
- Not obtainable: coordinates for Ursidae Station or the Northington substation — not in OSM/Nominatim/Overpass, no other PUCT filing mentions "Ursidae" (0 hits), CDSE imagery unavailable (processing credits exhausted), gmaps.py places/staticmap returned HTTP 429 on every attempt this session

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Northington Solar, LLC | SPV | Generator party on [signed IA](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interconnection-agreem.pdf) |
| Matrix Renewables USA LLC | manager / developer | Signature block: "Northington Solar LLC, By: Matrix Renewables USA LLC, its Manager" — Cindy Tindell (Managing Director) and Philipp Rusch (CFO) both @matrixrenewables.com ([p14](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p14.png)); notice address 800 Brickell Ave Suite 901, Miami FL 33131 ([p54](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p54.png)) matches Matrix Renewables' Miami HQ |

- Financing: none announced. Matrix's 2026-06-26 close of $1.3B financing for an 859 MWdc/167 MWh portfolio (Tormes Solar TX, Alamo BESS CA, Gaskell West CA, Pleasant Valley ID) does **not** include Northington ([pv-magazine-usa.com](https://pv-magazine-usa.com/2026/06/26/matrix-renewables-secures-1-3-billion-for-u-s-solar-and-storage-portfolio/)); Matrix's own "existing projects" page also omits it ([matrixrenewables.com/existing-projects/u-s/](https://matrixrenewables.com/existing-projects/u-s/), fetched 2026-07-20) — negative evidence, consistent with pre-financing stage

## 4. Land & county records

- Tenure: **unknown** — no acreage/tenure exhibit in the IA; Wharton CAD (whartoncad.net/property-search) is a JS-rendered portal not queryable via WebFetch/curl (returns "Public Portal" shell only, no data)
- Abatements/agreements: **none found** — `ch313.py resolve 25INR0319` returns 0 Ch.313/JETI hits; expected for a post-2022 project under the JETI-only regime with no filing yet
- CAD: 0 parcels obtainable (portal not queryable this session)

## 5. Interconnection & contractual schedule

- POI per signed IA: TSP's first dead-end structure outside the fence of AEP's "Ursidae Station," terminating Generator's 138 kV line from its own Northington substation ([IA Exhibit C, p35](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p35.png)) — matches queue POI text
- Equipment (Exhibit C): nominal 129.81 MW at the inverter terminal, 39× Sungrow SG3600UD inverters at 3.3285 MW each

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interconnection-agreem.pdf)) | 2024-10-02 | $11,000,000 (LC / corporate guaranty / other TSP-acceptable collateral, [Exhibit E, p57](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p57.png)) |

(No amendment exists — `puct.py search "Northington"` returns exactly 1 filing on docket 35077.)

| Milestone | Original IA 2024 (from Execution Date 2024-10-02) |
|---|---|
| In-Service | 2027-06-02 (32 months) |
| Trial Operation | 2027-07-02 (33 months) |
| Scheduled COD | 2027-08-02 (34 months) |

([Exhibit B, p33-34](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p33.png))
- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2025-12-31 → 2026-12-01 → 2027-07-15 → 2027-11-30; in reports since 2023-02 (41 snapshots)

## 6. Satellite timeline

- **No imagery obtained.** `cdse.py chip` failed 3× with `RemoteDisconnected`; direct diagnostic `curl` to the CDSE openEO `/result` endpoint with a valid cached token returned a clean `HTTP 402 Payment Required — "You do not have sufficient credits to perform this request"`. This is account-level processing-credit exhaustion, not a transient fault, and did not resolve on retry. `gmaps.py places`/`staticmap` returned `HTTP 429` on every attempt.
- Verdict: **unknown** — cannot be determined this session; not guessed

## 7. COD assessment

- Reported 2027-11-30 is a **self-reported queue value only** — the countersigned [IA](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interconnection-agreem.pdf) computes a **contractual** Scheduled COD of **2027-08-02** (34 months from the 2024-10-02 Execution Date, [Exhibit B](sources/2026-07-19_puct_35077-1964_ercot-standard-generation-interco_p33.png))
- The queue tracked this contractual date closely for 16 months (held 2027-07-15 from 2024-12 through 2026-04, within ~2 weeks of the IA calc), then slipped ~4 months to 2027-11-30 starting the 2026-05 snapshot — but `puct.py search "Northington"` finds **no amendment** re-papering this later date; the slip is unconfirmed by any filed document
- FIS has been requested since 2023-02 and is still **not approved** as of the 2026-06 snapshot (~3.3 years pending, [timeline.md](timeline.md)) — an unusual, unexplained regulatory delay that is a more concrete schedule-risk signal than the COD claim itself
- Not in EIA-860M ([eia_history.py](https://) output, confirmed 2026-07-20) — no independent second-source cross-check; consistent with pre-construction, not decisive either way
- No construction imagery available to check observed pace against either date
- **Independent estimate: 2027-Q3 (grounded in the signed contractual schedule), drift risk medium** — weight given to the stalled FIS and the unamended self-reported slip

## 8. Could not determine

- Site coordinates for Ursidae Station or the Northington substation (text-only location, no independent geocode)
- Construction stage / first activity date (no satellite imagery — CDSE account out of processing credits)
- Land tenure (leased vs. purchased) and project acreage (no CAD access, no Ch.313/JETI filing, no acreage exhibit in the IA)
- Reason for the ~3.3-year FIS delay
- Whether the 2026-05 COD slip to 2027-11-30 reflects a real schedule change or a routine queue-data update (no amendment filed either way)
