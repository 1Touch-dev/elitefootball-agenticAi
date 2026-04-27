# GRUNT HANDOFF — PAP-246

## Scope Completed
Implemented a deterministic seeded end-to-end validation workflow for the scrape-to-dashboard path.

## Root Cause Confirmed
There was no single command/workflow validating the full path from scrape-like input through pipeline output and into dashboard-consumable data. Existing tests were seam-local:
- route tests mocked loaders
- dashboard client tests mocked HTTP
- current checked-in artifacts are empty, so they could not prove the happy path

## What Changed

### Core validation helper
- `tests/e2e_dashboard_flow_support.py`
  - seeds sample raw + parsed inputs into a temporary workspace
  - runs the real pipeline via `run_pipeline()`
  - verifies Bronze/Silver/Gold artifact counts and storage
  - optionally verifies backend/API + dashboard client paths when FastAPI is available
  - returns stage-by-stage PASS/FAIL results plus limitations

### One-command regression test
- `tests/test_e2e_dashboard_flow.py`
  - runnable with:
    - `python3 -m unittest tests.test_e2e_dashboard_flow`

### Operator-friendly verification script
- `scripts/verify_dashboard_flow.py`
  - runnable with:
    - `python3 scripts/verify_dashboard_flow.py`
  - prints stage-by-stage PASS/FAIL output

### Documentation
- `README.md`
  - added end-to-end validation instructions and known limitations

## Verification Run
- `python3 -m unittest tests.test_e2e_dashboard_flow` ✅
- `python3 scripts/verify_dashboard_flow.py` ✅
- `python3 -m py_compile tests/e2e_dashboard_flow_support.py tests/test_e2e_dashboard_flow.py scripts/verify_dashboard_flow.py` ✅

Observed in this environment:
- seeded mode passes
- FastAPI is unavailable here, so backend-route and dashboard-client stages are skipped cleanly
- the core pipeline/artifact validation still executes and passes

## Known Limitations
- the required regression path uses seeded parsed inputs, not a mandatory live scrape
- live scrape validation remains best-effort because source access and Playwright/browser setup are environment-sensitive
- dashboard validation stops at payload receipt, not full browser automation
- when FastAPI is unavailable, route/client stages are skipped rather than hard-failing the whole workflow

## Files Changed
- `tests/e2e_dashboard_flow_support.py`
- `tests/test_e2e_dashboard_flow.py`
- `scripts/verify_dashboard_flow.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`
- `ARCHITECT_PLAN_PAP-246.md`
- `GRUNT_HANDOFF_PAP-246.md`
- `PEDANT_HANDOFF_PAP-246.md`

## Next Recommended Issue
PAP-247 - make `full_refresh` self-targeting with a concrete scrape target registry so optional live E2E validation does not require manual URL injection.
