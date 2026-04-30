from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any

from app.config import settings
from app.services.logging_service import get_logger, log_event, log_exception

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    PlaywrightTimeoutError = TimeoutError
    sync_playwright = None

try:
    from fake_useragent import UserAgent
    _UA = UserAgent()
    _UA_AVAILABLE = True
except Exception:
    _UA = None
    _UA_AVAILABLE = False


logger = get_logger(__name__)

READY_SELECTORS = {
    "transfermarkt": ["main", "div.data-header__headline-container", "div.marktwert", "body"],
    "fbref": ["section.content", "div[id^='all_stats']", "table[id*='stats']", "div#content", "body"],
}
CHALLENGE_MARKERS = ("just a moment", "cf-mitigated", "challenge", "captcha", "access denied")

_FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # seconds; doubles each attempt
_RATE_LIMIT_MIN = 1.0    # minimum random delay between requests (seconds)
_RATE_LIMIT_MAX = 5.0    # maximum random delay between requests (seconds)


def _random_user_agent() -> str:
    if _UA_AVAILABLE:
        try:
            return _UA.random
        except Exception:
            pass
    return random.choice(_FALLBACK_USER_AGENTS)


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = True
    delay_seconds: float = settings.scrape_delay_seconds
    timeout_ms: int = settings.scrape_timeout_ms
    max_retries: int = _MAX_RETRIES
    rate_limit_min: float = _RATE_LIMIT_MIN
    rate_limit_max: float = _RATE_LIMIT_MAX
    proxy: str | None = None       # "http://host:port" or "socks5://host:port"
    proxy_username: str | None = None
    proxy_password: str | None = None


class PlaywrightUnavailableError(RuntimeError):
    """Raised when Playwright is required but unavailable."""


def _wait_for_ready_content(page: object, source: str | None, timeout_ms: int) -> str | None:
    selectors = READY_SELECTORS.get(source or "", ["body"])
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=max(1000, min(timeout_ms, 5000)))
            return selector
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue
    return None


def _build_proxy_settings(config: BrowserConfig) -> dict[str, Any] | None:
    if not config.proxy:
        return None
    proxy: dict[str, Any] = {"server": config.proxy}
    if config.proxy_username:
        proxy["username"] = config.proxy_username
    if config.proxy_password:
        proxy["password"] = config.proxy_password
    return proxy


def _rate_limit_sleep(config: BrowserConfig) -> None:
    delay = random.uniform(config.rate_limit_min, config.rate_limit_max)
    time.sleep(delay)


def _attempt_fetch(
    url: str,
    config: BrowserConfig,
    context: dict[str, Any],
    attempt: int,
) -> str:
    """Single Playwright fetch attempt. Raises on failure."""
    user_agent = _random_user_agent()
    proxy_settings = _build_proxy_settings(config)

    with sync_playwright() as playwright:
        launch_kwargs: dict[str, Any] = {"headless": config.headless}
        if proxy_settings:
            launch_kwargs["proxy"] = proxy_settings

        browser = playwright.chromium.launch(**launch_kwargs)
        try:
            ctx_kwargs: dict[str, Any] = {"user_agent": user_agent}
            browser_ctx = browser.new_context(**ctx_kwargs)
            page = browser_ctx.new_page()
            page.set_default_timeout(config.timeout_ms)

            log_event(logger, logging.DEBUG, "fetch.attempt",
                      attempt=attempt, user_agent=user_agent[:40], **context)

            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            ready_selector = _wait_for_ready_content(page, context.get("source"), config.timeout_ms)

            if config.delay_seconds > 0:
                time.sleep(config.delay_seconds)

            html = page.content()
            try:
                title = page.title() or ""
            except Exception:
                title = ""

            challenge_detected = any(
                marker in (title + " " + html[:2000]).lower() for marker in CHALLENGE_MARKERS
            )

            if challenge_detected:
                log_event(logger, logging.WARNING, "fetch.challenge_detected",
                          attempt=attempt, page_title=title, **context)

            if not ready_selector:
                log_event(logger, logging.WARNING, "fetch.selector_missing", attempt=attempt, **context)

            return html
        finally:
            browser.close()


def fetch_page_html(
    url: str,
    config: BrowserConfig | None = None,
    *,
    source: str | None = None,
    slug: str | None = None,
) -> str:
    """
    Fetch fully rendered HTML using Playwright with retry, rate limiting, and UA rotation.
    Retries up to config.max_retries times with exponential backoff.
    """
    runtime_config = config or BrowserConfig()
    start = time.perf_counter()
    context = {
        "source": source,
        "slug": slug,
        "url": url,
        "timeout_ms": runtime_config.timeout_ms,
    }
    log_event(logger, logging.INFO, "fetch.start", **context)

    if sync_playwright is None:
        exc = PlaywrightUnavailableError(
            "Playwright is not installed. Run `playwright install` before scraping."
        )
        log_exception(logger, "fetch.playwright_unavailable", exc, **context)
        raise exc

    last_exc: Exception | None = None
    for attempt in range(1, runtime_config.max_retries + 1):
        try:
            if attempt > 1:
                backoff = _RETRY_BASE_DELAY * (2 ** (attempt - 2))
                log_event(logger, logging.INFO, "fetch.retry",
                          attempt=attempt, backoff_seconds=backoff, **context)
                time.sleep(backoff)
            else:
                _rate_limit_sleep(runtime_config)

            html = _attempt_fetch(url, runtime_config, context, attempt)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            log_event(logger, logging.INFO, "fetch.success",
                      html_length=len(html), elapsed_ms=elapsed_ms, attempt=attempt, **context)
            return html

        except Exception as exc:
            last_exc = exc
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            log_event(logger, logging.WARNING, "fetch.attempt_failed",
                      attempt=attempt, error=str(exc)[:200], elapsed_ms=elapsed_ms, **context)

    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    log_exception(logger, "fetch.failed",
                  last_exc or RuntimeError("all retries exhausted"),
                  elapsed_ms=elapsed_ms, attempts=runtime_config.max_retries, **context)
    raise last_exc or RuntimeError(f"fetch_page_html failed after {runtime_config.max_retries} attempts: {url}")
