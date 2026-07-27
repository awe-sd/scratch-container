# REFRESH DIRECTIVE — 20INR0091 Fagus Solar Park 1 SLF (user-ordered deep scan, 2026-07-22)

Pre-computed systematic leads. Read FIRST, do not redo these lookups blind.

## Queue facts (2026-06-01 snapshot, authoritative)
- Fagus Solar Park 1 SLF, Childress County, 166.42 MW SOL/PV.
- POI: **60501 Tesla 345kV**. Interconnecting facility: **Excel Advantage Services, LLC dba Misae Solar Park II**.
- IA signed 2019-02-21; financial security + NTP: Yes; projectCod 2026-05-20 (now passed); ginrStudyPhase "SS Completed, FIS Completed, IA".
- In queue since **2018-05** (98 snapshots) — run `queue_history.py 20INR0091` to get the full capacity/COD drift story.

## TWIN-PHASE CLUSTER — explicit attribution required
**25INR0672 Fagus Solar Park 2 SLF** (research/25INR0672_fagus-solar-park-2-slf/, scanned in parallel with you) is the sibling: SAME county, SAME POI, SAME interconnecting entity, SAME iaSigned 2019-02-21, 166.57 MW, COD 2026-05-20. It only appears in the queue from **2024-06** — and EIA plant capacity dropped 517.0 → 331.6 MW in exactly the 2024-06 report. Working hypothesis: the original single Fagus project was SPLIT into two ~166 MW queue phases summing to the 331.6 MW EIA plant. Verify or refute this with primary documents; never attribute the same footprint/filing to both INRs without saying so explicitly.

## Leads already run (build on them, do not re-run blind)
1. **EIA-860M is DECISIVE and POSITIVE**: plant **67123 'Fagus Solar Park'**, entity **Excel Advantage Services, LLC**, 331.6 MW, coords **34.35099, -100.0493** (Childress). Status history: (U) ≤50% through 2024-12 → (V) >50% 2025-01→2026-03 → **(OP) Operating from the 2026-04 report, actual operating date 2025-12**. Capacity 517.0 MW through 2024-05, 331.6 from 2024-06. `eia_history.py 20INR0091 --write` will regenerate this — run it at wrap-up.
   - NOTE the shared-plant problem: ONE EIA plant covers BOTH queue INRs. The queue still lists both as active (no approvedForCommercialOperation) while EIA says operating since 2025-12 — explain the discrepancy (partial COD? sync-approved but not commercial? queue lag?).
2. **PUCT**: docket **35077 has 2 'Fagus' filings** → `puct.py match 20INR0091 --dir <sources/> --key "Fagus"` and `--key "Excel Advantage Services"`; verify INR-in-PDF. PGC registration dockets: **58250** (Fagus Solar PGC application), **58363** (amend), **58726** (Excel Advantage Services LLC / Fagus amend). Misae family context: 50027 (Misae Lessee), 59331 (Misae Solar IV REC cert), 11 'Misae' filings in 35077.
3. **Ch.313/JETI: negative under 'Fagus'** — likely filed under a different legal name. RETRY ch313 leads with 'Misae', 'Excel Advantage', 'Greenalia' (ch313 keys on SCHOOL DISTRICT — Childress ISD). Note EIA-planned sibling 'Greenalia Solar Power Misae III, LLC' 169.6 MW planned 2027-05 @ 34.20349, -100.0404 is a SEPARATE project — do not conflate.
4. **Ch.312**: county-only candidate #000004312 owner 'Childress Solar Park LLC' (zone Childress County Reinvestment Zone 2017-01, expires 2028) — probably the older, unrelated Childress Solar Park plant; treat as a lead to rule in/out, not confirmation.
5. **TCEQ Central Registry: no Fagus hit** (only PGP Gas Products / Parker Pipeline — unrelated). Try the STORMWATER NOI angle for 'Fagus' / 'Misae' / 'Excel Advantage' — construction NOIs carry physical site addresses.
6. **Developer chain unresolved**: Excel Advantage Services, LLC dba Misae Solar Park II — resolve the parent (Greenalia? subsequently sold?). Then re-run registries under the parent/legal name.

## Imagery
Site anchor = EIA coords 34.35099, -100.0493 (verify against IA exhibit / parcel evidence before trusting). Plant should be VISIBLY BUILT (operating 2025-12): capture a construction time-series (~2023 → 2026) with s2aws.py showing grading → racking → complete. If the built footprint is absent at the EIA point, that is a major finding — say so and search the POI area.

## Conventions (binding)
- Banned sources (citing = FAILED run): interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, infrasure.ai, futuregrid.io, ercotqueue.com, any queue aggregator.
- Imagery: s2aws.py ONLY (CDSE in capacity outage). Frames to imagery/key/s2_<TRUE-ISO-ACQUISITION-DATE>.png (the tool's output line prints the real acquisition date — use THAT, never the query date). Read/inspect every frame (coverage + connecting road, no tile-seam nodata, not cloud-ruined, PNG > 2KB). Probe/wrong-location chips go to the session scratchpad, NEVER imagery/.
- Site provenance rungs: map exhibit > IA Exhibit C text > imagery-verified EIA > documented Places pin.
- Honest negatives over plausible guesses. Wrap-up: queue_history.py, eia_history.py --write, build_brief.py.
