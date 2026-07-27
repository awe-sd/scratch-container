# REFRESH DIRECTIVE — 25INR0672 Fagus Solar Park 2 SLF (user-ordered deep scan, 2026-07-22)

Pre-computed systematic leads. Read FIRST, do not redo these lookups blind.

## Queue facts (2026-06-01 snapshot, authoritative)
- Fagus Solar Park 2 SLF, Childress County, 166.57 MW SOL/PV.
- POI: **60501 Tesla 345kV**. Interconnecting facility: **Excel Advantage Services, LLC dba Misae Solar Park II**.
- IA signed 2019-02-21 (predates this INR — inherited from the original project); financial security + NTP: Yes; projectCod 2026-05-20 (now passed); ginrStudyPhase "SS Completed, FIS Completed, IA".
- First queue appearance **2024-06** (25 snapshots) — this INR is NEW even though its IA date is 2019. Run `queue_history.py 25INR0672`.

## TWIN-PHASE CLUSTER — explicit attribution required
**20INR0091 Fagus Solar Park 1 SLF** (research/20INR0091_fagus-solar-park-1-slf/, scanned in parallel with you) is the sibling: SAME county, SAME POI, SAME interconnecting entity, SAME iaSigned, 166.42 MW, SAME COD — but it has been in the queue since 2018-05. EIA plant capacity dropped 517.0 → 331.6 MW in exactly the 2024-06 report, the month this INR appeared. Working hypothesis: the original single Fagus project was SPLIT into two ~166 MW queue phases summing to the 331.6 MW EIA plant. Your job is the Phase-2 half of that story: was there an amended/assigned IA creating this INR? A PUCT filing should exist. Never attribute the same footprint/filing to both INRs without saying so explicitly.

## Leads already run (build on them, do not re-run blind)
1. **EIA-860M: SHARED plant** — plant **67123 'Fagus Solar Park'**, entity **Excel Advantage Services, LLC**, 331.6 MW, coords **34.35099, -100.0493** (Childress). (U) ≤50% through 2024-12 → (V) >50% 2025-01→2026-03 → **(OP) Operating from the 2026-04 report, actual operating date 2025-12**. ONE EIA plant covers BOTH queue INRs — EIA does not distinguish the phases. The queue still lists this INR as active while EIA says the plant is operating — explain (partial/phase COD? queue lag? phase 2 not yet energized?).
2. **PUCT**: docket **35077 has 2 'Fagus' filings** → `puct.py match 25INR0672 --dir <sources/> --key "Fagus"` and `--key "Excel Advantage Services"`; verify INR-in-PDF (an amendment splitting the IA is the key artifact for THIS phase). PGC dockets: 58250, 58363, **58726** (Excel Advantage Services LLC / Fagus PGC amendment). Misae family: 50027, 59331, 11 'Misae' filings in 35077.
3. **Ch.313/JETI: negative under 'Fagus'** — RETRY with 'Misae', 'Excel Advantage', 'Greenalia' (ch313 keys on SCHOOL DISTRICT — Childress ISD). EIA-planned 'Greenalia Solar Power Misae III, LLC' 169.6 MW planned 2027-05 @ 34.20349, -100.0404 is a SEPARATE project — do not conflate.
4. **Ch.312**: county-only candidate #000004312 owner 'Childress Solar Park LLC' (Reinvestment Zone 2017-01) — probably the older, unrelated Childress Solar Park; rule in/out, don't assume.
5. **TCEQ Central Registry: no Fagus hit**. Try STORMWATER NOIs for 'Fagus' / 'Misae' / 'Excel Advantage' — construction NOIs carry site addresses and phase names.
6. **Developer chain unresolved**: Excel Advantage Services, LLC dba Misae Solar Park II — resolve the parent (Greenalia? sold?); re-run registries under the legal/parent name.

## Imagery
Site anchor = EIA coords 34.35099, -100.0493 (shared plant). If Phase 1 vs Phase 2 have distinguishable footprints (separate blocks/feeders on the parcel), document which block is which with evidence; otherwise record the footprint as shared/indistinguishable. Plant should be VISIBLY BUILT — capture a ~2023 → 2026 construction series with s2aws.py. If a second, unbuilt expansion area exists (phase 2 not yet constructed), that is the decisive finding — look for it.

## Conventions (binding)
- Banned sources (citing = FAILED run): interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, infrasure.ai, futuregrid.io, ercotqueue.com, any queue aggregator.
- Imagery: s2aws.py ONLY (CDSE in capacity outage). Frames to imagery/key/s2_<TRUE-ISO-ACQUISITION-DATE>.png (use the tool output's real acquisition date, never the query date). Read/inspect every frame (coverage + connecting road, no tile-seam nodata, not cloud-ruined, PNG > 2KB). Probe/wrong-location chips go to the session scratchpad, NEVER imagery/.
- Site provenance rungs: map exhibit > IA Exhibit C text > imagery-verified EIA > documented Places pin.
- Honest negatives over plausible guesses. Wrap-up: queue_history.py, eia_history.py --write, build_brief.py.
