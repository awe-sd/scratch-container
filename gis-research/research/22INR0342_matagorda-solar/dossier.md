# Dossier — Matagorda Solar (22INR0342)

Researched 2026-07-20 · site **not located** · verdict **unclear**

## 1. Verdict

- **unclear** — queue claims `iaSigned` 2022-06-08 and financial security posted, but this scan found NO independent trace of that IA anywhere: not in the local docket-35077 text index under any TSP or name key, not in the permanent docket↔INR join table (1,743 items), not in the pre-computed SPV-candidates table (772 rows) ([log.md](log.md))
- Construction: **no_activity** (as far as observable) — zero construction milestone in 67 monthly queue snapshots since 2020; site could not be located so no imagery exists to confirm or refute
- Site: **not located** — POI text "5555 Shropshire 69kV" does not resolve to any real substation/switch in Texas via search, Nominatim, or PUCT filings ([log.md](log.md)); PLAYBOOK rule 4 forbids a county-centroid placeholder
- COD: reported 2027-08-25 → independent **not determinable**, drift risk **high** (4 prior slips, no corroborated IA, no construction, no locatable site)

## 2. Site identification

- Derivation: **none obtainable this run**. POI "5555 Shropshire 69kV" was searched via `search.py` (7+ query variants), Nominatim (bounded to Matagorda Co. and unbounded "Shropshire, Texas"), Google Places (`gmaps.py places` — HTTP 429 rate-limited on every attempt, both this run and triage), and `puct.py filings --party` swept across AEP/CenterPoint/Oncor/LCRA/TNMP/Entergy. No hit.
- **Stated project area: unknown** — no abatement/IA/CAD document found for this project to state acreage
- Cross-checks: none available — no pin, no POI match, no parcel, no map document
- Not obtainable: exact site coordinates, project boundary, land tenure

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Leeward Renewable Energy Development, LLC | developer (unconfirmed this run) | Carried from 2026-07-19 triage web search only — no primary document found this scan naming Leeward as this INR's developer |
| "Matagorda Solar, LLC" (packet name) | SPV, unverified | Identity packet only; `spv.py resolve`, `ch313.py resolve`, and `puct.py match` all returned zero candidates for this legal name |

- Financing: unknown — `financialSecurityAndNoticeToProceedProvided=Yes` is claimed in the ERCOT queue data (factsheet.json) but no LC/security amount or counterparty could be independently verified (no IA on file)

## 4. Land & county records

- Tenure: **unknown** — no parcel, lease, or CAD record found
- Abatements/agreements: **none found**. `ch313.py resolve` (by INR, by `--county Matagorda`, by `--name Tidehaven`) returned negative evidence each time. Manually scanned the full 740-row Ch.313 table for Matagorda-area solar entries: only Danish Fields Solar LLC and HIF USA LLC (both Tidehaven ISD) — neither name overlaps "Matagorda Solar"/"Leeward"
- CAD: Matagorda County Appraisal District's search portal (esearch.matagorda-cad.org) is a session-token-gated JS app; not searchable without a live browser — not pursued (web-last rule)
- Other Matagorda County solar projects found and **ruled out as different projects** (name/owner/MW mismatch): Eldora Energy/Advanced Power AG (200 MW — [gem.wiki](https://www.gem.wiki/Eldora_solar_farm)); Midfield Solar and Storage LLC/Hanwha Q Cells ($260M — [Bay City Tribune 2024-07-23](sources/)); the Tidehaven ISD 200 MW/$157.5M Ch.313 application ([Bay City Tribune 2021-04-13](sources/2026-07-20_baycitytribune_tidehaven-tax-base.html)) which matches the withdrawn sibling **22INR0441 "Milwaukee Solar"** (confirmed via `queue_history.py`: only 11 snapshots 2021-03→2022-01, never signed IA, dropped from queue), not this 101 MW project

## 5. Interconnection & contractual schedule

- POI per queue data: "5555 Shropshire 69kV" — **no signed IA document obtained**; this text is unverified against any primary filing
- Equipment: unknown — no IA exhibits available

| IA document | Signed | Financial security posted |
|---|---|---|
| — none found — | queue claims 2022-06-08 | queue claims "Yes"; amount unknown |

- `puct.py match 22INR0342` (queue name + `--key "Matagorda Solar Farm"`) returns only one candidate filing, 35077-2315 — verified by full-text extraction to be **CenterPoint's SGIA for Peyton Creek Wind Farm II, LLC (INR 20INR0155)**, a different Matagorda County project; INR-in-text check correctly flags it UNCONFIRMED. Not this project's IA.
- `puct.py filings 35077 --party <TSP>` swept AEP Texas, CenterPoint, Oncor, LCRA, TNMP, Entergy: **zero filings** mention "Matagorda", "Leeward", or "Shropshire" in the FilingDescription (AEP alone has ~60 solar SGIAs 2013–2026, none matching)
- Zero hits for INR 22INR0342 in the permanent docket↔INR join table (`_reference/puct_inr_join.json`, 1,743 items) or the pre-computed SPV-candidates table (`_reference/spv_candidates.csv`, 772 rows)
- Queue-history COD drift (from [timeline.md](timeline.md)): **4 changes** — 2023-06 → 2023-12-28 → 2025-12-27 → 2026-08-24 → 2027-08-25, across 67 monthly snapshots since 2020-12

## 6. Satellite timeline

- **No imagery pulled.** Site coordinates could not be established (see §2); PLAYBOOK rule 4 ("no county centroids") prohibits substituting a placeholder location, so no `cdse.py` chips were fetched this run.

## 7. COD assessment

- Reported 2027-08-25 is the queue's self-reported claim only — it has already slipped 4 times over ~4 years in queue, roughly one slip per year
- `iaSigned` and `financial_security=Yes` are genuine ERCOT GIS milestone flags (factsheet.json) and posting security is a real capital commitment, which argues some activity occurred — but this scan could not independently corroborate the IA through any systematic channel (docket text search across all major TSPs, permanent join table, SPV-candidates table, Ch.313/JETI, TCEQ, EIA-860M, news)
- No construction milestone reported in 67 monthly snapshots since 2020; `eia_history.py` confirms the project is **not in EIA-860M** at all (negative second-source check)
- Given zero corroborated paper trail and zero observable construction, the 2027-08-25 date (13 months from now) is not supportable as a near-term COD — a real project with a genuinely executed 2022 IA and no construction 4+ years later would be highly unusual
- **Independent estimate: not determinable; drift risk high** — recommend re-triage after attempting a live-browser CAD/PUCT lookup or waiting for the next monthly ERCOT snapshot to see if construction milestones appear

## 8. Could not determine

- Site coordinates — POI "5555 Shropshire 69kV" does not resolve on any public source (search engines, Nominatim, PUCT filings); Google Places API rate-limited (HTTP 429) on every attempt across both triage and this deep scan
- Whether the queue's `iaSigned=2022-06-08` corresponds to a real, filed IA — no matching document found anywhere in the PUCT docket-35077 index despite an exhaustive systematic sweep (name-key match, all-TSP party sweep, permanent join table, pre-computed SPV table)
- The legal SPV name (packet's "Matagorda Solar, LLC" is unverified; the triage-log candidate "Matagorda Solar Farm LLC" also unverified — both are leads, not confirmations)
- Project acreage, land tenure, EPC, offtaker — no documents found
- Construction status — cannot be visually verified without a site location
