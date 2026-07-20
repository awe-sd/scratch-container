"""Append-only S3 mirror of the gis-research artifact tree. DRY-RUN by default.

Layout (spec §10): same relative paths as the repo; parquet snapshots get dated keys;
NEVER --delete (S3 is the superset archive). Transcripts are gzipped into
transcripts/ before sync. Bucket: s3://gis-research (us-east-1).
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
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]   # gis-research/
BUCKET = "s3://gis-research/gis-research"
TODAY = dt.date.today().isoformat()

GROUPS = {
    "research": ["aws", "s3", "sync", str(BASE / "research"), f"{BUCKET}/research",
                 "--exclude", "*", "--include", "*/sources/*", "--include", "*/imagery/*",
                 "--include", "*/transcripts/*", "--include", "*/findings.json",
                 "--include", "*/triage_findings.json", "--include", "*/factsheet.json",
                 "--include", "*/eia_history.json", "--include", "*/brief.html",
                 "--include", "*/dossier.md"],
    "data": ["aws", "s3", "sync", str(BASE / "data" / "reference"),
             f"{BUCKET}/data/reference"],
}


def gzip_transcripts() -> int:
    n = 0
    for src in BASE.glob("research/*/run_stream_*.jsonl"):
        dest_dir = src.parent / "transcripts"
        dest = dest_dir / (src.name + ".gz")
        if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
            continue
        dest_dir.mkdir(exist_ok=True)
        with src.open("rb") as fi, gzip.open(dest, "wb") as fo:
            shutil.copyfileobj(fi, fo)
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
    ap.add_argument("--only", choices=[*GROUPS, "analysis"], default=None)
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
        run = cmd if a.execute else (cmd + ["--dryrun"] if cmd[2] == "sync" else None)
        print(f"\n== {name}: {' '.join(cmd)}")
        if run is None:
            continue   # cp has no --dryrun preview worth running; printed above
        r = subprocess.run(run, capture_output=True, text=True)
        tail = (r.stdout or r.stderr).strip().splitlines()[-3:]
        print("\n".join(tail))
        if r.returncode != 0:
            failed += 1
            if "AccessDenied" in (r.stderr or ""):
                print("  -> AccessDenied: admin policy for s3://gis-research still pending.")
    return 3 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
