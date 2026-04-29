from __future__ import annotations
import pytest
from app.analysis.valuation_v2 import (
    age_curve_score, performance_component, minutes_probability_score,
    risk_discount_component, compute_valuation_score, valuation_tier_v2,
    future_value_projection, DEFAULT_WEIGHTS,
)


def test_age_curve_peaks_at_25():
    assert age_curve_score(25) > age_curve_score(30)
    assert age_curve_score(25) > age_curve_score(20)
    assert 95 <= age_curve_score(25) <= 100


def test_age_curve_none():
    assert age_curve_score(None) == 50.0


def test_performance_component_zeros():
    assert performance_component(None, None, None, None, None) == 0.0


def test_performance_component_positive():
    assert performance_component(70.0, 0.4, 0.3, 0.5, 0.5) > 0


def test_minutes_probability_capped():
    assert minutes_probability_score(1000, 10) == 100.0  # 1000/900 > 1 → capped at 100


def test_minutes_probability_zero():
    assert minutes_probability_score(None, None) == 40.0


def test_risk_discount_range():
    d = risk_discount_component(80.0)
    assert 0 <= d <= 25


def test_valuation_score_range():
    score = compute_valuation_score(60, 80, 70, 50, 75, 10)
    assert 0 <= score <= 100


def test_valuation_tiers():
    assert valuation_tier_v2(85) == "elite"
    assert valuation_tier_v2(68) == "high"
    assert valuation_tier_v2(52) == "mid"
    assert valuation_tier_v2(37) == "developing"
    assert valuation_tier_v2(10) == "low"


def test_future_value_projection():
    fv = future_value_projection(70.0, 22.0, "ascending")
    assert "current" in fv
    assert "in_2yr" in fv
    assert "in_5yr" in fv
    assert "peak_window" in fv
