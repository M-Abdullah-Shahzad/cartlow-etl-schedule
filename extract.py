import os

import pandas as pd
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()


def _required_database_url(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name}. "
            "Copy .env.example to .env and configure the database URL."
        )
    return value


def get_source_engine():
    """Create the MariaDB source engine without opening a connection at import time."""
    return db.create_engine(
        _required_database_url("SOURCE_DATABASE_URL"),
        connect_args={"connect_timeout": 60},
        pool_recycle=3600,
    )


def get_target_engine():
    """Create the PostgreSQL target engine."""
    return db.create_engine(_required_database_url("TARGET_DATABASE_URL"))


def ensure_pipeline_state(target_engine) -> int:
    """Create/read the single high-water-mark row in the target database."""
    with target_engine.begin() as connection:
        connection.execute(
            db.text(
                "CREATE TABLE IF NOT EXISTS pipeline_state "
                "(last_id BIGINT NOT NULL)"
            )
        )
        last_id = connection.execute(
            db.text("SELECT MAX(last_id) FROM pipeline_state")
        ).scalar_one()

        if last_id is None:
            connection.execute(
                db.text("INSERT INTO pipeline_state (last_id) VALUES (0)")
            )
            return 0

        return int(last_id)


def extract_order_chunks(source_engine, last_id: int, chunksize: int = 10000):
    """Yield source orders newer than the saved high-water mark."""
    query = db.text(
        "SELECT * FROM cartlow_prod.orders "
        "WHERE id > :last_id ORDER BY id ASC"
    ).bindparams(last_id=int(last_id))

    with source_engine.connect() as connection:
        for chunk in pd.read_sql(query, connection, chunksize=chunksize):
            yield chunk
