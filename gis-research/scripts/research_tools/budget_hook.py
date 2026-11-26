#!/usr/bin/env python3
"""PostToolUse hook — mid-run budget messages + checkpoint watchdog for headless
research agents.

The runner (run_agent.py) streams the session and keeps <proj_dir>/.budget_state.json
current. This hook fires after every tool call: at >=80% of the fresh-token budget it
warns the agent once; at >=100% it orders an immediate wrap-up once. Exit code 2 feeds
stderr back into the agent's conversation. The runner does the actual kill at
budget + grace. Stdlib only — runs bare python3 to keep per-tool-call overhead tiny.

Budget checks run first and always win (their exit 2 short-circuits the watchdog below
in the same invocation). The checkpoint watchdog (pipeline v2) then reads the PostToolUse
stdin payload and warns when the agent has gone CHECKPOINT_EVERY tool calls without
writing findings.json/triage_findings.json — it tracks its own state in the sibling
<dir>/.checkpoint_state.json (never .budget_state.json, which the runner owns and could
race). The watchdog must work even in a directory with no budget state at all, so the
budget block below computes a msg/exit pair instead of returning early.
"""

import json
import sys
from pathlib import Path


def main() -> int:
    d = Path(sys.argv[1])
    state_f = d / ".budget_state.json"

    budget_msg = None
    budget_exit = 0

    if state_f.exists():
        try:
            state = json.loads(state_f.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}
        spent, budget = state.get("spent", 0), state.get("budget")
        if budget:
            exhaust_marker = d / ".budget_exhaust_sent"
            warn_marker = d / ".budget_warn_sent"

            if spent >= budget and not exhaust_marker.exists():
                exhaust_marker.write_text(str(spent))
                if not warn_marker.exists():
                    warn_marker.write_text(str(spent))
                budget_msg = (
                    f"BUDGET EXHAUSTED: {spent:,}/{budget:,} fresh tokens. STOP researching NOW. "
                    "Write your output files immediately with what you already have "
                    "(triage: triage_findings.json + triage.md; deep: findings.json + dossier.md "
                    "+ log.md). You have roughly 10,000 grace tokens before the session is killed "
                    "— files on disk are all that survives.")
                budget_exit = 2
            elif spent >= 0.8 * budget and not warn_marker.exists():
                warn_marker.write_text(str(spent))
                budget_msg = (
                    f"BUDGET WARNING: {spent:,}/{budget:,} fresh tokens spent (>=80%). Wrap up: "
                    "finish the current step fast, skip anything optional, and make sure your "
                    "output files get written before the budget runs out.")
                budget_exit = 2

    if budget_exit:
        print(budget_msg, file=sys.stderr)
        return budget_exit

    # --- checkpoint watchdog (pipeline v2): warn when the agent has gone
    # CHECKPOINT_EVERY tool calls without persisting findings ---------------------
    CHECKPOINT_EVERY = 25
    try:
        payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except (json.JSONDecodeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}  # valid JSON but not an object (e.g. a bare list/number) -- no tool_name/tool_input to read
    if payload:
        cp_f = d / ".checkpoint_state.json"
        try:
            cp = json.loads(cp_f.read_text()) if cp_f.exists() else {"since": 0}
        except (json.JSONDecodeError, OSError):
            cp = {"since": 0}
        fp = (payload.get("tool_input") or {}).get("file_path", "")
        if payload.get("tool_name") in ("Write", "Edit") and \
                fp.endswith(("findings.json", "triage_findings.json")):
            cp["since"] = 0
        else:
            cp["since"] = cp.get("since", 0) + 1
        cp_f.write_text(json.dumps(cp))
        if cp["since"] > CHECKPOINT_EVERY:
            cp["since"] = 0
            cp_f.write_text(json.dumps(cp))
            print(f"CHECKPOINT: {CHECKPOINT_EVERY}+ tool calls since findings.json was "
                  "last written. Update findings.json NOW with everything learned so far "
                  "(nulls are fine for unknowns) — work not on disk is lost if the run "
                  "is killed. Then continue.", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
