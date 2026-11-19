
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")


def get_connection():
    """Create a connection to PostgreSQL."""

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
    )


if __name__ == "__main__":

    print("Starting database connection...", flush=True)

    try:
        with get_connection() as conn:

            print("Connected successfully!", flush=True)

            with conn.cursor() as cur:

                cur.execute("SELECT current_database();")
                print("Database:", cur.fetchone()[0])

                cur.execute("SELECT version();")
                print("PostgreSQL version:", cur.fetchone()[0])

    except Exception as error:
        print("Database connection failed:")
        print(error)
        raise
