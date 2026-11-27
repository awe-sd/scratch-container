"""Month valuation of the screened shortlist: on-peak fast-scan P(bind), shadow price over the
negative-headroom distribution, ticket/days coverage, cheapest path SF and edge.

`value_shortlist` attaches these columns to ScreeningResult.shortlist; the per-constraint pieces
(`value_row`, `coverage_and_days`, ...) are importable on their own.
"""
from __future__ import annotations

import gc

import pandas as pd

from .. import config, periods
from ..cache import StudyCache
from ..constraint_id import ConstraintId, constraint_key
from ..extract import fastscan, gen_mapping, popt, shifts
from . import marginal_units, shadow_price as sp
from .constraints import BINDING_PCT
from .screening import ScreeningResult


def month_bind_dates(ctgviol: pd.DataFrame, runs: pd.DataFrame, cutoff: str, month: str):
    """Per-constraint: (distinct post-cutoff in-month SIMDATEs it binds on,
    distinct post-cutoff in-month SIMDATEs sampled at all) — the days-active
    proxy for un-ticketed class-A coverage."""
    r = runs.copy()
    r["SIMDATE"] = pd.to_datetime(r["SIMDATE"])
    first, last = periods.month_range(month)
    r = r[(r["SIMDATE"] >= pd.to_datetime(cutoff)) & (r["SIMDATE"] >= first) & (r["SIMDATE"] <= last)]
    n_sampled = r["SIMDATE"].dt.date.nunique()
    cv = ctgviol.copy()
    cv["CONSTRAINT"] = constraint_key(cv)
    cv = cv[cv["LIMVIOLPCT"] >= BINDING_PCT].merge(r[["RUNID", "SIMDATE"]], on="RUNID", how="inner")
    bind_days = cv.groupby("CONSTRAINT")["SIMDATE"].apply(lambda s: s.dt.date.nunique())
    return bind_days, n_sampled


def coverage_and_days(c: str, has_ticket: bool, start, end, bind_days_map, n_sampled, month: str):
    """(coverage fraction, outage days in the month, marker, thin_evidence)."""
    if has_ticket:
        first, last = periods.month_range(month)
        days = pd.bdate_range(max(pd.Timestamp(start), first), min(pd.Timestamp(end), last))
        days = days[~days.isin(periods.nerc_holidays(first.year))]
        n_days = len(days)
        cov = round(n_days * 16 / (len(periods.onpeak_days(month)) * 16), 3)
        return cov, n_days, "", n_days < 3
    n_days = int(bind_days_map.get(c, 0))
    cov = round(n_days / n_sampled, 3) if n_sampled else 0.0
    return cov, n_days, "(days-proxy)", n_days < 3


def fastscan_month_onpeak(config_id: int, month: str):
    """Fast-scan headroom for the calendar month across all years, restricted to weekday HE7-22
    on-peak rows (ex-NERC holidays); returns (p_bind_onpeak, need_df) where need_df is the
    NEED_MW frame (negative-headroom onpeak hours only, for shadow_price)."""
    df = fastscan.headroom_for_month(config_id, periods.parse_month(month)[1])
    if df.empty:
        return None, pd.DataFrame()
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    onpk = df[periods.fastscan_hour_class(df["TIMESTAMP"]) == "OnPeak"]
    if onpk.empty:
        return None, pd.DataFrame()
    p_bind = float((onpk["HEADROOM"] < 0).mean())
    need = onpk[onpk["HEADROOM"] < 0].copy()
    need["NEED_MW"] = -need["HEADROOM"].astype(float)
    return p_bind, need


def cpnode_sf(study_id: int, constraint: str, names: list[str]) -> dict[str, float]:
    names = [n for n in names if isinstance(n, str) and n]
    if not names:
        return {}
    cid = ConstraintId.parse(constraint)
    df = shifts.cpnode_sf_by_name(study_id, cid, names)
    return {r["NAME"]: float(r["SF"]) for _, r in df.iterrows()} if len(df) else {}


def value_row(study_id: int, c: str, gen, bus_names, genunit, scedname, month: str) -> dict:
    """Step-2 valuation components for one class-A constraint."""
    out: dict = {"_status": "ok"}
    cid = ConstraintId.parse(c)
    f, t, ctg = cid.fromnum, cid.tonum, cid.ctglabel
    cfgs = fastscan.find_configs(study_id, int(f), int(t), ctg)
    if cfgs.empty:
        out["_status"] = "no fast-scan config"
        return out
    config_id = int(cfgs["CONFIG_ID"].iloc[0])
    direction = int(cfgs["DIRECTION"].iloc[0]) if pd.notna(cfgs["DIRECTION"].iloc[0]) else 1
    label = periods.month_label(month)
    p_bind, need = fastscan_month_onpeak(config_id, month)
    if p_bind is None:
        out["_status"] = f"no {label} on-peak fast-scan hours"
        return out
    out[f"P(bind) {label} on-peak"] = round(p_bind, 3)

    # DIRECTION matters: on a reverse-bound branch (-1) a positive-PSENS
    # unit is relief (up), not the problem (down) — see relief_set's
    # docstring for the study-14412 canary this fixes (3380-3390-1@DPNAONA5).
    relief = sp.relief_set(study_id, c, gen, bus_names, genunit, scedname, direction=direction)
    if relief.units.empty:
        out["_status"] = "no relief-set units in SF band"
        return out
    if relief.capacity.empty or not relief.up or not relief.down:
        out["_status"] = "no DAM offer coverage for relief-set units"
        return out
    curve = relief.curve()
    if not curve or need.empty:
        out["_status"] = "no fast-scan negative-headroom hours"
        return out
    dist = sp.lambda_distribution(curve, need)
    priced = dist["LAMBDA"].dropna()
    if priced.empty:
        out["_status"] = "fast-scan need exceeds relief-set capacity at every hour"
        return out
    pct = sp.percentiles(priced)
    out["E[lambda|bind]"] = round(float(priced.mean()), 1)
    out["lambda P50"] = pct.get("P50")
    out["lambda P90"] = pct.get("P90")
    out["unpriced deep hours %"] = round(100.0 * dist["LAMBDA"].isna().mean(), 1)

    paths = popt.best_paths(study_id, c)
    if paths is not None:
        p = paths.iloc[0]
        source, sink = str(p["SOURCENAME"]), str(p["SINKNAME"])
        sfs = cpnode_sf(study_id, c, [source, sink])
        if source in sfs and sink in sfs:
            eff_sf = sfs[source] - sfs[sink]
            sf_marker = ""
        else:
            eff_sf = float(p["AVG_SF"])
            sf_marker = "~"
        out["Path"] = f"{source}->{sink} ${float(p['OPTIONPRICE']):.2f}"
        out["Path SF"] = f"{sf_marker}{eff_sf:.3f}"
        out["_eff_sf"] = eff_sf
        out["_path_price"] = float(p["OPTIONPRICE"])
    return out


def value_columns(month: str) -> list[str]:
    label = periods.month_label(month)
    return [
        f"Outage days in {label}", "coverage", "thin window evidence", f"P(bind) {label} on-peak",
        "E[lambda|bind]", "lambda P50", "lambda P90", "unpriced deep hours %",
        f"{label} value $/MWh/SF", "Path", "Path SF", "Edge $", "status",
    ]


def value_shortlist(result: ScreeningResult, month: str) -> pd.DataFrame:
    """result.shortlist with the month-valuation columns appended (see value_columns).

    Every shortlist row is valued; a failed lookup puts "lookup failed: ..." in that row's status.
    """
    label = periods.month_label(month)
    cols = value_columns(month)
    short = result.shortlist
    if short.empty:
        return short.assign(**{c: pd.Series(dtype=object) for c in cols})

    study = result.study
    cache = StudyCache(study)
    runs = cache.load("opfrun")
    ctgviol = cache.load("outctgviol2", columns=[
        "RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "BRANCHID",
    ])
    bind_days_map, n_sampled = month_bind_dates(ctgviol, runs, result.cutoff, month)
    del ctgviol
    gen = cache.load("outgen2", columns=["RUNID", "BUSNUM", "ID", "LPDELTAMW", "FUELTYPE", "MW", "MWMAX"])
    branch = cache.load("outbranch2", columns=["RUNID", "FROMNUM", "TONUM", "CKT", "FROMNAME", "TONAME"])
    genunit = cache.load("genunit")
    scedname = gen_mapping.fetch_genunit_sced_name()
    bus_names = marginal_units.bus_name_map(branch)
    del branch
    gc.collect()

    ranked = (pd.read_csv(config.OUTPUT_ROOT / f"study_{study}" / "ranked_constraints.csv", low_memory=False)
              .drop_duplicates("CONSTRAINT").set_index("CONSTRAINT"))

    rows = []
    for c in short.index:
        row = {k: None for k in cols}
        try:
            r = ranked.loc[c]
            has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
            cov, n_days, marker, thin = coverage_and_days(
                c, has_ticket, r.get("DRIVER_TICKET_START"), r.get("DRIVER_TICKET_END"),
                bind_days_map, n_sampled, month)
            comp = value_row(study, c, gen, bus_names, genunit, scedname, month)
            p_bind = comp.get(f"P(bind) {label} on-peak")
            elam = comp.get("E[lambda|bind]")
            value = round(p_bind * elam * cov, 3) if (p_bind is not None and elam is not None) else None
            eff_sf, path_price = comp.get("_eff_sf"), comp.get("_path_price")
            edge = (round(value * eff_sf - path_price, 2)
                    if value is not None and eff_sf is not None and path_price is not None else None)
            row.update({
                f"Outage days in {label}": n_days,
                "coverage": f"{cov}{marker}",
                "thin window evidence": "thin window evidence" if thin else "",
                f"P(bind) {label} on-peak": p_bind,
                "E[lambda|bind]": elam,
                "lambda P50": comp.get("lambda P50"), "lambda P90": comp.get("lambda P90"),
                "unpriced deep hours %": comp.get("unpriced deep hours %"),
                f"{label} value $/MWh/SF": value,
                "Path": comp.get("Path"), "Path SF": comp.get("Path SF"),
                "Edge $": edge,
                "status": comp.get("_status", "ok") if value is not None else comp.get("_status", "unpriced"),
            })
        except Exception as e:
            row["status"] = f"lookup failed: {type(e).__name__}: {e}"
        rows.append(row)
    return pd.concat([short, pd.DataFrame(rows, index=short.index)], axis=1)
