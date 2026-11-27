"""Path-opt results (AW.POPT — built on the FWD auction decomposition table,
so OPTIONPRICE is the expected auction-cost mark for the path).

PATHOPT_BATCH_INPUT.PATHOPTRUNID is NULL for every row in practice (dead end —
batches never got linked back to a run id), so path costs come straight from
AW.POPT.PATHOPTDETAILVIEW instead, keyed on STUDYID/BRANCHLABEL/CTGLABEL.

BRANCHLABEL resolution: PATHOPTDETAILVIEW's BRANCHLABEL is the same LABEL
field AWOPF.DBO.OUTBRANCH2 carries for the branch (confirmed empirically for
1436-2081@DWCSRAM5 in study 14411: OUTBRANCH2.LABEL='35100_A', and filtering
PATHOPTDETAILVIEW to that exact label gives WCPP->CHISMGRD_RN, $2.24 @
SF~0.31 — the known-good answer). Labels are opaque tokens that do NOT embed
FROMNUM/TONUM, so house rule: resolve the label from FROMNUM/TONUM/CKT, match
it EXACTLY, and if it does not resolve return None — never fuzzy-match names.
"""
from __future__ import annotations

import pandas as pd

from .. import sf
from ..constraint_id import ConstraintId


def _branch_labels(study_id: int, f: int, t: int, ckt: str) -> list[str]:
    """OUTBRANCH2.LABEL(s) for this study's FROMNUM/TONUM/CKT (exact; empty if none)."""
    df = sf.query("AWOPF", f"""
        SELECT DISTINCT LABEL FROM AWOPF.DBO.OUTBRANCH2
        WHERE RUNID IN (SELECT RUNID FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)})
          AND FROMNUM = {int(f)} AND TONUM = {int(t)} AND TRIM(CKT) = '{ckt.strip()}'
          AND LABEL IS NOT NULL""")
    return [str(x) for x in df["LABEL"]] if len(df) else []


def best_paths(study_id: int, constraint: str, top_n: int = 3) -> pd.DataFrame | None:
    """Cheapest completed path-opt paths per unit exposure for one constraint, or None when its branch label does not resolve exactly."""
    cid = ConstraintId.parse(constraint)
    ctg = cid.ctglabel
    labels = _branch_labels(study_id, cid.fromnum, cid.tonum, cid.ckt)
    if not labels:
        return None
    label_filter = "BRANCHLABEL IN (" + ", ".join(f"'{x}'" for x in labels) + ")"
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
        ORDER BY PRICE_PER_SF ASC, SOURCENAME, SINKNAME LIMIT {int(top_n)}""")
    return df if len(df) else None


def get_run_config(run_id: int) -> pd.Series:
    """PathOpt run config (topology set, study, direction, etc)."""
    df = sf.query("AW", f"""
        SELECT PATHOPTRUNID, STUDYID, TOPOLOGYSHIFTSETID, SIMHOUR,
               DIRECTION, FLIPDIRECTION, WINDOWDAYS, DEADBUSFILTER,
               BRANCHLABEL, CTGLABEL, STATUS
        FROM AW.POPT.PATHOPTRUNVIEW
        WHERE PATHOPTRUNID = {int(run_id)}
        LIMIT 1""")
    if len(df) == 0:
        raise ValueError(f"Run {run_id} not found")
    return df.iloc[0]


def fetch_detail(run_id: int, columns: list[str] | None = None, top_n: int | None = None) -> pd.DataFrame:
    """PathOpt detail rows for one run (default: all ~500k paths). Column selection for memory control."""
    cols = ", ".join(columns) if columns else "*"
    limit_clause = f"LIMIT {int(top_n)}" if top_n else ""
    return sf.query("AW", f"""
        SELECT {cols}
        FROM AW.POPT.PATHOPTDETAIL
        WHERE PATHOPTRUNID = {int(run_id)}
        {limit_clause}""")


def get_topology_set_members(set_id: int) -> pd.DataFrame:
    """Topology set members (psenshiftid, topologyid) with simdate/simhour from OPFRUN."""
    return sf.query("AW", f"""
        SELECT ts.TOPOLOGYSHIFTSETID, ts.PSENSHIFTID, ts.TOPOLOGYID,
               r.RUNID, r.SIMDATE, r.SIMHOUR
        FROM AW.POPT.TOPOLOGYSHIFTSET ts
        JOIN AWOPF.DBO.OPFRUN r ON ts.TOPOLOGYID = r.TOPOLOGYID
        WHERE ts.TOPOLOGYSHIFTSETID = {int(set_id)}
        ORDER BY r.SIMDATE, r.SIMHOUR, ts.TOPOLOGYID""")


def fetch_constraint_sp(run_ids: list[int], frm: int, to: int, ckt: str, ctg: str) -> pd.DataFrame:
    """OUTCONSTRAINT2 shadow price (OPFCNLAMBDA) per run for one constraint; absent rows = not enforced."""
    ids = ",".join(str(int(r)) for r in run_ids)
    return sf.query("AWOPF", f"""
        SELECT RUNID, MAX(OPFCNLAMBDA) AS SP FROM AWOPF.DBO.OUTCONSTRAINT2
        WHERE RUNID IN ({ids}) AND FROMNUM = {int(frm)} AND TONUM = {int(to)}
          AND CKT = '{ckt}' AND LPOPFCTGID = '{ctg}'
        GROUP BY RUNID""")


def fetch_ctg_loading(study_id: int, frm: int, to: int, ckt: str, ctg: str) -> pd.DataFrame:
    """OUTCTGVIOL2 LIMVIOLPCT per run (all runs where the constraint row exists) joined to OPFRUN date/hour."""
    return sf.query("AWOPF", f"""
        SELECT v.RUNID, r.SIMDATE, r.SIMHOUR, MAX(v.LIMVIOLPCT) AS LIMVIOLPCT
        FROM AWOPF.DBO.OUTCTGVIOL2 v JOIN AWOPF.DBO.OPFRUN r ON r.RUNID = v.RUNID
        WHERE r.STUDYID = {int(study_id)} AND v.FROMNUM = {int(frm)} AND v.TONUM = {int(to)}
          AND v.CKT = '{ckt}' AND v.CTGLABEL = '{ctg}'
        GROUP BY v.RUNID, r.SIMDATE, r.SIMHOUR""")


def fetch_study_runs(study_id: int) -> pd.DataFrame:
    return sf.query("AWOPF", f"""
        SELECT RUNID, SIMDATE, SIMHOUR, TOPOLOGYID FROM AWOPF.DBO.OPFRUN
        WHERE STUDYID = {int(study_id)}""")
