#!/usr/bin/env python3
# gis-research/scripts/research_tools/blocklist_hook.py
"""PreToolUse hook: block domains proven 100%-dead or replaced by local tools.

Log forensics 2026-07-19: 3,012 WebFetches to the PUCT portal (100% HTTP 402),
1,196 to SEC EDGAR (100% fail), 7,260 search-engine scrapes. Exit 2 blocks the
call; stderr names the replacement so the agent course-corrects in one turn.
Stdlib only — runs on bare python3.
"""
import json
import sys

BLOCKED = [
    ("interchange.puc.texas.gov",
     "BLOCKED: the PUCT portal rate-limits ad-hoc fetches (HTTP 402, 100% fail rate). "
     "Use `uv run gis-research/scripts/research_tools/puct.py match <INR> --dir <sources/>` "
     "(or puct.py search/filings/fetch)."),
    ("sec.gov",
     "BLOCKED: SEC full-text fetches failed 100% in prior runs. Entity leads come from "
     "`spv.py resolve <INR>` and the registry resolvers (ch313/faa/tceq)."),
    ("duckduckgo.com",
     "BLOCKED: do not scrape search engines. Use "
     "`uv run gis-research/scripts/research_tools/search.py \"<query>\"`."),
    ("bing.com/search",
     "BLOCKED: do not scrape search engines. Use search.py."),
    ("search.yahoo.com",
     "BLOCKED: do not scrape search engines. Use search.py."),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    haystack = ti.get("url", "") if tool == "WebFetch" else \
        ti.get("command", "") if tool == "Bash" else ""
    if not haystack:
        return 0
    if tool == "Bash" and not any(t in haystack for t in ("curl ", "wget ", "http")):
        return 0
    for dom, msg in BLOCKED:
        if dom in haystack:
            print(msg, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
