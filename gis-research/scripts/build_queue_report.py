"""Build a self-contained interactive HTML queue report from the ERCOT GIS parquet.

Source `ercotGenerationInterconnect` (SQL Server AW.dbo, downloaded to parquet) IS the
ERCOT GIS monthly report: one row per (INR project, fileDate monthly snapshot). Verified
identical to the official "GIS_Report_<mon><yr>.xlsx" Project Details sheets (INR set and
per-fuel capacity match exactly for 2026-06).

We pick ONE report date (default = latest fileDate), drop terminal / already-online
projects, derive a normalized "Fuel Technology" label + milestone booleans + a Texas
county FIPS, and embed the active-queue rows as JSON inside a single self-contained
.html (Plotly.js + TX-county GeoJSON inlined). All filtering/aggregation happens
client-side (no server).

Layout:
  - Table: rows = CDR Reporting Zone (+ TOTAL); column groups = milestone gates, each
    showing Capacity (GW) and # Projects. Fuel Technology dropdown; Projected COD range
    filter (defaults start = today). Clicking a cell (zone x milestone) drives the map.
  - Map: Texas county choropleth of the selected subset's capacity (GW); hover shows
    county + total GW + project names; click a county for a side list (name, GW, COD, status).

Read-only. Run from repo root:
  uv run gis-research/scripts/build_queue_report.py                    # latest date
  uv run gis-research/scripts/build_queue_report.py --report-date 2025-06-01
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PARQUET = BASE / "data" / "ercot_generation_interconnect.parquet"
ASSETS = BASE / "assets"
OUT_DIR = BASE / "output"

ZONE_ORDER = ["COASTAL", "EAST-SPP", "HOUSTON", "NORTH", "PANHANDLE", "SOUTH", "WEST", "Unassigned"]

# Milestone column groups: (key, header). Each renders as (Capacity GW, # Projects).
# "total" is the denominator (all active projects); the rest are independent gates.
MILESTONES = [
    ("total", "In Queue (Total)"),
    ("screening", "Screening Complete"),
    ("fis", "FIS Approved"),
    ("ia", "IA Signed"),
    ("finsec", "Financial Security"),
    ("s691", "Meets 6.9(1)"),
    ("s69", "Meets all 6.9"),
]

# Projects already online / no longer in the interconnection queue -> excluded.
# The first three match ERCOT's own "Project Details" active list; the last two add the
# user's "treat approved-for-sync/energization as online" refinement.
TERMINAL_COLS = [
    "cancelDate",
    "inActiveDate",
    "approvedForCommercialOperation",
    "approvedForSynchronization",
    "ApprovedForEnergization",
]


def _norm_county(s: str) -> str:
    return "".join(ch for ch in str(s).upper() if ch.isalnum())


def normalize_fuel_tech(fuel: str | None, tech: str | None) -> str:
    """Map messy (fuel, technology) code/word forms to a friendly Fuel Technology label.

    Handles None / NaN safely (NaN is truthy, so `fuel or ""` would leak a float).
    """
    f = "" if pd.isna(fuel) else str(fuel).strip().upper()
    t = "" if pd.isna(tech) else str(tech).strip().upper()
    if f in {"SOL", "SOLAR"} or f.startswith("SOLAR"):
        return "Solar PV" if t in {"PV", ""} else f"Solar ({t})"
    if f in {"WIN", "WIND"}:
        return "Wind"
    # Batteries: fuel is often OTH or "Battery Storage"/BAT, technology BA.
    if t == "BA" or f in {"BAT", "BATTERY", "STORAGE"} or "BATTERY" in f or "STORAGE" in f:
        return "Battery / Storage"
    if f == "GAS":
        return {
            "CC": "Gas - Combined Cycle",
            "GT": "Gas - Combustion Turbine",
            "IC": "Gas - Internal Combustion",
            "ST": "Gas - Steam Turbine",
        }.get(t, "Gas - Other")
    return "Other"


def build_records(df: pd.DataFrame, report_date: str) -> tuple[list[dict], dict]:
    """Return (active-queue records, metadata) for the chosen report date."""
    dates = sorted(pd.Series(df["fileDate"].unique()).astype(str))
    if report_date == "latest":
        report_date = dates[-1]
    if report_date not in dates:
        raise SystemExit(
            f"report-date {report_date!r} not in data. "
            f"Available range {dates[0]} .. {dates[-1]} ({len(dates)} monthly snapshots)."
        )

    snap = df[df["fileDate"].astype(str) == report_date].copy()
    n_snapshot = len(snap)

    terminal = pd.Series(False, index=snap.index)
    for col in TERMINAL_COLS:
        terminal |= snap[col].notna()
    active = snap[~terminal].copy()

    name2fips = json.loads((ASSETS / "tx_county_fips.json").read_text())

    cod = pd.to_datetime(active["projectCod"], errors="coerce")
    records = []
    unmatched_counties: set[str] = set()
    for (_, row), cod_ts in zip(active.iterrows(), cod):
        county = row["county"] if pd.notna(row["county"]) else None
        fips = name2fips.get(_norm_county(county)) if county else None
        if county and not fips:
            unmatched_counties.add(county)
        records.append(
            {
                "inr": row["INR"],
                "name": row["projectName"] if pd.notna(row["projectName"]) else row["INR"],
                "fuelTech": normalize_fuel_tech(row["fuel"], row["technology"]),
                "zone": row["cdrReportingZone"] if pd.notna(row["cdrReportingZone"]) else "Unassigned",
                "county": county,
                "fips": fips,
                "gw": (float(row["capacityMw"]) / 1000.0) if pd.notna(row["capacityMw"]) else 0.0,
                "cod": cod_ts.strftime("%Y-%m-%d") if pd.notna(cod_ts) else None,
                "status": row["ginrStudyPhase"] if pd.notna(row["ginrStudyPhase"]) else "—",
                "screening": bool(pd.notna(row["screeningStudyComplete"])),
                "fis": bool(pd.notna(row["fisApproved"])),
                "ia": bool(pd.notna(row["iaSigned"])),
                "finsec": row["financialSecurityAndNoticeToProceedProvided"] == "Yes",
                "s691": bool(pd.notna(row["meetsSection691"])),
                "s69": bool(pd.notna(row["meetsAllSection69"])),
            }
        )

    if unmatched_counties:
        print(f"WARNING: {len(unmatched_counties)} counties had no FIPS match "
              f"(dropped from map): {sorted(unmatched_counties)}")

    cod_valid = [r["cod"] for r in records if r["cod"]]
    meta = {
        "reportDate": report_date,
        "nSnapshot": int(n_snapshot),
        "nActive": len(records),
        "nTerminalExcluded": int(n_snapshot - len(records)),
        "codMin": min(cod_valid) if cod_valid else None,
        "codMax": max(cod_valid) if cod_valid else None,
        "fuelTechs": sorted({r["fuelTech"] for r in records}),
        "zoneOrder": [z for z in ZONE_ORDER if any(r["zone"] == z for r in records)],
        "milestones": MILESTONES,
    }
    return records, meta


def render_html(records: list[dict], meta: dict) -> str:
    plotly_js = (ASSETS / "plotly.min.js").read_text()
    geojson = (ASSETS / "tx_counties.geojson").read_text()
    return (
        HTML_TEMPLATE
        .replace("/*__PLOTLYJS__*/", plotly_js)
        .replace('"__GEOJSON__"', geojson)
        .replace('"__DATA__"', json.dumps(records, separators=(",", ":")))
        .replace('"__META__"', json.dumps(meta, separators=(",", ":")))
    )


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ERCOT GIS Queue Report</title>
<style>
  :root {
    --bg: #ffffff; --surface: #f7f8fa; --ink: #1a1d21; --ink-2: #545a63;
    --muted: #8a919c; --line: #e2e6ec; --accent: #2563eb; --accent-soft: #eef3ff;
    --group-a: #f7f8fa; --sel: #ffe9b3; --sel-line: #e0a800;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #14171c; --surface: #1c2027; --ink: #eceff3; --ink-2: #b3bac4;
      --muted: #7d8590; --line: #2a2f38; --accent: #6ea8fe; --accent-soft: #1e2633;
      --group-a: #1c2027; --sel: #4a3a12; --sel-line: #e0a800;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0 auto; padding: 24px; max-width: 1280px; background: var(--bg); color: var(--ink);
    font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  h1 { font-size: 20px; margin: 0 0 2px; }
  h2 { font-size: 15px; margin: 26px 0 10px; }
  .sub { color: var(--ink-2); font-size: 13px; margin-bottom: 18px; }
  .sub b { color: var(--ink); }
  .controls {
    display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end;
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px 18px; margin-bottom: 18px;
  }
  .ctl label { display: block; font-size: 11px; text-transform: uppercase;
    letter-spacing: .04em; color: var(--muted); margin-bottom: 5px; }
  select, input[type="date"] {
    background: var(--bg); color: var(--ink); border: 1px solid var(--line);
    border-radius: 7px; padding: 7px 9px; font-size: 14px; min-width: 150px;
  }
  .cod-row { display: flex; gap: 6px; align-items: center; }
  .cod-row span { color: var(--muted); }
  .cod-row select { min-width: 0; padding: 7px 6px; }
  .kpis { display: flex; gap: 26px; margin-left: auto; }
  .kpi .v { font-size: 22px; font-weight: 650; }
  .kpi .k { font-size: 11px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
  .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 10px; }
  table { border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; }
  th, td { padding: 8px 12px; text-align: right; white-space: nowrap; border-bottom: 1px solid var(--line); }
  thead th { position: sticky; top: 0; background: var(--surface); z-index: 1; }
  th.zone, td.zone { text-align: left; font-weight: 600; position: sticky; left: 0; background: var(--surface); }
  td.zone { background: var(--bg); }
  .grp-head { text-align: center; border-left: 2px solid var(--line); font-size: 12px; }
  .sub-head { font-size: 11px; color: var(--muted); font-weight: 500; }
  td.gw { border-left: 2px solid var(--line); }
  td.cell { cursor: pointer; }
  td.cell:hover { background: var(--accent-soft) !important; }
  tbody tr:nth-child(odd) td:not(.zone) { background: var(--group-a); }
  tbody tr.total td { font-weight: 700; border-top: 2px solid var(--line); background: var(--accent-soft); }
  tbody tr.total td.zone { background: var(--accent-soft); }
  td.sel, td.sel:hover { background: var(--sel) !important; box-shadow: inset 0 0 0 2px var(--sel-line); }
  .muted-cell { color: var(--muted); }
  .footnote { color: var(--muted); font-size: 12px; margin-top: 12px; }
  .map-row { display: flex; gap: 16px; align-items: stretch; flex-wrap: wrap; }
  /* MapLibre tile map — fills its box at any size (no projection letterboxing). */
  #map { flex: 1 1 auto; min-width: 480px; height: 720px; background: var(--surface);
    border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
  #side { flex: 0 0 320px; min-width: 280px; max-height: 720px; overflow-y: auto;
    border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; background: var(--surface); }
  #side h3 { margin: 0 0 4px; font-size: 14px; }
  #side .hint { color: var(--muted); font-size: 12px; }
  .proj { padding: 8px 0; border-bottom: 1px solid var(--line); }
  .proj .pn { font-weight: 600; }
  .proj .meta { color: var(--ink-2); font-size: 12px; margin-top: 2px; }
  .proj .meta b { color: var(--ink); font-weight: 600; }
  .cap { color: var(--muted); font-size: 12px; margin: 4px 0 10px; }
  .cap b { color: var(--ink); }
</style>
</head>
<body>
  <h1>ERCOT GIS Interconnection Queue</h1>
  <div class="sub">Report date <b id="rd"></b> · active queue only
    (terminal &amp; approved-for-sync/energization excluded) · <span id="counts"></span></div>

  <div class="controls">
    <div class="ctl">
      <label for="fuelSel">Fuel Technology</label>
      <select id="fuelSel"></select>
    </div>
    <div class="ctl">
      <label>Projected COD range (default from this month)</label>
      <div class="cod-row">
        <select id="coyMin"></select><select id="comMin"></select>
        <span>to</span>
        <select id="coyMax"></select><select id="comMax"></select>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v" id="kpiGw"></div><div class="k">Total GW (shown)</div></div>
      <div class="kpi"><div class="v" id="kpiN"></div><div class="k">Projects (shown)</div></div>
    </div>
  </div>

  <div class="table-wrap">
    <table id="tbl"><thead></thead><tbody></tbody></table>
  </div>
  <div class="footnote">
    Each milestone column counts active-queue projects that have reached that gate
    (milestone date present; Financial Security = "Yes"), filtered by the selected Fuel
    Technology and Projected COD range. Each milestone is a subset of "In Queue (Total)";
    the milestones are independent gates, not a strict funnel.
    <b>Click any capacity/count cell</b> to drive the county map below.
  </div>

  <h2>Where the generation is — Texas county map</h2>
  <div class="cap" id="mapCap"></div>
  <div class="map-row">
    <div id="map"></div>
    <div id="side">
      <h3>Projects by county</h3>
      <div class="hint">Click a county on the map to list its projects (name, capacity, COD, status).</div>
    </div>
  </div>

<script>/*__PLOTLYJS__*/</script>
<script>
const DATA = "__DATA__";
const META = "__META__";
const GEOJSON = "__GEOJSON__";

const isDark = matchMedia("(prefers-color-scheme: dark)").matches;
const fmtGw = v => v.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
const fmtN  = v => v.toLocaleString();
const KEYS = META.milestones.map(m => m[0]);
const LABEL = Object.fromEntries(META.milestones);

let sel = {zone: null, milestone: "total"};   // table selection driving the map
let selCounty = null;                          // clicked county fips
let mapWired = false;                          // attach plotly_click once

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function fillSelect(el, values, labels, value) {
  for (let i = 0; i < values.length; i++) {
    const o = document.createElement("option");
    o.value = values[i]; o.textContent = labels[i]; el.appendChild(o);
  }
  el.value = value;
}

function init() {
  document.getElementById("rd").textContent = META.reportDate;
  document.getElementById("counts").textContent =
    `${fmtN(META.nActive)} active projects (${fmtN(META.nTerminalExcluded)} excluded of ${fmtN(META.nSnapshot)})`;

  const selEl = document.getElementById("fuelSel");
  for (const o of ["All", ...META.fuelTechs]) {
    const el = document.createElement("option"); el.value = o; el.textContent = o; selEl.appendChild(el);
  }
  selEl.value = META.fuelTechs.includes("Solar PV") ? "Solar PV" : "All";

  // COD range as Month + Year dropdowns (no native date picker / horizontal year scroll)
  const yMin = +META.codMin.slice(0, 4), yMax = +META.codMax.slice(0, 4);
  const years = [], mVals = [];
  for (let y = yMin; y <= yMax; y++) years.push(y);
  for (let m = 1; m <= 12; m++) mVals.push(String(m).padStart(2, "0"));
  const monthLabels = MONTHS.slice();

  const now = new Date();
  const startY = Math.min(Math.max(now.getFullYear(), yMin), yMax);     // default start = this month
  const startM = String(now.getMonth() + 1).padStart(2, "0");

  fillSelect(document.getElementById("coyMin"), years, years, startY);
  fillSelect(document.getElementById("comMin"), mVals, monthLabels, startM);
  fillSelect(document.getElementById("coyMax"), years, years, yMax);
  fillSelect(document.getElementById("comMax"), mVals, monthLabels, META.codMax.slice(5, 7));

  buildHead();
  const ctrls = ["fuelSel", "coyMin", "comMin", "coyMax", "comMax"].map(id => document.getElementById(id));
  ctrls.forEach(e => e.addEventListener("change", () => { selCounty = null; renderAll(); }));
  renderAll();
}

function codBounds() {
  const lo = `${document.getElementById("coyMin").value}-${document.getElementById("comMin").value}`;
  const hi = `${document.getElementById("coyMax").value}-${document.getElementById("comMax").value}`;
  return [lo, hi];   // "YYYY-MM" inclusive
}

function filteredRows() {
  const fuel = document.getElementById("fuelSel").value;
  const [lo, hi] = codBounds();
  return DATA.filter(r =>
    (fuel === "All" || r.fuelTech === fuel) &&
    (!r.cod || (r.cod.slice(0, 7) >= lo && r.cod.slice(0, 7) <= hi))
  );
}

function buildHead() {
  const thead = document.querySelector("#tbl thead");
  const r1 = document.createElement("tr");
  const zt = document.createElement("th"); zt.className = "zone"; zt.rowSpan = 2;
  zt.textContent = "CDR Reporting Zone"; r1.appendChild(zt);
  for (const [, label] of META.milestones) {
    const th = document.createElement("th");
    th.className = "grp-head"; th.colSpan = 2; th.textContent = label; r1.appendChild(th);
  }
  const r2 = document.createElement("tr");
  for (const _ of META.milestones) {
    const a = document.createElement("th"); a.className = "sub-head gw"; a.textContent = "GW";
    const b = document.createElement("th"); b.className = "sub-head"; b.textContent = "#";
    r2.appendChild(a); r2.appendChild(b);
  }
  thead.appendChild(r1); thead.appendChild(r2);
}

function renderAll() {
  const rows = filteredRows();

  // zone -> milestone -> {gw, n}
  const agg = {}; const zones = [...META.zoneOrder];
  const blank = () => Object.fromEntries(KEYS.map(k => [k, {gw: 0, n: 0}]));
  const total = blank();
  for (const r of rows) {
    if (!zones.includes(r.zone)) zones.push(r.zone);
    const a = (agg[r.zone] ??= blank());
    for (const k of KEYS) if (k === "total" || r[k]) {
      a[k].gw += r.gw; a[k].n += 1; total[k].gw += r.gw; total[k].n += 1;
    }
  }

  const tbody = document.querySelector("#tbl tbody");
  tbody.innerHTML = "";
  const addRow = (zoneLabel, cells, cls, zoneKey) => {
    const tr = document.createElement("tr");
    if (cls) tr.className = cls;
    const z = document.createElement("td"); z.className = "zone"; z.textContent = zoneLabel; tr.appendChild(z);
    for (const k of KEYS) {
      const c = cells[k];
      const isSel = sel.milestone === k && sel.zone === zoneKey;
      const gw = document.createElement("td");
      gw.className = "gw cell" + (c.n ? "" : " muted-cell") + (isSel ? " sel" : "");
      gw.textContent = c.n ? fmtGw(c.gw) : "–";
      const n = document.createElement("td");
      n.className = "cell" + (c.n ? "" : " muted-cell") + (isSel ? " sel" : "");
      n.textContent = c.n ? fmtN(c.n) : "–";
      for (const td of [gw, n]) td.addEventListener("click", () => {
        sel = {zone: zoneKey, milestone: k}; selCounty = null; renderAll();
      });
      tr.appendChild(gw); tr.appendChild(n);
    }
    tbody.appendChild(tr);
  };

  for (const z of zones) if (agg[z]) addRow(z, agg[z], "", z);
  addRow("TOTAL", total, "total", null);   // zoneKey null = all zones

  document.getElementById("kpiGw").textContent = fmtGw(total.total.gw);
  document.getElementById("kpiN").textContent = fmtN(total.total.n);

  renderMap(rows);
}

function selectionRows(rows) {
  return rows.filter(r =>
    (sel.zone === null || r.zone === sel.zone) &&
    (sel.milestone === "total" || r[sel.milestone])
  );
}

function renderMap(rows) {
  const subset = selectionRows(rows);
  const zoneTxt = sel.zone === null ? "All zones" : sel.zone;
  document.getElementById("mapCap").innerHTML =
    `Showing <b>${LABEL[sel.milestone]}</b> · <b>${zoneTxt}</b> — ` +
    `${fmtN(subset.length)} projects, ${fmtGw(subset.reduce((s,r)=>s+r.gw,0))} GW ` +
    `(county-level; projects with no county are omitted from the map).`;

  // aggregate by fips
  const byF = {};
  for (const r of subset) {
    if (!r.fips) continue;
    const f = (byF[r.fips] ??= {gw: 0, n: 0, county: r.county, names: []});
    f.gw += r.gw; f.n += 1; f.names.push(`${r.name} (${fmtGw(r.gw)} GW)`);
  }
  const fips = Object.keys(byF);
  const z = fips.map(f => byF[f].gw);
  const text = fips.map(f => {
    const d = byF[f];
    const shown = d.names.slice(0, 6).join("<br>");
    const more = d.n > 6 ? `<br>+${d.n - 6} more` : "";
    return `<b>${d.county} County</b><br>${fmtGw(d.gw)} GW · ${d.n} project(s)<br>${shown}${more}`;
  });

  // MapLibre tile map (plotly `choroplethmap`): real basemap underneath, native pan/zoom,
  // fills the container at any size, and accepts extra tile layers (OpenInfraMap next).
  const border = isDark ? "#20262e" : "#b9c0ca";
  const ink    = isDark ? "#eceff3" : "#1a1d21";
  const scale = [[0, "#fff5cc"], [0.2, "#fee08b"], [0.45, "#fdae61"],
                 [0.7, "#f46d43"], [1, "#a50026"]];

  const data = {
    type: "choroplethmap", geojson: GEOJSON, featureidkey: "id",
    locations: fips, z: z, zmin: 0, text: text, hovertemplate: "%{text}<extra></extra>",
    colorscale: scale, marker: {line: {color: border, width: 0.6}, opacity: 0.8},
    colorbar: {
      title: {text: "GW"}, thickness: 10, len: 0.8, x: 1, xanchor: "right",
      xpad: 6, outlinewidth: 0, bgcolor: isDark ? "rgba(28,32,39,0.7)" : "rgba(247,248,250,0.7)",
    },
  };
  const layout = {
    map: {
      style: isDark ? "carto-darkmatter" : "carto-positron",
      center: {lon: -99.7, lat: 31.2}, zoom: 4.8,   // Texas
      layers: [{  // faint outline of ALL TX counties for context
        sourcetype: "geojson", source: GEOJSON, type: "line",
        color: border, line: {width: 0.5}, opacity: 0.5,
      }],
    },
    margin: {t: 0, b: 0, l: 0, r: 0}, paper_bgcolor: "rgba(0,0,0,0)",
    font: {color: ink},
  };
  const mapEl = document.getElementById("map");
  Plotly.react(mapEl, [data], layout, {responsive: true, displayModeBar: false, scrollZoom: true});

  if (!mapWired) {                 // attach once — react() re-renders keep the listener
    mapEl.on("plotly_click", ev => {
      selCounty = ev.points[0].location;
      renderSide(selectionRows(filteredRows()));
    });
    mapWired = true;
  }
  renderSide(subset);
}

function renderSide(subset) {
  const side = document.getElementById("side");
  if (!selCounty) {
    side.innerHTML = '<h3>Projects by county</h3><div class="hint">Click a county on the map ' +
      'to list its projects (name, capacity, COD, status).</div>';
    return;
  }
  const inC = subset.filter(r => r.fips === selCounty)
                    .sort((a, b) => b.gw - a.gw);
  const cty = inC.length ? inC[0].county : selCounty;
  const totGw = inC.reduce((s, r) => s + r.gw, 0);
  let html = `<h3>${cty} County</h3><div class="cap"><b>${fmtN(inC.length)}</b> project(s) · ` +
             `<b>${fmtGw(totGw)} GW</b></div>`;
  for (const r of inC) {
    html += `<div class="proj"><div class="pn">${r.name}</div>` +
      `<div class="meta"><b>${fmtGw(r.gw)} GW</b> · COD ${r.cod || "—"} · ${r.fuelTech}` +
      `<br>${r.status}</div></div>`;
  }
  if (!inC.length) html += '<div class="hint">No projects in this county for the current selection.</div>';
  side.innerHTML = html;
}

init();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report-date", default="latest",
                    help="fileDate snapshot (YYYY-MM-DD) or 'latest' (default)")
    ap.add_argument("--parquet", default=str(PARQUET), help="source parquet path")
    args = ap.parse_args()

    df = pd.read_parquet(args.parquet)
    records, meta = build_records(df, args.report_date)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"gis_queue_report_{meta['reportDate']}.html"
    out.write_text(render_html(records, meta), encoding="utf-8")

    print(f"report date : {meta['reportDate']}")
    print(f"active queue: {meta['nActive']} projects "
          f"({meta['nTerminalExcluded']} excluded of {meta['nSnapshot']})")
    print(f"fuel techs  : {', '.join(meta['fuelTechs'])}")
    print(f"wrote       : {out}  ({out.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
