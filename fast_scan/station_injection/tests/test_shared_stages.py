"""Drift guard: calculation blocks that are copied between the two V2 procedures must stay equal.

Blocks are located by SQL structure (statement splitter, CTE name + balanced parenthesis) on
comment-stripped text, then compared after normalising indentation, trailing whitespace and
blank lines. See DEPLOY_FAST_SCAN_V2.md, "Shared calculation between the two V2 procedures".
"""
import difflib
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import proc_extraction as pe  # noqa: E402

FAST = "sp_fast_scan_v2.sql"
VALID = "validation_spV2.sql"
MAIN_INSERT = r"INSERT\s+INTO\s+FLOW_ANALYSIS\.FAST_SCAN_RESULTS\s*\("


def _statements(sql_text, source):
    return pe.split_statements(pe.strip_line_comments(pe.procedure_body(sql_text, source)))


def _statement(stmts, pattern, what):
    hits = [s for s in stmts if re.match(pattern, s, re.I)]
    if len(hits) != 1:
        raise AssertionError(f"{what}: expected exactly one statement matching {pattern!r}, found {len(hits)}")
    return hits[0]


def _cte(text, name):
    m = re.search(rf"(?<![\w]){name}\s+AS\s*\(", text)
    if not m:
        raise AssertionError(f"CTE {name} not found")
    return text[m.start(): pe._balanced_paren_end(text, m.end() - 1) + 1]


def _paren_from(text, pattern):
    m = re.search(pattern, text, re.I)
    if not m:
        raise AssertionError(f"{pattern!r} not found")
    return text[m.start(): pe._balanced_paren_end(text, m.end() - 1) + 1]


# name -> function(statements, source) returning the block text
BLOCKS = {
    "StationBusMapping CTE (stage TMP_STATION_KV_SHIFTS)": lambda st: _cte(
        _statement(st, r"CREATE\s+OR\s+REPLACE\s+TEMPORARY\s+TABLE\s+TMP_STATION_KV_SHIFTS\b", "stage 1"),
        "StationBusMapping"),
    "Snapshots CTE (stage TMP_INJECTION_FLOW)": lambda st: _cte(
        _statement(st, r"CREATE\s+OR\s+REPLACE\s+TEMPORARY\s+TABLE\s+TMP_INJECTION_FLOW\b", "stage 2"),
        "Snapshots"),
    "TMP_BINDING_ROWS stage (whole statement)": lambda st: _statement(
        st, r"CREATE\s+OR\s+REPLACE\s+TEMPORARY\s+TABLE\s+TMP_BINDING_ROWS\b", "stage 2b"),
    "main INSERT column list": lambda st: _paren_from(_statement(st, MAIN_INSERT, "main insert"), MAIN_INSERT),
    "DAMLimits CTE": lambda st: _cte(_statement(st, MAIN_INSERT, "main insert"), "DAMLimits"),
    "RTConstraint CTE": lambda st: _cte(_statement(st, MAIN_INSERT, "main insert"), "RTConstraint"),
    "RenewableUnits CTE": lambda st: _cte(_statement(st, MAIN_INSERT, "main insert"), "RenewableUnits"),
    "WHERE NOT EXISTS guard": lambda st: _paren_from(
        _statement(st, MAIN_INSERT, "main insert"), r"WHERE\s+NOT\s+EXISTS\s*\("),
    "RT-constraints refresh DELETE": lambda st: _statement(
        st, r"DELETE\s+FROM\s+FLOW_ANALYSIS\.FAST_SCAN_RT_CONSTRAINTS\b", "RT refresh delete"),
    "RT-constraints refresh INSERT": lambda st: _statement(
        st, r"INSERT\s+INTO\s+FLOW_ANALYSIS\.FAST_SCAN_RT_CONSTRAINTS\b", "RT refresh insert"),
}


def _normalise(text):
    lines = (ln.strip() for ln in text.split("\n"))
    return [ln for ln in lines if ln]


def assert_blocks_match(fast_sql, valid_sql):
    fast_st, valid_st = _statements(fast_sql, FAST), _statements(valid_sql, VALID)
    for name, get in BLOCKS.items():
        a, b = _normalise(get(fast_st)), _normalise(get(valid_st))
        if a != b:
            diff = "\n".join(difflib.unified_diff(a, b, FAST, VALID, lineterm="", n=2))
            raise AssertionError(f"shared block drifted: {name}\n{diff}")


def _read(fname):
    return (HERE.parent / fname).read_text()


def test_shared_blocks_are_identical_in_both_procedures():
    assert_blocks_match(_read(FAST), _read(VALID))


def test_every_block_is_found_in_both_files():
    for sql, src in ((_read(FAST), FAST), (_read(VALID), VALID)):
        st = _statements(sql, src)
        for name, get in BLOCKS.items():
            assert _normalise(get(st)), f"{name} empty in {src}"


@pytest.mark.parametrize("old,new,block", [
    ("PRICETYPEID = 2", "PRICETYPEID = 3", "TMP_BINDING_ROWS"),
    ("RATEB AS DAM_RATE_B", "RATEA AS DAM_RATE_B", "DAMLimits"),
    ("UNIT_CODE != ''NA''", "UNIT_CODE != ''XX''", "RenewableUnits"),
])
def test_altering_one_copy_is_detected(old, new, block):
    fast, valid = _read(FAST), _read(VALID)
    assert old in valid
    altered = valid.replace(old, new, 1)
    with pytest.raises(AssertionError, match=f"shared block drifted: .*{block}") as ei:
        assert_blocks_match(fast, altered)
    assert "@@" in str(ei.value)   # unified diff is shown
