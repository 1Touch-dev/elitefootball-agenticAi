# GRUNT_HANDOFF_PAP-239 — Scraping Audit Handoff for Pedant

## Ticket
PAP-239

## What I changed
No production code changes.

Created/updated documentation artifacts only:
- `PAP-239_SCRAPING_AUDIT.md`
- `memory/progress.md`
- `memory/decisions.md`
- `GRUNT_HANDOFF_PAP-239.md`

## What was verified concretely
1. `full_refresh` does not perform a real scrape unless a URL is manually passed into the scraper payload.
2. there is no canonical IDV target URL inventory in the repo.
3. the current runtime cannot import Playwright.
4. direct fetch-layer execution raises `PlaywrightUnavailableError`.
5. Bronze manifest is empty.
6. Silver and Gold artifacts are all empty in the current checkout.
7. orchestrated scraping uses Transfermarkt only; FBref scrape modules are present but not wired into refresh.
8. dashboard/API consume Silver/Gold artifacts, not raw scraper output.

## Main root cause summary
The system is not scraping successfully because the default orchestration path usually never starts real scraping, and the current runtime would fail immediately even if it did because Playwright is unavailable. After those blockers, a second structural gap remains: Transfermarkt-only orchestration cannot produce the FBref-driven match stats required by downstream analytics and dashboard views.

## Pedant review focus
Please review:
- whether the identified root-cause priority order is correct
- whether any source modules were omitted from the affected-file list
- whether the recommended next issue should be split into two tickets:
  - scrape target registry + orchestration wiring
  - runtime preflight + scrape diagnostics
- whether the parser fragility assessment is sufficiently evidenced from the code

## Suggested validation commands used during audit
- `find data -maxdepth 3 -type d | sort`
- `find data/raw data/parsed -type f 2>/dev/null | sort`
- `python3 -c 'from playwright.sync_api import sync_playwright'`
- `PYTHONPATH=. python3 - <<"PY" ... fetch_page_html(...) ... PY`
- `PYTHONPATH=. python3 - <<"PY" ... run_pipeline() ... PY`
- grep-based source tracing across `app/`

## Recommended next issue
`PAP-240 - Wire Concrete IDV Scrape Targets Into full_refresh and Add Scrape Runtime Preflight`
