"""
Pick a topology-matched May psen for the May-8 6945/SRGRMGS5 (congConstraintID
231176) binding event, pull its vector, and compare its regional structure to
the user-supplied July vector 86037069. This groupby is the tie-breaker for
which vector to use in the decomposition plot (advisor step 2).

Read-only; caches the chosen May vector to parquet.
"""
import sys
from pathlib import Path

import awconnect
import pandas as pd
from awconnect import db

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_common import load  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
JULY_ID = 86037069


def region_profile(psen, tag):
    dim = load("sced_gen_dim")
    dim = dim[dim.ResourceType == "WIND"].copy()
    dim["rn"] = dim.ResourceName.str.upper().str.strip()
    dim["cp"] = pd.to_numeric(dim.cpnodeid, errors="coerce")
    ur = load("wind_unit_region")
    ur["rn"] = ur.unitName.str.upper().str.strip()
    urm = ur[["rn", "windRegion"]].drop_duplicates("rn")
    j = (dim.merge(psen, left_on="cp", right_on="cpNodeId", how="inner")
            .merge(urm, on="rn", how="left"))
    j["windRegion"] = j["windRegion"].fillna("Unmapped")
    prof = j.groupby("windRegion")["psen"].agg(["count", "mean", "sum"]).round(4)
    prof.columns = [f"{tag}_{c}" for c in prof.columns]
    return prof, j


def main():
    pd.set_option("display.width", 220)
    awconnect.configure("read_only")

    # best May psen for 231176 nearest May 8 (the event day)
    cand = db.getDfFromAwDb(
        "SELECT psenShiftID, psenShiftCreationDate FROM dbo.psenShiftDef "
        "WHERE congConstraintID = 231176 "
        "AND psenShiftCreationDate BETWEEN '2026-05-07' AND '2026-05-10' "
        "ORDER BY ABS(DATEDIFF(hour, psenShiftCreationDate, '2026-05-08 20:00')) ASC"
    )
    print(f"May-8 231176 psen candidates: {len(cand)}")
    print(cand.head(8).to_string())
    may_id = int(cand["psenShiftID"].iloc[0])
    print(f"\nChosen May psen: {may_id} (created {cand['psenShiftCreationDate'].iloc[0]})")

    may = db.getDfFromAwDb(
        f"SELECT psenShiftID, cpNodeId, psen FROM dbo.psenShift WHERE psenShiftID = {may_id}"
    )
    may.to_parquet(DATA / f"psenShift_{may_id}.parquet", index=False)
    july = load(f"psenShift_{JULY_ID}")
    print(f"May vector nodes: {len(may)}; July vector nodes: {len(july)}")

    pj, _ = region_profile(july, "jul")
    pm, _ = region_profile(may, "may")
    cmp = pj.join(pm, how="outer")
    print("\n=== regional psen structure: July 86037069 vs May %d ===" % may_id)
    print(cmp.to_string())

    # correlation on shared cpnodes (are the vectors basically the same shape?)
    m = july.merge(may, on="cpNodeId", suffixes=("_jul", "_may"))
    print(f"\nshared cpnodes: {len(m)}; corr(psen_jul, psen_may) = "
          f"{m['psen_jul'].corr(m['psen_may']):.4f}; "
          f"mean|diff| = {(m['psen_jul']-m['psen_may']).abs().mean():.4f}")
    with open(DATA / "chosen_may_psen.txt", "w") as f:
        f.write(str(may_id))
    print(f"\nwrote chosen May psen id -> data/chosen_may_psen.txt")


if __name__ == "__main__":
    main()
