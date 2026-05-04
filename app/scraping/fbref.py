"""
FBref scraper — production-grade, requests-only (no Selenium/browser required).

Strategy:
  1. Attempt direct FBref fetch with UA rotation + delay
  2. On 403/block: use Wayback Machine (web.archive.org) with retry backoff
  3. Parse HTML via our _FBrefTableParser (BeautifulSoup-style, pure Python)
  4. Extract: xG, xA, goals, assists, minutes, progressive actions (real values)
  5. NO synthetic data — if parsing fails, returns None fields

Rate limiting:
  - FBref: 5s min between requests
  - Wayback: 3s min between requests
  - Retry with exponential backoff: 1s, 2s, 4s
"""
from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings
from app.scraping.fbref_parsers import (
    parse_fbref_match_payload,
    parse_fbref_player_match_stats,
    parse_fbref_player_per_90,
)
from app.scraping.validation import validate_fbref_payload
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify
from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

# --- User-agent pool for rotation ---
_USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

_LAST_REQUEST: dict[str, float] = {}
_RATE_LIMITS = {
    "fbref": 5.0,
    "wayback": 3.0,
}


def _rotate_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def _rate_limit(source: str) -> None:
    limit = _RATE_LIMITS.get(source, 3.0)
    last = _LAST_REQUEST.get(source, 0)
    elapsed = time.time() - last
    if elapsed < limit:
        time.sleep(limit - elapsed + random.uniform(0.1, 0.5))
    _LAST_REQUEST[source] = time.time()


def fetch_page_html(url: str, *, source: str = "fbref", slug: str = "", retries: int = 3) -> str:
    """
    Fetch page HTML with retry + rate limiting + UA rotation.
    Falls back to Wayback Machine if direct access returns 403.
    Returns raw HTML string. Raises on total failure.
    """
    import requests

    for attempt in range(retries):
        try:
            _rate_limit(source)
            headers = _rotate_headers()
            resp = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            if resp.status_code == 200 and len(resp.text) > 5000:
                return resp.text
            elif resp.status_code in (403, 429):
                # Fallback to Wayback
                log_event(logger, logging.WARNING, "scrape.fbref.blocked",
                          url=url, status=resp.status_code, attempt=attempt)
                break
            elif resp.status_code >= 500:
                wait = 2 ** attempt
                log_event(logger, logging.WARNING, "scrape.fbref.server_error",
                          url=url, status=resp.status_code, wait=wait)
                time.sleep(wait)
                continue
        except Exception as exc:
            wait = 2 ** attempt
            log_event(logger, logging.WARNING, "scrape.fbref.request_error",
                      url=url, error=str(exc)[:100], attempt=attempt, wait=wait)
            time.sleep(wait)
            continue

    # Wayback Machine fallback
    archive_url = f"https://web.archive.org/web/2/{url}"
    for attempt in range(retries):
        try:
            _rate_limit("wayback")
            headers = _rotate_headers()
            resp = requests.get(archive_url, headers=headers, timeout=45, allow_redirects=True)
            if resp.status_code == 200 and len(resp.text) > 5000:
                log_event(logger, logging.INFO, "scrape.fbref.wayback_success",
                          url=url, archive_url=archive_url, size=len(resp.text))
                return resp.text
            wait = 2 ** attempt
            time.sleep(wait)
        except Exception as exc:
            wait = 2 ** attempt
            log_event(logger, logging.WARNING, "scrape.fbref.wayback_error",
                      url=url, error=str(exc)[:100], attempt=attempt)
            time.sleep(wait)

    raise RuntimeError(f"Failed to fetch FBref page: {url} (all sources exhausted)")


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "fbref-page"
    return slugify(path.split("/")[-1])


def scrape_fbref_page(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    """
    Scrape a FBref page (match report or player page).
    Returns structured payload with player_match_stats, match data, diagnostics.
    No synthetic data generated — missing fields are None.
    """
    runtime_slug = slug or _slug_from_url(url)
    context = {"source": "fbref", "slug": runtime_slug, "url": url}
    log_event(logger, logging.INFO, "scrape.start", **context)
    try:
        html = fetch_page_html(url, source="fbref", slug=runtime_slug)
        raw_path = save_raw_html(runtime_slug, html, directory=settings.fbref_raw_data_dir)
        log_event(logger, logging.INFO, "scrape.raw_saved",
                  raw_html_path=raw_path, html_length=len(html), **context)

        match_payload = parse_fbref_match_payload(html, url)
        player_match_stats = parse_fbref_player_match_stats(html, url)
        if not player_match_stats:
            # Only add metadata row — no synthetic numeric values
            player_match_stats.append({
                "source": "fbref",
                "source_url": url,
                "player_name": (runtime_slug or "Unknown").replace("-", " ").title(),
                "minutes": None,
                "goals": None,
                "assists": None,
                "xg": None,
                "xa": None,
            })
        player_per_90 = parse_fbref_player_per_90(html, url)
        challenge_detected = bool(match_payload.get("challenge_detected"))
        diagnostics = validate_fbref_payload(
            match_payload,
            player_match_stats,
            player_per_90,
            challenge_detected=challenge_detected,
        )

        payload = {
            "match": match_payload,
            "player_match_stats": player_match_stats,
            "player_per_90": player_per_90,
            "diagnostics": diagnostics,
        }
        parsed_path = save_parsed_payload(
            runtime_slug,
            payload,
            directory=settings.fbref_parsed_data_dir,
        )
        log_event(logger, logging.INFO, "scrape.complete",
                  parsed_path=parsed_path,
                  player_stats_count=len(player_match_stats),
                  **context)
        return {"payload": payload}
    except Exception as exc:
        log_event(logger, logging.ERROR, "scrape.error",
                  error=str(exc)[:200], **context)
        return {"payload": {
            "match": {},
            "player_match_stats": [{
                "source": "fbref",
                "source_url": url,
                "player_name": runtime_slug.replace("-", " ").title(),
                "minutes": None,
                "goals": None,
                "assists": None,
                "xg": None,
                "xa": None,
                "_error": str(exc)[:100],
            }],
            "player_per_90": [],
            "diagnostics": {"error": str(exc)[:200]},
        }}
