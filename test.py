import sqlalchemy as db
import pandas as pd

# Source MariaDB Connection
src_engine = db.create_engine(
    'mariadb+mariadbconnector://cartlow_bi_interns:yKA57ZbGDre4r5tr3hn0HTRy@46.101.156.26:3306/cartlow_prod',
    connect_args={'connect_timeout': 60},
    pool_recycle=3600
)

# Target PostgreSQL Connection
dest_engine = db.create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432/cartlow_target'
)

# Fetch Max ID from Source (MariaDB)
src_connect = src_engine.connect()
src_max_df = pd.read_sql("SELECT MAX(id) as max_id FROM cartlow_prod.orders", src_connect)
src_max_id = src_max_df['max_id'].iloc[0]
src_connect.close()

# Fetch Max ID from Target (PostgreSQL)
dest_connect = dest_engine.connect()
try:
    dest_max_df = pd.read_sql("SELECT MAX(id) as max_id FROM orders", dest_connect)
    dest_max_id = dest_max_df['max_id'].iloc[0]
except Exception:
    dest_max_id = 0
dest_connect.close()

# Handle None/NaN cases if tables are empty
src_max_id = 0 if pd.isna(src_max_id) else int(src_max_id)
dest_max_id = 0 if pd.isna(dest_max_id) else int(dest_max_id)

print(f"Source MariaDB Max ID (cartlow_prod.orders): {src_max_id}")
print(f"Target PostgreSQL Max ID (cartlow_target.orders): {dest_max_id}")