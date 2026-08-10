"""Path-opt results (AW.POPT — built on the FWD auction decomposition table,
so OPTIONPRICE is the expected auction-cost mark for the path)."""
from __future__ import annotations

import pandas as pd

from .. import sf


def best_paths(study_id: int, constraint: str, top_n: int = 3) -> pd.DataFrame | None:
    """Cheapest completed path-opt paths per unit exposure for one constraint."""
    f, t, rest = constraint.split("-", 2)
    ctg = rest.split("@")[1]
    batches = sf.query("AW", f"""
        SELECT PATHOPTRUNID FROM AW.POPT.PATHOPT_BATCH_INPUT
        WHERE STUDYID = {int(study_id)} AND CTGLABEL = '{ctg}' AND PATHOPTRUNID IS NOT NULL
          AND (BRANCHLABEL ILIKE '%{f} %{t} %' OR
               (BRANCHLABEL NOT LIKE '%[0-9] %' AND BRANCHLABEL NOT ILIKE '% %'))
        LIMIT 8""")
    if batches.empty:
        return None
    run_ids = ",".join(str(int(x)) for x in batches["PATHOPTRUNID"].unique())
    df = sf.query("AW", f"""
        WITH d AS (
          SELECT SOURCENAME, SINKNAME, OPTIONPRICE, AVG_SF, WAVG_DOLLAR_MWH,
                 OPTIONPRICE / NULLIF(AVG_SF, 0) AS PRICE_PER_SF
          FROM AW.POPT.PATHOPTDETAIL
          WHERE PATHOPTRUNID IN ({run_ids}) AND AVG_SF >= 0.05
        )
        SELECT * FROM d ORDER BY PRICE_PER_SF ASC LIMIT {int(top_n)}""")
    return df if len(df) else None
