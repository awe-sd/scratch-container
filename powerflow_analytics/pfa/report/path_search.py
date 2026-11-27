"""Path-search pages and READMEs from pfa.analysis.path_search results."""
from __future__ import annotations

import os
import re
import shlex

import pandas as pd
import plotly.graph_objects as go

from pfa import config
from pfa.report import html, markdown


def invocation(args: list[str]) -> str:
    """A runnable command line for `pfa paths` with the arguments as given, shell-quoted (whichever entry point was used)."""
    return " ".join(["uv run pfa paths", *(shlex.quote(a) for a in args)])


def short_name(label: str) -> str:
    return re.sub(r"\d+[A-Z]?$", "", label)


def date_range_text(dates: list[str]) -> str:
    d = sorted(pd.to_datetime(dates))
    a, b = d[0], d[-1]
    if a == b:
        return f"{a:%b} {a.day}"
    return f"{a:%b} {a.day}-{b.day}" if a.month == b.month else f"{a:%b} {a.day}-{b:%b} {b.day}"


def holiday_text(holidays) -> str:
    ds = sorted(pd.Timestamp(x) for x in holidays)
    return ", ".join(f"{d:%b} {d.day}" for d in ds) or "no holidays"


def holiday_sentence(hol: str, hs: dict, n_periods: int, holiday_periods: list, binding: dict, po_study, ctx_study) -> str:
    """The holiday caveat, one clause per grain and study: PathOpt periods (PathOpt study) and, when the context study
    was read, its on-peak runs. Empty when no listed holiday falls inside either data window."""
    clauses = []
    if holiday_periods:
        if len(holiday_periods) == 1:
            clause = f"The {hol} topology is one of the {n_periods} PathOpt periods (study {po_study})"
        else:
            clause = f"{len(holiday_periods)} of the {n_periods} PathOpt periods (study {po_study}) contain a listed holiday"
        if binding["basis"] == "periods":
            total = binding["total"]
            legs = ", ".join(f"{l}: {n}" for l, n in binding["by_leg"].items() if n)
            clause += (f"; {total} binding periods fall on a listed holiday ({legs}), so the holiday filter matters for the legs named"
                       if total else "; no binding periods fall on a listed holiday")
        clauses.append(clause + ".")
    if binding["basis"] == "runs" and binding.get("n_runs_on_holiday"):
        total = binding["total"]
        legs = ", ".join(f"{l}: {n}" for l, n in binding["by_leg"].items() if n)
        found = (f"{total} binding runs fall on a listed holiday ({legs}), so the holiday filter matters for the legs named" if total
                 else "no binding runs fall on a listed holiday")
        clauses.append(f"In study {ctx_study}, {binding['n_runs_on_holiday']} of the {binding['n_runs']} on-peak runs fall on a listed holiday; {found}.")
    return f"{hol}: holiday filter effect {hs}. " + " ".join(clauses) if clauses else ""


# ------------------------------------------------------------------ multi --

def _tab(df: pd.DataFrame, cols: list[str], n: int = 25) -> str:
    d = df[[c for c in cols if c in df]].head(n)
    return html.table(d, html.auto_cols(d))


def _full(df: pd.DataFrame) -> str:
    return html.table(df, html.auto_cols(df))


def _index_table(df: pd.DataFrame) -> str:
    d = df.round(3)
    text = html.pandas_text(d)
    text.insert(0, "", list(d.index))
    return html.table(text, [html.Col(str(c), c, "text", "l" if i == 0 else "r") for i, c in enumerate(text.columns)])


def multi_caveats(r) -> list[str]:
    spec, cand, per = r.spec, r.cand, r.per
    labels, required, floor = spec.all_labels, spec.required, spec.floor
    vo = cand.head(10)["VO_SHARE"]
    hol = holiday_text(spec.holidays)
    n_words = {1: "one", 2: "two", 3: "three", 4: "four"}.get(len(required), str(len(required)))
    value_only = [l for l in labels if l not in required]
    vo_txt = f"; value-only legs ({', '.join(value_only)}) supply {vo.min():.0%}-{vo.max():.0%} of VALUE_ALL in the top 10 singles" if value_only and len(vo) else ""
    bind_dates = lambda l: per.loc[per[f"SPSUM_{l}"] > 0, "DATES"].str.split(",").explode().tolist()
    lines = [f"NET ranks on VALUE_ALL (signed sum over all legs). NET_REQ = VALUE_REQ - price counts the {n_words} required constraint{'s' if len(required) != 1 else ''} only{vo_txt}."]
    if {"BLESSING1382", "JCKSTP18A", "JCKREF27A", "STPHLJ_DHLJNHK5", "STPHLJ_SHLJSTP5"} <= set(labels):  # 14966 analysis
        pn = cand[cand["SOURCENAME"] == "PCT_RN"].head(1)
        lines.append(f"Blessing is a passenger on the PCT_RN->BRP family (BLESSING1382 MIN_SF ~{pn['MIN_SF_BLESSING1382'].iloc[0] if len(pn) else float('nan'):.3f}, just above the {floor} floor): the NET there comes from JCK and the STP-Hillje legs.")
    lines.append(f"SP value scale comes from study {r.po_study} (the PathOpt study): mean SP over its {r.n_runs} on-peak runs ({hol} excluded), zero where not enforced. binding_summary.csv / binding_runs.csv come from study {spec.study}. Scale rests on few SP runs for some legs ({', '.join(f'{x.constraint}: {int(x.n_runs_with_sp)}' for x in r.sp_tab.itertuples())}). value_k = scale_k x stored SHADOWPRICEPRECENT_k/100 where the path is in that PathOpt run, reconstructed from set SFs only as fallback.")
    lines.append("Value covers only the listed constraints and on-peak only; the path's other congestion is NOT included.")
    live_txt = ", ".join(f"{l} live {int(per[f'LIVE_{l}'].sum())}" if i == 0 else f"{l} {int(per[f'LIVE_{l}'].sum())}" for i, l in enumerate(required[:2]))
    cobind = f"MIN_SF is a stress statistic over the constraint's live topology periods (at most {len(per)}; {live_txt}), not a probability of earning."
    unbound = [l for l in required if not bind_dates(l)]
    if unbound:
        cobind += f" No binding period for {', '.join(unbound)}."
    if len(required) >= 2 and not unbound:
        la, lb = required[0], required[1]
        n_co = int(((per[f"SPSUM_{la}"] > 0) & (per[f"SPSUM_{lb}"] > 0)).sum())
        if n_co == 0:
            ranges = ", ".join(f"{short_name(l)} {date_range_text(bind_dates(l))}"
                               for l in sorted((lb, la), key=lambda l: min(bind_dates(l))))
            cobind += f" {la} and {lb} never co-bind ({ranges}), yet the filter requires both."
        else:
            cobind += f" {la} and {lb} co-bind in {n_co} of {len(per)} periods."
    lines.append(cobind)
    hol_line = holiday_sentence(hol, r.hs, len(per), r.holiday_periods, r.holiday_binding, r.po_study, spec.study) if spec.holidays else ""
    if hol_line:
        lines.append(hol_line)
    lines.append(f"Dedup: aliases collapsed on MIN/AVG SF of every leg at 3 dp (cheapest kept); FAMILY groups rows whose per-leg MIN and AVG SFs all agree within 0.015 of the family leader{' (e.g. PAVLOV_BT_RN/PAVLOV_RN, BRP_BRAZ_RN/BRPANGLE_RN)' if 'BLESSING1382' in labels else ''}.")
    lines.append(f"Pairs: PRICE_2MW and VALUE_ALL_2MW are totals for 2 MW (1 MW each leg); per-MW = half; SF halved to per-MW before the filter; complementary only (neither leg passes alone). Pool = top {spec.pool} per constraint by value per $, so the search is not exhaustive. Pair values are additive.")
    return lines


def multi_scatter(r) -> go.Figure:
    required, ov, cand, pairs = r.spec.required, r.ov, r.cand, r.pairs
    xl = required[:-1] if len(required) > 1 else required
    ylab = required[-1]
    xs = lambda d: d[[f"AVG_SF_{l}" for l in xl]].mean(axis=1)
    samp = ov.sample(min(len(ov), 20000), random_state=0)
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=xs(samp), y=samp[f"AVG_SF_{ylab}"], mode="markers", name="overlap paths (sample)",
                               marker=dict(size=3, opacity=0.5, color=samp["OPTIONPRICE"], colorscale="Viridis",
                                           colorbar=dict(title="Price $/MWh"))))
    top = cand.head(25)
    if len(top):
        fig.add_trace(go.Scatter(x=xs(top), y=top[f"AVG_SF_{ylab}"], mode="markers+text", name="top singles (by NET)",
                                 text=[str(i + 1) for i in range(len(top))], textposition="top center",
                                 marker=dict(size=10, color="red", symbol="circle-open", line=dict(width=2)),
                                 customdata=(top["SOURCENAME"] + "→" + top["SINKNAME"] + "  $" + top["OPTIONPRICE"].round(2).astype(str)),
                                 hovertemplate="%{customdata}<extra></extra>"))
    if len(pairs):
        pp = pairs.head(25)
        fig.add_trace(go.Scatter(x=pp[[f"AVG_SF_{l}" for l in xl]].mean(axis=1), y=pp[f"AVG_SF_{ylab}"], mode="markers",
                                 name="top pairs (per-MW SF)", marker=dict(size=9, color="orange", symbol="star"),
                                 customdata=(pp["A_PATH"] + " + " + pp["B_PATH"]), hovertemplate="%{customdata}<extra></extra>"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray"); fig.add_vline(x=0, line_dash="dash", line_color="gray")
    fig.update_layout(title=f"Overlap paths: x = mean AVG_SF of {'/'.join(xl)}, y = AVG_SF {ylab}", width=1200, height=800,
                      xaxis_title="/".join(xl) + " avg SF", yaxis_title=f"{ylab} avg SF")
    return fig


def multi_html(r) -> str:
    spec, per, floor = r.spec, r.per, r.spec.floor
    labels, required = spec.all_labels, spec.required
    reqtxt = ", ".join(required)
    sc = (["SOURCENAME", "SINKNAME", "ALIAS_COUNT", "OPTIONPRICE"] + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels]
          + ["VALUE_REQ", "VALUE_ALL", "NET_REQ", "VO_SHARE", "SHORT_FLAG", "NET", "RATIO", "FAMILY", "FAMILY_SIZE"])
    pc = (["A_PATH", "B_PATH", "PRICE_2MW", "VALUE_ALL_2MW", "PRICE_PER_MW", "VALUE_ALL_PER_MW", "NET_PER_MW", "NET_REQ_PER_MW", "VO_SHARE", "SHORT_FLAG", "FAMILY", "FAMILY_SIZE"]
          + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels])
    S = html.section
    body = "\n".join([
        html.note(f"PathOpt runs: {', '.join(f'{l}={spec.all_runs[l]}' for l in labels)} (study {r.po_study}, PRICECLASS 2). "
                  f"Filter: live-period MIN_SF &gt;= {floor} on EVERY required constraint ({reqtxt}). "
                  f"Ranked by NET = VALUE_ALL - OPTIONPRICE, where VALUE_ALL is the signed sum over all legs (required + co-binders). "
                  f"SHORT_FLAG = a non-required binding leg has AVG_SF &lt; -0.02."),
        S("Balanced-filter counts (overlap of required runs)",
          html.note(f"Live-period MIN floor: {r.floors}. Binding-period MIN: {r.floors_b}. Holiday: {r.hs}")),
        S("Top single families (best member per ~2 dp SF family)", _tab(r.fam, sc + ["FAMILY_MEMBERS"], 15)),
        S(f"Near-miss families (pass all required floors but one, which is in [{0.4*floor:.3f}, {floor}))", _tab(r.nm, sc + ["FAILING_LEG", "FAMILY_MEMBERS"], 10)),
        S("Top single paths", _tab(r.cand, sc)),
        S("Top complementary pairs (PRICE_2MW / VALUE_ALL_2MW are totals for 2 MW; per-MW columns = half)",
          _tab(r.pairs, pc + ["MEMBER"]) if len(r.pairs) else "none"),
        S(f"Paid-to-take: {len(r.ptt)}", _tab(r.ptt, sc, 10) if len(r.ptt) else ""),
        S("Scatter", html.figure(multi_scatter(r), True)),
        S("Directional compatibility: AVG_SF correlation, overlap of required runs", _index_table(r.corr_o)),
        S("Same, all union paths", _index_table(r.corr_u)),
        S("On-peak periods", _full(per)),
        S("Overlap counts", _full(r.counts), html.note(f"OPTIONPRICE consistency: {r.price_cons.to_dict('records')[0]}")),
        S("Reproduction of PathOpt stats from set shift factors", _full(r.repro)),
        S(f"Study {spec.study} context (secondary)", _full(r.ctx_sum) if r.ctx_sum is not None else "n/a"),
        S("SP scale", _full(r.sp_tab)),
        S("Caveats", html.preformatted("\n".join("- " + l for l in multi_caveats(r)))),
    ])
    return html.page(f"Paths long {reqtxt} @ {r.ctg_label} (on-peak)", body)


def multi_readme(r, command: str) -> str:
    spec, floor, required, labels = r.spec, r.spec.floor, r.spec.required, r.spec.all_labels
    reqtxt = ", ".join(required)
    sc_md = ["SOURCENAME", "SINKNAME", "OPTIONPRICE"] + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels] + ["VALUE_ALL", "NET", "SHORT_FLAG"]
    pc_md = ["A_PATH", "B_PATH", "PRICE_2MW", "VALUE_ALL_2MW", "PRICE_PER_MW", "VALUE_ALL_PER_MW", "NET_PER_MW", "NET_REQ_PER_MW", "VO_SHARE", "FAMILY_SIZE"] + [f"MIN_SF_{l}" for l in labels]
    caveats = "\n".join("- " + l for l in multi_caveats(r))
    return f"""# Multi-constraint path search: {reqtxt}

Command (from {config.PROJECT_ROOT.parent}; needs `pyopenssl`, so add `--with "pyopenssl>=26.4"` after `uv run` if it is not installed):

{markdown.code_block(command)}

Filter: live-period MIN_SF >= {floor} on every required constraint (counts at 0.05 / 0.10: {r.floors.get(0.05)} / {r.floors.get(0.1)} overlap paths).
Rank: NET = VALUE_ALL - OPTIONPRICE.

## Top 3 single families (best member; members listed in candidates_families.csv)
{markdown.table(r.fam, sc_md + ["NET_REQ", "VO_SHARE", "FAMILY_SIZE", "FAMILY_MEMBERS"], 3)}

## Top 5 single paths
{markdown.table(r.cand, sc_md + ["NET_REQ", "VO_SHARE"], 5)}

## Near-miss (fails exactly one required floor)
{markdown.table(r.nm, sc_md + ["FAILING_LEG", "NET_REQ"], 3)}

## Top 3 complementary pair families (PRICE_2MW / VALUE_ALL_2MW are 2-MW totals)
{markdown.table(r.pairs[r.pairs["FAMILY_RANK"] == 1], pc_md, 3) if len(r.pairs) else 'none'}

## Caveats
{caveats}

Files: report.html, candidates_single.csv, candidates_pairs.csv, paths_all.parquet, reproduction_check.csv, overlap_counts.csv,
periods.csv, pathopt_study_sp_scale.csv, binding_runs.csv, binding_summary.csv.
Legacy 2-run mode (`--run-x/--run-y/--date/--hour`) is unchanged.
"""


# ----------------------------------------------------------------- spread --

def _spread_cols(L: str, Sh: list[str]) -> list[str]:
    return (["SOURCENAME", "SINKNAME", "OPTIONPRICE", f"MIN_SF_{L}", f"AVG_SF_{L}"] + [f"MAXB_SF_{l}" for l in Sh] + [f"MAX_SF_{l}" for l in Sh]
            + [f"AVGB_SF_{l}" for l in Sh]
            + ["VALUE_LONG", "VALUE_SHORT", "VALUE_OBLIG", "VALUE_ALL_OPT", "NET_OPT", "RATIO", "PRICE_PER_LONG_SF", "SHORT_FLAG", "FAMILY_SIZE", "FAMILY_MEMBERS"])


def cobind_warnings(r) -> list[str]:
    """One warning when the long and short legs bind in the same run(s); the two directions share the same runs, so it is not repeated per direction."""
    for d in r.directions:
        cb = d.cobind
        if cb["runs_both"]:
            return [f"{d.long} and {', '.join(d.short)} co-bind in {cb['runs_both']} of {cb['n_runs']} runs ({cb['n_both']} of {cb['n_periods']} periods; "
                    f"{d.long} binds in {cb['long_runs']} runs, {', '.join(d.short)} in {cb['short_runs']}). VALUE_LONG assumes the short leg costs nothing "
                    f"when only the long leg binds, so the long-leg option value is overstated for those runs; VALUE_LONG is not adjusted."]
    return []


def spread_caveats(r) -> list[str]:
    spec, floor = r.spec, r.spec.floor
    hol = holiday_text(spec.holidays)
    d0 = r.directions[0]
    L0, Sh0 = d0.long, d0.short
    pair = f"{L0} and {Sh0[0]}"
    live_txt = ", ".join(f"{l} {r.live_counts.get(l, '?')}/{r.n_periods}" for l in (L0, *Sh0))
    other_legs = ", ".join(l for l in spec.all_labels if l not in {L0, *Sh0})
    overstated = [d for d in r.directions if d.cobind["runs_both"]]
    if overstated:
        cb = overstated[0].cobind
        valid = (f"NOT valid in the {cb['runs_both']} of {cb['n_runs']} runs where {pair} co-bind: there the short leg costs money "
                 f"and VALUE_LONG overstates the long-leg option value")
    else:
        cb = r.directions[0].cobind
        shared = f" in any run (they share {cb['n_both']} of {cb['n_periods']} periods)" if cb["n_both"] else ""
        valid = f"valid because {pair} never co-bind{shared}"
    return [
        f"Short leg tested on MAX_SF over its BINDING periods (study {r.po_study} SP>0) <= -{floor} (the strict all-live-period test passes 0 paths, see counts: the two constraints are near-collinear in the topologies where both are live); long leg = MIN_SF >= {floor} on the basis given by --long-basis ({spec.long_basis}). Universe is the long leg's PathOpt run (MAX_SF>0 there); short-leg SFs come from its own topology set.",
        f"VALUE_LONG = long-leg value only (option view: no cost to the short leg in hours when only the other constraint binds, {valid}). VALUE_OBLIG = signed sum incl. the short leg (obligation view). VALUE_ALL_OPT = exact per-run payoff max(0, sum over ALL legs SP x SF) over {r.n_runs} on-peak runs ({hol} excluded), study {r.po_study} shadow prices; computed for the top 3000 rows only.",
        f"Other legs ({other_legs}) are info only (SHORT_FLAG: AVG_SF < -0.02 while binding); they are not in NET_OPT. SP scale = study {r.po_study} mean over {r.n_runs} runs, zero-imputed: {', '.join(f'{k} {v:.2f}' for k, v in r.sp_scale.items())}.",
        f"Value counts only the listed constraints, on-peak only. MIN/MAX are stress statistics over live topologies ({live_txt}), not probabilities. {hol} effect not separately tested here.",
        "Thesis test: comparison.csv gives price per unit long AVG_SF for short-passing vs long-only paths in matched AVG_SF bands; families group paths within 0.015 on every leg's MIN/AVG SF.",
    ]


def _spread_title(r) -> str:
    d0 = r.directions[0]
    return os.path.commonprefix([d0.long, *d0.short]) or "Path"


def spread_html(r) -> str:
    sections = []
    for d in r.directions:
        L, Sh = d.long, d.short
        cols = _spread_cols(L, Sh)
        cheap = d.cand[d.cand[f"MIN_SF_{L}"] >= 0.10].sort_values("OPTIONPRICE").head(10)
        fam = d.families
        sections.append(html.section(
            f"Long {L} / short {', '.join(Sh)}",
            html.note(f"Universe (run {L} paths with price&gt;0): {d.n_universe:,}. Counts by floor "
                      f"(long_only = long live MIN&gt;=floor; short_live_basis also needs short MAX over ALL its live periods &lt;=-floor; short_binding_basis needs short MAX over its BINDING periods &lt;=-floor, the basis used for ranking): {d.counts}. Pooled path-SF correlation long vs short "
                      f"(periods live for both): {d.path_corr:.3f} over {d.n_shared_obs:,} obs; opposite-sign share {d.frac_opposite_sign:.1%}."),
            html.section("Top families by NET_OPT = VALUE_LONG - price", _tab(fam, cols, 15), level=3),
            html.section("Cheapest with long MIN >= 0.10", _tab(cheap, cols, 10), level=3)))
    warnings = [html.warning(w) for w in cobind_warnings(r)]
    caveats = "\n".join("- " + l for l in spread_caveats(r))
    body = "\n".join([
        *warnings,
        html.section("Co-live topologies and collinearity", _full(r.co_live)),
        *sections,
        html.section("Price per unit long SF: short-passing vs long-only", _full(r.comp)),
        html.section("Caveats", html.preformatted(caveats)),
    ])
    return html.page(f"{_spread_title(r)} spread: long one leg / short the other", body)


def spread_readme(r, command: str) -> str:
    md = []
    for d in r.directions:
        L, Sh = d.long, d.short
        md.append(f"### Long {L} / short {', '.join(Sh)}\nUniverse {d.n_universe:,}; pass counts by floor {d.counts}; pooled path-SF corr {d.path_corr:.3f}.\n")
        md.append(markdown.table(d.families, [c for c in _spread_cols(L, Sh) if c != "FAMILY_MEMBERS"], 5) + "\n")
    warn = "".join(f"> WARNING: {w}\n\n" for w in cobind_warnings(r))
    caveats = "\n".join("- " + l for l in spread_caveats(r))
    return f"""# {_spread_title(r)} spread search (long A / short B, both directions)

Command (from {config.PROJECT_ROOT.parent}; needs `pyopenssl`, so add `--with "pyopenssl>=26.4"` after `uv run` if it is not installed):

{markdown.code_block(command)}

{warn}{''.join(md)}
Co-live / collinearity: co_live.csv. Thesis test: comparison.csv.

## Caveats
{caveats}
"""


# ------------------------------------------------------------ legacy pair --

def pair_scatter(paths: pd.DataFrame, candidates: pd.DataFrame, spec, run_x, run_y) -> go.Figure:
    """Interactive scatter of X/Y path SFs coloured by price, top candidates and day spikes highlighted."""
    fig = go.Figure()
    non_spike, spike = paths[~paths["DAY_SPIKE"]], paths[paths["DAY_SPIKE"]]
    if len(non_spike) > 0:
        fig.add_trace(go.Scattergl(
            x=non_spike["SF_X"], y=non_spike["SF_Y"], mode="markers",
            marker=dict(size=3, color=non_spike["OPTIONPRICE"], colorscale="Viridis", colorbar=dict(title="Price ($/MWh)"), opacity=0.6),
            text=[f"${row.OPTIONPRICE:.2f}/MWh<br>SF: {row.SF_X:.3f}, {row.SF_Y:.3f}" for row in non_spike.itertuples()],
            hovertemplate="%{text}<extra></extra>", name="All paths", showlegend=False))
    if len(spike) > 0:
        fig.add_trace(go.Scattergl(
            x=spike["SF_X"], y=spike["SF_Y"], mode="markers",
            marker=dict(size=4, color=spike["OPTIONPRICE"], colorscale="Viridis", symbol="diamond-open",
                        line=dict(width=1, color="orange"), opacity=0.8),
            text=[f"⚠ DAY SPIKE<br>${row.OPTIONPRICE:.2f}/MWh<br>SF: {row.SF_X:.3f}, {row.SF_Y:.3f}" for row in spike.itertuples()],
            hovertemplate="%{text}<extra></extra>", name="Day spike"))
    top_25 = candidates.head(25)
    if len(top_25) > 0:
        hover_text = []
        for i, row in enumerate(top_25.itertuples(), 1):
            text = (f"#{i}: {row.SOURCENAME}→{row.SINKNAME}<br>Aliases: {row.ALIAS_COUNT}<br>"
                    f"{row.SOURCEBUSKV:.0f}→{row.SINKBUSKV:.0f} kV<br>Price: ${row.OPTIONPRICE:.2f}/MWh<br>"
                    f"Day SF: {row.SF_X:.4f}, {row.SF_Y:.4f}<br>AVG SF: {row.AVG_SF_X:.4f}, {row.AVG_SF_Y:.4f}<br>"
                    f"MIN SF: {row.MIN_SF_X:.4f}, {row.MIN_SF_Y:.4f}<br>Ratio: {row.Y_TO_X_RATIO:.2f} ({row.DOMINANT_AXIS})<br>"
                    f"Score: {row.SCORE:.4f}")
            if row.DAY_SPIKE:
                text += "<br>⚠ DAY SPIKE"
            hover_text.append(text)
        fig.add_trace(go.Scatter(
            x=top_25["SF_X"], y=top_25["SF_Y"], mode="markers+text",
            marker=dict(size=10, color="red", symbol="circle-open", line=dict(width=2)),
            text=[f"{i+1}" for i in range(len(top_25))], textposition="top center", textfont=dict(size=10, color="red"),
            customdata=hover_text, hovertemplate="%{customdata}<extra></extra>", name="Top 25 distinct"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    x_max, y_max = paths["SF_X"].max(), paths["SF_Y"].max()
    fig.add_shape(type="rect", x0=0, y0=0, x1=x_max, y1=y_max, fillcolor="lightgreen", opacity=0.1, layer="below", line_width=0)
    fig.add_annotation(x=x_max * 0.95, y=y_max * 0.95, text="LONG BOTH", showarrow=False, font=dict(size=16, color="green"), opacity=0.3)
    sx, sy = f"{run_x.BRANCHLABEL} / {run_x.CTGLABEL} (run {spec.run_x})", f"{run_y.BRANCHLABEL} / {run_y.CTGLABEL} (run {spec.run_y})"
    fig.update_layout(
        title=f"PathOpt Scatter: Study {spec.study}, {spec.date} HE{spec.hour}<br>X: {sx} | Y: {sy}<br>{len(paths):,} paths",
        xaxis_title=f"Path SF on {sx}", yaxis_title=f"Path SF on {sy}", hovermode="closest", width=1200, height=800)
    return fig


def pair_scatter_html(fig: go.Figure) -> str:
    return fig.to_html(include_plotlyjs=True, full_html=True)


PAIR_OUTPUT_COLS = ["SOURCENAME", "SINKNAME", "ALIASES", "ALIAS_COUNT", "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE",
                    "MIN_SF_X", "MIN_SF_Y", "AVG_SF_X", "AVG_SF_Y", "SF_X", "SF_Y",
                    "Y_TO_X_RATIO", "DOMINANT_AXIS", "MIN_SF_BOTH", "AVG_SCORE", "SCORE", "DAY_SPIKE"]
PAIR_FULL_COLS = [c for c in PAIR_OUTPUT_COLS if c not in ("SF_X", "SF_Y")]


def pair_readme(r) -> str:
    s, rx, ry, full = r.spec, r.run_x, r.run_y, r.full
    cf = r.candidates_full
    top_sources = cf.groupby("SOURCENAME")["ALIAS_COUNT"].sum().sort_values(ascending=False).head(3)
    notes = []
    for source in top_sources.index:
        sp = cf[cf["SOURCENAME"] == source]
        dominant = sp["DOMINANT_AXIS"].mode().iloc[0] if len(sp) > 0 else "BALANCED"
        notes.append(f"  - **{source}**: {len(sp)} paths, avg Y/X ratio {sp['Y_TO_X_RATIO'].mean():.1f} ({dominant}-dominant)")
    n = r.neg_counts
    pct = lambda k: f"{100 * n[k] / len(full):.1f}"
    nd, nfd = len(r.paths_deduped), len(r.full_deduped)
    return f"""# PathOpt Scatter: Study {s.study}

**Date:** {s.date} HE{s.hour}
**Paths analyzed (scatter):** {nd:,} distinct (top {s.top:,} cheapest before dedup)
**Distinct electrical paths (full universe):** {nfd:,}

## Constraints

- **X-axis:** {rx.BRANCHLABEL} / {rx.CTGLABEL} (run {s.run_x}, direction {rx.DIRECTION}, set {rx.TOPOLOGYSHIFTSETID})
- **Y-axis:** {ry.BRANCHLABEL} / {ry.CTGLABEL} (run {s.run_y}, direction {ry.DIRECTION}, set {ry.TOPOLOGYSHIFTSETID})

## Method

**Path SF** = psens(source) − psens(sink) from node shift factors (CPNODE_SHIFTS_VIEW).
- Positive SF = LONG (path earns when constraint binds).
- Price = OPTIONPRICE ($/MWh, forward OnPeak price class 2 option mark) from PathOpt detail.
- **Robustness score** = min(MIN_SF_X, MIN_SF_Y) / OPTIONPRICE, where MIN_SF is worst-case across PathOpt's 10-day window.
- Materiality floor: MIN_SF_X ≥ {s.min_sf} AND MIN_SF_Y ≥ {s.min_sf}.

**Electrical path deduplication:** Paths with identical (rounded psens, MIN_SF, AVG_SF, price) are grouped; one representative kept with aliases.

**Day spike flag:** Day SF > 2× AVG_SF on either axis (outlier topology on {s.date}).

**Y-to-X ratio:** AVG_SF_Y / AVG_SF_X. Dominant axis: ratio >3 → Y, <1/3 → X, else BALANCED.

## PathOpt Pre-Filtering Disclosure

PathOpt filters on **MAX_SF > 0** (best of the 10 topologies), NOT SF ∈ [0, 1.1]. The inner join produces paths that are **long both on their best day**, not long-both by construction.

**MIN_SF ranges:** X: [{full["MIN_SF_X"].min():.4f}, {full["MIN_SF_X"].max():.4f}], Y: [{full["MIN_SF_Y"].min():.4f}, {full["MIN_SF_Y"].max():.4f}]

**Paths with negative MIN/AVG:**
- Negative MIN_SF_X: {n['MIN_SF_X']:,} ({pct('MIN_SF_X')}%)
- Negative MIN_SF_Y: {n['MIN_SF_Y']:,} ({pct('MIN_SF_Y')}%)
- Negative AVG_SF_X: {n['AVG_SF_X']:,} ({pct('AVG_SF_X')}%)
- Negative AVG_SF_Y: {n['AVG_SF_Y']:,} ({pct('AVG_SF_Y')}%)

The MIN_SF floor (≥{s.min_sf} on both axes) removes these from candidates.

**MIN_SF_X scarcity:** Only {r.min_sf_x_pass} of {nfd:,} distinct paths ({100*r.min_sf_x_pass/nfd:.1f}%) have MIN_SF_X ≥ 0.05 (median {r.median_min_sf_x:.6f}). Score ≈ MIN_SF_X / price for most paths.

Load zones excluded by PathOpt's deadbus filter: LZ_HOUSTON, HB_NORTH (only HB_HOUSTON, HB_WEST, LZ_CPS, LZ_LCRA, LZ_AEN, LZ_RAYBN present).

## Results

### Full Universe (all {nfd:,} distinct paths)
- **Passing MIN_SF floor (≥{s.min_sf} both axes):** {len(cf):,}
- **Near-miss (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05):** {len(r.near_miss):,}
- **Paid-to-take:** {len(r.paid_to_take_full)} (OPTIONPRICE≤0)

### Top {s.top:,} Cheapest (scatter, with day SFs)
- **Distinct electrical paths:** {nd:,}
- **Day spike paths (all):** {r.spike_count_all} ({100*r.spike_count_all/nd:.1f}%)
- **Day spike paths (AVG>0.02 both axes):** {r.spike_count_avg} of {r.n_avg_both_002:,} ({100*r.spike_count_avg/r.n_avg_both_002 if r.n_avg_both_002 > 0 else 0:.1f}%)
- **Passing MIN_SF floor:** {len(r.candidates):,}
- **Day spike in candidates:** {r.spike_count_candidates}

**Score is a screen, not a valuation.** MIN_SF captures worst-case exposure across the 10-day window; use for robustness ranking only.

## Files

- `scatter.html` — Interactive scatter plot (Plotly): {s.date} day SFs for top {s.top:,} cheapest, top 25 distinct candidates highlighted, day spikes marked
- `candidates.csv` — Ranked candidates from top {s.top:,} cheapest (with day SFs)
- `candidates_full.csv` — Ranked candidates from FULL universe ({len(cf):,} rows, no day SFs)
- `near_miss.csv` — Near-miss paths ({len(r.near_miss):,} rows)
- `paths_deduped.parquet` — All {nd:,} distinct paths (top {s.top:,} cheapest) with day SFs and spike flag
- `README.md` — This file

## Top Candidate Sources (from full universe)

{chr(10).join(notes)}
"""


def pair_console(r) -> str:
    """The top-15 / top-10 tables and summary the legacy mode prints."""
    s = r.spec
    out = [f"\n{'='*80}", "Top 15 Distinct Paths from FULL Universe (MIN_SF Robustness Score)", "=" * 80,
           f"{'#':<4} {'Source→Sink':<35} {'Al':<4} {'Price':<8} {'MIN_X':<7} {'MIN_Y':<7} {'AVG_X':<7} {'AVG_Y':<7} "
           f"{'Ratio':<7} {'Dom':<9} {'Score':<8} {'Spike':<6}", "-" * 140]
    for rank, row in enumerate(r.candidates_full.head(15).itertuples(), 1):
        path_str = f"{row.SOURCENAME}→{row.SINKNAME}"
        out.append(f"{rank:<4} {path_str[:34]:<35} {row.ALIAS_COUNT:<4} ${row.OPTIONPRICE:>6.2f} "
                   f"{row.MIN_SF_X:>6.3f} {row.MIN_SF_Y:>6.3f} {row.AVG_SF_X:>6.3f} {row.AVG_SF_Y:>6.3f} "
                   f"{row.Y_TO_X_RATIO:>6.2f} {row.DOMINANT_AXIS:<9} {row.SCORE:>7.4f} {'⚠' if row.DAY_SPIKE else '':<6}")
    out += [f"\n{'='*80}", "Top 10 Near-Miss Paths (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05)", "=" * 80,
            f"{'#':<4} {'Source→Sink':<35} {'Al':<4} {'Price':<8} {'MIN_X':<7} {'MIN_Y':<7} {'AVG_X':<7} {'AVG_Y':<7} "
            f"{'Ratio':<7} {'Dom':<9} {'Score':<8}", "-" * 140]
    for rank, row in enumerate(r.near_miss.head(10).itertuples(), 1):
        path_str = f"{row.SOURCENAME}→{row.SINKNAME}"
        out.append(f"{rank:<4} {path_str[:34]:<35} {row.ALIAS_COUNT:<4} ${row.OPTIONPRICE:>6.2f} "
                   f"{row.MIN_SF_X:>6.3f} {row.MIN_SF_Y:>6.3f} {row.AVG_SF_X:>6.3f} {row.AVG_SF_Y:>6.3f} "
                   f"{row.Y_TO_X_RATIO:>6.2f} {row.DOMINANT_AXIS:<9} {row.SCORE:>7.4f}")
    nd, nfd = len(r.paths_deduped), len(r.full_deduped)
    pct = lambda a, b: 100 * a / b if b > 0 else 0
    out += ["\nSummary:", f"  - Full universe: {nfd:,} distinct paths",
            f"  - Candidates (full): {len(r.candidates_full):,} passing MIN_SF ≥ {s.min_sf} floor",
            f"  - Near-miss: {len(r.near_miss):,} paths (MIN_SF_X in [0.03, 0.05))",
            f"  - Day spikes (all): {r.spike_count_all} of {nd:,} distinct ({100*r.spike_count_all/nd:.1f}%)",
            f"  - Day spikes (AVG>0.02 both): {r.spike_count_avg} of {r.n_avg_both_002:,} ({pct(r.spike_count_avg, r.n_avg_both_002):.1f}%)",
            f"  - CHAR_SLR_RN→PIN_BESS_RN flagged: {r.char_pin_flag if r.char_pin_flag is not None else 'N/A (not in top 100k)'}"]
    return "\n".join(out)
