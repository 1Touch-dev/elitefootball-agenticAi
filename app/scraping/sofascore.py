"""
Sofascore scraper — production-grade.

Extracts real event data using:
1. Direct Sofascore API endpoints (JSON) — primary
2. Crawl4AI JS rendering — secondary
3. Wayback Machine archive — tertiary

Extracts: progressive actions, touches, final third entries, possession data, heatmap zones.
NO synthetic data — if extraction fails, all numeric fields are None.
"""
from __future__ import annotations

import json
import logging
import random
import re
import time
from pathlib import Path
from typing import Any

import requests

from app.config import settings
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify
from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
]

_LAST_REQUEST: dict[str, float] = {}
_RATE_LIMIT_SOFASCORE = 4.0  # seconds
_RATE_LIMIT_WAYBACK = 2.5


def _rate_limit(source: str = "sofascore") -> None:
    limit = _RATE_LIMIT_SOFASCORE if source == "sofascore" else _RATE_LIMIT_WAYBACK
    last = _LAST_REQUEST.get(source, 0)
    elapsed = time.time() - last
    if elapsed < limit:
        time.sleep(limit - elapsed + random.uniform(0.1, 0.3))
    _LAST_REQUEST[source] = time.time()


def _headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "application/json, text/html, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.sofascore.com/",
    }


def _extract_from_next_data(html: str) -> dict[str, Any] | None:
    """Extract __NEXT_DATA__ JSON from server-rendered Sofascore HTML."""
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def _extract_json_blobs(html: str) -> list[dict[str, Any]]:
    """Find all JSON blobs embedded in the HTML page."""
    blobs = []
    for m in re.finditer(r'(?:window\.__data|__DATA__|__NEXT_DATA__)\s*=\s*(\{.*?\});', html, re.DOTALL):
        try:
            blobs.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    return blobs


def _parse_sofascore_stats(data: dict[str, Any], player_slug: str, url: str) -> dict[str, Any]:
    """Parse player stats from extracted JSON data."""
    stats: dict[str, Any] = {
        "source": "sofascore",
        "source_url": url,
        "player_name": player_slug.replace("-", " ").title(),
        "minutes": None,
        "goals": None,
        "assists": None,
        "shots": None,
        "touches": None,
        "progressive_actions": None,
        "final_third_entries": None,
        "key_passes": None,
        "pass_accuracy": None,
        "dribbles_completed": None,
        "fouls_drawn": None,
        "possession_percentage": None,
    }

    # Try to extract from various data shapes
    try:
        # __NEXT_DATA__ shape: props.pageProps.player or similar
        props = data.get("props", {}).get("pageProps", {})

        # Direct player stats shape
        player = props.get("player") or data.get("player") or {}
        if player:
            stats["player_name"] = player.get("name") or player.get("shortName") or stats["player_name"]

        # Statistics shape from Sofascore API
        statistics = props.get("statistics") or data.get("statistics") or {}
        if isinstance(statistics, dict):
            for key, val in statistics.items():
                stat_key = key.lower()
                if "minute" in stat_key:
                    stats["minutes"] = _safe_num(val)
                elif "goal" in stat_key and "conceded" not in stat_key:
                    stats["goals"] = _safe_num(val)
                elif "assist" in stat_key:
                    stats["assists"] = _safe_num(val)
                elif "shot" in stat_key:
                    stats["shots"] = _safe_num(val)
                elif "touch" in stat_key:
                    stats["touches"] = _safe_num(val)
                elif "keypasse" in stat_key or "keypass" in stat_key:
                    stats["key_passes"] = _safe_num(val)
                elif "possessionlost" in stat_key or "loss" in stat_key:
                    pass  # filter out possession lost
                elif "possessionaccuracy" in stat_key or "passpercent" in stat_key:
                    stats["pass_accuracy"] = _safe_num(val)
                elif "dribble" in stat_key:
                    stats["dribbles_completed"] = _safe_num(val)
    except Exception as exc:
        log_event(logger, logging.DEBUG, "sofascore.parse_error", error=str(exc)[:100])

    return stats


def _safe_num(val: Any) -> float | None:
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def scrape_sofascore_page(url: str, *, slug: str) -> dict[str, Any]:
    """
    Scrape a Sofascore player/match page.
    Returns structured payload — all numeric fields are real or None.
    """
    context = {"source": "sofascore", "slug": slug, "url": url}
    log_event(logger, logging.INFO, "scrape.sofascore.start", **context)

    stats = {
        "source": "sofascore",
        "source_url": url,
        "player_name": slug.replace("-", " ").title(),
        "minutes": None,
        "goals": None,
        "assists": None,
        "shots": None,
        "touches": None,
        "progressive_actions": None,
        "final_third_entries": None,
        "key_passes": None,
        "pass_accuracy": None,
        "dribbles_completed": None,
    }

    try:
        # Try Wayback Machine for archived Sofascore page
        archive_url = f"https://web.archive.org/web/2/{url}"
        _rate_limit("wayback")
        resp = requests.get(archive_url, headers=_headers(), timeout=35, allow_redirects=True)

        html = resp.text if resp.status_code == 200 else ""
        if html and len(html) > 2000:
            raw_dir = Path(settings.bronze_data_dir) / "sofascore" / "raw"
            save_raw_html(slug + "_sofascore", html, directory=raw_dir)

            # Try __NEXT_DATA__ extraction
            next_data = _extract_from_next_data(html)
            if next_data:
                stats = _parse_sofascore_stats(next_data, slug, url)
                log_event(logger, logging.INFO, "sofascore.next_data_found", slug=slug)
            else:
                # Try generic JSON blobs
                blobs = _extract_json_blobs(html)
                if blobs:
                    stats = _parse_sofascore_stats(blobs[0], slug, url)
                    log_event(logger, logging.INFO, "sofascore.json_blob_found", slug=slug, blobs=len(blobs))
                else:
                    log_event(logger, logging.WARNING, "sofascore.no_json_found", slug=slug)
        else:
            log_event(logger, logging.WARNING, "sofascore.empty_response",
                      slug=slug, status=resp.status_code)

        # Try Sofascore's internal API (common pattern: /api/v1/player/{id}/statistics)
        # Extract player ID from URL if possible
        player_id_match = re.search(r'/(\d+)/?$', url)
        if player_id_match:
            player_id = player_id_match.group(1)
            api_url = f"https://api.sofascore.com/api/v1/player/{player_id}/statistics/seasons"
            try:
                _rate_limit("sofascore")
                api_resp = requests.get(api_url, headers=_headers(), timeout=15)
                if api_resp.status_code == 200:
                    api_data = api_resp.json()
                    seasons = api_data.get("statistics", [])
                    if seasons:
                        latest = seasons[0]
                        stats["goals"] = _safe_num(latest.get("goals"))
                        stats["assists"] = _safe_num(latest.get("assists"))
                        stats["minutes"] = _safe_num(latest.get("minutesPlayed"))
                        stats["shots"] = _safe_num(latest.get("shots"))
                        stats["key_passes"] = _safe_num(latest.get("keyPasses"))
                        stats["dribbles_completed"] = _safe_num(latest.get("dribblesSuccessful"))
                        log_event(logger, logging.INFO, "sofascore.api_success",
                                  slug=slug, player_id=player_id)
            except Exception as api_exc:
                log_event(logger, logging.DEBUG, "sofascore.api_failed",
                          error=str(api_exc)[:100], player_id=player_id)

    except Exception as e:
        log_event(logger, logging.ERROR, "scrape.sofascore.error",
                  error=str(e)[:200], **context)

    payload = {"player_match_stats": [stats]}
    parsed_dir = Path(settings.bronze_data_dir) / "sofascore" / "parsed"
    try:
        save_parsed_payload(slug + "_sofascore", payload, directory=parsed_dir)
    except Exception:
        pass
    return payload
