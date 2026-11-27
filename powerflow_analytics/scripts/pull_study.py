"""Shim: the implementation is pfa.cli.pull_study (`uv run pfa pull`)."""
from pfa.cli.pull_study import main

if __name__ == "__main__":
    raise SystemExit(main())
