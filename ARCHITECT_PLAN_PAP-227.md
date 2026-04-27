# ARCHITECT PLAN — PAP-227

## Ticket
PAP-227 — End-to-End System Test (Full Pipeline)

## Role
Architect — planning/design only. No runtime implementation changes in this phase.

## Goal
Define a concrete, non-breaking implementation plan for a true end-to-end system validation that covers:
- scraping
- DB ingestion
- KPI/analysis generation
- backend/UI-facing delivery
- output validation

This phase should leave the next role with a precise plan for what to implement, what to validate, and what should count as success.

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/progress.md`
- `memory/decisions.md`

Repo inspection completed:
- `app/pipeline/run_pipeline.py`
- `app/agents/orchestrator.py`
- `app/db/persistence.py`
- `app/api/data_access.py`
- `app/api/routes.py`
- `app/main.py`
- `dashboard/Home.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`
- `tests/test_e2e_full_system.py`
- `scripts/verify_full_system_flow.py`
- `ARCHITECT_PLAN_PAP-243.md`
- `ARCHITECT_PLAN_PAP-246.md`

---

## Current System State
The repo now has most of the seams required for a full-pipeline system test:
1. scrape-like raw/parsed inputs can exist under source-specific directories
2. Bronze/Silver/Gold pipeline stages are implemented
3. Silver-to-DB ingestion exists in `app/db/persistence.py`
4. backend routes read from artifact files rather than from the live DB
5. dashboard pages consume backend API responses through the dashboard client
6. a seeded full-system validator already exists in:
   - `tests/test_e2e_full_system.py`
   - `scripts/verify_full_system_flow.py`

However, the current system is still constrained by environment/runtime realities:
- live scraping remains fragile because source access and browser/runtime dependencies are not guaranteed
- backend/API validation depends on FastAPI availability in the environment
- DB validation depends on SQLAlchemy availability in the environment
- the product path remains artifact-first even though DB ingestion now exists

---

## Root Cause / Gap Analysis
PAP-227 is not primarily about inventing a new architecture. The gap is that the project still lacks a **clearly defined, strict contract** for what a “full pipeline” validation must prove.

The existing PAP-226 implementation already validates much of the path, but PAP-227 should tighten the definition of required stages and expected outputs.

### Specific gap
The repo currently has a seeded validator, but the acceptance boundary for “scraping → DB → KPIs → UI” is still ambiguous because:
1. the scrape stage is represented by seeded scrape-like inputs rather than a guaranteed live scrape
2. the DB stage can skip when SQLAlchemy is unavailable
3. the UI stage is validated through backend + dashboard client payload checks, not through browser-rendered Streamlit interaction
4. there is no single documented contract that says which stages are mandatory, which may skip, and which outputs must be non-empty

PAP-227 should fix that ambiguity.

---

## Architectural Recommendation
Preserve the existing architecture.

Do **not**:
- redesign the pipeline around the DB
- make the dashboard read directly from the DB or raw artifacts
- require a live external scrape as the only passing test path
- couple the validation to one machine’s browser setup

Do:
- treat the seeded fixture path as the primary deterministic regression gate
- define a stricter required-output contract for the full pipeline
- keep live scrape verification as optional/best-effort
- keep DB validation additive to the current artifact-first system

### Architecture principle
The authoritative operational path remains:
1. scrape/raw+parsed artifacts
2. Bronze manifest
3. Silver normalized tables
4. DB ingestion from Silver
5. Gold/KPI/analysis artifacts
6. backend endpoints serving artifact-backed data
7. dashboard client consuming backend payloads

That is the path PAP-227 should validate.

---

## Recommended Deliverable Shape
The next role should extend the existing full-system validation surface rather than create a parallel system.

### Primary files to update
- `tests/e2e_full_pipeline_support.py`
- `tests/test_e2e_full_system.py`
- `scripts/verify_full_system_flow.py`

### Supporting docs
- `README.md`
- `GRUNT_HANDOFF_PAP-227.md`
- `PEDANT_HANDOFF_PAP-227.md`

Recommendation: build PAP-227 on top of the current PAP-226 seeded validator instead of duplicating it under a new file family.

---

## Required Validation Contract
PAP-227 should define the following stages and mark each one as either **required** or **conditionally skippable**.

### Stage 1 — scrape-stage inputs exist (required)
This does not need to be a live network scrape in the required path.

#### What counts as success
- raw scrape-like HTML fixture files exist
- parsed source payloads exist for both Transfermarkt-like and FBref-like paths
- payloads are shaped realistically enough to exercise downstream normalization

#### Why
This preserves determinism while still validating the system’s scrape boundary.

---

### Stage 2 — Bronze manifest builds correctly (required)

#### Success conditions
- Bronze manifest file exists
- artifact count is non-zero
- manifest includes expected raw + parsed source artifacts

---

### Stage 3 — Silver normalization succeeds (required)

#### Success conditions
- `players` is non-empty
- `matches` is non-empty
- `player_match_stats` is non-empty
- `player_per90` is non-empty
- required counts match the seeded scenario contract

#### Minimum recommended seeded dataset
- at least 2 players
- at least 2 matches
- at least 4 player match stat rows
- at least 4 per-90 rows

Why 2+ players instead of 1:
- similarity/compare outputs are more meaningful
- UI comparison path becomes a true happy-path test rather than a degenerate fallback

---

### Stage 4 — DB ingestion verifies persisted rows (required when SQLAlchemy is installed; otherwise explicit SKIP)

#### Success conditions when available
- DB ingest runs from Silver tables
- persistence status is `success_complete` or `success_partial` with zero critical verification failures
- row counts for clubs, players, matches, and stats are query-verified
- persisted counts meet seeded minimum expectations

#### Skip behavior
If SQLAlchemy is unavailable in the environment:
- the stage may skip
- the report must explicitly say why
- the overall run must still make it obvious that the environment is not release-complete for DB verification

#### Important recommendation
PAP-227 should introduce a stronger concept of **environment readiness**:
- local/dev: DB stage may skip
- CI/release-ready environments: DB stage should be expected to pass

---

### Stage 5 — KPI and downstream analysis outputs exist (required)

#### Required artifacts
- `player_features`
- `kpi_engine`
- `advanced_metrics`
- `player_risk`
- `player_similarity`
- `player_valuation`
- `club_development_rankings`

#### Success conditions
- each required artifact exists
- each required artifact is non-empty where appropriate
- at least one similarity row contains non-empty `similar_players`
- at least one valuation row contains a `valuation_score`

---

### Stage 6 — backend serves generated outputs (required when FastAPI is installed; otherwise explicit SKIP)

#### Required endpoints
- `GET /health`
- `GET /dashboard/status`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare?player_name=...`
- `GET /value?player_name=...`

#### Success conditions
- HTTP 200 for happy-path calls
- responses are non-empty for the seeded player(s)
- `/dashboard/status` reflects ready/partial state consistently with artifact presence

#### Skip behavior
If FastAPI is unavailable:
- explicit SKIP only
- do not present this as a full backend-verified success

---

### Stage 7 — dashboard client receives expected payloads (required when FastAPI is installed; otherwise explicit SKIP)

#### Success conditions
- dashboard client loads status successfully
- player list contains seeded players
- player stats count > 0
- compare payload includes non-empty `similar_players`
- value payload includes `valuation_score`

#### Scope boundary
This stage validates the dashboard data contract, not full browser-rendered Streamlit automation.

---

## Required Output Reporting
The next role should keep explicit stage reporting and make it slightly stricter.

### Report format recommendation
Each stage should emit:
- `PASS`
- `FAIL`
- `SKIP`

And include:
- stage name
- concise details
- observed counts where relevant
- limitation or dependency reason for SKIPs

### Additional recommendation
Add a final rollup line with one of:
- `READY`
- `READY_WITH_LIMITATIONS`
- `NOT_READY`

#### Suggested semantics
- `READY`: all required stages passed and no dependency-based skips occurred
- `READY_WITH_LIMITATIONS`: required core artifact stages passed, but DB/API/UI stages were skipped due to missing runtime dependencies
- `NOT_READY`: any required executed stage failed

This will make release-readiness more explicit than the current binary pass model.

---

## Environment Readiness Preflight
PAP-227 should add a lightweight preflight stage or summary that checks whether runtime dependencies for the full pipeline are available.

### Preflight should report
- SQLAlchemy available: yes/no
- FastAPI available: yes/no
- optional live scrape/browser dependencies available: yes/no

### Why
This makes it clear whether a result is:
- a full verification run
- or a partial-but-still-useful seeded verification run

This does not require changing the product architecture; it is a validation ergonomics improvement.

---

## Live Scrape Policy
Live scrape execution should remain optional.

### Required path
- seeded scrape-like fixtures

### Optional path
- live source fetch followed by the same validation stages

### Why
Live source access remains too unstable to be the only valid regression path because of:
- missing Playwright/browser setup
- anti-bot blocking
- network variability
- source markup changes

If implemented later, live mode should be clearly labeled:
- best-effort
- diagnostic
- not required for CI acceptance

---

## Recommended Implementation Steps For Grunt

### Step 1
Review the current seeded validator in:
- `tests/e2e_full_pipeline_support.py`
- `tests/test_e2e_full_system.py`
- `scripts/verify_full_system_flow.py`

### Step 2
Tighten the seeded scenario contract so it explicitly covers:
- 2+ players
- 2+ matches
- non-empty compare/similarity path
- non-empty valuation path
- DB verification counts when available

### Step 3
Add an environment preflight summary to the script/test reporting.

### Step 4
Add final release-readiness rollup states:
- `READY`
- `READY_WITH_LIMITATIONS`
- `NOT_READY`

### Step 5
Document the contract in `README.md` so operators know the difference between:
- deterministic required validation
- optional live-source verification
- dependency-limited partial validation

### Step 6
Leave Pedant clear review targets for:
- stage strictness
- skip semantics
- readiness semantics
- whether backend/UI/DB stages are strict enough

---

## Non-Breaking Constraints
Do not:
- move API reads from artifacts to DB-backed queries for this ticket
- require Streamlit browser automation to claim UI-contract validation
- rewrite scraper/orchestrator architecture
- remove seeded-mode support

Do:
- build on the existing validator
- preserve hermetic temp-path behavior
- keep stage outputs explicit and operator-readable
- make release-readiness semantics clearer than they are today

---

## Pedant Review Checklist
Pedant should verify:
1. the PAP-227 implementation extends the current full-system validator rather than duplicating it unnecessarily
2. the seeded dataset truly exercises scrape → DB → KPI → UI seams
3. SKIP behavior is explicit and not mistaken for full success
4. final readiness rollup is accurate
5. backend and dashboard validations are routed through real generated artifacts, not mocks of data loaders
6. DB verification checks persisted query counts when SQLAlchemy is available
7. documentation clearly distinguishes deterministic required mode from best-effort live mode

---

## Recommended Next Issue
Add a dedicated environment-readiness command for the pipeline stack so operators can see before runtime whether the current machine can perform:
- live scrape verification
- DB verification
- backend verification
- dashboard-contract verification

---

## Artifact For Next Role
Grunt should treat PAP-227 as a tightening pass on the existing full-system validator: preserve the seeded deterministic workflow, strengthen stage requirements and reporting, add environment-readiness semantics, and clearly define when the full pipeline is truly release-ready versus merely validated with limitations.
