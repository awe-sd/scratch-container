"""Web search for research agents — one tool, three backends, cached + throttled.

Research agents run on Bedrock, where Claude Code's WebSearch server tool is
unavailable; historically they scraped DuckDuckGo/Bing HTML 7,260 times. This tool
gives them ONE search entrypoint:

  backend 1  AgentCore Gateway (AWS-managed web search over MCP, $7/1k) — used
             automatically when AGENTCORE_GATEWAY_URL is set in the env
             (~/.config/gis-research.env). PREFERRED once admin approves the gateway.
  backend 2  OAuth bridge (TEMPORARY until the gateway exists): spawns a headless
             `claude -p` on the container's Anthropic OAuth seat (Bedrock env vars
             stripped) with only the WebSearch tool, Haiku model. Consumes the seat's
             rate window — hence the cache and the hourly cap below.
  backend 3  DuckDuckGo HTML scrape — last resort (--ddg or when 1 and 2 fail).

Safety rails (all backends): on-disk result cache keyed by normalized query
(data/reference/search_cache/, TTL 7 days, --fresh to bypass) so parallel agents
never re-buy a query; cross-process 3s flock throttle; 120-queries/hour fleet-wide
cap (exceeding prints a budget message and exits 2 — treat as negative evidence and
move on, do NOT retry-loop).

Agent usage (run from repo root with `uv run`):
  search.py "Hanson Solar Coleman County construction"
  search.py "Red Egret BESS Clearway" --n 8
  search.py --selftest

Output: numbered plain lines (TITLE / URL / snippet) + a provenance line naming the
backend and cache status. A no-result search prints an explicit negative line.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]  # gis-research/
CACHE_DIR = BASE / "data" / "reference" / "search_cache"
ENV_FILE = Path.home() / ".config" / "gis-research.env"
THROTTLE = Path(tempfile.gettempdir()) / ".search_throttle.json"
MIN_INTERVAL = 3.0
MAX_PER_HOUR = 120
CACHE_TTL = 7 * 86400
CLAUDE_TIMEOUT = 500  # first probe took ~3min wall (headless startup + search)
# queue aggregators are BANNED sources (citing one = automatic fail) — suppress at
# the tool layer so agents never see them
BANNED = ("interconnection.fyi", "cleanview.co", "gridinfo.com", "energyacuity",
          "infrasure.ai", "futuregrid.io")


def load_env_file() -> None:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _throttle_and_budget() -> None:
    """3s min interval + 120/h fleet-wide cap, shared across processes via flock."""
    THROTTLE.touch(exist_ok=True)
    with THROTTLE.open("r+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            d = json.loads(fh.read() or "{}")
        except ValueError:
            d = {}
        now = time.time()
        stamps = [t for t in d.get("stamps", []) if now - t < 3600]
        if len(stamps) >= MAX_PER_HOUR:
            print(f"SEARCH BUDGET EXHAUSTED: {MAX_PER_HOUR} queries in the last hour "
                  "(fleet-wide cap). Record as negative evidence and continue without "
                  "this search — do NOT retry in a loop.")
            sys.exit(2)
        # once the sliding hour window is already more than half full, back off to a
        # 30s interval -- prevents a burst of ~7 concurrent agents from exhausting the
        # fleet hour-cap in minutes instead of spreading it across the hour
        min_interval = 30.0 if len(stamps) > MAX_PER_HOUR / 2 else MIN_INTERVAL
        wait = (stamps[-1] + min_interval - now) if stamps else 0
        if wait > 0:
            time.sleep(wait)
        stamps.append(time.time())
        fh.seek(0), fh.truncate(), fh.write(json.dumps({"stamps": stamps}))


def _norm(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())


def cache_path(q: str) -> Path:
    return CACHE_DIR / (hashlib.sha1(_norm(q).encode()).hexdigest()[:16] + ".json")


def cache_get(q: str, fresh: bool):
    p = cache_path(q)
    if fresh or not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except ValueError:
        return None
    if time.time() - d.get("ts", 0) > CACHE_TTL:
        return None
    return d


def cache_put(q: str, backend: str, results: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(q).write_text(json.dumps(
        {"query": q, "backend": backend, "ts": time.time(), "results": results}))


# ---- backend 1: AgentCore Gateway (MCP over SigV4) -------------------------
def search_agentcore(q: str, n: int) -> list[dict] | None:
    url = os.environ.get("AGENTCORE_GATEWAY_URL")
    if not url:
        return None
    try:
        import boto3
        import requests as rq
        from botocore.auth import SigV4Auth
        from botocore.awsrequest import AWSRequest
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": "WebSearch",
                                      "arguments": {"query": q, "maxResults": n}}})
        req = AWSRequest(method="POST", url=url, data=body,
                         headers={"Content-Type": "application/json",
                                  "Accept": "application/json, text/event-stream"})
        creds = boto3.Session().get_credentials()
        SigV4Auth(creds, "bedrock-agentcore", "us-east-1").add_auth(req)
        r = rq.post(url, data=body, headers=dict(req.headers), timeout=60)
        r.raise_for_status()
        payload = r.json() if r.headers.get("content-type", "").startswith("application/json") \
            else json.loads(re.search(r"data: (\{.*\})", r.text).group(1))
        content = payload.get("result", {}).get("content", [])
        out = []
        for c in content:
            if c.get("type") == "text":
                try:
                    for item in json.loads(c["text"]).get("results", []):
                        out.append({"title": item.get("title", ""),
                                    "url": item.get("url", ""),
                                    "snippet": item.get("snippet", "")[:200]})
                except (ValueError, AttributeError):
                    out.append({"title": "", "url": "", "snippet": c["text"][:400]})
        return out[:n] if out else None
    except Exception as e:
        print(f"  [agentcore backend failed: {e.__class__.__name__} — falling back]",
              file=sys.stderr)
        return None


# ---- backend 2: OAuth bridge (temporary) -----------------------------------
def search_oauth(q: str, n: int) -> list[dict] | None:
    env = os.environ.copy()
    for k in ("CLAUDE_CODE_USE_BEDROCK", "ANTHROPIC_MODEL",
              "ANTHROPIC_SMALL_FAST_MODEL", "AWS_PROFILE", "AWS_REGION"):
        env.pop(k, None)
    prompt = (f"Use WebSearch once for: {q}\nOutput ONLY the top {n} results, one per "
              "line, exactly this format:\nTITLE | URL | one-line snippet\n"
              "No preamble, no numbering, no other text. If no results: NO_RESULTS")
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", "haiku",
             "--allowedTools", "WebSearch", "--max-turns", "4"],
            capture_output=True, text=True, timeout=CLAUDE_TIMEOUT, env=env,
            cwd=tempfile.gettempdir())  # neutral cwd: no project context to load
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  [oauth backend failed: {e.__class__.__name__} — falling back]",
              file=sys.stderr)
        return None
    out = []
    for line in r.stdout.splitlines():
        if line.strip() == "NO_RESULTS":
            return []
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 2 and parts[1].startswith("http"):
            out.append({"title": parts[0], "url": parts[1],
                        "snippet": parts[2][:200] if len(parts) > 2 else ""})
    return out[:n] or None


# ---- backend 3: DDG HTML (last resort) --------------------------------------
def search_ddg(q: str, n: int) -> list[dict] | None:
    import requests as rq
    from urllib.parse import unquote, urlencode
    try:
        r = rq.get("https://html.duckduckgo.com/html/?" + urlencode({"q": q}),
                   headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"  [ddg backend failed: {e.__class__.__name__}]", file=sys.stderr)
        return None
    out = []
    for m in re.finditer(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text):
        url, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        uddg = re.search(r"uddg=([^&]+)", url)
        if uddg:
            url = unquote(uddg.group(1))
        out.append({"title": title.strip(), "url": url, "snippet": ""})
        if len(out) >= n:
            break
    return out or None


def run(q: str, n: int, fresh: bool, force_ddg: bool) -> int:
    load_env_file()
    hit = cache_get(q, fresh)
    if hit:
        _print(q, hit["results"], hit["backend"], cached=True, n=n)
        return 0
    _throttle_and_budget()
    order = [("ddg", search_ddg)] if force_ddg else \
        [("agentcore", search_agentcore), ("oauth", search_oauth), ("ddg", search_ddg)]
    for backend, fn in order:
        res = fn(q, n + 5)  # headroom: banned queue-trackers are filtered at print time
        if res is not None:
            cache_put(q, backend, res)
            _print(q, res, backend, cached=False, n=n)
            return 0
    print(f"SEARCH FAILED on all backends for: {q} — record as negative evidence.")
    return 1


def _print(q: str, results: list[dict], backend: str, cached: bool, n: int = 5) -> None:
    kept = [r for r in results if not any(b in r.get("url", "") for b in BANNED)]
    dropped = len(results) - len(kept)
    results = kept[:n]
    print(f"provenance: search backend={backend} cached={'yes' if cached else 'no'} "
          f"query={q!r}"
          + (f" ({dropped} banned queue-tracker result(s) suppressed)" if dropped else ""))
    if not results:
        if dropped:
            print(f"NO USABLE RESULTS — all {dropped} hits were banned queue-tracker "
                  "sites. The project likely EXISTS in aggregators (weak existence "
                  "signal, do not cite); refine the query toward primary sources "
                  "(news, developer, county).")
        else:
            print("NO RESULTS — explicit negative: nothing indexed for this query.")
        return
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        if r.get("snippet"):
            print(f"   {r['snippet']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--fresh", action="store_true", help="bypass the 7-day cache")
    ap.add_argument("--ddg", action="store_true", help="force the DDG fallback backend")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(run("ERCOT interconnection queue", 3, True, False))
    if not a.query:
        raise SystemExit("usage: search.py \"<query>\" [--n N] [--fresh] [--ddg]")
    sys.exit(run(a.query, a.n, a.fresh, a.ddg))


if __name__ == "__main__":
    main()
