"""Shim: the implementation is pfa.cli.history (`uv run pfa history`)."""
from pfa.cli.history import main

if __name__ == "__main__":
    raise SystemExit(main())
