"""Constraint valuation: a fact sheet and the monthly $/MWh mark.

Two halves with DIFFERENT binding definitions (pending an owner decision):
- fact_sheet(): binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2 (constraints.BINDING_PCT); lambda is
  OUTCONSTRAINT2.OPFCNLAMBDA over those runs; marginal units come from LPBASICVARID.
- binding_stats() / dollars_per_mwh(): binding = the run has a row for the constraint in
  OUTCONSTRAINT2; on-peak 5x16 only.

Fact-sheet marginal units: OUTCONSTRAINT2.GENBUSNUM/GENID are NULL for ERCOT studies, so the only
live identity is the free-text LPBASICVARID ("Gen 8968 #1 MW Control" resolves to a generator;
"Slack-Line ..." rows are dropped). Bus number -> name uses marginal_units.bus_name_map(outbranch2)
(a generator bus with no line-endpoint appearance in the cache is dropped, not guessed). PSENS comes
from CPNODE_SHIFTS_VIEW scoped to the constraint and CPNODEID.

Monthly mark (per constraint):
1. Binding stats from the study LP: P(bind | hour block) and the lambda distribution, restricted to
   the driving outage's window.
2. Normalize to $/MWh: expected rent per MW of flowgate over the month divided by the month's total
   on-peak hours (M-F 5x16, NERC holidays excluded).

Study runs sample a few hours (e.g. HE 3/12/18); each sampled hour represents a block of on-peak
hours (HOUR_BLOCKS). Scale a path by its shift factor on the flowgate to get $/MWh of CRR path.
The lambda cross-check from marginal-unit offers lives in shadow_price.
"""
from __future__ import annotations

from dataclasses import dataclass

import re

import pandas as pd

from .. import periods
from ..cache import StudyCache
from ..constraint_id import ConstraintId
from ..extract import gen_mapping, results, shifts, study
from .constraints import BINDING_PCT, constraint_key
from .marginal_units import bus_name_map
from .shadow_price import PRICE_CAP

_GEN_RE = re.compile(r"^Gen (\d+) #(\d+)")

# sampled sim-hour -> number of on-peak hours it represents (16h on-peak day)
HOUR_BLOCKS = {12: 10, 18: 6}  # midday block HE7-16, evening block HE17-22

def onpeak_days(year: int, month: int) -> pd.DatetimeIndex:
    """Business days (M-F minus NERC holidays) in a month."""
    return periods.onpeak_days(f"{year}-{month:02d}")


@dataclass
class BindingStats:
    constraint: str
    p_bind: dict[int, float]          # sim hour -> P(bind) within the window
    lam: pd.DataFrame                 # per sim hour: p25/p50/p75/mean of lambda
    window: tuple[str, str] | None    # outage window the stats are conditioned on
    n_window_runs: int


def binding_stats(
    outcon: pd.DataFrame,
    runs: pd.DataFrame,
    constraint: str,
    window: tuple[str, str] | None = None,
) -> BindingStats:
    """P(bind|sim hour) and lambda distribution, within the outage window."""
    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["CONSTRAINT"] = constraint_key(oc)
    c = oc[oc["CONSTRAINT"] == constraint].merge(
        runs[["RUNID", "SIMDATE", "SIMHOUR"]], on="RUNID"
    )
    r = runs.copy()
    if window is not None:
        in_win = (pd.to_datetime(r["SIMDATE"]) >= window[0]) & (
            pd.to_datetime(r["SIMDATE"]) <= window[1])
        r = r[in_win]
        c = c[(pd.to_datetime(c["SIMDATE"]) >= window[0])
              & (pd.to_datetime(c["SIMDATE"]) <= window[1])]
    tot = r.groupby("SIMHOUR")["RUNID"].nunique()
    bind = c.groupby("SIMHOUR")["RUNID"].nunique()
    p = (bind / tot).fillna(0.0).to_dict()
    lam = c.groupby("SIMHOUR")["OPFCNLAMBDA"].agg(
        p25=lambda s: s.quantile(0.25), p50="median",
        p75=lambda s: s.quantile(0.75), mean="mean",
    ).clip(upper=PRICE_CAP)
    return BindingStats(constraint, {int(k): float(v) for k, v in p.items()},
                        lam, window, int(r["RUNID"].nunique()))


def dollars_per_mwh(
    stats: BindingStats,
    year: int,
    month: int,
    outage_window: tuple[str, str],
    lam_col: str = "p50",
    sf: float = 1.0,
) -> dict:
    """Expected congestion $/MWh over the month's 5x16 block, per MW at `sf`.

    rent = sum over outage business days of sum over hour blocks of
           P(bind|block) x lambda x block hours; divided by total on-peak MWh.
    """
    days = onpeak_days(year, month)
    total_onpeak_h = len(days) * 16
    win = days[(days >= outage_window[0]) & (days <= outage_window[1])]
    rent_per_day = 0.0
    for hour, block_h in HOUR_BLOCKS.items():
        p = stats.p_bind.get(hour, 0.0)
        lam = float(stats.lam[lam_col].get(hour, 0.0)) if hour in stats.lam.index else 0.0
        rent_per_day += p * lam * block_h
    total_rent = rent_per_day * len(win) * sf
    return {
        "constraint": stats.constraint,
        "onpeak_days": len(days),
        "outage_onpeak_days": len(win),
        "rent_per_mw_month": round(total_rent, 2),
        "dollars_per_mwh": round(total_rent / total_onpeak_h, 3) if total_onpeak_h else 0.0,
        "lam_col": lam_col,
        "sf": sf,
    }


# ------------------------------------------------------------ fact sheet --

def _load_from_cache_or_snowflake(study_id: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (ctgviol, outcon, runs, branch), preferring the local parquet cache."""
    cache = StudyCache(study_id)
    if cache.has("outctgviol2") and cache.has("outconstraint2") and cache.has("opfrun") and cache.has("outbranch2"):
        return (
            cache.load("outctgviol2"),
            cache.load("outconstraint2"),
            cache.load("opfrun"),
            cache.load("outbranch2"),
        )
    return (results.fetch_ctgviol(study_id), results.fetch_constraint(study_id),
            study.fetch_runs(study_id), results.fetch_branch(study_id))


def fact_sheet(study_id: int, fromnum: int, tonum: int, ckt: str, ctglabel: str) -> dict:
    """Binding run count (LIMVIOLPCT >= 99.5 in OUTCTGVIOL2) + lambda distribution + marginal
    units + their PSENS, for one (study, FROMNUM, TONUM, CKT, CTGLABEL)."""
    ckt = str(ckt).strip()
    ctgviol, outcon, runs, branch = _load_from_cache_or_snowflake(study_id)

    n_total_runs = int(runs["RUNID"].nunique())

    cv = ctgviol[
        (ctgviol["FROMNUM"].astype(int) == int(fromnum))
        & (ctgviol["TONUM"].astype(int) == int(tonum))
        & (ctgviol["CKT"].astype(str).str.strip() == ckt)
        & (ctgviol["CTGLABEL"].astype(str).str.strip() == str(ctglabel).strip())
    ]
    n_total_cases = int(cv["RUNID"].nunique())
    binding = cv[cv["LIMVIOLPCT"] >= BINDING_PCT]
    binding_runids = set(binding["RUNID"].unique())
    n_binding_cases = int(binding["RUNID"].nunique())

    oc = outcon.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc_match = oc[
        (oc["FROMNUM"].astype(int) == int(fromnum))
        & (oc["TONUM"].astype(int) == int(tonum))
        & (oc["CKT"].astype(str).str.strip() == ckt)
        & (oc["CTGLABEL"].astype(str).str.strip() == str(ctglabel).strip())
    ]
    oc_binding = oc_match[oc_match["RUNID"].isin(binding_runids)]

    # OUTCONSTRAINT2 has one row per basic-variable per run — OPFCNLAMBDA is
    # constant per RUNID for a given constraint, so dedupe to RUNID before
    # computing distribution stats to avoid overweighting runs with many
    # marginal units.
    lam = oc_binding.dropna(subset=["OPFCNLAMBDA"]).drop_duplicates("RUNID")["OPFCNLAMBDA"]
    lambda_stats = {
        "min": float(lam.min()) if len(lam) else None,
        "p25": float(lam.quantile(0.25)) if len(lam) else None,
        "median": float(lam.median()) if len(lam) else None,
        "mean": float(lam.mean()) if len(lam) else None,
        "p75": float(lam.quantile(0.75)) if len(lam) else None,
        "max": float(lam.max()) if len(lam) else None,
        "n": int(len(lam)),
    }
    lambda_n_mismatch = lambda_stats["n"] != n_binding_cases
    if lambda_n_mismatch:
        print(
            f"WARNING: lambda_stats['n']={lambda_stats['n']} != n_binding_cases="
            f"{n_binding_cases} — OPFCNLAMBDA may not be constant per RUNID, or some "
            "binding RUNIDs have no OUTCONSTRAINT2 row for this constraint."
        )

    # --- marginal units: parse "Gen <busnum> #<id>" out of LPBASICVARID ---
    parsed_raw = oc_binding["LPBASICVARID"].astype(str).str.extract(_GEN_RE)
    parsed_raw.columns = ["BUSNUM", "GENID"]
    n_slack_line_dropped = int(parsed_raw["BUSNUM"].isna().sum())
    parsed = parsed_raw.dropna(subset=["BUSNUM"])
    parsed["BUSNUM"] = parsed["BUSNUM"].astype(int)
    unit_counts = parsed.groupby(["BUSNUM", "GENID"]).size().rename("N_APPEARANCES").reset_index()

    bnames = bus_name_map(branch)
    units = unit_counts.merge(bnames, on="BUSNUM", how="left")
    n_bus_unresolved = int(units["BUSNAME"].isna().sum())
    units = units.dropna(subset=["BUSNAME"])

    # GENUNIT has no column carrying the PowerWorld "#<id>" generator index
    # (UNITNAME/UNITCODE suffixes are a different, unrelated naming scheme —
    # see gen_mapping.fetch_genunit_sced_name docstring for the one place a
    # real (BUSNAME, unit-index) bridge exists, GENUNITSCEDNAME, which is not
    # wired in here). Rather than guess a wrong join or arbitrarily keep one
    # unit per bus (the old drop_duplicates("BUSNAME") behavior, which
    # silently mispriced any bus with multiple units), keep ALL matching
    # GENUNIT rows per bus and flag when a bus has more than one candidate
    # unit so disambiguation-was-not-possible is visible in the output.
    genunit = gen_mapping.fetch_genunit()
    bus_unit_counts = genunit.groupby("BUSNAME").size().rename("N_GENUNIT_CANDIDATES")
    units = units.merge(
        genunit[["BUSNAME", "UNITNAME", "CPNODEID", "GENFUELTYPE"]],
        on="BUSNAME", how="left",
    )
    units = units.merge(bus_unit_counts, on="BUSNAME", how="left")
    units["N_GENUNIT_CANDIDATES"] = units["N_GENUNIT_CANDIDATES"].fillna(0).astype(int)
    units["genunit_ambiguous"] = units["N_GENUNIT_CANDIDATES"] > 1
    units = units.sort_values(
        ["N_APPEARANCES", "BUSNUM", "GENID"], ascending=[False, False, False]
    ).reset_index(drop=True)

    # --- PSENS from CPNODE_SHIFTS_VIEW, scoped to this study + constraint ---
    # CPNODEID can come back float64 here (NaNs introduced by the left-joins
    # above) while Snowflake returns int64 for the SHIFT_FACTORS query —
    # cast both sides to nullable Int64 before merging so the join actually
    # matches instead of silently producing all-NaN PSENS.
    units["CPNODEID"] = units["CPNODEID"].astype("Int64")
    cpnode_ids = [int(c) for c in units["CPNODEID"].dropna().unique()]
    if cpnode_ids:
        sfs = shifts.cpnode_psens_by_id(
            study_id, ConstraintId(int(fromnum), int(tonum), ckt, str(ctglabel).strip()), cpnode_ids)
        sfs["CPNODEID"] = sfs["CPNODEID"].astype("Int64")
        units = units.merge(sfs, on="CPNODEID", how="left")
    else:
        units["PSENS"] = None

    marginal_units = units.head(10).to_dict(orient="records")

    return {
        "constraint": f"{fromnum}-{tonum}-{ckt}@{ctglabel}",
        "study_id": int(study_id),
        "n_binding_cases": n_binding_cases,
        "n_total_cases": n_total_cases,
        "n_total_study_runs": n_total_runs,
        "lambda_stats": lambda_stats,
        "lambda_n_mismatch": lambda_n_mismatch,
        "n_slack_line_dropped": n_slack_line_dropped,
        "n_bus_unresolved": n_bus_unresolved,
        "marginal_units": marginal_units,
    }


def mark_table(stats: BindingStats, year: int, month: int, window: tuple[str, str], sf: float = 1.0) -> pd.DataFrame:
    """One dollars_per_mwh row per lambda statistic (p25, p50, p75, mean)."""
    return pd.DataFrame([dollars_per_mwh(stats, year, month, window, col, sf) for col in ("p25", "p50", "p75", "mean")])
