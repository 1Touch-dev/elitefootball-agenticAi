# GRUNT_HANDOFF_PAP-221

## Scope
Implement the risk model planned in `ARCHITECT_PLAN_PAP-221.md`.

## What to build
- `app/analysis/risk.py`
- `app/analysis/risk_engine.py`
- pipeline integration in `app/pipeline/run_pipeline.py`
- valuation integration updates in:
  - `app/analysis/valuation.py`
  - `app/analysis/valuation_engine.py`
- tests:
  - `tests/test_risk.py`
  - `tests/test_risk_engine.py`
  - update `tests/test_valuation_engine.py`
- optionally README note for the new artifact if time permits

## Required architectural rules
- Do not touch scraper modules for this ticket
- Do not change DB schema
- Keep the model artifact-backed and downstream only
- Injury risk must be documented/implemented as an availability proxy, not a true medical injury classifier
- Preserve valuation fallback behavior if risk rows are absent

## Recommended implementation shape
### `app/analysis/risk.py`
Pure helper functions only, no I/O.
Expected helpers:
- clamp helpers
- coefficient-of-variation helper
- date-gap helper from sorted appearance dates
- small-sample penalty helper
- injury/availability proxy scorer
- volatility scorer
- risk tier helper

### `app/analysis/risk_engine.py`
Expected behavior:
- consume silver tables (players, player_match_stats)
- optionally use gold/kpi inputs where helpful
- build one row per player
- write `data/gold/player_risk.json`
- return `{ "path": ..., "rows": ... }`

### Output contract
Include at least:
- `player_name`
- `position`
- `current_club`
- `risk_score`
- `risk_tier`
- `components`
  - `injury_risk_score`
  - `volatility_risk_score`
  - `discipline_risk_score`
  - optional penalties
- `inputs`
  - `age`
  - `matches`
  - `minutes`
  - gap stats
  - volatility stats
  - `consistency_score`
- `model_version`

## Valuation integration target
- add optional `risk_rows` input to valuation engine
- if present, use risk artifact as the primary risk deduction source
- if absent, keep current discipline/consistency fallback
- bump valuation model version to something explicit like `mvp_v2_risk`

## Test minimums
- stable player < unstable player on risk
- long appearance gaps increase injury proxy risk
- tiny sample does not crash and applies bounded caution
- valuation score decreases when risk artifact shows elevated risk
- legacy valuation test path still passes without risk rows

## Suggested execution order
1. Add formula helpers
2. Add engine
3. Wire pipeline
4. Integrate valuation
5. Add tests
6. Run targeted tests
7. Update docs if needed
