# ARCHITECT PLAN — PAP-246

## Ticket
Create end-to-end test for scrape to dashboard data flow.

## Scope
Plan only. Do not implement code in this phase.

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Code and test inspection completed:
- `app/pipeline/run_pipeline.py`
- `app/pipeline/bronze.py`
- `app/pipeline/io.py`
- `app/agents/orchestrator.py`
- `app/agents/scraper_agent.py`
- `app/scraping/players.py`
- `app/api/routes.py`
- `dashboard/api_client.py`
- `tests/test_api_routes.py`
- `tests/test_agents_orchestrator.py`

## Current System State
The intended product path is:
1. scrape source pages
2. persist raw + parsed artifacts
3. build Bronze/Silver/Gold pipeline outputs
4. serve dashboard-facing data through backend API routes
5. consume that data via the Streamlit dashboard API client

However, the current checkout still has important limitations:
- `full_refresh` does not guarantee a real scrape by itself because the scraper agent only performs an actual fetch when a concrete `url` is supplied.
- the current checked-in dashboard-facing artifacts are empty (`[]`) even though the files exist.
- the current runtime may lack live scraping dependencies and source access reliability, especially for FBref.
- current API route tests are mocked/unit-style rather than true flow-through tests.

## Root Cause Found
There is currently **no single command or workflow** that validates the full scrape-to-dashboard path end-to-end.

More specifically:
1. the scraper/orchestrator seam is not yet self-sufficient for a live run because `full_refresh` does not carry a concrete target inventory by default.
2. dashboard-facing API tests mock route loaders instead of exercising real generated artifacts.
3. dashboard client tests mock HTTP responses instead of hitting a test backend against seeded artifacts.
4. the checked-in data artifacts are empty, so a naive end-to-end test against repo data would prove only the empty-state path, not the happy path.

## Architectural Recommendation
Keep the current architecture intact:
- scraper and parsing under `app/scraping/`
- Bronze/Silver/Gold building under `app/pipeline/` + `app/analysis/`
- dashboard reads backend endpoints, not artifacts directly
- end-to-end validation should operate by preparing controlled inputs and then verifying each seam in order

Do **not** redesign the system for this ticket.
Do **not** make the dashboard read files directly.
Do **not** require a live external scrape as the only test mode.

## Recommended Strategy
PAP-246 should produce **one primary deterministic validation workflow** and **one optional live verification mode**.

### Primary mode: fixture-driven E2E smoke validation
This should be the required regression-catching path.

Why:
- deterministic
- runnable in CI/local without fragile network access
- validates parse/storage/pipeline/API/dashboard-client flow
- avoids dependence on Playwright/browser setup and source anti-bot behavior

### Secondary mode: optional live-source verification
This should be explicitly best-effort/manual.

Why:
- useful as an operator check
- but too fragile to be the required regression gate because live scraping currently depends on source accessibility and runtime setup

---

## Recommended Deliverable Shape
Create a single script or test module that can be invoked with one command.

### Preferred deliverable
- `tests/test_e2e_dashboard_flow.py`

### Optional companion script
- `scripts/verify_dashboard_flow.py`

### Recommendation
Prefer a **test module first** because it fits existing repo conventions and is easiest to run in CI:
```bash
python3 -m unittest tests.test_e2e_dashboard_flow
```

If the team wants a more operator-friendly wrapper later, add:
```bash
python3 scripts/verify_dashboard_flow.py
```
which can call the same helpers and print a pass/fail summary.

---

## Minimal Test Scenario
Use a single-player, minimal-but-non-empty dataset that exercises the full path.

### Required seeded entities
At minimum the seeded scenario should produce:
- 1 player in Silver `players`
- 1+ rows in Silver `player_match_stats`
- 1+ rows in Gold `player_features`
- 1+ rows in Gold `kpi_engine`
- 1+ rows in Gold `player_similarity`
- 1+ rows in Gold `player_valuation`

### Suggested canonical player
Use a stable test fixture player, for example:
- `John Doe`

### Why one player is enough
The ticket asks for a minimal end-to-end validation, not full scrape breadth.
One seeded player plus one compare target row is enough to verify:
- parsed count > 0
- storage artifacts written
- API route data loads
- dashboard client receives expected payload shape

### Compare caveat
Similarity requires at least one target neighbor row in the output structure.
Even if the player pool is tiny, the fixture should still seed a valid `similar_players` list so the compare/dashboard path is exercised.

---

## Proposed Validation Stages
The end-to-end test should validate these stages in sequence and emit pass/fail at each stage.

### Stage 1: seed scrape-like parsed inputs
Prepare deterministic parsed inputs rather than depending on a live network fetch.

#### Recommended mechanism
Write fixture parsed JSON into the same directories the pipeline expects, for example under the configured parsed-data roots.

#### Why this is acceptable
It still validates the operational downstream flow:
- parsed input exists
- Bronze sees it
- Silver/Gold are rebuilt from it
- API serves the rebuilt artifacts
- dashboard client consumes the API

#### Important note
If the repo already has pure parser unit tests, PAP-246 should not duplicate deep parser correctness testing. It should assume parser correctness is separately covered and focus on **system flow**.

---

### Stage 2: run the pipeline
Call the real pipeline builder:
- `run_pipeline()` from `app/pipeline/run_pipeline.py`

#### Validate
- Bronze manifest artifact count > 0
- Silver tables contain expected record counts
- Gold/analysis outputs contain expected record counts

#### Pass/fail examples
- PASS: `players >= 1`, `player_match_stats >= 1`, `valuation >= 1`
- FAIL: any required table remains empty

---

### Stage 3: verify artifact storage
After pipeline execution, inspect the real artifact files on disk.

#### Required file checks
- `data/bronze/manifest.json`
- `data/silver/players.json`
- `data/silver/player_match_stats.json`
- `data/gold/player_features.json`
- `data/gold/kpi_engine.json`
- `data/gold/player_similarity.json`
- `data/gold/player_valuation.json`

#### Validate
- files exist
- payloads are lists/dicts as expected
- key counts match the pipeline-return summary

---

### Stage 4: verify backend/API responses
Use FastAPI `TestClient` if FastAPI is installed.

#### Recommended endpoints to verify
- `GET /health`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare?player_name=<name>`
- `GET /value?player_name=<name>`

#### Validate
- `200` status for happy-path requests
- response shapes match current frontend expectations
- counts/items are non-empty for the seeded player

#### Important addition
If PAP-245-style `/dashboard/status` exists in the active checkout by implementation time, include:
- `GET /dashboard/status`

Validate:
- top-level status is `ready` or `partial` as appropriate
- required artifacts report non-zero rows for the seeded path

#### Fallback if FastAPI unavailable
The test should either:
- skip API-layer assertions cleanly, or
- split into a separate test class behind a `skipUnless(fastapi installed)` guard

Recommendation: use a guarded API class so the core artifact/pipeline validation still runs.

---

### Stage 5: verify dashboard client receives expected payloads
Use the real `DashboardAPIClient`, but point it at a test backend instead of mocking requests.

#### Recommended approach
- instantiate FastAPI `TestClient`
- expose it through a lightweight adapter or monkeypatch `requests.get`
- then call real dashboard client methods:
  - `get_players()`
  - `get_player_stats()`
  - `get_compare()`
  - `get_value()`
  - optionally `get_dashboard_status()` if present in checkout

#### Validate
- client returns dict payloads with expected keys
- player list contains seeded player
- stats count > 0
- compare payload includes `similar_players`
- value payload includes `valuation_score`

This verifies the dashboard’s data-receipt contract without requiring actual Streamlit browser automation.

---

## Recommended Test Layout

### 1. Helper fixture builder
Add a helper that seeds minimal parsed artifacts into a temporary workspace.

Possible location:
- inline inside `tests/test_e2e_dashboard_flow.py`, or
- `tests/fixtures/dashboard_flow_fixture.py`

### 2. Temporary directory patching
Patch configuration or artifact paths so the test does not overwrite repo working data.

#### Recommendation
Use `tempfile.TemporaryDirectory()` and patch:
- parsed/raw data roots
- Silver/Gold output paths if needed
- API data-access artifact paths if route tests read directly from `data/`

This is critical so the test is hermetic.

### 3. Flow-through assertions in order
Recommended test methods:
- `test_pipeline_generates_non_empty_dashboard_artifacts_from_seeded_inputs`
- `test_api_serves_seeded_dashboard_data`
- `test_dashboard_client_receives_expected_payloads_from_test_backend`

### 4. Optional operator script
If added, it should print stage-by-stage checks like:
- `[PASS] seeded parsed inputs`
- `[PASS] pipeline generated 1 players row`
- `[PASS] /players returned non-empty payload`
- `[PASS] dashboard client received player payload`
- `[FAIL] /compare returned empty similar_players`

---

## What Should Count as “Scrape” in This Ticket
Because the current live scraper requires runtime dependencies and a concrete URL, PAP-246 should define two supported modes:

### Mode A — required: seeded parsed-input mode
This is the official regression test.

### Mode B — optional: live scrape verification mode
This may call:
- scraper entrypoint with an explicit Transfermarkt test URL
- then pipeline + API checks

But it must be documented as best-effort because it can fail for reasons unrelated to regressions:
- missing Playwright
- browser not installed
- network issues
- anti-bot/source changes

### Recommendation
Document clearly that seeded mode is the required CI-safe E2E path, while live mode is an operator diagnostic.

---

## Known Limitations To Document
PAP-246 should explicitly document these limitations:

1. **Live scrape mode is not yet reliable enough to be mandatory**
   - current runtime may not have Playwright/browser installed
   - `full_refresh` is not self-targeting by default
2. **FBref cannot currently be the required live-source path**
   - source access is challenge-prone in current environment
3. **Fixture-driven E2E validates system integration, not source accessibility**
   - parser logic and source compatibility still need their own focused tests
4. **Dashboard rendering is validated at payload-contract level, not full browser UI level**
   - this ticket should stop at dashboard client/API payload verification unless Streamlit smoke support is already available

---

## Pass/Fail Output Recommendation
The validation workflow should emit explicit stage-level pass/fail output.

### If using unittest only
Encode pass/fail via clear assertion messages.

### If using a script wrapper
Print concise lines like:
- `PASS: bronze manifest contains parsed artifacts`
- `PASS: silver players count = 1`
- `PASS: GET /players returned 1 item`
- `PASS: dashboard client received seeded player payload`
- `FAIL: player valuation payload missing valuation_score`

Recommendation: even if the main deliverable is a unittest module, include helper assertion messages that are operator-readable.

---

## Files Likely To Change In Grunt Phase
### Core test/workflow
- `tests/test_e2e_dashboard_flow.py`
- optionally `scripts/verify_dashboard_flow.py`

### Supporting test helpers
- optional fixture/helper module under `tests/fixtures/` or `tests/helpers/`

### Documentation
- `README.md` with one-command validation instructions
- `GRUNT_HANDOFF_PAP-246.md`
- `PEDANT_HANDOFF_PAP-246.md`

### Memory
- `memory/progress.md`
- `memory/decisions.md`

---

## Non-Breaking Constraints
Do not:
- make the dashboard read artifacts directly in production code
- require a live external scrape as the only passing mode
- overwrite checked-in repo data during tests
- couple the validation to one developer machine’s browser setup

Do:
- make the validation hermetic by default
- verify real artifact writes and real route/client behavior where available
- keep live-source verification optional
- preserve current architecture boundaries

---

## QA Checklist For Pedant
Pedant should verify:
- the new E2E test runs with one command
- the seeded mode is hermetic and uses temp paths
- pipeline outputs are truly non-empty in the test
- API responses are validated against real generated artifacts, not mocks
- dashboard client path is exercised against a test backend, not just mocked requests
- assertion messages are clear enough to diagnose which stage failed
- any live mode is explicitly optional/documented as best-effort

---

## Recommended Next Issue After PAP-246
PAP-247 - make `full_refresh` self-targeting with a small concrete scrape target registry so an optional live E2E verification can run without manual URL injection.

---

## Artifact For Next Role
Grunt should implement a deterministic, one-command E2E validation test centered on seeded parsed-input fixtures, real pipeline execution, artifact verification, backend route checks, and dashboard client payload checks, while documenting an optional live-scrape verification mode as best-effort rather than required.
