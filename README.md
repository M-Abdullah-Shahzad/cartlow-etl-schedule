Project Overview

This repository contains an incremental extract, transform, and load pipeline designed to fetch data from a production MariaDB database and load it into a local PostgreSQL database. The pipeline uses ID-based incremental loading to ensure that only new records are processed during each run, optimizing resource usage and execution time. The entire workflow is automated using APScheduler and includes automatic synchronization with Metabase.

Key Features

* Incremental Data Extraction: Tracks the maximum record identifier from the target state table to fetch only new records from the source database.
* Chunked Processing: Processes large datasets in manageable chunks to prevent memory overhead and connection timeouts.
* Automated Scheduling: Runs the pipeline automatically at fixed intervals using APScheduler.
* Business Intelligence Sync: Triggers Metabase schema updates automatically after data loading completes.

Technology Stack

* Language: Python
* Libraries: SQLAlchemy, Pandas, APScheduler, Psycopg2, MariaDB Connector
* Databases: MariaDB, PostgreSQL
* Dashboard Tool: Metabase

Project Structure

* schedule.py: The main script that manages the scheduled execution of the pipeline.
* extract.py: Handles connection management, state tracking, and incremental data extraction.
* requirements.txt: Lists all required Python dependencies for the project.

Setup and Installation

1. Clone the repository:
git clone [https://github.com/Abdullah17521/cartlow-etl-schedule.git](https://www.google.com/search?q=https://github.com/Abdullah17521/cartlow-etl-schedule.git)
2. Navigate to the project directory:
cd cartlow-etl-schedule
3. Create and activate a virtual environment:
python -m venv .venv
.venv\Scripts\Activate
4. Install the required dependencies:
pip install -r requirements.txt
5. Run the scheduler:
python schedule.py
