# elitefootball-agenticAi

Welcome to our System

## Project Bootstrap
This repository now includes a minimal Python backend scaffold, scraping module, database layer, and a mandatory memory system for future multi-agent work focused on IDV players.

## Memory Workflow
All future tasks MUST:
- read memory before work
- update memory after work

## API Endpoints (MVP)
The backend now exposes read-only artifact-backed endpoints:
- `GET /health`
- `GET /summary`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare?player_name=...`
- `GET /value`
- `GET /value?player_name=...`

## API Notes
- These endpoints read generated artifacts from `data/silver/` and `data/gold/`.
- They do not write data or query the live database in the MVP.
- Run the pipeline first so required artifacts exist before calling compare/value routes.
