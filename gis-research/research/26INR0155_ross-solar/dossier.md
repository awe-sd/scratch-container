# Dossier — Ross Solar (26INR0155)

Researched 2026-07-18 · site unresolved · verdict **paper**

## 1. Verdict

- **paper** — no signed IA obtainable, no LCs posted (`financialSecurityAndNoticeToProceedProvided` = "No"), no FIS-approval milestone in 36 monthly snapshots, developer S&S Renewables has near-zero public footprint, POI target "Static" is not a public ERCOT/CCN transmission asset. Multiple stage-1/2 threads dry-holed.
- Construction: **no_activity** — no site to observe; queue milestones show no construction start through [2026-06 snapshot](timeline.md)
- Site: **unresolved** — playbook rule 4 (no county centroids) applied
- COD: reported 2027-07-31 → independent **unknown**, drift risk **high** (no anchoring contractual doc, no security posted, unbuilt tap)

## 2. Site identification

- Derivation: **could not derive**. No delivery pin (gmaps 429-rate-limited across all retries), no CAD parcel hit (refugiocad.org blocks server-side owner search — API returns 500 without JS session, [search response](sources/cad_v3.json)), no IA map (no PUCT filing under any LLC variant, [PUCT search summary](sources/puct_search_summary.md)), no news/drone photo, no OpenInfraMap "Static" node
- **Stated project area: unknown** — no abatement/IA/CAD document obtained. Rule-of-thumb 1,025.57 MW solar ≈ 5,000–9,000 ac is a derivation, not evidence
- Cross-checks: only Angstrom endpoint is geolocatable — "4 mi east of Sinton, 0.5 mi N of SH 188" in San Patricio County ([PUCT Docket 51912 Final Order §9, p.4](sources/2026-07-18_puct_51912_174_final_order.pdf)); Static is not on the Angstrom-Grissom (docket 51912) or Angstrom–SDI Buffalo (docket 50726) or Angstrom–Naismith (docket 52656) approved routes
- Not obtainable: site parcel (Refugio CAD JS-required); IA POI map (no PUCT filing); developer PR; Static substation coordinates (no public record found)

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Ross Solar, LLC | presumed SPV | naming convention; TX Comptroller franchise-tax registry returned NO record ([search](sources/2026-07-18_comptroller_search_ross_solar.json), [search-LLC](sources/2026-07-18_comptroller_search_ross_solar_llc.json)) |
| S&S Renewables, LLC | interconnecting entity | ERCOT queue field; TX Comptroller taxpayer 32087260116, mailing zip 97008 = Beaverton, OR ([Comptroller record](sources/2026-07-18_comptroller_ss_renewables.json)) |
| Parent / developer | unknown | Oregon SOS business search JS-gated / captcha; no press releases, no LinkedIn, no other ERCOT-queue projects surfaced under S&S Renewables |
| EPC / offtaker | unknown | none found |

- Financing: **no evidence** — LCs not posted (`financialSecurityAndNoticeToProceedProvided` = "No" in latest [snapshot](timeline.md)); no financing PR; no green-bond or tax-equity mention

## 4. Land & county records

- Tenure: **unknown** — Refugio CAD portal blocks automated owner search
- Abatements/agreements: **none found** — Ch.313 expired 2022 before project entered queue 2023-07 (expected absence); no JETI filing surfaced (comptroller portal not searchable via WebFetch); commissioners-court minutes not indexed for keyword search
- CAD: 0 obtainable hits under any owner variant (portal returns 500 on server-side search API without JS session)

## 5. Interconnection & contractual schedule

- POI per queue: "tap 345kV 8249 Angstrom – 8676 Static". Angstrom = existing AEP Texas 345 kV station ~4 mi E of Sinton, San Patricio County ([CCN Order, p.4](sources/2026-07-18_puct_51912_174_final_order.pdf)). **Static: no public record** — PUCT case-style + FilingDescription searches for "Static Substation"/"Static Switch" return 0 records; likely a proposed IE-owned tap facility, not yet built
- Signed IA: **not obtainable** — PUCT Interchange FilingParty + Case Style searches for "Ross Solar" / "Ross Solar, LLC" / "S&S Renewables" / "S&S Renewables, LLC" all returned 0 records ([search summary](sources/puct_search_summary.md)); AEP Texas Central IAs for generation interconnections are not routinely filed at PUCT under the generator's name
- Equipment: unknown (no IA exhibits)

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA — reported by ERCOT queue only | 2024-06-27 | **None** (`financialSecurityAndNoticeToProceedProvided` = "No") |

| Milestone | Original IA | Reported COD |
|---|---|---|
| In-Service | unknown | — |
| Trial Operation | unknown | — |
| Scheduled COD | — | 2027-07-31 (queue) |

- Queue-history COD drift ([timeline.md](timeline.md)): **1 change** — 2026-03-31 → 2027-07-31 (Oct 2023, pre-IA); held stable across 32 subsequent snapshots
- Queue anomaly: `fisApproved` NEVER populated across all 36 monthly snapshots, yet `iaSigned` = 2024-06-27 — unusual ordering (milestones are independent gates but this pair typically comes together)

## 6. Satellite timeline

Imagery **skipped** — no defensible site candidate. Per PLAYBOOK stage-3 "nothing better than somewhere in the county → SKIP imagery, log no site candidate" ([log.md T6, T10](log.md)).

Substitute evidence: queue milestones through 2026-06 snapshot show no `constructionStart`/`approvedForEnergization`/`approvedForSynchronization`/`approvedForCommercialOperation` — internally consistent with `no_activity`.

## 7. COD assessment

- **Contractual grounding: absent.** Unlike Hanson (23INR0086) where PUCT Amendment 1 anchored the COD to a signed 2027-04-17 date, Ross Solar's reported 2027-07-31 has NO independently readable IA text — the queue field is the only source.
- **No financial security posted.** For a 1 GW+ project ~3 years from claimed COD, LCs would normally be in place; their absence is a strong paper-project signal.
- **Unbuilt tap.** "Static" substation is not a public ERCOT/CCN facility — construction of the interconnection itself would need to precede or overlap the generator build, adding uncertainty.
- **Developer capacity unproven.** S&S Renewables has no discoverable portfolio, no other ERCOT projects under this LLC, no press coverage — inconsistent with executing a 5,000–9,000-acre solar farm on a 3-year timeline.
- **Independent estimate: unknown, drift risk high.** A 2027-Q3 COD is not credible on current evidence; a paper cancellation or multi-year slip is more likely than the reported date.

## 8. Could not determine

- Site coordinates (no derivable method — CAD JS-gated, no gmaps pin, no IA map, no news photo)
- Signed IA text, POI schedule exhibit, LC amount (no PUCT filing under any name variant)
- Ross Solar, LLC parent chain (S&S Renewables OR-based, SOS site JS-captcha'd; no press disclosure)
- "Static" substation location and ownership (not in any public database searched)
- Land tenure and parcel acreage (Refugio CAD portal blocks automated access)
- Whether the missing FIS-approval milestone is a data anomaly or an unresolved technical hold
