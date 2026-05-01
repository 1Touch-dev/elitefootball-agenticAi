"""
Crawl4AI-based scraping engine with Playwright fallback.

Crawl4AI provides structured JSON/Markdown extraction, async crawling,
and anti-bot techniques. When unavailable, falls back to Playwright.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from app.config import settings
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)

_CRAWL4AI_AVAILABLE = True
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode  # type: ignore
except ImportError:
    _CRAWL4AI_AVAILABLE = False

# Cache TTL: 24 hours
_CACHE_TTL_SECONDS = 86_400


def _cache_path(url: str) -> Path:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_dir = Path(settings.bronze_data_dir) / "crawl_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{url_hash}.json"


def _load_cache(url: str) -> dict[str, Any] | None:
    path = _cache_path(url)
    if not path.exists():
        return None
    try:
        stat = path.stat()
        if time.time() - stat.st_mtime > _CACHE_TTL_SECONDS:
            return None
        return json.loads(path.read_text())
    except Exception:
        return None


def _save_cache(url: str, data: dict[str, Any]) -> None:
    try:
        _cache_path(url).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        pass


# ── Playwright fallback ───────────────────────────────────────────────────────

def _fetch_with_playwright(url: str, headless: bool = True) -> str:
    """Fetch page HTML via Playwright (sync wrapper)."""
    from app.scraping.browser import BrowserConfig, fetch_page_html
    return fetch_page_html(url, BrowserConfig(headless=headless), source="crawl4ai_fallback", slug="crawl4ai")


def _playwright_crawl(url: str, retries: int = 3) -> dict[str, Any]:
    """Playwright-based crawl with retry and exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            html = _fetch_with_playwright(url)
            return {"url": url, "html": html, "markdown": "", "success": True, "engine": "playwright"}
        except Exception as exc:
            last_exc = exc
            wait = 2 ** attempt
            log_event(logger, logging.WARNING, "crawl4ai.playwright_retry",
                      url=url, attempt=attempt + 1, retries=retries, wait=wait, error=str(exc))
            time.sleep(wait)
    raise RuntimeError(f"Playwright crawl failed after {retries} attempts: {last_exc}") from last_exc


# ── Crawl4AI async implementation ─────────────────────────────────────────────

def _requests_fallback(url: str) -> dict[str, Any]:
    """Direct requests fallback when crawl4ai / Playwright browser is unavailable."""
    import requests as _requests
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    resp = _requests.get(url, headers=headers, timeout=20, allow_redirects=True)
    resp.raise_for_status()
    html = resp.text
    return {
        "url": url,
        "html": html,
        "markdown": "",
        "success": True,
        "engine": "crawl4ai_httpx_fallback",
        "source": "crawl4ai_httpx_fallback",
    }


async def _crawl4ai_fetch(url: str) -> dict[str, Any]:
    """Fetch using Crawl4AI with structured extraction."""
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle",
        page_timeout=30_000,
        verbose=False,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        if not result.success:
            raise RuntimeError(f"Crawl4AI fetch failed: {result.error_message}")
        return {
            "url": url,
            "html": result.html or "",
            "markdown": result.markdown or "",
            "success": True,
            "engine": "crawl4ai",
        }


def _crawl4ai_crawl(url: str, retries: int = 3) -> dict[str, Any]:
    """Sync wrapper for Crawl4AI with exponential backoff. Falls back to requests on browser error."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return asyncio.run(_crawl4ai_fetch(url))
        except Exception as exc:
            err_str = str(exc).lower()
            # If it's a browser/Playwright error, skip retries and go straight to fallback
            if any(kw in err_str for kw in ("playwright", "browser", "chromium", "executable")):
                log_event(logger, logging.WARNING, "crawl4ai.browser_unavailable",
                          url=url, error=str(exc))
                break
            last_exc = exc
            wait = 2 ** attempt
            log_event(logger, logging.WARNING, "crawl4ai.retry",
                      url=url, attempt=attempt + 1, retries=retries, wait=wait, error=str(exc))
            time.sleep(wait)

    # Fall back to direct requests
    log_event(logger, logging.INFO, "crawl4ai.fallback_to_requests", url=url)
    try:
        return _requests_fallback(url)
    except Exception as exc2:
        raise RuntimeError(
            f"Crawl4AI and requests fallback both failed for {url}: {exc2}"
        ) from exc2


# ── Public API ────────────────────────────────────────────────────────────────

def crawl_page(
    url: str,
    *,
    headless: bool = True,
    retries: int = 3,
    use_cache: bool = True,
    slug: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """
    Fetch a page using Crawl4AI (preferred) or Playwright (fallback).

    Returns dict with keys:
      - url: str
      - html: str
      - markdown: str (empty for Playwright fallback)
      - success: bool
      - engine: "crawl4ai" | "playwright"
      - cached: bool
    """
    if use_cache:
        cached = _load_cache(url)
        if cached:
            cached["cached"] = True
            log_event(logger, logging.DEBUG, "crawl4ai.cache_hit", url=url, engine=cached.get("engine"))
            return cached

    context = {"url": url, "crawl4ai_available": _CRAWL4AI_AVAILABLE}
    log_event(logger, logging.INFO, "crawl4ai.fetch_start", **context)

    try:
        if _CRAWL4AI_AVAILABLE:
            result = _crawl4ai_crawl(url, retries=retries)
        else:
            # No crawl4ai: try Playwright, fall back to requests
            try:
                result = _playwright_crawl(url, retries=retries)
            except Exception as pw_exc:
                log_event(logger, logging.WARNING, "crawl4ai.playwright_failed_fallback",
                          url=url, error=str(pw_exc))
                result = _requests_fallback(url)

        result["cached"] = False
        if use_cache:
            _save_cache(url, result)

        log_event(logger, logging.INFO, "crawl4ai.fetch_complete",
                  engine=result.get("engine", "unknown"), html_len=len(result.get("html", "")), url=url)
        return result

    except Exception as exc:
        log_exception(logger, "crawl4ai.fetch_failed", exc, url=url)
        raise


def crawl_squad_page(
    squad_url: str,
    *,
    headless: bool = True,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Crawl a squad/team page for player discovery.
    Returns the raw page plus basic metadata.
    """
    result = crawl_page(squad_url, headless=headless, use_cache=use_cache)
    result["page_type"] = "squad"
    return result


def crawl_player_profile(
    transfermarkt_url: str,
    fbref_url: str | None = None,
    *,
    use_cache: bool = True,
) -> dict[str, dict[str, Any]]:
    """
    Multi-source crawl for a single player.
    Returns dict keyed by source name with raw page data.
    """
    results: dict[str, dict[str, Any]] = {}

    try:
        results["transfermarkt"] = crawl_page(transfermarkt_url, use_cache=use_cache)
    except Exception as exc:
        log_exception(logger, "crawl4ai.transfermarkt_failed", exc, url=transfermarkt_url)
        results["transfermarkt"] = {"success": False, "error": str(exc), "html": "", "markdown": ""}

    if fbref_url:
        try:
            results["fbref"] = crawl_page(fbref_url, use_cache=use_cache)
        except Exception as exc:
            log_exception(logger, "crawl4ai.fbref_failed", exc, url=fbref_url)
            results["fbref"] = {"success": False, "error": str(exc), "html": "", "markdown": ""}

    return results


def detect_challenge(html: str) -> bool:
    """Check if the page is a bot-challenge/CAPTCHA."""
    lower = html.lower()
    signals = [
        "cf-challenge", "cf_chl_", "captcha", "recaptcha",
        "challenge-form", "challenge-running", "just a moment",
        "please wait", "cloudflare", "ddos-guard",
    ]
    return any(s in lower for s in signals)


def extract_json_ld(html: str) -> list[dict[str, Any]]:
    """Extract all JSON-LD structured data blocks from a page."""
    import re
    results = []
    pattern = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
    for match in pattern.finditer(html):
        try:
            results.append(json.loads(match.group(1).strip()))
        except json.JSONDecodeError:
            pass
    return results
