# GRUNT HANDOFF — PAP-247

## Scope Completed
Implemented dashboard empty-state and failure-message improvements without changing the artifact-backed architecture.

## Root Cause Found
The dashboard already handled many failure paths without crashing, but it still left users with ambiguous states because:
- `/dashboard/status` exposed artifact state only, not sync/failure metadata
- Home/Player/Compare used generic messages that did not clearly distinguish backend failure vs missing/empty/invalid artifacts vs no records for the current view
- pages stopped early once data was empty, which made the UI feel blank or silently broken
- there was no explicit retry affordance in the dashboard itself

## What Changed

### Backend status metadata
- `app/api/data_access.py`
  - enriched `inspect_dashboard_artifacts()` with:
    - `diagnostics.upstream_status`
    - `diagnostics.recommended_action`
    - `sync.last_successful_sync_at`
    - `sync.last_failed_sync_at`
    - `sync.last_failure_stage`
    - `sync.last_failure_message`
    - `sync.recommended_action`
  - uses artifact mtimes as a safe fallback approximation for last successful sync
  - keeps failure fields nullable when there is no authoritative failure timestamp

### Shared dashboard UX helpers
- `dashboard/helpers.py`
  - added `format_sync_time(...)`
  - added `build_dashboard_state(...)`
  - added `placeholder_message_lines(...)`
  - kept the older explain-* helpers but made their wording clearer for empty/no-record cases

### Home page UX
- `dashboard/Home.py`
  - now renders a richer status panel with:
    - explicit title/message severity
    - last successful sync detail when available
    - latest failure detail when available
    - next-step guidance
    - retry button via `st.rerun()`

### Player page UX
- `dashboard/pages/1_Player.py`
  - now distinguishes backend failure from empty player data
  - shows friendlier placeholder content before stopping
  - adds retry button
  - shows placeholder text when valuation/KPI/stats are missing instead of leaving sections feeling blank
  - recent-match-stats section now reports no-record vs backend-error cases more clearly

### Compare page UX
- `dashboard/pages/2_Compare.py`
  - now distinguishes backend failure from empty player/comparison data
  - adds retry button
  - shows explicit placeholder messaging for missing comparison features / no similar players
  - warns separately when valuation enrichment is unavailable even though similarity rows loaded

### Tests updated
- `tests/test_data_access.py`
- `tests/test_dashboard_api_client.py`
- `tests/test_api_routes.py`

## Verification Run
- `python3 -m unittest tests.test_data_access tests.test_dashboard_api_client` ✅
- `python3 -m py_compile app/api/data_access.py dashboard/helpers.py dashboard/Home.py dashboard/pages/1_Player.py dashboard/pages/2_Compare.py tests/test_data_access.py tests/test_dashboard_api_client.py tests/test_api_routes.py` ✅
- `python3 -m unittest tests.test_api_routes` ✅ (skipped in this environment because FastAPI is unavailable)

## Known Limitations
- `last_successful_sync_at` is currently approximated from artifact mtimes when explicit run metadata is unavailable
- `last_failed_sync_at` often remains null because the current product path does not yet persist authoritative run-failure timestamps
- backend-error differentiation on Streamlit pages is driven by request exceptions rather than a richer health channel
- page behavior is improved via helper-backed messaging, but there is still no dedicated backend operations history artifact

## Files Changed
- `app/api/data_access.py`
- `dashboard/helpers.py`
- `dashboard/Home.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- `tests/test_data_access.py`
- `tests/test_dashboard_api_client.py`
- `tests/test_api_routes.py`
- `memory/progress.md`
- `memory/decisions.md`
- `GRUNT_HANDOFF_PAP-247.md`

## Pedant Review Focus
1. Confirm the new status metadata is conservative and does not overclaim failure certainty.
2. Check wording consistency across Home / Player / Compare.
3. Verify no Streamlit control-flow regressions were introduced by the retry buttons and early-stop placeholders.
4. Confirm helper coverage is sufficient and page-level logic is still thin.
5. Review whether `partial` should remain warning-level or shift to info-level.

## Next Recommended Issue
Add a dedicated backend operations/status artifact for scrape + pipeline runs so dashboard sync/failure messaging can rely on explicit run history instead of artifact-mtime heuristics.
