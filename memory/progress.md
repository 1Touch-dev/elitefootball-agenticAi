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

## Working Rules
All future tasks MUST:
- read memory before work
- update memory after work
