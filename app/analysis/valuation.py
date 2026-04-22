from __future__ import annotations


def clamp_score(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, float(value))), 3)


def normalize_player_key(value: str | None) -> str:
    # Normalize player identifiers across datasets for consistent joins.
    return str(value or "unknown-player").strip().lower()


def performance_score(
    base_kpi_score: float | None,
    progression_score_value: float | None,
    goal_contribution_per_90: float | None,
    shots: int | float | None,
    matches: int | float | None,
) -> float:
    if base_kpi_score is not None:
        score = float(base_kpi_score) * 8.0
        if progression_score_value is not None:
            score += float(progression_score_value) * 0.12
        return round(min(45.0, score), 3)

    match_count = max(float(matches or 0), 1.0)
    score = ((goal_contribution_per_90 or 0.0) * 18.0) + ((float(shots or 0) / match_count) * 2.0)
    return round(min(45.0, score), 3)


def age_score(age: int | None) -> float:
    if age is None:
        return 10.0
    if 18 <= age <= 21:
        return 18.0
    if 22 <= age <= 24:
        return 16.0
    if 25 <= age <= 27:
        return 13.0
    if 28 <= age <= 30:
        return 9.0
    if age >= 31:
        return 5.0
    return 10.0


def minutes_score(minutes: int | float | None) -> float:
    return round(min(15.0, (float(minutes or 0) / 900.0) * 3.0), 3)


def club_factor(club_name: str | None) -> float:
    normalized = str(club_name or "").strip().lower()
    if not normalized:
        return 4.0
    if "independiente del valle" in normalized or normalized == "idv":
        return 8.0
    if any(token in normalized for token in ("u20", "u-20", "u17", "u-17", "reserves", "reserve", "ii", "b team", "academy", "youth")):
        return 3.0
    return 6.0


def league_adjustment(competition_name: str | None, club_name: str | None = None) -> float:
    competition = str(competition_name or "").strip().lower()
    club = str(club_name or "").strip().lower()
    if competition:
        if any(token in competition for token in ("libertadores", "sudamericana", "serie a", "liga pro", "primera división", "first division")):
            return 6.0
        if any(token in competition for token in ("reserve", "reserves", "u20", "u-20", "u17", "u-17", "academy", "youth")):
            return 2.0
        return 5.0
    if any(token in club for token in ("reserve", "reserves", "u20", "u-20", "u17", "u-17", "academy", "youth")):
        return 2.0
    return 4.0


def risk_score(discipline_risk_score: float | None, consistency_score: float | None) -> float:
    score = float(discipline_risk_score or 0.0) * 1.5
    if consistency_score is not None:
        score += max(0.0, (60.0 - float(consistency_score)) * 0.08)
    return round(min(12.0, score), 3)


def risk_deduction(risk_score_value: float | None, scale: float = 0.12, max_deduction: float = 15.0) -> float:
    if risk_score_value is None:
        return 0.0
    return round(min(max_deduction, float(risk_score_value) * scale), 3)


def valuation_tier(score: float) -> str:
    if score >= 85.0:
        return "elite_mvp"
    if score >= 70.0:
        return "strong_mvp"
    if score >= 55.0:
        return "solid_mvp"
    if score >= 40.0:
        return "rotation_mvp"
    return "development_mvp"
