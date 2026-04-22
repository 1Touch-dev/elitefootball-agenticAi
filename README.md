# elitefootball-agenticAi

Welcome to our System

## Project Bootstrap
This repository now includes a minimal Python backend scaffold, scraping module, database layer, and a mandatory memory system for future multi-agent work focused on IDV players.

## Memory Workflow
All future tasks MUST:
- read memory before work
- update memory after work

## API Endpoints (MVP)
The backend now exposes read-only artifact-backed endpoints:
- `GET /health`
- `GET /summary`
- `GET /players`
- `GET /players/{player_name}/stats`
- `GET /compare?player_name=...`
- `GET /value`
- `GET /value?player_name=...`

## API Notes
- These endpoints read generated artifacts from `data/silver/` and `data/gold/`.
- They do not write data or query the live database in the MVP.
- Run the pipeline first so required artifacts exist before calling compare/value routes.

## Gold Artifacts
- `data/gold/player_risk.json` now stores a transparent MVP risk model for each player.
- The `injury_risk_score` inside that artifact is an availability-risk proxy derived from appearance gaps and minutes patterns, not true medical injury data.
- Valuation now optionally consumes the risk artifact when available and falls back to the legacy discipline/consistency risk deduction when it is not.

## Safety + Approval Layer (PAP-224)
The backend now includes a lightweight safety policy layer for evaluating high-risk actions before execution.

### Policy outcomes
- `allow`
- `require_approval`
- `deny`

### Blocked examples
- delete-repo operations
- `rm -rf .`
- `git clean -fdx`
- remote fetch-and-execute patterns like `curl ... | sh`

### Approval flow endpoints
- `POST /safety/evaluate`
- `GET /approvals/{approval_id}`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`

The MVP approval store is in-memory and approvals are bound to a normalized action fingerprint.
