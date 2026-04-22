# ARCHITECT PLAN — PAP-213

## Ticket
Implement core KPI engine (Per 90 + Age Adjusted).

## Requested Build
- per 90 stats
- rolling averages
- consistency score

Memory must be updated with:
- KPI formulas

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo currently has:
- source-specific scraping for Transfermarkt and FBref
- normalized DB schema for clubs, players, matches, and stats
- a pipeline runner under `app/pipeline/`
- simple Gold feature generation in `app/pipeline/gold.py`

What is **not** present yet in the current working tree:
- no `app/analysis/` KPI module
- no dedicated KPI engine artifact
- no per-90 / rolling / age-adjusted engine in the current pipeline runner

So this ticket should be treated as a real implementation gap, not just refinement.

---

## High-Level Recommendation
Implement the KPI engine as a dedicated analysis layer downstream from Silver tables.

### Preferred direction
Add an `app/analysis/` package that:
- contains pure KPI formulas
- contains an engine/orchestrator that consumes Silver outputs
- writes a dedicated Gold-layer KPI output artifact

This preserves the existing architecture:
- scraping remains in `app/scraping/`
- transformations remain in `app/pipeline/`
- KPI scoring lives in an analysis-specific package

---

## Recommended File / Module Plan
Suggested additions:
- `app/analysis/__init__.py`
- `app/analysis/kpi_formulas.py`
  - pure calculation helpers
- `app/analysis/kpi_engine.py`
  - reads Silver tables and writes KPI output

Recommended integration update:
- `app/pipeline/run_pipeline.py`
  - call the KPI engine after Silver + Gold generation

Possible supporting update:
- `app/pipeline/silver.py`
  - carry enough match ordering metadata into player match stats to support rolling windows safely

Preferred output path:
- `data/gold/kpi_engine.json`

---

## Input Data Recommendation
The KPI engine should consume Silver tables, especially:
- `players`
- `player_match_stats`
- optionally `player_per90`

### Why Silver is the right input
- Silver is already cleaned and source-agnostic
- KPI formulas should not depend on source-specific parser quirks
- it preserves the Bronze → Silver → Gold architecture

---

## KPI Formula Recommendations
These formulas should be explicitly written into memory during implementation.

### 1. Per-90 metrics
Recommended formula:
```text
per_90(metric_total, minutes_played) = (metric_total / minutes_played) * 90
```

Guardrails:
- only compute if `minutes_played > 0`
- otherwise return `null`

Recommended MVP metrics:
- goals_per_90
- assists_per_90
- shots_per_90
- passes_completed_per_90
- goal_contributions_per_90

### 2. Rolling averages
Use recent-match windows over player match rows.

Recommended windows:
- last 3 matches
- last 5 matches

Recommended formula:
```text
rolling_average(metric, window) = sum(last_n_values) / count(last_n_values)
```

Guardrails:
- if there are fewer than `window` matches, use the available rows
- never fail on short histories

Recommended rolling KPIs:
- rolling_3_goals_per_90
- rolling_5_goal_contributions_per_90
- rolling_3_shots_per_90
- rolling_5_minutes

### 3. Consistency score
Use recent per-90 outputs and convert lower variation into a higher score.

Recommended MVP formula:
```text
consistency_score = max(0, min(100, 100 - (std_dev * scaling_factor)))
```

Recommended defaults:
- use recent `goal_contributions_per_90`
- use a scaling factor around `25`
- clamp to `0..100`

### 4. Age adjustment
Use a transparent multiplier based on age bands.

Recommended MVP multipliers:
```text
<21      -> 1.10
21-24    -> 1.05
25-29    -> 1.00
30+      -> 0.95
unknown  -> 1.00
```

Recommended formula:
```text
age_adjusted_score = base_kpi_score * age_multiplier
```

---

## Composite KPI Recommendation
Use a simple weighted base score before age adjustment.

Suggested base score:
```text
base_score =
  (goal_contributions_per_90 * 0.45) +
  (shots_per_90 * 0.20) +
  (passes_completed_per_90 * 0.15) +
  ((consistency_score / 100) * 0.20)
```

Why this works for MVP:
- transparent
- explainable
- easy to tune later

---

## Output Shape Recommendation
Recommended row shape:
```json
{
  "player_name": "...",
  "minutes_played": 0,
  "age": 0,
  "goals_per_90": 0.0,
  "assists_per_90": 0.0,
  "shots_per_90": 0.0,
  "goal_contributions_per_90": 0.0,
  "passes_completed_per_90": 0.0,
  "rolling_3_goals_per_90": 0.0,
  "rolling_5_goal_contributions_per_90": 0.0,
  "rolling_3_shots_per_90": 0.0,
  "rolling_5_minutes": 0.0,
  "consistency_score": 0.0,
  "age_multiplier": 1.0,
  "base_kpi_score": 0.0,
  "age_adjusted_kpi_score": 0.0
}
```

Store as:
- `data/gold/kpi_engine.json`

---

## Matching / Join Guidance
Recommended MVP join key:
- normalized `player_name`

Caveat:
- this is imperfect without source-stable IDs
- acceptable for MVP, but should be documented in memory/handoff

---

## Non-Breaking Architecture Guidance
Do not break the current architecture.

Specifically:
- do not put KPI formulas in scraper code
- do not put scoring logic in DB models
- do not calculate rolling KPIs in API routes
- keep KPI logic downstream from Silver tables

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- KPI engine implemented
- per-90, rolling, consistency, and age-adjusted scoring added

### `memory/decisions.md`
Add:
- exact KPI formulas
- consistency score decision
- age-band multiplier decision

### `memory/architecture.md`
Add:
- KPI engine location
- connection between Silver tables, Gold features, and KPI outputs

---

## Risks / Watchouts
- computing KPIs from raw HTML instead of Silver tables
- mixing source-reported per-90 metrics with computed per-90 metrics without labeling them
- rolling windows without a stable order field
- aggressive age multipliers that distort rankings
- silent failures when DOB is missing

---

## QA Checklist for Pedant
Pedant should verify:
- KPI code is isolated outside scraper and DB modules
- per-90 metrics guard against zero or missing minutes
- rolling averages handle short histories safely
- consistency score stays bounded `0..100`
- missing DOB defaults to neutral age multiplier
- pipeline runner emits KPI output after implementation
- memory includes explicit KPI formulas

---

## Files Expected to Change in Grunt Phase
Most likely:
- `app/analysis/__init__.py`
- `app/analysis/kpi_formulas.py`
- `app/analysis/kpi_engine.py`
- `app/pipeline/run_pipeline.py`
- possibly `app/pipeline/silver.py`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-213.md`

---

## Artifact for Next Role
Grunt should implement a dedicated KPI analysis package that consumes Silver tables, computes per-90 metrics, rolling averages, a bounded consistency score, and an age-adjusted composite KPI, then writes a dedicated Gold-layer KPI artifact and updates memory with the exact formulas used.
