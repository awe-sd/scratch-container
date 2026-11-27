"""Path scatter analysis: find paths that are LONG both constraints and CHEAP.

Path SF = psens(source) − psens(sink). Positive SF = long (path earns when that
constraint binds). Candidates ranked by robustness score = min(MIN_SF_x, MIN_SF_y) / OPTIONPRICE,
where MIN_SF is the worst-case SF across PathOpt's 10-day window.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

from .. import config


def compute_path_shift_factors(
    paths: pd.DataFrame,
    node_sf_x: pd.DataFrame,
    node_sf_y: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """Compute path SFs for two constraints from node psens.

    Args:
        paths: DataFrame with SOURCECPNODEID, SINKCPNODEID, OPTIONPRICE, etc.
        node_sf_x: Node psens for constraint X (CPNODEID, PSENS).
        node_sf_y: Node psens for constraint Y (CPNODEID, PSENS).

    Returns:
        (paths_with_sfs, dropped_count): paths with SF_X, SF_Y, PSENS_* columns; count dropped.
    """
    # Build node psens lookup
    psens_x = node_sf_x.set_index("CPNODEID")["PSENS"].to_dict()
    psens_y = node_sf_y.set_index("CPNODEID")["PSENS"].to_dict()

    # Compute path SFs: psens(source) - psens(sink)
    paths = paths.copy()
    paths["PSENS_SRC_X"] = paths["SOURCECPNODEID"].map(psens_x)
    paths["PSENS_SINK_X"] = paths["SINKCPNODEID"].map(psens_x)
    paths["PSENS_SRC_Y"] = paths["SOURCECPNODEID"].map(psens_y)
    paths["PSENS_SINK_Y"] = paths["SINKCPNODEID"].map(psens_y)

    # Drop paths with missing nodes
    before = len(paths)
    paths = paths.dropna(subset=["PSENS_SRC_X", "PSENS_SINK_X", "PSENS_SRC_Y", "PSENS_SINK_Y"])
    dropped = before - len(paths)

    # Compute path SFs
    paths["SF_X"] = paths["PSENS_SRC_X"] - paths["PSENS_SINK_X"]
    paths["SF_Y"] = paths["PSENS_SRC_Y"] - paths["PSENS_SINK_Y"]

    return paths, dropped


def dedup_by_electrical_path(paths: pd.DataFrame, has_day_sf: bool = True) -> pd.DataFrame:
    """Dedup by electrical path: group by rounded statistics, keep alphabetically first with aliases.

    Args:
        paths: DataFrame with MIN_SF_X/Y, AVG_SF_X/Y, OPTIONPRICE, optionally PSENS columns + MAX_SF.
        has_day_sf: If True, use day psens + MIN/AVG. If False, use PathOpt MIN/AVG/MAX only.

    Returns:
        Deduplicated DataFrame with ALIASES column (semicolon-separated) and ALIAS_COUNT.
    """
    paths = paths.copy()

    if has_day_sf and "PSENS_SRC_X" in paths.columns:
        # For 100k set with day SFs: use day psens + MIN/AVG + price
        paths["SRC_X_R"] = paths["PSENS_SRC_X"].round(5)
        paths["SRC_Y_R"] = paths["PSENS_SRC_Y"].round(5)
        paths["SINK_X_R"] = paths["PSENS_SINK_X"].round(5)
        paths["SINK_Y_R"] = paths["PSENS_SINK_Y"].round(5)
        paths["MIN_X_R"] = paths["MIN_SF_X"].round(5)
        paths["MIN_Y_R"] = paths["MIN_SF_Y"].round(5)
        paths["AVG_X_R"] = paths["AVG_SF_X"].round(5)
        paths["AVG_Y_R"] = paths["AVG_SF_Y"].round(5)
        paths["PRICE_R"] = paths["OPTIONPRICE"].round(5)
        group_cols = ["SRC_X_R", "SRC_Y_R", "SINK_X_R", "SINK_Y_R",
                      "MIN_X_R", "MIN_Y_R", "AVG_X_R", "AVG_Y_R", "PRICE_R"]
    else:
        # For full universe without day SFs: use PathOpt MIN/AVG/MAX + price only
        # Don't use CPNODEID — aliases are different cpnodes at same bus
        paths["MIN_X_R"] = paths["MIN_SF_X"].round(5)
        paths["MIN_Y_R"] = paths["MIN_SF_Y"].round(5)
        paths["AVG_X_R"] = paths["AVG_SF_X"].round(5)
        paths["AVG_Y_R"] = paths["AVG_SF_Y"].round(5)
        paths["MAX_X_R"] = paths["MAX_SF_X"].round(5)
        paths["MAX_Y_R"] = paths["MAX_SF_Y"].round(5)
        paths["PRICE_R"] = paths["OPTIONPRICE"].round(5)
        group_cols = ["MIN_X_R", "MIN_Y_R", "AVG_X_R", "AVG_Y_R",
                      "MAX_X_R", "MAX_Y_R", "PRICE_R"]

    # For each group, keep alphabetically first source/sink and collect aliases
    def agg_aliases(group):
        # Sort by source, then sink alphabetically to pick representative
        group = group.sort_values(["SOURCENAME", "SINKNAME"])
        first = group.iloc[0].copy()

        if len(group) > 1:
            # Collect all source->sink pairs as aliases
            aliases = [f"{row.SOURCENAME}→{row.SINKNAME}" for _, row in group.iterrows()]
            first["ALIASES"] = "; ".join(aliases)
            first["ALIAS_COUNT"] = len(group)
        else:
            first["ALIASES"] = f"{first.SOURCENAME}→{first.SINKNAME}"
            first["ALIAS_COUNT"] = 1
        return first

    deduped = paths.groupby(group_cols, as_index=False).apply(agg_aliases, include_groups=False).reset_index(drop=True)

    # Drop grouping columns
    drop_cols = [c for c in group_cols if c in deduped.columns]
    if drop_cols:
        deduped = deduped.drop(columns=drop_cols)

    return deduped


def add_derived_columns(paths: pd.DataFrame, has_day_sf: bool = False) -> pd.DataFrame:
    """Add Y_TO_X_RATIO, DOMINANT_AXIS, DAY_SPIKE columns.

    Args:
        paths: DataFrame with AVG_SF_X, AVG_SF_Y, optionally SF_X, SF_Y.
        has_day_sf: Whether paths has day SF_X, SF_Y columns for spike detection.

    Returns:
        paths with added columns.
    """
    paths = paths.copy()

    # Y-to-X ratio and dominance
    paths["Y_TO_X_RATIO"] = paths["AVG_SF_Y"] / paths["AVG_SF_X"].replace(0, float("nan"))

    def classify_dominance(ratio):
        if pd.isna(ratio):
            return "BALANCED"
        elif ratio > 3:
            return "Y"
        elif ratio < 1/3:
            return "X"
        else:
            return "BALANCED"

    paths["DOMINANT_AXIS"] = paths["Y_TO_X_RATIO"].apply(classify_dominance)

    # Day spike flag (only if day SFs available)
    if has_day_sf and "SF_X" in paths.columns and "SF_Y" in paths.columns:
        paths["DAY_SPIKE"] = ((paths["SF_X"] > 2 * paths["AVG_SF_X"]) |
                              (paths["SF_Y"] > 2 * paths["AVG_SF_Y"]))
    else:
        paths["DAY_SPIKE"] = False

    return paths


def rank_by_min_sf(
    paths: pd.DataFrame,
    min_sf_floor: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Rank paths by robustness: score = min(MIN_SF_x, MIN_SF_y) / OPTIONPRICE.

    Args:
        paths: DataFrame with MIN_SF_X, MIN_SF_Y, AVG_SF_X, AVG_SF_Y, OPTIONPRICE.
        min_sf_floor: Minimum threshold on both MIN_SF_x and MIN_SF_y.

    Returns:
        (paid_to_take, ranked_candidates):
            - paid_to_take: paths with OPTIONPRICE <= 0.
            - ranked_candidates: paths passing floor, ranked by robustness score.
    """
    paths = paths.copy()

    # Add AVG score column
    paths["AVG_SCORE"] = (paths["AVG_SF_X"] + paths["AVG_SF_Y"]) / paths["OPTIONPRICE"]

    # Separate paid-to-take
    paid_to_take = paths[paths["OPTIONPRICE"] <= 0].copy()
    paid_to_take["SCORE"] = float("inf")

    # Filter by MIN_SF floor on both axes
    candidates = paths[(paths["OPTIONPRICE"] > 0) &
                       (paths["MIN_SF_X"] >= min_sf_floor) &
                       (paths["MIN_SF_Y"] >= min_sf_floor)].copy()

    # Compute robustness score
    candidates["MIN_SF_BOTH"] = candidates[["MIN_SF_X", "MIN_SF_Y"]].min(axis=1)
    candidates["SCORE"] = candidates["MIN_SF_BOTH"] / candidates["OPTIONPRICE"]
    candidates = candidates.sort_values("SCORE", ascending=False)

    return paid_to_take, candidates


def find_near_miss(
    paths: pd.DataFrame,
    min_x_range: tuple[float, float] = (0.03, 0.05),
    min_y_floor: float = 0.05,
) -> pd.DataFrame:
    """Find near-miss paths: MIN_SF_X in [min_x_range] with MIN_SF_Y >= min_y_floor.

    Args:
        paths: DataFrame with MIN_SF_X, MIN_SF_Y, AVG_SF_X, AVG_SF_Y, OPTIONPRICE.
        min_x_range: (low, high) for MIN_SF_X.
        min_y_floor: Minimum MIN_SF_Y.

    Returns:
        Near-miss paths ranked by score.
    """
    near_miss = paths[(paths["OPTIONPRICE"] > 0) &
                      (paths["MIN_SF_X"] >= min_x_range[0]) &
                      (paths["MIN_SF_X"] < min_x_range[1]) &
                      (paths["MIN_SF_Y"] >= min_y_floor)].copy()

    near_miss["MIN_SF_BOTH"] = near_miss[["MIN_SF_X", "MIN_SF_Y"]].min(axis=1)
    near_miss["AVG_SCORE"] = (near_miss["AVG_SF_X"] + near_miss["AVG_SF_Y"]) / near_miss["OPTIONPRICE"]
    near_miss["SCORE"] = near_miss["MIN_SF_BOTH"] / near_miss["OPTIONPRICE"]
    near_miss = near_miss.sort_values("SCORE", ascending=False)

    return near_miss


def build_scatter_plot(
    paths: pd.DataFrame,
    candidates: pd.DataFrame,
    study_id: int,
    run_x_id: int,
    run_y_id: int,
    run_x_branch: str,
    run_x_ctg: str,
    run_y_branch: str,
    run_y_ctg: str,
    sim_date: str,
    sim_hour: int,
    output_path: Path,
) -> None:
    """Build interactive Plotly scatter: X/Y path SFs, colored by price, with top candidates and spikes highlighted.

    Args:
        paths: All paths with SF_X, SF_Y, OPTIONPRICE, DAY_SPIKE.
        candidates: Top-ranked candidates (first 25 distinct will be highlighted).
        study_id: PathOpt study ID.
        run_x_id: X-axis run ID.
        run_y_id: Y-axis run ID.
        run_x_branch: X-axis branch label.
        run_x_ctg: X-axis contingency label.
        run_y_branch: Y-axis branch label.
        run_y_ctg: Y-axis contingency label.
        sim_date: Simulation date (YYYY-MM-DD).
        sim_hour: Simulation hour.
        output_path: Output HTML file path.
    """
    fig = go.Figure()

    # Separate spike and non-spike paths
    non_spike = paths[~paths["DAY_SPIKE"]]
    spike = paths[paths["DAY_SPIKE"]]

    # Main scatter: non-spike paths (simplified hover)
    if len(non_spike) > 0:
        fig.add_trace(go.Scattergl(
            x=non_spike["SF_X"],
            y=non_spike["SF_Y"],
            mode="markers",
            marker=dict(
                size=3,
                color=non_spike["OPTIONPRICE"],
                colorscale="Viridis",
                colorbar=dict(title="Price ($/MWh)"),
                opacity=0.6,
            ),
            text=[
                f"${row.OPTIONPRICE:.2f}/MWh<br>SF: {row.SF_X:.3f}, {row.SF_Y:.3f}"
                for row in non_spike.itertuples()
            ],
            hovertemplate="%{text}<extra></extra>",
            name="All paths",
            showlegend=False,
        ))

    # Spike paths: different symbol (diamond with outline)
    if len(spike) > 0:
        fig.add_trace(go.Scattergl(
            x=spike["SF_X"],
            y=spike["SF_Y"],
            mode="markers",
            marker=dict(
                size=4,
                color=spike["OPTIONPRICE"],
                colorscale="Viridis",
                symbol="diamond-open",
                line=dict(width=1, color="orange"),
                opacity=0.8,
            ),
            text=[
                f"⚠ DAY SPIKE<br>${row.OPTIONPRICE:.2f}/MWh<br>SF: {row.SF_X:.3f}, {row.SF_Y:.3f}"
                for row in spike.itertuples()
            ],
            hovertemplate="%{text}<extra></extra>",
            name="Day spike",
        ))

    # Overlay top 25 distinct candidates
    top_25 = candidates.head(25)
    if len(top_25) > 0:
        hover_text = []
        for i, row in enumerate(top_25.itertuples(), 1):
            text = (f"#{i}: {row.SOURCENAME}→{row.SINKNAME}<br>"
                    f"Aliases: {row.ALIAS_COUNT}<br>"
                    f"{row.SOURCEBUSKV:.0f}→{row.SINKBUSKV:.0f} kV<br>"
                    f"Price: ${row.OPTIONPRICE:.2f}/MWh<br>"
                    f"Day SF: {row.SF_X:.4f}, {row.SF_Y:.4f}<br>"
                    f"AVG SF: {row.AVG_SF_X:.4f}, {row.AVG_SF_Y:.4f}<br>"
                    f"MIN SF: {row.MIN_SF_X:.4f}, {row.MIN_SF_Y:.4f}<br>"
                    f"Ratio: {row.Y_TO_X_RATIO:.2f} ({row.DOMINANT_AXIS})<br>"
                    f"Score: {row.SCORE:.4f}")
            if row.DAY_SPIKE:
                text += "<br>⚠ DAY SPIKE"
            hover_text.append(text)

        fig.add_trace(go.Scatter(
            x=top_25["SF_X"],
            y=top_25["SF_Y"],
            mode="markers+text",
            marker=dict(
                size=10,
                color="red",
                symbol="circle-open",
                line=dict(width=2),
            ),
            text=[f"{i+1}" for i in range(len(top_25))],
            textposition="top center",
            textfont=dict(size=10, color="red"),
            customdata=hover_text,
            hovertemplate="%{customdata}<extra></extra>",
            name="Top 25 distinct",
        ))

    # Draw axis lines at 0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Shade top-right "long both" quadrant
    x_max = paths["SF_X"].max()
    y_max = paths["SF_Y"].max()
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=x_max, y1=y_max,
        fillcolor="lightgreen",
        opacity=0.1,
        layer="below",
        line_width=0,
    )
    fig.add_annotation(
        x=x_max * 0.95,
        y=y_max * 0.95,
        text="LONG BOTH",
        showarrow=False,
        font=dict(size=16, color="green"),
        opacity=0.3,
    )

    # Layout
    fig.update_layout(
        title=f"PathOpt Scatter: Study {study_id}, {sim_date} HE{sim_hour}<br>"
              f"X: {run_x_branch} / {run_x_ctg} (run {run_x_id}) | Y: {run_y_branch} / {run_y_ctg} (run {run_y_id})<br>"
              f"{len(paths):,} paths",
        xaxis_title=f"Path SF on {run_x_branch} / {run_x_ctg} (run {run_x_id})",
        yaxis_title=f"Path SF on {run_y_branch} / {run_y_ctg} (run {run_y_id})",
        hovermode="closest",
        width=1200,
        height=800,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path)


# ---------------------------------------------------------------------------
# N-run generalisation: overlap of several PathOpt runs, per-period SFs from the
# runs' topology shift sets, PathOpt-stat reproduction, ranking, pair search.
# PathOpt convention (reproduced to 1e-3, see reproduction_check): a period is a
# distinct psenshift in the set holding >=1 weekday SIMHOUR 7-22 run (holidays NOT
# excluded); stats are over periods where BOTH path nodes have DEADBUS=0 (that
# count is BINDINGPAIRCOUNT). Stored psens are already oriented to the binding direction.
# ---------------------------------------------------------------------------
import numpy as np

STAT_COLS = ["MIN_SF", "AVG_SF", "MAX_SF", "SHADOWPRICEPRECENT", "BINDINGPAIRCOUNT"]
KEY = ["SOURCECPNODEID", "SINKCPNODEID"]


def onpeak_members(members: pd.DataFrame, hours: tuple[int, int] = (7, 22)) -> pd.DataFrame:
    """Set members that are weekday on-peak runs (SIMHOUR within hours)."""
    d = pd.to_datetime(members["SIMDATE"])
    return members[(d.dt.dayofweek < 5) & members["SIMHOUR"].between(*hours)].copy()


def overlap_runs(details: dict[str, pd.DataFrame], required: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Outer-join per-run PathOpt details on (source, sink); stat columns suffixed _<label>.

    Returns (union frame with IN_<label> flags, price-consistency table)."""
    out = None
    price_cols = []
    for lab, d in details.items():
        d = d.rename(columns={c: f"{c}_{lab}" for c in STAT_COLS + ["OPTIONPRICE", "WAVG_DOLLAR_MWH"]})
        d[f"IN_{lab}"] = True
        price_cols.append(f"OPTIONPRICE_{lab}")
        if out is None:
            out = d
        else:
            ids = ["SOURCENAME", "SINKNAME", "SOURCEBUSKV", "SINKBUSKV"]
            out = out.merge(d.rename(columns={c: c + "__n" for c in ids}), on=KEY, how="outer")
            for c in ids:
                out[c] = out[c].combine_first(out.pop(c + "__n"))
    for c in [c for c in out.columns if c.startswith("IN_")]:
        out[c] = out[c].fillna(False).astype(bool)
    out["OPTIONPRICE"] = out[price_cols].bfill(axis=1).iloc[:, 0]
    pr = out[price_cols]
    ncov = pr.notna().sum(axis=1)
    multi = out[ncov >= 2]
    spread = (multi[price_cols].max(axis=1) - multi[price_cols].min(axis=1))
    cons = pd.DataFrame([{"paths_in_2plus_runs": len(multi), "max_price_spread": float(spread.max()),
                          "n_spread_gt_0.001": int((spread > 1e-3).sum())}])
    return out, cons


def overlap_counts(paths: pd.DataFrame, labels: list[str], required: list[str]) -> pd.DataFrame:
    import itertools
    rows = [{"set": "union of all runs", "n": len(paths)}]
    for lab in labels:
        rows.append({"set": f"in {lab}", "n": int(paths[f"IN_{lab}"].sum())})
    for r in (2, 3, 4):
        for combo in itertools.combinations(labels, r):
            m = np.logical_and.reduce([paths[f"IN_{c}"] for c in combo])
            rows.append({"set": " & ".join(combo), "n": int(m.sum())})
    return pd.DataFrame(rows)


def path_sf_matrix(paths: pd.DataFrame, P: pd.DataFrame, D: pd.DataFrame, sign: float = 1.0) -> np.ndarray:
    """Per-period path SF = sign*(psens(src)-psens(sink)); NaN where either node is dead/missing that period.
    P, D: CPNODEID-indexed, one column per period (same column order for every constraint)."""
    src, snk = paths["SOURCECPNODEID"].values, paths["SINKCPNODEID"].values
    S = P.reindex(src).values - P.reindex(snk).values
    live = (D.reindex(src).values == 0) & (D.reindex(snk).values == 0)
    return (sign * np.where(live, S, np.nan)).astype(np.float32)


def sf_stats(S: np.ndarray) -> pd.DataFrame:
    live = ~np.isnan(S)
    n = live.sum(axis=1)
    hi = np.where(live, S, -np.inf).max(axis=1)
    lo = np.where(live, S, np.inf).min(axis=1)
    avg = np.where(live, S, 0).sum(axis=1) / np.maximum(n, 1)
    return pd.DataFrame({"MIN_SF": np.where(n > 0, lo, np.nan), "AVG_SF": np.where(n > 0, avg, np.nan),
                         "MAX_SF": np.where(n > 0, hi, np.nan), "BINDINGPAIRCOUNT": n})


def reproduction_check(paths: pd.DataFrame, S_pos: np.ndarray, label: str, direction) -> tuple[dict, float]:
    """Compare recomputed per-period stats with PathOpt's stored stats for paths in this run.
    Tries both orientations and returns (row, chosen sign)."""
    m = paths[f"IN_{label}"].values
    res = {}
    for sgn in (1.0, -1.0):
        st = sf_stats(sgn * S_pos[m])
        res[sgn] = {s: np.abs(st[s].values - paths.loc[m, f"{s}_{label}"].values) for s in ("MIN_SF", "AVG_SF", "MAX_SF")}
    score = {s: np.mean([(res[s][k] < 1e-3).mean() for k in res[s]]) for s in res}
    sign = 1.0 if score[1.0] >= score[-1.0] else -1.0
    st = sf_stats(sign * S_pos[m])
    row = {"constraint": label, "pathopt_direction": direction, "sign_applied": sign, "n_paths": int(m.sum()),
           "bpc_exact_match": float((st["BINDINGPAIRCOUNT"].values == paths.loc[m, f"BINDINGPAIRCOUNT_{label}"].values).mean())}
    for s in ("MIN_SF", "AVG_SF", "MAX_SF"):
        d = res[sign][s]
        row[f"{s}_within_1e-3"] = float((d < 1e-3).mean())
        row[f"{s}_within_1e-4"] = float((d < 1e-4).mean())
        row[f"{s}_max_abs_diff"] = float(np.nanmax(d))
    row["sign_match_if_flipped"] = float(score[-sign])
    return row, sign


def dedup_multi(paths: pd.DataFrame, cols: list[str], decimals: int = 5, order: list[str] | None = None) -> pd.DataFrame:
    """Collapse electrical aliases (identical rounded `cols`); keep the first row under `order`
    (default alphabetical; pass OPTIONPRICE first for cheapest) with ALIASES / ALIAS_COUNT."""
    p = paths.sort_values(order or ["SOURCENAME", "SINKNAME"]).copy()
    lab = p["SOURCENAME"] + "→" + p["SINKNAME"]
    if "OPTIONPRICE" in p and "OPTIONPRICE" not in cols:
        lab = lab + "($" + p["OPTIONPRICE"].round(2).astype(str) + ")"
    p["_pair"] = lab
    p["_g"] = pd.util.hash_pandas_object(p[cols].round(decimals).fillna(-9e9), index=False).values
    cnt = p.groupby("_g")["_pair"].agg(ALIAS_COUNT="size", ALIASES=lambda s: "; ".join(s.head(12)) + (" ..." if len(s) > 12 else ""))
    out = p.drop_duplicates("_g").merge(cnt, left_on="_g", right_index=True).drop(columns=["_g", "_pair"])
    return out.reset_index(drop=True)


def add_families(df: pd.DataFrame, cols: list[str], member_col: str, tol: float = 0.015, show: int = 6,
                 max_rows: int = 6000) -> pd.DataFrame:
    """Greedy near-duplicate families. df sorted best-first; a row joins the first earlier family representative whose
    `cols` all agree within `tol` (max abs diff), else starts a new family. Adds FAMILY (1 = best), FAMILY_RANK
    (1 = best member), FAMILY_SIZE, FAMILY_MEMBERS. Only the first `max_rows` rows are grouped (rest get FAMILY NaN)."""
    d = df.copy()
    X = d[cols].fillna(-9e3).to_numpy(dtype=np.float32)[:max_rows]
    reps = np.empty((0, len(cols)), dtype=np.float32)
    fam = np.empty(len(X), dtype=np.int64)
    for i, x in enumerate(X):
        if len(reps):
            ok = np.flatnonzero((np.abs(reps - x) <= tol).all(axis=1))
        else:
            ok = []
        if len(ok):
            fam[i] = ok[0] + 1
        else:
            reps = np.vstack([reps, x]); fam[i] = len(reps)
    d["FAMILY"] = pd.Series(fam, index=d.index[:len(X)]).reindex(d.index)
    g = d.groupby("FAMILY")[member_col]
    d["FAMILY_RANK"] = g.cumcount() + 1
    d["FAMILY_SIZE"] = g.transform("size")
    d["FAMILY_MEMBERS"] = d["FAMILY"].map(g.agg(lambda s: "; ".join(s.head(show)) + (" ..." if len(s) > show else "")))
    return d


def add_value_columns(paths: pd.DataFrame, labels: list[str], required: list[str], sp_scale: dict[str, float]) -> pd.DataFrame:
    """VALUE_<lab> = sp_scale[lab] * SHADOWPRICEPRECENT_<lab>/100 ($/MWh on-peak, that constraint only).

    SHADOWPRICEPRECENT ~ SP-weighted average path SF in percent (reconstruction corr 0.996), and
    sp_scale = mean SP over ALL on-peak runs of the PathOpt study (zero where not enforced), so
    E[SP*SF] ~= sp_scale * SP-weighted SF. Proxy for the listed constraints only."""
    p = paths.copy()
    for lab in labels:
        p[f"VALUE_{lab}"] = sp_scale[lab] * p[f"SHADOWPRICEPRECENT_{lab}"].fillna(0) / 100.0
    p["VALUE_REQ"] = p[[f"VALUE_{l}" for l in required]].sum(axis=1)
    p["VALUE_ALL"] = p[[f"VALUE_{l}" for l in labels]].sum(axis=1)
    return p


def rank_single(paths: pd.DataFrame, required: list[str], floor: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Balanced long-all filter: live-period MIN_SF >= floor on EVERY required constraint.
    Returns (paid_to_take, candidates sorted by NET = VALUE_ALL - OPTIONPRICE); RATIO = VALUE_ALL / price."""
    p = paths.copy()
    mins = p[[f"MIN_SF_{l}" for l in required]]
    p["MIN_SF_REQ"] = mins.min(axis=1)
    p = p[(mins >= floor).all(axis=1)]
    ptt = p[p["OPTIONPRICE"] <= 0].copy()
    c = p[p["OPTIONPRICE"] > 0].copy()
    c["NET"] = c["VALUE_ALL"] - c["OPTIONPRICE"]
    c["RATIO"] = c["VALUE_ALL"] / c["OPTIONPRICE"]
    return ptt, c.sort_values("NET", ascending=False)


def find_pairs(pool: pd.DataFrame, S: dict[str, np.ndarray], required: list[str], floor: float,
               extra: list[str] | None = None, chunk: int = 50, value_col: str = "VALUE_REQ",
               per_mw: bool = False) -> pd.DataFrame:
    """Pairs (A,B) of pool paths, 1 MW each. Per-period combined SF = S_A + S_B (halved if per_mw);
    a period is live only if all four nodes are. Long = min over live periods >= floor on every required
    constraint. Rows of `pool` align with rows of each S[k]. Output A/B are pool positions."""
    n = len(pool)
    price, val = pool["OPTIONPRICE"].values, pool[value_col].values
    k_div = 2.0 if per_mw else 1.0
    rows = []
    for a0 in range(0, n, chunk):
        a1 = min(n, a0 + chunk)
        ok = np.ones((a1 - a0, n), dtype=bool)
        mins = {}
        for k in required:
            comb = (S[k][a0:a1, None, :] + S[k][None, :, :]) / k_div
            m = np.where(np.isnan(comb), np.inf, comb).min(axis=2)
            ok &= np.isfinite(m) & (m >= floor)
            mins[k] = m
        ia, ib = np.nonzero(ok)
        for i0, j in zip(ia, ib):
            i = i0 + a0
            if i >= j:
                continue
            r = {"A": i, "B": j}
            for k in required + list(extra or []):
                comb = (S[k][i] + S[k][j]) / k_div
                live = ~np.isnan(comb)
                r[f"MIN_SF_{k}"] = float(comb[live].min()) if live.any() else np.nan
                r[f"AVG_SF_{k}"] = float(comb[live].mean()) if live.any() else np.nan
            r["PRICE"], r[value_col] = float(price[i] + price[j]), float(val[i] + val[j])
            rows.append(r)
    out = pd.DataFrame(rows)
    if len(out):
        out["NET"] = out[value_col] - out["PRICE"]
        out["NET_PER_MW"] = out["NET"] / 2.0
        out["RATIO"] = out[value_col] / out["PRICE"].where(out["PRICE"] > 0)
        out["MIN_SF_REQ"] = out[[f"MIN_SF_{k}" for k in required]].min(axis=1)
        out = out.sort_values("NET", ascending=False).reset_index(drop=True)
    return out


def _short_name(label: str) -> str:
    return re.sub(r"\d+[A-Z]?$", "", label)


def _date_range_text(dates: list[str]) -> str:
    d = sorted(pd.to_datetime(dates))
    a, b = d[0], d[-1]
    if a == b:
        return f"{a:%b} {a.day}"
    return f"{a:%b} {a.day}-{b.day}" if a.month == b.month else f"{a:%b} {a.day}-{b:%b} {b.day}"


def _holiday_text(holidays: str | None) -> str:
    ds = [pd.Timestamp(x) for x in holidays.split(",")] if holidays else []
    return ", ".join(f"{d:%b} {d.day}" for d in ds) or "no holidays"


def build_multi_report(out, args, labels, required, runs, cfg, counts, price_cons, repro, sp_tab, ctx_sum, ov, cand, ptt,
                       pairs, corr_u, corr_o, both, floors, hs, per, floors_b, sp_scale, n_runs, fam, nm) -> None:
    """report.html + README.md for the N-run overlap analysis."""
    import plotly.io as pio
    out = Path(out)
    floor = args.min_sf_each
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
    fig_html = pio.to_html(fig, include_plotlyjs=True, full_html=False)

    fl = lambda v: f"{v:.4g}"
    tab = lambda df, cols, n=25: df[[c for c in cols if c in df]].head(n).to_html(index=False, float_format=fl, border=0, classes="t")
    h = lambda df: df.to_html(index=False, border=0, classes="t", float_format=fl)
    sc = (["SOURCENAME", "SINKNAME", "ALIAS_COUNT", "OPTIONPRICE"] + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels]
          + ["VALUE_REQ", "VALUE_ALL", "NET_REQ", "VO_SHARE", "SHORT_FLAG", "NET", "RATIO", "FAMILY", "FAMILY_SIZE"])
    pc = (["A_PATH", "B_PATH", "PRICE_2MW", "VALUE_ALL_2MW", "PRICE_PER_MW", "VALUE_ALL_PER_MW", "NET_PER_MW", "NET_REQ_PER_MW", "VO_SHARE", "SHORT_FLAG", "FAMILY", "FAMILY_SIZE"]
          + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels])
    reqtxt = ", ".join(required)
    vo = cand.head(10)["VO_SHARE"]
    po_study = int(cfg[labels[0]].STUDYID)
    hol = _holiday_text(args.holidays)
    n_words = {1: "one", 2: "two", 3: "three", 4: "four"}.get(len(required), str(len(required)))
    value_only = [l for l in labels if l not in required]
    vo_txt = f"; value-only legs ({', '.join(value_only)}) supply {vo.min():.0%}-{vo.max():.0%} of VALUE_ALL in the top 10 singles" if value_only and len(vo) else ""
    bind_dates = lambda l: per.loc[per[f"SPSUM_{l}"] > 0, "DATES"].str.split(",").explode().tolist()
    lines = [f"- NET ranks on VALUE_ALL (signed sum over all legs). NET_REQ = VALUE_REQ - price counts the {n_words} required constraint{'s' if len(required) != 1 else ''} only{vo_txt}."]
    if {"BLESSING1382", "JCKSTP18A", "JCKREF27A", "STPHLJ_DHLJNHK5", "STPHLJ_SHLJSTP5"} <= set(labels):  # 14966 analysis
        pn = cand[cand["SOURCENAME"] == "PCT_RN"].head(1)
        lines.append(f"- Blessing is a passenger on the PCT_RN->BRP family (BLESSING1382 MIN_SF ~{pn['MIN_SF_BLESSING1382'].iloc[0] if len(pn) else float('nan'):.3f}, just above the {floor} floor): the NET there comes from JCK and the STP-Hillje legs.")
    lines.append(f"- SP value scale comes from study {po_study} (the PathOpt study): mean SP over its {n_runs} on-peak runs ({hol} excluded), zero where not enforced. binding_summary.csv / binding_runs.csv come from study {args.study}. Scale rests on few SP runs for some legs ({', '.join(f'{r.constraint}: {int(r.n_runs_with_sp)}' for r in sp_tab.itertuples())}). value_k = scale_k x stored SHADOWPRICEPRECENT_k/100 where the path is in that PathOpt run, reconstructed from set SFs only as fallback.")
    lines.append("- Value covers only the listed constraints and on-peak only; the path's other congestion is NOT included.")
    live_txt = ", ".join(f"{l} live {int(per[f'LIVE_{l}'].sum())}" if i == 0 else f"{l} {int(per[f'LIVE_{l}'].sum())}" for i, l in enumerate(required[:2]))
    cobind = f"MIN_SF is a stress statistic over the constraint's live topology periods (at most {len(per)}; {live_txt}), not a probability of earning."
    unbound = [l for l in required if not bind_dates(l)]
    if unbound:
        cobind += f" No binding period for {', '.join(unbound)}."
    if len(required) >= 2 and not unbound:
        la, lb = required[0], required[1]
        n_co = int(((per[f"SPSUM_{la}"] > 0) & (per[f"SPSUM_{lb}"] > 0)).sum())
        if n_co == 0:
            ranges = ", ".join(f"{_short_name(l)} {_date_range_text(bind_dates(l))}"
                               for l in sorted((lb, la), key=lambda l: min(bind_dates(l))))
            cobind += f" {la} and {lb} never co-bind ({ranges}), yet the filter requires both."
        else:
            cobind += f" {la} and {lb} co-bind in {n_co} of {len(per)} periods."
    lines.append("- " + cobind)
    if args.holidays:
        lines.append(f"- {hol}: holiday filter effect {hs}. The {hol} topology is one of the {len(per)} PathOpt periods; no binding runs fall on it.")
    lines.append(f"- Dedup: aliases collapsed on MIN/AVG SF of every leg at 3 dp (cheapest kept); FAMILY groups rows whose per-leg MIN and AVG SFs all agree within 0.015 of the family leader{' (e.g. PAVLOV_BT_RN/PAVLOV_RN, BRP_BRAZ_RN/BRPANGLE_RN)' if 'BLESSING1382' in labels else ''}.")
    lines.append(f"- Pairs: PRICE_2MW and VALUE_ALL_2MW are totals for 2 MW (1 MW each leg); per-MW = half; SF halved to per-MW before the filter; complementary only (neither leg passes alone). Pool = top {args.pool} per constraint by value per $, so the search is not exhaustive. Pair values are additive.")
    caveats = "\n".join(lines)
    html = f"""<html><head><meta charset="utf-8"><title>Multi-constraint paths</title><style>
body{{font-family:sans-serif;max-width:1400px;margin:20px auto}} table.t{{border-collapse:collapse;font-size:12px}}
table.t td,table.t th{{border:1px solid #ccc;padding:2px 6px}} h2{{margin-top:30px}}</style></head><body>
<h1>Paths long {reqtxt} @ {cfg[labels[0]].CTGLABEL} (on-peak)</h1>
<p>PathOpt runs: {', '.join(f'{l}={runs[l]}' for l in labels)} (study {int(cfg[labels[0]].STUDYID)}, PRICECLASS 2). Filter: live-period MIN_SF &gt;= {floor} on EVERY required constraint ({reqtxt}).
Ranked by NET = VALUE_ALL - OPTIONPRICE, where VALUE_ALL is the signed sum over all legs (required + co-binders).
SHORT_FLAG = a non-required binding leg has AVG_SF &lt; -0.02.</p>
<h2>Balanced-filter counts (overlap of required runs)</h2><p>Live-period MIN floor: {floors}. Binding-period MIN: {floors_b}. Holiday: {hs}</p>
<h2>Top single families (best member per ~2 dp SF family)</h2>{tab(fam, sc + ["FAMILY_MEMBERS"], 15)}
<h2>Near-miss families (pass all required floors but one, which is in [{0.4*floor:.3f}, {floor}))</h2>{tab(nm, sc + ["FAILING_LEG", "FAMILY_MEMBERS"], 10)}
<h2>Top single paths</h2>{tab(cand, sc)}
<h2>Top complementary pairs (PRICE_2MW / VALUE_ALL_2MW are totals for 2 MW; per-MW columns = half)</h2>{tab(pairs, pc + ["MEMBER"]) if len(pairs) else 'none'}
<h2>Paid-to-take: {len(ptt)}</h2>{tab(ptt, sc, 10) if len(ptt) else ''}
<h2>Scatter</h2>{fig_html}
<h2>Directional compatibility: AVG_SF correlation, overlap of required runs</h2>{corr_o.round(3).to_html(border=0, classes='t')}
<h2>Same, all union paths</h2>{corr_u.round(3).to_html(border=0, classes='t')}
<h2>On-peak periods</h2>{h(per)}
<h2>Overlap counts</h2>{h(counts)}<p>OPTIONPRICE consistency: {price_cons.to_dict('records')[0]}</p>
<h2>Reproduction of PathOpt stats from set shift factors</h2>{h(repro)}
<h2>Study {args.study} context (secondary)</h2>{h(ctx_sum) if ctx_sum is not None else 'n/a'}
<h2>SP scale</h2>{h(sp_tab)}
<h2>Caveats</h2><pre>{caveats}</pre></body></html>"""
    (out / "report.html").write_text(html)

    def md(df, cols, n):
        d = df[[c for c in cols if c in df]].head(n)
        lines = ["| " + " | ".join(d.columns) + " |", "|" + "---|" * len(d.columns)]
        for _, r in d.iterrows():
            lines.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |")
        return "\n".join(lines)

    sc_md = ["SOURCENAME", "SINKNAME", "OPTIONPRICE"] + [f"MIN_SF_{l}" for l in labels] + [f"AVG_SF_{l}" for l in labels] + ["VALUE_ALL", "NET", "SHORT_FLAG"]
    pc_md = ["A_PATH", "B_PATH", "PRICE_2MW", "VALUE_ALL_2MW", "PRICE_PER_MW", "VALUE_ALL_PER_MW", "NET_PER_MW", "NET_REQ_PER_MW", "VO_SHARE", "FAMILY_SIZE"] + [f"MIN_SF_{l}" for l in labels]
    (out / "README.md").write_text(f"""# Multi-constraint path search: {reqtxt}

Command (from {config.PROJECT_ROOT.parent}):

```
uv run --with "pyopenssl>=26.4" --project powerflow_analytics python powerflow_analytics/scripts/pathopt_scatter.py \\
  --study {args.study} --out-dir {out} --min-sf-each {floor} --pool {args.pool} --holidays {args.holidays} \\
  --runs {args.runs} --value-only {args.value_only} --required {','.join(required)} --constraints {args.constraints}
```

Filter: live-period MIN_SF >= {floor} on every required constraint (counts at 0.05 / 0.10: {floors.get(0.05)} / {floors.get(0.1)} overlap paths).
Rank: NET = VALUE_ALL - OPTIONPRICE.

## Top 3 single families (best member; members listed in candidates_families.csv)
{md(fam, sc_md + ["NET_REQ", "VO_SHARE", "FAMILY_SIZE", "FAMILY_MEMBERS"], 3)}

## Top 5 single paths
{md(cand, sc_md + ["NET_REQ", "VO_SHARE"], 5)}

## Near-miss (fails exactly one required floor)
{md(nm, sc_md + ["FAILING_LEG", "NET_REQ"], 3)}

## Top 3 complementary pair families (PRICE_2MW / VALUE_ALL_2MW are 2-MW totals)
{md(pairs[pairs["FAMILY_RANK"] == 1], pc_md, 3) if len(pairs) else 'none'}

## Caveats
{caveats}

Files: report.html, candidates_single.csv, candidates_pairs.csv, paths_all.parquet, reproduction_check.csv, overlap_counts.csv,
periods.csv, pathopt_study_sp_scale.csv, binding_runs.csv, binding_summary.csv.
Legacy 2-run mode (`--run-x/--run-y/--date/--hour`) is unchanged.
""")


def build_spread_report(out, args, dirs, res, comp, co_live, sp_scale, n_runs, floor, labels, live_cols,
                        po_study: int) -> None:
    """report.html + README.md for the long-A / short-B spread search."""
    out = Path(out)
    fl = lambda v: f"{v:.4g}"
    h = lambda df: df.to_html(index=False, border=0, classes="t", float_format=fl)
    sec, md = [], []
    for (L, Sh), r in res.items():
        cand = r["cand"]
        fam = cand[cand["FAMILY_RANK"] == 1]
        cols = (["SOURCENAME", "SINKNAME", "OPTIONPRICE", f"MIN_SF_{L}", f"AVG_SF_{L}"] + [f"MAXB_SF_{l}" for l in Sh] + [f"MAX_SF_{l}" for l in Sh] + [f"AVGB_SF_{l}" for l in Sh]
                + ["VALUE_LONG", "VALUE_SHORT", "VALUE_OBLIG", "VALUE_ALL_OPT", "NET_OPT", "RATIO", "PRICE_PER_LONG_SF", "SHORT_FLAG", "FAMILY_SIZE", "FAMILY_MEMBERS"])
        cheap = cand[cand[f"MIN_SF_{L}"] >= 0.10].sort_values("OPTIONPRICE").head(10)
        sec.append(f"<h2>Long {L} / short {', '.join(Sh)}</h2><p>Universe (run {L} paths with price&gt;0): {r['n_universe']:,}. Counts by floor "
                   f"(long_only = long live MIN&gt;=floor; short_live_basis also needs short MAX over ALL its live periods &lt;=-floor; short_binding_basis needs short MAX over its BINDING periods &lt;=-floor, the basis used for ranking): {r['cnt']}. Pooled path-SF correlation long vs short "
                   f"(periods live for both): {r['path_corr']:.3f} over {r['n_shared_obs']:,} obs; opposite-sign share {r['frac_opposite_sign']:.1%}.</p>"
                   f"<h3>Top families by NET_OPT = VALUE_LONG - price</h3>{h(fam[[c for c in cols if c in fam]].head(15))}"
                   f"<h3>Cheapest with long MIN &gt;= 0.10</h3>{h(cheap[[c for c in cols if c in cheap]])}")
        md.append(f"### Long {L} / short {', '.join(Sh)}\nUniverse {r['n_universe']:,}; pass counts by floor {r['cnt']}; pooled path-SF corr {r['path_corr']:.3f}.\n")
        d = fam[[c for c in cols if c in fam and c != 'FAMILY_MEMBERS']].head(5)
        md.append("| " + " | ".join(d.columns) + " |\n|" + "---|" * len(d.columns) + "\n" + "\n".join(
            "| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in row) + " |" for row in d.itertuples(index=False)) + "\n")
    hol = _holiday_text(args.holidays)
    L0, Sh0 = next(iter(res))
    pair = f"{L0} and {Sh0[0]}"
    live_txt = ", ".join(f"{l} {int(live_cols[l].sum()) if l in live_cols else '?'}/{len(next(iter(live_cols.values())))}" for l in (L0, *Sh0))
    prefix = os.path.commonprefix([L0, *Sh0]) or "Path"
    other_legs = ", ".join(l for l in labels if l not in {L0, *Sh0})
    caveats = f"""- Short leg tested on MAX_SF over its BINDING periods (study {po_study} SP>0) <= -{floor} (the strict all-live-period test passes 0 paths, see counts: the two constraints are near-collinear in the topologies where both are live); long leg = MIN_SF >= {floor} on the basis given by --long-basis ({args.long_basis}). Universe is the long leg's PathOpt run (MAX_SF>0 there); short-leg SFs come from its own topology set.
- VALUE_LONG = long-leg value only (option view: no cost to the short leg in hours when only the other constraint binds, valid because {pair} never co-bind). VALUE_OBLIG = signed sum incl. the short leg (obligation view). VALUE_ALL_OPT = exact per-run payoff max(0, sum over ALL legs SP x SF) over {n_runs} on-peak runs ({hol} excluded), study {po_study} shadow prices; computed for the top 3000 rows only.
- Other legs ({other_legs}) are info only (SHORT_FLAG: AVG_SF < -0.02 while binding); they are not in NET_OPT. SP scale = study {po_study} mean over {n_runs} runs, zero-imputed: {', '.join(f'{k} {v:.2f}' for k, v in sp_scale.items())}.
- Value counts only the listed constraints, on-peak only. MIN/MAX are stress statistics over live topologies ({live_txt}), not probabilities. {hol} effect not separately tested here.
- Thesis test: comparison.csv gives price per unit long AVG_SF for short-passing vs long-only paths in matched AVG_SF bands; families group paths within 0.015 on every leg's MIN/AVG SF."""
    html = f"""<html><head><meta charset="utf-8"><style>body{{font-family:sans-serif;max-width:1400px;margin:20px auto}} table.t{{border-collapse:collapse;font-size:12px}}
table.t td,table.t th{{border:1px solid #ccc;padding:2px 6px}}</style></head><body><h1>{prefix} spread: long one leg / short the other</h1>
<h2>Co-live topologies and collinearity</h2>{h(co_live)}{''.join(sec)}<h2>Price per unit long SF: short-passing vs long-only</h2>{h(comp)}<h2>Caveats</h2><pre>{caveats}</pre></body></html>"""
    (out / "report.html").write_text(html)
    (out / "README.md").write_text(f"""# {prefix} spread search (long A / short B, both directions)

```
uv run --with "pyopenssl>=26.4" --project powerflow_analytics python -u powerflow_analytics/scripts/pathopt_scatter.py --study {args.study} \\
  --out-dir {out} --min-sf-each {floor} --runs {args.runs} --value-only {args.value_only} --required {args.required} --short {args.short} \\
  --constraints {args.constraints}
```

{''.join(md)}
Co-live / collinearity: co_live.csv. Thesis test: comparison.csv.

## Caveats
{caveats}
""")
