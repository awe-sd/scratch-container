import importlib

import pytest

from pfa import cli


def _exit_code(argv):
    try:
        return cli.main(argv)
    except SystemExit as e:
        return e.code


def test_top_level_help_lists_commands_in_funnel_order(capsys):
    assert _exit_code(["--help"]) == 0
    out = capsys.readouterr().out
    names = [n for n, _, _ in cli.COMMANDS]
    assert names[:4] == ["summary", "shortlist", "deep-dive", "paths"]
    assert [out.index(f"  {n} ") for n in names] == sorted(out.index(f"  {n} ") for n in names)


@pytest.mark.parametrize("name", [n for n, _, _ in cli.COMMANDS])
def test_subcommand_help_exits_zero(name, capsys):
    assert _exit_code([name, "--help"]) == 0
    assert "usage:" in capsys.readouterr().out


def test_unknown_command_is_an_error(capsys):
    assert _exit_code(["nope"]) == 2


@pytest.mark.parametrize("module", [m for _, m, _ in cli.COMMANDS if m != "headroom"])
def test_script_shims_import_and_point_at_cli(module):
    import runpy
    from pathlib import Path

    shim = Path(__file__).resolve().parents[1] / "scripts" / f"{module}.py"
    ns = runpy.run_path(str(shim), run_name="not_main")
    assert ns["main"] is importlib.import_module(f"pfa.cli.{module}").main


# ---------------------------------------------------------------- exit status --

import sys
import types

import pandas as pd


def test_main_returns_the_subcommand_exit_status(monkeypatch):
    mod = types.ModuleType("pfa.cli.fakecmd")
    mod.main = lambda argv: 3
    monkeypatch.setitem(sys.modules, "pfa.cli.fakecmd", mod)
    monkeypatch.setitem(cli._MODULES, "fakecmd", "fakecmd")
    assert cli.main(["fakecmd"]) == 3
    mod.main = lambda argv: None
    assert cli.main(["fakecmd"]) == 0


def test_shortlist_before_summary_names_the_missing_file_and_command(monkeypatch, tmp_path, capsys):
    from pfa import config
    from pfa.cli import build_stage2_list as cmd

    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    (tmp_path / "study_7").mkdir()
    rc = cmd.main(["--study", "7", "--cutoff", "2026-09-15", "--month", "2026-09"])
    err = capsys.readouterr().err
    assert rc == 2 and "ranked_constraints.csv is missing" in err and "pfa summary --study 7 --cutoff 2026-09-15 --tickets" in err
    assert "Traceback" not in err


def _screening_stub(cmd, monkeypatch, tmp_path):
    from pfa import config
    from pfa.analysis.screening import ScreeningResult, Thresholds

    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    (tmp_path / "study_7").mkdir()
    short = pd.DataFrame({"FROMNAME": ["A"], "TONAME": ["B"], "share": [1.0], "pre_binds": [0], "post_binds": [1], "post_days": [1],
                          "lam_p50_gate": [1.0], "intensity": [1.0], "NQUAL": [3], "RENT_POST": [1.0], "flip_exempt": [False],
                          "thin_intensity": [False], "DRIVER_TICKET": [None], "DRIVER_TICKET_STATUS": [None]},
                         index=["1-2-1@X"])
    res = ScreeningResult(7, "2026-09-15", Thresholds(), pd.Series(dtype=float), short, pd.DataFrame(), short, short.iloc[0:0])
    res.universe = short.assign(**{"class": "A target"})
    res.flips = pd.DataFrame()
    monkeypatch.setattr(cmd, "screen_study", lambda *a, **k: res)
    monkeypatch.setattr(cmd.shortlist_report, "render", lambda *a, **k: "<html></html>")
    monkeypatch.setattr(cmd, "shortlist_rows", lambda *a, **k: pd.DataFrame({"x": [1]}))
    return res


def test_shortlist_exits_nonzero_and_summarises_when_lookups_raise(monkeypatch, tmp_path, capsys):
    from pfa.analysis import shortlist_value as sv
    from pfa.cli import build_stage2_list as cmd

    res = _screening_stub(cmd, monkeypatch, tmp_path)
    monkeypatch.setattr(sv, "StudyCache", _AllCache)
    monkeypatch.setattr(sv.gen_mapping, "fetch_genunit_sced_name", lambda: pd.DataFrame())
    monkeypatch.setattr(sv.marginal_units, "bus_name_map", lambda b: {})
    monkeypatch.setattr(sv.dam_offers, "latest_delivery_date", lambda: pd.Timestamp("2026-09-26").date())
    monkeypatch.setattr(sv, "value_row", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("snowflake down")))
    pd.DataFrame({"CONSTRAINT": ["1-2-1@X"]}).to_csv(tmp_path / "study_7" / "ranked_constraints.csv", index=False)
    monkeypatch.setattr(cmd, "value_shortlist", sv.value_shortlist)
    rc = cmd.main(["--study", "7", "--cutoff", "2026-09-15", "--month", "2026-09"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "VALUATION: 1 rows, 0 priced, 0 unpriced by a data reason, 1 failed" in out and "1 x RuntimeError: snowflake down" in out


class _AllCache:
    def __init__(self, study):
        pass

    def load(self, table, columns=None):
        runs = pd.DataFrame({"RUNID": [1], "SIMDATE": ["2026-09-16"]})
        if table == "opfrun":
            return runs
        if table == "outctgviol2":
            return pd.DataFrame({"RUNID": [1], "FROMNUM": [1], "TONUM": [2], "CKT": ["1"], "CTGLABEL": ["X"], "LIMVIOLPCT": [100.0],
                                 "LIMVIOLLIMIT": [10.0], "BRANCHID": [1]})
        if table == "outconstraint2":
            return pd.DataFrame({"RUNID": [1], "FROMNUM": [1], "TONUM": [2], "CKT": ["1"], "LPOPFCTGID": ["X"], "OPFCNLAMBDA": [5.0]})
        return pd.DataFrame(columns=columns or [])


def test_failed_row_keeps_the_columns_computed_before_the_error(monkeypatch, tmp_path):
    from pfa import config
    from pfa.analysis import shortlist_value as sv
    from pfa.analysis.screening import ScreeningResult, Thresholds

    monkeypatch.setattr(config, "OUTPUT_ROOT", tmp_path)
    (tmp_path / "study_7").mkdir()
    pd.DataFrame({"CONSTRAINT": ["1-2-1@X"]}).to_csv(tmp_path / "study_7" / "ranked_constraints.csv", index=False)
    monkeypatch.setattr(sv, "StudyCache", _AllCache)
    monkeypatch.setattr(sv.gen_mapping, "fetch_genunit_sced_name", lambda: pd.DataFrame())
    monkeypatch.setattr(sv.marginal_units, "bus_name_map", lambda b: {})
    monkeypatch.setattr(sv.dam_offers, "latest_delivery_date", lambda: pd.Timestamp("2026-09-26").date())

    def partial(study, c, *a, out=None, **k):
        out["P(bind) Sept on-peak"] = 0.25
        raise RuntimeError("offers unavailable")

    monkeypatch.setattr(sv, "value_row", partial)
    short = pd.DataFrame({"x": [1]}, index=["1-2-1@X"])
    res = ScreeningResult(7, "2026-09-15", Thresholds(), pd.Series(dtype=float), short, pd.DataFrame(), short, short)
    r = sv.value_shortlist(res, "2026-09").iloc[0]
    assert r["status"] == "lookup failed: RuntimeError: offers unavailable"
    assert r["P(bind) Sept on-peak"] == 0.25 and r["coverage"] == "1.0(days-proxy)" and not r["Low P(bind)"]


def test_value_prints_the_cache_only_mark_first_when_the_database_is_down(monkeypatch, capsys):
    from pfa.analysis import valuation
    from pfa.cli import value_constraint as cmd

    class Cache:
        def __init__(self, study):
            pass

        def load(self, table, columns=None):
            if table == "opfrun":
                return pd.DataFrame({"RUNID": [1, 2], "SIMDATE": ["2026-09-16", "2026-09-17"], "SIMHOUR": [12, 18]})
            return pd.DataFrame({"RUNID": [1], "FROMNUM": [1], "TONUM": [2], "CKT": ["1"], "LPOPFCTGID": ["X"], "OPFCNLAMBDA": [20.0]})

    monkeypatch.setattr(cmd, "StudyCache", Cache)
    monkeypatch.setattr(valuation, "fact_sheet", lambda *a: (_ for _ in ()).throw(RuntimeError("database unavailable")))
    rc = cmd.main(["--study", "7", "--constraint", "1-2-1@X", "--month", "2026-09", "--window", "2026-09-16", "2026-09-17"])
    out = capsys.readouterr().out
    assert rc == 1
    assert out.index("Monthly on-peak mark") < out.index("dollars_per_mwh") < out.index("fact sheet failed: RuntimeError: database unavailable")
