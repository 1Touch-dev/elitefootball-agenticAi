# PEDANT HANDOFF — PAP-246

## Review Focus
Please verify the seeded E2E workflow is hermetic, stage-complete, and clear when stages are skipped due to missing environment dependencies.

## Root Cause Confirmed
The repo lacked any single regression path that exercised seeded scrape-like input -> pipeline -> artifact storage -> backend API -> dashboard client. Existing tests stopped at mocked seams.

## What Changed
### New helper
- `tests/e2e_dashboard_flow_support.py`
  - temporary workspace setup via patched settings
  - seeded Transfermarkt + FBref parsed payloads and raw HTML samples
  - real `run_pipeline()` execution
  - artifact verification
  - optional FastAPI/TestClient API + dashboard-client verification
  - stage-by-stage PASS/FAIL report rendering

### New test
- `tests/test_e2e_dashboard_flow.py`

### New script
- `scripts/verify_dashboard_flow.py`

### Docs
- `README.md` updated with one-command workflows and limitations

## Verification Already Run
- `python3 -m unittest tests.test_e2e_dashboard_flow` ✅
- `python3 scripts/verify_dashboard_flow.py` ✅
- `python3 -m py_compile tests/e2e_dashboard_flow_support.py tests/test_e2e_dashboard_flow.py scripts/verify_dashboard_flow.py` ✅

## Things To Check Closely
1. **Hermeticity**
   - test must not mutate checked-in `data/` artifacts
   - temp-path settings restoration must be reliable
2. **Similarity happy path**
   - seeded data should always produce non-empty similarity neighbors
3. **API patching behavior**
   - when FastAPI is available, patched `ARTIFACT_PATHS` must point routes at temp artifacts instead of repo data
4. **Dashboard client bridging**
   - request monkeypatch should accurately route dashboard client calls through TestClient
5. **Skip semantics**
   - missing FastAPI should skip API/client stages cleanly without marking the whole validation as failed
6. **Assertion/report clarity**
   - failure output should identify the stage that broke

## Next Recommended Issue
PAP-247 - make `full_refresh` self-targeting so a live optional end-to-end verification can run without manual URL injection.
