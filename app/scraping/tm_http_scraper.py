"""
Transfermarkt HTTP scraper using requests + BeautifulSoup.
Uses TM's public profile page and internal JSON APIs.

Works on servers without Playwright (plain HTTP, no JS rendering needed).
All scraped raw HTML and parsed JSON are stored to disk.
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

_SESSION = requests.Session()
_SESSION.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
)
_API_HEADERS = {
    **_SESSION.headers,
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
}
_TIMEOUT = 20
_MIN_DELAY = 2.0  # seconds between requests


def _get(url: str, *, api: bool = False, retries: int = 3) -> requests.Response:
    headers = _API_HEADERS if api else _SESSION.headers
    for attempt in range(retries):
        try:
            time.sleep(_MIN_DELAY)
            r = _SESSION.get(url, headers=headers, timeout=_TIMEOUT)
            if r.status_code in (429, 503):
                time.sleep(10 * (attempt + 1))
                continue
            return r
        except requests.RequestException as exc:
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url} after {retries} retries")


def _save_raw(slug: str, html: str) -> str:
    path = Path(settings.raw_data_dir) / f"{slug}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path)


def _save_parsed(slug: str, payload: dict[str, Any]) -> str:
    path = Path(settings.parsed_data_dir) / f"{slug}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _parse_market_value(raw: str) -> float | None:
    """€9.00m → 9_000_000, €500k → 500_000"""
    if not raw:
        return None
    raw = raw.strip()
    m = re.search(r"€([\d,.]+)\s*([mk]?)", raw, re.IGNORECASE)
    if not m:
        return None
    number = float(m.group(1).replace(",", ""))
    suffix = m.group(2).lower()
    if suffix == "m":
        return number * 1_000_000
    if suffix == "k":
        return number * 1_000
    return number


def _parse_profile_page(html: str, tm_id: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")

    # Player name from title
    title = soup.title.string if soup.title else ""
    name_match = re.match(r"^(.*?)\s*-\s*Player profile", title)
    player_name = name_match.group(1).strip() if name_match else None

    # Market value from market value link
    mv_raw = None
    mv_link = soup.select_one("a[href*='marktwertverlauf']")
    if mv_link:
        mv_raw = mv_link.get_text(strip=True)
        mv_raw = re.sub(r"Last update.*", "", mv_raw).strip()

    # Info table — li elements with label: value pattern
    info: dict[str, str] = {}
    for li in soup.select("li.data-header__label"):
        text = li.get_text(" ", strip=True)
        if ":" in text:
            k, _, v = text.partition(":")
            info[k.strip()] = v.strip()

    # Also parse info-table spans (more detailed)
    detail: dict[str, str] = {}
    spans = soup.select("span.info-table__content")
    for i in range(0, len(spans) - 1, 2):
        k = spans[i].get_text(strip=True).rstrip(":")
        v = spans[i + 1].get_text(strip=True)
        detail[k] = v

    dob_raw = detail.get("Date of birth/Age") or info.get("Date of birth/Age")
    dob = None
    age = None
    if dob_raw:
        m = re.match(r"(\d{2}/\d{2}/\d{4})\s*\((\d+)\)", dob_raw)
        if m:
            dob = m.group(1)
            age = int(m.group(2))

    return {
        "tm_id": tm_id,
        "player_name": player_name,
        "date_of_birth": dob,
        "age": age,
        "nationality": detail.get("Citizenship") or info.get("Citizenship"),
        "height": detail.get("Height") or info.get("Height"),
        "position": detail.get("Position") or info.get("Position"),
        "foot": detail.get("Foot"),
        "current_club": detail.get("Current club"),
        "on_loan_from": detail.get("On loan from"),
        "contract_expires": detail.get("Contract expires"),
        "market_value": mv_raw,
        "market_value_eur": _parse_market_value(mv_raw or ""),
    }


def _fetch_mv_history(tm_id: str) -> list[dict[str, Any]]:
    url = f"https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{tm_id}"
    try:
        r = _get(url, api=True)
        if r.status_code != 200:
            return []
        data = r.json()
        history = []
        for item in data.get("list", []):
            history.append(
                {
                    "date": item.get("datum_mw"),
                    "value_eur": item.get("y"),
                    "value_str": item.get("mw"),
                    "club": item.get("verein"),
                    "age": item.get("age"),
                }
            )
        return history
    except Exception:
        return []


def _fetch_performance(tm_id: str) -> list[dict[str, Any]]:
    url = f"https://www.transfermarkt.com/ceapi/player/performance/{tm_id}"
    try:
        r = _get(url, api=True)
        if r.status_code != 200:
            return []
        rows = r.json()
        if not isinstance(rows, list):
            return []
        stats = []
        for row in rows:
            stats.append(
                {
                    "competition": row.get("competitionDescription", "").strip(),
                    "season": row.get("nameSeason"),
                    "games_played": row.get("gamesPlayed", 0),
                    "goals": row.get("goalsScored", 0),
                    "assists": row.get("assists", 0),
                    "yellow_cards": row.get("yellowCards", 0),
                    "red_cards": row.get("redCards", 0) + row.get("secondYellowCards", 0),
                    "minutes_played": row.get("minutesPlayed", 0),
                }
            )
        return stats
    except Exception:
        return []


def scrape_player(
    slug: str,
    tm_id: str,
    display_name: str | None = None,
) -> dict[str, Any]:
    """
    Scrape TM player: profile + MV history + season stats.
    Saves raw HTML + parsed JSON. Returns parsed payload dict.
    """
    log_event(logger, logging.INFO, "tm_scrape.start", slug=slug, tm_id=tm_id)

    profile_url = f"https://www.transfermarkt.com/{slug}/profil/spieler/{tm_id}"
    r = _get(profile_url)
    if r.status_code != 200:
        raise RuntimeError(f"TM profile returned {r.status_code} for {slug}")

    raw_path = _save_raw(slug, r.text)
    profile = _parse_profile_page(r.text, tm_id)
    if display_name and not profile.get("player_name"):
        profile["player_name"] = display_name

    profile["source"] = "transfermarkt"
    profile["source_url"] = profile_url

    mv_history = _fetch_mv_history(tm_id)
    performance_stats = _fetch_performance(tm_id)

    payload = {
        "profile": profile,
        "transfers": [],  # TM transfer history requires JS; use existing known data
        "mv_history": mv_history,
        "performance_stats": performance_stats,
    }

    parsed_path = _save_parsed(slug, payload)
    log_event(
        logger,
        logging.INFO,
        "tm_scrape.complete",
        slug=slug,
        tm_id=tm_id,
        raw_path=raw_path,
        parsed_path=parsed_path,
        perf_records=len(performance_stats),
        mv_records=len(mv_history),
    )
    return {"slug": slug, "raw_path": raw_path, "parsed_path": parsed_path, "payload": payload}


def scrape_all_idv(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Scrape all IDV players from the URL registry. Returns list of results."""
    from scripts.player_urls import IDV_PLAYER_URLS

    results = []
    for slug, info in IDV_PLAYER_URLS.items():
        tm_url = info.get("transfermarkt", "")
        if not tm_url:
            continue
        m = re.search(r"/spieler/(\d+)", tm_url)
        if not m:
            continue
        tm_id = m.group(1)

        # Skip if already scraped today and force_refresh is False
        parsed_path = Path(settings.parsed_data_dir) / f"{slug}.json"
        if not force_refresh and parsed_path.exists():
            age_hours = (time.time() - parsed_path.stat().st_mtime) / 3600
            if age_hours < 24:
                log_event(logger, logging.INFO, "tm_scrape.skip_cached", slug=slug, age_hours=round(age_hours, 1))
                results.append({"slug": slug, "status": "cached"})
                continue

        try:
            result = scrape_player(slug, tm_id, display_name=info.get("display_name"))
            result["status"] = "ok"
            results.append(result)
        except Exception as exc:
            log_event(logger, logging.ERROR, "tm_scrape.error", slug=slug, error=str(exc))
            results.append({"slug": slug, "status": "error", "error": str(exc)})

    return results
