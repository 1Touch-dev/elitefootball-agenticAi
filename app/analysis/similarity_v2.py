"""
Role-aware similarity engine v2.
Adds: role-based feature weighting, trajectory similarity, clustering,
      successful vs failed comp classification.
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "similarity_v2_role_aware"

# Role-specific feature weight profiles
ROLE_WEIGHTS: dict[str, dict[str, float]] = {
    "forward": {
        "goal_contribution_per_90": 0.35,
        "shots": 0.20,
        "xg_per_90": 0.20,
        "minutes": 0.10,
        "base_kpi_score": 0.10,
        "discipline_risk_score": 0.05,
    },
    "midfielder": {
        "goal_contribution_per_90": 0.15,
        "shots": 0.10,
        "progression_score": 0.25,
        "minutes": 0.15,
        "base_kpi_score": 0.20,
        "consistency_score": 0.15,
    },
    "defender": {
        "minutes": 0.25,
        "consistency_score": 0.25,
        "base_kpi_score": 0.20,
        "discipline_risk_score": 0.15,
        "goal_contribution_per_90": 0.05,
        "shots": 0.10,
    },
    "goalkeeper": {
        "minutes": 0.35,
        "consistency_score": 0.30,
        "base_kpi_score": 0.25,
        "discipline_risk_score": 0.10,
    },
    "default": {
        "goal_contribution_per_90": 0.20,
        "shots": 0.15,
        "minutes": 0.20,
        "base_kpi_score": 0.20,
        "consistency_score": 0.15,
        "discipline_risk_score": 0.10,
    },
}

ALL_FEATURE_KEYS = [
    "goal_contribution_per_90",
    "shots",
    "minutes",
    "base_kpi_score",
    "consistency_score",
    "discipline_risk_score",
    "xg_per_90",
    "xa_per_90",
    "progression_score",
]


def _normalize_position(position: str | None) -> str:
    pos = str(position or "").strip().lower()
    if any(x in pos for x in ["forward", "striker", "winger", "attacker", "fw", "st", "cf", "lw", "rw"]):
        return "forward"
    if any(x in pos for x in ["midfield", "cm", "dm", "am", "mf"]):
        return "midfielder"
    if any(x in pos for x in ["defender", "back", "cb", "lb", "rb", "df"]):
        return "defender"
    if any(x in pos for x in ["keeper", "gk", "goalkeeper"]):
        return "goalkeeper"
    return "default"


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _build_feature_vector(
    feature_row: dict[str, Any],
    kpi_row: dict[str, Any],
    adv_row: dict[str, Any],
) -> dict[str, float]:
    return {
        "goal_contribution_per_90": _safe_float(feature_row.get("goal_contribution_per_90")),
        "shots": _safe_float(feature_row.get("shots")),
        "minutes": _safe_float(feature_row.get("minutes")),
        "base_kpi_score": _safe_float(kpi_row.get("base_kpi_score")),
        "consistency_score": _safe_float(kpi_row.get("consistency_score")),
        "discipline_risk_score": _safe_float(feature_row.get("discipline_risk_score")),
        "xg_per_90": _safe_float(adv_row.get("xg_per_90")),
        "xa_per_90": _safe_float(adv_row.get("xa_per_90")),
        "progression_score": _safe_float(adv_row.get("progression_score")),
    }


def _min_max_normalize(vectors: list[dict[str, float]]) -> list[dict[str, float]]:
    if not vectors:
        return []
    keys = list(vectors[0].keys())
    mins = {k: min(v[k] for v in vectors) for k in keys}
    maxs = {k: max(v[k] for v in vectors) for k in keys}
    normalized = []
    for vec in vectors:
        normalized.append({
            k: round((vec[k] - mins[k]) / (maxs[k] - mins[k]) + 1e-9, 6) if maxs[k] > mins[k] else 0.0
            for k in keys
        })
    return normalized


def _weighted_cosine_distance(
    vec_a: dict[str, float],
    vec_b: dict[str, float],
    weights: dict[str, float],
) -> float:
    all_keys = set(vec_a) | set(vec_b)
    dot = sum(vec_a.get(k, 0.0) * vec_b.get(k, 0.0) * weights.get(k, 0.1) for k in all_keys)
    mag_a = math.sqrt(sum((vec_a.get(k, 0.0) * weights.get(k, 0.1)) ** 2 for k in all_keys))
    mag_b = math.sqrt(sum((vec_b.get(k, 0.0) * weights.get(k, 0.1)) ** 2 for k in all_keys))
    if mag_a < 1e-9 or mag_b < 1e-9:
        return 1.0
    cosine_sim = dot / (mag_a * mag_b)
    return round(1.0 - max(-1.0, min(1.0, cosine_sim)), 6)


def _trajectory_similarity(traj_a: str | None, traj_b: str | None) -> float:
    """1.0 if same trajectory, partial credit otherwise."""
    if traj_a == traj_b:
        return 1.0
    compatible = {("ascending", "stable"), ("stable", "ascending")}
    if (traj_a, traj_b) in compatible or (traj_b, traj_a) in compatible:
        return 0.7
    return 0.3


def _classify_comp(
    target_val_score: float,
    comp_val_score: float,
    comp_trajectory: str | None,
) -> str:
    """Classify comparable as successful, neutral, or failed."""
    if comp_val_score >= target_val_score * 1.1 or comp_trajectory == "ascending":
        return "successful"
    if comp_val_score < target_val_score * 0.7 or comp_trajectory == "declining":
        return "failed"
    return "neutral"


def build_similarity_v2_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    advanced_metric_rows: list[dict[str, Any]] | None = None,
    pathway_rows: list[dict[str, Any]] | None = None,
    valuation_rows: list[dict[str, Any]] | None = None,
    neighbor_limit: int = 5,
) -> dict[str, object]:
    advanced_metric_rows = advanced_metric_rows or []
    pathway_rows = pathway_rows or []
    valuation_rows = valuation_rows or []

    def _key(v: str | None) -> str:
        return str(v or "").strip().lower()

    players_by_name = {_key(r.get("player_name")): r for r in silver_tables.get("players", [])}
    features_by_name = {_key(r.get("player_name")): r for r in gold_tables.get("player_features", [])}
    kpi_by_name = {_key(r.get("player_name")): r for r in kpi_rows}
    adv_by_name = {_key(r.get("player_name")): r for r in advanced_metric_rows}
    pathway_by_name = {_key(r.get("player_name")): r for r in pathway_rows}
    val_by_name = {_key(r.get("player_name")): r for r in valuation_rows}

    all_names = sorted(set(features_by_name) | set(kpi_by_name))
    if not all_names:
        path = write_json(Path(settings.gold_data_dir) / "player_similarity.json", [])
        return {"path": path, "rows": []}

    # Build raw vectors
    raw_vectors = [
        _build_feature_vector(features_by_name.get(n, {}), kpi_by_name.get(n, {}), adv_by_name.get(n, {}))
        for n in all_names
    ]
    normalized = _min_max_normalize(raw_vectors)
    vector_map = {n: normalized[i] for i, n in enumerate(all_names)}

    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        pr = players_by_name.get(name, {})
        fr = features_by_name.get(name, {})
        kr = kpi_by_name.get(name, {})
        patr = pathway_by_name.get(name, {})
        vr = val_by_name.get(name, {})

        position = pr.get("position") or fr.get("position")
        role = _normalize_position(position)
        weights = ROLE_WEIGHTS.get(role, ROLE_WEIGHTS["default"])
        target_vec = vector_map[name]
        target_traj = patr.get("trajectory")
        target_val = float(vr.get("valuation_score") or 50.0)

        distances: list[tuple[float, str]] = []
        for other_name in all_names:
            if other_name == name:
                continue
            other_vec = vector_map[other_name]
            feature_dist = _weighted_cosine_distance(target_vec, other_vec, weights)
            other_traj = pathway_by_name.get(other_name, {}).get("trajectory")
            traj_bonus = (1.0 - _trajectory_similarity(target_traj, other_traj)) * 0.15
            combined = feature_dist * 0.85 + traj_bonus
            distances.append((combined, other_name))

        distances.sort(key=lambda x: x[0])
        top_n = distances[:neighbor_limit]

        similar_players: list[dict[str, Any]] = []
        for dist, comp_name in top_n:
            comp_pr = players_by_name.get(comp_name, {})
            comp_vr = val_by_name.get(comp_name, {})
            comp_patr = pathway_by_name.get(comp_name, {})
            comp_val = float(comp_vr.get("valuation_score") or 50.0)
            comp_traj = comp_patr.get("trajectory")
            classification = _classify_comp(target_val, comp_val, comp_traj)

            similar_players.append({
                "player_name": comp_pr.get("player_name") or comp_name,
                "position": comp_pr.get("position"),
                "current_club": comp_pr.get("current_club"),
                "similarity_score": round(1.0 - dist, 4),
                "distance": round(dist, 4),
                "trajectory": comp_traj,
                "valuation_score": comp_val,
                "comp_classification": classification,
            })

        display_name = pr.get("player_name") or fr.get("player_name") or kr.get("player_name") or name

        output_rows.append({
            "player_name": display_name,
            "position": position,
            "role": role,
            "current_club": pr.get("current_club") or fr.get("current_club"),
            "trajectory": target_traj,
            "similar_players": similar_players,
            "comparison_features": raw_vectors[all_names.index(name)],
            "model_version": MODEL_VERSION,
        })

    path = write_json(Path(settings.gold_data_dir) / "player_similarity.json", output_rows)
    return {"path": path, "rows": output_rows}
