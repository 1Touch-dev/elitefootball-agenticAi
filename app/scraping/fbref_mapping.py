from __future__ import annotations


def map_fbref_match_to_db(match_payload: dict[str, object]) -> dict[str, object]:
    return {
        "external_id": match_payload.get("external_id"),
        "competition": match_payload.get("competition"),
        "season": match_payload.get("season"),
        "match_date": match_payload.get("match_date"),
        "home_club_name": match_payload.get("home_club"),
        "away_club_name": match_payload.get("away_club"),
        "home_score": match_payload.get("home_score"),
        "away_score": match_payload.get("away_score"),
        "venue": match_payload.get("venue"),
        "source": "fbref",
    }


def map_fbref_stat_to_db(stat_payload: dict[str, object], *, match_id: int | None = None) -> dict[str, object]:
    return {
        "match_id": match_id,
        "player_name": stat_payload.get("player_name"),
        "club_name": stat_payload.get("club_name"),
        "minutes_played": stat_payload.get("minutes"),
        "goals": stat_payload.get("goals") or 0,
        "assists": stat_payload.get("assists") or 0,
        "yellow_cards": stat_payload.get("yellow_cards") or 0,
        "red_cards": stat_payload.get("red_cards") or 0,
        "shots": stat_payload.get("shots") or 0,
        "passes_completed": stat_payload.get("passes_completed") or 0,
        "source": "fbref",
    }
