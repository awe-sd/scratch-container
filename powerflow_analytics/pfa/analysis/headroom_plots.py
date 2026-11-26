"""Headroom scatter/heatmap plots: fast-scan HEADROOM_AFTER_CURTAILMENT vs. two
driver axes (wind level + solar or load level), split on/off-peak.

Reproduces (and generalizes) the ad hoc `ph_headroom_wind_solar.html` figure
built in an earlier session with no committed source. Reverse-engineered from
that HTML's embedded Plotly JSON:

- Data source: AW.FLOW_ANALYSIS.FAST_SCAN_RESULTS (TIMESTAMP, HEADROOM,
  HEADROOM_AFTER_CURTAILMENT) for one CONFIG_ID (see fastscan.find_configs).
- Wind axis: "West" region wind level from AW.dbo.ercotWindRegionHourly
  (SQL Server, via pfa.mssql) -- WIND_MW = avgHSLPct/100 * totalInstalledCapacityMW.
  isActual flips to False after 2026-05-14 for rows that ARE actuals (stale
  flag, verified corr 1.000 against the pre-flip actuals) -- don't filter on it.
- Solar axis (legacy wind-vs-solar variant): AW.dbo.solarGenAct system solar
  generation (solarGen), joined via AW.dbo.awDate.
- Load axis (new): AW.dbo.ercotLoadView.ERCOT_ALL_LD (SQL Server, via
  pfa.mssql) -- ERCOT system total load, hourly (date, he) grain, 2011+
  coverage. This is the same series the original figure's OFFPEAK panel used.
- Peak split, confirmed empirically against the reference HTML's embedded
  hover timestamps (not the repo's Mon-Fri "5x16" convention used elsewhere,
  e.g. scripts/build_screening_report.py): ONPEAK = HE7-22 (hour-of-day 6-21
  in 0-indexed HOUR()), ALL SEVEN DAYS OF WEEK. OFFPEAK = the complement
  (HE1-6, HE23-24). No weekday/weekend filter -- every day-of-week appeared
  in both the onpeak and offpeak trace timestamps of the reference figure.

Two entry points:
- plot_headroom_scatter(): new, generic function -- x is always wind, y is
  either 'solar' or 'load'; peak is 'onpeak' or 'offpeak'.
- The original wind-vs-solar look (with the load-filter slider) is
  reproduced by calling with y='solar'; the slider only made sense there
  because load was NOT already an axis. When y='load', the slider is
  dropped (it would show the same variable on two axes) -- this is called
  out in the figure title.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .. import mssql
from ..extract import fastscan, renewables

ONPEAK_HOURS = set(range(6, 22))  # HOUR(TIMESTAMP) is 0-23; HE7-22 == hour 6-21
LOAD_FILTER_STEPS = [0, 45, 50, 55, 60, 65, 70, 75]  # GW, matches original slider

# Existing reference/variant figures the user explicitly said must never be
# overwritten by this module -- any write to one of these basenames is refused.
_PROTECTED_OUTPUT_BASENAMES = {
    "ph_headroom_wind_solar.html", "ph_headroom_wind_solar1.html",
    "ph_headroom_wind_solar_v1.html", "ph_headroom_wind_solar_sep25.html",
    "ph_headroom_load_wind_onpeak.html",
}


def _write_html_guarded(fig: go.Figure, out_html: str | Path) -> None:
    out_path = Path(out_html)
    if out_path.name in _PROTECTED_OUTPUT_BASENAMES:
        raise RuntimeError(
            f"refusing to write to {out_path} -- this basename is protected "
            f"(existing reference/variant figure); use a new filename."
        )
    fig.write_html(str(out_path), include_plotlyjs="cdn")


def _fetch_headroom(config_id: int) -> pd.DataFrame:
    df = fastscan.headroom_with_curtailment(config_id)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])
    return df


def _fetch_west_wind(hist_start: str, hist_end: str) -> pd.DataFrame:
    df = renewables.wind_region_hourly(hist_start, hist_end, region="West")
    df["WIND_GW"] = (df["avgHSLPct"].astype(float) / 100.0) * df["totalInstalledCapacityMW"].astype(float) / 1000.0
    df = df.rename(columns={"TimeStamp": "TIMESTAMP"})
    return df[["TIMESTAMP", "WIND_GW"]]


def _fetch_solar(hist_start: str, hist_end: str, iso_zone: int = 67) -> pd.DataFrame:
    df = renewables.solar_hourly(hist_start, hist_end, iso_zone)
    df["TIMESTAMP"] = pd.to_datetime(df["TimeStampDate"]) + pd.to_timedelta(df["HE"].astype(int) - 1, unit="h")
    df["SOLAR_GW"] = df["solarGen"].astype(float) / 1000.0
    return df[["TIMESTAMP", "SOLAR_GW"]]


def _fetch_load(hist_start: str, hist_end: str) -> pd.DataFrame:
    """AW.dbo.ercotLoadView.ERCOT_ALL_LD -- ERCOT system total load, GW."""
    df = mssql.query(
        f"""SELECT date, he, ERCOT_ALL_LD
            FROM AW.dbo.ercotLoadView
            WHERE date >= '{hist_start}' AND date < '{hist_end}'""",
    )
    df["TIMESTAMP"] = pd.to_datetime(df["date"]) + pd.to_timedelta(df["he"].astype(int) - 1, unit="h")
    df["LOAD_GW"] = df["ERCOT_ALL_LD"].astype(float) / 1000.0
    return df[["TIMESTAMP", "LOAD_GW"]]


def _peak_mask(ts: pd.Series, peak: str) -> pd.Series:
    hours = ts.dt.hour
    onpeak = hours.isin(ONPEAK_HOURS)
    return onpeak if peak == "onpeak" else ~onpeak


def _binned_heatmap(df: pd.DataFrame, xcol: str, ycol: str, zcol: str,
                     xbin: float, ybin: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xedges = np.arange(0, df[xcol].max() + xbin, xbin)
    yedges = np.arange(0, df[ycol].max() + ybin, ybin)
    df = df.copy()
    df["_xb"] = pd.cut(df[xcol], xedges, labels=xedges[:-1])
    df["_yb"] = pd.cut(df[ycol], yedges, labels=yedges[:-1])
    piv = df.groupby(["_yb", "_xb"], observed=True)[zcol].median().unstack()
    piv = piv.reindex(index=yedges[:-1], columns=xedges[:-1])
    return xedges[:-1], yedges[:-1], piv.values


def plot_headroom_scatter(
    config_id: int,
    y: str = "load",
    peak: str = "onpeak",
    *,
    hist_start: str,
    hist_end: str,
    out_html: str | Path | None = None,
    title_prefix: str = "",
) -> go.Figure:
    """Headroom heatmap + scatter: West wind (GW) on x, `y` ('solar' or
    'load') on y, restricted to `peak` ('onpeak' or 'offpeak') hours.

    ONPEAK = HOUR(TIMESTAMP) in 6..21 (HE7-22), all 7 days of week.
    OFFPEAK = complement. This matches the reference `ph_headroom_wind_solar`
    figure's embedded data, NOT the repo's separate Mon-Fri "5x16" convention
    used elsewhere (e.g. build_screening_report.py).

    A load-filter slider (as in the original wind-vs-solar figure) is only
    added when y == 'solar' -- with y == 'load' it would duplicate the y-axis
    variable, so it's dropped.
    """
    assert y in ("solar", "load")
    assert peak in ("onpeak", "offpeak")

    hr = _fetch_headroom(config_id)
    wind = _fetch_west_wind(hist_start, hist_end)
    df = hr.merge(wind, on="TIMESTAMP", how="inner")

    if y == "solar":
        other = _fetch_solar(hist_start, hist_end)
        ycol, yname, ybin = "SOLAR_GW", "Solar (GW)", 1.0
        # the legacy wind-vs-solar figure also filtered by a load threshold via
        # its slider, so fetch load here purely as a filter column (not an axis)
        load = _fetch_load(hist_start, hist_end)
        df = df.merge(load, on="TIMESTAMP", how="left")
    else:
        other = _fetch_load(hist_start, hist_end)
        ycol, yname, ybin = "LOAD_GW", "Load (GW)", 5.0

    df = df.merge(other, on="TIMESTAMP", how="inner")
    n_peak_fastscan = int(_peak_mask(hr["TIMESTAMP"], peak).sum())
    df = df[_peak_mask(df["TIMESTAMP"], peak)].dropna(subset=["WIND_GW", ycol, "HEADROOM_AFTER_CURTAILMENT"])
    n_dropped = n_peak_fastscan - len(df)
    if n_dropped:
        print(f"[headroom_plots] {peak} fast-scan hours: {n_peak_fastscan} -> {len(df)} plotted "
              f"after joining wind/{y} (dropped {n_dropped}, e.g. missing driver-series coverage "
              f"or a timestamp with no match in {'ercotWindRegionHourly' if y == 'load' else 'ercotWindRegionHourly/solarGenAct'})")

    use_slider = y == "solar"
    # ROW-WISE: heatmap on top row, stress-hour scatter on bottom row, sharing
    # the wind-GW x-axis (both panels' x is West wind GW) -- avoids the
    # side-by-side layout + colorbar-overlap complaint from the column layout.
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
                         subplot_titles=(
        f"{peak.upper()}: median headroom (West wind x {yname})",
        f"{peak.upper()}: hours < 50 MW headroom",
    ))

    # One shared diverging colorscale (red = tight/low headroom, blue = comfortable/
    # high headroom) for both panels, so color reads consistently even though the
    # two panels intentionally use different z-ranges (heatmap: full range around
    # zmid=0; scatter: capped at cmax=50, per grading round 2 -- do not unify the
    # ranges, only the color family). Each row gets exactly one colorbar, placed
    # to the right of its own row (outside the plot area) so they never overlap:
    # top row's centered at y~0.79, bottom row's at y~0.21, both x=1.02.
    _DIVERGING = [[0.0, "#67001f"], [0.15, "#d6604d"], [0.35, "#f4a582"],
                  [0.5, "#f7f7f7"], [0.65, "#92c5de"], [0.85, "#4393c3"],
                  [1.0, "#053061"]]

    def _add_panel(sub: pd.DataFrame, visible: bool, label: str | None):
        xe, ye, z = _binned_heatmap(sub, "WIND_GW", ycol, "HEADROOM_AFTER_CURTAILMENT", 1.0, ybin)
        fig.add_trace(go.Heatmap(
            x=xe, y=ye, z=z, visible=visible, zmid=0,
            colorbar=dict(title=dict(text="Median headroom (MW)", side="right"),
                          x=1.02, xanchor="left", y=0.79, len=0.42, thickness=15,
                          outlinewidth=0),
            colorscale=_DIVERGING,
            hovertemplate=f"West %{{x}} GW, {yname} %{{y}}<br>median %{{z:.0f}} MW<extra></extra>",
        ), row=1, col=1)
        # scatter panel is genuinely filtered to near-limit hours (matches the
        # reference figure's "hours < 50 MW headroom" panel) -- NOT the full
        # `sub` used for the heatmap median.
        scat = sub[sub["HEADROOM_AFTER_CURTAILMENT"] < 50]
        text = [f"{t:%Y-%m-%d %H:%M} · {yname.split()[0].lower()} {v:.0f} GW"
                for t, v in zip(scat["TIMESTAMP"], scat[ycol])]
        fig.add_trace(go.Scattergl(
            x=scat["WIND_GW"], y=scat[ycol], mode="markers", visible=visible, text=text,
            marker=dict(size=5, color=scat["HEADROOM_AFTER_CURTAILMENT"], colorscale=_DIVERGING,
                        cmin=-400, cmax=50, showscale=True,
                        colorbar=dict(title=dict(text="Headroom (MW), capped <50", side="right"),
                                      x=1.02, xanchor="left", y=0.21, len=0.42, thickness=15,
                                      tickvals=[-400, -200, -50, 0, 50], outlinewidth=0)),
            hovertemplate=f"West %{{x:.1f}}, {yname.split()[0]} %{{y:.1f}} GW<br>"
                          "headroom %{marker.color:.0f} MW<br>%{text}<extra></extra>",
        ), row=2, col=1)
        return len(sub), len(scat)

    panel_counts: list[tuple[int, int]] = []
    if use_slider:
        for i, thresh in enumerate(LOAD_FILTER_STEPS):
            sub = df[df["LOAD_GW"] >= thresh]
            panel_counts.append(_add_panel(sub, visible=(i == 0), label=f">= {thresh} GW"))
        steps = []
        for i, thresh in enumerate(LOAD_FILTER_STEPS):
            vis = [False] * (2 * len(LOAD_FILTER_STEPS))
            vis[2 * i] = True
            vis[2 * i + 1] = True
            steps.append(dict(method="restyle", args=[{"visible": vis}], label=f">= {thresh} GW"))
        fig.update_layout(sliders=[dict(active=0, currentvalue={"prefix": f"{peak.title()} load filter: "},
                                         pad={"t": 60}, steps=steps)])
        print(f"[headroom_plots] per-slider-step (heatmap_n, scatter_n<50MW): {panel_counts}")
    else:
        panel_counts.append(_add_panel(df, visible=True, label=None))
        print(f"[headroom_plots] heatmap_n={panel_counts[0][0]}, scatter_n(<50MW)={panel_counts[0][1]}")

    n = len(df)
    fig.update_xaxes(title_text="West wind (GW)", row=2, col=1)
    fig.update_yaxes(title_text=yname, row=1, col=1)
    fig.update_yaxes(title_text=yname, row=2, col=1)
    subtitle = (f"{title_prefix} West wind (GW) vs {yname} — {peak.upper()} "
                f"(HE7-22, all days of week) — {hist_start}..{hist_end} — n={n} hrs — "
                "curtailment-restored headroom, red = at/near limit")
    if not use_slider:
        subtitle += " [no load-filter slider: load is already an axis]"
    # extra right margin gives each row's far-right colorbar (x=1.02) room
    # without getting clipped or overlapping the plot area; taller figure for
    # the stacked (row-wise) layout
    fig.update_layout(title=dict(text=subtitle), height=900, width=950,
                       margin=dict(r=130))

    if out_html:
        _write_html_guarded(fig, out_html)
    return fig


_ORIG_HEATMAP_COLORSCALE = [
    [0.0, "#4a0000"], [0.1388888888888889, "#8b0000"], [0.2222222222222222, "#e31a1c"],
    [0.2777777777777778, "#fd8d3c"], [0.3611111111111111, "#fecc5c"],
    [0.4722222222222222, "#c7e9b4"], [0.6666666666666666, "#41b6c4"], [1.0, "#253494"],
]
_ORIG_HEATMAP_TICKVALS = [-400, -150, 0, 100, 250, 450, 800, 1400]
_ORIG_SCATTER_COLORSCALE = [[0, "#4a0000"], [0.55, "#8b0000"], [0.89, "#e31a1c"], [1, "#fd8d3c"]]


def _orig_heatmap_trace(xe, ye, z, visible, cb_x, cb_y, yname):
    return go.Heatmap(
        x=xe, y=ye, z=z, visible=visible, showscale=True,
        zmin=-400, zmax=1400,
        colorbar=dict(title=dict(text="median MW"), tickvals=_ORIG_HEATMAP_TICKVALS,
                      x=cb_x, y=cb_y, len=0.42),
        colorscale=_ORIG_HEATMAP_COLORSCALE,
        hovertemplate=f"West %{{x}} GW, {yname} %{{y}}<br>median %{{z:.0f}} MW<extra></extra>",
    )


def _orig_scatter_trace(sub, ycol, yname, visible, cb_x, cb_y):
    scat = sub[sub["HEADROOM_AFTER_CURTAILMENT"] < 50]
    text = [f"{t:%Y-%m-%d %H:%M} · {yname.lower()} {v:.0f} GW"
            for t, v in zip(scat["TIMESTAMP"], scat[ycol])]
    return go.Scattergl(
        x=scat["WIND_GW"], y=scat[ycol], mode="markers", visible=visible, text=text,
        marker=dict(size=4.5, opacity=0.6, color=scat["HEADROOM_AFTER_CURTAILMENT"],
                    colorscale=_ORIG_SCATTER_COLORSCALE, cmin=-400, cmax=50, showscale=True,
                    colorbar=dict(title=dict(text="dot MW"), x=cb_x, y=cb_y, len=0.42)),
        hovertemplate=f"West %{{x:.1f}}, {yname} %{{y:.1f}} GW<br>"
                      "headroom %{marker.color:.0f} MW<br>%{text}<extra></extra>",
    ), len(scat)


def plot_wind_load_both(
    config_id: int,
    *,
    hist_start: str,
    hist_end: str,
    out_html: str | Path | None = None,
    title_prefix: str = "",
) -> go.Figure:
    """Exact clone of the reference `ph_headroom_wind_solar.html` 4-panel
    figure (same layout, slider, colorbars, colorscales, subplot domains,
    2x2 grid) with ONE substantive change: the ONPEAK panels' y-axis becomes
    LOAD instead of SOLAR. Per explicit user request, the ONPEAK load-filter
    slider is KEPT and still filters on LOAD_GW even though load is now also
    the y-axis -- each slider step therefore both filters points AND crops
    the visible y-range, which is the literal behavior asked for.

    OFFPEAK panels are unchanged from the reference (they already plotted
    West wind vs LOAD there). So this figure is "wind vs load, everywhere."

    Unlike plot_headroom_scatter(), this does NOT use the row-wise layout or
    the zmid=0/shared-colorscale styling from later grading rounds -- those
    were specific to the separate onpeak-only deliverable
    (ph_headroom_load_wind_onpeak.html). Here the ORIGINAL figure's exact
    look is the spec, reproduced from its decoded Plotly JSON (colorbar
    positions x=0.45/1.0, y=0.8 top row/0.26 bottom row, len=0.42; fixed
    zmin=-400/zmax=1400 heatmap scale with 8 tickvals; scatter cmin=-400/
    cmax=50, size=4.5, opacity=0.6; 2x2 domain grid; height=1200, width=1560).
    """
    hr = _fetch_headroom(config_id)
    wind = _fetch_west_wind(hist_start, hist_end)
    load = _fetch_load(hist_start, hist_end)
    df = hr.merge(wind, on="TIMESTAMP", how="inner").merge(load, on="TIMESTAMP", how="inner")

    onpeak = df[_peak_mask(df["TIMESTAMP"], "onpeak")].dropna(
        subset=["WIND_GW", "LOAD_GW", "HEADROOM_AFTER_CURTAILMENT"])
    offpeak = df[_peak_mask(df["TIMESTAMP"], "offpeak")].dropna(
        subset=["WIND_GW", "LOAD_GW", "HEADROOM_AFTER_CURTAILMENT"])

    fig = go.Figure()
    fig.update_layout(
        grid=dict(rows=2, columns=2),
        annotations=[
            dict(text="OnPeak 7x16: median headroom (West x load)", x=0.2366, y=1.0,
                 xref="paper", yref="paper", showarrow=False, xanchor="center", font=dict(size=14)),
            dict(text="OnPeak 7x16: hours < 50 MW headroom", x=0.7816, y=1.0,
                 xref="paper", yref="paper", showarrow=False, xanchor="center", font=dict(size=14)),
            dict(text="OffPeak 7x8: median headroom (West x LOAD)", x=0.2366, y=0.44,
                 xref="paper", yref="paper", showarrow=False, xanchor="center", font=dict(size=14)),
            dict(text="OffPeak 7x8: hours < 50 MW (y = load)", x=0.7816, y=0.44,
                 xref="paper", yref="paper", showarrow=False, xanchor="center", font=dict(size=14)),
        ],
        xaxis=dict(anchor="y", domain=[0.0, 0.4732], title=dict(text="West wind (GW)"), range=[0, 21]),
        yaxis=dict(anchor="x", domain=[0.56, 1.0], title=dict(text="Load (GW)")),
        xaxis2=dict(anchor="y2", domain=[0.5632, 1.0], title=dict(text="West wind (GW)"), range=[0, 21]),
        yaxis2=dict(anchor="x2", domain=[0.56, 1.0]),
        xaxis3=dict(anchor="y3", domain=[0.0, 0.4732], title=dict(text="West wind (GW)"), range=[0, 21]),
        yaxis3=dict(anchor="x3", domain=[0.0, 0.44], title=dict(text="ERCOT load (GW)"), range=[28, 85]),
        xaxis4=dict(anchor="y4", domain=[0.5632, 1.0], title=dict(text="West wind (GW)"), range=[0, 21]),
        yaxis4=dict(anchor="x4", domain=[0.0, 0.44], title=dict(text="ERCOT load (GW)")),
        height=1200, width=1560,
    )

    # ---- ONPEAK: 8 slider steps, West wind x LOAD, load-filtered ----
    n_visible_traces = 2 * len(LOAD_FILTER_STEPS)
    onpeak_counts = []
    for i, thresh in enumerate(LOAD_FILTER_STEPS):
        sub = onpeak[onpeak["LOAD_GW"] >= thresh]
        xe, ye, z = _binned_heatmap(sub, "WIND_GW", "LOAD_GW", "HEADROOM_AFTER_CURTAILMENT", 1.0, 3.0)
        ht = _orig_heatmap_trace(xe, ye, z, visible=(i == 0), cb_x=0.45, cb_y=0.8, yname="Load")
        ht.update(xaxis="x", yaxis="y")
        fig.add_trace(ht)
        sc, n_scat = _orig_scatter_trace(sub, "LOAD_GW", "Load", visible=(i == 0), cb_x=1.0, cb_y=0.8)
        sc.update(xaxis="x2", yaxis="y2")
        fig.add_trace(sc)
        onpeak_counts.append((len(sub), n_scat))

    steps = []
    for i, thresh in enumerate(LOAD_FILTER_STEPS):
        vis = [False] * n_visible_traces + [True, True]  # OFFPEAK traces always visible
        vis[2 * i] = True
        vis[2 * i + 1] = True
        steps.append(dict(method="restyle", args=[{"visible": vis}], label=f">= {thresh} GW"))
    fig.update_layout(sliders=[dict(active=0, currentvalue={"prefix": "OnPeak load filter: "},
                                     pad={"t": 60}, steps=steps)])

    # ---- OFFPEAK: single panel, West wind x LOAD (unchanged from reference) ----
    xe, ye, z = _binned_heatmap(offpeak, "WIND_GW", "LOAD_GW", "HEADROOM_AFTER_CURTAILMENT", 1.0, 3.0)
    ht_off = _orig_heatmap_trace(xe, ye, z, visible=True, cb_x=0.45, cb_y=0.26, yname="Load")
    ht_off.update(xaxis="x3", yaxis="y3")
    fig.add_trace(ht_off)
    sc_off, n_scat_off = _orig_scatter_trace(offpeak, "LOAD_GW", "Load", visible=True, cb_x=1.0, cb_y=0.26)
    sc_off.update(xaxis="x4", yaxis="y4")
    fig.add_trace(sc_off)

    title = (f"{title_prefix} West wind x LOAD (both onpeak and offpeak) — "
             f"{hist_start}..{hist_end} — curtailment-restored headroom, red = at/near limit")
    fig.update_layout(title=dict(text=title))

    print(f"[headroom_plots] plot_wind_load_both: onpeak per-slider-step (heatmap_n, scatter_n<50MW): "
          f"{onpeak_counts}")
    print(f"[headroom_plots] plot_wind_load_both: offpeak heatmap_n={len(offpeak)}, "
          f"scatter_n(<50MW)={n_scat_off}")

    if out_html:
        _write_html_guarded(fig, out_html)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--study", type=int, required=True)
    ap.add_argument("--fromnum", type=int, required=True)
    ap.add_argument("--tonum", type=int, required=True)
    ap.add_argument("--ctglabel", required=True)
    ap.add_argument("--y", choices=["solar", "load"], default="load")
    ap.add_argument("--peak", choices=["onpeak", "offpeak"], default="onpeak")
    ap.add_argument("--hist-start", required=True)
    ap.add_argument("--hist-end", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    configs = fastscan.find_configs(args.study, args.fromnum, args.tonum, args.ctglabel)
    if configs.empty:
        raise SystemExit(f"no active fast-scan config for study={args.study} "
                          f"{args.fromnum}-{args.tonum}@{args.ctglabel}")
    config_id = int(configs.iloc[0]["CONFIG_ID"])
    label = configs.iloc[0]["BRANCH_LABEL"]

    plot_headroom_scatter(
        config_id, y=args.y, peak=args.peak,
        hist_start=args.hist_start, hist_end=args.hist_end,
        out_html=args.out,
        title_prefix=f"{label} @ {args.ctglabel} (config {config_id}) —",
    )
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
