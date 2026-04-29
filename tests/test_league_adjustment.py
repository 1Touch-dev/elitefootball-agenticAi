from __future__ import annotations
from app.analysis.league_adjustment import league_coefficient, league_tier, cross_league_comparison


def test_premier_league_coef():
    assert league_coefficient("premier league") == 15.0


def test_liga_pro_coef():
    assert league_coefficient("liga pro") == 5.0


def test_club_hint_fallback():
    coef = league_coefficient(None, "benfica")
    assert coef == 10.0


def test_idv_hint():
    coef = league_coefficient(None, "IDV")
    assert coef == 5.0


def test_unknown_returns_zero():
    assert league_coefficient("made up league") == 0.0


def test_league_tier():
    assert league_tier("premier league") == "elite"
    assert league_tier("eredivisie") == "high"
    assert league_tier("liga pro") == "mid"
    assert league_tier("unknown") == "unknown"


def test_cross_league_comparison():
    players = [
        {"player_name": "A", "base_kpi_score": 60, "competition": "liga pro"},
        {"player_name": "B", "base_kpi_score": 60, "competition": "premier league"},
    ]
    result = cross_league_comparison(players)
    assert len(result) == 2
    a = next(r for r in result if r["player_name"] == "A")
    b = next(r for r in result if r["player_name"] == "B")
    assert a["base_kpi_score_league_normalized"] > b["base_kpi_score_league_normalized"]
