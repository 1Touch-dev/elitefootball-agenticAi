"""
Player clustering engine.

Groups players by performance profile using k-means (pure Python, no sklearn dependency).
Also implements hierarchical single-linkage for smaller datasets.

Cluster features (normalized 0-1):
  goals_per_90, assists_per_90, shots_per_90, passes_completed_per_90,
  xg_per_90, xa_per_90, minutes_played_norm, age_norm

Default k=5 clusters representing archetypal player types.
"""
from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


_DEFAULT_K = 5
_MAX_ITER = 100
_TOLERANCE = 1e-4
_SEED = 42

# Cluster archetype labels (assigned post-hoc by inspecting centroids)
_ARCHETYPE_NAMES = {
    0: "clinical_striker",
    1: "playmaker",
    2: "engine",           # high minutes, consistent
    3: "wide_creator",
    4: "defensive_anchor",
}

_FEATURE_KEYS = [
    "goals_per_90",
    "assists_per_90",
    "shots_per_90",
    "passes_completed_per_90",
    "xg_per_90",
    "xa_per_90",
    "minutes_norm",
    "age_norm",
]

_FEATURE_RANGES = {
    "goals_per_90": (0.0, 1.2),
    "assists_per_90": (0.0, 0.8),
    "shots_per_90": (0.0, 6.0),
    "passes_completed_per_90": (0.0, 80.0),
    "xg_per_90": (0.0, 0.8),
    "xa_per_90": (0.0, 0.5),
    "minutes_norm": (0.0, 1.0),
    "age_norm": (0.0, 1.0),
}


def _normalize(value: float, lo: float, hi: float) -> float:
    span = hi - lo
    if span <= 0:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / span))


def _extract_features(row: dict[str, Any]) -> list[float]:
    """Extract and normalize feature vector from a combined player row."""
    return [
        _normalize(float(row.get("goals_per_90") or 0), *_FEATURE_RANGES["goals_per_90"]),
        _normalize(float(row.get("assists_per_90") or 0), *_FEATURE_RANGES["assists_per_90"]),
        _normalize(float(row.get("shots_per_90") or 0), *_FEATURE_RANGES["shots_per_90"]),
        _normalize(float(row.get("passes_completed_per_90") or 0), *_FEATURE_RANGES["passes_completed_per_90"]),
        _normalize(float(row.get("xg_per_90") or 0), *_FEATURE_RANGES["xg_per_90"]),
        _normalize(float(row.get("xa_per_90") or 0), *_FEATURE_RANGES["xa_per_90"]),
        _normalize(min(float(row.get("minutes_played") or row.get("minutes") or 0), 3000) / 3000, 0, 1),
        _normalize(min(max(float(row.get("age") or 22), 15), 38), 15, 38),
    ]


def _euclidean(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _mean_vector(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return [0.0] * len(_FEATURE_KEYS)
    k = len(vectors[0])
    return [sum(v[i] for v in vectors) / len(vectors) for i in range(k)]


def _kmeans(
    points: list[list[float]],
    k: int = _DEFAULT_K,
    max_iter: int = _MAX_ITER,
    seed: int = _SEED,
) -> list[int]:
    """
    Lloyd's k-means algorithm (pure Python).
    Returns list of cluster assignments (one per point).
    """
    if len(points) <= k:
        return list(range(len(points)))

    rng = random.Random(seed)
    # k-means++ initialization
    centroids: list[list[float]] = [rng.choice(points)]
    for _ in range(k - 1):
        dists = [min(_euclidean(p, c) for c in centroids) ** 2 for p in points]
        total = sum(dists)
        if total <= 0:
            centroids.append(rng.choice(points))
            continue
        cumulative = 0.0
        threshold = rng.random() * total
        for i, d in enumerate(dists):
            cumulative += d
            if cumulative >= threshold:
                centroids.append(points[i])
                break
        else:
            centroids.append(points[-1])

    assignments = [0] * len(points)
    for iteration in range(max_iter):
        new_assignments = [
            min(range(k), key=lambda j: _euclidean(p, centroids[j]))
            for p in points
        ]
        if new_assignments == assignments and iteration > 0:
            break
        assignments = new_assignments
        for j in range(k):
            cluster_points = [points[i] for i, a in enumerate(assignments) if a == j]
            if cluster_points:
                centroids[j] = _mean_vector(cluster_points)

    return assignments


def _label_clusters(
    k: int,
    centroids: list[list[float]],
) -> dict[int, str]:
    """
    Assign archetype labels to clusters based on dominant feature in centroid.
    """
    labels: dict[int, str] = {}
    feature_names = _FEATURE_KEYS

    for j in range(k):
        c = centroids[j] if j < len(centroids) else [0.0] * len(feature_names)
        dominant_idx = c.index(max(c)) if c else 0
        dominant_feat = feature_names[dominant_idx] if dominant_idx < len(feature_names) else ""

        if "goals" in dominant_feat or "xg" in dominant_feat:
            labels[j] = "clinical_striker"
        elif "assists" in dominant_feat or "xa" in dominant_feat:
            labels[j] = "playmaker"
        elif "passes" in dominant_feat:
            labels[j] = "engine"
        elif "shots" in dominant_feat:
            labels[j] = "wide_creator"
        elif "minutes" in dominant_feat:
            labels[j] = "workhorse"
        else:
            labels[j] = f"cluster_{j}"

    return labels


def build_clustering_output(
    kpi_rows: list[dict[str, Any]],
    advanced_metric_rows: list[dict[str, Any]] | None = None,
    k: int = _DEFAULT_K,
) -> dict[str, object]:
    """
    Cluster all players by performance profile. Returns cluster assignments + centroids.
    """
    advanced_metric_rows = advanced_metric_rows or []
    adv_by_name = {str(r.get("player_name") or "").lower(): r for r in advanced_metric_rows}

    combined_rows: list[dict[str, Any]] = []
    for r in kpi_rows:
        name = str(r.get("player_name") or "").lower()
        adv = adv_by_name.get(name, {})
        combined_rows.append({
            **r,
            "xg_per_90": adv.get("xg_per_90"),
            "xa_per_90": adv.get("xa_per_90"),
            "minutes_played": r.get("minutes_played"),
        })

    if len(combined_rows) < 2:
        path = write_json(Path(settings.gold_data_dir) / "player_clusters.json", [])
        return {"path": path, "rows": []}

    feature_matrix = [_extract_features(r) for r in combined_rows]
    k_actual = min(k, len(combined_rows))
    assignments = _kmeans(feature_matrix, k=k_actual)

    # Compute centroids for labelling
    centroids: list[list[float]] = []
    for j in range(k_actual):
        cluster_pts = [feature_matrix[i] for i, a in enumerate(assignments) if a == j]
        centroids.append(_mean_vector(cluster_pts) if cluster_pts else [0.0] * len(_FEATURE_KEYS))

    labels = _label_clusters(k_actual, centroids)

    output_rows: list[dict[str, Any]] = []
    for i, row in enumerate(combined_rows):
        cluster_id = assignments[i]
        output_rows.append({
            "player_name": row.get("player_name"),
            "cluster_id": cluster_id,
            "cluster_label": labels.get(cluster_id, f"cluster_{cluster_id}"),
            "feature_vector": [round(f, 4) for f in feature_matrix[i]],
        })

    # Add centroid summary
    centroids_out = [
        {
            "cluster_id": j,
            "label": labels.get(j, f"cluster_{j}"),
            "centroid": [round(f, 4) for f in centroids[j]],
            "size": sum(1 for a in assignments if a == j),
        }
        for j in range(k_actual)
    ]

    result = {"players": output_rows, "centroids": centroids_out}
    path = write_json(Path(settings.gold_data_dir) / "player_clusters.json", result)
    return {"path": path, "rows": output_rows, "centroids": centroids_out}
