"""Shim: the implementation is pfa.cli.offers (`uv run pfa offers`)."""
from pfa.cli.offers import main

if __name__ == "__main__":
    raise SystemExit(main())
