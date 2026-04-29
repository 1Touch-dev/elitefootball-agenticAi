from __future__ import annotations
from app.analysis.pathway_engine import (
    age_league_percentile, improvement_rate, development_velocity,
    minutes_growth_curve, career_trajectory, best_pathway, success_probability,
    development_stage,
)


def test_percentile_range():
    p = age_league_percentile(22, 60.0, None)
    assert 0 < p <= 100


def test_improvement_rate_ascending():
    assert improvement_rate([50, 60, 70]) > 0


def test_improvement_rate_declining():
    assert improvement_rate([70, 60, 50]) < 0


def test_improvement_rate_single_value():
    assert improvement_rate([60]) == 0.0


def test_development_velocity_young_boost():
    rate_young = development_velocity([50, 60, 70], age=19)
    rate_old = development_velocity([50, 60, 70], age=32)
    assert rate_young > rate_old


def test_minutes_growth_curve_ascending():
    result = minutes_growth_curve([200, 500, 900, 2500])
    assert result["trend"] == "ascending"
    assert result["delta"] > 0


def test_minutes_growth_curve_empty():
    result = minutes_growth_curve([])
    assert result["trend"] == "unknown"


def test_career_trajectory_ascending():
    assert career_trajectory([50, 65, 80], age=22) == "ascending"


def test_best_pathway_idv_ascending():
    paths = best_pathway("Independiente del Valle", "Forward", 21, "ascending", 70)
    assert len(paths) >= 1


def test_success_probability_range():
    p = success_probability(22, 70, "ascending", 75)
    assert 0 <= p <= 1


def test_development_stage():
    assert development_stage(19, 60) == "prospect"
    assert development_stage(22, 60) == "emerging"
    assert development_stage(26, 70) == "peak"
    assert development_stage(31, 55) == "veteran"
