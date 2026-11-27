"""Month valuation of the screened shortlist: on-peak fast-scan P(bind), shadow price over the
negative-headroom distribution, ticket/days coverage, cheapest path SF and edge.

`value_shortlist` attaches these columns to ScreeningResult.shortlist; the per-constraint pieces
(`value_row`, `coverage_and_days`, ...) are importable on their own.
"""
from __future__ import annotations

import gc
import re

import pandas as pd

from .. import config, periods
from ..cache import StudyCache
from ..constraint_id import ConstraintId, constraint_key
from ..extract import dam_offers, fastscan, gen_mapping, popt, shifts
from . import marginal_units, shadow_price as sp
from .constraints import BINDING_PCT, congestion_rent
from .screening import PENALTY_TIERS, ScreeningResult


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
    on-peak rows (ex-NERC holidays); returns (p_bind_onpeak, need_df, n_onpeak_hours, years) where
    need_df is the NEED_MW frame (negative-headroom onpeak hours only, for shadow_price) and years
    is the sorted list of years the on-peak hours span."""
    df = fastscan.headroom_for_month(config_id, periods.parse_month(month)[1])
    if df.empty:
        return None, pd.DataFrame(), 0, []
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    onpk = df[periods.fastscan_hour_class(df["TIMESTAMP"]) == "OnPeak"]
    if onpk.empty:
        return None, pd.DataFrame(), 0, []
    p_bind = float((onpk["HEADROOM"] < 0).mean())
    need = onpk[onpk["HEADROOM"] < 0].copy()
    need["NEED_MW"] = -need["HEADROOM"].astype(float)
    return p_bind, need, int(len(onpk)), sorted(int(y) for y in onpk["TIMESTAMP"].dt.year.unique())


def cpnode_sf(study_id: int, constraint: str, names: list[str]) -> dict[str, float]:
    names = [n for n in names if isinstance(n, str) and n]
    if not names:
        return {}
    cid = ConstraintId.parse(constraint)
    df = shifts.cpnode_sf_by_name(study_id, cid, names)
    return {r["NAME"]: float(r["SF"]) for _, r in df.iterrows()} if len(df) else {}


def offer_window_text(newest, days: int = dam_offers.LOOKBACK_DAYS) -> str:
    """'YYYY-MM-DD..YYYY-MM-DD': the offer-table window the capacity readers use."""
    end = pd.Timestamp(newest).normalize()
    return f"{(end - pd.Timedelta(days=days)).date()}..{end.date()}"


def relief_status(relief: sp.ReliefSet, window: str) -> str | None:
    """The reason a relief set cannot be priced (None when both stacks have units)."""
    if relief.n_band == 0:
        return "no relief units in SF band"
    n_map = len(relief.units)
    if n_map == 0:
        return f"{relief.n_band} in-band units, 0 mapped to a settlement point"
    if relief.capacity.empty:
        return f"{n_map} mapped units, 0 with DAM offers in {window}"
    if relief.up and relief.down:
        return None
    side = relief.units["SIDE"].value_counts()
    detail = (f"{int(side.get('up', 0))} up / {int(side.get('down', 0))} down mapped, {len(relief.capacity)} with DAM rows in {window}, "
              f"{len(relief.up)} up / {len(relief.down)} down with a usable offer")
    if not relief.up and not relief.down:
        return f"no units on either side with a usable offer ({detail})"
    return f"no units on the {'up' if not relief.up else 'down'} side ({detail})"


def value_row(study_id: int, c: str, gen, bus_names, genunit, scedname, month: str,
              offer_window: str = "the latest 14 days", out: dict | None = None) -> dict:
    """Step-2 valuation components for one class-A constraint; pass `out` to keep what was computed if a lookup raises."""
    out = {} if out is None else out
    out["_status"] = "ok"
    cid = ConstraintId.parse(c)
    f, t, ctg = cid.fromnum, cid.tonum, cid.ctglabel
    cfgs = fastscan.find_configs(study_id, int(f), int(t), ctg)
    if cfgs.empty:
        out["_status"] = "no fast-scan config"
        return out
    config_id = int(cfgs["CONFIG_ID"].iloc[0])
    direction = int(cfgs["DIRECTION"].iloc[0]) if pd.notna(cfgs["DIRECTION"].iloc[0]) else 1
    label = periods.month_label(month)
    p_bind, need, n_hours, years = fastscan_month_onpeak(config_id, month)
    if p_bind is None:
        out["_status"] = f"no {label} on-peak fast-scan hours"
        return out
    out[f"P(bind) {label} on-peak"] = round(p_bind, 3)
    out["_pbind_hours"] = n_hours
    out["_pbind_years"] = ", ".join(str(y) for y in years)

    # DIRECTION matters: on a reverse-bound branch (-1) a positive-PSENS
    # unit is relief (up), not the problem (down) — see relief_set's
    # docstring for the study-14412 canary this fixes (3380-3390-1@DPNAONA5).
    relief = sp.relief_set(study_id, c, gen, bus_names, genunit, scedname, direction=direction)
    out.update({"_n_band": relief.n_band, "_n_mapped": len(relief.units),
                "_n_offer_rows": len(relief.capacity), "_n_up": len(relief.up), "_n_down": len(relief.down)})
    reason = relief_status(relief, offer_window)
    if reason:
        out["_status"] = reason
        return out
    curve = relief.curve()
    out["_n_steps"] = len(curve)
    if not curve:
        out["_status"] = "no priceable up/down pair (shift-factor spread under 0.001)"
        return out
    if need.empty:
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
    out["_elam_low"] = round(float(dist["LAMBDA"].fillna(0.0).mean()), 1)
    out["_elam_high"] = round(float(dist["LAMBDA"].fillna(curve[-1]["lambda"]).mean()), 1)
    if float(priced.mean()) == 0.0 and pct.get("P50") == 0 and pct.get("P90") == 0:
        out["_status"] = "priced at 0: cheapest step is free relief"

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
        out["_sf_approx"] = bool(sf_marker)
    return out


def value_columns(month: str) -> list[str]:
    label = periods.month_label(month)
    return [
        f"Outage days in {label}", "coverage", "thin window evidence", f"P(bind) {label} on-peak",
        "E[lambda|bind]", "lambda P50", "lambda P90", "unpriced deep hours %",
        f"{label} value $/MWh/SF", "Path", "Path SF", "Edge $", "status",
    ]


def added_columns(month: str, cutoff: str) -> list[str]:
    """Columns appended after value_columns (the existing ones keep their names and order)."""
    label = periods.month_label(month)
    return [
        f"{label} value LOW $/MWh/SF", f"{label} value HIGH $/MWh/SF", "Edge LOW $", "Edge HIGH $",
        "Path price $/MWh", "Path SF value", "Path SF approximate",
        "valuation detail", "offer window", "relief units in band", "relief units mapped",
        "relief units with DAM rows", "relief units usable up", "relief units usable down", "curve steps",
        "P(bind) on-peak hours", "P(bind) years",
        "Post days sampled", "Sampled days in month", "Outage-day basis",
        rent_ex_penalty_col_name(cutoff), "Sibling/corridor note", "Low P(bind)",
    ]


# ticket states that grant no coverage (ERCOT outage scheduler: rejected / cancelled / withdrawn)
DEAD_TICKET_PREFIXES = ("rej", "cancel", "cncl", "withdr", "denied", "abort")
LOW_PBIND = 0.005
FAILED_PREFIX = "lookup failed: "
CORRIDOR_OVERLAP = 0.8


def ticket_dead_state(state, cancellation_date=None) -> str | None:
    """The ticket state to report when the ticket gives no coverage (rejected/cancelled), else None."""
    st = str(state).strip() if pd.notna(state) else ""
    if st and st.lower().startswith(DEAD_TICKET_PREFIXES):
        return st
    if pd.notna(cancellation_date):
        return st or "cancelled"
    return None


def binding_run_sets(ctgviol: pd.DataFrame) -> dict[str, frozenset]:
    """constraint -> the set of RUNIDs where it binds (LIMVIOLPCT >= BINDING_PCT)."""
    cv = ctgviol[ctgviol["LIMVIOLPCT"] >= BINDING_PCT]
    return {k: frozenset(g) for k, g in cv["RUNID"].groupby(constraint_key(cv))}


def sibling_notes(keys, run_sets: dict[str, frozenset], overlap_min: float = CORRIDOR_OVERLAP) -> dict[str, str]:
    """Per key: 'sibling of <key>' for constraints binding the identical run set, and 'corridor with <key>
    (overlap n/m)' for constraints on a different line whose runs overlap >= overlap_min of the larger set."""
    notes = {}
    for k in keys:
        a = run_sets.get(k)
        if not a:
            notes[k] = ""
            continue
        line = ConstraintId.parse(k).line_key
        sib, cor = [], []
        for k2, b in run_sets.items():
            if k2 == k:
                continue
            if b == a:
                sib.append(k2)
                continue
            m = max(len(a), len(b))
            if min(len(a), len(b)) / m < overlap_min or ConstraintId.parse(k2).line_key == line:
                continue
            n = len(a & b)
            if n / m >= overlap_min:
                cor.append((n, m, k2))
        parts = []
        if sib:
            parts.append("sibling of " + ", ".join(sorted(sib)[:3]) + (f" (+{len(sib) - 3} more)" if len(sib) > 3 else ""))
        for n, m, k2 in sorted(cor, key=lambda x: (-x[0] / x[1], x[2]))[:3]:
            parts.append(f"corridor with {k2} (overlap {n}/{m})")
        notes[k] = "; ".join(parts)
    return notes


def _bounds(p_bind, cov, elam_low, elam_high, eff_sf, path_price):
    """(value LOW, value HIGH, edge LOW, edge HIGH); None for any piece that cannot be computed."""
    if p_bind is None or cov is None or elam_low is None:
        return None, None, None, None
    lo, hi = round(p_bind * elam_low * cov, 3), round(p_bind * elam_high * cov, 3)
    if eff_sf is None or path_price is None:
        return lo, hi, None, None
    return lo, hi, round(lo * eff_sf - path_price, 2), round(hi * eff_sf - path_price, 2)


def value_shortlist(result: ScreeningResult, month: str) -> pd.DataFrame:
    """result.shortlist with the month-valuation columns appended (see value_columns, added_columns).

    Every shortlist row is valued; a failed lookup puts "lookup failed: ..." in that row's status.
    """
    label = periods.month_label(month)
    cols = value_columns(month) + added_columns(month, result.cutoff)
    short = result.shortlist
    if short.empty:
        return short.assign(**{c: pd.Series(dtype=object) for c in cols})

    study = result.study
    cache = StudyCache(study)
    runs = cache.load("opfrun")
    ctgviol = cache.load("outctgviol2", columns=[
        "RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "LIMVIOLLIMIT", "BRANCHID",
    ])
    bind_days_map, n_sampled = month_bind_dates(ctgviol, runs, result.cutoff, month)
    run_sets = binding_run_sets(ctgviol)
    outcon = cache.load("outconstraint2", columns=["RUNID", "FROMNUM", "TONUM", "CKT", "LPOPFCTGID", "OPFCNLAMBDA"])
    rent_ex = (congestion_rent(ctgviol, outcon, runs, result.cutoff, exclude_lambda=PENALTY_TIERS)
               .set_index("CONSTRAINT")["RENT_POST"])
    del ctgviol, outcon
    n_post_days = int(pd.to_datetime(runs["SIMDATE"])[pd.to_datetime(runs["SIMDATE"]) >= pd.to_datetime(result.cutoff)].dt.date.nunique())
    notes = sibling_notes(list(short.index), run_sets)
    gen = cache.load("outgen2", columns=["RUNID", "BUSNUM", "ID", "LPDELTAMW", "FUELTYPE", "MW", "MWMAX"])
    branch = cache.load("outbranch2", columns=["RUNID", "FROMNUM", "TONUM", "CKT", "FROMNAME", "TONAME"])
    genunit = cache.load("genunit")
    scedname = gen_mapping.fetch_genunit_sced_name()
    bus_names = marginal_units.bus_name_map(branch)
    del branch
    gc.collect()
    offer_window = offer_window_text(dam_offers.latest_delivery_date())

    ranked = (pd.read_csv(config.OUTPUT_ROOT / f"study_{study}" / "ranked_constraints.csv", low_memory=False)
              .drop_duplicates("CONSTRAINT").set_index("CONSTRAINT"))
    rent_col = rent_ex_penalty_col_name(result.cutoff)

    rows = []
    for c in short.index:
        row = {k: None for k in cols}
        comp: dict = {}
        cov = n_days = dead = None
        marker, thin, has_ticket, err = "", False, False, None
        try:
            r = ranked.loc[c]
            has_ticket = pd.notna(r.get("DRIVER_TICKET")) and pd.notna(r.get("DRIVER_TICKET_START"))
            dead = ticket_dead_state(r.get("DRIVER_TICKET_STATUS"), r.get("DRIVER_TICKET_CANCELLED")) if has_ticket else None
            cov, n_days, marker, thin = coverage_and_days(
                c, has_ticket, r.get("DRIVER_TICKET_START"), r.get("DRIVER_TICKET_END"),
                bind_days_map, n_sampled, month)
            if dead:
                cov, n_days, marker, thin = None, None, "", False
            value_row(study, c, gen, bus_names, genunit, scedname, month, offer_window, out=comp)
        except Exception as e:
            err = e
        p_bind = comp.get(f"P(bind) {label} on-peak")
        elam = comp.get("E[lambda|bind]")
        value = round(p_bind * elam * cov, 3) if (p_bind is not None and elam is not None and cov is not None) else None
        eff_sf, path_price = comp.get("_eff_sf"), comp.get("_path_price")
        edge = (round(value * eff_sf - path_price, 2)
                if value is not None and eff_sf is not None and path_price is not None else None)
        lo, hi, edge_lo, edge_hi = _bounds(p_bind, cov, comp.get("_elam_low"), comp.get("_elam_high"), eff_sf, path_price)
        detail = comp.get("_status", "ok") if value is not None else comp.get("_status", "unpriced")
        row.update({
            f"Outage days in {label}": n_days,
            "coverage": None if cov is None else f"{cov}{marker}",
            "thin window evidence": "thin window evidence" if thin else "",
            f"P(bind) {label} on-peak": p_bind,
            "E[lambda|bind]": elam,
            "lambda P50": comp.get("lambda P50"), "lambda P90": comp.get("lambda P90"),
            "unpriced deep hours %": comp.get("unpriced deep hours %"),
            f"{label} value $/MWh/SF": value,
            "Path": comp.get("Path"), "Path SF": comp.get("Path SF"),
            "Edge $": edge,
            "status": f"driver ticket {dead}" if dead else detail,
            f"{label} value LOW $/MWh/SF": lo, f"{label} value HIGH $/MWh/SF": hi,
            "Edge LOW $": edge_lo, "Edge HIGH $": edge_hi,
            "Path price $/MWh": path_price,
            "Path SF value": None if eff_sf is None else round(eff_sf, 3),
            "Path SF approximate": comp.get("_sf_approx"),
            "valuation detail": detail,
            "offer window": offer_window,
            "relief units in band": comp.get("_n_band"), "relief units mapped": comp.get("_n_mapped"),
            "relief units with DAM rows": comp.get("_n_offer_rows"),
            "relief units usable up": comp.get("_n_up"), "relief units usable down": comp.get("_n_down"),
            "curve steps": comp.get("_n_steps"),
            "P(bind) on-peak hours": comp.get("_pbind_hours"), "P(bind) years": comp.get("_pbind_years"),
            "Post days sampled": n_post_days, "Sampled days in month": n_sampled,
            "Outage-day basis": (f"ticket ({dead})" if dead else "ticket") if has_ticket else "sampled bind days (no ticket)",
            rent_col: float(rent_ex.get(c, 0.0)),
            "Sibling/corridor note": notes.get(c, ""),
            "Low P(bind)": bool(p_bind is not None and p_bind <= LOW_PBIND),
        })
        if err is not None:
            row["status"] = row["valuation detail"] = f"{FAILED_PREFIX}{type(err).__name__}: {err}"
        rows.append(row)
    return pd.concat([short, pd.DataFrame(rows, index=short.index)], axis=1)


def reason_key(status) -> str:
    """A status with its counts, dates and parenthesised detail removed, so equal reasons group."""
    t = str(status).split(" (")[0]
    t = re.sub(r"\d{4}-\d{2}-\d{2}\.\.\d{4}-\d{2}-\d{2}", "<window>", t)
    return re.sub(r"\d+", "N", t)


def valuation_summary(valued: pd.DataFrame, month: str) -> dict:
    """{n_rows, n_priced (non-null month value), reasons {reason: n} for unpriced rows, failed {error message: n}}."""
    value = pd.to_numeric(valued[f"{periods.month_label(month)} value $/MWh/SF"], errors="coerce")
    status = valued["status"].astype(str)
    failed = status[status.str.startswith(FAILED_PREFIX)]
    reasons = status[value.isna() & ~status.str.startswith(FAILED_PREFIX)].map(reason_key).value_counts()
    return {"n_rows": len(valued), "n_priced": int(value.notna().sum()), "reasons": reasons.to_dict(),
            "failed": failed.str[len(FAILED_PREFIX):].value_counts().to_dict()}


def rent_col_name(cutoff: str) -> str:
    d = pd.Timestamp(cutoff)
    return f"Rent post-{d.month}/{d.day} ($)"


def rent_ex_penalty_col_name(cutoff: str) -> str:
    d = pd.Timestamp(cutoff)
    return f"Rent post-{d.month}/{d.day} ex-penalty ($)"


def shortlist_rows(study: int, gated: pd.DataFrame, dirs: pd.Series, cutoff: str, month: str) -> pd.DataFrame:
    """One display row per shortlisted constraint (line label, names, direction, gate evidence, value columns), rent-sorted."""
    rent_col = rent_col_name(cutoff)
    br = (
        StudyCache(study).load("outbranch2", columns=["LABEL", "FROMNUM", "TONUM", "CKT"])
        .drop_duplicates(["FROMNUM", "TONUM", "CKT"])
        .set_index(["FROMNUM", "TONUM", "CKT"])
    )
    rows = []
    for c, r in gated.iterrows():
        cid = ConstraintId.parse(c)
        f, t, ckt, ctg = cid.fromnum, cid.tonum, cid.ckt, cid.ctglabel
        lab = br.loc[(f, t, ckt), "LABEL"] if (f, t, ckt) in br.index else None
        rows.append(
            {
                "Label": lab,
                "From bus": f,
                "From name": r.FROMNAME,
                "To bus": t,
                "To name": r.TONAME,
                "Ckt": ckt,
                "Contingency": ctg,
                "Direction": int(dirs.get(c, 1)),
                "Impact share": r["share"],
                "Pre binds": int(r.pre_binds),
                "Post binds": int(r.post_binds),
                "Post days (of 5)": int(r.post_days),
                "lam avg": r.lam_mean,
                "lam p50": r.lam_p50,
                "lam p50 gate": r.lam_p50_gate,
                "Dispatch nodes": int(r.NQUAL),
                rent_col: r.RENT_POST,
                "Ticket": r.DRIVER_TICKET if pd.notna(r.DRIVER_TICKET) else "",
                "Status": r.DRIVER_TICKET_STATUS if pd.notna(r.DRIVER_TICKET_STATUS) else "",
                "Flip exempt": bool(r.flip_exempt),
                "Thin intensity": bool(r.thin_intensity),
                **{k: r[k] for k in value_columns(month) + added_columns(month, cutoff)},
            }
        )
    return pd.DataFrame(rows).sort_values(rent_col, ascending=False)
