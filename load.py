import os

import pandas as pd
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()

if "df" not in globals():
    df = pd.DataFrame()

target_database_url = os.getenv("TARGET_DATABASE_URL")
if not target_database_url:
    raise RuntimeError(
        "Missing required environment variable: TARGET_DATABASE_URL. "
        "Copy .env.example to .env and configure it before running the ETL."
    )

dest_engine = db.create_engine(target_database_url)

if "df" in globals() and not df.empty:
    with dest_engine.begin() as dest_connect:
        df.to_sql(
            name="orders",
            con=dest_connect,
            if_exists="append",
            index=False,
            method="multi",
        )

        new_max_id = int(df["id"].max())
        dest_connect.execute(
            db.text("UPDATE pipeline_state SET last_id = :last_id"),
            {"last_id": new_max_id},
        )
