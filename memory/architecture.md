# Architecture

## System Design
The system uses a multi-agent design with clear boundaries:
- Coordinator Agent: routes tasks and keeps workflows organized
- Scraper Agent: gathers and normalizes IDV player data
- Memory Agent: reads memory before work and updates memory after work
- Analysis Agent: interprets collected data for future reporting and insight workflows

## Base Architecture
- Python backend in `app/`
- API surface in `app/api/`
- agent coordination in `app/agents/`
- scraping module in `app/scraping/`
- database layer in `app/db/`
- memory helpers in `app/services/`
- mandatory project memory in `memory/`

## Database Direction
The MVP database design should preserve the current architecture and introduce normalized football domain models for:
- clubs
- players
- matches
- stats

The ORM layer stays inside `app/db/`, and SQL output aligns with the same model boundaries through `app/db/schema.sql`.

## Scraping Pipeline Direction
Transfermarkt scraping should stay inside `app/scraping/` and be split by responsibility:
- browser/session handling
- source-specific scraping orchestration
- parsing helpers
- raw HTML storage
- parsed payload storage

This keeps scraping concerns separate from API routes and DB models while supporting later ingestion.

The current scraping flow is expected to persist:
- raw HTML under a raw Transfermarkt data path
- parsed profile + transfer payloads under a parsed Transfermarkt data path

FBref scraping should follow the same source-specific pattern, with parsing kept separate from DB mapping so that match-safe fields can map into the existing schema while per-90 outputs remain available for future schema expansion.

The FBref pipeline now mirrors the Transfermarkt split:
- page fetch
- raw HTML persistence
- source-specific parsing
- DB-safe mapping helpers
- parsed JSON persistence

A downstream pipeline and analysis layer should handle:
- Bronze/Silver/Gold transformations
- KPI computation from Silver tables
- dedicated Gold-layer KPI output generation

The KPI implementation now belongs under `app/analysis/`, while the main pipeline runner remains responsible for invoking it and writing the final Gold-layer KPI artifact.

## Working Rules
All future tasks MUST:
- read memory before work
- update memory after work
