# Dossier — Tulsita Solar (21INR0223)

Researched 2026-07-19 · site ~28.51, -97.68 (corridor estimate) · verdict **real_active**

## 1. Verdict

- **real_active** — Approved-for-synchronization 2024-10-30 ([queue timeline](timeline.md)); Ch.313 App.1839 (Goliad ISD) first qualifying tax year 2025 ([web sweep](sources/web_sweep.md)) — assets commissioned by early 2025
- Construction: **substantially_complete** (approved-for-sync = construction done); first activity date unknown (imagery did not confirm site location)
- Site: ~28.51, -97.68 — POI corridor estimate (Tuleta bus #8590 at 28.57,-97.80 to Berclair anchor ~28.44,-97.60), low-medium confidence ([Tuleta map](https://www.google.com/maps/@28.57,-97.80,5000m/data=!3m1!1e3))
- COD: reported 2026-09-15 → independent **2026-Q3**, drift risk **low** (sync-approved Oct 2024; monthly slip = settlement/metering, not construction)

## 2. Site identification

- Derivation: POI "Tap 138kV 8590 Tuleta - 8595 Euler" places site on AEP Texas 138kV segment; Tuleta TX (OSM Nominatim: 28.5713N, -97.7962W) = bus #8590 endpoint; [Berclair VFD donation](sources/web_sweep.md) by ENGIE + Blattner confirms community proximity to Berclair (~28.44N,-97.60W)
- **Stated project area: not obtained** — PUCT IA PDF blocked (402); Ch.313 PDF blocked; Goliad CAD portal down; 256.2 MW implies ~1,300-2,500 acres typical solar footprint
- Cross-checks: Tuleta bus location (OSM) and Berclair VFD donation corroborate Goliad County west/central corridor — consistent with each other within ~25 km
- Not obtainable: Exact POI tap coordinates (CEII); parcel geometry (CAD down); Google Places pin (429 rate-limited)
- **Imagery note**: 6 Sentinel-2 chips searched across Goliad County; no solar array confirmed. Site may be in inter-chip gap. Summer chips (Jun–Jul 2026) were heavily clouded. March 2025 chip at Tuleta center clear — no array in 6 km window at town center, suggesting site is offset from Tuleta proper.

## 3. Ownership & money

| Entity | Role | Evidence |
|---|---|---|
| Ray Ranch Solar LLC (f/k/a Tulsita Solar, LLC) | SPV | [Ch.313 App.1839](sources/web_sweep.md); ERCOT queue |
| ENGIE North America | Developer/owner | [Berclair VFD donation](sources/web_sweep.md) |
| Blattner Company | EPC | [Berclair VFD donation](sources/web_sweep.md) |
| AEP Texas Central Company | TSP (IA counterparty) | PUCT filing reference ([web sweep](sources/web_sweep.md)) |

- Financing: not obtained — no press release found; ENGIE is a publicly traded parent (ENGI.PA), project-level financing unknown

## 4. Land & county records

- Tenure: **unknown** — CAD portal down; no parcel search completed
- Ch.313: App.1839, Ray Ranch Solar LLC, Goliad ISD, filed 2022-05-04, first qualifying year 2025 ([web sweep](sources/web_sweep.md)) — strongly implies assets placed in service before Jan 1, 2025
- Ch.312 county abatement: referenced on county website for Charro Creek Solar (different project); Ray Ranch Solar status unknown (2022 agendas not available online)
- CAD: no parcel search completed (portal maintenance)
- PUCT IA PDF: 402 paywall on all interchange.puc.texas.gov document requests

## 5. Interconnection & contractual schedule

- POI per ERCOT queue: "Tap 138kV 8590 Tuleta - 8595 Euler" — AEP Texas 138kV network, Goliad County
- IA PDF: not retrieved (PUCT interchange 402) — parties confirmed as AEP Texas Central + Ray Ranch Solar LLC via triage research

| IA document | Signed | Financial security posted |
|---|---|---|
| Original IA ([not retrieved](sources/stage1_web_research.md)) | 2022-09-19 | Unknown — document blocked |

| Milestone | Queue date | Source |
|---|---|---|
| IA Signed | 2022-09-19 | [ERCOT queue](timeline.md) |
| FIS Approved | 2024-03-01 | [ERCOT queue](timeline.md) |
| Approved for Energization | 2024-10-22 | [ERCOT queue](timeline.md) |
| Approved for Synchronization | 2024-10-30 | [ERCOT queue](timeline.md) |
| Commercial Operation Approved | — (not yet) | [ERCOT queue](timeline.md) |

- Queue-history COD drift ([timeline.md](timeline.md)): **12 changes** — 2021-05-28 → 2026-09-15; monthly 1-month slips since 2025-10

## 6. Satellite timeline

| Date | Location searched | Observation | Frame |
|---|---|---|---|
| 2026-07-01 | 28.53N,-97.58W (eastern Goliad) | Undisturbed farmland/rangeland, clear | [png](imagery/s2_2026-07-01.png) |
| 2026-06-01 | 28.57N,-97.80W (Tuleta area) | >80% cloud, Tuleta town visible, no array | [png](imagery/s2_tuleta_2026-06-01.png) |
| 2025-03-01 | 28.57N,-97.80W (Tuleta area) | Clear; no solar array in 6km window at Tuleta | [png](imagery/s2_tuleta_2025-03-01.png) |
| 2025-03-01 | 28.65N,-97.50W (Goliad city area) | Clear; San Antonio River, undisturbed ag | [png](imagery/s2_goliad_2025-03-01.png) |
| 2025-03-01 | 28.47N,-97.72W (SW of Tuleta) | Clear; undisturbed ranching/ag | [png](imagery/s2_sw_2025-03-01.png) |
| 2024-06-01 | 28.55N,-97.68W (mid-county) | >70% cloud, no usable observation | [png](imagery/s2_mid_2024-06-01.png) |

- Verdict: **no_activity_confirmed** in searched chips — **but site not pinpointed**. Approved-for-sync status (Oct 2024) makes construction-complete near-certain. Array is likely in the uncovered Tuleta-Euler corridor gap.

## 7. COD assessment

- Approved-for-synchronization 2024-10-30 is the decisive milestone: ERCOT grants sync approval only after energization testing — construction physically complete by that date
- Ch.313 first qualifying tax year 2025: per TX law, first year is the year qualified property is placed in service; implies commercial operation by early 2025 or a contractual commitment for 2025
- No `approvedForCommercialOperation` date in the June 2026 ERCOT queue snapshot — gap likely reflects billing/settlement administrative clearance, not physical non-completion
- Monthly 1-month COD slips since Oct 2025 (10 consecutive slips) are a metering/settlement delay pattern, not a construction-stall pattern; construction-stall produces larger irregular jumps
- **Independent estimate: 2026-Q3, drift risk low** — project is physically commissioned, slip to beyond 2026-Q4 would require administrative anomaly; the reported 2026-09-15 is plausible but may already be past (commercial operation could have occurred since June 2026 snapshot)

## 8. Could not determine

- Exact site lat/lon — no pin, no parcel, PUCT IA blocked; imagery grid did not cover full Tuleta-Euler 138kV corridor
- Project area in acres — PUCT IA PDF and Ch.313 PDF both inaccessible
- Financial security / IA schedule milestones — PUCT interchange 402 on all requests
- PPA offtaker — no press release found; ENGIE-NA news archive did not list Tulsita/Ray Ranch
- Exact construction start date — not a reported ERCOT milestone; imagery did not cover site
- Ch.312 county tax abatement — 2022 Goliad County agendas not available online
- Whether commercial operation was achieved between July 2025 and June 2026 (gap in queue data)
