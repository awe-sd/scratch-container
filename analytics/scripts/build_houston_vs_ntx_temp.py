"""
Houston temperature vs average North-Texas temperature, last Augusts (2022-2025).

Houston  = KIAH (Houston Intercontinental).
North TX = mean of DFW-metro stations (KDFW, KDTO, KFTW, KAFW, KDAL) per hour.

Panel A: hourly scatter Houston (x) vs North-TX avg (y), colored by August
year, with a 1:1 reference line. Panel B: box of the hourly (Houston − NorthTX)
difference by year. Read-only pull -> parquet -> plotly HTML.
Source: dbo.weatherWXTempHourlyObservations (hourly, degF).
"""
from pathlib import Path

import awconnect
import pandas as pd
import plotly.graph_objects as go
from awconnect import db
from plotly.subplots import make_subplots

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = Path(__file__).resolve().parents[1] / "output"
OUT.mkdir(parents=True, exist_ok=True)

HOU = ["KIAH"]
NTX = ["KDFW", "KDTO", "KFTW", "KAFW", "KDAL"]
YEARS = [2022, 2023, 2024, 2025]
YEAR_COLOR = {2022: "#4c9fc9", 2023: "#66a61e", 2024: "#e6ab02", 2025: "#d73027"}


def fetch():
    f = DATA / "temp_hou_ntx_aug.parquet"
    if f.exists():
        return pd.read_parquet(f)
    awconnect.configure("read_only")
    stations = "','".join(HOU + NTX)
    yrs = ",".join(str(y) for y in YEARS)
    df = db.getDfFromAwDb(
        "SELECT local_time, station, temp FROM dbo.weatherWXTempHourlyObservations "
        f"WHERE station IN ('{stations}') AND MONTH(local_time)=8 "
        f"AND YEAR(local_time) IN ({yrs})")
    df.to_parquet(f, index=False)
    print(f"[fetch] {len(df):,} temp rows")
    return df


def main():
    t = fetch()
    t["local_time"] = pd.to_datetime(t["local_time"])
    t["hour"] = t["local_time"].dt.floor("h")
    t["grp"] = t["station"].map(lambda s: "hou" if s in HOU else "ntx")
    # per hour: Houston temp, North-TX avg temp
    hourly = (t.groupby(["hour", "grp"])["temp"].mean().unstack("grp")
                .dropna(subset=["hou", "ntx"]).reset_index())
    hourly["year"] = hourly["hour"].dt.year
    hourly["diff"] = hourly["hou"] - hourly["ntx"]
    hourly["ts"] = hourly["hour"].dt.strftime("%Y-%m-%d %H:00")
    print(f"hours: {len(hourly):,}  mean Houston {hourly.hou.mean():.1f}F  "
          f"mean NorthTX {hourly.ntx.mean():.1f}F  mean diff {hourly['diff'].mean():+.1f}F")
    hourly.to_parquet(DATA / "houston_vs_ntx_hourly.parquet", index=False)

    fig = make_subplots(rows=1, cols=2, column_widths=[0.62, 0.38], horizontal_spacing=0.1,
                        subplot_titles=("Hourly: Houston vs North-TX avg temp (1:1 dashed)",
                                        "Houston − North-TX difference by year"))
    lo, hi = 60, 112
    fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines",
                             line=dict(color="black", dash="dash", width=1.5),
                             name="1:1", hoverinfo="skip"), row=1, col=1)
    for y in YEARS:
        g = hourly[hourly["year"] == y]
        fig.add_trace(go.Scattergl(
            x=g["hou"], y=g["ntx"], mode="markers",
            marker=dict(size=4, color=YEAR_COLOR[y], opacity=0.5),
            name=str(y), legendgroup=str(y), customdata=g["ts"],
            hovertemplate="<b>%{customdata}</b><br>Houston %{x:.0f}°F<br>NorthTX %{y:.0f}°F<extra></extra>"),
            row=1, col=1)
        fig.add_trace(go.Box(y=hourly.loc[hourly.year == y, "diff"], name=str(y),
                             marker_color=YEAR_COLOR[y], legendgroup=str(y),
                             showlegend=False, boxmean=True),
                      row=1, col=2)
    fig.add_hline(y=0, line_color="rgba(0,0,0,0.5)", row=1, col=2)
    fig.update_xaxes(title_text="Houston (KIAH) temp (°F)", range=[lo, hi], row=1, col=1)
    fig.update_yaxes(title_text="North-TX avg temp (°F)", range=[lo, hi], row=1, col=1)
    fig.update_xaxes(title_text="August", row=1, col=2)
    fig.update_yaxes(title_text="Houston − North-TX (°F)", row=1, col=2)
    fig.update_layout(
        title=dict(text=("Houston vs average North-Texas temperature — Augusts 2022-2025"
                         "<br><sup>hourly; Houston=KIAH, North-TX avg=mean(KDFW,KDTO,KFTW,KAFW,KDAL). "
                         "Points below the 1:1 line = Houston hotter than North TX.</sup>")),
        template="plotly_white", width=1200, height=620,
        legend=dict(title="August", orientation="v", y=1, x=1.01))
    out = OUT / "houston_vs_ntx_temp.html"
    fig.write_html(out, include_plotlyjs=True)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
