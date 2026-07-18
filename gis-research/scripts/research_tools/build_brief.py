"""One-page HTML brief per researched project — most relevant info on top, drill-down links.

Reads findings.json + timeline.json + imagery/key/*.png + sources/ from the project dir,
writes brief.html beside them. Human reviewer scans 50-60 of these; keep it terse.

Usage:
  uv run gis-research/scripts/research_tools/build_brief.py 23INR0086
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]

CSS = """
:root{--bg:#fff;--sur:#f6f7f9;--ink:#191c20;--ink2:#555b64;--mut:#899;--line:#e1e5ea;
--good:#0a7d33;--warn:#b45309;--bad:#b91c1c;--acc:#2563eb}
@media(prefers-color-scheme:dark){:root{--bg:#14171c;--sur:#1c2027;--ink:#eceff3;
--ink2:#b3bac4;--mut:#7d8590;--line:#2a2f38;--good:#34d399;--warn:#fbbf24;--bad:#f87171;--acc:#6ea8fe}}
*{box-sizing:border-box}body{margin:0 auto;max-width:1080px;padding:20px;background:var(--bg);
color:var(--ink);font:14px/1.45 -apple-system,"Segoe UI",Roboto,sans-serif}
h1{font-size:19px;margin:0}h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;
color:var(--mut);margin:22px 0 8px}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-weight:700;font-size:12px}
.b-good{background:color-mix(in srgb,var(--good) 15%,transparent);color:var(--good)}
.b-warn{background:color-mix(in srgb,var(--warn) 15%,transparent);color:var(--warn)}
.b-bad{background:color-mix(in srgb,var(--bad) 15%,transparent);color:var(--bad)}
.hdr{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
.sub{color:var(--ink2);font-size:13px;margin:4px 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:10px}
.card{background:var(--sur);border:1px solid var(--line);border-radius:9px;padding:10px 13px}
.card .k{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--mut)}
.card .v{font-weight:650;margin-top:2px}.card .v small{font-weight:400;color:var(--ink2)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{padding:5px 10px;text-align:left;border-bottom:1px solid var(--line);font-size:13px}
th{color:var(--mut);font-size:11px;text-transform:uppercase}
.imgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:8px}
.imgs figure{margin:0}.imgs img{width:100%;border-radius:8px;border:1px solid var(--line)}
.imgs figcaption{font-size:12px;color:var(--ink2);margin-top:2px}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
ul{margin:6px 0;padding-left:20px}li{margin:3px 0}
.small{font-size:12px;color:var(--ink2)}
"""

VERDICT_CLASS = {"real_active": "b-good", "real_early": "b-warn", "paper": "b-bad", "unclear": "b-warn"}
RISK_CLASS = {"low": "b-good", "med": "b-warn", "medium": "b-warn", "high": "b-bad"}


def esc(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def build(proj_dir: Path) -> Path:
    f = json.loads((proj_dir / "findings.json").read_text())
    tl = json.loads((proj_dir / "timeline.json").read_text()) if (proj_dir / "timeline.json").exists() else None

    site = f.get("site", {})
    lat, lon = site.get("lat"), site.get("lon")
    gmaps = f"https://www.google.com/maps/@{lat},{lon},5000m/data=!3m1!1e3" if lat else "#"
    con = f.get("construction", {})
    cod = f.get("cod_assessment", {})
    verdict = f.get("real_project_verdict", "unclear")

    chain = " → ".join(e["entity"] for e in f.get("llc_chain", [])) or "unknown"

    # key imagery: prefer imagery/key/, fallback to any s2_*.png (latest 4)
    key_dir = proj_dir / "imagery" / "key"
    frames = sorted(key_dir.glob("s2_*.png")) if key_dir.exists() else sorted((proj_dir / "imagery").glob("s2_*.png"))[-4:]

    src_files = sorted((proj_dir / "sources").glob("*")) if (proj_dir / "sources").exists() else []

    cod_hist = ""
    if tl:
        rows = "".join(f"<tr><td>{esc(r['value'])}</td><td>{esc(r['from'])}</td><td>{esc(r['to'])}</td></tr>"
                       for r in tl.get("reported_cod_history", []))
        mrows = "".join(f"<tr><td>{esc(m['milestone'])}</td><td>{esc(m['achieved'])}</td></tr>"
                        for m in tl.get("milestones", []) if m.get("achieved"))
        cod_hist = f"""
<h2>Reported-COD drift (queue history, {esc(tl.get('snapshots'))} monthly reports since {esc(tl.get('first_seen_in_reports'))})</h2>
<table><tr><th>Reported COD</th><th>Held from</th><th>Until</th></tr>{rows}</table>
<h2>Milestones achieved (latest report)</h2>
<table><tr><th>Milestone</th><th>Date</th></tr>{mrows}</table>"""

    # contractual schedule from the signed IA (if researched)
    cs = f.get("contractual_schedule")
    cs_html = ""
    if cs:
        cols = [k for k in cs["milestones"][0] if k != "name"]
        head = "".join(f"<th>{esc(c.replace('_', ' '))}</th>" for c in cols)
        rows = "".join("<tr><td>" + esc(m["name"]) + "</td>" +
                       "".join(f"<td>{esc(m.get(c))}</td>" for c in cols) + "</tr>"
                       for m in cs["milestones"])
        docs = " · ".join(f'<a href="{esc(u)}">{esc(Path(u).name)}</a>' for u in cs.get("source_docs", []))
        cs_html = (f"<h2>Contractual schedule (from the signed IA)</h2>"
                   f"<table><tr><th>Milestone</th>{head}</tr>{rows}</table>"
                   f'<div class="small">{esc(cs.get("note",""))}<br>Source: {docs}</div>')

    ev_items = []
    for e in con.get("evidence", [])[:4] + cod.get("reasoning_evidence", [])[:3]:
        ev_items.append(f"<li>{esc(e)}</li>")

    # sources grouped: documents (pdf) first, then web captures, then extracts
    groups = [("Documents", [p for p in src_files if p.suffix == ".pdf"]),
              ("Web captures", [p for p in src_files if p.suffix in (".html", ".htm")]),
              ("Extracted pages/images", [p for p in src_files if p.suffix == ".png"]),
              ("Other", [p for p in src_files if p.suffix not in (".pdf", ".html", ".htm", ".png")])]
    src_items = "".join(
        f"<h3 class='small'>{name} ({len(fs)})</h3><ul>" +
        "".join(f'<li><a href="sources/{esc(p.name)}">{esc(p.name)}</a></li>' for p in fs) + "</ul>"
        for name, fs in groups if fs)

    imgs = "".join(
        f'<figure><a href="{p.relative_to(proj_dir)}"><img src="{p.relative_to(proj_dir)}" loading="lazy"></a>'
        f"<figcaption>{esc(p.stem.replace('s2_',''))}</figcaption></figure>"
        for p in frames)

    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(f.get('project'))} — research brief</title><style>{CSS}</style></head><body>
<div class="hdr"><h1>{esc(f.get('project'))} <span class="small">({esc(f.get('inr'))})</span></h1>
<span class="badge {VERDICT_CLASS.get(verdict,'b-warn')}">{esc(verdict)}</span>
<span class="badge {RISK_CLASS.get(cod.get('drift_risk'),'b-warn')}">COD drift: {esc(cod.get('drift_risk'))}</span></div>
<div class="sub">researched {esc(f.get('researched_at'))} ·
<a href="{gmaps}" target="_blank">site {esc(lat)}, {esc(lon)}</a> ({esc(site.get('method'))}, {esc(site.get('confidence'))} conf) ·
<a href="dossier.md">dossier</a> · <a href="log.md">log</a> · <a href="timeline.md">timeline</a></div>
<div class="grid">
<div class="card"><div class="k">Construction</div><div class="v">{esc(con.get('verdict'))}
<small>since {esc(con.get('first_activity_seen'))}</small></div></div>
<div class="card"><div class="k">COD reported → independent</div>
<div class="v">{esc(cod.get('reported'))} → {esc(cod.get('independent'))}</div></div>
<div class="card"><div class="k">Owner chain</div><div class="v">{esc(chain)}</div></div>
<div class="card"><div class="k">Land</div><div class="v">{esc(f.get('land_tenure',{}).get('status'))}</div></div>
</div>
<h2>Site imagery (Sentinel-2, key dates)</h2><div class="imgs">{imgs}</div>
{cs_html}
{cod_hist}
<h2>Key evidence</h2><ul>{''.join(ev_items)}</ul>
<h2>Saved sources ({len(src_files)})</h2>{src_items}
</body></html>"""
    out = proj_dir / "brief.html"
    out.write_text(page)
    print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB, {len(frames)} images, {len(src_files)} sources)")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inr")
    a = ap.parse_args()
    hits = sorted((BASE / "research").glob(f"{a.inr}_*"))
    if not hits:
        raise SystemExit(f"no research dir matching {a.inr}_*")
    build(hits[0])


if __name__ == "__main__":
    main()
