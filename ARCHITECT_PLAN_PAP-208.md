# ARCHITECT PLAN — PAP-208

## Ticket
Design player + match database schema (MVP).

## Requested Deliverables
Design, for the MVP:
- tables: `players`, `clubs`, `matches`, `stats`
- focus: IDV + 5 clubs
- output: SQL schema + ORM models
- update memory with schema decisions and normalization approach

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The repo already has:
- a Python backend scaffold in `app/`
- a database package in `app/db/`
- `Base` and SQLAlchemy engine/session setup in `app/db/base.py`
- a placeholder player model in `app/db/models.py`
- a memory system that must be read before work and updated after work

### Important architectural constraint
Do **not** break the current package boundaries:
- keep DB concerns in `app/db/`
- keep memory docs in `memory/`
- avoid introducing migrations/framework sprawl in this ticket

---

## High-Level Recommendation
Implement the MVP schema by **evolving** the existing SQLAlchemy model layer, not replacing the database architecture.

### Preferred direction
- replace the placeholder `PlayerProfile` model with a normalized MVP schema
- keep all ORM models in `app/db/models.py` unless Grunt has a strong reason to split them
- add a matching SQL schema artifact in the repo for clarity and future migration reference

Recommended SQL artifact:
- `app/db/schema.sql`

This preserves the current architecture and gives both requested outputs:
- SQL schema
- ORM models

---

## Recommended Normalization Approach
Use a light normalization strategy appropriate for the MVP.

### Core principle
Separate stable entities from event-level data.

Recommended entity boundaries:
- `clubs` = club reference data
- `players` = player reference data
- `matches` = match-level event data
- `stats` = per-player-per-match stat records

This avoids duplication while staying simple.

### Why this fits the MVP
- players can appear in many matches
- clubs can participate in many matches
- stats belong to a specific player in a specific match
- the system only needs enough structure for IDV + 5 clubs, not a full league platform

---

## Recommended Table Design

### 1) `clubs`
Purpose:
- store the small set of tracked clubs
- support player ownership and match participation

Recommended columns:
- `id` primary key
- `name` unique club name
- `short_code` unique short identifier
- `country` nullable
- `is_target` boolean to indicate tracked MVP club set
- `created_at`
- `updated_at`

Notes:
- `is_target` helps mark IDV + the additional tracked clubs
- this is better than hardcoding club lists elsewhere

### 2) `players`
Purpose:
- store canonical player records

Recommended columns:
- `id` primary key
- `club_id` foreign key → `clubs.id`
- `full_name`
- `preferred_name` nullable
- `position`
- `shirt_number` nullable
- `nationality` nullable
- `date_of_birth` nullable
- `source`
- `is_active` boolean
- `created_at`
- `updated_at`

Notes:
- replace the current placeholder model with this richer canonical player entity
- keep source/provenance because scraping is core to the system

### 3) `matches`
Purpose:
- store match metadata for tracked clubs

Recommended columns:
- `id` primary key
- `external_id` nullable unique source identifier
- `competition` nullable
- `season` nullable
- `match_date`
- `home_club_id` foreign key → `clubs.id`
- `away_club_id` foreign key → `clubs.id`
- `home_score` nullable
- `away_score` nullable
- `venue` nullable
- `source`
- `created_at`
- `updated_at`

Notes:
- use two foreign keys to `clubs` for home/away roles
- keep this table match-centric, not player-centric

### 4) `stats`
Purpose:
- store player performance in a specific match

Recommended columns:
- `id` primary key
- `match_id` foreign key → `matches.id`
- `player_id` foreign key → `players.id`
- `club_id` foreign key → `clubs.id`
- `minutes_played` nullable
- `goals` default 0
- `assists` default 0
- `yellow_cards` default 0
- `red_cards` default 0
- `shots` default 0
- `passes_completed` default 0
- `source`
- `created_at`
- `updated_at`

Recommended uniqueness rule:
- unique constraint on (`match_id`, `player_id`)

Why:
- one player should have at most one aggregated stat line per match in the MVP

---

## Relationship Plan
Recommended relationships:
- one `club` → many `players`
- one `club` → many home matches
- one `club` → many away matches
- one `match` → many `stats`
- one `player` → many `stats`

Optional ORM relationships to define:
- `Club.players`
- `Club.home_matches`
- `Club.away_matches`
- `Player.club`
- `Player.stats`
- `Match.home_club`
- `Match.away_club`
- `Match.stats`
- `Stat.player`
- `Stat.match`
- `Stat.club`

---

## SQL Output Recommendation
Grunt should create an explicit SQL file in addition to ORM models.

Recommended file:
- `app/db/schema.sql`

The SQL file should:
- create `clubs`, `players`, `matches`, `stats`
- define foreign keys
- define uniqueness constraints
- use names aligned with ORM models

This makes the schema easy to inspect independently of Python code.

---

## ORM Implementation Recommendation
In `app/db/models.py`:
- replace `PlayerProfile`
- define four ORM models matching the SQL schema
- use SQLAlchemy 2-style mapped columns
- add indexes on common lookup fields where obvious (`club_id`, `match_date`, `full_name`, foreign keys)

Avoid:
- advanced inheritance
- polymorphic tables
- premature optimization
- migrations tooling in this ticket

---

## Compatibility / Non-Breaking Guidance
To avoid breaking the existing architecture:
- preserve `app/db/base.py`
- keep SQLAlchemy as the ORM layer
- keep settings-driven database URL usage intact
- do not restructure the app package unnecessarily
- only expand the DB layer and memory docs in support of this ticket

---

## Recommended Memory Updates During Implementation
Grunt should update memory after implementing the schema.

### `memory/progress.md`
Add:
- schema design completed
- SQL schema added
- ORM models added/replaced
- next steps around migrations/seeding/scraping integration

### `memory/decisions.md`
Add:
- normalization decision: clubs, players, matches, stats are separate entities
- one stat row per player per match for MVP
- focus limited to IDV + 5 clubs

### `memory/architecture.md`
Optionally add:
- DB layer now includes normalized football domain models

---

## Risks / Watchouts
- leaving the old `PlayerProfile` model alongside new tables and creating ambiguity
- mixing club reference data into the players table
- storing repeated player metadata inside match stats
- skipping a uniqueness rule on player/match stats
- over-expanding the schema beyond MVP needs
- adding too many stat columns for a first pass

---

## QA Checklist for Pedant
Pedant should verify:
- all four requested domain tables exist in both SQL and ORM outputs
- schema remains aligned with the current app architecture
- old placeholder player model is replaced or clearly superseded
- foreign keys and uniqueness constraints are sensible
- memory files were updated with schema decisions and normalization approach
- MVP scope remains focused on IDV + 5 clubs

---

## Files Expected to Change in Grunt Phase
Most likely:
- `app/db/models.py`
- `app/db/schema.sql` (new)
- `memory/progress.md`
- `memory/decisions.md`
- optionally `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-208.md`

---

## Artifact for Next Role
Grunt should implement a normalized MVP football schema with `clubs`, `players`, `matches`, and `stats`, add both SQL and SQLAlchemy ORM definitions, preserve the existing backend architecture, and update memory with schema decisions, normalization approach, what was built, and next steps.
