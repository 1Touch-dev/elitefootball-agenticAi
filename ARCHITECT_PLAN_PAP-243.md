# ARCHITECT_PLAN_PAP-243 — Audit and Fix Persistence Layer for Scraped Data

## Ticket
PAP-243

## Role
Architect — planning/design only. No code changes to runtime persistence logic in this phase.

## Goal
Investigate whether scraped data is failing to persist after extraction, identify the real storage boundary in the current project, and produce a concrete plan to make persistence verifiable, queryable, and non-silent.

This phase must answer:
- where scraped data is actually being saved today
- whether DB persistence is active or only scaffolded
- where schema/payload mismatches would break inserts
- what verification signals are missing after writes
- how to add durable write checks without breaking current architecture

---

## 1) Current Persistence Architecture Reviewed

## 1.1 Active persistence today is file-based, not relational DB
The currently active scrape/pipeline path persists data to files:
- raw scrape HTML via `app/scraping/storage.py`
- parsed scrape payloads via `app/scraping/storage.py`
- Silver/Gold artifacts via `app/pipeline/io.py`

The dashboard/API currently reads from generated artifact files:
- `app/api/data_access.py` loads `data/silver/*.json` and `data/gold/*.json`
- no current API read path queries SQLAlchemy models or a live DB session

## 1.2 DB setup exists but is not wired into the operational data path
`app/db/base.py`
- initializes SQLAlchemy `engine`
- configures `SessionLocal`
- emits `db.engine.initialized` and `db.session.configured`

`app/db/models.py`
- defines `Club`, `Player`, `Match`, `Stat`

But the current operational path does **not**:
- open sessions inside the scrape/pipeline flow
- insert `Club`, `Player`, `Match`, or `Stat` rows
- verify committed row counts
- query back persisted DB rows for confirmation

## 1.3 Current “DB write” behavior is preview-only, not actual ingestion
`app/scraping/fbref.py`
- builds a `db_mapping` preview using `map_fbref_match_to_db(...)` and `map_fbref_stat_to_db(...)`
- logs `db.write.result` with `persisted=False`
- saves this only inside parsed JSON payloads

That means the current repo has a **DB-shaped mapping seam**, but not a true persistence layer.

## 1.4 Silver is the real durable store used by product flows
`app/pipeline/silver.py`
- reads parsed payload JSONs
- normalizes them into `players`, `transfers`, `matches`, `player_match_stats`, `player_per90`
- writes those tables back to JSON under `data/silver/`

This is the data actually consumed downstream.

---

## 2) Root Cause Found

## Root cause A — there is no active DB ingestion path yet
The repo contains ORM models and session setup, but scraped data is not failing to persist to the DB because it is **not currently being inserted into the DB at all**.

The real situation is:
- **file persistence is active**
- **relational DB persistence is scaffolded only**

## Root cause B — persistence success is currently inferred, not verified
For file-based persistence:
- writes are logged
- exceptions are surfaced
- but record-count verification and read-after-write confirmation are limited

For DB-shaped preview mappings:
- no actual insert/update occurs
- `persisted=False` is logged, but there is no unified persistence audit summary to prevent confusion

## Root cause C — schema compatibility is only partially aligned
Current Silver and scrape payload schemas are reasonably aligned with artifact persistence.

But DB schema compatibility is incomplete:
- `Match.match_date` is non-nullable and typed as `DateTime(timezone=True)` while scraped payload often carries string dates or missing values
- `Match.home_club_id` and `away_club_id` are required foreign keys, while scraper mapping only has club names
- `Player.club_id` is required, but scraper outputs only club names
- `Stat.player_id`, `club_id`, `match_id` are required, but current mapping preview contains player/club names and optional `match_id`

So even if direct DB inserts were added naively right now, they would fail without entity-resolution/upsert logic.

## Root cause D — query verification is missing at the real persistence boundary
The system does not currently perform explicit read-after-write verification for:
- parsed scraper JSON payloads
- Silver table artifact counts
- future DB row ingestion

This makes storage issues harder to distinguish from empty scrape outputs.

---

## 3) What is and is not broken right now

## Not broken
- raw HTML file persistence is active
- parsed scrape JSON persistence is active
- Silver/Gold artifact persistence is active
- API/dashboard artifact loading is active

## Broken or missing
- true relational DB ingestion path is missing
- DB preview logs can be mistaken for successful DB persistence if not read carefully
- no unified persistence verification summary after scrape/pipeline runs
- no explicit query-verification layer for stored data
- no row-count reconciliation between parsed payloads, Silver outputs, and future DB tables

---

## 4) Persistence Audit Report

## 4.1 DB connection setup
### Current state
- SQLAlchemy engine/session are configured in `app/db/base.py`
- no connectivity check or test query is performed at runtime startup
- no session lifecycle helper/service exists for ingestion workflows

### Risk
- DB can appear “configured” without proving it is reachable or writable

### Recommendation
Add a dedicated DB persistence service with:
- session lifecycle management
- optional connectivity check (`SELECT 1` or equivalent)
- structured logs for begin/commit/rollback/query verification

---

## 4.2 Insert/update logic
### Current state
- no production insert/update logic exists for clubs, players, matches, or stats
- only mapping preview exists in `app/scraping/fbref_mapping.py`

### Risk
- scraped payloads can look DB-ready while never being persisted

### Recommendation
Introduce true persistence under a dedicated module, e.g.:
- `app/db/persistence.py`

Responsibilities:
- upsert clubs by canonical name / short code when available
- upsert players by `(full_name, club_id, source)` or another MVP-safe uniqueness key
- upsert matches by `external_id` when present, otherwise deterministic fallback key
- upsert stats by the existing DB unique key `(match_id, player_id)`

---

## 4.3 Schema compatibility with scraped payloads
### Current state
The current scraper outputs do not directly satisfy DB foreign-key requirements.

### Required translation layer
Need explicit entity resolution from artifact rows into DB rows:
- `club_name` -> `Club.id`
- `player_name` + club context -> `Player.id`
- `match` payload -> `Match.id`
- stat row -> `Stat(match_id, player_id, club_id, ...)`

### Recommendation
Keep current scraper/Silver outputs intact, and add a dedicated ingestion step that transforms artifact rows into DB-ready records.

Do **not** push DB coupling into parsers.

---

## 4.4 Failed writes and validation errors
### Current state
- file writes already raise exceptions and log them
- no DB validation/write failure path exists yet because no DB writes occur
- no persistence audit artifact summarizes counts and failures

### Recommendation
For the next role, persistence writes should emit:
- attempted row count
- inserted row count
- updated row count
- skipped row count
- failed row count
- validation errors by entity type
- verification query counts after commit

Persist these in a machine-readable audit artifact, e.g.:
- `data/bronze/persistence_report.json`
or
- `data/gold/persistence_report.json`

---

## 4.5 Prevent silent insert failures
### Current state
Silent DB insert failure is currently avoided only because DB inserts are absent.

### Recommendation
When DB ingestion is added:
- wrap each entity batch in explicit transaction handling
- log rollback causes with stack traces
- return structured persistence status, not just logs
- fail the ingestion step loudly when required entities cannot be resolved
- distinguish `validation_failed` from `write_failed` from `verification_failed`

---

## 4.6 Record count verification after writes
### Current state
- `storage.py` logs bytes and paths for scraper artifacts
- `silver.py` logs record counts written to Silver JSON
- no read-after-write verification is done on those paths
- no DB count verification exists

### Recommendation
Add verification at both levels:

#### File persistence verification
After JSON write:
- read file back
- confirm payload type
- confirm row count matches expected count

#### DB persistence verification
After commit:
- query counts for affected tables/entities
- optionally query the specific inserted keys
- include verification results in the persistence report

---

## 4.7 Query verification of stored data
### Current state
- API query layer currently reads only Silver/Gold artifacts
- no DB query verification exists

### Recommendation
For PAP-243, add focused verification helpers that can confirm:
- clubs query returns expected number of rows
- players query returns expected rows for scraped profiles
- matches/stats query returns expected counts after FBref ingestion

This can remain internal/test-only first.

---

## 5) Recommended Technical Direction

## 5.1 Preserve current architecture: artifact-first, DB ingestion as downstream step
Do **not** rewrite the scraper to write directly into ORM models.

Recommended flow:
1. scrape -> raw/parsed artifacts
2. parsed artifacts -> Silver tables
3. Silver tables -> DB ingestion step
4. verification queries + persistence report

Why:
- aligns with current Bronze/Silver/Gold architecture
- keeps parsers independent of relational concerns
- allows DB ingestion to be replayed from existing artifacts

## 5.2 Treat Silver as the canonical ingestion source
Use `data/silver/*.json` (or in-memory Silver tables returned by `build_silver_tables()`) as the source for DB ingestion.

Why:
- cleaner, normalized, table-shaped inputs
- fewer source-specific parser quirks at DB boundary
- stable contract for future ingestion/replay

---

## 6) Detailed Implementation Plan for the Next Role

## Step 1 — Add a real DB persistence module
### New file
- `app/db/persistence.py`

### Responsibilities
- open/close sessions safely
- upsert clubs
- upsert players
- upsert matches
- upsert stats
- collect structured counts and errors

### Suggested functions
- `ingest_silver_tables(silver_tables: dict[str, list[dict[str, object]]]) -> dict[str, object]`
- `_upsert_clubs(...)`
- `_upsert_players(...)`
- `_upsert_matches(...)`
- `_upsert_stats(...)`
- `verify_persistence(...)`

---

## Step 2 — Add DB readiness and schema bootstrap helper
### Files
- `app/db/base.py`
- optionally new `app/db/bootstrap.py`

### Plan
- add explicit engine/session health check helper
- ensure metadata create/check path exists for local/dev bootstrap
- keep this separate from scrape logic

### Verification
- perform a simple connectivity query
- log result clearly

---

## Step 3 — Implement club/player/match/stat resolution rules
### Club resolution
- create/find by normalized club name
- optionally derive short code conservatively when absent

### Player resolution
- for MVP, resolve by normalized `(full_name, club_id)`
- use `preferred_name`, `position`, `nationality`, DOB when available for enrichment/update

### Match resolution
- prefer `external_id`
- fallback to deterministic composite key from `(match_date, home_club_id, away_club_id, competition)` if external_id missing

### Stat resolution
- use DB uniqueness `(match_id, player_id)`
- upsert mutable numeric fields

---

## Step 4 — Add structured persistence reporting
### Artifact
- `data/bronze/persistence_report.json` or similar

### Include
- source file/table counts
- attempted inserts
- inserts vs updates vs skips vs failures
- validation errors grouped by entity type
- verification query counts
- final status

---

## Step 5 — Wire persistence into the pipeline, not the scraper
### Files
- `app/pipeline/run_pipeline.py`
- maybe `app/agents/orchestrator.py` if persistence needs orchestration visibility

### Plan
- after Silver build, call DB ingestion step
- return persistence results as part of pipeline result object
- do not make downstream Gold depend on DB success yet unless explicitly requested

This keeps rollout safe.

---

## Step 6 — Add focused verification queries
### Possible new file
- `app/db/query_verification.py`

### Checks
- count clubs
- count players
- count matches
- count stats
- fetch sample rows for the most recent ingest

Return these in the persistence report.

---

## Step 7 — Add tests
### New tests
- `tests/test_db_persistence.py`
- `tests/test_persistence_reporting.py`
- maybe `tests/test_pipeline_persistence.py`

### Cover
- session/engine health check
- club/player/match/stat upserts
- duplicate re-ingest behavior
- failure on unresolved required foreign-key context
- verification query counts
- persistence report structure

Use SQLite test DB.

---

## 7) Proposed Persistence Status Model

Each run should classify persistence like:
- `success_complete`
- `success_partial`
- `validation_failed`
- `write_failed`
- `verification_failed`

And include per-entity counts:
```json
{
  "clubs": {"attempted": 3, "inserted": 2, "updated": 1, "failed": 0},
  "players": {"attempted": 8, "inserted": 8, "updated": 0, "failed": 0},
  "matches": {"attempted": 1, "inserted": 1, "updated": 0, "failed": 0},
  "stats": {"attempted": 14, "inserted": 14, "updated": 0, "failed": 0}
}
```

---

## 8) Verification Query Results Expected Next Phase

PAP-243 should end with explicit verification outputs like:
- DB connectivity: OK
- clubs count: N
- players count: N
- matches count: N
- stats count: N
- sample player rows queried successfully
- sample match/stat rows queried successfully

And, separately for artifact persistence:
- parsed payload file counts verified
- Silver table row counts verified after write

---

## 9) Success Criteria Interpretation

PAP-243 should be considered complete when:
- scraped data is demonstrably stored at the intended persistence boundary
- record counts are confirmed after pipeline execution
- failures are explicit, logged, and summarized
- query verification proves stored data is readable

### Current best truth before implementation
- artifacts are currently being stored successfully
- DB persistence is not yet active
- therefore PAP-243 is primarily about implementing and verifying the missing DB ingestion layer while strengthening write verification/reporting across the active file-based path

---

## 10) Files Expected to Change in Next Role

### New
- `app/db/persistence.py`
- possibly `app/db/bootstrap.py`
- possibly `app/db/query_verification.py`
- `tests/test_db_persistence.py`
- `tests/test_persistence_reporting.py`

### Updated
- `app/db/base.py`
- `app/pipeline/run_pipeline.py`
- possibly `app/pipeline/silver.py`
- possibly `README.md`
- `memory/progress.md`
- `memory/decisions.md`

---

## 11) Next Recommended Issue

**Recommended next issue:**
`PAP-244 - Implement Silver-to-DB Ingestion and Persistence Verification`

Suggested scope:
- add real DB ingestion from Silver tables
- emit persistence report with counts/errors
- verify DB rows after commit
- keep API/dashboard artifact-based until DB-backed reads are explicitly requested

---

## 12) Files Changed In This Phase

Planning + memory only:
- `ARCHITECT_PLAN_PAP-243.md`
- `memory/progress.md`
- `memory/decisions.md`
