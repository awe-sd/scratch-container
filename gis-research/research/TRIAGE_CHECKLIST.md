# TRIAGE v2 — interpret the factsheet, don't rediscover it

Budget: ~15 assistant turns, 40k fresh tokens. The factsheet (below your packet, or
run `uv run gis-research/scripts/research_tools/factsheet.py <INR> --write`) already
holds queue history, EIA second source, SPV/registry candidates, IA status, and a
deterministic paper score with named factors. Your job is judgment, not collection.

T1 READ the factsheet. List (internally) its 2–3 weakest facts — the ones that, if
   wrong, flip the verdict.
T2 IDENTITY SANITY: do SPV/EIA/registry candidates cohere (same entity family, same
   county, compatible size)? Contradictions are findings — record them.
T3 CONTEST THE SCORE with at most 10 targeted web checks aimed at the weakest facts:
   cancellation/suspension news, financing/PPA announcements, developer project page,
   county news. Use `search.py "<query>"` (never scrape search engines; the PUCT
   portal and SEC are blocked — puct.py/spv.py are the doors). An empty result is
   negative evidence: record it, move on.
T4 VERDICT: `paper_dismissed` | `deep_candidate` | `ambiguous`, consistent with the
   gate unless you adjust the score. You may adjust ±15 points MAX and ONLY with a
   cited source (URL + one-line quote/paraphrase in `score_adjustment.citation`).
T5 WRITE `triage_findings.json` (all prior schema fields PLUS
   `score_adjustment {delta, citation}`) and `triage.md` (≤40 lines: verdict, the
   factors you confirmed/contested, citations). Files on disk are all that survives.
