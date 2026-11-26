"""Quick per-constraint valuation summary.

Usage:
  uv run powerflow_analytics/scripts/value_constraint_quick.py \
      --study 14425 --from 9045 --to 9188 --ckt 1 --ctg DLYTCIS5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.analysis.constraint_valuation import value_constraint


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--from", dest="fromnum", type=int, required=True)
    ap.add_argument("--to", dest="tonum", type=int, required=True)
    ap.add_argument("--ckt", required=True)
    ap.add_argument("--ctg", required=True)
    args = ap.parse_args()

    result = value_constraint(args.study, args.fromnum, args.tonum, args.ckt, args.ctg)

    print(f"constraint {result['constraint']} (study {result['study_id']})")
    print(f"  binding cases: {result['n_binding_cases']} / {result['n_total_cases']} rows flagged "
          f"in OUTCTGVIOL2 ({result['n_total_study_runs']} total study runs)")
    print("  lambda ($/MWh) over binding runs:")
    for k, v in result["lambda_stats"].items():
        print(f"    {k}: {v}")
    print(f"  top marginal units ({len(result['marginal_units'])}):")
    for u in result["marginal_units"]:
        print(f"    {json.dumps(u, default=str)}")


if __name__ == "__main__":
    main()
