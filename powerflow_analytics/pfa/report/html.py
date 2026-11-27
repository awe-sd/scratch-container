"""The one HTML toolkit: page shell, sections, notes, column-spec tables with filter/sort, Plotly figure blocks."""
from __future__ import annotations

import html as _html
from dataclasses import dataclass
from typing import Any, Callable, Iterable

import pandas as pd

CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:2rem auto;max-width:1400px;color:#1a1a2e;background:#fafafa}
h1{font-size:1.3rem} h2{font-size:1.1rem;margin-top:2rem} h3{font-size:1rem}
.meta,.note{color:#444;font-size:.88rem;max-width:75rem;line-height:1.45}
.generated{color:#777;font-size:.8rem;margin-bottom:1rem}
.warning{background:#fff3cd;border-left:4px solid #e0a800;padding:.5rem .8rem;font-size:.9rem;max-width:75rem;margin:.8rem 0}
table.t{border-collapse:collapse;font-size:.8rem;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.12);margin-top:.6rem}
table.t th,table.t td{border:1px solid #ddd;padding:3px 7px;text-align:right;white-space:nowrap}
table.t th{background:#22304a;color:#fff;position:sticky;top:0}
table.t td.l,table.t th.l{text-align:left}
table.t tbody tr:nth-child(even){background:#f4f6fa}
table.t tr.hi td{background:#fff8e1;font-weight:600}
table.t input.f{width:95%;font-size:.72rem;box-sizing:border-box}
table.t th.s{cursor:pointer}
pre{white-space:pre-wrap;font-size:.85rem;max-width:75rem}
"""

JS = """
function pfaFilter(t){const ins=[...t.querySelectorAll('input.f')];
[...t.tBodies[0].rows].forEach(r=>{let ok=true;ins.forEach((inp,i)=>{const v=inp.value.trim().toLowerCase();if(!v)return;
const cell=r.cells[i].innerText.trim();const num=parseFloat(cell.replace(/,/g,''));
if(v[0]==='>'&&!isNaN(num)){if(!(num>parseFloat(v.slice(1))))ok=false}
else if(v[0]==='<'&&!isNaN(num)){if(!(num<parseFloat(v.slice(1))))ok=false}
else if(!cell.toLowerCase().includes(v))ok=false;});r.style.display=ok?'':'none';});}
function pfaSort(t,i){const b=t.tBodies[0];const d=t.dataset.sd=(t.dataset.sc==i&&t.dataset.sd==='1')?'-1':'1';t.dataset.sc=i;
const k=r=>{const c=r.cells[i].innerText.trim();const n=parseFloat(c.replace(/,/g,''));return isNaN(n)?c.toLowerCase():n};
[...b.rows].sort((a,c)=>{const x=k(a),y=k(c);return (x>y?1:x<y?-1:0)*d}).forEach(r=>b.appendChild(r));}
"""

_counter = {"n": 0}


def esc(v: Any) -> str:
    """HTML-escape any value (quotes included)."""
    return _html.escape(str(v), quote=True)


def fmt(v: Any, kind: str = "text") -> str:
    """Cell text for a value: ids are never comma-formatted; missing values are empty except under 'auto' (pandas-like)."""
    if kind == "auto":
        if v is None:
            return "None"
        if isinstance(v, (bool,)) or type(v).__name__ == "bool_":
            return "True" if v else "False"
        if isinstance(v, (float,)) or type(v).__name__.startswith("float"):
            return "NaN" if pd.isna(v) else f"{float(v):.4g}"
        return str(v)
    if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NA or v is pd.NaT:
        return ""
    if kind == "int":
        return f"{int(v):,}"
    if kind == "num1":
        return f"{float(v):.1f}"
    if kind == "num2":
        return f"{float(v):.2f}"
    if kind == "num3":
        return f"{float(v):.3f}"
    if kind == "money":
        return f"{round(float(v)):,}"
    if kind == "bool":
        return "True" if v else "False"
    return str(v)  # text, id


@dataclass(frozen=True)
class Col:
    """One table column: header, a column name or accessor(row), number format, alignment ('l' or 'r')."""
    header: str
    key: str | Callable[[Any], Any]
    fmt: str = "text"
    align: str = "r"

    def value(self, row) -> Any:
        return self.key(row) if callable(self.key) else row[self.key]


def auto_cols(df: pd.DataFrame, columns: Iterable[str] | None = None) -> list[Col]:
    """Columns taken straight from a frame (pandas-like text), restricted to those present in `columns`."""
    names = [c for c in (columns if columns is not None else df.columns) if c in df.columns]
    return [Col(str(c), c, "auto", "l" if df[c].dtype == object else "r") for c in names]


def page(title: str, body: str, *, generated: str | None = None, extra_css: str = "", with_js: bool = True) -> str:
    """Full HTML document: consistent CSS, title/h1 is the caller's first body block, optional generated-at line."""
    gen = f'<div class="generated">Generated {esc(generated)}</div>' if generated else ""
    js = f"<script>{JS}</script>" if with_js else ""
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{CSS}{extra_css}</style>{js}</head><body>\n<h1>{esc(title)}</h1>{gen}\n{body}\n</body></html>")


def heading(text: str, level: int = 2) -> str:
    return f"<h{level}>{esc(text)}</h{level}>"


def section(title: str, *blocks: str, level: int = 2) -> str:
    return f"{heading(title, level)}\n" + "\n".join(b for b in blocks if b)


def paragraph(html: str, cls: str = "note") -> str:
    """A text block; `html` is trusted markup (escape dynamic text with esc())."""
    return f'<div class="{cls}">{html}</div>'


def note(html: str) -> str:
    return paragraph(html, "note")


def warning(html: str) -> str:
    return paragraph(html, "warning")


def preformatted(text: str) -> str:
    return f"<pre>{esc(text)}</pre>"


def table(data: pd.DataFrame, cols: list[Col], *, filter_row: bool = True, sortable: bool = True,
          row_class: Callable[[Any], str] | None = None, empty: str = "none") -> str:
    """Table from a column spec; no rows still renders the header (so the table set stays stable), data=None renders the `empty` note.
    Filter inputs accept text, or >/< on numbers; header click sorts."""
    if data is None:
        return f'<div class="note">{esc(empty)}</div>'
    _counter["n"] += 1
    tid = f"t{_counter['n']}"
    cls = lambda c: ' class="l"' if c.align == "l" else ""

    def head_attr(i, c):
        if not sortable:
            return cls(c)
        return f' class="s{" l" if c.align == "l" else ""}" onclick="pfaSort(this.closest(\'table\'),{i})"'

    head = "".join(f"<th{head_attr(i, c)}>{esc(c.header)}</th>" for i, c in enumerate(cols))
    filt = ""
    if filter_row:
        filt = "<tr>" + "".join(f"<th{cls(c)}><input class='f' oninput='pfaFilter(this.closest(\"table\"))'></th>" for c in cols) + "</tr>"
    body = []
    for row in data.to_dict("records"):
        rc = row_class(row) if row_class else ""
        cells = "".join(f"<td{cls(c)}>{esc(fmt(c.value(row), c.fmt))}</td>" for c in cols)
        rattr = f' class="{esc(rc)}"' if rc else ""
        body.append(f"<tr{rattr}>{cells}</tr>")
    return (f'<table class="t" id="{tid}"><thead><tr>{head}</tr>{filt}</thead>'
            f'<tbody>{"".join(body)}</tbody></table>')


def figure(fig, plotlyjs: bool | str = True) -> str:
    """Plotly figure as an embeddable block (plotlyjs: True embeds the library, 'cdn' links it)."""
    return fig.to_html(full_html=False, include_plotlyjs=plotlyjs)


def pandas_text(df: pd.DataFrame) -> pd.DataFrame:
    """Frame of strings formatted the way pandas prints each column (uniform decimals, NaN), for display-only tables."""
    return pd.DataFrame({c: [x.strip() for x in df[c].to_string(index=False).split("\n")] for c in df.columns}, index=df.index)
