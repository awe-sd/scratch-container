"""Shim: the implementation is pfa.cli.value_constraint (`uv run pfa value`)."""
from pfa.cli.value_constraint import main

if __name__ == "__main__":
    raise SystemExit(main())
