from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.analysis.kpi_formulas import age_in_years
from app.analysis.risk import (
    availability_gap_component,
    coefficient_of_variation,
    composite_risk_score,
    days_between_appearances,
    discipline_component,
    injury_risk_score,
    minutes_instability_component,
    risk_tier,
    safe_mean,
    series_per_90,
    small_sample_penalty,
    volatility_risk_score,
)
from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "risk_mvp_v1"


def _player_key(row: dict[str, Any]) -> str:
    return str(row.get("player_name") or "unknown-player").strip().lower()


def build_risk_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]] | None = None,
    kpi_rows: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    gold_tables = gold_tables or {}
    kpi_rows = kpi_rows or []

    players_by_name = {_player_key(row): row for row in silver_tables.get("players", [])}
    features_by_name = {_player_key(row): row for row in gold_tables.get("player_features", [])}
    kpi_by_name = {_player_key(row): row for row in kpi_rows}

    grouped_stats: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in silver_tables.get("player_match_stats", []):
        grouped_stats[_player_key(row)].append(row)

    player_names = sorted(set(players_by_name.keys()) | set(features_by_name.keys()) | set(kpi_by_name.keys()) | set(grouped_stats.keys()))
    if not player_names:
        output_path = write_json(Path(settings.gold_data_dir) / "player_risk.json", [])
        return {"path": output_path, "rows": []}

    output_rows: list[dict[str, Any]] = []
    for player_name in player_names:
        player_row = players_by_name.get(player_name, {})
        feature_row = features_by_name.get(player_name, {})
        kpi_row = kpi_by_name.get(player_name, {})
        stat_rows = grouped_stats.get(player_name, [])

        minutes_series = [row.get("minutes") or 0 for row in stat_rows]
        goals_series = [row.get("goals") or 0 for row in stat_rows]
        assists_series = [row.get("assists") or 0 for row in stat_rows]
        shots_series = [row.get("shots") or 0 for row in stat_rows]
        gc_series = [(goal or 0) + (assist or 0) for goal, assist in zip(goals_series, assists_series)]
        gc_p90_series = series_per_90(gc_series, minutes_series)
        shots_p90_series = series_per_90(shots_series, minutes_series)
        gap_days = days_between_appearances([row.get("match_date") for row in stat_rows])

        match_count = len(stat_rows) or int(feature_row.get("matches") or 0)
        total_minutes = sum(float(value or 0) for value in minutes_series)
        age = kpi_row.get("age")
        if age is None:
            age = age_in_years(player_row.get("date_of_birth"))

        discipline_raw = feature_row.get("discipline_risk_score")
        if discipline_raw is None:
            discipline_raw = sum((row.get("yellow_cards") or 0) + ((row.get("red_cards") or 0) * 2) for row in stat_rows)

        injury_score = injury_risk_score(age, gap_days, minutes_series, match_count)
        volatility_score_value = volatility_risk_score(gc_p90_series, shots_p90_series, minutes_series, kpi_row.get("consistency_score"))
        discipline_score = discipline_component(discipline_raw)
        total_risk_score = composite_risk_score(injury_score, volatility_score_value, discipline_score)

        max_gap_days = max(gap_days) if gap_days else 0
        avg_gap_days = safe_mean(gap_days) if gap_days else 0.0
        minutes_cv = coefficient_of_variation(minutes_series, minimum_mean=15.0)
        gc_p90_cv = coefficient_of_variation(gc_p90_series, minimum_mean=0.35)
        shots_p90_cv = coefficient_of_variation(shots_p90_series, minimum_mean=0.5)

        output_rows.append(
            {
                "player_name": player_row.get("player_name") or feature_row.get("player_name") or kpi_row.get("player_name") or player_name,
                "position": player_row.get("position"),
                "current_club": player_row.get("current_club") or feature_row.get("current_club"),
                "risk_score": total_risk_score,
                "risk_tier": risk_tier(total_risk_score),
                "components": {
                    "injury_risk_score": injury_score,
                    "volatility_risk_score": volatility_score_value,
                    "discipline_risk_score": discipline_score,
                    "availability_penalty": availability_gap_component(max_gap_days, avg_gap_days),
                    "minutes_instability_score": minutes_instability_component(minutes_series),
                    "small_sample_penalty": small_sample_penalty(match_count),
                },
                "inputs": {
                    "age": age,
                    "matches": match_count,
                    "minutes": round(total_minutes, 3),
                    "minutes_per_match": round(total_minutes / match_count, 3) if match_count else 0.0,
                    "max_gap_days": max_gap_days,
                    "avg_gap_days": avg_gap_days,
                    "minutes_cv": minutes_cv,
                    "goal_contribution_p90_cv": gc_p90_cv,
                    "shots_p90_cv": shots_p90_cv,
                    "consistency_score": kpi_row.get("consistency_score"),
                },
                "model_version": MODEL_VERSION,
            }
        )

    output_rows.sort(key=lambda row: row["risk_score"], reverse=True)
    output_path = write_json(Path(settings.gold_data_dir) / "player_risk.json", output_rows)
    return {"path": output_path, "rows": output_rows}
