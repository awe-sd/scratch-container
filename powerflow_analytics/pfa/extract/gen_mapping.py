"""Generator identity bridges: OUTGENREF -> GENUNIT (and later, DAM offers)."""
from __future__ import annotations

import pandas as pd

from .. import config, sf


def fetch_genref(ptoid: int) -> pd.DataFrame:
    """(BUSNUM, ID) -> GENUNITID bridge; OUTGEN2.GENUNITID is null in current studies."""
    df = sf.query(
        "AWOPF",
        f"""
        SELECT OUTGENID, BUSNUM, ID, FUELTYPE, UNITTYPE, GENUNITID, BRANCHGENID
        FROM AWOPF.DBO.OUTGENREF
        WHERE ISOMARKETID = {config.ISO_MARKET_ID} AND PTOID = {int(ptoid)}
        """,
    )
    sf.validate_columns(df, ["BUSNUM", "ID", "GENUNITID"], "OUTGENREF")
    return df


def fetch_genunit() -> pd.DataFrame:
    df = sf.query(
        "AWDEV",
        f"""
        SELECT GENUNITID, UNITNAME, UNITCODE, GENFUELTYPE, NAMEPLATEMW, BUSNAME,
               CPNODEID, ISONODEID, TRANSMISSIONZONE, ZONE, RESOURCE_TYPE, NOTES
        FROM AWDEV.DBO.GENUNIT
        WHERE ISOMARKETID = {config.ISO_MARKET_ID}
        """,
    )
    sf.validate_columns(df, ["GENUNITID", "UNITNAME", "BUSNAME"], "GENUNIT")
    return df
