import sqlalchemy as db
import pandas as pd

if 'df' not in globals():
    df = pd.DataFrame()

dest_engine = db.create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432/cartlow_target'
)

if 'df' in globals() and not df.empty:
    dest_connect = dest_engine.connect()
    
    df.to_sql(
        name='orders', 
        con=dest_connect, 
        if_exists='append', 
        index=False,
        method='multi'
    )
    
    new_max_id = int(df['id'].max())
    dest_connect.execute(db.text(f"UPDATE pipeline_state SET last_id = {new_max_id}"))
    dest_connect.commit()
    
    dest_connect.close()