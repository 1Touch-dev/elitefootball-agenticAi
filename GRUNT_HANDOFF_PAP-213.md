# GRUNT HANDOFF — PAP-213

## What changed
- Added a dedicated KPI analysis package under `app/analysis/`.
- Implemented reusable KPI helpers for:
  - per-90 metrics
  - rolling averages
  - bounded consistency score
  - age parsing and age multipliers
  - base KPI score composition
- Implemented a KPI engine that consumes Silver tables and writes `data/gold/kpi_engine.json`.
- Integrated KPI generation into the main pipeline runner.
- Extended Silver player-match rows with match metadata needed for rolling windows.
- Updated memory with KPI formulas, decisions, and next steps.

## Files changed
- `app/config.py`
- `app/pipeline/run_pipeline.py`
- `app/pipeline/silver.py`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Files added
- `ARCHITECT_PLAN_PAP-213.md`
- `GRUNT_HANDOFF_PAP-213.md`
- `app/analysis/__init__.py`
- `app/analysis/kpi_formulas.py`
- `app/analysis/kpi_engine.py`

## Pedant QA checklist
- Verify KPI code is isolated under `app/analysis/`.
- Verify per-90 metrics handle zero or missing minutes safely.
- Verify rolling averages work with short match histories.
- Verify consistency score stays within `0..100`.
- Verify missing DOB uses neutral age multiplier `1.00`.
- Verify `run_pipeline()` now returns a `kpi` section and writes `data/gold/kpi_engine.json`.
- Verify memory files mention the exact KPI formulas and multiplier bands.

## Notes
- Player matching currently uses normalized `player_name` because stable IDs are not yet propagated across all layers.
- KPI output is safe to generate even when Silver tables are empty.
- I did not push a branch or create a PR.
