# Triage log — Lupinus Storage 1 (24INR0153)

T1 start
Queue history: 50 snapshots (2022-05-01 → 2026-06-01). COD drifted 3×:
2024-12-30 → 2025-12-31 → 2026-09-21 → **2027-09-13** (current, held since 2025-03-01).
Capacity: 82.97 MW → 84.01 MW (bumped 2025-12-01). 
Milestones: Screening done (2022-03-10), FIS requested (2022-05-11), Meets 6.9(1) (2025-09-22).
NO: FIS approved, IA signed, Meets all 6.9, construction start/end, energization, sync, COD.
Significant gap: FIS requested but never approved (3+ years). IA not signed.
T1 done.

T2 start
gmaps.py places: HTTP 429 on both attempts (exact name; name + county). Budget exhausted.
No pins found.
T2 done. pins_found=0.

T3 start
Web sweep results:
- Developer: Sunraycer Renewables; SPV = Lupinus Solar LLC / Lupinus BESS LLC
- $901M financing closed May 14, 2026 (MUFG, Ally, Nomura, Nord/LB, SocGen)
- Projects broke ground late 2025; Lupinus 1&2 COD late 2027
- Google long-term PPA confirmed
- Battery supplier: Canadian Solar e-STORAGE
- PUC Control No. 35077 = IA between Oncor + Lupinus Solar LLC, signed 2025-06-26;
  Amendment No. 1 filed 2026-02-12
- ercotqueue.com notes "No IA" (stale) and 4% build chance (likely pre-financing update)
Source saved: sources/sunraycer_financing_may2026.md
T3 done. news_found=true, developer=Sunraycer Renewables.

T4 start
PUCT Interchange: all fetch attempts blocked (HTTP 402). Cannot retrieve IA PDF.
From T3/web: IA confirmed (PUCT Control No. 35077), filed 2025-06-26 by Lupinus Solar LLC
+ Oncor; Amendment No. 1 filed 2026-02-12. Covers 24INR0150 (solar) + 24INR0153 (storage).
Milestone schedule exhibit NOT retrieved — PUCT portal inaccessible this session.
ia_found=true (via web sources), schedule_exhibit=blocked.
T4 done.

T5 start
TX Comptroller Ch.313: portal returned general page, no Franklin County data surfaced.
DDG sweep for JETI/abatement: no results for Sunraycer/Lupinus in Franklin County.
Ch.313 expired post-2022; JETI is replacement. Project entered queue 2021 (pre-JETI cutoff
period) — abatement absence is expected / normal.
abatement_found=false.
T5 done.

T6 start
Site candidate: no GPS pin from gmaps (429). Using knowledge-based estimate:
Monticello SES is near 33.07°N, 94.88°W (Titus County). Franklin County runs ~33.1-33.3°N,
95.0-95.4°W. Lupinus site likely in eastern Franklin County near 345kV corridor.
Estimate: 33.12°N, 95.05°W (low confidence — no pin, no IA map, no abatement parcel).

CDSE imagery: HTTP 401 on chip attempt (auth failure). Budget exhausted for imagery.
construction_visible=unknown (imagery blocked).

Additional construction evidence from T3: groundbreaking confirmed March 17, 2026 per
infrasure.ai; financing closed May 2026; construction active per multiple sources.
T6 done.

T7 start
triage_findings.json written.
triage.md written.
Turns used: ~22. T7 done. STOP.
