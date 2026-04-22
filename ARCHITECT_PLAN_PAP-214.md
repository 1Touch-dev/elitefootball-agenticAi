# ARCHITECT PLAN — PAP-214

## Ticket
Implement advanced metrics: xG, xA, and progression.

## Requested Build
- integrate xG / xA
- compute progression stats

Memory must be updated with:
- metric formulas
- metric assumptions

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo currently has:
- FBref scraping and parsing for match payloads, player match stats, and per-90 payloads
- Silver table construction for:
  - `players`
  - `transfers`
  - `matches`
  - `player_match_stats`
  - `player_per90`
- Gold feature generation under `app/pipeline/gold.py`

Current implementation gap for this ticket:
- no advanced-metrics-specific analysis module in the current working tree
- FBref player stat parsing does not yet normalize xG/xA or progression metrics into Silver rows
- no downstream feature output for xG/xA/progression

This should be treated as a new implementation task, not a refactor-only pass.

---

## Architectural Recommendation
Keep the existing boundaries intact:
- scraping/parsing stays in `app/scraping/`
- Silver normalization stays in `app/pipeline/silver.py`
- advanced metric derivation belongs in a dedicated analysis module under `app/analysis/`
- pipeline orchestration remains in `app/pipeline/run_pipeline.py`

### Recommended new module layout
Add:
- `app/analysis/__init__.py`
- `app/analysis/advanced_metrics.py`
  - pure helpers for metric normalization and formula composition
- `app/analysis/advanced_metrics_engine.py`
  - consumes Silver tables and writes advanced-metric output

Integrate via:
- `app/pipeline/run_pipeline.py`

Preferred output path:
- `data/gold/advanced_metrics.json`

---

## Source Data Strategy
Use FBref as the primary source for these advanced metrics.

### Silver-layer responsibility
`app/pipeline/silver.py` should normalize and preserve, when available:
- `xg`
- `xa`
- progression-related stat fields such as:
  - progressive carries
  - progressive passes
  - progressive receptions / progressive passes received
  - carries into final third
  - passes into final third
  - carries into penalty area
  - passes into penalty area

### Why Silver normalization matters
- advanced metrics should not depend directly on raw HTML in the analysis layer
- formulas should operate on stable, cleaned keys
- it keeps source-specific parser quirks isolated upstream

---

## FBref Parsing Recommendation
Extend `app/scraping/fbref_parsers.py` to capture advanced stat columns when present.

### Recommended normalized field mapping
Map FBref row keys into cleaned match-stat outputs using fallbacks such as:
- `xg` ← `xg` or `expected_goals`
- `xa` ← `xa` or `expected_assists`
- `progressive_carries` ← `progressive_carries` or `prgc`
- `progressive_passes` ← `progressive_passes` or `prgp`
- `progressive_receptions` ← `progressive_passes_received` or `prgr`
- `carries_into_final_third` ← `carries_into_final_third` or equivalent source field
- `passes_into_final_third` ← `passes_into_final_third` or equivalent source field
- `carries_into_penalty_area` ← `carries_into_penalty_area`
- `passes_into_penalty_area` ← `passes_into_penalty_area`

Implementation should be tolerant of missing columns and partial tables.

---

## Recommended Silver Schema Additions
Extend `player_match_stats` rows with nullable numeric fields:
- `xg`
- `xa`
- `progressive_carries`
- `progressive_passes`
- `progressive_receptions`
- `carries_into_final_third`
- `passes_into_final_third`
- `carries_into_penalty_area`
- `passes_into_penalty_area`

Do not force these into the DB schema yet unless explicitly required by a separate ticket.
For now, Silver + Gold is sufficient and non-breaking.

---

## Metric Formula Recommendations
These formulas should be written explicitly into memory during implementation.

### 1. xG per 90
```text
xg_per_90 = (xg / minutes_played) * 90
```
Guardrails:
- only compute when `minutes_played > 0`
- otherwise return `null`

### 2. xA per 90
```text
xa_per_90 = (xa / minutes_played) * 90
```
Guardrails:
- only compute when `minutes_played > 0`
- otherwise return `null`

### 3. Goal overperformance / underperformance
Useful derived metric:
```text
goals_minus_xg = goals - xg
```
Interpretation:
- positive = finishing above xG
- negative = finishing below xG

### 4. Assist overperformance / underperformance
```text
assists_minus_xa = assists - xa
```

### 5. Progressive actions total
Recommended simple aggregate:
```text
progressive_actions =
  progressive_carries +
  progressive_passes +
  progressive_receptions
```
Use `0` for missing component values only when the field is absent for that row after Silver normalization.

### 6. Progressive actions per 90
```text
progressive_actions_per_90 = (progressive_actions / minutes_played) * 90
```

### 7. Final-third progression total
Recommended aggregate:
```text
final_third_entries =
  carries_into_final_third +
  passes_into_final_third
```

### 8. Penalty-area progression total
Recommended aggregate:
```text
penalty_area_entries =
  carries_into_penalty_area +
  passes_into_penalty_area
```

### 9. Progression score
Recommended MVP composite score:
```text
progression_score =
  (progressive_actions_per_90 * 0.50) +
  (final_third_entries_per_90 * 0.30) +
  (penalty_area_entries_per_90 * 0.20)
```

This is intentionally simple and explainable.

---

## Output Recommendation
Write a dedicated Gold-layer artifact with player-level aggregated advanced metrics.

### Recommended output fields
```json
{
  "player_name": "...",
  "minutes_played": 0,
  "xg": 0.0,
  "xa": 0.0,
  "xg_per_90": 0.0,
  "xa_per_90": 0.0,
  "goals_minus_xg": 0.0,
  "assists_minus_xa": 0.0,
  "progressive_carries": 0,
  "progressive_passes": 0,
  "progressive_receptions": 0,
  "progressive_actions": 0,
  "progressive_actions_per_90": 0.0,
  "final_third_entries": 0,
  "final_third_entries_per_90": 0.0,
  "penalty_area_entries": 0,
  "penalty_area_entries_per_90": 0.0,
  "progression_score": 0.0
}
```

Output path:
- `data/gold/advanced_metrics.json`

---

## Join / Identity Guidance
For MVP, use normalized `player_name` joins between:
- Transfermarkt player profile rows
- FBref player stat rows

Document assumption clearly:
- player-name joining is acceptable for MVP
- source-stable IDs should be added later when parser coverage improves

---

## Non-Breaking Constraints
Do not:
- move advanced-metric formulas into scraper modules
- push xG/xA/progression directly into API routes
- require DB schema changes unless separately requested
- replace existing Silver or Gold outputs

Do:
- extend Silver rows safely with nullable fields
- add a new Gold output for advanced metrics
- preserve existing pipeline outputs and behavior

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- advanced metric parsing and output support implemented
- xG/xA and progression engine added

### `memory/decisions.md`
Add:
- exact xG/xA per-90 formulas
- progression composite assumptions
- missing-field handling rules

### `memory/architecture.md`
Add:
- advanced metrics engine location
- relation between FBref parser output, Silver normalization, and Gold advanced metrics artifact

---

## Risks / Watchouts
- FBref columns differ across table types and competitions
- some progression columns may not exist in every payload
- treating missing columns as true zero everywhere can distort players with incomplete source coverage
- multiple FBref tables may duplicate the same player row unless filtered carefully
- player-name joins remain imperfect for duplicates / aliases

---

## QA Checklist for Pedant
Pedant should verify:
- parser additions tolerate absent advanced columns
- Silver rows contain stable nullable advanced metric fields
- xG/xA per-90 calculations handle zero minutes safely
- progression totals do not crash on missing components
- progression score remains explainable and deterministic
- pipeline runner emits a dedicated advanced metrics artifact
- memory includes exact formulas and assumptions

---

## Expected Files for Grunt Phase
Likely changes:
- `app/scraping/fbref_parsers.py`
- `app/pipeline/silver.py`
- `app/pipeline/run_pipeline.py`
- `app/analysis/__init__.py`
- `app/analysis/advanced_metrics.py`
- `app/analysis/advanced_metrics_engine.py`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-214.md`

---

## Artifact for Next Role
Grunt should extend FBref parsing and Silver normalization to carry xG, xA, and progression-related fields, then implement a dedicated analysis engine that aggregates those fields into player-level advanced metrics and writes a new Gold artifact with explicit formulas documented in memory.
