# Decisions

## Initial Decisions
1. Python is the backend foundation for the project.
2. Scraping is isolated into its own module for maintainability.
3. A database layer is created early so scraped player data has a clear persistence path.
4. The system is designed as a multi-agent workflow rather than a single monolith.
5. The MVP scope is limited to IDV players to keep delivery focused.
6. Memory is treated as mandatory operating infrastructure, not optional documentation.
7. The MVP schema should normalize clubs, players, matches, and stats into separate tables.
8. The stats table should represent one aggregated player stat line per match for the MVP.
9. The schema focus remains limited to IDV plus five clubs to avoid premature expansion.

## Normalization Approach
- `clubs` stores reference club data.
- `players` stores canonical player records and links each player to a club.
- `matches` stores match metadata with home and away club references.
- `stats` stores per-player, per-match performance rows.
- the MVP uses a unique (`match_id`, `player_id`) stat line to prevent duplicate match records for the same player.

## Schema Decisions Added in PAP-208
- The old placeholder `PlayerProfile` model is replaced by canonical `Player`, `Club`, `Match`, and `Stat` entities.
- `matches` references clubs twice to model home and away roles without duplicating club data.
- SQL schema output is stored alongside ORM definitions in `app/db/schema.sql` for inspection and future migration work.

## Scraping Decisions Added in PAP-209
- Playwright is the required scraping technology for Transfermarkt interactions.
- Raw HTML and parsed structured data should both be stored for traceability and parser iteration.
- Scraping should remain conservative and serialized by default to reduce rate-limit risk.

## Parsing Structure
- player profile parsing should output a structured profile object.
- transfer history parsing should output a structured list of transfer rows.
- the combined parsed result should separate `profile` and `transfers` payloads.

## Rate Limit Guidance
- use session reuse where possible.
- add a delay between page fetches.
- avoid burst parallelism for the MVP.
- preserve raw HTML even when parsing is only partially successful.

## Scraper Build Decisions Added in PAP-209
- raw HTML is saved under a dedicated Transfermarkt raw-data path.
- parsed payloads are saved separately as JSON for later ingestion.
- the scraper keeps profile parsing and transfer-history parsing as separate concerns.
- Playwright browser startup is isolated from parsing and storage modules to preserve architecture boundaries.

## Stat Mapping Decisions Added in PAP-210
- FBref match-level data should map only into fields already supported by `matches` and `stats`.
- FBref per-90 metrics should be preserved in parsed outputs and not forced into the current match-granular `stats` table.
- Parsed FBref outputs should separate match metadata, player match stat rows, and per-90 stat rows.
- DB-bound rows derived from FBref should carry source provenance as `fbref`.
- Comment-wrapped FBref tables should be normalized before parsing so stat extraction is resilient to source markup quirks.

## Pipeline Design Decisions Added in PAP-211
- Bronze should represent source-preserving raw/parsed scraper artifacts and manifests.
- Silver should hold cleaned table-shaped records derived from parsed source outputs.
- Gold should hold only derived features computed from Silver outputs.
- Transformation logic should live in a dedicated pipeline module rather than inside scraper files.

## KPI Formula Decisions Added in PAP-212/PAP-213
- per-90 metrics should be computed from match totals and minutes played, scaled to 90.
- rolling averages should use recent-match windows and degrade gracefully when fewer matches exist.
- consistency should use a bounded score derived from the variation of recent per-90 outputs.
- age adjustment should apply a small transparent multiplier based on age bands rather than a large opaque bonus.
- the MVP consistency score should clamp to `0..100`.
- the MVP age multipliers should be `1.10` (<21), `1.05` (21-24), `1.00` (25-29), and `0.95` (30+), with `1.00` used when age is unknown.
- the initial composite KPI should weight goal contributions per 90 most heavily, with supporting weight from shots per 90, passes completed per 90, and normalized consistency.

## Critical Rule
All future tasks MUST:
- read memory before work
- update memory after work
