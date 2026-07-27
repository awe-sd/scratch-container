# Dossier — Trailblazer Solar (27INR0578)

Researched 2026-07-19 · site **not determined** · verdict **unclear**

## 1. Verdict

- **unclear** — Project entered queue only 4 months ago (2026-03); no developer identified, IA not signed, FIS not approved, zero construction visible across estimated site area
- Construction: **pre-construction / no_activity**, first activity not seen ([2026-07 frame](imagery/s2_2026-07-01_center.png))
- Site: **not determined** — no delivery pin (GMaps rate-limited), no parcel, no news; POI "Sweetwater East Switch 345 kV" east of Sweetwater TX but exact location not derivable without artifact
- COD: reported 2027-12-12 → independent **2029-Q1 or later**, drift risk **high** (no IA, no FIS, 17.5 mo to reported COD impossible)

## 2. Site identification

- Derivation: **none** — no artifacts found. POI = "Sweetwater East Switch 345 kV" in Nolan County; Sweetwater TX at [32.47°N, 100.41°W](https://www.google.com/maps/@32.47,-100.41,5000m/data=!3m1!1e3); "East Switch" implies ~5-15 mi east but no public coords found
- **Stated project area: unknown** — no abatement, IA, or CAD records found; imagery footprint unverifiable
- Cross-checks: none achievable — no pin, no parcel, no article, no OSM substation node for "Sweetwater East"
- Not obtainable: exact "Sweetwater East Switch" coordinates (AEP Texas; not in public OSM or ERCOT open data)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Trailblazer Solar, LLC | SPV (presumed) | Queue identity packet only — not confirmed via TX Comptroller (portal redirects, no searchable via WebFetch) |
| Unknown | Developer/parent | No PR, SEC filing, web article, or LinkedIn post found in any search |
| Unknown | EPC | Not identified |
| Unknown | PPA offtaker | Not identified |

- Financing: not identified; no press release or financial announcement found

## 4. Land & county records

- Tenure: **unknown** — no CAD parcel hit (nolancad.org DNS not found; no other CAD portal accessible)
- Abatements: no Ch.313/JETI or Ch.312/380 agreement found for "Trailblazer Solar" or Nolan County solar projects via TX Comptroller (navigation-only pages, no database queries possible via WebFetch)
- CAD: 0 hits — CAD portal unavailable (DNS resolution failed for nolancad.org)

## 5. Interconnection & contractual schedule

- IA: **not signed** per queue history (4 snapshots 2026-03 → 2026-06, iaSigned = null throughout)
- PUCT Interchange: 402 Payment Required — could not access to search for IA filings
- No IA documents found; no equipment or POI confirmed from signed documents

| IA document | Signed | Financial security posted |
|---|---|---|
| — | Not yet signed | — |

| Milestone | Queue status (2026-06-01) |
|---|---|
| Screening started | 2026-03-18 |
| Screening complete | 2026-06-15 |
| FIS requested | 2026-03-11 |
| FIS approved | **Not yet** |
| IA signed | **Not yet** |
| Financial security | **Not yet** |

- Queue-history COD drift ([timeline.md](timeline.md)): **0 changes** — COD 2027-12-12 stable since first appearance 2026-03-01 (4 snapshots)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2026-07 | Undisturbed West Texas rangeland across ~18 km radius from Sweetwater city | [center](imagery/s2_2026-07-01_center.png) |
| 2026-07 | Sweetwater city and surroundings: no graded polygons, no racking | [sweetwater](imagery/s2_2026-07-01_sweetwater.png) |
| 2026-07 | NE Nolan County along I-20 corridor: undisturbed rangeland | [northeast](imagery/s2_2026-07-01_northeast.png) |

- Verdict: **no_activity** — no solar construction signature in any chip covering estimated site area. Consistent with pre-construction queue state.
- Caveat: exact site location unconfirmed — cannot guarantee the actual parcel was imaged.

## 7. COD assessment

- Reported COD 2027-12-12 is 17.5 months from today (2026-07-19). FIS not yet approved.
- Critical path minimum: FIS approval (≥6 mo) → IA execution (≥3 mo) → procurement + construction (≥18 mo for 323 MW) = ~27 months minimum from today = **Q3 2028 at earliest**
- Optimistic case (FIS fast-tracked, IA quick): COD late 2028; independent estimate **2029-Q1** reflects realistic FIS + build schedule
- No developer, no EPC, no PPA, no financing identified — zero external maturity signals
- Zero COD drift is uninformative: project too new; drift typically emerges after first 6-12 months in queue
- **Independent estimate: 2029-Q1 or later, drift risk high**

## 8. Could not determine

- Developer/parent company (no web presence; TX Comptroller POST search unavailable via WebFetch; PUCT Interchange requires login)
- Exact site location (Google Places rate-limited; no parcel, CAD, or news artifact; AEP Texas maps not publicly accessible)
- Whether LLC is even registered (TX SOS / TX Comptroller not queryable via WebFetch)
- Project area in acres (no abatement application, no IA found)
- Whether FIS study timeline will extend further — ERCOT queue is congested; FIS studies frequently take 12-18+ months
