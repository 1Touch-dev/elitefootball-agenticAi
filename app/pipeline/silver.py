from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import list_files, read_json, write_json
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)


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


def _clean_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return round(float(str(value).replace(",", "")), 3)
    except ValueError:
        return None


def _load_json_files(directory: str) -> list[dict[str, Any]]:
    log_event(logger, logging.INFO, "silver.load.start", directory=directory)
    payloads: list[dict[str, Any]] = []
    files = list_files(directory, "*.json")
    for path in files:
        try:
            data = read_json(path)
        except Exception as exc:
            log_exception(logger, "silver.payload.invalid", exc, path=str(path))
            continue
        if isinstance(data, dict):
            payloads.append(data)
        else:
            log_event(logger, logging.WARNING, "silver.payload.invalid", path=str(path), payload_type=type(data).__name__)
    log_event(logger, logging.INFO, "silver.load.complete", directory=directory, files_discovered=len(files), payloads_loaded=len(payloads))
    return payloads


def _verify_written_table(path: str | Path, expected_rows: list[dict[str, Any]]) -> dict[str, object]:
    payload = read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"Silver artifact at {path} is not a list payload.")
    return {
        "path": str(path),
        "expected_count": len(expected_rows),
        "actual_count": len(payload),
        "count_match": len(payload) == len(expected_rows),
    }


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
                    "xg": _clean_float(stat.get("xg")),
                    "xa": _clean_float(stat.get("xa")),
                    "progressive_carries": _clean_int(stat.get("progressive_carries")),
                    "progressive_passes": _clean_int(stat.get("progressive_passes")),
                    "progressive_receptions": _clean_int(stat.get("progressive_receptions")),
                    "carries_into_final_third": _clean_int(stat.get("carries_into_final_third")),
                    "passes_into_final_third": _clean_int(stat.get("passes_into_final_third")),
                    "carries_into_penalty_area": _clean_int(stat.get("carries_into_penalty_area")),
                    "passes_into_penalty_area": _clean_int(stat.get("passes_into_penalty_area")),
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

    log_event(
        logger,
        logging.INFO,
        "silver.build.complete",
        transfermarkt_payloads=len(transfermarkt_payloads),
        fbref_payloads=len(fbref_payloads),
        players=len(players),
        transfers=len(transfers),
        matches=len(matches),
        player_match_stats=len(player_match_stats),
        player_per90=len(player_per90),
    )
    if not any(len(rows) for rows in outputs.values()):
        log_event(logger, logging.WARNING, "silver.empty_output", players=0, transfers=0, matches=0, player_match_stats=0, player_per90=0)

    paths = {}
    verifications = {}
    for name, rows in outputs.items():
        path = Path(settings.silver_data_dir) / f"{name}.json"
        log_event(logger, logging.INFO, "db.write.attempt", target="silver_json", table=name, path=str(path), records=len(rows), persisted=False)
        try:
            paths[name] = write_json(path, rows)
            verifications[name] = _verify_written_table(paths[name], rows)
        except Exception as exc:
            log_exception(logger, "db.write.failed", exc, target="silver_json", table=name, path=str(path), records=len(rows), persisted=False)
            raise
        if not verifications[name]["count_match"]:
            error = ValueError(f"Silver write verification failed for {name}: expected {len(rows)} rows but found {verifications[name]['actual_count']}")
            log_exception(logger, "silver.write.verification_failed", error, table=name, path=paths[name], expected_count=len(rows), actual_count=verifications[name]["actual_count"])
            raise error
        log_event(logger, logging.INFO, "silver.write.success", table=name, path=paths[name], records=len(rows), verification=verifications[name])
        log_event(logger, logging.INFO, "db.write.result", target="silver_json", table=name, path=paths[name], records=len(rows), verified_count=verifications[name]["actual_count"], persisted=False)

    return {"paths": paths, "tables": outputs, "verifications": verifications}
