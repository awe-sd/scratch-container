"""Study setup: OPFSTUDY / OPFRUN / OPFRUNSCENARIO."""
from __future__ import annotations

import pandas as pd

from .. import sf


def fetch_study(study_id: int) -> pd.DataFrame:
    df = sf.query("AWOPF", f"SELECT * FROM AWOPF.DBO.OPFSTUDY WHERE STUDYID = {int(study_id)}")
    if df.empty:
        raise ValueError(f"study {study_id} not found in AWOPF.DBO.OPFSTUDY")
    sf.validate_columns(df, ["STUDYID", "STUDYNAME", "ISOMARKETID", "PTOID"], "OPFSTUDY")
    return df


def fetch_runs(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"SELECT * FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)} ORDER BY RUNID",
    )
    if df.empty:
        raise ValueError(f"study {study_id} has no runs in AWOPF.DBO.OPFRUN")
    sf.validate_columns(df, ["RUNID", "STUDYID", "SIMDATE", "SIMHOUR", "TOUTREFID"], "OPFRUN")
    return df


def fetch_run_scenarios(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"SELECT * FROM AWOPF.DBO.OPFRUNSCENARIO WHERE STUDYID = {int(study_id)}",
    )
    sf.validate_columns(df, ["RUNID", "STUDYID", "CASEID", "SCENARIOID"], "OPFRUNSCENARIO")
    return df
