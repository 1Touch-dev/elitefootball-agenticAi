from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.analysis.legacy.advanced_metrics import per_90, progression_score, safe_sum
from app.config import settings
from app.pipeline.io import write_json


ADVANCED_FIELDS = (
    "xg",
    "xa",
    "progressive_carries",
    "progressive_passes",
    "progressive_receptions",
    "carries_into_final_third",
    "passes_into_final_third",
    "carries_into_penalty_area",
    "passes_into_penalty_area",
)


def _player_key(row: dict[str, Any]) -> str:
    return str(row.get("player_name") or "unknown-player").strip().lower()


def build_advanced_metrics_output(silver_tables: dict[str, list[dict[str, Any]]]) -> dict[str, object]:
    grouped_stats: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in silver_tables.get("player_match_stats", []):
        grouped_stats[_player_key(row)].append(row)

    output_rows: list[dict[str, Any]] = []
    for key, rows in grouped_stats.items():
        minutes = sum(row.get("minutes") or 0 for row in rows)
        goals = sum(row.get("goals") or 0 for row in rows)
        assists = sum(row.get("assists") or 0 for row in rows)
        totals = {field: safe_sum(*(row.get(field) for row in rows)) for field in ADVANCED_FIELDS}

        progressive_actions = safe_sum(
            totals["progressive_carries"],
            totals["progressive_passes"],
            totals["progressive_receptions"],
        )
        final_third_entries = safe_sum(
            totals["carries_into_final_third"],
            totals["passes_into_final_third"],
        )
        penalty_area_entries = safe_sum(
            totals["carries_into_penalty_area"],
            totals["passes_into_penalty_area"],
        )

        progressive_actions_p90 = per_90(progressive_actions, minutes)
        final_third_entries_p90 = per_90(final_third_entries, minutes)
        penalty_area_entries_p90 = per_90(penalty_area_entries, minutes)

        output_rows.append(
            {
                "player_name": rows[0].get("player_name"),
                "minutes_played": minutes,
                "xg": totals["xg"],
                "xa": totals["xa"],
                "xg_per_90": per_90(totals["xg"], minutes),
                "xa_per_90": per_90(totals["xa"], minutes),
                "goals_minus_xg": round(goals - totals["xg"], 3),
                "assists_minus_xa": round(assists - totals["xa"], 3),
                "progressive_carries": totals["progressive_carries"],
                "progressive_passes": totals["progressive_passes"],
                "progressive_receptions": totals["progressive_receptions"],
                "progressive_actions": progressive_actions,
                "progressive_actions_per_90": progressive_actions_p90,
                "final_third_entries": final_third_entries,
                "final_third_entries_per_90": final_third_entries_p90,
                "penalty_area_entries": penalty_area_entries,
                "penalty_area_entries_per_90": penalty_area_entries_p90,
                "progression_score": progression_score(
                    progressive_actions_p90,
                    final_third_entries_p90,
                    penalty_area_entries_p90,
                ),
            }
        )

    output_rows.sort(key=lambda row: row["progression_score"], reverse=True)
    output_path = write_json(Path(settings.gold_data_dir) / "advanced_metrics.json", output_rows)
    return {"path": output_path, "rows": output_rows}
