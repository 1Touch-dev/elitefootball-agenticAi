# GRUNT HANDOFF — PAP-214

## What changed
- Extended FBref player stat parsing to capture xG, xA, and progression-related fields when present.
- Extended Silver normalization to preserve advanced metric fields and match metadata needed for downstream ordering.
- Added a dedicated advanced metrics analysis module under `app/analysis/`.
- Added a Gold-layer advanced metrics engine that writes `data/gold/advanced_metrics.json`.
- Integrated advanced metrics generation into the main pipeline runner.
- Updated memory with advanced metric formulas, assumptions, and next steps.

## Files changed
- `app/config.py`
- `app/pipeline/silver.py`
- `app/pipeline/run_pipeline.py`
- `app/scraping/fbref_parsers.py`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Files added
- `ARCHITECT_PLAN_PAP-214.md`
- `GRUNT_HANDOFF_PAP-214.md`
- `app/analysis/__init__.py`
- `app/analysis/advanced_metrics.py`
- `app/analysis/advanced_metrics_engine.py`

## Pedant QA checklist
- Verify parser additions tolerate missing advanced-stat columns without crashing.
- Verify Silver rows now contain nullable advanced metric fields.
- Verify `xg_per_90` and `xa_per_90` handle zero or missing minutes safely.
- Verify progression totals and progression score are deterministic and safe with partial data.
- Verify `run_pipeline()` now returns an `advanced_metrics` section and writes `data/gold/advanced_metrics.json`.
- Verify memory includes exact formulas and assumptions for xG/xA/progression.

## Notes
- Advanced metrics are sourced from FBref stat rows only when the relevant columns are present.
- Missing advanced-stat columns remain nullable in Silver and are handled safely downstream.
- Player aggregation currently uses normalized `player_name` for MVP simplicity.
- I did not push a branch or create a PR.
