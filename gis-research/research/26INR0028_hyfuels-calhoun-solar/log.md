# Triage log — HyFuels Calhoun Solar (26INR0028)

## T1 start
- queue_history.py: 36 snapshots (2023-07-01 → 2026-06-01)
- Screening complete: 2023-01-15
- FIS requested: 2023-07-07 (appeared in 2025-04-01 snapshot — filed late)
- FIS approved: NOT achieved
- IA signed: NOT achieved
- All subsequent milestones: NOT achieved
- COD drift: 2026-10-01 (held 2023-07 → 2025-08), then slipped to 2027-10-01 (current)
- 1 COD slip (12-month push)
- RESULT: Pre-IA stage. FIS requested but not approved. No construction milestones.

## T2 start
- gmaps.py: HTTP 429 on first call; one retry also 429. Portal blocked — no pins found.
- RESULT: 0 pins. Normal for pre-construction project.

## T3 start
- DDG search "HyFuels Calhoun Solar": found project entries on infrasure.ai, ercotqueue.com, interconnection.fyi, gridstatus.io. ercotqueue.com rates build-chance at 5%. Developer name surfaced: "HyFuels Green Lake Solar LLC" (alternate SPV name, not the one in the INR packet).
- DDG search LLC registration: no results for HyFuels Calhoun Solar LLC or HyFuels Green Lake Solar.
- DDG search "HyFuels solar developer Texas": KEY FIND — HyFuels is a ~1 GW wind+solar portfolio across Calhoun and Victoria counties (~25,000 acres). Developed by BNB Renewable Energy (20-yr history). In April 2024 Nova Clean Energy (backed by Bluestar Energy Capital) acquired the entire HyFuels portfolio. Green ammonia component also in portfolio.
- No news/PR articles specifically about this 26INR0028 project found.
- Saved source notes below. No files saved (no dedicated project pages with direct text to preserve).
- RESULT: Developer confirmed (Nova Clean Energy / Bluestar Energy Capital, acquired April 2024 from BNB). Portfolio context: multi-project, Gulf Coast, ~25k acres.

## T4 start
- PUCT Interchange portal: HTTP 402 on all three attempts (FilingParty=HyFuels Calhoun Solar; Description=HyFuels Calhoun Solar; base URL). Portal blocked — no retry budget remaining.
- RESULT: IA not found via PUCT. Consistent with queue data (iaSigned = NULL).

## T5 start
- TX Comptroller Ch.313 page: generic overview page only — no searchable data returned via WebFetch.
- County-filtered URL attempt: same result.
- DDG search JETI/Ch.313 for HyFuels / Nova Clean Energy / BNB Renewable + Victoria County: no abatement filings found.
- NOTE: Ch.313 expired 2022; project INR prefix 26 = applied 2026 vintage, so JETI is the relevant successor. No JETI filing found — normal for a project at FIS-requested stage.
- RESULT: No abatement found. Normal for pre-IA project post-2022.

## T6 start
- No pin from T2 (gmaps blocked). No IA map (PUCT blocked). No abatement map (T5 negative).
- POI: "Tap 345kV 8715 RADIANT7A - 8728 COBRA7A" — no public coordinates found for RADIANT/COBRA substations via 2 web searches.
- infrasure.ai and interconnection.fyi: only county-level detail (Victoria County).
- Portfolio context: HyFuels is 25,000 acres in Calhoun AND Victoria counties; this INR is filed as Victoria County.
- Best site estimate: county centroid only (~28.80°N, 97.00°W). Per triage rules: "no site candidate better than somewhere in the county" → SKIP imagery.
- RESULT: no site candidate. Imagery skipped per checklist.

## T7 start
- Written: triage_findings.json, triage.md
- Turns used: ~22
- COMPLETE
