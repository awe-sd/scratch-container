"""
RT dynamic EMERGENCY 2-HOUR rating vs local temperature, for one or more
ERCOT elements. Temp on X, rating on Y.

One dot per hour, colored by calendar month. Two panels: on-peak (HE 7-22)
and off-peak (HE 23-6). Year and Month dropdowns filter (independently);
the month legend also toggles months. A black median-per-5F line is drawn
per panel; an optional published temperature-rating schedule is overlaid.
Hover shows date+hour, temperature, rating.

Read-only pull -> parquet cache -> plotly HTML. Never writes to the DB.
Sources (SQL Server dbo):
  ercotRtDynamicRating   WHERE elementTEID = <teid>   (15-min ratings, MVA)
  weatherWXTempHourlyObservations WHERE station=<id>  (hourly temp, degF)

Configs below: 6945 (MGSES->CATSW, teid 748510) vs Midland KMAF with the
published temp schedule; and 6437_F (KNAPP->SCRCV, teid 823) vs Snyder
KSNK (Scurry Co, TX) with no schedule supplied.
"""
import calendar
from pathlib import Path

import awconnect
import pandas as pd
import plotly.graph_objects as go
from awconnect import db
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)

# month -> color: cool in winter, warm in summer (so summer dots read hot)
MONTH_COLOR = {
    1: "#3b6fb6", 2: "#4c9fc9", 3: "#66c2a5", 4: "#a6d96a", 5: "#d9ef8b",
    6: "#fee08b", 7: "#fdae61", 8: "#f46d43", 9: "#d73027", 10: "#a50026",
    11: "#8c6bb1", 12: "#5e4fa2",
}

# Published temperature-based rating schedule for 6945 (defined emergency
# 2-hr limit, MVA, per the TO temperature curve). Only 6945 has one here.
SCHED_6945 = {
    "temp": [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95,
             100, 105, 110, 115],
    "limit": [1527, 1505, 1482, 1458, 1435, 1410, 1385, 1360, 1334, 1307, 1280,
              1251, 1223, 1194, 1163, 1132, 1098, 1065, 1031, 994],
}

# NOTE: the 6945 config is intentionally frozen (kept for reference but NOT
# rebuilt) — its committed plot (rating_vs_temp_6945.html) must not be
# overwritten. Re-add to CONFIGS only if you deliberately want to regenerate it.
_FROZEN_6945 = dict(elem=748510, station="KMAF", temp_start="2025-04-01",
                    elem_label="6945 (MGSES→CATSW 345kV, teid 748510)",
                    station_label="Midland (KMAF)", schedule=SCHED_6945,
                    out="rating_vs_temp_6945")

CONFIGS = [
    dict(elem=823, station="KSNK", temp_start="2024-01-01",
         elem_label="6437_F (KNAPP→SCRCV 138kV, teid 823)",
         station_label="Snyder / Scurry Co (KSNK)", schedule=None,
         out="rating_vs_temp_6437F"),
    dict(elem=214167, station="KSNK", temp_start="2024-01-01",
         elem_label="6240_C (SACRC→DPCRK 138kV, teid 214167)",
         station_label="Snyder / Scurry Co (KSNK)", schedule=None,
         out="rating_vs_temp_6240C"),
]

HOVER = ("<b>%{customdata}</b><br>Temp: %{x:.0f} °F"
         "<br>Emerg 2hr rating: %{y:.0f} MVA<extra></extra>")


def fetch(elem, station, temp_start):
    rp = DATA / f"rt_rating_{elem}.parquet"
    tp = DATA / f"temp_{station}.parquet"
    awconnect.configure("read_only")
    if not rp.exists():
        print(f"[fetch] RT ratings teid={elem} ...")
        db.getDfFromAwDb(
            "SELECT createTime, TEIDDefId, normalRatings, emergencyRatings, "
            f"emergency15MinRatings FROM dbo.ercotRtDynamicRating WHERE elementTEID = {elem}"
        ).to_parquet(rp, index=False)
    if not tp.exists():
        print(f"[fetch] temp station={station} ...")
        db.getDfFromAwDb(
            "SELECT local_time, temp FROM dbo.weatherWXTempHourlyObservations "
            f"WHERE station = '{station}' AND local_time >= '{temp_start}'"
        ).to_parquet(tp, index=False)
    return pd.read_parquet(rp), pd.read_parquet(tp)


def join_hourly(r, t):
    r["createTime"] = pd.to_datetime(r["createTime"])
    t["local_time"] = pd.to_datetime(t["local_time"])
    r = r.groupby("createTime", as_index=False)["emergencyRatings"].mean()
    r["hour"] = r["createTime"].dt.floor("h")
    rh = r.groupby("hour", as_index=False)["emergencyRatings"].mean()
    t["hour"] = t["local_time"].dt.floor("h")
    th = t.groupby("hour", as_index=False)["temp"].mean()
    df = (rh.merge(th, on="hour", how="inner")
            .dropna(subset=["temp", "emergencyRatings"])
            .sort_values("hour").reset_index(drop=True))
    df["ts"] = df["hour"].dt.strftime("%Y-%m-%d %H:00")
    df["month"] = df["hour"].dt.month
    df["year"] = df["hour"].dt.year
    # on-peak = HE 7-22 (clock 07:00-22:59); off-peak = HE 23-6 (23:00-06:59)
    df["onpeak"] = df["hour"].dt.hour.between(7, 22)
    return df


def median_line(sub):
    if sub.empty:
        return pd.DataFrame(columns=["tc", "median"])
    b = sub.assign(tbin=(sub["temp"] // 5 * 5).astype(int))
    m = b.groupby("tbin")["emergencyRatings"].agg(median="median", n="size").reset_index()
    m = m[m["n"] >= 8]
    m["tc"] = m["tbin"] + 2.5
    return m


def build(cfg):
    r, t = fetch(cfg["elem"], cfg["station"], cfg["temp_start"])
    df = join_hourly(r, t)
    sched = cfg["schedule"]
    print(f"[{cfg['out']}] hours: {len(df):,}  on-peak {int(df.onpeak.sum()):,} / "
          f"off-peak {int((~df.onpeak).sum()):,}  temp {df.temp.min():.0f}-{df.temp.max():.0f}F  "
          f"years {sorted(df.year.unique())}")

    # binned CSV + companion static plot
    binned = (df.assign(tbin=(df["temp"] // 5 * 5).astype(int))
                .groupby("tbin")["emergencyRatings"]
                .agg(median="median", n="size",
                     p10=lambda s: s.quantile(.10), p90=lambda s: s.quantile(.90))
                .reset_index())
    binned = binned[binned["n"] >= 10]
    binned["tc"] = binned["tbin"] + 2.5
    binned.to_csv(OUT / f"{cfg['out']}_binned.csv", index=False)
    build_binned_plot(binned, cfg)

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
        subplot_titles=("On-peak (HE 7–22)", "Off-peak (HE 23–6)"))

    years = sorted(df["year"].unique())
    months = sorted(df["month"].unique())
    ym_pairs = sorted(df.groupby(["year", "month"]).groups.keys())

    trace_ym = []          # (year, month) per trace; (None, None) = always-on
    legend_shown = set()
    for (yr, m) in ym_pairs:
        for col, mask in ((1, df["onpeak"]), (2, ~df["onpeak"])):
            g = df[(df["year"] == yr) & (df["month"] == m) & mask]
            show = col == 1 and m not in legend_shown
            fig.add_trace(
                go.Scattergl(
                    x=g["temp"], y=g["emergencyRatings"], mode="markers",
                    marker=dict(size=5, color=MONTH_COLOR[m], opacity=0.55),
                    name=calendar.month_abbr[m], legendgroup=f"m{m}",
                    legendrank=m, showlegend=show,
                    customdata=g["ts"], hovertemplate=HOVER),
                row=1, col=col)
            if show:
                legend_shown.add(m)
            trace_ym.append((yr, m))

    for col, mask in ((1, df["onpeak"]), (2, ~df["onpeak"])):
        ml = median_line(df[mask])
        fig.add_trace(
            go.Scatter(x=ml["tc"], y=ml["median"], mode="lines",
                       line=dict(color="black", width=3),
                       name="median (per 5°F)", legendgroup="median",
                       legendrank=100, showlegend=(col == 1),
                       hovertemplate="Temp ~%{x:.0f} °F<br>median %{y:.0f} MVA<extra></extra>"),
            row=1, col=col)
        trace_ym.append((None, None))

    if sched:
        for col in (1, 2):
            fig.add_trace(
                go.Scatter(x=sched["temp"], y=sched["limit"], mode="lines",
                           line=dict(color="firebrick", width=2.5, dash="dash"),
                           name="definition (temp schedule)", legendgroup="def",
                           legendrank=101, showlegend=(col == 1),
                           hovertemplate="Temp %{x:.0f} °F<br>defined limit %{y:.0f} MVA<extra></extra>"),
                row=1, col=col)
            trace_ym.append((None, None))

    n = len(trace_ym)
    year_buttons = [dict(label="All years", method="update", args=[{"visible": [True] * n}])]
    for yr in years:
        vis = [(ty == yr or ty is None) for (ty, tm) in trace_ym]
        year_buttons.append(dict(label=str(yr), method="update", args=[{"visible": vis}]))
    month_buttons = [dict(label="All months", method="update", args=[{"visible": [True] * n}])]
    for m in months:
        vis = [(tm == m or tm is None) for (ty, tm) in trace_ym]
        month_buttons.append(dict(label=calendar.month_name[m], method="update", args=[{"visible": vis}]))

    for c in (1, 2):
        fig.update_xaxes(title_text=f"{cfg['station_label']} temperature (°F)", row=1, col=c)
    fig.update_yaxes(title_text="emergency 2-hr rating (MVA)", row=1, col=1)
    fig.update_layout(
        title=dict(text=(
            f"{cfg['elem_label']} emergency 2-hr RT rating vs {cfg['station_label']} temp"
            f"<br><sup>One dot per hour by month, {df.hour.min():%Y-%m-%d}–"
            f"{df.hour.max():%Y-%m-%d} ({len(df):,} hrs). Year/Month dropdowns filter "
            "(independently); legend toggles months. Black = median per 5°F.</sup>")),
        template="plotly_white", width=1250, height=700, margin=dict(t=150),
        legend=dict(title="month", orientation="v", y=1, x=1.01),
        updatemenus=[
            dict(buttons=year_buttons, direction="down", showactive=True,
                 x=0.0, y=1.16, xanchor="left", yanchor="top"),
            dict(buttons=month_buttons, direction="down", showactive=True,
                 x=0.16, y=1.16, xanchor="left", yanchor="top"),
        ],
        annotations=list(fig.layout.annotations) + [
            dict(text="<b>Year</b>", xref="paper", yref="paper", showarrow=False,
                 x=0.0, y=1.205, xanchor="left", font=dict(size=11, color="gray")),
            dict(text="<b>Month</b>", xref="paper", yref="paper", showarrow=False,
                 x=0.16, y=1.205, xanchor="left", font=dict(size=11, color="gray")),
        ])
    out_html = OUT / f"{cfg['out']}.html"
    fig.write_html(out_html, include_plotlyjs=True)
    print(f"-> {out_html}")


def build_binned_plot(med, cfg):
    med = med.sort_values("tbin")
    sched = cfg["schedule"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=med["tc"], y=med["p90"], mode="lines",
                             line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=med["tc"], y=med["p10"], mode="lines",
                             line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(30,120,200,0.18)", name="p10–p90",
                             hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=med["tc"], y=med["median"], mode="lines+markers",
        line=dict(color="rgb(30,120,200)", width=3), marker=dict(size=8),
        name="median", customdata=med[["n", "p10", "p90"]].values,
        hovertemplate=("Temp ~%{x:.0f} °F<br>median %{y:.0f} MVA"
                       "<br>p10–p90 %{customdata[1]:.0f}–%{customdata[2]:.0f}"
                       "<br>n=%{customdata[0]}<extra></extra>")))
    if sched:
        fig.add_trace(go.Scatter(
            x=sched["temp"], y=sched["limit"], mode="lines+markers",
            line=dict(color="firebrick", width=2.5, dash="dash"), marker=dict(size=5),
            name="definition (temp schedule)",
            hovertemplate="Temp %{x:.0f} °F<br>defined limit %{y:.0f} MVA<extra></extra>"))
    fig.add_trace(go.Bar(x=med["tc"], y=med["n"], name="hours in bin",
                         marker_color="rgba(150,150,150,0.35)", yaxis="y2",
                         hovertemplate="Temp ~%{x:.0f} °F<br>n=%{y}<extra></extra>"))
    drop = med["median"].iloc[0] - med["median"].iloc[-1]
    fig.update_layout(
        title=dict(text=(
            f"{cfg['elem_label']} emergency 2-hr rating vs {cfg['station_label']} temp — binned per 5 °F"
            f"<br><sup>median with p10–p90 band; falls ~{drop:.0f} MVA from "
            f"{int(med['tbin'].iloc[0])}°F to {int(med['tbin'].iloc[-1])+5}°F. "
            "Bars = hours sampled per bin.</sup>")),
        xaxis_title=f"{cfg['station_label']} temperature (°F)",
        yaxis=dict(title="emergency 2-hr rating (MVA)"),
        yaxis2=dict(title="hours in bin", overlaying="y", side="right", showgrid=False),
        template="plotly_white", width=1050, height=600,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    out = OUT / f"{cfg['out']}_binned.html"
    fig.write_html(out, include_plotlyjs=True)
    print(f"-> {out}")


def main():
    for cfg in CONFIGS:
        build(cfg)


if __name__ == "__main__":
    main()
