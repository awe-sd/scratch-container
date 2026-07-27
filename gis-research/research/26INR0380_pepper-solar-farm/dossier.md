# Dossier — Pepper Solar Farm (26INR0380)

Researched 2026-07-20 · site 31.6784, -97.0460 · verdict **real_early**

## 1. Verdict

- **real_early** — countersigned [IA](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf) + $17M LC posted, ownership sold OCI Energy → Sabanci Renewables for cash ([PR Newswire](sources/2026-07-20_prnewswire_oci-sabanci-sale.html)), but no verified construction activity yet
- Construction: **unclear** — imagery inconclusive, could not distinguish site clearing from ordinary tilled cropland ([grid chip](imagery/s2_grid_5_31.6784_-97.0460_2026-07-01.png))
- Site: 31.6784, -97.0460 — EIA-860M coords × [GEM Wiki](sources/2026-07-20_gemwiki_pepper-solar-farm.html) independent cross-match ("exact"), medium-high confidence
- COD: reported 2027-09-20 → independent **2027-Q3**, drift risk **low-medium** (schedule steady in queue/EIA, but developer's own FNTP date has already slipped ~5 months past the IA's)

## 2. Site identification

- Derivation: EIA-860M plant coords (31.67836, -97.04595) independently matched by Global Energy Monitor's Global Solar Power Tracker, which states 31.6784, -97.0460 "(exact)" ([GEM wiki](sources/2026-07-20_gemwiki_pepper-solar-farm.html)) — two independent sources agree to 4 decimals
- Cross-checks: IA POI text "proposed Axtell Switch...within TSP's Tradinghouse S.E.S. Switch – Elm Mott Switch 345 kV line," McLennan County ([IA Exhibit C](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf)) matches queue POI description verbatim
- Not obtainable: exact site-location sentence in IA Exhibit C item 2 is **redacted** (black bar in the filed PDF); Google Places delivery-pin check rate-limited (429) both in triage and this session — never resolved
- **Stated project area: not found.** No acreage figure in the IA (Exhibit C states no tract size) or in any news source; sister project Lucky 7 (Hopkins Co.) is reported at 745 acres but Pepper's is never stated. Imagery footprint therefore cannot be sanity-checked against a documented acreage.

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Pepper Solar Farm, LLC | SPV | party on [IA](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf) |
| OCI Energy LLC | original developer (sold 2025-07-15) | [PR Newswire](sources/2026-07-20_prnewswire_oci-sabanci-sale.html) |
| Sabanci Renewables (Sabancı Holding, Turkey) | current owner/developer post-acquisition | [PR Newswire](sources/2026-07-20_prnewswire_oci-sabanci-sale.html); [Sabanci project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) |
| Signal Energy | EPC | [Sabanci project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) |
| Waaree | module supplier | [Sabanci project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) |
| Game Change | tracker supplier | [Sabanci project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) |
| (PPA offtaker) | **under exclusivity, not signed** | [Sabanci project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) |

- Financing: Sabanci Renewables acquired the project outright (cash sale from OCI Energy, 2025-07-15); no separate non-recourse project-financing close specifically documented for Pepper in primary sources found this session — earlier triage cited a combined $533M Sabanci financing figure covering Pepper + Lucky 7, sourced from Mercom Capital (see log.md T3, not re-verified against a primary filing this session)
- PPA note: Sabanci's own project page states PPA "**Under exclusivity**" (not fully executed) as of this scan — this is a downgrade from triage's T3 claim of a signed 100%-to-Meta PPA, which should be treated as premature/unconfirmed press framing

## 4. Land & county records

- Tenure: **unknown** — IA Exhibit C land clauses are generic ERCOT-template boilerplate (no site-specific statement); Sabanci's page lists "Site Control Completed" but doesn't specify leased vs. purchased
- Abatements/agreements: **none found** — Ch.313/JETI registry search returned 0 hits (`ch313.py resolve`, triage T5); normal for a 2024-formed LLC post-Ch.313 sunset, not a paper-project signal given the IA + LC + acquisition are all confirmed
- CAD: **not searched** — McLennan CAD portal (esearch.mclennancad.org) is TLS-unreachable from this tooling (handshake failure via curl; hostname/cert mismatch + "socket closed" via WebFetch); parcel/owner-name search could not be performed

## 5. Interconnection & contractual schedule

- POI per signed IA: "proposed Axtell Switch to be located within TSP's Tradinghouse S.E.S. Switch – Elm Mott Switch 345 kV line," McLennan County ([IA](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf), [Amend 1](sources/2026-07-19_puct_35077-2196_amendment-no-1-to-the-standard-generation-interc.pdf))
- Equipment (Exhibit C): 33× solar inverters (HEM_GENIII-FS4010M), 4.01 MVA each, 32.33 MVA gross / 122.28 MW at generator terminals / 120.69 MW at 34.5kV bus

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([pdf](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf)) | 2025-06-23 | $16,987,109.00 irrevocable LC, effective on/before 2025-07-01 |
| Amendment 1 ([pdf](sources/2026-07-19_puct_35077-2196_amendment-no-1-to-the-standard-generation-interc.pdf)) | 2025-07-02/03 | $16,987,109.00 — unchanged amount; only the effective/NTP date moved to 2025-07-11 |

| Milestone | Original IA 2025 | Amendment 1 2025 |
|---|---|---|
| In-Service | 2027-05-13 | 2027-05-13 (unchanged) |
| Trial Operation | 2027-05-23 | 2027-05-23 (unchanged) |
| Scheduled COD | 2027-09-20 | 2027-09-20 (unchanged) |

- Queue-history COD drift ([timeline.md](timeline.md)): **2 changes** — 2026-07 (initial screening estimate) → 2027-07 → **2027-09-20**, current since 2025-05-01 (14 consecutive monthly snapshots stable)
- **Divergent signal:** Sabanci's own project page ([source](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html)) states **Final NTP: 12 Dec 2025** — five months later than the IA's July 2025 NTP-to-proceed date — implying the pre-construction schedule has already slipped even though the queue/IA COD field hasn't moved

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07-01 | Reddish-tan geometric polygons at site candidate, but the same coloring appears scattered across all 4 grid chips (up to ~6 km away) — consistent with regional tilled/fallow cropland, not a confirmed disturbance signature | [grid_5 frame](imagery/s2_grid_5_31.6784_-97.0460_2026-07-01.png) |

- Verdict: **unclear** — CDSE API was unavailable this entire session (`RemoteDisconnected` on 6+ retries over ~25 min, likely fleet contention from concurrent deep-scan agents; token cache was valid, ruling out a credentials issue). The mandatory pre-2025 baseline comparison and a proper look-around grid could not be obtained. Triage's "activity_visible" call is **not corroborated** — the same tan/pink hue recurs region-wide and is not site-specific in the imagery available.

## 7. COD assessment

- Reported 2027-09-20 is the **contractual** Scheduled COD in the signed [IA](sources/2026-07-19_puct_35077-2195_standard-generation-interconnection-agreement-be.pdf), reissued unchanged in [Amendment 1](sources/2026-07-19_puct_35077-2196_amendment-no-1-to-the-standard-generation-interc.pdf) — this is the source of the queue figure, not independent confirmation of it
- Independent corroboration: Sabanci's [acquisition PR](sources/2026-07-20_prnewswire_oci-sabanci-sale.html) (2025-07-15) and [project page](sources/2026-07-20_sabanciclimatetech_pepper-project-detail.html) both separately state "Q3 2027" — three sources (IA, PR, project page) converge on the same quarter
- Risk: FNTP on Sabanci's own page (Dec 2025) is 5 months later than the IA's original NTP date (Jul 2025), suggesting real schedule pressure at the pre-construction stage that hasn't yet propagated to the queue's COD field; EIA-860M ([eia_history.json](eia_history.json)) has held status at "(P) Planned for installation, but regulatory approvals not initiated" across all 18 monthly reports through 2026-05 — no construction-stage upgrade registered there either
- For: countersigned IA, $17M LC posted and unchanged through one amendment, outright acquisition by a well-capitalized parent (Sabancı Holding), three independent sources agreeing on Q3 2027
- Against: PPA still "under exclusivity" not signed per the developer's own page; no verified construction activity in available imagery; EIA has not moved the project past planning status
- **Independent estimate: 2027-Q3, drift risk low-medium** (contractually grounded and multiply corroborated, but the FNTP slip and absent construction confirmation keep this from "low")

## 8. Could not determine

- Construction stage (clearing/racking/complete) — CDSE imagery API unavailable all session; no baseline or look-around imagery beyond triage's 4 same-day grid chips
- Project area/acreage — not stated in the IA or any source found
- Land tenure (leased vs. purchased) — McLennan CAD portal unreachable (TLS failure)
- Exact site-location text in IA Exhibit C — redacted in the filed PDF
- Current PPA offtaker/status beyond "under exclusivity" as of the Sabanci project page
- Whether the $533M Sabanci financing figure (Mercom Capital, cited in triage) applies specifically to Pepper vs. the combined Pepper+Lucky7 portfolio — not re-verified against a primary filing this session
