"""Shim: the implementation is pfa.cli.paths (`uv run pfa paths`)."""
from pfa.cli.paths import main

if __name__ == "__main__":
    raise SystemExit(main())
