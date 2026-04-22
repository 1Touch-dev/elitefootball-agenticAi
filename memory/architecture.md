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

## Working Rules
All future tasks MUST:
- read memory before work
- update memory after work
