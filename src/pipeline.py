
import time

from database import ROOT, get_connection
from load_database import load_data
from run_analysis import run_analysis
from download_data import ensure_dataset

def initialize_database():

    schema = (
        ROOT / "sql/schema.sql"
    ).read_text(encoding="utf-8")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)

    print("Database schema initialized.")


def validate_database():

    query = """
        SELECT
            COUNT(*),
            SUM(count),
            COUNT(*) FILTER (
                WHERE same_country = FALSE
            ),
            SUM(count) FILTER (
                WHERE same_country = FALSE
            )
        FROM mobility;
    """

    expected = (
        588109,
        2554116,
        587225,
        2551560,
    )

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(query)
            actual = cur.fetchone()

    if actual != expected:
        raise ValueError(
            f"Validation failed: {actual}"
        )

    print("Database validation passed.")
    print(f"Total records: {actual[0]:,}")
    print(f"Total mobility: {actual[1]:,}")
    print(f"International records: {actual[2]:,}")
    print(f"International mobility: {actual[3]:,}")


def main():

    start = time.perf_counter()

    print("=" * 50)
    print("ERASMUS+ MOBILITY DATA PIPELINE")
    print("=" * 50)
    
    print("[1/5] Checking dataset...")
    ensure_dataset()

    print("\n[2/5] Initializing database...")
    initialize_database()

    print("\n[3/5] Loading dataset...")
    load_data()

    print("\n[4/5] Validating database...")
    validate_database()

    print("\n[5/5] Running SQL analysis...")
    run_analysis()

    elapsed = time.perf_counter() - start

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Total execution time: {elapsed:.3f} seconds")
    print("=" * 50)


if __name__ == "__main__":
    main()
