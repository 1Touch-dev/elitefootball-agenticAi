from __future__ import annotations

from datetime import date, datetime
from statistics import pstdev


def clamp_score(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, float(value))), 3)


def safe_mean(values: list[int | float | None]) -> float:
    numeric = [float(value) for value in values if value is not None]
    if not numeric:
        return 0.0
    return round(sum(numeric) / len(numeric), 3)


def coefficient_of_variation(values: list[int | float | None], minimum_mean: float = 0.5) -> float:
    numeric = [float(value) for value in values if value is not None]
    if len(numeric) < 2:
        return 0.0

    mean_value = sum(numeric) / len(numeric)
    baseline = max(abs(mean_value), float(minimum_mean))
    return round(float(pstdev(numeric)) / baseline, 3)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None

    text = str(value).strip()
    for candidate in (text, text.replace("Z", "+00:00")):
        try:
            return datetime.fromisoformat(candidate).date()
        except ValueError:
            continue

    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def days_between_appearances(match_dates: list[str | None]) -> list[int]:
    parsed_dates = sorted(parsed for parsed in (_parse_date(value) for value in match_dates) if parsed is not None)
    if len(parsed_dates) < 2:
        return []
    return [(current - previous).days for previous, current in zip(parsed_dates, parsed_dates[1:])]


def age_risk_component(age: int | None) -> float:
    if age is None:
        return 8.0
    if age <= 21:
        return 6.0
    if age <= 27:
        return 8.0
    if age <= 30:
        return 12.0
    if age <= 33:
        return 16.0
    return 20.0


def availability_gap_component(max_gap_days: int | None, avg_gap_days: float | None) -> float:
    max_gap = float(max_gap_days or 0)
    avg_gap = float(avg_gap_days or 0)
    score = max(0.0, max_gap - 10.0) * 0.8
    score += max(0.0, avg_gap - 7.0) * 0.9
    return clamp_score(score, 0.0, 35.0)


def minutes_instability_component(minutes_series: list[int | float | None]) -> float:
    numeric = [float(value or 0) for value in minutes_series]
    if not numeric:
        return 0.0

    cv_score = coefficient_of_variation(numeric, minimum_mean=15.0) * 18.0
    cameo_ratio = sum(1 for value in numeric if value < 30.0) / len(numeric)
    return clamp_score(cv_score + (cameo_ratio * 10.0), 0.0, 25.0)


def small_sample_penalty(match_count: int | float | None) -> float:
    count = int(match_count or 0)
    if count >= 8:
        return 0.0
    if count >= 5:
        return 3.0
    if count >= 3:
        return 6.0
    if count == 2:
        return 10.0
    return 14.0


def injury_risk_score(age: int | None, gap_days: list[int], minutes_series: list[int | float | None], match_count: int | float | None) -> float:
    max_gap = max(gap_days) if gap_days else 0
    avg_gap = safe_mean(gap_days) if gap_days else 0.0
    score = age_risk_component(age)
    score += availability_gap_component(max_gap, avg_gap)
    score += minutes_instability_component(minutes_series)
    score += small_sample_penalty(match_count)
    return clamp_score(score)


def series_per_90(metric_series: list[int | float | None], minutes_series: list[int | float | None]) -> list[float]:
    output: list[float] = []
    for metric, minutes in zip(metric_series, minutes_series):
        if minutes is None or float(minutes) <= 0:
            output.append(0.0)
            continue
        output.append(round((float(metric or 0) / float(minutes)) * 90.0, 3))
    return output


def volatility_component(series: list[int | float | None], scale: float = 25.0, minimum_mean: float = 0.5) -> float:
    return clamp_score(coefficient_of_variation(series, minimum_mean=minimum_mean) * scale, 0.0, 40.0)


def consistency_penalty(consistency_score: float | None) -> float:
    if consistency_score is None:
        return 6.0
    return clamp_score(max(0.0, (60.0 - float(consistency_score)) * 0.25), 0.0, 15.0)


def volatility_risk_score(
    gc_p90_series: list[int | float | None],
    shots_p90_series: list[int | float | None],
    minutes_series: list[int | float | None],
    consistency_score: float | None,
) -> float:
    score = volatility_component(gc_p90_series, scale=24.0, minimum_mean=0.35) * 0.45
    score += volatility_component(shots_p90_series, scale=18.0, minimum_mean=0.5) * 0.30
    score += volatility_component(minutes_series, scale=16.0, minimum_mean=30.0) * 0.25
    score += consistency_penalty(consistency_score)
    return clamp_score(score)


def discipline_component(discipline_risk_score: float | None) -> float:
    return clamp_score(float(discipline_risk_score or 0.0) * 6.0, 0.0, 100.0)


def composite_risk_score(injury_score: float, volatility_score_value: float, discipline_score: float) -> float:
    return clamp_score((float(injury_score) * 0.45) + (float(volatility_score_value) * 0.40) + (float(discipline_score) * 0.15))


def risk_tier(score: float) -> str:
    if score >= 75.0:
        return "high"
    if score >= 50.0:
        return "elevated"
    if score >= 25.0:
        return "moderate"
    return "low"
