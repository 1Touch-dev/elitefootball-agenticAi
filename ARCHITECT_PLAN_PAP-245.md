# ARCHITECT PLAN — PAP-245

## Ticket
Fix dashboard rendering for scraped data.

## Scope
Plan only. Do not implement code in this phase.

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Code inspection completed:
- `dashboard/api_client.py`
- `dashboard/Home.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- `app/api/routes.py`
- `app/api/data_access.py`
- `app/api/schemas.py`
- `tests/test_api_routes.py`

## Current System State
The dashboard is API-backed, which matches the intended architecture.

Current UI flow:
- `Home.py` calls `/health`
- `1_Player.py` calls `/players` and `/players/{player_name}/stats`
- `2_Compare.py` calls `/players`, `/compare`, and `/value`

Current backend flow:
- API routes read Silver/Gold JSON artifacts through `app/api/data_access.py`
- routes return stable player, stats, comparison, and valuation payloads
- current checkout does **not** include a dashboard-specific readiness/status endpoint yet

Current artifact state in this checkout:
- `data/silver/players.json` -> `[]`
- `data/silver/player_match_stats.json` -> `[]`
- `data/gold/player_features.json` -> `[]`
- `data/gold/kpi_engine.json` -> `[]`
- `data/gold/player_similarity.json` -> `[]`
- `data/gold/player_valuation.json` -> `[]`

## Root Cause Found
The dashboard’s rendering problem is a mix of **real empty data** and **insufficient UI state distinction**.

### Confirmed causes
1. The current artifacts are empty, so the dashboard legitimately has nothing to render.
2. The current dashboard pages do not distinguish clearly enough between:
   - backend reachable but no data yet
   - backend route failure
   - comparison/stats unavailable for one selected player
   - partial data availability (for example, players exist but stats or valuation do not)
3. The current home page only checks `/health`, which is too shallow to explain whether dashboard data is actually ready.
4. The current compare page treats `/compare` failures as a page-level fatal error, even though player summary data may still be renderable.
5. The current UI does not have an explicit reusable loading pattern; it effectively jumps straight from request to success/error.

### Important non-root-cause note
There is no primary evidence of a frontend/backend field-name mismatch in the inspected code. The endpoint shapes and page field access are broadly aligned.

## Architectural Recommendation
Keep the existing architecture:
- dashboard -> backend API -> artifact-backed storage

Do **not** make the dashboard read artifacts directly.
Do **not** move dashboard logic into backend routes.
Do **not** introduce DB-backed reads for this ticket.

## Implementation Plan for Grunt

### 1. Add backend dashboard readiness/status support
Because the current checkout does not yet expose data-readiness diagnostics, PAP-245 should include a small backend support change.

#### Add endpoint
- `GET /dashboard/status`

#### Endpoint responsibilities
Return:
- top-level status: `ready`, `partial`, `empty`, `artifact_missing`, `artifact_invalid`
- per-artifact state
- row counts
- optional sample rows
- human-readable errors

#### Backend modules likely to change
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- add focused tests for artifact inspection logic if needed

#### Why this matters
The dashboard needs a reliable source of truth for “no data” vs “fetch failed” vs “partially ready.” `/health` alone cannot provide that.

---

### 2. Expand the dashboard API client
#### Add client method
- `get_dashboard_status()` in `dashboard/api_client.py`

#### Client behavior
- preserve current error normalization via `DashboardAPIError`
- return parsed status payload from `/dashboard/status`
- avoid any direct artifact reading fallback

#### Optional helper improvement
Add a small response-normalization helper in the client so pages can consistently ask for:
- `is_ready`
- `is_empty`
- `is_partial`
- `status_message`

This can also live in a dashboard helper module if that keeps the Streamlit pages cleaner.

---

### 3. Fix Home page to show real dashboard readiness
Current Home only shows backend reachability.

#### Required changes
- call `/dashboard/status` in addition to or instead of `/health`
- show distinct UI states:
  - backend unreachable -> `st.error(...)`
  - artifacts empty -> `st.warning(...)`
  - artifacts partially ready -> `st.info(...)`
  - ready -> `st.success(...)`
- show small readiness summary table/card:
  - players rows
  - stats rows
  - similarity rows
  - valuation rows

#### Goal
Make the Home page the first place a user can understand whether the dashboard has renderable data.

---

### 4. Fix Player page rendering behavior
The Player page should remain useful even when some downstream artifacts are missing.

#### Required rendering states
1. **Loading state**
   - wrap the initial player fetch in `st.spinner("Loading player data...")`
2. **Fatal backend error**
   - if `/players` fails, show `st.error(...)` and stop
3. **Empty state**
   - if `/players` returns zero items, show a specific empty-state message
   - include dashboard-status hints when available
4. **Partial data state**
   - if player rows exist but stats fail or are empty, still render profile/valuation/KPI cards
   - stats section should show its own warning/info state instead of taking down the page
5. **Missing valuation/KPI/features**
   - preserve current graceful fallbacks, but make messaging slightly more explicit

#### Additional recommendation
Fetch dashboard status once per page load and use it to enrich empty-state messaging. Example:
- “Players artifact is empty. Run the pipeline first.”
- “Player list exists, but match-stats artifact is empty.”

#### Possible helper extraction
Create a small shared helper module, for example:
- `dashboard/ui_state.py` or `dashboard/helpers.py`

Suggested helpers:
- `render_backend_error(...)`
- `render_empty_state(...)`
- `format_dashboard_status(...)`

This reduces repeated logic across pages.

---

### 5. Fix Compare page rendering behavior
This page currently fails too hard when compare data is unavailable.

#### Required rendering changes
1. **Loading state**
   - wrap initial player fetch and compare fetch in `st.spinner(...)`
2. **Fatal error only when player list cannot load**
   - if `/players` fails, stop the page
3. **Non-fatal compare failure**
   - if `/compare` fails, keep rendering the selected player summary
   - show a dedicated compare-section error/warning instead of stopping the whole page
4. **Partial data rendering**
   - if selected player exists and valuation exists, render those even if similarity data is absent
5. **Enriched similar-player table correctness**
   - current code may replace similarity rows with valuation rows, dropping distance/similarity fields
   - the implementation should merge valuation fields **into** similarity rows, not replace them

#### Important correctness issue to plan for
Current code:
- builds `enriched_rows.append(valuation_lookup.get(row.get("player_name"), {**row}))`

That means when a valuation row exists, the original similarity row fields can be lost.

#### Recommended fix
For each similar-player row:
- start from the similarity row
- merge in selected valuation fields if present, for example:
  - `valuation_score`
  - `valuation_tier`
- preserve:
  - `distance`
  - `similarity_score`
  - `position`

This is the clearest rendering bug found in current dashboard code.

---

### 6. Add explicit reusable state language
The dashboard should use consistent wording for three distinct cases:

#### Loading
- “Loading dashboard data…”
- “Loading player data…”
- “Loading comparison data…”

#### Empty
- “No dashboard data is available yet.”
- “Player data is not available yet.”
- “Comparison data is not available yet.”

#### Error
- “Could not reach backend API.”
- “Backend data is unavailable because required artifacts are missing.”
- “Comparison request failed, but player summary data is still available below.”

This should be centralized where practical.

---

### 7. Validate field names against backend contract
#### Confirmed aligned fields
Player page expects fields that backend already returns:
- `player_name`
- `preferred_name`
- `position`
- `current_club`
- `nationality`
- `date_of_birth`
- nested `valuation`
- nested `kpi`
- nested `features`

Stats page fields align with backend:
- `match_date`
- `club_name`
- `minutes`
- `goals`
- `assists`
- `shots`
- `passes_completed`
- `yellow_cards`
- `red_cards`
- `source`

Compare fields align with backend:
- `player_name`
- `position`
- `comparison_features`
- `similar_players[*].player_name`
- `similar_players[*].position`
- `similar_players[*].distance`
- `similar_players[*].similarity_score`

Valuation list fields align with backend:
- `player_name`
- `valuation_score`
- `valuation_tier`
- `model_version`

#### Conclusion
PAP-245 should not focus on schema renaming. It should focus on state handling and row-merge correctness.

---

### 8. Add targeted tests
#### Dashboard client tests
Add or expand:
- `tests/test_dashboard_api_client.py`

Cover:
- `get_dashboard_status()` success
- backend error handling for `/dashboard/status`
- invalid JSON behavior

#### Pure helper tests
If page logic is moved into helpers, add tests for:
- compare-row enrichment preserves similarity fields
- status-to-message mapping
- empty/error-state classification helpers

#### Route tests
If `/dashboard/status` is added in this ticket, add focused backend tests for:
- empty artifacts -> `status == "empty"`
- partial artifacts -> `status == "partial"`
- missing required artifacts -> `status == "artifact_missing"`
- invalid artifact payload -> `status == "artifact_invalid"`

---

### 9. Verification plan
If the project environment supports Streamlit/manual verification, Grunt should capture notes or screenshots.

#### Minimum verification notes
1. Backend reachable, artifacts empty:
   - Home page shows empty/partial explanation, not just healthy API
   - Player page shows explicit empty state
   - Compare page shows explicit empty state
2. Backend reachable, sample mocked/non-empty data:
   - Player page renders profile, valuation/KPI/features, and stats table
   - Compare page renders selected-player summary and similar-player table
   - enriched compare rows retain both similarity and valuation fields
3. Backend unavailable:
   - pages show explicit error state
4. Partial data:
   - player list renders even if stats or compare data is missing

#### Screenshot guidance
If screenshots are feasible, capture:
- Home page empty state
- Player page with sample data
- Compare page with sample data and preserved similarity columns

---

## Files Likely to Change in Grunt Phase
### Backend support
- `app/api/data_access.py`
- `app/api/routes.py`
- `tests/test_api_routes.py`
- possibly `tests/test_data_access.py`

### Dashboard
- `dashboard/api_client.py`
- `dashboard/Home.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- optionally a new helper module such as `dashboard/helpers.py`
- `tests/test_dashboard_api_client.py`
- optionally helper tests

### Documentation / handoff
- `README.md` if run/behavior notes change
- `GRUNT_HANDOFF_PAP-245.md`
- `PEDANT_HANDOFF_PAP-245.md`

---

## Non-Breaking Constraints
Do not:
- make dashboard pages read raw files directly
- collapse backend failure into generic “no data” messaging
- replace the current API-backed dashboard pattern
- stop rendering the whole page when only one section fails

Do:
- keep the dashboard API-first
- preserve current route contracts where possible
- add section-level loading/error/empty handling
- fix compare-row enrichment so valid similarity data remains visible

---

## QA Checklist for Pedant
Pedant should verify:
- dashboard uses `/dashboard/status` for readiness messaging if implemented
- empty state and error state are visually distinct on Home, Player, and Compare pages
- Compare page does not lose `distance` and `similarity_score` after valuation enrichment
- Player page still renders profile if stats request fails
- Compare page still renders selected player summary if compare request fails
- field names still match backend payloads
- no direct artifact reads were introduced into dashboard code

---

## Recommended Next Issue After PAP-245
PAP-246 - add lightweight dashboard smoke coverage or screenshot-based validation against a running backend with seeded non-empty artifacts.

---

## Artifact for Next Role
Grunt should implement PAP-245 by adding a backend dashboard-status endpoint if still absent, expanding the dashboard client to consume it, and updating the Home/Player/Compare Streamlit pages so they clearly distinguish loading, empty, partial, and error states while preserving valid partial data and fixing the compare-table enrichment bug that can hide similarity fields.
