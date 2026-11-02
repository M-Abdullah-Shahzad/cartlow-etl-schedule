import pandas as pd
import sqlalchemy as db
from dotenv import load_dotenv

load_dotenv()


def load_chunk(dataframe: pd.DataFrame, target_engine, chunksize: int = 1000) -> int:
    """Append one transformed chunk and advance the high-water mark atomically."""
    if dataframe.empty:
        raise ValueError("Cannot load an empty dataframe.")
    if "id" not in dataframe.columns:
        raise ValueError("The transformed dataframe must contain an 'id' column.")

    new_max_id = int(pd.to_numeric(dataframe["id"], errors="raise").max())

    with target_engine.begin() as connection:
        dataframe.to_sql(
            name="orders",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize,
        )
        result = connection.execute(
            db.text("UPDATE pipeline_state SET last_id = :last_id"),
            {"last_id": new_max_id},
        )
        if result.rowcount == 0:
            connection.execute(
                db.text("INSERT INTO pipeline_state (last_id) VALUES (:last_id)"),
                {"last_id": new_max_id},
            )

    return new_max_id
