# Dossier — Musgravite Solar (27INR0198)

Researched 2026-07-20 · site 32.16995, -95.5803 · verdict **real_early**

## 1. Verdict

- **real_early** — independently registered in [EIA-860M](eia_history.json) as entity BT Thompson Solar, LLC / plant "Musgravite Solar," reporting "(L) Regulatory approvals pending. Not under construction" across all 13 monthly filings on file (2025-05 → 2026-05); FIS approved and financial security posted in the queue, but no IA obtained and no construction evidence
- Construction: **unknown** — CDSE imagery outage (fleet-wide, persisted the full session) blocked all satellite verification; EIA's own most recent status (2026-05 report) says not under construction
- Site: 32.16995, -95.5803 — EIA-860M coordinate cross-validated against the queue's own POI text, medium confidence ([satellite view](https://www.google.com/maps/@32.16995,-95.5803,5000m/data=!3m1!1e3))
- COD: reported 2027-11-01 → independent **2028-Q1**, drift risk **high** (no signed IA, no construction evidence, one prior slip)

## 2. Site identification

- Derivation: EIA-860M plant-name match gives 32.16995,-95.5803 (`spv.py resolve` / [eia_history.json](eia_history.json)); cross-checked against the queue's own POI text "Tap 138 kV (6855) Coffee - (6849) New York" — Coffee City, TX (32.1160,-95.4994) and New York, TX (32.1700,-95.6700) are both real, independently confirmed Henderson County places (Wikipedia via `search.py`+WebFetch, not a queue aggregator); the EIA point sits 3.0 km from the Coffee↔New York midpoint and is roughly equidistant from both endpoints (9.7 km / 8.4 km) — geometrically consistent with a mid-span tap
- **Stated project area: not obtainable** — no abatement/IA/CAD document on file; imagery footprint unverifiable (CDSE outage)
- Cross-checks: triage's LaRue web-aggregator guess (32.1169,-95.6747) is off-axis to the POI geometry (16.5 km from Coffee vs. 5.9 km from New York — lopsided, not consistent with a tap between the two named points) and traces only to banned-adjacent tracker sites — **superseded, not used**
- Not obtainable this run: parcel-level confirmation (CAD requires interactive form submission), Google Places pin (429 rate-limited throughout), satellite imagery (CDSE outage throughout)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| BT Thompson Solar, LLC | SPV (unverified against any INR-bearing document) | [EIA-860M](eia_history.json) plant-name match; TX SOS File #0805261272 filed 2023-10-11, Farmers Branch TX (triage web sweep, no artifact saved) |
| Belltown Power Texas LLC | possible parent (lead only) | naming pattern "BT \<Surname\> Solar/Storage, LLC" matches multiple confirmed Belltown Power Texas IA filings in the PUCT docket (e.g. "BT Majewski Storage," "BT McMurtre Storage" — both Oncor filings, seen while searching the 2025-05 docket window); no document directly ties BT Thompson Solar to Belltown |

- Financing: no information found — no press coverage of Musgravite Solar exists under any name tried (`search.py`, multiple queries, see log.md)

## 4. Land & county records

- Tenure: **unknown** — no parcel, abatement, or news document obtained
- Abatements/agreements: **negative** — `ch313.py resolve 27INR0198`: no Ch.313 or JETI match for "Musgravite Solar." Expected for a project SOS-filed Oct 2023 (post-Ch.313 sunset); no JETI application found either
- CAD: Henderson County Appraisal District has an owner-name search portal (esearch.henderson-cad.org) but requires interactive form submission — not reachable via WebFetch this run; not searched

## 5. Interconnection & contractual schedule

- POI per queue: "Tap 138 kV (6855) Coffee - (6849) New York" — used as the independent site cross-check (§2); no signed IA obtained to confirm this text against a primary document
- **No IA document obtained.** Queue claims `iaSigned`=2025-05-20 with financial security posted ("Yes"), but an exhaustive systematic search found nothing:
  - PUCT rung 0 (docket↔INR join table, 1,743 items): 0 matches for "27INR0198"
  - PUCT rung 1 (exact name keys: "Musgravite Solar," "Musgravite"): 0 candidates
  - PUCT rung 2 (registry resolvers): `ch313.py` negative, `tceq.py` negative (no mandatory paper trail expected for solar anyway)
  - PUCT rung 3 (SPV name "BT Thompson Solar," parent lead "Belltown Power"): 0 exact-name candidates; 2 coincidental matches surfaced and were **verified as different projects** — Tanzanite/Sowers Storage (22INR0549/22INR0552, Belltown Power via Rayburn Electric Coop) and Sol Marina Energy Center (26INR0241/26INR0242, Adapture Solar via Oncor, filed the same day as Musgravite's claimed signing) — both discarded, not cited
  - Ad-hoc docket window scan (±5 days around 2025-05-20, all TSPs, 8 filings total): none reference Musgravite, BT Thompson, or Henderson County
  - `puct.py filings --match "Thompson"` / `puct.py search --field desc`: 0 results anywhere in the docket-35077 index
- Milestone table and financial-security amounts: **not obtainable** — no IA on disk
- Queue-history COD drift (from [timeline.md](timeline.md)): **1 change** — 2027-05-28 → 2027-11-01 (shifted at the 2025-10-01 snapshot); in reports since 2024-03-01 (28 snapshots)
- Anomaly: the queue's `iaSigned` milestone (2025-05-20) did not first appear in ERCOT's own monthly report until the **2026-02-01** snapshot — a 9-month lag between claimed signing and its first appearance in reported data

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| — | **No imagery obtained.** CDSE (Sentinel-2 provider) suffered a fleet-wide capacity outage (`RemoteDisconnected`, escalating 15s/45s/120s backoff) for the entire duration of this run — confirmed by a separate container-wide probe/watchdog process also observed failing. Retried at start, middle, and end of session; never recovered. | — |
| 2026-06 (superseded site) | Triage's 3 chips were taken at the LaRue web-guess coordinates (now superseded) — 50-70% cloud cover, rural/agricultural, no arrays visible in clear windows; low evidentiary value since the site itself is wrong | [triage chips](imagery/) |

- Verdict: **unknown** — no imagery exists at the corrected, POI-cross-validated coordinates. Cannot confirm or rule out construction activity this run.

## 7. COD assessment

- Queue-reported COD (2027-11-01) has slipped once already (from 2027-05-28, at the 2025-10-01 snapshot), before any construction evidence exists either way ([timeline.md](timeline.md))
- EIA-860M second source ([eia_history.json](eia_history.json)) is materially consistent with the queue: planned COD **2027-12** (1 month later) across all 13 monthly reports on file (2025-05 → 2026-05) — but its status field has read **"(L) Regulatory approvals pending. Not under construction"** unchanged for that entire window, most recently as of the 2026-05 report
- No signed IA obtained despite an exhaustive search (§5) — the queue's `iaSigned` claim and financial-security posting remain contractually unverified by any primary document
- No satellite imagery to independently confirm or contradict EIA's "not under construction" read (CDSE outage, §6)
- For a 100.6 MW solar project with no confirmed construction start as of the latest independent report (2026-05), a 2027-11/12 COD requires breaking ground within the next few months and a fast (~18-month) build — plausible but with little slack, and resting entirely on self-reported planning dates rather than a contractual milestone schedule
- **Independent estimate: 2028-Q1, drift risk HIGH** — one quarter later than the queue claim, reflecting EIA's slightly later planned date and the total absence of a grounding contractual document or visual construction evidence

## 8. Could not determine

- Whether an IA has actually been signed/filed — the queue's claim is unverified by any PUCT document despite an exhaustive systematic search
- Construction status — CDSE (satellite imagery) was down fleet-wide for the entire session
- Any parcel, acreage, or land-tenure detail — CAD and county records require interactive form submission not reachable via WebFetch
- Developer/parent company beyond a naming-pattern lead (Belltown Power Texas) — no document directly confirms the link
- Any financing, EPC, or offtake information — zero press coverage found under any name variant tried
