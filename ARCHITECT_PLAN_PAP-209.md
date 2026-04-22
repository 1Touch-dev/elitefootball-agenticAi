# ARCHITECT PLAN — PAP-209

## Ticket
Build Transfermarkt scraper (players + transfers).

## Requested Deliverables
Scrape and support storage for:
- player profiles
- transfer history
- raw HTML + parsed data

Tech requirement:
- Playwright

Memory must be updated with:
- scraping strategy
- rate limits
- parsing structure

---

## Memory Review Completed
Reviewed before planning:
- `memory/project_context.md`
- `memory/architecture.md`
- `memory/progress.md`
- `memory/decisions.md`

## Current System State
The current repo already has:
- backend scaffold under `app/`
- scraping package under `app/scraping/`
- database schema/models for clubs, players, matches, and stats
- no real scraping implementation yet
- no Playwright dependency yet
- only a placeholder scrape-plan function in `app/scraping/players.py`

### Architectural constraint
Do **not** break the current structure:
- keep scraping logic in `app/scraping/`
- keep DB concerns in `app/db/`
- keep memory updates in `memory/`
- do not entangle scraping implementation directly with API routes in this ticket

---

## High-Level Recommendation
Implement this as a scraping subsystem expansion rather than a one-file scraper.

### Preferred direction
Preserve the existing package boundaries and add focused modules for:
- Playwright browser/session management
- player profile scraping
- transfer history scraping
- raw HTML persistence
- parsed payload shaping

This keeps the scraper testable and makes future enrichment work safer.

---

## Recommended File / Module Plan
Grunt should extend `app/scraping/` with a small but clear structure.

Suggested additions:
- `app/scraping/browser.py`
  - Playwright bootstrap and browser/page helpers
- `app/scraping/transfermarkt.py`
  - source-specific scraping orchestration
- `app/scraping/parsers.py`
  - DOM/text extraction helpers and structured parsing
- `app/scraping/storage.py`
  - save raw HTML and parsed JSON payloads to disk

Existing file to update:
- `app/scraping/players.py`
  - either delegate to the new source-specific scraper or remain as a high-level scraping entrypoint

Support path recommended for raw outputs:
- `data/raw/transfermarkt/`
- `data/parsed/transfermarkt/`

This is consistent with the requirement to store both raw HTML and parsed data while not forcing DB persistence in the same ticket.

---

## Scraping Strategy Recommendation
Memory must record the strategy, and implementation should follow it.

### Strategy
Use Playwright for deterministic page fetches and parsing-friendly HTML capture.

Recommended flow:
1. open a Playwright browser/session
2. request a Transfermarkt player page
3. wait for stable page content
4. capture the full raw HTML
5. parse profile data into a structured dictionary
6. parse transfer history into a structured list
7. store raw HTML to disk
8. store parsed data to disk as JSON or equivalent structured output

### Why this works
- Playwright handles dynamic rendering better than plain requests
- raw HTML capture supports debugging and parser iteration
- parsed output supports later DB ingestion without tightly coupling scraping to persistence right now

---

## Parsing Structure Recommendation
The parser should separate profile parsing from transfer parsing.

### Player profile output shape
Recommended fields:
- `source`
- `source_url`
- `scraped_at`
- `player_name`
- `preferred_name` if available
- `position`
- `date_of_birth` if available
- `nationality` or list of nationalities
- `current_club`
- `market_value` if available

### Transfer history output shape
Recommended fields per entry:
- `season`
- `date`
- `from_club`
- `to_club`
- `market_value`
- `fee`
- `source_url`

### Combined parsed output shape
Recommended top-level structure:
```json
{
  "profile": { ... },
  "transfers": [ ... ]
}
```

This makes downstream ingestion and validation easier.

---

## Storage Recommendation
Store both raw HTML and parsed payloads to disk.

### Raw storage
Recommended naming convention:
- `data/raw/transfermarkt/<player-slug>.html`

### Parsed storage
Recommended naming convention:
- `data/parsed/transfermarkt/<player-slug>.json`

### Reasoning
- raw HTML is essential for parser debugging and replay
- parsed JSON is a stable intermediate format before DB ingestion
- this preserves the current architecture by not overloading `app/db/` with crawler-specific artifacts

---

## Rate Limit / Reliability Recommendation
Memory must capture rate-limit behavior. The implementation should stay conservative.

Recommended rules:
- serialize requests by default
- add a configurable delay between page fetches
- prefer one browser context/session reuse instead of repeated relaunches
- fail gracefully when required selectors are missing
- preserve raw HTML even on partial parse success where possible

Suggested delay baseline:
- 2–5 seconds between pages for MVP

Suggested configuration knobs:
- headless on/off
- timeout
- delay_seconds
- output directories

Avoid:
- parallel scraping bursts
- aggressive retry loops
- hidden scraping complexity with unclear throttling behavior

---

## Database Integration Recommendation
Do not force full DB ingestion in this ticket unless Grunt can do so safely with minimal extra work.

Primary requested outputs are:
- scraper implementation
- raw HTML storage
- parsed data storage

If Grunt adds any DB integration, it should be optional and isolated.

---

## Playwright Integration Recommendation
The project currently lacks Playwright in `requirements.txt`.

Recommended implementation updates:
- add `playwright` to `requirements.txt`
- optionally document that browser binaries need installation separately

If a simple CLI entrypoint is added later, it should not be required for this ticket.

---

## Compatibility / Non-Breaking Guidance
To preserve architecture:
- do not restructure `app/`
- do not move DB models
- do not replace the placeholder scraping scope with coupled route logic
- keep scraping as a service/module concern
- update memory to reflect scraping strategy and next steps

---

## Recommended Memory Updates During Implementation
Grunt should update memory after implementing the scraper.

### `memory/progress.md`
Add:
- Transfermarkt scraper scaffold/implementation completed
- raw HTML storage added
- parsed data storage added
- next steps around DB ingestion/testing

### `memory/decisions.md`
Add:
- Playwright chosen for source interaction
- raw HTML + parsed JSON both preserved
- conservative rate limiting adopted

### `memory/architecture.md`
Add:
- scraping pipeline boundaries
- parsing/storage responsibilities

---

## Risks / Watchouts
- mixing scraping, parsing, and storage into a single hard-to-test file
- skipping raw HTML persistence and losing debugging traceability
- assuming selectors are stable without fallback handling
- over-scraping too quickly and triggering rate limits
- tightly coupling Transfermarkt parsing to DB writes prematurely

---

## QA Checklist for Pedant
Pedant should verify:
- Playwright dependency was added
- scraping modules remain inside `app/scraping/`
- implementation supports both player profile and transfer history scraping
- raw HTML storage exists
- parsed data storage exists
- memory reflects scraping strategy, rate limits, and parsing structure
- architecture boundaries remain intact

---

## Files Expected to Change in Grunt Phase
Most likely:
- `requirements.txt`
- `app/scraping/players.py`
- one or more new files under `app/scraping/`
- `memory/progress.md`
- `memory/decisions.md`
- `memory/architecture.md`
- `GRUNT_HANDOFF_PAP-209.md`

---

## Artifact for Next Role
Grunt should implement a Playwright-based Transfermarkt scraping subsystem that captures player profile data and transfer history, stores raw HTML and parsed outputs separately, preserves the current architecture, and updates memory with scraping strategy, rate-limit decisions, parsing structure, what was built, and next steps.
