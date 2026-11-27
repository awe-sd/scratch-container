"""Shortlist page: a Valued table and a Not-valued table, one column spec drives header, filter row, body and alignment."""
from __future__ import annotations

import pandas as pd

from pfa import periods
from pfa.analysis.screening import PENALTY_TIERS, Thresholds
from pfa.analysis.shadow_price import MAX_SF, MIN_SF
from pfa.analysis.shortlist_value import (LOW_EVIDENCE_HOURS, LOW_PBIND, RELAXATION_LABEL, RELAXATION_LP_P50,
                                          START_REQUIRED_SHARE_FLAG, rent_col_name, rent_ex_penalty_col_name)
from pfa.report import html

NOT_VALUED_CLASS = "A – not valued"
EXTRA_CSS = (".lowp td{background:#fdecea}.legend table.t td{white-space:normal;text-align:left;min-width:12rem}"
             ".legend table.t th{position:static}")


def columns(rent_col: str, rent_ex_col: str, label: str, n_post, not_valued: bool = False) -> list[html.Col]:
    lbl = label
    days_key = f"Outage days in {lbl}"
    cols = []
    if not_valued:
        cols.append(html.Col("Reason not valued", "status", "text", "l"))
    cols += [
        html.Col("Class", lambda r: NOT_VALUED_CLASS if not_valued else "A target", "text", "l"),
        html.Col("Low P(bind)", lambda r: "LOW P(bind)" if r.get("Low P(bind)") else "", "text", "l"),
        html.Col("Low evidence", lambda r: f"LOW EVIDENCE ({int(r['P(bind) negative-headroom hours'])} h)" if r.get("Low evidence") is True else "", "text", "l"),
        html.Col("Edge sign", lambda r: "EDGE SIGN AMBIGUOUS" if r.get("Edge sign ambiguous") is True else "", "text", "l"),
        html.Col("Start-required relief", lambda r: f"START-REQUIRED {100 * r['start-required share of curve']:.0f}% OF CURVE" if r.get("start-required > 25%") is True else "", "text", "l"),
        html.Col("LP price flag", lambda r: RELAXATION_LABEL if r.get("LP price above structural range") is True else "", "text", "l"),
        html.Col("Label", "Label", "text", "l"),
        html.Col("From bus", "From bus", "id"),
        html.Col("From name", "From name", "text", "l"),
        html.Col("To bus", "To bus", "id"),
        html.Col("To name", "To name", "text", "l"),
        html.Col("Ckt", "Ckt", "text", "l"),
        html.Col("Contingency", "Contingency", "text", "l"),
        html.Col("Direction", "Direction", "id"),
        html.Col("Outage flow change / |preflow|", "Impact share", "num2"),
        html.Col("Pre binds", "Pre binds", "int"),
        html.Col("Post binds", "Post binds", "int"),
        html.Col(f"Post days (of {n_post})", "Post days (of 5)", "int"),
        html.Col("LP λ avg, all rows ($/MWh)", "lam avg", "num1"),
        html.Col("LP λ P50, all rows ($/MWh)", "lam p50", "num1"),
        html.Col("LP λ P50, post-cutoff ex-cap non-zero ($/MWh; gate basis)", "lam p50 gate", "num1"),
        html.Col("Dispatch nodes", "Dispatch nodes", "int"),
        html.Col(f"{rent_col[:-4]} total LP rent over sampled runs ($)", rent_col, "money"),
        html.Col(f"{rent_ex_col[:-4]} ($)", rent_ex_col, "money"),
        html.Col("Ticket", "Ticket", "text", "l"),
        html.Col("Ticket state", "Status", "text", "l"),
        html.Col("Flip exempt", "Flip exempt", "bool", "l"),
        html.Col("Thin intensity", "Thin intensity", "bool", "l"),
        html.Col("Sibling / corridor note", "Sibling/corridor note", "text", "l"),
        html.Col(f"Ticket outage days in {lbl}", lambda r: r.get(days_key) if str(r.get("Outage-day basis", "")).startswith("ticket") else None, "int"),
        html.Col(f"Sampled bind days in {lbl} (no ticket; proxy)", lambda r: None if str(r.get("Outage-day basis", "")).startswith("ticket") else r.get(days_key), "int"),
        html.Col("Sampled days in month", "Sampled days in month", "int"),
        html.Col("Coverage", "coverage", "text"),
        html.Col("Thin window", "thin window evidence", "text", "l"),
        html.Col(f"P(bind) {lbl} on-peak, pooled history", f"P(bind) {lbl} on-peak", "num3"),
        html.Col("P(bind) basis (on-peak hours; years)",
                 lambda r: "" if pd.isna(r.get("P(bind) on-peak hours")) else f"{int(r['P(bind) on-peak hours']):,} h; {r.get('P(bind) years')}", "text", "l"),
        html.Col("Negative-headroom hours behind P(bind)", "P(bind) negative-headroom hours", "int"),
        html.Col("offer λ mean | bind ($/MWh of flow)", "E[lambda|bind]", "num1"),
        html.Col("offer λ P50 ($/MWh of flow)", "lambda P50", "num1"),
        html.Col("offer λ P90 ($/MWh of flow)", "lambda P90", "num1"),
        html.Col("Unpriced deep hours %", "unpriced deep hours %", "num1"),
        html.Col(f"{lbl} value ($/MWh per unit SF)", f"{lbl} value $/MWh/SF", "num3"),
        html.Col("value LOW (unpriced at $0)", f"{lbl} value LOW $/MWh/SF", "num3"),
        html.Col("value HIGH (unpriced at last step; blank when it is $0)", f"{lbl} value HIGH $/MWh/SF", "num3"),
        html.Col("Curve steps", "curve steps", "int"),
        html.Col("Start-required curve flow MW", "start-required curve MW", "num1"),
        html.Col("Start-required share of curve MW", "start-required share of curve", "num2"),
        html.Col("Relief units mapped via CPNODE id", "relief units mapped via CPNODE id", "int"),
        html.Col("Relief units mapped via name", "relief units mapped via name", "int"),
        html.Col("Path", "Path", "text", "l"),
        html.Col("Path option price ($/MWh, on-peak)", "Path price $/MWh", "num2"),
        html.Col("Path SF", "Path SF value", "num3"),
        html.Col("Path SF approximate", "Path SF approximate", "bool", "l"),
        html.Col("Edge ($/MWh per MW of path)", "Edge $", "num2"),
        html.Col("Edge LOW", "Edge LOW $", "num2"),
        html.Col("Edge HIGH", "Edge HIGH $", "num2"),
    ]
    if not not_valued:
        cols.append(html.Col("Valuation status", "status", "text", "l"))
    return cols


def split_rows(rows: pd.DataFrame, month: str, cutoff: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(valued, not valued): valued = non-zero month value, sorted by edge descending (no path last);
    not valued = everything else, sorted by post-cutoff rent excluding penalty-tier rows, descending."""
    label = periods.month_label(month)
    v = pd.to_numeric(rows[f"{label} value $/MWh/SF"], errors="coerce")
    ok = v.notna() & (v != 0)
    valued = rows[ok].assign(_e=pd.to_numeric(rows.loc[ok, "Edge $"], errors="coerce")).sort_values("_e", ascending=False, na_position="last").drop(columns="_e")
    return valued, rows[~ok].sort_values(rent_ex_penalty_col_name(cutoff), ascending=False)


def legend(label: str, th: Thresholds) -> str:
    items = [
        ("Outage flow change / |preflow|", "Direction-signed mean flow change from the top outage group divided by |mean pre-outage flow| (CSV: Impact share). Not a share: above 1 means the outage adds more flow than the line carried before."),
        ("Post days (of N)", "Distinct sampled post-cutoff study days on which the constraint binds; N = sampled post-cutoff days in the study."),
        ("LP λ ...", "Study LP shadow price (OUTCONSTRAINT2 OPFCNLAMBDA), $/MWh of flow on the constraint. 'all rows' includes penalty-tier rows; the gate basis is post-cutoff, non-zero, ex-penalty rows."),
        ("Dispatch nodes", f"Count of live non-LZ_/WZ_ settlement nodes with {MIN_SF} <= |SF| <= {MAX_SF} shift factor; a node count, not a count of generating units."),
        ("Rent", f"Total LP rent (λ x limit MW) summed over the sampled study runs after the cutoff. Not a monthly figure. The ex-penalty column drops LP rows priced exactly at the penalty tiers {PENALTY_TIERS[0]:.0f} / {PENALTY_TIERS[1]:.0f}."),
        (f"Ticket outage days in {label}", "Business days (ex NERC holidays) of the driver ticket inside the month; rows without a ticket leave this blank."),
        (f"Sampled bind days in {label} (no ticket; proxy)", "Rows without a ticket: sampled post-cutoff in-month study days on which the constraint binds, out of 'Sampled days in month'. Not outage days."),
        ("Coverage", "Ticket: outage business days / on-peak business days of the month. No ticket: sampled bind days / sampled days (marked days-proxy). Blank when the ticket is rejected or cancelled."),
        (f"P(bind) {label} on-peak", "Share of pooled fast-scan history hours (weekday HE7-22 ex-holidays, all years available) with negative headroom; the basis column gives the hour count and years."),
        ("offer λ ...", "Shadow price implied by DAM offer stacks (P60 offers, latest 14 days of the disclosure) priced at the fast-scan negative-headroom depth, $/MWh of flow. Mean is over priced hours only."),
        (f"{label} value", f"P(bind) x offer-λ mean x coverage, $/MWh per unit of shift factor. The headline value assumes unpriced deep hours (hours needing more relief than the curve can supply) are valued at the AVERAGE of the priced hours, although they need more relief than the curve can supply, so the headline sits near LOW whenever the last step is far above the priced average (e.g. 1436-2081-1@DWCSRAM5). LOW counts those hours at $0; HIGH prices them at the curve's last step and is left blank when that last step is $0 (a $0 last step is not a ceiling)."),
        ("Valuation status", "'relief set covers N% of binding hours (K curve steps)' appears when the curve has 2 or fewer steps or more than 50% of binding hours are deeper than the curve (N = 100 - unpriced %); such rows are NOT 'priced at 0' and their HIGH is blank when the last step is $0. 'priced at 0: cheapest step is free relief' is reserved for rows whose binding hours sit essentially inside a curve of more than 2 steps."),
        ("Negative-headroom hours", f"Number of pooled on-peak fast-scan hours with negative headroom behind P(bind). Rows resting on fewer than {LOW_EVIDENCE_HOURS} such hours are flagged LOW EVIDENCE."),
        ("Edge sign", "EDGE SIGN AMBIGUOUS = Edge LOW is negative and Edge HIGH is positive: the sign of the edge depends on how the unpriced deep hours are valued."),
        ("Start-required relief", f"Share of the depth curve's flow MW whose up unit was not committed in DAM (relief needs a start). Flagged when above {START_REQUIRED_SHARE_FLAG:.0%}. Not re-priced."),
        ("Relief units mapped via CPNODE id / via name", "Units are matched to DAM offers by GENUNIT.CPNODEID, falling back to the SCED-name key when the ID key has no offer rows (combined-cycle plants are keyed on a plant node). The value depends on this mapping: for 1436-2081-1@DWCSRAM5 an ID-only mapping gives 27.9 / +6.43 because it loses those plants."),
        ("LP price flag", f"{RELAXATION_LABEL}: LP shadow-price P50 (ex-cap, post-cutoff non-zero) above {RELAXATION_LP_P50:.0f} $/MWh while the all-rows P50 is not exactly a penalty tier."),
        ("Edge", "Value x path shift factor - path option price: $/MWh per MW of path. LOW / HIGH use the LOW / HIGH values. Path SF approximate = the path tool's AVG_SF was used because source/sink node shift factors were unavailable."),
        ("Sibling / corridor note", "parallel element of = identical run set under the same contingency on a different element; sibling contingency of = same element, different contingency, identical run set (both: one flowgate, do not add rents); corridor with = a different line whose runs overlap at least 80% of the SMALLER of the two run sets (n/m runs)."),
        ("Low P(bind)", f"On-peak P(bind) at or below {LOW_PBIND}; the row is shaded."),
        ("Ticket states", "Apprv = approved; RatE = rated, awaiting approval (inferred from the rated -> approved lifecycle); Rejct = rejected. A rejected / cancelled driver ticket gives no coverage (status 'driver ticket <state>')."),
    ]
    df = pd.DataFrame(items, columns=["Column", "Meaning"])
    return '<div class="legend">' + html.table(df, [html.Col("Column", "Column", "text", "l"), html.Col("Meaning", "Meaning", "text", "l")],
                                               filter_row=False, sortable=False) + "</div>"


def render(rows: pd.DataFrame, study: int, cutoff: str, month: str, th: Thresholds) -> str:
    label = periods.month_label(month)
    rent_col, rent_ex_col = rent_col_name(cutoff), rent_ex_penalty_col_name(cutoff)
    n_post = int(rows["Post days sampled"].dropna().iloc[0]) if "Post days sampled" in rows and rows["Post days sampled"].notna().any() else "N"
    intro = html.note(
        f"Step-1 screen output after gates (impact share &ge; {th.share_min} direction-corrected, &ge;{th.post_days_min} of {n_post} sampled "
        f"post-cutoff days, rent &ge; ${th.rent_min:,}, &ge;{th.nqual_min} dispatch nodes), then a soft binding-intensity band on "
        f"post_binds &times; &lambda;P50(ex-cap, post-cutoff, non-zero, non-penalty): hard floor {th.intensity_min_hard}, full pass "
        f"{th.intensity_min_full}. Rows in the soft band are kept and flagged <b>Thin intensity</b>; rows below the hard floor are "
        f"kept only if rescued by the flip-detection heuristic (<b>Flip exempt</b>). C no-dispatch (see step1_screen.csv) uses a "
        f"penalty-share test (&gt;{th.penalty_share_max*100:.0f}% of LP rows at the {PENALTY_TIERS[0]:.0f}/{PENALTY_TIERS[1]:.0f} "
        f"SCOPF penalty cap) plus the legacy flatness test. Direction = OUTBRANCHDIRECTION. Filters accept text or &gt;/&lt; on "
        f"numbers.")
    valued, not_valued = split_rows(rows, month, cutoff)
    lowp = lambda r: "lowp" if (r.get("Low P(bind)") or r.get("Low evidence") is True) else ""
    body = [intro, html.section("Column legend", legend(label, th), level=2),
            html.section(f"Valued ({len(valued)}): non-zero {label} value, sorted by edge",
                         html.scroll(html.table(valued, columns(rent_col, rent_ex_col, label, n_post), row_class=lowp)))]
    body.append(html.section(
        f"Not valued ({len(not_valued)}): sorted by post-cutoff rent excluding penalty-tier rows",
        html.warning("These constraints passed the screen but could not be priced (or priced at exactly zero). They are <b>not vetted targets</b>: "
                     "the rent shown is study LP rent, not a priced opportunity. The reason column says which step failed."),
        html.scroll(html.table(not_valued, columns(rent_col, rent_ex_col, label, n_post, not_valued=True), row_class=lowp))))
    return html.page(f"Stage-2 candidates — study {study}, {len(rows)} constraints", "\n".join(body), extra_css=EXTRA_CSS)


def console_screen(res) -> str:
    """Funnel counts and flip pairs printed after screening."""
    fl = res.flips
    return "\n".join([
        f"FUNNEL: {res.universe['class'].value_counts().to_dict()} | universe: {len(res.universe)}", "",
        "=== FLIP PAIRS (baseline fades -> new binder emerges, shared bus) ===",
        fl.head(15).to_string(index=False) if not fl.empty else "(none)"])


def console_shortlist(gated: pd.DataFrame, dropped: pd.DataFrame) -> str:
    show = ["FROMNAME", "TONAME", "share", "pre_binds", "post_binds", "post_days", "lam_p50_gate",
            "intensity", "NQUAL", "RENT_POST", "flip_exempt", "thin_intensity", "DRIVER_TICKET", "DRIVER_TICKET_STATUS"]
    return "\n".join([
        f"STAGE-2 LIST — {len(gated)} constraints", gated[show].round(2).to_string(), "",
        "=== rows dropped by the hard intensity floor ===",
        dropped[["FROMNAME", "TONAME", "post_binds", "lam_p50_gate", "intensity"]].round(2).to_string() if not dropped.empty else "(none)"])


def console_valuation_summary(summary: dict) -> str:
    """Counts after the valuation step: rows, priced, per unpriced reason, failed lookups with their messages."""
    lines = [f"VALUATION: {summary['n_rows']} rows, {summary['n_priced']} priced, "
             f"{summary['n_rows'] - summary['n_priced'] - sum(summary['failed'].values())} unpriced by a data reason, "
             f"{sum(summary['failed'].values())} failed"]
    lines += [f"  {n:>3} x {reason}" for reason, n in summary["reasons"].items()]
    if summary["failed"]:
        lines.append("  FAILED lookups (each row kept the columns computed before the error):")
        lines += [f"  {n:>3} x {msg}" for msg, n in summary["failed"].items()]
    return "\n".join(lines)
