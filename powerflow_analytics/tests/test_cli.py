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
