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


def fetch_genunit_sced_name() -> pd.DataFrame:
    """GENUNITID -> SCED resource NAME (AWDEV.DBO.GENUNITSCEDNAME).

    Explored via DESCRIBE/LIMIT 3: columns are GENUNITID, NAME, KIND
    ('GEN'/'ESR'/'LOAD' — a BESS unit gets one row per role), EPOCH
    ('PRE'/'POST'/'BOTH' — SCED naming-convention era the row applies to).
    NAME already carries the trailing per-unit index used by SCED
    (JACKCNTY_CC1_1, _2, _3 for a 3-train combined cycle at one bus) — this
    is the same index OUTGEN2.ID uses, so joining on GENUNITID then matching
    that trailing digit against ID disambiguates multi-unit buses exactly,
    instead of the old BUSNAME-only dedup (which arbitrarily kept one row
    per bus and silently mispriced any unit sharing a bus with siblings).
    No (BUSNUM, ID) -> GENUNITID bridge exists for ERCOT — AWOPF.DBO.OUTGENREF
    is empty for ISOMARKETID=6 (only NaN/8 present) — so GENUNIT.BUSNAME is
    still the entry point; only the disambiguation step changes.
    """
    df = sf.query("AWDEV", "SELECT GENUNITID, NAME, KIND, EPOCH FROM AWDEV.DBO.GENUNITSCEDNAME")
    sf.validate_columns(df, ["GENUNITID", "NAME", "KIND"], "GENUNITSCEDNAME")
    return df
