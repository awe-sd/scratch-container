import pandas as pd

from pfa.report import html


def test_cells_and_headers_are_escaped():
    df = pd.DataFrame({"a": ['x<b>&"y"', "ok"]})
    out = html.table(df, [html.Col("h<1>&", "a", "text", "l")])
    assert "x&lt;b&gt;&amp;&quot;y&quot;" in out and "<b>" not in out
    assert "<th class=\"s l\"" in out and "h&lt;1&gt;&amp;" in out


def test_number_formats():
    assert html.fmt(1234567.4, "int") == "1,234,567"
    assert html.fmt(1.25, "num1") == "1.2" and html.fmt(1.256, "num2") == "1.26" and html.fmt(0.12345, "num3") == "0.123"
    assert html.fmt(1234.5, "money") == "1,234" and html.fmt(1234.6, "money") == "1,235"
    assert html.fmt(5915, "id") == "5915" and html.fmt(True, "bool") == "True"
    assert html.fmt(None, "num2") == "" and html.fmt(float("nan"), "int") == ""
    assert html.fmt(0.123456, "auto") == "0.1235" and html.fmt(float("nan"), "auto") == "NaN" and html.fmt(7, "auto") == "7"


def test_empty_table_renders_a_note_not_a_table():
    out = html.table(pd.DataFrame({"a": []}), [html.Col("a", "a")], empty="no rows")
    assert "<table" not in out and "no rows" in out


def test_filter_row_has_one_input_per_column_and_can_be_dropped():
    df = pd.DataFrame({"a": [1], "b": [2]})
    cols = [html.Col("a", "a", "int"), html.Col("b", "b", "int")]
    assert html.table(df, cols).count("<input") == 2
    assert "<input" not in html.table(df, cols, filter_row=False)


def test_accessor_columns_and_row_class():
    df = pd.DataFrame({"a": [1, 2]})
    out = html.table(df, [html.Col("double", lambda r: r["a"] * 2, "int")], row_class=lambda r: "hi" if r["a"] == 2 else "")
    assert "<td>4</td>" in out and out.count('class="hi"') == 1


def test_page_shell_and_figure():
    import plotly.graph_objects as go
    p = html.page("T <x>", html.section("S", html.note("n"), html.warning("w")), generated="2026-01-01 00:00")
    assert "<title>T &lt;x&gt;</title>" in p and "Generated 2026-01-01 00:00" in p and 'class="warning"' in p
    assert "Plotly.newPlot" in html.figure(go.Figure(go.Scatter(x=[1], y=[2])), plotlyjs="cdn")
