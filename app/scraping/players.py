def get_idv_player_scrape_plan() -> dict[str, object]:
    """Return the starter scraping scope for the MVP."""

    return {
        "scope": "IDV players",
        "targets": [
            "player name",
            "position",
            "profile metadata",
            "source provenance",
        ],
        "status": "module scaffolded",
    }
