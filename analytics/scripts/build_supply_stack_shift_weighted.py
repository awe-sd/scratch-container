"""
Shift-WEIGHTED supply-stack COMPARISON behind ERCOT constraint 35055.

Unlike build_supply_stack_constraint.py (x = cumulative offered MW), here the
x-axis is CUMULATIVE (offered incremental MW x the owning unit's signed shift
factor) = MW of *constraint loading* implied by each offer tranche. y = SCED
offer price ($/MWh). Each curve is drawn as a merit-order step (sort tranches by
price, cumsum of the shift-weighted MW).

  x = SUM over tranches of (incremental offered MW  x  signed shift of the unit)
  y = SCED offer price

The total x-extent of a curve = SUM(offered MW x shift) = "loading-weighted MW
behind 35055" -- the headline number printed + annotated per curve.

Constraint 35055 = SAMSW 345kV -> VENSW 345kV (congConstraintID 195162,
"35055__A ... CONT:SVENFTS5"). Positive signed shift = the unit LOADS the
constraint (source / SAMSW side). Resource set per curve = signed shift >= 0.02
(inclusive) on the shift vector used.

ONE panel, TWO overlaid curves -- a pure TOPOLOGY (shift) comparison on the
SAME generation stack (2026-05-05 14:40 SCED offers, ON units):
  * PRE  shift = psenShiftID 75138717 (extracted 2026-05-13)
  * POST shift = psenShiftID 87025608 (extracted 2026-07-12)
Only the shift vector differs between the two curves, so the plot isolates how
the topology change re-weighted the same dispatch onto 35055.

NON-THERMAL ONLY: we keep only zero-fuel-cost resource types (WIND / PVGR solar
/ PWRSTR battery) and exclude every fuel-burning thermal type (CLLIG, CCGT*,
SCGT*, GS*, NUC, DSL, DGR, ...). The kept-vs-excluded ResourceType breakdown is
printed for transparency.

Shift vector: AW.dbo.psenShiftView, signed shift = psen*psenShiftSign, joined
cpnode -> isoErcotScedGen for ResourceName/ResourceType. A resource maps to one
cpnode; we dedupe per (psenShiftID, ResourceName) keeping max |shift|.

Offer curve: isoErcotScedGenResource.CurveMW1..15 / CurvePrice1..15 are the
CUMULATIVE offered MW at ascending offer prices; per (resource, interval) we
sort by price and diff to incremental tranches (increments()). ON units only
(TelemeteredStatus LIKE 'ON%').

READ-ONLY. Pulls cache to analytics/data/ss_sw_*.parquet; re-runs read the cache.
Each shift vector was extracted on a different date than the 2026-05-05 offers,
a documented climatology approximation (a shift vector from one topology/date
applied to dispatch from another date).
"""
import sys
from pathlib import Path

import awconnect
import pandas as pd
import plotly.graph_objects as go
from awconnect import db

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from build_supply_stack_constraint import increments, supply_curve  # noqa: E402

DATA = SCRIPTS.parents[0] / "data"
OUT = SCRIPTS.parents[0] / "output"
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

PRICE_COLS = [f"CurvePrice{i}" for i in range(1, 16)]
MW_COLS = [f"CurveMW{i}" for i in range(1, 16)]
ALL_CURVE_SQL = ", ".join(f"T1.{c}" for c in (PRICE_COLS + MW_COLS))

PRE_SHIFT = 75138717   # extracted 2026-05-13 (pre-topology)
POST_SHIFT = 87025608  # extracted 2026-07-12 (post/current)
SHIFT_FLOOR = 0.02     # inclusive
ELEM = "35055 (SAMSW->VENSW 345kV)"

TS_2026 = "2026-05-05 14:40"

# DENYLIST: exclude fuel-burning THERMAL resource types; keep ALL other
# (non-thermal) gen types -- WIND, PVGR (solar), PWRSTR (battery), HYDRO, ESR,
# and anything else that isn't in this set. A denylist (vs allowlist) means new
# non-thermal types are covered automatically.
THERMAL = {
    "CLLIG", "CCGT90", "CCGT180", "CCLE90", "CCLE180", "SCLE90", "SCGT90",
    "GSNONR", "GSREH", "GSSUP", "GSCND", "GSTUR", "DSL", "NUC",
}

# per-gen-type colors for the legend groups; unknown types fall back to a cycle
TYPE_COLOR = {
    "Combined": "#333333",
    "WIND": "#2ca02c", "PVGR": "#ff7f0e", "PWRSTR": "#9467bd",
    "HYDRO": "#17becf", "ESR": "#8c564b",
}
FALLBACK_COLORS = ["#e377c2", "#bcbd22", "#7f7f7f", "#1f77b4", "#d62728"]
# line dash encodes the shift vector; color encodes the gen type
SHIFT_STYLE = {"PRE": ("solid", "circle"), "POST": ("dash", "x")}


# ----------------------------------------------------------------------------- fetch
def fetch_shift(psen):
    """Signed shift per unit (>= SHIFT_FLOOR) for one shift vector."""
    f = DATA / f"ss_sw_shift_{psen}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    sql = f"""
        SELECT g.ResourceName, g.ResourceType, (ps.psen*ps.psenShiftSign) AS shift
        FROM AW.dbo.psenShiftView ps
        JOIN AW.dbo.cpnode c ON ps.cpNodeId = c.cpnodeid
        JOIN AW.dbo.isoErcotScedGen g ON g.cpnodeid = c.cpnodeid
        WHERE ps.psenShiftID = {psen}
          AND (ps.psen*ps.psenShiftSign) >= {SHIFT_FLOOR}
    """
    df = db.getDfFromAwDb(sql)
    # dedupe per ResourceName keeping the max |shift| (all positive here)
    df["abs_shift"] = df["shift"].abs()
    df = (df.sort_values("abs_shift", ascending=False)
            .drop_duplicates("ResourceName")
            .drop(columns="abs_shift")
            .reset_index(drop=True))
    df.to_parquet(f, index=False)
    print(f"[shift {psen}] {len(df)} units >= {SHIFT_FLOOR} "
          f"({df['ResourceType'].value_counts().to_dict()})")
    return df


def fetch_offers(ts, names):
    """One SCED interval covering ts, for the given resource-name set (union)."""
    t = pd.Timestamp(ts)
    f = DATA / f"ss_sw_offers_{t:%Y%m%d_%H%M}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    lo = t.strftime("%Y-%m-%d %H:%M:00")
    hi = (t + pd.Timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:00")
    in_list = ", ".join("'" + n.replace("'", "''") + "'" for n in sorted(names))
    sql = f"""
        SELECT T1.TimeStamp, T2.ResourceName, T2.ResourceType, T1.TelemeteredStatus,
               T1.BasePoint, T1.HSL, T1.LSL, {ALL_CURVE_SQL}
        FROM AW.dbo.isoErcotScedGenResource T1
        JOIN AW.dbo.isoErcotScedGen T2 ON T1.genID = T2.genID
        WHERE T1.TimeStamp >= '{lo}' AND T1.TimeStamp < '{hi}'
          AND T2.ResourceName IN ({in_list})
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[offers {ts}] {len(df)} rows, {df['TimeStamp'].nunique()} interval(s) matched")
    return df


# ----------------------------------------------------------------------------- transform
def shift_weighted_long(offers, shift_df, tag=None):
    """Non-thermal shift-weighted offer tranches for one (offers, shift) pair.

    ON units only; inner-join the per-unit signed shift (enforces the >=0.02
    set); keep ALL non-thermal resource types (everything NOT in THERMAL); w_mw =
    incremental offered MW * signed shift. Returns the long tranche table
    (NOT yet cumsum'd) so callers can cumsum the combined set or any per-type
    subset. If `tag` is given, print the kept-vs-excluded ResourceType breakdown.
    """
    on = offers[offers["TelemeteredStatus"].str.startswith("ON", na=False)].copy()
    long = increments(on, weight=1.0)               # w_mw == inc_mw here
    long = long.merge(shift_df[["ResourceName", "shift"]], on="ResourceName", how="inner")
    long["w_mw"] = long["inc_mw"] * long["shift"]    # shift-weighted MW = constraint loading
    long = long[long["w_mw"] > 0].copy()

    nonthermal = ~long["ResourceType"].isin(THERMAL)
    if tag is not None:
        by_unit = long.drop_duplicates("ResourceName")
        kept = by_unit[~by_unit["ResourceType"].isin(THERMAL)]["ResourceType"].value_counts().to_dict()
        excl = by_unit[by_unit["ResourceType"].isin(THERMAL)]["ResourceType"].value_counts().to_dict()
        print(f"[{tag}] KEPT non-thermal units {sum(kept.values())}: {kept}")
        print(f"[{tag}] EXCLUDED thermal units {sum(excl.values())}: {excl}")
    return long[nonthermal].copy()


# ----------------------------------------------------------------------------- plot
def type_color(t, i):
    return TYPE_COLOR.get(t, FALLBACK_COLORS[i % len(FALLBACK_COLORS)])


def add_curve(fig, curve, color, dash, symbol, name, group, width=2):
    """One shift-weighted step supply curve. legendgroup = gen type so the
    legend toggles BY TYPE (with groupclick='togglegroup'). Returns loading-MW."""
    if not len(curve):
        return 0.0
    total = float(curve["cum"].iloc[-1])
    fig.add_trace(go.Scatter(
        x=curve["cum"], y=curve["price"], mode="lines",
        line=dict(color=color, width=width, shape="hv", dash=dash),
        name=name, legendgroup=group, legendgrouptitle_text=group,
        showlegend=True, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=curve["cum"], y=curve["price"], mode="markers",
        marker=dict(size=5, color=color, symbol=symbol, line=dict(width=0.4, color="white")),
        name=name, legendgroup=group, showlegend=False,
        customdata=curve[["ResourceName", "ResourceType", "w_mw", "shift", "inc_mw"]].to_numpy(),
        hovertemplate=(
            "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
            "offer $%{y:,.2f}/MWh<br>"
            "tranche %{customdata[4]:.1f} MW x shift %{customdata[3]:.3f} "
            "= %{customdata[2]:.2f} loading-MW<br>"
            "cum loading %{x:,.1f} MW<extra>" + name + "</extra>")))
    return total


def build():
    awconnect.configure("read_only")

    shift_pre = fetch_shift(PRE_SHIFT)
    shift_post = fetch_shift(POST_SHIFT)
    union = set(shift_pre["ResourceName"]) | set(shift_post["ResourceName"])
    print(f"[union] {len(union)} distinct units across PRE+POST sets")

    off = fetch_offers(TS_2026, union)
    n_on = off[off["TelemeteredStatus"].str.startswith("ON", na=False)]["ResourceName"].nunique()
    print(f"[offers {TS_2026}] {off['ResourceName'].nunique()} units, {n_on} ON")

    # SAME generation stack (2026-05-05 14:40 ON offers), two shifts, ALL non-thermal
    long_pre = shift_weighted_long(off, shift_pre, tag="PRE 75138717")
    long_post = shift_weighted_long(off, shift_post, tag="POST 87025608")

    # gen types present across either shift, ordered by total loading-MW desc, so
    # the biggest contributors sit at the top of the (per-type) legend groups
    tot_by_type = (pd.concat([long_pre, long_post])
                     .groupby("ResourceType")["w_mw"].sum().sort_values(ascending=False))
    types_present = list(tot_by_type.index)
    color_idx = {t: i for i, t in enumerate(types_present)}
    series = ["Combined"] + types_present   # each per-type curve = that type's own cumulative stack
    print(f"[types] non-thermal gen types present: {types_present}")

    # ---------- figure: Combined + one curve per gen type, x2 shifts ----------
    fig = go.Figure()
    totals, csv_rows = {}, []
    for sk, psen, long_df in [("PRE", str(PRE_SHIFT), long_pre), ("POST", str(POST_SHIFT), long_post)]:
        dash, symbol = SHIFT_STYLE[sk]
        for s in series:
            sub = long_df if s == "Combined" else long_df[long_df["ResourceType"] == s]
            if not len(sub):
                continue
            curve = supply_curve(sub)
            color = TYPE_COLOR["Combined"] if s == "Combined" else type_color(s, color_idx.get(s, 0))
            tot = add_curve(fig, curve, color, dash, symbol, f"{s} · {sk} {psen}", s,
                            width=3 if s == "Combined" else 2)
            totals[(sk, s)] = tot
            csv_rows.append({"shift": f"{sk} {psen}", "series": s,
                             "n_units": int(sub["ResourceName"].nunique()),
                             "total_loading_MW": tot})

    t_pre, t_post = totals.get(("PRE", "Combined"), 0.0), totals.get(("POST", "Combined"), 0.0)
    delta = t_post - t_pre
    direction = "INCREASED" if delta > 0 else "DECREASED"
    pct = (delta / t_pre * 100) if t_pre else 0.0
    fig.add_annotation(
        xref="x domain", yref="y domain", x=0.97, y=0.05,
        xanchor="right", yanchor="bottom", align="right", showarrow=False,
        bordercolor="#888", borderwidth=1, bgcolor="rgba(255,255,255,0.92)",
        font=dict(size=12),
        text="<br>".join([
            "<b>Total loading-weighted MW behind 35055</b> (all non-thermal)",
            "<i>Σ offered MW × signed shift</i>",
            f"PRE  shift 75138717 (Combined): {t_pre:,.0f} MW",
            f"POST shift 87025608 (Combined): {t_post:,.0f} MW",
            f"<b>Pre→Post: {direction} {abs(delta):,.0f} MW ({pct:+.1f}%)</b>",
            "<i>click a gen-type in the legend to toggle it; double-click to isolate</i>",
        ]))

    fig.update_yaxes(title_text="SCED offer price ($/MWh)")
    fig.update_xaxes(title_text="cumulative offered MW × signed shift (loading-MW behind 35055)")
    fig.update_layout(
        template="plotly_white", width=1250, height=780,
        title=dict(text=(
            f"Shift-weighted supply stack behind constraint {ELEM} — topology (shift) change, by gen type"
            "<br><sup>SAME generation stack (2026-05-05 14:40 SCED offers, ON, ALL non-thermal gen types) "
            "weighted by two shift vectors — PRE 75138717 (solid) vs POST 87025608 (dashed). "
            "x = cumulative (offered incremental MW × unit signed shift) = MW of 35055 loading; "
            "y = SCED offer price. Color = gen type; each per-type curve is that type's OWN cumulative "
            "stack, 'Combined' is the full stack. Resource set = signed shift ≥ 0.02 on 195162 / "
            "CONT:SVENFTS5; thermal (fuel-burning) units excluded. "
            "CLIMATOLOGY CAVEAT: each shift vector was extracted on a different date than the offers."
            "</sup>"), x=0.01, xanchor="left"),
        legend=dict(groupclick="togglegroup", tracegroupgap=8, x=1.01, xanchor="left",
                    y=1, yanchor="top"),
        margin=dict(t=150, r=240))

    html_out = OUT / "supply_stack_shift_weighted_35055.html"
    fig.write_html(html_out, include_plotlyjs=True, full_html=True)

    summary = pd.DataFrame(csv_rows)
    csv_out = OUT / "supply_stack_shift_weighted_35055.csv"
    summary.to_csv(csv_out, index=False)

    print("\n=== loading-weighted MW behind 35055 by shift × gen type ===")
    print(summary.to_string(index=False))
    print(f"\nTopology effect (Combined): PRE {t_pre:,.0f} -> POST {t_post:,.0f} MW "
          f"({direction} by {abs(delta):,.0f} MW, {pct:+.1f}%)")
    print(f"-> {html_out}")
    print(f"-> {csv_out}")


if __name__ == "__main__":
    build()
