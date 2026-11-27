"""Shift factors: SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW (per settlement/CP node)
and BUS_SHIFTS_VIEW (per PSSE bus). The one module that queries them.

Both are readable by read_only. Rows are keyed (ISOMARKETID, STUDYID, FROMNUM,
TONUM, CKT, CTGLABEL) and hold PSENS on the FROMNUM->TONUM sense, repeated per
topology, so per-constraint readers AVG(PSENS) over topologies. CPNODE rows
carry DEADBUS (0 = live; aggregate LZ_/HB_ nodes carry 4) and NAME; the
constraint-scoped readers exclude LZ_/WZ_ aggregates unless noted.
SHIFT_FACTORS.DBO.DEVICE_SHIFTS has no rows for recent studies; use these views.
"""
from __future__ import annotations


import pandas as pd

from .. import config, sf
from ..constraint_id import ConstraintId

_DB = "SHIFT_FACTORS"
_CPNODE = "SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW"
_BUS = "SHIFT_FACTORS.DBO.BUS_SHIFTS_VIEW"


def _ids(values) -> str:
    return ",".join(str(int(v)) for v in values)


# ---------------------------------------------------------------- bus view --

def bus_sf_for_buses(study_id: int, cid: ConstraintId, busnums: list[int]) -> pd.DataFrame:
    """BUSNUM, SF (AVG PSENS) for the listed buses on one constraint."""
    ids = ",".join(str(int(b)) for b in set(busnums))
    return sf.query(_DB, f"""
        SELECT BUSNUM, AVG(PSENS) SF
        FROM {_BUS}
        WHERE ISOMARKETID={config.ISO_MARKET_ID} AND STUDYID={int(study_id)}
          AND FROMNUM={int(cid.fromnum)} AND TONUM={int(cid.tonum)} AND CKT={sf.quote(cid.ckt)} AND CTGLABEL={sf.quote(cid.ctglabel)}
          AND BUSNUM IN ({ids})
        GROUP BY BUSNUM""")


def bus_sf_all_buses(study_id: int, cid: ConstraintId) -> pd.DataFrame:
    """BUSNUM, NAME, SF (AVG PSENS) for every non-LZ_/WZ_ bus on one constraint."""
    return sf.query(_DB, f"""
        SELECT BUSNUM, NAME, AVG(PSENS) SF
        FROM {_BUS}
        WHERE ISOMARKETID={config.ISO_MARKET_ID} AND STUDYID={int(study_id)}
          AND FROMNUM={int(cid.fromnum)} AND TONUM={int(cid.tonum)} AND CKT={sf.quote(cid.ckt)} AND CTGLABEL={sf.quote(cid.ctglabel)}
          AND LEFT(NAME, 3) NOT IN ('LZ_', 'WZ_')
        GROUP BY BUSNUM, NAME""")


# -------------------------------------------------------------- cpnode view --

def cpnode_sf_by_name(study_id: int, cid: ConstraintId, names: list[str]) -> pd.DataFrame:
    """NAME, SF (AVG PSENS) for the listed node names on one constraint."""
    in_list = ",".join(sf.quote(n) for n in names)
    return sf.query(_DB, f"""
        SELECT NAME, AVG(PSENS) SF
        FROM {_CPNODE}
        WHERE ISOMARKETID={config.ISO_MARKET_ID} AND STUDYID={int(study_id)}
          AND FROMNUM={int(cid.fromnum)} AND TONUM={int(cid.tonum)} AND CKT={sf.quote(cid.ckt)} AND CTGLABEL={sf.quote(cid.ctglabel)}
          AND NAME IN ({in_list})
        GROUP BY NAME""")


def cpnode_psens_by_id(study_id: int, cid: ConstraintId, cpnode_ids: list[int]) -> pd.DataFrame:
    """CPNODEID, PSENS (AVG) for the listed CPNODEIDs on one constraint."""
    return sf.query(
        _DB,
        f"""
            SELECT CPNODEID, AVG(PSENS) AS PSENS
            FROM {_CPNODE}
            WHERE ISOMARKETID = {config.ISO_MARKET_ID} AND STUDYID = {int(study_id)}
              AND FROMNUM = {int(cid.fromnum)} AND TONUM = {int(cid.tonum)}
              AND CKT = {sf.quote(cid.ckt)} AND CTGLABEL = {sf.quote(cid.ctglabel)}
              AND CPNODEID IN ({_ids(cpnode_ids)})
            GROUP BY CPNODEID
            """,
    )


def cpnode_live_nodes(study_id: int, cid: ConstraintId) -> pd.DataFrame:
    """NAME, CPNODEID, PSENS (AVG), N (row count) per live non-LZ_/WZ_ node on one constraint."""
    return sf.query(_DB, f"""
        SELECT NAME, CPNODEID, AVG(PSENS) PSENS, COUNT(*) N
        FROM {_CPNODE}
        WHERE ISOMARKETID={config.ISO_MARKET_ID} AND STUDYID={int(study_id)}
          AND FROMNUM={int(cid.fromnum)} AND TONUM={int(cid.tonum)} AND CKT={sf.quote(cid.ckt)} AND CTGLABEL={sf.quote(cid.ctglabel)}
          AND DEADBUS=0 AND LEFT(NAME,3) NOT IN ('LZ_','WZ_')
        GROUP BY NAME, CPNODEID
    """)


def cpnode_qualifying_count(study_id: int, cid: ConstraintId, min_sf: float, max_sf: float) -> pd.DataFrame:
    """One row, column N: distinct live non-LZ_/WZ_ node names with min_sf <= |PSENS| < max_sf."""
    return sf.query(_DB, f"""
        SELECT COUNT(DISTINCT NAME) N
        FROM {_CPNODE}
        WHERE ISOMARKETID = {config.ISO_MARKET_ID} AND STUDYID = {int(study_id)}
          AND FROMNUM = {int(cid.fromnum)} AND TONUM = {int(cid.tonum)}
          AND CKT = {sf.quote(cid.ckt)} AND CTGLABEL = {sf.quote(cid.ctglabel)}
          AND DEADBUS = 0
          AND LEFT(NAME, 3) NOT IN ('LZ_', 'WZ_')
          AND ABS(PSENS) >= {min_sf} AND ABS(PSENS) < {max_sf}
    """)


def cpnode_pair_counts(study_id: int, cid: ConstraintId, pair_min_sf: float, pair_max_sf: float) -> pd.DataFrame:
    """One row: N_POS, N_NEG = live non-LZ_/WZ_ rows with PSENS>0 / <0 inside the |PSENS| pair band."""
    return sf.query(_DB, f"""
        SELECT
          SUM(CASE WHEN PSENS > 0 THEN 1 ELSE 0 END) AS N_POS,
          SUM(CASE WHEN PSENS < 0 THEN 1 ELSE 0 END) AS N_NEG
        FROM {_CPNODE}
        WHERE ISOMARKETID = {config.ISO_MARKET_ID} AND STUDYID = {int(study_id)}
          AND FROMNUM = {int(cid.fromnum)} AND TONUM = {int(cid.tonum)}
          AND CKT = {sf.quote(cid.ckt)} AND CTGLABEL = {sf.quote(cid.ctglabel)}
          AND DEADBUS = 0
          AND LEFT(NAME, 3) NOT IN ('LZ_', 'WZ_')
          AND ABS(PSENS) >= {pair_min_sf} AND ABS(PSENS) < {pair_max_sf}
    """)


def cpnode_dispatch_features(study_id: int, constraints: list[str], min_sf: float, max_sf: float,
                             pair_min_sf: float, pair_max_sf: float) -> pd.DataFrame:
    """Bulk, one row per constraint that has view rows: FROMNUM, TONUM, CKT, CTGLABEL,
    N_QUAL (distinct nodes in the min/max band), N_POS_PAIR / N_NEG_PAIR (rows in the pair band by sign).
    Empty frame if `constraints` is empty."""
    tuples = []
    for c in constraints:
        cid = ConstraintId.parse(c)
        tuples.append(f"({int(cid.fromnum)}, {int(cid.tonum)}, {sf.quote(cid.ckt)}, {sf.quote(cid.ctglabel)})")
    if not tuples:
        return pd.DataFrame()
    values_sql = ",".join(tuples)
    return sf.query(_DB, f"""
        WITH targets AS (
          SELECT * FROM VALUES {values_sql} AS t(FROMNUM, TONUM, CKT, CTGLABEL)
        )
        SELECT t.FROMNUM, t.TONUM, t.CKT, t.CTGLABEL,
               COUNT(DISTINCT CASE WHEN ABS(v.PSENS) >= {min_sf} AND ABS(v.PSENS) < {max_sf}
                                    THEN v.NAME END) N_QUAL,
               SUM(CASE WHEN v.PSENS >= {pair_min_sf} AND v.PSENS < {pair_max_sf} THEN 1 ELSE 0 END) N_POS_PAIR,
               SUM(CASE WHEN v.PSENS <= -{pair_min_sf} AND v.PSENS > -{pair_max_sf} THEN 1 ELSE 0 END) N_NEG_PAIR
        FROM targets t
        JOIN {_CPNODE} v
          ON v.FROMNUM = t.FROMNUM AND v.TONUM = t.TONUM AND v.CKT = t.CKT AND v.CTGLABEL = t.CTGLABEL
        WHERE v.ISOMARKETID = {config.ISO_MARKET_ID} AND v.STUDYID = {int(study_id)}
          AND v.DEADBUS = 0 AND LEFT(v.NAME, 3) NOT IN ('LZ_', 'WZ_')
        GROUP BY t.FROMNUM, t.TONUM, t.CKT, t.CTGLABEL
    """)


def cpnode_dispatch_nodes(study_id: int, constraints: list[str], sf_min: float, sf_max: float) -> pd.DataFrame:
    """Bulk: FN, TN, KK (CKT), GG (CTGLABEL) as strings, NQUAL (distinct live non-LZ_/WZ_ nodes with
    sf_min <= |PSENS| <= sf_max, inclusive), MAXSF. Constraints with no qualifying rows are absent."""
    tuples = ",".join("('{0.fromnum}','{0.tonum}',{1},{2})".format(cid, sf.quote(cid.ckt), sf.quote(cid.ctglabel))
                       for cid in map(ConstraintId.parse, constraints))
    return sf.query(_DB, f"""
    SELECT FROMNUM::STRING FN, TONUM::STRING TN, TRIM(CKT) KK, TRIM(CTGLABEL) GG,
           COUNT(DISTINCT NAME) NQUAL, MAX(ABS(PSENS)) MAXSF
    FROM {_CPNODE}
    WHERE ISOMARKETID={config.ISO_MARKET_ID} AND STUDYID={study_id} AND DEADBUS=0
      AND NAME NOT LIKE 'LZ_%' AND NAME NOT LIKE 'WZ_%' AND ABS(PSENS) BETWEEN {sf_min} AND {sf_max}
      AND (FROMNUM::STRING, TONUM::STRING, TRIM(CKT), TRIM(CTGLABEL)) IN ({tuples})
    GROUP BY 1,2,3,4""")


# ------------------------------------------------------------ by PSENSHIFTID --

def node_shift_factors(psenshiftid: int) -> pd.DataFrame:
    """Node shift factors (psens) for one psenshiftid, dead buses filtered out."""
    return sf.query(_DB, f"""
        SELECT PSENSHIFTID, TOPOLOGYID, CPNODEID, NAME, PSENS, DIRECTION, DEADBUS, RUNID
        FROM {_CPNODE}
        WHERE PSENSHIFTID = {int(psenshiftid)} AND DEADBUS = 0""")


def node_shift_factors_multi(psenshift_ids: list[int]) -> pd.DataFrame:
    """Node psens for several psenshiftids at once (no DEADBUS filter — aggregate LZ_/HB_ nodes
    carry DEADBUS=4 and must stay). Exact duplicate (PSENSHIFTID, CPNODEID) rows are collapsed."""
    ids = ",".join(str(int(i)) for i in psenshift_ids)
    return sf.query(_DB, f"""
        SELECT PSENSHIFTID, TOPOLOGYID, CPNODEID, PSENS, DEADBUS
        FROM {_CPNODE}
        WHERE PSENSHIFTID IN ({ids})
        QUALIFY ROW_NUMBER() OVER (PARTITION BY PSENSHIFTID, CPNODEID ORDER BY DEADBUS) = 1""")
