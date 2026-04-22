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

## Next Steps
- validate KPI output against real Silver data and tune weights if needed
- validate FBref and Transfermarkt selectors against live pages and refine parser accuracy
- connect FBref and Transfermarkt parsed outputs to database ingestion workflows
- seed tracked club records for IDV + five clubs
- add tests for parsing behavior, storage outputs, KPI calculations, mapping helpers, and backend entrypoints
- refine the coordinator workflow between agents

## Working Rules
All future tasks MUST:
- read memory before work
- update memory after work
