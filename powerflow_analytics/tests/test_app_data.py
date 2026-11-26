import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import data


@pytest.fixture
def fake_study(tmp_path, monkeypatch):
    """Minimal cache + output for study 99: enough for a StudyBundle."""
    cache = tmp_path / "cache" / "study_99"
    out = tmp_path / "output" / "study_99"
    cache.mkdir(parents=True)
    out.mkdir(parents=True)

    pd.DataFrame({"STUDYID": [99], "STUDYNAME": ["TEST_V1"], "PTOID": [1504]}).to_parquet(
        cache / "opfstudy.parquet", index=False
    )
    pd.DataFrame({"RUNID": [1, 2], "SIMDATE": ["2026-09-01", "2026-09-01"], "SIMHOUR": [1, 2]}).to_parquet(
        cache / "opfrun.parquet", index=False
    )
    pd.DataFrame({
        "RUNID": [1, 2], "FROMNUM": [10, 10], "TONUM": [11, 11], "CKT": ["1", "1"],
        "CTGLABEL": ["CTGA", "CTGA"], "LIMVIOLPCT": [120.0, 80.0],
        "FROMNAME": ["A", "A"], "TONAME": ["B", "B"],
    }).to_parquet(cache / "outctgviol2.parquet", index=False)

    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "N_RUNS_BINDING": [1], "SCORE": [21.0]}).to_csv(
        out / "ranked_constraints.csv", index=False
    )
    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "BUSNUM": [100], "DIFF_MW": [30.0]}).to_csv(
        out / "marginal_units.csv", index=False
    )
    pd.DataFrame({"CONSTRAINT": ["10-11-1@CTGA"], "OUTAGE_GROUP": ["X - Y"], "MEAN_FLOWDELTA": [40.0]}).to_csv(
        out / "tofinder_summary.csv", index=False
    )

    monkeypatch.setattr(data, "CACHE_ROOT", tmp_path / "cache")
    monkeypatch.setattr(data, "OUTPUT_ROOT", tmp_path / "output")
    data.load_study.cache_clear()
    yield 99
    data.load_study.cache_clear()


def test_list_studies(fake_study, tmp_path):
    # cache-only study (no output) must NOT appear
    (tmp_path / "cache" / "study_50").mkdir()
    assert data.list_studies() == [99]


def test_load_study_bundle(fake_study):
    b = data.load_study(99)
    assert b.study_name == "TEST_V1"
    assert b.n_runs == 2
    assert list(b.ranked["CONSTRAINT"]) == ["10-11-1@CTGA"]
    assert len(b.marginal_units) == 1 and len(b.tofinder) == 1
    # binding profile: only the LIMVIOLPCT >= 99.5 row survives, joined to run hours
    assert list(b.binding["SIMHOUR"]) == [1]
    assert b.binding["CONSTRAINT"].iloc[0] == "10-11-1@CTGA"


def test_load_study_memoized(fake_study):
    assert data.load_study(99) is data.load_study(99)
