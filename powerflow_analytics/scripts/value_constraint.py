"""Shim: the implementation is pfa.cli.value (`uv run pfa value`)."""
from pfa.cli.value import main

if __name__ == "__main__":
    raise SystemExit(main())
