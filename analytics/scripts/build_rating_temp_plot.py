"""
6945 (MGSES->CATSW 345kV, elementTEID 748510) RT dynamic EMERGENCY 2-HOUR
rating vs Midland (KMAF) temperature. Temp on X, rating on Y.

One dot per hour, colored by calendar month. Two panels: on-peak
(HE 7-21) and off-peak (HE 1-6, 22-24). A dropdown filters to a single
month (or All); the month legend also toggles both panels together. A
black median-per-5F line is drawn in each panel as a reference. Hover
shows date+hour, temperature, and rating.

Read-only pull -> parquet cache -> plotly HTML. Never writes to the DB.
Sources (SQL Server dbo):
  ercotRtDynamicRating   WHERE elementTEID = 748510   (15-min ratings, MVA)
  weatherWXTempHourlyObservations WHERE station='KMAF' (hourly temp, degF)
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
ELEM = 748510
STATION = "KMAF"            # Midland Regional
RATING_START = "2025-04-01"  # ratings begin 2025-04-02

# Published temperature-based rating schedule for 6945 (defined emergency
# 2-hr limit, MVA, per the TO temperature curve). Reference line for both plots.
DEF_TEMP = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95,
            100, 105, 110, 115]
DEF_LIMIT = [1527, 1505, 1482, 1458, 1435, 1410, 1385, 1360, 1334, 1307, 1280,
             1251, 1223, 1194, 1163, 1132, 1098, 1065, 1031, 994]

# month -> color: cool in winter, warm in summer (so summer dots read hot)
MONTH_COLOR = {
    1: "#3b6fb6", 2: "#4c9fc9", 3: "#66c2a5", 4: "#a6d96a", 5: "#d9ef8b",
    6: "#fee08b", 7: "#fdae61", 8: "#f46d43", 9: "#d73027", 10: "#a50026",
    11: "#8c6bb1", 12: "#5e4fa2",
}


def fetch():
    rp = DATA / f"rt_rating_{ELEM}.parquet"
    tp = DATA / f"temp_{STATION}.parquet"
    awconnect.configure("read_only")
    if not rp.exists():
        print("[fetch] RT ratings ...")
        db.getDfFromAwDb(
            "SELECT createTime, TEIDDefId, normalRatings, emergencyRatings, "
            f"emergency15MinRatings FROM dbo.ercotRtDynamicRating WHERE elementTEID = {ELEM}"
        ).to_parquet(rp, index=False)
    if not tp.exists():
        print("[fetch] Midland temp ...")
        db.getDfFromAwDb(
            "SELECT local_time, temp FROM dbo.weatherWXTempHourlyObservations "
            f"WHERE station = '{STATION}' AND local_time >= '{RATING_START}'"
        ).to_parquet(tp, index=False)
    return pd.read_parquet(rp), pd.read_parquet(tp)


def median_line(sub):
    """median emergency-2hr rating per 5F temp bin for a subset."""
    if sub.empty:
        return pd.DataFrame(columns=["tc", "median"])
    b = sub.assign(tbin=(sub["temp"] // 5 * 5).astype(int))
    m = b.groupby("tbin")["emergencyRatings"].agg(median="median", n="size").reset_index()
    m = m[m["n"] >= 8]
    m["tc"] = m["tbin"] + 2.5
    return m


HOVER = ("<b>%{customdata}</b><br>Temp: %{x:.0f} °F"
         "<br>Emerg 2hr rating: %{y:.0f} MVA<extra></extra>")


def main():
    r, t = fetch()
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
    df["HE"] = df["hour"].dt.hour + 1                 # hour ending
    df["onpeak"] = df["HE"].between(7, 21)
    print(f"joined hours: {len(df):,}  on-peak {int(df.onpeak.sum()):,} / "
          f"off-peak {int((~df.onpeak).sum()):,}")

    # still refresh the binned CSV + companion static plot (emergency 2-hr)
    binned = (df.assign(tbin=(df["temp"] // 5 * 5).astype(int))
                .groupby("tbin")["emergencyRatings"]
                .agg(median="median", n="size",
                     p10=lambda s: s.quantile(.10), p90=lambda s: s.quantile(.90))
                .reset_index())
    binned = binned[binned["n"] >= 10]
    binned["tc"] = binned["tbin"] + 2.5
    binned.to_csv(OUT / "rating_vs_temp_binned.csv", index=False)
    build_binned_plot(binned)

    # ---- main 2-panel, month-colored plot ----
    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
        subplot_titles=("On-peak (HE 7–21)", "Off-peak (HE 1–6, 22–24)"))

    months = sorted(df["month"].unique())
    trace_month = []   # month value per trace, or None for medians
    for m in months:
        for col, mask in ((1, df["onpeak"]), (2, ~df["onpeak"])):
            g = df[(df["month"] == m) & mask]
            fig.add_trace(
                go.Scattergl(
                    x=g["temp"], y=g["emergencyRatings"], mode="markers",
                    marker=dict(size=5, color=MONTH_COLOR[m], opacity=0.55),
                    name=calendar.month_abbr[m], legendgroup=f"m{m}",
                    showlegend=(col == 1), customdata=g["ts"], hovertemplate=HOVER),
                row=1, col=col)
            trace_month.append(m)

    for col, mask in ((1, df["onpeak"]), (2, ~df["onpeak"])):
        ml = median_line(df[mask])
        fig.add_trace(
            go.Scatter(x=ml["tc"], y=ml["median"], mode="lines",
                       line=dict(color="black", width=3),
                       name="median (per 5°F)", legendgroup="median",
                       showlegend=(col == 1),
                       hovertemplate="Temp ~%{x:.0f} °F<br>median %{y:.0f} MVA<extra></extra>"),
            row=1, col=col)
        trace_month.append(None)

    # published temperature-based rating definition (both panels, always shown)
    for col in (1, 2):
        fig.add_trace(
            go.Scatter(x=DEF_TEMP, y=DEF_LIMIT, mode="lines",
                       line=dict(color="firebrick", width=2.5, dash="dash"),
                       name="definition (temp schedule)", legendgroup="def",
                       showlegend=(col == 1),
                       hovertemplate="Temp %{x:.0f} °F<br>defined limit %{y:.0f} MVA<extra></extra>"),
            row=1, col=col)
        trace_month.append(None)

    # month dropdown: All + each month (medians + definition always visible)
    n = len(trace_month)
    buttons = [dict(label="All months", method="update",
                    args=[{"visible": [True] * n}])]
    for m in months:
        vis = [(tm == m or tm is None) for tm in trace_month]
        buttons.append(dict(label=calendar.month_name[m], method="update",
                            args=[{"visible": vis}]))

    for c in (1, 2):
        fig.update_xaxes(title_text="Midland (KMAF) temperature (°F)", row=1, col=c)
    fig.update_yaxes(title_text="6945 emergency 2-hr rating (MVA)", row=1, col=1)
    fig.update_layout(
        title=dict(text=(
            "6945 (MGSES→CATSW 345kV, teid 748510) emergency 2-hr RT rating vs Midland temp"
            f"<br><sup>One dot per hour by month, {df.hour.min():%Y-%m-%d}–"
            f"{df.hour.max():%Y-%m-%d} ({len(df):,} hrs). Dropdown filters to a month; "
            "legend toggles months. Black = median per 5°F.</sup>")),
        template="plotly_white", width=1250, height=680,
        legend=dict(title="month", orientation="v", y=1, x=1.01),
        updatemenus=[dict(buttons=buttons, direction="down", showactive=True,
                          x=0, y=1.15, xanchor="left", yanchor="top",
                          pad=dict(l=0, r=0))])
    out_html = OUT / "rating_vs_temp_6945.html"
    fig.write_html(out_html, include_plotlyjs=True)
    print(f"-> {out_html}")


def build_binned_plot(med):
    """Static summary: median emergency 2-hr rating per 5F temp bin with a
    p10-p90 band and per-bin sample counts."""
    med = med.sort_values("tbin")
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
    fig.add_trace(go.Scatter(
        x=DEF_TEMP, y=DEF_LIMIT, mode="lines+markers",
        line=dict(color="firebrick", width=2.5, dash="dash"), marker=dict(size=5),
        name="definition (temp schedule)",
        hovertemplate="Temp %{x:.0f} °F<br>defined limit %{y:.0f} MVA<extra></extra>"))
    fig.add_trace(go.Bar(x=med["tc"], y=med["n"], name="hours in bin",
                         marker_color="rgba(150,150,150,0.35)", yaxis="y2",
                         hovertemplate="Temp ~%{x:.0f} °F<br>n=%{y}<extra></extra>"))
    drop = med["median"].iloc[0] - med["median"].iloc[-1]
    fig.update_layout(
        title=dict(text=(
            "6945 emergency 2-hr rating vs Midland temp — binned per 5 °F"
            f"<br><sup>median with p10–p90 band; falls ~{drop:.0f} MVA from "
            f"{int(med['tbin'].iloc[0])}°F to {int(med['tbin'].iloc[-1])+5}°F. "
            "Bars = hours sampled per bin.</sup>")),
        xaxis_title="Midland (KMAF) temperature (°F)",
        yaxis=dict(title="emergency 2-hr rating (MVA)"),
        yaxis2=dict(title="hours in bin", overlaying="y", side="right", showgrid=False),
        template="plotly_white", width=1050, height=600,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    out = OUT / "rating_vs_temp_binned.html"
    fig.write_html(out, include_plotlyjs=True)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
