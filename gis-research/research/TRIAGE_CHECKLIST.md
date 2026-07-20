# TRIAGE v2 — interpret the factsheet, don't rediscover it

Budget: ~15 assistant turns (hard verdict deadline: turn 20 — see T3), 120k fresh tokens.
If a BUDGET WARNING arrives at any point, skip directly to T5 and write files; a verdict
with what you have beats no verdict. The factsheet (below your packet, or
run `uv run gis-research/scripts/research_tools/factsheet.py <INR> --write`) already
holds queue history, EIA second source, SPV/registry candidates, IA status, and a
deterministic paper score with named factors. Your job is judgment, not collection.

T1 READ the factsheet. List (internally) its 2–3 weakest facts — the ones that, if
   wrong, flip the verdict.
T2 IDENTITY SANITY: do SPV/EIA/registry candidates cohere (same entity family, same
   county, compatible size)? Contradictions are findings — record them.
T3 CONTEST THE SCORE with at most 6 targeted `search.py "<query>"` calls aimed at the
   weakest facts: cancellation/suspension news, financing/PPA announcements, developer
   project page, county news (never scrape search engines; the PUCT portal and SEC are
   blocked — puct.py/spv.py are the doors). Do NOT WebFetch a result page unless its
   search-result snippet is decisive for the verdict — one such fetch, max. An empty
   result is negative evidence: record it, move on. HARD DEADLINE: commit a verdict by
   assistant turn 20 — if still uncertain then, verdict = `ambiguous` with whatever
   evidence you have; do not keep searching past it.
T4 VERDICT: `paper_dismissed` | `deep_candidate` | `ambiguous`, consistent with the
   gate unless you adjust the score. You may adjust ±15 points MAX and ONLY with a
   cited source (URL + one-line quote/paraphrase in `score_adjustment.citation`).
T5 WRITE `triage_findings.json` (all prior schema fields PLUS
   `score_adjustment {delta, citation}`) and `triage.md` (≤40 lines: verdict, the
   factors you confirmed/contested, citations). Files on disk are all that survives.
