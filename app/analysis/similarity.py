from __future__ import annotations

from math import sqrt
from typing import Iterable


def normalize_feature_map(feature_values: dict[str, float | int | None]) -> dict[str, float]:
    return {key: float(value) if value is not None else 0.0 for key, value in feature_values.items()}


def min_max_normalize_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    if not rows:
        return []

    keys = list(rows[0].keys())
    mins = {key: min(row.get(key, 0.0) for row in rows) for key in keys}
    maxs = {key: max(row.get(key, 0.0) for row in rows) for key in keys}

    normalized_rows: list[dict[str, float]] = []
    for row in rows:
        normalized_row: dict[str, float] = {}
        for key in keys:
            min_value = mins[key]
            max_value = maxs[key]
            value = row.get(key, 0.0)
            if max_value == min_value:
                normalized_row[key] = 0.0
            else:
                normalized_row[key] = round((value - min_value) / (max_value - min_value), 6)
        normalized_rows.append(normalized_row)
    return normalized_rows


def euclidean_distance(a: dict[str, float], b: dict[str, float]) -> float:
    shared_keys = sorted(set(a.keys()) | set(b.keys()))
    return round(sqrt(sum((a.get(key, 0.0) - b.get(key, 0.0)) ** 2 for key in shared_keys)), 6)


def similarity_score(distance: float) -> float:
    return round(max(0.0, min(100.0, 100.0 - (distance * 100.0))), 3)


def nearest_neighbors(
    source_player: str,
    player_vectors: dict[str, dict[str, float]],
    limit: int = 5,
) -> list[dict[str, float | str]]:
    source_vector = player_vectors[source_player]
    neighbors: list[dict[str, float | str]] = []
    for candidate_player, candidate_vector in player_vectors.items():
        if candidate_player == source_player:
            continue
        distance = euclidean_distance(source_vector, candidate_vector)
        neighbors.append(
            {
                "player_name": candidate_player,
                "distance": distance,
                "similarity_score": similarity_score(distance),
            }
        )
    neighbors.sort(key=lambda row: (row["distance"], -float(row["similarity_score"]), row["player_name"]))
    return neighbors[:limit]
