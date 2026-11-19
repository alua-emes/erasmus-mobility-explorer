
import csv
import time

from database import ROOT, get_connection


DATA_PATH = (
    ROOT
    / "data/raw/Erasmus_2014-2023_aggregate_NUTS.csv"
)

REQUIRED_COLUMNS = {
    "OD_ID",
    "ORIGIN",
    "DESTINATION",
    "YEAR",
    "COUNT",
}


def load_data():

    if not DATA_PATH.is_file():
        raise FileNotFoundError(DATA_PATH)

    print("Loading Erasmus+ mobility data...")

    start = time.perf_counter()
    rows_loaded = 0

    with get_connection() as conn:
        with conn.cursor() as cur:

            # Reset the table before loading
            cur.execute(
                "TRUNCATE TABLE mobility RESTART IDENTITY;"
            )

            # Load records using PostgreSQL COPY
            with DATA_PATH.open(
                "r",
                encoding="utf-8-sig",
                newline=""
            ) as file:

                reader = csv.DictReader(
                    file,
                    delimiter=";"
                )

                if not REQUIRED_COLUMNS.issubset(
                    reader.fieldnames or []
                ):
                    raise ValueError(
                        "Unexpected CSV structure"
                    )

                with cur.copy("""
                    COPY mobility (
                        od_id,
                        origin,
                        destination,
                        year,
                        count
                    )
                    FROM STDIN
                """) as copy:

                    for row in reader:

                        copy.write_row((
                            row["OD_ID"],
                            row["ORIGIN"],
                            row["DESTINATION"],
                            int(row["YEAR"]),
                            int(row["COUNT"]),
                        ))

                        rows_loaded += 1

            # Validate the number of loaded rows
            cur.execute("SELECT COUNT(*) FROM mobility;")
            database_rows = cur.fetchone()[0]

            assert database_rows == rows_loaded

        conn.commit()

    elapsed = time.perf_counter() - start

    print("Data loading completed successfully!")
    print(f"Rows loaded: {rows_loaded:,}")
    print(f"Database rows: {database_rows:,}")
    print(f"Loading time: {elapsed:.3f} seconds")


if __name__ == "__main__":
    load_data()
