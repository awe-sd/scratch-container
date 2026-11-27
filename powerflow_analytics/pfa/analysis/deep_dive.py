"""Deep-dive calculations for binding constraints: wind/solar binding conditions, dispatch profile, price formation,
flip attribution between constraints. Returns plain data/DataFrames; markdown is built in pfa.report.deep_dive.

Hours in results are fast-scan clock hours (TIMESTAMP is hour-beginning); label them with pfa.periods.fastscan_he_label.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pfa import constraint_id, periods
from pfa.analysis import marginal_units, shadow_price
from pfa.analysis.constraints import BINDING_PCT, constraint_key
from pfa.cache import StudyCache
from pfa.analysis import drivers, shortlist_value
from pfa.extract import fastscan, gen_mapping, renewables, shifts
from pfa.extract import load as load_reader


# ---------------------------------------------------------------- resolve --

def resolve_constraint(cache: StudyCache, spec: str) -> dict:
    """spec is either 'F-T-CKT@CTG' or a line LABEL; returns dict with
    fromnum, tonum, ckt, ctglabel, label, direction, n_binding_runs."""
    branch = cache.load("outbranch2", columns=["FROMNUM", "TONUM", "CKT", "LABEL",
                                                "FROMNAME", "TONAME"])
    ov = cache.load("outctgviol2", columns=["RUNID", "FROMNUM", "TONUM", "CKT",
                                            "CTGLABEL", "LIMVIOLPCT", "OUTBRANCHDIRECTION"])

    cid = constraint_id.resolve(cache, spec)
    fromnum, tonum, ckt, ctg = cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel

    sub = ov[(ov.FROMNUM == fromnum) & (ov.TONUM == tonum) & (ov.CKT == ckt) & (ov.CTGLABEL == ctg)]
    bind = sub[sub.LIMVIOLPCT >= BINDING_PCT]
    direction = int(bind["OUTBRANCHDIRECTION"].mode().iloc[0]) if len(bind) else 1
    bname = branch[(branch.FROMNUM == fromnum) & (branch.TONUM == tonum) & (branch.CKT == ckt)]
    label = bname["LABEL"].iloc[0] if len(bname) else spec
    fromname = bname["FROMNAME"].iloc[0] if len(bname) else "?"
    toname = bname["TONAME"].iloc[0] if len(bname) else "?"
    key = str(cid)
    return dict(fromnum=fromnum, tonum=tonum, ckt=ckt, ctglabel=ctg, label=label,
                fromname=fromname, toname=toname, direction=direction, key=key,
                n_binding_runs=len(bind))


# --------------------------------------------------------- 1. binding cond --

def _fetch_wind(hist_start: str, hist_end: str) -> pd.DataFrame:
    df = renewables.wind_region_hourly(hist_start, hist_end)
    # avgHSLPct is a PERCENT (0-100), not a fraction -- divide by 100 or wind MW
    # comes out ~100x too big (caught in review: a naive pct*capacity join
    # produced a "SYSTEM_WIND_MW" threshold of 2.7M MW against ~40GW installed).
    df["WIND_MW"] = (df["avgHSLPct"].astype(float) / 100.0) * df["totalInstalledCapacityMW"].astype(float)
    cap_total = df.groupby("TimeStamp")["totalInstalledCapacityMW"].sum()
    return df, cap_total


def _fetch_solar(hist_start: str, hist_end: str, iso_zone: int = 67) -> pd.DataFrame:
    df = renewables.solar_hourly(hist_start, hist_end, iso_zone)
    df["TIMESTAMP"] = pd.to_datetime(df["TimeStampDate"]) + pd.to_timedelta(df["HE"].astype(int) - 1, unit="h")
    return df[["TIMESTAMP", "solarGen", "solarMax"]]


CORR_MATERIALITY = 0.15  # below this |corr| a variable is not named as a driver
DRIVER_LEAD = 0.10       # a single driver is named only if its |corr| leads the runner-up by at least this much
CLEAR_DIRECTION = 0.05   # below this |corr| the binding direction of a variable is not stated
LOW_SF = shadow_price.MIN_SF


def attribute_driver(corrs: dict) -> dict:
    """Wind / solar / load by |corr| with HEADROOM: one driver only if it leads the runner-up by DRIVER_LEAD, else 'mixed';
    'none' when no |corr| reaches CORR_MATERIALITY. Variables without a correlation (None) are skipped."""
    vals = {k: v for k, v in corrs.items() if v is not None}
    ranked = sorted(vals, key=lambda k: -abs(vals[k]))
    if not ranked or abs(vals[ranked[0]]) < CORR_MATERIALITY:
        return {"kind": "none", "lead": None}
    lead = abs(vals[ranked[0]]) - (abs(vals[ranked[1]]) if len(ranked) > 1 else 0.0)
    return {"kind": ranked[0] if lead >= DRIVER_LEAD else "mixed", "lead": round(lead, 3)}


def trigger_levels(df: pd.DataFrame, col: str) -> dict | None:
    """Where this variable sits when headroom is negative. If headroom FALLS as the variable rises (corr < 0) the constraint
    binds when it is high and the informative level is a LOW percentile among binding hours (P10: where binding starts);
    the mirror for corr > 0 (P90). Also the binding rate by quintile of the variable over all hours."""
    sub = df.dropna(subset=[col, "HEADROOM"])
    if sub.empty:
        return None
    corr = float(sub["HEADROOM"].corr(sub[col])) if sub[col].nunique() > 1 else float("nan")
    neg = sub[sub["HEADROOM"] < 0]
    if pd.isna(corr) or abs(corr) < CLEAR_DIRECTION:
        direction, start = "no clear direction", None
    elif corr < 0:
        direction, start = "binds when high", "P10"
    else:
        direction, start = "binds when low", "P90"
    out = {"corr": None if pd.isna(corr) else round(corr, 3), "direction": direction, "n_neg": int(len(neg)),
           "start_pctile": start}
    if len(neg):
        q = neg[col].quantile([0.1, 0.5, 0.9])
        out.update({"p10": round(float(q.iloc[0]), 0), "p50": round(float(q.iloc[1]), 0), "p90": round(float(q.iloc[2]), 0)})
        out["start_level"] = out["p10"] if start == "P10" else out["p90"] if start == "P90" else None
    quint = []
    try:
        bins = pd.qcut(sub[col], 5, duplicates="drop")
        for iv, g in sub.groupby(bins, observed=True):
            quint.append({"lo": round(float(iv.left), 0), "hi": round(float(iv.right), 0), "n": int(len(g)),
                          "bind_rate": round(float((g["HEADROOM"] < 0).mean()), 3)})
    except ValueError:
        pass
    out["quintiles"] = quint
    return out


def _load_series(first: pd.Timestamp, last: pd.Timestamp) -> pd.Series:
    """System load MW indexed by the hour-beginning stamp, for the years the window touches."""
    frames = []
    for year in range(first.year, last.year + 1):
        lo = first if year == first.year else pd.Timestamp(year=year, month=1, day=1)
        hi = last if year == last.year else pd.Timestamp(year=year, month=12, day=31)
        frames.append(load_reader.get_load_window(year, f"{lo:%m-%d}", f"{hi:%m-%d}"))
    d = pd.concat(frames, ignore_index=True)
    d["TIMESTAMP"] = pd.to_datetime(d["date"]) + pd.to_timedelta(d["he"].astype(int) - 1, unit="h")
    return d.drop_duplicates("TIMESTAMP").set_index("TIMESTAMP")["load_mw"].astype(float)


def _month_names(ts: pd.Series) -> str:
    months = sorted(ts.dt.month.unique())
    names = [pd.Timestamp(2000, m, 1).strftime("%b") for m in months]
    return names[0] if len(names) == 1 else f"{names[0]}-{names[-1]}"


def binding_conditions(config_id: int, hist_start: str, hist_end: str, month: str) -> dict:
    """Fast-scan headroom joined against regional wind + system solar + system load."""
    hr = fastscan.headroom_window(config_id, hist_start, hist_end)
    if hr.empty:
        return {"empty": True}
    hr["TIMESTAMP"] = pd.to_datetime(hr["TIMESTAMP"])
    n_fastscan = len(hr)

    wind, wind_cap = _fetch_wind(hist_start, hist_end)
    wind_piv = wind.pivot_table(index="TimeStamp", columns="windRegion", values="WIND_MW", aggfunc="mean")
    wind_piv["SYSTEM_WIND_MW"] = wind_piv.sum(axis=1)
    wind_piv.index = pd.to_datetime(wind_piv.index)
    system_cap_mw = round(float(wind_cap.max()), 0)  # sanity ceiling for SYSTEM_WIND_MW

    solar = _fetch_solar(hist_start, hist_end).set_index("TIMESTAMP")

    df = hr.set_index("TIMESTAMP").join(wind_piv, how="left").join(
        solar[["solarGen"]].rename(columns={"solarGen": "SOLAR_MW"}), how="left")
    first, last = df.index.min(), df.index.max()
    load_error = None
    try:
        df = df.join(_load_series(first, last).rename("LOAD_MW"), how="left")
    except Exception as e:
        load_error = f"{type(e).__name__}: {e}"
        df["LOAD_MW"] = np.nan
    df = df.reset_index()
    assert len(df) == n_fastscan, "join changed row count -- duplicate keys in wind/solar source"
    n_wind_matched = int(df["SYSTEM_WIND_MW"].notna().sum())
    n_solar_matched = int(df["SOLAR_MW"].notna().sum())
    n_load_matched = int(df["LOAD_MW"].notna().sum())
    if df["SYSTEM_WIND_MW"].notna().any():
        assert df["SYSTEM_WIND_MW"].max() <= system_cap_mw * 1.05, (
            f"SYSTEM_WIND_MW ({df['SYSTEM_WIND_MW'].max()}) exceeds installed capacity "
            f"({system_cap_mw}) -- unit/scale bug in _fetch_wind")
    df["HOUR"] = df["TIMESTAMP"].dt.hour
    df["DOW"] = df["TIMESTAMP"].dt.dayofweek
    df["NEG"] = df["HEADROOM"] < 0

    region_cols = [c for c in wind_piv.columns if c != "SYSTEM_WIND_MW"]
    corr = {c: df[["HEADROOM", c]].dropna()["HEADROOM"].corr(df[c]) for c in region_cols + ["SYSTEM_WIND_MW"]}
    corr["SOLAR_MW"] = df[["HEADROOM", "SOLAR_MW"]].dropna()["HEADROOM"].corr(df["SOLAR_MW"])
    corr["LOAD_MW"] = df[["HEADROOM", "LOAD_MW"]].dropna()["HEADROOM"].corr(df["LOAD_MW"]) if n_load_matched > 1 else None
    corr = {k: (round(float(v), 3) if v is not None and pd.notna(v) else None) for k, v in corr.items()}
    region_corrs = {c: corr[c] for c in region_cols if corr.get(c) is not None}
    dominant_region = None
    if region_corrs:
        cand = min(region_corrs, key=region_corrs.get)
        if region_corrs[cand] <= -CORR_MATERIALITY:
            dominant_region = cand

    triggers = {c: trigger_levels(df, c) for c in ["SYSTEM_WIND_MW", "SOLAR_MW", "LOAD_MW", *region_cols]}

    # on/off-peak hit rate in the target calendar month (any year in the window)
    in_month = df[df["TIMESTAMP"].dt.month == periods.parse_month(month)[1]]
    is_onpeak = periods.fastscan_hour_class(in_month["TIMESTAMP"]) == "OnPeak"
    onpeak, offpeak = in_month[is_onpeak], in_month[~is_onpeak]
    pct_onpeak = round(100 * onpeak["NEG"].mean(), 1) if len(onpeak) else None
    pct_offpeak = round(100 * offpeak["NEG"].mean(), 1) if len(offpeak) else None

    hod = df.groupby("HOUR")["NEG"].mean().round(3)
    peak_hour = int(hod.idxmax()) if hod.notna().any() else None
    attribution = attribute_driver({"wind": corr.get("SYSTEM_WIND_MW"), "solar": corr.get("SOLAR_MW"), "load": corr.get("LOAD_MW")})
    driver = {**attribution, "wind_corr": corr.get("SYSTEM_WIND_MW"), "solar_corr": corr.get("SOLAR_MW"),
              "load_corr": corr.get("LOAD_MW"), "peak_hour": peak_hour}

    pooled = cfg_span = None
    try:
        p_bind, _, n_pooled, years = shortlist_value.fastscan_month_onpeak(config_id, month)
        pooled = {"p_bind": p_bind, "n_onpeak_hours": n_pooled, "years": years}
        t0, t1, n_all = fastscan.timestamp_span(config_id)
        cfg_span = {"start": t0, "end": t1, "n_hours": n_all}
    except Exception as e:
        pooled = {"error": f"{type(e).__name__}: {e}"}

    return {"empty": False, "n_hours": n_fastscan, "config_id": config_id,
            "window": {"start": hist_start, "end": hist_end}, "span": {"start": first, "end": last, "months": _month_names(df["TIMESTAMP"])},
            "n_month_hours": int(len(in_month)), "pooled_month": pooled, "config_span": cfg_span,
            "n_wind_matched": n_wind_matched, "n_solar_matched": n_solar_matched, "n_load_matched": n_load_matched,
            "load_error": load_error,
            "corr": corr, "dominant_wind_region": dominant_region,
            "triggers": triggers, "system_wind_cap_mw": system_cap_mw,
            "pct_neg_onpeak_month": pct_onpeak, "pct_neg_offpeak_month": pct_offpeak,
            "month_name": periods.month_name(month),
            "hour_of_day_neg_rate": {int(k): float(v) for k, v in hod.items()}, "driver": driver}


# --------------------------------------------------------- 2. dispatch ------

def dispatch_profile(study_id: int, c: dict, genunit: pd.DataFrame, scedname: pd.DataFrame) -> pd.DataFrame:
    nodes = shifts.cpnode_live_nodes(
        study_id, constraint_id.ConstraintId(c["fromnum"], c["tonum"], c["ckt"], c["ctglabel"]))
    if nodes.empty:
        return nodes
    nodes["PSENS"] = nodes["PSENS"].astype(float)
    nodes = nodes[nodes["PSENS"].abs().between(shadow_price.MIN_SF, shadow_price.MAX_SF)].copy()
    # several NAME rows are aliases for the same underlying node (identical PSENS/CPNODEID) --
    # collapse them so the top-N table shows distinct nodes, not repeats of one node's aliases.
    # CPNODEID=0 is a shared placeholder for MULTIPLE distinct unmapped nodes (e.g. four separate
    # Red Oak data-center load cpnodes all sit at CPNODEID=0 with identical PSENS) -- identity
    # must include NAME or those genuinely-distinct nodes get wrongly collapsed into one row.
    nodes = nodes.sort_values(["N", "NAME", "CPNODEID"], ascending=[False, True, True]).drop_duplicates(["CPNODEID", "NAME", "PSENS"])
    # sign convention: PSENS is on FROMNUM->TONUM; direction=-1 flips relief/harm sense
    nodes["EFFECTIVE_SIGN"] = np.sign(nodes["PSENS"]) * c["direction"]
    nodes["RELIEF_OR_HARM"] = np.where(nodes["EFFECTIVE_SIGN"] < 0, "relief (up relieves)", "harm (up loads)")

    # a CPNODEID can host multiple co-located GENUNITID rows of DIFFERENT fuel
    # (e.g. a battery + solar hybrid site) -- an arbitrary drop_duplicates
    # silently mislabels the fuel. Flag ambiguity instead of picking one.
    gu_raw = genunit[["CPNODEID", "GENFUELTYPE", "RESOURCE_TYPE"]].dropna(subset=["CPNODEID"])
    fuel_counts = gu_raw.drop_duplicates(["CPNODEID", "GENFUELTYPE"]).groupby("CPNODEID").size()
    ambiguous_ids = set(fuel_counts[fuel_counts > 1].index)
    gu = gu_raw.drop_duplicates("CPNODEID").copy()
    gu.loc[gu["CPNODEID"].isin(ambiguous_ids), ["GENFUELTYPE", "RESOURCE_TYPE"]] = "AMBIGUOUS(multi-fuel site)"
    nodes = nodes.merge(gu, on="CPNODEID", how="left")
    nodes["ABS_PSENS"] = nodes["PSENS"].abs()
    return nodes.sort_values(["ABS_PSENS", "NAME", "CPNODEID"], ascending=[False, True, True]).drop(columns="ABS_PSENS").head(20)


# --------------------------------------------------------- 3. price form ---

def outage_flow(c: dict, tofinder: pd.DataFrame | None) -> dict | None:
    """The driving outage group's signed flow change on this constraint (mean over runs x OUTBRANCHDIRECTION, as the summary's signed_fd)."""
    if tofinder is None or tofinder.empty:
        return None
    summ = drivers.tofinder_summary(tofinder)
    top = summ[summ["CONSTRAINT"] == c["key"]]
    if top.empty:
        return None
    t = top.reindex(top["MEAN_FLOWDELTA"].abs().sort_values(ascending=False).index).iloc[0]
    return {"group": t["OUTAGE_GROUP"], "signed_fd": round(float(t["MEAN_FLOWDELTA"]) * c["direction"], 1),
            "mean_preflow": round(float(t["MEAN_PREFLOW"]), 1), "n_runs": int(t["N_RUNS"])}


def locate_on_curve(curve: list[dict], price: float) -> dict:
    """Where `price` falls on the depth curve: the first step whose price reaches it, or beyond either end."""
    if not curve:
        return {"where": "empty"}
    if price < curve[0]["lambda"]:
        return {"where": "below_first", "first_price": curve[0]["lambda"]}
    for i, st in enumerate(curve):
        if st["lambda"] >= price:
            return {"where": "at_step", "step": i + 1, "depth_lo": st["depth_lo"], "depth_hi": st["depth_hi"], "step_price": st["lambda"]}
    return {"where": "above_last", "last_price": curve[-1]["lambda"], "exhaustion_mw": curve[-1]["depth_hi"]}


def marginal_unit_table(study_id: int, c: dict, marg: pd.DataFrame, bus_names: pd.DataFrame,
                        genunit: pd.DataFrame, scedname: pd.DataFrame) -> pd.DataFrame:
    """Marginal units with a name and their shift factor on this constraint (bound sense); |SF| under MIN_SF = not a price setter."""
    out = marg.copy()
    out["UNIT"] = [f"bus {b} #{i}" for b, i in zip(out["BUSNUM"], out["ID"])]
    try:
        pair = out[["BUSNUM", "ID"]].assign(SIDE="x")
        named = shadow_price.sced_names(pair, bus_names, genunit, scedname)
        bn = bus_names.drop_duplicates("BUSNUM").set_index("BUSNUM")["BUSNAME"]
        out["UNIT"] = [sc if isinstance(sc, str) else (f"{bn.get(b)} #{i}" if b in bn.index else u)
                       for sc, b, i, u in zip(named["SCED"], out["BUSNUM"], out["ID"], out["UNIT"])]
    except Exception:
        pass
    try:
        sfs = shifts.bus_sf_for_buses(study_id, constraint_id.ConstraintId(c["fromnum"], c["tonum"], c["ckt"], c["ctglabel"]),
                                      [int(b) for b in out["BUSNUM"]])
        out = out.merge(sfs.assign(SF=sfs["SF"].astype(float) * c["direction"]), on="BUSNUM", how="left")
    except Exception:
        out["SF"] = np.nan
    out["PRICE_SETTER"] = np.where(out["SF"].isna(), "unknown (no shift factor)",
                                   np.where(out["SF"].abs() < LOW_SF, f"no: abs(SF) < {LOW_SF} (not a price setter for this constraint)", "yes"))
    return out


def price_formation(study_id: int, c: dict, ctgviol: pd.DataFrame, outcon: pd.DataFrame,
                    gen: pd.DataFrame, bus_names: pd.DataFrame, genunit: pd.DataFrame,
                    scedname: pd.DataFrame, tofinder: pd.DataFrame | None = None) -> dict:
    key = c["key"]
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    binding_runs = set(cv[(cv["CONSTRAINT"] == key) & (cv["LIMVIOLPCT"] >= BINDING_PCT)]["RUNID"])

    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"}).copy()
    oc["CONSTRAINT"] = constraint_key(oc)
    lp = oc[(oc["CONSTRAINT"] == key) & (oc["RUNID"].isin(binding_runs))]
    penalty_tiers = {500.0, 3500.0}
    lp_lambda = lp["OPFCNLAMBDA"].dropna()
    lp_unpriced_frac = round(float(lp_lambda.isin(penalty_tiers).mean()), 3) if len(lp_lambda) else None
    lp_stats = None
    if len(lp_lambda):
        lp_stats = {"n": int(len(lp_lambda)), "n_binding_runs": len(binding_runs),
                    "mean": round(float(lp_lambda.mean()), 1),
                    "p50": round(float(lp_lambda.median()), 1), "max": round(float(lp_lambda.max()), 1),
                    "pct_penalty_tier": lp_unpriced_frac}

    # marginal units: BUSMARGCOSTMW ~ EDMARGCOSTMW within $1, MWMIN<MW<MWMAX, in binding runs
    g = gen[gen["RUNID"].isin(binding_runs)].copy()
    marg = g[(g["MW"] > g["MWMIN"]) & (g["MW"] < g["MWMAX"]) &
             ((g["BUSMARGCOSTMW"] - g["EDMARGCOSTMW"]).abs() <= 1.0)]
    marg_summary = (marg.groupby(["BUSNUM", "ID", "FUELTYPE"])
                    .size().rename("N").reset_index().sort_values(["N", "BUSNUM", "ID", "FUELTYPE"], ascending=[False, True, True, True]).head(10))
    marg_summary = marginal_unit_table(study_id, c, marg_summary, bus_names, genunit, scedname)

    # structural lambda via shadow_price relief-set stack, shallow vs deep
    struct = None
    try:
        rs = shadow_price.relief_set(study_id, key, gen, bus_names, genunit, scedname,
                                     direction=c["direction"])
        relief, cap, up, down = rs.units, rs.capacity, rs.up, rs.down
        if not relief.empty:
            curve = rs.curve()
            if not curve:
                # relief_set found qualifying units, but build_stacks/lambda_depth_curve
                # produced no priced step -- distinct from "no relief set at all": this is
                # an empty UP-or-DOWN stack (no counterparty offer/capacity on one side),
                # not a missing relief-eligible unit. Conflating the two hides the fact
                # that a relief set existed and merely lacked one-sided coverage. Derive
                # which side is actually empty rather than assuming -- it varies by constraint.
                if not up and not down:
                    empty_desc = "both stacks empty"
                elif not up:
                    empty_desc = "up-stack empty"
                elif not down:
                    empty_desc = "down-stack empty"
                else:
                    empty_desc = "both stacks populated but no priced pair"
                struct = {"empty_curve": True, "n_relief_units": int(len(relief)), "empty_desc": empty_desc}
            if curve:
                shallow = curve[0]
                deep = curve[-1]
                renew_down_sced = set(relief[(relief["SIDE"] == "down") & relief["IS_RENEWABLE"]]["SCED"])
                battery_down_sced = set(relief[(relief["SIDE"] == "down") &
                                               relief["FUELTYPE"].astype(str).str.upper().str.contains("MWH|BATTERY", na=False)]["SCED"])

                def _pair_sceds(step):
                    down_sced, up_sced = step["pair"].split("↓/")
                    return down_sced, up_sced.rstrip("↑")

                def _step_status(step):
                    """A lambda of exactly 0.0 has two distinct causes that must not
                    be conflated: (a) a genuine NaN offer price for one side of the
                    pair (unpriced -- lambda_depth_curve's max(0.0, min(nan, cap))
                    collapses a NaN spread to 0.0), or (b) both offers are real and
                    the down (displaced) unit's price already sits at/above the up
                    unit's -- a genuinely free/negative-cost redispatch. Distinguish
                    by checking cap.loc[sced, 'P60'] directly rather than inferring
                    from step count, which says nothing about the cause."""
                    down_sced, up_sced = _pair_sceds(step)
                    p_down = cap.loc[down_sced, "P60"] if down_sced in cap.index else None
                    p_up = cap.loc[up_sced, "P60"] if up_sced in cap.index else None
                    nan_side = pd.isna(p_down) or pd.isna(p_up)
                    if step["lambda"] == 0.0 and nan_side:
                        missing = down_sced if pd.isna(p_down) else up_sced
                        return None, f"unpriced (no DAM offer price found for {missing})"
                    uncommitted_note = "" if step.get("up_committed", True) else \
                        f" -- CAVEAT: {up_sced} has AWARDEDQUANTITY=0 in DAM (not committed); this " \
                        f"relief requires STARTING the unit, not just ramping an online one"
                    if step["lambda"] == 0.0:
                        return 0.0, ("free relief (down offer >= up offer at this depth, not a data gap)"
                                     + uncommitted_note)
                    down_sced_r = down_sced
                    if down_sced_r in renew_down_sced:
                        return step["lambda"], "wind/solar-curtailment-priced" + uncommitted_note
                    if down_sced_r in battery_down_sced:
                        return step["lambda"], "battery-priced" + uncommitted_note
                    return step["lambda"], "gas-spread-priced" + uncommitted_note

                shallow_lambda, shallow_regime = _step_status(shallow)
                deep_lambda, deep_regime = _step_status(deep)
                exhaustion_mw = round(curve[-1]["depth_hi"], 1)
                # _step_status only inspects the shallow/deep endpoints; a curve can
                # have committed endpoints but uncommitted interior steps (or vice
                # versa), so the exhaustion-depth headline needs its own whole-curve
                # split -- otherwise "exhausts at N MW" silently mixes real ramp
                # capacity with DAM-uncommitted (start-required) capacity.
                uncommitted_mw = round(sum(s["depth_hi"] - s["depth_lo"] for s in curve
                                          if not s.get("up_committed", True)), 1)
                n_uncommitted_steps = sum(1 for s in curve if not s.get("up_committed", True))
                committed_mw = round(exhaustion_mw - uncommitted_mw, 1)
                struct = {"shallow_lambda": shallow_lambda, "shallow_pair": shallow["pair"],
                          "exhaustion_depth_mw": exhaustion_mw, "single_step": len(curve) == 1,
                          "committed_mw": committed_mw, "uncommitted_mw": uncommitted_mw,
                          "n_uncommitted_steps": n_uncommitted_steps,
                          "deep_lambda": deep_lambda, "deep_pair": deep["pair"],
                          "n_steps": len(curve),
                          "shallow_regime": shallow_regime, "deep_regime": deep_regime, "steps": curve,
                          "lp_p50_on_curve": locate_on_curve(curve, lp_stats["p50"]) if lp_stats else None,
                          "regime_hint": f"{shallow_regime} at shallow relief -> {deep_regime} at deep relief"}
        else:
            # no |SF|-qualified unit at all -- distinct from finding units but failing to
            # price a curve for them (the empty_curve case above)
            struct = {"empty_relief": True}
    except Exception as e:
        struct = {"error": str(e)}

    return {"lp_stats": lp_stats, "marginal_units": marg_summary, "structural_lambda": struct,
            "outage_flow": outage_flow(c, tofinder)}


# --------------------------------------------------------- 4. flip attrib --

def flip_attribution(cache: StudyCache, constraints: list[dict]) -> pd.DataFrame:
    if len(constraints) < 2:
        return pd.DataFrame()
    tofinder = cache.load("outtofindermax2")
    tf = tofinder.rename(columns={"FROMNUM_TARGET": "FROMNUM", "TONUM_TARGET": "TONUM",
                                  "CKT_TARGET": "CKT"})
    tf["CONSTRAINT"] = constraint_key(tf)
    rows = []
    for c in constraints:
        sub = tf[tf["CONSTRAINT"] == c["key"]]
        if sub.empty:
            continue
        g = sub.groupby("OUTAGE_GROUP").agg(
            N_RUNS=("RUNID", "nunique"),
            MEAN_FLOWDELTA=("FLOWDELTA", "mean"),
            MEAN_PREFLOW=("PREGROUPOUTLINEFLOW", "mean"),
        ).reset_index()
        g["SIGNED_FLOWDELTA"] = g["MEAN_FLOWDELTA"] * c["direction"]
        g.insert(0, "CONSTRAINT", c["key"])
        g.insert(1, "LABEL", c["label"])
        # sort by SIGNED_FLOWDELTA descending (not abs) so a flow-adding group ranks
        # above a flow-reducing one -- an abs-sort can put a relief group ahead of
        # the actual loading driver in a "what explains this constraint binding" table
        rows.append(g.sort_values(["SIGNED_FLOWDELTA", "OUTAGE_GROUP"], ascending=[False, True]).head(5))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def flip_synthesis_facts(results: list[dict], flip_df: pd.DataFrame) -> dict | None:
    """Evidence for the flip mechanism between exactly two constraints: a shared dispatch node whose effective sign
    differs, and whether each constraint's endpoint names appear in the OTHER constraint's top outage groups."""
    if len(results) != 2 or flip_df.empty:
        return None
    d0, d1 = results[0]["dispatch"], results[1]["dispatch"]
    c0, c1 = results[0]["c"], results[1]["c"]
    sign_flip = None
    if not d0.empty and not d1.empty:
        m = d0[["NAME", "EFFECTIVE_SIGN", "PSENS"]].merge(
            d1[["NAME", "EFFECTIVE_SIGN", "PSENS"]], on="NAME", suffixes=("_0", "_1"))
        flips = m[m["EFFECTIVE_SIGN_0"] != m["EFFECTIVE_SIGN_1"]]
        if not flips.empty:
            row = flips.iloc[0]
            sign_flip = {"name": row["NAME"], "psens_0": float(row["PSENS_0"]), "psens_1": float(row["PSENS_1"])}

    def names_in_other_groups(mine, other):
        other_terms = [str(other["fromname"]).split("_")[0], str(other["toname"]).split("_")[0]]
        rows = flip_df[flip_df["LABEL"] == mine["label"]]
        return not rows[rows["OUTAGE_GROUP"].astype(str).apply(
            lambda g: any(t.upper() in g.upper() for t in other_terms))].empty

    return {"c0": c0, "c1": c1, "sign_flip": sign_flip,
            "c0_names_c1": names_in_other_groups(c0, c1), "c1_names_c0": names_in_other_groups(c1, c0)}


# --------------------------------------------------------- orchestration --

@dataclass
class StudyTables:
    """Cached study tables and reference maps shared by every constraint of one deep dive."""
    cache: StudyCache
    ctgviol: pd.DataFrame
    outcon: pd.DataFrame
    gen: pd.DataFrame
    genunit: pd.DataFrame
    bus_names: pd.DataFrame
    scedname: pd.DataFrame
    tofinder: pd.DataFrame | None = None


def load_tables(study_id: int) -> StudyTables:
    cache = StudyCache(study_id)
    return StudyTables(cache, cache.load("outctgviol2"), cache.load("outconstraint2"), cache.load("outgen2"),
                       cache.load("genunit"), marginal_units.bus_name_map(cache.load("outbranch2")),
                       gen_mapping.fetch_genunit_sced_name(), cache.load("outtofindermax2"))


def analyze_constraint(study_id: int, c: dict, t: StudyTables, hist_start: str, hist_end: str, month: str) -> dict:
    """All per-constraint sections: {'c', 'binding', 'dispatch', 'price'}."""
    configs = fastscan.find_configs(study_id, c["fromnum"], c["tonum"], c["ctglabel"])
    binding = {"empty": True}
    if not configs.empty:
        binding = binding_conditions(int(configs.iloc[0]["CONFIG_ID"]), hist_start, hist_end, month)
    return {"c": c, "binding": binding,
            "dispatch": dispatch_profile(study_id, c, t.genunit, t.scedname),
            "price": price_formation(study_id, c, t.ctgviol, t.outcon, t.gen, t.bus_names, t.genunit, t.scedname, t.tofinder)}
