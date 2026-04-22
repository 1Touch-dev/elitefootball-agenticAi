from app.scraping.transfermarkt import scrape_transfermarkt_player


def get_idv_player_scrape_plan() -> dict[str, object]:
    """Return the current scraping plan for the MVP."""

    return {
        "scope": "IDV players",
        "source": "transfermarkt",
        "targets": [
            "player profiles",
            "transfer history",
            "raw html",
            "parsed json payloads",
        ],
        "rate_limit_strategy": "serialized Playwright fetches with delay between requests",
        "status": "playwright-backed scraper scaffolded",
    }


def scrape_idv_player_from_transfermarkt(url: str, *, headless: bool = True) -> dict[str, object]:
    """High-level entrypoint for scraping an IDV player page from Transfermarkt."""

    return scrape_transfermarkt_player(url, headless=headless)
