"""Fast-scan results and configs (AW.FLOW_ANALYSIS.FAST_SCAN_CONFIG / FAST_SCAN_RESULTS).

FAST_SCAN_RESULTS holds one row per replayed historical hour for a CONFIG_ID;
negative HEADROOM = the hour would have loaded the branch past its rating on
the study topology. HEADROOM_AFTER_CURTAILMENT restores curtailed wind/solar;
SOLAR_IMPACT is solar's MW contribution to headroom relief.
"""
from __future__ import annotations

import pandas as pd

from .. import config, sf


def find_configs(study_id: int, fromnum: int, tonum: int, ctglabel: str) -> pd.DataFrame:
    """Active configs for a constraint, newest first: CONFIG_ID, STUDY_ID, TOPOLOGY_ID, CTG_LABEL, DIRECTION, BRANCH_LABEL, CREATED_AT."""
    return sf.query(
        config.FLOW_ANALYSIS_DB,
        f"""
        SELECT CONFIG_ID, STUDY_ID, TOPOLOGY_ID, CTG_LABEL, DIRECTION, BRANCH_LABEL, CREATED_AT
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_CONFIG
        WHERE STUDY_ID = {int(study_id)} AND FROM_NUM = {int(fromnum)}
          AND TO_NUM = {int(tonum)} AND CTG_LABEL = {sf.quote(ctglabel)} AND IS_ACTIVE
        ORDER BY CREATED_AT DESC LIMIT 20
        """,
    )


def headroom_profile(config_id: int) -> pd.DataFrame:
    """Per hour-of-day: sample count, % negative headroom (raw and with
    curtailment restored), median headroom MW."""
    return sf.query(
        config.FLOW_ANALYSIS_DB,
        f"""
        SELECT HOUR(TIMESTAMP) AS HR, COUNT(*) AS N,
               100 * AVG(IFF(HEADROOM < 0, 1, 0)) AS PCT_NEG,
               100 * AVG(IFF(HEADROOM_AFTER_CURTAILMENT < 0, 1, 0)) AS PCT_NEG_CURT,
               MEDIAN(HEADROOM) AS MED_HEADROOM,
               APPROX_PERCENTILE(HEADROOM, 0.1) AS P10_HEADROOM
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
        GROUP BY 1 ORDER BY 1
        """,
    )


def negative_headroom(config_id: int) -> pd.DataFrame:
    """TIMESTAMP, HEADROOM for the config's negative-headroom hours only."""
    return sf.query(config.FLOW_ANALYSIS_DB, f"""
        SELECT TIMESTAMP, HEADROOM
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)} AND HEADROOM < 0
    """)


def solar_impact(config_id: int) -> pd.DataFrame:
    """TIMESTAMP, SOLAR_IMPACT for every hour of the config."""
    return sf.query(config.FLOW_ANALYSIS_DB, f"""
        SELECT TIMESTAMP, SOLAR_IMPACT
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
    """)


def headroom_with_curtailment(config_id: int) -> pd.DataFrame:
    """TIMESTAMP, HEADROOM, HEADROOM_AFTER_CURTAILMENT for every hour of the config."""
    return sf.query(
        config.FLOW_ANALYSIS_DB,
        f"""
        SELECT TIMESTAMP, HEADROOM, HEADROOM_AFTER_CURTAILMENT
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
        """,
    )


def headroom_for_month(config_id: int, month_number: int) -> pd.DataFrame:
    """TIMESTAMP, HEADROOM for the calendar month (1-12), all years."""
    return sf.query(config.FLOW_ANALYSIS_DB, f"""
        SELECT TIMESTAMP, HEADROOM
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)} AND MONTH(TIMESTAMP) = {int(month_number)}
    """)


def headroom_window(config_id: int, start: str, end: str) -> pd.DataFrame:
    """TIMESTAMP, HEADROOM, HEADROOM_RT, HEADROOM_AFTER_CURTAILMENT for start <= TIMESTAMP < end."""
    return sf.query(config.FLOW_ANALYSIS_DB, f"""
        SELECT TIMESTAMP, HEADROOM, HEADROOM_RT, HEADROOM_AFTER_CURTAILMENT
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
          AND TIMESTAMP >= '{start}' AND TIMESTAMP < '{end}'
    """)


def timestamp_span(config_id: int) -> tuple[pd.Timestamp, pd.Timestamp, int]:
    """(first TIMESTAMP, last TIMESTAMP, row count) of every hour stored for the config."""
    df = sf.query(config.FLOW_ANALYSIS_DB, f"""
        SELECT MIN(TIMESTAMP) AS T0, MAX(TIMESTAMP) AS T1, COUNT(*) AS N
        FROM {config.FLOW_ANALYSIS}.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
    """)
    df.columns = [c.upper() for c in df.columns]
    return pd.Timestamp(df["T0"].iloc[0]), pd.Timestamp(df["T1"].iloc[0]), int(df["N"].iloc[0])
