"""Shim: the implementation is pfa.cli.lambda_dist (`uv run pfa lambda-dist`)."""
from pfa.cli.lambda_dist import main

if __name__ == "__main__":
    raise SystemExit(main())
