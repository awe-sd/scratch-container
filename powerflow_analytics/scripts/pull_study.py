"""Pull one SCOPF study's setup + results from Snowflake into the local parquet cache.

Usage: uv run powerflow_analytics/scripts/pull_study.py --study 14411 [--refresh]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pfa.cache import StudyCache
from pfa.extract import gen_mapping, results, study


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--refresh", action="store_true", help="re-pull tables already cached")
    args = ap.parse_args()

    cache = StudyCache(args.study)
    study_df = study.fetch_study(args.study)
    cache.save("opfstudy", study_df)
    ptoid = int(study_df["PTOID"].iloc[0])
    print(f"study {args.study}: {study_df['STUDYNAME'].iloc[0]} (ptoid {ptoid})")

    pulls = {
        "opfrun": lambda: study.fetch_runs(args.study),
        "opfrunscenario": lambda: study.fetch_run_scenarios(args.study),
        "outctgviol2": lambda: results.fetch_ctgviol(args.study),
        "outbranch2": lambda: results.fetch_branch(args.study),
        "outinterface2": lambda: results.fetch_interface(args.study),
        "outgen2": lambda: results.fetch_gen(args.study),
        "outtofindermax2": lambda: results.fetch_tofinder(args.study),
        "outconstraint2": lambda: results.fetch_constraint(args.study),
        "outgenref": lambda: gen_mapping.fetch_genref(ptoid),
        "genunit": gen_mapping.fetch_genunit,
    }
    for table, fetch in pulls.items():
        if cache.has(table) and not args.refresh:
            print(f"  {table}: cached, skipping")
            continue
        t0 = time.time()
        df = fetch()
        p = cache.save(table, df)
        print(f"  {table}: {len(df):,} rows -> {p.name} ({time.time() - t0:.0f}s)")

    print(f"cache dir: {cache.dir}")


if __name__ == "__main__":
    main()
