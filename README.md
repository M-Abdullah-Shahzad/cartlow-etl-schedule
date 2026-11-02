# Cartlow Incremental ETL Pipeline

A Python ETL pipeline that extracts new Cartlow orders from MariaDB in chunks, applies lightweight transformations, loads them into PostgreSQL, and can request a Metabase schema refresh after a successful load.

## Architecture

1. **Extract** — reads the current high-water mark from PostgreSQL and selects source orders with a larger ID.
2. **Transform** — removes duplicate rows, fills null values, trims text columns, and adds the existing `transformed_column`.
3. **Load** — appends the transformed rows and updates the pipeline high-water mark in the same PostgreSQL transaction.
4. **Optional BI sync** — requests a Metabase schema refresh when Metabase settings are supplied.

## Technology

Python, Pandas, SQLAlchemy, MariaDB Connector/Python, PostgreSQL, APScheduler, Requests, python-dotenv, and Metabase.

## Requirements

- Python 3.10 or newer
- Access to a MariaDB source database with read permission on `cartlow_prod.orders`
- A PostgreSQL target database with permission to create and update the pipeline state table
- Optional: a reachable Metabase instance and account allowed to request database schema synchronization

## Setup

1. Clone this repository and enter its directory.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set the connection details. Do not commit `.env` or paste production credentials into source files.

   Required:
   - `SOURCE_DATABASE_URL` — SQLAlchemy URL for the MariaDB source
   - `TARGET_DATABASE_URL` — SQLAlchemy URL for the PostgreSQL target

   Optional Metabase settings:
   - `METABASE_URL`
   - `METABASE_USERNAME`
   - `METABASE_PASSWORD`
   - `METABASE_DATABASE_ID`

   Optional scheduling:
   - `ETL_INTERVAL_MINUTES` — defaults to `0`, which runs the pipeline once. Set a positive integer to run repeatedly at that interval.

5. Run the pipeline:

   ```bash
   python schedule.py
   ```

## Example environment file

See [\.env.example](.env.example). Use your own database credentials and never commit populated environment files.

## Operational notes

- The source query is parameterized and uses the saved high-water mark.
- The target load and high-water-mark update run in one transaction.
- The scheduler is opt-in. A default run completes once and exits, matching the script's prior one-shot execution behavior.
- Metabase synchronization is skipped when its settings are absent.
- The pipeline does not create production source credentials; obtain authorization and credentials from the database owner.
- Before deploying, confirm that the source user has least-privilege read access and that the target database is backed up.

## Repository layout

- `extract.py` — source extraction and pipeline-state lookup
- `transformation.py` — chunk transformation
- `load.py` — PostgreSQL load and state update
- `schedule.py` — one-shot runner, optional scheduler, and optional Metabase sync
