#!/usr/bin/env python3
"""Per-run path narratives for sample runs, built from tool_sequences.parquet."""
import pandas as pd, json
from pathlib import Path
OUT=Path("/tmp/claude-1000/-workspaces-scratch-workspace/f07f0766-08e4-46c8-9188-c0e2b33c332c/scratchpad/logmine")
df=pd.read_parquet(OUT/"tool_sequences.parquet")
s=pd.read_csv(OUT/"per_run_summary.csv")

def narrate(inr,mode):
    g=df[(df.inr==inr)&(df["mode"]==mode)].sort_values("seq_no")
    row=s[(s.inr==inr)&(s["mode"]==mode)].iloc[0]
    print(f"\n### {row['dir']} [{mode}]  cost=${row['total_cost_usd']} turns={row['num_turns']} calls={len(g)} state={row['terminal_state']}")
    # stage counts
    print("  stage calls:", g.stage.value_counts().to_dict())
    # top web domains
    web=g[g.tool_name=="WebFetch"]
    if len(web): print("  top WebFetch domains:", web.domain.value_counts().head(6).to_dict())
    # error breakdown
    print("  outcomes:", g.outcome.value_counts().to_dict())
    # consecutive loops within this run (>=5)
    key=list(zip(g.tool_name,g.arg_fingerprint)); i=0; loops=[]
    while i<len(key):
        j=i
        while j+1<len(key) and key[j+1]==key[i]: j+=1
        if j-i+1>=5: loops.append((key[i],j-i+1))
        i=j+1
    if loops: print("  stuck loops(>=5):",loops)
    # compressed stage timeline (run-length of stages)
    stages=list(g.stage); tl=[]; i=0
    while i<len(stages):
        j=i
        while j+1<len(stages) and stages[j+1]==stages[i]: j+=1
        tl.append(f"{stages[i]}x{j-i+1}"); i=j+1
    print("  stage timeline:"," > ".join(tl[:40]))
    print("  last 8 calls:", " | ".join(f"{r.tool_name}:{r.arg_fingerprint}"[:34] for _,r in g.tail(8).iterrows()))

print("="*70); print("5 WORST-COST DEEP")
for inr in ["24INR0339","26INR0269","26INR0113","23INR0070","27INR0084"]:
    narrate(inr,"deep")
print("\n"+"="*70); print("5 BUDGET-KILLED DEEP (highest cost)")
for inr in ["26INR0375","23INR0056","21INR0324","25INR0591","20INR0255"]:
    narrate(inr,"deep")
