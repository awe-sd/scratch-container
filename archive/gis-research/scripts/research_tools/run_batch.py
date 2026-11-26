"""Batch runner — triage many queue projects via run_agent.py, few at a time.

Selects INRs from the latest parquet snapshot (active queue only: no cancel/inactive/
commercial-ops date) by COD window and optional fuel, then runs run_agent.py per INR
with a concurrency cap. Resumable: projects that already have triage_findings.json
(or findings.json for --mode deep) are skipped unless --force.

Writes a batch summary (per-project signals + cost + violations, totals) to
research/_batches/<name>/summary.{json,csv}.

Usage:
  uv run gis-research/scripts/research_tools/run_batch.py --name cod-2028H1 \
      --cod-from 2028-01-01 --cod-to 2028-06-01 --dry-run     # list selection only
  uv run gis-research/scripts/research_tools/run_batch.py --name cod-2028H1 \
      --cod-from 2028-01-01 --cod-to 2028-06-01 --concurrency 3
  uv run gis-research/scripts/research_tools/run_batch.py --name pilot --inrs 26INR0686,27INR0084
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
ROOT = BASE.parent
RUN_AGENT = Path(__file__).with_name("run_agent.py")

_print_lock = threading.Lock()


def say(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def select(a: argparse.Namespace) -> pd.DataFrame:
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()].copy()
    if a.inrs:
        sel = latest[latest.INR.isin([i.strip() for i in a.inrs.split(",")])]
    else:
        # active queue only
        for col in ("cancelDate", "inActiveDate", "approvedForCommercialOperation"):
            latest = latest[latest[col].isna()]
        latest["cod"] = pd.to_datetime(latest.projectCod, errors="coerce")
        sel = latest[(latest.cod >= a.cod_from) & (latest.cod < a.cod_to)]
        if a.fuel:
            sel = sel[sel.fuel.str.upper().str.startswith(a.fuel.upper())]
        if a.min_mw:
            sel = sel[sel.capacityMw >= a.min_mw]
    return sel.sort_values("capacityMw", ascending=False)


def done_marker(mode: str) -> str:
    return "triage_findings.json" if mode == "triage" else "findings.json"


def run_one(inr: str, mode: str, token_budget: int | None = None) -> dict:
    say(f"[{inr}] start ({mode})")
    cmd = ["uv", "run", str(RUN_AGENT), inr, "--mode", mode]
    if token_budget:
        cmd += ["--token-budget", str(token_budget)]
    rc = subprocess.run(
        cmd,
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    say(f"[{inr}] done rc={rc}")
    return {"inr": inr, "rc": rc}


def collect(inr: str, name: str, mode: str) -> dict:
    row = {"inr": inr, "project": name}
    hits = sorted((BASE / "research").glob(f"{inr}_*"))
    if not hits:
        row["status"] = "no_dir"
        return row
    d = hits[0]
    meta_f = d / f"run_meta_{mode}.json"
    if meta_f.exists():
        m = json.loads(meta_f.read_text())
        row.update(cost_usd=m.get("total_cost_usd"), turns=m.get("num_turns"),
                   violations="; ".join(m.get("audit", {}).get("violations", [])))
    tf = d / "triage_findings.json"
    if mode == "triage" and tf.exists():
        try:
            t = json.loads(tf.read_text())
            sig = t.get("signals", {})
            row.update(status="ok", deep_scan=t.get("deep_scan_recommended"),
                       ia=sig.get("ia_found"), abatement=sig.get("abatement_found"),
                       pins=sig.get("pins_found"), news=sig.get("news_found"),
                       construction=sig.get("construction_visible"),
                       cod_plausible=t.get("cod_first_look", {}).get("plausible"),
                       focus=" | ".join(t.get("deep_scan_focus", [])[:2]))
        except json.JSONDecodeError:
            row["status"] = "bad_json"
    elif mode == "deep" and (d / "findings.json").exists():
        f = json.loads((d / "findings.json").read_text())
        row.update(status="ok", verdict=f.get("real_project_verdict"),
                   construction=f.get("construction", {}).get("verdict"),
                   cod_independent=f.get("cod_assessment", {}).get("independent"))
    else:
        row["status"] = "no_findings"
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", required=True, help="batch name → research/_batches/<name>/")
    ap.add_argument("--mode", choices=("triage", "deep"), default="triage")
    ap.add_argument("--cod-from")
    ap.add_argument("--cod-to")
    ap.add_argument("--fuel", help="filter: fuel code prefix (SOL, OTH, GAS, WIN)")
    ap.add_argument("--min-mw", type=float, default=None)
    ap.add_argument("--inrs", help="explicit comma-separated INR list (overrides filters)")
    ap.add_argument("--inrs-file", help="file with one INR per line (e.g. a batch's deep_queue.txt)")
    ap.add_argument("--concurrency", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None, help="cap batch size (largest-MW first)")
    ap.add_argument("--token-budget", type=int, default=None,
                    help="forward a per-run fresh-token budget to run_agent.py (re-run policy: 1000000 for user-ordered runs)")
    ap.add_argument("--force", action="store_true", help="re-run even if findings exist")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.inrs_file:
        listed = [ln.split()[0] for ln in Path(a.inrs_file).read_text().splitlines()
                  if ln.strip() and not ln.startswith("#")]
        a.inrs = ",".join(listed)
    if not a.inrs and not (a.cod_from and a.cod_to):
        ap.error("need --inrs, --inrs-file, or both --cod-from/--cod-to")

    sel = select(a)
    if a.limit:
        sel = sel.head(a.limit)
    names = dict(zip(sel.INR, sel.projectName))

    todo, skipped = [], []
    for inr in sel.INR:
        hits = sorted((BASE / "research").glob(f"{inr}_*"))
        if not a.force and hits and (hits[0] / done_marker(a.mode)).exists():
            skipped.append(inr)
        else:
            todo.append(inr)

    print(f"batch '{a.name}': {len(sel)} selected, {len(skipped)} already done, "
          f"{len(todo)} to run, concurrency {a.concurrency}, mode {a.mode}")
    print(sel[["INR", "projectName", "county", "capacityMw", "fuel", "technology",
               "projectCod"]].to_string(index=False))
    if a.dry_run:
        return

    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(run_one, inr, a.mode, a.token_budget) for inr in todo]
        for _ in as_completed(futs):
            pass

    out_dir = BASE / "research" / "_batches" / a.name
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [collect(inr, names.get(inr, ""), a.mode) for inr in sel.INR]
    total_cost = sum(r.get("cost_usd") or 0 for r in rows)
    summary = {"batch": a.name, "mode": a.mode, "selected": len(sel),
               "ran": len(todo), "skipped_done": len(skipped),
               "total_cost_usd": round(total_cost, 2), "projects": rows}
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1))
    keys = sorted({k for r in rows for k in r})
    with (out_dir / "summary.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")

    # deep-scan queue: the organized handoff — triage-flagged INRs, one per line with
    # context, feeds straight back in via --inrs-file for the deep pass
    flagged = [r for r in rows if r.get("deep_scan")]
    if a.mode == "triage":
        lines = ["# deep-scan queue — triage-flagged projects; run with:",
                 f"#   uv run gis-research/scripts/research_tools/run_batch.py "
                 f"--name {a.name}-deep --mode deep --inrs-file {out_dir / 'deep_queue.txt'}"]
        lines += [f"{r['inr']}  # {r.get('project','')} — {r.get('focus','')}" for r in flagged]
        (out_dir / "deep_queue.txt").write_text("\n".join(lines) + "\n")

    print(f"\nbatch done: {ok}/{len(rows)} ok, {len(flagged)} flagged for deep scan, "
          f"total cost ${total_cost:.2f}")
    print(f"summary: {out_dir}/summary.json + .csv"
          + (f" · deep queue: {out_dir}/deep_queue.txt" if a.mode == 'triage' else ""))


if __name__ == "__main__":
    main()
