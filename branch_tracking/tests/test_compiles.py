import py_compile
from pathlib import Path


def test_every_script_compiles(repo_root):
    for p in sorted((repo_root / "branch_tracking").rglob("*.py")):
        py_compile.compile(str(p), doraise=True)
