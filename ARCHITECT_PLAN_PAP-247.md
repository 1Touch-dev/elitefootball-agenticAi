# ARCHITECT PLAN — PAP-247

## Ticket
PAP-247 — Improve Dashboard Empty State and Failure Messaging

## Scope
Improve dashboard UX so the Streamlit UI never looks silently broken when data is unavailable, scraping failed upstream, or the backend cannot serve the expected artifacts.

## Root Cause Found
The current dashboard already avoids many hard crashes, but it still leaves users with ambiguous states:
- Home/Player/Compare mostly show generic warnings or raw request failures, not a clear diagnosis of **why** data is unavailable.
- `/dashboard/status` exposes artifact state, but it does **not** yet expose user-facing sync/failure metadata such as last successful sync time, last failure time, or an explicit upstream scrape/pipeline failure summary.
- Streamlit pages stop early when players are empty, which prevents rendering a richer placeholder state with recovery guidance.
- There is no consistent reusable empty/error-state component across Home, Player, and Compare.
- There is no dashboard-level retry action; users must manually refresh the page or infer what to do next.

## Current Stack Notes
### Existing strengths
- Backend route: `GET /dashboard/status`
- Artifact inspection seam: `app/api/data_access.py::inspect_dashboard_artifacts(...)`
- Dashboard status interpretation: `dashboard/helpers.py::dashboard_status_message(...)`
- Page-level empty/error handling already exists in:
  - `dashboard/Home.py`
  - `dashboard/pages/1_Player.py`
  - `dashboard/pages/2_Compare.py`

### Current gaps
- status payload is artifact-only and lacks operational metadata
- helper functions explain artifact emptiness but not upstream failure cause or recency
- no standard placeholder card/table-empty rendering pattern
- no explicit distinction between:
  - no data yet
  - scrape/pipeline failure
  - backend unreachable/error
  - player-specific “no records found”

## Design Constraints
- Preserve current architecture: Streamlit remains a thin UI over backend endpoints.
- Do not move analysis logic into the dashboard.
- Reuse `/dashboard/status` as the primary UX-status seam instead of teaching each page to inspect artifacts on its own.
- Keep the MVP implementation dependency-light; use existing Streamlit and Python standard library only.

## Proposed Implementation Plan

### 1) Enrich backend dashboard status payload
**Files to update**
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- possibly `tests/test_data_access.py` if status inspection coverage belongs there

**Plan**
Extend `inspect_dashboard_artifacts()` so the payload can include a small `sync` or `diagnostics` section with:
- `last_successful_sync_at`
- `last_failed_sync_at`
- `last_failure_stage`
- `last_failure_message`
- `recommended_action`

**Implementation source options**
Priority order:
1. Read from the existing machine-readable persistence/validation artifacts if present.
2. Fall back to artifact file mtimes for last successful sync approximation.
3. If no failure metadata exists, return `None` values rather than inventing failures.

**Reasoning**
This keeps user-facing messaging anchored to a backend truth source and avoids scattering filesystem heuristics across Streamlit pages.

### 2) Add reusable dashboard UX-state helpers
**Files to update**
- `dashboard/helpers.py`
- `tests/test_dashboard_api_client.py` or a new focused helper test file

**Plan**
Add reusable helpers for:
- classify dashboard availability into explicit categories:
  - `ready`
  - `partial`
  - `empty`
  - `no_records`
  - `upstream_failure`
  - `backend_error`
- derive a friendly title/body/action hint for each category
- format `last_successful_sync_at` for display
- optionally produce a compact retry/help block model consumed by pages

**Reasoning**
The same empty/failure logic is currently duplicated implicitly across pages. A helper seam keeps messages consistent and easy to tune.

### 3) Improve Home page status area
**Files to update**
- `dashboard/Home.py`

**Plan**
Replace the current status-only box with a richer state panel that shows:
- status headline (ready / partial / empty / backend unavailable / upstream failure)
- friendly explanation
- last successful sync time when available
- last failure stage/message when available
- a retry action using `st.button("Retry")` + `st.rerun()`
- a next-step hint such as “run pipeline”, “check backend logs”, or “refresh after scrape completes”

**Reasoning**
Home is the first landing page and should act as the diagnosis hub instead of just a lightweight status echo.

### 4) Improve Player page empty and failure states
**Files to update**
- `dashboard/pages/1_Player.py`

**Plan**
Handle four separate states explicitly:
1. **Backend unreachable** → clear error card, keep page structure visible, offer retry button
2. **No players artifact data** → show friendly empty-state block with sync info and action hint
3. **Player list available but selected player has no valuation/KPI/stats** → show placeholder cards per section instead of blank gaps
4. **Stats endpoint returns nothing or fails** → render an empty-state container under “Recent match stats” with the likely reason and retry hint

**Reasoning**
The page should not just `st.stop()` on empty players unless the page has already rendered a clear placeholder experience.

### 5) Improve Compare page empty and failure states
**Files to update**
- `dashboard/pages/2_Compare.py`

**Plan**
Handle these states explicitly:
1. no players loaded
2. compare request failed due to backend error
3. similarity artifact empty
4. selected player has no similar rows
5. valuation enrichment unavailable while compare rows exist

Render:
- a placeholder panel for “no comparison records found yet”
- a warning banner for valuation enrichment being unavailable without hiding similarity rows
- retry button for compare fetch failures

**Reasoning**
Compare currently does better than Player in some cases, but still collapses multiple failure causes into generic messages.

### 6) Add consistent “no records found” placeholder UI
**Files to update**
- `dashboard/helpers.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`

**Plan**
Introduce a simple reusable rendering helper or content contract for placeholders that includes:
- title
- short explanation
- optional last sync info
- optional action hint
- optional retry CTA

Keep it lightweight with Streamlit primitives (`st.info`, `st.warning`, `st.error`, `st.caption`, `st.button`) rather than custom components.

### 7) Test coverage updates
**Files to update**
- `tests/test_dashboard_api_client.py`
- `tests/test_api_routes.py`
- optionally new `tests/test_dashboard_helpers.py`

**Planned assertions**
- helper classification distinguishes empty vs upstream failure vs backend unavailable
- `/dashboard/status` returns sync/failure metadata shape even when values are null
- Player/Compare-facing helper logic produces stable user guidance for:
  - missing artifacts
  - empty artifacts
  - partial data
  - backend request errors
- if page-level tests are too heavy for current stack, keep logic concentrated in helper functions so it can be unit-tested without Streamlit browser automation

## Recommended File Change Set
Primary likely files:
- `app/api/data_access.py`
- `app/api/routes.py`
- `dashboard/helpers.py`
- `dashboard/Home.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- `tests/test_api_routes.py`
- `tests/test_dashboard_api_client.py`
- possibly `tests/test_data_access.py`
- possibly new `tests/test_dashboard_helpers.py`
- `README.md` (brief UX/status note if needed)

## Acceptance Mapping
### Requirement: friendly empty state message
Covered by reusable helper-backed placeholder blocks on Home/Player/Compare.

### Requirement: retry action if relevant
Covered by page-level retry buttons using Streamlit rerun behavior.

### Requirement: show last successful sync time if available
Covered by enriched `/dashboard/status` sync metadata.

### Requirement: show scrape failure or backend failure status
Covered by explicit upstream failure metadata in backend status plus separate dashboard handling for API request failure.

### Requirement: add placeholder UI for no records found
Covered by Player/Compare section placeholders even when the page has loaded partially.

## Risks / Edge Cases
- There may be no authoritative failure artifact today. In that case, last-failure fields should remain null and messaging should degrade gracefully to artifact-based diagnosis.
- File mtime is an approximation of successful sync time; document it as such if used.
- Streamlit `st.rerun()` behavior should be tied to button clicks only, never automatic loops.
- Avoid marking `partial` data as a hard error when some views remain useful.

## Handoff for Grunt
1. Inspect whether any existing runtime artifact already records pipeline verification or scrape failure metadata.
2. If none exists, implement minimal status metadata with file-mtime fallback and nullable failure fields.
3. Centralize all user-facing dashboard state text in helpers before editing pages.
4. Prefer helper tests over brittle page tests.
5. Keep pages informative even when sections are empty; avoid silent `st.stop()` unless a placeholder is already rendered.

## Next Recommended Issue
After PAP-247, implement a lightweight backend-generated operations/status artifact for scrape + pipeline runs so dashboard sync/failure messaging can rely on explicit run history instead of artifact heuristics.
