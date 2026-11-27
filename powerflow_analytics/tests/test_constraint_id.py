from pathlib import Path

import pandas as pd
import pytest

from pfa.analysis import constraints
from pfa.constraint_id import ConstraintId, constraint_key, resolve

STEP1 = Path(__file__).resolve().parents[1] / "output/_baseline_20261126/fresh/study_14412/step1_screen.csv"

REAL_KEYS = [
    "44000-44500-99@SOBWA2P5", "8397-8398-1@DPROPOM5", "7345-7346-1@DSALGA58", "283-1653-1@SCMNCPS5",
    "6309-61015-1@SCISPUT8", "8399-8398-1@DPRNPOM5", "8458-8515-1@SN_SLON5", "8260-8267-1@SBRAPIN8",
    "1695-11699-1@DVLSPAC5", "126-3636-1@DFRYSK8", "6477-6527-1@SCARLVO8", "5133-5371-1@DELMMAR5",
    "8033-8347-1@MKNGSTE5", "42111-43300-26@SRICBFP8", "1436-2081-1@DWCSRAM5", "8314-8315-2@MKNGSTE5",
]
ODD_KEYS = [  # CTG labels with '-', spaces, parentheses seen in other studies' caches
    "100-200-1@D_POSSUMTROT-RATTLESNAKE_STJOHNS5",
    "100-200-3@BELL COUNTY EAST - BADGER & VOSS LAKE_5 (DOUBLE B TO B )",
    "100-200-99@D_WOLF-REITER_METEOR-WOLF",
]


@pytest.mark.parametrize("key", REAL_KEYS + ODD_KEYS)
def test_round_trip(key):
    cid = ConstraintId.parse(key)
    assert str(cid) == key
    assert ConstraintId.parse(str(cid)) == cid


def test_fields_and_line_key():
    cid = ConstraintId.parse("1436-2081-1@DWCSRAM5")
    assert (cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel) == (1436, 2081, "1", "DWCSRAM5")
    assert cid.line_key == "1436-2081-1"
    with pytest.raises(AttributeError):
        cid.ckt = "2"


def test_ctg_with_dash_and_at():
    cid = ConstraintId.parse("1-2-3@A-B@C")
    assert (cid.ckt, cid.ctglabel) == ("3", "A-B@C")
    assert str(cid) == "1-2-3@A-B@C"


def test_no_stripping():
    cid = ConstraintId.parse("1-2-1 @ X ")
    assert (cid.ckt, cid.ctglabel) == ("1 ", " X ")
    assert str(cid) == "1-2-1 @ X "


@pytest.mark.parametrize("bad", ["", "garbage", "1-2@X", "1-2-3", "a-2-1@X", "1-b-1@X", "-2-1@X"])
def test_malformed(bad):
    with pytest.raises(ValueError):
        ConstraintId.parse(bad)


@pytest.mark.skipif(not STEP1.exists(), reason="baseline step1_screen.csv not present")
def test_round_trip_every_14412_key():
    keys = pd.read_csv(STEP1)["C"].drop_duplicates().tolist()
    assert len(keys) > 100
    for k in keys:
        assert str(ConstraintId.parse(k)) == k


def test_dataframe_key_matches_old_function():
    df = pd.DataFrame({"FROMNUM": [1436, 8397.0], "TONUM": [2081, 8398.0],
                       "CKT": ["1 ", "A"], "CTGLABEL": [" DWCSRAM5", "X-Y Z"]})
    old = (df["FROMNUM"].astype(int).astype(str) + "-" + df["TONUM"].astype(int).astype(str)
           + "-" + df["CKT"].astype(str).str.strip() + "@" + df["CTGLABEL"].astype(str).str.strip())
    assert constraint_key(df).tolist() == old.tolist() == ["1436-2081-1@DWCSRAM5", "8397-8398-A@X-Y Z"]
    assert constraints.constraint_key is constraint_key
    assert [str(ConstraintId.parse(k)) for k in constraint_key(df)] == old.tolist()


class _Cache:
    def __init__(self, tables):
        self.tables = tables

    def load(self, table, columns=None):
        df = self.tables[table]
        return df[columns] if columns else df


def _cache():
    branch = pd.DataFrame({"FROMNUM": [10, 10, 30], "TONUM": [20, 20, 40], "CKT": ["1", "2", "1"],
                           "LABEL": ["LINE_A", "LINE_A", "LINE_B"]})
    ov = pd.DataFrame({"FROMNUM": [10] * 5, "TONUM": [20] * 5, "CKT": ["1"] * 5,
                       "CTGLABEL": ["C1", "C2", "C2", "C3", "C2"],
                       "LIMVIOLPCT": [100.0, 99.9, 100.0, 50.0, 99.6]})
    return _Cache({"outbranch2": branch, "outctgviol2": ov})


def test_resolve_full_key_passthrough():
    assert resolve(_cache(), "10-20-1@C1") == ConstraintId(10, 20, "1", "C1")


def test_resolve_label_picks_dominant_binding_ctg():
    assert resolve(_cache(), "LINE_A") == ConstraintId(10, 20, "1", "C2")


def test_resolve_label_errors():
    with pytest.raises(ValueError, match="not found"):
        resolve(_cache(), "NOPE")
    with pytest.raises(ValueError, match="no binding"):
        resolve(_cache(), "LINE_B")


def test_resolve_strips_label_and_ckt_on_both_sides():
    branch = pd.DataFrame({"FROMNUM": [10], "TONUM": [20], "CKT": ["1 "], "LABEL": ["LINE_A  "]})
    ov = pd.DataFrame({"FROMNUM": [10], "TONUM": [20], "CKT": ["1"], "CTGLABEL": ["C1"], "LIMVIOLPCT": [100.0]})
    got = resolve(_Cache({"outbranch2": branch, "outctgviol2": ov}), " LINE_A")
    assert got == ConstraintId(10, 20, "1", "C1")
