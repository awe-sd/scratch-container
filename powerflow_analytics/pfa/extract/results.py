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
    """Note (2026-08-11 offer-chain diagnosis): OUTGEN2.CUSTOMSTRING2/3 and
    CUSTOMFLOAT4 were investigated as a possible direct DAM-settlement-point
    bridge (avoiding the BUSNAME->GENUNIT->GENUNITSCEDNAME name-matching
    chain below) but are 100% NULL for this study (230,370/230,370 rows) —
    not populated for ISOMARKETID=6. Also checked AW.DBO.CPNODE.DISPLAYNAME
    (joined via GENUNIT.CPNODEID) as an alternate SCED-name source: its
    per-unit names (e.g. JCKCNTY2_CT3/_CT4) do NOT appear in
    ERCOT60DDAMGENRESOURCE.SETTLEMENTPOINTNAME at all, while the existing
    GENUNITSCEDNAME-derived name (JCKCNTY2_CC1) does — confirming the
    current sced_names()/dam_offers() chain already uses the only naming
    convention the DAM disclosure actually matches. Neither alternate is
    wired in; this note exists so the next person doesn't re-try them.

    FUELZONE / RENEWZONE (2026-09-11, study 14605): some OUTGEN2 schema
    versions lack these columns entirely (14605 is ptoid 1517, a different
    vintage than 14411/12/25/31/14492 which all still carry them). Probe
    INFORMATION_SCHEMA.COLUMNS first and only select a column when present;
    otherwise emit it as a NULL literal so downstream code that references
    the column keeps working without a KeyError."""
    cols_df = sf.query(
        "AWOPF",
        """
        SELECT COLUMN_NAME FROM AWOPF.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'DBO' AND TABLE_NAME = 'OUTGEN2'
          AND COLUMN_NAME IN ('FUELZONE', 'RENEWZONE')
        """,
    )
    present = set(cols_df["COLUMN_NAME"]) if not cols_df.empty else set()
    fuelzone_expr = "FUELZONE" if "FUELZONE" in present else "NULL AS FUELZONE"
    renewzone_expr = "RENEWZONE" if "RENEWZONE" in present else "NULL AS RENEWZONE"
    df = sf.query(
        "AWOPF",
        f"""
        SELECT RUNID, LABEL, GENUNITID, BUSNUM, ID, UNITTYPE, MW, MWMIN, MWMAX,
               EDMARGCOSTMW, BUSMARGCOSTMW, GENSTATUS, LPDELTAMW, AGC, PARTFACT,
               FUELTYPE, {fuelzone_expr}, {renewzone_expr}, AREANAME, ZONENAME
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
