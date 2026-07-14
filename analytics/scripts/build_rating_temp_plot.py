"""
6945 (MGSES->CATSW 345kV, elementTEID 748510) RT dynamic EMERGENCY 2-HOUR
rating vs Midland (KMAF) temperature. Temp on X, rating on Y.

One dot per hour. A slider along the top steps through calendar days and
highlights that day's hourly dots on top of the faint full cloud. A black
median line (median emergency rating per 5F temp bin) shows the trend.
Hover shows the date+hour, temperature, and rating.

Read-only pull -> parquet cache -> plotly HTML. Never writes to the DB.
Sources (SQL Server dbo):
  ercotRtDynamicRating   WHERE elementTEID = 748510   (15-min ratings, MVA)
  weatherWXTempHourlyObservations WHERE station='KMAF' (hourly temp, degF)
"""
from pathlib import Path

import awconnect
import pandas as pd
import plotly.graph_objects as go
from awconnect import db

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)
ELEM = 748510
STATION = "KMAF"            # Midland Regional
RATING_START = "2025-04-01"  # ratings begin 2025-04-02


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


def build_binned_plot(med):
    """Static summary of rating_vs_temp_binned.csv: median emergency 2-hr
    rating per 5F temp bin with a p10-p90 band and per-bin sample counts."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=med["tc"], y=med["p90"], mode="lines",
                             line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=med["tc"], y=med["p10"], mode="lines",
                             line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(30,120,200,0.18)", name="p10–p90",
                             hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=med["tc"], y=med["median"], mode="lines+markers",
        line=dict(color="rgb(30,120,200)", width=3),
        marker=dict(size=8, color="rgb(30,120,200)"),
        name="median", customdata=med[["n", "p10", "p90"]].values,
        hovertemplate=("Temp ~%{x:.0f} °F<br>median %{y:.0f} MVA"
                       "<br>p10–p90 %{customdata[1]:.0f}–%{customdata[2]:.0f}"
                       "<br>n=%{customdata[0]}<extra></extra>")))
    fig.add_trace(go.Bar(x=med["tc"], y=med["n"], name="hours in bin",
                         marker_color="rgba(150,150,150,0.35)", yaxis="y2",
                         hovertemplate="Temp ~%{x:.0f} °F<br>n=%{y}<extra></extra>"))
    drop = med["median"].iloc[0] - med["median"].iloc[-1]
    fig.update_layout(
        title=dict(text=(
            "6945 emergency 2-hr rating vs Midland temp — binned per 5 °F"
            f"<br><sup>median with p10–p90 band; falls ~{drop:.0f} MVA from "
            f"{med['tbin'].iloc[0]}°F to {med['tbin'].iloc[-1]+5}°F. "
            "Bars = hours sampled per bin.</sup>")),
        xaxis_title="Midland (KMAF) temperature (°F)",
        yaxis=dict(title="emergency 2-hr rating (MVA)"),
        yaxis2=dict(title="hours in bin", overlaying="y", side="right",
                    showgrid=False),
        template="plotly_white", width=1050, height=600,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
    )
    out = OUT / "rating_vs_temp_binned.html"
    fig.write_html(out, include_plotlyjs=True)
    print(f"-> {out}")


def main():
    r, t = fetch()
    r["createTime"] = pd.to_datetime(r["createTime"])
    t["local_time"] = pd.to_datetime(t["local_time"])

    # ratings: dedupe overlapping TEIDDef versions per stamp, then 15-min -> hourly mean
    r = r.groupby("createTime", as_index=False)["emergencyRatings"].mean()
    r["hour"] = r["createTime"].dt.floor("h")
    rh = r.groupby("hour", as_index=False)["emergencyRatings"].mean()

    t["hour"] = t["local_time"].dt.floor("h")
    th = t.groupby("hour", as_index=False)["temp"].mean()

    df = (rh.merge(th, on="hour", how="inner")
            .dropna(subset=["temp", "emergencyRatings"])
            .sort_values("hour").reset_index(drop=True))
    df["day"] = df["hour"].dt.strftime("%Y-%m-%d")
    df["ts"] = df["hour"].dt.strftime("%Y-%m-%d %H:00")
    print(f"joined hours: {len(df):,}  temp {df.temp.min():.0f}-{df.temp.max():.0f}F  "
          f"emerg2hr {df.emergencyRatings.min():.0f}-{df.emergencyRatings.max():.0f} MVA")

    # emergency-2hr rating distribution per 5F temp bin
    df["tbin"] = (df["temp"] // 5 * 5).astype(int)
    med = (df.groupby("tbin")["emergencyRatings"]
             .agg(median="median", n="size",
                  p10=lambda s: s.quantile(0.10),
                  p90=lambda s: s.quantile(0.90))
             .reset_index())
    med = med[med["n"] >= 10]
    med["tc"] = med["tbin"] + 2.5
    med.to_csv(OUT / "rating_vs_temp_binned.csv", index=False)
    build_binned_plot(med)

    HOVER = ("<b>%{customdata}</b><br>Temp: %{x:.0f} °F"
             "<br>Emerg 2hr rating: %{y:.0f} MVA<extra></extra>")

    # base traces: faint full cloud, median line, and the highlighted day
    days = df["day"].unique().tolist()
    d0 = df[df["day"] == days[0]]
    fig = go.Figure(
        data=[
            go.Scattergl(
                x=df["temp"], y=df["emergencyRatings"], mode="markers",
                marker=dict(size=4, color="rgba(120,120,120,0.28)"),
                customdata=df["ts"], hovertemplate=HOVER, name="all hours",
            ),
            go.Scatter(
                x=med["tc"], y=med["median"], mode="lines+markers",
                line=dict(color="black", width=3), marker=dict(size=6),
                name="median (per 5°F)",
                hovertemplate="Temp ~%{x:.0f} °F<br>median %{y:.0f} MVA<extra></extra>",
            ),
            go.Scattergl(
                x=d0["temp"], y=d0["emergencyRatings"], mode="markers",
                marker=dict(size=11, color="crimson", line=dict(width=1, color="white")),
                customdata=d0["ts"], hovertemplate=HOVER, name="selected day",
            ),
        ]
    )

    # one frame per day; each updates the highlight trace (index 2)
    frames, steps = [], []
    for d in days:
        g = df[df["day"] == d]
        frames.append(go.Frame(
            name=d,
            data=[go.Scattergl(x=g["temp"], y=g["emergencyRatings"], mode="markers",
                               marker=dict(size=11, color="crimson",
                                           line=dict(width=1, color="white")),
                               customdata=g["ts"], hovertemplate=HOVER)],
            traces=[2],
        ))
        steps.append(dict(method="animate", label=d,
                          args=[[d], dict(mode="immediate",
                                          frame=dict(duration=0, redraw=True),
                                          transition=dict(duration=0))]))
    fig.frames = frames

    fig.update_layout(
        title=dict(text=(
            "6945 (MGSES→CATSW 345kV, teid 748510) emergency 2-hr RT rating vs Midland temp"
            f"<br><sup>One dot per hour, {df.hour.min():%Y-%m-%d}–{df.hour.max():%Y-%m-%d} "
            f"({len(df):,} hrs). Slider highlights a day. emergencyRatings (2-hr) from "
            "dbo.ercotRtDynamicRating; temp = KMAF.</sup>")),
        xaxis_title="Midland (KMAF) temperature (°F)",
        yaxis_title="6945 emergency 2-hr rating (MVA)",
        template="plotly_white", width=1150, height=680,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
        sliders=[dict(active=0, currentvalue=dict(prefix="Day: "),
                      pad=dict(t=30, b=10), len=1.0, x=0, y=0, steps=steps)],
        updatemenus=[dict(type="buttons", direction="left", x=0, y=1.12,
                          xanchor="left", pad=dict(t=0, b=0),
                          buttons=[
                              dict(label="▶ play", method="animate",
                                   args=[None, dict(frame=dict(duration=250, redraw=True),
                                                    fromcurrent=True,
                                                    transition=dict(duration=0))]),
                              dict(label="⏸ pause", method="animate",
                                   args=[[None], dict(mode="immediate",
                                                      frame=dict(duration=0, redraw=False))]),
                          ])],
    )
    out_html = OUT / "rating_vs_temp_6945.html"
    fig.write_html(out_html, include_plotlyjs=True, auto_play=False)
    print(f"-> {out_html}  ({len(days)} day-steps)")


if __name__ == "__main__":
    main()
