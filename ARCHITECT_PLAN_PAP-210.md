# ARCHITECT PLAN — PAP-210

## Ticket
Build FBref scraper (match + player stats).

## Requested Deliverables
Scrape:
- per 90 stats
- match stats

Map outputs to the existing DB schema.

Memory must be updated with:
- stat mapping decisions

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo already contains:
- normalized DB models for `clubs`, `players`, `matches`, and `stats`
- a Playwright-based Transfermarkt scraping subsystem under `app/scraping/`
- raw HTML and parsed JSON persistence patterns for scraping outputs

Relevant DB constraints already in place:
- `Match` supports competition, season, match date, home/away clubs, scores, venue, and source
- `Stat` supports one row per `(match_id, player_id)` and stores MVP-safe aggregated match stats
- current `Stat` fields are limited to:
  - `minutes_played`
  - `goals`
  - `assists`
  - `yellow_cards`
  - `red_cards`
  - `shots`
  - `passes_completed`

This means FBref scraping must be planned carefully so it maps cleanly to the current schema without breaking architecture.

---

## High-Level Recommendation
Implement FBref scraping as a sibling source-specific pipeline inside `app/scraping/`, not as an extension of the Transfermarkt parser.

### Preferred direction
Add FBref-specific scraping modules that reuse the same architectural pattern:
- source fetch
- raw HTML persistence
- parsing helpers
- structured output
- DB mapping helpers

This avoids mixing source-specific parsing logic and preserves clear boundaries.

---

## Recommended File / Module Plan
Suggested additions:
- `app/scraping/fbref.py`
  - source-specific orchestration for FBref pages
- `app/scraping/fbref_parsers.py`
  - extraction/parsing logic for match and player stat tables
- `app/scraping/fbref_mapping.py`
  - mapping helpers from parsed FBref payloads into the existing DB schema shape

Existing reusable modules that should be reused rather than duplicated:
- `app/scraping/storage.py`
- `app/scraping/browser.py` if Playwright remains the chosen fetch strategy for dynamic content

If FBref pages are fetchable with plain requests later, that can be optimized in a future ticket, but for now the implementation should keep the current scraping architecture consistent.

---

## Scraping Scope Recommendation
Grunt should implement two distinct FBref parsing flows:

### 1. Match metadata + match-level stat scraping
Target output should capture:
- match identity/source URL
- competition
- season
- match date
- home club
- away club
- final score if available
- venue if available
- per-player match stat lines for tracked players

### 2. Per-90 player stat scraping
Target output should capture player season-level per-90 metrics from FBref, but this should **not** be forced directly into the current `stats` table.

Reason:
- the current `stats` table is match-granular
- per-90 stats are season/profile aggregates, not single-match rows

So for MVP planning, per-90 output should be scraped and stored as parsed data, while DB mapping should only include fields that cleanly fit current tables.

---

## Critical Mapping Decision
This ticket explicitly asks to map to the DB schema, so the plan must distinguish what maps now versus what stays as parsed output.

### Safe direct DB mappings
#### FBref match page → `matches`
Map these fields where available:
- `competition` → `Match.competition`
- `season` → `Match.season`
- `match_date` → `Match.match_date`
- `home_club` → lookup/create `Club`, then `Match.home_club_id`
- `away_club` → lookup/create `Club`, then `Match.away_club_id`
- `home_score` → `Match.home_score`
- `away_score` → `Match.away_score`
- `venue` → `Match.venue`
- source marker → `Match.source = "fbref"`
- external identifier if derivable from URL → `Match.external_id`

#### FBref player match line → `stats`
Map these fields where available:
- player lookup → `Stat.player_id`
- club lookup → `Stat.club_id`
- match lookup → `Stat.match_id`
- minutes → `Stat.minutes_played`
- goals → `Stat.goals`
- assists → `Stat.assists`
- yellow cards → `Stat.yellow_cards`
- red cards → `Stat.red_cards`
- shots → `Stat.shots`
- completed passes → `Stat.passes_completed`
- source marker → `Stat.source = "fbref"`

### Parsed-only for now
Per-90 values should remain in parsed JSON output unless a later ticket expands the DB schema.

Examples of parsed-only values for now:
- shots per 90
- assists per 90
- expected goals per 90
- progressive passes per 90
- other season aggregate metrics not tied to one match row

---

## Stat Mapping Decisions for Memory
These should be explicitly recorded during implementation.

Recommended decisions:
- FBref match-level stats map into `matches` and `stats` only when they are match-granular.
- FBref per-90 stats are stored in parsed outputs but not forced into the current `stats` table.
- The current schema remains authoritative; scraper output should adapt to it rather than silently overloading columns.
- Source provenance should be set to `fbref` on DB-bound match/stat rows.

---

## Parsing Structure Recommendation
Use separate parsed payload sections.

Recommended top-level structure:
```json
{
  "match": { ... },
  "player_match_stats": [ ... ],
  "player_per_90": [ ... ]
}
```

### Why this structure
- separates match-granular data from season-rate data
- makes DB mapping explicit and safe
- preserves richer scraped data for future schema expansion

---

## Storage Recommendation
Reuse the current raw/parsed storage approach with FBref-specific paths.

Suggested paths:
- raw HTML: `data/raw/fbref/`
- parsed JSON: `data/parsed/fbref/`

Recommended naming:
- based on match slug or FBref identifier from URL

---

## Fetch Strategy Recommendation
No special new browser strategy is required at planning level.

Preferred implementation behavior:
- reuse existing browser helper patterns where practical
- stay conservative with fetch cadence
- preserve raw HTML on every successful fetch
- fail softly when optional stat columns are missing

---

## Non-Breaking Architecture Guidance
Do not break the existing architecture.

Specifically:
- keep FBref code inside `app/scraping/`
- do not modify API routes just to support scraping
- do not force schema expansion in this ticket unless absolutely necessary
- do not merge FBref parsing logic into Transfermarkt files

---

## Recommended Memory Updates During Implementation
### `memory/progress.md`
Add:
- FBref scraper implemented for match metadata and player stats
- parsed per-90 outputs retained for future schema expansion
- mapping helpers added for DB-safe fields

### `memory/decisions.md`
Add:
- stat mapping decisions
- match-granular vs per-90 storage decision
- source provenance decision for FBref-mapped rows

### `memory/architecture.md`
Add:
- FBref scraping path mirrors the source-specific scraper pattern
- mapping helpers bridge parsed output to DB-safe structures

---

## Risks / Watchouts
- forcing per-90 values into the match-granular `stats` table
- mixing season aggregates with single-match rows
- tightly coupling parsing directly to DB writes
- assuming every FBref page exposes the same tables/column names
- overextending schema changes during a scraper ticket

---

## QA Checklist for Pedant
Pedant should verify:
- FBref scraping code stays in `app/scraping/`
- raw HTML + parsed outputs exist for FBref
- parsed output separates `match`, `player_match_stats`, and `player_per_90`
- DB mapping only targets fields supported by current `Match` and `Stat` models
- per-90 stats are not incorrectly written into the current `stats` table shape
- memory includes explicit stat mapping decisions

---

## Files Expected to Change in Grunt Phase
Most likely:
- `app/scraping/fbref.py`
- `app/scraping/fbref_parsers.py`
- `app/scraping/fbref_mapping.py`
- possibly `app/scraping/players.py` or a new match-focused entrypoint if needed
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-210.md`

---

## Artifact for Next Role
Grunt should implement a source-specific FBref scraping flow that captures match metadata, per-player match stats, and per-90 player metrics; persists raw HTML and parsed JSON separately; maps only match-safe fields into the current DB schema shape; and updates memory with explicit stat mapping decisions and next steps.
