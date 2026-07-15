"""
Supply stack behind a transmission constraint, from SCED offer curves.

For a constraint (identified by a psenShiftID whose shift vector says which
resources materially affect it), build the merit-order supply stack of those
resources' SCED energy offer curves. Two panels in ONE html:

  Panel A -- SINGLE SCED interval (e.g. the binding interval you picked).
  Panel B -- AVERAGE offer stack over a set of hours in a period
             (e.g. May 2026, HE 12-16 on-peak afternoon).

"Behind the constraint" = resources whose signed shift factor
(psen * psenShiftSign) on the constraint is >= a threshold (default 0.10),
i.e. the units SCED can move to control the constraint flow. This mirrors the
production ercot_create_gen_supply_stack_curve_from_SCED logic.

Offer curve: isoErcotScedGenResource.CurveMW1..15 / CurvePrice1..15 are the
CUMULATIVE offered MW at each ascending offer price. Per (resource, interval)
we sort by price and diff to incremental MW per tranche, then pool.

  * Panel A weights every increment by 1.0 (one interval).
  * Panel B weights by 1/N where N = number of distinct SCED intervals in the
    window, so the x-axis reads "average offered MW per interval at each price"
    (OUT/offline intervals correctly contribute 0 for that unit).

Markers added on top of the stack:
  * marginal unit(s) on the constraint = ON units dispatched strictly interior
    to their limits (LSL+tol < BasePoint < HSL-tol) -- the ones SCED is actually
    regulating; highlighted with a star at their offer-price-at-dispatch and
    named. (Panel B: interior-unit concept is per-interval, so we only annotate
    the modal interior unit over the window -- no invented marker.)
  * RT energy price = ercotLambda.SystemLambda (system marginal energy price),
    drawn as a horizontal reference. Expect a large gap below the renewable
    offers: that gap is the shift x shadow-price congestion effect, not a bug.

Read-only. Pulls cache to analytics/data/*.parquet; re-runs read the cache.
The psen (shift) vector is the current topology applied to the chosen dispatch
period -- a documented climatology approximation when the period predates the
psen extraction.
"""
from pathlib import Path

import awconnect
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from awconnect import db
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PRICE_COLS = [f"CurvePrice{i}" for i in range(1, 16)]
MW_COLS = [f"CurveMW{i}" for i in range(1, 16)]
INTERIOR_TOL = 0.5  # MW: dispatch must be this far inside both limits to count as "marginal"

TYPE_COLOR = {
    "WIND": "#1b9e77", "PVGR": "#e6ab02", "PWRSTR": "#7570b3",
    "CLLIG": "#d95f02", "SCGT90": "#e7298a", "CCGT90": "#a6761d",
}
DEFAULT_TYPE_COLOR = "#999999"

CONFIGS = [
    {
        "psenShiftID": 87025608,
        "shift_threshold": 0.10,
        "elem_label": "35055 (SAMSW→VENSW 345kV)",
        # Panel A: the binding SCED interval you picked (nearest 5-min interval used)
        "single_ts": "2026-05-05 14:40",
        # Panel B: average offer stack over this window
        "period_start": "2026-05-01",
        "period_end": "2026-06-01",
        "period_HEs": [12, 13, 14, 15, 16],   # on-peak afternoon, hour-ending
        "period_label": "May 2026, HE 12–16 (on-peak afternoon)",
        "out": "supply_stack_35055",
    },
]

_ALL_CURVE_SQL = ", ".join(f"T1.{c}" for c in (PRICE_COLS + MW_COLS))


# ----------------------------------------------------------------------------- fetch
def fetch_resources(cfg):
    """Resources behind the constraint (signed shift >= threshold) + their shift."""
    f = DATA / f"supply_resources_{cfg['psenShiftID']}_{int(cfg['shift_threshold']*100)}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    sql = f"""
        SELECT DISTINCT g.ResourceName, g.ResourceType, (ps.psen*ps.psenShiftSign) AS shift
        FROM AW.dbo.psenShiftView ps
        JOIN AW.dbo.cpnode c ON ps.cpNodeId = c.cpnodeid
        JOIN AW.dbo.isoErcotScedGen g ON g.cpnodeid = c.cpnodeid
        WHERE ps.psenShiftID = {cfg['psenShiftID']}
          AND (ps.psen*ps.psenShiftSign) >= {cfg['shift_threshold']}
    """
    df = db.getDfFromAwDb(sql)
    df = df.sort_values("shift", ascending=False).drop_duplicates("ResourceName")
    df.to_parquet(f, index=False)
    print(f"[resources] {len(df)} units behind constraint "
          f"({df['ResourceType'].value_counts().to_dict()})")
    return df


def _res_subquery(cfg):
    return f"""(SELECT DISTINCT g.ResourceName FROM AW.dbo.psenShiftView ps
                 JOIN AW.dbo.cpnode c ON ps.cpNodeId=c.cpnodeid
                 JOIN AW.dbo.isoErcotScedGen g ON g.cpnodeid=c.cpnodeid
                 WHERE ps.psenShiftID={cfg['psenShiftID']}
                   AND (ps.psen*ps.psenShiftSign) >= {cfg['shift_threshold']})"""


def fetch_single(cfg):
    """One SCED interval: the interval covering single_ts (floor to the 5-min slot)."""
    ts = pd.Timestamp(cfg["single_ts"])
    f = DATA / f"supply_single_{cfg['psenShiftID']}_{ts:%Y%m%d_%H%M}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    lo = ts.strftime("%Y-%m-%d %H:%M:00")
    hi = (ts + pd.Timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:00")
    sql = f"""
        SELECT T1.TimeStamp, T2.ResourceName, T2.ResourceType, T1.TelemeteredStatus,
               T1.BasePoint, T1.HSL, T1.LSL, {_ALL_CURVE_SQL}
        FROM AW.dbo.isoErcotScedGenResource T1
        JOIN AW.dbo.isoErcotScedGen T2 ON T1.genID = T2.genID
        WHERE T1.TimeStamp >= '{lo}' AND T1.TimeStamp < '{hi}'
          AND T2.ResourceName IN {_res_subquery(cfg)}
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[single] {cfg['single_ts']}: {len(df)} rows "
          f"({df['TimeStamp'].nunique()} interval(s) matched)")
    return df


def fetch_period(cfg):
    """All SCED rows for the constrained resources over the period + hour-ending set."""
    f = DATA / (f"supply_period_{cfg['psenShiftID']}_"
                f"{cfg['period_start'].replace('-', '')}_{cfg['period_end'].replace('-', '')}.parquet")
    if f.exists():
        return pd.read_parquet(f)
    clock_hours = ",".join(str(he - 1) for he in cfg["period_HEs"])  # HE -> clock hour
    sql = f"""
        SELECT T1.TimeStamp, T2.ResourceName, T2.ResourceType, T1.TelemeteredStatus,
               T1.BasePoint, T1.HSL, T1.LSL, {_ALL_CURVE_SQL}
        FROM AW.dbo.isoErcotScedGenResource T1
        JOIN AW.dbo.isoErcotScedGen T2 ON T1.genID = T2.genID
        WHERE T1.TimeStamp >= '{cfg['period_start']}' AND T1.TimeStamp < '{cfg['period_end']}'
          AND DATEPART(hour, T1.TimeStamp) IN ({clock_hours})
          AND T2.ResourceName IN {_res_subquery(cfg)}
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[period] {cfg['period_label']}: {len(df):,} rows, "
          f"{df['TimeStamp'].nunique()} intervals")
    return df


def fetch_lambda(cfg):
    f = DATA / (f"supply_lambda_{cfg['period_start'].replace('-', '')}_"
                f"{cfg['period_end'].replace('-', '')}.parquet")
    if f.exists():
        return pd.read_parquet(f)
    sql = (f"SELECT SCEDTimestamp, SystemLambda FROM AW.dbo.ercotLambda "
           f"WHERE SCEDTimestamp >= '{cfg['period_start']}' AND SCEDTimestamp < '{cfg['period_end']}'")
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[lambda] {len(df):,} rows")
    return df


# ----------------------------------------------------------------------------- transform
def increments(df, weight):
    """Wide offer-curve rows -> long incremental tranches (price, inc_mw, w_mw).

    Diffs cumulative CurveMW *within each row* (a single (resource, interval)),
    then scales by `weight`. df must have one row per (resource, interval)."""
    d = df.reset_index(drop=True).copy()
    d["_rid"] = np.arange(len(d))
    p = d.melt(id_vars="_rid", value_vars=PRICE_COLS, var_name="pc", value_name="price")
    p["k"] = p["pc"].str.removeprefix("CurvePrice").astype(int)
    m = d.melt(id_vars="_rid", value_vars=MW_COLS, var_name="mc", value_name="cum_mw")
    m["k"] = m["mc"].str.removeprefix("CurveMW").astype(int)
    long = p.merge(m[["_rid", "k", "cum_mw"]], on=["_rid", "k"]).dropna(subset=["price", "cum_mw"])
    long = long.sort_values(["_rid", "price", "cum_mw"])
    long["inc_mw"] = long.groupby("_rid")["cum_mw"].diff().fillna(long["cum_mw"])
    long = long[long["inc_mw"] > 0].copy()
    long = long.merge(d[["_rid", "ResourceName", "ResourceType"]], on="_rid")
    long["w_mw"] = long["inc_mw"] * weight
    return long


def supply_curve(long):
    """Merit order: sort tranches by price, cumulative sum of weighted MW."""
    s = long.sort_values("price").reset_index(drop=True)
    s["cum"] = s["w_mw"].cumsum()
    s["cum_start"] = s["cum"] - s["w_mw"]
    return s


def offer_at_dispatch(row):
    """Offer price of the tranche whose cumulative MW first reaches BasePoint."""
    tr = [(row[f"CurvePrice{i}"], row[f"CurveMW{i}"]) for i in range(1, 16)]
    tr = [(pp, mm) for pp, mm in tr if pd.notna(pp) and pd.notna(mm)]
    if not tr:
        return np.nan
    tr.sort(key=lambda x: x[1])  # by cumulative MW
    for pp, mm in tr:
        if mm >= row["BasePoint"] - 1e-6:
            return pp
    return tr[-1][0]


def interior_units(df):
    """ON units dispatched strictly inside their limits = SCED-regulated (marginal)."""
    on = df[df["TelemeteredStatus"].str.startswith("ON", na=False)].copy()
    mask = (on["BasePoint"] > on["LSL"] + INTERIOR_TOL) & (on["BasePoint"] < on["HSL"] - INTERIOR_TOL)
    m = on[mask].copy()
    if len(m):
        m["offer_at_dispatch"] = m.apply(offer_at_dispatch, axis=1)
    return m


# ----------------------------------------------------------------------------- plot
def add_stack(fig, curve, row, col, xtitle):
    """Draw one supply stack: grey step line + per-ResourceType colored tranche dots."""
    fig.add_trace(go.Scatter(
        x=curve["cum"], y=curve["price"], mode="lines", line=dict(color="rgba(80,80,80,0.55)",
        width=1.5, shape="hv"), name="supply curve", legendgroup="curve",
        showlegend=(col == 1), hoverinfo="skip"), row=row, col=col)
    for rtype, g in curve.groupby("ResourceType"):
        fig.add_trace(go.Scatter(
            x=g["cum"], y=g["price"], mode="markers",
            marker=dict(size=6, color=TYPE_COLOR.get(rtype, DEFAULT_TYPE_COLOR),
                        line=dict(width=0.4, color="white")),
            name=rtype, legendgroup=rtype, showlegend=(col == 1),
            customdata=np.stack([g["ResourceName"], g["w_mw"]], axis=-1),
            hovertemplate=("<b>%{customdata[0]}</b> (" + rtype + ")<br>"
                           "offer $%{y:,.2f}/MWh<br>tranche %{customdata[1]:.1f} MW<br>"
                           "cum %{x:,.0f} MW<extra></extra>")), row=row, col=col)


def build(cfg):
    resources = fetch_resources(cfg)
    single = fetch_single(cfg)
    period = fetch_period(cfg)
    lam = fetch_lambda(cfg)
    lam["SCEDTimestamp"] = pd.to_datetime(lam["SCEDTimestamp"])
    lam["SystemLambda"] = pd.to_numeric(lam["SystemLambda"], errors="coerce")

    # ---- Panel A: single interval (ON units only, per reference) ----
    single_on = single[single["TelemeteredStatus"].str.startswith("ON", na=False)].copy()
    curve_a = supply_curve(increments(single_on, weight=1.0))
    marg = interior_units(single)
    ts = pd.Timestamp(cfg["single_ts"])
    lam_a = lam.loc[(lam["SCEDTimestamp"] >= ts) & (lam["SCEDTimestamp"] < ts + pd.Timedelta(minutes=5)),
                    "SystemLambda"]
    lam_a = float(lam_a.iloc[0]) if len(lam_a) else float("nan")

    # ---- Panel B: averaged over period (ON rows pooled, /N intervals) ----
    n_int = period["TimeStamp"].nunique()
    period_on = period[period["TelemeteredStatus"].str.startswith("ON", na=False)].copy()
    curve_b = supply_curve(increments(period_on, weight=1.0 / n_int))
    clock_hours = [he - 1 for he in cfg["period_HEs"]]
    lam_p = lam[lam["SCEDTimestamp"].dt.hour.isin(clock_hours)]["SystemLambda"]
    lam_b = float(lam_p.mean())
    # modal interior unit over the window (per-interval interior test)
    per_marg = interior_units(period)
    modal = (per_marg["ResourceName"].value_counts().idxmax() if len(per_marg) else "n/a")

    # ---------- figure ----------
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
        subplot_titles=(
            f"A. Single interval — {ts:%Y-%m-%d %H:%M} (HE{ts.hour + 1})",
            f"B. Average offer stack — {cfg['period_label']}"))

    add_stack(fig, curve_a, 1, 1, "cumulative offered MW")
    add_stack(fig, curve_b, 1, 2, "avg offered MW / interval")

    # marginal-unit stars (Panel A) at each interior unit's offer-price-at-dispatch,
    # placed on the aggregate curve at the cum MW where that unit's tranches sit
    for _, u in marg.iterrows():
        seg = curve_a[curve_a["ResourceName"] == u["ResourceName"]]
        xpos = float(seg["cum"].iloc[-1]) if len(seg) else float(curve_a["cum"].iloc[-1])
        fig.add_trace(go.Scatter(
            x=[xpos], y=[u["offer_at_dispatch"]], mode="markers+text",
            marker=dict(symbol="star", size=16, color="gold", line=dict(width=1.2, color="black")),
            text=[u["ResourceName"]], textposition="top center", textfont=dict(size=10),
            name="marginal unit", legendgroup="marg", showlegend=(_ == marg.index[0]),
            hovertemplate=(f"<b>{u['ResourceName']}</b> — marginal on constraint<br>"
                           f"dispatched {u['BasePoint']:.0f} MW (LSL {u['LSL']:.0f} / HSL {u['HSL']:.0f})<br>"
                           f"offer @ dispatch $%{{y:,.2f}}/MWh<extra></extra>")), row=1, col=1)

    # RT energy price horizontal reference on each panel
    for col, val, lab in ((1, lam_a, "single"), (2, lam_b, "avg")):
        if np.isfinite(val):
            fig.add_hline(y=val, line=dict(color="firebrick", width=1.6, dash="dash"),
                          annotation_text=f"RT energy price ${val:,.1f}/MWh ({lab})",
                          annotation_position="top left", row=1, col=col)

    fig.update_yaxes(title_text="SCED offer price ($/MWh)", row=1, col=1)
    fig.update_xaxes(title_text="cumulative offered MW (merit order)", row=1, col=1)
    fig.update_xaxes(title_text="avg offered MW per interval", row=1, col=2)

    n_on_a = single_on["ResourceName"].nunique()
    fig.update_layout(
        template="plotly_white", width=1350, height=720,
        title=dict(text=(
            f"Supply stack behind constraint {cfg['elem_label']} — SCED offer curves"
            f"<br><sup>resources with signed shift ≥ {cfg['shift_threshold']:.2f} on the constraint "
            f"(psenShiftID {cfg['psenShiftID']}); ON units only. "
            f"A: {n_on_a} ON units at the binding interval, marginal = interior-dispatch unit(s). "
            f"B: averaged over {n_int:,} SCED intervals (1/N-weighted); modal interior unit: {modal}. "
            "Renewable offers sit far below the energy-price line — that gap is the shift×shadow-price "
            "congestion effect.</sup>"), x=0.01, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=140))

    html_out = OUT / f"{cfg['out']}.html"
    fig.write_html(html_out, include_plotlyjs=True, full_html=True)
    print(f"\n[A] {n_on_a} ON units, marginal={list(marg['ResourceName'])}, "
          f"energy ${lam_a:,.2f}")
    print(f"[B] N={n_int} intervals, avg energy ${lam_b:,.2f}, modal interior unit={modal}")
    print(f"-> {html_out}")

    # tidy CSV of both stacks
    curve_a.assign(panel="single")[["panel", "ResourceName", "ResourceType", "price", "w_mw", "cum"]] \
        .to_csv(OUT / f"{cfg['out']}_stack.csv", index=False)


def main():
    awconnect.configure("read_only")
    for cfg in CONFIGS:
        print(f"\n=== {cfg['elem_label']} (psen {cfg['psenShiftID']}) ===")
        build(cfg)


if __name__ == "__main__":
    main()
