"""Dedicated deep-scan worker — safe to run SEVERAL in parallel over the flagged queue.

Each worker loops: pick the largest-MW project with deep_scan_recommended=true that is
not done, not given-up-on, and not currently claimed by another worker; atomically CLAIM
it; run run_agent.py --mode deep on it; repeat. When the queue is dry it idles and
re-checks (triage batches keep adding flags); exits after --idle-exit consecutive dry
checks. Kill any worker anytime — per-project runs are atomic and resumable.

Coordination (lets N workers share one queue without stepping on each other):
- `.deep_claim`  — an in-progress marker (JSON: attempts, ts, pid). Created with O_EXCL so
  exactly one worker wins a race for the same INR. A claim older than STALE_CLAIM_SEC is
  treated as a crashed worker and stolen.
- `findings.json` — the permanent "done" gate (written by a successful deep run).
- `.deep_failed`  — written after MAX_ATTEMPTS runs fail to produce findings.json; the INR
  is then skipped for good instead of retried forever (the old loop re-ran the same INR
  indefinitely — this bounds it).

Usage:
  uv run gis-research/scripts/research_tools/deep_worker.py                 # Sonnet deep, 1 worker
  uv run gis-research/scripts/research_tools/deep_worker.py --model opus    # Opus instead
  # 4 in parallel: launch this command 4 times (each in its own background task)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]  # gis-research/
ROOT = BASE.parent
RUN_AGENT = Path(__file__).with_name("run_agent.py")
MODELS = {"opus": "us.anthropic.claude-opus-4-7", "sonnet": "us.anthropic.claude-sonnet-4-6"}

MAX_ATTEMPTS = 2         # deep runs per INR before giving up (writing .deep_failed)
STALE_CLAIM_SEC = 3600   # a claim older than this = crashed worker → steal it


def mw_map() -> dict:
    df = pd.read_parquet(BASE / "data" / "ercot_generation_interconnect.parquet")
    latest = df[df.fileDate == df.fileDate.max()]
    return dict(zip(latest.INR, latest.capacityMw))


def read_claim(d: Path) -> dict | None:
    f = d / ".deep_claim"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except (json.JSONDecodeError, OSError):
        return {"attempts": 0, "ts": 0}  # unreadable → treat as re-claimable


def next_inr(mw: dict) -> tuple[str, Path, int] | None:
    """Largest-MW flagged project that is unfinished, not given up on, and not freshly
    claimed. Returns (inr, proj_dir, attempts_so_far) or None when the queue is dry."""
    now = time.time()
    cands = []
    for tf in BASE.glob("research/*/triage_findings.json"):
        try:
            t = json.loads(tf.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        if not t.get("deep_scan_recommended"):
            continue
        d = tf.parent
        if (d / "findings.json").exists() or (d / ".deep_failed").exists():
            continue
        claim = read_claim(d)
        if claim and now - claim.get("ts", 0) < STALE_CLAIM_SEC:
            continue  # another worker owns it (fresh claim)
        inr = t.get("inr") or d.name.split("_")[0]
        cands.append((mw.get(inr, 0), inr, d, (claim or {}).get("attempts", 0)))
    if not cands:
        return None
    _, inr, d, attempts = max(cands, key=lambda c: c[0])
    return inr, d, attempts


def claim(d: Path, attempts: int) -> bool:
    """Atomically take the in-progress marker. O_EXCL means only one of several racing
    workers wins; the losers get FileExistsError and move to the next INR. A stale claim
    (crashed worker) is stolen."""
    payload = json.dumps({"attempts": attempts, "ts": time.time(), "pid": os.getpid()})
    f = d / ".deep_claim"
    try:
        fd = os.open(f, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        cur = read_claim(d)
        if cur and time.time() - cur.get("ts", 0) >= STALE_CLAIM_SEC:
            f.write_text(payload)  # steal the stale claim
            return True
        return False
    with os.fdopen(fd, "w") as fh:
        fh.write(payload)
    return True


def finish(d: Path, attempts: int) -> str:
    """Record the outcome of one deep run and release/mark the claim accordingly."""
    if (d / "findings.json").exists():
        (d / ".deep_claim").unlink(missing_ok=True)  # done — findings.json is the gate now
        return "ok"
    attempts += 1
    if attempts >= MAX_ATTEMPTS:
        (d / ".deep_failed").write_text(f"{attempts} deep runs, no findings.json")
        (d / ".deep_claim").unlink(missing_ok=True)
        return "gave_up"
    # re-claimable immediately (ts=0), attempts carried forward so retries stay bounded
    (d / ".deep_claim").write_text(json.dumps({"attempts": attempts, "ts": 0}))
    return "retry"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", choices=("opus", "sonnet"), default="sonnet")
    ap.add_argument("--idle-exit", type=int, default=6,
                    help="exit after this many consecutive dry checks (5 min apart)")
    a = ap.parse_args()
    mw = mw_map()

    done, dry = 0, 0
    while dry < a.idle_exit:
        pick = next_inr(mw)
        if pick is None:
            dry += 1
            print(f"queue dry ({dry}/{a.idle_exit}) — sleeping 5 min", flush=True)
            time.sleep(300)
            continue
        inr, d, attempts = pick
        if not claim(d, attempts):
            continue  # lost the race to another worker; pick again immediately
        dry = 0
        print(f"deep scan start: {inr} ({mw.get(inr, '?')} MW) [{a.model}] "
              f"attempt {attempts + 1}/{MAX_ATTEMPTS}", flush=True)
        rc = subprocess.run(
            ["uv", "run", str(RUN_AGENT), inr, "--mode", "deep", "--model", MODELS[a.model]],
            cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        outcome = finish(d, attempts)
        done += 1
        print(f"deep scan done:  {inr} rc={rc} outcome={outcome} (total {done})", flush=True)

    print(f"deep worker exiting: {done} deep runs completed, queue dry")


if __name__ == "__main__":
    main()
