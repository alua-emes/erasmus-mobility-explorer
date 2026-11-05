
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

RAW = ROOT / "data/raw/Erasmus_2014-2023_aggregate_NUTS.csv"
OUT = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)

# 1. Load original dataset
df = pd.read_csv(
    RAW,
    sep=";",
    encoding="utf-8-sig",
    dtype={
        "OD_ID": "string",
        "ORIGIN": "string",
        "DESTINATION": "string",
        "YEAR": "Int64",
        "COUNT": "Int64",
    },
)

# 2. Validate original records
required = ["OD_ID", "ORIGIN", "DESTINATION", "YEAR", "COUNT"]
assert df[required].notna().all().all(), "Missing values found"
assert not df.duplicated(
    subset=["ORIGIN", "DESTINATION", "YEAR"]
).any(), "Duplicate routes found"
assert df["COUNT"].gt(0).all(), "Invalid counts found"
assert df["YEAR"].between(2014, 2023).all(), "Unexpected years"

# 3. Verify origin-destination identifiers
expected_id = df["ORIGIN"] + "_" + df["DESTINATION"]
mismatched_ids = (df["OD_ID"] != expected_id).sum()
print("OD_ID mismatches:", mismatched_ids)

# 4. Create country-code prefixes
# These are preliminary codes, not verified country names.
df["ORIGIN_COUNTRY"] = df["ORIGIN"].str[:2]
df["DEST_COUNTRY"] = df["DESTINATION"].str[:2]

# 5. Flag movements within the same region/country
df["SAME_REGION"] = df["ORIGIN"].eq(df["DESTINATION"])
df["SAME_COUNTRY"] = df["ORIGIN_COUNTRY"].eq(
    df["DEST_COUNTRY"]
)

# 6. Preserve all original mobility records
df.to_csv(OUT / "mobility_clean.csv", index=False)

# 7. Mobility count by year
yearly = (
    df.groupby("YEAR", as_index=False)
    .agg(
        TOTAL_MOBILITY=("COUNT", "sum"),
        ROUTE_COUNT=("OD_ID", "size"),
    )
)
yearly.to_csv(OUT / "mobility_by_year.csv", index=False)

# 8. Country-to-country flows
country_flows = (
    df.groupby(
        ["YEAR", "ORIGIN_COUNTRY", "DEST_COUNTRY"],
        as_index=False
    )["COUNT"]
    .sum()
)
country_flows.to_csv(
    OUT / "country_flows.csv",
    index=False
)

# 9. Regional flows through time
regional_flows = (
    df.groupby(
        ["YEAR", "ORIGIN", "DESTINATION"],
        as_index=False
    )["COUNT"]
    .sum()
)
regional_flows.to_csv(
    OUT / "regional_flows.csv",
    index=False
)

# 10. Diagnostic output
print("\n=== PREPARATION COMPLETE ===")
print("Original rows:", len(df))
print("Total mobility count:", df["COUNT"].sum())
print("Same-region rows:", df["SAME_REGION"].sum())
print("Same-country rows:", df["SAME_COUNTRY"].sum())

print("\nMobility by year:")
print(yearly.to_string(index=False))

print("\nOrigin country-code prefixes:")
print(sorted(df["ORIGIN_COUNTRY"].unique().tolist()))

print("\nDestination country-code prefixes:")
print(sorted(df["DEST_COUNTRY"].unique().tolist()))

assert yearly["TOTAL_MOBILITY"].sum() == df["COUNT"].sum()
assert country_flows["COUNT"].sum() == df["COUNT"].sum()

print("\nAll aggregation checks passed.")
