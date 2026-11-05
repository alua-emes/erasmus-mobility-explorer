"""Inspect all raw CSVs without loading a whole large dataset into memory.

Run from the project root: uv run python src/inspect_data.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
INVENTORY_PATH = ROOT / "docs" / "data_inventory.csv"
CHUNK_SIZE = 50_000


def inspect_file(path: Path) -> list[dict[str, object]]:
    print(f"\n=== {path.name} ({path.stat().st_size / (1024 ** 2):,.1f} MB) ===")
    # sep=None auto-detects delimiter from a small sample using Python engine.
    # The actual full file is then processed efficiently with the C engine.
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as f:
                sample = f.read(16384)
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            break
        except (UnicodeError, csv.Error):
            continue
    else:
        raise ValueError(f"Could not detect text encoding/delimiter: {path.name}")

    print(f"Encoding: {encoding} | delimiter: {delimiter!r}")
    row_count = 0
    missing_counts = None
    examples: dict[str, list[str]] = {}
    columns = None
    for chunk in pd.read_csv(
        path,
        sep=delimiter,
        encoding=encoding,
        chunksize=CHUNK_SIZE,
        dtype=str,
        low_memory=False,
        on_bad_lines="warn",
    ):
        if columns is None:
            columns = list(chunk.columns)
            missing_counts = pd.Series(0, index=columns, dtype="int64")
            examples = {c: [] for c in columns}
        row_count += len(chunk)
        assert missing_counts is not None
        missing_counts += chunk.isna().sum()
        for col in columns:
            if len(examples[col]) < 3:
                for v in chunk[col].dropna().astype(str).unique():
                    if v.strip() and v not in examples[col]:
                        examples[col].append(v[:100])
                    if len(examples[col]) >= 3:
                        break

    if columns is None:
        print("No data rows found.")
        return []

    print(f"Rows: {row_count:,} | Columns: {len(columns)}")
    print("Column names:", columns)
    records = []
    for col in columns:
        missing = int(missing_counts[col])
        records.append({
            "file": path.name,
            "rows": row_count,
            "column": col,
            "missing_count": missing,
            "missing_pct": round(100 * missing / row_count, 2) if row_count else 0,
            "example_values": " | ".join(examples[col]),
        })
    return records


def main() -> None:
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        print(f"No CSV files yet. Put downloaded CSVs in: {RAW_DIR}")
        return
    records = []
    for path in files:
        try:
            records.extend(inspect_file(path))
        except Exception as exc:
            print(f"FAILED to inspect {path.name}: {exc}")
            raise
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(INVENTORY_PATH, index=False, encoding="utf-8-sig")
    print(f"\nSaved column inventory to {INVENTORY_PATH}")


if __name__ == "__main__":
    main()
