from __future__ import annotations


def per_90(metric_total: int | float | None, minutes_played: int | float | None) -> float | None:
    if metric_total is None or minutes_played is None or minutes_played <= 0:
        return None
    return round((float(metric_total) / float(minutes_played)) * 90.0, 3)


def safe_sum(*values: int | float | None) -> float:
    return round(sum(float(value or 0) for value in values), 3)


def progression_score(
    progressive_actions_per_90: float | None,
    final_third_entries_per_90: float | None,
    penalty_area_entries_per_90: float | None,
) -> float:
    return round(
        ((progressive_actions_per_90 or 0.0) * 0.50)
        + ((final_third_entries_per_90 or 0.0) * 0.30)
        + ((penalty_area_entries_per_90 or 0.0) * 0.20),
        3,
    )
