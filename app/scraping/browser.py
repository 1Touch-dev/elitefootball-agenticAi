from dataclasses import dataclass
import logging
import time

from app.config import settings
from app.services.logging_service import log_event, log_exception, get_logger

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency may not be installed in bootstrap environments.
    PlaywrightTimeoutError = TimeoutError
    sync_playwright = None


logger = get_logger(__name__)
READY_SELECTORS = {
    "transfermarkt": ["main", "div.data-header__headline-container", "div.marktwert", "body"],
    "fbref": ["section.content", "div[id^='all_stats']", "table[id*='stats']", "section[data-stat='player_stats']", "div#content", "body"],
}
CHALLENGE_MARKERS = ("just a moment", "cf-mitigated", "challenge", "captcha", "access denied")


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = True
    delay_seconds: float = settings.scrape_delay_seconds
    timeout_ms: int = settings.scrape_timeout_ms


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


def fetch_page_html(
    url: str,
    config: BrowserConfig | None = None,
    *,
    source: str | None = None,
    slug: str | None = None,
) -> str:
    """Fetch fully rendered HTML using Playwright."""

    runtime_config = config or BrowserConfig()
    start = time.perf_counter()
    context = {
        "source": source,
        "slug": slug,
        "url": url,
        "timeout_ms": runtime_config.timeout_ms,
        "headless": runtime_config.headless,
        "delay_seconds": runtime_config.delay_seconds,
    }
    log_event(logger, logging.INFO, "fetch.start", **context)

    if sync_playwright is None:
        exc = PlaywrightUnavailableError(
            "Playwright is not installed. Install dependencies and run `playwright install` before scraping."
        )
        log_exception(logger, "fetch.playwright_unavailable", exc, **context)
        raise exc

    browser = None
    try:
        with sync_playwright() as playwright:
            log_event(logger, logging.INFO, "fetch.browser_launch", **context)
            browser = playwright.chromium.launch(headless=runtime_config.headless)
            page = browser.new_page()
            page.set_default_timeout(runtime_config.timeout_ms)
            log_event(logger, logging.INFO, "fetch.goto", **context)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            ready_selector = _wait_for_ready_content(page, source, runtime_config.timeout_ms)
            if runtime_config.delay_seconds > 0:
                time.sleep(runtime_config.delay_seconds)
            html = page.content()
            try:
                title = page.title() or ""
            except Exception:
                title = ""
            challenge_detected = any(marker in (title + " " + html[:2000]).lower() for marker in CHALLENGE_MARKERS)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            log_event(
                logger,
                logging.INFO,
                "fetch.render_complete",
                html_length=len(html),
                elapsed_ms=elapsed_ms,
                ready_selector=ready_selector,
                challenge_detected=challenge_detected,
                page_title=title,
                **context,
            )
            if not ready_selector:
                log_event(logger, logging.WARNING, "fetch.selector_missing", elapsed_ms=elapsed_ms, **context)
            if challenge_detected:
                log_event(logger, logging.WARNING, "fetch.challenge_detected", elapsed_ms=elapsed_ms, page_title=title, **context)
            log_event(logger, logging.INFO, "fetch.success", html_length=len(html), elapsed_ms=elapsed_ms, **context)
            return html
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        log_exception(logger, "fetch.failed", exc, elapsed_ms=elapsed_ms, **context)
        raise
    finally:
        if browser is not None:
            browser.close()
