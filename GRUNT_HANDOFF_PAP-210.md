# GRUNT HANDOFF — PAP-210

## What changed
- Added source-specific FBref scraping modules under `app/scraping/`.
- Implemented FBref parsing for:
  - match metadata
  - player match stat rows
  - player per-90 rows
- Added DB mapping helpers that shape FBref match-level data into the current `matches` and `stats` schema.
- Added FBref-specific raw HTML and parsed JSON storage paths.
- Updated memory with stat mapping decisions, what was built, and next steps.

## Files changed
- `app/config.py`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Files added
- `ARCHITECT_PLAN_PAP-210.md`
- `GRUNT_HANDOFF_PAP-210.md`
- `app/scraping/fbref.py`
- `app/scraping/fbref_parsers.py`
- `app/scraping/fbref_mapping.py`

## Pedant QA checklist
- Verify FBref scraping code stays inside `app/scraping/`.
- Verify parsed output separates `match`, `player_match_stats`, and `player_per_90`.
- Verify raw HTML and parsed JSON are saved to FBref-specific paths.
- Verify DB mapping only targets fields supported by the current `Match` and `Stat` schema.
- Verify per-90 rows are preserved in parsed output and not mapped into match-granular stat columns.
- Verify memory files mention stat mapping decisions and next steps.

## Notes
- The parser removes HTML comment wrappers before table parsing because FBref often wraps tables in comments.
- Full runtime validation still requires installed Playwright browser binaries.
- I did not push a branch or create a PR.
