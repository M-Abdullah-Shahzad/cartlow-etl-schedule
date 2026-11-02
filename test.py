"""Diagnostic script for checking the source and target database connections.

Configure SOURCE_DATABASE_URL and TARGET_DATABASE_URL in your local .env file.
This script prints row-ID watermarks only; it never prints credentials.
"""

import os

import pandas as pd
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()


def _engine_from_env(name: str):
    url = os.getenv(name)
    if not url:
        raise RuntimeError(
            f"Missing {name}. Configure it in your local .env file."
        )
    return db.create_engine(url)


def main() -> None:
    source_engine = _engine_from_env("SOURCE_DATABASE_URL")
    target_engine = _engine_from_env("TARGET_DATABASE_URL")

    try:
        with source_engine.connect() as source_connection:
            source_max_df = pd.read_sql(
                "SELECT MAX(id) AS max_id FROM cartlow_prod.orders",
                source_connection,
            )
            source_max_id = source_max_df["max_id"].iloc[0]

        with target_engine.connect() as target_connection:
            try:
                target_max_df = pd.read_sql(
                    "SELECT MAX(id) AS max_id FROM orders",
                    target_connection,
                )
                target_max_id = target_max_df["max_id"].iloc[0]
            except Exception:
                target_max_id = 0

        source_max_id = 0 if pd.isna(source_max_id) else int(source_max_id)
        target_max_id = 0 if pd.isna(target_max_id) else int(target_max_id)

        print(f"Source MariaDB Max ID: {source_max_id}")
        print(f"Target PostgreSQL Max ID: {target_max_id}")
    finally:
        source_engine.dispose()
        target_engine.dispose()


if __name__ == "__main__":
    main()
