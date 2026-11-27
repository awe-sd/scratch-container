"""Shim: the implementation is pfa.cli.build_stage2_list (`uv run pfa shortlist`)."""
from pfa.cli.build_stage2_list import main

if __name__ == "__main__":
    raise SystemExit(main())
