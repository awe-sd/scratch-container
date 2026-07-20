"""Headless research-agent runner — one INR per invocation via `claude -p` on AWS Bedrock.

Two modes:
  triage (default) — Sonnet, hard 60-turn cap, follows research/TRIAGE_CHECKLIST.md
                     (T1-T5, factsheet-first). Cheap first pass; ends with a verdict:
                     paper_dismissed | deep_candidate | ambiguous.
  deep             — Sonnet (Opus available via --model us.anthropic.claude-opus-4-8),
                     follows research/PLAYBOOK.md end-to-end (run only after a
                     human approves the triage recommendation).

The RUNNER builds the identity packet from the local parquet; the AGENT is blocked from
reading it (--disallowedTools). Stream events → <project_dir>/run_stream.jsonl; summary +
budget-violation report → <project_dir>/run_meta.json.

Usage:
  uv run gis-research/scripts/research_tools/run_agent.py 24INR0201                # triage
  uv run gis-research/scripts/research_tools/run_agent.py 24INR0201 --mode deep
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
ROOT = BASE.parent                          # repo/worktree root (agent cwd)

TRIAGE_MODEL = "us.anthropic.claude-sonnet-4-6"
DEEP_MODEL = "us.anthropic.claude-sonnet-5"  # user-enabled 2026-07-20 (probe OK); Opus via --model us.anthropic.claude-opus-4-8
SMALL_MODEL = "us.anthropic.claude-sonnet-4-6"
TRIAGE_MAX_TURNS = 60  # v2 checklist goal is ~15 agent turns; cap left unchanged as headroom
DEEP_MAX_TURNS = 120
MAX_FULLSIZE_IMAGE_READS = {"triage": 4, "deep": 6}  # contact sheet counts as 1 in triage
# Fresh-token budget (input + cache_creation + output; cache READS excluded — they are the
# cheap re-reads). Graceful enforcement via budget_hook.py: warn the agent at 80%, order
# wrap-up at 100%, hard-kill at budget + GRACE_TOKENS. None = uncapped.
# cold-start cache-write is ~63k; the cap stops runaway work, not boot cost — pilot 2026-07-20
# evidence (40k and 80k both died to legitimate T1-T3 work on an ambiguous project before a
# verdict was written). Cost stays ~$0.40/run either way since cap != spend.
TOKEN_BUDGET = {"triage": 120_000, "deep": 400_000}
GRACE_TOKENS = 10_000
# v2 triage_findings.json verdict enum (TRIAGE_CHECKLIST.md T4); validate() also accepts
# the v1 `deep_scan_recommended` bool for back-compat with the 774 pre-v2 triage files.
VERDICT_ENUM = {"paper_dismissed", "deep_candidate", "ambiguous"}

ALLOWED_TOOLS = "Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch,TodoWrite"
DISALLOWED_TOOLS = (
    "Read(./gis-research/data/**),Read(./gis-research/output/**),"
    "Grep(./gis-research/data/**),Grep(./gis-research/output/**)"
)

FUEL_LABEL = {("SOL", "PV"): "Solar PV", ("WIN", "WT"): "Wind", ("OTH", "BA"): "Battery/Storage",
              ("GAS", "CC"): "Gas combined-cycle", ("GAS", "GT"): "Gas turbine",
              ("GAS", "IC"): "Gas reciprocating", ("GAS", "ST"): "Gas steam",
              ("NUC", "ST"): "Nuclear steam"}

FUEL_NOTES = {
    "battery": """Fuel-specific guidance (BATTERY):
- Site is COMPACT: 10-80 acres even at 1 GW — pale gravel pad + parallel container rows
  beside a substation. Search 1-km-buffer chips around the POI substation; wide grids
  scan right past it.
- Build is fast (~12-18 months): bare ground today can still make a near-term COD.
- County paper trail is thin (little land) — weight the IA, substation work, and
  developer PRs over CAD/abatements.""",
    "thermal": """Fuel-specific guidance (THERMAL):
- MANDATORY permits: a TCEQ air permit (NSR) must exist — search the TCEQ air-permit
  database; no air permit = strong paper-project evidence. Also check water supply.
- "(TEF ...)" in the project name = Texas Energy Fund loan applicant → check the PUCT
  TEF docket for due-diligence status.
- Turbine orders (GE/Siemens/Mitsubishi) in PRs = strong reality signal (multi-year lead).
- Imagery: one industrial site — laydown yard, cranes, turbine hall, cooling structures;
  multi-year build, usually near pipelines / existing industry.""",
    "wind": """Fuel-specific guidance (WIND):
- FAA OE/AAA obstruction filings carry exact turbine coordinates — decisive, search early.
- Imagery: no single polygon — strings of small turbine pads + new access roads across
  tens of km. Grid wide; look for pad strings and road networks.""",
}


def fuel_notes(fuel: str, tech: str) -> str:
    f, t = str(fuel).upper(), str(tech).upper()
    if t == "BA" or "BATTERY" in f:
        return FUEL_NOTES["battery"]
    if f in ("GAS", "NUC", "COA", "BIO") or t in ("CC", "GT", "IC", "ST"):
        return FUEL_NOTES["thermal"]
    if t == "WT" or f.startswith("WIN"):
        return FUEL_NOTES["wind"]
    return ""  # solar is the PLAYBOOK/checklist default

PACKET = """Identity packet (this is ALL the queue data you get; the reported COD is a CLAIM \
to verify, never evidence):
- Project: {project}
- INR: {inr}
- Likely SPV/LLC name: {project}, LLC (verify)
- County: {county}, Texas
- Capacity: {mw} MW
- Fuel/technology: {fueltech}
- POI description: "{poi}"
- CDR zone: {zone}
- Reported COD (claim): {cod}

Your assigned project directory (already created): gis-research/research/{dirname}/
Write ONLY inside it. Do NOT read gis-research/data/ or gis-research/output/.
Satellite/maps tools load creds from ~/.config/gis-research.env themselves; run them with
`uv run` from the repo root.
{fuel_notes}"""

TRIAGE_PROMPT = """You are running a TRIAGE pass on one ERCOT interconnection-queue project. \
This is a budgeted first look, NOT deep research. Follow {checklist_path} \
(T1–T5). The factsheet is your starting state — contest it, don't rebuild it. Verdict enum: \
paper_dismissed | deep_candidate | ambiguous. The runner enforces a hard token budget: you \
get a warning at 80%, a wrap-up order at 100%, and ~10k grace tokens after that before the \
session is killed — if you overspend early steps, T5 (your output) gets squeezed or lost.

{packet}

THE CHECKLIST (your complete and only instructions):

{checklist}

Begin with T1 now. When T5 is written, reply with the triage.md summary (verdict, the \
factors you confirmed/contested, citations) and stop."""

DEEP_PROMPT = """You are a project research agent. Research ONE ERCOT interconnection-queue \
project and decide: is it real or paper, and what is a defensible independent COD estimate.

{packet}

Follow {playbook_path} EXACTLY — stages D0–D5 in order, all hard rules \
(banned sources, artifacts-or-didn't-happen, write-as-you-go, log negative evidence, no county \
centroids, search-tight-present-wide, ≤6 full-size frame reads). The dossier must follow \
{dossier_template_path} exactly; reference example \
{hanson_example_path}.

Stage D0 writes the findings.json skeleton FIRST; every stage ends by updating findings.json \
— a checkpoint hook will interrupt you if you drift past 25 tool calls without persisting.

A triage pass may already exist in your project dir (triage_findings.json / triage.md) — \
read it first and chase its deep_scan_focus threads before anything else.

Findings.json schema: docs/superpowers/specs/2026-07-17-project-research-agent-design.md §5, \
plus: `project_area` {{acres, source, artifact}} (from abatement/IA/CAD docs — reviewer \
sanity-checks the imagery footprint with it); `site.map_artifacts` [paths] — the extracted \
parcel/boundary-map page images (PLAYBOOK rule 4b) the site fix rests on; and \
`contractual_schedule` if you obtain the signed IA (see the Hanson example) with a \
`documents` list — one entry per IA document {{doc, signed, financial_security, artifact}}; \
security amounts often rise with amendments, record them per document.

{budget_line}

When done, run the deterministic wrap-up commands from PLAYBOOK.md stage D5, then reply \
with a 10-line summary: verdict, site lat/lon + method, construction stage, independent COD, \
drift risk, and your 3 most decisive artifacts."""


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def identity_packet(inr: str) -> dict:
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    row = latest[latest.INR == inr]
    if row.empty:
        raise SystemExit(f"{inr} not in latest snapshot ({df.fileDate.max().date()})")
    r = row.iloc[0]
    fueltech = FUEL_LABEL.get((r.fuel, r.technology), f"{r.fuel}/{r.technology}")
    return dict(project=r.projectName, inr=inr, county=r.county, mw=r.capacityMw,
                fueltech=fueltech, poi=r.poiLocation, zone=r.cdrReportingZone,
                cod=str(r.projectCod)[:10], dirname=f"{inr}_{slugify(r.projectName)}",
                fuel_notes=fuel_notes(r.fuel, r.technology))


def validate(stream_path: Path, mode: str, proj_dir: Path) -> dict:
    """Post-run budget audit from the stream log. Violations are report-only."""
    turns = 0
    image_reads = 0
    tool_counts: dict[str, int] = {}
    seen_msg_ids: set[str] = set()
    for line in stream_path.read_text().splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") != "assistant":
            continue
        # The CLI streams one JSONL line PER CONTENT BLOCK (thinking/text/tool_use), all
        # sharing one message.id and the SAME cumulative usage snapshot for that logical
        # turn — count each distinct message.id once, or turns/fresh_tokens balloon by the
        # blocks-per-turn factor (pilot 2026-07-20 evidence: a single ~32k-token turn with
        # 4 content blocks was counted as 128k). tool_counts/image_reads are unaffected
        # (each tool_use block appears on exactly one line) so they still iterate every line.
        msg_id = ev.get("message", {}).get("id")
        if not msg_id or msg_id not in seen_msg_ids:
            if msg_id:
                seen_msg_ids.add(msg_id)
            turns += 1
        for b in ev.get("message", {}).get("content", []):
            if b.get("type") == "tool_use":
                tool_counts[b["name"]] = tool_counts.get(b["name"], 0) + 1
                if b["name"] == "Read" and str(b.get("input", {}).get("file_path", "")).endswith(".png"):
                    image_reads += 1

    violations = []
    if image_reads > MAX_FULLSIZE_IMAGE_READS[mode]:
        violations.append(f"image_reads {image_reads} > {MAX_FULLSIZE_IMAGE_READS[mode]}")
    if mode == "triage":
        tf = proj_dir / "triage_findings.json"
        if not tf.exists():
            violations.append("triage_findings.json missing")
        else:
            try:
                d = json.loads(tf.read_text())
                sa = d.get("score_adjustment")
                v2_ok = d.get("verdict") in VERDICT_ENUM and (
                    sa is None or {"delta", "citation"} <= set(sa))
                v1_ok = isinstance(d.get("deep_scan_recommended"), bool)
                if not (v2_ok or v1_ok):
                    violations.append(
                        "triage_findings.json matches neither v2 schema (verdict in "
                        f"{sorted(VERDICT_ENUM)} + valid score_adjustment) nor v1 "
                        "(deep_scan_recommended bool)")
            except json.JSONDecodeError:
                violations.append("triage_findings.json invalid JSON")
    else:
        for f in ("findings.json", "dossier.md", "log.md"):
            if not (proj_dir / f).exists():
                violations.append(f"{f} missing")
    return {"assistant_turns": turns, "image_reads": image_reads,
            "tool_counts": tool_counts, "violations": violations}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inr")
    ap.add_argument("--mode", choices=("triage", "deep"), default="triage")
    ap.add_argument("--model", default=None, help="override the mode's default model")
    ap.add_argument("--profile", default="read_only")
    ap.add_argument("--region", default="us-east-1")
    ap.add_argument("--max-turns", type=int, default=None)
    ap.add_argument("--token-budget", type=int, default=None,
                    help="fresh-token kill switch (default: mode's TOKEN_BUDGET)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print assembled prompt, don't spawn")
    a = ap.parse_args()

    model = a.model or (TRIAGE_MODEL if a.mode == "triage" else DEEP_MODEL)
    max_turns = a.max_turns or (TRIAGE_MAX_TURNS if a.mode == "triage" else DEEP_MAX_TURNS)
    budget = a.token_budget if a.token_budget is not None else TOKEN_BUDGET[a.mode]

    pkt = identity_packet(a.inr)
    proj_dir = BASE / "research" / pkt["dirname"]
    if not a.dry_run:
        for sub in ("sources", "imagery"):
            (proj_dir / sub).mkdir(parents=True, exist_ok=True)

    packet = PACKET.format(**pkt)
    # Absolute paths (not relative-looking ones) — a relative path here caused the agent to
    # guess the wrong repo root and burn ~10 Glob/find tool calls hunting for the file before
    # every deep run (pilot 2026-07-20 evidence, both deep pilots identically).
    checklist_path = (BASE / "research" / "TRIAGE_CHECKLIST.md").resolve()
    playbook_path = (BASE / "research" / "PLAYBOOK.md").resolve()
    dossier_template_path = (BASE / "research" / "DOSSIER_TEMPLATE.md").resolve()
    hanson_example_path = (BASE / "research" / "23INR0086_hanson-solar" / "dossier.md").resolve()
    if a.mode == "triage":
        factsheet_path = proj_dir / "factsheet.md"
        if factsheet_path.exists():
            packet += ("\n\n== FACTSHEET (deterministic, trust but verify) ==\n"
                       + factsheet_path.read_text())
        checklist = checklist_path.read_text()
        prompt = TRIAGE_PROMPT.format(packet=packet, checklist=checklist,
                                       checklist_path=checklist_path)
    else:
        wrap_at = int(max_turns * 0.8)
        turn_line = (f"- TURNS: ~{max_turns} turn hard cap; at ~{wrap_at} turns, STOP "
                     "researching and synthesize what you have.")
        if budget:
            budget_line = (
                "Two hard limits the runner enforces — hit either and you are cut off "
                f"mid-thought:\n{turn_line}\n"
                f"- TOKENS: ~{budget:,} fresh-token budget. You get a WARNING at 80% and a "
                "WRAP-UP ORDER at 100%, then ~10k grace tokens before the session is killed.\n"
                "When you see the 80% warning, finish the current thread fast and make sure "
                "findings.json + dossier.md + log.md are written — unwritten findings are lost, "
                "and a partial dossier beats a truncated one.")
        else:
            budget_line = (f"Budget: {turn_line[2:]} A partial dossier beats a truncated one.")
        prompt = DEEP_PROMPT.format(packet=packet, budget_line=budget_line,
                                     playbook_path=playbook_path,
                                     dossier_template_path=dossier_template_path,
                                     hanson_example_path=hanson_example_path)

    if a.dry_run:
        print(prompt)
        return

    stream_path = proj_dir / f"run_stream_{a.mode}.jsonl"

    env = os.environ.copy()
    env.update({
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "AWS_PROFILE": a.profile,
        "AWS_REGION": a.region,
        "ANTHROPIC_MODEL": model,
        "ANTHROPIC_SMALL_FAST_MODEL": SMALL_MODEL,
    })

    cmd = ["claude", "-p", prompt,
           "--model", model,
           "--allowedTools", ALLOWED_TOOLS,
           "--disallowedTools", DISALLOWED_TOOLS,
           "--output-format", "stream-json", "--verbose",
           "--max-turns", str(max_turns)]

    # budget plumbing: runner keeps .budget_state.json current; a PostToolUse hook
    # (budget_hook.py) reads it and feeds the 80% warning / 100% wrap-up order into the
    # agent's conversation. Markers make each message fire exactly once per run.
    state_f = proj_dir / ".budget_state.json"
    for stale in (".budget_warn_sent", ".budget_exhaust_sent"):
        (proj_dir / stale).unlink(missing_ok=True)
    state_f.write_text(json.dumps({"spent": 0, "budget": budget}))
    hook_py = Path(__file__).with_name("budget_hook.py")
    blocklist_py = Path(__file__).with_name("blocklist_hook.py")
    settings_f = proj_dir / ".budget_settings.json"
    settings_f.write_text(json.dumps({"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [
        {"type": "command", "command": f"python3 {hook_py} {proj_dir}"}]}],
        "PreToolUse": [{"matcher": "WebFetch|Bash", "hooks": [
            {"type": "command", "command": f"python3 {blocklist_py}"}]}]}}))
    cmd += ["--settings", str(settings_f)]

    print(f"mode:        {a.mode}")
    print(f"project dir: {proj_dir}")
    print(f"stream log:  {stream_path}")
    grace_note = f" (+{GRACE_TOKENS} grace)" if budget else ""
    print(f"model:       {model}  max_turns: {max_turns}  token_budget: {budget}{grace_note}")

    # Stream-parse as the agent runs: accumulate fresh tokens (input + cache_creation +
    # output; cache reads excluded), publish to the hook, hard-kill at budget + grace.
    # NOTE: the CLI streams one JSONL line PER CONTENT BLOCK of a turn (thinking/text/
    # tool_use), all sharing one message.id and the same cumulative usage snapshot — sum
    # each distinct message.id's usage ONCE, or a single turn's real spend gets multiplied
    # by however many content blocks it had (pilot 2026-07-20: a real ~32k-token/$0.12 turn
    # was counted as 128k+ and falsely killed the run). Every line is still logged/scanned
    # below; only the usage-sum is deduplicated.
    spent = 0
    budget_killed = False
    seen_msg_ids: set[str] = set()
    proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    with stream_path.open("w") as log:
        for line in proc.stdout:
            log.write(line)
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") != "assistant":
                continue
            msg_id = ev.get("message", {}).get("id")
            if msg_id and msg_id in seen_msg_ids:
                continue  # same logical turn as an earlier content-block line — already summed
            if msg_id:
                seen_msg_ids.add(msg_id)
            u = ev.get("message", {}).get("usage") or {}
            spent += (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                      + u.get("output_tokens", 0))
            if budget:
                tmp = state_f.with_suffix(".tmp")
                tmp.write_text(json.dumps({"spent": spent, "budget": budget}))
                tmp.replace(state_f)  # atomic — the hook may be reading concurrently
                if spent > budget + GRACE_TOKENS and not budget_killed:
                    budget_killed = True
                    print(f"TOKEN BUDGET + GRACE EXCEEDED ({spent:,} > "
                          f"{budget + GRACE_TOKENS:,}) — killing session")
                    proc.terminate()
    rc = proc.wait()

    meta = {"mode": a.mode, "model": model}
    for line in reversed(stream_path.read_text().splitlines()):
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            meta.update({k: ev.get(k) for k in
                         ("subtype", "is_error", "duration_ms", "num_turns",
                          "total_cost_usd", "usage", "session_id")})
            break
    meta["audit"] = validate(stream_path, a.mode, proj_dir)
    meta["fresh_tokens"] = spent
    meta["token_budget"] = budget
    if budget_killed:
        meta["audit"]["violations"].append(f"token budget exceeded: {spent} > {budget} (killed)")

    # max-turns with the required artifacts on disk = usable run, not a failure —
    # otherwise `triage && deep` chains and run_batch.py misread it as "no output"
    required = ["triage_findings.json"] if a.mode == "triage" else ["findings.json", "dossier.md"]
    if rc != 0 and meta.get("subtype") == "error_max_turns" \
            and all((proj_dir / f).exists() for f in required):
        print("max-turns hit but required artifacts present — exit 0")
        rc = 0
    meta["exit_code"] = rc
    (proj_dir / f"run_meta_{a.mode}.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))
    sys.exit(rc)


if __name__ == "__main__":
    main()
