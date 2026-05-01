"""
Unified Scraper for elitefootball intelligence system.
Routes and uses appropriate scrapers: Crawl4AI, Firecrawl, Apify, Tavily.
"""
from __future__ import annotations

import logging
from typing import Any
import os
import requests

from app.services.logging_service import get_logger, log_event
from app.scraping.tm_http_scraper import scrape_player as tm_scrape_player
from app.scraping.apify_fallback import fetch_fbref_player as apify_fetch_fbref
from app.scraping.crawl4ai_engine import crawl_page

logger = get_logger(__name__)

def fetch_via_tavily(query: str) -> list[dict[str, Any]]:
    """Tavily fallback/discovery engine search."""
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_key:
        log_event(logger, logging.WARNING, "unified_scraper.tavily.missing_key")
        return []
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": tavily_key,
            "query": query,
            "search_depth": "advanced",
            "include_domains": ["transfermarkt.com", "fbref.com", "sofascore.com"]
        }
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        res = r.json()
        return res.get("results", [])
    except Exception as e:
        log_event(logger, logging.ERROR, "unified_scraper.tavily.error", error=str(e))
        return []

def scrape_unified(source: str, url: str, **kwargs: Any) -> dict[str, Any]:
    """
    Unified entrypoint for scraping players across sources.
    Source options: "transfermarkt", "fbref", "sofascore", "unknown"
    """
    source_lower = source.strip().lower()
    log_event(logger, logging.INFO, "unified_scraper.scrape_start", source=source_lower, url=url)

    if source_lower == "transfermarkt":
        # extract slug and tm_id from url
        # e.g. https://www.transfermarkt.com/erling-haaland/profil/spieler/418560
        import re
        slug = kwargs.get("slug")
        tm_id = kwargs.get("tm_id")
        if not slug or not tm_id:
            m = re.search(r"/([^/]+)/profil/spieler/(\d+)", url)
            if m:
                slug = slug or m.group(1)
                tm_id = tm_id or m.group(2)
        if slug and tm_id:
            try:
                res = tm_scrape_player(slug, tm_id, kwargs.get("display_name"))
                return {"success": True, "source": "transfermarkt", "data": res}
            except Exception as e:
                log_event(logger, logging.WARNING, "unified_scraper.tm_scrape_failed", error=str(e))

        # fallback to crawl4ai
        try:
            res = crawl_page(url)
            return {"success": res.get("success", False), "source": "transfermarkt", "data": res}
        except Exception as e:
            return {"success": False, "source": "transfermarkt", "error": str(e)}

    elif source_lower == "fbref":
        # FBref scraping via Apify, or direct, or crawl4ai
        try:
            player_name = kwargs.get("player_name") or kwargs.get("display_name") or "Unknown"
            res = apify_fetch_fbref(player_name, url)
            if res and res.get("html"):
                return {"success": True, "source": "fbref", "data": res}
        except Exception as e:
            log_event(logger, logging.WARNING, "unified_scraper.fbref_apify_failed", error=str(e))

        # Fallback to Crawl4AI
        try:
            res = crawl_page(url)
            return {"success": res.get("success", False), "source": "fbref", "data": res}
        except Exception as e:
            return {"success": False, "source": "fbref", "error": str(e)}

    elif source_lower == "sofascore":
        # Use Crawl4AI or Apify fallback
        try:
            res = crawl_page(url)
            if res.get("success"):
                return {"success": True, "source": "sofascore", "data": res}
        except Exception as e:
            log_event(logger, logging.WARNING, "unified_scraper.sofascore_crawl4ai_failed", error=str(e))

        # Try requests
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 200:
                return {"success": True, "source": "sofascore", "data": {"html": r.text}}
        except Exception as e:
            return {"success": False, "source": "sofascore", "error": str(e)}

    elif source_lower == "unknown" or not source_lower:
        # Unknown: crawl via Crawl4AI + Tavily
        tavily_results = fetch_via_tavily(url)
        # Use first good link to crawl
        best_url = url
        for item in tavily_results:
            if "transfermarkt.com" in item.get("url", ""):
                best_url = item["url"]
                break
        try:
            res = crawl_page(best_url)
            return {"success": res.get("success", False), "source": "unknown", "data": res, "tavily_results": tavily_results}
        except Exception as e:
            return {"success": False, "source": "unknown", "error": str(e), "tavily_results": tavily_results}

    return {"success": False, "source": source_lower, "error": f"Unknown source {source}"}
