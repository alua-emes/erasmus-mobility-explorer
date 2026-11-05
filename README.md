# Erasmus+ Mobility Explorer

Joint CIDS research and Data Visualization project (separate course deliverables).

## Setup (Windows PowerShell)

Open this folder in VS Code, open a terminal, then run:

```powershell
uv sync
uv run python src/inspect_data.py
```

Place original CSV files in `data/raw/` before running the inspection.

## Data folders

- `data/raw/` — untouched original CSV files (not tracked in Git)
- `data/interim/` — intermediate cleaned files (not tracked)
- `data/processed/` — prepared analysis tables (not tracked)
- `docs/data_sources.md` — exact source URLs, download dates and licenses
- `src/` — reusable processing and analysis code
- `notebooks/` — exploratory work
- `visualizations/` — exported charts
- `presentations/` — course presentations

## First step

```powershell
uv run python src/inspect_data.py
```

This creates `docs/data_inventory.csv` containing row counts, columns, sample values, and missingness statistics, and also prints a summary to the terminal. The script streams the data in chunks rather than loading all CSVs into memory at once.

## Development workflow

Use shared source data and analysis, but document the CIDS and Data Visualization contributions separately. Check the courses' policies on submitting overlapping work.
