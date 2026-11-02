import pandas as pd
from sqlalchemy import create_engine, text

from extract import ensure_pipeline_state
from load import load_chunk
from transformation import transform_chunk


def test_transform_chunk_removes_duplicates_and_normalizes_values():
    source = pd.DataFrame([
        {"id": 1, "quantity": 2, "description": "  item  "},
        {"id": 1, "quantity": 2, "description": "  item  "},
        {"id": 2, "quantity": None, "description": None},
    ])

    transformed = transform_chunk(source)

    assert len(transformed) == 2
    assert transformed.loc[transformed["id"] == 1, "description"].iloc[0] == "item"
    assert transformed.loc[transformed["id"] == 2, "quantity"].iloc[0] == 0
    assert transformed.loc[transformed["id"] == 2, "description"].iloc[0] == "N/A"
    assert transformed["transformed_column"].tolist() == [1, 2]


def test_load_updates_pipeline_state_in_same_database_transaction():
    engine = create_engine("sqlite:///:memory:")
    try:
        assert ensure_pipeline_state(engine) == 0
        rows = transform_chunk(pd.DataFrame([
            {"id": 10, "quantity": 1, "description": "first"},
            {"id": 11, "quantity": 2, "description": "second"},
        ]))

        assert load_chunk(rows, engine) == 11

        with engine.connect() as connection:
            last_id = connection.execute(
                text("SELECT MAX(last_id) FROM pipeline_state")
            ).scalar_one()
            count = connection.execute(
                text("SELECT COUNT(*) FROM orders")
            ).scalar_one()

        assert last_id == 11
        assert count == 2
    finally:
        engine.dispose()
