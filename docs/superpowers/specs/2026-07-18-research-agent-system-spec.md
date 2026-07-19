# ERCOT Project-Research Agent System — Full Spec (for refactor handoff)

**Date:** 2026-07-18 · **Subproject:** `gis-research/` · **Audience:** an agent doing a
deep, critical-eye refactor of `gis-research/scripts/research_tools/`.

**This document supersedes `2026-07-17-project-research-agent-design.md` as the description
of the *running* system.** That earlier doc describes "v1" as a single in-session deep agent
and labels headless/batch execution as "phase 2, out of scope." The system that now exists
*is* that phase 2 — headless `claude -p` runners with a triage/deep split and batch
orchestration. Where the two disagree, this doc is authoritative. The 2026-07-17 doc is still
the reference for the original design rationale (§2 "why the previous runner failed" and the
findings.json v1 schema in its §5, which the code still targets).

---

## 0. How to read this spec

Three layers, in priority order for a refactor:

1. **§1 Invariants** — things that must still be true after the refactor. Most were paid for
   in failures this session. Do not optimize any of these away without understanding the
   constraint. A "critical eye" that deletes a workaround because the code looks ugly, without
   the constraint that forced it, will regress the system.
2. **§2–§6 Current implementation** — what each piece does, the data flow, the instruction-set
   artifacts (prompts/checklist/playbook/templates) that *are* the product.
3. **§7 Known issues & drift** — bugs, staleness, and duplication, each with its "why."
   This is the refactor's raw material. Every item here has a reason attached; preserve the
   behavior, improve the form.

**The self-check for any change:** could a fresh agent, given only this spec and the code,
make the change without breaking an invariant (§1) or re-introducing a bug already fixed
this session (§7)? If a proposed edit fails that test, it is wrong regardless of how much
cleaner it looks.

---

## 1. Invariants (must survive the refactor)

**I1. The Hanson Solar benchmark must still pass.** `research/23INR0086_hanson-solar/` is the
gold-standard exemplar the deep playbook was tuned against (blind run converged on the
hand-researched site within ~1 km). Any change to the deep prompt, PLAYBOOK, or DOSSIER
template must be re-validated against it. It is also the worked example the deep prompt points
the agent at.

**I2. Security model.**
- Real credentials live ONLY in `~/.config/gis-research.env` (outside the repo, chmod 600).
  Keys: `CDSE_USERNAME`, `CDSE_PASSWORD`, `GMAPS_API_KEY` (satellite/maps), plus AWS creds via
  the standard chain. Never committed, never printed by tools, never pasted into chat.
  `.gitignore` blocks `*.env` except `example.env`.
- Agents are blocked from reading the raw queue data: `--disallowedTools` denies
  `Read`/`Grep` on `gis-research/data/**` and `gis-research/output/**`. The RUNNER reads the
  parquet and hands the agent a curated identity packet; the agent must never see the full
  table (that is what made the previous agent parrot the milestone columns as "findings").
- **Banned sources** (queue aggregators that republish the GIS report — citing them is an
  automatic fail): interconnection.fyi, cleanview.co, gridinfo.com, energyacuity, any
  "interconnection queue tracker." Enforced by prompt/PLAYBOOK, not code.
- Agents write ONLY inside their assigned `research/<INR>_<slug>/` directory.

**I3. Identity-packet-only input.** The agent receives project name, INR, LLC guess, county,
MW, fuel/tech, POI description, CDR zone, and the reported COD *explicitly labeled as an
unverified claim*. It never receives the milestone/status columns. This is the anti-word-salad
rule; violating it reintroduces the original failure mode.

**I4. Imagery discipline (the #1 cost driver).** Satellite image reads dominate cost because
each full-size PNG a headless agent reads is re-sent from cache on every subsequent turn
(cache-read compounding). The rules that exist because of this:
- Search TIGHT (2–3 km buffer grid, ±0.03° steps), present WIDE (6 km xwide only for final
  reviewer frames).
- Judge from ONE contact sheet (`cdse.py sheet`), not individual frames.
- Hard cap **≤6 full-size frame reads (deep), ≤4 (triage, incl. the contact sheet)**. The
  post-run audit counts PNG `Read` tool-uses and flags breaches.
- "Look around before concluding": the delivery pin is the gate, not the array centroid; a
  600 MW site spans ~10 km, so re-center on edge activity before calling `no_activity`.

**I5. Triage-first, deep is gated.** Triage (cheap, budgeted) runs across the whole cohort and
emits `deep_scan_recommended`. Deep (expensive, full playbook) runs ONLY on flagged projects,
and only via a human decision or the dedicated deep worker. **Never chain `triage && deep`**
in one command — that was an early mistake that spent Opus money on paper projects the triage
had already correctly killed.

**I6. Concurrency ceiling ≤15 simultaneous agents.** Running ~20 crashed the Claude Code
session. Current stable topology: **4 triage batches × concurrency 3 = 12 Sonnet triage
agents + 1 serial deep worker = 13**. Stay at or below 15. The true agent count is
`pgrep -fc 'claude [-]p'`; process-table rows over-count because each agent is a
`zsh → uv → python → claude` chain (batch-spawned agents skip the zsh layer, so ~2–4 rows each).

**I7. Everything is resumable and idempotent per project.** A run writes into
`research/<INR>_<slug>/`. Re-running skips projects whose completion marker exists
(`triage_findings.json` for triage, `findings.json` for deep) unless `--force`. A killed batch
or worker loses only in-flight work; relaunch continues. This is what made the mid-session
crash cost only time. Do not introduce shared mutable state that breaks this.

**I8. Deterministic wrap-up tools are the source of truth for queue history.** COD-drift and
milestone timelines come from `queue_history.py` reading the local parquet (all monthly
snapshots since 2014) — NOT from the agent's web research. The agent must not invent milestone
history. `build_brief.py` and `build_index.py` are likewise deterministic renderers; the agent
runs them, it does not hand-write their outputs.

**I9. Cost-reporting rule (org policy).** Operations costing ≥ $1 must be reported to the user
with a token/cost breakdown. `run_meta_<mode>.json.total_cost_usd` (Bedrock-metered) is the
source of truth, not estimates.

---

## 2. System overview & data flow

```
                        parquet (ercot_generation_interconnect.parquet)
                             │  latest snapshot, active-queue filter
                             ▼
   run_batch.py ── selects INRs (COD window / fuel / MW / explicit list)
       │  ThreadPoolExecutor(concurrency)
       │  skips projects with completion marker (resumable)
       ▼
   run_agent.py <INR> --mode triage|deep      ◄── one INR per process
       │  builds identity packet (RUNNER reads parquet; agent cannot)
       │  spawns:  claude -p <prompt> --model … --allowedTools … --disallowedTools …
       │           --output-format stream-json --settings <budget hook>
       │  streams stdout: accumulates fresh tokens, updates .budget_state.json,
       │                  hard-kills at budget+grace
       ▼
   headless claude agent  (Bedrock: CLAUDE_CODE_USE_BEDROCK=1)
       │  triage → follows TRIAGE_CHECKLIST.md (injected INLINE into prompt)
       │  deep   → follows PLAYBOOK.md (read BY PATH by the agent)
       │  tools it calls: cdse.py (Sentinel-2), gmaps.py (Places/staticmap),
       │                  queue_history.py, build_brief.py, build_index.py,
       │                  WebFetch, Bash/curl
       ▼
   research/<INR>_<slug>/   ← per-project evidence dir (see §5)
       │
       ├─ triage_findings.json ──► run_batch summary.csv + deep_queue.txt
       │                            make_deep_queue.py → deep_queue_all.txt
       ▼
   deep_worker.py  ── serial loop: pick largest-MW flagged & not-yet-deep,
                      run run_agent --mode deep, repeat; idle when dry
```

**Two ways the instruction set reaches the agent, and they differ:**
- **Triage:** `TRIAGE_CHECKLIST.md` is read by the runner and **interpolated verbatim into the
  prompt string** (`run_agent.py:234`). The agent gets the checklist as part of its initial
  message; it does not read the file itself.
- **Deep:** `PLAYBOOK.md`, `DOSSIER_TEMPLATE.md`, and the Hanson example are referenced **by
  path** in the prompt (`run_agent.py:128–132`); the agent reads them with its own `Read` tool.

A refactor that unifies these must preserve the distinction or account for it (triage's
checklist is guaranteed in-context; deep's playbook depends on the agent actually reading it).

---

## 3. Execution environment (Bedrock headless)

- Auth: `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_PROFILE=read_only`, `AWS_REGION=us-east-1`
  (`run_agent.py:242–249`). Standard AWS credential chain.
- Models are Bedrock inference-profile IDs: `us.anthropic.claude-sonnet-4-6`,
  `us.anthropic.claude-opus-4-7`.
- **`ANTHROPIC_SMALL_FAST_MODEL=sonnet` is a required workaround** — the account is not
  authorized for Haiku (`bedrock:InvokeModelWithResponseStream` on the Haiku profile → 403),
  and Claude Code otherwise makes internal Haiku calls that would 403 the whole run.
- **`WebSearch` is in `ALLOWED_TOOLS` but is a dead tool on Bedrock** — server-side web search
  is Anthropic-API-only. Agents fall back to `WebFetch` against search-engine HTML. Listing it
  is harmless but misleading.
- Headless `claude -p` has **no stdin** — you cannot steer or `/compact` a running session.
  This is why mid-run budget messaging is done through a PostToolUse hook (§4), not interaction.
- `--output-format stream-json --verbose` emits one JSON event per line: `type=assistant`
  (with `message.content[].tool_use` blocks and `message.usage`), and a final `type=result`
  (with `total_cost_usd`, `num_turns`, `usage`, `subtype`, `session_id`).

---

## 4. Budget & guardrail system (three overlapping mechanisms — all deliberate)

Because a headless run cannot be steered, three independent limits protect it. A refactor
should keep all three; they cover different failure modes.

1. **`--max-turns` hard cap** (`TRIAGE_MAX_TURNS=60`, `DEEP_MAX_TURNS=120`). Stops runaway
   loops. Note: the API turn count runs ~1.5× the agent's self-counted turns, which is why the
   triage cap is 60 even though the checklist targets ~35.

2. **Fresh-token budget with graceful shutdown** (triage 100k, deep uncapped by default):
   - The runner stream-parses `message.usage` live and accumulates **fresh tokens =
     `input_tokens + cache_creation_input_tokens + output_tokens`**. Cache *reads* are
     excluded — they are the cheap re-reads, and including them would punish the agent for the
     runner's own context growth.
   - It writes `.budget_state.json` (atomically, via `.tmp` + `replace`) after every assistant
     event.
   - `budget_hook.py` runs as a **PostToolUse hook** (registered via a generated
     `.budget_settings.json` passed with `--settings`). After each tool call it reads the
     state file and, using once-only marker files:
     - **≥80%** → prints a wrap-up *warning* to stderr and exits 2 (exit-2 feeds stderr back
       into the agent's conversation).
     - **≥100%** → prints a STOP-and-write-output order, exits 2.
   - The runner **hard-kills at `budget + GRACE_TOKENS` (10k)** so the agent gets ~10k tokens
     to flush its output files after the 100% order. Files on disk are all that survive a kill.
   - `budget_hook.py` is intentionally **stdlib-only on bare `python3`** (not `uv run`) — it
     fires on every tool call and uv startup overhead would tax each one. This is the one
     sanctioned exception to the "always use uv" rule.

3. **Post-run audit** (`validate()`, `run_agent.py:170`): re-parses the stream and records
   `assistant_turns`, `image_reads` (PNG `Read` tool-uses), per-tool counts, and a `violations`
   list (image-read cap breach; missing/invalid required artifacts; budget-kill). Written to
   `run_meta_<mode>.json`. Report-only — it does not fail the run, it characterizes it.

**`max-turns + valid-artifacts → exit 0` remap** (`run_agent.py:325–332`): if the run hit
max-turns (`subtype == error_max_turns`) but the required artifacts exist on disk, the runner
rewrites the exit code to 0. Reason: a usable run that merely ran long should not be read as a
failure by `run_batch`/chains (which key off exit code and marker presence). Do not "clean this
up" into a plain pass-through of the child exit code — it will make good runs look failed.

---

## 5. Per-project directory & artifacts

```
research/<INR>_<slug>/            # slug = slugify(projectName)
  # TRIAGE outputs
  triage_findings.json            # machine-readable; completion marker for triage
  triage.md                       # ≤10-line human summary
  # DEEP outputs
  findings.json                   # machine-readable; completion marker for deep
  dossier.md                      # analyst report, follows DOSSIER_TEMPLATE.md
  log.md                          # every search incl. negatives (write-as-you-go)
  brief.html                      # generated by build_brief.py
  # shared / tool outputs
  timeline.json / timeline.md     # queue_history.py (deterministic, from parquet)
  sources/                        # saved docs: <YYYY-MM-DD>_<source>_<desc>.<ext>
  imagery/                        # s2_*.png chips; imagery/key/ = reviewer frames
  run_stream_<mode>.jsonl         # raw stream log
  run_meta_<mode>.json            # result stats + audit + fresh_tokens + violations
  .budget_state.json/.tmp, .budget_settings.json, .budget_*_sent   # transient budget plumbing
```

**`triage_findings.json` schema** (validated keys: `signals`, `deep_scan_recommended`,
`cod_first_look`):
```json
{"inr","project","triage_date",
 "signals":{"ia_found","abatement_found","pins_found","news_found","construction_visible"},
 "site_candidate":{"lat","lon","method","confidence"}|null,
 "construction":{"verdict","evidence"}|null,
 "cod_first_look":{"reported","plausible","why"},
 "deep_scan_recommended":bool, "deep_scan_focus":[…], "turns_used":int}
```

**`findings.json` schema** = 2026-07-17 spec §5 (site, parcels, llc_chain, land_tenure,
construction, cod_assessment, real_project_verdict, …) **plus two fields added this session:**
- `project_area`: `{acres, source, artifact}` — stated acreage from abatement/IA/CAD docs, so
  the reviewer can sanity-check the imagery footprint. Rendered as a card in brief.html.
- `contractual_schedule.documents`: `[{doc, signed, financial_security, artifact}]` — one entry
  per IA document. **Financial security is recorded per-document, not as one number, because it
  often rises with amendments.** Rendered as the "IA document | Signed | Financial security"
  table in brief.html and DOSSIER_TEMPLATE §5.

`build_index.py` scans all `findings.json` → `research/index.json` (programmatic) +
`research/INDEX.md` (human table). Only deep-scanned projects appear (keyed off findings.json).

---

## 6. The instruction-set artifacts (these ARE the product)

### 6.1 Identity packet (`run_agent.py:89`, `PACKET`)
Formatted with the parquet row + `fuel_notes()`. Fuel-specific guidance is injected by fuel:
- **battery** — compact site (10–80 acres even at 1 GW), search 1-km chips around the POI
  substation, fast build, thin county paper trail.
- **thermal** (GAS/NUC/COA/BIO or CC/GT/IC/ST) — TCEQ air permit (NSR) is MANDATORY (absence =
  strong paper signal); "(TEF …)" name → PUCT Texas Energy Fund docket; turbine orders =
  reality signal; industrial-site imagery signature.
- **wind** — FAA OE/AAA filings carry exact turbine coordinates; imagery = turbine-pad strings
  + access roads, not one polygon.
- **solar** — no note (it is the PLAYBOOK/checklist default).

### 6.2 Triage checklist (`research/TRIAGE_CHECKLIST.md`, injected inline)
Goal ≤35 agent turns. Rules of engagement: execute T1→T7 in order, each within its tool-call
budget; budget spent → log result (even "nothing") → next step; log `T<n> start` before each;
drift → stop/log/return; ≤1 contact sheet + ≤3 full-size reads; blocked portal = ONE retry then
negative log; T7 always runs (all-negative triage is a valid result — likely paper).
- **T1** queue_history.py + read timeline (budget 2)
- **T2** gmaps places pins — name, name+county, name+fuel+town, LLC (budget 4)
- **T3** web sweep DDG/Bing via WebFetch (budget 5)
- **T4** PUCT Interchange: FilingParty → Description → alt name; IA → parties + schedule pages
  only (budget 6)
- **T5** Ch.313 + JETI, county-filtered (budget 4)
- **T6** imagery: best estimate pin > map > POI, else SKIP; 3×3 tight grid (2 km, ±0.03°) →
  contact sheet → read the SHEET; activity → recenter + 1 current + 1 baseline full read
  (budget 8)
- **T7** write triage_findings.json + triage.md ≤10 lines; NO build_brief/index (budget 6)

### 6.3 Deep playbook (`research/PLAYBOOK.md`, read by path)
Five stages, evidence first, opinion last. Hard rules: banned sources; artifacts-or-it-didn't-
happen; log negative evidence; **write-as-you-go** (append to log.md the moment you find
something — context may be compacted); no county centroids; search-tight/present-wide; ≤6
full-size frame reads.
- **Stage 1** LLC → parent (TX Comptroller taxable-entity search, SOS, PRs, LinkedIn)
- **Stage 2** county records (CAD parcel-by-owner, Ch.312/313/JETI, commissioners' minutes,
  PUCT Interchange for the signed IA); capture `project_area`; fuel-specific paper trails
- **Stage 3** site pinpoint (delivery-pin trick first; POI/OpenInfraMap; parcel; news; cross-
  check pin↔parcel↔POI, investigate disagreement rather than average)
- **Stage 4** satellite ground truth (cdse.py chip/timelapse/sheet; present-first early-exit;
  fuel-specific 10 m/px signatures; ≤6 reads)
- **Stage 5** synthesis (dossier.md per DOSSIER_TEMPLATE.md + findings.json), then the three
  deterministic wrap-up commands (queue_history, build_brief, build_index)

### 6.4 Dossier template (`research/DOSSIER_TEMPLATE.md`)
8 sections, ≤~60 lines, every claim inline-linked to a `sources/` artifact or URL. §2 carries
the stated project area vs imagery-footprint check; §5 carries the per-document IA/security
table + contractual schedule.

### 6.5 Prompts (`run_agent.py`)
`TRIAGE_PROMPT` (checklist as "complete and only instructions" + budget-kill warning) and
`DEEP_PROMPT` (PLAYBOOK by path, read triage handoff first, wrap-at-80%-turns instruction,
findings.json schema pointer). Both embed the identity packet.

---

## 7. Known issues, drift & refactor targets (each with its "why")

**Behavior to preserve — do not "fix" these into regressions:**
- The `max-turns + artifacts → exit 0` remap (§4). Reason: chains/batch key off exit code.
- The three-mechanism budget system (§4). Reason: headless has no stdin; each mechanism covers
  a different failure.
- `budget_hook.py` on bare `python3`. Reason: per-tool-call overhead.
- Imagery read caps and contact-sheet discipline (I4). Reason: cache-read cost compounding.
- `ANTHROPIC_SMALL_FAST_MODEL=sonnet` (§3). Reason: Haiku 403s on this account.

**Genuine defects / staleness to fix:**
1. **`run_agent.py` module docstring is stale** (lines 1–16): says "triage — Sonnet, hard
   45-turn cap" and "deep — Opus." Actual: triage cap 60; deep default is **Sonnet**
   (`DEEP_MODEL`, line 34), Opus only via `--model`.
2. **Deep model is inconsistent across entry points** — state precisely, then unify:
   - `run_agent.py --mode deep` → Sonnet (`DEEP_MODEL`).
   - `deep_worker.py` → **Opus** by default (`--model opus`, its own `MODELS` map).
   - `run_batch.py --mode deep` → whatever `run_agent` defaults to → Sonnet.
   The live deep worker is therefore running Opus while a batch deep pass would run Sonnet.
   This directly affects cost; a refactor should make deep-model selection single-sourced.
3. **`WebSearch` listed but dead on Bedrock** (§3). Decide: drop it from `ALLOWED_TOOLS`, or
   document why it stays.
4. **`validate()` parses the stream file a second time** after the runner already parsed it
   live (`run_agent.py:170` vs the streaming loop at 285). One pass could produce both the live
   token tally and the audit.
5. **Duplication across the tool scripts** (ripe for a shared module):
   - `load_env()` — identical in `cdse.py:39` and `gmaps.py:24`.
   - `slugify()` — identical in `run_agent.py:152` and `run_batch.py:33`.
   - "read parquet, filter to latest snapshot" — in `run_agent.py`, `run_batch.py`,
     `queue_history.py`, `make_deep_queue.py`, and (active-queue variant) `run_batch.select`.
   - `BASE = Path(__file__).resolve().parents[2]` prologue — every script.
   - active-queue exclusion (`cancelDate`/`inActiveDate`/`approvedForCommercialOperation`
     isna) — in `run_batch.select` and elsewhere; should be one documented helper.
6. **Two overlapping deep-queue builders:** `run_batch.py` writes a per-batch `deep_queue.txt`
   (triage mode only); `make_deep_queue.py` writes a global `deep_queue_all.txt` across all
   triaged dirs. `deep_worker.py` uses neither file — it re-scans `triage_findings.json`
   directly. Three ways to answer "what needs a deep scan." Consider consolidating to one
   queue source of truth.
7. **`run_batch.py` and `deep_worker.py` both shell out to `run_agent.py` via `uv run`
   subprocess** rather than importing it. Fine for process isolation and the token-budget kill
   (which needs its own process), but means CLI args are the only interface — keep that
   interface stable or refactor both callers together.
8. **`cdse.py` heavy deps imported lazily** inside functions (`numpy`, `xarray`, `PIL` in
   `timelapse`; `PIL` in `sheet`) — intentional (keeps `chip` fast), note before "tidying"
   imports to module top.
9. **`FUEL_LABEL`/`fuel_notes` fuel-code matching** duplicates logic that
   `build_queue_report.py::normalize_fuel_tech` already does elsewhere in the subproject; the
   messy 12-year fuel/tech code forms (SOL/Solar/SOLAR, OTH+BA=battery) are a documented data
   gotcha (see `gis-research/CLAUDE.md`). Reuse one normalizer.
10. **Operational hygiene lesson (not code):** `pkill -f "run_batch.py"` matches its own
    command line and self-terminates the kill before it works; use the bracket trick
    `pkill -f "run_batch[.]py"`. Worth a comment or a small `stop_all` helper script.

---

## 8. Current operational state (snapshot; changes as batches run)

- Triage batches launched for COD windows: 2028H1 (205), 2026H2 (146), 2027H1 (118),
  2027H2 (310), each at concurrency 3. One serial Opus deep worker over flagged projects.
- At last count ~243 triaged, ~114 flagged `deep_scan_recommended`. Flag rate is high
  (~40–47%); the deep pass is the expensive one, so the human/worker gate on the flag queue is
  where cost is actually controlled.
- Benchmarks/format tests done this session: Zeus Mitchell BESS II (paper), Aegle Power
  (paper; Opus deep $12.13 — the cost argument for Sonnet-default deep), Hobby BESS I (first
  `deep_scan_recommended`). Short Creek Solar (24INR0201) is the imagery-discipline cautionary
  tale (site misidentification fixed by georeferencing).

---

## 9. File map

| File | Role |
|---|---|
| `scripts/research_tools/run_agent.py` | one INR, one mode; builds packet, spawns headless agent, enforces token budget, audits |
| `scripts/research_tools/run_batch.py` | selects INRs from parquet, runs run_agent at concurrency N, writes summary.{json,csv} + deep_queue.txt |
| `scripts/research_tools/deep_worker.py` | serial loop: deep-scan largest-MW flagged-not-done project; idles when queue dry |
| `scripts/research_tools/make_deep_queue.py` | global deep_queue_all.txt from all triaged dirs |
| `scripts/research_tools/budget_hook.py` | PostToolUse hook: 80% warn / 100% wrap-up order (stdlib, bare python3) |
| `scripts/research_tools/cdse.py` | Sentinel-2 via CDSE openEO: chip / chips / timelapse / sheet |
| `scripts/research_tools/gmaps.py` | Google Places text search + Static Map |
| `scripts/research_tools/queue_history.py` | per-project milestone/COD-drift timeline from parquet (deterministic) |
| `scripts/research_tools/build_brief.py` | findings.json → one-page brief.html |
| `scripts/research_tools/build_index.py` | all findings.json → index.json + INDEX.md |
| `research/TRIAGE_CHECKLIST.md` | triage instruction set (injected inline into prompt) |
| `research/PLAYBOOK.md` | deep instruction set (read by path by the agent) |
| `research/DOSSIER_TEMPLATE.md` | required dossier shape |
| `research/23INR0086_hanson-solar/` | benchmark exemplar (I1) |
| `docs/superpowers/specs/2026-07-17-project-research-agent-design.md` | original design rationale + findings.json v1 schema |
