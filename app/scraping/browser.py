from dataclasses import dataclass
import time

from app.config import settings

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency may not be installed in bootstrap environments.
    sync_playwright = None


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = True
    delay_seconds: float = settings.scrape_delay_seconds
    timeout_ms: int = settings.scrape_timeout_ms


class PlaywrightUnavailableError(RuntimeError):
    """Raised when Playwright is required but unavailable."""


def fetch_page_html(url: str, config: BrowserConfig | None = None) -> str:
    """Fetch fully rendered HTML using Playwright."""

    if sync_playwright is None:
        raise PlaywrightUnavailableError(
            "Playwright is not installed. Install dependencies and run `playwright install` before scraping."
        )

    runtime_config = config or BrowserConfig()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=runtime_config.headless)
        page = browser.new_page()
        page.set_default_timeout(runtime_config.timeout_ms)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        if runtime_config.delay_seconds > 0:
            time.sleep(runtime_config.delay_seconds)
        html = page.content()
        browser.close()
        return html
