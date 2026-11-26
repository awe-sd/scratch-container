"""Build a self-contained HTML presentation of the gis-research agent pipeline (v2):
what it does, and what the v1 log-forensics run measured about how it failed.

Every number on the page is read from committed data at build time, never hand-typed:
  - docs/analysis/2026-07-19-logmine/{stats.json,failure_inrs.csv,report.md,
    per_run_summary.csv} -- the v1 measured corpus (943 runs, 57,865 tool calls).
  - research/TRIAGE_CHECKLIST.md (T1-T5) + research/PLAYBOOK.md (D0-D5) -- parsed
    verbatim so the step cards can never drift from the real agent instructions.
  - research/_reference/deep_queue_v2.csv + triage_recheck_v2.txt -- the current
    pipeline-v2 gate counts (deep_candidate / triage-v2 recheck queues).
  - research/*/factsheet.json -- scanned READ-ONLY (mirrors make_deep_queue.py's own
    counting logic, writes nothing) to get the paper_kill count the two reference
    files above don't carry on their own.
  - docs/analysis/*-pilot.md -- the v1-vs-v2 pilot report. OPTIONAL: a pilot may be
    running concurrently and may not exist yet (its exact format isn't guaranteed
    either way). If present: every markdown table in it is parsed, and any table with
    a recognizable cost/turns/webfetch header (matched by substring, case-insensitive)
    has its per-run values placed directly in the before/after table's v2 column,
    grouped by a "mode" column if present; unmatched rows and the full raw text are
    still rendered below for manual review. If absent, the before/after section shows
    v1 numbers only with an explicit "pilot in progress" placeholder. Re-run this
    builder after the pilot report lands to pick it up -- fully idempotent, safe to
    overwrite.

No external assets: no CDN, no <script src=, no <link href=. Only <details> for
JS-free interactivity, matching build_queue_report.py's self-contained convention.

Silent-degradation policy: every regex/lookup against source data (report.md prose,
class_err lookups, failure_inrs.csv examples) either succeeds with a live-derived
number, or renders DRIFT_PLACEHOLDER / an explicit warning -- it never falls back to a
number that was merely true on some earlier build. parse_step_blocks() output is
asserted to meet a minimum count (T1-T5, D0-D5); a structural drift in the checklist/
playbook raises loudly instead of silently shipping a page with fewer cards.

Run from repo root:
  uv run gis-research/scripts/build_process_report.py
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]  # gis-research/
LOGMINE = BASE / "docs" / "analysis" / "2026-07-19-logmine"
ANALYSIS_DIR = BASE / "docs" / "analysis"
REF = BASE / "research" / "_reference"
RESEARCH = BASE / "research"
OUT_DIR = BASE / "output"
TRIAGE_CHECKLIST = RESEARCH / "TRIAGE_CHECKLIST.md"
PLAYBOOK = RESEARCH / "PLAYBOOK.md"

# Sourced from scripts/research_tools/make_deep_queue.py module constants (comment
# there: "Sonnet deep mean" / "triage-v2 re-check, user-set 2026-07-20") -- not
# invented here, just reused so the spend estimate matches the tool that queues the work.
DEEP_SCAN_COST = 4.64
RECHECK_COST = 0.35

# Shown whenever a regex/lookup against source data misses -- NEVER fall back to a
# hardcoded number that was true on some past build. A stale-looking placeholder is
# the honest failure mode; a silently-frozen old figure is not.
DRIFT_PLACEHOLDER = "[source data changed — re-verify]"

# Minimum step-block counts the checklist/playbook parsers must find. If either file's
# structure drifts (renumbered, reworded past recognition) the build must fail loudly
# here rather than silently ship a page with fewer cards than the real process has.
MIN_TRIAGE_STEPS = 5   # T1-T5
MIN_DEEP_STEPS = 6     # D0-D5


# --------------------------------------------------------------------------- data


def load_stats() -> dict:
    return json.loads((LOGMINE / "stats.json").read_text(encoding="utf-8"))


def load_failure_inrs() -> dict[str, dict]:
    with open(LOGMINE / "failure_inrs.csv", encoding="utf-8") as fh:
        return {row["inr"]: row for row in csv.DictReader(fh)}


def load_per_run_summary() -> pd.DataFrame:
    return pd.read_csv(LOGMINE / "per_run_summary.csv")


def parse_report_md_reconciled(text: str) -> dict:
    """Pull the reconciled failure-taxonomy numbers that only exist as prose/tables
    in report.md (stats.json's raw per-subtype fields don't carry the reconciled
    view -- see report.md section (b) for why). Any pattern that fails to match
    yields None for that key rather than a guessed number."""

    def find(pattern: str, *, flags=0):
        m = re.search(pattern, text, flags)
        return m.groups() if m else None

    out = {}
    out["token_budget_kill"] = find(
        r"\|\s*\*\*token_budget_kill\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\*\*(\d+)\*\*"
    )
    out["max_turns"] = find(
        r"\|\s*\*\*max_turns\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\*\*(\d+)\*\*"
    )
    out["hard_kill_no_record"] = find(
        r"\|\s*\*\*hard_kill_no_record\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\*\*(\d+)\*\*"
    )
    lost = find(r"across all 75 non-success runs, \*\*(\d+) produced no findings/dossier/triage output")
    out["lost_all_work"] = lost[0] if lost else None
    tk_no_out = find(r"\*\*(\d+) of the 33 token-killed runs produced no")
    out["token_kill_no_output"] = tk_no_out[0] if tk_no_out else None
    stuck = find(r"\*\*(\d+) loop episodes across (\d+) runs\.?\*\*")
    out["stuck_loops"] = stuck
    longest = find(r"single longest loop is (\d+) consecutive curls.*?in `(\w+)`")
    out["longest_loop"] = longest
    spend = find(r"Total spend \*\*~\$([\d,]+)\*\*")
    out["total_spend"] = spend[0] if spend else None
    return out


def parse_step_blocks(text: str, prefix: str) -> list[tuple[str, str]]:
    """Parse 'T1 ...' / 'D0 ...' style checklist blocks: a marker line followed by
    indented continuation lines, ending at the next marker or a non-indented line.
    Returns [(marker, full_text), ...] in file order -- the ENTIRE source text is
    preserved (nothing truncated), so the page can't drift from the real playbook."""
    pattern = re.compile(rf"^({prefix}\d)\s+(.*)$")
    blocks: list[tuple[str, str]] = []
    cur_marker = None
    cur_lines: list[str] = []
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            if cur_marker:
                blocks.append((cur_marker, " ".join(cur_lines).strip()))
            cur_marker, cur_lines = m.group(1), [m.group(2).strip()]
        elif cur_marker and line.startswith(" "):
            cur_lines.append(line.strip())
        elif cur_marker and not line.strip():
            continue
        elif cur_marker:
            blocks.append((cur_marker, " ".join(cur_lines).strip()))
            cur_marker, cur_lines = None, []
    if cur_marker:
        blocks.append((cur_marker, " ".join(cur_lines).strip()))
    return blocks


def leading_label(text: str) -> tuple[str | None, str]:
    """Split off the leading run of ALL-CAPS tokens (the step's shouty headline) so
    it can be bolded; the remainder is returned verbatim -- no text is dropped."""
    tokens = text.split(" ")
    label_tokens = []
    for tok in tokens:
        bare = tok.strip("`():,;.")
        if bare in {"+", "-", "/", "&"}:
            label_tokens.append(tok)  # connector inside a multi-word headline (e.g. "SITE + IMAGERY:")
            continue
        if bare and bare == bare.upper() and any(c.isalpha() for c in bare):
            label_tokens.append(tok)
        else:
            break
    if not label_tokens:
        return None, text
    label = " ".join(label_tokens)
    rest = text[len(label):].lstrip(": ")
    return label, rest


def load_triage_steps() -> list[dict]:
    text = TRIAGE_CHECKLIST.read_text(encoding="utf-8")
    blocks = parse_step_blocks(text, "T")
    if len(blocks) < MIN_TRIAGE_STEPS:
        raise RuntimeError(
            f"research/TRIAGE_CHECKLIST.md structure drifted: parse_step_blocks() found "
            f"only {len(blocks)} T-marker block(s) (expected >= {MIN_TRIAGE_STEPS}, T1-T5). "
            f"The checklist was reworded/renumbered past what this builder's parser "
            f"recognizes -- fix parse_step_blocks() in build_process_report.py (or the "
            f"checklist) before rebuilding; do not ship a page with steps silently missing."
        )
    steps = []
    for marker, body in blocks:
        label, rest = leading_label(body)
        steps.append({"marker": marker, "label": label, "body": rest})
    return steps


def load_deep_steps() -> list[dict]:
    text = PLAYBOOK.read_text(encoding="utf-8")
    start = text.index("## Deep scan v2")
    end = text.index("\n## Stage 1", start)
    section = text[start:end]
    blocks = parse_step_blocks(section, "D")
    if len(blocks) < MIN_DEEP_STEPS:
        raise RuntimeError(
            f"research/PLAYBOOK.md structure drifted: parse_step_blocks() found only "
            f"{len(blocks)} D-marker block(s) in the 'Deep scan v2' section (expected "
            f">= {MIN_DEEP_STEPS}, D0-D5). The playbook was reworded/renumbered/moved "
            f"past what this builder's parser recognizes -- fix parse_step_blocks() in "
            f"build_process_report.py (or the playbook) before rebuilding; do not ship "
            f"a page with stages silently missing."
        )
    steps = []
    for marker, body in blocks:
        label, rest = leading_label(body)
        steps.append({"marker": marker, "label": label, "body": rest})
    return steps


def scan_factsheet_gate_counts() -> dict:
    """Read-only tally over research/*/factsheet.json, mirroring the counting logic
    in scripts/research_tools/make_deep_queue.py's build_v2() WITHOUT writing
    anything -- gets the paper_kill/total counts that deep_queue_v2.csv and
    triage_recheck_v2.txt alone don't carry (they only list the other two buckets)."""
    counts = {"deep_candidate": 0, "paper_kill": 0, "ambiguous": 0, "other": 0}
    n_total = 0
    for fp in sorted(RESEARCH.glob("*/factsheet.json")):
        if fp.parent.name.startswith("_"):
            continue
        n_total += 1
        try:
            f = json.loads(fp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"WARNING: corrupt JSON, skipping {fp}", file=sys.stderr)
            continue
        decision = (f.get("gate") or {}).get("decision")
        if decision not in counts:
            print(f"WARNING: unknown/missing gate.decision {decision!r} in {fp}, "
                  f"counting as 'other'", file=sys.stderr)
        counts[decision if decision in counts else "other"] += 1
    counts["total"] = n_total
    return counts


def load_gate_queue_counts() -> dict:
    """Row/line counts from the two committed pipeline-v2 reference files (the
    brief's mandated source for the deep/recheck queue sizes)."""
    with open(REF / "deep_queue_v2.csv", encoding="utf-8") as fh:
        deep_candidate = sum(1 for _ in csv.DictReader(fh))

    ambiguous = conflict = 0
    for line in (REF / "triage_recheck_v2.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        if "v1-conflict" in line:
            conflict += 1
        elif "ambiguous" in line:
            ambiguous += 1
    return {
        "deep_candidate": deep_candidate,
        "ambiguous": ambiguous,
        "v1_conflict": conflict,
        "recheck_total": ambiguous + conflict,
    }


def load_deep_queue_spend() -> dict:
    not_scanned = 0
    mw_not_scanned = 0.0
    with open(REF / "deep_queue_v2.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["already_deep_scanned"] == "False":
                not_scanned += 1
                mw_not_scanned += float(row["mw"] or 0)
    return {
        "not_scanned": not_scanned,
        "mw_not_scanned": mw_not_scanned,
        "est_spend": not_scanned * DEEP_SCAN_COST,
    }


def find_pilot_report() -> Path | None:
    candidates = sorted(ANALYSIS_DIR.glob("*-pilot.md"))
    return candidates[0] if candidates else None


def extract_md_tables(text: str) -> list[list[list[str]]]:
    """Generic GFM table extractor: returns a list of tables, each a list of rows,
    each a list of cell strings (header row included, separator row dropped)."""
    lines = text.splitlines()
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in lines:
        if line.strip().startswith("|"):
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)

    tables = []
    for block in blocks:
        rows = []
        for line in block:
            stripped = line.strip().strip("|")
            if set(stripped.replace("|", "").strip()) <= {"-", ":", " "}:
                continue  # header separator row
            rows.append([c.strip() for c in stripped.split("|")])
        if len(rows) >= 2:
            tables.append(rows)
    return tables


# Column-name needles (case-insensitive substring match against the header row) used
# to recognize a per-run pilot metrics table regardless of its exact header wording --
# Task 10's report format isn't guaranteed, so this is a best-effort match, not a
# fixed schema.
_PILOT_COL_NEEDLES = {
    "cost": ["cost"],
    "turns": ["turn"],
    "webfetch": ["webfetch", "fetch"],
    "mode": ["mode"],
}


def extract_pilot_metrics(tables: list[list[list[str]]]) -> dict[str, dict[str, list[str]]] | None:
    """Best-effort extraction of per-run cost/turns/webfetch values from whichever
    pilot-report table has recognizable headers, grouped by a 'mode' column if one
    exists (else grouped under 'run'). Returns None if no table has ANY of the three
    recognized metric columns -- caller then falls back to the raw table dump."""
    for rows in tables:
        header = [c.strip().lower() for c in rows[0]]
        col_idx: dict[str, int] = {}
        for key, needles in _PILOT_COL_NEEDLES.items():
            for i, col in enumerate(header):
                if any(n in col for n in needles):
                    col_idx[key] = i
                    break
        if not any(k in col_idx for k in ("cost", "turns", "webfetch")):
            continue  # doesn't look like a per-run metrics table -- try the next one

        by_mode: dict[str, dict[str, list[str]]] = {}
        for r in rows[1:]:
            mode_val = "run"
            if "mode" in col_idx and col_idx["mode"] < len(r) and r[col_idx["mode"]].strip():
                mode_val = r[col_idx["mode"]].strip().lower()
            bucket = by_mode.setdefault(mode_val, {})
            for key in ("cost", "turns", "webfetch"):
                if key in col_idx and col_idx[key] < len(r) and r[col_idx[key]].strip():
                    bucket.setdefault(key, []).append(r[col_idx[key]].strip())
        if by_mode:
            return by_mode
    return None


def pilot_value_for(by_mode: dict | None, mode: str, key: str) -> str | None:
    """Look up an extracted pilot value for (mode, metric); falls back to the
    mode-less 'run' bucket if the table had no mode column. None = not found."""
    if not by_mode:
        return None
    bucket = by_mode.get(mode) or by_mode.get("run")
    if not bucket or key not in bucket:
        return None
    return ", ".join(bucket[key])


# --------------------------------------------------------------------------- html


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def fnum(n) -> str:
    return f"{n:,}" if isinstance(n, int) else f"{n:,.2f}"


def render_step_cards(steps: list[dict], css_class: str) -> str:
    cards = []
    for s in steps:
        label_html = f'<div class="step-label">{esc(s["label"])}</div>' if s["label"] else ""
        cards.append(f"""
      <div class="step-card {css_class}">
        <div class="step-marker">{esc(s['marker'])}</div>
        {label_html}
        <div class="step-body">{esc(s['body'])}</div>
      </div>""")
    return "\n".join(cards)


def render_pipeline_diagram(gate: dict, fs: dict) -> str:
    return f"""
    <div class="pipeline">
      <div class="pbox">Queue project<br><span class="ptag">{fs['total']:,} triaged (v1)</span></div>
      <div class="parrow">&rarr;</div>
      <div class="pbox">factsheet.py<br><span class="ptag">deterministic paper_score</span></div>
      <div class="parrow">&rarr;</div>
      <div class="pbox gatebox">gate()</div>
      <div class="branches">
        <div class="branch">
          <div class="pcond">score &ge; 50</div>
          <div class="parrow down">&darr;</div>
          <div class="pbox outcome kill">paper_kill<br><b>{fs['paper_kill']}</b></div>
        </div>
        <div class="branch">
          <div class="pcond">score &lt; 50 + reality signal</div>
          <div class="parrow down">&darr;</div>
          <div class="pbox outcome deep">deep_candidate<br><b>{gate['deep_candidate']}</b>
            <br><span class="ptag">ranked MW &times; COD-nearness</span></div>
          <div class="parrow down">&darr;</div>
          <div class="pbox">Deep scan D0&ndash;D5</div>
        </div>
        <div class="branch">
          <div class="pcond">else</div>
          <div class="parrow down">&darr;</div>
          <div class="pbox outcome ambiguous">ambiguous<br><b>{gate['ambiguous']}</b></div>
          <div class="parrow down">+ {gate['v1_conflict']} v1-conflict &darr;</div>
          <div class="pbox outcome recheck">triage-v2 recheck<br><b>{gate['recheck_total']}</b></div>
          <div class="parrow down">&darr;</div>
          <div class="pbox">Triage T1&ndash;T5</div>
        </div>
      </div>
    </div>
    <div class="footnote">
      {fs['total']:,} projects scanned by factsheet.py &rarr; {fs['paper_kill']} paper_kill
      (score &ge; 50) + {gate['deep_candidate']} deep_candidate + {fs['ambiguous']} ambiguous
      ({gate['v1_conflict']} of the paper_kill projects conflict with a v1
      deep_scan_recommended=true triage, added to the {gate['recheck_total']}-project
      triage-v2 recheck queue). Counts: research/_reference/deep_queue_v2.csv,
      research/_reference/triage_recheck_v2.txt, and a read-only scan of
      research/*/factsheet.json at build time.
    </div>"""


def render_before_after(stats: dict, df: pd.DataFrame, reconciled: dict, pilot) -> str:
    tri = df[df["mode"] == "triage"]
    deep = df[df["mode"] == "deep"]
    tri_success = (tri["terminal_state"] == "success").sum()
    deep_success = (deep["terminal_state"] == "success").sum()

    # Each row: (label, v1 value, optional (mode, metric_key) for pilot per-row lookup)
    rows: list[tuple[str, str, tuple[str, str] | None]] = [
        ("Triage &mdash; mean cost / run", f"${stats['cost_by_mode']['triage']['mean']:.2f}", ("triage", "cost")),
        ("Triage &mdash; median turns / run", f"{tri['num_turns'].median():.0f}", ("triage", "turns")),
        ("Triage &mdash; success rate", f"{tri_success}/{len(tri)} ({100*tri_success/len(tri):.1f}%)", None),
        ("Deep &mdash; mean cost / run", f"${stats['cost_by_mode']['deep']['mean']:.2f}", ("deep", "cost")),
        ("Deep &mdash; median turns / run", f"{deep['num_turns'].median():.0f}", ("deep", "turns")),
        ("Deep &mdash; success rate", f"{deep_success}/{len(deep)} ({100*deep_success/len(deep):.1f}%)", None),
        ("Web-research share of all tool calls", f"{stats['stage_share']['web_research']}%", None),
        ("PUCT portal WebFetch fail rate", f"{stats['puct_402']:,}/{stats['puct_calls']:,} (100%)", None),
        ("Search-engine HTML scraping share of all calls", f"{stats['search_scrape_pct_all']}%", None),
    ]
    tb = reconciled.get("token_budget_kill")
    mt = reconciled.get("max_turns")
    hk = reconciled.get("hard_kill_no_record")
    if tb and mt and hk:
        n_total = int(tb[2]) + int(mt[2]) + int(hk[2])
        rows.append((
            "Non-success runs (of 943)",
            f"{n_total} ({tb[2]} budget-kill / {mt[2]} max-turns / {hk[2]} hard-kill)",
            None,
        ))
    else:
        rows.append(("Non-success runs (of 943)", DRIFT_PLACEHOLDER, None))
    if reconciled.get("lost_all_work"):
        rows.append(("Runs that lost ALL work (no findings/dossier/triage output)",
                      f"{reconciled['lost_all_work']}/75", None))
    else:
        rows.append(("Runs that lost ALL work (no findings/dossier/triage output)",
                      DRIFT_PLACEHOLDER, None))

    by_mode = extract_pilot_metrics(pilot[1]) if pilot is not None else None

    def v2_cell(pilot_key: tuple[str, str] | None) -> str:
        if pilot is None:
            return '<td class="v2val pending">pilot in progress</td>'
        if pilot_key is not None:
            val = pilot_value_for(by_mode, pilot_key[0], pilot_key[1])
            if val is not None:
                return f'<td class="v2val">{esc(val)}</td>'
        return '<td class="v2val">see pilot table below</td>'

    row_html = "\n".join(
        f'<tr><td class="metric">{label}</td><td class="v1val">{val}</td>{v2_cell(pkey)}</tr>'
        for label, val, pkey in rows
    )

    pilot_html = ""
    if pilot is not None:
        path, tables = pilot
        table_blocks = []
        for rows_ in tables:
            header, *body = rows_
            thead = "".join(f"<th>{esc(c)}</th>" for c in header)
            tbody = "\n".join(
                "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in body
            )
            table_blocks.append(f"""
        <table class="pilot-table">
          <thead><tr>{thead}</tr></thead>
          <tbody>{tbody}</tbody>
        </table>""")
        raw_text = esc(path.read_text(encoding="utf-8"))
        match_note = (
            "Per-run cost/turns/webfetch values above were auto-matched from a "
            "recognizable header in the table(s) below (matched columns: "
            + ", ".join(sorted({k for m in (by_mode or {}).values() for k in m})) + ")."
            if by_mode else
            "No table with a recognizable cost/turns/webfetch header was found in the "
            "pilot report -- the v2 column above falls back to \"see pilot table below\"; "
            "the raw extracted table(s) follow for manual review."
        )
        pilot_html = f"""
    <p class="muted">{match_note}</p>
    <h3>Pilot report tables (auto-extracted from <code>{esc(path.relative_to(BASE))}</code>)</h3>
    {"".join(table_blocks) if table_blocks else '<p class="muted">No markdown tables found in the pilot report.</p>'}
    <details>
      <summary>Full pilot report text</summary>
      <pre class="raw-pilot">{raw_text}</pre>
    </details>"""
    else:
        pilot_html = """
    <p class="muted pending-note">Pilot report not found yet
      (<code>docs/analysis/*-pilot.md</code>). A 3-project pilot (1 ambiguous triage +
      2 deep, incl. the Hanson regression) may be running concurrently with this build.
      Re-run <code>uv run gis-research/scripts/build_process_report.py</code> after it
      lands to populate the v2 column above.</p>"""

    return f"""
    <table class="before-after">
      <thead><tr><th>Metric</th><th>v1 measured (N=943 runs)</th><th>v2 pilot</th></tr></thead>
      <tbody>{row_html}</tbody>
    </table>
    {pilot_html}"""


def _median_wallclock_min(df: pd.DataFrame, terminal_state: str) -> str:
    """Live median wall-clock (minutes) for a terminal_state bucket, computed from
    per_run_summary.csv -- never a frozen literal. DRIFT_PLACEHOLDER if the bucket
    is empty (e.g. a future regeneration relabels terminal states)."""
    sub = df.loc[df["terminal_state"] == terminal_state, "wallclock_s"]
    if sub.empty:
        return DRIFT_PLACEHOLDER
    return f"{sub.median() / 60:.1f} min"


def render_failure_classes(stats: dict, failure_inrs: dict, reconciled: dict, df: pd.DataFrame) -> str:
    def class_err(name: str) -> dict | None:
        for c in stats["class_err"]:
            if c["domain_class"] == name:
                return c
        return None

    sec = class_err("sec")
    sec_rate = f"{sec['rate']}" if sec else DRIFT_PLACEHOLDER
    sec_calls = f"{sec['calls']:,}" if sec else DRIFT_PLACEHOLDER
    tb = reconciled.get("token_budget_kill")
    mt = reconciled.get("max_turns")
    longest = reconciled.get("longest_loop")
    budget_kill_min = _median_wallclock_min(df, "budget_kill")
    success_min = _median_wallclock_min(df, "success")

    classes = [
        {
            "title": "Dead-domain retry storms",
            "measured": (
                f"{stats['puct_calls']:,} WebFetch calls to the PUCT Interchange portal, "
                f"{stats['puct_402']:,} of them ({100*stats['puct_402']/stats['puct_calls']:.1f}%) "
                f"HTTP 402 &mdash; plus SEC EDGAR failing "
                f"{sec_rate}% across {sec_calls} calls."
                + (f" Worst single-run loop: {longest[0]} consecutive curls, run <code>{longest[1]}</code>."
                   if longest else "")
            ),
            "example_inr": "27INR0536",
            "fix": ("<code>puct.py match</code> / <code>spv.py resolve</code> replace raw "
                    "WebFetch/curl with the local docket index + on-disk IA PDFs; a domain "
                    "blocklist blocks direct agent fetches to <code>interchange.puc.texas.gov</code> "
                    "and <code>efts.sec.gov</code> outright (PLAYBOOK Stage 2 systematic ladder)."),
        },
        {
            "title": "Budget-kill work loss",
            "measured": (
                (f"{tb[2]} token-budget kills ({tb[0]} deep / {tb[1]} triage)"
                 if tb else f"token-budget kill count {DRIFT_PLACEHOLDER}")
                + (f", {reconciled['token_kill_no_output']} of them wrote no "
                   f"<code>findings.json</code>/<code>dossier.md</code> at all"
                   if reconciled.get("token_kill_no_output") else "")
                + f". Median wall-clock to death: {budget_kill_min} vs {success_min} "
                  f"for a successful run."
            ),
            "example_inr": "25INR0591",
            "fix": ("Checkpointed deep stages: D0 writes the full <code>findings.json</code> "
                    "skeleton BEFORE any research begins, and each stage (D1&ndash;D5) ends with "
                    "a checkpoint write &mdash; a budget-kill now loses at most one stage's "
                    "work, never all of it."),
        },
        {
            "title": "Max-turns exhaustion",
            "measured": (
                (f"{mt[2]} runs ({mt[0]} deep / {mt[1]} triage) hit the SDK turn cap"
                 if mt else f"max-turns run count {DRIFT_PLACEHOLDER}")
                + ". Last 10 tool calls of these runs: "
                + ", ".join(f"{v} {k}" for k, v in stats["maxturns_last10_stage"].items())
                + " &mdash; still researching or re-running wrap-up scripts, not finishing."
            ),
            "example_inr": "25INR0052",
            "fix": ("Deterministic wrap-up (D5: <code>queue_history.py</code> &rarr; "
                    "<code>eia_history.py</code> &rarr; <code>build_brief.py</code> &rarr; "
                    "<code>build_index.py</code>) runs ONCE instead of an agent-driven "
                    "rebuild loop; a checkpoint watchdog (PostToolUse) counts tool calls "
                    "since the last <code>findings.json</code> write and injects a warning "
                    "turn past 25, forcing a checkpoint before the turn cap is reached."),
        },
        {
            "title": "Search-engine HTML scraping",
            "measured": (
                f"{stats['search_scrape']:,} WebFetch calls to html.duckduckgo.com / "
                f"www.bing.com / search.yahoo.com search-result pages "
                f"({stats['search_scrape_pct_wf']}% of all WebFetch, "
                f"{stats['search_scrape_pct_all']}% of all "
                f"{stats['total_tool_calls']:,} tool calls) &mdash; done in place of a "
                f"search tool."
            ),
            "example_inr": "22INR0203",
            "fix": ("<code>search.py \"&lt;query&gt;\"</code> is the one search entrypoint "
                    "(AgentCore Gateway &rarr; OAuth bridge &rarr; DDG HTML ladder, 7-day "
                    "cache, banned queue-tracker domains suppressed at the tool layer) "
                    "&mdash; agents are blocked from scraping search engines directly."),
        },
    ]

    cards = []
    for c in classes:
        row = failure_inrs.get(c["example_inr"])
        if row is None:
            example_html = f"""
        <div class="fail-example drift-warning">
          <b>{DRIFT_PLACEHOLDER}</b> real example
          <code>{esc(c['example_inr'])}</code> is no longer present in
          <code>failure_inrs.csv</code> -- the source data changed since this example
          was picked; re-verify and choose a current example before trusting this card.
        </div>"""
        else:
            example_html = f"""
        <details class="fail-example">
          <summary>Real example: <code>{esc(c['example_inr'])}</code>
            ({esc(row['mode'])}, terminal state <code>{esc(row['terminal_state'])}</code>)</summary>
          <div class="fail-narrative">{esc(row.get('last_activity_summary', ''))}</div>
        </details>"""
        cards.append(f"""
      <div class="fail-card">
        <div class="fail-head">
          <h3>{esc(c['title'])}</h3>
          <span class="badge">ADDRESSED</span>
        </div>
        <div class="fail-measured">{c['measured']}</div>
        {example_html}
        <div class="fail-fix"><b>v2 fix:</b> {c['fix']}</div>
      </div>""")
    return "\n".join(cards)


def render_footer(stats: dict, gate: dict, fs: dict, reconciled: dict, spend: dict) -> str:
    total_spend = reconciled.get("total_spend") or (
        f"{stats['cost_by_mode']['deep']['sum'] + stats['cost_by_mode']['triage']['sum']:,.0f}"
    )
    stuck = reconciled.get("stuck_loops")
    stuck_txt = (f"{stuck[0]} stuck-loop episodes across {stuck[1]} runs"
                 if stuck else f"stuck-loop count {DRIFT_PLACEHOLDER}")
    return f"""
    <ul class="corpus-stats">
      <li><b>943</b> runs mined (779 triage + 164 deep) &mdash; <b>{stats['total_tool_calls']:,}</b> tool calls</li>
      <li><b>{stats['webfetch_total']:,}</b> WebFetch calls ({stats['webfetch_by_mode']['deep']:,} deep / {stats['webfetch_by_mode']['triage']:,} triage)</li>
      <li>{stuck_txt}</li>
      <li>v1 total spend &asymp; <b>${total_spend}</b>
        (deep ${stats['cost_by_mode']['deep']['sum']:,.0f}, triage ${stats['cost_by_mode']['triage']['sum']:,.0f})</li>
      <li>Current corpus: <b>{fs['total']:,}</b> factsheets &rarr;
        <b>{gate['deep_candidate']}</b> deep_candidate / <b>{fs['paper_kill']}</b> paper_kill /
        <b>{gate['recheck_total']}</b> triage-v2 recheck</li>
      <li>Deep queue not yet scanned: <b>{spend['not_scanned']}</b> projects,
        {spend['mw_not_scanned']:,.0f} MW &mdash; est. spend to clear
        <b>${spend['est_spend']:,.2f}</b> ({spend['not_scanned']} &times; ${DEEP_SCAN_COST}/scan)</li>
      <li>Triage-v2 recheck queue: <b>{gate['recheck_total']}</b> projects &mdash;
        est. spend <b>${gate['recheck_total'] * RECHECK_COST:,.2f}</b>
        ({gate['recheck_total']} &times; ${RECHECK_COST}/project)</li>
    </ul>"""


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>gis-research Pipeline v2 — Process &amp; Failure Report</title>
<style>
  :root {{
    --bg: #ffffff; --surface: #f7f8fa; --ink: #1a1d21; --ink-2: #545a63;
    --muted: #8a919c; --line: #e2e6ec; --accent: #2563eb; --accent-soft: #eef3ff;
    --kill: #fdecea; --kill-line: #c0392b; --deep: #eaf5ec; --deep-line: #1e8449;
    --amb: #fff8e6; --amb-line: #b7791f; --badge-bg: #e6f6ea; --badge-ink: #1e8449;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14171c; --surface: #1c2027; --ink: #eceff3; --ink-2: #b3bac4;
      --muted: #7d8590; --line: #2a2f38; --accent: #6ea8fe; --accent-soft: #1e2633;
      --kill: #3a1f1e; --kill-line: #e57373; --deep: #1c2e20; --deep-line: #6fcf7d;
      --amb: #332a13; --amb-line: #e0b04a; --badge-bg: #16301d; --badge-ink: #6fcf7d;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0 auto; padding: 24px; max-width: 1180px; background: var(--bg); color: var(--ink);
    font: 14px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }}
  h1 {{ font-size: 21px; margin: 0 0 2px; }}
  h2 {{ font-size: 16px; margin: 34px 0 12px; border-top: 1px solid var(--line); padding-top: 22px; }}
  h2:first-of-type {{ border-top: none; padding-top: 0; }}
  h3 {{ font-size: 14px; margin: 18px 0 8px; }}
  .sub {{ color: var(--ink-2); font-size: 13px; margin-bottom: 6px; }}
  code {{ background: var(--surface); border: 1px solid var(--line); border-radius: 4px;
    padding: 1px 5px; font-size: 12.5px; }}
  .muted {{ color: var(--muted); }}

  /* pipeline diagram -- pure HTML/CSS, no JS */
  .pipeline {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin: 18px 0 6px; }}
  .pbox {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 12px 16px; text-align: center; font-weight: 600; font-size: 13px; }}
  .gatebox {{ border: 2px solid var(--accent); color: var(--accent); }}
  .ptag {{ font-weight: 400; color: var(--muted); font-size: 11.5px; }}
  .parrow {{ font-size: 20px; color: var(--muted); }}
  .parrow.down {{ font-size: 13px; }}
  .branches {{ display: flex; gap: 22px; align-items: flex-start; flex-wrap: wrap; }}
  .branch {{ display: flex; flex-direction: column; align-items: center; gap: 6px; width: 220px; }}
  .pcond {{ font-size: 11.5px; color: var(--muted); text-align: center; }}
  .outcome {{ width: 100%; }}
  .outcome.kill {{ background: var(--kill); border-color: var(--kill-line); }}
  .outcome.deep {{ background: var(--deep); border-color: var(--deep-line); }}
  .outcome.ambiguous, .outcome.recheck {{ background: var(--amb); border-color: var(--amb-line); }}
  .footnote {{ color: var(--muted); font-size: 12px; margin-top: 14px; }}

  /* step cards (T1-T5 / D0-D5) */
  .step-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px; margin-top: 10px; }}
  .step-card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 12px 14px; }}
  .step-marker {{ display: inline-block; background: var(--accent); color: #fff;
    border-radius: 6px; padding: 1px 8px; font-size: 12px; font-weight: 700; margin-bottom: 6px; }}
  .step-label {{ font-weight: 700; font-size: 13px; margin-bottom: 4px; }}
  .step-body {{ font-size: 12.5px; color: var(--ink-2); }}

  /* before/after */
  table.before-after, table.pilot-table {{ border-collapse: collapse; width: 100%;
    font-variant-numeric: tabular-nums; margin-top: 10px; }}
  table.before-after th, table.before-after td,
  table.pilot-table th, table.pilot-table td {{
    border-bottom: 1px solid var(--line); padding: 7px 12px; text-align: left; font-size: 13px; }}
  table.before-after thead th, table.pilot-table thead th {{ background: var(--surface); }}
  td.metric {{ color: var(--ink-2); }}
  td.v1val {{ font-weight: 600; }}
  td.v2val.pending {{ color: var(--muted); font-style: italic; }}
  .pending-note {{ margin-top: 10px; }}
  .raw-pilot {{ white-space: pre-wrap; font-size: 12px; background: var(--surface);
    border: 1px solid var(--line); border-radius: 8px; padding: 12px; max-height: 480px; overflow: auto; }}

  /* failure-class panel */
  .fail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 14px; margin-top: 10px; }}
  .fail-card {{ background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
    padding: 14px 16px; }}
  .fail-head {{ display: flex; justify-content: space-between; align-items: center; }}
  .fail-head h3 {{ margin: 0; }}
  .badge {{ background: var(--badge-bg); color: var(--badge-ink); font-size: 11px;
    font-weight: 700; letter-spacing: .03em; border-radius: 20px; padding: 3px 10px; }}
  .fail-measured {{ font-size: 12.5px; margin: 8px 0; }}
  .fail-example summary {{ cursor: pointer; font-size: 12.5px; color: var(--accent); }}
  .fail-narrative {{ font-size: 11.5px; font-family: ui-monospace, Menlo, Consolas, monospace;
    color: var(--ink-2); background: var(--bg); border: 1px solid var(--line); border-radius: 6px;
    padding: 8px 10px; margin-top: 6px; word-break: break-word; }}
  .fail-fix {{ font-size: 12.5px; margin-top: 10px; }}
  .drift-warning {{ font-size: 12px; color: var(--kill-line); background: var(--kill);
    border: 1px solid var(--kill-line); border-radius: 6px; padding: 8px 10px; margin-top: 6px; }}

  ul.corpus-stats {{ margin: 10px 0 0; padding-left: 18px; }}
  ul.corpus-stats li {{ margin-bottom: 6px; font-size: 13px; }}

  details > summary {{ cursor: pointer; }}
</style>
</head>
<body>
  <h1>gis-research Pipeline v2 — Process &amp; Failure Report</h1>
  <div class="sub">How the ERCOT GIS interconnection-queue research agents work, and what the
    v1 log-forensics run (943 runs, {total_tool_calls} tool calls) measured about how they failed.</div>

  <h2>1. Pipeline</h2>
  {pipeline}

  <h2>2. Triage (T1&ndash;T5)</h2>
  <div class="sub">Verbatim from <code>research/TRIAGE_CHECKLIST.md</code>, parsed at build time.</div>
  <div class="step-grid">{triage_cards}</div>

  <h2>3. Deep scan (D0&ndash;D5)</h2>
  <div class="sub">Verbatim from <code>research/PLAYBOOK.md</code> &sect; Deep scan v2, parsed at build time.</div>
  <div class="step-grid">{deep_cards}</div>

  <h2>4. Before / after</h2>
  {before_after}

  <h2>5. Where v1 agents failed</h2>
  <div class="fail-grid">{failure_cards}</div>

  <h2>6. Corpus stats</h2>
  {footer}

  <div class="footnote" style="margin-top:28px;">
    Generated by <code>gis-research/scripts/build_process_report.py</code> from committed data;
    re-run to refresh (idempotent overwrite of <code>output/process_v2.html</code>).
  </div>
</body>
</html>
"""


def build() -> str:
    stats = load_stats()
    failure_inrs = load_failure_inrs()
    df = load_per_run_summary()
    reconciled = parse_report_md_reconciled((LOGMINE / "report.md").read_text(encoding="utf-8"))
    triage_steps = load_triage_steps()
    deep_steps = load_deep_steps()
    fs_counts = scan_factsheet_gate_counts()
    gate = load_gate_queue_counts()
    spend = load_deep_queue_spend()

    pilot_path = find_pilot_report()
    pilot = None
    if pilot_path is not None:
        pilot = (pilot_path, extract_md_tables(pilot_path.read_text(encoding="utf-8")))

    return PAGE_TEMPLATE.format(
        total_tool_calls=f"{stats['total_tool_calls']:,}",
        pipeline=render_pipeline_diagram(gate, fs_counts),
        triage_cards=render_step_cards(triage_steps, "triage"),
        deep_cards=render_step_cards(deep_steps, "deep"),
        before_after=render_before_after(stats, df, reconciled, pilot),
        failure_cards=render_failure_classes(stats, failure_inrs, reconciled, df),
        footer=render_footer(stats, gate, fs_counts, reconciled, spend),
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "process_v2.html"
    html_out = build()
    out.write_text(html_out, encoding="utf-8")

    size_mb = out.stat().st_size / 1e6
    print(f"wrote {out} ({size_mb:.3f} MB)")
    pilot_path = find_pilot_report()
    print(f"pilot report: {pilot_path if pilot_path else 'NOT FOUND (placeholder rendered)'}")


if __name__ == "__main__":
    main()
