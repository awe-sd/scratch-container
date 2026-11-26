"""Shared pieces of the study-vs-DART shift-factor benchmark scripts: validation-set
lookup, reference node, output folders and the DART psenShiftDef lookup chain."""
from pathlib import Path

import pandas as pd
from pfa.sf import query

REFERENCE_CPNODEID = 12791
OUTPUT_ROOT = Path(__file__).resolve().parent / "output" / "validation_shift_compare"

_DART_DEDUPE = "QUALIFY ROW_NUMBER() OVER (PARTITION BY psd.psenshiftid, ps.cpnodeid ORDER BY psd.psenshiftid) = 1"


def study_dir(study_id: int) -> Path:
    return OUTPUT_ROOT / str(study_id)


def cache_dir(study_id: int) -> Path:
    return study_dir(study_id) / "cache"


def output_dir(study_id: int, subdir: str | None = None) -> Path:
    base = study_dir(study_id)
    return base / subdir if subdir else base


def window_label(date_from: str, date_to: str) -> str:
    """Month name when the window lies inside one calendar month, else ''."""
    a, b = pd.Timestamp(date_from), pd.Timestamp(date_to)
    return a.strftime("%B") if (a.year, a.month) == (b.year, b.month) else ""


def get_configs(study_id: int, created_after: str) -> pd.DataFrame:
    sql = f"""
    SELECT TOPOLOGYSHIFTSETID, BRANCHLABEL, CTGLABEL, INTERFACENAME, DIRECTION,
        CREATEDATE, NOTES, FROMNUM, TONUM, CKT
    FROM AW.POPT.TOPOLOGYSHIFTSETDEF
    WHERE STUDYID={study_id} AND CREATEDATE >= '{created_after}'
    """
    return query("AW", sql)


def get_config_labels(study_id: int, created_after: str) -> pd.DataFrame:
    return get_configs(study_id, created_after)[["TOPOLOGYSHIFTSETID", "BRANCHLABEL", "CTGLABEL"]]


def dart_chain_sql(select: str, start: str, end: str, branch_label: str, ctg_label: str, *,
                   psenshift: bool = False, cpnode: bool = False, dedupe: bool = False,
                   extra_where: str = "") -> str:
    """DART shifts for one branch/ctg label pair: psenShiftDef -> [PSENSHIFT] -> congDefConstraint
    -> congDefMonitor -> congDefContingency -> branchMonitored -> branch -> [CPNODE]."""
    joins = ["AW.dbo.psenShiftDef psd"]
    if psenshift:
        joins.append("INNER JOIN AW.DBO.PSENSHIFT ps ON ps.psenshiftid = psd.psenshiftid")
    joins += [
        "INNER JOIN AW.DBO.congDefConstraint cd ON cd.congConstraintID = psd.congConstraintID",
        "INNER JOIN AW.DBO.congDefMonitor cdm ON cdm.congMontID = cd.congMontID",
        "INNER JOIN AW.DBO.congDefContingency cdc ON cdc.congContID = cd.congContID",
        "INNER JOIN AW.DBO.branchMonitored bm ON bm.branchMonitoredID = cdm.branchMonitoredId",
        "INNER JOIN AW.DBO.branch b ON b.branchID = bm.branchID",
    ]
    if cpnode:
        joins.append("INNER JOIN AW.DBO.CPNODE cp ON cp.cpnodeid = ps.cpnodeid")
    nl = "\n        "
    return (
        f"SELECT {select}\n        FROM {nl.join(joins)}\n"
        f"        WHERE psd.isoMarketID = 6 AND psd.psenShiftTypeId = 14\n"
        f"            AND psd.extractionEnd >= '{start}' AND psd.extractionEnd <= '{end}'\n"
        f"            AND b.branchName = '{branch_label}'\n"
        f"            AND cdc.congContName = '{ctg_label}'"
        + (f"\n            {extra_where}" if extra_where else "")
        + (f"\n        {_DART_DEDUPE}" if dedupe else "")
    )
