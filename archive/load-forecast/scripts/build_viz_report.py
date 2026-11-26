"""Build the static, offline model-visualization report for load-forecast.

Reads whatever is currently on disk under load-forecast/data/derived and
load-forecast/output and writes ONE self-contained HTML file (plotly.js
inlined once, no external/CDN requests) to output/model_report.html.

Pure function of these files (all under PROJECT_ROOT, see paths below):
    data/derived/size_index.parquet
    data/derived/scenario_hourly.parquet
    output/validation_scores.parquet
    output/backtest_rolling.csv
    output/experiments.csv
    output/analog_benchmark.csv

A background pipeline may be refreshing these files concurrently. Every read
is defensive: a missing file, an empty file, a file that fails to parse
(mid-write), or a file missing an expected column degrades that section (or
just that metric, for the header tiles) to a visible "not yet generated"
placeholder rather than raising. Re-run this script at any time to pick up
new numbers -- it never needs to be told what changed.

Run:    uv run python load-forecast/scripts/build_viz_report.py
Output: load-forecast/output/model_report.html

Design notes (dataviz skill, references/palette.md):
  - Zone color is a fixed categorical assignment, never cycled, never
    repainted by any filter: NCENT = slot 1 (blue), COAST = slot 2 (orange),
    SCENT = slot 3 (aqua). All three validate all-pairs CVD in light mode
    (see the palette-validation note printed at the end of a run); SCENT's
    aqua sits below 3:1 contrast on the light surface by design in the
    reference palette -- the relief channel (direct labels + the table-view
    twin on every chart) is shipped specifically to cover that WARN.
  - Sec. 3's bottom row plots ONE bar series per zone (monthly miss_gwh,
    zone-categorical hue -- the same color identity as that zone's top-row
    lines) with a neutral dotted line overlay (model-estimated weather
    anomaly vs. climate-normal; ink-primary, never zone-colored, so it reads
    as "the same diagnostic in every panel"). Bar color is NOT a sign
    encoder; bar position vs. the zero baseline carries the sign. The
    former two-bar weather/trend decomposition was removed 2026-08-14 (Opus
    review D2) -- the old trend_component_gwh column carried no trend
    information (see validate.py's module docstring). The zero baseline is
    drawn in the neutral axis/baseline token, emphasized.
  - Committed to a single light theme deliberately (see the banner in the
    rendered report) -- Plotly figures are baked at generation time, so a
    reactive dark mode would mean doubling every figure or re-theming via
    client JS, disproportionate for an internal static snapshot.
"""
from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DERIVED_DIR = PROJECT_ROOT / "data" / "derived"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUT_HTML = OUTPUT_DIR / "model_report.html"

SIZE_INDEX_PATH = DERIVED_DIR / "size_index.parquet"
SCENARIO_PATH = DERIVED_DIR / "scenario_hourly.parquet"
LOAD_HOURLY_PATH = DERIVED_DIR / "load_hourly.parquet"
VALIDATION_PATH = OUTPUT_DIR / "validation_scores.parquet"
VALIDATION_REPORT_PATH = OUTPUT_DIR / "validation_report.md"
BACKTEST_PATH = OUTPUT_DIR / "backtest_rolling.csv"
EXPERIMENTS_PATH = OUTPUT_DIR / "experiments.csv"
ANALOG_PATH = OUTPUT_DIR / "analog_benchmark.csv"

# ---------------------------------------------------------------------------
# Palette (dataviz skill reference instance, references/palette.md) -- light
# theme only, committed deliberately (see module docstring + report banner).
# ---------------------------------------------------------------------------
ZONES = ["NCENT", "COAST", "SCENT"]  # fixed order -- never cycled, never repainted by filters
ZONE_METRO = {"NCENT": "DFW metroplex", "COAST": "Houston / Harris Co.", "SCENT": "Austin + San Antonio"}
ZONE_COLOR = {"NCENT": "#2a78d6", "COAST": "#eb6834", "SCENT": "#1baf7a"}  # categorical slots 1 / 2 / 3

SURFACE = "#fcfcfb"
PAGE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BORDER = "rgba(11,11,11,0.10)"

STATUS_GOOD_TEXT = "#006300"      # palette.md "Delta up good / success text" token
STATUS_CRITICAL_TEXT = "#d03b3b"  # palette.md status "critical" token (4.68:1 on light surface)

ZERO_LINE = BASELINE            # neutral axis/baseline token, NOT the diverging near-white neutral
ANOMALY_LINE_COLOR = INK_PRIMARY  # Sec. 3 weather-anomaly overlay -- neutral, never zone-colored,
                                   # so the same line reads identically in every panel

MAPE_TARGET = 4.0
GROWTH_TARGET_PP = 1.0

FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

_SECTION_LOG: list[tuple[str, bool, str]] = []  # (title, rendered_ok, detail) -- for the end-of-run summary
_FILES_READ: list[tuple[str, float, int]] = []  # (rel_path, mtime, row_count) -- footer provenance block
_BUILD_TS: datetime | None = None  # set once at the top of build_html() so header + footer agree


def _log_read(path: Path, row_count: int) -> None:
    _FILES_READ.append((_rel(path), path.stat().st_mtime, row_count))


# ---------------------------------------------------------------------------
# Defensive readers -- never raise; a missing/empty/unparseable/short-schema
# file all degrade to (None, "<reason>") so callers can render a placeholder.
# ---------------------------------------------------------------------------
def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _read_parquet(path: Path, columns: list[str] | None = None) -> tuple[pd.DataFrame | None, str | None]:
    if not path.exists():
        return None, f"{_rel(path)} not found"
    try:
        df = pd.read_parquet(path, columns=columns)
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: any parse failure means "not ready yet"
        return None, f"{_rel(path)} unreadable ({exc.__class__.__name__}) -- likely mid-write from the refresh"
    _log_read(path, len(df))
    if df is None or df.empty:
        return None, f"{_rel(path)} is empty"
    return df, None


def _read_csv(path: Path) -> tuple[pd.DataFrame | None, str | None]:
    if not path.exists():
        return None, f"{_rel(path)} not found"
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        return None, f"{_rel(path)} unreadable ({exc.__class__.__name__}) -- likely mid-write from the refresh"
    _log_read(path, len(df))
    if df is None or df.empty:
        return None, f"{_rel(path)} is empty"
    return df, None


def _read_text(path: Path) -> tuple[str | None, str | None]:
    if not path.exists():
        return None, f"{_rel(path)} not found"
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return None, f"{_rel(path)} unreadable ({exc.__class__.__name__}) -- likely mid-write from the refresh"
    _log_read(path, text.count("\n") + 1)
    if not text.strip():
        return None, f"{_rel(path)} is empty"
    return text, None


def _require_columns(df: pd.DataFrame, cols: set[str], path: Path) -> tuple[pd.DataFrame | None, str | None]:
    missing = cols - set(df.columns)
    if missing:
        return None, f"{_rel(path)} is missing expected column(s) {sorted(missing)}"
    return df, None


# ---------------------------------------------------------------------------
# Small HTML helpers
# ---------------------------------------------------------------------------
def esc(x) -> str:
    return html.escape("" if x is None else str(x))


def fmt_pct(x, nd: int = 2) -> str:
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}%"


def fmt_pp(x, nd: int = 2) -> str:
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{nd}f} pp"


def placeholder(message: str) -> str:
    return (
        '<div class="placeholder"><span class="ph-icon" aria-hidden="true">&#8987;</span>'
        '<strong>not yet generated</strong>'
        f'<div class="ph-detail">{esc(message)}</div></div>'
    )


def details_table(summary: str, inner_html: str, open_default: bool = False) -> str:
    open_attr = " open" if open_default else ""
    return f'<details class="table-toggle"{open_attr}><summary>{esc(summary)}</summary>{inner_html}</details>'


def section_header(n: int, title: str, slug: str) -> str:
    return f'<h2 class="section-header" id="sec-{slug}">{n}. {esc(title)}</h2>'


def build_table(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    headers: dict[str, str] | None = None,
    formatters: dict[str, "callable"] | None = None,
    numeric_cols: set[str] | None = None,
) -> str:
    """Zebra-striped HTML table, right-aligned numerics -- the accessibility
    table-view twin for every chart, and the render used directly for the
    sections that are tables by nature (analog replay, scenario matrix)."""
    cols = columns or list(df.columns)
    headers = headers or {}
    formatters = formatters or {}
    numeric_cols = numeric_cols or set()
    thead = "".join(
        f'<th class="{"num" if c in numeric_cols else ""}">{esc(headers.get(c, c))}</th>' for c in cols
    )
    body_rows = []
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            val = row[c]
            text = formatters[c](val) if c in formatters else esc(val)
            cls = "num" if c in numeric_cols else ""
            cells.append(f'<td class="{cls}">{text}</td>')
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return f'<table class="data-table"><thead><tr>{thead}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'


def style_layout(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT, color=INK_SECONDARY, size=13),
        margin=dict(l=56, r=24, t=44, b=48),
        height=height,
        hoverlabel=dict(bgcolor=SURFACE, font=dict(family=FONT, color=INK_PRIMARY, size=12), bordercolor=BORDER),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0, font=dict(color=INK_SECONDARY)),
    )
    fig.update_xaxes(gridcolor=GRIDLINE, zeroline=False, linecolor=BASELINE, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(gridcolor=GRIDLINE, zeroline=False, linecolor=BASELINE, tickfont=dict(color=INK_MUTED))
    return fig


def fig_div(fig: go.Figure, div_id: str) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id=div_id,
        config={"displayModeBar": "hover", "displaylogo": False, "responsive": True},
    )


def _scrape_top50h_bias_2026() -> tuple[dict[str, float], str | None]:
    """Best-effort scrape of top50h_bias_pct for year 2026, per zone, out of
    validation_report.md. validate.py does not persist hourly/peak metrics to a
    structured file by design (see its module docstring) -- this is a defensive
    text parse of its markdown tables, not a schema contract; any parse miss
    just leaves that zone absent from the returned dict rather than raising."""
    text, err = _read_text(VALIDATION_REPORT_PATH)
    if text is None:
        return {}, err
    try:
        out: dict[str, float] = {}
        for zone, block in re.findall(r"## (\w+) — .*?\n(.*?)(?=\n## |\Z)", text, flags=re.S):
            for tbl in re.findall(r"(\|.+\|(?:\n\|.+\|)+)", block):
                lines = [ln for ln in tbl.splitlines() if ln.strip()]
                if len(lines) < 3:
                    continue
                header = [c.strip() for c in lines[0].strip("|").split("|")]
                if "top50h_bias_pct" not in header or "year" not in header:
                    continue
                yi, bi = header.index("year"), header.index("top50h_bias_pct")
                for ln in lines[2:]:
                    cells = [c.strip() for c in ln.strip("|").split("|")]
                    if len(cells) <= max(yi, bi):
                        continue
                    try:
                        if int(float(cells[yi])) == 2026:
                            out[zone] = float(cells[bi])
                    except ValueError:
                        continue
        if not out:
            return {}, f"no parsable top50h_bias_pct rows for 2026 in {_rel(VALIDATION_REPORT_PATH)}"
        return out, None
    except Exception as exc:  # noqa: BLE001 -- defensive: a parse-format surprise degrades, not crashes
        return {}, f"{_rel(VALIDATION_REPORT_PATH)} parse failed ({exc.__class__.__name__})"


# ---------------------------------------------------------------------------
# Section 1 -- header stat tiles
# ---------------------------------------------------------------------------
def section_header_tiles() -> str:
    header = section_header(1, "Header — forecast scorecard", "scorecard")

    val_df, val_err = _read_parquet(VALIDATION_PATH)
    if val_df is not None:
        val_df, val_err = _require_columns(val_df, {"weather_zone", "ape_pct", "month"}, VALIDATION_PATH)

    bt_df, bt_err = _read_csv(BACKTEST_PATH)
    if bt_df is not None:
        bt_df, bt_err = _require_columns(
            bt_df,
            {"zone", "wall_year", "target_year", "monthly_mape_pct", "growth_err_pp", "status"},
            BACKTEST_PATH,
        )

    top50_bias, top50_err = _scrape_top50h_bias_2026()

    tiles = []
    for zone in ZONES:
        mape_val = None
        if val_df is not None:
            zdf = val_df.loc[val_df["weather_zone"] == zone]
            if len(zdf):
                mape_val = float(zdf["ape_pct"].mean())

        growth_val = fold_label = bt_mean = None
        n_folds = 0
        if bt_df is not None:
            zdf = bt_df.loc[(bt_df["zone"] == zone) & (bt_df["status"] == "ok")]
            if len(zdf):
                bt_mean = float(zdf["monthly_mape_pct"].mean())
                n_folds = len(zdf)
                last = zdf.sort_values("target_year").iloc[-1]
                growth_val = float(last["growth_err_pp"])
                fold_label = f'{int(last["wall_year"])}→{int(last["target_year"])}'

        mape_ok = mape_val is not None and mape_val <= MAPE_TARGET
        growth_ok = growth_val is not None and abs(growth_val) <= GROWTH_TARGET_PP
        have_both = mape_val is not None and growth_val is not None
        verdict = "PASS" if (have_both and mape_ok and growth_ok) else ("FAIL" if have_both else None)

        growth_label = f"Growth error (backtest fold {fold_label})" if fold_label else "Growth error (backtest, latest fold)"

        # Latest-fold MAPE (wall_year==2024, i.e. the 2024->2025 fold) replaces the old
        # all-fold mean as this tile's primary number -- 2024->2025 is the fold whose
        # target year overlaps the honest validation window (sdalvi 2026-08-14). The
        # fold mean survives as small secondary text in the same row.
        latest_fold_mape = None
        if bt_df is not None:
            zdf24 = bt_df.loc[
                (bt_df["zone"] == zone) & (bt_df["wall_year"] == 2024) & (bt_df["status"] == "ok")
            ]
            if len(zdf24):
                latest_fold_mape = float(zdf24["monthly_mape_pct"].iloc[0])
        fold_mean_secondary = f"{n_folds}-fold mean {bt_mean:.2f}%" if bt_mean is not None else None

        top50_val = top50_bias.get(zone) if top50_bias else None

        rows = [
            ("Monthly MAPE (2025–26)", mape_val, fmt_pct(mape_val),
             mape_ok if mape_val is not None else None, None),
            (growth_label, growth_val, fmt_pp(growth_val),
             growth_ok if growth_val is not None else None, None),
            ("Backtest latest fold MAPE (2024→2025)", latest_fold_mape, fmt_pct(latest_fold_mape),
             None, fold_mean_secondary),
            ("Top-50h bias 2026", top50_val, (f"{top50_val:+.2f}%" if top50_val is not None else None),
             None, None),
        ]
        row_html = []
        for label, raw, text, ok, secondary in rows:
            if raw is None:
                row_html.append(
                    f'<div class="stat-row"><span class="stat-label">{esc(label)}</span>'
                    f'<span class="stat-value muted">not yet generated</span></div>'
                )
            else:
                cls = "" if ok is None else ("good-text" if ok else "bad-text")
                secondary_html = (
                    f'<span class="stat-value-secondary">{esc(secondary)}</span>' if secondary else ""
                )
                row_html.append(
                    f'<div class="stat-row"><span class="stat-label">{esc(label)}</span>'
                    f'<span class="stat-value-wrap"><span class="stat-value {cls}">{esc(text)}</span>'
                    f'{secondary_html}</span></div>'
                )

        if verdict == "PASS":
            badge = '<span class="badge badge-pass">&#10003; PASS</span>'
        elif verdict == "FAIL":
            badge = '<span class="badge badge-fail">&#10007; FAIL</span>'
        else:
            badge = '<span class="badge badge-unknown">not yet generated</span>'

        tiles.append(
            f'<div class="stat-tile" style="border-top-color:{ZONE_COLOR[zone]}">'
            f'<div class="stat-tile-head"><span class="zone-dot" style="background:{ZONE_COLOR[zone]}"></span>'
            f'<span class="stat-tile-title">{esc(zone)}</span>{badge}</div>'
            f'<div class="stat-tile-sub">{esc(ZONE_METRO[zone])}</div>'
            + "".join(row_html)
            + "</div>"
        )

    caption = (
        '<p class="caption">Growth error is sourced from <code>backtest_rolling.csv</code> (the rolling-origin '
        'backtest’s most recent fold: trained through the wall year, scored against the following year’s '
        'actual weather) rather than recomputed from <code>validation_scores.parquet</code>, which carries energy / '
        'APE columns only and has no growth-error field. See §4 for the full fold history. '
        f'PASS requires monthly MAPE ≤ {MAPE_TARGET:.0f}% AND |growth error| ≤ {GROWTH_TARGET_PP:.0f} pp.</p>'
    )
    body = f'<div class="stat-tile-grid">{"".join(tiles)}</div>' + caption
    if val_err:
        body += placeholder(f"Monthly MAPE: {val_err}")
    if bt_err:
        body += placeholder(f"Growth error / backtest latest-fold MAPE: {bt_err}")
    if top50_err:
        body += placeholder(f"Top-50h bias 2026: {top50_err}")

    _SECTION_LOG.append((
        "1. Header scorecard",
        val_df is not None or bt_df is not None,
        val_err or bt_err or top50_err or "ok",
    ))
    return header + body


# ---------------------------------------------------------------------------
# Section 2 -- size index
# ---------------------------------------------------------------------------
def section_size_index() -> str:
    header = section_header(2, "Size index — weather-normalized annual load level", "size-index")
    df, err = _read_parquet(SIZE_INDEX_PATH)
    if df is not None:
        df, err = _require_columns(df, {"weather_zone", "year", "size_idx", "normalized_gwh", "source"}, SIZE_INDEX_PATH)
    if df is None:
        _SECTION_LOG.append(("2. Size index", False, err))
        return header + placeholder(err)

    fig = go.Figure()
    end_labels = []
    for zone in ZONES:
        zdf = df.loc[df["weather_zone"] == zone].sort_values("year")
        if zdf.empty:
            continue
        color = ZONE_COLOR[zone]
        fitted = zdf.loc[zdf["source"] == "fitted"]
        extrap = zdf.loc[zdf["source"] == "extrapolated"]
        bridge = pd.concat([fitted.tail(1), extrap], ignore_index=True) if not fitted.empty else extrap

        if not fitted.empty:
            fig.add_trace(
                go.Scatter(
                    x=fitted["year"], y=fitted["size_idx"], mode="lines", name=zone, legendgroup=zone,
                    showlegend=True, line=dict(color=color, width=2, dash="solid"),
                    hovertemplate=f"{esc(zone)} " + "%{x}<br>size_idx %{y:.3f} (fitted)<extra></extra>",
                )
            )
        if not bridge.empty:
            fig.add_trace(
                go.Scatter(
                    x=bridge["year"], y=bridge["size_idx"], mode="lines", name=zone, legendgroup=zone,
                    showlegend=False, line=dict(color=color, width=2, dash="dash"),
                    hovertemplate=f"{esc(zone)} " + "%{x}<br>size_idx %{y:.3f} (extrapolated)<extra></extra>",
                )
            )
        last = zdf.iloc[-1]
        end_labels.append((float(last["year"]), float(last["size_idx"]), zone, color))

    # Terminal-year values were checked for label-collision risk before committing to bare
    # direct labels (see build log) -- at the last projected year the three zones separate by
    # >0.09 index points, comfortably clear of overlap; no leader lines needed.
    for year, val, zone, color in end_labels:
        fig.add_annotation(
            x=year, y=val, text=f"<b>{esc(zone)}</b>", showarrow=False, xanchor="left", xshift=8,
            font=dict(color=color, size=12), align="left",
        )

    fig.update_xaxes(title_text="Year", dtick=1, range=[df["year"].min() - 0.3, df["year"].max() + 1.6])
    fig.update_yaxes(title_text="Size index (2019 = 1.0)")
    style_layout(fig, height=420)
    div = fig_div(fig, "fig-size-index")

    caption = (
        '<p class="caption">Solid = fitted (≤ 2024); dashed = extrapolated. One shared y-axis; '
        'color = zone (fixed order, never repainted).</p>'
    )
    table = build_table(
        df.sort_values(["weather_zone", "year"])[["weather_zone", "year", "size_idx", "normalized_gwh", "source"]],
        headers={
            "weather_zone": "Zone", "year": "Year", "size_idx": "Size index",
            "normalized_gwh": "Normalized GWh", "source": "Source",
        },
        formatters={"size_idx": lambda v: f"{v:.3f}", "normalized_gwh": lambda v: f"{v:,.1f}"},
        numeric_cols={"year", "size_idx", "normalized_gwh"},
    )
    _SECTION_LOG.append(("2. Size index", True, "ok"))
    return header + f'<div class="chart-card">{div}</div>' + caption + details_table("View as table", table)


# ---------------------------------------------------------------------------
# Section 3 -- validation small multiples
# ---------------------------------------------------------------------------
def section_validation() -> str:
    header = section_header(3, "Validation — 2025–26 actual vs. weather-adjusted prediction", "validation")
    need = {"month", "actual", "pred_wx", "ape_pct", "miss_gwh", "weather_anomaly_gwh", "weather_zone"}
    df, err = _read_parquet(VALIDATION_PATH)
    if df is not None:
        df, err = _require_columns(df, need, VALIDATION_PATH)
    if df is None:
        _SECTION_LOG.append(("3. Validation", False, err))
        return header + placeholder(err)

    d = df.copy()
    d["month_dt"] = pd.to_datetime(d["month"], format="%Y-%m")
    for c in ["actual", "pred_wx"]:
        d[c + "_twh"] = d[c] / 1000.0

    fig = make_subplots(
        rows=2, cols=3, subplot_titles=[f"<b>{esc(z)}</b>" for z in ZONES],
        shared_xaxes=True, vertical_spacing=0.09, horizontal_spacing=0.035,
        row_heights=[0.55, 0.45],
    )
    for i, zone in enumerate(ZONES, start=1):
        zdf = d.loc[d["weather_zone"] == zone].sort_values("month_dt")
        color = ZONE_COLOR[zone]
        show_leg = i == 1
        fig.add_trace(
            go.Scatter(
                x=zdf["month_dt"], y=zdf["actual_twh"], mode="lines", name="Actual",
                legendgroup="actual", showlegend=show_leg, line=dict(color=color, width=2, dash="solid"),
                hovertemplate="%{x|%b %Y}<br>Actual %{y:.1f} TWh<extra></extra>",
            ),
            row=1, col=i,
        )
        fig.add_trace(
            go.Scatter(
                x=zdf["month_dt"], y=zdf["pred_wx_twh"], mode="lines", name="Predicted (weather-adj.)",
                legendgroup="pred", showlegend=show_leg, line=dict(color=color, width=2, dash="dash"),
                hovertemplate="%{x|%b %Y}<br>Predicted %{y:.1f} TWh<extra></extra>",
            ),
            row=1, col=i,
        )
        fig.add_trace(
            go.Bar(
                x=zdf["month_dt"], y=zdf["miss_gwh"], name="Monthly miss (pred − actual)",
                legendgroup="miss", showlegend=show_leg,
                marker=dict(color=color, line=dict(color=SURFACE, width=1.5)),
                hovertemplate="%{x|%b %Y}<br>Miss %{y:+.1f} GWh<extra></extra>",
            ),
            row=2, col=i,
        )
        fig.add_trace(
            go.Scatter(
                x=zdf["month_dt"], y=zdf["weather_anomaly_gwh"], mode="lines",
                name="model-estimated weather anomaly (GWh vs normal)",
                legendgroup="anomaly", showlegend=show_leg,
                line=dict(color=ANOMALY_LINE_COLOR, width=2, dash="dot"),
                hovertemplate="%{x|%b %Y}<br>Weather anomaly %{y:+.1f} GWh<extra></extra>",
            ),
            row=2, col=i,
        )
        fig.add_hline(y=0, line=dict(color=ZERO_LINE, width=1.5), row=2, col=i)

    row1_vals = pd.concat([d["actual_twh"], d["pred_wx_twh"]])
    row1_pad = (row1_vals.max() - row1_vals.min()) * 0.08
    fig.update_yaxes(range=[row1_vals.min() - row1_pad, row1_vals.max() + row1_pad], row=1)
    row2_vals = pd.concat([d["miss_gwh"], d["weather_anomaly_gwh"]])
    row2_pad = (row2_vals.max() - row2_vals.min()) * 0.08
    fig.update_yaxes(range=[row2_vals.min() - row2_pad, row2_vals.max() + row2_pad], row=2)
    fig.update_yaxes(title_text="TWh", row=1, col=1)
    fig.update_yaxes(title_text="GWh", row=2, col=1)
    for c in (2, 3):
        fig.update_yaxes(showticklabels=False, row=1, col=c)
        fig.update_yaxes(showticklabels=False, row=2, col=c)

    fig.update_layout(barmode="relative", hovermode="x unified")
    style_layout(fig, height=640)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="left", x=0))
    div = fig_div(fig, "fig-validation")

    caption = (
        '<p class="caption">Top row: solid = actual, dashed = predicted (weather-adjusted); line color = zone '
        '(the legend swatch shows the first panel’s color as a style key -- solid/dashed is what carries the '
        'meaning, not the specific hue). Shared y-axis across all three zones, as-is (SCENT is a genuinely smaller '
        'zone). Bottom row: monthly miss (predicted − actual, zone-colored bar against a zero baseline) with the '
        'model’s own estimate of the weather anomaly overlaid as a neutral dotted line -- how far that month’s '
        'weather pushed load off climate-normal, same GWh units. The two are related but not a decomposition: miss '
        'is the actual forecast error; weather anomaly is a diagnostic for how much of a given month’s swing was '
        'weather-driven. Hovering a month shows actual, predicted, miss, and the weather anomaly together.</p>'
    )
    table = build_table(
        d.sort_values(["weather_zone", "month"])[
            ["weather_zone", "month", "actual", "pred_wx", "ape_pct", "miss_gwh", "weather_anomaly_gwh"]
        ],
        headers={
            "weather_zone": "Zone", "month": "Month", "actual": "Actual (GWh)", "pred_wx": "Pred, actual wx (GWh)",
            "ape_pct": "APE %", "miss_gwh": "Miss (GWh)",
            "weather_anomaly_gwh": "Weather anomaly (GWh vs normal)",
        },
        formatters={
            "actual": lambda v: f"{v:,.1f}", "pred_wx": lambda v: f"{v:,.1f}",
            "ape_pct": lambda v: f"{v:.2f}", "miss_gwh": lambda v: f"{v:+,.1f}",
            "weather_anomaly_gwh": lambda v: f"{v:+,.1f}",
        },
        numeric_cols={"actual", "pred_wx", "ape_pct", "miss_gwh", "weather_anomaly_gwh"},
    )
    _SECTION_LOG.append(("3. Validation", True, "ok"))
    return header + f'<div class="chart-card">{div}</div>' + caption + details_table("View as table", table)


# ---------------------------------------------------------------------------
# Section 4 -- rolling backtest (+ subordinate experiment leaderboard)
# ---------------------------------------------------------------------------
def section_backtest() -> str:
    header = section_header(4, "Rolling backtest — honest level error by vintage", "backtest")
    need = {
        "zone", "wall_year", "target_year", "monthly_mape_pct", "annual_err_pct",
        "growth_err_pp", "hourly_mape_pct", "n_hours", "status",
    }
    df, err = _read_csv(BACKTEST_PATH)
    if df is not None:
        df, err = _require_columns(df, need, BACKTEST_PATH)

    if df is None:
        body = placeholder(err)
        _SECTION_LOG.append(("4. Rolling backtest", False, err))
    else:
        ok = df.loc[df["status"] == "ok"].copy()
        ok["fold"] = ok["wall_year"].astype(int).astype(str) + "→" + ok["target_year"].astype(int).astype(str)

        fig = make_subplots(
            rows=1, cols=2, subplot_titles=["Growth error by fold", "Monthly MAPE by fold"],
            horizontal_spacing=0.09,
        )
        for zone in ZONES:
            zdf = ok.loc[ok["zone"] == zone].sort_values("wall_year")
            color = ZONE_COLOR[zone]
            fig.add_trace(
                go.Scatter(
                    x=zdf["fold"], y=zdf["growth_err_pp"], mode="lines+markers", name=zone,
                    legendgroup=zone, showlegend=True,
                    line=dict(color=color, width=1.5), opacity=0.9,
                    marker=dict(color=color, size=10, line=dict(color=SURFACE, width=1.5)),
                    hovertemplate=f"{esc(zone)} " + "%{x}<br>growth error %{y:+.2f} pp<extra></extra>",
                ),
                row=1, col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=zdf["fold"], y=zdf["monthly_mape_pct"], mode="lines+markers", name=zone,
                    legendgroup=zone, showlegend=False,
                    line=dict(color=color, width=1.5), opacity=0.9,
                    marker=dict(color=color, size=10, line=dict(color=SURFACE, width=1.5)),
                    hovertemplate=f"{esc(zone)} " + "%{x}<br>monthly MAPE %{y:.2f}%<extra></extra>",
                ),
                row=1, col=2,
            )
        fig.add_hline(y=0, line=dict(color=BASELINE, width=2), row=1, col=1)
        fig.add_hline(
            y=MAPE_TARGET, line=dict(color=BASELINE, width=2, dash="dot"), row=1, col=2,
            annotation_text=f"{MAPE_TARGET:.0f}% target", annotation_position="top right",
            annotation_font=dict(color=INK_MUTED, size=11),
        )
        fig.update_yaxes(title_text="pp", row=1, col=1)
        fig.update_yaxes(title_text="%", row=1, col=2)
        fig.update_xaxes(title_text="Fold (wall→target)", row=1, col=1)
        fig.update_xaxes(title_text="Fold (wall→target)", row=1, col=2)
        style_layout(fig, height=420)
        div = fig_div(fig, "fig-backtest")

        caption = (
            '<p class="caption">Dot = one (zone, wall-year) fold; thin guide line traces the vintage trend. '
            'Left: zero line emphasized. Right: dotted line marks the '
            f'{MAPE_TARGET:.0f}% acceptance target. Color = zone (fixed order).</p>'
        )
        table = build_table(
            ok.sort_values(["zone", "wall_year"])[
                ["zone", "wall_year", "target_year", "monthly_mape_pct", "growth_err_pp", "hourly_mape_pct", "n_hours"]
            ],
            headers={
                "zone": "Zone", "wall_year": "Wall year", "target_year": "Target year",
                "monthly_mape_pct": "Monthly MAPE %", "growth_err_pp": "Growth err (pp)",
                "hourly_mape_pct": "Hourly MAPE %", "n_hours": "N hours",
            },
            formatters={
                "monthly_mape_pct": lambda v: f"{v:.2f}", "growth_err_pp": lambda v: f"{v:+.2f}",
                "hourly_mape_pct": lambda v: f"{v:.2f}", "n_hours": lambda v: f"{int(v):,}",
            },
            numeric_cols={"wall_year", "target_year", "monthly_mape_pct", "growth_err_pp", "hourly_mape_pct", "n_hours"},
        )
        body = f'<div class="chart-card">{div}</div>' + caption + details_table("View as table", table)
        _SECTION_LOG.append(("4. Rolling backtest", True, "ok"))

    # experiments.csv is a listed data input with no dedicated section in the spec -- folded in
    # here (subordinate, collapsed) rather than invented as its own numbered section.
    exp_df, exp_err = _read_csv(EXPERIMENTS_PATH)
    exp_need = {"zone", "wall_year", "target_year", "monthly_mape_pct", "growth_err_pp", "hourly_mape_pct", "tag", "status"}
    if exp_df is not None:
        exp_df, exp_err = _require_columns(exp_df, exp_need, EXPERIMENTS_PATH)

    if exp_df is not None:
        candidate_cols = [
            "tag", "zone", "wall_year", "target_year", "monthly_mape_pct",
            "growth_err_pp", "hourly_mape_pct", "n_fit_years", "status",
        ]
        cols = [c for c in candidate_cols if c in exp_df.columns]
        exp_table = build_table(
            exp_df[cols],
            headers={
                "tag": "Tag", "zone": "Zone", "wall_year": "Wall", "target_year": "Target",
                "monthly_mape_pct": "Monthly MAPE %", "growth_err_pp": "Growth err (pp)",
                "hourly_mape_pct": "Hourly MAPE %", "n_fit_years": "n_fit_years", "status": "Status",
            },
            formatters={
                "monthly_mape_pct": lambda v: f"{v:.2f}", "growth_err_pp": lambda v: f"{v:+.2f}",
                "hourly_mape_pct": lambda v: f"{v:.2f}",
                "n_fit_years": lambda v: "—" if pd.isna(v) else f"{int(v)}",
            },
            numeric_cols={"wall_year", "target_year", "monthly_mape_pct", "growth_err_pp", "hourly_mape_pct", "n_fit_years"},
        )
        exp_block = details_table(
            f"Experiment leaderboard — development iterations ({len(exp_df)} runs logged, scripts/experiment.py)",
            exp_table,
        )
    else:
        exp_block = f'<p class="caption">Experiment leaderboard: {esc(exp_err)}</p>'

    return header + body + exp_block


# ---------------------------------------------------------------------------
# Section 5 -- analog replay
# ---------------------------------------------------------------------------
def section_analog() -> str:
    header = section_header(5, "Analog replay — weather-matched historical benchmark", "analog")
    need = {
        "zone", "analog", "target", "pred_energy_gwh", "actual_energy_gwh", "energy_err_pct",
        "pred_peak_mw", "actual_peak_mw", "peak_err_pct", "distance_f",
    }
    df, err = _read_csv(ANALOG_PATH)
    if df is not None:
        df, err = _require_columns(df, need, ANALOG_PATH)
    if df is None:
        _SECTION_LOG.append(("5. Analog replay", False, err))
        return header + placeholder(err)

    d = df.copy().sort_values(["zone", "distance_f"])
    d["pred_energy_twh"] = d["pred_energy_gwh"] / 1000.0
    d["actual_energy_twh"] = d["actual_energy_gwh"] / 1000.0
    d["pred_peak_gw"] = d["pred_peak_mw"] / 1000.0
    d["actual_peak_gw"] = d["actual_peak_mw"] / 1000.0

    table = build_table(
        d[
            ["zone", "analog", "target", "distance_f", "pred_energy_twh", "actual_energy_twh", "energy_err_pct",
             "pred_peak_gw", "actual_peak_gw", "peak_err_pct"]
        ],
        headers={
            "zone": "Zone", "analog": "Analog month", "target": "Target month",
            "distance_f": "Weather distance (°F)", "pred_energy_twh": "Pred energy (TWh)",
            "actual_energy_twh": "Actual energy (TWh)", "energy_err_pct": "Energy err %",
            "pred_peak_gw": "Pred peak (GW)", "actual_peak_gw": "Actual peak (GW)", "peak_err_pct": "Peak err %",
        },
        formatters={
            "distance_f": lambda v: f"{v:.2f}",
            "pred_energy_twh": lambda v: f"{v:.1f}", "actual_energy_twh": lambda v: f"{v:.1f}",
            "energy_err_pct": lambda v: f"{v:+.2f}",
            "pred_peak_gw": lambda v: f"{v:.1f}", "actual_peak_gw": lambda v: f"{v:.1f}",
            "peak_err_pct": lambda v: f"{v:+.2f}",
        },
        numeric_cols={
            "distance_f", "pred_energy_twh", "actual_energy_twh", "energy_err_pct",
            "pred_peak_gw", "actual_peak_gw", "peak_err_pct",
        },
    )
    caption = (
        '<p class="caption">Closest historical weather analogs per zone, replayed at the target year’s system '
        'size (<code>src/analog.py</code>); sorted by weather distance within zone. Distance = RMSE of daily '
        'temperature quantile vectors + 0.25× mean dewpoint offset. Replay uses the analog month’s own '
        'weekday/holiday calendar; weekday-mix difference adds ~1% noise to monthly energy comparisons.</p>'
    )
    _SECTION_LOG.append(("5. Analog replay", True, "ok"))
    return header + f'<div class="table-card">{table}</div>' + caption


# ---------------------------------------------------------------------------
# Section 6 -- scenario matrix
# ---------------------------------------------------------------------------
def section_scenario_matrix() -> str:
    header = section_header(6, "Scenario matrix — weather year × system year", "scenario")
    df, err = _read_parquet(SCENARIO_PATH, columns=["weather_zone", "scenario_id", "load_mw_pred"])
    if df is not None:
        df, err = _require_columns(df, {"weather_zone", "scenario_id", "load_mw_pred"}, SCENARIO_PATH)
    if df is None:
        _SECTION_LOG.append(("6. Scenario matrix", False, err))
        return header + placeholder(err)

    parsed = df["scenario_id"].str.extract(r"^wx(\d{4})_sys(\d{4})$")
    d = df.assign(wx_year=parsed[0], sys_year=parsed[1])
    d = d.loc[d["wx_year"].notna() & d["sys_year"].notna()].copy()
    d["wx_year"] = d["wx_year"].astype(int)
    d["sys_year"] = d["sys_year"].astype(int)

    agg = (
        d.groupby(["weather_zone", "wx_year", "sys_year"])
        .agg(
            twh=("load_mw_pred", lambda s: float(s.sum()) / 1e6),
            peak_gw=("load_mw_pred", lambda s: float(s.max()) / 1000.0),
            n_hours=("load_mw_pred", "size"),
        )
        .reset_index()
    )
    full_hours = int(agg["n_hours"].max()) if len(agg) else None

    # "actual 2025 (weather as realized)" reference row -- a real-world anchor to eyeball
    # each modeled column against. Same actual-hours convention validate.py uses (raw
    # ts_local year, uri/outage excluded) -- see its module docstring.
    lh_df, lh_err = _read_parquet(
        LOAD_HOURLY_PATH, columns=["weather_zone", "ts_local", "load_mw", "event_flag"]
    )
    actual_2025: dict[str, tuple[float, float]] = {}
    if lh_df is not None:
        clean = lh_df.loc[
            (lh_df["ts_local"].dt.year == 2025) & ~lh_df["event_flag"].fillna("").isin(["uri", "outage"])
        ]
        for zone in ZONES:
            zdf_lh = clean.loc[clean["weather_zone"] == zone]
            if len(zdf_lh):
                actual_2025[zone] = (
                    float(zdf_lh["load_mw"].sum()) / 1e6,
                    float(zdf_lh["load_mw"].max()) / 1000.0,
                )

    blocks = []
    any_partial = False
    for zone in ZONES:
        zdf = agg.loc[agg["weather_zone"] == zone]
        if zdf.empty:
            blocks.append(
                f'<h3 class="zone-subhead" style="color:{ZONE_COLOR[zone]}">{esc(zone)}</h3>'
                + placeholder(f"no scenarios found for {zone}")
            )
            continue
        wx_years = sorted(zdf["wx_year"].unique())
        sys_years = sorted(zdf["sys_year"].unique())
        cell = {(int(r["wx_year"]), int(r["sys_year"])): r for _, r in zdf.iterrows()}

        thead = '<th>Weather year (rows) / System year (cols)</th>' + "".join(
            f'<th class="num">{sy}</th>' for sy in sys_years
        )
        ref_row_html = ""
        if zone in actual_2025:
            a_twh, a_peak_gw = actual_2025[zone]
            tds_ref = "".join(
                f'<td class="num" title="realized 2025 weather -- not a modeled scenario cell">'
                f'{a_twh:.1f} TWh / {a_peak_gw:.1f} GW</td>'
                for _ in sys_years
            )
            ref_row_html = f'<tr class="ref-row"><td><em>actual 2025 (weather as realized)</em></td>{tds_ref}</tr>'
        rows_html = []
        for wy in wx_years:
            partial = any(cell[(wy, sy)]["n_hours"] < full_hours for sy in sys_years if (wy, sy) in cell)
            any_partial = any_partial or partial
            wy_label = f"{wy}*" if partial else str(wy)
            tds = []
            for sy in sys_years:
                r = cell.get((wy, sy))
                if r is None:
                    tds.append('<td class="num">—</td>')
                    continue
                nh = int(r["n_hours"])
                # Every cell carries its exact hour count on hover (not just the truncated ones) --
                # useful context even for full-year cells, and keeps this branch-free.
                title_attr = f' title="{nh:,} hours"'
                tds.append(f'<td class="num"{title_attr}>{r["twh"]:.1f} TWh / {r["peak_gw"]:.1f} GW</td>')
            rows_html.append(f"<tr><td>{esc(wy_label)}</td>{''.join(tds)}</tr>")
        table = (
            f'<table class="data-table scenario-table"><thead><tr>{thead}</tr></thead>'
            f'<tbody>{ref_row_html}{"".join(rows_html)}</tbody></table>'
        )
        blocks.append(f'<h3 class="zone-subhead" style="color:{ZONE_COLOR[zone]}">{esc(zone)}</h3>' + table)
        if zone == "NCENT":
            blocks.append(
                '<p class="zone-warning">&#9888; NCENT column carries a known structural under-forecast '
                '(~3 pp/yr growth); see §7.</p>'
            )

    note = ""
    if any_partial:
        note += (
            '<p class="caption">* wx2021 covers 8,495 h (ex-Uri) vs. ≈ 8,759 h for other weather years — '
            'its TWh/peak is not directly comparable to a full-year column at face value; hover any cell for its '
            'exact hour count. See §7.</p>'
        )
    if not actual_2025:
        note += placeholder(f"actual 2025 reference row: {lh_err or 'no zone matched 2025 data'}")
    _SECTION_LOG.append(("6. Scenario matrix", True, "ok"))
    return header + '<div class="scenario-grid">' + "".join(blocks) + "</div>" + note


# ---------------------------------------------------------------------------
# Section 7 -- footer caveats (verbatim)
# ---------------------------------------------------------------------------
def section_footer() -> str:
    header = section_header(7, "Data caveats", "caveats")
    items = [
        "NOAA truncation patched via Mesonet 2025-08-25+",
        "2016-07-01 missing in source view",
        "wx2021 scenarios are ex-Uri (8,495 h)",
        "NCENT growth under-forecast is a known open item",
    ]
    lis = "".join(f"<li>{esc(item)}</li>" for item in items)

    # Provenance block: build timestamp + mtime/row-count of every input file this run
    # actually read (deduped by path -- a file read by more than one section, e.g.
    # backtest_rolling.csv, appears once here; repeat reads within one build are identical).
    seen: dict[str, tuple[float, int]] = {}
    for rel_path, mtime, rows in _FILES_READ:
        seen.setdefault(rel_path, (mtime, rows))
    prov_rows = "".join(
        f"<tr><td>{esc(path)}</td>"
        f'<td class="num">{esc(datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"))}</td>'
        f'<td class="num">{rows:,}</td></tr>'
        for path, (mtime, rows) in sorted(seen.items())
    )
    build_ts_label = _BUILD_TS.strftime("%Y-%m-%d %H:%M:%S") if _BUILD_TS is not None else "—"
    provenance = (
        '<div class="provenance">'
        f'<p class="caption">Build timestamp: {esc(build_ts_label)} (container local time). Every input file '
        "this report read, as of this build (rows = text files' line count):</p>"
        '<table class="data-table provenance-table"><thead><tr><th>Input file</th>'
        '<th class="num">Last modified</th><th class="num">Rows</th></tr></thead>'
        f"<tbody>{prov_rows}</tbody></table>"
        "</div>"
    )

    _SECTION_LOG.append(("7. Data caveats", True, "ok"))
    return header + f'<ul class="caveats">{lis}</ul>' + provenance


# ---------------------------------------------------------------------------
# CSS (plain string -- deliberately NOT an f-string; CSS braces would collide
# with Python's f-string interpolation syntax)
# ---------------------------------------------------------------------------
CSS = """
:root {
  --surface-1:#fcfcfb; --page:#f9f9f7; --ink-primary:#0b0b0b; --ink-secondary:#52514e;
  --ink-muted:#898781; --gridline:#e1e0d9; --baseline:#c3c2b7; --border:rgba(11,11,11,0.10);
}
* { box-sizing: border-box; }
html, body { background:var(--page); color:var(--ink-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif; margin:0; }
body { padding: 28px clamp(16px, 4vw, 48px) 72px; }
.report-wrap { max-width: 1320px; margin: 0 auto; }
.report-header h1 { font-size: 1.55rem; margin: 0 0 4px; }
.report-sub { color: var(--ink-secondary); font-size: 0.9rem; margin: 0 0 14px; }
.notice { background: #fff8e6; border: 1px solid var(--border); border-left: 4px solid #c98500;
  border-radius: 6px; padding: 10px 16px; font-size: 0.86rem; color: var(--ink-secondary); margin-bottom: 26px; }
.notice strong { color: var(--ink-primary); }
.theme-note { font-size: 0.8rem; color: var(--ink-muted); margin: 4px 0 0; }
.report-section { margin-bottom: 42px; }
.section-header { font-size: 1.12rem; border-bottom: 1px solid var(--gridline); padding-bottom: 8px; margin: 0 0 16px; }
.caption { color: var(--ink-secondary); font-size: 0.84rem; margin: 8px 2px 0; line-height: 1.5; }
.chart-card, .table-card { background: var(--surface-1); border: 1px solid var(--border); border-radius: 10px;
  padding: 10px 16px 4px; overflow-x: auto; }
.stat-tile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.stat-tile { background: var(--surface-1); border: 1px solid var(--border); border-top: 4px solid var(--baseline);
  border-radius: 10px; padding: 14px 18px 16px; }
.stat-tile-head { display:flex; align-items:center; gap:8px; margin-bottom:2px; }
.zone-dot { width:10px; height:10px; border-radius:50%; display:inline-block; flex: none; }
.stat-tile-title { font-weight:600; font-size:1.05rem; flex:1; }
.stat-tile-sub { color: var(--ink-muted); font-size:0.76rem; margin-bottom:10px; }
.stat-row { display:flex; justify-content:space-between; gap:12px; padding:5px 0; border-top:1px solid var(--gridline);
  font-size:0.87rem; }
.stat-row:first-of-type { border-top:none; }
.stat-label { color: var(--ink-secondary); }
.stat-value { font-weight:600; font-variant-numeric: tabular-nums; }
.stat-value.muted { color: var(--ink-muted); font-weight:400; font-style:italic; font-variant-numeric: normal; }
.good-text { color:#006300; }
.bad-text { color:#d03b3b; }
.badge { font-size:0.7rem; font-weight:700; padding:3px 9px; border-radius:999px; letter-spacing:0.02em; white-space:nowrap; }
.badge-pass { background: rgba(0,99,0,0.12); color:#006300; }
.badge-fail { background: rgba(208,59,59,0.12); color:#d03b3b; }
.badge-unknown { background: rgba(137,135,129,0.14); color: var(--ink-muted); font-weight:600; }
.placeholder { border:2px dashed #c9c7bd; border-radius:10px; padding:18px 20px; color: var(--ink-muted); }
.ph-icon { font-size:1.05rem; margin-right:8px; }
.ph-detail { font-size:0.8rem; margin-top:6px; color: var(--ink-muted); }
details.table-toggle { margin-top:10px; }
details.table-toggle summary { cursor:pointer; color: var(--ink-secondary); font-size:0.84rem; padding:4px 0;
  user-select:none; }
details.table-toggle summary:hover { color: var(--ink-primary); }
table.data-table { border-collapse: collapse; width:100%; font-size:0.84rem; margin-top:6px; }
table.data-table th { text-align:left; color: var(--ink-secondary); border-bottom:1px solid var(--baseline);
  padding:6px 10px; font-weight:600; white-space:nowrap; }
table.data-table td { padding:6px 10px; border-bottom:1px solid var(--gridline); font-variant-numeric: tabular-nums;
  white-space:nowrap; }
table.data-table th.num, table.data-table td.num { text-align:right; }
table.data-table tbody tr:nth-child(even) { background: rgba(11,11,11,0.025); }
.scenario-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:24px; align-items:start; }
.zone-subhead { margin: 0 0 8px; font-size:1rem; }
.caveats { font-size:0.87rem; color: var(--ink-secondary); line-height:1.7; }
code { background: rgba(11,11,11,0.05); border-radius:4px; padding:1px 5px; font-size:0.85em; }
.stat-value-wrap { display:flex; flex-direction:column; align-items:flex-end; line-height:1.25; }
.stat-value-secondary { font-size:0.72rem; color: var(--ink-muted); font-weight:400; margin-top:1px;
  font-variant-numeric: tabular-nums; }
.zone-warning { font-size:0.82rem; color:#8a5300; margin:6px 2px 14px; }
table.scenario-table tr.ref-row td { font-style:italic; background: rgba(11,11,11,0.035);
  border-bottom:2px solid var(--baseline); }
.provenance { margin-top:10px; }
table.provenance-table { font-size:0.78rem; }
"""


# ---------------------------------------------------------------------------
# Assemble & write
# ---------------------------------------------------------------------------
def build_html() -> str:
    global _BUILD_TS
    _BUILD_TS = datetime.now()  # single source of truth -- header and footer (§7 provenance) agree
    sections_html = "\n".join(
        f'<div class="report-section">{fn()}</div>'
        for fn in (
            section_header_tiles,
            section_size_index,
            section_validation,
            section_backtest,
            section_analog,
            section_scenario_matrix,
            section_footer,
        )
    )
    generated_ts = _BUILD_TS.strftime("%Y-%m-%d %H:%M")
    plotly_js = pyo.get_plotlyjs()

    head_html = (
        "<header class=\"report-header\">"
        "<h1>ERCOT Zonal Load Forecast — Model Report</h1>"
        f"<p class=\"report-sub\">NCENT / COAST / SCENT · generated {esc(generated_ts)} (container local time) "
        "· static offline snapshot, plotly bundled inline, no CDN.</p>"
        "<div class=\"notice\"><strong>In progress:</strong> a background pipeline is currently refreshing the "
        "load-forecast data files. This report is a pure function of whatever was on disk at generation time -- "
        "re-run <code>uv run python load-forecast/scripts/build_viz_report.py</code> after the refresh completes "
        "to regenerate it with final numbers. Any input that was missing, empty, or mid-write at generation time "
        "renders as a visible “not yet generated” placeholder below rather than being silently skipped."
        "<p class=\"theme-note\">Rendered in a single light theme by deliberate choice (no reactive dark-mode "
        "variant this pass -- Plotly figures are baked at generation time, so a reactive dark theme would mean "
        "doubling every figure). Zone color is fixed (NCENT/COAST/SCENT = categorical slots 1/2/3) and validated "
        "all-pairs CVD-safe in light mode; SCENT’s aqua sits below 3:1 contrast on the light surface by design "
        "in the reference palette, which is why every chart in this report ships direct labels and a table-view "
        "twin as the relief channel.</p>"
        "</div>"
        "</header>"
    )

    doc = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>ERCOT Zonal Load Forecast — Model Report</title>\n"
        "<style>" + CSS + "</style>\n"
        "</head>\n<body>\n"
        "<script>" + plotly_js + "</script>\n"
        "<div class=\"report-wrap\">\n" + head_html + "\n" + sections_html + "\n</div>\n"
        "</body>\n</html>\n"
    )
    return doc


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = build_html()
    OUT_HTML.write_text(doc, encoding="utf-8")
    size_kb = OUT_HTML.stat().st_size / 1024
    print(f"wrote {OUT_HTML} ({size_kb:,.0f} KB)")
    print("\nsection status:")
    for title, ok, detail in _SECTION_LOG:
        flag = "ok" if ok else "PLACEHOLDER"
        print(f"  [{flag:11s}] {title} -- {detail}")


if __name__ == "__main__":
    main()
