# PEDANT_HANDOFF_PAP-221

## Implementation summary from Grunt
Implemented the PAP-221 risk model as a dedicated downstream analysis artifact and wired valuation to consume it optionally.

### Files changed by Grunt
- added `app/analysis/risk.py`
- added `app/analysis/risk_engine.py`
- updated `app/pipeline/run_pipeline.py`
- updated `app/analysis/valuation.py`
- updated `app/analysis/valuation_engine.py`
- updated `README.md`
- added `tests/test_risk.py`
- added `tests/test_risk_engine.py`
- updated `tests/test_valuation.py`
- updated `tests/test_valuation_engine.py`

### Validation run
- `python3 -m unittest tests.test_risk tests.test_risk_engine tests.test_valuation tests.test_valuation_engine` ✅
- `python3 -m app.pipeline.run_pipeline` ✅

### Specific review requests
- sanity-check the risk weight scaling versus valuation deduction (`risk_deduction`)
- verify the availability proxy language is clear enough and not overstated
- verify the fallback path in valuation does not double-count new and legacy risk inputs

## Review focus
Verify the PAP-221 implementation against the architect plan and existing repo patterns.

## Files expected
- `app/analysis/risk.py`
- `app/analysis/risk_engine.py`
- updates to `app/pipeline/run_pipeline.py`
- updates to `app/analysis/valuation.py`
- updates to `app/analysis/valuation_engine.py`
- `tests/test_risk.py`
- `tests/test_risk_engine.py`
- updated `tests/test_valuation_engine.py`

## What to check carefully

### Architecture
- risk logic is isolated under `app/analysis/`
- pipeline owns orchestration; API routes do not compute risk inline
- no scraper or schema changes slipped in
- artifact path is `data/gold/player_risk.json`

### Semantics
- injury risk is clearly described as an availability proxy
- formulas are transparent and bounded
- output row contains readable `components` and `inputs`
- player-name joins follow existing normalization patterns

### Robustness
- missing dates/minutes do not crash the engine
- low sample sizes remain bounded and sensible
- near-zero means do not cause unstable CV explosions
- rows are sorted predictably (prefer descending risk)

### Valuation integration
- valuation still works when risk rows are absent
- risk-aware valuation uses the new risk artifact when present
- model version is bumped to reflect formula change
- no double-counting bug between new risk artifact and old fallback logic

### Tests
- new tests actually assert ranking/relative behavior, not just field presence
- regression coverage exists for fallback behavior
- existing valuation behavior is not accidentally broken where artifact is missing

## Reject if
- implementation pretends to use true injury data that does not exist
- calculations are opaque or impossible to inspect
- pipeline/API contract breaks existing consumers unnecessarily
- risk is only stuffed into valuation without a dedicated artifact
