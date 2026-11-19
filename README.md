
# Erasmus+ Mobility Data Pipeline

Individual project for Computational Infrastructures for Data Science (CIDS).

## 1. Project Overview

This project implements a reproducible data processing infrastructure for Erasmus+ mobility records between 2014 and 2023.

The system integrates Python, PostgreSQL, Docker Compose, and GitHub for automated data loading, validation, analytical processing, and performance evaluation.

## 2. Research Questions

- What are the main patterns of international Erasmus+ mobility?
- How efficiently can mobility data be stored and processed using PostgreSQL?
- How does increasing data volume affect computational performance and storage requirements?

## 3. Dataset

File: `Erasmus_2014-2023_aggregate_NUTS.csv`

- Period: 2014–2023
- Records: 588,109
- Format: Semicolon-separated CSV
- Observation unit: Aggregated regional mobility flow per year

The original dataset is not included in the Git repository.

Place the dataset in:

`data/raw/Erasmus_2014-2023_aggregate_NUTS.csv`

See `docs/data_sources.md` for dataset documentation.

**Data source:** [Zenodo — Erasmus+ Mobility Dataset,
Version 1.1](https://doi.org/10.5281/zenodo.16737523)

Download `Erasmus_2014-2023_aggregate_NUTS.csv`
and place it in `data/raw/`.


## 4. Technology Stack

- Python 3.12
- pandas
- PostgreSQL 16
- psycopg
- Docker
- Docker Compose
- uv
- Jupyter Notebook
- Git and GitHub

## 5. System Architecture

The system consists of two Docker services:

- `db`: PostgreSQL database.
- `pipeline`: Python application responsible for database initialization, data loading, validation, and analytical processing.

The source dataset is mounted as a read-only directory.

PostgreSQL data is stored in a persistent Docker volume.

Analytical outputs are exported to the local filesystem.

## 6. Quick Start

### Prerequisites

- Docker Desktop or Docker Engine with Docker Compose.
- Original Erasmus+ dataset.

### Step 1: Clone the repository

```bash
git clone https://github.com/alua-emes/erasmus-mobility-explorer.git
cd erasmus-mobility-explorer
```

### Step 2: Configure environment variables

Create a `.env` file using `.env.example` as a template.

For PowerShell:

```powershell
Copy-Item .env.example .env
```

For Linux or macOS:

```bash
cp .env.example .env
```

Adjust the database password if necessary.

### Step 3: Prepare the dataset

Place the original CSV file in `data/raw/`.

### Step 4: Start the system

```bash
docker compose up --build
```

The pipeline automatically creates the database table, loads the dataset, validates the records, and executes the analytical SQL queries.

Successful execution is indicated by:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

The pipeline container exits with code 0, while PostgreSQL remains available.

### Step 5: Stop the system

```bash
docker compose down
```

The PostgreSQL data volume is preserved.

## 7. Analytical Outputs

The SQL pipeline generates:

- annual_mobility.csv
- country_balance.csv
- relative_imbalance.csv
- bilateral_flows.csv

All files are stored in:

`data/processed/sql/`

## 8. Performance Benchmarking

The benchmark evaluates 25%, 50%, and 100% of the dataset.

Each dataset size is tested three times.

Run the benchmark:

```bash
docker compose up -d db
docker compose build pipeline
docker compose run --rm pipeline uv run --no-sync python -u src/benchmark.py
```

The generated files are:

- benchmark_results.csv
- benchmark_summary.csv

Both files are saved in `data/processed/sql/`.

### Benchmark Results

| Measurement | 25% | 50% | 100% |
|---|---:|---:|---:|
| Records | 147,027 | 294,054 | 588,109 |
| Loading time (s) | 0.656 | 1.197 | 2.838 |
| Annual query (ms) | 17.66 | 27.78 | 40.38 |
| Country balance (ms) | 49.45 | 63.13 | 87.44 |
| Relative imbalance (ms) | 50.82 | 61.34 | 88.65 |
| Bilateral query (ms) | 30.73 | 38.78 | 58.76 |
| Pipeline time (s) | 0.949 | 1.551 | 3.303 |
| Database size (MiB) | 27.33 | 46.43 | 85.58 |
| Table and indexes (MiB) | 19.80 | 38.89 | 78.04 |

Execution times and storage measurements are averages of three runs.

### Memory Consumption

Peak container memory measured during a separate full-dataset execution:

| Container | Peak Memory |
|---|---:|
| Python pipeline | 98.84 MiB |
| PostgreSQL | 289.13 MiB |

### Experimental Environment

- Intel Core i5-1240P
- 12 physical cores and 16 logical processors
- Approximately 16 GB host RAM
- 7.57 GiB available Docker memory
- Windows with WSL 2
- PostgreSQL 16.16

Recorded experimental results are available in
`docs/benchmarks/`.

These files preserve the original measurements
used in the project report.


## 9. Database Validation

| Metric | Result |
|---|---:|
| Total records | 588,109 |
| Total mobility count | 2,554,116 |
| International records | 587,225 |
| International mobility count | 2,551,560 |
| Number of years | 10 |
| Directional country connections | 1,217 |

The aggregate results are consistent with the pandas reference analysis.

## 10. Project Structure

```text
erasmus-mobility-explorer/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
├── notebooks/
│   └── 02_cids_report.ipynb
├── sql/
│   ├── schema.sql
│   ├── analysis.sql
│   └── validation.sql
├── src/
│   ├── inspect_data.py
│   ├── profile_data.py
│   ├── prepare_data.py
│   ├── validate_data.py
│   ├── build_analysis_tables.py
│   ├── database.py
│   ├── load_database.py
│   ├── run_analysis.py
│   ├── pipeline.py
│   └── benchmark.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## 11. Research Notebook

The complete analytical and technical report is available in:

`notebooks/02_cids_report.ipynb`

To execute the notebook locally:

```bash
uv sync
```

Select the project's Python environment as the Jupyter kernel.

The database must be running and the benchmark output files must be available before executing the technical evaluation sections.

## 12. Limitations

The performance evaluation was conducted on a single local machine.

The scalability experiment is limited to three dataset sizes.

Memory measurements represent one full-dataset execution.

The results should be interpreted within the tested experimental conditions.
