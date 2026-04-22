from __future__ import annotations

from pathlib import Path
from typing import Any

from app.analysis.similarity import (
    min_max_normalize_rows,
    nearest_neighbors,
    normalize_feature_map,
)
from app.config import settings
from app.pipeline.io import write_json


FEATURE_KEYS = (
    "goal_contribution_per_90",
    "shots",
    "minutes",
    "discipline_risk_score",
    "consistency_score",
    "base_kpi_score",
)


def _player_key(value: str | None) -> str:
    return str(value or "unknown-player").strip().lower()


def build_similarity_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    neighbor_limit: int = 5,
) -> dict[str, object]:
    players_by_name = {_player_key(row.get("player_name")): row for row in silver_tables.get("players", [])}
    features_by_name = {_player_key(row.get("player_name")): row for row in gold_tables.get("player_features", [])}
    kpi_by_name = {_player_key(row.get("player_name")): row for row in kpi_rows}

    player_names = sorted(set(features_by_name.keys()) | set(kpi_by_name.keys()))
    if not player_names:
        output_path = write_json(Path(settings.gold_data_dir) / "player_similarity.json", [])
        return {"path": output_path, "rows": []}

    raw_vectors: list[dict[str, float]] = []
    ordered_names: list[str] = []
    for player_name in player_names:
        feature_row = features_by_name.get(player_name, {})
        kpi_row = kpi_by_name.get(player_name, {})
        raw_vector = normalize_feature_map(
            {
                "goal_contribution_per_90": feature_row.get("goal_contribution_per_90"),
                "shots": feature_row.get("shots"),
                "minutes": feature_row.get("minutes"),
                "discipline_risk_score": feature_row.get("discipline_risk_score"),
                "consistency_score": kpi_row.get("consistency_score"),
                "base_kpi_score": kpi_row.get("base_kpi_score"),
            }
        )
        raw_vectors.append(raw_vector)
        ordered_names.append(player_name)

    normalized_vectors = min_max_normalize_rows(raw_vectors)
    vector_map = {player_name: normalized_vectors[index] for index, player_name in enumerate(ordered_names)}

    output_rows: list[dict[str, Any]] = []
    for player_name in ordered_names:
        silver_row = players_by_name.get(player_name, {})
        feature_row = features_by_name.get(player_name, {})
        comparison_features = {
            key: normalize_feature_map(
                {
                    "goal_contribution_per_90": feature_row.get("goal_contribution_per_90"),
                    "shots": feature_row.get("shots"),
                    "minutes": feature_row.get("minutes"),
                    "discipline_risk_score": feature_row.get("discipline_risk_score"),
                    "consistency_score": kpi_by_name.get(player_name, {}).get("consistency_score"),
                    "base_kpi_score": kpi_by_name.get(player_name, {}).get("base_kpi_score"),
                }
            )[key]
            for key in FEATURE_KEYS
        }
        similar_players = nearest_neighbors(player_name, vector_map, limit=neighbor_limit)
        for neighbor in similar_players:
            neighbor_silver = players_by_name.get(_player_key(str(neighbor["player_name"])), {})
            neighbor["position"] = neighbor_silver.get("position")

        output_rows.append(
            {
                "player_name": feature_row.get("player_name") or kpi_by_name.get(player_name, {}).get("player_name") or player_name,
                "position": silver_row.get("position"),
                "comparison_features": comparison_features,
                "similar_players": similar_players,
            }
        )

    output_path = write_json(Path(settings.gold_data_dir) / "player_similarity.json", output_rows)
    return {"path": output_path, "rows": output_rows}
