# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a scratch/sandbox container, not a single-purpose project. There is no one major goal — the user tests different ideas here before branching mature ones out into their own dedicated repos. Expect loosely related, in-progress subfolders (e.g. `branch_tracking/`) rather than one coherent codebase. Don't assume subfolders share dependencies, conventions, or a common architecture unless they clearly do.

## Before compaction: dump context to memory

ALWAYS update the persistent memory files (project status, pending items, decisions made this session) BEFORE the context is compacted — when the user runs `/compact`, when context is getting long, or after any major milestone. Compaction summaries are lossy; memory is the durable record. Do not defer memory updates to "after".

## Git / credential setup

- `gitaccess.sh` — for use *outside* the Docker agent image. Installs a git credential helper (`~/.local/bin/git-credential-token-vending`) that fetches a fresh token from a token-vending sidecar (`TOKEN_VENDING_URL`, default `http://localhost:8080`) on every git network operation, using `AGENT_ID` and `AGENT_SECRET_FILE`/`AGENT_SECRET`. Source it once per shell: `. ./gitaccess.sh`. Only works over HTTPS remotes (`https://github.com/...`), not `git@github.com:...` SSH URLs.
- `startup.sh` — entrypoint wrapper intended for the Docker agent image itself. Points git at a tmpfs-backed config (`GIT_CONFIG_GLOBAL=/tmp/.gitconfig`) so vended tokens never touch persistent disk, sets `user.name`/`user.email` from `AGENT_GIT_NAME`/`AGENT_GIT_EMAIL`, then `exec`s the given command.

## Independent repos cloned elsewhere

Other Appian Way repos (`LocalSkills`, `awconnect`) have been cloned under `/home/node/` rather than inside this repo, since they are independent projects with their own git history — keep it that way rather than nesting other repos' `.git` directories under this one.

## Python environment

`.venv` here is a `uv`-managed virtualenv (`uv venv`) local to this repo. `awconnect` is declared in `pyproject.toml` as an editable path dependency on `/home/node/awconnect`, so `uv sync` keeps it — edits to that checkout are picked up immediately without reinstalling.

`pfa` (the `powerflow_analytics/pfa/` library) is installed editable from `powerflow_analytics/` (a uv workspace member), so scripts and tests import it without `sys.path` edits.

**Always run Python through `uv`** (`uv run script.py`, `uv run python -c ...`, `uv pip install ...`), never a bare `python`/`pip`. A minimal `pyproject.toml` marks this directory as the uv project root, so plain `uv run ...` from here (or any subfolder) resolves to this repo's `.venv` automatically — no `VIRTUAL_ENV=` override needed. If a container-wide `VIRTUAL_ENV` env var is set to something else, `uv run` still prefers the project `.venv` because `pyproject.toml` is present; only `uv pip install` without a preceding `uv run` can be redirected by a stray `VIRTUAL_ENV`, so prefer `uv run python -m pip install ...` or `uv add`/`uv pip install` from this directory if that ever resurfaces.

pyarrow is capped below 24 (root `pyproject.toml`) because awconnect 1.5.x requires it. The `awconnect` source is the absolute path `/home/node/awconnect` so git worktrees under `.claude/worktrees/` resolve it too.

## Division of labor (sdalvi's standing rule, 2026-08-10)

The main session model (Fable/Opus-class) does **thinking, grading, and planning only**: design the approach, write specs/briefs, review and grade results, decide what's next. **All coding labor is dispatched to Sonnet 5 subagents** (`model: sonnet` on the Agent tool) — file edits, script writing, debugging, running pipelines. This saves tokens and keeps the expensive model's context for judgment. Small verification queries/greps by the main session are fine; writing or fixing code directly is not.

**Mandatory grading gate (sdalvi, 2026-08-12):** every substantive deliverable (report, ranking, valuation output, analysis HTML) must be graded by an **Opus reviewer agent** (`model: opus`) BEFORE being presented to the user as done. The grader gets: the spec/brief, the deliverable file(s), and explicit "would a senior trader find this ranking sane?" review questions — including whole-output sanity (does the SORT make sense? are top rows defensible end-to-end?), not just per-cell checks. Failures go back to the implementer; the deliverable is only surfaced after a passing grade. This exists because per-cell verification repeatedly missed structurally broken rankings.

## Subprojects

Live:

- `powerflow_analytics/` — SCOPF study output (Snowflake AWOPF) → CRR opportunity finder: binding constraints, marginal units, offer-derived λ(depth), outage drivers, valuation. Own `CLAUDE.md` (data gotchas + study-family rules).
- `fast_scan/` — study-vs-DART shift-factor benchmarking and fast-scan work; includes `station_injection/` (SE net injection by kV, fast-scan V2 procs, bus-injection plan).
- `analytics/` — ad-hoc congestion/shift-factor analysis scripts (own `CLAUDE.md`).

Archived (frozen, not developed here):

- `archive/branch_tracking/` — transmission-branch tracking table (ERCOT / `isomarketid = 6`); graduated to the baseline repo.
- `archive/gis-research/` — ERCOT GIS interconnection-queue research + HTML queue report; graduated to the precog repo.
- `archive/load-forecast/` — ERCOT weather-zone load-growth + scenario-replay engine; parked.

## Branches and specs

1. `master` is the single line of work; each session works on a short-lived branch off master and merges back when its task is done; no long-lived per-project branches.
2. Worktrees go only under `.claude/worktrees/`, never `/tmp`.
3. Plans and specs are not committed as files; they go in GitHub issues on awe-sd/scratch-container.
