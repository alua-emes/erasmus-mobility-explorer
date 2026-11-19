
import csv
import time

from database import ROOT, get_connection


SQL_PATH = ROOT / "sql/analysis.sql"
OUTPUT_DIR = ROOT / "data/processed/sql"

QUERY_NAMES = [
    "annual_mobility",
    "country_balance",
    "relative_imbalance",
    "bilateral_flows",
]


def run_analysis(output_dir=OUTPUT_DIR):

    output_dir.mkdir(parents=True, exist_ok=True)

    queries = [
        query.strip()
        for query in SQL_PATH.read_text(
            encoding="utf-8"
        ).split(";")
        if query.strip()
    ]

    if len(queries) != len(QUERY_NAMES):
        raise ValueError("Unexpected number of SQL queries")

    timings = {}

    print("Starting SQL analysis...")

    with get_connection() as conn:
        with conn.cursor() as cur:

            for name, query in zip(QUERY_NAMES, queries):

                start = time.perf_counter()

                cur.execute(query)

                columns = [
                    col.name for col in cur.description
                ]

                rows = cur.fetchall()

                elapsed = time.perf_counter() - start
                timings[name] = elapsed

                output_path = output_dir / f"{name}.csv"

                with output_path.open(
                    "w",
                    encoding="utf-8",
                    newline=""
                ) as file:

                    writer = csv.writer(file)
                    writer.writerow(columns)
                    writer.writerows(rows)

                print(
                    f"{name}: {len(rows)} rows | "
                    f"{elapsed:.4f} seconds"
                )

    print("SQL analysis completed successfully!")

    return timings


if __name__ == "__main__":
    run_analysis()
