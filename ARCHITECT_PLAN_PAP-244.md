# ARCHITECT_PLAN_PAP-244 — Audit Backend Data Endpoints Used by Dashboard

## Ticket
PAP-244

## Role
Architect — planning/design only. No runtime code changes in this phase.

## Goal
Determine why the dashboard shows no data after scraping by tracing the full path from stored artifacts into backend endpoints and then into the Streamlit UI.

This phase answers:
- what the dashboard actually calls
- what the backend actually reads
- whether response shapes match the frontend contract
- whether “no data” is a real empty-state or a hidden backend failure
- what implementation changes should be made next without breaking the artifact-first architecture

---

## 1) Current End-to-End Data Flow

## 1.1 Dashboard data source
The dashboard does **not** read files or the DB directly.
It uses `dashboard/api_client.py` to call backend HTTP endpoints:
- `GET /health`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare`
- `GET /value`

## 1.2 Backend query source
The backend endpoints do **not** query the relational DB.
They read JSON artifacts via `app/api/data_access.py`:
- `data/silver/players.json`
- `data/silver/player_match_stats.json`
- `data/gold/player_features.json`
- `data/gold/kpi_engine.json`
- `data/gold/player_similarity.json`
- `data/gold/player_valuation.json`

## 1.3 Pipeline source of those artifacts
Those artifacts are produced by the pipeline:
- scrape raw/parsed artifacts
- build Silver tables
- build Gold/KPI/similarity/valuation artifacts
- dashboard reads those generated artifact files through the backend API

So the dashboard’s live dependency is:
**dashboard -> backend API -> artifact loader -> Silver/Gold JSON files**

---

## 2) Root Cause Found

## Primary root cause
The current backend/dashboard path is artifact-backed, and the checked-in artifact files that the backend reads are currently empty:
- `data/silver/players.json` -> `[]`
- `data/silver/player_match_stats.json` -> `[]`
- `data/gold/player_valuation.json` -> `[]`

That means the dashboard can legitimately show no data even when the backend contract is functioning correctly.

## Secondary finding
The current response shapes appear aligned with dashboard expectations:
- `/players` returns `{ count, items }`
- `/players/{player_name}/stats` returns `{ player_name, count, items }`
- `/compare` returns `{ player_name, position, comparison_features, similar_players }`
- `/value` returns either a single valuation row or `{ count, items }`

So the current issue is **not primarily a frontend/backend schema mismatch**.

## Tertiary risk
The dashboard currently cannot distinguish cleanly between:
- real empty artifacts
- pipeline never run
- artifact load failures for optional enrichments
- upstream scrape/pipeline outputs being empty because source data never populated

Some of that is surfaced already (503 on required missing artifacts), but not enough context is returned to explain why the dataset is empty.

---

## 3) What Is Working vs What Is Missing

## Working
- dashboard client paths match backend routes
- backend route payload shapes broadly match frontend expectations
- player page and compare page handle empty `items` lists gracefully
- `ArtifactUnavailableError` becomes HTTP 503 for required missing artifacts

## Missing or weak
- no backend data-status/debug endpoint explaining current artifact availability and row counts
- no route-level visibility into which artifacts are empty vs missing vs malformed
- no compact sample payload endpoint/output for quick dashboard debugging
- no explicit confirmation that pipeline outputs are populated before the dashboard is launched
- no operational summary tying scrape success, Silver counts, and dashboard-readable endpoint counts together

---

## 4) Backend Data Flow Audit

## 4.1 Dashboard expectations
### Player page
Calls:
- `/players?include=features,kpi,valuation`
- `/players/{player_name}/stats`

Expects:
- player list under `items`
- each player row may include `valuation`, `kpi`, `features`
- stats endpoint returns `items` list with match rows

### Compare page
Calls:
- `/players`
- `/compare`
- `/value`

Expects:
- player list under `items`
- compare payload with `similar_players`
- valuation list under `items` for enrichment lookup

These expectations currently align with backend shapes.

## 4.2 Backend route dependencies
- `/players` depends primarily on `silver/players.json`
- `/players/{name}/stats` depends on `silver/player_match_stats.json`
- `/compare` depends on `gold/player_similarity.json`
- `/value` depends on `gold/player_valuation.json`

If those artifacts are empty, the dashboard will be empty even though the backend is healthy.

## 4.3 Observed artifact state in current checkout
Observed sample state in this repo:
- `players.json`: empty list
- `player_match_stats.json`: empty list
- `player_valuation.json`: empty list

This strongly suggests the current dashboard symptom is a truthful reflection of empty backend data, not a UI rendering defect.

---

## 5) Recommended Technical Direction

## 5.1 Preserve the current architecture
Do **not** rewrite the dashboard to read the DB or raw files directly.
Do **not** move analysis logic into dashboard pages.

Keep:
- dashboard -> backend API
- backend API -> artifact-backed loaders (for now)

## 5.2 Add explicit backend observability for dashboard-facing data
The next implementation should make the backend explain its state clearly.

Recommended additions:
1. a dashboard-data status endpoint
2. tighter artifact validation in `app/api/data_access.py`
3. optional debug metadata on existing responses or a dedicated debug endpoint
4. route tests covering empty/missing/malformed artifact cases

---

## 6) Detailed Implementation Plan for the Next Role

## Step 1 — Add a backend dashboard data-status endpoint
### New endpoint
- `GET /dashboard/status`

### Response should include
- whether each required artifact exists
- whether it is missing vs empty vs malformed
- row counts for each artifact
- a few sample records per artifact when present
- a top-level status like:
  - `ready`
  - `partial`
  - `empty`
  - `artifact_missing`
  - `artifact_invalid`

### Why
This turns “dashboard has no data” from guesswork into something directly inspectable.

---

## Step 2 — Strengthen `app/api/data_access.py`
### Current weakness
Malformed artifacts currently degrade to `[]` in some cases, which can blur empty-data vs invalid-data.

### Plan
Add a richer loader result or stricter error paths so the backend can distinguish:
- missing file
- non-list payload
- list with non-dict rows
- empty but valid artifact
- non-empty valid artifact

### Suggested approach
Either:
- add metadata-returning helper functions
or
- add parallel inspection helpers for status/debug paths while preserving existing simple loaders

---

## Step 3 — Audit existing route behavior under empty and partial data
### `/players`
Verify behavior when:
- `players.json` empty
- optional feature/kpi/valuation artifacts missing or empty

### `/players/{name}/stats`
Verify behavior when:
- stats artifact empty
- player exists in players but has no stats
- player missing entirely

### `/compare`
Verify behavior when:
- players list exists but similarity artifact empty
- similarity exists but no entry for selected player

### `/value`
Verify behavior when:
- valuation artifact empty but players list exists

### Goal
Make sure actual backend failures do not masquerade as simple empty UI states.

---

## Step 4 — Add route-level sample debug output if needed
If the product wants fast debugging without a new admin page, add temporary or guarded debug output such as:
- row counts
- data-source artifact names
- generation timestamps

Best done in a dedicated status/debug endpoint rather than polluting user-facing response contracts.

---

## Step 5 — Document the response shapes explicitly
Add or update documentation for:
- `/players`
- `/players/{player_name}/stats`
- `/compare`
- `/value`
- `/dashboard/status`

Include a sample non-empty payload so frontend debugging has a known-good target.

---

## Step 6 — Add backend tests for dashboard-facing endpoint states
### Suggested new tests
- `tests/test_dashboard_status.py`
- or expand `tests/test_api_routes.py`

### Cover cases
- required artifact missing -> 503 or status endpoint flags `artifact_missing`
- valid but empty artifact -> endpoint returns empty list/count and status endpoint flags `empty`
- malformed artifact -> explicit error/status classification
- non-empty artifact -> response payload sample matches dashboard expectations

---

## 7) Proposed Status Contract

Example `GET /dashboard/status` payload:

```json
{
  "status": "empty",
  "artifacts": {
    "players": {
      "path": "data/silver/players.json",
      "exists": true,
      "valid": true,
      "row_count": 0,
      "state": "empty"
    },
    "player_match_stats": {
      "path": "data/silver/player_match_stats.json",
      "exists": true,
      "valid": true,
      "row_count": 0,
      "state": "empty"
    },
    "valuation": {
      "path": "data/gold/player_valuation.json",
      "exists": true,
      "valid": true,
      "row_count": 0,
      "state": "empty"
    }
  },
  "samples": {
    "players": [],
    "player_match_stats": [],
    "valuation": []
  }
}
```

---

## 8) Sample Working Response Payload Target

Example non-empty `/players` payload the dashboard already expects:

```json
{
  "count": 1,
  "items": [
    {
      "player_name": "Patrik Mercado",
      "preferred_name": "Patrik Mercado",
      "position": "Attacking Midfield",
      "current_club": "Independiente del Valle",
      "nationality": "Ecuador",
      "date_of_birth": "2003-01-01",
      "features": {"matches": 20, "goal_contribution_per_90": 0.82},
      "kpi": {"base_kpi_score": 68.4, "consistency_score": 72.1},
      "valuation": {"valuation_score": 71.2, "valuation_tier": "strong_mvp", "model_version": "mvp_v1"}
    }
  ]
}
```

This shape is consistent with current dashboard page usage.

---

## 9) Success Criteria Interpretation

PAP-244 should be complete when:
- backend data availability is observable and explainable
- backend endpoints return valid non-empty data when artifacts contain records
- empty dashboard states are clearly distinguished from backend artifact failures
- response shapes are documented and verified against frontend expectations

### Current best truth before implementation
- the dashboard is using the correct backend endpoints
- the backend response shapes broadly match the frontend contract
- the checked-in artifact data currently appears empty
- therefore the most likely immediate cause of “no data” is empty upstream artifacts, not a dashboard rendering bug

---

## 10) Files Expected to Change in Next Role

### Likely updates
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- maybe new `tests/test_dashboard_status.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`

### Possible new file
- `app/api/dashboard_status.py` or keep it inside `routes.py`

---

## 11) Next Recommended Issue

**Recommended next issue:**
`PAP-245 - Add Dashboard Data Status Endpoint and Artifact Validation`

Suggested scope:
- expose dashboard-readable artifact readiness and row counts
- distinguish missing vs empty vs invalid artifacts
- provide sample response payloads for frontend debugging
- keep dashboard contract artifact-backed for now

---

## 12) Files Changed In This Phase

Planning + memory only:
- `ARCHITECT_PLAN_PAP-244.md`
- `memory/progress.md`
- `memory/decisions.md`
