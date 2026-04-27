# PEDANT_HANDOFF_PAP-243

## Scope Completed
Implemented the Silver-to-DB persistence path planned in PAP-243 without changing scraper architecture.

## What Changed

### New DB ingestion module
- `app/db/persistence.py`
  - ensures schema exists
  - ingests Silver tables into `clubs`, `players`, `matches`, `stats`
  - logs validation failures and write failures
  - writes `data/bronze/persistence_report.json`
  - runs post-commit verification queries with counts + sample rows

### Silver write verification
- `app/pipeline/silver.py`
  - now re-reads each written Silver JSON artifact
  - verifies row counts immediately
  - raises on count mismatch instead of silently continuing

### Pipeline integration
- `app/pipeline/run_pipeline.py`
  - now returns `persistence` in the pipeline result
  - ingests Silver rows before Gold/KPI downstream analysis

### Tests added
- `tests/test_db_persistence.py`
  - success path
  - validation-failure path

## Root Cause Confirmed
The DB layer existed only as scaffolding. Scraped data was being stored to files, but there was no actual DB ingestion path, no verification query path, and no structured persistence report.

## Things For Pedant To Check Closely
1. **Player identity strategy**
   - fallback player creation in stat ingestion currently uses `(player_name, club_id, source)` MVP logic
   - confirm this is acceptable for current scope and doesn’t over-duplicate when Transfermarkt/FBref names differ slightly

2. **Club short-code derivation**
   - generated codes are deterministic enough for MVP, but pedant should confirm collision handling is acceptable

3. **Match resolution fallback**
   - primary path uses `match_external_id`
   - composite fallback exists but current Silver stat rows mostly rely on external IDs
   - check whether more match context should be propagated into Silver rows later

4. **Status classification**
   - currently returns `success_complete`, `success_partial`, or `validation_failed`
   - confirm whether `verification_failed` should be surfaced explicitly in more scenarios

5. **Environment blocker**
   - sandbox lacks installed `sqlalchemy`, so runtime DB tests could not execute here
   - syntax checking succeeded with `python3 -m py_compile ...`
   - pedant should run the new tests in an environment with dependencies installed

## Commands Run
- `python3 -m unittest tests.test_db_persistence` -> failed because `sqlalchemy` is not installed in this sandbox
- `python3 - <<'PY' ... run_pipeline() ... PY` -> failed for the same dependency reason
- `python3 -m py_compile app/db/persistence.py app/pipeline/silver.py app/pipeline/run_pipeline.py tests/test_db_persistence.py` -> passed

## Files Changed
- `app/db/persistence.py`
- `app/pipeline/silver.py`
- `app/pipeline/run_pipeline.py`
- `tests/test_db_persistence.py`
- `PAP-243_PERSISTENCE_AUDIT_REPORT.md`

## Recommended Next Issue
PAP-244 - Add optional DB-backed read/verification endpoints while keeping the current artifact-backed dashboard contract stable.
