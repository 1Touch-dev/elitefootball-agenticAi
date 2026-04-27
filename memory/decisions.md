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

## Similarity Planning Decisions Added in PAP-215
- similarity should be computed from normalized derived player features rather than directly from raw source fields.
- the MVP similarity engine should use Euclidean distance over normalized feature vectors.
- the MVP similarity score should be a bounded `0..100` transformation derived from distance.
- nearest-neighbor search should exclude the source player and return the top-ranked matches by ascending distance.
- the first version should work with existing Gold and KPI outputs and should not require advanced metrics.
- player-name joining is acceptable for the MVP similarity engine until stable IDs are propagated through the pipeline.
- the initial similarity vector should use `goal_contribution_per_90`, `shots`, `minutes`, `discipline_risk_score`, `consistency_score`, and `base_kpi_score`.
- feature values should be min-max normalized before distance calculation, with zero used when a feature column has no variance.
- the default nearest-neighbor depth should be five players or fewer when the pool is smaller.

## Valuation Planning Decisions Added in PAP-216
- the MVP valuation output should be a synthetic `0..100` valuation score rather than a fake currency-denominated transfer estimate.
- valuation should live in a dedicated downstream analysis module under `app/analysis/` and write to `data/gold/player_valuation.json`.
- the valuation formula should be transparent and additive: performance + age + minutes + club factor + league adjustment - risk.
- KPI output should remain the primary performance input, with advanced metrics used only as optional enrichment.
- age scoring for valuation should use explicit bands rather than reusing the KPI age multiplier directly.
- club factor and league adjustment should use small bounded static lookup rules for the MVP, with conservative defaults when context is missing.
- risk should be modeled from existing discipline and consistency signals, not from unavailable injury or contract data.
- missing optional inputs should degrade gracefully to defaults and should not block valuation output generation.
- the first implemented valuation model version is `mvp_v1`.
- the implemented performance component should prioritize `base_kpi_score`, optionally enrich with `progression_score`, and fall back to Gold feature scoring when KPI data is missing.
- the implemented minutes component should scale linearly from accumulated minutes and cap at `15`.
- the implemented club factor should score IDV highest, youth/reserve contexts lowest, and use conservative defaults for unknown clubs.
- the implemented league adjustment should use simple competition-name heuristics with neutral defaults when competition context is missing.
- the implemented risk component should subtract value using discipline risk plus a consistency penalty when consistency falls below `60`.
- the valuation artifact should include transparent component breakdowns, raw inputs, a model version tag, and a derived valuation tier.
- PAP-221 should be implemented as a dedicated downstream risk-analysis artifact rather than by expanding scraper or schema scope.
- PAP-221 injury risk should be modeled as a conservative availability-risk proxy derived from existing appearance and minutes patterns, not as a true medical injury classifier.
- PAP-221 volatility risk should be derived from match-to-match variation in per-90 production and minutes, with KPI consistency reused only as a supporting signal.
- the planned PAP-221 risk artifact path is `data/gold/player_risk.json`.
- valuation should consume the PAP-221 risk artifact as optional enrichment while preserving the current fallback risk logic when the artifact is absent.
- the implemented PAP-221 risk model uses a transparent weighted blend of injury/availability proxy risk, performance volatility risk, and scaled discipline risk.
- the implemented PAP-221 volatility model uses match-level per-90 goal contribution variance, shot variance, minutes variance, and a KPI consistency penalty.
- the implemented PAP-221 valuation integration converts artifact risk into a bounded deduction through `risk_deduction(...)`, while retaining the legacy `risk_score(...)` path as a fallback when risk rows are missing.

## UI Planning Decisions Added in PAP-218
- Streamlit should be chosen over Next.js for the MVP dashboard because the repository is already Python-first and API-driven.
- the dashboard should be a separate UI layer that consumes backend endpoints rather than reading raw artifacts directly.
- the MVP dashboard should ship as a small multipage app with `player` and `compare` pages.
- the dashboard should remain internal-facing and prioritize simple Streamlit widgets over custom frontend styling.
- missing backend or analysis data should surface as explicit UI states rather than causing page crashes.
- the first dashboard implementation should use Streamlit multipage layout with `Home`, `Player`, and `Compare` pages.
- the dashboard should use a lightweight requests-based API client with `ELITEFOOTBALL_API_BASE_URL` as the backend base-url override.
- valuation enrichment on the compare page is acceptable as a UI join over API responses and should not introduce new analysis logic.

## Multi-Agent Planning Decisions Added in PAP-222
- PAP-222 should be implemented as a lightweight in-process orchestration layer, not a distributed agent runtime.
- the orchestrator should own a central task-kind route map instead of hiding routing logic inside individual agent modules.
- `app/agents/` should coordinate existing scraping, pipeline, and analysis modules rather than duplicating their logic.
- the initial PAP-222 agent roster should be Scraper Agent, Data Cleaner Agent, Analyst Agent, and Report Generator Agent.
- agent task/result contracts should be explicit and structured so composite workflows remain testable.
- a memory-backed agent role manifest should be added to document responsibilities and boundaries.
- `/summary` compatibility should be preserved while enriching the agent model.
- the implemented PAP-222 agent task kinds are `scrape_players`, `clean_data`, `run_analysis`, `generate_report`, and `full_refresh`.
- the implemented PAP-222 orchestrator should pass cleaner outputs into analyst/reporter steps through explicit in-memory task metadata rather than introducing new persistence.
- the implemented Scraper Agent should default to a safe plan-only response unless a concrete scrape URL is supplied.

## Async Queue Planning Decisions Added in PAP-223
- Redis + Celery should be used for async task execution because the ticket explicitly requires them.
- the queue layer should wrap orchestrator execution instead of duplicating route or business logic.
- one generic orchestrator-backed Celery task is preferable to many task-specific workers for the MVP.
- one-off scheduling via Celery `countdown` or `eta` is in scope; recurring schedules should be deferred.
- FastAPI should expose enqueue/status endpoints and use Celery result state as the MVP job-status source.
- unit/API tests for PAP-223 should mock Celery/Redis interactions and should not require live infrastructure.
- the implementation should degrade gracefully when Celery is not installed by surfacing queue unavailability instead of crashing imports.
- task submission validation should reject simultaneous `schedule_at` and `countdown_seconds` inputs with a 400-style validation path.
- confirmed that API routes provide stable and JSON-safe task submission/export, while the orchestrator handles routing logically and consistently.

## Safety + Policy Planning Decisions Added in PAP-224
- PAP-224 should be implemented as a dedicated `app/safety/` package rather than ad hoc checks inside routes or agents.
- safety evaluation should normalize candidate actions and return explicit `allow`, `require_approval`, or `deny` decisions.
- repo-deletion intent and clearly destructive shell patterns should be hard-denied and should not be approval-escapable in the MVP.
- ambiguous but potentially legitimate mutating commands should use an approval-required path.
- the MVP approval flow should use a lightweight in-memory approval store behind a service boundary so persistence can be added later without changing callers.
- approvals should be bound to a normalized action fingerprint and should be single-use or short-lived.
- if HTTP exposure is needed now, approval endpoints should live in a dedicated router rather than being mixed into existing artifact routes.
- planning should target the actual checkout state: current repo has orchestrator-based agents and read-only API routes, but does not currently contain the PAP-223 task files mentioned in memory.
- the implemented PAP-224 approval API returns 403 for denied actions and 200 with an approval record for approval-required actions.
- the implemented safety preflight currently allows existing orchestrator task kinds but creates a stable seam for future risky task types.
- timezone-aware UTC timestamps should be used for approval lifecycle fields to avoid naive datetime drift.

## Scraping Audit Decisions Added in PAP-239
- the primary scraping failure is structural non-execution: `full_refresh` currently reaches the scraper agent without a concrete target inventory and therefore performs no real fetch unless a URL is manually supplied.
- scrape runtime readiness must be treated as an explicit precondition; the current Playwright dependency/browser requirement should fail fast with clear diagnostics before a scrape workflow is considered healthy.
- Transfermarkt-only orchestration is insufficient for the current downstream product path because dashboard/API analysis depends on FBref-derived match-stat artifacts.
- source-target registries should be maintained explicitly inside the scraping/orchestration boundary rather than relying on ad hoc one-off URL payloads.
- scraper fetch and parser stages should emit diagnostic signals for timeout, challenge/login walls, selector readiness, and partial-field extraction so empty artifacts do not appear as silent success.
- database ingestion remains a later follow-up and should not be prioritized ahead of making the scrape-to-artifact path reliably non-empty.

## Structured Logging Planning Decisions Added in PAP-240
- PAP-240 should introduce a small shared logging helper under `app/services/` rather than scattering logger setup across scraper modules.
- the MVP should use Python standard-library logging with structured key/value terminal-friendly messages instead of adding third-party logging dependencies.
- debug logging must be environment-gated and should increase diagnostic detail without changing scraper behavior or dumping full HTML bodies.
- file logging should be optional and explicitly configured; terminal logging remains the default behavior.
- fetch, parse, storage, and Silver build stages should emit stable event names and record counts so empty-results and partial-results are visible as first-class outcomes.
- exception logging should always include stack traces (`exc_info`) at the top-level fetch/scrape/store boundaries.
- PAP-240 should not fabricate database-write behavior; it should instrument current file-based persistence and leave a documented DB logging seam for future ingestion work.

## Structured Logging Decisions Added in PAP-240 Implementation
- the implemented structured logging layer now lives in `app/services/logging_service.py` and is shared by scraper, parser, storage, pipeline, and DB-base modules.
- the MVP log format is terminal-readable key/value text with stable event names rather than raw JSON logging.
- logging defaults remain terminal-only at `INFO`, while debug detail and file logging are enabled only through environment flags.
- empty or partial scrape outcomes should be logged as warning-level first-class events (`scrape.empty_result`, `parse.partial_result`, `silver.empty_output`) instead of being inferred only from empty artifacts.
- fetch and scrape boundary failures should log stack traces through shared exception helpers so dependency/runtime problems are immediately visible.
- current `db.write.*` events document active persistence attempts/results at the file-artifact seam and should not be interpreted as completed relational DB ingestion.

## Source Compatibility Decisions Added in PAP-241
- the source stack should be treated as source-specific rather than fetch-method-uniform: Transfermarkt and FBref do not currently have the same accessibility profile.
- the tested Transfermarkt squad page currently returns usable HTML to static HTTP requests, so requests-first is a valid preferred strategy for that page class.
- the tested FBref squad/stats page currently returns a Cloudflare challenge response (`403`, `cf-mitigated: challenge`) to static HTTP requests, so requests-only is not a valid strategy for FBref in the current environment.
- for FBref, the next technical validation step should use the existing Playwright-based browser stack rather than introducing Puppeteer or another parallel browser technology.
- FBref failures should be classified first as source-access/challenge failures until a browser-based compatibility probe proves that real content can be reached.

## Compatibility Probe Decisions Added in PAP-241 Implementation
- the repo now carries a reusable static compatibility probe under `app/scraping/compatibility.py` so source accessibility can be classified explicitly instead of inferred from downstream parse failures.
- compatibility checks should capture status code, challenge markers, cookies, title, source-marker hits, and a final classification for each tested source URL.
- `challenge_page` is currently the canonical classification for Cloudflare-style blocked responses that return interstitial HTML rather than source content.
- the current live compatibility evidence supports keeping Transfermarkt on a requests-first path for the tested page class while treating FBref as browser-validation-required.

## Adjustments Made During PAP-241
- `javascript_likely_required` was replaced with `anti_bot_mitigation_required` to improve clarity around access challenges
- the probe explicitly detects and classifies Cloudflare challenges as `challenge_page`
- each statically-probed source URL captures a final status classification plus indicator remarks for deeper diagnostics

## Critical Rule
All future tasks MUST:
- read memory before work
- update memory after work
