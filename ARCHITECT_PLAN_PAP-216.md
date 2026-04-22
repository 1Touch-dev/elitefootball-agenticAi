# ARCHITECT PLAN — PAP-216

## Ticket
Implement player valuation model (simplified).

## Requested Build
Value =
- Performance
- Age
- Minutes
- Club Factor
- League Adjustment
- Risk

## Memory to Capture
- model assumptions

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

Additional code inspection completed:
- `app/analysis/kpi_formulas.py`
- `app/analysis/kpi_engine.py`
- `app/analysis/advanced_metrics.py`
- `app/analysis/advanced_metrics_engine.py`
- `app/analysis/similarity_engine.py`
- `app/pipeline/gold.py`
- `app/pipeline/run_pipeline.py`

---

## Current System State
The repo already has a clean downstream analysis pattern:
- Silver tables from parsed source data
- Gold aggregate player features
- KPI engine output in `data/gold/kpi_engine.json`
- advanced metrics output in `data/gold/advanced_metrics.json`
- player similarity output in `data/gold/player_similarity.json`

That means PAP-216 should **not** introduce scraping changes or DB changes.
It should be implemented as another analysis-layer output alongside KPI and similarity.

---

## Architectural Recommendation
Add the valuation model as a dedicated downstream analysis module.

### Keep current boundaries
- scraping stays in `app/scraping/`
- Silver cleaning stays in `app/pipeline/silver.py`
- base Gold aggregates stay in `app/pipeline/gold.py`
- valuation logic belongs in `app/analysis/`
- orchestration remains in `app/pipeline/run_pipeline.py`

### Recommended new modules
Add:
- `app/analysis/valuation.py`
  - pure helper formulas
  - normalization helpers
  - component-score helpers
- `app/analysis/valuation_engine.py`
  - joins input tables
  - builds per-player valuation rows
  - writes output JSON artifact

Integrate via:
- `app/pipeline/run_pipeline.py`

Preferred output path:
- `data/gold/player_valuation.json`

---

## Input Data Recommendation
Use existing downstream artifacts and Silver metadata rather than raw scraper payloads.

### Primary sources
From Gold `player_features`:
- `player_name`
- `minutes`
- `matches`
- `goal_contribution_per_90`
- `discipline_risk_score`
- `shots`

From KPI rows:
- `base_kpi_score`
- `age_adjusted_kpi_score`
- `consistency_score`
- `age`

From advanced metrics rows when available:
- `progression_score`
- `xg_per_90`
- `xa_per_90`

From Silver `players` rows:
- `position`
- `current_club`
- `date_of_birth`
- `nationality`

From Silver `matches` rows if competition names exist:
- `competition`

From Silver `transfers` rows only if club / league context is needed later.

### Important constraint
The MVP valuation engine must work even if advanced metrics or transfer rows are missing.
Use them as optional enrichments, not hard dependencies.

---

## Output Recommendation
Produce one valuation row per player with transparent component scores.

### Recommended output file
- `data/gold/player_valuation.json`

### Recommended output shape
```json
{
  "player_name": "...",
  "position": "...",
  "current_club": "...",
  "valuation_score": 0.0,
  "valuation_tier": "...",
  "components": {
    "performance_score": 0.0,
    "age_score": 0.0,
    "minutes_score": 0.0,
    "club_factor": 0.0,
    "league_adjustment": 0.0,
    "risk_score": 0.0
  },
  "inputs": {
    "age": 0,
    "minutes": 0,
    "base_kpi_score": 0.0,
    "consistency_score": 0.0,
    "discipline_risk_score": 0.0,
    "progression_score": 0.0
  },
  "model_version": "mvp_v1"
}
```

Sort descending by `valuation_score`.

---

## Model Strategy Recommendation
Use a transparent additive score, not a fake market-currency estimate.

### Why this is the right MVP move
The ticket gives a formula in additive terms:
- Performance + Age + Minutes + Club Factor + League Adjustment - Risk

A synthetic `valuation_score` is therefore safer than pretending to infer a real transfer value in euros.
It is:
- explainable
- easy to test
- stable with partial data
- consistent with the repo's current Gold-output pattern

If needed later, the team can map this score into a rough transfer band or euro estimate.

---

## Recommended Formula
Build the final score on a `0..100` scale.

```text
valuation_score = clamp(
    performance_score
  + age_score
  + minutes_score
  + club_factor
  + league_adjustment
  - risk_score,
  0,
  100
)
```

Use simple bounded components so each term is interpretable.

---

## Component Formula Recommendations

### 1. Performance Score
This should carry the most weight.

#### Recommended source priority
1. KPI output
2. advanced metrics enrichment when present
3. fallback to Gold player features if KPI is missing

#### Recommended formula
```text
performance_score = min(
  45,
  (base_kpi_score * 8)
  + (progression_score * 0.12)
)
```

Fallback when `progression_score` is unavailable:
```text
performance_score = min(45, base_kpi_score * 8)
```

Fallback when KPI is missing entirely:
```text
performance_score = min(45, (goal_contribution_per_90 * 18) + (shots / max(matches, 1) * 2))
```

### Why
- preserves KPI as the main performance signal
- allows advanced metrics to modestly improve valuation
- keeps the component capped and explainable

---

### 2. Age Score
This should reward strong ages for current value while still favoring youth upside.

#### Recommended age bands
```text
18-21 => 18
22-24 => 16
25-27 => 13
28-30 => 9
31+   => 5
unknown => 10
```

### Why
- simplified and transparent
- favors prime-young players without exploding value
- avoids a complicated nonlinear curve for MVP

Note: this is a **valuation** age scale, not the KPI multiplier scale. The two should remain distinct.

---

### 3. Minutes Score
This should reward evidence and availability, but not dominate performance.

#### Recommended formula
```text
minutes_score = min(15, (minutes / 900) * 3)
```

Interpretation:
- every 900 minutes (~10 full matches) adds 3 points
- cap at 15

### Why
- rewards sustained usage
- remains small enough that low-quality high-minute players are not overvalued

---

### 4. Club Factor
Because the dataset is narrow, use a simple bounded club-context score.

#### Recommended MVP approach
Use a static lookup by current club name.

Example initial mapping:
```text
idv / independiente del valle => 8
other tracked top-flight clubs => 6
unknown club => 4
reserve / youth context => 3
```

### Implementation note
This should be handled through a helper like:
- normalize club name
- map known club names to scores
- default conservatively when unknown

### Why
- the repo does not yet have a robust external club-strength model
- a static map is easy to document and test
- it can later be replaced with a league/club-strength table

---

### 5. League Adjustment
Keep this deliberately small in the MVP.

#### Recommended approach
Use a competition-name or club-context based lookup.

Example initial mapping:
```text
ecuador serie a / copa libertadores / sudamericana => 6
other senior first-division competitions => 5
unknown senior competition => 4
youth / reserve / unknown low-context => 2
```

#### Fallback rule
If competition is unavailable, derive a neutral default from club context:
```text
league_adjustment = 4
```

### Why
- league quality matters, but the current repo does not yet maintain a rich competition taxonomy
- small bounded values prevent this from overpowering observed performance

---

### 6. Risk Score
Risk should subtract value using existing discipline and consistency signals.

#### Recommended formula
```text
risk_score = min(
  12,
  (discipline_risk_score * 1.5)
  + max(0, (60 - consistency_score) * 0.08)
)
```

Fallback when `consistency_score` is missing:
```text
risk_score = min(12, discipline_risk_score * 1.5)
```

### Why
- yellow/red cards already exist in Gold features
- consistency is already computed by KPI engine
- the cap prevents risk from zeroing out otherwise strong players too aggressively

---

## Data Assumptions to Record in Memory
These assumptions should be documented explicitly:

1. The MVP output is a **synthetic valuation score**, not a real currency estimate.
2. KPI remains the primary performance signal.
3. Advanced metrics enrich valuation when available but are optional.
4. Club and league context use bounded static lookups for now.
5. Name-based joins remain acceptable for MVP until stable IDs exist across the pipeline.
6. Missing optional fields should degrade to conservative defaults, not fail the run.
7. Risk is modeled through discipline plus inconsistency, not injuries or contract status.

---

## Suggested Helper Functions
In `app/analysis/valuation.py`:
- `clamp_score(value: float, low: float = 0.0, high: float = 100.0) -> float`
- `normalize_player_key(value: str | None) -> str`
- `performance_score(...) -> float`
- `age_score(age: int | None) -> float`
- `minutes_score(minutes: int | float | None) -> float`
- `club_factor(club_name: str | None) -> float`
- `league_adjustment(competition_name: str | None, club_name: str | None = None) -> float`
- `risk_score(discipline_risk_score: float | None, consistency_score: float | None) -> float`
- `valuation_tier(score: float) -> str`

In `app/analysis/valuation_engine.py`:
- row joins across Silver / Gold / KPI / advanced metrics
- per-player component assembly
- output writing to `player_valuation.json`

---

## Valuation Tier Recommendation
Add a human-readable tier for downstream UX.

```text
85+ => elite_mvp
70-84.999 => strong_mvp
55-69.999 => solid_mvp
40-54.999 => rotation_mvp
<40 => development_mvp
```

This is optional but strongly recommended because it makes the artifact easier to review.

---

## Pipeline Integration Recommendation
Update `app/pipeline/run_pipeline.py` to call the new valuation engine after KPI and advanced metrics are available.

### Recommended order
1. Bronze
2. Silver
3. Gold
4. KPI
5. advanced metrics
6. similarity
7. valuation

### Reason
Valuation depends on already-derived signals and should remain downstream.

If the current pipeline does not invoke advanced metrics yet, the implementation can either:
- integrate advanced metrics first, then valuation, or
- make valuation tolerate a missing advanced metrics input and only consume it when provided.

Preferred MVP choice:
- call advanced metrics in the pipeline before valuation if that can be done without collateral change

---

## Non-Breaking Constraints
Do not:
- modify scraper structure
- add DB schema changes
- replace KPI or similarity outputs
- depend on external APIs or live market data
- invent currency-denominated transfer values

Do:
- add a new analysis module
- emit a new Gold artifact
- keep formulas transparent and documented
- make defaults conservative when source data is incomplete

---

## QA Checklist for Pedant
Pedant should verify:
- valuation output writes successfully even with sparse input data
- score remains bounded `0..100`
- missing advanced metrics do not crash the engine
- missing club / competition values fall back to defaults
- risk subtracts rather than adds
- rows are sorted descending by valuation score
- tier mapping matches thresholds
- memory explicitly documents model assumptions

---

## Expected Files for Grunt Phase
Likely changes:
- `app/analysis/valuation.py`
- `app/analysis/valuation_engine.py`
- `app/pipeline/run_pipeline.py`
- `tests/test_valuation.py`
- possibly `tests/test_valuation_engine.py`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-216.md`

---

## Artifact for Next Role
Grunt should implement a new downstream valuation engine that computes a transparent `0..100` player valuation score from performance, age, minutes, club context, league context, and risk, writes the result to `data/gold/player_valuation.json`, and documents the model assumptions in memory.
