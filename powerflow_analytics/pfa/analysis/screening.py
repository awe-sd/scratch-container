"""Constraint screening: universe -> signed impact -> dispatch-node count -> class -> flips -> stage-2 gate.

The one classification scheme (A target / B baseline / C no-dispatch / D bearish / weak) and the
shortlist gate. Reads the local study cache and the two CSVs written by `pfa summary --tickets`;
NQUAL comes from one grouped CPNODE_SHIFTS_VIEW query via pfa.extract.shifts. No file writing here.
"""
from __future__ import annotations

import gc
import warnings
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .. import config
from ..constraint_id import ConstraintId, constraint_key
from ..extract import shifts
from .constraints import BINDING_PCT
from .shadow_price import MAX_SF as SF_MAX, MIN_SF as SF_MIN

PENALTY_TIERS = (500.0, 3500.0)  # SCOPF unresolvable-violation price caps
FLATNESS_IQR_MAX = 1.0  # legacy flatness test: p50 exactly in a tier AND IQR below this
CLASS_A_SHARE_MIN = 0.25  # classification threshold, independent of the gate's share_min
BEARISH_SHARE = -0.10


@dataclass(frozen=True)
class Thresholds:
    share_min: float = 0.25
    post_days_min: int = 3
    rent_min: float = 200_000
    nqual_min: int = 2
    intensity_min_hard: float = 600  # below this a row is dropped unless flip-exempt
    intensity_min_full: float = 1000  # at/above this a row passes unflagged
    penalty_share_max: float = 0.4  # C no-dispatch if more of a constraint's LP rows sit in a penalty tier


@dataclass
class ScreeningResult:
    study: int
    cutoff: str
    thresholds: Thresholds
    dirs: pd.Series
    universe: pd.DataFrame  # classified, sorted (class, RENT_POST desc)
    flips: pd.DataFrame
    shortlist: pd.DataFrame  # gated
    intensity_dropped: pd.DataFrame  # passed the gate columns, dropped by the hard intensity floor


def constraint_directions(cache_dir) -> pd.Series:
    """constraint -> DIR (mode of OUTBRANCHDIRECTION in cached outctgviol2)."""
    cv = pd.read_parquet(
        f"{cache_dir}/outctgviol2.parquet",
        columns=["FROMNUM", "TONUM", "CKT", "CTGLABEL", "OUTBRANCHDIRECTION"],
    )
    cv["C"] = constraint_key(cv)
    dirs = cv.groupby("C").OUTBRANCHDIRECTION.agg(lambda s: s.mode().iloc[0]).rename("DIR")
    del cv
    gc.collect()
    return dirs


def build_universe(cache_dir, runs: pd.DataFrame, cutoff: str) -> pd.DataFrame:
    """Universe = ctgviol binding (>=BINDING_PCT) UNION outconstraint2 (LP-priced); `runs` has RUNID, SIMDATE, post."""
    cv = pd.read_parquet(
        f"{cache_dir}/outctgviol2.parquet",
        columns=["RUNID", "FROMNUM", "TONUM", "CKT", "CTGLABEL", "LIMVIOLPCT", "FROMNAME", "TONAME"],
    )
    cv = cv[cv.LIMVIOLPCT >= BINDING_PCT].copy()
    cv["C"] = constraint_key(cv)
    cv = cv.merge(runs, on="RUNID")

    oc = pd.read_parquet(
        f"{cache_dir}/outconstraint2.parquet",
        columns=["RUNID", "FROMNUM", "TONUM", "CKT", "LPOPFCTGID", "OPFCNLAMBDA"],
    )
    oc = oc.rename(columns={"LPOPFCTGID": "CTGLABEL"})
    oc["C"] = constraint_key(oc)
    oc = oc.merge(runs, on="RUNID")

    pre = cv[~cv.post].groupby("C").RUNID.nunique().rename("pre_binds")
    post = cv[cv.post].groupby("C").RUNID.nunique().rename("post_binds")
    pdays = cv[cv.post].groupby("C").SIMDATE.nunique().rename("post_days")

    lam_p50 = oc.groupby("C").OPFCNLAMBDA.median().rename("lam_p50")
    lam_mean = oc.groupby("C").OPFCNLAMBDA.mean().rename("lam_mean")
    lam_iqr = (
        oc.groupby("C").OPFCNLAMBDA.quantile(0.75) - oc.groupby("C").OPFCNLAMBDA.quantile(0.25)
    ).rename("lam_iqr")

    in_tier = oc.OPFCNLAMBDA.isin(PENALTY_TIERS)
    penalty_share = in_tier.groupby(oc.C).mean().rename("penalty_share")

    # gate basis: post-cutoff, non-zero, ex-penalty LP rows only
    ex_cap = oc[oc.post & (oc.OPFCNLAMBDA > 0) & (~oc.OPFCNLAMBDA.isin(PENALTY_TIERS))]
    lam_p50_gate = ex_cap.groupby("C").OPFCNLAMBDA.median().rename("lam_p50_gate")

    names = cv.drop_duplicates("C").set_index("C")[["FROMNAME", "TONAME", "FROMNUM", "TONUM"]]

    df = (
        pd.concat([pre, post, pdays], axis=1)
        .fillna(0)
        .join(lam_p50)
        .join(lam_mean)
        .join(lam_iqr)
        .join(penalty_share)
        .join(lam_p50_gate)
        .join(names)
    )
    del cv, oc, ex_cap
    gc.collect()
    return df


def signed_impact(universe: pd.DataFrame, tofinder: pd.DataFrame, dirs: pd.Series) -> pd.DataFrame:
    """Adds signed_fd, MEAN_PREFLOW and share = direction-signed top-group flow delta / |preflow| (NaN if |preflow| <= 1)."""
    tf = tofinder.join(dirs, on="CONSTRAINT")
    tf["signed_fd"] = tf.MEAN_FLOWDELTA * tf.DIR.fillna(1)
    top = (
        tf.reindex(tf.signed_fd.abs().sort_values(ascending=False).index)
        .drop_duplicates("CONSTRAINT")
        .set_index("CONSTRAINT")
    )
    df = universe.join(top[["signed_fd", "MEAN_PREFLOW"]], how="left")
    df["share"] = (df.signed_fd / df.MEAN_PREFLOW.abs()).where(df.MEAN_PREFLOW.abs() > 1)
    return df


def bulk_dispatch_nodes(universe: pd.DataFrame, study: int) -> pd.DataFrame:
    """Adds NQUAL (dispatchable-node count) and MAXSF for every constraint that binds pre or post."""
    cand = universe[(universe.post_binds > 0) | (universe.pre_binds > 0)]
    nq = shifts.cpnode_dispatch_nodes(study, list(cand.index), SF_MIN, SF_MAX)
    nq["C"] = nq["FN"] + "-" + nq["TN"] + "-" + nq["KK"] + "@" + nq["GG"]
    out = universe.join(nq.set_index("C")[["NQUAL", "MAXSF"]], how="left")
    out["NQUAL"] = out.NQUAL.fillna(0).astype(int)
    return out


def classify(df: pd.DataFrame, thresholds: Thresholds = Thresholds()) -> pd.DataFrame:
    """Adds `class`: D bearish > C no-dispatch > B baseline > A target > weak (first match wins)."""

    def flatness_pen(r):
        return pd.notna(r.lam_p50) and r.lam_p50 in PENALTY_TIERS and (r.lam_iqr or 0) < FLATNESS_IQR_MAX

    def penalty_share_pen(r):
        return pd.notna(r.get("penalty_share")) and r.penalty_share > thresholds.penalty_share_max

    def cls(r):
        if (r.pre_binds > 0 and r.post_binds == 0) or (pd.notna(r["share"]) and r["share"] < BEARISH_SHARE):
            return "D bearish"
        if flatness_pen(r) or penalty_share_pen(r) or r.NQUAL == 0 or r.NQUAL == 1:
            return "C no-dispatch"
        if r.pre_binds >= max(1, 0.5 * r.post_binds):
            return "B baseline"
        if pd.notna(r["share"]) and r["share"] >= CLASS_A_SHARE_MIN:
            return "A target"
        return "weak"

    df = df.copy()
    df["class"] = df.apply(cls, axis=1)
    return df


def detect_flips(df: pd.DataFrame) -> pd.DataFrame:
    """D-bearish constraints sharing an endpoint bus with a post-only binder on a different line."""
    D = df[df["class"] == "D bearish"]
    NEW = df[(df.pre_binds == 0) & (df.post_binds > 0)]
    flips = []
    for c, d in D.iterrows():
        line = ConstraintId.parse(c).line_key
        for b in (d.FROMNUM, d.TONUM):
            hits = NEW[(NEW.FROMNUM == b) | (NEW.TONUM == b)]
            for c2, n in hits.iterrows():
                if ConstraintId.parse(c2).line_key != line:
                    flips.append(
                        {
                            "fades": c,
                            "fades_name": f"{d.FROMNAME}-{d.TONAME}",
                            "pre": int(d.pre_binds),
                            "emerges": c2,
                            "emerges_name": f"{n.FROMNAME}-{n.TONAME}",
                            "post": int(n.post_binds),
                            "shared_bus": int(b),
                        }
                    )
    fl = pd.DataFrame(flips)
    if not fl.empty:
        fl = fl.drop_duplicates(["fades", "emerges"]).sort_values("post", ascending=False)
    return fl


def _gate_candidates(df: pd.DataFrame, th: Thresholds) -> pd.DataFrame:
    A = df[df["class"] == "A target"].copy()
    return A[
        (A["share"] >= th.share_min)
        & (A.post_days >= th.post_days_min)
        & (A.RENT_POST >= th.rent_min)
        & (A.NQUAL >= th.nqual_min)
    ].copy()


def stage2_gate(df: pd.DataFrame, flips: pd.DataFrame, thresholds: Thresholds = Thresholds()) -> pd.DataFrame:
    """Class A rows clearing share/days/rent/NQUAL, then the soft intensity band
    (post_binds x lam_p50_gate: >= hard keeps, >= full unflagged, flip targets rescued)."""
    th = thresholds
    gated = _gate_candidates(df, th)

    flip_targets = set(flips["emerges"]) if not flips.empty else set()
    intensity = gated.post_binds * gated.lam_p50_gate
    gated["intensity"] = intensity
    is_flip_target = gated.index.to_series().isin(flip_targets)
    hard_pass = intensity >= th.intensity_min_hard
    full_pass = intensity >= th.intensity_min_full

    keep = hard_pass | is_flip_target
    gated = gated[keep].copy()
    hard_pass, full_pass, is_flip_target = hard_pass[keep], full_pass[keep], is_flip_target[keep]

    gated["flip_exempt"] = is_flip_target & ~hard_pass
    gated["thin_intensity"] = hard_pass & ~full_pass & ~gated["flip_exempt"]
    return gated.sort_values("RENT_POST", ascending=False)


def intensity_dropped(df: pd.DataFrame, flips: pd.DataFrame, thresholds: Thresholds = Thresholds()) -> pd.DataFrame:
    """Rows that cleared the gate columns but fell under the hard intensity floor and are not flip targets."""
    g = _gate_candidates(df, thresholds)
    flip_targets = set(flips["emerges"]) if not flips.empty else set()
    g["intensity"] = g.post_binds * g.lam_p50_gate
    return g[(g["intensity"] < thresholds.intensity_min_hard) & (~g.index.to_series().isin(flip_targets))]


def screen_study(study: int, cutoff: str, thresholds: Thresholds = Thresholds(),
                 cache_dir: Path | None = None, out_dir: Path | None = None) -> ScreeningResult:
    """Classified universe, flips and gated shortlist for one study.

    Inputs: cache/study_<id>/{opfrun,outctgviol2,outconstraint2}.parquet and
    output/study_<id>/{ranked_constraints,tofinder_summary}.csv (from `pfa summary --tickets`).
    """
    cache_dir = Path(cache_dir) if cache_dir else config.CACHE_ROOT / f"study_{study}"
    out_dir = Path(out_dir) if out_dir else config.OUTPUT_ROOT / f"study_{study}"
    for name in ("ranked_constraints.csv", "tofinder_summary.csv"):
        if not (out_dir / name).exists():
            raise FileNotFoundError(f"{out_dir / name} is missing; run `pfa summary --study {study} --cutoff {cutoff} --tickets` first")

    runs = pd.read_parquet(cache_dir / "opfrun.parquet", columns=["RUNID", "SIMDATE"])
    runs["post"] = pd.to_datetime(runs.SIMDATE) >= cutoff
    sim_lo, sim_hi = runs.SIMDATE.min(), runs.SIMDATE.max()
    if not (sim_lo <= pd.to_datetime(cutoff) <= sim_hi):
        warnings.warn(f"cutoff {cutoff} falls outside this study's SIMDATE range [{sim_lo}, {sim_hi}]")

    dirs = constraint_directions(cache_dir)
    df = build_universe(cache_dir, runs, cutoff)
    rk = (
        pd.read_csv(out_dir / "ranked_constraints.csv", low_memory=False)
        .drop_duplicates("CONSTRAINT")
        .set_index("CONSTRAINT")
    )
    df = df.join(rk[["TOTAL_RENT", "RENT_POST", "DRIVER_TICKET", "DRIVER_TICKET_STATUS"]], how="left")
    df = signed_impact(df, pd.read_csv(out_dir / "tofinder_summary.csv"), dirs)
    df = bulk_dispatch_nodes(df, study)
    df = classify(df, thresholds)
    fl = detect_flips(df)
    return ScreeningResult(
        study=study,
        cutoff=cutoff,
        thresholds=thresholds,
        dirs=dirs,
        universe=df.sort_values(["class", "RENT_POST"], ascending=[True, False]),
        flips=fl,
        shortlist=stage2_gate(df, fl, thresholds),
        intensity_dropped=intensity_dropped(df, fl, thresholds),
    )
