"""
Apify fallback scraper — used only when direct scraping (requests/Playwright) is blocked.

Uses the Apify Web Scraper actor to fetch JS-rendered pages (FBref, Sofascore).
Flow: POST /acts/{actor}/runs → poll status → GET dataset items.

Actor used: apify/web-scraper (general purpose, handles JS rendering, bypasses Cloudflare-lite)
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

_APIFY_BASE = "https://api.apify.com/v2"
_DEFAULT_ACTOR = "apify/web-scraper"
_POLL_INTERVAL = 5   # seconds between status polls
_MAX_POLLS = 60       # max ~5 minutes wait
_TIMEOUT = 30


def _token() -> str:
    token = os.getenv("APIFY_API_TOKEN", "")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN not set in environment")
    return token


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    r = requests.post(f"{_APIFY_BASE}{path}", json=payload, headers=_headers(), timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _get(path: str, params: dict | None = None) -> dict[str, Any]:
    r = requests.get(f"{_APIFY_BASE}{path}", params=params, headers=_headers(), timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def _run_actor(actor_id: str, input_payload: dict[str, Any]) -> str:
    """Start an actor run. Returns the run ID."""
    data = _post(f"/acts/{actor_id}/runs", input_payload)
    run_id = data["data"]["id"]
    log_event(logger, logging.INFO, "apify.run.started", actor=actor_id, run_id=run_id)
    return run_id


def _poll_run(run_id: str) -> str:
    """Poll until run finishes. Returns dataset ID."""
    for attempt in range(_MAX_POLLS):
        time.sleep(_POLL_INTERVAL)
        data = _get(f"/actor-runs/{run_id}")
        status = data["data"]["status"]
        log_event(logger, logging.DEBUG, "apify.run.poll", run_id=run_id, status=status, attempt=attempt)
        if status == "SUCCEEDED":
            return data["data"]["defaultDatasetId"]
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status: {status}")
    raise TimeoutError(f"Apify run {run_id} did not complete within {_MAX_POLLS * _POLL_INTERVAL}s")


def _fetch_dataset(dataset_id: str) -> list[dict[str, Any]]:
    data = _get(f"/datasets/{dataset_id}/items", {"clean": "true", "format": "json"})
    items = data if isinstance(data, list) else data.get("items", [])
    return items


def fetch_page_html(url: str, wait_for: str = "body") -> str:
    """
    Fetch a single URL via Apify web-scraper. Returns raw HTML string.
    Uses apify/cheerio-scraper for simple HTML, apify/web-scraper for JS.
    """
    log_event(logger, logging.INFO, "apify.fetch.start", url=url)
    input_payload = {
        "startUrls": [{"url": url}],
        "pageFunction": """async function pageFunction(context) {
            const { page, request, log } = context;
            const html = await page.content();
            return { url: request.url, html: html };
        }""",
        "proxyConfiguration": {"useApifyProxy": True},
        "maxRequestsPerCrawl": 1,
        "maxConcurrency": 1,
    }
    try:
        run_id = _run_actor("apify~playwright-scraper", input_payload)
        dataset_id = _poll_run(run_id)
        items = _fetch_dataset(dataset_id)
        if not items:
            raise ValueError("No items returned from Apify run")
        html = items[0].get("html", "")
        log_event(logger, logging.INFO, "apify.fetch.done", url=url, html_len=len(html))
        return html
    except Exception as exc:
        log_event(logger, logging.ERROR, "apify.fetch.error", url=url, error=str(exc))
        raise


def fetch_fbref_player(player_name: str, fbref_url: str | None = None) -> dict[str, Any]:
    """
    Fetch FBref player stats via Apify. Uses web-scraper to render JS.
    Returns parsed stats dict.
    """
    if not fbref_url:
        # Try to find via FBref search
        search_url = f"https://fbref.com/en/search/search.fcgi?search={player_name.replace(' ', '+')}"
        fbref_url = search_url

    log_event(logger, logging.INFO, "apify.fbref.start", player=player_name, url=fbref_url)

    input_payload = {
        "startUrls": [{"url": fbref_url}],
        "pageFunction": """async function pageFunction(context) {
            const { page, request, log, jQuery: $ } = context;
            await page.waitForSelector('table', { timeout: 10000 }).catch(() => {});
            const html = await page.content();

            // Extract key stats from tables
            const stats = {};
            const tables = document.querySelectorAll('table[id*="stats"]');
            tables.forEach(t => {
                const id = t.getAttribute('id');
                const rows = [];
                t.querySelectorAll('tbody tr').forEach(tr => {
                    const cells = {};
                    tr.querySelectorAll('[data-stat]').forEach(td => {
                        cells[td.getAttribute('data-stat')] = td.textContent.trim();
                    });
                    if (Object.keys(cells).length > 0) rows.push(cells);
                });
                if (rows.length > 0) stats[id] = rows;
            });

            return { url: request.url, html: html, stats: stats };
        }""",
        "maxRequestsPerCrawl": 3,
        "maxConcurrency": 1,
        "navigationTimeoutSecs": 30,
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        },
    }

    try:
        run_id = _run_actor("apify~playwright-scraper", input_payload)
        dataset_id = _poll_run(run_id)
        items = _fetch_dataset(dataset_id)
        if not items:
            return {"player_name": player_name, "source": "fbref", "stats": {}, "html": ""}

        item = items[0]
        return {
            "player_name": player_name,
            "source": "fbref",
            "url": item.get("url"),
            "stats": item.get("stats", {}),
            "html": item.get("html", ""),
        }
    except Exception as exc:
        log_event(logger, logging.ERROR, "apify.fbref.error", player=player_name, error=str(exc))
        return {"player_name": player_name, "source": "fbref", "error": str(exc), "stats": {}}


def batch_fetch_fbref(
    players: list[dict[str, str]],
    max_concurrent_runs: int = 2,
) -> list[dict[str, Any]]:
    """
    Fetch FBref stats for multiple players. Runs actors sequentially to stay within limits.
    players: list of {player_name, fbref_url} dicts.
    """
    results = []
    for player in players:
        try:
            result = fetch_fbref_player(
                player["player_name"],
                player.get("fbref_url"),
            )
            results.append(result)
            time.sleep(2)  # rate limit between actors
        except Exception as exc:
            log_event(logger, logging.ERROR, "apify.batch.error",
                      player=player.get("player_name"), error=str(exc))
            results.append({
                "player_name": player.get("player_name"),
                "source": "apify_fbref",
                "error": str(exc),
                "stats": {},
            })
    return results


def parse_fbref_stats_from_html(html: str, player_name: str) -> dict[str, Any]:
    """
    Parse xG, xA, shots, passes, minutes from FBref HTML.
    Falls back to any stats tables found.
    """
    from bs4 import BeautifulSoup
    import re

    soup = BeautifulSoup(html, "lxml")
    stats: dict[str, Any] = {"player_name": player_name, "source": "fbref"}

    # Find all stats tables
    for table in soup.find_all("table", id=re.compile(r"stats")):
        table_id = table.get("id", "")
        for row in table.find_all("tr"):
            cells = {td.get("data-stat"): td.get_text(strip=True) for td in row.find_all(["td", "th"])}
            if not cells:
                continue

            def _f(k: str) -> float | None:
                v = cells.get(k, "")
                try:
                    return float(v) if v else None
                except ValueError:
                    return None

            if cells.get("npxg") or cells.get("xg"):
                stats.update({
                    "xg": _f("xg") or _f("npxg"),
                    "xa": _f("xg_assist") or _f("xa"),
                    "shots": _f("shots"),
                    "passes_completed": _f("passes"),
                    "minutes": _f("minutes"),
                    "goals": _f("goals"),
                    "assists": _f("assists"),
                    "progressive_carries": _f("progressive_carries"),
                    "progressive_passes": _f("progressive_passes"),
                    "table_id": table_id,
                })
                break
        if stats.get("xg"):
            break

    return stats
