import pandas as pd


def transform_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Apply the existing lightweight cleanup to one extracted order chunk."""
    if chunk is None or chunk.empty:
        return pd.DataFrame()

    dataframe = chunk.drop_duplicates().copy()

    for column in dataframe.columns:
        if not dataframe[column].isna().any():
            continue
        if pd.api.types.is_numeric_dtype(dataframe[column]):
            dataframe[column] = dataframe[column].fillna(0)
        else:
            dataframe[column] = dataframe[column].fillna("N/A")

    for column in dataframe.select_dtypes(include=["object"]).columns:
        dataframe[column] = dataframe[column].astype(str).str.strip()

    if "id" not in dataframe.columns:
        raise ValueError("Source order data must contain an 'id' column.")

    dataframe["transformed_column"] = dataframe["id"]
    return dataframe
