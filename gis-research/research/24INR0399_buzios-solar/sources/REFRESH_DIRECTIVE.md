# REFRESH DIRECTIVE — 24INR0399 Buzios Solar (user-ordered deep scan, 2026-07-22)

Pre-computed systematic leads. Read FIRST, do not redo these lookups blind.

## Queue facts (2026-06-01 snapshot, authoritative)
- Buzios Solar, Motley County, 252.0 MW SOL/PV.
- POI: **tap between Cottonwood (#59904) and White River (#23922)**. SPV: **Roaring Springs Solar, LLC** (Roaring Springs is the town in Motley Co; 'Buzios' is a codename — Brazilian beach town, possibly a Brazilian/Iberian developer naming pattern).
- IA signed 2023-11-06; financial security + NTP: Yes; projectCod 2026-04-30 (now passed); ginrStudyPhase "SS Completed, FIS Completed, IA". In queue since 2022-08. Run `queue_history.py 24INR0399`.

## EIA IDENTITY PUZZLE — resolve explicitly
Two EIA-860M matches point at the SAME coords **33.87751, -100.8902** (Motley), 250.0 MW:
- eia_history matched plant **68458 'Stafford Solar, LLC'** (entity Stafford Solar, LLC): (P) planned 2024-12→2025-01 → (V) >50% 2025-02→2025-10 → **(OP) Operating from the 2025-11 report, actual operating date 2025-10**.
- spv.py name-matched an Operating row 'Roaring Springs, LLC' at the same coords/MW.
Most likely ONE plant renamed (Stafford ↔ Roaring Springs) — but VERIFY: pull the 860M history for plant 68458 (`eia_history.py 24INR0399 --plant-id 68458 --write`), check whether entity/plant name changed between snapshots, and confirm the plant = Buzios via the IA site description, not name-vibes. If they are genuinely two different plants, that's a major disambiguation finding — document both.
Discrepancy to explain: EIA says operating 2025-10, but the 2026-06 queue snapshot still lists Buzios active with no approvedForCommercialOperation. Queue lag vs wrong-plant match — decide with evidence.

## Leads already run (build on them, do not re-run blind)
1. **PUCT rung — 3 confirmed-looking filings in docket 35077** (from the local index):
   - **35077-1709** (2023-11-22): "Generation Interconnection Agreement between Oncor Electric Delivery Company LLC and Buzios Solar (Roaring Spr…" — the executed IA. Exhibit B/C = site description + schedule. PULL THIS FIRST.
   - **35077-1794** (2024-04-26): Amendment No. 1.
   - **35077-2122** (2025-04-25): Amendment No. 2 — what changed? (COD? capacity? assignment?)
   → `puct.py match 24INR0399 --dir <sources/> --key "Roaring Springs Solar"` (and `--key "Buzios"`); verify INR-in-PDF.
2. **Ch.313/JETI: negative** (Buzios post-dates Ch.313 anyway). **Ch.312: weak negative** (CAD-submitted registry, gaps) — check Motley County commissioners minutes for reinvestment zone / abatement (data/reference/county_minutes_census.json has the Motley URLs + platform), and local news via search.py.
3. **TCEQ Central Registry: no Buzios hit** (only DCP pipeline in Motley). Try STORMWATER NOIs for 'Roaring Springs' / 'Buzios' / 'Stafford' — construction NOIs carry physical addresses and start dates.
4. **Developer identity**: resolve Roaring Springs Solar, LLC's parent (check the IA signature block first — cheapest source; then SOS-style lookups / search.py). 'Stafford Solar, LLC' entity name from EIA is a second thread to the same parent, or evidence of an asset sale — either way document the chain.

## Imagery
Site anchor = EIA coords 33.87751, -100.8902 (verify against IA Exhibit site description before trusting). If the EIA match is right, the plant should be VISIBLY BUILT (operating 2025-10): capture a construction series (~2024 → 2026) with s2aws.py showing grading → complete, and confirm the footprint sits on the Cottonwood–White River line corridor consistent with the POI tap. If nothing is built there, say so and re-derive the site from the IA exhibit.

## Conventions (binding)
- Banned sources (citing = FAILED run): interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, infrasure.ai, futuregrid.io, ercotqueue.com, any queue aggregator.
- Imagery: s2aws.py ONLY (CDSE in capacity outage). Frames to imagery/key/s2_<TRUE-ISO-ACQUISITION-DATE>.png (use the tool output's real acquisition date, never the query date). Read/inspect every frame (coverage + connecting road, no tile-seam nodata, not cloud-ruined, PNG > 2KB). Probe/wrong-location chips go to the session scratchpad, NEVER imagery/.
- Site provenance rungs: map exhibit > IA Exhibit C text > imagery-verified EIA > documented Places pin.
- Honest negatives over plausible guesses. Wrap-up: queue_history.py, eia_history.py --write, build_brief.py.
