"""The `pfa` command: one entry, sub-commands in funnel order; each sub-command module has `main(argv)`."""
from __future__ import annotations

import importlib
import sys

# (sub-command, module in pfa.cli, one-line description) in funnel order
COMMANDS = [
    ("summary", "build_report", "step 1: rank a study's binding constraints (CSVs in output/study_<id>/)"),
    ("shortlist", "build_stage2_list", "step 2: classify, gate and value the shortlist for a settlement month"),
    ("deep-dive", "constraint_deep_dive", "step 3: wind/solar thresholds, dispatch and price formation for constraints"),
    ("paths", "pathopt_scatter", "step 4: cheapest paths that are long all required constraints (PathOpt runs)"),
    ("value", "value_constraint", "fact sheet and on-peak monthly mark for one constraint"),
    ("compare", "build_study_comparison_report", "compare two studies' constraints (persisting vs new)"),
    ("lambda-dist", "lambda_distribution", "shadow-price distribution for one constraint from offers and fast-scan"),
    ("pull", "pull_study", "extract a study from Snowflake into the local cache"),
    ("history", "constraint_history", "realized ISO constraint history lookup"),
    ("offers", "pull_dam_offers", "pull DAM generator offers"),
    ("load-profile", "load_profile", "median ERCOT load profile figure"),
    ("headroom", "headroom", "fast-scan headroom scatter for one constraint (HTML)"),
]
_MODULES = {name: mod for name, mod, _ in COMMANDS}


def _usage() -> str:
    width = max(len(n) for n, _, _ in COMMANDS)
    lines = ["usage: pfa <command> [options]   (pfa <command> --help for a command's arguments)", "", "commands:"]
    lines += [f"  {n.ljust(width)}  {d}" for n, _, d in COMMANDS]
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(_usage())
        return 0
    name = argv[0]
    if name not in _MODULES:
        print(f"pfa: unknown command {name!r}\n\n{_usage()}", file=sys.stderr)
        return 2
    sys.argv[0] = f"pfa {name}"
    importlib.import_module(f"pfa.cli.{_MODULES[name]}").main(argv[1:])
    return 0
