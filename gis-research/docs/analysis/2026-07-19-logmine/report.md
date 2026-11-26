# gis-research agent log forensics

Deterministic parse of every run stream under `gis-research/research/<INR>_<slug>/`.
Corpus: **943 runs** (779 triage + 164 deep), **57,865 tool calls**, ~$1,393 total spend.

- Parser: `parse_streams.py` -> `tool_sequences.parquet`/`.csv` (one row per tool call), `per_run_summary.csv`, `failure_inrs.csv`, `validation.txt`.
- Aggregation: `aggregate.py` -> `stats.json`; loop detail `stuck_loops.csv`; sample narratives `narratives.py`.
- **Validation gate**: parsed per-run `tool_counts` equal `meta.audit.tool_counts` for **941/943** runs. The 2 exceptions (`20INR0162_diamondback-solar`, `25INR0554_dan-kearney-bess`, both deep) are stream/meta inconsistencies -- the on-disk stream was truncated/overwritten by a later partial re-run while the meta reflects the earlier full run. Hanson sanity run matches exactly (Write 3 / Bash 2 / Read 3 / Edit 2 = 10).

## Tool-call totals

| tool | deep | triage | | tool | deep | triage |
|---|---:|---:|---|---|---:|---:|
| WebFetch | 13,371 | 12,521 | | Read | 2,539 | 1,142 |
| Bash | 8,983 | 9,675 | | Write | 344 | 2,473 |
| Edit | 109 | 4,296 | | Glob | 285 | 828 |
| ToolSearch | 205 | 771 | | Agent | 87 | 5 |

WebFetch is 45% of all tool calls. Bash (18,658) is ~1,000 curl calls plus shell/`uv run` tool invocations.

---

## (a) WebFetch breakdown

25,892 WebFetch calls (13,371 deep / 12,521 triage). Top domains:

| domain | deep | triage | total | error rate | note |
|---|---:|---:|---:|---:|---|
| html.duckduckgo.com | 350 | 3,010 | 3,360 | 4.3% | search scraping |
| www.bing.com | 1,079 | 2,264 | 3,343 | 0.1% | search scraping |
| comptroller.texas.gov | 722 | 2,515 | 3,237 | 4.1% | Ch.313/local-gov registries |
| **interchange.puc.texas.gov** | 621 | 2,390 | **3,011** | **100.0%** | **3,010 are HTTP 402** |
| efts.sec.gov | 936 | 33 | 969 | **100.0%** | SEC EDGAR full-text API, all fail |
| www.ercot.com | 828 | 139 | 967 | 71.4% (class) | |
| nominatim.openstreetmap.org | 163 | 373 | 536 | (maps 20.8%) | |
| mycpa.cpa.state.tx.us | 319 | 71 | 390 | -- | TX Comptroller entity search |
| search.yahoo.com | 252 | 0 | 252 | 8.7% | |
| oeaaa.faa.gov | 168 | 48 | 216 | 62.5% | FAA OE/AAA (blocked 2026-07) |
| propaccess.trueautomation.com | -- | -- | 55 | 38.2% | county CAD |
| www.eia.gov | 146 | 44 | 190 | 18.9% | |

**Error rate by domain class** (WebFetch only):

| class | calls | errors | rate |
|---|---:|---:|---:|
| search (ddg/bing/yahoo/google) | 7,260 | 176 | 2.4% |
| comptroller | 3,776 | 223 | 5.9% |
| **puct_portal** | 3,447 | 3,446 | **100.0%** |
| maps | 1,572 | 327 | 20.8% |
| ercot | 1,204 | 860 | 71.4% |
| **sec** | 1,196 | 1,196 | **100.0%** |
| county_cad | 959 | 430 | 44.8% |
| news_pr | 607 | 421 | 69.4% |
| faa | 263 | 170 | 64.6% |
| tceq | 227 | 101 | 44.5% |
| eia | 213 | 57 | 26.8% |

**Findings:**
- **The PUCT Interchange portal is WebFetched 3,011 times and returns HTTP 402 every single time** (3,010/3,011). The playbook explicitly says *"use `puct.py match`, never raw WebFetch (the portal rate-limits ad-hoc fetches to HTTP 402)"* -- yet agents ignore it wholesale. These 402s carry `is_error: null`, so a flag-only analysis would have reported 0 errors; detection here is content-based (`"402 Payment Required"`).
- **SEC EDGAR full-text search (`efts.sec.gov`) fails 100% (969 calls)** and `www.sec.gov` adds 227 more at ~100% -- 1,196 dead fetches to SEC.
- **County CADs (44.8%), FAA (64.6%), TCEQ (44.5%), ercot.com (71.4%), news/PR (69.4%)** are all high-failure targets -- these portals block or 404 ad-hoc fetches.
- **Search-engine HTML scraping** (ddg/bing/yahoo) is 7,260 calls (28% of all WebFetch): the agents run web search by fetching search-engine result pages, not via the `WebSearch` tool.
- **Retries**: 658 WebFetch calls (2.5%) re-fetch a URL already fetched earlier in the same run, across 234 runs; 50 are back-to-back identical-URL repeats.
- *Caveat*: `puct_portal`/`sec` rates are exact (specific-string / genuine ~100%); mid-tier class rates (`other` 59.9%, `ercot` 71.4%, `news_pr` 69.4%) are **upper bounds** -- the content regex can match HTTP-status-like strings inside page bodies, so treat those as approximate.

---

## (b) Failure taxonomy (75 non-success runs)

The task's "52 deep + 13 triage" counts are the **meta-recorded** non-success runs. Including 10 runs whose stream exists but whose meta file was never written (hardest kills), there are **75 non-success runs**. Cleanly unified by kill mechanism (verified via `exit_code` and `audit.violations`):

| bucket | deep | triage | total | signature |
|---|---:|---:|---:|---|
| **token_budget_kill** | 30 | 3 | **33** | exit 143 (runner SIGTERM at budget+grace); `"token budget exceeded (killed)"` violation |
| **max_turns** | 22 | 6 | **28** | hit SDK `num_turns` cap (exit 0/1) |
| **hard_kill_no_record** | 5 | 9 | **14** | exit -9 (SIGKILL) / -1; no meta file, no result line, nothing recorded |

The `run_meta.subtype` field splits the token-budget kills three ways that are **not real differences**, only hook-timing artifacts: 15 land as `error_during_execution` **with** a `.budget_exhaust_sent` marker (the PostToolUse hook fired the "STOP now" message before the runner killed), 13 as `error_during_execution` **without** the marker, and 5 as `None`-subtype meta. All 33 carry the same `"token budget exceeded > {100000|400000} (killed)"` violation and exit 143. **Zero of the `error_during_execution` runs had an actual API error** (`api_error_status` is null for all). Deep budget = 400k fresh tokens, triage = 100k.

**What the token-killed agents were doing in their last 10 tool calls** (137 web_research, 130 shell/other, 28 imagery, only **24 wrap-up**, 4 queue): they were **still researching, not wrapping up**. Checked against files on disk, **23 of the 33 token-killed runs produced no `findings.json`/`dossier.md` at all** (only 10 persisted output); across all 75 non-success runs, **39 produced no findings/dossier/triage output.** The budget-exhaust "write your files NOW" message largely fails to redirect the agent in time -- the direct cause of the 74 "output file missing" violations in (c). (Note: the `hard_kill_no_record` bucket is heterogeneous -- all 10 triage runs in it actually finished writing outputs before the process was killed pre-result; the no-output runs are concentrated in the deep token-kills.)

Budget/token kills and max-turns runs burn the most wall-clock (medians 12.4 min and 19.5 min vs 5.2 min for success).

---

## (c) Violations (68 deep runs + 10 triage runs; 137 entries: 126 deep, 11 triage)

Reconciliation of the task's "68 deep violations": **68 deep runs carry >=1 violation, and those 68 runs book 126 violation entries total** (a token-killed run typically logs three: `dossier.md missing` + `findings.json missing` + `token budget exceeded (killed)`). 10 triage runs carry 11 entries.

| violation category | count | meaning |
|---|---:|---|
| output_file_missing: `dossier.md` | 35 | deep run never wrote its dossier |
| output_file_missing: `findings.json` | 31 | deep run never wrote structured findings |
| output_file_missing: `triage_findings.json` (+1 missing-keys) | 8 | triage/deep never wrote triage output |
| **token_budget_exceeded_killed** | 33 | runner hard-killed at fresh-token cap |
| **image_read_over_cap** | 30 | read 7-16 images vs the 6-image cap |

**74 of 137 violations (54%) are missing-output-file violations** -- the agent was killed (or ran out of turns) before persisting its work. The 33 token-kill violations are the same 33 runs from (b). The 30 image-cap violations are runs that read 7-16 satellite/contact-sheet images against a documented cap of 6.

---

## (d) Stuck-loop motifs (>=5 consecutive identical tool + arg-fingerprint)

**363 loop episodes across 209 runs.** Top motifs by total wasted calls:

| tool | fingerprint | episodes | max run | total calls | what it is |
|---|---|---:|---:|---:|---|
| WebFetch | comptroller.texas.gov/economy/local | 63 | 12 | 343 | hammering Ch.313/local-gov registry pages |
| Bash curl | interchange.puc.texas.gov | 38 | **26** | 330 | curl-ing the 402 portal (same as (a), via curl) |
| WebFetch | efts.sec.gov/LATEST/search-index | 35 | 26 | 272 | SEC EDGAR FTS, all failing |
| WebFetch | www.bing.com/search | 38 | 24 | 253 | repeated Bing search variants |
| Bash | `uv run ...` | 29 | 11 | 180 | local tool retries |
| Bash curl | www.sec.gov | 13 | 16 | 95 | SEC, failing |
| Bash curl | overpass-api.de | 14 | 10 | 86 | OSM Overpass geometry |
| Bash curl | *cad.org (refugio/upton/...) | several | 21 | -- | county CAD scraping |

**The two worst motifs are exactly the two 100%-failure targets from (a):** agents get stuck curling `interchange.puc.texas.gov` up to **26 times in a row** (every one a 402) and hammering `efts.sec.gov` up to 26 times in a row (every one failing). The single longest loop is 26 consecutive curls to the PUCT portal in `27INR0536` deep. These are retry storms against endpoints the agent cannot access -- not productive search-space exploration.

---

## (e) Turn-budget spend by stage & replaceability

Stages approximated per the requested heuristic (queue-parquet/`queue_history.py`=stage0; `spv/puct/faa/ch313/tceq/eia_history` resolvers=identity; WebFetch/curl-to-web=web_research bucketed by domain class; `cdse.py`/`gmaps.py`/image reads=imagery; Write/Edit of findings/dossier/brief/log=wrap-up).

| stage | deep total | triage total | deep avg/run | triage avg/run | % of all calls |
|---|---:|---:|---:|---:|---:|
| web_research | 16,958 | 12,728 | **103.4** | 16.3 | **51.3%** |
| other (shell: ls/cat/mkdir, Glob, ToolSearch, Task*) | 6,384 | 5,879 | 38.9 | 7.5 | 21.2% |
| wrap-up | 431 | 6,613 | 2.6 | 8.5 | 12.2% |
| imagery | 2,116 | 4,846 | 12.9 | 6.2 | 12.0% |
| stage0_queue | 250 | 1,660 | 1.5 | 2.1 | 3.3% |

- **A deep run spends 103 tool calls on web research on average** -- half of everything. `identity` (the local resolvers puct/spv/faa/ch313/tceq) barely registers as its own stage because those calls are rare relative to raw web fetching.
- **Replaceable by local systematic tools that now exist**: of 29,700 web calls (WebFetch + curl-to-domain), **12,708 (42.8%) hit a domain with a direct local replacement** (`puct_portal`->`puct.py match`+on-disk IA PDFs 4,314; `search`->`WebSearch` 7,465; `eia`->`eia_history.py` 270; `faa`->`faa.py` 350; `tceq`->`tceq.py` 309; `sec`->`spv.py` 1,531). That is **22.0% of ALL 57,865 tool calls**. Including partial-coverage domains (`comptroller`->`ch313.py`, `sec`->`spv.py`) pushes it to **18,367 web calls = 61.8% of web / 31.7% of all tool calls.**
- **Search-engine scraping alone** (7,260 WebFetch to ddg/bing/yahoo) is 28% of WebFetch / 12.5% of all calls and is directly replaceable by the `WebSearch` tool.
- The single highest-leverage fix: **the 3,011 WebFetch + ~330 curl calls to the 402-only PUCT portal are 100% wasted and 100% replaceable by `puct.py match` against the local docket index and the IA PDFs already on disk.** SEC (1,196 dead fetches) is covered by `spv.py`'s EIA-860M/docket-index path.

---

## (f) Sample-run path narratives (from `narratives.py`)

### 5 worst-cost deep runs

1. **24INR0339 mystic-springs -- $15.72, 37 turns, 387 calls, success.** 344/387 calls are web_research. Burns the whole budget on Bing (183 fetches, incl. one 24-in-a-row loop and an 18-in-a-row loop) + SEC EDGAR (two loops of 14 and 13). 57 HTTP-4xx + 8 402s + 16 tool errors. Only reaches wrap-up (`build_brief`/`build_index`) in the final 3 calls. A run that succeeded but at ~5x the median cost because it brute-forced search engines.
2. **26INR0269 moccasin -- $13.16, 120 turns, 576 calls, success.** 456 web_research; 197 HTTP-4xx + 66 tool errors + 14 402s. Long web sprints of 98->76->81->131->47 consecutive fetches to Engie sites, ERCOT, SEC, KTXS news, interleaved with imagery (`cdse.py`). Wrap-up (dossier/findings/brief) only at the very end.
3. **26INR0113 meitner-wind -- $13.03, 192 turns, 188 calls, success.** Fewer web calls (61) but 192 turns and 36 imagery calls -- cost driven by turn count and a 10-image `cdse.py` burst (gray-county CAD hunt) plus an 8-deep `TaskCreate` loop.
4. **23INR0070 chillingham -- $12.50, 35 turns, 105 calls, exec_error (token-kill).** Starts with 18 shell calls, then scattered web research; hits a 5-in-a-row curl loop against `interchange.puc.texas.gov` (all 402). Killed at the token cap while chasing EIA electricity endpoints; last calls are `uv`/curl/WebFetch -- never wrapped up.
5. **27INR0084 aegle-power -- $12.13, 117 turns, 113 calls, success.** Modest fetch count but 117 turns; repeated `build_brief.py` rebuilds at the end (build -> read -> edit findings -> rebuild) and an 8-deep `TaskCreate` loop inflate turns.

### 5 budget-killed deep runs (highest cost)

6. **26INR0375 avalon-bess -- $6.89, 260 calls, token-kill.** 212 web_research. Multiple retry storms: 11-in-a-row empty Bash, 8- and 6-in-a-row curls to the 402 PUCT portal, DDG loop. Last calls are WebFetch to `interchange.puc` + `fbcad`, then re-reading its own `triage_findings`/`log` -- killed mid-research, minimal output.
7. **23INR0056 caliche-mound -- $5.60, 351 calls, token-kill.** 316 web_research, and it went on a **202-consecutive-web-fetch** sprint (SEC EDGAR 73 calls, comptroller 21, deaf-smith CAD 11, FERC eLibrary). 149 HTTP-4xx + 48 tool errors. Managed a last-second `findings.json`/`log.md` write before the SIGTERM.
8. **21INR0324 board-creek-wind -- $5.03, 365 calls, token-kill (exit 143).** A **235-consecutive-web-fetch** block (Engie 36, SEC 25, USGS wind map 16, EIA 14, thewindpower 12, FAA 10) -- 168 HTTP-4xx + 45 tool errors. Only wrote `triage_findings.json` (not the deep `findings.json`/`dossier.md`) before being killed.
9. **25INR0591 zeus-rusk-bess -- $3.80, 156 calls, token-kill.** 121 web_research incl. loops on `data.texas.gov` (7x) and comptroller local/development (5x each). Ends spawning an `Agent` + `ToolSearch` + two more 402 PUCT fetches right as it dies.
10. **20INR0255 renegade -- $3.69, 224 calls, token-kill.** 160 web_research + 15 imagery. A 108-consecutive-web-fetch block (SEC, blueplanetfunding, deaf-smith CAD, Google/DDG). Did reach wrap-up (findings/dossier written) plus a trailing `queue_history.py`.

**Common thread:** cost and death are dominated by *raw web research* -- long uninterrupted fetch sprints (100-235 calls) against high-failure or 402-only portals (PUCT, SEC, county CADs, developer sites), with search-engine scraping and retry loops on top. The local systematic tools that now exist (`puct.py`, `spv.py`, `faa.py`, on-disk IA PDFs, `WebSearch`) target exactly these buckets.

---

## Top-8 quantitative findings

1. The PUCT Interchange portal was WebFetched **3,011 times with a 100% HTTP-402 failure rate** (plus ~330 curls), despite the playbook banning raw fetches of it -- the single largest pool of wasted, fully-replaceable calls.
2. **web_research is 51.3% of all 57,865 tool calls**; a deep run averages **103 web fetches**, and **42.8% of the 29,700 web calls (22% of ALL tool calls) hit a domain with a now-existing local replacement** (61.8%/31.7% counting partial-coverage tools).
3. Of 75 non-success runs, **33 are token-budget kills** (exit 143 runner SIGTERM), **28 max-turns**, **14 hard-killed before the SDK emitted a result** -- and **39 of the 75 produced no findings/dossier/triage output on disk** (23 of the 33 token-kills wrote nothing).
4. **SEC EDGAR (`efts.sec.gov`) fails 100% across 969 fetches** (SEC as a class: 1,196 dead calls) -- the second-biggest dead-fetch bucket, fully covered by `spv.py`.
5. **137 audit violations, 54% (74) are "output file missing"** (`dossier.md` 35, `findings.json` 31) -- the direct cost of agents researching until killed instead of persisting work.
6. **363 stuck-loop episodes across 209 runs**; the two worst motifs are retry storms against the two 100%-failure endpoints -- up to **26 consecutive curls to the 402 PUCT portal** and 26 consecutive SEC-EDGAR fetches.
7. **Search-engine HTML scraping (ddg/bing/yahoo) is 7,260 WebFetch calls (28% of all WebFetch, 12.5% of all tool calls)** done in place of the available `WebSearch` tool.
8. Total spend **~$1,393** (deep $660, mean $4.26/run, max $15.72; triage $732, mean $0.95/run); the 5 worst deep runs alone cost **$66**, all driven by 100-450 web fetches per run.

Report + artifacts in this directory.
