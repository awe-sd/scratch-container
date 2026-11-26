"""
THERMAL generators electrically behind ERCOT constraint 35055 (SAMSW->VENSW 345kV).

Read-only. Answers four questions and writes a CSV + a plotly HTML.

  Q1  Why does n_res differ so much between the PRE topology shift vector
      (psenShiftID 75138717, ~859 res at shift>=0.05) and the POST/current one
      (87025608, ~106)?  Compare both FULL vectors: universe size + shift-
      magnitude distribution + which high-shift resources dropped out.

  Q2  Thermal gens on the SOURCE side of 35055 under the CURRENT shift (87025608)
      = thermal ResourceType with signed shift (psen*psenShiftSign) >= 0.05.
      (0.05 is the convention the "behind the constraint" count is built on; the
      any-positive set is 493 units of weakly-coupled South-Texas fleet, reported
      only in aggregate.)  Enriched with plant/fuel from AW.DBO.GENUNIT.

  Q3  Do they run consistently in summer 2025 (Jun 1 - Sep 30)?  Per unit:
      capacity (max HSL), % intervals online, avg BasePoint when online,
      avg offer-price-at-dispatch when online.  -> CSV.

  Q4  Does their running correlate with system load?  Hourly mean output vs
      ercotLoadView ERCOT_ALL_LD (HE = clock hour + 1); Pearson + Spearman.

Signed shift convention (verified): shift = psen*psenShiftSign on psenShiftView;
positive = unit on the SOURCE (SAMSW) side, loads the constraint.  Dedup per
(psenShiftID, ResourceName) keeping max signed shift.

DB pulls cache to analytics/data/thm_*.parquet; re-runs read the cache.
"""
from pathlib import Path

import awconnect
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from awconnect import db, snowflake
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)

PRE_PID, POST_PID = 75138717, 87025608
SHIFT_CUT = 0.05
# fuel-burning dispatchable ResourceTypes (from DISTINCT isoErcotScedGen.ResourceType)
THERMAL = {"CCGT90", "CCLE90", "CLLIG", "SCGT90", "SCLE90", "GSNONR", "GSREH", "GSSUP", "DSL"}
PRICE_COLS = [f"CurvePrice{i}" for i in range(1, 16)]
MW_COLS = [f"CurveMW{i}" for i in range(1, 16)]

SUMMER_LO, SUMMER_HI = "2025-06-01", "2025-10-01"  # [Jun 1, Oct 1)  == Jun1..Sep30 incl


# --------------------------------------------------------------------------- helpers
def dedup_vector(pid):
    """Cached full shift vector -> one row per ResourceName (generator nodes), max shift."""
    df = pd.read_parquet(DATA / f"thm_shiftvec_{pid}.parquet")
    g = df[df["ResourceName"].notna()].copy()
    g = g.sort_values("shift", ascending=False).drop_duplicates("ResourceName")
    return df, g


def offer_at_dispatch(row):
    """Offer price of the tranche whose cumulative CurveMW first reaches BasePoint."""
    tr = [(row[f"CurvePrice{i}"], row[f"CurveMW{i}"]) for i in range(1, 16)]
    tr = [(pp, mm) for pp, mm in tr if pd.notna(pp) and pd.notna(mm)]
    if not tr:
        return np.nan
    tr.sort(key=lambda x: x[1])
    for pp, mm in tr:
        if mm >= row["BasePoint"] - 1e-6:
            return pp
    return tr[-1][0]


# --------------------------------------------------------------------------- Q1
def q1_compare():
    (pre_all, pre_g), (post_all, post_g) = dedup_vector(PRE_PID), dedup_vector(POST_PID)
    rows = []
    for pid, alldf, g in ((PRE_PID, pre_all, pre_g), (POST_PID, post_all, post_g)):
        # distinct-cpnode dedup for the "universe" and distribution (avoid join fan-out)
        cp = alldf.drop_duplicates("cpNodeId")
        gcp = g  # already one row per ResourceName
        rec = {"psenShiftID": pid,
               "distinct_cpnodes": cp["cpNodeId"].nunique(),
               "distinct_gen_resources": g["ResourceName"].nunique()}
        for thr in (0.01, 0.05, 0.10, 0.20):
            rec[f"cpnode_signed>={thr}"] = int((cp["shift"] >= thr).sum())
            rec[f"gen_signed>={thr}"] = int((gcp["shift"] >= thr).sum())
        rows.append(rec)
    summary = pd.DataFrame(rows)

    # which generator resources were high-shift PRE but tiny/absent POST
    m = pre_g[["ResourceName", "ResourceType", "shift"]].rename(columns={"shift": "shift_pre"}).merge(
        post_g[["ResourceName", "shift"]].rename(columns={"shift": "shift_post"}),
        on="ResourceName", how="left")
    dropped = m[(m["shift_pre"] >= SHIFT_CUT) & (m["shift_post"].fillna(0) < SHIFT_CUT)]
    return summary, pre_g, post_g, dropped


# --------------------------------------------------------------------------- Q2
def q2_core(post_g):
    pos = post_g[post_g["shift"] > 0]
    th_all = pos[pos["ResourceType"].isin(THERMAL)]                 # 493 any-positive
    core = th_all[th_all["shift"] >= SHIFT_CUT].copy()             # ~14 core
    core = core.sort_values("shift", ascending=False)
    # aggregate context for the any-positive thermal tail
    agg = (th_all.assign(bucket=lambda d: pd.cut(d["shift"],
             [0, 0.02, 0.03, 0.04, 0.05, 1.0], right=False,
             labels=["0-0.02", "0.02-0.03", "0.03-0.04", "0.04-0.05", ">=0.05"]))
           .groupby("bucket", observed=True)["ResourceName"].count())
    return core, th_all, agg


def enrich_genunit(core):
    """Join core units to AW.DBO.GENUNIT by CPNODEID for plant name + fuel."""
    f = DATA / "thm_genunit_core.parquet"
    if f.exists():
        gu = pd.read_parquet(f)
    else:
        cpids = ",".join(str(int(c)) for c in sorted(core["cpNodeId"].unique()))
        gu = snowflake.performQuery(dbName="AW", warehouse=snowflake.READ_ONLY_WH,
            sqlQuery=f"""SELECT CPNODEID, UNITNAME, BUSNAME, GENFUELTYPE, NAMEPLATEMW
                         FROM AW.DBO.GENUNIT WHERE ISOMARKETID=6 AND CPNODEID IN ({cpids})""")
        gu.to_parquet(f, index=False)
    # one plant label per cpnode (BUSNAME is the station); take max nameplate row
    gu = gu.sort_values("NAMEPLATEMW", ascending=False).drop_duplicates("CPNODEID")
    gu = gu.rename(columns={"CPNODEID": "cpNodeId"})
    out = core.merge(gu[["cpNodeId", "BUSNAME", "GENFUELTYPE", "UNITNAME", "NAMEPLATEMW"]],
                     on="cpNodeId", how="left")
    return out


# --------------------------------------------------------------------------- Q3 fetch
def fetch_sced(names):
    f = DATA / "thm_sced_summer2025.parquet"
    if f.exists():
        return pd.read_parquet(f)
    inlist = ",".join(f"'{n}'" for n in names)
    curves = ", ".join(f"T1.{c}" for c in (PRICE_COLS + MW_COLS))
    sql = f"""
        SELECT T1.TimeStamp, T2.ResourceName, T2.ResourceType, T1.TelemeteredStatus,
               T1.BasePoint, T1.HSL, T1.LSL, {curves}
        FROM AW.dbo.isoErcotScedGenResource T1
        JOIN AW.dbo.isoErcotScedGen T2 ON T1.genID = T2.genID
        WHERE T1.TimeStamp >= '{SUMMER_LO}' AND T1.TimeStamp < '{SUMMER_HI}'
          AND T2.ResourceName IN ({inlist})
    """
    df = db.getDfFromAwDb(sql)
    df.to_parquet(f, index=False)
    print(f"[sced] {len(df):,} rows, {df['ResourceName'].nunique()} resources, "
          f"{df['TimeStamp'].nunique()} intervals")
    return df


import re


def _plant_key(name):
    """Physical plant key: strip the trailing CC-config / settlement-node index.

    ERCOT registers each combined-cycle block under several ResourceNames (one per
    operating CONFIGURATION); only one is telemetered ON per interval. Sandy Creek
    is split across settlement nodes _J01.._J04. Collapse both to the plant."""
    return re.sub(r"_(J?\d+)$", "", name)


def reduce_to_plant_interval(sced):
    """Wide SCED -> one row per (plant, TimeStamp): active-config output/HSL/offer.

    online = any config ON; output = active config BasePoint (0 if none ON, since
    only one config is ON at a time); offer = that config's offer-at-dispatch."""
    sced = sced.copy()
    sced["TimeStamp"] = pd.to_datetime(sced["TimeStamp"])
    for c in ["BasePoint", "HSL", "LSL"]:
        sced[c] = pd.to_numeric(sced[c], errors="coerce")
    sced["plant"] = sced["ResourceName"].map(_plant_key)
    sced["online"] = sced["TelemeteredStatus"].str.startswith("ON", na=False)
    sced["out_mw"] = np.where(sced["online"], sced["BasePoint"], 0.0)
    sced["offer_on"] = [offer_at_dispatch(r) if o else np.nan
                        for o, (_, r) in zip(sced["online"], sced.iterrows())]
    pi = (sced.groupby(["plant", "TimeStamp"])
          .agg(online=("online", "max"), output=("out_mw", "max"),
               hsl=("HSL", "max"), offer=("offer_on", "max"))
          .reset_index())
    pi["online"] = pi["online"].astype(bool)
    return sced, pi


def q3_aggregate(pi, plant_meta):
    recs = []
    for plant, g in pi.groupby("plant"):
        on = g[g["online"]]
        recs.append({
            "plant": plant,
            "n_intervals": len(g),
            "capacity_maxHSL": g["hsl"].max(),
            "pct_online": 100.0 * g["online"].mean(),
            "avg_output_MW_online": on["output"].mean() if len(on) else np.nan,
            "avg_offer_at_dispatch": on["offer"].mean() if len(on) else np.nan,
            "median_offer_at_dispatch": on["offer"].median() if len(on) else np.nan,
        })
    out = pd.DataFrame(recs).merge(plant_meta, on="plant", how="left")
    return out.sort_values("pct_online", ascending=False)


# --------------------------------------------------------------------------- Q4
def load_hourly():
    lv = pd.read_parquet(DATA / "ercotLoadView.parquet")
    lv = lv[["date", "he", "ERCOT_ALL_LD"]].copy()
    lv["date"] = pd.to_datetime(lv["date"]).dt.normalize()
    lv["he"] = pd.to_numeric(lv["he"], errors="coerce").astype("Int64")
    lv["clock_hour"] = lv["he"] - 1                 # HE = clock hour + 1
    lv["ERCOT_ALL_LD"] = pd.to_numeric(lv["ERCOT_ALL_LD"], errors="coerce")
    return lv[["date", "clock_hour", "ERCOT_ALL_LD"]]


def q4_correlate(pi):
    """Plant hourly mean output (incl. 0 when off) vs ERCOT load; Pearson+Spearman."""
    lv = load_hourly()
    hourly = (pi.assign(date=pi["TimeStamp"].dt.normalize(),
                        clock_hour=pi["TimeStamp"].dt.hour)
              .groupby(["plant", "date", "clock_hour"], as_index=False)["output"].mean())
    j = hourly.merge(lv, on=["date", "clock_hour"], how="inner")
    recs, joined = [], {}
    for plant, g in j.groupby("plant"):
        gg = g.dropna(subset=["output", "ERCOT_ALL_LD"])
        if gg["output"].std(ddof=0) == 0 or len(gg) < 10:
            recs.append({"plant": plant, "n_hours": len(gg),
                         "pearson_r": np.nan, "spearman_r": np.nan})
        else:
            recs.append({"plant": plant, "n_hours": len(gg),
                         "pearson_r": gg["output"].corr(gg["ERCOT_ALL_LD"]),
                         "spearman_r": gg["output"].rank().corr(gg["ERCOT_ALL_LD"].rank())})
        joined[plant] = gg
    return pd.DataFrame(recs), joined


# --------------------------------------------------------------------------- plot
FUEL_COLOR = {"COAL": "#8c564b", "GAS": "#1f77b4"}


def build_plot(q3, q4, joined):
    order = q3.sort_values("pct_online", ascending=False)["plant"].tolist()
    plants = [p for p in order]                      # all 5 plants (incl. Sandy Creek)
    ncol = len(plants)
    q4i = q4.set_index("plant")
    q3i = q3.set_index("plant")

    titles = []
    for p in plants:
        r = q4i.loc[p]
        rr = "n/a (never ran)" if pd.isna(r["pearson_r"]) else \
            f"r={r['pearson_r']:.2f} ρ={r['spearman_r']:.2f}"
        titles.append(f"{p}<br><sub>{rr}</sub>")
    titles = ["online % per plant", "avg output when online (MW)"] + titles

    specs = [[{"colspan": max(1, ncol // 2)}] + [None] * (max(1, ncol // 2) - 1)
             + [{"colspan": ncol - max(1, ncol // 2)}] + [None] * (ncol - max(1, ncol // 2) - 1)]
    specs += [[{} for _ in range(ncol)]]
    fig = make_subplots(rows=2, cols=ncol, specs=specs, subplot_titles=titles,
                        vertical_spacing=0.16, horizontal_spacing=0.05)

    bar = q3.sort_values("pct_online", ascending=True)
    colors = [FUEL_COLOR.get(f, "#888") for f in bar["GENFUELTYPE"]]
    fig.add_trace(go.Bar(x=bar["pct_online"], y=bar["plant"], orientation="h",
                         marker_color=colors, showlegend=False,
                         hovertemplate="%{y}: %{x:.1f}% online<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Bar(x=bar["avg_output_MW_online"].fillna(0), y=bar["plant"], orientation="h",
                         marker_color=colors, showlegend=False,
                         hovertemplate="%{y}: %{x:.0f} MW avg<extra></extra>"),
                  row=1, col=1 + max(1, ncol // 2))

    for i, p in enumerate(plants):
        gg = joined.get(p)
        f = q3i.loc[p, "GENFUELTYPE"]
        if gg is None or not len(gg):
            continue
        fig.add_trace(go.Scatter(x=gg["ERCOT_ALL_LD"] / 1000, y=gg["output"],
                      mode="markers", marker=dict(size=3, opacity=0.35,
                      color=FUEL_COLOR.get(f, "#888")), showlegend=False,
                      hovertemplate="load %{x:.1f} GW<br>out %{y:.0f} MW<extra></extra>"),
                      row=2, col=i + 1)
        fig.update_xaxes(title_text="ERCOT load (GW)", row=2, col=i + 1)
    fig.update_yaxes(title_text="plant output (MW)", row=2, col=1)
    fig.update_xaxes(title_text="online %", row=1, col=1)
    fig.update_xaxes(title_text="avg MW", row=1, col=1 + max(1, ncol // 2))

    fig.update_layout(
        template="plotly_white", width=1400, height=760,
        title=dict(text=(
            "Thermal plants electrically behind ERCOT 35055 (SAMSW→VENSW 345kV) — "
            "summer 2025<br><sup>physical plants with signed shift ≥ 0.05 on current "
            f"topology (psenShiftID {POST_PID}); CC configuration-registrations collapsed "
            "to the plant. Bottom: hourly plant output vs ERCOT system load "
            "(r = Pearson, ρ = Spearman). Brown = Sandy Creek (coal, OUT all summer), "
            "blue = gas CCGT.</sup>"), x=0.01, xanchor="left"),
        margin=dict(t=120))
    return fig


# --------------------------------------------------------------------------- main
def main():
    awconnect.configure("read_only")
    pd.set_option("display.width", 200); pd.set_option("display.max_columns", None)

    print("\n===== Q1 =====")
    summary, pre_g, post_g, dropped = q1_compare()
    print(summary.to_string(index=False))
    print(f"\ngenerator resources high-shift PRE (>= {SHIFT_CUT}) but tiny/absent POST: "
          f"{len(dropped)} of {(pre_g['shift'] >= SHIFT_CUT).sum()}")
    print("dropped by ResourceType:\n", dropped["ResourceType"].value_counts().to_string())

    print("\n===== Q2 =====")
    core, th_all, agg = q2_core(post_g)
    core = enrich_genunit(core)
    print(f"thermal any-positive-shift: {len(th_all)} units; core (>= {SHIFT_CUT}): {len(core)}")
    print("thermal any-positive shift buckets:\n", agg.to_string())
    show = core[["ResourceName", "ResourceType", "shift", "BUSNAME", "GENFUELTYPE",
                 "UNITNAME", "NAMEPLATEMW"]]
    print(show.to_string(index=False))
    core.to_csv(OUT / "thermal_behind_35055_units.csv", index=False)

    print("\n===== Q3 (physical-plant level) =====")
    names = core["ResourceName"].tolist()
    sced_raw = fetch_sced(names)
    sced, pi = reduce_to_plant_interval(sced_raw)
    # plant metadata: fuel/station/max shift + member ResourceNames
    core = core.assign(plant=core["ResourceName"].map(_plant_key))
    plant_meta = (core.groupby("plant")
                  .agg(ResourceType=("ResourceType", "first"),
                       GENFUELTYPE=("GENFUELTYPE", "first"),
                       BUSNAME=("BUSNAME", "first"),
                       UNITNAME=("UNITNAME", "first"),
                       max_shift=("shift", "max"),
                       n_registrations=("ResourceName", "nunique"),
                       members=("ResourceName", lambda s: ";".join(sorted(s))))
                  .reset_index())
    q3 = q3_aggregate(pi, plant_meta)

    print("\n===== Q4 =====")
    q4, joined = q4_correlate(pi)
    out = q3.merge(q4, on="plant", how="left").sort_values("pct_online", ascending=False)
    cols = ["plant", "UNITNAME", "ResourceType", "GENFUELTYPE", "BUSNAME", "max_shift",
            "n_registrations", "capacity_maxHSL", "pct_online", "avg_output_MW_online",
            "avg_offer_at_dispatch", "median_offer_at_dispatch",
            "n_hours", "pearson_r", "spearman_r", "n_intervals", "members"]
    out = out[cols]
    out.to_csv(OUT / "thermal_behind_35055_summer2025.csv", index=False)
    print(out.drop(columns=["members"]).round(3).to_string(index=False))

    fig = build_plot(q3, q4, joined)
    html = OUT / "thermal_behind_35055.html"
    fig.write_html(html, include_plotlyjs=True, full_html=True)
    print(f"\n-> {OUT/'thermal_behind_35055_units.csv'}")
    print(f"-> {OUT/'thermal_behind_35055_summer2025.csv'}")
    print(f"-> {html}")


if __name__ == "__main__":
    main()
