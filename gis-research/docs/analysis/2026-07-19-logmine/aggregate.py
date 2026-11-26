#!/usr/bin/env python3
"""Aggregate tool_sequences.parquet + per_run_summary.csv into report numbers."""
import pandas as pd, json, collections
from pathlib import Path
OUT = Path("/tmp/claude-1000/-workspaces-scratch-workspace/f07f0766-08e4-46c8-9188-c0e2b33c332c/scratchpad/logmine")
df = pd.read_parquet(OUT/"tool_sequences.parquet")
s = pd.read_csv(OUT/"per_run_summary.csv")
R = {}
def p(*a): print(*a)

# ---------- overview ----------
p("="*70); p("OVERVIEW")
R["total_tool_calls"]=len(df)
R["by_mode"]=df.groupby("mode").size().to_dict()
R["tool_by_mode"]=df.groupby(["mode","tool_name"]).size().unstack(fill_value=0).to_dict("index")
p("total tool calls:",len(df),"| by mode:",R["by_mode"])
p(df.groupby(["mode","tool_name"]).size().unstack(fill_value=0).T.to_string())

# ---------- (a) WebFetch breakdown ----------
p("="*70); p("(a) WEBFETCH BREAKDOWN")
wf = df[df.tool_name=="WebFetch"].copy()
R["webfetch_total"]=len(wf); R["webfetch_by_mode"]=wf.groupby("mode").size().to_dict()
p("WebFetch total:",len(wf),"by mode:",R["webfetch_by_mode"])
# top domains triage vs deep
dom_mode = wf.groupby(["domain","mode"]).size().unstack(fill_value=0)
dom_mode["total"]=dom_mode.sum(axis=1)
dom_mode=dom_mode.sort_values("total",ascending=False)
p("\nTop 20 WebFetch domains (triage/deep/total):")
p(dom_mode.head(20).to_string())
R["top_domains"]=dom_mode.head(25).reset_index().to_dict("records")
# error rate per domain
err = wf.groupby("domain").agg(calls=("is_error","size"), errors=("is_error","sum")).sort_values("calls",ascending=False)
err["err_rate"]=(err["errors"]/err["calls"]*100).round(1)
# 402 specifically
wf["is402"]=wf.outcome=="http_402"
puct402 = wf[wf.domain=="interchange.puc.texas.gov"]
p("\ninterchange.puc.texas.gov: calls=%d, 402s=%d (%.1f%%), other-err=%d"%(
    len(puct402), puct402.is402.sum(), 100*puct402.is402.mean() if len(puct402) else 0,
    (puct402.is_error & ~puct402.is402).sum()))
R["puct_calls"]=int(len(puct402)); R["puct_402"]=int(puct402.is402.sum())
p("\nerror rate for key domains:")
outc = wf.groupby("domain")["outcome"].value_counts().unstack(fill_value=0)
for dom in ["interchange.puc.texas.gov","www.google.com","www.bing.com","html.duckduckgo.com",
            "search.yahoo.com","comptroller.texas.gov","efts.sec.gov","propaccess.trueautomation.com",
            "oeaaa.faa.gov","www.eia.gov"]:
    if dom in err.index:
        row=err.loc[dom]
        p("  %-34s calls=%5d err=%5d (%.1f%%)"%(dom,row.calls,row.errors,row.err_rate))
R["domain_err"]=err.head(30).reset_index().to_dict("records")
# error rate by domain_class
cls = wf.groupby("domain_class").agg(calls=("is_error","size"),err=("is_error","sum"))
cls["rate"]=(cls.err/cls.calls*100).round(1)
p("\nby domain_class:"); p(cls.sort_values("calls",ascending=False).to_string())
R["class_err"]=cls.reset_index().to_dict("records")
# retries: same URL fetched >1x within a run
def retry_stats(sub):
    dup=0; runs_with_dup=set()
    for (inr,mode),g in sub.groupby(["inr","mode"]):
        vc=g.arg_full.value_counts()
        d=(vc[vc>1]-1).sum()
        if d>0: runs_with_dup.add((inr,mode))
        dup+=d
    return int(dup), len(runs_with_dup)
tot_dup, runs_dup = retry_stats(wf)
p("\nRETRIES (same exact URL re-fetched within a run): %d redundant WebFetch calls across %d runs (%.1f%% of WebFetch)"%(
    tot_dup, runs_dup, 100*tot_dup/len(wf)))
R["webfetch_retries"]=tot_dup; R["webfetch_retry_runs"]=runs_dup
# consecutive same-URL
def consec_same(sub, col):
    total=0
    for (inr,mode),g in sub.groupby(["inr","mode"]):
        vals=list(g.sort_values("seq_no")[col]); run=1
        for i in range(1,len(vals)):
            if vals[i]==vals[i-1] and vals[i]: run+=1
            else:
                if run>=2: total+=run-1
                run=1
        if run>=2: total+=run-1
    return total
p("consecutive same-URL WebFetch (back-to-back identical url): %d"%consec_same(wf,"arg_full"))

# ---------- (b) failure taxonomy ----------
p("="*70); p("(b) FAILURE TAXONOMY")
fail = s[s.terminal_state!="success"]
p("terminal_state x mode (all non-success):")
p(fail.groupby(["mode","terminal_state"]).size().to_string())
R["failure_tax"]=fail.groupby(["mode","terminal_state"]).size().to_dict()
# budget-kill: last-10 tool stage distribution
p("\nBudget-kill (deep+triage) last-10-tool-call STAGE distribution:")
bk=s[s.terminal_state=="budget_kill"]
stage_last10=collections.Counter()
for _,r in bk.iterrows():
    g=df[(df.inr==r.inr)&(df["mode"]==r["mode"])].sort_values("seq_no").tail(10)
    for st in g.stage: stage_last10[st]+=1
p("  ",dict(stage_last10))
R["budgetkill_last10_stage"]=dict(stage_last10)
# max_turns last-10 stage
p("\nMax_turns last-10-tool stage distribution:")
mt=s[s.terminal_state=="max_turns"]; stmt=collections.Counter()
for _,r in mt.iterrows():
    g=df[(df.inr==r.inr)&(df["mode"]==r["mode"])].sort_values("seq_no").tail(10)
    for st in g.stage: stmt[st]+=1
p("  ",dict(stmt))
R["maxturns_last10_stage"]=dict(stmt)

# ---------- (c) violations ----------
p("="*70); p("(c) VIOLATIONS")
cat=collections.Counter()
for v in s[s.violations_n>0]["violations"]:
    for item in json.loads(v):
        it=str(item)
        if "missing" in it: cat["output_file_missing: "+it]+=1
        elif "image_reads" in it: cat["image_read_over_cap"]+=1
        elif "token budget" in it: cat["token_budget_exceeded_killed"]+=1
        else: cat["other: "+it[:60]]+=1
p("total violations: deep=%d triage=%d"%(s[s['mode']=='deep'].violations_n.sum(), s[s['mode']=='triage'].violations_n.sum()))
for k,n in cat.most_common(): p("  %3d  %s"%(n,k))
R["violations"]=dict(cat)
R["viol_deep"]=int(s[s['mode']=='deep'].violations_n.sum()); R["viol_triage"]=int(s[s['mode']=='triage'].violations_n.sum())

# ---------- (d) stuck loops ----------
p("="*70); p("(d) STUCK LOOPS (>=5 consecutive identical tool+arg_fingerprint)")
motifs=[]
for (inr,mode),g in df.groupby(["inr","mode"]):
    g=g.sort_values("seq_no"); key=list(zip(g.tool_name,g.arg_fingerprint))
    i=0
    while i<len(key):
        j=i
        while j+1<len(key) and key[j+1]==key[i]: j+=1
        L=j-i+1
        if L>=5: motifs.append((inr,mode,key[i][0],key[i][1],L))
        i=j+1
mdf=pd.DataFrame(motifs,columns=["inr","mode","tool","fp","runlen"])
p("total stuck-loop episodes (>=5 consecutive):",len(mdf),"across",mdf[['inr','mode']].drop_duplicates().shape[0],"runs")
p("\nby (tool, fingerprint) - top 20 motifs:")
p(mdf.groupby(["tool","fp"]).agg(episodes=("runlen","size"),max_len=("runlen","max"),total_calls=("runlen","sum")).sort_values("total_calls",ascending=False).head(20).to_string())
R["stuck_episodes"]=len(mdf)
R["stuck_top"]=mdf.groupby(["tool","fp"]).agg(episodes=("runlen","size"),max_len=("runlen","max"),total=("runlen","sum")).sort_values("total",ascending=False).head(15).reset_index().to_dict("records")
mdf.sort_values("runlen",ascending=False).to_csv(OUT/"stuck_loops.csv",index=False)
p("\nlongest 10 individual loops:")
p(mdf.sort_values("runlen",ascending=False).head(10).to_string())

# ---------- (e) stage spend + replaceable ----------
p("="*70); p("(e) STAGE SPEND per mode")
stg = df.groupby(["mode","stage"]).size().unstack(fill_value=0)
p("total calls per stage:"); p(stg.T.to_string())
# avg per run
nruns=s.groupby("mode").size()
avg = stg.div(nruns,axis=0).round(1)
p("\navg calls per RUN per stage:"); p(avg.T.to_string())
R["stage_total"]=stg.to_dict("index"); R["stage_avg_per_run"]=avg.to_dict("index")
# fraction of calls by stage
p("\nstage share of all tool calls:")
p((df.stage.value_counts(normalize=True)*100).round(1).to_string())
R["stage_share"]=(df.stage.value_counts(normalize=True)*100).round(1).to_dict()
# replaceable
web = df[(df.tool_name=="WebFetch")|((df.tool_name=="Bash")&(df.script=="curl"))].copy()
p("\nweb calls (WebFetch+curl):",len(web))
rep = web.groupby("replaceable").size()
p("replaceable tag on web calls:"); p(rep.to_string())
repl_yes = web[web.replaceable.isin(["yes"])]
repl_any = web[web.replaceable.isin(["yes","partial"])]
p("\nweb calls with a NOW-existing local tool (yes): %d = %.1f%% of web, %.1f%% of ALL tool calls"%(
    len(repl_yes), 100*len(repl_yes)/len(web), 100*len(repl_yes)/len(df)))
p("web calls replaceable yes+partial: %d = %.1f%% of web, %.1f%% of ALL tool calls"%(
    len(repl_any), 100*len(repl_any)/len(web), 100*len(repl_any)/len(df)))
R["web_total"]=len(web); R["repl_yes"]=len(repl_yes); R["repl_any"]=len(repl_any)
R["repl_yes_pct_all"]=round(100*len(repl_yes)/len(df),1); R["repl_any_pct_all"]=round(100*len(repl_any)/len(df),1)
# breakdown by domain_class for replaceable
p("\nreplaceable web calls by domain_class:")
p(repl_any.groupby("domain_class").size().sort_values(ascending=False).to_string())
R["repl_by_class"]=repl_any.groupby("domain_class").size().to_dict()
# search-scraping share (search engines via WebFetch)
srch=df[(df.tool_name=="WebFetch")&(df.domain_class=="search")]
p("\nSEARCH-ENGINE SCRAPING via WebFetch: %d = %.1f%% of WebFetch, %.1f%% of ALL tool calls (WebSearch tool exists)"%(
    len(srch),100*len(srch)/len(wf),100*len(srch)/len(df)))
R["search_scrape"]=len(srch); R["search_scrape_pct_wf"]=round(100*len(srch)/len(wf),1)
R["search_scrape_pct_all"]=round(100*len(srch)/len(df),1)

# ---------- cost ----------
p("="*70); p("COST")
p("total cost by mode:"); p(s.groupby("mode")["total_cost_usd"].agg(["sum","mean","max"]).round(2).to_string())
R["cost_by_mode"]=s.groupby("mode")["total_cost_usd"].agg(["sum","mean","max"]).round(3).to_dict("index")

def strkeys(o):
    if isinstance(o,dict): return {str(k):strkeys(v) for k,v in o.items()}
    if isinstance(o,list): return [strkeys(x) for x in o]
    return o
json.dump(strkeys(R), open(OUT/"stats.json","w"), indent=1, default=str)
p("\n[stats.json written]")
