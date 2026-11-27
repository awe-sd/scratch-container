"""Read-only data access for the dashboard: local cache + analysis CSVs only.

No Snowflake / SQL Server access from the app — pull and analyze first:
  uv run pfa pull --study <id>
  uv run pfa summary --study <id> --cutoff <YYYY-MM-DD> --tickets
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd


from pfa.analysis import constraints
from pfa.config import CACHE_ROOT, OUTPUT_ROOT  # re-bound at module level so tests can monkeypatch

CACHE_ROOT = CACHE_ROOT
OUTPUT_ROOT = OUTPUT_ROOT


@dataclass(frozen=True)
class StudyBundle:
    study_id: int
    study_name: str
    ranked: pd.DataFrame
    marginal_units: pd.DataFrame
    tofinder: pd.DataFrame
    binding: pd.DataFrame  # per binding row: CONSTRAINT, RUNID, SIMDATE, SIMHOUR, LIMVIOLPCT
    n_runs: int


def list_studies() -> list[int]:
    out = []
    for d in sorted(CACHE_ROOT.glob("study_*")):
        try:
            sid = int(d.name.removeprefix("study_"))
        except ValueError:
            continue
        if (OUTPUT_ROOT / d.name / "ranked_constraints.csv").exists():
            out.append(sid)
    return out


@lru_cache(maxsize=8)
def load_study(study_id: int) -> StudyBundle:
    cache = CACHE_ROOT / f"study_{study_id}"
    out = OUTPUT_ROOT / f"study_{study_id}"
    study = pd.read_parquet(cache / "opfstudy.parquet")
    runs = pd.read_parquet(cache / "opfrun.parquet")
    ctgviol = pd.read_parquet(cache / "outctgviol2.parquet")
    return StudyBundle(
        study_id=study_id,
        study_name=str(study["STUDYNAME"].iloc[0]),
        ranked=pd.read_csv(out / "ranked_constraints.csv"),
        marginal_units=pd.read_csv(out / "marginal_units.csv"),
        tofinder=pd.read_csv(out / "tofinder_summary.csv"),
        binding=constraints.binding_hours(ctgviol, runs),
        n_runs=int(runs["RUNID"].nunique()),
    )
