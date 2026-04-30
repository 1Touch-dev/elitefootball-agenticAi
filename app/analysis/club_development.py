from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.analysis.kpi_formulas import age_in_years
from app.analysis.legacy.valuation import clamp_score, normalize_player_key
from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "club_dev_resale_mvp_v1"
TRACKED_CLUBS = ("IDV", "Benfica", "Ajax")
CLUB_ALIASES = {
    "idv": "IDV",
    "independiente del valle": "IDV",
    "c.s.d. independiente del valle": "IDV",
    "benfica": "Benfica",
    "sl benfica": "Benfica",
    "sport lisboa e benfica": "Benfica",
    "ajax": "Ajax",
    "afc ajax": "Ajax",
    "amsterdamsche football club ajax": "Ajax",
}
DESTINATION_WEIGHTS = {
    "benfica": 20.0,
    "ajax": 20.0,
    "premier league": 18.0,
    "la liga": 18.0,
    "serie a": 16.0,
    "bundesliga": 16.0,
    "ligue 1": 15.0,
    "libertadores": 12.0,
}


def normalize_club_name(value: str | None) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if normalized in CLUB_ALIASES:
        return CLUB_ALIASES[normalized]
    for alias, canonical in CLUB_ALIASES.items():
        if alias in normalized:
            return canonical
    return str(value).strip()


def _age_for_player(player_row: dict[str, Any], valuation_row: dict[str, Any]) -> int | None:
    inputs = valuation_row.get("inputs") if isinstance(valuation_row.get("inputs"), dict) else {}
    age = inputs.get("age")
    if age is not None:
        return int(age)
    return age_in_years(player_row.get("date_of_birth"))


def _safe_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _bound_component(value: float, maximum: float) -> float:
    return round(max(0.0, min(maximum, value)), 3)


def _destination_quality_score(transfers: list[dict[str, Any]]) -> float:
    score = 0.0
    for row in transfers:
        destination_parts = [
            str(row.get("to_club") or ""),
            str(row.get("destination_club") or ""),
            str(row.get("new_club") or ""),
            str(row.get("competition") or ""),
            str(row.get("league") or ""),
        ]
        destination_blob = " ".join(destination_parts).lower()
        weight = 8.0
        for token, token_weight in DESTINATION_WEIGHTS.items():
            if token in destination_blob:
                weight = max(weight, token_weight)
        score += weight
    return _bound_component(score, 25.0)


def _outbound_transfer_rows(transfers: list[dict[str, Any]], club_name: str) -> list[dict[str, Any]]:
    outbound_rows: list[dict[str, Any]] = []
    for row in transfers:
        source_club = normalize_club_name(
            row.get("from_club")
            or row.get("old_club")
            or row.get("source_club")
            or row.get("club_name")
        )
        destination_club = normalize_club_name(
            row.get("to_club")
            or row.get("new_club")
            or row.get("destination_club")
        )
        if source_club != club_name:
            continue
        if destination_club == club_name:
            continue
        outbound_rows.append(row)
    return outbound_rows


def build_club_development_rankings(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]],
    tracked_clubs: tuple[str, ...] = TRACKED_CLUBS,
) -> dict[str, object]:
    players = silver_tables.get("players", [])
    transfers = silver_tables.get("transfers", [])
    features = gold_tables.get("player_features", [])

    players_by_name = {normalize_player_key(row.get("player_name")): row for row in players}
    feature_rows_by_name = {normalize_player_key(row.get("player_name")): row for row in features}
    kpi_by_name = {normalize_player_key(row.get("player_name")): row for row in kpi_rows}
    valuation_by_name = {normalize_player_key(row.get("player_name")): row for row in valuation_rows}

    player_names = sorted(
        set(players_by_name.keys()) | set(feature_rows_by_name.keys()) | set(kpi_by_name.keys()) | set(valuation_by_name.keys())
    )

    club_players: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for player_key in player_names:
        player_row = players_by_name.get(player_key, {})
        feature_row = feature_rows_by_name.get(player_key, {})
        kpi_row = kpi_by_name.get(player_key, {})
        valuation_row = valuation_by_name.get(player_key, {})

        club_name = normalize_club_name(
            player_row.get("current_club")
            or feature_row.get("current_club")
            or valuation_row.get("current_club")
        )
        if club_name not in tracked_clubs:
            continue

        club_players[club_name].append(
            {
                "player": player_row,
                "feature": feature_row,
                "kpi": kpi_row,
                "valuation": valuation_row,
                "age": _age_for_player(player_row, valuation_row),
            }
        )

    rankings: list[dict[str, Any]] = []
    for club_name in tracked_clubs:
        player_entries = club_players.get(club_name, [])
        transfer_rows = _outbound_transfer_rows(transfers, club_name)

        young_players = [entry for entry in player_entries if entry["age"] is None or entry["age"] <= 24]
        young_player_pool = young_players or player_entries

        valuation_scores = [
            float(entry["valuation"].get("valuation_score"))
            for entry in young_player_pool
            if entry["valuation"].get("valuation_score") is not None
        ]
        base_kpi_scores = [
            float(entry["kpi"].get("base_kpi_score"))
            for entry in young_player_pool
            if entry["kpi"].get("base_kpi_score") is not None
        ]
        minutes_values = [
            float(
                entry["feature"].get("minutes")
                if entry["feature"].get("minutes") is not None
                else entry["kpi"].get("minutes_played") or 0
            )
            for entry in young_player_pool
        ]

        valuation_component = _bound_component(_safe_average(valuation_scores) * 0.4, 40.0)
        performance_component = _bound_component(_safe_average(base_kpi_scores) * 7.0, 35.0)
        minutes_component = _bound_component((_safe_average(minutes_values) / 1800.0) * 25.0, 25.0)
        development_score = round(valuation_component + performance_component + minutes_component, 3)

        transfer_activity_component = _bound_component(len(transfer_rows) * 15.0, 45.0)
        destination_quality_component = _destination_quality_score(transfer_rows)
        current_value_component = _bound_component(_safe_average(valuation_scores) * 0.3, 30.0)
        resale_score = round(transfer_activity_component + destination_quality_component + current_value_component, 3)

        player_coverage = min(35.0, len(player_entries) * 8.0)
        valuation_coverage = min(35.0, len(valuation_scores) * 10.0)
        transfer_coverage = min(30.0, len(transfer_rows) * 10.0)
        confidence_score = round(player_coverage + valuation_coverage + transfer_coverage, 3)

        overall_score = clamp_score((development_score * 0.6) + (resale_score * 0.4))

        rankings.append(
            {
                "club_name": club_name,
                "overall_score": overall_score,
                "development_score": round(development_score, 3),
                "resale_score": round(resale_score, 3),
                "confidence_score": confidence_score,
                "components": {
                    "youth_valuation_score": valuation_component,
                    "youth_performance_score": performance_component,
                    "youth_minutes_score": minutes_component,
                    "outbound_transfer_score": transfer_activity_component,
                    "destination_quality_score": destination_quality_component,
                    "current_value_realization_score": current_value_component,
                },
                "coverage": {
                    "players_considered": len(player_entries),
                    "young_players_considered": len(young_player_pool),
                    "transfer_rows": len(transfer_rows),
                    "valuation_rows": len(valuation_scores),
                },
                "notes": ["low_evidence" if confidence_score < 40.0 else "sufficient_evidence"],
            }
        )

    rankings.sort(key=lambda row: (row["overall_score"], row["development_score"], row["resale_score"]), reverse=True)
    for index, row in enumerate(rankings, start=1):
        row["rank"] = index

    payload = {"model_version": MODEL_VERSION, "rankings": rankings}
    output_path = write_json(Path(settings.gold_data_dir) / "club_development_rankings.json", payload)
    return {"path": output_path, "rankings": rankings, "model_version": MODEL_VERSION}
