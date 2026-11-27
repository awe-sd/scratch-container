import pandas as pd

from pfa.analysis import dispatch_screen
from pfa.extract import shifts


def test_dispatch_screen_no_coverage_returns_none(monkeypatch):
    monkeypatch.setattr(shifts.sf, "query", lambda *a, **k: pd.DataFrame())
    assert dispatch_screen.dispatch_screen(14411, "1436-2081-1@DWCSRAM5") is None


def test_dispatch_screen_flags_when_no_opposite_sign_pair(monkeypatch):
    """Same-sign-only (or empty) cpnode population: no redispatch pair, so
    the constraint is unenforceable. Covers the STHRSCH8 canary shape: only
    one-sided movers clear the PAIR_MIN_SF..PAIR_MAX_SF band."""
    monkeypatch.setattr(shifts.sf, "query",
                        lambda *a, **k: pd.DataFrame({"N_POS": [1], "N_NEG": [0]}))
    result = dispatch_screen.dispatch_screen(14411, "8186-8913-1@STHRSCH8")
    assert result is not None
    assert "unenforceable" in result


def test_dispatch_screen_passes_when_an_opposite_sign_pair_exists(monkeypatch):
    """Both signs present in the band: a genuine redispatch pair exists, so
    the constraint is not flagged. Covers the DWCSRAM5 canary shape."""
    monkeypatch.setattr(shifts.sf, "query",
                        lambda *a, **k: pd.DataFrame({"N_POS": [3], "N_NEG": [5]}))
    result = dispatch_screen.dispatch_screen(14411, "1436-2081-1@DWCSRAM5")
    assert result is None
