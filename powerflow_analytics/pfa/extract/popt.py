"""Path-opt results (AW.POPT — built on the FWD auction decomposition table,
so OPTIONPRICE is the expected auction-cost mark for the path).

PATHOPT_BATCH_INPUT.PATHOPTRUNID is NULL for every row in practice (dead end —
batches never got linked back to a run id), so path costs come straight from
AW.POPT.PATHOPTDETAILVIEW instead, keyed on STUDYID/BRANCHLABEL/CTGLABEL.

BRANCHLABEL resolution: PATHOPTDETAILVIEW's BRANCHLABEL is the same LABEL
field AWOPF.DBO.OUTBRANCH2 carries for the branch (confirmed empirically for
1436-2081@DWCSRAM5 in study 14411: OUTBRANCH2.LABEL='35100_A', and filtering
PATHOPTDETAILVIEW to that exact label gives WCPP->CHISMGRD_RN, $2.24 @
SF~0.31 — the known-good answer). Labels are opaque ISO-style tokens
('35100_A') that do NOT embed FROMNUM/TONUM, so pattern-matching on the
numbers (the original approach) is unreliable: for this same constraint it
also pulled in an unrelated branch ('BOWFMR1') that happens to contain no
spaces either. A descriptive multi-word style ('1436 PARKER_5 2081 HICKS_SW
1') has been seen in isolated docs/other studies, so the ILIKE match on
FROMNUM/TONUM is kept as a fallback for when the exact-label lookup misses.
"""
from __future__ import annotations

import pandas as pd

from .. import sf


def _branch_label(study_id: int, f: str, t: str) -> str | None:
    """Single targeted lookup: OUTBRANCH2.LABEL for this study's FROMNUM/TONUM."""
    df = sf.query("AWOPF", f"""
        SELECT DISTINCT LABEL FROM AWOPF.DBO.OUTBRANCH2
        WHERE RUNID IN (SELECT RUNID FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)})
          AND FROMNUM = {int(f)} AND TONUM = {int(t)}
        LIMIT 1""")
    return str(df["LABEL"].iloc[0]) if len(df) else None


def best_paths(study_id: int, constraint: str, top_n: int = 3) -> pd.DataFrame | None:
    """Cheapest completed path-opt paths per unit exposure for one constraint."""
    f, t, rest = constraint.split("-", 2)
    ctg = rest.split("@")[1]
    label = _branch_label(study_id, f, t)
    label_filter = (f"BRANCHLABEL = '{label}'" if label else
                    f"(BRANCHLABEL ILIKE '%{f} %{t}%' OR BRANCHLABEL NOT LIKE '% %')")
    df = sf.query("AW", f"""
        WITH ranked AS (
          SELECT SOURCENAME, SINKNAME, OPTIONPRICE, AVG_SF, WAVG_DOLLAR_MWH, RUNCREATEDATE,
                 OPTIONPRICE / NULLIF(AVG_SF, 0) AS PRICE_PER_SF,
                 ROW_NUMBER() OVER (PARTITION BY SOURCENAME, SINKNAME
                                     ORDER BY RUNCREATEDATE DESC) AS rn
          FROM AW.POPT.PATHOPTDETAILVIEW
          WHERE STUDYID = {int(study_id)} AND CTGLABEL = '{ctg}' AND PRICECLASSID = 2
            AND STATUS = 'COMPLETED' AND AVG_SF >= 0.05 AND {label_filter}
        )
        SELECT SOURCENAME, SINKNAME, OPTIONPRICE, AVG_SF, WAVG_DOLLAR_MWH, PRICE_PER_SF
        FROM ranked WHERE rn = 1
        ORDER BY PRICE_PER_SF ASC LIMIT {int(top_n)}""")
    return df if len(df) else None
