# ARCHITECT PLAN — PAP-217

## Ticket
Expose APIs for players, stats, comparison, and valuation.

## Requested endpoints
- `/players`
- `/compare`
- `/value`

## Memory to Capture
- API design

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Code inspection completed:
- `app/api/routes.py`
- `app/main.py`
- `app/db/models.py`
- `app/services/memory_service.py`
- `README.md`

---

## Current System State
The repo currently has:
- a minimal FastAPI app in `app/main.py`
- a single API router in `app/api/routes.py`
- existing endpoints:
  - `GET /`
  - `GET /health`
  - `GET /summary`
- downstream JSON artifacts for Silver / Gold / KPI / similarity / valuation outputs
- no implemented database session layer in the API path yet
- no current API schemas for player, comparison, stat, or valuation responses

### Important implication
For MVP API exposure, the safest design is **read-only endpoints backed by existing generated JSON artifacts**, not live ORM/database queries.

That matches the current architecture and avoids inventing ingestion/runtime persistence that does not exist yet.

---

## Architectural Recommendation
Expose the new APIs as read-only FastAPI endpoints that load already-generated pipeline artifacts from `data/silver/` and `data/gold/`.

### Keep current boundaries
- API route definitions stay in `app/api/`
- artifact loading logic should live in a dedicated API/service helper
- analysis generation remains in `app/analysis/` and `app/pipeline/`
- do not move business logic into route functions
- do not introduce DB dependencies for this ticket

### Recommended new modules
Add:
- `app/api/schemas.py`
  - typed response models / Pydantic schemas
- `app/api/data_access.py`
  - JSON artifact loading helpers
  - filtering / lookup helpers for routes
  - consistent not-found / empty-state handling

Update:
- `app/api/routes.py`

Optional small helper reuse:
- `app/pipeline/io.py` may be reused for reading JSON files if convenient

---

## API Source of Truth Recommendation
Use pipeline artifacts as the API source of truth for MVP.

### Recommended artifact sources
- `data/silver/players.json`
- `data/silver/player_match_stats.json`
- `data/gold/player_similarity.json`
- `data/gold/player_valuation.json`
- optionally `data/gold/kpi_engine.json` for enriched player summaries
- optionally `data/gold/player_features.json` for aggregate player-level stats

### Why
- the repo already generates these artifacts
- the API can be shipped without waiting for DB ingestion
- this avoids mismatch between unpopulated DB tables and usable analysis outputs
- it keeps the API read-only and deterministic for MVP

---

## Endpoint Design Recommendation

### 1. `GET /players`
Primary listing endpoint for player-level profile + aggregate stats.

#### Recommended behavior
Return one row per player using Silver `players` as the base row, enriched with:
- Gold `player_features`
- KPI output when present
- valuation summary when present

#### Recommended query params
- `name`: optional substring filter
- `position`: optional exact or normalized filter
- `club`: optional exact or normalized filter
- `limit`: optional integer, default `50`, max `200`
- `offset`: optional integer, default `0`
- `include`: optional comma-separated enrichments, e.g. `features,kpi,valuation`

#### Recommended response shape
```json
{
  "count": 1,
  "items": [
    {
      "player_name": "...",
      "preferred_name": "...",
      "position": "...",
      "current_club": "...",
      "nationality": "...",
      "date_of_birth": "...",
      "features": { ... },
      "kpi": { ... },
      "valuation": { ... }
    }
  ]
}
```

#### MVP fallback behavior
- if enrichments are missing, return the base player row with omitted or `null` subobjects
- if no players exist, return `count: 0` and `items: []`

---

### 2. `GET /players/{player_name}/stats`
The ticket text mentions stats even though it did not explicitly list a `/stats` endpoint. To satisfy the stated feature scope, expose player stats under a nested player route rather than a top-level `/stats` route.

#### Recommended behavior
Return match-level stat rows for one player from Silver `player_match_stats.json`.

#### Recommended query params
- `limit`: optional integer, default `20`, max `100`
- `offset`: optional integer, default `0`
- `sort`: optional, default `-match_date`

#### Recommended response shape
```json
{
  "player_name": "...",
  "count": 2,
  "items": [
    {
      "match_date": "...",
      "club_name": "...",
      "minutes": 0,
      "goals": 0,
      "assists": 0,
      "shots": 0,
      "passes_completed": 0,
      "yellow_cards": 0,
      "red_cards": 0,
      "source": "fbref"
    }
  ]
}
```

#### Why nested route is preferable
- stats are player-scoped in the current MVP
- avoids adding a vague top-level `/stats` endpoint with unclear filtering rules
- aligns better with the currently available Silver artifact structure

---

### 3. `GET /compare`
Comparison endpoint backed by the similarity artifact.

#### Recommended behavior
Return similar-player results for a requested player.

#### Recommended query params
- `player_name`: required
- `limit`: optional integer, default `5`, max `20`

#### Recommended response shape
```json
{
  "player_name": "...",
  "position": "...",
  "comparison_features": { ... },
  "similar_players": [
    {
      "player_name": "...",
      "position": "...",
      "distance": 0.0,
      "similarity_score": 0.0
    }
  ]
}
```

#### Error behavior
- missing `player_name` query param → `422`
- requested player not found → `404`
- similarity artifact missing → `503` with a message that analysis output is not generated yet

---

### 4. `GET /value`
Valuation lookup endpoint backed by the valuation artifact.

#### Recommended behavior
Support both:
- single-player lookup by `player_name`
- ranked list view when `player_name` is omitted

#### Recommended query params
- `player_name`: optional
- `limit`: optional integer, default `20`, max `100`
- `offset`: optional integer, default `0`
- `tier`: optional filter on `elite_mvp|strong_mvp|solid_mvp|rotation_mvp|development_mvp`

#### Recommended response shapes
Single-player lookup:
```json
{
  "player_name": "...",
  "position": "...",
  "current_club": "...",
  "valuation_score": 0.0,
  "valuation_tier": "...",
  "components": { ... },
  "inputs": { ... },
  "model_version": "mvp_v1"
}
```

List mode:
```json
{
  "count": 10,
  "items": [ ... ]
}
```

#### Error behavior
- requested player not found → `404`
- valuation artifact missing → `503`

---

## Route Layout Recommendation
Keep everything in the existing router for MVP unless route count starts growing significantly.

### Recommended additions to `app/api/routes.py`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare`
- `GET /value`

This is enough for MVP and does not require route splitting yet.

If route growth continues after this ticket, a follow-up can split into:
- `app/api/player_routes.py`
- `app/api/analysis_routes.py`

---

## Response Modeling Recommendation
Add Pydantic schemas for API clarity and validation.

### Suggested schema groups
In `app/api/schemas.py`:
- `PlayerListItem`
- `PlayerListResponse`
- `PlayerStatRow`
- `PlayerStatsResponse`
- `CompareResponse`
- `ValuationRow`
- `ValuationListResponse`
- `ErrorResponse`

### Why
- keeps route return shapes stable
- documents the API surface clearly
- improves testability and future OpenAPI docs

---

## Data Access Helper Recommendation
Create one small helper layer for artifact reads.

### Suggested responsibilities
In `app/api/data_access.py`:
- `load_players()`
- `load_player_features()`
- `load_kpi_rows()`
- `load_similarity_rows()`
- `load_valuation_rows()`
- `load_player_match_stats()`
- normalized name lookup helpers
- pagination helper
- artifact existence checks

### Important behavior
If a required artifact file does not exist:
- raise a controlled API-layer error
- route should convert this into a `503 Service Unavailable`

This is preferable to generic tracebacks or pretending empty data means success.

---

## Filtering / Lookup Recommendation
Use normalized player-name matching consistently across API lookups.

### MVP lookup rule
- normalize by lowercasing and trimming whitespace
- exact normalized match for single-player endpoints
- substring normalized match only for list filtering

### Why
- aligns with existing similarity / valuation implementation
- avoids introducing fuzzy matching complexity during MVP

---

## Pagination Recommendation
Use simple offset/limit pagination everywhere list results appear.

### Reason
- consistent with the repo's current simplicity
- no need for cursor pagination yet
- good enough for the narrow IDV-focused MVP dataset

### Standard defaults
- `limit=20` for analysis/list endpoints
- `limit=50` for `/players`
- enforce maximums to prevent accidental large reads

---

## Error Handling Recommendation
Use explicit FastAPI `HTTPException`s.

### Recommended cases
- `404` when a specific player is requested and not found
- `422` for invalid query parameters (FastAPI already helps here)
- `503` when required pipeline artifacts have not been generated yet

### Example 503 detail
```json
{
  "detail": "Required analysis artifact is not available. Run the pipeline first."
}
```

---

## Non-Breaking Constraints
Do not:
- add write/update/delete endpoints
- add authentication/authorization in this ticket
- depend on live DB queries
- duplicate analysis formulas inside route logic
- make routes generate pipeline outputs automatically

Do:
- expose read-only APIs from existing artifacts
- keep business logic outside route functions
- use typed schemas
- return stable JSON shapes

---

## Testing Recommendation
Add API tests using FastAPI `TestClient`.

### Recommended test file
- `tests/test_api_routes.py`

### Coverage targets
1. `GET /health` still works
2. `GET /summary` still works
3. `GET /players` returns list response shape
4. `/players` filters work for `name`, `position`, `club`
5. `GET /players/{player_name}/stats` returns only that player's rows
6. `GET /compare?player_name=...` returns expected similarity payload
7. `GET /compare` returns `404` for unknown player
8. `GET /value` list mode returns valuation rankings
9. `GET /value?player_name=...` returns one valuation row
10. missing artifact file returns `503` instead of a traceback

### Test strategy note
Tests should use temporary JSON fixtures or monkeypatch the artifact loader so the API layer is tested independently from the full pipeline.

---

## Documentation Recommendation
Update `README.md` after implementation to document:
- available endpoints
- required pipeline artifacts
- example requests
- note that endpoints are read-only and artifact-backed in MVP

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- API endpoints for players, stats, comparison, and valuation implemented

### `memory/decisions.md`
Add:
- MVP APIs are read-only and backed by generated artifact files rather than live DB queries
- stats exposure uses a nested player route
- compare/value endpoints read from Gold-layer analysis outputs

### `memory/architecture.md`
Add:
- API layer now exposes artifact-backed read endpoints over Silver and Gold outputs

---

## Risks / Watchouts
- artifact-backed APIs can return stale data if the pipeline has not been rerun
- missing artifact files must not silently appear as empty success responses
- name-based lookups can collide if duplicate player names appear later
- route logic can become messy if loading/filtering is not pushed into helpers
- nested enrichment objects should stay optional so partial artifacts do not break `/players`

---

## QA Checklist for Pedant
Pedant should verify:
- read-only endpoints do not mutate data
- missing artifacts produce `503`
- single-player lookups return `404` when appropriate
- `/players/{player_name}/stats` filters correctly
- `/compare` and `/value` use normalized player-name lookup
- pagination limits are enforced
- response shapes match the documented schema
- existing `/health` and `/summary` endpoints still pass

---

## Expected Files for Grunt Phase
Likely changes:
- `app/api/routes.py`
- `app/api/schemas.py`
- `app/api/data_access.py`
- `tests/test_api_routes.py`
- possibly `README.md`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-217.md`

---

## Artifact for Next Role
Grunt should implement read-only FastAPI endpoints for `/players`, `/players/{player_name}/stats`, `/compare`, and `/value` using generated Silver/Gold JSON artifacts as the MVP source of truth, with typed schemas, helper-based artifact loading, pagination/filtering, and explicit `404`/`503` behavior.
