# PAP-239 — Scraping Pipeline Audit and Root-Cause Report

## Ticket
PAP-239

## Role
Grunt — implementation/audit artifact phase. No production code changes were made in this phase.

## Scope Reviewed
This audit traced the current pipeline across:
- scraper trigger/orchestration
- page fetch/browser layer
- source-specific parsing
- raw + parsed artifact persistence
- Silver/Gold pipeline ingestion
- API consumption
- dashboard consumption

---

## 1) End-to-End Lifecycle Today

### 1.1 Trigger layer
Primary orchestration entrypoints:
- `app/agents/orchestrator.py`
- `app/agents/scraper_agent.py`
- `app/api/task_routes.py`
- `app/tasks/jobs.py` / `app/tasks/service.py` (async path wrapper)

Observed flow:
1. A task such as `scrape_players` or `full_refresh` is routed to the scraper agent.
2. `app/agents/scraper_agent.py` always builds a scrape plan.
3. It only performs a real scrape when `payload["url"]` is supplied.
4. If no URL is supplied, the scraper step ends after returning plan metadata.

### 1.2 Fetch/browser layer
Primary module:
- `app/scraping/browser.py`

Observed flow:
1. `fetch_page_html(...)` requires `playwright.sync_api.sync_playwright`.
2. Chromium is launched headless.
3. Navigation uses `page.goto(url, wait_until="domcontentloaded")`.
4. The page then waits for `networkidle` and sleeps for the configured scrape delay.
5. Final rendered HTML is returned via `page.content()`.

### 1.3 Source-specific scrape layer
Primary modules:
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `app/scraping/players.py`

Observed flow:
- Transfermarkt scraper fetches one supplied player URL, writes raw HTML, parses profile + transfers, and writes parsed JSON.
- FBref scraper fetches one supplied URL, writes raw HTML, parses match + player stats + per-90 sections, and writes parsed JSON.
- Only the Transfermarkt player scraper is currently wired into the orchestrated scraper agent.
- FBref scraping exists as a module but is not part of the orchestrated refresh path.

### 1.4 Parsing layer
Primary modules:
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`

Observed flow:
- Transfermarkt parsing is regex/label based.
- FBref parsing uses a lightweight HTML table parser with comment stripping.
- Both parsers consume saved/fetched HTML and emit structured dict/list payloads.

### 1.5 Storage layer
Primary module:
- `app/scraping/storage.py`

Observed flow:
- raw HTML goes to:
  - `data/raw/transfermarkt/`
  - `data/raw/fbref/`
- parsed JSON goes to:
  - `data/parsed/transfermarkt/`
  - `data/parsed/fbref/`

### 1.6 Pipeline ingestion
Primary modules:
- `app/pipeline/bronze.py`
- `app/pipeline/silver.py`
- `app/pipeline/gold.py`
- `app/pipeline/run_pipeline.py`

Observed flow:
- Bronze indexes raw/parsed artifacts from the source directories.
- Silver loads parsed JSON files only.
- Gold/analysis derive downstream artifacts from Silver.
- No live re-fetch occurs inside `run_pipeline()`.

### 1.7 API + dashboard consumption
Primary modules:
- `app/api/data_access.py`
- `app/api/routes.py`
- `dashboard/api_client.py`

Observed flow:
- API reads only generated Silver/Gold JSON artifacts.
- Dashboard reads only backend API responses.
- Dashboard does not read scraper output directly.
- If scrape artifacts are missing/empty, Silver/Gold stay empty and the dashboard has nothing useful to display.

---

## 2) Concrete Root Causes Identified

## Root Cause 1 — The orchestrated refresh path does not actually scrape any pages by default

### Evidence
- `app/agents/scraper_agent.py` only calls `scrape_idv_player_from_transfermarkt(...)` when `payload.get("url")` is present.
- `app/agents/orchestrator.py` routes `full_refresh` through the scraper agent but does not inject any scrape target URLs.
- `app/scraping/players.py:get_idv_player_scrape_plan()` returns descriptive scope metadata only; it does not provide concrete URLs.

### Impact
- `full_refresh` can complete successfully without making a single network request.
- The system then proceeds to Bronze/Silver/Gold generation against empty source directories.
- This produces empty downstream artifacts while appearing structurally healthy.

### Severity
Critical.

---

## Root Cause 2 — The runtime environment currently cannot execute Playwright scraping

### Evidence
Audit command output:
- `python3 -c 'from playwright.sync_api import sync_playwright'` fails with `ModuleNotFoundError: No module named 'playwright'`.
- Direct invocation of `fetch_page_html(...)` raises `PlaywrightUnavailableError: Playwright is not installed. Install dependencies and run playwright install before scraping.`

### Impact
- Even if a URL is supplied, the fetch layer fails immediately in the current environment.
- No raw HTML or parsed payloads can be produced.

### Severity
Critical.

---

## Root Cause 3 — The primary orchestrated scraper only covers Transfermarkt, while downstream analytics/dashboard depend heavily on FBref-derived match stats

### Evidence
- `app/agents/scraper_agent.py` imports and uses only `scrape_idv_player_from_transfermarkt(...)`.
- `app/scraping/fbref.py` exists but is not called by the scraper agent or orchestrated `full_refresh` route.
- `app/pipeline/gold.py`, KPI, similarity, valuation, and risk engines all depend primarily on `silver["player_match_stats"]` and related match-stat artifacts, which are produced from FBref payloads.

### Impact
- Even a successful Transfermarkt scrape would populate player profiles/transfers only.
- Match-stat-dependent Silver/Gold outputs remain empty or near-empty.
- Compare/value/dashboard views cannot become meaningfully populated from Transfermarkt-only scraping.

### Severity
Critical.

---

## Root Cause 4 — No concrete IDV target inventory is configured in code for either source

### Evidence
- No maintained list of IDV player profile URLs exists in `app/scraping/`, `app/config.py`, or agent payload defaults.
- Grep across the repo shows source references but no canonical scrape target registry.

### Impact
- Operators must manually pass URLs one at a time.
- The system has no stable way to perform a repeatable team scrape.
- `full_refresh` has no source of truth for what it should fetch.

### Severity
High.

---

## Root Cause 5 — The current Transfermarkt parser is highly brittle and may silently return partial/empty fields on markup changes

### Evidence
Transfermarkt field extraction relies on:
- `extract_labeled_value(html, "Name in home country")`
- `extract_labeled_value(html, "Position")`
- `extract_labeled_value(html, "Date of birth")`
- `extract_labeled_value(html, "Citizenship")`
- `extract_labeled_value(html, "Current club")`
- `extract_labeled_value(html, "Market value")`
- transfer history parsed by broad `<tr>` regex scanning with token heuristics

### Impact
- Minor label/markup changes can yield empty or incorrect parsed output.
- There is no validation/error flag when required profile fields come back empty.
- This can create false-success scrape artifacts.

### Severity
High.

---

## Root Cause 6 — The fetch layer uses generic JS-render wait logic but lacks source-aware readiness checks and anti-bot diagnostics

### Evidence
`app/scraping/browser.py` currently does only:
- `goto(..., wait_until="domcontentloaded")`
- `wait_for_load_state("networkidle")`
- static sleep delay
- `page.content()`

Missing capabilities:
- target selector readiness checks
- screenshot/error artifact capture on failure
- response status inspection
- anti-bot/challenge detection
- login-wall detection
- timeout classification

### Impact
- The audit cannot currently distinguish among:
  - page loaded correctly
  - challenge page returned
  - JS rendered partial shell only
  - selector never appeared
  - timeout occurred before useful content loaded
- Failures collapse into generic exceptions or empty downstream parsing.

### Severity
High.

---

## Root Cause 7 — There is no DB ingestion path in the active pipeline, despite DB models existing

### Evidence
- `app/db/` contains models/base/schema.
- Pipeline and API read/write JSON artifacts only.
- Grep across `app/` shows no active DB insert/commit flow for scraper outputs.

### Impact
- Scraped data never reaches the normalized database layer.
- The current storage flow ends at JSON artifacts.
- This is not the cause of “no scraping,” but it is a confirmed persistence gap in the advertised end-to-end architecture.

### Severity
Medium.

---

## 3) Target URLs and Selectors Currently Used

## Transfermarkt
### Target URLs
- No hard-coded or configured target inventory found.
- Expected runtime input: one explicit player URL supplied to `scrape_transfermarkt_player(url=...)`.

### Field selectors / extraction logic
- title / JSON-LD / `og:title`
- label-based text extraction for:
  - `Name in home country`
  - `Position`
  - `Date of birth`
  - `Citizenship`
  - `Current club`
  - `Market value`
- transfer history inferred from generic `<tr>` rows containing terms like:
  - `season`
  - `club`
  - `loan`
  - `transfer`
  - `joined`

## FBref
### Target URLs
- No hard-coded or configured target inventory found.
- Expected runtime input: one explicit FBref page URL supplied to `scrape_fbref_page(url=...)`.

### Field selectors / extraction logic
- match title parsing from `<title>`
- match date from `<time datetime="...">`
- table parsing from full HTML after comment removal
- table row/cell parsing via `data-stat` attributes
- player match-stat tables selected when table id contains:
  - `stats`
  - `summary`
- per-90 rows selected when either:
  - keys end with `_per90` / `per90`
  - table id contains `per_90`

---

## 4) Request/Fetch Verification

## What was verified successfully
- The code is designed for JavaScript-rendered page capture via Playwright.
- The browser layer explicitly assumes JS rendering is required or at least supported.
- The pipeline can execute end-to-end against local artifact directories.

## What failed concretely
- The current environment does not have Playwright importable.
- A direct call to the fetch layer raises `PlaywrightUnavailableError`.
- No raw source directories currently exist under `data/raw/...` or `data/parsed/...`.
- `data/bronze/manifest.json` shows `artifact_count: 0`.
- Running the local pipeline yields zero rows in Silver and Gold outputs.

## Result classification
- Current system behavior is **empty data**, not a healthy scrape.
- The emptiness is caused by upstream non-execution plus missing runtime dependency, not by a healthy fetch returning legitimate no-result pages.

---

## 5) JS Rendering / Anti-Bot / Timeout / Login / Rate-Limit Assessment

## JavaScript rendering
- Yes, the code assumes rendered-page capture via Playwright.
- This is appropriate for modern Transfermarkt/FBref flows, but it is not enough by itself.

## Anti-bot/challenge handling
- No explicit anti-bot detection is implemented.
- No challenge-page fingerprinting exists.
- No retry/backoff or browser-context tuning exists beyond serialized delay.

## Timeout handling
- A generic page timeout exists through `page.set_default_timeout(...)`.
- Timeout failures are not classified or persisted with diagnostic artifacts.

## Login handling
- No login/session/auth flow exists.
- If a source requires auth or region gating, the scraper will not handle it.

## Rate-limit handling
- There is a fixed delay and serialized scraping guidance.
- There is no response-based rate-limit detection, retry-after handling, or throttling state.

## Audit conclusion on blocking class
Most concrete currently verified blockers are:
1. scraping is often never triggered
2. Playwright is unavailable in the present runtime
3. even after that, source-specific failure diagnosis would still be weak because anti-bot/selector readiness diagnostics are missing

---

## 6) Scrape Output Handoff Trace

### Trigger → scraper
- `app/agents/orchestrator.py`
- `app/agents/scraper_agent.py`

### scraper → browser fetch
- `app/scraping/players.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/browser.py`

### browser fetch → raw artifact
- `app/scraping/storage.py:save_raw_html(...)`

### browser fetch → parser
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`

### parser → parsed artifact
- `app/scraping/storage.py:save_parsed_payload(...)`

### parsed artifact → Bronze
- `app/pipeline/bronze.py`

### parsed artifact → Silver
- `app/pipeline/silver.py`

### Silver → Gold + analysis
- `app/pipeline/gold.py`
- `app/analysis/kpi_engine.py`
- `app/analysis/advanced_metrics_engine.py`
- `app/analysis/risk_engine.py`
- `app/analysis/similarity_engine.py`
- `app/analysis/valuation_engine.py`

### Gold/Silver → API
- `app/api/data_access.py`
- `app/api/routes.py`

### API → dashboard
- `dashboard/api_client.py`
- Streamlit pages under `dashboard/pages/`

---

## 7) Confirmed Failure Points by Stage

1. **Trigger/orchestration failure**
   - `full_refresh` does not include any default scrape targets.
   - Result: no actual scraping occurs.

2. **Runtime dependency failure**
   - Playwright is unavailable in the current environment.
   - Result: fetch cannot begin even when URLs are supplied.

3. **Source coverage failure**
   - Scraper agent only executes Transfermarkt scraping.
   - Result: FBref-dependent match-stat pipeline remains empty.

4. **Target inventory failure**
   - No configured IDV URL list exists.
   - Result: scraping is not repeatable or automatable.

5. **Parser fragility failure**
   - Transfermarkt selectors are regex/label based with no validation.
   - Result: partial or empty parsed data can appear successful.

6. **Observability failure**
   - No fetch diagnostics, response-status capture, screenshot capture, or challenge detection.
   - Result: root causes remain opaque during live scrape failures.

7. **Persistence architecture gap**
   - DB layer exists but is not connected to ingestion.
   - Result: end-to-end architecture stops at JSON artifacts.

---

## 8) Affected Files / Modules

## Trigger / orchestration
- `app/agents/orchestrator.py`
- `app/agents/scraper_agent.py`
- `app/agents/types.py`
- `app/api/task_routes.py`
- `app/tasks/jobs.py`
- `app/tasks/service.py`

## Scraping / fetch
- `app/scraping/browser.py`
- `app/scraping/players.py`
- `app/scraping/transfermarkt.py`
- `app/scraping/fbref.py`
- `app/scraping/parsers.py`
- `app/scraping/fbref_parsers.py`
- `app/scraping/storage.py`

## Pipeline / artifact consumption
- `app/pipeline/bronze.py`
- `app/pipeline/silver.py`
- `app/pipeline/gold.py`
- `app/pipeline/run_pipeline.py`

## API / dashboard
- `app/api/data_access.py`
- `app/api/routes.py`
- `dashboard/api_client.py`
- `dashboard/pages/1_Player.py`
- `dashboard/pages/2_Compare.py`

## DB layer gap
- `app/db/base.py`
- `app/db/models.py`
- `app/db/schema.sql`

---

## 9) Root Cause Summary

The website is not successfully scraping data because the system currently fails before meaningful extraction begins:

1. the orchestrated refresh path usually does not trigger real scraping at all because no target URLs are injected
2. when scraping is explicitly attempted, the runtime currently lacks Playwright, so page fetch fails immediately
3. even if Transfermarkt scraping succeeds, the dashboard/analytics path still lacks FBref ingestion, which is required for match-stat-driven outputs
4. the parser/fetch layers lack diagnostics and validation, so future live failures would still be difficult to classify

In short: **the primary failure is structural non-execution plus missing runtime dependency, with additional pipeline coverage gaps behind it.**

---

## 10) Recommended Fix Order

### Fix 1 — Add a concrete IDV scrape target registry and wire it into orchestrated refresh
Why first:
- without targets, the scraper agent can report success while doing nothing

Expected implementation shape:
- add a source-aware target inventory for IDV players/matches
- have `full_refresh` iterate those targets explicitly
- emit per-target result metadata

### Fix 2 — Make the scraping runtime bootstrappable and fail fast with environment checks
Why second:
- current runtime cannot scrape because Playwright is missing

Expected implementation shape:
- environment preflight for Playwright import + browser install
- clearer startup/status surface for scrape readiness

### Fix 3 — Wire FBref scraping into the orchestrated refresh path
Why third:
- downstream Silver/Gold/dashboard value depends on match stats

Expected implementation shape:
- add FBref task execution to scraper workflow
- preserve current source-specific boundaries

### Fix 4 — Add source-aware readiness checks and scrape diagnostics
Why fourth:
- once execution is happening, next blocker will be live-page classification

Expected implementation shape:
- selector presence checks
- response status capture
- timeout classification
- screenshot/raw failure artifact capture
- anti-bot/challenge fingerprints

### Fix 5 — Harden parsers with required-field validation and partial-failure reporting
Why fifth:
- prevents silent empty-success artifacts

### Fix 6 — Add DB ingestion only after scraper + artifact pipeline is proven non-empty
Why sixth:
- DB ingestion should not be built on top of a still-empty scrape layer

---

## 11) Next Recommended Issue

**Recommended next issue:**
`PAP-240 - Wire Concrete IDV Scrape Targets Into full_refresh and Add Scrape Runtime Preflight`

Suggested scope:
- add a maintained IDV source target registry
- make `full_refresh` execute real scrape targets
- add Playwright/runtime readiness checks
- fail with explicit scrape diagnostics instead of silent empty refreshes

---

## 12) Files Changed In This Phase

Documentation / memory only:
- `PAP-239_SCRAPING_AUDIT.md`
- `GRUNT_HANDOFF_PAP-239.md`
- `memory/progress.md`
- `memory/decisions.md`
