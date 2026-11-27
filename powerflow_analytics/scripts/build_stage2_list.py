"""Shim: the implementation is pfa.cli.shortlist (`uv run pfa shortlist`)."""
from pfa.cli.shortlist import main

if __name__ == "__main__":
    raise SystemExit(main())
