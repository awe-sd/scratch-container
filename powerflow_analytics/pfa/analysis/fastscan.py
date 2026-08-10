"""Fast-scan overlay: how often would the constraint bind under historical
injection patterns replayed on the study topology (AWDEV.FLOW_ANALYSIS).

Negative HEADROOM = the historical hour would have loaded the branch past its
rating on this topology. HEADROOM_AFTER_CURTAILMENT restores curtailed
wind/solar, so pct-negative there shows stress that curtailment currently
masks.
"""
from __future__ import annotations

import pandas as pd

from .. import sf


def find_configs(study_id: int, fromnum: int, tonum: int, ctglabel: str) -> pd.DataFrame:
    return sf.query(
        "AWDEV",
        f"""
        SELECT CONFIG_ID, STUDY_ID, TOPOLOGY_ID, CTG_LABEL, DIRECTION, BRANCH_LABEL, CREATED_AT
        FROM AWDEV.FLOW_ANALYSIS.FAST_SCAN_CONFIG
        WHERE STUDY_ID = {int(study_id)} AND FROM_NUM = {int(fromnum)}
          AND TO_NUM = {int(tonum)} AND CTG_LABEL = '{ctglabel}' AND IS_ACTIVE
        ORDER BY CREATED_AT DESC LIMIT 20
        """,
    )


def headroom_profile(config_id: int) -> pd.DataFrame:
    """Per hour-of-day: sample count, % negative headroom (raw and with
    curtailment restored), median headroom MW."""
    return sf.query(
        "AWDEV",
        f"""
        SELECT HOUR(TIMESTAMP) AS HR, COUNT(*) AS N,
               100 * AVG(IFF(HEADROOM < 0, 1, 0)) AS PCT_NEG,
               100 * AVG(IFF(HEADROOM_AFTER_CURTAILMENT < 0, 1, 0)) AS PCT_NEG_CURT,
               MEDIAN(HEADROOM) AS MED_HEADROOM
        FROM AWDEV.FLOW_ANALYSIS.FAST_SCAN_RESULTS
        WHERE CONFIG_ID = {int(config_id)}
        GROUP BY 1 ORDER BY 1
        """,
    )
