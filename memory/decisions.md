# Decisions

## Initial Decisions
1. Python is the backend foundation for the project.
2. Scraping is isolated into its own module for maintainability.
3. A database layer is created early so scraped player data has a clear persistence path.
4. The system is designed as a multi-agent workflow rather than a single monolith.
5. The MVP scope is limited to IDV players to keep delivery focused.
6. Memory is treated as mandatory operating infrastructure, not optional documentation.

## Critical Rule
All future tasks MUST:
- read memory before work
- update memory after work
