# Pipeline v2 — facts first, agents second

Design spec for the second-generation gis-research workflow. Approved by sdalvi
2026-07-19 through interactive brainstorming; supersedes the incremental
TRIAGE_CHECKLIST/PLAYBOOK patches of 2026-07-18/19 as the system's shape.

## 1. Purpose and the gating inversion

The business question is the ERCOT queue's **real capacity and its real timing**:
which claimed MW will actually reach commercial operation, where, and when.

- **Triage exists to kill paper cheaply.** A project with strong paper signals
  (dropped from EIA-860M, no IA anywhere, FIS stalled for years, unresolvable SPV,
  absent from EIA with near-term claimed COD) is dismissed at triage with the
  evidence listed. Paper projects get **no deep scan** — there is nothing on the
  ground to scan.
- **Deep scan exists for precision on projects that look real.** Reality signals
  (EIA status (U)/(V), TPIT gen-tie activity, IA signed + FIS approved, registry
  filings, construction plausible in imagery) route a project to deep scan, whose
  deliverable is independent COD/drift, exact site, construction stage, and the IA
  milestone schedule. Deep queue is ranked **MW × COD-nearness** — the big
  near-term projects move the market.
- Exemplars validating the frame: Red Egret (real, construction started, gen tie
  unfinished 43 days before claimed COD → drift finding) and Buffalo Creek (built,
  synced, stalled 4.5 years → anomaly finding) are exactly the deep-worthy class;
  Zeus Mitchell (paper BESS) never needed $4 of deep scanning.

## 2. Evidence (log forensics, 944 runs, 57,865 tool calls, $1,393)

| Finding | Number |
|---|---|
| Web fetches as share of all tool calls | 51.3% |
| PUCT portal WebFetches, 100% HTTP-402 | 3,012 |
| SEC EDGAR fetches, 100% failed | 1,196 |
| Search-engine HTML scraping (WebSearch unavailable on Bedrock) | 7,260 |
| Web calls hitting domains with a local tool replacement | ~43% |
| Non-success deep runs | 52/159 |
| — token-budget kills / max-turns / hard kills | 33 / 28 / 14 |
| Failed runs that wrote NO findings (work fully lost) | 39/75 |
| Violations that are "output file missing" | 74/137 (54%) |
| Stuck-loop episodes (same call ≥5× consecutively, worst 26) | 363 |

Full analysis: `docs/analysis/2026-07-19-logmine/` (copied from the forensics
scratchpad; includes tool_sequences.parquet, failure_inrs.csv, report.md).

## 3. Stage 0 — `factsheet.py` (new tool, deterministic, no LLM)

Per INR, assembles everything answerable locally, in seconds:

- queue row + milestone staleness (ercot parquet; grain (INR, fileDate), milestone
  columns are dates-or-null)
- COD slip history (`queue_history`)
- EIA-860M history: planned-COD/capacity/MWh/status change-points, coords, county,
  divergence vs queue COD, DROPPED_FROM_860M (`eia_history.resolve`, in-process)
- SPV candidates (`spv.py`) and fuel-appropriate registry hits (`ch313.py` /
  `faa.py` / `tceq.py` resolvers)
- IA inventory: verified PDFs already in `sources/`, else docket items from
  `research/_reference/puct_inr_join.json` (the harvest join table: 1,743 items,
  1,201 with INRs, 897 distinct INRs, 22 image-only)
- **reality/paper score** (§4) with every contributing factor named

Outputs `factsheet.json` + human-readable `factsheet.md` into the project dir.
Bulk mode (`--all`, resumable) backfills all ~779 triaged projects.

## 4. Score and gate

Score axis = **paper risk** (high = paper). All factors deterministic:

| Factor | Points |
|---|---|
| COD slips ≥3 (scaled to 20 at ~10 slips) | up to 20 |
| EIA planned COD ≥2 quarters later than queue COD | 15 |
| DROPPED_FROM_860M — whole plant | 25 |
| DROPPED_FROM_860M — units only | 10 |
| iaSigned but no verified IA PDF (disk + join table both dry) | 10 |
| FIS requested >2y ago, never approved | 10 |
| Queue age >4y without sync approval | 10 |
| SPV unresolvable (spv.py + all registries dry) | 10 |
| Absent from EIA entirely with claimed COD <18 months out | 10 |

Reality signals recorded alongside (not scored, listed): EIA status (U)/(V),
operating-date present, verified IA on disk, FIS approved,
financial_security_posted (adjudicated 2026-07-20), TPIT reference if known.
Registry hits (ch313/JETI/FAA) are unverified leads, not a reality signal — they
suppress the `spv_unresolvable` score factor (a registry hit counts as SPV
resolved) but do not gate deep scans on their own; a project whose only reality
claim is an unverified registry hit still routes to the ambiguous/recheck band.

**Gate (as adjudicated by sdalvi 2026-07-20 — supersedes the original draft):**

```
paper_score ≥ 50                        → paper_kill
paper_score < 50 AND ≥1 reality signal  → deep_candidate,
                                          priority = MW × COD-nearness
otherwise                               → ambiguous → triage-v2 LLM decides
```

Rationale (Task 7 evidence): the original draft's bare `COD<18mo OR MW≥200`
triggers gated 89% of the corpus deep; v1 agent verdicts agreed with the
reality-signal cohort 79% but with the bare-trigger cohort only 25%. The
bare triggers survive only inside the priority number. Additionally,
paper_kill projects whose v1 triage recommended deep (10 conflicts) are
routed to the triage-v2 re-check list (`triage_recheck_v2.txt`) rather than
dismissed unseen.

Triage agent may adjust the score **±15 max, only with a cited source**; the
adjustment and citation are recorded in `triage_findings.json.score_adjustment`.
The human gate on the deep queue remains.

## 5. Triage v2 (Sonnet, ~15 turns, 40k fresh-token budget)

T1 read `factsheet.md` (injected into the prompt; no rediscovery)
T2 identity sanity: SPV/EIA/registry coherence; flag contradictions
T3 contest the score: ≤10 targeted web checks on the weakest facts only
   (cancellation/financing news, developer site, county news)
T4 verdict (`paper_dismissed` / `deep_candidate` / `ambiguous`) + score
   adjustment with citation
T5 write `triage_findings.json` (schema adds `score_adjustment{delta, citation}`)

Expected cost ~$0.25–0.40 vs $0.95 today; expected WebFetch ≤10 vs ~16.

## 6. Deep v2 (Sonnet, 400k fresh-token budget, checkpointed)

D0 write `findings.json` **skeleton first** (all keys, nulls), read factsheet +
   inventory `sources/` (IA PDFs are usually already there)
D1 IA milestone-schedule exhibits → `contractual_schedule` (per-document rows)
D2 site fix + imagery: cdse chips (≤6 image reads), boundary-map extraction →
   `site.map_artifacts`
D3 gap-fill: county records/news — local tools first, web last
D4 narrative, independent COD, drift verdict
D5 deterministic wrap-up: `queue_history` → `eia_history --write` →
   `build_brief` → `build_index`

**Every stage ends with a findings.json checkpoint write.** A budget kill then
costs at most one stage (fixes the 39 fully-lost runs).

## 7. Runner and hook changes (`run_agent.py`, `budget_hook.py`)

1. **PreToolUse domain blocklist**: `interchange.puc.texas.gov`, `sec.gov`
   full-text/EDGAR, `duckduckgo.com/html` + bing/yahoo scraping. Deny message
   names the replacement (`puct.py`, `spv.py`, `search.py`). Kills 4,208
   guaranteed-dead calls and the 26-deep retry storms.
2. **Checkpoint watchdog**: PostToolUse counts tool calls since the last
   `findings.json` write; >25 → inject warning turn.
3. **Provider flag**: `--provider bedrock|anthropic` (env-driven); Bedrock stays
   default. Insurance if an org `ANTHROPIC_API_KEY` ever lands (native WebSearch).
4. Prompts rewritten for T1–T5 / D0–D5; budgets: triage 40k, deep unchanged 400k.

## 8. `search.py` — managed web search on AWS (AgentCore)

- Backend: Bedrock **AgentCore Gateway** web-search connector (us-east-1, $7 per
  1,000 queries, inbound auth AWS_IAM/SigV4 — confirmed supported in the SDK).
- One-time infra: `scripts/setup_agentcore_gateway.py` (run with an admin
  profile) creates outbound role + gateway `gis-research-search` + web-search
  target, prints the inbound policy for the agents' principal and the
  `AGENTCORE_GATEWAY_URL` for `~/.config/gis-research.env`.
- `search.py "<query>"`: SigV4-signed MCP `tools/call` to the gateway; flock
  throttle; on-disk result cache keyed by normalized query (7 parallel agents
  never re-buy a query); plain-line output with provenance; `--selftest`.
- Fallback when the gateway env var is absent: throttled DDG HTML with the same
  cache, clearly labeled in provenance.

## 9. `puct.py match` rung 0

Before any name matching: look the INR up in `puct_inr_join.json` → exact docket
items → fetch + verify as today (INR-in-PDF). Name keys remain rung 1 for the 22
image-only filings and post-harvest filings until the join table is re-run
(`inr_harvest.py` is resumable; re-run monthly with the queue refresh).

## 10. Preservation — git + S3

**Git** (branch `worktree-GIS-research`): all scripts, playbooks/checklists,
docs, specs, every `triage_findings/findings/eia_history/timeline/factsheet`
JSON, dossiers, briefs, `_reference` join tables + CSVs, batch summaries,
gzipped agent transcripts, logmine analysis. **.gitignore'd (S3-only)**:
`sources/*.pdf`, `imagery/`, `data/reference/puct_docket_pdfs/`, `data/*.parquet`.

**S3** (bucket TBD by sdalvi, prefix `gis-research/`), append-only sync via new
`sync_s3.py` (dry-run default, `--execute` to run, never `--delete`):

```
s3://<bucket>/gis-research/
├── research/<INR>_<slug>/...            # 1:1 mirror of repo tree (PDFs, imagery,
│                                        #   transcripts .jsonl.gz, findings, briefs)
├── data/reference/puct_docket_pdfs/     # shared docket cache
├── data/reference/                      # join tables, indexes, 860M xlsx
├── data/snapshots/<table>/<YYYY-MM-DD>.parquet   # dated; S3 accumulates history
└── analysis/logmine/<YYYY-MM-DD>/
```

Rules: same relative paths as the repo; parquet snapshots get dated keys; local
is always "latest", S3 is the superset archive.

## 11. HTML presentation (`output/process_v2.html`, self-contained)

Audience: sdalvi + stakeholders. Content: (a) step 1→N instruction cards for
triage T1–T5 and deep D0–D5; (b) before/after panel with the real numbers
(cost/project, WebFetch counts, failure rates); (c) "where agents failed" — the
four measured failure classes, each with a real example from the logs and the
specific v2 fix, marked resolved; (d) the gate diagram (paper-kill vs deep).
No external assets; charts follow the repo's report conventions.

## 12. Migration order

1. Wire `puct.py match` rung 0 (join table is ready) — immediate
2. `factsheet.py` + rubric; backfill all 779 (no LLM); re-rank deep queue by
   MW × COD-nearness among gate-passers → sdalvi review
3. Checklist/playbook v2 + runner hooks + `search.py`
4. **Pilot: 3 projects** (1 triage-only ambiguous, 2 deep incl. one known truth
   e.g. re-run of a Hanson-class project) — acceptance: verdicts match known
   truth, cost within estimate, zero blocklist violations, checkpoints present
5. Commit everything (spec §10 list) + first S3 sync (needs bucket)
6. HTML presentation from real pilot + corpus data
7. Relaunch 7 Sonnet deep workers on the prioritized queue (absolute paths,
   ≤15 concurrent, claim files as today)

## 13. Invariants preserved (unchanged from v1)

Security model (creds only in `~/.config/gis-research.env`, agents write only in
their project dir, banned queue-aggregator sources, read-only SQL, subagents
never commit); triage-first, human deep gate; ≤6 image reads; ≤15 concurrent
agents; iaSigned never a join key; deterministic verification before citing any
IA PDF; Hanson 23INR0086 remains the benchmark exemplar.

## 14. Open items

- S3 bucket name + writable principal (sdalvi providing)
- AgentCore gateway URL after `setup_agentcore_gateway.py` run (sdalvi, admin
  profile)
- Optional: native WebSearch retest if an org Anthropic key ever appears
