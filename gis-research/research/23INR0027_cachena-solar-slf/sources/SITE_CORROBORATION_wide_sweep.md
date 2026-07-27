> **RETRACTED 2026-07-21.** The site adopted below (29.456,-97.750) is Hoke Solar's
> (23INR0231) footprint, in Gonzales County on a 138kV tap -- NOT this project's. The
> "visually confirmed construction matching developer's own timeline" claim was circular:
> Enbridge's project-updates page gives a construction START date with NO location, and
> this pass matched that date order to *a* real construction site at a plausible bearing
> without checking county (Gonzales, not Wilson), voltage (138kV, not the 345kV Elm
> Creek-STP circuit Cachena interconnects to), or scale (~550 acres fits Hoke's 95MW, not
> Cachena's 602MW/4,600 acres). See `research/23INR0231_hoke-solar/sources/SITE_DERIVATION.md`
> and `findings.json` `retraction` (this project, corrected 2026-07-21) for the true site
> (TCEQ-address-geocoded, 29.2579,-97.8057) and full chain. Left below for provenance only
# Site correction — Cachena Solar SLF 23INR0027 (user-directed 2nd pass, 2026-07-20)

**The EIA-860M coordinate used previously (29.26357, -97.78055) is wrong for siting
purposes**: it is the town centroid of Nixon, TX (a dense residential street grid sits
exactly at that point in a Sentinel-2 chip) — an administrative/reporting point, not the
plant. This is the same class of bug as Yellow Viking (21INR0520): a plausible-looking
EIA-860M coordinate that was never independently checked against imagery.

## Re-derivation

1. **Elm Creek Substation** located via `OpenGridMap/transnet-models` (`csv_nodes.csv`,
   a GitHub dataset, not a banned queue-tracker): CPS Energy, 345kV, **29.4673, -97.99988**.
   This matches the IA's own POI text: "18.5 mi East of Elm Creek substation on 345kV Elm
   Creek-STP circuit 2."
2. A **wide (15 km buffer) AWS Open Data sweep** centered between Nixon and a due-east
   projection from Elm Creek Substation found one obvious candidate: a large multi-block
   rectangular cleared/graded site, visually unmistakable at 600 MW scale.
3. Confirmed center: **29.456, -97.750** — ~15 mi due east of Elm Creek Substation
   (18% short of the stated 18.5 mi, but same bearing/order of magnitude; likely
   straight-line vs. actual transmission-line-routing distance).

## Construction timeline (AWS Open Data, this point, 6 dates)

| Date (acquired) | Cloud | Observation |
|---|---|---|
| 2024-06-09 | 19.2% (partial) | Woodland/brush, no clearing |
| 2025-06-17 | 0.5% | Woodland/brush, no clearing |
| 2025-11-04 | 0.2% | **Still no visible clearing** |
| 2026-02-04 | 0.0% | First visible disturbance — lighter terrain, faint access patterns |
| 2026-03-21 | 0.0% | Clear rectangular grading, block segmentation underway |
| 2026-06-29 | 0.0% | Fully graded, ~6 distinct rectangular blocks |

This refines (not contradicts) Enbridge's own public project-updates page ("Aug 2025 =
site prep/clearing; Q4 2025 = construction began"): whatever began in 2025 was not yet
spectrally visible through a clean, near-zero-cloud November 2025 scene. The
imagery-visible grading start is **Jan/Feb 2026**, roughly 3-4 months after Enbridge's
reported site-prep date — consistent with an initial non-visible survey/mobilization
phase preceding visible earthwork, not a contradiction of Enbridge's timeline.

=> Verdict unchanged (`real_active`), but site coordinate corrected and construction
stage upgraded from "clearing" (text-only, no imagery) to `grading_active` with a full
6-date visual timeline.

[2026-07-21: this entire 6-date timeline is Hoke Solar's (23INR0231) footprint, not
Cachena's -- see retraction banner at top of file. It has been deleted from
imagery/key/. Current site/construction status: findings.json.]
