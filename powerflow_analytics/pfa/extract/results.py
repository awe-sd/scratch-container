"""SCOPF output tables, sliced to one study's runs.

All AWOPF output tables key on RUNID only; each fetch filters through a
subquery on OPFRUN so we never scan outside the study.
"""
from __future__ import annotations

import pandas as pd

from .. import sf


def _runid_filter(study_id: int) -> str:
    return f"RUNID IN (SELECT RUNID FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)})"


def fetch_ctgviol(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"""
        SELECT RUNID, FROMNUM, TONUM, CKT, BRANCHNAME, BRANCHID, CTGLABEL,
               BRANCHCONTINGENCYID, LIMVIOLPCT, CTGPCT, LIMVIOLLIMIT, LIMVIOLSCALE,
               CTGRANK, OUTBRANCHDIRECTION, FROMNAME, TONAME
        FROM AWOPF.DBO.OUTCTGVIOL2
        WHERE {_runid_filter(study_id)}
        """,
    )
    sf.validate_columns(
        df, ["RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "FROMNAME", "TONAME"],
        "OUTCTGVIOL2",
    )
    return df


def fetch_branch(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"""
        SELECT RUNID, LABEL, FROMNUM, TONUM, CKT, BRANCHID, MWFROM,
               LIMITMVANORMAL, LIMITMVACTG, PERCENTMVA, MARGCOSTMVA, CTGVIOL,
               CTGMAXPERC, CTGMAXPERCNAME, BRANCHCONTINGENCYID,
               MONITORED, MONITOREDACTUAL, OPFBINDING, FROMNAME, TONAME, LINESTATUS
        FROM AWOPF.DBO.OUTBRANCH2
        WHERE {_runid_filter(study_id)}
        """,
    )
    sf.validate_columns(
        df, ["RUNID", "FROMNUM", "TONUM", "CKT", "PERCENTMVA", "MARGCOSTMVA"], "OUTBRANCH2"
    )
    return df


def fetch_interface(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"SELECT * FROM AWOPF.DBO.OUTINTERFACE2 WHERE {_runid_filter(study_id)}",
    )
    sf.validate_columns(df, ["RUNID", "INTERFACENAME", "PERCENTMVA", "LIMITUSED"], "OUTINTERFACE2")
    return df


def fetch_gen(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"""
        SELECT RUNID, LABEL, GENUNITID, BUSNUM, ID, UNITTYPE, MW, MWMIN, MWMAX,
               EDMARGCOSTMW, BUSMARGCOSTMW, GENSTATUS, LPDELTAMW, AGC, PARTFACT,
               FUELTYPE, FUELZONE, RENEWZONE, AREANAME, ZONENAME
        FROM AWOPF.DBO.OUTGEN2
        WHERE {_runid_filter(study_id)}
        """,
    )
    sf.validate_columns(df, ["RUNID", "BUSNUM", "ID", "MW", "LPDELTAMW", "BUSMARGCOSTMW"], "OUTGEN2")
    return df


def fetch_constraint(study_id: int) -> pd.DataFrame:
    """LP constraint rows: OPFCNLAMBDA is the shadow price, LPOPFCTGID the ctg label,
    LPBASICVARID the marginal control variable (usually a gen)."""
    df = sf.query(
        "AWOPF",
        f"SELECT * FROM AWOPF.DBO.OUTCONSTRAINT2 WHERE {_runid_filter(study_id)}",
    )
    sf.validate_columns(
        df, ["RUNID", "FROMNUM", "TONUM", "CKT", "LPOPFCTGID", "OPFCNLAMBDA", "LPBASICVARID"],
        "OUTCONSTRAINT2",
    )
    return df


def fetch_tofinder(study_id: int) -> pd.DataFrame:
    df = sf.query(
        "AWOPF",
        f"SELECT * FROM AWOPF.DBO.OUTTOFINDERMAX2 WHERE {_runid_filter(study_id)}",
    )
    sf.validate_columns(
        df,
        ["RUNID", "FROMNUM_TARGET", "TONUM_TARGET", "CKT_TARGET", "CTGLABEL",
         "BRANCHID_OUTAGE", "FLOWDELTA", "OUTAGE_GROUP"],
        "OUTTOFINDERMAX2",
    )
    return df
