# Progress

## Current Status
Initial repository bootstrap completed at the scaffold level.

## Completed
- created Python application package structure
- created API, agent, scraping, database, and service module placeholders
- created required memory files
- added starter dependency list and `.gitignore`
- completed architecture planning for MVP player + match database schema
- defined the target domain tables as clubs, players, matches, and stats
- identified SQL schema and ORM models as the required implementation outputs
- implemented normalized SQLAlchemy ORM models for clubs, players, matches, and stats
- added SQL schema output at `app/db/schema.sql`
- replaced the placeholder player-only model with the MVP football schema
- completed architecture planning for a Playwright-based Transfermarkt scraper
- defined raw HTML and parsed data storage as required outputs for scraping work
- added Playwright-backed scraping modules for browser access, parsing, storage, and Transfermarkt orchestration
- implemented raw HTML and parsed JSON persistence for Transfermarkt scraping outputs
- completed architecture planning for an FBref scraper covering match stats and player stat extraction
- added source-specific FBref scraping, parsing, and DB-mapping helpers for match and player stat extraction
- implemented FBref raw HTML and parsed JSON persistence with match, player match stats, and per-90 payload sections
- completed architecture planning for a core KPI engine covering per-90, rolling averages, and age-adjusted scoring
- completed a follow-up implementation plan for a dedicated KPI analysis package and pipeline-integrated KPI output
- added a dedicated KPI analysis package with formula helpers and pipeline-integrated KPI output generation
- completed architecture planning for a player similarity and comparison engine
- implemented a player similarity engine with nearest-neighbor output generation
- completed architecture planning for a simplified player valuation model
- implemented a simplified player valuation engine with pipeline-integrated Gold output generation
- completed architecture planning for an MVP Streamlit dashboard covering player and comparison views
- implemented an MVP Streamlit dashboard with player and comparison pages
- completed architecture planning for PAP-221 risk modeling covering injury-risk proxy and performance volatility as a dedicated downstream analysis artifact
- added architect handoff artifacts for PAP-221 at `ARCHITECT_PLAN_PAP-221.md`, `GRUNT_HANDOFF_PAP-221.md`, and `PEDANT_HANDOFF_PAP-221.md`
- implemented PAP-221 risk modeling with new `app/analysis/risk.py` and `app/analysis/risk_engine.py`
- integrated the PAP-221 risk artifact into `app/pipeline/run_pipeline.py` and valuation consumption in `app/analysis/valuation_engine.py`
- added PAP-221 test coverage in `tests/test_risk.py` and `tests/test_risk_engine.py`, plus valuation regression updates
- completed architecture planning for PAP-223 async task queue + orchestrator execution using Redis + Celery
- added architect handoff artifacts for PAP-223 at `ARCHITECT_PLAN_PAP-223.md`, `GRUNT_HANDOFF_PAP-223.md`, and `PEDANT_HANDOFF_PAP-223.md`
- implemented PAP-223 queue infrastructure in `app/tasks/` with Celery wiring, async submission/status service helpers, and queue-safe task schemas
- expanded `app/agents/orchestrator.py` with supported task kinds, route mapping, synchronous execution helpers, and serializable `run_task_dict(...)`
- added async task API coverage in `tests/test_task_routes.py` and orchestrator coverage in `tests/test_orchestrator.py`
- verified Redis + Celery initialization, task submission, and status querying in a test environment without live infrastructure
- confirmed submission/task status endpoints provide stable JSON-safe API paths
- enabled mock-based queue viabilities by reinforcing Celery/Redis interactions inside tests
- completed architecture planning for PAP-224 safety + policy layer in `ARCHITECT_PLAN_PAP-224.md`
- documented that PAP-224 should add a dedicated safety layer with hard-deny rules for repo deletion, approval-gated risky commands, and a lightweight approval flow
- noted a repo-state mismatch during planning: memory references PAP-223 queue files that are not present in the current checkout, so PAP-224 should be implemented against the actual tree
- implemented PAP-224 safety controls in `app/safety/` with policy evaluation, approval store/service, and request/response schemas
- added approval endpoints in `app/api/safety_routes.py` and wired them into `app/main.py`
- integrated a safety preflight into `app/agents/orchestrator.py` and surfaced safety capability metadata in `/summary`
- documented PAP-224 behavior in `README.md` and `memory/safety_policy.md`
- added PAP-224 coverage in `tests/test_safety_policies.py`, `tests/test_safety_service.py`, and `tests/test_safety_routes.py`
- stabilized partial PAP-223 queue files already present in the checkout so the repo remains internally consistent during PAP-224 work

## Next Steps
- validate player similarity rankings against real player data and tune feature weighting if needed
- validate KPI output against real Silver data and tune weights if needed
- validate FBref and Transfermarkt selectors against live pages and refine parser accuracy
- connect FBref and Transfermarkt parsed outputs to database ingestion workflows
- seed tracked club records for IDV + five clubs
- add tests for parsing behavior, storage outputs, KPI calculations, mapping helpers, similarity logic, and backend entrypoints
- validate valuation output against real player data and tune weights if needed
- refine static club/league lookup assumptions against real player data
- expand valuation coverage if richer competition or club-strength context becomes available
- validate the dashboard against a live backend with real player and comparison data
- refine the player and comparison layouts once real data is available
- add non-UI smoke coverage in an environment where Streamlit is installed and runnable
- pedant-review PAP-221 weighting and fallback behavior, especially risk-to-valuation scaling
- validate PAP-221 risk outputs against richer real player data once non-empty Silver artifacts are available
- refine the coordinator workflow between agents
- implement PAP-224 by adding `app/safety/` decision types, policy rules, approval service/store, and focused tests
- decide during implementation whether the MVP approval flow should be exposed immediately via dedicated FastAPI routes or only wired internally for future mutation endpoints
- reconcile the stale PAP-223 memory notes with the actual repository contents before building PAP-224 integrations that assume task/queue files exist
- pedant-review PAP-224 command classification boundaries, especially the deny vs approval-required split for shell commands
- validate PAP-224 approval endpoint semantics in an environment with FastAPI installed and confirm 200/403 behavior matches product expectations
- decide whether future risky execution endpoints should consume approvals directly or only use the safety layer as a preflight gate

## Working Rules
All future tasks MUST:
- read memory before work
- update memory after work
