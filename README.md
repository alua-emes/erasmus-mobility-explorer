
# Erasmus+ Mobility Data Pipeline

Individual project for Computational Infrastructures for Data Science (CIDS).

## Project Objective

This project develops a reproducible data processing infrastructure for Erasmus+ mobility records from 2014 to 2023.

The project focuses on data validation, preprocessing, aggregation, database storage, containerization, and computational performance evaluation.

## Dataset

- File: Erasmus_2014-2023_aggregate_NUTS.csv
- Period: 2014–2023
- Records: 588,109
- Format: Semicolon-separated CSV
- Observation unit: Aggregated regional mobility flow per year

The original dataset must be placed in `data/raw/`.

## Current Project Status

Implemented:

- Dataset inspection and profiling
- Data validation and preprocessing
- Annual and country-level mobility aggregation
- Bilateral mobility analysis
- Reference analytical tables

Planned:

- PostgreSQL integration
- SQL-based analytical processing
- Docker Compose
- Performance benchmarking
- Scalability analysis

## Technology Stack

- Python 3.12
- pandas
- Jupyter
- uv
- Git and GitHub

PostgreSQL and Docker will be integrated in the next development stage.

## Setup

From the project root:

```powershell
uv sync
```

## Run the Data Processing Pipeline

Execute the following commands in order:

```powershell
uv run python src/inspect_data.py
uv run python src/profile_data.py
uv run python src/prepare_data.py
uv run python src/validate_data.py
uv run python src/build_analysis_tables.py
```

## Research Notebook

The main notebook is:

`notebooks/02_cids_report.ipynb`

It contains data quality assessment, data preparation, mobility analysis, and reference results.

## Project Structure

- `data/raw/` — original dataset
- `data/interim/` — intermediate data
- `data/processed/` — generated analytical tables
- `docs/` — dataset documentation and validation reports
- `src/` — reusable data processing scripts
- `notebooks/` — analytical report

Raw and generated datasets are excluded from version control.
