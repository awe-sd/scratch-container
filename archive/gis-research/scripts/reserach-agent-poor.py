"""
Generation Research Runner (Claude Code CLI edition)
----------------------------------------------------
Reads each project row from the input Excel and asks Claude (via the headless
Claude Code CLI, which has built-in web search) to:
  1. Find available online information (permitting, construction, regulatory, etc.)
  2. Produce an independent Commercial Operations Date (COD) estimate.
  3. Report the project's approximate latitude/longitude (a sanity check).
The COD is compared locally against the reported in-service date in the input
file; if they differ by more than 6 months, an alert is raised in the report.

This is the original ChatGPT runner ported to the Claude Code CLI — same flow and
output, but the per-project research runs through `claude -p` (live WebSearch/
WebFetch) instead of the OpenAI API. Auth is stored Claude Code login

Results are written to outputs/gen_research_<timestamp>.md
Previous responses are stored in gen_research_state.json and (in --delta mode)
passed back to Claude as context for delta updates.

Usage:
    python gen_research_runner.py                      # research all projects
    python gen_research_runner.py --project "Hoke"     # single project by name
    python gen_research_runner.py --model haiku        # cheaper model, default is sonnet
    python gen_research_runner.py --concurrency 8      # more parallelism
    python gen_research_runner.py --excel path.xlsx    # override input workbook
    python gen_research_runner.py --delta              # use prior report as context
"""

from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import pandas as pd
import os

#path to the claude executable (installed per-user; not on the system PATH).
CLAUDE_CLI_PATH = os.getenv('CLAUDE_CLI_PATH', str(Path.home() / '.local' / 'bin' / 'claude.exe'))
#model alias for the CLI: 'sonnet' | 'opus' | 'haiku' | 'fable'.
CLAUDE_CODE_MODEL = 'sonnet'
#how many projects to research in parallel (each is its own claude process).
CLAUDE_CODE_CONCURRENCY = 4
#per-project timeout in seconds (web research can take a few minutes).
CLAUDE_CODE_TIMEOUT = 600

# ── paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
STATE_FILE = BASE_DIR / "gen_research_state.json"

OUTPUT_DIR.mkdir(exist_ok=True)

# Fuel type code → human-readable label
FUEL_LABELS = {
    "SUN": "Solar (PV)", "SOL": "Solar (PV)", "PV": "Solar (PV)",
    "WND": "Wind", "WIN": "Wind",
    "NUC": "Nuclear", "NG": "Natural Gas", "GAS": "Natural Gas",
    "OIL": "Oil", "COL": "Coal", "HYD": "Hydro",
    "BAT": "Battery / Storage", "ESR": "Battery / Storage",
}

# Sentinel / empty values that should be treated as "no data"
_NULLS = {"", "nan", "nat", "none", "null", "[null]"}


def _clean(val):
    """Return val, or None if it is empty / NaN / a '[NULL]'-style sentinel."""
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    if str(val).strip().lower() in _NULLS:
        return None
    return val


def _cleanstr(val) -> Optional[str]:
    v = _clean(val)
    return None if v is None else str(v).strip()


def _load_state(path: Path) -> dict:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"version": 1, "projects": {}}


def _save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _project_key(row: dict) -> str:
    """Stable key for a project row (uses genUnitId/INR or a hash of the name)."""
    uid = row.get("genUnitId")
    if uid and str(uid).strip() not in ("", "0", "nan"):
        return str(uid)
    name = str(row.get("genPlantName", "")) + str(row.get("queueId", ""))
    return hashlib.sha256(name.encode()).hexdigest()[:16]


def _update_state(state: dict, row: dict, text: str) -> None:
    state.setdefault("projects", {})[_project_key(row)] = {
        "genPlantName": row.get("genPlantName"),
        "last_run": datetime.now(timezone.utc).isoformat(),
        "last_output": text,
    }


#input normalization
def _is_ercot_schema(df: pd.DataFrame) -> bool:
    cols = set(df.columns)
    return "INR" in cols and ("projectCod" in cols or "projectName" in cols)


def _ercot_facts_block(r: dict) -> str:
    """Interconnection / permitting milestones handed to Claude as a starting point."""
    lines: List[str] = []

    def add(label: str, val, is_date: bool = False):
        if _clean(val) is None:
            return
        lines.append(f"- {label}: {_fmt_date(val) if is_date else _cleanstr(val)}")

    fuel = _cleanstr(r.get("fuel")) or ""
    tech = _cleanstr(r.get("technology")) or ""
    ft = " / ".join(x for x in (fuel, tech) if x)
    if ft:
        lines.append(f"- Fuel / Technology: {ft}")
    add("Capacity (MW)", r.get("capacityMw"))
    add("County (TX)", r.get("county"))
    add("CDR reporting zone", r.get("cdrReportingZone"))
    add("Point of interconnection", r.get("poiLocation"))
    add("Interconnecting entity", r.get("interconnectingFacility"))
    add("Reported / target COD (projectCod)", r.get("projectCod"), is_date=True)
    add("GINR study phase", r.get("ginrStudyPhase"))
    add("Screening study started", r.get("screeningStudyStarted"), is_date=True)
    add("Screening study complete", r.get("screeningStudyComplete"), is_date=True)
    add("Full Interconnection Study (FIS) requested", r.get("fisRequested"), is_date=True)
    add("FIS approved", r.get("fisApproved"), is_date=True)
    add("Interconnection Agreement (IA) signed", r.get("iaSigned"), is_date=True)
    add("Financial security & Notice to Proceed provided", r.get("financialSecurityAndNoticeToProceedProvided"))
    add("Air permit", r.get("airPermit"))
    add("GHG permit", r.get("ghgPermit"))
    add("Water availability", r.get("waterAvailability"))
    add("Construction start", r.get("constructionStart"), is_date=True)
    add("Construction end", r.get("constructionEnd"), is_date=True)
    add("Meets ERCOT Planning Guide §6.9.1 (criteria met on)", r.get("meetsSection691"), is_date=True)
    add("Comments", r.get("comments"))
    return "\n".join(lines)


def _normalize_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Canonical row dicts. ERCOT columns are mapped; other schemas pass through."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    raw_rows = df.to_dict(orient="records")

    if not _is_ercot_schema(df):
        return raw_rows

    rows: List[Dict[str, Any]] = []
    for r in raw_rows:
        inr = _cleanstr(r.get("INR"))
        rows.append({
            "genUnitId": inr,
            "queueId": inr,
            "genPlantName": _cleanstr(r.get("projectName")) or "Unknown Project",
            "UnitName": _cleanstr(r.get("projectName")),
            "genFuelType": _cleanstr(r.get("fuel")) or "",
            "maxMW": r.get("capacityMw"),
            "OnlineDate": r.get("projectCod"),          # reported in-service date
            "State": "TX",
            "City": _cleanstr(r.get("county")) or "",
            "TransmissionZone": _cleanstr(r.get("cdrReportingZone")) or "",
            "unitOwner": _cleanstr(r.get("interconnectingFacility")) or "",
            "url": "",
            "notes": _cleanstr(r.get("comments")) or "",
            "_facts": _ercot_facts_block(r),
        })
    return rows

#prompt building
def _fmt_date(val) -> str:
    if _clean(val) is None:
        return "Unknown"
    try:
        if isinstance(val, (datetime, pd.Timestamp)):
            return pd.Timestamp(val).strftime("%Y-%m-%d")
        ts = pd.Timestamp(val)
        if not pd.isna(ts):
            return ts.strftime("%Y-%m-%d")
    except Exception:
        pass
    return str(val)


def _fmt_mw(val) -> str:
    try:
        f = float(val)
        return f"{f:,.1f}" if f != int(f) else f"{int(f):,}"
    except Exception:
        return str(val)


def _parse_cod(response: str) -> Optional[datetime]:
    """Extract **COD-ESTIMATE: YYYY-MM** and return a datetime."""
    import re
    m = re.search(r"COD-ESTIMATE:\s*(\d{4})-(\d{2})", response)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), 1)
        except ValueError:
            pass
    return None


def _parse_latlon(response: str) -> Optional[str]:
    """Extract **LATLON: <lat>, <lon>** and return 'lat, lon' (or None)."""
    import re
    m = re.search(r"LATLON:\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)", response)
    if m:
        return f"{m.group(1)}, {m.group(2)}"
    return None


def _months_diff(a: datetime, b: datetime) -> int:
    return (a.year - b.year) * 12 + (a.month - b.month)


def build_messages(row: dict, previous_output: Optional[str], previous_timestamp: Optional[str]) -> List[Dict[str, Any]]:
    """Build the system/user messages for a single project row."""

    fuel_code = str(row.get("genFuelType", "")).strip().upper()
    fuel_label = FUEL_LABELS.get(fuel_code, fuel_code)

    name     = row.get("genPlantName") or row.get("UnitName") or "Unknown Project"
    mw       = _fmt_mw(row.get("maxMW", ""))
    location = f"{row.get('City', '')}, {row.get('State', '')}".strip(", ")
    queue_id = _cleanstr(row.get("queueId")) or ""
    owner    = _cleanstr(row.get("unitOwner")) or ""
    notes    = _cleanstr(row.get("notes")) or ""
    url      = _cleanstr(row.get("url")) or ""
    zone     = _cleanstr(row.get("TransmissionZone")) or ""
    facts    = _cleanstr(row.get("_facts")) or ""

    project_block = (
        f"- **Project Name**: {name}\n"
        f"- **Capacity**: {mw} MW\n"
        f"- **Fuel / Technology**: {fuel_label}\n"
        f"- **Location**: {location}\n"
        f"- **Interconnection Queue ID**: {queue_id if queue_id and queue_id != '0' else 'N/A'}\n"
        f"- **Reporting / Transmission Zone**: {zone if zone else 'N/A'}\n"
        f"- **Owner / Developer**: {owner if owner and owner != '0' else 'Unknown'}\n"
    )
    if notes:
        project_block += f"- **Internal Notes**: {notes}\n"
    if url:
        project_block += f"- **Reference URL**: {url}\n"

    facts_block = ""
    if facts:
        facts_block = (
            "## Known Interconnection & Permitting Milestones\n"
            "(from ERCOT interconnection tracking — use as a starting point; verify with web search)\n"
            f"{facts}\n\n"
        )

    tag_instruction = (
        "**Important**: At the very end of your response, include these two machine-readable "
        "lines exactly (substitute real values; no other format accepted):\n"
        "`**COD-ESTIMATE: YYYY-MM**`\n"
        "`**LATLON: <latitude>, <longitude>**`  — approximate site coordinates in decimal degrees "
        "(from the point of interconnection / location; if you truly cannot determine them, write UNKNOWN)."
    )

    system = (
        "You are a senior power-industry analyst with deep expertise in ERCOT generation "
        "interconnection (the GINR process and ERCOT Planning Guide Section 6.9), Texas permitting "
        "(TCEQ air/GHG, water), and renewable-energy project development timelines. You have web "
        "search and web fetch tools — use them to find the most recent public information about the "
        "specific project (developer announcements, ERCOT filings, TCEQ permits, county records, "
        "trade-press/news, construction progress). Prefer primary and recent sources; cite them for "
        "material claims, and do not fabricate sources, filings, or dates.\n\n"
        "Structure every response using the exact Markdown headings below — do NOT omit any section, "
        "even with limited information. Be concise and factual; use bullet points where appropriate. "
        "Do not wrap the response in a code block."
    )

    if not previous_output:
        user = (
            f"Please research the following power generation project and provide a structured update.\n\n"
            f"## Project Details\n{project_block}\n"
            f"{facts_block}"
            "---\n\n"
            "Respond using **exactly** these three Markdown sections:\n\n"
            "### 1. Project Status Summary\n"
            "Summarize what this project is and its current overall development status "
            "(e.g., pre-construction, financial close, under construction, commissioning).\n\n"
            "### 2. Permitting & Interconnection Updates\n"
            "List the most recent interconnection study progress (screening, FIS, IA), financial "
            "security / notice-to-proceed, permitting (air, GHG, water), construction milestones, and "
            "any known delays or issues. Include dates and source citations where known.\n\n"
            "### 3. Independent COD Estimate\n"
            "Based on the information above and your web research, provide your best independent "
            "estimate of when this project will reach Commercial Operations. State a specific month "
            "and year, explain the key factors, and note whether it looks on track vs. the reported COD.\n"
            f"{tag_instruction}"
        )
    else:
        prev_label = previous_timestamp or "previous run"
        user = (
            f"Please provide an updated research report for the following power generation project.\n\n"
            f"## Project Details\n{project_block}\n"
            f"{facts_block}"
            f"---\n\n"
            f"**Previous report (from {prev_label}):**\n{previous_output}\n\n"
            "---\n\n"
            "Focus on what has **changed** since the previous report. Use exactly these sections:\n\n"
            "### 1. Project Status Summary\n"
            "Briefly note the current status and any changes since the previous report.\n\n"
            "### 2. Permitting & Interconnection Updates\n"
            "List only NEW developments since the previous report. If nothing new: state "
            "'No new updates found.'\n\n"
            "### 3. Independent COD Estimate\n"
            "Provide your current best estimate of COD. Note if your estimate has changed and why.\n"
            f"{tag_instruction}"
        )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


#claude code cli querie
def _messages_to_prompt(messages: List[Dict[str, Any]]) -> str:
    """Flatten system+user messages into one prompt string."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    user = "\n\n".join(m["content"] for m in messages if m["role"] == "user")
    return f"{system}\n\n{user}" if system else user


def run_query(messages: List[Dict[str, Any]], cli_path: str, model: str, timeout: int) -> Dict[str, Any]:
    """Research the project via the headless Claude Code CLI (live WebSearch/WebFetch).

    Uses stream-json so we can count the ACTUAL WebSearch/WebFetch tool calls the
    agent makes across all turns
    Returns {text, cost, web_searches, web_fetches, num_turns}. The prompt is passed
    on stdin so long prompts don't hit command-line length limits.
    """
    prompt = _messages_to_prompt(messages)
    #Least privilege read-only research, so allow ONLY the web tools and auto-deny
    #everything else 'dontAsk' denies un-allowed tools automatically (no prompt,
    # no hang) — so Claude cannot run Bash or write/delete/modify any files.
    cmd = [
        cli_path, "-p",
        "--output-format", "stream-json", "--verbose",
        "--allowedTools", "WebSearch,WebFetch",
        "--disallowedTools", "Bash,Write,Edit,NotebookEdit",
        "--permission-mode", "dontAsk",
        "--model", model,
    ]
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                              encoding="utf-8", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"text": f"**Error (claude cli)**: timed out after {timeout}s", "cost": 0.0, "web_searches": 0}
    except FileNotFoundError:
        return {"text": f"**Error (claude cli)**: executable not found at {cli_path}", "cost": 0.0, "web_searches": 0}

    if proc.returncode != 0:
        return {"text": f"**Error (claude cli, rc={proc.returncode})**: {(proc.stderr or '')[-800:]}",
                "cost": 0.0, "web_searches": 0}

    # Parse the newline-delimited JSON event stream.
    text, cost, num_turns, err = "", 0.0, None, False
    web_searches = web_fetches = 0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        etype = ev.get("type")
        if etype == "assistant":
            for block in (ev.get("message", {}) or {}).get("content", []) or []:
                if isinstance(block, dict) and block.get("type") in ("tool_use", "server_tool_use"):
                    nm = block.get("name")
                    if nm == "WebSearch":
                        web_searches += 1
                    elif nm == "WebFetch":
                        web_fetches += 1
        elif etype == "result":
            text = ev.get("result", "") or text
            cost = float(ev.get("total_cost_usd") or cost)
            num_turns = ev.get("num_turns")
            err = bool(ev.get("is_error"))

    if err:
        text = f"**Error (claude cli)**: {text}"
    if not text:
        text = f"**Error (claude cli)**: no result parsed from stream (rc={proc.returncode})"
    return {"text": text, "cost": cost, "web_searches": web_searches,
            "web_fetches": web_fetches, "num_turns": num_turns}


def _score_row(row: dict, response: str, previous_timestamp) -> Dict[str, Any]:
    """Parse Claude's COD estimate + coordinates and compute variance vs the reported COD."""
    cod = _parse_cod(response)
    latlon = _parse_latlon(response)
    our_cod_raw = _clean(row.get("OnlineDate"))
    try:
        our_cod_dt = pd.Timestamp(our_cod_raw).to_pydatetime().replace(tzinfo=None) if our_cod_raw is not None else None
    except Exception:
        our_cod_dt = None

    variance_months = None
    cod_str = "Could not parse"
    if cod:
        cod_str = cod.strftime("%Y-%m")
        if our_cod_dt:
            variance_months = _months_diff(cod, our_cod_dt.replace(day=1))

    return {
        "row": row,
        "response": response,
        "previous_timestamp": previous_timestamp,
        "claude_cod_str": cod_str,
        "latlon": latlon or "—",
        "cod_variance_months": variance_months,
    }



def save_markdown(projects_output: List[Dict[str, Any]], output_dir: Path,
                  model_label: str, total_cost: float) -> Path:
    """Write all project results to a single timestamped Markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_file = output_dir / f"gen_research_{timestamp}.md"

    alert_projects = [
        p for p in projects_output
        if p.get("cod_variance_months") is not None and abs(p["cod_variance_months"]) > 6
    ]

    #the estimated cost here only accures after exceeding session limits, so the value may not reflect any actual cost incurred for this run
    lines = [
        "# Generation Research — Project Status Report\n",
        f"- **Run date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Projects covered**: {len(projects_output)}",
        f"- **Model**: {model_label} (Claude Code CLI, live web search)",
        f"- **Estimated cost**: ${total_cost:,.4f}",
        "",
        "> _Generated with AI (Claude Code + web search). Coordinates are an approximate sanity "
        "check. Please verify cited sources independently._",
        "",
    ]

    if alert_projects:
        lines.append(f"> **⚠ COD VARIANCE ALERT — {len(alert_projects)} project(s) differ from the reported COD by more than 6 months:**")
        for ap in alert_projects:
            aname = ap["row"].get("genPlantName") or "Unknown"
            diff = ap["cod_variance_months"]
            claude_d = ap.get("claude_cod_str", "?")
            our_d = _fmt_date(ap["row"].get("OnlineDate"))
            direction = "later" if diff > 0 else "earlier"
            lines.append(f"> - **{aname}**: Claude {claude_d} vs. reported {our_d} ({abs(diff)} months {direction})")
        lines.append("")

    lines += ["---", ""]

    for idx, proj in enumerate(projects_output, 1):
        row = proj["row"]
        fuel_code = str(row.get("genFuelType", "")).strip().upper()
        fuel_label = FUEL_LABELS.get(fuel_code, fuel_code)
        name = row.get("genPlantName") or row.get("UnitName") or "Unknown"
        our_cod = _fmt_date(row.get("OnlineDate"))
        queue_id = _cleanstr(row.get("queueId")) or ""
        mw = _fmt_mw(row.get("maxMW", ""))
        location = f"{row.get('City', '')}, {row.get('State', '')}".strip(", ")
        owner = _cleanstr(row.get("unitOwner")) or ""
        cod_str = proj.get("claude_cod_str", "Could not parse")
        latlon = proj.get("latlon", "—")
        variance = proj.get("cod_variance_months")

        lines.append(f"## {idx}. {name}")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        lines.append(f"| Capacity | {mw} MW |")
        lines.append(f"| Fuel / Technology | {fuel_label} |")
        lines.append(f"| Location | {location} |")
        lines.append(f"| Coordinates (lat, lon) | {latlon} |")
        lines.append(f"| Queue ID | {queue_id if queue_id and queue_id != '0' else 'N/A'} |")
        lines.append(f"| Owner / Developer | {owner if owner and owner != '0' else 'Unknown'} |")
        lines.append(f"| Reported COD | {our_cod} |")
        lines.append(f"| Claude COD Estimate | {cod_str} |")
        if variance is not None:
            direction = "later" if variance > 0 else "earlier"
            flag = " ⚠" if abs(variance) > 6 else " ✓"
            lines.append(f"| COD Variance | {abs(variance)} months {direction}{flag} |")
        lines.append("")

        lines.append(proj["response"])

        if variance is not None and abs(variance) > 6:
            direction = "later" if variance > 0 else "earlier"
            lines.append("")
            lines.append("> **⚠ COD VARIANCE ALERT**")
            lines.append(f"> Claude estimates COD in **{cod_str}**, which is **{abs(variance)} months {direction}** ")
            lines.append(f"> than the reported COD of **{our_cod}**.")
            lines.append("> See Section 3 above for the reasoning behind Claude's estimate.")

        lines.append("")
        lines.append("---")
        lines.append("")

    md_file.write_text("\n".join(lines), encoding="utf-8")
    return md_file


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Research generation projects via the Claude Code CLI")
    parser.add_argument("--model", type=str, default=None, help="Model alias (sonnet|opus|haiku|fable). Default: CLAUDE_CODE_MODEL")
    parser.add_argument("--concurrency", type=int, default=None, help="Number of projects to research in parallel")
    parser.add_argument("--delta", action="store_true", help="Pass previous response as context so Claude returns only changes")
    parser.add_argument("--project", type=str, default=None, help="Only query projects whose name contains this string (case-insensitive)")
    parser.add_argument("--excel", type=str, default=None, help="Path to the input workbook (newGen691.xlsx, gen_research.xlsx, etc)")
    args = parser.parse_args()

    if not args.excel:
        raise ValueError("Excel file path must be provided via --excel argument.")

    excel_file = Path(args.excel)
    model = (args.model or CLAUDE_CODE_MODEL or "sonnet").strip()
    cli_path = CLAUDE_CLI_PATH
    timeout = CLAUDE_CODE_TIMEOUT
    concurrency = max(1, args.concurrency or CLAUDE_CODE_CONCURRENCY)

    print("Generation Research Runner (Claude Code CLI)")
    print(f"Time        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model       : {model}   |   concurrency {concurrency}")
    print(f"Mode        : {'delta (using previous responses as context)' if args.delta else 'full (fresh research, no prior context)'}")
    print(f"Excel       : {excel_file}")

    if not excel_file.exists():
        raise FileNotFoundError(f"Input workbook not found: {excel_file}")

    state = _load_state(STATE_FILE)
    df = pd.read_excel(excel_file)
    rows = _normalize_rows(df)
    print(f"Loaded {len(rows)} projects from Excel\n")

    if args.project:
        filt = args.project.lower()
        rows = [r for r in rows if filt in str(r.get("genPlantName", "")).lower()]
        if not rows:
            raise ValueError(f"No projects matched '{args.project}'.")
        print(f"Filtered to {len(rows)} project(s) matching '{args.project}'\n")

    n = len(rows)

    def work(item):
        i, row = item
        entry = state.get("projects", {}).get(_project_key(row), {})
        prev_out = entry.get("last_output") if args.delta else None
        prev_ts = entry.get("last_run") if args.delta else None
        messages = build_messages(row, prev_out, prev_ts)
        res = run_query(messages, cli_path, model, timeout)
        return i, row, prev_ts, res

    results: Dict[int, Any] = {}
    done = 0
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(work, (i, row)) for i, row in enumerate(rows, 1)]
        for fut in as_completed(futures):
            i, row, prev_ts, res = fut.result()
            done += 1
            name = row.get("genPlantName") or f"Project {i}"
            extra = f", {res.get('web_searches', 0)} searches, {res.get('web_fetches', 0)} fetches"
            print(f"[{done:2d}/{n}] {str(name)[:45]:45s} done (${res['cost']:.3f}{extra})")
            results[i] = (row, prev_ts, res)

    projects_output: List[Dict[str, Any]] = []
    total_cost = 0.0
    for i in sorted(results):
        row, prev_ts, res = results[i]
        total_cost += res["cost"]
        _update_state(state, row, res["text"])
        projects_output.append(_score_row(row, res["text"], prev_ts))
    _save_state(STATE_FILE, state)

    print(f"\nQueried: {len(projects_output)}")
    print(f"Total estimated cost: ${total_cost:,.4f}")
    md_file = save_markdown(projects_output, OUTPUT_DIR, model, total_cost)
    print(f"✓ Report saved: {md_file.name}")
