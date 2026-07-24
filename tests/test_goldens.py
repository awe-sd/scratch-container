import hashlib
import json
import subprocess


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_dbfree_rerun_reproduces_goldens(repo_root):
    golden = json.loads((repo_root / "tests/goldens/hashes.json").read_text())
    for script in [
        "branch_tracking/scripts/map_unmapped_dampsse_teids.py",
        "branch_tracking/scripts/build_final_branch_table.py",
    ]:
        r = subprocess.run(
            ["uv", "run", script], cwd=repo_root, capture_output=True, text=True
        )
        assert r.returncode == 0, r.stderr[-2000:]
    for rel, expected in golden.items():
        assert _sha(repo_root / rel) == expected, f"{rel} changed vs golden"
