# ARCHITECT PLAN — PAP-215

## Ticket
Build player similarity + comparison engine.

## Requested Build
- nearest neighbor search
- similarity scoring

## Required Output
- similar players list

Memory must be updated with:
- similarity logic

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo currently has:
- Silver table generation for player and match-stat data
- Gold feature generation for aggregated player features
- KPI analysis support in the current working tree
- a pipeline runner that already orchestrates Bronze, Silver, Gold, and KPI outputs

Current gap for this ticket:
- no player-similarity analysis module in the current working tree
- no nearest-neighbor or pairwise comparison output
- no dedicated similarity artifact under Gold outputs

This should be treated as a new analysis-layer feature.

---

## Architectural Recommendation
Implement the comparison engine as a dedicated downstream analysis module.

### Keep existing boundaries
- scraping remains in `app/scraping/`
- Silver normalization remains in `app/pipeline/silver.py`
- simple aggregate features remain in `app/pipeline/gold.py`
- similarity logic belongs under `app/analysis/`
- orchestration remains in `app/pipeline/run_pipeline.py`

### Recommended new modules
Add:
- `app/analysis/similarity.py`
  - pure helpers for normalization, distance, and score conversion
- `app/analysis/similarity_engine.py`
  - builds player vectors, computes neighbors, writes output

Integrate via:
- `app/pipeline/run_pipeline.py`

Preferred output path:
- `data/gold/player_similarity.json`

---

## Input Data Recommendation
Primary input should be Gold and Silver outputs, not raw source payloads.

### Recommended sources
From Gold:
- `player_features`

From KPI output, when present:
- goal-contribution and related per-90 values
- consistency score
- age-adjusted or base KPI score

From Silver, when needed:
- `players`
- `player_match_stats`

### Why this is the right layer
- similarity should compare normalized derived features, not raw HTML fields
- upstream parser noise should already be removed
- the feature set can evolve without touching scrapers

---

## Similarity Strategy Recommendation
Use feature-vector comparison with simple normalization and Euclidean distance for MVP.

### Why Euclidean for MVP
- transparent and easy to explain
- easy to debug
- no new dependency required
- works fine for a small player set

### Candidate future upgrades
- cosine similarity
- position-aware weighting
- percentile-normalized features
- role-specific templates

Those are good follow-ups, not MVP requirements.

---

## Feature Vector Recommendation
Build one comparison vector per player from stable derived metrics.

### Suggested MVP features
- `goal_contribution_per_90`
- `shots`
- `minutes`
- `discipline_risk_score`
- `consistency_score` (if available)
- `base_kpi_score` or `age_adjusted_kpi_score` (if available)

If advanced metrics are available later, these can be added:
- `xg_per_90`
- `xa_per_90`
- `progression_score`

### Important constraint
Do not require advanced metrics to exist for the similarity engine to function.
The first version should work on currently available Gold + KPI outputs.

---

## Normalization Recommendation
Before distance calculation, normalize each numeric feature across the compared player set.

### Recommended MVP formula: min-max normalization
```text
normalized_value = (value - min_value) / (max_value - min_value)
```

Guardrails:
- if `max_value == min_value`, use `0.0` for that feature across all players
- missing values should default to `0.0` only after feature extraction and explicit normalization handling

This avoids one large-scale metric dominating distance.

---

## Distance and Score Formula Recommendations
### 1. Euclidean distance
```text
distance(a, b) = sqrt(sum((a_i - b_i)^2))
```

### 2. Similarity score
Convert distance into an intuitive bounded score.

Recommended MVP formula:
```text
similarity_score = max(0, 100 - (distance * 100))
```

Rationale:
- easy to interpret as percentage-like similarity
- bounded to `0..100`
- sufficient for small normalized vectors

### 3. Nearest neighbors
For each player:
- compute distances to all other players
- sort ascending by distance
- keep top `k`

Recommended default:
- `k = 5`

If fewer players exist, return as many as are available.

---

## Position / Context Recommendation
For MVP, do **not** hard-block comparisons by position, but preserve position in output.

Optional light heuristic:
- if positions exist, include a soft bonus or secondary sort for same-position matches later

Reason:
- current player coverage may be too small or incomplete for strict position filtering
- keeping it simple avoids empty results

Document assumption in memory:
- first version is global similarity, not role-scoped similarity

---

## Output Shape Recommendation
Write one row per source player with a ranked neighbor list.

### Recommended output example
```json
{
  "player_name": "...",
  "position": "...",
  "comparison_features": {
    "goal_contribution_per_90": 0.0,
    "shots": 0,
    "minutes": 0,
    "discipline_risk_score": 0,
    "consistency_score": 0.0,
    "base_kpi_score": 0.0
  },
  "similar_players": [
    {
      "player_name": "...",
      "position": "...",
      "distance": 0.0,
      "similarity_score": 0.0
    }
  ]
}
```

Output file:
- `data/gold/player_similarity.json`

---

## Data Join Recommendation
Recommended join key for MVP:
- normalized `player_name`

Join sources:
- Gold `player_features`
- KPI output rows
- Silver `players` for metadata like position

Caveat:
- name-based joins are acceptable for MVP only
- should be replaced later with stable IDs when available

---

## Non-Breaking Constraints
Do not:
- move comparison logic into scraper code
- require DB schema changes
- replace existing Gold or KPI outputs
- block the engine on advanced metrics availability

Do:
- create a new dedicated analysis module
- emit a new Gold-layer similarity artifact
- keep the engine resilient to partial feature availability

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- similarity engine implemented
- similar-player output generated

### `memory/decisions.md`
Add:
- feature-vector composition
- normalization rule
- distance and score formulas
- nearest-neighbor selection logic

### `memory/architecture.md`
Add:
- similarity engine location
- dependency on Gold/KPI features rather than raw scraper output

---

## Risks / Watchouts
- very small player pools can produce unstable similarity rankings
- missing KPI rows can create inconsistent vectors if not defaulted carefully
- raw shot counts and minutes can bias results if not normalized first
- name-based joins can collapse different players with the same name
- zero-variance features must not divide by zero during normalization

---

## QA Checklist for Pedant
Pedant should verify:
- normalization handles all-constant feature columns safely
- missing feature values do not crash vector building
- self-comparisons are excluded from neighbor results
- similarity score stays bounded `0..100`
- nearest neighbors are sorted by increasing distance / decreasing similarity
- output artifact is written even for small player pools
- memory documents the similarity logic explicitly

---

## Expected Files for Grunt Phase
Likely changes:
- `app/analysis/similarity.py`
- `app/analysis/similarity_engine.py`
- `app/pipeline/run_pipeline.py`
- possibly `app/pipeline/gold.py` if an extra feature field is needed
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-215.md`

---

## Artifact for Next Role
Grunt should implement a dedicated similarity engine that builds normalized player feature vectors from Gold and KPI outputs, computes Euclidean-distance nearest neighbors, converts distances into bounded similarity scores, and writes a player-level similar-players artifact with the similarity logic documented in memory.
