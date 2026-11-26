"""CLI: historical realized congestion for a monitored element (any contingency).

Usage:
    uv run powerflow_analytics/scripts/constraint_history.py --monitored SARDIS%
    uv run powerflow_analytics/scripts/constraint_history.py --monitored '%SARDIS%' \
        --start 2023-01-01 --contingency '%N58%'
"""
from __future__ import annotations

import argparse


import pandas as pd

from pfa.extract.cong_history import lookup_constraint_history


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--monitored", required=True, help="ILIKE pattern, e.g. '%SARDIS%'")
    ap.add_argument("--contingency", default=None, help="optional ILIKE pattern on CONGCONTNAME")
    ap.add_argument("--start", default=None)
    ap.add_argument("--end", default=None)
    ap.add_argument("--price-type", type=int, default=1, help="1=DA, 2=RT")
    args = ap.parse_args()

    df = lookup_constraint_history(
        args.monitored, contingency_like=args.contingency,
        start=args.start, end=args.end, price_type=args.price_type,
    )
    pd.set_option("display.width", 160)
    if df.empty:
        print(f"no realized-congestion rows found for monitored ILIKE {args.monitored!r}")
        return
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
