
import csv
import statistics
import time

from database import ROOT, get_connection


OUTPUT_DIR = ROOT / "data/processed/sql"
REPEATS = 3

QUERY = """
    SELECT
        dest_country,
        SUM(count) AS total_mobility
    FROM mobility
    WHERE origin_country = 'AL'
        AND year = 2022
        AND same_country = FALSE
    GROUP BY dest_country
    ORDER BY total_mobility DESC, dest_country;
"""

INDEX_SQL = """
    CREATE INDEX idx_mobility_benchmark
    ON mobility (origin_country, year)
    WHERE same_country = FALSE;
"""


def get_scan_types(plan):

    scans = []

    if "Scan" in plan["Node Type"]:
        scans.append(plan["Node Type"])

    for child in plan.get("Plans", []):
        scans.extend(get_scan_types(child))

    return scans


def measure_query(cur):

    cur.execute(
        "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
        + QUERY
    )

    result = cur.fetchone()[0][0]

    return (
        result["Execution Time"],
        ", ".join(get_scan_types(result["Plan"]))
    )


def benchmark_indexes():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT COUNT(*) FROM mobility;")

            if cur.fetchone()[0] != 588109:
                raise ValueError("Full dataset required")

            cur.execute("ANALYZE mobility;")

            # Baseline: existing indexes only
            print("\nWITHOUT ADDITIONAL INDEX")

            cur.execute(QUERY)
            baseline_rows = cur.fetchall()

            # Warm-up
            measure_query(cur)

            for run in range(1, REPEATS + 1):

                elapsed, scan = measure_query(cur)

                results.append({
                    "condition": "without_index",
                    "run": run,
                    "execution_ms": elapsed,
                    "scan_type": scan,
                })

                print(f"Run {run}: {elapsed:.3f} ms")
                print(f"Scan: {scan}")

            # Create experimental index
            start = time.perf_counter()

            cur.execute(INDEX_SQL)

            creation_time = time.perf_counter() - start

            cur.execute("""
                SELECT pg_relation_size(
                    'idx_mobility_benchmark'
                );
            """)

            index_bytes = cur.fetchone()[0]

            print(
                f"\nIndex creation: "
                f"{creation_time:.3f} seconds"
            )

            print(
                f"Index size: "
                f"{index_bytes / 1024**2:.3f} MiB"
            )

            cur.execute(QUERY)

            if cur.fetchall() != baseline_rows:
                raise ValueError("Query results differ")

            print("Query result validation passed.")

            # Indexed experiment
            print("\nWITH ADDITIONAL INDEX")

            # Warm-up
            measure_query(cur)

            for run in range(1, REPEATS + 1):

                elapsed, scan = measure_query(cur)

                results.append({
                    "condition": "with_index",
                    "run": run,
                    "execution_ms": elapsed,
                    "scan_type": scan,
                })

                print(f"Run {run}: {elapsed:.3f} ms")
                print(f"Scan: {scan}")

        # Remove experimental index by rolling back
        conn.rollback()

    without_index = statistics.mean(
        row["execution_ms"]
        for row in results
        if row["condition"] == "without_index"
    )

    with_index = statistics.mean(
        row["execution_ms"]
        for row in results
        if row["condition"] == "with_index"
    )

    speedup = without_index / with_index

    for row in results:
        row["index_bytes"] = (
            index_bytes
            if row["condition"] == "with_index"
            else 0
        )

        row["index_creation_seconds"] = (
            creation_time
            if row["condition"] == "with_index"
            else 0
        )

    output_path = OUTPUT_DIR / "index_benchmark.csv"

    with output_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0])
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nINDEX BENCHMARK SUMMARY")

    print(f"Without index: {without_index:.3f} ms")
    print(f"With index: {with_index:.3f} ms")
    print(f"Speedup: {speedup:.2f}x")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    benchmark_indexes()
