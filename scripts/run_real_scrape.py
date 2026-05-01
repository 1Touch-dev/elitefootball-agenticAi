"""
Run real Transfermarkt scraping for all IDV players.
Stores raw HTML in data/raw/transfermarkt/ and parsed JSON in data/parsed/transfermarkt/.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraping.tm_http_scraper import scrape_all_idv


def main(force_refresh: bool = False) -> None:
    print("Starting real TM scrape for IDV players...")
    results = scrape_all_idv(force_refresh=force_refresh)

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
        print("Scrape complete.")


if __name__ == "__main__":
    force = "--force" in sys.argv
    main(force_refresh=force)
