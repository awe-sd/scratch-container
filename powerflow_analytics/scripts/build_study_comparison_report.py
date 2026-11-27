"""Shim: the implementation is pfa.cli.compare (`uv run pfa compare`)."""
from pfa.cli.compare import main

if __name__ == "__main__":
    raise SystemExit(main())
