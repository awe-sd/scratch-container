# Dossier — El Sauz Ranch (20INR0097)

Researched 2026-07-19 · site 26.497309, -97.599482 · verdict **real_active**

## 1. Verdict

- **real_active** — turbines physically erected by Feb-Mar 2022 per Sentinel-2 ([frame](imagery/key/s2_2022-03-01.png)); approved for synchronization 2023-02-28
- Construction: **substantially_complete**, first activity Oct 2021 ([frame](imagery/key/s2_2021-10-01.png))
- Site: 26.497309, -97.599482 — Google Maps Places pin "El Sauz Wind Farm Laydown", 25498 FM 3142, Raymondville TX 78580 ([map](https://google.com/maps/@26.497309,-97.599482,5000m/data=!3m1!1e3))
- COD: reported 2026-08-02 → independent **2026-Q4**, drift risk **high** (post-sync stall 40+ months, monthly slippage pattern continues)

## 2. Site identification

- Derivation: Google Maps Places API — "El Sauz Wind Farm Laydown" pin at 25498 FM 3142, Raymondville TX 78580; place type: association_or_organization (construction staging yard)
- **Stated project area: unknown** — CAD parcel search returned 404; Ch.312/313 search returned server error; IA not retrieved
- Cross-checks: Pin at FM 3142 in Willacy County matches queue county. POI "8663 EL SAUZ POI 345kV" consistent with AEP Texas Central 345kV system (Willacy County service area). Turbines visible at 10m/px scattered NE of laydown pin, consistent with wind farm extending several km east across ranch lands toward coast.
- Not obtainable: exact turbine coordinates (FAA OE/AAA unavailable — govt shutdown); POI switch location (CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| El Sauz Ranch, LLC (presumed) | SPV | ERCOT queue name; unverified |
| Unknown | Developer/owner | No press release, SEC filing, or TX SOS record retrieved |
| Unknown | EPC | Not found |
| Unknown | Offtaker/PPA | Not found |

- Financing: Unknown — no public filings found. Adjacent Avangrid projects (Magic Valley, Los Vientos) suggest Avangrid may be developer but not confirmed.

## 4. Land & county records

- Tenure: **unknown** — Willacy CAD esearch returned 404; no parcel owner data retrieved
- Abatements/agreements: None confirmed — TX Comptroller Ch.312/313 search returned server error; absence not confirmed
- CAD: Search unavailable (404 on esearch.willacycad.org direct GET)

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "8663 EL SAUZ POI 345kV" — AEP Texas Central transmission area
- IA signed per queue: 2021-01-27; PUCT Interchange returned 402, document not retrieved

| IA document | Signed | Financial security posted |
|---|---|---|
| IA (not retrieved) | 2021-01-27 per ERCOT queue | Unknown |

| Milestone | Queue date |
|---|---|
| Approved for energization | 2022-09-28 |
| Approved for synchronization | 2023-02-28 |
| Commercial operation approved | — (not achieved) |
| Reported COD | 2026-08-02 (latest; 33rd change) |

- Queue-history COD drift ([timeline.md](timeline.md)): 33 changes, 2021-09-30 → 2026-08-02 (57-month range)

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2020-06 | Pre-construction — undisturbed agricultural fields | [png](imagery/s2_2020-06-01.png) |
| 2021-06 | Early earthworks — partial clearing, road formation beginning | [png](imagery/s2_2021-06-01.png) |
| 2021-10 | **Active construction** — extensive graded land, curved access road network at turbine pad locations | [png](imagery/key/s2_2021-10-01.png) |
| 2022-03 | **Turbines erected** — multiple white T/nacelle-shadow marks in repeating regular pattern across fields | [png](imagery/key/s2_2022-03-01.png) |
| 2026-07 | Operating infrastructure — same turbine pattern present, no change in layout | [png](imagery/key/s2_2026-07-01.png) |

- Verdict: **substantially_complete** — turbines physically erected by Feb-Mar 2022; in sync testing since Feb 2023; stuck in post-sync gap. South Texas summer cloud cover limits scene quality but turbine marks confirmed in multiple clear-enough frames.

## 7. COD assessment

- Project is physically built: turbines erected ~early 2022, synchronized to grid ~Feb 2023 — construction is not the blocker
- 40+ month post-sync gap is highly anomalous; causes may include: AEP transmission upgrade required before commercial op, ERCOT voltage/stability testing failures, unresolved punch-list items, PPA terms not yet satisfied, or developer financial/permit issues
- 33 COD changes over 57 months with monthly slippage frequency — reported 2026-08-02 is implausible as final date; pattern predicts another slip
- Independent estimate: **2026-Q4** on optimistic assumption the blocker resolves in H2 2026; if grid testing / transmission upgrade is the cause, **2027-Q1** is more likely
- Drift risk: **high** — project has never held a COD for more than ~2 months since Feb 2023; each monthly slip is a separate event

## 8. Could not determine

- Developer/owner identity — no public records accessible (SEC 403, TX SOS requires paid account, Bing search blocked by CAPTCHA/grammar spam)
- Exact turbine count, turbine model, hub height — FAA OE/AAA unavailable
- IA document content — PUCT Interchange requires authentication
- Cause of post-sync commercial-op delay — no public filings found
- Project area in acres — CAD and abatement records not accessible
- Ch.312/313 tax abatement — database returned server error; existence unconfirmed
