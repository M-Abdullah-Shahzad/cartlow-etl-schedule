import importlib
import logging
import os

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def trigger_metabase_sync() -> bool:
    """Trigger a Metabase schema refresh when credentials are configured."""
    base_url = os.getenv("METABASE_URL", "").rstrip("/")
    username = os.getenv("METABASE_USERNAME")
    password = os.getenv("METABASE_PASSWORD")
    database_id = os.getenv("METABASE_DATABASE_ID", "1")

    if not all((base_url, username, password, database_id)):
        logger.info("Metabase sync skipped: Metabase environment settings are incomplete.")
        return False

    try:
        with requests.Session() as session:
            auth_res = session.post(
                f"{base_url}/api/session",
                json={"username": username, "password": password},
                timeout=20,
            )
            auth_res.raise_for_status()
            token = auth_res.json().get("id")
            if not token:
                logger.error("Metabase authentication response did not contain a session ID.")
                return False

            sync_res = session.post(
                f"{base_url}/api/database/{database_id}/sync_schema",
                headers={"X-Metabase-Session": token},
                timeout=30,
            )
            sync_res.raise_for_status()

        logger.info("Metabase schema synchronization request completed.")
        return True
    except requests.RequestException:
        logger.exception("Metabase synchronization failed. Check the service and configured credentials.")
        return False


def run_etl_job() -> None:
    logger.info("Incremental ETL job started.")

    import extract
    importlib.reload(extract)

    has_data = False
    try:
        for chunk in extract.chunk_generator:
            has_data = True

            import transformation
            transformation.current_chunk = chunk
            importlib.reload(transformation)

            import load
            load.df = transformation.df
            importlib.reload(load)

            logger.info("Processed and loaded %s rows to PostgreSQL.", len(transformation.df))

        if not has_data:
            logger.info("No new orders found.")
        else:
            logger.info("ETL job finished. Triggering Metabase schema synchronization.")
            trigger_metabase_sync()
    finally:
        source_connection = getattr(extract, "src_connect", None)
        if source_connection is not None:
            source_connection.close()


def main() -> None:
    try:
        interval_minutes = int(os.getenv("ETL_INTERVAL_MINUTES", "0"))
    except ValueError as exc:
        raise RuntimeError("ETL_INTERVAL_MINUTES must be an integer.") from exc

    if interval_minutes < 0:
        raise RuntimeError("ETL_INTERVAL_MINUTES cannot be negative.")

    if interval_minutes == 0:
        run_etl_job()
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_etl_job,
        trigger="interval",
        minutes=interval_minutes,
        id="incremental_etl",
        max_instances=1,
        coalesce=True,
    )
    logger.info("Starting ETL scheduler with a %s-minute interval.", interval_minutes)
    scheduler.start()


if __name__ == "__main__":
    main()
