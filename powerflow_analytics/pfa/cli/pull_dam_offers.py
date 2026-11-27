"""Pull ERCOT DAM gen-resource energy offer curves.

Usage:
  uv run pfa offers \
      --resource FRNYPP% --start 2026-05-01 --end 2026-07-01 [--summary]
"""
from __future__ import annotations

import argparse
from datetime import date


from pfa import config
from pfa.extract import dam_offers

LARGE_ROWS = 500


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--resource",
        required=True,
        help="ILIKE pattern matched against RESOURCENAME in ERCOT60DDAMGEN, e.g. FRNYPP%%",
    )
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD (exclusive)")
    ap.add_argument("--summary", action="store_true", help="print monthly summary instead of raw curves")
    args = ap.parse_args(argv)

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)

    if args.summary:
        df = dam_offers.summarize_offers(args.resource, start, end)
        label = "summary"
    else:
        df = dam_offers.get_offer_curves(args.resource, start, end)
        label = "curves"

    if df.empty:
        print(f"no offer rows found for resource_like={args.resource!r} in [{start}, {end})")
        return

    print(f"{label}: {len(df):,} rows for resource_like={args.resource!r} [{start}, {end})")
    print(df.to_string(index=False))

    if len(df) > LARGE_ROWS:
        config.OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        out_path = config.OUTPUT_ROOT / f"dam_offers_{label}_{args.resource.strip('%')}.csv"
        df.to_csv(out_path, index=False)
        print(f"\nwrote full result to {out_path}")

