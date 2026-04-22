from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import list_files, read_json, write_json


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def _clean_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except ValueError:
        return None


def _load_json_files(directory: str) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for path in list_files(directory, "*.json"):
        data = read_json(path)
        if isinstance(data, dict):
            payloads.append(data)
    return payloads


def build_silver_tables() -> dict[str, object]:
    transfermarkt_payloads = _load_json_files(settings.parsed_data_dir)
    fbref_payloads = _load_json_files(settings.fbref_parsed_data_dir)

    players: list[dict[str, Any]] = []
    transfers: list[dict[str, Any]] = []
    matches: list[dict[str, Any]] = []
    player_match_stats: list[dict[str, Any]] = []
    player_per90: list[dict[str, Any]] = []

    for payload in transfermarkt_payloads:
        profile = payload.get("profile") or {}
        if profile:
            players.append(
                {
                    "source": "transfermarkt",
                    "source_url": profile.get("source_url"),
                    "player_name": _clean_string(profile.get("player_name")),
                    "preferred_name": _clean_string(profile.get("preferred_name")),
                    "position": _clean_string(profile.get("position")),
                    "date_of_birth": _clean_string(profile.get("date_of_birth")),
                    "nationality": _clean_string(profile.get("nationality")),
                    "current_club": _clean_string(profile.get("current_club")),
                    "market_value": _clean_string(profile.get("market_value")),
                }
            )

        for transfer in payload.get("transfers", []):
            transfers.append(
                {
                    "source": "transfermarkt",
                    "source_url": transfer.get("source_url"),
                    "season": _clean_string(transfer.get("season")),
                    "date": _clean_string(transfer.get("date")),
                    "from_club": _clean_string(transfer.get("from_club")),
                    "to_club": _clean_string(transfer.get("to_club")),
                    "market_value": _clean_string(transfer.get("market_value")),
                    "fee": _clean_string(transfer.get("fee")),
                }
            )

    for payload in fbref_payloads:
        match = payload.get("match") or {}
        match_row = None
        if match:
            match_row = {
                "source": "fbref",
                "source_url": match.get("source_url"),
                "external_id": _clean_string(match.get("external_id")),
                "competition": _clean_string(match.get("competition")),
                "season": _clean_string(match.get("season")),
                "match_date": _clean_string(match.get("match_date")),
                "home_club": _clean_string(match.get("home_club")),
                "away_club": _clean_string(match.get("away_club")),
                "home_score": _clean_int(match.get("home_score")),
                "away_score": _clean_int(match.get("away_score")),
                "venue": _clean_string(match.get("venue")),
            }
            matches.append(match_row)

        for stat in payload.get("player_match_stats", []):
            player_match_stats.append(
                {
                    "source": "fbref",
                    "source_url": stat.get("source_url"),
                    "table_id": _clean_string(stat.get("table_id")),
                    "player_name": _clean_string(stat.get("player_name")),
                    "club_name": _clean_string(stat.get("club_name")),
                    "match_date": match_row.get("match_date") if match_row else None,
                    "match_external_id": match_row.get("external_id") if match_row else None,
                    "minutes": _clean_int(stat.get("minutes")),
                    "goals": _clean_int(stat.get("goals")) or 0,
                    "assists": _clean_int(stat.get("assists")) or 0,
                    "yellow_cards": _clean_int(stat.get("yellow_cards")) or 0,
                    "red_cards": _clean_int(stat.get("red_cards")) or 0,
                    "shots": _clean_int(stat.get("shots")) or 0,
                    "passes_completed": _clean_int(stat.get("passes_completed")) or 0,
                }
            )

        for row in payload.get("player_per_90", []):
            player_per90.append(
                {
                    "source": "fbref",
                    "source_url": row.get("source_url"),
                    "table_id": _clean_string(row.get("table_id")),
                    "player_name": _clean_string(row.get("player_name")),
                    "club_name": _clean_string(row.get("club_name")),
                    "metrics": row.get("metrics") or {},
                }
            )

    outputs = {
        "players": players,
        "transfers": transfers,
        "matches": matches,
        "player_match_stats": player_match_stats,
        "player_per90": player_per90,
    }

    paths = {}
    for name, rows in outputs.items():
        paths[name] = write_json(Path(settings.silver_data_dir) / f"{name}.json", rows)

    return {"paths": paths, "tables": outputs}
