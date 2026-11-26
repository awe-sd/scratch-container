"""Build a self-contained interactive HTML map of ERCOT data-center load additions.

Source: `data/Large_loads_grouped_High_dispatchable.csv` — one row per
(data-center project x development phase / LoadID). Each row carries the new MW
being added (`NewLoad`), the existing/old MW at that bus (`OldLoad`), an expected
online date, voltage, crypto/non-crypto flag, dispatchability, and SSWG/NMMS bus
identifiers.

The CSV has no geography, so we join each row's `BusID (SSWG)` to the ERCOT data
dictionary (`AW.dbo.ercotDataDictionary`, latest monthly snapshot) on
`SswgBusNumber` to get `PlanningBusCounty`. That county join is the authoritative
source (verified against project names: Rockdale->Milam, Pecos->Reeves,
Odessa->Ector, McCamey->Upton, Abilene->Taylor). The CSV's own NmmsStation*/
weather-zone columns are unreliable and are NOT used for geography.

Buses absent from the snapshot (currently 909 CoreScientific/Denton and
6230 Lancium/Abilene) are patched from `data/missing_bus_counties.csv` — fill its
`County` column and re-run. Rows still lacking a county are listed in a banner and
omitted from the choropleth.

County -> FIPS via `assets/tx_county_fips.json`; the map reuses the same MapLibre
TX-county choropleth + inlined assets as `build_queue_report.py`. All
filtering/aggregation is client-side (no server).

Layout (map-centric):
  - Control bar: Crypto/Non-Crypto, Dispatchable, kV dropdowns; Online-Date range
    (Month/Year from-to); KPIs (Total New MW, Total Old MW, # Projects, # Counties).
  - Map: TX county choropleth colored by summed New MW; hover = county + New MW +
    project count + top names. Click a county -> side table of its projects
    (New MW vs Old MW, online date, kV, crypto, dispatchable).

Read-only. Run from repo root (so uv resolves awconnect):
  uv run gis-research/scripts/build_datacenter_report.py
"""

from __future__ import annotations

import argparse
import csv as csvmod
import json
from pathlib import Path

import pandas as pd

import awconnect
from awconnect import db

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data" / "Large_loads_grouped_High_dispatchable.csv"
PATCH = BASE / "data" / "missing_bus_counties.csv"
ASSETS = BASE / "assets"
OUT_DIR = BASE / "output"


def _norm_county(s: str) -> str:
    return "".join(ch for ch in str(s).upper() if ch.isalnum())


def _clean(v) -> str | None:
    """Strip a cell to a clean string, or None if blank/NaN."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip()
    return s or None


def _num(v) -> float:
    return 0.0 if pd.isna(v) else float(v)


def load_county_map(snapshot: str) -> tuple[dict[int, str], str]:
    """Return ({SswgBusNumber -> PlanningBusCounty}, snapshot_date) for a snapshot.

    snapshot='latest' resolves to MAX(fileDateMonth).
    """
    awconnect.configure("read_only")
    if snapshot == "latest":
        snapshot = str(
            db.getDfFromAwDb("SELECT MAX(fileDateMonth) AS m FROM dbo.ercotDataDictionary")["m"].iloc[0]
        )[:10]
    edd = db.getDfFromAwDb(
        f"""SELECT SswgBusNumber, PlanningBusCounty
            FROM dbo.ercotDataDictionary
            WHERE fileDateMonth = '{snapshot}' AND PlanningBusCounty IS NOT NULL"""
    )
    edd = edd.drop_duplicates("SswgBusNumber")
    return dict(zip(edd["SswgBusNumber"].astype(int), edd["PlanningBusCounty"])), snapshot


def load_patch() -> dict[int, str]:
    """{BusID_SSWG -> County} from the manual patch file, blanks skipped."""
    out: dict[int, str] = {}
    if not PATCH.exists():
        return out
    with PATCH.open(newline="") as fh:
        for row in csvmod.DictReader(fh):
            # Uppercase to match the dictionary's county style (e.g. "Taylor" ->
            # "TAYLOR", "San Patricio" -> "SAN PATRICIO") so display names don't split.
            county = (row.get("County") or "").strip().upper()
            bid = (row.get("BusID_SSWG") or "").strip()
            if county and bid:
                out[int(float(bid))] = county
    return out


def build_records(snapshot: str) -> tuple[list[dict], dict]:
    df = pd.read_csv(CSV)
    df.columns = [c.strip() for c in df.columns]

    county_by_bus, snapshot_date = load_county_map(snapshot)
    patch = load_patch()
    name2fips = json.loads((ASSETS / "tx_county_fips.json").read_text())

    records: list[dict] = []
    pending: list[str] = []
    unmatched_counties: set[str] = set()

    for _, row in df.iterrows():
        bid = row["BusID (SSWG)"]
        bid = int(bid) if pd.notna(bid) else None
        # The manual patch WINS over the dictionary — it covers both buses absent
        # from the snapshot AND buses the dictionary mislocates (e.g. 6235
        # ABMULCW7A resolves to Jones in the dictionary but is really Taylor).
        county = None
        source = None
        if bid is not None and bid in patch:
            county, source = patch[bid], "manual"
        elif bid is not None:
            county = county_by_bus.get(bid)
            source = "dictionary" if county else None
        fips = name2fips.get(_norm_county(county)) if county else None
        if county and not fips:
            unmatched_counties.add(county)

        online = _clean(row["Online Date"])
        if online and len(online) >= 10:
            online = online[:10]

        rec = {
            "name": _clean(row["Data Center Name"]) or f"bus {bid}",
            "county": county,
            "fips": fips,
            "countySource": source if county else None,
            "newLoad": round(_num(row["NewLoad"]), 1),
            "oldLoad": round(_num(row["OldLoad"]), 1),
            "maxMw": round(_num(row["Max MW"]), 1),
            "expectedMw": round(_num(row["Expected MW"]), 1),
            "damMw": round(_num(row["DAM MW"]), 1),
            "online": online,
            "kv": _clean(row["kV"]),
            "crypto": _clean(row["Crypto/Non-Crypto"]),
            "dispatchable": _clean(row["Dispatchable"]),
            "busName": _clean(row["BusName (SSWG)"]),
            "busId": bid,
            "loadId": _clean(row["LoadID"]),
        }
        records.append(rec)
        if not county:
            pending.append(rec["name"])

    if unmatched_counties:
        print(f"WARNING: {len(unmatched_counties)} counties had no FIPS match "
              f"(omitted from map): {sorted(unmatched_counties)}")

    onl = sorted(r["online"][:7] for r in records if r["online"])
    kvs = sorted({r["kv"] for r in records if r["kv"]},
                 key=lambda x: (float(x) if x.replace(".", "").isdigit() else 1e9, x))
    meta = {
        "snapshotDate": snapshot_date,
        "nProjects": len(records),
        "nMapped": sum(1 for r in records if r["fips"]),
        "nCounties": len({r["fips"] for r in records if r["fips"]}),
        "nManual": sum(1 for r in records if r["countySource"] == "manual"),
        "pending": pending,
        "totalNew": round(sum(r["newLoad"] for r in records), 1),
        "totalOld": round(sum(r["oldLoad"] for r in records), 1),
        "onlineMin": onl[0] if onl else None,
        "onlineMax": onl[-1] if onl else None,
        "cryptoTypes": sorted({r["crypto"] for r in records if r["crypto"]}),
        "kvs": kvs,
        "dispatchables": sorted({r["dispatchable"] for r in records if r["dispatchable"]}),
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
<title>ERCOT Data Center Load Additions</title>
<style>
  :root {
    --bg: #ffffff; --surface: #f7f8fa; --ink: #1a1d21; --ink-2: #545a63;
    --muted: #8a919c; --line: #e2e6ec; --accent: #2563eb; --accent-soft: #eef3ff;
    --sel: #ffe9b3; --sel-line: #e0a800; --warn: #fff4e5; --warn-line: #f0b429;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #14171c; --surface: #1c2027; --ink: #eceff3; --ink-2: #b3bac4;
      --muted: #7d8590; --line: #2a2f38; --accent: #6ea8fe; --accent-soft: #1e2633;
      --sel: #4a3a12; --sel-line: #e0a800; --warn: #2c2410; --warn-line: #a9812a;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0 auto; padding: 24px; max-width: 1280px; background: var(--bg); color: var(--ink);
    font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  h1 { font-size: 20px; margin: 0 0 2px; }
  h2 { font-size: 15px; margin: 26px 0 10px; }
  .sub { color: var(--ink-2); font-size: 13px; margin-bottom: 14px; }
  .sub b { color: var(--ink); }
  .banner { background: var(--warn); border: 1px solid var(--warn-line); border-radius: 8px;
    padding: 9px 13px; margin-bottom: 16px; font-size: 12.5px; color: var(--ink); }
  .banner b { font-weight: 650; }
  .controls {
    display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end;
    background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px 18px; margin-bottom: 18px;
  }
  .ctl label { display: block; font-size: 11px; text-transform: uppercase;
    letter-spacing: .04em; color: var(--muted); margin-bottom: 5px; }
  select {
    background: var(--bg); color: var(--ink); border: 1px solid var(--line);
    border-radius: 7px; padding: 7px 9px; font-size: 14px; min-width: 140px;
  }
  .cod-row { display: flex; gap: 6px; align-items: center; }
  .cod-row span { color: var(--muted); }
  .cod-row select { min-width: 0; padding: 7px 6px; }
  .kpis { display: flex; gap: 24px; margin-left: auto; }
  .kpi .v { font-size: 22px; font-weight: 650; }
  .kpi .k { font-size: 11px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }
  .footnote { color: var(--muted); font-size: 12px; margin-top: 12px; }
  .map-row { display: flex; gap: 16px; align-items: stretch; flex-wrap: wrap; }
  #map { flex: 1 1 auto; min-width: 480px; height: 720px; background: var(--surface);
    border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
  #side { flex: 0 0 340px; min-width: 300px; max-height: 720px; overflow-y: auto;
    border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; background: var(--surface); }
  #side h3 { margin: 0 0 4px; font-size: 14px; }
  #side .hint { color: var(--muted); font-size: 12px; }
  .cap { color: var(--muted); font-size: 12px; margin: 4px 0 10px; }
  .cap b { color: var(--ink); }
  .proj { padding: 9px 0; border-bottom: 1px solid var(--line); }
  .proj .pn { font-weight: 600; }
  .mw { display: flex; gap: 14px; margin: 4px 0 2px; }
  .mw .box { font-size: 12px; }
  .mw .box .n { font-size: 15px; font-weight: 650; }
  .mw .new .n { color: #2f9e44; } .mw .old .n { color: var(--ink-2); }
  @media (prefers-color-scheme: dark) { .mw .new .n { color: #51cf66; } }
  .mw .k { color: var(--muted); font-size: 10.5px; text-transform: uppercase; letter-spacing: .03em; }
  .proj .meta { color: var(--ink-2); font-size: 12px; margin-top: 2px; }
  .proj .meta b { color: var(--ink); font-weight: 600; }
  .tag { display: inline-block; font-size: 10.5px; padding: 1px 6px; border-radius: 5px;
    background: var(--accent-soft); color: var(--accent); margin-left: 4px; }
</style>
</head>
<body>
  <h1>ERCOT Data Center Load Additions</h1>
  <div class="sub">County via <b>ercotDataDictionary</b> snapshot <b id="snap"></b>
    (<code>BusID (SSWG) &rarr; SswgBusNumber &rarr; PlanningBusCounty</code>) ·
    <span id="counts"></span></div>
  <div class="banner" id="banner" style="display:none"></div>

  <div class="controls">
    <div class="ctl"><label for="cryptoSel">Crypto / Non-Crypto</label><select id="cryptoSel"></select></div>
    <div class="ctl"><label for="dispSel">Dispatchable</label><select id="dispSel"></select></div>
    <div class="ctl"><label for="kvSel">Voltage (kV)</label><select id="kvSel"></select></div>
    <div class="ctl">
      <label>Online Date range</label>
      <div class="cod-row">
        <select id="oyMin"></select><select id="omMin"></select>
        <span>to</span>
        <select id="oyMax"></select><select id="omMax"></select>
      </div>
    </div>
    <div class="kpis">
      <div class="kpi"><div class="v" id="kpiNew"></div><div class="k">New MW (shown)</div></div>
      <div class="kpi"><div class="v" id="kpiOld"></div><div class="k">Old MW (shown)</div></div>
      <div class="kpi"><div class="v" id="kpiN"></div><div class="k">Projects</div></div>
      <div class="kpi"><div class="v" id="kpiC"></div><div class="k">Counties</div></div>
    </div>
  </div>

  <h2>Where data centers are being added — Texas county map</h2>
  <div class="cap" id="mapCap"></div>
  <div class="map-row">
    <div id="map"></div>
    <div id="side">
      <h3>Projects by county</h3>
      <div class="hint">Click a county on the map to list its projects (New MW vs Old MW, online date, kV, type).</div>
    </div>
  </div>
  <div class="footnote" id="foot"></div>

<script>/*__PLOTLYJS__*/</script>
<script>
const DATA = "__DATA__";
const META = "__META__";
const GEOJSON = "__GEOJSON__";

const isDark = matchMedia("(prefers-color-scheme: dark)").matches;
const fmtMw = v => v.toLocaleString(undefined, {maximumFractionDigits: 0});
const fmtN  = v => v.toLocaleString();
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

let selCounty = null;      // clicked county fips
let mapWired = false;

function fillSelect(el, values, labels, value) {
  for (let i = 0; i < values.length; i++) {
    const o = document.createElement("option");
    o.value = values[i]; o.textContent = labels[i]; el.appendChild(o);
  }
  if (value !== undefined) el.value = value;
}

function init() {
  document.getElementById("snap").textContent = META.snapshotDate;
  document.getElementById("counts").textContent =
    `${fmtN(META.nProjects)} project rows · ${fmtN(META.nMapped)} mapped across ` +
    `${fmtN(META.nCounties)} counties · ${fmtMw(META.totalNew)} MW new / ${fmtMw(META.totalOld)} MW old (all)`;

  if (META.pending && META.pending.length) {
    const b = document.getElementById("banner");
    b.style.display = "";
    b.innerHTML = `<b>${META.pending.length} project(s) pending a county</b> (bus not in the ` +
      `${META.snapshotDate} dictionary snapshot) — fill <code>data/missing_bus_counties.csv</code> ` +
      `and re-run to map them: ${META.pending.join(", ")}.`;
  }

  fillSelect(document.getElementById("cryptoSel"),
    ["All", ...META.cryptoTypes], ["All", ...META.cryptoTypes], "All");
  fillSelect(document.getElementById("dispSel"),
    ["All", ...META.dispatchables], ["All", ...META.dispatchables], "All");
  fillSelect(document.getElementById("kvSel"),
    ["All", ...META.kvs], ["All", ...META.kvs.map(k => k + " kV")], "All");

  // Online-Date range as Month + Year dropdowns (default = full range)
  const yMin = +META.onlineMin.slice(0, 4), yMax = +META.onlineMax.slice(0, 4);
  const years = []; for (let y = yMin; y <= yMax; y++) years.push(y);
  const mVals = []; for (let m = 1; m <= 12; m++) mVals.push(String(m).padStart(2, "0"));
  fillSelect(document.getElementById("oyMin"), years, years, yMin);
  fillSelect(document.getElementById("omMin"), mVals, MONTHS, META.onlineMin.slice(5, 7));
  fillSelect(document.getElementById("oyMax"), years, years, yMax);
  fillSelect(document.getElementById("omMax"), mVals, MONTHS, META.onlineMax.slice(5, 7));

  document.getElementById("foot").innerHTML =
    `Choropleth color = <b>summed New MW</b> being added per county. County joins verified against ` +
    `project names; the CSV's own station/weather-zone columns are not used for geography. ` +
    (META.nManual ? `${META.nManual} county assigned manually. ` : "") +
    `Projects without a county are omitted from the map. <b>Click a county</b> for its project list.`;

  ["cryptoSel","dispSel","kvSel","oyMin","omMin","oyMax","omMax"]
    .forEach(id => document.getElementById(id).addEventListener("change", () => { selCounty = null; renderAll(); }));
  renderAll();
}

function onlineBounds() {
  const lo = `${document.getElementById("oyMin").value}-${document.getElementById("omMin").value}`;
  const hi = `${document.getElementById("oyMax").value}-${document.getElementById("omMax").value}`;
  return [lo, hi];
}

function filteredRows() {
  const crypto = document.getElementById("cryptoSel").value;
  const disp = document.getElementById("dispSel").value;
  const kv = document.getElementById("kvSel").value;
  const [lo, hi] = onlineBounds();
  return DATA.filter(r =>
    (crypto === "All" || r.crypto === crypto) &&
    (disp === "All" || r.dispatchable === disp) &&
    (kv === "All" || r.kv === kv) &&
    (!r.online || (r.online.slice(0, 7) >= lo && r.online.slice(0, 7) <= hi))
  );
}

function renderAll() {
  const rows = filteredRows();
  const mapped = rows.filter(r => r.fips);
  document.getElementById("kpiNew").textContent = fmtMw(rows.reduce((s, r) => s + r.newLoad, 0));
  document.getElementById("kpiOld").textContent = fmtMw(rows.reduce((s, r) => s + r.oldLoad, 0));
  document.getElementById("kpiN").textContent = fmtN(rows.length);
  document.getElementById("kpiC").textContent = fmtN(new Set(mapped.map(r => r.fips)).size);
  renderMap(mapped);
}

function renderMap(mapped) {
  document.getElementById("mapCap").innerHTML =
    `${fmtN(mapped.length)} mapped project(s) · <b>${fmtMw(mapped.reduce((s,r)=>s+r.newLoad,0))} MW</b> new ` +
    `(county-level; projects with no county omitted).`;

  const byF = {};
  for (const r of mapped) {
    const f = (byF[r.fips] ??= {new: 0, old: 0, n: 0, county: r.county, names: []});
    f.new += r.newLoad; f.old += r.oldLoad; f.n += 1;
    f.names.push({name: r.name, mw: r.newLoad});
  }
  const fips = Object.keys(byF);
  const z = fips.map(f => byF[f].new);
  const text = fips.map(f => {
    const d = byF[f];
    d.names.sort((a, b) => b.mw - a.mw);
    const shown = d.names.slice(0, 6).map(x => `${x.name} (+${fmtMw(x.mw)} MW)`).join("<br>");
    const more = d.n > 6 ? `<br>+${d.n - 6} more` : "";
    return `<b>${d.county} County</b><br>+${fmtMw(d.new)} MW new · ${fmtMw(d.old)} MW old · ${d.n} project(s)<br>${shown}${more}`;
  });

  const border = isDark ? "#20262e" : "#b9c0ca";
  const ink    = isDark ? "#eceff3" : "#1a1d21";
  const scale = [[0, "#e8f5e9"], [0.2, "#a5d6a7"], [0.45, "#66bb6a"],
                 [0.7, "#2e9e44"], [1, "#1b5e20"]];

  const data = {
    type: "choroplethmap", geojson: GEOJSON, featureidkey: "id",
    locations: fips, z: z, zmin: 0, text: text, hovertemplate: "%{text}<extra></extra>",
    colorscale: scale, marker: {line: {color: border, width: 0.6}, opacity: 0.85},
    colorbar: {
      title: {text: "New MW"}, thickness: 10, len: 0.8, x: 1, xanchor: "right",
      xpad: 6, outlinewidth: 0, bgcolor: isDark ? "rgba(28,32,39,0.7)" : "rgba(247,248,250,0.7)",
    },
  };
  const layout = {
    map: {
      style: isDark ? "carto-darkmatter" : "carto-positron",
      center: {lon: -98.5, lat: 31.3}, zoom: 4.7,
      layers: [{ sourcetype: "geojson", source: GEOJSON, type: "line",
        color: border, line: {width: 0.5}, opacity: 0.5 }],
    },
    margin: {t: 0, b: 0, l: 0, r: 0}, paper_bgcolor: "rgba(0,0,0,0)", font: {color: ink},
  };
  const mapEl = document.getElementById("map");
  Plotly.react(mapEl, [data], layout, {responsive: true, displayModeBar: false, scrollZoom: true});

  if (!mapWired) {
    mapEl.on("plotly_click", ev => { selCounty = ev.points[0].location; renderSide(); });
    mapWired = true;
  }
  renderSide();
}

function renderSide() {
  const side = document.getElementById("side");
  if (!selCounty) {
    side.innerHTML = '<h3>Projects by county</h3><div class="hint">Click a county on the map ' +
      'to list its projects (New MW vs Old MW, online date, kV, type).</div>';
    return;
  }
  const inC = filteredRows().filter(r => r.fips === selCounty).sort((a, b) => b.newLoad - a.newLoad);
  const cty = inC.length ? inC[0].county : selCounty;
  const totNew = inC.reduce((s, r) => s + r.newLoad, 0);
  const totOld = inC.reduce((s, r) => s + r.oldLoad, 0);
  let html = `<h3>${cty} County</h3><div class="cap"><b>${fmtN(inC.length)}</b> project(s) · ` +
             `<b>+${fmtMw(totNew)} MW</b> new · ${fmtMw(totOld)} MW old</div>`;
  for (const r of inC) {
    const tags = [r.crypto, r.dispatchable === "YES" ? "Dispatchable" : null, r.kv ? r.kv + " kV" : null]
      .filter(Boolean).map(t => `<span class="tag">${t}</span>`).join("");
    html += `<div class="proj"><div class="pn">${r.name}${tags}</div>` +
      `<div class="mw"><div class="box new"><div class="n">+${fmtMw(r.newLoad)}</div><div class="k">New MW</div></div>` +
      `<div class="box old"><div class="n">${fmtMw(r.oldLoad)}</div><div class="k">Old MW</div></div></div>` +
      `<div class="meta">Online <b>${r.online || "—"}</b> · bus ${r.busName || r.busId || "—"}</div></div>`;
  }
  if (!inC.length) html += '<div class="hint">No projects in this county for the current filters.</div>';
  side.innerHTML = html;
}

init();
</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--snapshot", default="latest",
                    help="ercotDataDictionary fileDateMonth (YYYY-MM-DD) or 'latest' (default)")
    args = ap.parse_args()

    records, meta = build_records(args.snapshot)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"datacenter_load_map_{meta['snapshotDate']}.html"
    out.write_text(render_html(records, meta), encoding="utf-8")

    print(f"snapshot     : {meta['snapshotDate']}")
    print(f"projects     : {meta['nProjects']} rows, {meta['nMapped']} mapped, "
          f"{meta['nCounties']} counties ({meta['nManual']} manual)")
    if meta["pending"]:
        print(f"pending county: {', '.join(meta['pending'])}")
    print(f"new / old MW : {meta['totalNew']:.0f} / {meta['totalOld']:.0f}")
    print(f"wrote        : {out}  ({out.stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
