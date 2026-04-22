# ARCHITECT_PLAN_PAP-221 — Implement Risk Model (Injury + Volatility)

## Ticket
PAP-221

## Role
Architect — planning/design only. No application code implemented in this phase.

## Goal
Introduce a transparent MVP risk model covering:
- injury risk
- performance volatility

The implementation must preserve the current architecture, use existing available data, and integrate cleanly with the downstream analysis pipeline.

---

## 1) Current System State

### Existing analysis architecture
The repository already follows a clean downstream-analysis pattern:
- `app/pipeline/gold.py` builds aggregate feature artifacts
- `app/analysis/kpi_engine.py` builds KPI artifact output
- `app/analysis/advanced_metrics_engine.py` builds advanced metrics output
- `app/analysis/similarity_engine.py` builds similarity output
- `app/analysis/valuation_engine.py` builds valuation output
- `app/pipeline/run_pipeline.py` orchestrates all artifact generation

### Existing valuation behavior
Current valuation risk is narrow and embedded inside `app/analysis/valuation.py`:
- `risk_score(discipline_risk_score, consistency_score)`
- this only models discipline and low consistency
- there is no explicit injury-risk artifact
- there is no explicit volatility artifact

### Available data we can safely use now
Without changing scraping or schema boundaries, the model can use:
- `silver.players`
  - `player_name`
  - `date_of_birth`
  - `position`
  - `current_club`
- `silver.player_match_stats`
  - `match_date`
  - `minutes`
  - `goals`
  - `assists`
  - `shots`
  - `yellow_cards`
  - `red_cards`
  - optional advanced columns when present
- `gold.player_features`
  - aggregated minutes / matches / discipline risk
- `gold.kpi_engine`
  - `consistency_score`
  - per-90 derived values

### Important constraint
We do **not** currently have true injury-event data (medical reports, missed matches due to injury, rehab intervals, etc.). So the MVP injury model must be explicitly framed as an **availability-risk proxy**, not a medical predictor.

---

## 2) Design Decision

### Decision summary
Implement PAP-221 as a **dedicated downstream risk-analysis module** that writes a new Gold artifact:
- `data/gold/player_risk.json`

This artifact should then be consumed by valuation as an optional enrichment input.

### Why this is the right fit
This preserves the architecture already established for KPI, similarity, advanced metrics, and valuation:
- no scraper changes
- no DB/schema changes
- no route logic mixed into calculation code
- transparent artifact-backed analysis
- risk becomes independently testable and reusable

### Explicit non-goals for PAP-221
Do **not** in this ticket:
- add live injury scraping
- infer medical diagnoses
- alter database schema
- move analysis logic into API routes
- introduce opaque black-box scoring

---

## 3) Proposed File-Level Changes

### New files
1. `app/analysis/risk.py`
   - pure helper/formula functions
   - no file I/O
   - bounded score helpers and volatility/injury proxy functions

2. `app/analysis/risk_engine.py`
   - builds player-level risk rows from silver/gold/kpi inputs
   - writes `data/gold/player_risk.json`

3. `tests/test_risk.py`
   - unit tests for pure formula helpers

4. `tests/test_risk_engine.py`
   - integration-style tests for artifact row generation

### Existing files to update
1. `app/pipeline/run_pipeline.py`
   - invoke `build_risk_output(...)`
   - pass risk rows into valuation builder

2. `app/analysis/valuation.py`
   - refactor valuation risk composition so it can accept explicit injury + volatility inputs
   - preserve transparent additive scoring

3. `app/analysis/valuation_engine.py`
   - optionally consume risk artifact rows
   - bump model version to reflect the new risk-aware valuation formula
   - include risk artifact inputs in valuation output breakdown

4. `app/api/data_access.py` *(optional but recommended if exposure is desired now)*
   - add `player_risk` artifact loader

5. `app/api/routes.py` *(optional follow-up, not required for core PAP-221)*
   - optionally expose risk payload via `/players?...include=risk` or a dedicated endpoint later

6. `README.md`
   - document the new artifact and any valuation enrichment behavior

---

## 4) Proposed Data Contract for `player_risk.json`

Each row should remain transparent and inspection-friendly.

### Suggested shape
```json
{
  "player_name": "Example Player",
  "position": "Forward",
  "current_club": "Independiente del Valle",
  "risk_score": 41.2,
  "risk_tier": "moderate",
  "components": {
    "injury_risk_score": 28.0,
    "volatility_risk_score": 46.5,
    "discipline_risk_score": 9.0,
    "availability_penalty": 12.0,
    "small_sample_penalty": 4.0
  },
  "inputs": {
    "age": 22,
    "matches": 11,
    "minutes": 744,
    "minutes_per_match": 67.6,
    "max_gap_days": 19,
    "avg_gap_days": 8.2,
    "minutes_cv": 0.31,
    "goal_contribution_p90_cv": 0.58,
    "shots_p90_cv": 0.44,
    "consistency_score": 63.0
  },
  "model_version": "risk_mvp_v1"
}
```

### Contract notes
- `risk_score` should be bounded to `0..100`
- `injury_risk_score` should explicitly mean **availability proxy risk**
- `volatility_risk_score` should reflect unstable match-to-match performance and/or role instability
- component fields should be easy to reason about and debug

---

## 5) Formula Design

## 5.1 Injury risk (availability proxy)
Because true injury labels do not exist, compute a conservative proxy from availability patterns.

### Signals to use
1. **Age pressure**
   - mild increase for older players
   - small/neutral impact for prime-age players

2. **Appearance gap pressure**
   - sort matches by `match_date`
   - compute day gaps between appearances
   - larger unexplained gaps raise availability risk

3. **Minutes stability / abrupt drop-offs**
   - repeated low-minute cameos or sharp minutes decline can indicate reduced availability/fitness/selection instability
   - this should be weighted modestly to avoid overclaiming injury

4. **Small-sample caution**
   - very few matches should not create fake certainty
   - use a bounded penalty or uncertainty uplift

### Recommended output semantics
- name the internal component `injury_risk_score`, but document it as an availability proxy
- keep weighting conservative so valuation is not dominated by a weak proxy

### Recommended helper functions
In `app/analysis/risk.py`:
- `clamp_score(...)`
- `safe_mean(...)`
- `coefficient_of_variation(...)`
- `days_between_appearances(...)`
- `age_risk_component(age)`
- `availability_gap_component(max_gap_days, avg_gap_days)`
- `minutes_instability_component(minutes_series)`
- `small_sample_penalty(match_count)`
- `injury_risk_score(age, gap_days, minutes_series, match_count)`

---

## 5.2 Performance volatility
This should measure how unstable output is from match to match.

### Signals to use
1. **Goal contributions per 90 volatility**
2. **Shots per 90 volatility**
3. **Minutes volatility**
4. **Consistency score inverse** from KPI (optional stabilizer)

### Rationale
- KPI already computes a bounded consistency score
- risk should not duplicate KPI blindly, but it can reuse consistency as a sanity signal
- volatility should primarily come from per-match variability, not only from aggregate KPI

### Recommended helper functions
- `series_per_90(...)`
- `volatility_component(series)` using coefficient of variation or std/mean fallback
- `consistency_penalty(consistency_score)`
- `volatility_risk_score(gc_p90_series, shots_p90_series, minutes_series, consistency_score)`

### Recommended behavior
- if a series lacks enough data, return a conservative default plus small-sample caution
- keep the score bounded and avoid exploding values when mean is near zero
- use floor logic to avoid divide-by-near-zero CV distortions

---

## 5.3 Composite player risk
### Proposed combination
Use a transparent weighted blend:
- injury / availability proxy: **45%**
- volatility risk: **40%**
- discipline risk: **15%**

Then clamp to `0..100`.

### Why these weights
- injury proxy is useful but imperfect, so it should matter without pretending to be medical truth
- volatility is central to this ticket and should be nearly equal weight
- discipline remains relevant but secondary

### Risk tiers
Suggested simple bands:
- `0-24.999` → `low`
- `25-49.999` → `moderate`
- `50-74.999` → `elevated`
- `75+` → `high`

---

## 6) Valuation Integration Plan

### Current issue
Valuation already subtracts `risk_score(...)`, but that score is limited to discipline and low consistency.

### Proposed change
Refactor valuation to consume explicit risk rows when available.

### Recommended integration behavior
In `build_valuation_output(...)`:
- add optional `risk_rows: list[dict[str, Any]] | None = None`
- index risk rows by normalized player name
- if risk row exists:
  - use `risk_row["risk_score"]` as the primary risk input
  - optionally blend with legacy discipline/consistency fallback only when artifact is absent
- if no risk row exists:
  - preserve current fallback behavior for backward compatibility

### Recommended valuation formula change
Current valuation subtracts a small capped risk component.
For PAP-221:
- keep valuation additive and transparent
- convert the 0..100 risk artifact into a bounded deduction sized appropriately for valuation
- recommended deduction: `risk_score * 0.12`, capped at the existing or slightly expanded risk ceiling

### Model versioning
Bump valuation version from:
- `mvp_v1`

to something explicit like:
- `mvp_v2_risk`

---

## 7) Testing Plan

## Unit tests (`tests/test_risk.py`)
Cover:
- clamping and safe numeric helpers
- coefficient-of-variation behavior for empty/zero/low-mean inputs
- age component banding
- appearance-gap component increasing with larger gaps
- small-sample penalty behavior
- volatility score increasing when variance increases

## Engine tests (`tests/test_risk_engine.py`)
Cover:
- artifact generation path ends with `player_risk.json`
- output rows contain `components`, `inputs`, and `model_version`
- higher gap / unstable minutes player scores riskier than stable player
- low-sample player gets bounded caution, not broken output
- missing optional fields degrade gracefully

## Valuation regression updates
Update `tests/test_valuation_engine.py` to verify:
- valuation accepts optional risk rows
- risk-aware valuation decreases score versus no-risk scenario
- fallback still works when risk artifact is absent

---

## 8) Implementation Sequence for Grunt

1. Create `app/analysis/risk.py`
2. Create `app/analysis/risk_engine.py`
3. Add pipeline integration in `app/pipeline/run_pipeline.py`
4. Refactor `app/analysis/valuation_engine.py` to accept optional risk rows
5. Update `app/analysis/valuation.py` risk deduction logic to support risk artifact input
6. Add tests:
   - `tests/test_risk.py`
   - `tests/test_risk_engine.py`
   - valuation regression updates
7. Run targeted test suite
8. If stable, update README with new artifact documentation

---

## 9) Implementation Notes / Guardrails

- Do not claim medical truth; document injury risk as an availability proxy.
- Do not add schema or scraper dependencies for this ticket.
- Keep formulas transparent and bounded.
- Reuse existing name-normalization patterns.
- Preserve current pipeline behavior when risk artifact is missing.
- Keep artifact rows sorted by descending `risk_score` for operator usability.

---

## 10) Acceptance Criteria

PAP-221 should be considered complete when:
- a dedicated risk artifact is generated at `data/gold/player_risk.json`
- the artifact contains explicit injury proxy and volatility components
- valuation can consume the risk artifact without breaking existing fallback behavior
- tests cover formulas, engine output, and valuation integration
- documentation clearly states that injury risk is a proxy derived from availability patterns, not true injury records

---

## 11) Suggested Handoff Summary

This ticket should be implemented as a new downstream analysis engine, not as a schema or scraping task. The safest architecture is:
- new `risk.py` helpers
- new `risk_engine.py` artifact builder
- pipeline integration
- optional valuation enrichment
- comprehensive tests

That keeps the system aligned with its existing KPI / similarity / valuation design and avoids pretending we have data we do not actually have.
