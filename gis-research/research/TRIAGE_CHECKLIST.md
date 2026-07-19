# Triage checklist — first pass, hard-budgeted. This is NOT the deep scan.

Goal: in **≤35 turns** produce a signals score + deep-scan recommendation. Projects sit at
different development stages — most will NOT have every document. A missing doc is a
NORMAL finding to log, never a reason to dig deeper. Depth belongs to the deep scan, which
runs only after a human approves it.

## Rules of engagement (violating these = failed run)

1. Execute steps T1→T7 IN ORDER. Each step has a tool-call budget. Budget spent → write
   the result to `log.md` (even if the result is "nothing found") → move to the next step.
   No retries beyond budget. No exceptions.
2. Before each step, append to `log.md`: `T<n> start`.
3. If you notice you are doing something not on this list, STOP, log the drift, return.
4. Image economy: ≤1 contact sheet + ≤3 full-size frame reads TOTAL.
5. A blocked portal (CAPTCHA, session cookies, 403) gets ONE retry, then a negative log
   line. Never engineer around a blocked site during triage.
6. T7 always runs, even if T2-T6 all came up empty — an all-negative triage is a valid,
   useful result (likely paper project).

## Steps

- **T1 — queue history (budget 2).**
  `uv run gis-research/scripts/research_tools/queue_history.py <INR>` then read the
  project's `timeline.md`. Note COD-drift count and milestone dates in `log.md`.
- **T2 — delivery pins (budget 4).**
  `gmaps.py places` with: exact project name; name + county; name + "solar"/"wind" +
  nearest town; LLC name. Log every pin with coords. No pin = normal.
- **T3 — web sweep (budget 5).**
  Search (DDG/Bing HTML): project name + news/PR; LLC name + registration; any developer
  name that surfaces. Save only pages directly about THIS project to `sources/`.
  FIRST run the systematic resolver (local + instant, costs ~1 tool call):
  `uv run gis-research/scripts/research_tools/spv.py resolve <INR>`
  — candidates from EIA-860M (entity, plant coords, EIA status/COD) and the PUCT docket
  index. Then ALWAYS record in triage_findings.json: `spv_name` (the project LLC's legal
  name) and `developer` — these are the join keys the IA matcher (T4) and every later
  pass depend on; a queue name alone often fails to match filings ("Operation Sunshine"
  is a codename; the IA names the real SPV). An 860M lat/lon is also a site candidate
  for T6, and an 860M planned-COD that contradicts the queue COD goes in cod_first_look.
- **T4 — PUCT Interchange (budget 6).**
  Use the dedicated tool — do NOT WebFetch the portal (it rate-limits to HTTP 402):
  `uv run gis-research/scripts/research_tools/puct.py match <INR> --dir <your sources/>`
  This is SYSTEMATIC: it scans a local snapshot of the central §25.195(e) docket (35077 —
  where every TSP files its IAs), matches exact name keys (queue name + any spv_name/
  developer you recorded in T3), downloads candidates, and VERIFIES each by finding the
  INR inside the PDF text (CONFIRMED / PROBABLE via county+MW / unverified_-prefixed).
  Found a different SPV name during T3? add `--key "<SPV legal name>"`.
  CONFIRMED/PROBABLE → extract ONLY the parties/POI page and milestone-schedule exhibit.
  Nothing → negative log, move on (deep scan will chase the SPV name).
- **T5 — abatements (budget 4).**
  TX Comptroller Ch.313 list + JETI registry, filtered to the county. Hit → download the
  application PDF only (skip supplements during triage). Miss → normal for post-2022
  projects without JETI.
- **T6 — imagery (budget 8).**
  Pick best site estimate: pin > abatement/IA map > POI infrastructure. If nothing better
  than "somewhere in the county", SKIP imagery, log "no site candidate".
  Otherwise: 3×3 grid of TIGHT chips (`--buffer-km 2`, step ±0.03°) at the current date →
  `cdse.py sheet` → read the CONTACT SHEET (not the frames). Activity spotted → re-center,
  1 tight chip at the true center + 1 baseline 2-3 years back (your full-size reads).
- **T7 — write and stop (budget 6).**
  Write `triage_findings.json` + `triage.md` (≤10 lines, human-scannable), append final
  `log.md` entry with turns used, STOP. Do not run build_brief/build_index (deep-scan only).

## triage_findings.json schema

```json
{
  "inr": "", "project": "", "triage_date": "",
  "signals": {
    "ia_found": false, "abatement_found": false, "pins_found": 0,
    "news_found": false, "construction_visible": false
  },
  "site_candidate": {"lat": 0, "lon": 0, "method": "", "confidence": ""},
  "construction": {"verdict": "", "evidence": ""},
  "cod_first_look": {"reported": "", "plausible": true, "why": "one line"},
  "deep_scan_recommended": false,
  "deep_scan_focus": ["what the deep pass should chase first"],
  "turns_used": 0
}
```

`site_candidate` and `construction` are null when unknown — never invent. `deep_scan_focus`
is the handoff: name the specific threads worth money (e.g. "IA exists but schedule exhibit
CEII-redacted — try amendment filings", "pin found but no imagery signal — check newer dates").
