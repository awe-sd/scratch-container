"""
6945 (MGSES->CATSW 345kV, elementTEID 748510) RT DYNAMIC RATING vs
Midland (KMAF) temperature. Temp on X, rating on Y.

Dynamic line ratings fall as ambient temperature rises, so the scatter
should slope down — quantifies how much 6945's capacity erodes on hot
West-Texas afternoons (exactly when high net load + the low-West/high-Pan
wind pattern push flow onto it).

Read-only pull -> parquet cache -> plotly HTML. Never writes to the DB.
Sources (SQL Server dbo):
  ercotRtDynamicRating   WHERE elementTEID = 748510   (15-min ratings, MVA)
  weatherWXTempHourlyObservations WHERE station='KMAF' (hourly temp, degF)
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
OUT.mkdir(parents=True, exist_ok=True)
ELEM = 748510
STATION = "KMAF"           # Midland Regional
RATING_START = "2025-04-01"  # ratings begin 2025-04-02


def fetch():
    rp = DATA / f"rt_rating_{ELEM}.parquet"
    tp = DATA / f"temp_{STATION}.parquet"
    awconnect.configure("read_only")
    if not rp.exists():
        print("[fetch] RT ratings ...")
        r = db.getDfFromAwDb(
            "SELECT createTime, TEIDDefId, normalRatings, emergencyRatings, "
            f"emergency15MinRatings FROM dbo.ercotRtDynamicRating WHERE elementTEID = {ELEM}"
        )
        r.to_parquet(rp, index=False)
        print(f"        {len(r):,} rating rows")
    if not tp.exists():
        print("[fetch] Midland temp ...")
        t = db.getDfFromAwDb(
            "SELECT local_time, temp FROM dbo.weatherWXTempHourlyObservations "
            f"WHERE station = '{STATION}' AND local_time >= '{RATING_START}'"
        )
        t.to_parquet(tp, index=False)
        print(f"        {len(t):,} temp rows")
    return pd.read_parquet(rp), pd.read_parquet(tp)


def main():
    r, t = fetch()
    r["createTime"] = pd.to_datetime(r["createTime"])
    t["local_time"] = pd.to_datetime(t["local_time"])

    # ratings: 15-min -> hourly mean (dedupe overlapping TEIDDef versions per stamp first)
    r = r.groupby("createTime", as_index=False)[
        ["normalRatings", "emergencyRatings", "emergency15MinRatings"]].mean()
    r["hour"] = r["createTime"].dt.floor("h")
    rh = r.groupby("hour", as_index=False)[
        ["normalRatings", "emergencyRatings", "emergency15MinRatings"]].mean()

    # temp: already hourly-ish; floor to hour and mean
    t["hour"] = t["local_time"].dt.floor("h")
    th = t.groupby("hour", as_index=False)["temp"].mean()

    df = rh.merge(th, on="hour", how="inner").dropna(subset=["temp", "normalRatings"])
    df["month"] = df["hour"].dt.month
    df["year"] = df["hour"].dt.year
    print(f"joined hours: {len(df):,}  temp {df.temp.min():.0f}-{df.temp.max():.0f}F  "
          f"normalRating {df.normalRatings.min():.0f}-{df.normalRatings.max():.0f} MVA")
    df.to_parquet(DATA / "rating_temp_joined.parquet", index=False)

    # binned median rating per 5F temp bin (trend)
    df["tbin"] = (df["temp"] // 5 * 5).astype(int)
    binned = df.groupby("tbin").agg(
        n=("normalRatings", "size"),
        rating_med=("normalRatings", "median"),
        rating_p10=("normalRatings", lambda s: s.quantile(0.10)),
        rating_p90=("normalRatings", lambda s: s.quantile(0.90)),
        emerg_med=("emergencyRatings", "median"),
    ).reset_index()
    binned = binned[binned["n"] >= 10]
    binned.to_csv(OUT / "rating_vs_temp_binned.csv", index=False)
    print("\n=== normal rating (MVA) by 5F Midland-temp bin ===")
    print(binned.to_string(index=False))
    if len(df) > 2:
        # Spearman via Pearson-on-ranks (avoids a scipy dependency)
        rho = df["temp"].rank().corr(df["normalRatings"].rank())
        print(f"\nSpearman corr(temp, normalRating) = {rho:.3f}")

    # ---- plot ----
    fig = make_subplots(
        rows=1, cols=2, column_widths=[0.66, 0.34], horizontal_spacing=0.08,
        subplot_titles=(
            "Hourly points (colored by month) + median trend",
            "Rating vs temp: median with p10-p90 band",
        ),
    )
    # scatter colored by month
    fig.add_trace(
        go.Scattergl(
            x=df["temp"], y=df["normalRatings"], mode="markers",
            marker=dict(size=4, color=df["month"], colorscale="Turbo", opacity=0.45,
                        colorbar=dict(title="month", x=0.60, len=0.9)),
            name="hourly", hovertemplate="temp %{x:.0f}F<br>rating %{y:.0f} MVA<extra></extra>",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=binned["tbin"] + 2.5, y=binned["rating_med"], mode="lines+markers",
                   line=dict(color="black", width=3), name="median trend"),
        row=1, col=1,
    )
    # right: median + band
    fig.add_trace(
        go.Scatter(x=binned["tbin"] + 2.5, y=binned["rating_p90"], mode="lines",
                   line=dict(width=0), showlegend=False, hoverinfo="skip"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=binned["tbin"] + 2.5, y=binned["rating_p10"], mode="lines",
                   line=dict(width=0), fill="tonexty", fillcolor="rgba(30,120,200,0.2)",
                   name="p10-p90", hoverinfo="skip"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=binned["tbin"] + 2.5, y=binned["rating_med"], mode="lines+markers",
                   line=dict(color="rgb(30,120,200)", width=3), name="normal (median)"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=binned["tbin"] + 2.5, y=binned["emerg_med"], mode="lines+markers",
                   line=dict(color="firebrick", width=2, dash="dash"), name="emergency (median)"),
        row=1, col=2,
    )
    for c in (1, 2):
        fig.update_xaxes(title_text="Midland (KMAF) temperature (°F)", row=1, col=c)
    fig.update_yaxes(title_text="6945 RT rating (MVA)", row=1, col=1)
    fig.update_yaxes(title_text="6945 RT rating (MVA)", row=1, col=2)
    n = len(df)
    fig.update_layout(
        title=dict(text=(
            "6945 (MGSES→CATSW 345kV, teid 748510) RT dynamic rating vs Midland temperature"
            f"<br><sup>Hourly, {df.hour.min():%Y-%m-%d} to {df.hour.max():%Y-%m-%d} "
            f"({n:,} hrs). normalRatings from dbo.ercotRtDynamicRating; temp = KMAF. "
            "Higher temp → lower line rating.</sup>")),
        template="plotly_white", width=1250, height=620,
        legend=dict(orientation="h", y=-0.18),
    )
    out_html = OUT / "rating_vs_temp_6945.html"
    fig.write_html(out_html, include_plotlyjs=True)
    print(f"\n-> {out_html}")


if __name__ == "__main__":
    main()
