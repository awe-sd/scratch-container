"""Database-free tests for proc_extraction against the CURRENT V2 procedure files."""

import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import proc_extraction as pe  # noqa: E402

TARGET = "FLOW_ANALYSIS.FAST_SCAN_RESULTS"
FAST = ("sp_fast_scan_v2.sql", ["TMP_STATION_KV_SHIFTS", "TMP_INJECTION_FLOW", "TMP_BINDING_ROWS"])
VALID = ("validation_spV2.sql",
         ["TMP_VAL_MEMBER_HOURS", "TMP_STATION_KV_SHIFTS", "TMP_INJECTION_FLOW", "TMP_BINDING_ROWS"])
CASES = [FAST, VALID]

ALL_VALUES = {
    "P_CONFIG_ID": 1, "P_INCLUDE_CURTAILMENT": True, "P_ISO_MARKET_ID": 6,
    "v_actual_start": "2026-06-01", "v_actual_end": "2026-06-02",
    "v_psenshiftid": 10, "v_from_num": 1, "v_to_num": 2, "v_ckt": "1", "v_ctg_label": "X",
    "v_ptoid": 3, "v_branch_name": "B", "v_default_rate_b": 100.0, "v_default_rate_b_rt": None,
    "v_study_id": 5, "v_tssid": 6,
}


def extract(fname, stages):
    return pe.extract_readonly_query((HERE / fname).read_text(), stages, TARGET, source=fname)


def top_level_cte_names(query):
    # extractor emits each stage CTE header at column 0; source bodies are indented
    return re.findall(r"^(?:WITH )?(TMP_\w+?)(?:\(.*?\))? AS \($", query, re.M)


@pytest.mark.parametrize("fname,stages", CASES)
def test_all_stages_found_in_order(fname, stages):
    ex = extract(fname, stages)
    assert ex.stages == stages
    names = [n for n in top_level_cte_names(ex.query) if n in stages]
    assert names == stages
    positions = [names.index(s) for s in stages]
    assert positions == sorted(positions)


@pytest.mark.parametrize("fname,stages", CASES)
def test_single_select_no_writes_no_temp_tables(fname, stages):
    q = extract(fname, stages).query
    assert q.upper().startswith("WITH ")
    assert not re.search(r"\b(CREATE|INSERT|DELETE|UPDATE|MERGE|CALL)\b", q, re.I)
    assert "TEMPORARY" not in q.upper()
    assert ";" not in q
    assert "FAST_SCAN_RESULTS EXISTING" not in q.upper()
    for s in stages:   # each stage is a CTE, never created
        assert not re.search(rf"TABLE\s+{s}", q, re.I)


@pytest.mark.parametrize("fname,stages", CASES)
def test_all_parameters_bound(fname, stages):
    ex = extract(fname, stages)
    bound = pe.bind(ex.query, {**ex.declared_defaults, **ALL_VALUES})
    assert not re.search(r"(?<!:):[A-Za-z_]\w*", bound)
    assert "205" in bound   # v_cim_file_id came from the procedure's own DECLARE


def test_unbound_parameter_is_reported():
    ex = extract(*FAST)
    values = {k: v for k, v in ALL_VALUES.items() if k != "v_ptoid"}
    with pytest.raises(pe.UnboundParameter, match="v_ptoid"):
        pe.bind(ex.query, {**ex.declared_defaults, **values})


def test_validation_member_hours_deletes_become_filters():
    q = extract(*VALID).query
    assert "NOT COALESCE((RN > 1), FALSE)" in q
    assert "TS::DATE < :v_actual_start" in q


def test_rt_constraints_sub_proc_extracts_with_no_stages():
    ex = pe.extract_readonly_query(
        (HERE / "sp_load_fast_scan_rt_constraints.sql").read_text(), [],
        "FLOW_ANALYSIS.FAST_SCAN_RT_CONSTRAINTS", source="sp_load_fast_scan_rt_constraints.sql")
    assert ex.query.upper().startswith("WITH SNAPSHOTS AS")
    assert not re.search(r"\b(INSERT|DELETE)\b", ex.query, re.I)


def test_not_replayed_lists_the_rt_constraints_write():
    ex = extract(*FAST)
    assert any("FAST_SCAN_RT_CONSTRAINTS" in s for s in ex.not_replayed)


def test_missing_stage_raises_naming_the_stage():
    text = (HERE / FAST[0]).read_text()
    broken = re.sub(r"CREATE OR REPLACE TEMPORARY TABLE TMP_INJECTION_FLOW AS",
                    "SELECT 1 AS TMP_INJECTION_FLOW_REMOVED;\n    SELECT * FROM (", text, count=1)
    broken = broken.replace("GROUP BY si.\"TIMESTAMP\";", "GROUP BY si.\"TIMESTAMP\");", 1)
    with pytest.raises(pe.StageNotFound, match="TMP_INJECTION_FLOW"):
        pe.extract_readonly_query(broken, FAST[1], TARGET, source="broken.sql")


def test_missing_final_insert_raises():
    text = (HERE / FAST[0]).read_text().replace("INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RESULTS (", "INSERT INTO OTHER.T (")
    with pytest.raises(pe.StageNotFound, match="INSERT INTO FLOW_ANALYSIS.FAST_SCAN_RESULTS"):
        pe.extract_readonly_query(text, FAST[1], TARGET, source="broken.sql")


def test_unexpected_new_stage_order_raises():
    with pytest.raises(pe.ProcExtractionError, match="differ from expected order"):
        extract(FAST[0], list(reversed(FAST[1])))


def _proc(*stmts):
    return "CREATE PROCEDURE P() AS '\nBEGIN;\n" + "\n".join(stmts) + "\nEND;\n';"


STAGE = "CREATE OR REPLACE TEMPORARY TABLE T1 (A INT, B INT);"
FINAL = "INSERT INTO OUT.T (A, B) SELECT A, B FROM T1;"


def test_second_insert_into_a_stage_appends_rows():
    sql = _proc(STAGE, "INSERT INTO T1 SELECT 1, 2;", "INSERT INTO T1 SELECT 3, 4;", FINAL)
    q = pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql").query
    assert q.count("UNION ALL") == 1
    assert "T1__0(A, B) AS" in q and "SELECT 1, 2" in q and "SELECT 3, 4" in q
    assert "SELECT * FROM T1__0\nUNION ALL" in q


def test_update_or_merge_on_a_stage_raises():
    for stmt in ("UPDATE T1 SET A = 0 WHERE B = 2;", "MERGE INTO T1 USING X ON T1.A = X.A WHEN MATCHED THEN DELETE;"):
        sql = _proc(STAGE, "INSERT INTO T1 SELECT 1, 2;", stmt, FINAL)
        with pytest.raises(pe.UnsupportedStageStatement, match="T1"):
            pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql")


def test_insert_with_column_list_maps_onto_declared_stage_columns():
    sql = _proc(STAGE, "INSERT INTO T1 (B) SELECT 2;", FINAL)
    q = pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql").query
    assert "T1(A, B) AS" in q
    assert "SELECT NULL AS A, B FROM (\nSELECT 2\n) AS _ins(B)" in q


def test_insert_with_column_list_appends_after_plain_insert():
    sql = _proc(STAGE, "INSERT INTO T1 SELECT 1, 2;", "INSERT INTO T1 (B, A) SELECT 4, 3;", FINAL)
    q = pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql").query
    assert q.count("UNION ALL") == 1 and "AS _ins(B, A)" in q


def test_insert_with_column_list_into_ctas_stage_raises():
    sql = _proc("CREATE OR REPLACE TEMPORARY TABLE T1 AS SELECT 1 AS A, 2 AS B;", "INSERT INTO T1 (A) SELECT 3;", FINAL)
    with pytest.raises(pe.UnsupportedStageStatement, match="T1"):
        pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql")


def test_insert_with_unknown_column_raises():
    sql = _proc(STAGE, "INSERT INTO T1 (Z) SELECT 1;", FINAL)
    with pytest.raises(pe.ProcExtractionError, match="unknown"):
        pe.extract_readonly_query(sql, ["T1"], "OUT.T", source="tiny.sql")
