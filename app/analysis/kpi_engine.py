from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.analysis.kpi_formulas import (
    age_in_years,
    age_multiplier,
    base_kpi_score,
    bounded_consistency_score,
    per_90,
    rolling_average,
)
from app.config import settings
from app.pipeline.io import write_json


def _player_key(row: dict[str, Any]) -> str:
    return str(row.get("player_name") or "unknown-player").strip().lower()


def build_kpi_engine_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    confidence_index: dict[str, Any] | None = None,
) -> dict[str, object]:
    confidence_index = confidence_index or {}
    players_by_name = {_player_key(row): row for row in silver_tables.get("players", [])}
    grouped_stats: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in silver_tables.get("player_match_stats", []):
        grouped_stats[_player_key(row)].append(row)

    output_rows: list[dict[str, Any]] = []
    for key, rows in grouped_stats.items():
        rows.sort(key=lambda row: ((row.get("match_date") or ""), (row.get("source_url") or "")))
        player_info = players_by_name.get(key, {})

        minutes = sum(row.get("minutes") or 0 for row in rows)
        goals = sum(row.get("goals") or 0 for row in rows)
        assists = sum(row.get("assists") or 0 for row in rows)
        shots_raw = sum(row.get("shots") or 0 for row in rows)
        passes_raw = sum(row.get("passes_completed") or 0 for row in rows)

        # When shots/passes are missing (TM aggregate data), estimate from position and goals.
        # Shots: goals ÷ typical finishing rate by position; passes: position-based per-90 estimate.
        position = (player_info.get("position") or "").lower()
        is_forward = any(p in position for p in ("forward", "striker", "winger", "centre-f", "second striker"))
        is_defender = any(p in position for p in ("back", "defender", "goalkeeper"))
        finishing_rate = 0.18 if is_forward else (0.14 if not is_defender else 0.08)
        passes_p90_est = 35 if is_forward else (45 if not is_defender else 52)
        shots = shots_raw if shots_raw > 0 else round(goals / finishing_rate) if goals > 0 else 0
        passes_completed = passes_raw if passes_raw > 0 else round((minutes / 90) * passes_p90_est)

        goals_p90_series = [per_90(row.get("goals") or 0, row.get("minutes")) for row in rows]
        gc_p90_series = [per_90((row.get("goals") or 0) + (row.get("assists") or 0), row.get("minutes")) for row in rows]
        shots_p90_series = [per_90(shots_raw, minutes)] if shots_raw else [per_90(shots, minutes)]

        consistency = bounded_consistency_score(gc_p90_series[-5:])
        player_age = age_in_years(player_info.get("date_of_birth")) or player_info.get("age")
        age_factor = age_multiplier(player_age)

        base_score = base_kpi_score(
            per_90(goals + assists, minutes),
            per_90(shots, minutes),
            per_90(passes_completed, minutes),
            consistency,
        )

        conf = confidence_index.get(key, {})
        data_confidence = float(conf.get("data_confidence_score") or 1.0)
        validation_flag = conf.get("validation_flag", "OK")

        # Confidence-weighted KPI: raw * confidence (excludes LOW_CONFIDENCE from Gold aggregation)
        weighted_kpi = round(base_score * age_factor * data_confidence, 3)

        row_output = {
            "player_name": player_info.get("player_name") or rows[0].get("player_name"),
            "minutes_played": minutes,
            "age": player_age,
            "goals_per_90": per_90(goals, minutes),
            "assists_per_90": per_90(assists, minutes),
            "shots_per_90": per_90(shots, minutes),
            "goal_contributions_per_90": per_90(goals + assists, minutes),
            "passes_completed_per_90": per_90(passes_completed, minutes),
            "rolling_3_goals_per_90": rolling_average(goals_p90_series, 3),
            "rolling_5_goal_contributions_per_90": rolling_average(gc_p90_series, 5),
            "rolling_3_shots_per_90": rolling_average(shots_p90_series, 3),
            "rolling_5_minutes": rolling_average([row.get("minutes") or 0 for row in rows], 5),
            "consistency_score": consistency,
            "age_multiplier": age_factor,
            "base_kpi_score": base_score,
            "age_adjusted_kpi_score": round(base_score * age_factor, 3),
            "confidence_weighted_kpi": weighted_kpi,
            "data_confidence_score": round(data_confidence, 4),
            "validation_flag": validation_flag,
        }
        output_rows.append(row_output)

    output_rows.sort(key=lambda row: row["age_adjusted_kpi_score"], reverse=True)
    output_path = write_json(Path(settings.gold_data_dir) / "kpi_engine.json", output_rows)
    return {"path": output_path, "rows": output_rows}
