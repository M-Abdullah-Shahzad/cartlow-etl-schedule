import time
import importlib
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

METABASE_URL = "http://localhost:3000"
METABASE_USER = "abdullahrana5677@gmail.com"  
METABASE_PASSWORD = "metabase1"       
DATABASE_ID = 1                                    

def trigger_metabase_sync():
    session = requests.Session()
    auth_res = session.post(f"{METABASE_URL}/api/session", json={
        "username": METABASE_USER,
        "password": METABASE_PASSWORD
    })
    
    if auth_res.status_code == 200:
        token = auth_res.json().get("id")
        headers = {"X-Metabase-Session": token}
        
        
        session.post(f"{METABASE_URL}/api/database/{DATABASE_ID}/sync_schema", headers=headers)
        print("Metabase database synchronization triggered successfully.")
    else:
        print("Metabase authentication failed. Check credentials in schedule.py.")

def run_etl_job():
    print("Incremental ETL Job started...")
    
    import extract
    importlib.reload(extract)
    
    has_data = False
    for chunk in extract.chunk_generator:
        has_data = True
        
        import transformation
        transformation.current_chunk = chunk
        importlib.reload(transformation)
        
        import load
        load.df = transformation.df
        importlib.reload(load)
        
        print(f"Processed and loaded chunk of {len(transformation.df)} rows to PostgreSQL.")
        
    extract.src_connect.close()
    
    if not has_data:
        print("No new orders found.")
    else:
        print("ETL Job finished successfully. Updating Metabase dashboard...")
        trigger_metabase_sync()


run_etl_job()


# scheduler = BlockingScheduler()
# scheduler.add_job(run_etl_job, 'interval', minutes=2)

# print("APScheduler active. Running incremental pipeline every 2 minutes...")
# scheduler.start()