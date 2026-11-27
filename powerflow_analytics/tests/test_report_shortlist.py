import pandas as pd

from pfa.analysis import shortlist_value as sv
from pfa.analysis.screening import Thresholds
from pfa.report import shortlist as sr

CUT, MON = "2026-09-15", "2026-09"
RENT, RENT_EX = sv.rent_col_name(CUT), sv.rent_ex_penalty_col_name(CUT)


def _row(label, value, edge, rent, status="ok", low=False, basis="ticket", pbind=0.3):
    base = {"Label": label, "From bus": 1, "From name": "A", "To bus": 2, "To name": "B", "Ckt": "1", "Contingency": "X",
            "Direction": 1, "Impact share": 1.4, "Pre binds": 0, "Post binds": 5, "Post days (of 5)": 3, "lam avg": 1.0,
            "lam p50": 1.0, "lam p50 gate": 1.0, "Dispatch nodes": 4, RENT: rent, RENT_EX: rent / 2, "Ticket": "", "Status": "",
            "Flip exempt": False, "Thin intensity": False, "Sibling/corridor note": "", "Co-binding": "", "Outage days in Sept": 7,
            "Outage-day basis": basis, "Sampled days in month": 5, "coverage": "0.5", "thin window evidence": "",
            "P(bind) Sept on-peak": pbind, "P(bind) on-peak hours": 1200, "P(bind) years": "2022, 2024", "Low P(bind)": low,
            "E[lambda|bind]": 10.0, "lambda P50": 9.0, "lambda P90": 20.0, "unpriced deep hours %": 0.0,
            "Sept value $/MWh/SF": value, "Sept value LOW $/MWh/SF": value, "Sept value HIGH $/MWh/SF": value,
            "Path": "S->K $1.00", "Path price $/MWh": 1.0, "Path SF value": 0.3, "Path SF approximate": True,
            "Edge $": edge, "Edge LOW $": edge, "Edge HIGH $": edge, "status": status, "Post days sampled": 5,
            "P(bind) negative-headroom hours": 150, "Low evidence": False, "Edge sign ambiguous": False, "curve steps": 5,
            "start-required curve MW": 0.0, "start-required share of curve": 0.0, "start-required > 25%": False,
            "relief units mapped via CPNODE id": 4, "relief units mapped via name": 2, "LP price above structural range": False}
    return base


def _rows():
    return pd.DataFrame([
        _row("LOW_EDGE", 2.0, 0.5, 100),
        _row("HI_EDGE", 3.0, 2.5, 50),
        _row("ZERO", 0.0, -1.0, 900, status="priced at 0: cheapest step is free relief"),
        _row("NOPRICE", None, None, 800, status="no units on the up side (1 up)", low=True, basis="sampled bind days (no ticket)", pbind=0.001),
    ])


def test_split_rows_valued_by_edge_not_valued_by_rent():
    valued, nv = sr.split_rows(_rows(), MON, CUT)
    assert list(valued["Label"]) == ["HI_EDGE", "LOW_EDGE"]
    assert list(nv["Label"]) == ["ZERO", "NOPRICE"]


def test_render_has_two_tables_banner_flags_headers_and_scroll():
    page = sr.render(_rows(), 14412, CUT, MON, Thresholds())
    assert page.count('<table class="t"') == 3  # legend + valued + not valued
    assert "not vetted targets" in page and "A – not valued" in page and "Reason not valued" in page
    assert "Outage flow change / |preflow|</th>" in page and ">Impact share<" not in page
    assert "Post days (of 5)" in page
    assert "LP λ avg" in page and "offer λ mean" in page and "($/MWh per MW of path)" in page
    assert "Sampled bind days in Sept (no ticket; proxy)" in page and "Ticket outage days in Sept" in page
    assert page.count("overflow-x:auto") == 2 and 'class="lowp"' in page and "LOW P(bind)" in page
    assert "Rent post-9/15 ex-penalty" in page and "2022, 2024" in page and "RatE = rated" in page
    # the Not valued table starts with the reason column
    nv_html = page[page.index("Not valued ("):]
    assert nv_html.index("Reason not valued") < nv_html.index(">Label<")


def test_proxy_rows_show_sampled_days_not_outage_days():
    page = sr.render(_rows().iloc[[3]], 1, CUT, MON, Thresholds())
    cols = sr.columns(RENT, RENT_EX, "Sept", 5)
    row = _rows().iloc[3].to_dict()
    vals = {c.header: c.value(row) for c in cols}
    assert vals["Ticket outage days in Sept"] is None and vals["Sampled bind days in Sept (no ticket; proxy)"] == 7
    assert "A target" not in page.split("Not valued")[1].split("<tbody>")[1]


def test_not_valued_sorted_by_rent_excluding_penalty_rows():
    rows = _rows()
    rows.loc[rows["Label"] == "ZERO", RENT_EX] = 1.0  # big total rent, but nearly all of it penalty-tier
    _, nv = sr.split_rows(rows, MON, CUT)
    assert list(nv["Label"]) == ["NOPRICE", "ZERO"]


def test_new_flags_columns_and_legend_notes_are_rendered():
    rows = _rows()
    rows.loc[0, ["Low evidence", "Edge sign ambiguous", "start-required > 25%", "LP price above structural range"]] = True
    rows.loc[0, ["P(bind) negative-headroom hours", "start-required share of curve"]] = [9, 0.4]
    page = sr.render(rows, 14412, CUT, MON, Thresholds())
    assert "LOW EVIDENCE (9 h)" in page and "EDGE SIGN AMBIGUOUS" in page and "START-REQUIRED 40% OF CURVE" in page
    assert page.count("LP price above structural range — likely relaxation price") >= 2  # the row flag and the legend entry
    assert "Relief units mapped via CPNODE id" in page and "falling back to the SCED-name key" in page and "27.9 / +6.43" in page
    assert "valued at the AVERAGE of the priced hours" in page and "parallel element of" in page and "LARGER" in page


def test_thin_evidence_rows_move_to_their_own_table_between_valued_and_not_valued():
    rows = _rows()
    rows.loc[rows["Label"] == "LOW_EDGE", ["Low evidence", "P(bind) negative-headroom hours"]] = [True, 9]
    valued, thin = sr.split_thin(sr.split_rows(rows, MON, CUT)[0])
    assert list(valued["Label"]) == ["HI_EDGE"] and list(thin["Label"]) == ["LOW_EDGE"]
    page = sr.render(rows, 14412, CUT, MON, Thresholds())
    i_v, i_t, i_n = page.index("Valued (1)"), page.index("Valued on thin evidence (1)"), page.index("Not valued (")
    assert i_v < i_t < i_n and "rest on very few hours" in page
    assert page.count('<table class="t"') == 4
    low_p = _rows()
    low_p.loc[low_p["Label"] == "HI_EDGE", "Low P(bind)"] = True
    assert list(sr.split_thin(sr.split_rows(low_p, MON, CUT)[0])[1]["Label"]) == ["HI_EDGE"]
    assert "Valued on thin evidence" not in sr.render(_rows(), 14412, CUT, MON, Thresholds())


def test_page_header_summary_precedes_tables_and_legend_follows():
    page = sr.render(_rows(), 14412, CUT, MON, Thresholds())
    head = page[page.index("How to read this page"):page.index("Valued (")]
    assert head.count("<li>") == 5 and "even value HIGH is a floor if the constraint is enforced" in head
    assert page.index("Column legend") > page.index("Not valued (")


def test_co_binding_is_a_separate_low_emphasis_column():
    rows = _rows()
    rows["Co-binding"] = ["", "co-binds with 3-4-1@B (23 of 23; other binds 54 runs)", "", ""]
    page = sr.render(rows, 14412, CUT, MON, Thresholds())
    assert "Co-binding</th>" in page and 'class="l cobind"' in page and "co-binds with 3-4-1@B" in page
