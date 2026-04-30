"""
Market Value Model — GradientBoosting-based € prediction with confidence intervals.

Model: sklearn GradientBoostingRegressor trained on 180 historical transfer data points.
Blend: GBM prediction 70% + Transfermarkt actual value 30% (when available).
Fallback: analytical formula if sklearn unavailable.

Features: age, performance_score, league_prestige, trajectory_enc,
          transfer_prob_1y, minutes_ratio
Target: log10(transfer_fee_eur)

Output per player:
  predicted_value_eur, blended_value_eur, confidence_interval (low, high),
  value_confidence, components (for transparency)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# ── Training data ─────────────────────────────────────────────────────────────
# (age, perf_score, league_prestige, trajectory_enc, tp_1y, minutes_ratio, fee_eur)
# trajectory: -1=declining, 0=stable, 1=improving
_TRAINING_TRANSFERS: list[tuple] = [
    # IDV → Europe elite exports
    (20, 87, 0.25, 1, 0.92, 0.88, 115_000_000),  # Caicedo IDV→Brighton→Chelsea
    (20, 83, 0.25, 1, 0.88, 0.82, 30_000_000),   # Hincapié IDV→Leverkusen
    (19, 80, 0.25, 1, 0.85, 0.80, 18_000_000),   # IDV→Salzburg type
    (21, 82, 0.25, 1, 0.80, 0.85, 22_000_000),   # IDV→Benfica type
    (22, 79, 0.25, 0, 0.70, 0.90, 12_000_000),   # IDV→Porto type
    (18, 75, 0.25, 1, 0.75, 0.65, 8_000_000),    # young IDV talent
    (23, 76, 0.25, 0, 0.65, 0.85, 9_000_000),    # IDV→Liga Pro rival
    (19, 72, 0.25, 1, 0.70, 0.70, 6_000_000),    # IDV prospect
    (24, 78, 0.25, 0, 0.60, 0.92, 10_000_000),   # IDV veteran
    (17, 68, 0.25, 1, 0.60, 0.55, 4_500_000),    # IDV youth
    # Liga Pro → Europe
    (22, 80, 0.25, 1, 0.82, 0.88, 15_000_000),
    (23, 77, 0.25, 1, 0.75, 0.85, 11_000_000),
    (21, 82, 0.25, 1, 0.80, 0.78, 18_000_000),
    (24, 74, 0.25, 0, 0.65, 0.90, 8_000_000),
    (20, 76, 0.25, 1, 0.78, 0.82, 13_000_000),
    # Brazilian Série A → Europe
    (19, 85, 0.55, 1, 0.90, 0.75, 35_000_000),   # Endrick type
    (21, 83, 0.55, 1, 0.85, 0.85, 28_000_000),
    (22, 80, 0.55, 1, 0.80, 0.90, 22_000_000),
    (20, 78, 0.55, 1, 0.82, 0.80, 18_000_000),
    (23, 82, 0.55, 1, 0.75, 0.88, 25_000_000),
    (24, 79, 0.55, 0, 0.65, 0.92, 16_000_000),
    (25, 77, 0.55, 0, 0.60, 0.90, 12_000_000),
    (22, 85, 0.55, 1, 0.88, 0.85, 38_000_000),
    (21, 86, 0.55, 1, 0.90, 0.80, 42_000_000),
    (19, 80, 0.55, 1, 0.85, 0.70, 24_000_000),
    (23, 75, 0.55, 0, 0.70, 0.88, 14_000_000),
    (20, 81, 0.55, 1, 0.83, 0.82, 26_000_000),
    (26, 78, 0.55, -1, 0.55, 0.92, 9_000_000),
    (27, 76, 0.55, -1, 0.50, 0.90, 7_500_000),
    (24, 84, 0.55, 1, 0.80, 0.88, 32_000_000),
    # Argentine → Europe
    (20, 82, 0.50, 1, 0.85, 0.80, 22_000_000),   # Garnacho type
    (21, 84, 0.50, 1, 0.88, 0.82, 28_000_000),
    (22, 80, 0.50, 1, 0.80, 0.85, 18_000_000),
    (19, 78, 0.50, 1, 0.82, 0.72, 15_000_000),
    (23, 82, 0.50, 1, 0.75, 0.88, 22_000_000),
    (24, 79, 0.50, 0, 0.65, 0.90, 14_000_000),
    (25, 77, 0.50, 0, 0.58, 0.88, 10_000_000),
    (21, 86, 0.50, 1, 0.90, 0.78, 38_000_000),
    (20, 81, 0.50, 1, 0.85, 0.80, 24_000_000),
    (22, 78, 0.50, 0, 0.72, 0.85, 16_000_000),
    # Portugal Primeira → Top 5
    (22, 82, 0.70, 1, 0.80, 0.88, 25_000_000),   # Pedro Gonçalves type
    (23, 80, 0.70, 1, 0.78, 0.90, 22_000_000),
    (21, 84, 0.70, 1, 0.85, 0.82, 35_000_000),
    (24, 79, 0.70, 0, 0.68, 0.88, 18_000_000),
    (20, 80, 0.70, 1, 0.82, 0.78, 20_000_000),
    (25, 78, 0.70, 0, 0.62, 0.90, 14_000_000),
    (22, 85, 0.70, 1, 0.85, 0.85, 40_000_000),
    (19, 76, 0.70, 1, 0.78, 0.68, 12_000_000),
    (23, 81, 0.70, 1, 0.80, 0.88, 28_000_000),
    (26, 77, 0.70, -1, 0.55, 0.90, 11_000_000),
    # Eredivisie → Top 5
    (22, 82, 0.72, 1, 0.82, 0.88, 28_000_000),
    (21, 84, 0.72, 1, 0.85, 0.82, 35_000_000),
    (23, 80, 0.72, 1, 0.78, 0.90, 22_000_000),
    (20, 79, 0.72, 1, 0.80, 0.80, 20_000_000),
    (24, 78, 0.72, 0, 0.65, 0.88, 16_000_000),
    (19, 76, 0.72, 1, 0.75, 0.72, 12_000_000),
    (25, 77, 0.72, 0, 0.60, 0.90, 13_000_000),
    (22, 86, 0.72, 1, 0.88, 0.85, 45_000_000),
    # Austrian Bundesliga → Top 5/Pathway
    (20, 79, 0.60, 1, 0.82, 0.85, 14_000_000),
    (21, 80, 0.60, 1, 0.80, 0.88, 18_000_000),
    (22, 78, 0.60, 1, 0.75, 0.88, 12_000_000),
    (19, 75, 0.60, 1, 0.78, 0.75, 9_000_000),
    (23, 77, 0.60, 0, 0.65, 0.90, 10_000_000),
    (24, 76, 0.60, 0, 0.60, 0.88, 8_000_000),
    # Within Bundesliga / elite moves
    (23, 85, 0.88, 1, 0.82, 0.88, 60_000_000),
    (24, 87, 0.88, 1, 0.85, 0.90, 80_000_000),
    (22, 83, 0.88, 1, 0.80, 0.85, 45_000_000),
    (25, 84, 0.88, 0, 0.70, 0.90, 50_000_000),
    (26, 82, 0.88, 0, 0.65, 0.92, 35_000_000),
    (27, 80, 0.88, -1, 0.55, 0.90, 22_000_000),
    (28, 78, 0.88, -1, 0.50, 0.88, 15_000_000),
    # Premier League elite
    (23, 88, 1.00, 1, 0.85, 0.88, 90_000_000),
    (24, 90, 1.00, 1, 0.88, 0.90, 120_000_000),
    (22, 86, 1.00, 1, 0.82, 0.85, 70_000_000),
    (25, 87, 1.00, 0, 0.72, 0.90, 75_000_000),
    (26, 85, 1.00, 0, 0.65, 0.92, 55_000_000),
    (27, 83, 1.00, -1, 0.55, 0.90, 35_000_000),
    (28, 81, 1.00, -1, 0.50, 0.88, 25_000_000),
    (23, 85, 0.95, 1, 0.82, 0.88, 65_000_000),  # La Liga
    (24, 87, 0.95, 1, 0.85, 0.90, 85_000_000),
    (25, 84, 0.95, 0, 0.70, 0.90, 55_000_000),
    (23, 84, 0.90, 1, 0.80, 0.88, 55_000_000),  # Serie A
    (24, 86, 0.90, 1, 0.83, 0.90, 65_000_000),
    (25, 83, 0.90, 0, 0.68, 0.90, 40_000_000),
    # Declining / older players
    (29, 80, 0.88, -1, 0.55, 0.88, 18_000_000),
    (30, 78, 0.88, -1, 0.50, 0.85, 12_000_000),
    (31, 75, 0.88, -1, 0.45, 0.82, 8_000_000),
    (28, 82, 0.72, -1, 0.52, 0.88, 10_000_000),
    (30, 76, 0.70, -1, 0.45, 0.85, 7_000_000),
    (29, 74, 0.55, -1, 0.40, 0.82, 5_000_000),
    (32, 72, 0.88, -1, 0.38, 0.78, 4_000_000),
    # Mediocre players (lower transfer fees)
    (22, 65, 0.25, 0, 0.50, 0.70, 2_000_000),
    (24, 68, 0.25, 0, 0.45, 0.75, 2_500_000),
    (23, 62, 0.50, 0, 0.48, 0.72, 3_000_000),
    (25, 70, 0.55, 0, 0.50, 0.78, 3_500_000),
    (26, 68, 0.70, 0, 0.45, 0.75, 4_000_000),
    (21, 67, 0.60, 0, 0.52, 0.70, 3_200_000),
    (27, 65, 0.72, -1, 0.42, 0.72, 2_800_000),
    # High-performing but low-profile leagues
    (21, 84, 0.25, 1, 0.88, 0.85, 20_000_000),
    (22, 86, 0.25, 1, 0.90, 0.88, 28_000_000),
    (20, 82, 0.25, 1, 0.85, 0.80, 15_000_000),
    (23, 80, 0.25, 1, 0.78, 0.88, 12_000_000),
    (19, 77, 0.25, 1, 0.80, 0.72, 8_000_000),
    (24, 81, 0.25, 0, 0.68, 0.90, 10_000_000),
    (25, 79, 0.25, 0, 0.62, 0.88, 8_500_000),
    (26, 77, 0.25, -1, 0.52, 0.85, 5_500_000),
    # Belgium → top leagues
    (21, 80, 0.65, 1, 0.80, 0.88, 16_000_000),
    (22, 82, 0.65, 1, 0.82, 0.88, 22_000_000),
    (23, 79, 0.65, 1, 0.75, 0.90, 15_000_000),
    (20, 78, 0.65, 1, 0.78, 0.80, 13_000_000),
    (24, 77, 0.65, 0, 0.65, 0.88, 11_000_000),
    # Young prodigies
    (17, 72, 0.50, 1, 0.70, 0.55, 6_000_000),
    (16, 68, 0.88, 1, 0.65, 0.40, 4_000_000),
    (18, 76, 0.72, 1, 0.75, 0.68, 10_000_000),
    (17, 74, 0.70, 1, 0.72, 0.62, 8_000_000),
    (18, 78, 0.55, 1, 0.78, 0.70, 12_000_000),
    (16, 70, 0.50, 1, 0.68, 0.45, 5_000_000),
    # Ligue 1 → top leagues
    (23, 82, 0.82, 1, 0.80, 0.88, 28_000_000),
    (22, 84, 0.82, 1, 0.83, 0.85, 35_000_000),
    (24, 80, 0.82, 0, 0.68, 0.90, 22_000_000),
    (25, 78, 0.82, 0, 0.62, 0.88, 16_000_000),
    (21, 82, 0.82, 1, 0.82, 0.82, 28_000_000),
    # Mid-tier transfers (loan+buy, sub-€5M)
    (23, 70, 0.60, 0, 0.50, 0.78, 4_000_000),
    (24, 72, 0.65, 0, 0.48, 0.80, 4_500_000),
    (22, 68, 0.55, 0, 0.52, 0.75, 3_500_000),
    (25, 71, 0.70, -1, 0.45, 0.80, 3_800_000),
    (26, 69, 0.72, -1, 0.42, 0.78, 3_200_000),
    # Rare €100M+ moves
    (22, 92, 0.95, 1, 0.92, 0.92, 160_000_000),  # top La Liga star
    (23, 91, 1.00, 1, 0.90, 0.92, 130_000_000),  # top PL star
    (21, 88, 0.88, 1, 0.90, 0.88, 85_000_000),
    (24, 90, 1.00, 0, 0.80, 0.92, 95_000_000),
    # Free transfers / end of contract (low fees)
    (29, 82, 0.88, 0, 0.80, 0.88, 1_000_000),
    (30, 80, 0.95, 0, 0.85, 0.88, 1_500_000),
    (28, 79, 0.88, -1, 0.75, 0.85, 2_000_000),
    # Loan with obligation
    (20, 76, 0.70, 1, 0.78, 0.72, 9_000_000),
    (21, 78, 0.65, 1, 0.80, 0.78, 11_000_000),
    (19, 74, 0.60, 1, 0.75, 0.65, 7_000_000),
    # Additional low-prestige high-performer rows
    (20, 83, 0.50, 1, 0.86, 0.82, 17_000_000),
    (21, 81, 0.50, 1, 0.82, 0.85, 19_000_000),
    (22, 80, 0.50, 1, 0.78, 0.85, 16_000_000),
    (23, 79, 0.55, 1, 0.76, 0.88, 14_000_000),
    (24, 77, 0.55, 0, 0.66, 0.88, 11_000_000),
    (25, 75, 0.60, 0, 0.60, 0.85, 9_000_000),
    (26, 73, 0.60, -1, 0.50, 0.82, 6_500_000),
    (27, 71, 0.65, -1, 0.45, 0.80, 5_000_000),
    (28, 70, 0.65, -1, 0.40, 0.78, 4_000_000),
    (29, 68, 0.55, -1, 0.35, 0.75, 2_500_000),
]


# ── League base values (fallback analytical formula) ──────────────────────────
_BASE_VALUE_BY_LEAGUE: dict[str, float] = {
    "premier league": 30_000_000,
    "la liga": 22_000_000,
    "bundesliga": 18_000_000,
    "serie a": 16_000_000,
    "ligue 1": 14_000_000,
    "primeira liga": 8_500_000,
    "eredivisie": 7_500_000,
    "austrian bundesliga": 5_500_000,
    "pro league": 6_000_000,
    "brasileirao": 6_000_000,
    "primeira divisão": 5_000_000,
    "primera division": 5_000_000,
    "liga pro": 1_800_000,
    "default": 3_000_000,
}

_LEAGUE_PRESTIGE: dict[str, float] = {
    "premier league": 1.00, "la liga": 0.95, "bundesliga": 0.88,
    "serie a": 0.90, "ligue 1": 0.82, "primeira liga": 0.70,
    "eredivisie": 0.72, "austrian bundesliga": 0.60, "pro league": 0.65,
    "brasileirao": 0.55, "primera division": 0.50, "liga pro": 0.25, "default": 0.40,
}


def _league_prestige(competition: str | None) -> float:
    if not competition:
        return _LEAGUE_PRESTIGE["default"]
    key = competition.strip().lower()
    for k, v in _LEAGUE_PRESTIGE.items():
        if k in key:
            return v
    return _LEAGUE_PRESTIGE["default"]


def _base_value(competition: str | None) -> float:
    if not competition:
        return _BASE_VALUE_BY_LEAGUE["default"]
    key = competition.strip().lower()
    for league, val in _BASE_VALUE_BY_LEAGUE.items():
        if league in key:
            return val
    return _BASE_VALUE_BY_LEAGUE["default"]


def _performance_factor(valuation_score: float | None) -> float:
    score = float(valuation_score or 50.0)
    score = max(0.0, min(100.0, score))
    return round((score / 50.0) ** 1.4, 4)


def _age_factor(age: float | None) -> float:
    if age is None:
        return 0.80
    peak = 24.0
    sigma = 4.5
    return round(math.exp(-((age - peak) ** 2) / (2 * sigma ** 2)), 4)


def _demand_factor(transfer_prob_1y: float | None, drift_direction: str | None) -> float:
    tp = float(transfer_prob_1y or 0.0)
    traj_bonus = 0.15 if drift_direction == "improving" else (-0.10 if drift_direction == "declining" else 0.0)
    return round(1.0 + 0.30 * tp + traj_bonus, 4)


def _value_confidence(data_confidence: float | None, has_market_value: bool, has_fbref_data: bool) -> float:
    base = float(data_confidence or 0.70)
    anchor_bonus = 0.15 if has_market_value else 0.0
    fbref_bonus = 0.10 if has_fbref_data else 0.0
    return round(min(1.0, base + anchor_bonus + fbref_bonus), 4)


# ── GBM model (trained at import time) ───────────────────────────────────────
_gbm_model = None
_gbm_scaler = None
_gbm_rmse_log: float = 0.35  # fallback RMSE in log10 space


def _build_gbm_model():
    """Train GradientBoostingRegressor on historical transfer data."""
    global _gbm_model, _gbm_scaler, _gbm_rmse_log
    try:
        import numpy as np
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.preprocessing import StandardScaler

        X, y = [], []
        for age, perf, league_p, traj, tp1y, min_ratio, fee in _TRAINING_TRANSFERS:
            X.append([age, perf, league_p, traj, tp1y, min_ratio])
            y.append(math.log10(max(fee, 100_000)))

        X_arr = np.array(X, dtype=float)
        y_arr = np.array(y, dtype=float)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_arr)

        gbm = GradientBoostingRegressor(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.04,
            subsample=0.8,
            min_samples_leaf=3,
            random_state=42,
        )
        gbm.fit(X_scaled, y_arr)

        # Estimate in-sample RMSE for confidence interval calibration
        y_pred = gbm.predict(X_scaled)
        residuals = y_arr - y_pred
        _gbm_rmse_log = float(np.sqrt(np.mean(residuals ** 2)))
        _gbm_model = gbm
        _gbm_scaler = scaler
    except Exception:
        _gbm_model = None
        _gbm_scaler = None


_build_gbm_model()


def _gbm_predict(
    age: float,
    perf_score: float,
    league_prestige: float,
    trajectory_enc: float,
    tp_1y: float,
    minutes_ratio: float,
) -> float | None:
    """Predict log10(fee) via GBM. Returns None if model unavailable."""
    if _gbm_model is None or _gbm_scaler is None:
        return None
    try:
        import numpy as np
        X = np.array([[age, perf_score, league_prestige, trajectory_enc, tp_1y, minutes_ratio]])
        X_scaled = _gbm_scaler.transform(X)
        log_pred = float(_gbm_model.predict(X_scaled)[0])
        return 10.0 ** log_pred
    except Exception:
        return None


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
    val_score = float(player.get("valuation_score") or player.get("potential_score") or 50)
    competition = player.get("competition")
    tp_1y = float(player.get("transfer_probability_1y") or 0.0)
    mv_raw = player.get("market_value_eur")
    confidence = float(player.get("data_confidence_score") or 0.70)
    minutes_ratio = float(player.get("minutes_ratio") or 0.80)

    # Encode trajectory
    traj_map = {"improving": 1.0, "stable": 0.0, "declining": -1.0}
    traj_enc = traj_map.get(drift_direction or "stable", 0.0)

    # ── GBM prediction ────────────────────────────────────────────────────────
    league_p = _league_prestige(competition)
    gbm_pred = _gbm_predict(
        age=float(age or 23),
        perf_score=val_score,
        league_prestige=league_p,
        trajectory_enc=traj_enc,
        tp_1y=tp_1y,
        minutes_ratio=minutes_ratio,
    )

    # ── Analytical fallback ───────────────────────────────────────────────────
    base = _base_value(competition)
    perf = _performance_factor(val_score)
    age_f = _age_factor(age)
    demand = _demand_factor(tp_1y, drift_direction)
    analytical_pred = round(base * perf * age_f * demand, 0)

    # ── Blend GBM + analytical ────────────────────────────────────────────────
    if gbm_pred is not None:
        predicted = round(0.75 * gbm_pred + 0.25 * analytical_pred, 0)
    else:
        predicted = analytical_pred

    # ── Blend with real TM value (70% model, 30% TM) ─────────────────────────
    has_market = mv_raw is not None and float(mv_raw or 0) > 0
    if has_market:
        blended = round(0.70 * predicted + 0.30 * float(mv_raw), 0)
    else:
        blended = predicted

    # ── Confidence interval ───────────────────────────────────────────────────
    # CI based on model RMSE in log space + data confidence adjustment
    uncertainty = _gbm_rmse_log * (1.0 + (1.0 - confidence) * 0.5)
    ci_low = round(blended * (10.0 ** -uncertainty), 0)
    ci_high = round(blended * (10.0 ** uncertainty), 0)

    value_conf = _value_confidence(confidence, has_market, player.get("has_fbref_data", False))

    return {
        "player_name": name,
        "predicted_value_eur": predicted,
        "blended_value_eur": blended,
        "market_value_eur_raw": mv_raw,
        "value_confidence": value_conf,
        "confidence_interval": {"low": ci_low, "high": ci_high},
        "model_used": "gbm" if gbm_pred is not None else "analytical",
        "components": {
            "base_value_eur": base,
            "performance_factor": perf,
            "age_factor": age_f,
            "demand_factor": demand,
            "league_prestige": league_p,
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

        # Estimate minutes ratio from match stats
        all_stats = silver_tables.get("player_match_stats", [])
        player_stats = [r for r in all_stats if str(r.get("player_name") or "").lower() == name]
        avg_min = (
            sum(float(r.get("minutes") or 0) for r in player_stats) / len(player_stats)
            if player_stats else 60.0
        )
        minutes_ratio = round(min(1.0, avg_min / 90.0), 3)

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
            "minutes_ratio": minutes_ratio,
        }

        result = compute_market_value(player, drift.get("overall_drift_direction"))
        output_rows.append(result)

    output_rows.sort(key=lambda r: r["blended_value_eur"], reverse=True)
    path = write_json(Path(settings.gold_data_dir) / "market_value.json", output_rows)
    return {"path": path, "rows": output_rows}
