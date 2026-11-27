"""Shim: the implementation is pfa.cli.pull (`uv run pfa pull`)."""
from pfa.cli.pull import main

if __name__ == "__main__":
    raise SystemExit(main())
