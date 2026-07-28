import pandas as pd

if 'current_chunk' not in globals():
    current_chunk = pd.DataFrame()

df = current_chunk

if not df.empty:
    df = df.drop_duplicates()
    df = df.fillna(0)
    df = df.fillna('N/A')

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    df['transformed_column'] = df['id']