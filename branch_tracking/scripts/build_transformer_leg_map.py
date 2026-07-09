"""
Build a transformer leg map: for every CIM Transformer teid, surface BOTH
the high-side and low-side BRANCH rows (not just the single winner that
build_teid_branchid_map.py picks for the main teid->branch_id table).

Three cases per teid:
  1. Both legs share the same teid in BRANCH (the common case -- this is
     what build_teid_branchid_map.py had to pick one winner from).
  2. Both legs share the same teid but neither has a recognizable '_H'/'_L'
     naming suffix -- disambiguated instead by matching bus pair (see the
     LWSSW/OLN numeric-suffix-leg finding in thoughts.md). Reported as a
     pair but NOT labeled high/low with confidence (`leg_orientation_confirmed`
     = False), since there's no signal for which numeric suffix means which
     side.
  3. Only one leg carries the teid; the sibling leg exists in BRANCH but
     has a NULL teid (confirmed real example: DIB_MT2H/teid=280262 vs
     DIB_MT2L/teid=NULL -- see thoughts.md). Found here by matching base
     name (leg suffix stripped) and, where possible, bus pair, against the
     pool of NULL-teid Transformer rows.

Read-only. Writes only to branch_tracking/output/.
"""
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

from build_teid_branchid_map import (
    CIM_CSV,
    ISOMARKETID_ERCOT,
    HIGH_SIDE_RE,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = REPO_ROOT / "output" / "transformer_leg_map.csv"

LOW_SIDE_RE_STR = r"(_?LOSIDE|_?LOW|_?L)$"
LEG_STRIP_RE_STR = r"(_?HISIDE|_?HIGH|_?H|_?LOSIDE|_?LOW|_?L)$"

import re

LOW_SIDE_RE = re.compile(LOW_SIDE_RE_STR, re.IGNORECASE)
LEG_STRIP_RE = re.compile(LEG_STRIP_RE_STR, re.IGNORECASE)


def classify_leg(op_eqcode):
    s = str(op_eqcode).strip()
    if HIGH_SIDE_RE.search(s):
        return "H"
    if LOW_SIDE_RE.search(s):
        return "L"
    return None


def base_name(op_eqcode):
    return LEG_STRIP_RE.sub("", str(op_eqcode).strip().upper())


def bus_pair(row, from_col="FromName", to_col="ToName"):
    a, b = row[from_col], row[to_col]
    if pd.isna(a) or pd.isna(b):
        return None
    return frozenset([str(a), str(b)])


def load_cim_transformer_teids():
    df = pd.read_csv(CIM_CSV)
    xf = df[df["PsseType"] == "Transformer"].copy()
    return xf.rename(columns={"TransmissionElementId": "teid"})[["teid", "OpEqName"]]


def load_all_branch_transformers():
    return db.getDfFromAwDb(
        f"""
        SELECT branchID, branchName, OP_EQCODE, FromName, ToName, teid
        FROM dbo.BRANCH
        WHERE isomarketid = {ISOMARKETID_ERCOT}
          AND collapseId IS NULL
          AND DeviceType = 'Transformer'
        """
    )


def pick_best(rows, prefer_col="branchID"):
    return rows.sort_values(prefer_col, ascending=False).iloc[0]


def main():
    awconnect.configure("read_only")

    cim_teids = load_cim_transformer_teids()
    branch = load_all_branch_transformers()
    branch["leg"] = branch["OP_EQCODE"].apply(classify_leg)
    branch["base"] = branch["OP_EQCODE"].apply(base_name)
    branch["pair"] = branch.apply(bus_pair, axis=1)

    tagged = branch[branch["teid"].notna()]
    orphans = branch[branch["teid"].isna()]

    results = []
    for _, cim_row in cim_teids.iterrows():
        teid = cim_row["teid"]
        candidates = tagged[tagged["teid"] == teid]
        if candidates.empty:
            continue  # unmatched -- covered by analyze_unmatched.py, not this file

        highs = candidates[candidates["leg"] == "H"]
        lows = candidates[candidates["leg"] == "L"]

        if len(highs) and len(lows):
            h, l = pick_best(highs), pick_best(lows)
            results.append({
                "teid": teid, "OpEqName": cim_row["OpEqName"],
                "high_side_branch_id": h["branchID"], "high_side_op_eqcode": h["OP_EQCODE"],
                "low_side_branch_id": l["branchID"], "low_side_op_eqcode": l["OP_EQCODE"],
                "leg_orientation_confirmed": True,
                "pairing_method": "same_teid_hl_suffix",
            })
            continue

        unlabeled = candidates[candidates["leg"].isna()]
        if len(unlabeled) >= 2:
            pairs = unlabeled.dropna(subset=["pair"])
            match = pairs[pairs.duplicated(subset=["pair"], keep=False)]
            if len(match) >= 2:
                grp = match.sort_values("branchID")
                a, b = grp.iloc[0], grp.iloc[-1]
                results.append({
                    "teid": teid, "OpEqName": cim_row["OpEqName"],
                    "high_side_branch_id": b["branchID"], "high_side_op_eqcode": b["OP_EQCODE"],
                    "low_side_branch_id": a["branchID"], "low_side_op_eqcode": a["OP_EQCODE"],
                    "leg_orientation_confirmed": False,
                    "pairing_method": "same_teid_bus_pair_no_suffix",
                })
                continue

        # Single usable side (or ambiguous extras like a stale no-data row) --
        # take the best H or L candidate present and look for a NULL-teid
        # sibling in the orphan pool.
        known_leg, known = (None, None)
        if len(highs):
            known_leg, known = "H", pick_best(highs)
        elif len(lows):
            known_leg, known = "L", pick_best(lows)
        else:
            continue  # no leg-labeled candidate at all -- nothing to pair on

        want_leg = "L" if known_leg == "H" else "H"
        sibling_candidates = orphans[
            (orphans["leg"] == want_leg) & (orphans["base"] == base_name(known["OP_EQCODE"]))
        ]
        if len(sibling_candidates) == 1:
            sib = sibling_candidates.iloc[0]
            pair_confirmed = (
                known["pair"] is not None and sib["pair"] is not None and known["pair"] == sib["pair"]
            )
            row = {
                "teid": teid, "OpEqName": cim_row["OpEqName"],
                "leg_orientation_confirmed": True,
                "pairing_method": "sibling_teid_null_matched_by_name"
                + ("_and_pair" if pair_confirmed else "_only"),
            }
            if known_leg == "H":
                row["high_side_branch_id"], row["high_side_op_eqcode"] = known["branchID"], known["OP_EQCODE"]
                row["low_side_branch_id"], row["low_side_op_eqcode"] = sib["branchID"], sib["OP_EQCODE"]
            else:
                row["low_side_branch_id"], row["low_side_op_eqcode"] = known["branchID"], known["OP_EQCODE"]
                row["high_side_branch_id"], row["high_side_op_eqcode"] = sib["branchID"], sib["OP_EQCODE"]
            results.append(row)
        else:
            row = {
                "teid": teid, "OpEqName": cim_row["OpEqName"],
                "leg_orientation_confirmed": True,
                "pairing_method": "no_sibling_found"
                if len(sibling_candidates) == 0
                else "sibling_ambiguous_multiple_candidates",
            }
            if known_leg == "H":
                row["high_side_branch_id"], row["high_side_op_eqcode"] = known["branchID"], known["OP_EQCODE"]
                row["low_side_branch_id"], row["low_side_op_eqcode"] = None, None
            else:
                row["low_side_branch_id"], row["low_side_op_eqcode"] = known["branchID"], known["OP_EQCODE"]
                row["high_side_branch_id"], row["high_side_op_eqcode"] = None, None
            results.append(row)

    out = pd.DataFrame(results)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)

    print(f"CIM Transformer teids considered: {len(cim_teids)}")
    print(f"Teids with a leg-map row produced: {len(out)}")
    print(out["pairing_method"].value_counts().to_string())
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
