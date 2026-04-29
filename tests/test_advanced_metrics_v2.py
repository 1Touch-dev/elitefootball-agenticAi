from __future__ import annotations
from app.analysis.advanced_metrics_v2 import estimate_xg, estimate_xa, estimate_xt, estimate_epv, estimate_obv, per_90


def test_xg_from_shots_and_goals():
    xg = estimate_xg(shots=10, goals=2)
    assert xg is not None and xg > 0


def test_xg_none_for_no_shots():
    assert estimate_xg(shots=0, goals=0) is None


def test_xa_from_assists():
    xa = estimate_xa(assists=3, key_passes=5)
    assert xa is not None and xa > 0


def test_xa_none():
    assert estimate_xa(None, None) is None


def test_xt_from_progression():
    xt = estimate_xt(progressive_actions=20, final_third_entries=10)
    assert xt["xt_total"] is not None and xt["xt_total"] > 0


def test_xt_empty_returns_none():
    xt = estimate_xt()
    assert xt["xt_total"] is None


def test_epv_per_90():
    epv = estimate_epv(goals=5, assists=3, shots=20, minutes=900)
    assert epv is not None and epv > 0


def test_epv_no_minutes():
    assert estimate_epv(5, 3, 20, 0) is None


def test_obv_positive():
    obv = estimate_obv(goals=5, assists=3, shots=20)
    assert obv is not None and obv > 0


def test_per_90_calculation():
    assert per_90(9, 90) == 9.0
    assert per_90(9, 180) == 4.5
    assert per_90(None, 90) is None
    assert per_90(9, 0) is None
