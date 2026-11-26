"""
Classify the 'unmatched' rows from output/teid_branch_id_map.csv to check
whether the misses are a real gap in dbo.BRANCH or just CIM modeling
artifacts that were never expected to have a BRANCH row.

Two patterns explain effectively all of them:

1. transformer_tertiary_stub -- PsseType == 'Transformer' whose CIM `Name`
   shows the low-voltage terminal at ~1kV (e.g. 'MR1T 13.8kV-1kV'). This is
   the CIM 3-winding-transformer decomposition artifact: the tertiary leg
   to an internal star/dummy point, not a real second branch. BRANCH only
   carries the primary/secondary 2-winding equivalent.

2. generation_plant_internal -- remaining PsseType == 'Branch' rows
   (ACLineSegment / SeriesCompensator) sitting inside generation-plant
   substations (solar '_SLR', wind '_WND', battery '_ESS', industrial cogen
   'DOWGEN'/'RNPCOGEN'/'THW', station-load 'SL'). These are collector-system
   / reactor elements behind the generator interconnection point, not
   bulk-transmission branches, so BRANCH never carries them either.

Read-only. Writes only to branch_tracking/output/.
"""
import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = REPO_ROOT / "output" / "teid_branch_id_map.csv"
OUTPUT_CSV = REPO_ROOT / "output" / "unmatched_classified.csv"

TERTIARY_STUB_KV_THRESHOLD = 1.5

# Plant codes are arbitrary strings (e.g. 'BOG', 'MYR', 'DIESEL') -- there is
# no naming convention reliable enough for a regex. This is the exact,
# manually-verified set of Substation1/Substation2 values covering every one
# of the 56 non-transformer unmatched rows in the Jul ML1 CIM export: solar
# ('_SLR'), wind ('_WND'/'_WIND'), battery storage ('_ESS'), industrial cogen
# (DOWGEN, THW), and station-load buswork (SL), among others. Re-verify this
# list (rerun the substation-extraction snippet in the module docstring's
# investigation, or just eyeball new 'branch_other' rows) if this script is
# pointed at a different CIM export.
GEN_PLANT_SUBSTATIONS = {
    "AQLA_WND", "BAKE_SLR", "BBP", "BLSUMMIT", "BOG", "BUCHAN", "BYP", "BYU",
    "CORONA", "DIESEL", "DOWGEN", "FERD_ESS", "GRND_SLR", "LBRA_ESS", "MIN",
    "MYR", "NOBLESLR", "ROSELAND", "RRC_WIND", "SHAMROCK", "SL", "STEAM1A",
    "THW", "TRBT_SLR",
}


def min_kv(name):
    matches = re.findall(r"([\d.]+)kV", str(name))
    return min(float(m) for m in matches) if matches else None


def classify(row):
    if row["PsseType"] == "Transformer":
        kv = min_kv(row["Name"])
        if kv is not None and kv <= TERTIARY_STUB_KV_THRESHOLD:
            return "transformer_tertiary_stub"
        return "transformer_other"

    if row["Substation1"] in GEN_PLANT_SUBSTATIONS or row["Substation2"] in GEN_PLANT_SUBSTATIONS:
        return "generation_plant_internal"
    return "branch_other"


def main():
    df = pd.read_csv(INPUT_CSV)
    unmatched = df[df["match_status"] == "unmatched"].copy()

    unmatched["unmatched_reason"] = unmatched.apply(classify, axis=1)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    unmatched.to_csv(OUTPUT_CSV, index=False)

    print(f"Unmatched rows: {len(unmatched)}")
    print(unmatched["unmatched_reason"].value_counts().to_string())
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
