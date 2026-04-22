from __future__ import annotations

from urllib.parse import urlparse

from app.config import settings
from app.scraping.browser import BrowserConfig, fetch_page_html
from app.scraping.fbref_mapping import map_fbref_match_to_db, map_fbref_stat_to_db
from app.scraping.fbref_parsers import (
    parse_fbref_match_payload,
    parse_fbref_player_match_stats,
    parse_fbref_player_per_90,
)
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "fbref-page"
    return slugify(path.split("/")[-1])


def scrape_fbref_page(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    runtime_slug = slug or _slug_from_url(url)
    html = fetch_page_html(url, BrowserConfig(headless=headless))
    raw_path = save_raw_html(runtime_slug, html, directory=settings.fbref_raw_data_dir)

    match_payload = parse_fbref_match_payload(html, url)
    player_match_stats = parse_fbref_player_match_stats(html, url)
    player_per_90 = parse_fbref_player_per_90(html, url)

    payload = {
        "match": match_payload,
        "player_match_stats": player_match_stats,
        "player_per_90": player_per_90,
        "db_mapping": {
            "match": map_fbref_match_to_db(match_payload),
            "stats": [map_fbref_stat_to_db(row) for row in player_match_stats],
        },
    }
    parsed_path = save_parsed_payload(runtime_slug, payload, directory=settings.fbref_parsed_data_dir)

    return {
        "slug": runtime_slug,
        "raw_html_path": raw_path,
        "parsed_data_path": parsed_path,
        "payload": payload,
    }
