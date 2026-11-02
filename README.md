# Cartlow Incremental ETL Pipeline

A Python ETL pipeline that incrementally extracts Cartlow order records from MariaDB, transforms each chunk, loads it into PostgreSQL, and optionally requests a Metabase schema refresh.

## Architecture

```text
MariaDB: cartlow_prod.orders
          |
          v
extract.py — parameterized query using saved last_id
          |
          v
transformation.py — chunk cleanup and normalization
          |
          v
load.py — PostgreSQL append + atomic high-water-mark update
          |
          v
PostgreSQL: orders + pipeline_state
          |
          v
Optional Metabase schema synchronization
```

## Requirements

- Python 3.12 (matches `.python-version` and `pyproject.toml`)
- MariaDB source database with read access to `cartlow_prod.orders`
- PostgreSQL target database with create/insert/update permissions
- Optional Metabase instance and account authorized to request schema synchronization

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and configure:

   - `SOURCE_DATABASE_URL` — SQLAlchemy MariaDB connection URL
   - `TARGET_DATABASE_URL` — SQLAlchemy PostgreSQL connection URL

3. Optional Metabase configuration:

   - `METABASE_URL`
   - `METABASE_USERNAME`
   - `METABASE_PASSWORD`
   - `METABASE_DATABASE_ID`

   Leave these unset to skip Metabase synchronization.

## Run once

```bash
python schedule.py
```

By default, the pipeline executes one incremental cycle and exits.

## Enable recurring execution

Set `ETL_INTERVAL_MINUTES` to a positive integer in `.env` or the process environment:

```text
ETL_INTERVAL_MINUTES=30
```

Then run `python schedule.py`. The process stays active and runs the ETL at the configured interval. Set the value back to `0` for one-shot execution.

## Diagnostic

```bash
python test.py
```

The diagnostic compares the maximum order IDs in the source and target databases. It uses the same environment variables and does not print connection strings or credentials.

## Operational behavior

- The source query is parameterized and selects IDs greater than the saved high-water mark.
- Source rows are processed in chunks.
- The target insert and high-water-mark update occur in the same database transaction.
- The load uses bounded multi-row inserts to avoid oversized PostgreSQL statements.
- Database engines and source connections are closed/disposed after each ETL cycle.
- Metabase synchronization is optional and skipped when its configuration is incomplete.
- Scheduling is opt-in; a default run does not remain active.

## Security

Never commit `.env`, production connection strings, API tokens, private keys, or database exports. The values previously committed to this repository must be rotated with the relevant database and service owners. Removing a value from the latest source does not remove it from Git history.

## Repository layout

- `extract.py` — database engines, pipeline state, and chunk extraction
- `transformation.py` — deterministic chunk transformation
- `load.py` — transactional PostgreSQL load and state update
- `schedule.py` — one-shot runner, optional scheduler, and Metabase sync
- `test.py` — connection and high-water-mark diagnostic
