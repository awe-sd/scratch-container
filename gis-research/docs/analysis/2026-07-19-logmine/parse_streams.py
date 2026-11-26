#!/usr/bin/env python3
"""Deterministic parser for gis-research agent run streams.

Walks research/<INR>_<slug>/, parses run_stream_{triage,deep}.jsonl line-by-line
(skipping the non-JSON warning line), emits one row per tool call plus per-run summary.
Outputs: tool_sequences.parquet/.csv, per_run_summary.csv, failure_inrs.csv (+ validation report).
"""
import json, re, sys
from pathlib import Path
from datetime import datetime
import pandas as pd

RESEARCH = Path("/workspaces/scratch-workspace/.claude/worktrees/GIS-research/gis-research/research")
OUT = Path("/tmp/claude-1000/-workspaces-scratch-workspace/f07f0766-08e4-46c8-9188-c0e2b33c332c/scratchpad/logmine")

# --- research_tools script names (invoked via Bash) ---
RT_SCRIPTS = {"puct.py","spv.py","eia_history.py","eia_snapshot.py","cdse.py","gmaps.py",
              "ch313.py","faa.py","tceq.py","queue_history.py","ia_match_sweep.py","ia_backfill.py",
              "inr_harvest.py","build_brief.py","build_index.py","deep_worker.py","make_deep_queue.py",
              "run_agent.py","run_batch.py","build_queue_report.py","download_gis_parquet.py",
              "explore_gis_schema.py","find_gis_objects.py"}
IDENTITY_SCRIPTS = {"puct.py","spv.py","eia_history.py","eia_snapshot.py","ch313.py","faa.py",
                    "tceq.py","ia_match_sweep.py","ia_backfill.py","inr_harvest.py"}
IMAGERY_SCRIPTS = {"cdse.py","gmaps.py"}
QUEUE_SCRIPTS = {"queue_history.py"}
WRAPUP_FILES = ("findings.json","dossier.md","triage_findings.json","triage.md","log.md",
                "timeline.json","timeline.md","brief.html","dossier_v1_verbose.md")

def domain_of(url):
    m = re.match(r'https?://([^/]+)', url or "")
    return m.group(1).lower() if m else ""

def path_prefix(url):
    m = re.match(r'https?://[^/]+(/[^?#]*)', url or "")
    if not m: return ""
    parts = [p for p in m.group(1).split('/') if p][:2]
    return "/".join(parts)

def domain_class(dom):
    d = dom.lower()
    if any(s in d for s in ("duckduckgo","bing.com","yahoo.com","google.com")): return "search"
    if "interchange.puc.texas.gov" in d or "puc.texas.gov" in d: return "puct_portal"
    if "comptroller.texas.gov" in d or "mycpa.cpa.state.tx" in d: return "comptroller"
    if any(s in d for s in ("cad","trueautomation","propaccess","appraisal")): return "county_cad"
    if "ercot" in d: return "ercot"
    if "sec.gov" in d: return "sec"
    if any(s in d for s in ("openstreetmap","nominatim","overpass","openinframap","usgs")): return "maps"
    if "faa.gov" in d: return "faa"
    if "eia.gov" in d: return "eia"
    if "tceq" in d: return "tceq"
    if "sos.state.tx" in d: return "sos"
    if any(s in d for s in ("prnewswire","businesswire","linkedin","wikipedia","gem.wiki","thewindpower","reuters","bloomberg")): return "news_pr"
    if any(s in d for s in ("opencorporates","bizapedia","corporationwiki")): return "registry"
    if "gov.texas.gov" in d or "data.texas.gov" in d: return "gov_other"
    return "other"

# domain classes with a NOW-existing local systematic tool (question e)
REPLACEABLE = {"puct_portal":"yes","eia":"yes","faa":"yes","tceq":"yes","search":"yes",
               "comptroller":"partial","sec":"partial"}

ENV_ASSIGN = re.compile(r'^\s*(?:sudo\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|\'[^\']*\'|\S+)\s+)+')
def resolve_bash(cmd):
    """Return (script_or_binary, subcmd, curl_domain). Detect research_tools script anywhere."""
    if not cmd: return ("", "", "")
    low = cmd
    # research_tools script anywhere?
    for sc in RT_SCRIPTS:
        idx = low.find(sc)
        if idx != -1:
            after = low[idx+len(sc):].lstrip()
            sub = ""
            m = re.match(r'([a-z][a-z0-9_\-]+)', after)
            if m and m.group(1) not in ("py",): sub = m.group(1)
            return (sc, sub, "")
    # curl / wget -> domain
    if re.search(r'\b(curl|wget)\b', cmd):
        m = re.search(r'https?://[^\s"\'\\)>]+', cmd)
        return ("curl", "", domain_of(m.group(0)) if m else "")
    # else first meaningful token after stripping env/cd/source/timeout
    seg = cmd.split("&&")[0]
    for _ in range(4):
        seg2 = ENV_ASSIGN.sub("", seg)
        seg2 = re.sub(r'^\s*cd\s+\S+\s*(&&|;)?\s*', "", seg2)
        seg2 = re.sub(r'^\s*source\s+\S+\s*(&&|;)?\s*', "", seg2)
        seg2 = re.sub(r'^\s*timeout\s+[\d.]+\s*', "", seg2)
        if seg2 == seg: break
        seg = seg2
    tok = seg.strip().split()
    binary = tok[0] if tok else ""
    binary = binary.strip('"\'').split("/")[-1]
    if binary in ("uv","python3","python"):
        m = re.search(r'([\w\-]+\.py)', cmd)
        if m: return (m.group(1), "", "")
        return (binary, "", "")
    return (binary, "", "")

def basename(p): return (p or "").rstrip("/").split("/")[-1]

def classify_stage(tool, script, arg_full, fp, dom, curl_dom):
    if tool == "WebFetch": return "web_research"
    if tool == "Bash":
        if script in QUEUE_SCRIPTS: return "stage0_queue"
        if script in IDENTITY_SCRIPTS: return "identity"
        if script in IMAGERY_SCRIPTS: return "imagery"
        if script == "curl" and curl_dom: return "web_research"
        if re.search(r'ercot_generation_interconnect.*\.parquet|queue_history', arg_full or ""): return "stage0_queue"
        return "other"
    if tool in ("Write","Edit"):
        if any(w in (arg_full or "") for w in WRAPUP_FILES): return "wrapup"
        return "other"
    if tool == "Read":
        b = basename(arg_full)
        if re.search(r'\.(png|jpg|jpeg)$', b, re.I) or "imagery" in (arg_full or "") or "contact_sheet" in (arg_full or ""): return "imagery"
        return "other"
    return "other"

def extract_result_text(cont):
    if isinstance(cont, str): return cont
    if isinstance(cont, list):
        return " ".join((x.get("text","") if isinstance(x,dict) else str(x)) for x in cont)
    return str(cont) if cont is not None else ""

HTTP_RE = re.compile(r'HTTP\s+(\d{3})|returned HTTP (\d{3})|status(?:\s*code)?[:=]?\s*(\d{3})')
def fetch_outcome(err_flag, text):
    t = text or ""
    if "402 Payment" in t or "Payment Required" in t: return ("http_402", 402)
    m = HTTP_RE.search(t)
    status = None
    if m:
        status = int(next(g for g in m.groups() if g))
    if status and 400 <= status < 500: return ("http_4xx", status)
    if status and 500 <= status < 600: return ("http_5xx", status)
    if err_flag is True or "<tool_use_error>" in t: return ("tool_error", status)
    return ("ok", status)

def parse_stream(path, inr, mode):
    """Return (rows, meta_from_result, first_ts, last_ts)."""
    tooluses = []   # ordered list of dicts
    results = {}    # tool_use_id -> (err_flag, text)
    result_meta = None
    first_ts = last_ts = None
    for line in path.open(errors="replace"):
        line = line.strip()
        if not line.startswith("{"): continue
        try: d = json.loads(line)
        except Exception: continue
        ts = d.get("timestamp")
        if ts:
            if first_ts is None: first_ts = ts
            last_ts = ts
        typ = d.get("type")
        if typ == "assistant":
            for c in d.get("message",{}).get("content",[]):
                if isinstance(c,dict) and c.get("type")=="tool_use":
                    tooluses.append({"id":c.get("id"),"name":c.get("name"),"input":c.get("input",{}),"ts":ts})
        elif typ == "user":
            for c in d.get("message",{}).get("content",[]):
                if isinstance(c,dict) and c.get("type")=="tool_result":
                    results[c.get("tool_use_id")] = (c.get("is_error"), extract_result_text(c.get("content")))
        elif typ == "result":
            result_meta = d
    rows = []
    prev_ts = None
    for i,tu in enumerate(tooluses):
        tool = tu["name"]; inp = tu["input"] or {}
        err_flag, rtext = results.get(tu["id"], (None, ""))
        arg_full=""; fp=""; dom=""; script=""; subcmd=""; curl_dom=""; outcome="ok"; status=None
        if tool == "WebFetch":
            url = inp.get("url","")
            arg_full = url
            dom = domain_of(url)
            fp = dom + ("/"+path_prefix(url) if path_prefix(url) else "")
            outcome, status = fetch_outcome(err_flag, rtext)
        elif tool == "Bash":
            cmd = inp.get("command","")
            arg_full = re.sub(r'\s+'," ",cmd).strip()[:400]
            script, subcmd, curl_dom = resolve_bash(cmd)
            if script == "curl":
                dom = curl_dom
                fp = "curl:"+curl_dom
                outcome, status = fetch_outcome(err_flag, rtext)
            else:
                fp = script + (":"+subcmd if subcmd else "")
                if err_flag is True or "<tool_use_error>" in (rtext or "") or (rtext or "").startswith("Error"): outcome="tool_error"
        elif tool in ("Read","Write","Edit"):
            fp = basename(inp.get("file_path",""))
            arg_full = inp.get("file_path","")
            if err_flag is True or "<tool_use_error>" in (rtext or ""): outcome="tool_error"
        elif tool in ("Glob","Grep"):
            fp = (inp.get("pattern","") or "")[:60]
            arg_full = fp
            if err_flag is True: outcome="tool_error"
        else:
            fp = tool
            arg_full = json.dumps(inp)[:120]
            if err_flag is True or "<tool_use_error>" in (rtext or ""): outcome="tool_error"
        dcls = domain_class(dom) if dom else ""
        repl = REPLACEABLE.get(dcls,"no") if (tool=="WebFetch" or (tool=="Bash" and script=="curl")) else ""
        is_err = outcome != "ok"
        gap = None
        if tu["ts"] and prev_ts:
            try:
                a=datetime.fromisoformat(prev_ts.replace("Z","+00:00")); b=datetime.fromisoformat(tu["ts"].replace("Z","+00:00"))
                gap=(b-a).total_seconds()
            except Exception: pass
        prev_ts = tu["ts"] or prev_ts
        stage = classify_stage(tool, script, arg_full, fp, dom, curl_dom)
        rows.append(dict(inr=inr, mode=mode, seq_no=i, tool_name=tool, arg_fingerprint=fp,
                         arg_full=arg_full, domain=dom, domain_class=dcls, script=script, subcmd=subcmd,
                         is_error=is_err, err_flag=(err_flag is True), outcome=outcome, http_status=status,
                         replaceable=repl, stage=stage, gap_s=gap, ts=tu["ts"]))
    return rows, result_meta, first_ts, last_ts

def main():
    all_rows=[]; summaries=[]; mism=[]
    dirs = sorted([p for p in RESEARCH.iterdir() if p.is_dir() and not p.name.startswith("_")])
    for d in dirs:
        inr = d.name.split("_")[0]
        for mode in ("triage","deep"):
            stream = d / f"run_stream_{mode}.jsonl"
            if not stream.exists(): continue
            metaf = d / f"run_meta_{mode}.json"
            meta = {}
            if metaf.exists():
                try: meta = json.loads(metaf.read_text())
                except Exception: meta = {}
            rows, rmeta, first_ts, last_ts = parse_stream(stream, inr, mode)
            all_rows.extend(rows)
            # validation: parsed tool counts vs meta.audit.tool_counts
            audit = meta.get("audit",{}) or {}
            mt = audit.get("tool_counts",{}) or {}
            parsed_counts = {}
            for r in rows: parsed_counts[r["tool_name"]] = parsed_counts.get(r["tool_name"],0)+1
            if mt and parsed_counts != mt:
                mism.append((d.name, mode, mt, parsed_counts))
            # terminal state
            subtype = meta.get("subtype")
            has_exhaust = (d/".budget_exhaust_sent").exists()
            has_warn = (d/".budget_warn_sent").exists()
            has_deepfail = (d/".deep_failed").exists()
            if subtype is None:
                term = "hung_hardkilled"
            elif subtype == "success":
                term = "success"
            elif subtype == "error_max_turns":
                term = "max_turns"
            elif subtype == "error_during_execution":
                term = "budget_kill" if has_exhaust else "exec_error"
            else:
                term = subtype
            # per-stage counts
            stage_counts={}
            for r in rows: stage_counts[r["stage"]]=stage_counts.get(r["stage"],0)+1
            # wallclock
            wall=None
            if first_ts and last_ts:
                try: wall=(datetime.fromisoformat(last_ts.replace("Z","+00:00"))-datetime.fromisoformat(first_ts.replace("Z","+00:00"))).total_seconds()
                except: pass
            last10 = " > ".join(f"{r['tool_name']}:{r['arg_fingerprint']}"[:40] for r in rows[-10:])
            viols = audit.get("violations",[]) or []
            summaries.append(dict(inr=inr, mode=mode, dir=d.name, subtype=subtype, terminal_state=term,
                is_error=meta.get("is_error"), total_cost_usd=meta.get("total_cost_usd"),
                num_turns=meta.get("num_turns"), assistant_turns=audit.get("assistant_turns"),
                image_reads=audit.get("image_reads"), n_tool_calls=len(rows),
                violations_n=len(viols), violations=json.dumps(viols),
                exhaust=has_exhaust, warn=has_warn, deep_failed=has_deepfail,
                api_error_status=(rmeta or {}).get("api_error_status"),
                fresh_tokens=meta.get("fresh_tokens"), token_budget=meta.get("token_budget"),
                exit_code=meta.get("exit_code"), wallclock_s=wall,
                stage_counts=json.dumps(stage_counts), last10=last10))
    df = pd.DataFrame(all_rows)
    df.to_parquet(OUT/"tool_sequences.parquet", index=False)
    df.to_csv(OUT/"tool_sequences.csv", index=False)
    sdf = pd.DataFrame(summaries)
    sdf.to_csv(OUT/"per_run_summary.csv", index=False)
    # failure_inrs
    fail = sdf[sdf.terminal_state!="success"].copy()
    fail["last_activity_summary"] = fail["last10"]
    fail[["inr","mode","terminal_state","last_activity_summary"]].to_csv(OUT/"failure_inrs.csv", index=False)
    # validation report
    with (OUT/"validation.txt").open("w") as f:
        f.write(f"total tool-call rows: {len(df)}\n")
        f.write(f"runs parsed: {len(sdf)} (triage {sum(sdf['mode']=='triage')}, deep {sum(sdf['mode']=='deep')})\n")
        f.write(f"tool_count mismatches vs meta.audit.tool_counts: {len(mism)}\n")
        for name,mode,mt,pc in mism[:40]:
            f.write(f"  MISMATCH {name} {mode}: meta={mt} parsed={pc}\n")
    print(f"rows={len(df)} runs={len(sdf)} mismatches={len(mism)}")
    print("terminal_state x mode:")
    print(sdf.groupby(["mode","terminal_state"]).size())

if __name__=="__main__":
    main()
