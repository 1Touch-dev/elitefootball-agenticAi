# PEDANT_HANDOFF_PAP-244

## Scope Completed
Implemented backend-side dashboard data auditing and artifact validation so the API can explain whether the dashboard is empty because data is missing, empty, or invalid.

## Root Cause Confirmed
The dashboard is correctly API-backed. The current no-data state is primarily caused by empty Silver/Gold artifacts in `data/`, not by the frontend calling the wrong endpoints or expecting a different payload shape.

## What Changed

### Artifact inspection and validation
- `app/api/data_access.py`
  - added `ArtifactInvalidError`
  - added `inspect_artifact(...)`
  - added `inspect_dashboard_artifacts(...)`
  - loaders now distinguish missing vs invalid artifacts instead of quietly returning `[]` for malformed payloads

### New backend debug/status endpoint
- `app/api/routes.py`
  - added `GET /dashboard/status`
  - existing endpoints now map invalid artifacts to HTTP 500 and missing required artifacts to HTTP 503

### Tests
- `tests/test_data_access.py`
  - validates empty, missing, invalid, and partial-ready artifact states
- `tests/test_api_routes.py`
  - added dashboard status route coverage
  - added invalid-artifact error-path coverage

### Audit artifact
- `PAP-244_BACKEND_DATA_FLOW_AUDIT.md`

## Verification Run
- `python3 -m unittest tests.test_data_access` ✅
- `python3 -m unittest tests.test_api_routes` ✅ (skipped because FastAPI is not installed in this sandbox)
- `python3 -m py_compile app/api/data_access.py app/api/routes.py tests/test_api_routes.py tests/test_data_access.py` ✅
- `python3 - <<'PY' ... inspect_dashboard_artifacts() ... PY` ✅

Observed live artifact status in this checkout:
- overall status: `empty`
- all major dashboard artifacts exist but currently have `row_count: 0`

## Things For Pedant To Check Closely
1. Whether optional artifacts (`player_features`, `kpi`) should affect top-level status exactly as implemented.
2. Whether invalid optional artifacts should continue to fail `/players` with 500 rather than degrade gracefully.
3. Whether the status endpoint should expose generation timestamps in a follow-up.
4. Whether `dashboard/api_client.py` and Streamlit pages should start using `/dashboard/status` in the next ticket.

## Files Changed
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- `tests/test_data_access.py`
- `PAP-244_BACKEND_DATA_FLOW_AUDIT.md`
- `memory/progress.md`
- `memory/decisions.md`

## Recommended Next Issue
PAP-245 - Surface dashboard artifact readiness directly in the UI and add pipeline generation timestamps to the backend status response.
