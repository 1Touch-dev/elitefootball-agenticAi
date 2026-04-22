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


def build_kpi_engine_output(silver_tables: dict[str, list[dict[str, Any]]]) -> dict[str, object]:
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
        shots = sum(row.get("shots") or 0 for row in rows)
        passes_completed = sum(row.get("passes_completed") or 0 for row in rows)

        goals_p90_series = [per_90(row.get("goals") or 0, row.get("minutes")) for row in rows]
        gc_p90_series = [per_90((row.get("goals") or 0) + (row.get("assists") or 0), row.get("minutes")) for row in rows]
        shots_p90_series = [per_90(row.get("shots") or 0, row.get("minutes")) for row in rows]

        consistency = bounded_consistency_score(gc_p90_series[-5:])
        player_age = age_in_years(player_info.get("date_of_birth"))
        age_factor = age_multiplier(player_age)

        base_score = base_kpi_score(
            per_90(goals + assists, minutes),
            per_90(shots, minutes),
            per_90(passes_completed, minutes),
            consistency,
        )

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
        }
        output_rows.append(row_output)

    output_rows.sort(key=lambda row: row["age_adjusted_kpi_score"], reverse=True)
    output_path = write_json(Path(settings.gold_data_dir) / "kpi_engine.json", output_rows)
    return {"path": output_path, "rows": output_rows}
