# Project-Research Agent v1 — Design

**Date:** 2026-07-17 · **Subproject:** `gis-research/` · **Status:** approved approach A (single deep agent per project, in-session), pending spec review

## 1. Goal

For any ERCOT GIS interconnection-queue project, determine **(a) is it real** (a developing site, not a paper/speculative filing) and **(b) is the reported COD credible or likely to drift** — by reproducing the user's manual research methodology: county documents, LLC→parent tracing, land tenure, site pinpointing, and satellite ground truth. Output is a per-project evidence directory, not an essay.

**Acceptance test (benchmark):** run blind on **Hanson Solar (23INR0086, Coleman County, 398.83 MW Solar PV)** — a project the user has already researched by hand. The agent must independently converge on the user's findings: site lat/lon (≈ within 1 km), the site/parcel identification, and consistent satellite-imagery interpretation. Iterate the playbook until it does.

## 2. Why the previous runner failed (`scripts/reserach-agent-poor.py`)

1. Prompt embedded the full ERCOT milestone table → agent parroted it back as "findings," then "confirmed" via aggregator sites (interconnection.fyi, cleanview.co) that republish the same GIS report. Circular sourcing.
2. Coordinates were county centroids — no site-identification procedure existed.
3. `--disallowedTools Bash,Write` → agent structurally could not save documents, fetch imagery, or build a workspace.
4. Asked for opinion sections ("status summary", "COD estimate") instead of verifiable artifacts.
5. Single markdown output per run; no per-project state, no accumulation, no negative-evidence log.

## 3. The playbook (fixed evidence pipeline; opinion comes last)

Encoded in `gis-research/research/PLAYBOOK.md`; the agent executes stages in order.

| Stage | What | Key sources / tricks | Output |
|---|---|---|---|
| 1. LLC → parent | Trace the project LLC to its developer/parent | TX Comptroller taxable-entity search, TX SOS, press releases, LinkedIn | ownership chain + evidence |
| 2. County records | Parcel + documents sweep in the known county | **CAD parcel search by LLC owner name**; TX Comptroller Ch.312/313/JETI abatement registry; county commissioners-court minutes (tract descriptions buried in abatement docs); TCEQ where applicable | parcel IDs, acreage, situs, saved PDFs |
| 3. Site pinpoint | Converge on lat/lon with a stated method | parcel geometry; POI/switch names (OpenInfraMap); **Google Places "delivery-pin" search** (project name / construction entrance); news photos; FAA filings (wind) | lat/lon + derivation method + confidence |
| 4. Ground truth | Visual evidence over time | Sentinel-2 true-color chips (CDSE API), quarterly from queue entry (year is the INR prefix, e.g. 23INR… = 2023) → today, agent inspects for clearing/racking/complete; Google Static Map with site highlighted | `imagery/` series + activity verdict |
| 5. Synthesis | Verdict + COD assessment | only artifacts from stages 1–4 | dossier.md + findings.json |

## 4. Anti-word-salad rules

- Agent input = **identity fields only**: project name, INR, LLC, county, MW, fuel/tech, POI description. **Never** the milestone/status columns (nothing to parrot).
- **Banned sources** (mirror the GIS report; citing them as evidence = automatic reject): interconnection.fyi, cleanview.co, gridinfo.com and similar queue aggregators.
- **Artifacts or it didn't happen**: every findings.json claim references a file in `sources/` or a URL + quoted text.
- **Negative evidence is mandatory**: every search that returns nothing is logged in `log.md` with source, query, and date.
- County-centroid coordinates are an automatic fail; lat/lon must state its derivation (parcel / Places pin / imagery / news).

## 5. Per-project directory

```
gis-research/research/<INR>_<slug>/
  dossier.md        # human-readable research report
  findings.json     # machine-readable (schema below)
  log.md            # every search incl. negative results
  sources/          # saved artifacts: <date>_<source>_<desc>.<ext>
  imagery/          # s2_<YYYY-MM-DD>.png series, map_site.png
```

`findings.json` (v1 schema, roll-up-ready for the HTML dashboard):

```json
{
  "inr": "23INR0086", "project": "Hanson Solar", "researched_at": "…",
  "site": {"lat": 0.0, "lon": 0.0, "method": "parcel|places_pin|imagery|news", "confidence": "high|med|low"},
  "parcels": [{"cad_id": "…", "county": "…", "owner": "…", "acres": 0, "source": "sources/…"}],
  "llc_chain": [{"entity": "…", "relation": "subsidiary_of", "evidence": "…"}],
  "land_tenure": {"status": "leased|purchased|unknown", "evidence": "…"},
  "construction": {"verdict": "no_activity|clearing|racking|substantially_complete|operating",
                    "first_activity_seen": "YYYY-MM-DD", "evidence": ["imagery/…", "sources/…"]},
  "cod_assessment": {"reported": "YYYY-MM-DD", "independent": "YYYY-MM",
                      "drift_risk": "low|med|high", "reasoning_evidence": ["…"]},
  "real_project_verdict": "real_active|real_early|paper|unclear",
  "negative_searches": 0, "banned_source_violations": 0
}
```

## 6. Deterministic tooling (built once; agents call it)

- `gis-research/scripts/research_tools/cdse.py` — CDSE (Copernicus Data Space) auth + Sentinel-2 L2A true-color chip for (lat, lon, date, buffer_km). Creds from `~/.config/gis-research.env` (**outside the repo**; never committed, never pasted into chat). First run may require a one-time interactive OAuth-client setup in the CDSE dashboard.
- `gis-research/scripts/research_tools/gmaps.py` — Google Places text search (delivery-pin trick) + Static Map with site marker/polygon. API key from the same env file.
- Env file keys: `CDSE_USERNAME`, `CDSE_PASSWORD`, `GMAPS_API_KEY`.

Everything else (CAD portals, comptroller, SOS, TCEQ, news) the agent does live via WebSearch/WebFetch/curl, saving artifacts to `sources/`.

## 7. Execution shape

- **v1 (this spec):** one deep-research agent per project, run in-session in Claude Code with full tools (web + Bash/curl + Write restricted to the project dir), following PLAYBOOK.md. Single context so stage-1 discoveries (LLC name variants, developer aliases) feed stage-2/3 searches. **Research subagents run on Sonnet** (cost control — user directive); the orchestrating session may be any model.
- **Phase 2 (out of scope here):** after the benchmark passes — batch fan-out (Workflow) across filtered queue subsets, port to a standalone runner (headless `claude -p` **with** file tools + per-project cwd), and a "researched ✓ / verdict" layer joined into the HTML queue dashboard by INR.

## 8. Benchmark protocol (acceptance)

1. User keeps their Hanson Solar findings hidden.
2. Agent runs blind from identity fields only; produces the full evidence dir.
3. Compare: lat/lon within ~1 km; same site/parcel; imagery interpretation consistent (clearing dates, extent); LLC chain correct.
4. Miss ⇒ diagnose which stage failed, amend PLAYBOOK.md, rerun. Match ⇒ v1 accepted; proceed to phase 2 planning.

## 9. Risks / known constraints

- CAD/deed portals vary wildly by county and some block automated fetches; the playbook must record blockers as negative evidence and route around (e.g., commissioners' minutes often restate tract data). Deed records (lease-vs-purchase) may be unavailable without a paid account in some counties → `land_tenure: unknown` is an acceptable honest answer in v1.
- CDSE API auth flow may need one manual dashboard step (OAuth client creation) before `cdse.py` is fully automated.
- No browser rendering in this container: "Google Maps image with the site highlighted" is produced via the Static Maps API rather than screenshots.
