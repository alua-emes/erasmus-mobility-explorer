
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/mobility_clean.csv"
REPORTS = ROOT / "docs"
REPORTS.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

# 1. Annual coverage
annual = df.groupby("YEAR").agg(
    total_mobility=("COUNT", "sum"),
    route_count=("COUNT", "size"),
    origin_regions=("ORIGIN", "nunique"),
    destination_regions=("DESTINATION", "nunique"),
).reset_index()

annual["growth_pct"] = (
    annual["total_mobility"].pct_change() * 100
).round(2)

print("\n=== ANNUAL COVERAGE ===")
print(annual.to_string(index=False))

annual.to_csv(
    REPORTS / "annual_validation.csv",
    index=False
)

# 2. Check 2018 and 2019
a = df[df["YEAR"] == 2018][
    ["OD_ID", "COUNT"]
].set_index("OD_ID")

b = df[df["YEAR"] == 2019][
    ["OD_ID", "COUNT"]
].set_index("OD_ID")

comparison = a.join(
    b, how="outer", suffixes=("_2018", "_2019")
)

shared = comparison.dropna()

print("\n=== 2018 vs 2019 ===")
print("Routes in 2018:", len(a))
print("Routes in 2019:", len(b))
print("Shared routes:", len(shared))
print(
    "Shared routes with identical counts:",
    (shared["COUNT_2018"] == shared["COUNT_2019"]).sum()
)

# 3. Domestic mobility
domestic = df[df["SAME_COUNTRY"]]

print("\n=== DOMESTIC MOBILITY ===")
print("Domestic rows:", len(domestic))
print("Domestic mobility count:", domestic["COUNT"].sum())
print(
    "Share of total mobility (%):",
    round(domestic["COUNT"].sum() / df["COUNT"].sum() * 100, 3)
)

# 4. Top origin countries
origin = (
    df.groupby("ORIGIN_COUNTRY")["COUNT"]
    .sum()
    .sort_values(ascending=False)
)

print("\n=== TOP 10 ORIGIN COUNTRIES ===")
print(origin.head(10))

# 5. Top destination countries
destination = (
    df.groupby("DEST_COUNTRY")["COUNT"]
    .sum()
    .sort_values(ascending=False)
)

print("\n=== TOP 10 DESTINATION COUNTRIES ===")
print(destination.head(10))

# 6. Data consistency
print("\n=== CHECKS ===")
print("Total mobility preserved:",
      annual["total_mobility"].sum() == df["COUNT"].sum())
print("Unexpected years:",
      (~df["YEAR"].between(2014, 2023)).sum())
