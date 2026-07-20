# gis-research/scripts/research_tools/tests/test_blocklist_hook.py
import json, subprocess, sys
from pathlib import Path
HOOK = Path(__file__).parents[1] / "blocklist_hook.py"


def run_hook(payload):
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True)


def test_blocks_puct_webfetch():
    r = run_hook({"tool_name": "WebFetch",
                  "tool_input": {"url": "https://interchange.puc.texas.gov/search"}})
    assert r.returncode == 2 and "puct.py" in r.stderr


def test_blocks_sec_and_search_scrape():
    assert run_hook({"tool_name": "WebFetch",
                     "tool_input": {"url": "https://efts.sec.gov/LATEST/search-index?q=x"}}).returncode == 2
    r = run_hook({"tool_name": "WebFetch",
                  "tool_input": {"url": "https://html.duckduckgo.com/html/?q=x"}})
    assert r.returncode == 2 and "search.py" in r.stderr


def test_blocks_curl_to_blocked_domain():
    r = run_hook({"tool_name": "Bash",
                  "tool_input": {"command": "curl -s https://interchange.puc.texas.gov/x"}})
    assert r.returncode == 2


def test_allows_normal_fetch_and_puct_tool():
    assert run_hook({"tool_name": "WebFetch",
                     "tool_input": {"url": "https://www.ercot.com/x"}}).returncode == 0
    assert run_hook({"tool_name": "Bash",
                     "tool_input": {"command": "uv run gis-research/scripts/research_tools/puct.py match 23INR0086"}}).returncode == 0
