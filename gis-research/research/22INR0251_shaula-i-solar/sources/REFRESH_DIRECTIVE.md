# REFRESH DIRECTIVE — 22INR0251 Shaula I Solar (user-ordered deep scan, 2026-07-21)

Pre-computed systematic leads. Read FIRST, do not redo these lookups blind.

## Queue facts (2026-06-01 snapshot, authoritative)
- Shaula I Solar, DeWitt County, 205.2 MW SOL/PV, zone SOUTH.
- SPV/interconnecting entity: **Shaula Energy Project, LLC**.
- POI: **tap 345kV 5133 Elm Creek - 5915 SO TEX ckt 1** (Elm Creek→South Texas Project corridor).
- IA signed 2022-02-16; financial security + NTP: Yes; **projectCod 2026-03-31 — ALREADY PASSED**, constructionStart empty.
- ginrStudyPhase: "SS Completed, FIS Started, IA" — **FIS never completed after ~4 years** despite signed IA. Explain this.

## TWIN-PHASE CLUSTER — explicit attribution required
22INR0267 Shaula II Solar (research/22INR0267_shaula-ii-solar/) is the sibling: SAME county, SAME POI, SAME 205.2 MW. Any footprint/filing/news you find
must be attributed to the correct phase (or explicitly recorded as shared/indistinguishable).
Do NOT double-count one site as both. Cachena Solar SLF (23INR0027, Wilson Co, Enbridge) taps the
same Elm Creek 345kV family further north — do NOT cross-attribute (see its 2026-07-21 log for a
misattribution post-mortem).

## Leads already run (do not re-run; build on them)
1. **PUCT rung-0**: puct_inr_join.json has ZERO items for this INR (filed IA may be image-only or
   pre-index). BUT `puct.py search "Shaula"` shows **4 filings in docket 35077** matching Shaula.
   → Run `puct.py match 22INR0251 --dir <sources/> --key "Shaula Energy Project"` and pull all 4; verify INR-in-PDF.
   The executed IA is the best source for POI text/site description/schedule (Exhibit B/C).
2. **EIA-860M: DECISIVE NEGATIVE** — no "Shaula" match anywhere in the TX slice, and ZERO DeWitt
   County rows of any status. Neither phase has EVER registered with EIA. For an IA-signed,
   security-posted project with a passed COD this is strong paper-project evidence. Record it.
3. **Ch.313/JETI: negative** (740 agreements + 38 JETI apps, no Shaula match; unrecognized legal
   name possible — retry with any parent-co name you resolve). Ch.312: weak negative (registry gaps).
4. **TCEQ Central Registry: negative** (only DCP pipeline facility in DeWitt). Try the STORMWATER
   NOI angle explicitly (construction stormwater permits keyed on the SPV name gave Cachena its
   site address) — search TCEQ stormwater NOIs for "Shaula".
5. **County minutes**: DeWitt minutes ARE online (ezTask/CIRA, back to 2020):
   https://www.co.dewitt.tx.us/page/dewitt.comm.court.minutes — check minutes.py index/resolve
   first; harvest if not yet indexed. Abatement/reinvestment-zone mentions = developer identity + site.
6. **Developer identity unknown** — "Shaula" is a star-name codename. Resolve the SPV's parent via
   search.py + SOS-style lookups; then re-run registry searches with the LEGAL/parent name.

## Conventions (binding)
- Banned sources (citing = FAILED run): interconnection.fyi, cleanview.co, gridinfo.com,
  energyacuity, infrasure.ai, futuregrid.io, ercotqueue.com, any queue aggregator.
- Imagery: s2aws.py ONLY (CDSE in capacity outage since 2026-07-20). Frames to imagery/key/
  s2_<TRUE-ISO-ACQUISITION-DATE>.png; Read/inspect every frame (coverage+road, no tile-seam
  nodata, not cloud-ruined, PNG>2KB). Probe/wrong-location chips go to the session scratchpad,
  NEVER imagery/. Site provenance rungs: map exhibit > IA Exhibit C text > imagery-verified EIA
  (unavailable here — no EIA row) > documented Places pin.
- Honest negatives over plausible guesses. Wrap-up: queue_history.py, eia_history.py --write
  (will document the 860M absence), build_brief.py.
