#!/usr/bin/env python3
"""PostToolUse hook — mid-run budget messages for headless research agents.

The runner (run_agent.py) streams the session and keeps <proj_dir>/.budget_state.json
current. This hook fires after every tool call: at >=80% of the fresh-token budget it
warns the agent once; at >=100% it orders an immediate wrap-up once. Exit code 2 feeds
stderr back into the agent's conversation. The runner does the actual kill at
budget + grace. Stdlib only — runs bare python3 to keep per-tool-call overhead tiny.
"""

import json
import sys
from pathlib import Path


def main() -> int:
    d = Path(sys.argv[1])
    state_f = d / ".budget_state.json"
    if not state_f.exists():
        return 0
    try:
        state = json.loads(state_f.read_text())
    except (json.JSONDecodeError, OSError):
        return 0
    spent, budget = state.get("spent", 0), state.get("budget")
    if not budget:
        return 0

    exhaust_marker = d / ".budget_exhaust_sent"
    warn_marker = d / ".budget_warn_sent"

    if spent >= budget and not exhaust_marker.exists():
        exhaust_marker.write_text(str(spent))
        print(f"BUDGET EXHAUSTED: {spent:,}/{budget:,} fresh tokens. STOP researching NOW. "
              "Write your output files immediately with what you already have "
              "(triage: triage_findings.json + triage.md; deep: findings.json + dossier.md "
              "+ log.md). You have roughly 10,000 grace tokens before the session is killed "
              "— files on disk are all that survives.", file=sys.stderr)
        return 2

    if spent >= 0.8 * budget and not warn_marker.exists():
        warn_marker.write_text(str(spent))
        print(f"BUDGET WARNING: {spent:,}/{budget:,} fresh tokens spent (>=80%). Wrap up: "
              "finish the current step fast, skip anything optional, and make sure your "
              "output files get written before the budget runs out.", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
