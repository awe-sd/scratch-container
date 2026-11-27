# powerflow_analytics

SCOPF study results → CRR opportunity finder. One command, `pfa`, run from the repo root with `uv run pfa <command>`;
`uv run pfa --help` lists the commands and `uv run pfa <command> --help` shows a command's arguments.
Conventions and data rules are in `CLAUDE.md`.

## Setup (once per study)

```
uv run pfa pull --study 14412
```
Extracts the study from Snowflake into `cache/study_14412/` (parquet; gitignored). Every later step reads the cache.

## The funnel

Worked example: study 14412, outage cutoff 2026-09-15, settlement month 2026-09.

1. **summary** — rank every binding constraint with rent, outage-ticket drivers, marginal units and tofinder evidence.
   ```
   uv run pfa summary --study 14412 --cutoff 2026-09-15 --tickets
   ```
   Writes `output/study_14412/`: `ranked_constraints.csv`, `base_case_binders.csv`, `marginal_units.csv`, `tofinder_summary.csv`.

2. **shortlist** — classify the universe (A target / B baseline / C no-dispatch / D bearish / weak), detect flips, gate to the
   candidates worth a look and value each for the month (outage days, coverage, on-peak P(bind), shadow price, cheapest path SF, edge).
   ```
   uv run pfa shortlist --study 14412 --cutoff 2026-09-15 --month 2026-09
   ```
   Writes `output/study_14412/`: `step1_screen.csv` (classified universe), `step1_flips.csv`, `stage2_list.csv` and `stage2_list.html`
   (the shortlist with value columns), `constraint_dirs.csv`. Gate thresholds are options (`--share-min`, `--post-days-min`,
   `--rent-min`, `--nqual-min`, `--intensity-min-hard`, `--intensity-min-full`, `--penalty-share-max`).

3. **deep-dive** — wind/solar binding thresholds, dispatch profile and price formation for one or more shortlisted constraints.
   ```
   uv run pfa deep-dive --study 14412 --constraint "1436-2081-1@DWCSRAM5" \
       --history-start 2026-04-01 --history-end 2026-09-28 --month 2026-09
   ```
   Writes `output/study_14412/deep_dive_<labels>.md` (or `--out`).

4. **paths** — cheapest paths that are long every required constraint, from PathOpt runs. Needs `pyopenssl`:
   ```
   uv run --with "pyopenssl>=26.4" pfa paths --study 14966 --out-dir output/pathopt/14966_dblbywf5 \
       --min-sf-each 0.05 --pool 300 --holidays 2026-12-25 \
       --runs JCKSTP18A=10023193,JCKREF27A=10023204,BLESSING1382=10023214 \
       --required JCKSTP18A,JCKREF27A,BLESSING1382 \
       --constraints JCKSTP18A=5915-42530-18@DBLBYWF5,JCKREF27A=42400-42530-27@DBLBYWF5,BLESSING1382=8121-8123-1@DBLBYWF5
   ```
   Writes `report.html`, candidate CSVs and `README.md` to the `--out-dir` (default `output/pathopt/<study>_multi`).

## Other commands

| Command | Purpose |
|---|---|
| `value` | Fact sheet and on-peak monthly $/MWh mark for one constraint (`--study --constraint --month [--window START END]`) |
| `compare` | Persisting vs new constraints between two studies (`--study-a --study-b --month`); writes `comparison_<b>_vs_<a>.html` and CSVs in `output/study_<b>/` |
| `lambda-dist` | Shadow-price distribution for one constraint from DAM offers and fast-scan (`--study --constraint`) |
| `pull` | Extract a study into the cache (`--study [--refresh]`) |
| `history` | Realized ISO constraint history for a monitored element (`--monitored PATTERN`) |
| `offers` | DAM generator offer pull (`--start --end [--summary]`) |
| `load-profile` | Median ERCOT load profile figure (`--start MM-DD --end MM-DD`) |
| `headroom` | Fast-scan headroom scatter for one constraint, HTML (`--study --fromnum --tonum --ctglabel --hist-start --hist-end --out`) |

The old `scripts/<name>.py` command lines still work; each is a shim for the matching `pfa` command.

## Dashboard

`uv run powerflow_analytics/app/app.py` → http://127.0.0.1:8050 (reads only local files). **Explorer**: ranked binding constraints
with binding-hours profile, marginal units and tofinder outage evidence. **Comparison**: constraint deltas between two analyzed studies.

## Module map (`pfa/`)

- `extract/` — one reader per data source (Snowflake / SQL Server); the only place SQL lives.
- `analysis/` — calculations that return DataFrames or plain data (screening, valuation, deep dive, path search, study compare, summary); never build pages.
- `report/` — the one rendering layer: `html.py` toolkit (page shell, sections, filterable/sortable tables from a column spec, Plotly blocks), `markdown.py`, and one module per report.
- `cli/` — `pfa <sub-command>`: argument parsing, calls into analysis and report, file writing.

## Tests

`uv run pytest -q`
