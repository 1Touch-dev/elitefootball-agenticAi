# PAP-243 Persistence Audit Report

## Ticket
PAP-243 - Audit and Fix Persistence Layer for Scraped Data

## Root Cause Found
The project was successfully persisting scraped data to file artifacts, but **not** to the relational database.

### Specifically
- raw HTML persistence existed
- parsed JSON persistence existed
- Silver/Gold artifact persistence existed
- SQLAlchemy engine/session/model scaffolding existed
- **no active Silver-to-DB ingestion layer existed**
- **no post-write verification queries existed**
- **no machine-readable persistence report existed**

This meant the DB looked configured, but scraped data was never actually inserted there.

## What Was Implemented

### 1) Real DB ingestion from Silver tables
Added `app/db/persistence.py` with:
- schema bootstrap via `Base.metadata.create_all(...)`
- club upserts
- player upserts
- match upserts
- stat upserts
- validation error capture
- rollback-safe write failure logging
- verification queries after commit

### 2) Record-count verification for Silver writes
Updated `app/pipeline/silver.py` so each Silver JSON write is immediately re-read and count-verified.

### 3) Pipeline integration
Updated `app/pipeline/run_pipeline.py` so the standard pipeline now:
- builds Bronze
- builds Silver
- ingests Silver into DB
- returns persistence results alongside downstream analysis artifacts

### 4) Test coverage
Added `tests/test_db_persistence.py` for:
- successful ingest path
- validation-failure path without silent success

## Persistence Behavior After Fix

### File-backed persistence
- Silver JSON outputs are now verified after write
- count mismatches raise explicit errors

### DB-backed persistence
- Silver rows are translated into normalized DB rows
- foreign-key resolution is handled through clubs/players/matches
- stat writes use `(match_id, player_id)` uniqueness semantics
- failures are recorded in the persistence report instead of disappearing silently

## Verification Query Results Produced by the New Code
The new persistence layer emits:
- total row counts for `clubs`, `players`, `matches`, `stats`
- sample queried rows for each major entity type
- machine-readable report artifact at `data/bronze/persistence_report.json`

## Environment Note
Runtime verification in this sandbox is partially blocked because the current environment does not have `sqlalchemy` installed, even though it is declared in `requirements.txt`.

Observed command failure:
- `ModuleNotFoundError: No module named 'sqlalchemy'`

So:
- code was syntax-checked with `py_compile`
- DB integration tests were added
- full runtime execution of DB ingestion remains dependent on installing project requirements

## Files Changed
- `app/db/persistence.py`
- `app/pipeline/silver.py`
- `app/pipeline/run_pipeline.py`
- `tests/test_db_persistence.py`

## Next Recommended Issue
PAP-244 - Add DB-backed read endpoints or optional DB-backed API verification paths without replacing the current artifact-backed dashboard contract.
