"""Shim: the implementation is pfa.cli.deep_dive (`uv run pfa deep-dive`)."""
from pfa.cli.deep_dive import main

if __name__ == "__main__":
    raise SystemExit(main())
