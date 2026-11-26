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


def test_budget_exhaust_fires_once(tmp_path):
    (tmp_path / ".budget_state.json").write_text(json.dumps({"spent": 120, "budget": 100}))
    r1 = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                        input="", capture_output=True, text=True)
    assert r1.returncode == 2 and "BUDGET EXHAUSTED" in r1.stderr
    r2 = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                        input="", capture_output=True, text=True)
    assert r2.returncode == 0


def test_budget_warn_fires_once(tmp_path):
    (tmp_path / ".budget_state.json").write_text(json.dumps({"spent": 90, "budget": 100}))
    r1 = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                        input="", capture_output=True, text=True)
    assert r1.returncode == 2 and "BUDGET WARNING" in r1.stderr
    r2 = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                        input="", capture_output=True, text=True)
    assert r2.returncode == 0


def test_non_dict_stdin_payload_does_not_crash(tmp_path):
    # PostToolUse stdin is expected to be a JSON object; guard against valid-JSON-but-
    # not-a-dict payloads (a bare list or number) so payload.get(...) never AttributeErrors.
    r = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                       input="[1, 2, 3]", capture_output=True, text=True)
    assert r.returncode == 0 and r.stderr == ""

    r2 = subprocess.run([sys.executable, str(HOOK), str(tmp_path)],
                        input="42", capture_output=True, text=True)
    assert r2.returncode == 0 and r2.stderr == ""


def test_corrupted_budget_state_falls_through_to_watchdog(tmp_path):
    (tmp_path / ".budget_state.json").write_text("not json")
    fetch = {"tool_name": "WebFetch", "tool_input": {"url": "https://x.example"}}
    seen_stderr = []
    for _ in range(25):
        r = run_hook(tmp_path, fetch)
        assert r.returncode == 0
        seen_stderr.append(r.stderr)
    r = run_hook(tmp_path, fetch)   # 26th
    assert r.returncode == 2 and "CHECKPOINT" in r.stderr
    seen_stderr.append(r.stderr)
    assert all("BUDGET" not in s for s in seen_stderr)
