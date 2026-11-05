
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUT = DATA / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA / "mobility_clean.csv")

# Keep international movements only
international = df.loc[
    df["ORIGIN_COUNTRY"] != df["DEST_COUNTRY"]
].copy()

# 1. Annual international mobility
annual = (
    international.groupby("YEAR", as_index=False)
    .agg(
        mobility_count=("COUNT", "sum"),
        route_count=("COUNT", "size")
    )
)

annual.to_csv(
    OUT / "international_trends.csv",
    index=False
)

# 2. Country-to-country mobility flows
flows = (
    international.groupby(
        ["YEAR", "ORIGIN_COUNTRY", "DEST_COUNTRY"],
        as_index=False
    )["COUNT"].sum()
)

flows.to_csv(
    OUT / "international_country_flows.csv",
    index=False
)

# 3. Country mobility balance
outgoing = (
    international.groupby(
        ["YEAR", "ORIGIN_COUNTRY"]
    )["COUNT"]
    .sum()
    .rename("outgoing")
    .rename_axis(["YEAR", "COUNTRY"])
)

incoming = (
    international.groupby(
        ["YEAR", "DEST_COUNTRY"]
    )["COUNT"]
    .sum()
    .rename("incoming")
    .rename_axis(["YEAR", "COUNTRY"])
)

balance = pd.concat(
    [incoming, outgoing], axis=1
).fillna(0).reset_index()

balance[["incoming", "outgoing"]] = (
    balance[["incoming", "outgoing"]].astype(int)
)

balance["net_mobility"] = (
    balance["incoming"] - balance["outgoing"]
)

balance.to_csv(
    OUT / "country_balance.csv",
    index=False
)

# 4. Validate aggregation
total = international["COUNT"].sum()

assert annual["mobility_count"].sum() == total
assert flows["COUNT"].sum() == total
assert balance["incoming"].sum() == total
assert balance["outgoing"].sum() == total
assert balance["net_mobility"].sum() == 0

# 5. Show results
print("\n=== INTERNATIONAL MOBILITY ===")
print("International mobility count:", total)
print("\nAnnual trends:")
print(annual.to_string(index=False))

print("\n=== COUNTRY BALANCE: ALL YEARS ===")
overall = (
    balance.groupby("COUNTRY", as_index=False)
    [["incoming", "outgoing", "net_mobility"]]
    .sum()
)

print("\nTop 10 net destinations:")
print(
    overall.nlargest(10, "net_mobility")
    .to_string(index=False)
)

print("\nTop 10 net senders:")
print(
    overall.nsmallest(10, "net_mobility")
    .to_string(index=False)
)

print("\n=== TOP 10 COUNTRY CONNECTIONS ===")
top_flows = (
    flows.groupby(
        ["ORIGIN_COUNTRY", "DEST_COUNTRY"],
        as_index=False
    )["COUNT"].sum()
    .nlargest(10, "COUNT")
)

print(top_flows.to_string(index=False))
print("\nAll checks passed.")
