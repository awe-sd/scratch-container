# Dossier — Caney Creek Solar (23INR0045)

Researched 2026-07-20 · site 32.5658, -95.9953 (unconfirmed by imagery) · verdict **unclear**

## 1. Verdict

- **unclear** — real IA + real money posted ([signed SGIA](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf), $4.28M cash security), but the contractual schedule on file is 3 years stale and no amendment, abatement, or EIA listing backs the current COD claim
- Construction: **unknown** — no satellite imagery obtainable this session (CDSE + Google Static Maps both unavailable, see §8); opposition-group tracker still says "Est Build start: Summer 2026" ([savevzcounty.org](sources/2026-07-20_savevzcounty_current-projects.html)), i.e. not started
- Site: 32.5658, -95.9953 — derived from signed IA's POI text ("~8.3 mi west of Canton, TX on CR 2120... tapping the Glen Pine-Explorer 138kV line") geocoded via OSM Nominatim, medium confidence, imagery-unconfirmed ([map](https://www.google.com/maps/@32.5658,-95.9953,5000m/data=!3m1!1e3))
- COD: reported 2027-06-21 → independent **2027-Q3 to 2028-Q2** (wide band), drift risk **high** (contractual date on file is 2023-06-01, unamended)

## 2. Site identification

- Derivation: IA [Exhibit C](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf) POI text geocoded against OSM Nominatim's "County Road 2120" way centroid — matches identity-packet POI "Tap 138kV 6829 Glen Pine - 6833 Explorer" exactly (same two named substations)
- **Stated project area: 600+ acres** per [savevzcounty.org](sources/2026-07-20_savevzcounty_current-projects.html) — no primary-document (IA/CAD) acreage figure found; imagery footprint consistency unverified (no imagery obtained)
- Cross-checks: savevzcounty.org independently describes "East of FM 47 and South of I20" — same general quadrant as the CR 2120 estimate but not a tight match (FM 47 lies ~5-6 mi east of the CR 2120 point); no Google Places pin (429 rate-limited all session), no CAD parcel (portal unreachable), no imagery
- Not obtainable this session: satellite confirmation, delivery pin, parcel geometry — all blocked by tooling failures, not investigated dead ends (§8)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| HEP Caney Creek Solar, LLC | SPV | Named Generator party, [signed IA](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf) |
| hep North America / hep global GmbH | developer | IA signed by Ilan Caplan, "Authorized Signatory," @hep.global email domain; matches [hep's own site](sources/) tagline "We develop, build and operate solar farms" |
| Solareit | financing (unverified) | [savevzcounty.org](sources/savevzcounty_caney_creek.md) claim only — no primary-document corroboration |

- Financing: no closed-financing announcement found (contrast Hanson Solar's PR Newswire release); only the secondary-source Solareit claim and the IA's own posted cash security
- Security: **$4,277,047 cash** posted in tiers Dec 2021 → Jun 2022 ([IA Exhibit E](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf)) — real money, but posted 4+ years ago against a schedule that has since gone stale

## 4. Land & county records

- Tenure: **unknown** — savevzcounty.org claims six landowners leased easements to HEP Caney Creek Solar LLC ([source](sources/savevzcounty_caney_creek.md)), secondary source only
- Abatements/agreements: **0 Ch.313 agreements, 0 JETI applications** ([ch313.py resolve](sources/)) — no value-limitation filing found under Caney Creek/HEP/Van Zandt
- CAD: Van Zandt CAD (esearch.vzcad.org) unreachable from this container (TLS handshake failure) — 0 parcels searched, logged as tooling gap not project signal

## 5. Interconnection & contractual schedule

- POI per signed IA: "located approximately 8.3 miles west of Canton, TX on County Road 2120 in Van Zandt County, Texas... connected to a new substation tapping the Glen Pine-Explorer 138 kV transmission line via a 0.1 mile transmission line" ([IA Exhibit C](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf))
- Equipment (Exhibit C): 33× SMA SC4200UP-US inverters, 4.2 MVA each = 121.97 MW rated

| IA document | Signed | Financial security posted |
|---|---|---|
| Original SGIA ([pdf](sources/2026-07-19_puct_35077-1353_solar-generation-interconnection-agreement-betwe.pdf)) | 2021-12-24/29 | $50,000 (NTP) → $1.45M → $3.0M → **$4,277,047** (final tier, by 2022-06-01) |

(No amendment exists — see below.)

| Milestone | Original IA (2021) |
|---|---|
| In-Service | 2023-01-20 |
| Trial Operation | 2023-02-03 |
| Scheduled COD | **2023-06-01** |

- **No amendment on file.** Exhaustive PUCT docket 35077 sweep — `puct.py match` (INR-join + name-key), manual review of all 35 Rayburn-party filings, `--match Caney`/`--match HEP`, date-range grep — found only this single 2022-01-03 filing. Other Rayburn-interconnected projects in the same docket (BT Signal Ranch, Sowers/Tanzanite/Amador Storage) each have 2-6 amendments over the same period, so the absence here is a real signal, not a search gap.
- Queue-history COD drift ([timeline.md](timeline.md)): **3 changes** — 2023-06-01 → 2024-06-01 → 2025-05-15 → 2027-06-21, none matched by a corresponding contractual amendment

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | No imagery obtained — CDSE openEO endpoint returned `RemoteDisconnected` on 10+ retries across ~20 min (shared infra saturated by 8-18 concurrent deep-scan agents in this container); Google Static Maps returned HTTP 403 (API not enabled on this project's key) | — |

- Verdict: **unknown** — no imagery evidence either way this session; savevzcounty.org's own tracker (closest available ground signal) still reads "Est Build start: Summer 2026," i.e. not yet started as of 2026-07-20

## 7. COD assessment

- Reported 2027-06-21 has **no current contractual grounding** — the only Scheduled COD on file with PUCT is the original IA's 2023-06-01, three years stale, with zero amendments filed despite three subsequent queue-level COD changes
- This absence is the decisive fact: compare Hanson Solar (23INR0086), where every queue slip was backed by a filed, countersigned IA amendment. Caney Creek's queue COD appears to be a developer/administrative update not backed by a renegotiated interconnection contract
- For: $4.28M real cash security posted (2022), project still active in the queue (not cancelled), POI/developer identity cross-checks all consistent and primary-document-grounded
- Against: not in EIA-860M, no Ch.313/JETI filing, no imagery-confirmed construction, opposition tracker says build hasn't started, no amendment despite a 4-year total slip
- **Independent estimate: 2027-Q3 to 2028-Q2 (wide band), drift risk high** — if Summer-2026 build-start holds and a ~12-18 month solar build cadence applies, this range is a schedule-logic estimate only; it is NOT imagery- or contract-confirmed and should be treated with low confidence

## 8. Could not determine

- Any satellite/imagery evidence of construction — CDSE (openEO) unavailable all session due to container-wide contention (8-18 concurrent deep-scan agents sharing the same credentials/endpoint); Google Static Maps returned a permanent 403 (API not enabled)
- Google Places delivery pin — HTTP 429 rate-limited on 5 attempts across the session
- CAD parcel records — Van Zandt CAD portal (esearch.vzcad.org) TLS-unreachable from this container
- TX Comptroller taxable-entity detail (registered agent, officers) — dynamic ASP.NET form, not fetchable headlessly
- Exact acreage from a primary document (IA/CAD/abatement) — only the secondary-source "600+ acres" claim available
- Whether an IA amendment was negotiated but never filed with PUCT (a filing-compliance question outside this agent's tools) vs. the schedule genuinely lapsing
