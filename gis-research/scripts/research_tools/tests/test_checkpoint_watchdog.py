import json, subprocess, sys
from pathlib import Path
HOOK = Path(__file__).parents[1] / "budget_hook.py"


def run_hook(tmp, payload):
    return subprocess.run([sys.executable, str(HOOK), str(tmp)],
                          input=json.dumps(payload), capture_output=True, text=True)


def test_warns_after_25_calls_without_checkpoint(tmp_path):
    fetch = {"tool_name": "WebFetch", "tool_input": {"url": "https://x.example"}}
    for _ in range(25):
        r = run_hook(tmp_path, fetch)
        assert r.returncode == 0
    r = run_hook(tmp_path, fetch)   # 26th
    assert r.returncode == 2 and "findings.json" in r.stderr


def test_findings_write_resets_counter(tmp_path):
    fetch = {"tool_name": "WebFetch", "tool_input": {"url": "https://x.example"}}
    for _ in range(20):
        run_hook(tmp_path, fetch)
    run_hook(tmp_path, {"tool_name": "Write",
                        "tool_input": {"file_path": "/p/findings.json", "content": "{}"}})
    for _ in range(25):
        assert run_hook(tmp_path, fetch).returncode == 0


def test_budget_logic_unbroken_without_stdin(tmp_path):
    (tmp_path / ".budget_state.json").write_text(json.dumps({"spent": 90, "budget": 100}))
    r = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                       input="", capture_output=True, text=True)
    assert r.returncode == 2 and "BUDGET WARNING" in r.stderr
