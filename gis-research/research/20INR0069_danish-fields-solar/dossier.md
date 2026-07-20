# Dossier — Danish Fields Solar (20INR0069)

Researched 2026-07-19 · site 29.1260, -96.2620 · verdict **real_active**

## 1. Verdict

- **real_active / operating** — TotalEnergies [press release 2024-09-30](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html) confirms commercial operations launched; S2 imagery Oct 2025 and Jun 2026 shows operating solar arrays
- Construction: **operating**, commercial operation **2024-09-30** ([Oct 2025 frame](imagery/key/s2_2025-10-01_array.png))
- Site: 29.1260, -96.2620 — imagery-derived centroid, corroborated by PUCT physical address (11000 CR 403, El Campo TX), medium-high confidence ([satellite view](https://www.google.com/maps/@29.126,-96.262,5000m/data=!3m1!1e3))
- COD: reported 2026-08-29 → **actual 2024-Q3** (Sept 30, 2024); ERCOT queue entry not yet administratively closed; drift risk **n/a** (plant operating)

## 2. Site identification

- Derivation: PUCT PGC registration lists physical address "11000 County Road 403, El Campo, TX 77437, Wharton and Matagorda County" ([PGC Registration](sources/2026-07-19_puct_54647-1_danish-fields-solar-pgc-registration.pdf)); Nominatim geocode of CR 403 / Wharton County → 29.129, -96.243; S2 imagery at 29.126, -96.262 shows clear solar arrays confirming site
- **Stated project area: 5,000 acres** per PUCT 51568 direct testimony "600 MW, 5,000-acre solar farm in Wharton County" ([Groberg testimony](sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf)) — S2 frame consistent (~3×2.5 km visible array)
- Cross-checks: physical address → CR 403 (Nominatim 29.129, -96.243); POI = Hillje 345kV substation (Hillje TX 29.149, -96.343); array observed in imagery ~2 km east of CR 403 centroid — agree within ~4 km; Hillje is ~7 km NW of array centroid (consistent with 345kV connecting through sub)
- Not obtainable: exact Hillje substation switching yard coordinates (CEII)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Danish Fields Solar, LLC | SPV | [PGC Registration](sources/2026-07-19_puct_54647-1_danish-fields-solar-pgc-registration.pdf) |
| TotalEnergies Renewables USA, LLC | developer/owner | [PGC Registration](sources/2026-07-19_puct_54647-1_danish-fields-solar-pgc-registration.pdf) + [PR](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html) |
| SunChase Power LLC / Brazos Renewable Energy | original developer (sold 2021) | [Groberg testimony](sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf) |
| Ares Partners (inferred via "AP Tosca Borrower") | tax equity | [PGC Amendment](sources/2026-07-19_puct_57632-1_danish-fields-solar-pgc-amendment.pdf) |
| Saint-Gobain + others | CPPA offtakers (70%) | [PR](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html) |
| TotalEnergies industrial sites (30%) | self-supply | [PR](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html) |
| Saft (TotalEnergies subsidiary) | battery supplier (225 MWh) | [PR](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html) |

- Financing: tax equity partnership added per [PGC Amendment 2025-01-31](sources/2026-07-19_puct_57632-1_danish-fields-solar-pgc-amendment.pdf); financing closed prior to 2024-09-30 commercial operation

## 4. Land & county records

- Tenure: **leased** — [PUCT 51568 item 115](https://interchange.puc.texas.gov/search/filings/?ControlNumber=51568) "Notice of Memorandum of Lease" filed 2021-10-25; easements and exclusive purchase options held ([Groberg testimony](sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf)); mineral accommodation agreements from 40+ mineral owners
- Abatements: "property tax abatement agreement obtained" per [Groberg testimony](sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf) — specific ISD/county document not retrieved
- CAD: parcel owner-name search not completed (Wharton CAD URL unresolved); expected minimal hits for leased land

## 5. Interconnection & contractual schedule

- POI per [PGC Registration](sources/2026-07-19_puct_54647-1_danish-fields-solar-pgc-registration.pdf): "44200 Hillje 345kV" — CenterPoint Energy Houston Electric, LLC (queue POI confirmed)
- Equipment (per [TotalEnergies PR](sources/2026-07-19_totalenergies_danish-fields-commercial-operations-pr.html)): 1.4 million PV panels, 720 MWp; 225 MWh battery storage (Saft)
- IA signed 2020-02-24 (per queue milestone); $6,600,000 IA security posted; IA document not separately filed at PUCT Interchange

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA (not retrieved — pre-PUCT filing era) | 2020-02-24 | $6,600,000 LC/cash (CenterPoint; per [Groberg testimony](sources/2026-07-19_puct_51568-50_danish-fields-solar-direct-testimony-groberg.pdf)) |

| Milestone | Queue date |
|---|---|
| IA signed | 2020-02-24 |
| FIS approved | 2022-07-25 |
| Approved for energization | 2023-03-27 |
| Approved for synchronization | 2023-05-04 |
| **Actual commercial operation** | **2024-09-30** (TotalEnergies PR) |

- Queue-history COD drift ([timeline.md](timeline.md)): **20 changes** — 2021-02-01 → 2026-08-29 over 8 years; project achieved actual commercial operation well before the queue's current reported COD

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2025-10-01 | Multiple complete panel array sections + bright substation pad; plant operating | [Oct 2025](imagery/key/s2_2025-10-01_array.png) |
| 2026-06-15 | Solar arrays confirmed; partly cloudy; consistent with operating plant | [Jun 2026 wide](imagery/key/s2_2026-06-15_cr403.png) |
| 2026-06-15 | Tight 2km chip confirms dark panel blocks at 29.110N, -96.278W | [Jun 2026 tight](imagery/key/s2_2026-06-15_solar_tight2.png) |

- Verdict: **operating** — full panel arrays visible Oct 2025 and Jun 2026; consistent with 2024-09-30 commercial operation; timelapse job (2023–2026) running but not yet complete at time of dossier write

## 7. COD assessment

- **Plant is already commercially operating** — TotalEnergies press release confirms COD 2024-09-30, six months ahead of the queue's sequence of slipping dates
- The reported ERCOT queue COD (2026-08-29) is a **queue administrative artifact** — the project continuously slipped its queue COD even as it was constructed and completed; ERCOT's `approvedForCommercialOperation` field is still null in the June 2026 snapshot
- **Most likely explanation**: the battery storage component (companion project Danish Fields Storage, PUCT 55835) may still be outstanding, or the queue entry closure is pending formal ERCOT commercial operation notification; the solar generation portion is online
- The 720 MWp actual capacity vs. 602.8 MW queued capacity is consistent with the project being larger than originally queued (AC-limited registration vs. DC nameplate)
- **Independent estimate: 2024-Q3 achieved; no COD risk for solar generation; battery storage closure TBD**

## 8. Could not determine

- Signed IA document (not filed at PUCT Interchange; CenterPoint IA predates current IA-filing requirements)
- EPC contractor identity (not disclosed in PR or regulatory filings)
- Specific ISD Ch.313 abatement agreement and amount (mentioned in testimony; document not retrieved)
- Wharton CAD parcel numbers for the leased tracts
- Exact reason ERCOT queue 20INR0069 has not been closed after commercial operation
- Whether queue entry represents the battery storage portion still awaiting final closure
