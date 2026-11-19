
import csv
import random
import time
import tempfile
from pathlib import Path

import pandas as pd

from database import ROOT, get_connection
from load_database import DATA_PATH, load_data
from run_analysis import run_analysis
from pipeline import initialize_database


OUTPUT_DIR = ROOT / "data/processed/sql"

FRACTIONS = [0.25, 0.50, 1.00]
REPEATS = 3
RANDOM_SEED = 42


def prepare_samples(temp_dir):

    with DATA_PATH.open(
        encoding="utf-8-sig", newline=""
    ) as file:

        reader = csv.reader(file, delimiter=";")
        header = next(reader)
        total_rows = sum(1 for _ in reader)

    indices = list(range(total_rows))

    random.Random(RANDOM_SEED).shuffle(indices)

    samples = {1.00: DATA_PATH}

    for fraction in [0.25, 0.50]:

        sample_size = int(total_rows * fraction)
        selected = set(indices[:sample_size])

        sample_path = (
            temp_dir / f"sample_{int(fraction * 100)}.csv"
        )

        with DATA_PATH.open(
            encoding="utf-8-sig", newline=""
        ) as source:

            reader = csv.reader(source, delimiter=";")
            next(reader)

            with sample_path.open(
                "w", encoding="utf-8", newline=""
            ) as target:

                writer = csv.writer(target, delimiter=";")
                writer.writerow(header)

                for i, row in enumerate(reader):
                    if i in selected:
                        writer.writerow(row)

        samples[fraction] = sample_path

    return samples


def expected_metrics(data_path):

    records = 0
    total_mobility = 0
    international_records = 0
    international_mobility = 0

    with data_path.open(
        encoding="utf-8-sig", newline=""
    ) as file:

        reader = csv.DictReader(file, delimiter=";")

        for row in reader:

            count = int(row["COUNT"])

            records += 1
            total_mobility += count

            if row["ORIGIN"][:2] != row["DESTINATION"][:2]:

                international_records += 1
                international_mobility += count

    return (
        records,
        total_mobility,
        international_records,
        international_mobility,
    )


def validate_sample(expected):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(count), 0),
                    COUNT(*) FILTER (
                        WHERE same_country = FALSE
                    ),
                    COALESCE(SUM(count) FILTER (
                        WHERE same_country = FALSE
                    ), 0)
                FROM mobility;
            """)

            actual = cur.fetchone()

    if actual != expected:
        raise ValueError(
            f"Validation failed: {actual} != {expected}"
        )

    return actual[0]


def measure_disk():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    pg_database_size(current_database()),
                    pg_table_size('mobility'),
                    pg_indexes_size('mobility'),
                    pg_total_relation_size('mobility');
            """)

            return cur.fetchone()


def benchmark():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    with tempfile.TemporaryDirectory() as temp:

        temp_dir = Path(temp)

        print("Preparing dataset samples...")

        samples = prepare_samples(temp_dir)

        expected = {
            fraction: expected_metrics(path)
            for fraction, path in samples.items()
        }

        for run in range(1, REPEATS + 1):

            for fraction in FRACTIONS:

                print("\n" + "=" * 50)
                print(f"Dataset: {fraction:.0%}")
                print(f"Run: {run}/{REPEATS}")
                print("=" * 50)

                data_path = samples[fraction]

                pipeline_start = time.perf_counter()

                initialize_database()

                # Loading time
                start = time.perf_counter()

                load_data(data_path)

                loading_time = time.perf_counter() - start

                # Refresh PostgreSQL statistics
                start = time.perf_counter()

                with get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("ANALYZE mobility;")

                analyze_time = time.perf_counter() - start

                # Validate dataset
                records = validate_sample(expected[fraction])

                # Run analytical SQL queries
                query_times = run_analysis(
                    temp_dir / "analysis"
                )

                pipeline_time = (
                    time.perf_counter() - pipeline_start
                )

                # Measure storage
                db_size, table_size, index_size, total_size = (
                    measure_disk()
                )

                results.append({
                    "dataset_fraction": fraction,
                    "run": run,
                    "records": records,
                    "csv_bytes": data_path.stat().st_size,
                    "loading_seconds": loading_time,
                    "analyze_seconds": analyze_time,
                    "annual_seconds": query_times[
                        "annual_mobility"
                    ],
                    "balance_seconds": query_times[
                        "country_balance"
                    ],
                    "imbalance_seconds": query_times[
                        "relative_imbalance"
                    ],
                    "bilateral_seconds": query_times[
                        "bilateral_flows"
                    ],
                    "pipeline_seconds": pipeline_time,
                    "database_bytes": db_size,
                    "table_bytes": table_size,
                    "index_bytes": index_size,
                    "total_relation_bytes": total_size,
                })

                print(f"Pipeline time: {pipeline_time:.3f} s")

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        OUTPUT_DIR / "benchmark_results.csv",
        index=False
    )

    summary = (
        results_df
        .drop(columns="run")
        .groupby("dataset_fraction")
        .mean()
        .reset_index()
    )

    summary.to_csv(
        OUTPUT_DIR / "benchmark_summary.csv",
        index=False
    )

    print("\nBENCHMARK COMPLETED SUCCESSFULLY")

    print(summary[[
        "dataset_fraction",
        "records",
        "loading_seconds",
        "pipeline_seconds",
        "database_bytes",
    ]].to_string(index=False))


if __name__ == "__main__":
    benchmark()
