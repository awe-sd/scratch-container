"""Shim: the implementation is pfa.cli.summary (`uv run pfa summary`)."""
from pfa.cli.summary import main

if __name__ == "__main__":
    raise SystemExit(main())
