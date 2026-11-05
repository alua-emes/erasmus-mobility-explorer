
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/Erasmus_2014-2023_aggregate_NUTS.csv"

df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig")

print("\n=== DATASET OVERVIEW ===")
print("Shape:", df.shape)
print("\nFirst 10 rows:")
print(df.head(10).to_string(index=False))

print("\n=== DATA TYPES ===")
print(df.dtypes)

print("\n=== MISSING VALUES ===")
print(df.isna().sum())

print("\n=== UNIQUE VALUES ===")
for col in df.columns:
    print(f"{col}: {df[col].nunique(dropna=True):,}")

print("\n=== YEAR DISTRIBUTION ===")
print(df["YEAR"].value_counts(dropna=False).sort_index())

print("\n=== COUNT VALIDATION ===")
counts = pd.to_numeric(df["COUNT"], errors="coerce")
print("Non-numeric counts:", counts.isna().sum())
print("Negative counts:", (counts < 0).sum())
print("Zero counts:", (counts == 0).sum())
print("Total count:", counts.sum())
print("Minimum:", counts.min())
print("Maximum:", counts.max())

print("\n=== DUPLICATES ===")
print("Exact duplicate rows:", df.duplicated().sum())
print(
    "Duplicate origin-destination-year combinations:",
    df.duplicated(subset=["ORIGIN", "DESTINATION", "YEAR"]).sum()
)

print("\n=== ORIGIN AND DESTINATION EXAMPLES ===")
print("Origins:", df["ORIGIN"].dropna().unique()[:20])
print("Destinations:", df["DESTINATION"].dropna().unique()[:20])

print("\n=== SAME ORIGIN AND DESTINATION ===")
print(
    "Rows where origin equals destination:",
    (df["ORIGIN"] == df["DESTINATION"]).sum()
)
