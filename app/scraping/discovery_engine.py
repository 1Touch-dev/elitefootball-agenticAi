"""
Autonomous player discovery engine.

Crawls Transfermarkt league squad pages using Crawl4AI AsyncWebCrawler.arun_many()
to extract player links, names, clubs, and positions.

New players found → deduped via entity_resolution → added to job queue.

Target leagues:
  - Transfermarkt Ecuador Liga Pro squad pages
  - Transfermarkt Brasileirão squad pages
  - Transfermarkt Primeira Liga squad pages
  - Transfermarkt Eredivisie squad pages
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any
from urllib.parse import urljoin

from app.scraping.entity_resolution import (
    _normalize_name,
    build_resolution_index,
    resolve_player_slug,
)
from app.scraping.job_queue import JobPriority, PersistentJobQueue
from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

# ── League discovery targets ──────────────────────────────────────────────────

DISCOVERY_LEAGUES: dict[str, dict[str, Any]] = {
    "liga_pro": {
        "name": "Ecuador Liga Pro",
        "url": "https://www.transfermarkt.com/liga-pro/startseite/wettbewerb/ECA1",
        "priority": JobPriority.HIGH,
    },
    "brasileirao": {
        "name": "Brasileirão Serie A",
        "url": "https://www.transfermarkt.com/campeonato-brasileiro-serie-a/startseite/wettbewerb/BRA1",
        "priority": JobPriority.MEDIUM,
    },
    "primeira_liga": {
        "name": "Portugal Primeira Liga",
        "url": "https://www.transfermarkt.com/liga-nos/startseite/wettbewerb/PO1",
        "priority": JobPriority.MEDIUM,
    },
    "eredivisie": {
        "name": "Netherlands Eredivisie",
        "url": "https://www.transfermarkt.com/eredivisie/startseite/wettbewerb/NL1",
        "priority": JobPriority.MEDIUM,
    },
    "austrian_bl": {
        "name": "Austrian Bundesliga",
        "url": "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/A1",
        "priority": JobPriority.LOW,
    },
    "argentina_primera": {
        "name": "Argentina Primera División",
        "url": "https://www.transfermarkt.com/primera-division/startseite/wettbewerb/AR1N",
        "priority": JobPriority.LOW,
    },
}

_TM_BASE = "https://www.transfermarkt.com"
_PLAYER_LINK_RE = re.compile(r"/[^/]+/profil/spieler/(\d+)")


def _extract_player_links(html: str, base_url: str = _TM_BASE) -> list[dict[str, Any]]:
    """
    Parse Transfermarkt squad/league page HTML for player profile links.
    Returns list of {name, url, tm_id} dicts.
    """
    players: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    # Match player profile links
    href_pattern = re.compile(
        r'href="(/[^"]+/profil/spieler/(\d+))"[^>]*>([^<]*)<',
        re.IGNORECASE,
    )
    for match in href_pattern.finditer(html):
        href, tm_id, link_text = match.group(1), match.group(2), match.group(3).strip()
        if tm_id in seen_ids:
            continue
        if not link_text or len(link_text) < 2:
            continue
        # Filter out non-player links (coaches, leagues, etc.)
        if any(x in href.lower() for x in ["/trainer/", "/verein/", "/wettbewerb/", "/news/"]):
            continue
        full_url = base_url + href
        players.append({
            "player_name": link_text,
            "url": full_url,
            "tm_id": tm_id,
        })
        seen_ids.add(tm_id)

    return players


def _extract_player_names_from_markdown(markdown: str) -> list[str]:
    """Fallback: extract player names from Crawl4AI markdown output."""
    names: list[str] = []
    # Names typically appear as bold or link text
    for line in markdown.split("\n"):
        line = line.strip()
        # Bold markdown: **Name**
        for match in re.finditer(r"\*\*([A-Z][a-zÀ-ž]+(?: [A-Z][a-zÀ-ž]+)+)\*\*", line):
            names.append(match.group(1))
    return names


async def _crawl_league_pages_async(
    league_urls: list[str],
    max_concurrent: int = 3,
) -> list[dict[str, Any]]:
    """
    Async crawl multiple league pages using Crawl4AI arun_many when available,
    falling back to sequential Playwright fetches.
    """
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode  # type: ignore
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="networkidle",
            page_timeout=25_000,
            verbose=False,
        )
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun_many(league_urls, config=config)
            return [
                {
                    "url": r.url,
                    "html": r.html or "",
                    "markdown": r.markdown or "",
                    "success": r.success,
                    "engine": "crawl4ai",
                }
                for r in results
            ]
    except Exception as exc:
        log_event(logger, logging.WARNING, "discovery.crawl4ai_unavailable",
                  error=str(exc)[:120])

    # Sequential Playwright fallback
    results = []
    for url in league_urls:
        try:
            from app.scraping.crawl4ai_engine import crawl_page
            result = crawl_page(url, use_cache=True)
            results.append(result)
        except Exception as exc:
            log_event(logger, logging.WARNING, "discovery.playwright_failed",
                      url=url, error=str(exc)[:120])
            results.append({"url": url, "html": "", "markdown": "", "success": False})
    return results


def discover_league_players(
    league_keys: list[str] | None = None,
    known_players: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Crawl target league pages and return newly discovered players not already known.

    Returns list of {player_name, url, tm_id, league_key, is_new, slug}.
    """
    target_keys = league_keys or list(DISCOVERY_LEAGUES.keys())
    known_players = known_players or []
    resolution_index = build_resolution_index(known_players)

    league_urls = [DISCOVERY_LEAGUES[k]["url"] for k in target_keys if k in DISCOVERY_LEAGUES]
    if not league_urls:
        return []

    log_event(logger, logging.INFO, "discovery.crawl_start",
              leagues=target_keys, urls=len(league_urls))

    try:
        page_results = asyncio.run(_crawl_league_pages_async(league_urls))
    except RuntimeError:
        # If event loop already running (e.g. inside FastAPI), fall back to sync
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, _crawl_league_pages_async(league_urls))
            page_results = future.result(timeout=120)

    discovered: list[dict[str, Any]] = []
    for i, page in enumerate(page_results):
        league_key = target_keys[i] if i < len(target_keys) else "unknown"
        league_info = DISCOVERY_LEAGUES.get(league_key, {})
        html = page.get("html") or ""
        markdown = page.get("markdown") or ""

        players_on_page = _extract_player_links(html)
        if not players_on_page and markdown:
            for name in _extract_player_names_from_markdown(markdown):
                players_on_page.append({"player_name": name, "url": None, "tm_id": None})

        log_event(logger, logging.INFO, "discovery.page_parsed",
                  league=league_key, found=len(players_on_page),
                  success=page.get("success"))

        for p in players_on_page:
            slug, confidence = resolve_player_slug(p, resolution_index, source=league_key)
            is_new = slug is None or confidence < 0.80
            if is_new:
                slug = re.sub(r"\s+", "_", _normalize_name(p["player_name"]))

            discovered.append({
                "player_name": p["player_name"],
                "url": p.get("url"),
                "tm_id": p.get("tm_id"),
                "league_key": league_key,
                "league_name": league_info.get("name"),
                "priority": int(league_info.get("priority", JobPriority.LOW)),
                "is_new": is_new,
                "slug": slug,
                "match_confidence": confidence,
            })

    new_players = [p for p in discovered if p["is_new"]]
    log_event(logger, logging.INFO, "discovery.complete",
              total_found=len(discovered), new_players=len(new_players))
    return discovered


def enqueue_discovered_players(
    discovered: list[dict[str, Any]],
    queue: PersistentJobQueue | None = None,
) -> int:
    """
    Add newly discovered players to the job queue.
    Returns number of new jobs enqueued.
    """
    if queue is None:
        queue = PersistentJobQueue()

    enqueued = 0
    for player in discovered:
        if not player.get("is_new"):
            continue
        url = player.get("url")
        if not url:
            continue

        queue.enqueue(
            player_slug=player["slug"],
            source="transfermarkt",
            url=url,
            priority=JobPriority(int(player.get("priority", JobPriority.LOW))),
            metadata={
                "discovered_from": player.get("league_key"),
                "player_name": player.get("player_name"),
                "tm_id": player.get("tm_id"),
            },
        )
        enqueued += 1

    log_event(logger, logging.INFO, "discovery.enqueued", count=enqueued)
    return enqueued


def run_discovery_cycle(
    league_keys: list[str] | None = None,
    known_players: list[dict[str, Any]] | None = None,
    auto_enqueue: bool = True,
) -> dict[str, Any]:
    """
    Full discovery cycle: crawl → parse → resolve → enqueue.
    Returns summary dict.
    """
    discovered = discover_league_players(league_keys, known_players)
    new_players = [p for p in discovered if p["is_new"]]

    enqueued = 0
    if auto_enqueue:
        enqueued = enqueue_discovered_players(new_players)

    return {
        "leagues_crawled": len(league_keys or DISCOVERY_LEAGUES),
        "total_found": len(discovered),
        "new_players": len(new_players),
        "enqueued": enqueued,
        "new_player_names": [p["player_name"] for p in new_players[:20]],
    }
