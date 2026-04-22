from __future__ import annotations

from urllib.parse import urlparse

from app.scraping.browser import BrowserConfig, fetch_page_html
from app.scraping.parsers import parse_player_profile, parse_transfer_history
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "transfermarkt-player"
    return slugify(path.split("/")[-1])


def scrape_transfermarkt_player(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    runtime_slug = slug or _slug_from_url(url)
    html = fetch_page_html(url, BrowserConfig(headless=headless))
    raw_path = save_raw_html(runtime_slug, html)

    payload = {
        "profile": parse_player_profile(html, url),
        "transfers": parse_transfer_history(html, url),
    }
    parsed_path = save_parsed_payload(runtime_slug, payload)

    return {
        "slug": runtime_slug,
        "raw_html_path": raw_path,
        "parsed_data_path": parsed_path,
        "payload": payload,
    }
