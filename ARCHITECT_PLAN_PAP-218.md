# ARCHITECT PLAN — PAP-218

## Ticket
Build MVP dashboard for player and comparison views.

## Requested stack
- Streamlit or Next.js

## Requested pages
- `player`
- `compare`

## Memory to Capture
- UI decisions

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Code / stack inspection completed:
- `requirements.txt`
- `README.md`
- `app/api/routes.py`

---

## Current System State
The repo is currently:
- Python-first
- backend/API oriented
- artifact/pipeline oriented
- not set up as a multi-package frontend/backend monorepo
- not configured with Node, React, TypeScript, or Next.js tooling

The system already has:
- FastAPI backend routes
- generated analysis artifacts
- player, comparison, and valuation data available through backend/API layers or pipeline outputs

### Important implication
For the MVP dashboard, **Streamlit is the correct choice**.

It fits the current repo because:
- the project is already Python-based
- it avoids introducing a second runtime/toolchain
- it can consume the existing API or artifacts immediately
- it is faster to ship for an internal MVP dashboard

### Recommendation
Choose **Streamlit**, not Next.js, for PAP-218.

Next.js can be a later follow-up if the project graduates into a richer product UI.

---

## Architectural Recommendation
Build a small Streamlit dashboard as a separate UI layer that reads through the API, not directly from business-logic internals.

### Keep current boundaries
- backend/API remains in `app/`
- dashboard should live in a dedicated top-level UI folder or app file
- dashboard must not duplicate KPI/similarity/valuation formulas
- dashboard should call exposed endpoints instead of re-reading analysis logic

### Recommended new UI structure
Option A (simplest MVP):
- `dashboard/`
  - `Home.py`
  - `pages/1_Player.py`
  - `pages/2_Compare.py`
  - `api_client.py`

Option B (single-file MVP):
- `streamlit_app.py`
- `dashboard/api_client.py`

### Preferred option
Use **Option A** with Streamlit multipage layout.

Why:
- maps naturally to the requested `player` and `compare` pages
- keeps page code separate and readable
- easiest to extend later with valuation or scouting views

---

## Data Flow Recommendation
The dashboard should consume the API endpoints, not raw JSON artifacts.

### Recommended source endpoints
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare`
- `GET /value`

### Why this is better than reading artifacts directly
- preserves backend/UI separation
- keeps dashboard aligned with the API contract
- avoids duplicating artifact-path assumptions in the UI
- makes later deployment easier if backend and dashboard split onto different services

### Fallback note
If API availability is a blocker during implementation, a temporary artifact-backed fallback client is acceptable only as a thin adapter, but the intended architecture should remain **API-first**.

---

## Recommended Requirements Update
Add Streamlit and keep dependency scope small.

### Recommended additions to `requirements.txt`
- `streamlit>=1.44,<2.0`

Optional helper dependency only if implementation truly needs it:
- avoid adding pandas unless it clearly simplifies rendering materially

### Recommendation
Prefer native Python + Streamlit widgets first.
Do not add heavy frontend/data dependencies unless needed.

---

## Page Design Recommendation

### 1. Player Page
Purpose: show one player's profile, stats, valuation, and recent performance context.

#### Suggested layout
Top section:
- player selector (dropdown or searchable select)
- optional query param support via URL/session state

Primary content blocks:
1. **Player profile card**
   - name
   - preferred name
   - position
   - club
   - nationality
   - date of birth

2. **Aggregate metrics**
   - valuation score + tier
   - base KPI or key performance numbers when available
   - minutes / matches / goal contribution information

3. **Recent stats table**
   - match date
   - minutes
   - goals
   - assists
   - shots
   - passes completed
   - yellow/red cards

4. **Quick interpretation section**
   - simple badges/metrics only
   - no new analysis logic beyond displaying existing signals

#### Recommended API calls
- `GET /players?name=<player>`
- `GET /players/{player_name}/stats`
- `GET /value?player_name=<player>`

#### MVP goal
Make it easy to inspect one player end-to-end in one page.

---

### 2. Compare Page
Purpose: compare one player to their nearest similar players.

#### Suggested layout
Top section:
- source player selector
- optional result limit control

Primary content blocks:
1. **Selected player summary**
   - name
   - position
   - current valuation score (if available)

2. **Comparison feature summary**
   - the normalized/raw features already exposed by the compare output

3. **Similar players table**
   - player name
   - position
   - similarity score
   - distance

4. **Optional valuation enrichment**
   - if the compared players exist in `/value`, show valuation score/tier alongside similarity rows

#### Recommended API calls
- `GET /players`
- `GET /compare?player_name=<player>&limit=<n>`
- `GET /value` (for lookup/join enrichment)

#### MVP goal
Give a clear “who is this player most like?” workflow with minimal clicks.

---

## UX Recommendation
Keep the UI simple and internal-facing.

### MVP UX rules
- prioritize readability over styling
- use Streamlit metrics, tables, columns, and expanders
- no custom design system
- no authentication in this ticket
- no charting dependency unless existing data clearly benefits from one simple chart

### Suggested widget set
- `st.selectbox` for player selection
- `st.metric` for KPI/valuation snapshots
- `st.dataframe` or `st.table` for stats/comparison tables
- `st.columns` for profile + score layout
- `st.warning` / `st.error` for missing backend/artifact states

---

## Error / Empty State Recommendation
The dashboard must handle missing data gracefully.

### Required states
1. **Backend/API unavailable**
   - show a clear error banner
   - do not crash the app

2. **No players available**
   - show a helpful empty state
   - avoid rendering broken selectors

3. **Missing comparison result**
   - show “no comparison data yet” instead of blank widgets

4. **Missing valuation result**
   - still render player page with profile/stats only

### Why
The current project is pipeline-backed; artifact freshness and completeness will vary.
The dashboard should reflect that without pretending data exists.

---

## API Client Recommendation
Add a very small dashboard API client.

### Recommended file
- `dashboard/api_client.py`

### Suggested responsibilities
- read base API URL from env var
- make GET requests
- normalize error handling
- return parsed JSON payloads

### Suggested env var
- `ELITEFOOTBALL_API_BASE_URL`

Default suggestion:
- `http://localhost:8000`

### Suggested helper methods
- `get_players(...)`
- `get_player_stats(player_name, ...)`
- `get_compare(player_name, ...)`
- `get_value(player_name=None, ...)`

---

## Routing / Page Layout Recommendation
Use Streamlit's built-in multipage behavior.

### Suggested page order
- `Home.py`
  - quick intro
  - instructions
  - backend health status
- `pages/1_Player.py`
- `pages/2_Compare.py`

### Home page recommendation
Show:
- app title
- MVP scope note (IDV players)
- backend health check status
- links/instructions for the two pages

---

## Non-Breaking Constraints
Do not:
- replace FastAPI with Streamlit
- move dashboard code into `app/api/`
- duplicate analysis formulas in UI code
- read raw scraper files directly from the dashboard
- introduce Node/Next.js tooling for this ticket

Do:
- add a separate Streamlit layer
- keep UI dependent on API responses
- make missing-data states explicit
- keep dependency footprint small

---

## Testing Recommendation
For MVP, prioritize lightweight UI-adjacent tests rather than full browser automation.

### Recommended tests
- `tests/test_dashboard_api_client.py`
  - verifies API client request/response handling
  - verifies failure handling for unavailable backend

Optional:
- a small test for dashboard helper functions if page logic is split into pure helpers

### Do not require yet
- Playwright browser automation for dashboard pages
- visual regression tests
- complex frontend snapshot tests

---

## Documentation Recommendation
Update `README.md` after implementation to include:
- how to run the API
- how to run the Streamlit dashboard
- required environment variable for API base URL
- note that dashboard is MVP/internal and depends on backend availability

Suggested run examples:
```bash
uvicorn app.main:app --reload
streamlit run dashboard/Home.py
```

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- MVP Streamlit dashboard implemented for player and comparison views

### `memory/decisions.md`
Add:
- Streamlit chosen over Next.js for the MVP because the repo is Python-first and API-driven
- dashboard consumes API endpoints rather than raw artifacts directly

### `memory/architecture.md`
Add:
- dashboard is a separate UI layer that sits on top of the backend API

---

## Risks / Watchouts
- API and dashboard can drift if route shapes change without updating the client
- missing FastAPI/Streamlit dependencies in local environments can hide runtime issues
- dashboard pages can become brittle if page logic is not separated from rendering helpers
- direct artifact reads in the UI would create hidden coupling and should be avoided
- URL/session-state selection should remain simple in MVP to avoid unnecessary state bugs

---

## QA Checklist for Pedant
Pedant should verify:
- Streamlit is used, not Next.js
- dashboard reads through API client helpers, not raw artifact paths
- player page works when valuation is missing but profile/stats exist
- compare page handles missing comparison rows gracefully
- backend-unavailable state renders a user-visible error instead of crashing
- no analysis logic is duplicated in the UI layer
- README run instructions are accurate

---

## Expected Files for Grunt Phase
Likely changes:
- `requirements.txt`
- `dashboard/Home.py`
- `dashboard/api_client.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- possibly dashboard helper modules for shared rendering/state
- `tests/test_dashboard_api_client.py`
- `README.md`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-218.md`

---

## Artifact for Next Role
Grunt should implement a small Streamlit multipage dashboard with `player` and `compare` pages, backed by a lightweight API client that consumes the existing backend endpoints for players, stats, comparison, and valuation, while handling backend/missing-data states cleanly and without duplicating analysis logic.
