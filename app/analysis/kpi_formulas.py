from __future__ import annotations

from datetime import date, datetime
from math import sqrt
from typing import Iterable


def per_90(metric_total: int | float | None, minutes_played: int | float | None) -> float | None:
    if metric_total is None or minutes_played is None or minutes_played <= 0:
        return None
    return round((float(metric_total) / float(minutes_played)) * 90.0, 3)


def rolling_average(values: Iterable[int | float | None], window: int) -> float | None:
    recent = [float(value) for value in values if value is not None][-window:]
    if not recent:
        return None
    return round(sum(recent) / len(recent), 3)


def bounded_consistency_score(values: Iterable[int | float | None], scaling_factor: float = 25.0) -> float:
    series = [float(value) for value in values if value is not None]
    if not series:
        return 0.0
    mean = sum(series) / len(series)
    variance = sum((value - mean) ** 2 for value in series) / len(series)
    std_dev = sqrt(variance)
    score = 100.0 - (std_dev * scaling_factor)
    return round(max(0.0, min(100.0, score)), 3)


def parse_birth_date(value: str | None) -> date | None:
    if not value:
        return None
    normalized = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d, %Y", "%B %d, %Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue
    return None


def age_in_years(date_of_birth: str | None, reference_date: date | None = None) -> int | None:
    dob = parse_birth_date(date_of_birth)
    if dob is None:
        return None
    today = reference_date or date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def age_multiplier(age: int | None) -> float:
    if age is None:
        return 1.0
    if age < 21:
        return 1.10
    if age <= 24:
        return 1.05
    if age <= 29:
        return 1.00
    return 0.95


def base_kpi_score(
    goal_contributions_per_90: float | None,
    shots_per_90: float | None,
    passes_completed_per_90: float | None,
    consistency_score: float,
) -> float:
    return round(
        ((goal_contributions_per_90 or 0.0) * 0.45)
        + ((shots_per_90 or 0.0) * 0.20)
        + ((passes_completed_per_90 or 0.0) * 0.15)
        + ((consistency_score / 100.0) * 0.20),
        3,
    )
