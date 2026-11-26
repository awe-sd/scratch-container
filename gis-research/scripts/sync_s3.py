"""Append-only S3 mirror of the gis-research artifact tree. DRY-RUN by default.

Layout (spec §10): S3 is the superset archive — research/ mirrors 1:1 (PDFs,
imagery, gzipped transcripts, findings, briefs, dossiers, logs — everything),
except the raw pre-gzip *.jsonl transcripts, which are superseded by their
transcripts/*.jsonl.gz siblings and excluded from sync. data/reference/ mirrors
as-is; parquet snapshots get dated keys (data/snapshots/<table>/<date>.parquet).
Analysis writeups (docs/analysis/, e.g. logmine forensics) mirror under
analysis/. A group whose local source dir doesn't exist yet is skipped with a
printed note, not treated as a failure. NEVER --delete (S3 is the superset
archive, local is always "latest"). Bucket: s3://gis-research (us-east-1).
Prereq: the container principal needs s3:ListBucket on the bucket and
s3:GetObject/PutObject on gis-research/* — until the admin attaches that policy,
--execute will print AccessDenied per group and exit 3 (that is a REPORTED outcome,
not a crash).

  uv run gis-research/scripts/sync_s3.py                # plan + --dryrun listing
  uv run gis-research/scripts/sync_s3.py --execute
  uv run gis-research/scripts/sync_s3.py --execute --only research
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]   # gis-research/
BUCKET = "s3://gis-research/gis-research"
TODAY = dt.date.today().isoformat()
AWS_TIMEOUT_S = 3600

GROUPS = {
    "research": ["aws", "s3", "sync", str(BASE / "research"), f"{BUCKET}/research",
                 "--exclude", "*/run_stream_*.jsonl",
                 # runtime orchestration droppings — no archival value
                 "--exclude", "*/.budget_*", "--exclude", "*/.deep_*",
                 "--exclude", "*/.checkpoint_state.json"],
    "data": ["aws", "s3", "sync", str(BASE / "data" / "reference"),
             f"{BUCKET}/data/reference",
             "--exclude", "search_cache/*"],  # ephemeral query cache, grows unbounded
    "analysis": ["aws", "s3", "sync", str(BASE / "docs" / "analysis"),
                 f"{BUCKET}/analysis"],
}


def gzip_transcripts() -> int:
    n = 0
    for src in BASE.glob("research/*/run_stream_*.jsonl"):
        dest_dir = src.parent / "transcripts"
        dest = dest_dir / (src.name + ".gz")
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        dest_dir.mkdir(exist_ok=True)
        tmp = dest.with_suffix(".gz.tmp")
        with src.open("rb") as fi, gzip.open(tmp, "wb") as fo:
            shutil.copyfileobj(fi, fo)
        os.replace(tmp, dest)   # atomic: readers never see a partial .gz
        n += 1
    return n


def parquet_snapshot_cmds() -> list[list[str]]:
    return [["aws", "s3", "cp", str(p),
             f"{BUCKET}/data/snapshots/{p.stem}/{TODAY}.parquet"]
            for p in BASE.glob("data/*.parquet")]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--only", choices=list(GROUPS), default=None)
    a = ap.parse_args()

    print(f"gzipped {gzip_transcripts()} new transcript(s)")
    cmds = []
    for name, cmd in GROUPS.items():
        if not a.only or a.only == name:
            cmds.append((name, cmd))
    if not a.only or a.only == "data":
        cmds += [(f"snapshot:{c[3].split('/')[-1]}", c) for c in parquet_snapshot_cmds()]

    failed = 0
    for name, cmd in cmds:
        print(f"\n== {name}: {' '.join(cmd)}")
        local = Path(cmd[3])
        if not local.exists():
            print(f"  -> skipped: local path does not exist yet ({local}).")
            continue
        run = cmd if a.execute else (cmd + ["--dryrun"] if cmd[2] == "sync" else None)
        if run is None:
            continue   # cp has no --dryrun preview worth running; printed above
        try:
            r = subprocess.run(run, capture_output=True, text=True, timeout=AWS_TIMEOUT_S)
        except FileNotFoundError:
            failed += 1
            print("  -> aws CLI not found on PATH.")
            continue
        except subprocess.TimeoutExpired:
            failed += 1
            print(f"  -> timed out after {AWS_TIMEOUT_S}s.")
            continue
        tail = (r.stdout or r.stderr).strip().splitlines()[-3:]
        print("\n".join(tail))
        if r.returncode != 0:
            failed += 1
            if "AccessDenied" in (r.stderr or ""):
                print("  -> AccessDenied: admin policy for s3://gis-research still pending.")
    return 3 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
