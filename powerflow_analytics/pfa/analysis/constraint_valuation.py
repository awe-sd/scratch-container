"""Compact per-constraint valuation: binding stats, lambda distribution,
marginal units, and their shift factors on the constraint.

Reuses the cache layout from scripts/pull_study.py and the constraint-key /
binding convention from pfa.analysis.constraints, and marginal_units.bus_name_map
for the LPBASICVARID -> BUSNAME -> GENUNIT chain.

Binding = LIMVIOLPCT >= 99.5 in OUTCTGVIOL2 (see constraints.BINDING_PCT).
Lambda comes from OUTCONSTRAINT2.OPFCNLAMBDA for the RUNIDs that bind, joined
on (FROMNUM, TONUM, CKT, LPOPFCTGID-as-CTGLABEL).

Marginal units: OUTCONSTRAINT2.GENBUSNUM/GENID are NULL for ERCOT studies
(confirmed empty in study 14412) — the only live identity is the free-text
LPBASICVARID column, e.g. "Gen 8968 #1 MW Control" or
"Slack-Line 126  TO  3636 CKT 1". Only the "Gen <busnum> #<id>" rows resolve
to a generator; slack-line rows are dropped. Bus number -> bus name uses
marginal_units.bus_name_map(outbranch2) (line-endpoint names only — a
generator bus with no line-endpoint appearance in this study's cache will not
resolve, and is dropped rather than guessed).

PSENS (shift factor) comes from SHIFT_FACTORS.DBO.CPNODE_SHIFTS_VIEW, scoped
to (ISOMARKETID, STUDYID, FROMNUM, TONUM, CKT, CTGLABEL, CPNODEID) — never an
unscoped query.
"""
from __future__ import annotations

import re

import pandas as pd

from .. import config, sf
from ..cache import StudyCache
from ..constraint_id import ConstraintId
from ..extract import gen_mapping, shifts
from .constraints import BINDING_PCT
from .marginal_units import bus_name_map

_GEN_RE = re.compile(r"^Gen (\d+) #(\d+)")



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
    # Fall back to scoped Snowflake queries (AWOPF) if the cache is missing.
    # OUT* tables key on RUNID only (no STUDYID column) -- scope every one of
    # them through an OPFRUN subquery, same pattern as extract/results.py.
    config.configure()
    runid_filter = f"RUNID IN (SELECT RUNID FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)})"
    ctgviol = sf.query(
        "AWOPF",
        f"""SELECT RUNID, FROMNUM, TONUM, CKT, CTGLABEL, LIMVIOLPCT
            FROM AWOPF.DBO.OUTCTGVIOL2 WHERE {runid_filter}""",
    )
    outcon = sf.query(
        "AWOPF",
        f"""SELECT RUNID, FROMNUM, TONUM, CKT, LPOPFCTGID, OPFCNLAMBDA, LPBASICVARID
            FROM AWOPF.DBO.OUTCONSTRAINT2 WHERE {runid_filter}""",
    )
    runs = sf.query(
        "AWOPF", f"SELECT RUNID, STUDYID, SIMDATE, SIMHOUR FROM AWOPF.DBO.OPFRUN WHERE STUDYID = {int(study_id)}"
    )
    branch = sf.query(
        "AWOPF",
        f"""SELECT FROMNUM, TONUM, FROMNAME, TONAME FROM AWOPF.DBO.OUTBRANCH2
            WHERE {runid_filter}""",
    )
    return ctgviol, outcon, runs, branch


def value_constraint(study_id: int, fromnum: int, tonum: int, ckt: str, ctglabel: str) -> dict:
    """Binding stats + lambda distribution + marginal units + their PSENS
    on this constraint, for one (study, FROMNUM, TONUM, CKT, CTGLABEL)."""
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
