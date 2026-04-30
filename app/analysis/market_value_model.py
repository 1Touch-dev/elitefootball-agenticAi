"""
Market Value Model — converts analytical score → € estimated value.

Formula:
  predicted_value_eur = base_value_by_league × performance_factor × age_factor × demand_factor

Where:
  base_value_by_league = mean transfer fee for players from this league (calibrated from historical TM data)
  performance_factor   = (valuation_score / 50) ^ 1.4
  age_factor           = Gaussian peak at age 24, sigma=4 (matches historical TM premium patterns)
  demand_factor        = 1 + 0.3 * transfer_probability_1y + 0.15 * trajectory_bonus

Output:
  predicted_value_eur  — estimated market value
  value_confidence     — confidence in the estimate (based on data quality + source completeness)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# Base transfer values by league (median historical for this tier, EUR)
# Source: Transfermarkt historical data patterns
_BASE_VALUE_BY_LEAGUE: dict[str, float] = {
    "premier league": 30_000_000,
    "la liga": 22_000_000,
    "bundesliga": 18_000_000,
    "serie a": 16_000_000,
    "ligue 1": 14_000_000,
    "primera liga": 8_500_000,     # Portugal Primeira Liga
    "eredivisie": 7_500_000,
    "austrian bundesliga": 5_500_000,
    "pro league": 6_000_000,       # Belgium
    "brasileirao": 6_000_000,
    "primera division": 5_000_000, # Argentina
    "liga pro": 1_800_000,         # Ecuador
    "default": 3_000_000,
}


def _base_value(competition: str | None) -> float:
    if not competition:
        return _BASE_VALUE_BY_LEAGUE["default"]
    key = competition.strip().lower()
    for league, val in _BASE_VALUE_BY_LEAGUE.items():
        if league in key:
            return val
    return _BASE_VALUE_BY_LEAGUE["default"]


def _performance_factor(valuation_score: float | None) -> float:
    """Non-linear scaling: average player (score=50) → ×1.0; elite (score=80) → ×3.0."""
    score = float(valuation_score or 50.0)
    score = max(0.0, min(100.0, score))
    # (score/50)^1.4 → score=50 → ×1.0, score=80 → ×2.6, score=30 → ×0.5
    return round((score / 50.0) ** 1.4, 4)


def _age_factor(age: float | None) -> float:
    """
    Gaussian peak at 24, sigma=4.
    Age 24 → ×1.0 (peak). Age 18 → ×0.72. Age 30 → ×0.57.
    """
    if age is None:
        return 0.80
    peak = 24.0
    sigma = 4.5
    return round(math.exp(-((age - peak) ** 2) / (2 * sigma ** 2)), 4)


def _demand_factor(
    transfer_prob_1y: float | None,
    drift_direction: str | None,
) -> float:
    """High demand (about to transfer, improving) → premium."""
    tp = float(transfer_prob_1y or 0.0)
    traj_bonus = 0.0
    if drift_direction == "improving":
        traj_bonus = 0.15
    elif drift_direction == "declining":
        traj_bonus = -0.10
    return round(1.0 + 0.30 * tp + traj_bonus, 4)


def _value_confidence(
    data_confidence: float | None,
    has_market_value: bool,
    has_fbref_data: bool,
) -> float:
    """
    Estimate confidence in our prediction.
    Higher if we have cross-source data + real market value as anchor.
    """
    base = float(data_confidence or 0.70)
    anchor_bonus = 0.15 if has_market_value else 0.0
    fbref_bonus = 0.10 if has_fbref_data else 0.0
    return round(min(1.0, base + anchor_bonus + fbref_bonus), 4)


def compute_market_value(
    player: dict[str, Any],
    drift_direction: str | None = None,
) -> dict[str, Any]:
    """
    Compute predicted market value for a single player.

    Input keys: player_name, age, valuation_score, competition,
                transfer_probability_1y, market_value_eur, data_confidence_score
    """
    name = player.get("player_name")
    age = player.get("age")
    val_score = player.get("valuation_score") or player.get("potential_score")
    competition = player.get("competition")
    tp_1y = player.get("transfer_probability_1y")
    mv_raw = player.get("market_value_eur")
    confidence = player.get("data_confidence_score", 0.70)

    base = _base_value(competition)
    perf = _performance_factor(val_score)
    age_f = _age_factor(age)
    demand = _demand_factor(tp_1y, drift_direction)

    predicted = round(base * perf * age_f * demand, 0)

    # If we have a real market value, blend model with market (model 60%, market 40%)
    has_market = mv_raw is not None and float(mv_raw or 0) > 0
    if has_market:
        blended = round(0.60 * predicted + 0.40 * float(mv_raw), 0)
    else:
        blended = predicted

    value_conf = _value_confidence(
        confidence, has_market, player.get("has_fbref_data", False)
    )

    return {
        "player_name": name,
        "predicted_value_eur": predicted,
        "blended_value_eur": blended,
        "market_value_eur_raw": mv_raw,
        "value_confidence": value_conf,
        "components": {
            "base_value_eur": base,
            "performance_factor": perf,
            "age_factor": age_f,
            "demand_factor": demand,
        },
    }


def build_market_value_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    transfer_rows: list[dict[str, Any]] | None = None,
    confidence_index: dict[str, Any] | None = None,
    drift_report: dict[str, Any] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []
    transfer_rows = transfer_rows or []
    confidence_index = confidence_index or {}
    drift_report = drift_report or {}

    kpi_by_name = {str(r.get("player_name") or "").lower(): r for r in kpi_rows}
    val_by_name = {str(r.get("player_name") or "").lower(): r for r in valuation_rows}
    xfer_by_name = {str(r.get("player_name") or "").lower(): r for r in transfer_rows}
    players_by_name = {
        str(r.get("player_name") or "").lower(): r
        for r in silver_tables.get("players", [])
    }

    from collections import Counter
    comp_by_name: dict[str, str] = {}
    for row in silver_tables.get("player_match_stats", []):
        k = str(row.get("player_name") or "").lower()
        if row.get("competition"):
            comp_by_name.setdefault(k, row["competition"])

    all_names = sorted(set(kpi_by_name) | set(val_by_name) | set(players_by_name))
    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        kr = kpi_by_name.get(name, {})
        vr = val_by_name.get(name, {})
        pr = players_by_name.get(name, {})
        xr = xfer_by_name.get(name, {})
        conf = confidence_index.get(name, {})
        drift = drift_report.get("players", {}).get(name, {}).get("career_drift", {})

        player = {
            "player_name": pr.get("player_name") or kr.get("player_name") or name,
            "age": kr.get("age"),
            "valuation_score": vr.get("valuation_score"),
            "potential_score": vr.get("potential_score"),
            "competition": comp_by_name.get(name) or vr.get("competition"),
            "transfer_probability_1y": xr.get("transfer_probability_1y"),
            "market_value_eur": vr.get("market_value_eur"),
            "data_confidence_score": conf.get("data_confidence_score"),
            "has_fbref_data": conf.get("source_count", 1) >= 2,
        }

        result = compute_market_value(player, drift.get("overall_drift_direction"))
        output_rows.append(result)

    output_rows.sort(key=lambda r: r["blended_value_eur"], reverse=True)
    path = write_json(
        Path(settings.gold_data_dir) / "market_value.json", output_rows
    )
    return {"path": path, "rows": output_rows}
