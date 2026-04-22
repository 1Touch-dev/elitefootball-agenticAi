# GRUNT HANDOFF — PAP-216

## Implemented
Added a simplified downstream player valuation model with transparent additive scoring.

### Files changed
- `app/analysis/valuation.py`
- `app/analysis/valuation_engine.py`
- `app/pipeline/run_pipeline.py`
- `tests/test_valuation.py`
- `tests/test_valuation_engine.py`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`

### Behavior added
- computes `valuation_score` on a bounded `0..100` scale
- writes `data/gold/player_valuation.json`
- includes component breakdowns:
  - performance
  - age
  - minutes
  - club factor
  - league adjustment
  - risk
- includes `valuation_tier`
- integrates valuation into the pipeline return payload
- also wires `advanced_metrics` into `run_pipeline()` so valuation can consume progression enrichment when available

## Formula summary
`valuation_score = clamp(performance + age + minutes + club factor + league adjustment - risk, 0, 100)`

### Implemented assumptions
- KPI is the primary performance signal
- advanced metrics are optional enrichment only
- missing optional inputs fall back conservatively
- IDV gets the highest club factor in the MVP lookup
- reserve/youth contexts get reduced club/league values
- risk subtracts value via discipline plus low-consistency penalty

## Tests added
- `tests/test_valuation.py`
- `tests/test_valuation_engine.py`

## Pedant focus areas
Please verify:
1. valuation scores remain bounded `0..100`
2. valuation rows sort descending by `valuation_score`
3. fallback behavior is correct when KPI or advanced metrics are absent
4. club / league heuristic defaults are acceptable for MVP
5. `run_pipeline()` integration does not regress existing analysis outputs
6. generated artifact shape is stable and reviewable

## Notes
- No DB changes
- No scraper changes
- No branch/PR/push actions performed
