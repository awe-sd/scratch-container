"""Path search analysis: find paths that are LONG the required constraints and CHEAP.

Path SF = psens(source) - psens(sink). Positive SF = long (path earns when that constraint binds).
Three searches return result objects (frames + the facts the reports state); pages and files are written by pfa.report / pfa.cli:
run_multi (N PathOpt runs, overlap + pairs), run_spread (long A / short B), run_pair (legacy two-run scatter).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..constraint_id import ConstraintId
from ..extract import popt, shifts

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


# ---------------------------------------------------------------------------
# N-run generalisation: overlap of several PathOpt runs, per-period SFs from the
# runs' topology shift sets, PathOpt-stat reproduction, ranking, pair search.
# PathOpt convention (reproduced to 1e-3, see reproduction_check): a period is a
# distinct psenshift in the set holding >=1 weekday SIMHOUR 7-22 run (holidays NOT
# excluded); stats are over periods where BOTH path nodes have DEADBUS=0 (that
# count is BINDINGPAIRCOUNT). Stored psens are already oriented to the binding direction.
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Searches: each returns a result object (frames + the facts the reports state); files and pages are written elsewhere.
# ---------------------------------------------------------------------------
_NOLOG = lambda *a, **k: None  # noqa: E731


def parse_label_map(txt: str | None) -> dict[str, int]:
    """'A=1,B=2' -> {'A': 1, 'B': 2}."""
    return {k: int(v) for k, v in (x.split("=") for x in (txt or "").split(",") if x)}


def parse_constraints(txt: str | None) -> dict[str, tuple]:
    """'A=F-T-CKT@CTG,...' -> {'A': (fromnum, tonum, ckt, ctglabel)}."""
    cons = {}
    for x in (txt or "").split(","):
        if x:
            lab, c = x.split("=")
            cid = ConstraintId.parse(c)
            cons[lab] = (cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel)
    return cons


@dataclass
class PathSpec:
    """Inputs of an N-run / spread search (PathOpt runs by label, the study's constraint per label, floors, holidays)."""
    study: int
    runs: dict[str, int]
    value_only: dict[str, int]
    constraints: dict[str, tuple]
    required: list[str]
    short: list[str] = field(default_factory=list)
    floor: float = 0.05
    pool: int = 300
    holidays: frozenset = frozenset()
    long_basis: str = "live"
    short_basis: str = "binding"

    @classmethod
    def from_strings(cls, *, study: int, runs: str, value_only: str | None, required: str | None, short: str | None,
                     constraints: str | None, floor: float, pool: int, holidays: str | None,
                     long_basis: str = "live", short_basis: str = "binding") -> "PathSpec":
        run_map = parse_label_map(runs)
        req = required.split(",") if required else list(run_map)[:-1]
        return cls(study, run_map, parse_label_map(value_only), parse_constraints(constraints), req,
                   short.split(",") if short else [], floor, pool,
                   frozenset(holidays.split(",")) if holidays else frozenset(), long_basis, short_basis)

    @property
    def labels(self) -> list[str]:
        return list(self.runs)

    @property
    def all_labels(self) -> list[str]:
        return list(self.runs) + list(self.value_only)

    @property
    def all_runs(self) -> dict[str, int]:
        return {**self.runs, **self.value_only}


def holiday_binding(ctx_sum: pd.DataFrame | None, per: pd.DataFrame, labels: list[str], holidays) -> dict:
    """Binding runs that fall on a listed holiday: the study's on-peak binding runs when available, else PathOpt periods with SP>0."""
    if ctx_sum is not None:
        by = {r.constraint: int(r.onpeak_binding_on_holiday) for r in ctx_sum.itertuples()}
        return {"basis": "runs", "by_leg": by, "total": int(sum(by.values()))}
    by = {}
    for l in labels:
        dates = per.loc[per[f"SPSUM_{l}"] > 0, "DATES"].str.split(",")
        by[l] = int(sum(bool(set(d) & set(holidays)) for d in dates))
    return {"basis": "periods", "by_leg": by, "total": int(sum(by.values()))}


@dataclass
class MultiResult:
    spec: PathSpec
    po_study: int
    ctg_label: str
    n_runs: int
    n_periods: int
    holiday_periods: list
    holiday_binding: dict
    counts: pd.DataFrame
    price_cons: pd.DataFrame
    repro: pd.DataFrame
    sp_tab: pd.DataFrame
    ctx_sum: pd.DataFrame | None
    per: pd.DataFrame
    ov: pd.DataFrame
    cand: pd.DataFrame
    fam: pd.DataFrame
    nm: pd.DataFrame
    ptt: pd.DataFrame
    pairs: pd.DataFrame
    corr_u: pd.DataFrame
    corr_o: pd.DataFrame
    floors: dict
    floors_b: dict
    hs: dict
    sp_scale: dict
    csvs: dict          # file name -> frame (written index=False)


def run_multi(spec: PathSpec, log=_NOLOG) -> MultiResult:
    """Overlap of several PathOpt runs: per-period path SFs, PathOpt-stat reproduction, value columns, single and pair ranking."""
    runs, vruns = spec.runs, spec.value_only
    labels, alll, required = spec.labels, spec.all_labels, spec.required
    floor, hol, cons = spec.floor, set(spec.holidays), spec.constraints
    cfg = {l: popt.get_run_config(r) for l, r in spec.all_runs.items()}

    mem = {l: popt.get_topology_set_members(cfg[l].TOPOLOGYSHIFTSETID) for l in alll}
    onp = {l: onpeak_members(mem[l]) for l in alll}
    topo = sorted(set.intersection(*[set(onp[l]["TOPOLOGYID"]) for l in alll]))
    assert all(set(onp[l]["TOPOLOGYID"]) == set(topo) for l in alll), "on-peak topologies differ between runs"
    ps_of = {l: onp[l].drop_duplicates("TOPOLOGYID").set_index("TOPOLOGYID")["PSENSHIFTID"].reindex(topo) for l in alll}
    topo_date = onp[labels[0]].groupby("TOPOLOGYID")["SIMDATE"].agg(lambda s: sorted(set(pd.to_datetime(s).dt.strftime("%Y-%m-%d"))))
    hol_cols = [i for i, t in enumerate(topo) if hol & set(topo_date[t])]
    keep_cols = [i for i in range(len(topo)) if i not in hol_cols]
    log(f"{len(topo)} on-peak periods; holiday periods {[topo[i] for i in hol_cols]}")

    cols = ["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME", "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE",
            "MIN_SF", "AVG_SF", "MAX_SF", "SHADOWPRICEPRECENT", "BINDINGPAIRCOUNT"]
    details = {l: popt.fetch_detail(spec.all_runs[l], cols) for l in alll}
    for d in details.values():
        for c in ("MIN_SF", "AVG_SF", "MAX_SF", "SHADOWPRICEPRECENT", "SOURCEBUSKV", "SINKBUSKV"):
            d[c] = d[c].astype("float32")
        d["BINDINGPAIRCOUNT"] = d["BINDINGPAIRCOUNT"].astype("int16")
    U, price_cons = overlap_runs(details, required)
    del details
    counts = overlap_counts(U, labels, required)
    log(counts.to_string(index=False)); log(price_cons.to_string(index=False))

    S, repro, live_cols = {}, [], {}
    for l in alll:
        n = shifts.node_shift_factors_multi(list(ps_of[l].values))
        ps2t = dict(zip(ps_of[l].values, topo))
        n["T"] = n["PSENSHIFTID"].map(ps2t)
        P = n.pivot(index="CPNODEID", columns="T", values="PSENS")[topo]
        D = n.pivot(index="CPNODEID", columns="T", values="DEADBUS")[topo]
        S0 = path_sf_matrix(U, P, D)
        row, sign = reproduction_check(U, S0, l, cfg[l].DIRECTION)
        repro.append(row)
        S[l] = sign * S0
        live_cols[l] = (P.abs().max(axis=0) > 1e-3).values
        del n, P, D
    repro = pd.DataFrame(repro)
    log(repro.T.to_string())

    o0 = onp[labels[0]]
    runids = sorted(set(o0.loc[~pd.to_datetime(o0["SIMDATE"]).dt.strftime("%Y-%m-%d").isin(hol), "RUNID"]))
    n_runs = len(runids)
    sp_scale, weights, sp_rows = {}, {}, []
    for l in alll:
        f, t, ckt, ctg = cons[l]
        sp = popt.fetch_constraint_sp(runids, f, t, ckt, ctg).set_index("RUNID")["SP"].reindex(runids).fillna(0.0)
        r2t = onp[l].drop_duplicates("RUNID").set_index("RUNID")["TOPOLOGYID"]
        weights[l] = sp.groupby(r2t.reindex(runids).values).sum().reindex(topo).fillna(0.0).values
        sp_scale[l] = float(sp.sum() / n_runs)
        sp_rows.append({"constraint": l, "pathopt_study": int(cfg[l].STUDYID), "n_onpeak_runs_exholiday": n_runs,
                        "n_runs_with_sp": int((sp > 0).sum()), "mean_sp_when_present": float(sp[sp > 0].mean()) if (sp > 0).any() else 0.0,
                        "sp_scale_zero_imputed": sp_scale[l]})
    sp_tab = pd.DataFrame(sp_rows); log(sp_tab.to_string(index=False))

    # PathOpt MIN_SF spans all periods incl. topologies where the constraint carries no flow (psens all zero) -> pinned at 0.
    # Re-base on LIVE periods; MINB/AVGB = periods where the constraint binds in the PathOpt study. *_EXHOL drop holiday periods.
    per = pd.DataFrame({"TOPOLOGYID": topo, "DATES": [",".join(topo_date[t]) for t in topo]})
    for l in alll:
        bind = weights[l] > 0
        per[f"LIVE_{l}"], per[f"SPSUM_{l}"] = live_cols[l], weights[l]
        S[l] = np.where(live_cols[l][None, :], S[l], np.nan).astype(np.float32)
        st = sf_stats(S[l])
        stb = sf_stats(np.where(bind[None, :], S[l], np.nan))
        ste = sf_stats(S[l][:, keep_cols])
        for q in ("MIN_SF", "AVG_SF", "MAX_SF"):
            U[f"PO_{q}_{l}"] = U[f"{q}_{l}"]
            U[f"{q}_{l}"] = st[q].values
        U[f"MIN_SF_{l}_EXHOL"] = ste["MIN_SF"].values
        U[f"MINB_SF_{l}"], U[f"AVGB_SF_{l}"] = stb["MIN_SF"].values, stb["AVG_SF"].values
        U[f"NLIVE_{l}"], U[f"NBIND_{l}"] = st["BINDINGPAIRCOUNT"].values, stb["BINDINGPAIRCOUNT"].values
        log(f"{l}: live periods {int(live_cols[l].sum())}/{len(topo)}, binding periods {int(bind.sum())}")

    for l in alll:
        live = ~np.isnan(S[l]); w = weights[l][None, :] * live
        rec = 100 * (w * np.nan_to_num(S[l])).sum(1) / np.maximum(w.sum(1), 1e-12)
        m = U[f"IN_{l}"].values
        if m.any():
            c = np.corrcoef(rec[m], U.loc[m, f"SHADOWPRICEPRECENT_{l}"].values)[0, 1]
            repro.loc[repro.constraint == l, "spp_reconstruction_corr"] = c
        U[f"SHADOWPRICEPRECENT_{l}"] = np.where(m, U[f"SHADOWPRICEPRECENT_{l}"], rec)
    U = add_value_columns(U, alll, required, sp_scale)
    nonreq = [l for l in alll if l not in required]
    for l in nonreq:
        U[f"SHORT_{l}"] = (U[f"AVG_SF_{l}"] < -0.02) & (U[f"NBIND_{l}"] > 0)
    U["SHORT_FLAG"] = U[[f"SHORT_{l}" for l in nonreq]].any(axis=1)

    U = U.drop(columns=[c for c in U.columns if c.startswith("PO_")])
    f64 = [c for c in U.columns if U[c].dtype == "float64" and c != "OPTIONPRICE" and not c.startswith("VALUE")]
    U[f64] = U[f64].astype("float32")
    ov = U[np.logical_and.reduce([U[f"IN_{l}"] for l in required])].copy()
    mn = lambda frame, suf="": frame[[f"MIN_SF_{l}{suf}" for l in required]].min(axis=1)
    floors = {f: int((mn(ov) >= f).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
    floors_b = {f: int((ov[[f"MINB_SF_{l}" for l in required]].min(axis=1) >= f).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
    pa, pe = (mn(ov) >= floor), (mn(ov, "_EXHOL") >= floor)
    hs = {"floor": floor, "pass": int(pa.sum()), "lost_without_holiday": int((pa & ~pe).sum()), "gained_without_holiday": int((~pa & pe).sum())}
    log("overlap(required):", len(ov), "balanced filter counts", floors, "| binding-MIN", floors_b, "| holiday", hs)
    ov["MIN_SF_REQ"] = mn(ov)
    ptt, cand = rank_single(ov, required, floor)
    sfcols = [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF")]
    cand_d = dedup_multi(cand, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]) if len(cand) else cand
    cand_d["NET_REQ"] = cand_d["VALUE_REQ"] - cand_d["OPTIONPRICE"]
    cand_d["VO_SHARE"] = (cand_d["VALUE_ALL"] - cand_d["VALUE_REQ"]) / cand_d["VALUE_ALL"]
    cand_d = cand_d.sort_values("NET", ascending=False).reset_index(drop=True)
    cand_d["MEMBER"] = cand_d["SOURCENAME"] + "→" + cand_d["SINKNAME"] + "($" + cand_d["OPTIONPRICE"].round(2).astype(str) + ")"
    cand_d = add_families(cand_d, sfcols, "MEMBER")
    fam = cand_d[cand_d["FAMILY_RANK"] == 1].head(30)
    # near-miss: passes the floor on all required legs but one, which sits in [0.4*floor, floor)
    reqmin = ov[[f"MIN_SF_{l}" for l in required]]
    nfail = (reqmin < floor).sum(axis=1)
    nm = ov[(nfail == 1) & (reqmin.min(axis=1) >= 0.4 * floor) & (ov["OPTIONPRICE"] > 0)].copy()
    nm["FAILING_LEG"] = reqmin.loc[nm.index].idxmin(axis=1).str.replace("MIN_SF_", "")
    nm["NET"], nm["NET_REQ"] = nm["VALUE_ALL"] - nm["OPTIONPRICE"], nm["VALUE_REQ"] - nm["OPTIONPRICE"]
    nm["RATIO"] = nm["VALUE_ALL"] / nm["OPTIONPRICE"]
    nm = dedup_multi(nm, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]).sort_values("NET", ascending=False)
    nm["MEMBER"] = nm["SOURCENAME"] + "→" + nm["SINKNAME"] + "($" + nm["OPTIONPRICE"].round(2).astype(str) + ")"
    nm = add_families(nm, sfcols, "MEMBER")
    nm_f = nm[nm["FAMILY_RANK"] == 1].head(15)
    ptt_d = dedup_multi(ptt, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]) if len(ptt) else ptt
    keepcols = (["SOURCENAME", "SINKNAME", "ALIAS_COUNT", "ALIASES", "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE"]
                + [f"{s}_{l}" for l in alll for s in ("MIN_SF", "AVG_SF", "MAX_SF")]
                + [f"MIN_SF_{l}_EXHOL" for l in alll] + [f"MINB_SF_{l}" for l in required]
                + [f"VALUE_{l}" for l in alll] + ["VALUE_REQ", "VALUE_ALL", "SHORT_FLAG", "MIN_SF_REQ", "NET", "NET_REQ", "VO_SHARE", "RATIO",
                                             "FAMILY", "FAMILY_RANK", "FAMILY_SIZE", "FAMILY_MEMBERS"])
    single = cand_d[[c for c in keepcols if c in cand_d]].head(50)
    log(f"single candidates (floor {floor}): {len(cand)} raw, {len(cand_d)} distinct (3dp SF dedup); paid-to-take {len(ptt_d)}")

    # pairs over the union; S comes from node psens so paths PathOpt dropped for a run still count
    in_req = np.logical_or.reduce([U[f"IN_{l}"] for l in required]) & (U["OPTIONPRICE"] > 0)
    ridx = np.flatnonzero(in_req.values)
    Uq = U.iloc[ridx]
    sigm = np.round(np.hstack([S[k][ridx] for k in alll]), 3)
    sig = pd.util.hash_pandas_object(pd.DataFrame(sigm).fillna(-9e9), index=False).values
    pool_idx = set()
    for key in [f"VALUE_{l}" for l in required] + ["VALUE_ALL"]:
        r = (Uq[key] / Uq["OPTIONPRICE"]).values
        d = pd.DataFrame({"r": r, "sig": sig, "i": np.arange(len(Uq))}).sort_values("r", ascending=False).drop_duplicates("sig")
        pool_idx |= set(d.head(spec.pool)["i"])
    pool_pos = np.array(sorted(pool_idx))
    pool = Uq.iloc[pool_pos].reset_index(drop=True)
    Sp = {k: S[k][ridx][pool_pos] for k in alll}
    log("pair pool:", len(pool))
    pairs = find_pairs(pool, Sp, required, floor, extra=nonreq, value_col="VALUE_ALL", per_mw=True)
    pool["PASS_ALONE"] = (pool[[f"MIN_SF_{l}" for l in required]] >= floor).all(axis=1)
    if len(pairs):
        pairs = pairs[~(pool["PASS_ALONE"].values[pairs["A"]] | pool["PASS_ALONE"].values[pairs["B"]])]
        pairs = pairs[pool["SOURCENAME"].values[pairs["A"]] + pool["SINKNAME"].values[pairs["A"]] != pool["SOURCENAME"].values[pairs["B"]] + pool["SINKNAME"].values[pairs["B"]]]
    if len(pairs):
        sh = np.zeros(len(pairs), dtype=bool)
        for l in nonreq:
            if (U[f"NBIND_{l}"] > 0).any():
                sh |= (pairs[f"AVG_SF_{l}"].values < -0.02) & bool(per[f"SPSUM_{l}"].gt(0).any())
        pairs["SHORT_FLAG"] = sh
        for side in ("A", "B"):
            pairs[f"{side}_PATH"] = pool.loc[pairs[side], "SOURCENAME"].values + "→" + pool.loc[pairs[side], "SINKNAME"].values
            pairs[f"{side}_PRICE"] = pool.loc[pairs[side], "OPTIONPRICE"].values
        pairs["VALUE_REQ"] = pool["VALUE_REQ"].values[pairs["A"]] + pool["VALUE_REQ"].values[pairs["B"]]
        pairs = pairs.drop(columns=["A", "B"]).drop_duplicates([c for c in pairs.columns if c.startswith(("MIN_SF_", "AVG_SF_"))] + ["PRICE"])
        pairs = pairs.rename(columns={"PRICE": "PRICE_2MW", "VALUE_ALL": "VALUE_ALL_2MW", "VALUE_REQ": "VALUE_REQ_2MW", "NET": "NET_2MW"})
        pairs["PRICE_PER_MW"], pairs["VALUE_ALL_PER_MW"] = pairs["PRICE_2MW"] / 2, pairs["VALUE_ALL_2MW"] / 2
        pairs["NET_REQ_PER_MW"] = (pairs["VALUE_REQ_2MW"] - pairs["PRICE_2MW"]) / 2
        pairs["VO_SHARE"] = 1 - pairs["VALUE_REQ_2MW"] / pairs["VALUE_ALL_2MW"]
        pairs = pairs.sort_values("NET_PER_MW", ascending=False).reset_index(drop=True)
        pairs["MEMBER"] = pairs["A_PATH"] + " + " + pairs["B_PATH"]
        pairs = add_families(pairs, [c for c in pairs.columns if c.startswith(("MIN_SF_", "AVG_SF_")) and c != "MIN_SF_REQ"], "MEMBER")
    log(f"complementary pairs: {len(pairs)}; best NET_PER_MW {pairs['NET_PER_MW'].max() if len(pairs) else None}; best single NET {cand_d['NET'].max() if len(cand_d) else None}")

    ctx, ctx_sum = None, None
    if cons and spec.study:
        sruns = popt.fetch_study_runs(spec.study)
        sruns["SIMDATE"] = pd.to_datetime(sruns["SIMDATE"])
        sruns["ONPEAK"] = (sruns["SIMDATE"].dt.dayofweek < 5) & sruns["SIMHOUR"].between(7, 22)
        sruns["HOLIDAY"] = sruns["SIMDATE"].dt.strftime("%Y-%m-%d").isin(hol)
        ctx = sruns.set_index("RUNID")
        summ = []
        n_on = int((ctx["ONPEAK"] & ~ctx["HOLIDAY"]).sum())
        for l in alll:
            f, t, ckt, ctg = cons[l]
            lv = popt.fetch_ctg_loading(spec.study, f, t, ckt, ctg).set_index("RUNID")["LIMVIOLPCT"]
            sp = popt.fetch_constraint_sp(list(ctx.index), f, t, ckt, ctg).set_index("RUNID")["SP"]
            ctx[f"LIMVIOLPCT_{l}"] = lv.reindex(ctx.index)
            ctx[f"SP_{l}"] = sp.reindex(ctx.index)
            b = ctx[f"LIMVIOLPCT_{l}"] >= 99.5
            ctx[f"BINDING_{l}"] = b
            on = ctx["ONPEAK"]
            summ.append({"constraint": l, "n_onpeak_runs_exholiday": n_on, "onpeak_binding_runs": int((b & on).sum()),
                         "onpeak_binding_on_holiday": int((b & on & ctx["HOLIDAY"]).sum()),
                         "binding_missing_sp": int((b & on & ctx[f"SP_{l}"].isna()).sum()),
                         "mean_sp_present": float(ctx.loc[b & on, f"SP_{l}"].mean()),
                         "mean_sp_zero_imputed_over_binders": float(ctx.loc[b & on, f"SP_{l}"].fillna(0).mean()),
                         "onpeak_mean_sp_all_runs_exholiday": float(ctx.loc[on & ~ctx["HOLIDAY"], f"SP_{l}"].fillna(0).sum() / n_on)})
        ctx_sum = pd.DataFrame(summ); log(ctx_sum.to_string(index=False))
    corr_u = pd.DataFrame({l: U[f"AVG_SF_{l}"] for l in alll}).corr()
    corr_o = pd.DataFrame({l: ov[f"AVG_SF_{l}"] for l in alll}).corr()
    log("AVG-SF corr on overlap(required)\n", corr_o.round(3).to_string())

    csvs = {"overlap_counts.csv": counts, "pathopt_study_sp_scale.csv": sp_tab, "periods.csv": per,
            "reproduction_check.csv": repro, "candidates_families.csv": fam, "near_miss.csv": nm_f,
            "candidates_single.csv": single, "candidates_pairs.csv": pairs.head(50)}
    if len(pairs):
        csvs["candidates_pair_families.csv"] = pairs[pairs["FAMILY_RANK"] == 1].head(30)
    if ctx is not None:
        csvs["binding_runs.csv"] = ctx.reset_index()
        csvs["binding_summary.csv"] = ctx_sum
    return MultiResult(spec, int(cfg[labels[0]].STUDYID), cfg[labels[0]].CTGLABEL, n_runs, len(per),
                       [topo[i] for i in hol_cols], holiday_binding(ctx_sum, per, alll, hol), counts, price_cons, repro, sp_tab,
                       ctx_sum, per, ov, cand_d, fam, nm_f, ptt_d, pairs, corr_u, corr_o, floors, floors_b, hs, sp_scale,
                       csvs)


def _paths_all(self) -> pd.DataFrame:
    """The overlap frame as written to paths_all.parquet (WAVG_DOLLAR helper columns dropped)."""
    return self.ov.drop(columns=[c for c in self.ov.columns if c.startswith("WAVG_DOLLAR")])


MultiResult.paths_all = _paths_all


@dataclass
class SpreadDirection:
    long: str
    short: list[str]
    counts: dict
    n_universe: int
    cand: pd.DataFrame
    bm: pd.DataFrame
    mask_n: int
    path_corr: float
    n_shared_obs: int
    frac_opposite_sign: float
    cobind: dict
    csv_name: str
    families: pd.DataFrame


@dataclass
class SpreadResult:
    spec: PathSpec
    po_study: int
    n_runs: int
    n_periods: int
    directions: list
    comp: pd.DataFrame
    co_live: pd.DataFrame
    sp_scale: dict
    live_counts: dict
    csvs: dict


def spread_cobind(weights: dict, long: str, shorts: list[str]) -> dict:
    """Periods where the long leg and any short leg both have binding shadow price (SP sum > 0 in that PathOpt period)."""
    long_b = np.asarray(weights[long]) > 0
    short_b = np.logical_or.reduce([np.asarray(weights[s]) > 0 for s in shorts])
    return {"n_both": int((long_b & short_b).sum()), "n_periods": int(len(long_b)),
            "long_binds": int(long_b.sum()), "short_binds": int(short_b.sum())}


def run_spread(spec: PathSpec, log=_NOLOG) -> SpreadResult:
    """Long A / short B spread search (and the reverse): universe = PathOpt run A paths, B/other legs from their sets."""
    runs, vruns = spec.runs, spec.value_only
    alll = spec.all_labels
    longs, shorts = spec.required, spec.short
    assert len(longs) == 1, "spread mode: exactly one long leg per direction"
    dirs = [(longs[0], shorts)]
    if len(shorts) == 1:
        dirs.append((shorts[0], longs))
    floor, hol, cons = spec.floor, set(spec.holidays), spec.constraints
    cfg = {l: popt.get_run_config(r) for l, r in spec.all_runs.items()}
    mem = {l: popt.get_topology_set_members(cfg[l].TOPOLOGYSHIFTSETID) for l in alll}
    onp = {l: onpeak_members(mem[l]) for l in alll}
    topo = sorted(set.intersection(*[set(onp[l]["TOPOLOGYID"]) for l in alll]))
    ps_of = {l: onp[l].drop_duplicates("TOPOLOGYID").set_index("TOPOLOGYID")["PSENSHIFTID"].reindex(topo) for l in alll}
    o0 = onp[alll[0]]
    runids = sorted(set(o0.loc[~pd.to_datetime(o0["SIMDATE"]).dt.strftime("%Y-%m-%d").isin(hol), "RUNID"]))
    n_runs = len(runids)
    r2t = o0.drop_duplicates("RUNID").set_index("RUNID")["TOPOLOGYID"].reindex(runids)
    tidx = np.array([topo.index(t) for t in r2t.values])

    P, D, live_cols, sp_run, weights, sp_scale = {}, {}, {}, {}, {}, {}
    for l in alll:
        n = shifts.node_shift_factors_multi(list(ps_of[l].values))
        n["T"] = n["PSENSHIFTID"].map(dict(zip(ps_of[l].values, topo)))
        P[l] = n.pivot(index="CPNODEID", columns="T", values="PSENS")[topo]
        D[l] = n.pivot(index="CPNODEID", columns="T", values="DEADBUS")[topo]
        live_cols[l] = (P[l].abs().max(axis=0) > 1e-3).values
        f, t, ckt, ctg = cons[l]
        sp = popt.fetch_constraint_sp(runids, f, t, ckt, ctg).set_index("RUNID")["SP"].reindex(runids).fillna(0.0)
        sp_run[l] = sp.values
        weights[l] = sp.groupby(r2t.values).sum().reindex(topo).fillna(0.0).values
        sp_scale[l] = float(sp.sum() / n_runs)
        del n
    cols = ["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME", "OPTIONPRICE", "SHADOWPRICEPRECENT"]
    details = {l: popt.fetch_detail(spec.all_runs[l], cols) for l in alll}
    both_live = {}
    for a in alll:
        for b_ in alll:
            if a < b_:
                m = live_cols[a] & live_cols[b_]
                cs = []
                for ti in np.flatnonzero(m):
                    x = pd.concat([P[a].iloc[:, ti], P[b_].iloc[:, ti]], axis=1).dropna()
                    ok = (D[a].iloc[:, ti].reindex(x.index) == 0) & (D[b_].iloc[:, ti].reindex(x.index) == 0)
                    x = x[ok.values]
                    cs.append(np.corrcoef(x.iloc[:, 0], x.iloc[:, 1])[0, 1])
                both_live[(a, b_)] = (int(m.sum()), float(np.nanmean(cs)) if cs else float("nan"))

    comp, directions, csvs = [], [], {}
    for L, Sh in dirs:
        others = [l for l in alll if l != L and l not in Sh]
        U = details[L].copy().rename(columns={"SHADOWPRICEPRECENT": f"SPPSTORED_{L}"})
        U[f"SPPSTORED_{L}"] = U[f"SPPSTORED_{L}"].astype("float32")
        for l in alll:
            if l != L:
                d = details[l][["SOURCECPNODEID", "SINKCPNODEID", "SHADOWPRICEPRECENT"]].rename(columns={"SHADOWPRICEPRECENT": f"SPPSTORED_{l}"})
                d[f"SPPSTORED_{l}"] = d[f"SPPSTORED_{l}"].astype("float32")
                U = U.merge(d, on=["SOURCECPNODEID", "SINKCPNODEID"], how="left")
        S = {}
        for l in alll:
            Sl = path_sf_matrix(U, P[l], D[l])
            S[l] = np.where(live_cols[l][None, :], Sl, np.nan).astype(np.float32)
            st = sf_stats(S[l])
            for q in ("MIN_SF", "AVG_SF", "MAX_SF"):
                U[f"{q}_{l}"] = st[q].values
            stb = sf_stats(np.where((weights[l] > 0)[None, :], S[l], np.nan))
            U[f"MAXB_SF_{l}"], U[f"AVGB_SF_{l}"], U[f"MINB_SF_{l}"] = stb["MAX_SF"].values, stb["AVG_SF"].values, stb["MIN_SF"].values
            live = ~np.isnan(S[l]); w = weights[l][None, :] * live
            rec = 100 * (w * np.nan_to_num(S[l])).sum(1) / np.maximum(w.sum(1), 1e-12)
            U[f"VALUE_{l}"] = sp_scale[l] * np.where(U[f"SPPSTORED_{l}"].notna(), U[f"SPPSTORED_{l}"], rec) / 100.0
            U[f"NBIND_{l}"] = int((weights[l] > 0).sum())
        U["VALUE_LONG"] = U[f"VALUE_{L}"]
        U["VALUE_SHORT"] = U[[f"VALUE_{l}" for l in Sh]].sum(axis=1)
        U["VALUE_OBLIG"] = U["VALUE_LONG"] + U["VALUE_SHORT"]
        U["VALUE_OTHER_SIGNED"] = U[[f"VALUE_{l}" for l in others]].sum(axis=1)
        U["SHORT_FLAG"] = pd.concat([(U[f"AVG_SF_{l}"] < -0.02) & (U[f"NBIND_{l}"] > 0) for l in others], axis=1).any(axis=1)
        long_ok = lambda f: (U[f"MINB_SF_{L}" if spec.long_basis == "binding" else f"MIN_SF_{L}"] >= f) & (U["OPTIONPRICE"] > 0)
        short_ok = lambda f, basis=spec.short_basis: (U[[(f"MAXB_SF_{l}" if basis == "binding" else f"MAX_SF_{l}") for l in Sh]] <= -f).all(axis=1)
        cnt = {f: {"long_only": int(long_ok(f).sum()), "short_live_basis": int((long_ok(f) & short_ok(f, "live")).sum()),
                   "short_binding_basis": int((long_ok(f) & short_ok(f, "binding")).sum())} for f in (0.02, 0.05, 0.10)}
        cnt_b = {f: int(((U[f"MINB_SF_{L}"] >= f) & (U["OPTIONPRICE"] > 0) & short_ok(f, "binding")).sum()) for f in (0.0, 0.02, 0.05, 0.10)}
        q = U.loc[long_ok(floor), [f"MAXB_SF_{l}" for l in Sh]].min(axis=1)
        log(f"{L}: both legs on BINDING-period basis (long MINB>=f & short MAXB<=-f): {cnt_b}; short MAXB among long-pass paths: min {q.min():.3f}, p1 {q.quantile(.01):.3f}, p10 {q.quantile(.1):.3f}")
        mask = (long_ok(floor) & short_ok(floor)).values
        cand = U[mask].copy()
        cand["NET_OPT"] = cand["VALUE_LONG"] - cand["OPTIONPRICE"]
        cand["RATIO"] = cand["VALUE_LONG"] / cand["OPTIONPRICE"]
        cand["PRICE_PER_LONG_SF"] = cand["OPTIONPRICE"] / cand[f"AVG_SF_{L}"]
        sfcols = [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF")]
        cand = dedup_multi(cand, sfcols, decimals=3, order=["OPTIONPRICE", "SOURCENAME", "SINKNAME"]).sort_values("NET_OPT", ascending=False).reset_index(drop=True)
        cand["MEMBER"] = cand["SOURCENAME"] + "→" + cand["SINKNAME"] + "($" + cand["OPTIONPRICE"].round(2).astype(str) + ")"
        cand = add_families(cand, sfcols, "MEMBER")
        # exact per-run option value over ALL legs (floor at 0 per hour) for the top rows; needs S rows of those paths
        top = cand.head(3000)
        Ut = top[["SOURCECPNODEID", "SINKCPNODEID"]]
        tot = np.zeros((len(Ut), n_runs)); tot_long = np.zeros_like(tot)
        for l in alll:
            Sl = path_sf_matrix(Ut, P[l], D[l])
            Sl = np.where(live_cols[l][None, :], Sl, np.nan)
            contrib = np.nan_to_num(Sl[:, tidx]) * sp_run[l][None, :]
            tot += contrib
            if l == L:
                tot_long = contrib
        cand.loc[top.index, "VALUE_ALL_OPT"] = np.maximum(tot, 0).sum(1) / n_runs
        cand.loc[top.index, "VALUE_LONG_RUNMEAN"] = np.maximum(tot_long, 0).sum(1) / n_runs
        cand["VALUE_ALL_OPT_MINUS_LONG"] = cand["VALUE_ALL_OPT"] - cand["VALUE_LONG"]
        cand["NET_ALL_OPT"] = cand["VALUE_ALL_OPT"] - cand["OPTIONPRICE"]
        # benchmark: same long leg, no short requirement, matched on long AVG_SF bands
        bm = U[long_ok(floor)].copy()
        bm["PPS"] = bm["OPTIONPRICE"] / bm[f"AVG_SF_{L}"]
        sp_ = U[mask].copy(); sp_["PPS"] = sp_["OPTIONPRICE"] / sp_[f"AVG_SF_{L}"]
        bands = [(0.05, 0.1), (0.1, 0.2), (0.2, 0.4), (0.4, 9)]
        for lo, hi in bands:
            x = sp_[(sp_[f"AVG_SF_{L}"] >= lo) & (sp_[f"AVG_SF_{L}"] < hi)]
            y = bm[(bm[f"AVG_SF_{L}"] >= lo) & (bm[f"AVG_SF_{L}"] < hi)]
            comp.append({"long": L, "short": "+".join(Sh), "avg_sf_band": f"{lo}-{hi}", "n_short_pass": len(x), "n_long_only": len(y),
                         "median_price_short_pass": x["OPTIONPRICE"].median(), "median_price_long_only": y["OPTIONPRICE"].median(),
                         "median_price_per_sf_short_pass": x["PPS"].median(), "median_price_per_sf_long_only": y["PPS"].median(),
                         "p10_price_per_sf_short_pass": x["PPS"].quantile(0.1), "p10_price_per_sf_long_only": y["PPS"].quantile(0.1)})
        comp.append({"long": L, "short": "+".join(Sh), "avg_sf_band": "all", "n_short_pass": len(sp_), "n_long_only": len(bm),
                     "median_price_short_pass": sp_["OPTIONPRICE"].median(), "median_price_long_only": bm["OPTIONPRICE"].median(),
                     "median_price_per_sf_short_pass": sp_["PPS"].median(), "median_price_per_sf_long_only": bm["PPS"].median(),
                     "p10_price_per_sf_short_pass": sp_["PPS"].quantile(0.1), "p10_price_per_sf_long_only": bm["PPS"].quantile(0.1)})
        # collinearity on this universe
        samp = np.random.default_rng(0).choice(len(U), min(len(U), 60000), replace=False)
        xa, ya = S[L][samp].ravel(), S[Sh[0]][samp].ravel()
        okp = ~np.isnan(xa) & ~np.isnan(ya)
        pc = float(np.corrcoef(xa[okp], ya[okp])[0, 1]) if okp.sum() > 10 else float("nan")
        fam = cand[cand["FAMILY_RANK"] == 1]
        nm = lambda x: x.replace("JCKSTP18A", "STP").replace("JCKREF27A", "REF")
        keepc = (["SOURCENAME", "SINKNAME", "OPTIONPRICE", "ALIAS_COUNT"] + [f"{q}_{l}" for l in alll for q in ("MIN_SF", "AVG_SF", "MAX_SF", "MINB_SF", "MAXB_SF", "AVGB_SF")]
                 + ["VALUE_LONG", "VALUE_SHORT", "VALUE_OBLIG", "VALUE_OTHER_SIGNED", "VALUE_ALL_OPT", "NET_OPT", "RATIO", "NET_ALL_OPT",
                    "PRICE_PER_LONG_SF", "SHORT_FLAG", "FAMILY", "FAMILY_SIZE", "FAMILY_MEMBERS"])
        csv_name = f"candidates_long{nm(L)}_short{nm('+'.join(Sh))}.csv"
        csvs[csv_name] = fam[[c for c in keepc if c in fam]].head(50)
        directions.append(SpreadDirection(
            L, list(Sh), cnt, len(U), cand, bm, int(mask.sum()), pc, int(okp.sum()),
            float((np.sign(xa[okp]) != np.sign(ya[okp])).mean()) if okp.any() else float("nan"),
            spread_cobind(weights, L, list(Sh)), csv_name, fam))
        log(f"long {L} short {Sh}: universe {len(U)}, counts {cnt}, candidates {mask.sum()} -> {len(cand)} distinct, {int(fam.shape[0])} families")
    comp = pd.DataFrame(comp)
    co_live = pd.DataFrame([{"a": a, "b": b_, "topologies_both_live": v[0], "mean_node_psens_corr_in_shared_topologies": v[1]}
                            for (a, b_), v in both_live.items()])
    csvs["comparison.csv"] = comp
    csvs["co_live.csv"] = co_live
    return SpreadResult(spec, int(cfg[alll[0]].STUDYID), n_runs, len(topo), directions, comp, co_live, sp_scale,
                        {l: int(live_cols[l].sum()) for l in alll}, csvs)


@dataclass
class PairSpec:
    """Legacy two-run mode: one PathOpt run per axis, one simulation date/hour for the day shift factors."""
    study: int
    run_x: int
    run_y: int
    date: str
    hour: int
    top: int = 100000
    min_sf: float = 0.05


@dataclass
class PairResult:
    spec: PairSpec
    run_x: object
    run_y: object
    full: pd.DataFrame            # joined universe before dedup
    full_deduped: pd.DataFrame
    candidates_full: pd.DataFrame
    near_miss: pd.DataFrame
    paths_deduped: pd.DataFrame
    candidates: pd.DataFrame
    paid_to_take_full: pd.DataFrame
    neg_counts: dict
    min_sf_x_pass: int
    median_min_sf_x: float
    spike_count_all: int
    spike_count_avg: int
    n_avg_both_002: int
    spike_count_candidates: int
    char_pin_flag: object        # DAY_SPIKE of CHAR_SLR_RN->PIN_BESS_RN, None when not in the top N


class PairInputError(ValueError):
    """The chosen date/hour is not available in both runs' topology sets."""


def run_pair(spec: PairSpec, log=_NOLOG) -> PairResult:
    log("Step 1: Getting run configs and topology set members...")
    run_x = popt.get_run_config(spec.run_x)
    run_y = popt.get_run_config(spec.run_y)
    log(f"  Run X: {run_x.BRANCHLABEL} / {run_x.CTGLABEL}, direction {run_x.DIRECTION}, set {run_x.TOPOLOGYSHIFTSETID}")
    log(f"  Run Y: {run_y.BRANCHLABEL} / {run_y.CTGLABEL}, direction {run_y.DIRECTION}, set {run_y.TOPOLOGYSHIFTSETID}")
    members_x = popt.get_topology_set_members(run_x.TOPOLOGYSHIFTSETID)
    members_y = popt.get_topology_set_members(run_y.TOPOLOGYSHIFTSETID)
    log(f"  Set X has {len(members_x)} members")
    log(f"  Set Y has {len(members_y)} members")

    members_x["SIMDATE"] = pd.to_datetime(members_x["SIMDATE"]).dt.date
    members_y["SIMDATE"] = pd.to_datetime(members_y["SIMDATE"]).dt.date
    days_x = set(members_x[members_x["SIMHOUR"] == spec.hour]["SIMDATE"])
    days_y = set(members_y[members_y["SIMHOUR"] == spec.hour]["SIMDATE"])
    common_days = sorted(days_x & days_y)
    log(f"\n  Days at hour {spec.hour} in BOTH sets:")
    for d in common_days[:10]:
        log(f"    {d}")
    if len(common_days) > 10:
        log(f"    ... ({len(common_days)} total)")
    chosen_date = pd.Timestamp(spec.date).date()
    if chosen_date not in common_days:
        raise PairInputError(f"Chosen date {chosen_date} not available in both sets at hour {spec.hour}; available: {common_days}")
    log(f"\n  ✓ Chosen date: {chosen_date}")
    member_x = members_x[(members_x["SIMDATE"] == chosen_date) & (members_x["SIMHOUR"] == spec.hour)]
    member_y = members_y[(members_y["SIMDATE"] == chosen_date) & (members_y["SIMHOUR"] == spec.hour)]
    if len(member_x) == 0 or len(member_y) == 0:
        raise PairInputError(f"No psenshiftid found for date {chosen_date} hour {spec.hour}")
    psenshiftid_x, psenshiftid_y = member_x.iloc[0]["PSENSHIFTID"], member_y.iloc[0]["PSENSHIFTID"]
    log(f"  X: psenshiftid {psenshiftid_x}, runid {member_x.iloc[0]['RUNID']}")
    log(f"  Y: psenshiftid {psenshiftid_y}, runid {member_y.iloc[0]['RUNID']}")

    log("\nStep 2: Pulling FULL PathOpt detail rows...")
    detail_x = popt.fetch_detail(spec.run_x, columns=["SOURCECPNODEID", "SINKCPNODEID", "SOURCENAME", "SINKNAME",
                                                      "SOURCEBUSKV", "SINKBUSKV", "OPTIONPRICE", "MIN_SF", "MAX_SF", "AVG_SF"])
    detail_y = popt.fetch_detail(spec.run_y, columns=["SOURCECPNODEID", "SINKCPNODEID", "OPTIONPRICE", "MIN_SF", "MAX_SF", "AVG_SF"])
    log(f"  Run X: {len(detail_x):,} paths")
    log(f"  Run Y: {len(detail_y):,} paths")

    log("\nStep 3: Joining runs (FULL universe)...")
    full = detail_x.merge(detail_y, on=["SOURCECPNODEID", "SINKCPNODEID"], suffixes=("_X", "_Y"), how="inner")
    log(f"  Joined paths (full universe): {len(full):,}")
    mismatches = ((full["OPTIONPRICE_X"] - full["OPTIONPRICE_Y"]).abs() > 0.01).sum()
    log(f"  OPTIONPRICE mismatches (>$0.01): {mismatches}")
    full = full.rename(columns={"OPTIONPRICE_X": "OPTIONPRICE"}).drop(columns=["OPTIONPRICE_Y"])
    neg = {k: int((full[k] < 0).sum()) for k in ("MIN_SF_X", "MIN_SF_Y", "AVG_SF_X", "AVG_SF_Y")}
    for k, v in neg.items():
        log(f"  Paths with negative {k}: {v:,}")
    log(f"  MIN_SF_X range: [{full['MIN_SF_X'].min():.4f}, {full['MIN_SF_X'].max():.4f}]")
    log(f"  MIN_SF_Y range: [{full['MIN_SF_Y'].min():.4f}, {full['MIN_SF_Y'].max():.4f}]")

    log("\nStep 4: Deduplicating FULL universe (MIN/AVG/MAX + price, no day SF)...")
    full_deduped = dedup_by_electrical_path(full, has_day_sf=False)
    log(f"  Before dedup: {len(full):,} paths")
    log(f"  After dedup: {len(full_deduped):,} distinct electrical paths")
    log("\nStep 5: Adding derived columns (Y_TO_X_RATIO, DOMINANT_AXIS)...")
    full_deduped = add_derived_columns(full_deduped, has_day_sf=False)
    log("\nStep 6: Ranking candidates from FULL universe...")
    paid_to_take_full, candidates_full = rank_by_min_sf(full_deduped, min_sf_floor=spec.min_sf)
    log(f"  Paid-to-take paths (OPTIONPRICE≤0): {len(paid_to_take_full)}")
    log(f"  Candidates passing MIN_SF floor (≥{spec.min_sf} on both axes): {len(candidates_full):,}")
    log("\nStep 7: Finding near-miss paths (MIN_SF_X in [0.03, 0.05), MIN_SF_Y ≥ 0.05)...")
    near_miss = find_near_miss(full_deduped, min_x_range=(0.03, 0.05), min_y_floor=0.05)
    log(f"  Near-miss paths: {len(near_miss):,}")
    min_sf_x_pass = int((full_deduped["MIN_SF_X"] >= 0.05).sum())
    median_min_sf_x = float(full_deduped["MIN_SF_X"].median())
    log(f"  Distinct paths with MIN_SF_X ≥ 0.05: {min_sf_x_pass} of {len(full_deduped):,}")
    log(f"  Median MIN_SF_X: {median_min_sf_x:.6f}")

    log(f"\nStep 8: Pulling day SFs for top {spec.top:,} cheapest paths (scatter only)...")
    top_n = full.sort_values("OPTIONPRICE").head(spec.top)
    log(f"  Top {len(top_n):,} cheapest selected (price: ${top_n['OPTIONPRICE'].min():.2f} to ${top_n['OPTIONPRICE'].max():.2f}/MWh)")
    node_sf_x = shifts.node_shift_factors(psenshiftid_x)
    node_sf_y = shifts.node_shift_factors(psenshiftid_y)
    log(f"  Node SFs X: {len(node_sf_x):,} nodes")
    log(f"  Node SFs Y: {len(node_sf_y):,} nodes")
    with_day, dropped = compute_path_shift_factors(top_n, node_sf_x, node_sf_y)
    log(f"  Paths with day SFs computed: {len(with_day):,}")
    log(f"  Paths dropped (missing nodes): {dropped}")

    log("\nStep 9: Deduplicating top N with day SFs (psens + MIN/AVG + price)...")
    before_dedup = len(with_day)
    paths_deduped = dedup_by_electrical_path(with_day, has_day_sf=True)
    log(f"  Before dedup: {before_dedup:,} paths")
    log(f"  After dedup: {len(paths_deduped):,} distinct electrical paths")
    log("\nStep 10: Adding derived columns + day spike flag...")
    paths_deduped = add_derived_columns(paths_deduped, has_day_sf=True)
    spike_all = int(paths_deduped["DAY_SPIKE"].sum())
    avg_both = paths_deduped[(paths_deduped["AVG_SF_X"] > 0.02) & (paths_deduped["AVG_SF_Y"] > 0.02)]
    spike_avg = int(avg_both["DAY_SPIKE"].sum())
    log(f"  Day spike paths (all {len(paths_deduped):,} distinct): {spike_all}")
    log(f"  Day spike paths (AVG>0.02 both axes, {len(avg_both):,} paths): {spike_avg}")
    char_pin = paths_deduped[(paths_deduped["SOURCENAME"] == "CHAR_SLR_RN") & (paths_deduped["SINKNAME"] == "PIN_BESS_RN")]
    char_flag = char_pin.iloc[0]["DAY_SPIKE"] if len(char_pin) > 0 else None
    log(f"  ✓ CHAR_SLR_RN→PIN_BESS_RN spike flag: {char_flag}" if char_flag is not None
        else f"  ⚠ CHAR_SLR_RN→PIN_BESS_RN not in top {spec.top:,} cheapest")

    log("\nStep 11: Ranking top N candidates...")
    paid_to_take, candidates = rank_by_min_sf(paths_deduped, min_sf_floor=spec.min_sf)
    log(f"  Paid-to-take paths (OPTIONPRICE≤0): {len(paid_to_take)}")
    log(f"  Candidates passing MIN_SF floor: {len(candidates):,}")
    spike_cand = int(candidates["DAY_SPIKE"].sum()) if len(candidates) > 0 else 0
    log(f"  Day spike paths in candidates: {spike_cand}")
    return PairResult(spec, run_x, run_y, full, full_deduped, candidates_full, near_miss, paths_deduped, candidates,
                      paid_to_take_full, neg, min_sf_x_pass, median_min_sf_x, spike_all, spike_avg, len(avg_both), spike_cand,
                      char_flag)
