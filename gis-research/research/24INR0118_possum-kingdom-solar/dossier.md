# Dossier — Possum Kingdom Solar (24INR0118)

Researched 2026-07-19 · rescanned 2026-07-21 · site resolved (high confidence) · verdict **real_early**

## 1. Verdict

- **real_early** — IA executed 2025-07-30 (filed PUCT 2025-08-26); $15,508,166 combined
  financial security posted (Irrevocable Standby Letter of Credit, shared with companion
  BESS 24INR0375); Ch.313 tax-abatement agreement #1728 (Graford ISD) has been live since
  2022-11-21 and was still being administratively amended as recently as 2026-03-05;
  developer chain resolved to Nadara (a substantial international renewables group). This
  is a real, financially/administratively active project.
- Construction: **not started** — 5-date Sentinel-2 imagery (2024-07 → 2026-07) plus a wide
  verification frame show zero grading/panel rows at the resolved site through the latest
  clear acquisition (2026-07-07), despite the IA's own Notice-to-Proceed date (2025-07-01)
  being over a year in the past.
- Site: **resolved** to 33.0318°N, -98.2947°W (Jack County, near the Palo Pinto County line,
  ~7 mi NNW of Graford) — see `sources/SITE_DERIVATION.md` for the full three-way
  cross-confirmation chain (Ch.313 map exhibit → IA Exhibit C place name → GNIS/TIGER).
- COD: reported 2027-10-29 (matches the executed IA's own Exhibit B schedule exactly) →
  independent **2028-Q2/Q3**, drift risk **high** (imagery-confirmed absence of
  ground-breaking a year past the contractual NTP leaves only ~10 months of runway for a
  262 MW build).

## 2. Site identification

- Derivation chain (full detail: `sources/SITE_DERIVATION.md`):
  1. Executed IA Exhibit C names the POI **"Halsell Ranch Switch"** on the Thomas Price –
     Willow Creek 345kV line, Jack County — but the location sentence itself is REDACTED as
     CEII (Oncor's PUCT cover letter confirms this redaction).
  2. Ch.313 agreement #1728 (Graford ISD) includes actual **map exhibits** — a project
     boundary/solar-panel-footprint map and a "Proposed Reinvestment Zone" map anchored at
     a labeled landmark, **"Marluc Bella Vita Ranch."**
  3. That ranch/lodge's own site gives its address as "4636 **Halsell Ranch Road**, Graford,
     TX 76449" — independently matching the IA's redacted switch name.
  4. Overpass/OSM query for `name~"Halsell"` returns "Halsell Ranch Road" (TIGER,
     tiger:county=Jack, TX) and **"Halsell Ranch Cemetery" (GNIS feature_id 1337264)** at
     **33.0318°N, -98.2947°W** — used as the anchor.
- Three independent public records converge on the same place; not parcel-precise (~1km
  anchor, not a surveyed pin — the switch's actual coordinates remain CEII-redacted).
- Stated project area: **~2,500 acres** (original 2022 Ch.313 filing, ~305 MWac concept;
  the as-contracted 2025 design is 262.22 MW / 68 inverters, likely a smaller built footprint
  within that zone — no updated acreage has been filed publicly).
- Cross-checks: Ch.313's 65% Palo Pinto / 35% Jack county split is consistent with an anchor
  near the county line; prior POI triangulation (Willow Creek Switch, Jacksboro substation)
  bracketed "eastern Jack County" — the new anchor falls inside that zone.

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| PK Solar, LLC | SPV / IA counterparty | Executed IA text: "...PK Solar, LLC (Possum Kingdom Solar) (24INR0118)..." |
| Novis Renewables, LLC | Original developer (renamed to PK Solar, LLC) | Ch.313 agreement #1728 applicant history; 2022 application signed by Jonathan Koch (President) |
| Nadara Development US, LLC / Nadara North America, Inc. | Current parent / administrator | IA notice address "c/o Nadara Development US, LLC"; Ch.313 2026 amendment contacts (Thomas Leahy, John Lichtenberger, Erin Michelle Lunsford) all @nadara.com, 1 Bridge St Suite 11, Irvington NY |
| Unknown | EPC | not found |
| Unknown | PPA/offtaker | not found |

- Financing: **$15,508,166** combined Irrevocable Standby Letter of Credit (IA Exhibit E),
  covering both 24INR0118 and 24INR0375 jointly, effective on/before 2025-07-01.
- Note: developer identity previously untraceable ("PK Solar" alone returns no web results);
  resolved this rescan via the Ch.313 registry (`ch313.py resolve --name "PK Solar"`), which
  surfaced the f/k/a "Novis Renewables, LLC" name and, through it, the Nadara parent chain.

## 4. Land & county records

- Tenure: **leased** — Ch.313 application: "The applicant will lease approximately 2,500
  acres of land within in Jack and Palo Pinto Counties for the project."
- Ch.313 (Tax Code Chapter 313) value-limitation agreement **#1728**, Graford ISD: applied
  2022-03-14 (Novis Renewables LLC, $75,000 application fee), board-approved 2022-11-21,
  amended 2026-03-05 (PK Solar LLC, notarized 2025-12-16) — **still active and being
  administratively maintained**. This overturns the earlier assumption of a structural
  Ch.313 negative: the project actually entered the pipeline in 2021-2022 (well before the
  Sept-2023 sunset), not as a 2024 entrant.
- Ch.312 (post-2022 abatement registry): **negative (weak)** — no row for this
  project/entity/county; consistent with the incentive already being covered by Ch.313.
- CAD: Jack/Palo Pinto CAD parcel-level ownership still not retrieved (form-based portals).

## 5. Interconnection & contractual schedule

- POI: **Halsell Ranch Switch**, Thomas Price Switch – Willow Creek Switch 345kV line, Jack
  County (executed IA Exhibit C); co-tenant switchyard shared with 24INR0375 (Possum Kingdom
  BESS) per IA Attachment 1 one-line diagram.
- IA PDF: **retrieved and read in full** (56 pages, INR-in-text CONFIRMED). Oncor's PUCT
  cover letter discloses it redacted "station location information... in Exhibit C, and
  certain financial information... in Exhibit D" as CEII.
- IA executed **2025-07-30** (5 days after the ERCOT queue's self-reported iaSigned of
  2025-07-25 — use the document date as authoritative); filed at PUCT 2025-08-26.

| IA document | Signed | Financial security posted |
|---|---|---|
| Standard Generation Interconnection Agreement (co-tenant w/ 24INR0375) | 2025-07-30 | $15,508,166 (combined w/ 24INR0375) |

| Milestone | Date |
|---|---|
| Notice to Proceed | 2025-07-01 |
| In-Service Date | 2027-05-13 |
| Scheduled Trial Operation Date | 2027-05-17 |
| Scheduled Commercial Operation Date | 2027-10-29 |

- Queue-history COD drift (`timeline.md`): **3 changes** — 2024-11-22 → 2026-05-08 →
  2026-10-30 → 2027-10-29; in reports since 2022-05 (50 snapshots). The queue's own
  `construction_start_reported` (2025-05-01) / `construction_end_reported` (2026-05-08)
  fields are contradicted by imagery — treat as unreliable for this project.

## 6. Satellite timeline

| Date | Observation | Frame |
|---|---|---|
| 2024-07-12 | Rangeland, ranch tracks, oil/gas pads; no grading | imagery/key/s2_2024-07-01.png |
| 2025-07-19 | Unchanged; no construction | imagery/key/s2_2025-07-01.png |
| 2026-02-02 | Winter palette, unchanged land-use pattern | imagery/key/s2_2026-01-15.png |
| 2026-05-03 | Spring green-up, unchanged | imagery/key/s2_2026-04-15.png |
| 2026-07-07 | Unchanged; no construction | imagery/key/s2_2026-07-15.png |
| 2026-07-07 (wide) | 13km frame covering the full mapped zone (Marluc Bella Vita Ranch to FM 337) — no construction anywhere; neighboring Longhorn Solar (650MW, operating, ~4.5km west) visible as a positive imagery control | imagery/wide/s2_2026-07-15_wide.png |

- Verdict: **not started** as of the latest clear acquisition. Genuine finding, not an
  imagery gap — a nearby operating plant (Hecate Energy Longhorn Solar / Repsol Renewables
  NA, 650 MW) is clearly visible in the same regional frame, proving the imagery source
  resolves construction at this resolution when present.

## 7. COD assessment

- Executed IA Exhibit B Scheduled COD (2027-10-29) matches the ERCOT queue's self-reported
  projectCod exactly — a positive cross-check that the queue figure is the real contract
  date, not stale or invented.
- However: NTP was 2025-07-01 (over a year ago) and In-Service Date is 2027-05-13 (~10
  months away) — yet imagery shows zero ground-disturbance. That is tight-to-late versus a
  typical 12-18 month utility-scale solar construction cycle.
- Positive signals: $15.5M financial security posted; Ch.313 agreement active and
  administratively maintained through March 2026; developer (Nadara) identifiable and
  engaged — not an abandoned/paper project, just pre-construction.
- Companion BESS (24INR0375) shares the same COD and switchyard — added coordination risk.
- **Independent estimate: 2028-Q2/Q3, drift risk high.**

## 8. Could not determine

- EPC contractor
- PPA offtaker / financing structure beyond the ISLOC security amount
- Exact as-built project acreage (only the original ~2,500-acre 2022 Ch.313 zone figure is documented)
- CAD parcel-level ownership (Jack/Palo Pinto CAD portals remain form-based)
- Precise surveyed coordinates of Halsell Ranch Switch (redacted as CEII; site anchor is a cross-referenced place name, not a surveyed pin)
