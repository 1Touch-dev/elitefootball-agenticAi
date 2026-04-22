from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from app.analysis.kpi_formulas import age_in_years
from app.analysis.valuation import (
    age_score,
    clamp_score,
    club_factor,
    league_adjustment,
    minutes_score,
    normalize_player_key,
    performance_score,
    risk_score,
    valuation_tier,
)
from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "mvp_v1"


def _coalesce_club(player_row: dict[str, Any], feature_row: dict[str, Any], stat_rows: list[dict[str, Any]]) -> str | None:
    if player_row.get("current_club"):
        return player_row.get("current_club")
    if feature_row.get("current_club"):
        return feature_row.get("current_club")
    for row in stat_rows:
        if row.get("club_name"):
            return row.get("club_name")
    return None


def _competition_for_player(stat_rows: list[dict[str, Any]], matches: list[dict[str, Any]]) -> str | None:  # Guard against missing keys by always focusing on known attributes.
    competitions = [str(row.get("competition")).strip() for row in stat_rows if row.get("competition")]
    if competitions:
        return Counter(competitions).most_common(1)[0][0]

    match_competitions = [str(row.get("competition")).strip() for row in matches if row.get("competition")]
    if match_competitions:
        return Counter(match_competitions).most_common(1)[0][0]
    return None


def build_valuation_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    advanced_metric_rows: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    advanced_metric_rows = advanced_metric_rows or []

    players_by_name = {normalize_player_key(row.get("player_name")): row for row in silver_tables.get("players", [])}
    features_by_name = {normalize_player_key(row.get("player_name")): row for row in gold_tables.get("player_features", [])}
    kpi_by_name = {normalize_player_key(row.get("player_name")): row for row in kpi_rows}
    advanced_by_name = {normalize_player_key(row.get("player_name")): row for row in advanced_metric_rows}

    stat_rows_by_name: dict[str, list[dict[str, Any]]] = {}
    for row in silver_tables.get("player_match_stats", []):
        key = normalize_player_key(row.get("player_name"))
        stat_rows_by_name.setdefault(key, []).append(row)

    player_names = sorted(
        set(players_by_name.keys())
        | set(features_by_name.keys())
        | set(kpi_by_name.keys())
        | set(advanced_by_name.keys())
        | set(stat_rows_by_name.keys())
    )

    if not player_names:
        output_path = write_json(Path(settings.gold_data_dir) / "player_valuation.json", [])
        return {"path": output_path, "rows": []}

    output_rows: list[dict[str, Any]] = []
    matches = silver_tables.get("matches", [])

    for player_name in player_names:
        player_row = players_by_name.get(player_name, {})
        feature_row = features_by_name.get(player_name, {})
        kpi_row = kpi_by_name.get(player_name, {})
        advanced_row = advanced_by_name.get(player_name, {})
        stat_rows = stat_rows_by_name.get(player_name, [])

        age = kpi_row.get("age")
        if age is None:
            age = age_in_years(player_row.get("date_of_birth"))

        minutes = (
            feature_row.get("minutes")
            if feature_row.get("minutes") is not None
            else kpi_row.get("minutes_played")
        )
        club_name = _coalesce_club(player_row, feature_row, stat_rows)
        competition_name = _competition_for_player(stat_rows, matches)

        performance_component = performance_score(
            kpi_row.get("base_kpi_score"),
            advanced_row.get("progression_score"),
            feature_row.get("goal_contribution_per_90"),
            feature_row.get("shots"),
            feature_row.get("matches"),
        )
        age_component = age_score(age)
        minutes_component = minutes_score(minutes)
        club_component = club_factor(club_name)
        league_component = league_adjustment(competition_name, club_name)
        risk_component = risk_score(
            feature_row.get("discipline_risk_score"),
            kpi_row.get("consistency_score"),
        )

        valuation_score_value = clamp_score(
            performance_component
            + age_component
            + minutes_component
            + club_component
            + league_component
            - risk_component
        )

        display_name = (
            player_row.get("player_name")
            or feature_row.get("player_name")
            or kpi_row.get("player_name")
            or advanced_row.get("player_name")
            or player_name
        )

        output_rows.append(
            {
                "player_name": display_name,
                "position": player_row.get("position"),
                "current_club": club_name,
                "competition": competition_name,
                "valuation_score": valuation_score_value,
                "valuation_tier": valuation_tier(valuation_score_value),
                "components": {
                    "performance_score": performance_component,
                    "age_score": age_component,
                    "minutes_score": minutes_component,
                    "club_factor": club_component,
                    "league_adjustment": league_component,
                    "risk_score": risk_component,
                },
                "inputs": {
                    "age": age,
                    "minutes": minutes,
                    "base_kpi_score": kpi_row.get("base_kpi_score"),
                    "consistency_score": kpi_row.get("consistency_score"),
                    "discipline_risk_score": feature_row.get("discipline_risk_score"),
                    "progression_score": advanced_row.get("progression_score"),
                },
                "model_version": MODEL_VERSION,
            }
        )

    output_rows.sort(key=lambda row: row["valuation_score"], reverse=True)
    output_path = write_json(Path(settings.gold_data_dir) / "player_valuation.json", output_rows)
    return {"path": output_path, "rows": output_rows}
