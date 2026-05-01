"""
Tavily Discovery Engine — finds real player profile URLs across Transfermarkt.

Uses Tavily /search with domain restriction to locate genuine player pages,
extract TM player IDs, and feed them into the player registry.
"""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Any

import requests

from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

_TAVILY_BASE = "https://api.tavily.com"
_TIMEOUT = 20
_RATE_LIMIT = 1.2  # seconds between calls


def _api_key() -> str:
    key = os.getenv("TAVILY_API_KEY", "")
    if not key:
        raise RuntimeError("TAVILY_API_KEY not set in environment")
    return key


def _post(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{_TAVILY_BASE}{endpoint}"
    payload["api_key"] = _api_key()
    time.sleep(_RATE_LIMIT)
    r = requests.post(url, json=payload, timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _extract_tm_id(url: str) -> str | None:
    """Extract TM player numeric ID from a profile URL."""
    m = re.search(r"/spieler/(\d+)", url)
    return m.group(1) if m else None


def _is_player_profile_url(url: str) -> bool:
    return bool(re.search(r"transfermarkt\.com/[^/]+/profil/spieler/\d+", url))


# ── Public API ─────────────────────────────────────────────────────────────────

def search_players(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search Tavily for player pages on Transfermarkt matching the query.
    Returns list of {slug, name, tm_id, url} dicts for profile pages found.
    """
    try:
        data = _post("/search", {
            "query": query,
            "max_results": max_results,
            "include_domains": ["transfermarkt.com"],
            "search_depth": "basic",
        })
    except Exception as exc:
        log_event(logger, logging.WARNING, "tavily.search.error", query=query, error=str(exc))
        return []

    results = []
    for item in data.get("results", []):
        url = item.get("url", "")
        if not _is_player_profile_url(url):
            continue
        tm_id = _extract_tm_id(url)
        if not tm_id:
            continue
        title = item.get("title", "")
        # "Rodrigo Bentancur - Player profile 2026 | Transfermarkt"
        name_match = re.match(r"^(.*?)\s*[-–]\s*Player profile", title)
        name = name_match.group(1).strip() if name_match else title.split("-")[0].strip()
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        results.append({
            "slug": slug,
            "display_name": name,
            "tm_id": tm_id,
            "transfermarkt": url.split("?")[0],
        })
        log_event(logger, logging.INFO, "tavily.player.found", name=name, tm_id=tm_id, url=url)

    return results


def discover_league_players(
    league: str,
    country: str = "",
    max_age: int = 28,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """
    Use Tavily to discover young players in a specific league.
    """
    age_clause = f"under {max_age}" if max_age else ""
    country_clause = f"from {country}" if country else ""
    query = f"transfermarkt {league} players {country_clause} {age_clause} profile 2024 2025"
    return search_players(query.strip(), max_results=max_results)


def discover_all_leagues(force: bool = False) -> dict[str, list[dict[str, Any]]]:
    """
    Run discovery across all target leagues. Returns dict league → player list.
    """
    leagues = [
        ("Liga Pro Ecuador", "Ecuador", 30),
        ("Brasileirao Serie A", "Brazil", 26),
        ("Argentina Primera Division", "Argentina", 26),
        ("Primeira Liga Portugal", "Portugal", 26),
        ("Eredivisie Netherlands", "", 26),
        ("Austrian Bundesliga", "", 26),
        ("Belgian Pro League", "", 26),
        ("Colombian Primera A", "Colombia", 26),
        ("MLS young South Americans", "", 26),
    ]
    results: dict[str, list[dict[str, Any]]] = {}
    for league, country, max_age in leagues:
        found = discover_league_players(league, country, max_age, max_results=15)
        if found:
            results[league] = found
            log_event(logger, logging.INFO, "tavily.league.done", league=league, found=len(found))
    return results


def lookup_player_tm_id(player_name: str, club: str = "") -> dict[str, Any] | None:
    """
    Search Tavily to find a specific player's Transfermarkt profile.
    Returns {slug, display_name, tm_id, transfermarkt} or None.
    """
    club_clause = f"{club}" if club else ""
    query = f"transfermarkt {player_name} {club_clause} profil spieler"
    results = search_players(query, max_results=5)
    if not results:
        return None
    # Pick first result whose name roughly matches
    target = player_name.lower()
    for r in results:
        if any(part in r["display_name"].lower() for part in target.split()[-1:]):
            return r
    return results[0] if results else None


def extract_player_urls(tavily_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filter and deduplicate Tavily results to unique player profiles with valid TM IDs.
    """
    seen_ids: set[str] = set()
    out = []
    for r in tavily_results:
        if r.get("tm_id") and r["tm_id"] not in seen_ids:
            seen_ids.add(r["tm_id"])
            out.append(r)
    return out
