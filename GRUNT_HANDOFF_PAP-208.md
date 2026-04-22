# GRUNT HANDOFF — PAP-208

## What changed
- Replaced the placeholder player model with normalized SQLAlchemy ORM models for:
  - `clubs`
  - `players`
  - `matches`
  - `stats`
- Added a matching SQL schema file at `app/db/schema.sql`.
- Preserved the existing database package structure in `app/db/`.
- Updated memory with what was built, schema decisions, normalization approach, and next steps.

## Files changed
- `app/db/models.py`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Files added
- `ARCHITECT_PLAN_PAP-208.md`
- `GRUNT_HANDOFF_PAP-208.md`
- `app/db/schema.sql`

## Pedant QA checklist
- Verify the ORM defines `Club`, `Player`, `Match`, and `Stat`.
- Verify `app/db/schema.sql` contains all four required tables.
- Verify `stats` enforces one row per player per match.
- Verify home/away club foreign keys are wired correctly in `matches`.
- Verify memory files mention schema decisions and normalization approach.
- Verify the change did not break the existing `app/db/base.py` architecture.

## Notes
- Scope remains MVP-level and focused on IDV + 5 clubs.
- The schema is normalized but intentionally modest.
- I did not push a branch or create a PR.
