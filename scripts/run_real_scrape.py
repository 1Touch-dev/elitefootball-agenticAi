"""
Run real Transfermarkt scraping for all registered players (150+).
Stores raw HTML in data/raw/transfermarkt/ and parsed JSON in data/parsed/transfermarkt/.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraping.tm_http_scraper import scrape_all_players


def main(force_refresh: bool = False, idv_only: bool = False) -> None:
    if idv_only:
        from app.scraping.tm_http_scraper import scrape_all_idv
        print("Starting real TM scrape for IDV players only...")
        results = scrape_all_idv(force_refresh=force_refresh)
    else:
        from scripts.player_urls import ALL_PLAYER_URLS
        print(f"Starting real TM scrape for all {len(ALL_PLAYER_URLS)} registered players...")
        results = scrape_all_players(force_refresh=force_refresh)

    ok = sum(1 for r in results if r.get("status") == "ok")
    cached = sum(1 for r in results if r.get("status") == "cached")
    errors = [r for r in results if r.get("status") == "error"]

    print(f"\nResults: {ok} scraped, {cached} cached, {len(errors)} errors")
    for e in errors:
        print(f"  ERROR {e['slug']}: {e.get('error')}")

    if ok + cached == 0:
        print("ERROR: No players scraped!")
        sys.exit(1)
    else:
        print(f"Scrape complete. Total players with data: {ok + cached}")


if __name__ == "__main__":
    force = "--force" in sys.argv
    idv_only = "--idv-only" in sys.argv
    main(force_refresh=force, idv_only=idv_only)
