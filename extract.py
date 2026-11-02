import os

import pandas as pd
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and configure it before running the ETL."
        )
    return value


src_engine = db.create_engine(
    _required_env("SOURCE_DATABASE_URL"),
    connect_args={"connect_timeout": 60},
    pool_recycle=3600,
)

dest_engine = db.create_engine(_required_env("TARGET_DATABASE_URL"))

dest_connect = dest_engine.connect()
dest_connect.execute(db.text("CREATE TABLE IF NOT EXISTS pipeline_state (last_id BIGINT)"))
dest_connect.commit()

max_id_df = pd.read_sql("SELECT MAX(last_id) AS max_id FROM pipeline_state", dest_connect)
last_max_id = max_id_df["max_id"].iloc[0]

if pd.isna(last_max_id):
    dest_connect.execute(db.text("INSERT INTO pipeline_state VALUES (0)"))
    dest_connect.commit()
    last_max_id = 0
else:
    last_max_id = int(last_max_id)

dest_connect.close()

src_connect = src_engine.connect()
query = db.text(
    "SELECT * FROM cartlow_prod.orders WHERE id > :last_id ORDER BY id ASC"
).bindparams(last_id=int(last_max_id))
chunk_generator = pd.read_sql(query, src_connect, chunksize=10000)
