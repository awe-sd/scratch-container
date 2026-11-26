import pandas as pd

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 120)

TOL = 0.0008

def tier(s):
    if s > 0.98:
        return "DEGENERATE_ALL_ZERO"
    if s >= 0.5:
        return "HIGH"
    if s >= 0.2:
        return "MEDIUM"
    return "LOW"


df = pd.read_csv("pun_shift_equivalence.csv")
const = pd.read_csv("farfield_by_set.csv")[["PSENSHIFTID", "FARFIELD_CONST", "BUS_COUNT", "N_FARFIELD", "SHARE_FARFIELD"]]
const["RELIABILITY"] = const["SHARE_FARFIELD"].apply(tier)

df = df.merge(const, on="PSENSHIFTID", how="left")

df["PUN_FARFIELD"] = ((df["PSENS_PUN"] - df["FARFIELD_CONST"]).abs() <= TOL).astype("boolean")
df["ERCOT_FARFIELD"] = ((df["PSENS_ERCOT"] - df["FARFIELD_CONST"]).abs() <= TOL).astype("boolean")

# NaN PSENS -> flag should be NA, not False
df.loc[df["PSENS_PUN"].isna(), "PUN_FARFIELD"] = pd.NA
df.loc[df["PSENS_ERCOT"].isna(), "ERCOT_FARFIELD"] = pd.NA

df.to_csv("farfield_flagged.csv", index=False)

both_present = df[df["PSENS_ERCOT"].notna() & df["PSENS_PUN"].notna()].copy()
print("=== rows with both PSENS present:", len(both_present), "of", len(df), "===")

# (a) share of tie x set pairs where PUN far-field, ERCOT not, by CLASS
both_present["PUN_ONLY_FARFIELD"] = both_present["PUN_FARFIELD"] & (~both_present["ERCOT_FARFIELD"])
a = both_present.groupby("CLASS").agg(
    n_pairs=("PUN_ONLY_FARFIELD", "size"),
    n_pun_only=("PUN_ONLY_FARFIELD", "sum"),
).assign(share=lambda x: x["n_pun_only"] / x["n_pairs"])
print("\n(a) PUN far-field & ERCOT NOT far-field, by CLASS:")
print(a)

print("\n(a-supplement) same, by CLASS x set RELIABILITY tier (excl. DEGENERATE_ALL_ZERO sets):")
a2 = both_present[both_present["RELIABILITY"] != "DEGENERATE_ALL_ZERO"].groupby(["CLASS", "RELIABILITY"]).agg(
    n_pairs=("PUN_ONLY_FARFIELD", "size"),
    n_pun_only=("PUN_ONLY_FARFIELD", "sum"),
).assign(share=lambda x: x["n_pun_only"] / x["n_pairs"])
print(a2)

# (b) RADIAL pairs with |delta|*100 > 1 MW
radial = both_present[both_present["CLASS"] == "RADIAL"].copy()
radial_big = radial[radial["ABS_DELTA_X100_MW"] > 1]
print(f"\n(b) RADIAL pairs total: {len(radial)}; with |delta|x100 > 1 MW: {len(radial_big)}")
explained = radial_big[radial_big["PUN_FARFIELD"] == True]
not_explained = radial_big[radial_big["PUN_FARFIELD"] != True]
print(f"  explained by PUN_FARFIELD: {len(explained)} of {len(radial_big)}")
print(f"  NOT explained (PUN side not far-field) -- listing:")
cols = ["PSENSHIFTID", "BRANCH_LABEL", "BRANCHNAME_TIE", "PUN_STATION", "ERCOT_STATION",
        "PUN_SIDE_BUS", "ERCOT_SIDE_BUS", "PSENS_PUN", "PSENS_ERCOT", "FARFIELD_CONST", "ABS_DELTA_X100_MW"]
print(not_explained[cols].to_string(index=False))

# (c) MESHED distribution of |delta|*100 excluding PUN_FARFIELD rows
meshed = both_present[both_present["CLASS"] == "MESHED"].copy()
meshed_ex = meshed[meshed["PUN_FARFIELD"] != True]
print(f"\n(c) MESHED pairs total: {len(meshed)}; excluding PUN_FARFIELD: {len(meshed_ex)}")
print("  median:", meshed_ex["ABS_DELTA_X100_MW"].median())
print("  p90:", meshed_ex["ABS_DELTA_X100_MW"].quantile(0.9))
print("  max:", meshed_ex["ABS_DELTA_X100_MW"].max())
worst5 = meshed_ex.sort_values("ABS_DELTA_X100_MW", ascending=False).head(5)
cols_c = ["PSENSHIFTID", "BRANCH_LABEL", "BRANCHNAME_TIE", "DEFAULT_RATE_B", "PUN_STATION", "ERCOT_STATION",
          "PSENS_PUN", "PSENS_ERCOT", "FARFIELD_CONST", "ABS_DELTA_X100_MW"]
print("  worst 5:")
print(worst5[cols_c].to_string(index=False))

# (d) 73 distinct PUN-side buses: always far-field vs sometimes real
# PSENS_PUN depends only on (PSENSHIFTID, PUN_SIDE_BUS), not on which tie/ERCOT-side
# bus it is paired with in a given CSV row, so dedupe on that pair first to avoid
# double-counting buses that appear in more than one tie.
pun_bus_rows = df[df["PSENS_PUN"].notna()].drop_duplicates(subset=["PSENSHIFTID", "PUN_SIDE_BUS"]).copy()
bus_summary = pun_bus_rows.groupby("PUN_SIDE_BUS").agg(
    n_sets=("PSENSHIFTID", "nunique"),
    n_farfield=("PUN_FARFIELD", lambda x: (x == True).sum()),
)
bus_summary["always_farfield"] = bus_summary["n_farfield"] == bus_summary["n_sets"]
bus_summary["never_farfield"] = bus_summary["n_farfield"] == 0
n_total_buses = df["PUN_SIDE_BUS"].nunique()
n_with_data = bus_summary.shape[0]
n_always = bus_summary["always_farfield"].sum()
n_sometimes = (~bus_summary["always_farfield"] & ~bus_summary["never_farfield"]).sum()
n_never = bus_summary["never_farfield"].sum()
print(f"\n(d) distinct PUN-side buses total in CSV: {n_total_buses}; with at least one non-null PSENS_PUN: {n_with_data}")
print(f"  always far-field (every set where present): {n_always}")
print(f"  sometimes real / sometimes far-field: {n_sometimes}")
print(f"  never far-field (always real, if any): {n_never}")

bus_summary.to_csv("farfield_bus_summary.csv")
print("\nBus summary sample:")
print(bus_summary.sort_values("n_sets", ascending=False).head(15))

# (d-supplement) restrict to HIGH-reliability sets only (genuine concentrated far-field cluster)
high_rows = pun_bus_rows[pun_bus_rows["RELIABILITY"] == "HIGH"]
bus_summary_high = high_rows.groupby("PUN_SIDE_BUS").agg(
    n_sets=("PSENSHIFTID", "nunique"),
    n_farfield=("PUN_FARFIELD", lambda x: (x == True).sum()),
)
bus_summary_high["frac"] = bus_summary_high["n_farfield"] / bus_summary_high["n_sets"]
print(f"\n(d-supplement) restricted to HIGH-reliability sets only ({high_rows['PSENSHIFTID'].nunique()} sets):")
print(f"  buses with data: {len(bus_summary_high)}")
print(f"  mean far-field fraction: {bus_summary_high['frac'].mean():.3f}")
print(f"  buses always far-field (frac==1): {(bus_summary_high['frac']==1).sum()}")
print(f"  buses never far-field (frac==0): {(bus_summary_high['frac']==0).sum()}")
print(bus_summary_high['frac'].describe())
