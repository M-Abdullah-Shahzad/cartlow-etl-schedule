import sqlalchemy as db
import pandas as pd

src_engine = db.create_engine(
    'mariadb+mariadbconnector://cartlow_bi_interns:yKA57ZbGDre4r5tr3hn0HTRy@46.101.156.26:3306/cartlow_prod',
    connect_args={'connect_timeout': 60},
    pool_recycle=3600
)

dest_engine = db.create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432/cartlow_target'
)

dest_connect = dest_engine.connect()

dest_connect.execute(db.text("CREATE TABLE IF NOT EXISTS pipeline_state (last_id BIGINT)"))
dest_connect.commit()

max_id_df = pd.read_sql("SELECT MAX(last_id) as max_id FROM pipeline_state", dest_connect)
last_max_id = max_id_df['max_id'].iloc[0]

if pd.isna(last_max_id):
    dest_connect.execute(db.text("INSERT INTO pipeline_state VALUES (0)"))
    dest_connect.commit()
    last_max_id = 0
else:
    last_max_id = int(last_max_id)

dest_connect.close()

src_connect = src_engine.connect()
query = db.text(f"SELECT * FROM cartlow_prod.orders WHERE id > {last_max_id} ORDER BY id ASC")
chunk_generator = pd.read_sql(query, src_connect, chunksize=10000)