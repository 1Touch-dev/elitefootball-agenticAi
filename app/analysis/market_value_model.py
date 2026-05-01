"""
Market Value Model — GradientBoosting-based € prediction with confidence intervals.

Model: sklearn GradientBoostingRegressor trained on real TM market value history
       (150+ players × multiple career snapshots from data/parsed/transfermarkt/).
       Falls back to hardcoded seed data if parsed files not available.
Blend: GBM prediction 70% + Transfermarkt actual value 30% (when available).
Fallback: analytical formula if sklearn unavailable.

Features: age, performance_score, league_prestige, trajectory_enc,
          transfer_prob_1y, minutes_ratio
Target: log10(market_value_eur) — peak MV at each career stage is the label.

Output per player:
  predicted_value_eur, blended_value_eur, confidence_interval (low, high),
  value_confidence, components (for transparency)
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# ── Club → league prestige lookup (for training data extraction) ──────────────
_CLUB_PRESTIGE_HINTS: dict[str, float] = {
    "real madrid": 1.00, "manchester city": 1.00, "barcelona": 0.97,
    "liverpool": 0.97, "arsenal": 0.92, "chelsea": 0.92,
    "manchester united": 0.90, "psg": 0.88, "paris saint-germain": 0.88,
    "inter milan": 0.90, "ac milan": 0.90, "juventus": 0.88,
    "napoli": 0.85, "atletico madrid": 0.90, "bayer leverkusen": 0.85,
    "rb leipzig": 0.85, "borussia dortmund": 0.85, "atalanta": 0.80,
    "monaco": 0.80, "lyon": 0.78, "feyenoord": 0.72, "ajax": 0.72,
    "psv": 0.68, "anderlecht": 0.65, "club brugge": 0.65,
    "rb salzburg": 0.60, "sporting cp": 0.70, "benfica": 0.72,
    "porto": 0.72, "flamengo": 0.55, "palmeiras": 0.55,
    "fluminense": 0.50, "santos": 0.50, "corinthians": 0.50,
    "river plate": 0.52, "boca juniors": 0.50, "racing club": 0.45,
    "independiente del valle": 0.25, "barcelona sc": 0.25,
    "newcastle": 0.82, "aston villa": 0.80, "tottenham": 0.85,
    "default": 0.40,
}


def _club_prestige(club_name: str | None) -> float:
    if not club_name:
        return _CLUB_PRESTIGE_HINTS["default"]
    key = club_name.strip().lower()
    for k, v in _CLUB_PRESTIGE_HINTS.items():
        if k in key:
            return v
    return _CLUB_PRESTIGE_HINTS["default"]


def _extract_real_training_data() -> list[tuple]:
    """
    Build training samples from real TM mv_history in parsed files.
    Each player contributes one sample per career club stage.
    Returns list of (age, perf_score, league_prestige, trajectory_enc, tp_1y, min_ratio, mv_eur).
    """
    parsed_dir = Path("data/parsed/transfermarkt")
    if not parsed_dir.exists():
        return []

    samples: list[tuple] = []
    files = list(parsed_dir.glob("*.json"))

    for fpath in files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue

        mv_history = data.get("mv_history") or []
        if len(mv_history) < 2:
            continue

        # Sort by age
        mv_sorted = sorted(
            [e for e in mv_history if e.get("value_eur") and e.get("age")],
            key=lambda e: float(e.get("age", 0))
        )
        if not mv_sorted:
            continue

        peak_mv = max(e["value_eur"] for e in mv_sorted if e.get("value_eur"))
        if peak_mv < 100_000:
            continue

        # Walk through career stages, grouping by club
        club_groups: list[dict] = []
        current_club = None
        current_vals: list[float] = []
        current_ages: list[float] = []

        for entry in mv_sorted:
            club = entry.get("club", "")
            val = float(entry.get("value_eur", 0))
            age = float(entry.get("age", 0))
            if val <= 0 or age <= 0:
                continue
            if club != current_club:
                if current_vals:
                    club_groups.append({
                        "club": current_club,
                        "ages": current_ages,
                        "values": current_vals,
                    })
                current_club = club
                current_vals = [val]
                current_ages = [age]
            else:
                current_vals.append(val)
                current_ages.append(age)

        if current_vals:
            club_groups.append({"club": current_club, "ages": current_ages, "values": current_vals})

        for grp in club_groups:
            if not grp["values"]:
                continue
            peak_at_club = max(grp["values"])
            mid_age = grp["ages"][len(grp["ages"]) // 2]

            # Trajectory within club spell
            vals = grp["values"]
            if len(vals) >= 2:
                delta = (vals[-1] - vals[0]) / max(vals[0], 1)
                traj_enc = 1.0 if delta > 0.20 else (-1.0 if delta < -0.10 else 0.0)
            else:
                traj_enc = 0.0

            prestige = _club_prestige(grp["club"])
            # Normalize perf_score: peak value relative to position in career
            rel_val = peak_at_club / max(peak_mv, 1)
            perf_score = round(40 + 60 * min(1.0, rel_val), 1)

            # Transfer probability proxy: high for young improving players at development clubs
            tp_proxy = 0.70 if (mid_age <= 24 and prestige < 0.60 and traj_enc >= 0.0) else (
                0.50 if mid_age <= 27 else 0.30
            )

            samples.append((
                mid_age, perf_score, prestige, traj_enc,
                tp_proxy, 0.85,
                peak_at_club
            ))

    return samples


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


# ── Hardcoded seed data (augmentation when parsed files unavailable) ──────────
# (age, perf_score, league_prestige, trajectory_enc, tp_1y, minutes_ratio, mv_eur)
_SEED_TRANSFERS: list[tuple] = [
    (20, 87, 0.25, 1, 0.92, 0.88, 115_000_000),
    (20, 83, 0.25, 1, 0.88, 0.82, 30_000_000),
    (19, 80, 0.25, 1, 0.85, 0.80, 18_000_000),
    (21, 82, 0.25, 1, 0.80, 0.85, 22_000_000),
    (22, 79, 0.25, 0, 0.70, 0.90, 12_000_000),
    (18, 75, 0.25, 1, 0.75, 0.65, 8_000_000),
    (19, 85, 0.55, 1, 0.90, 0.75, 35_000_000),
    (21, 83, 0.55, 1, 0.85, 0.85, 28_000_000),
    (22, 82, 0.50, 1, 0.85, 0.80, 22_000_000),
    (22, 82, 0.70, 1, 0.80, 0.88, 25_000_000),
    (22, 82, 0.72, 1, 0.82, 0.88, 28_000_000),
    (20, 79, 0.60, 1, 0.82, 0.85, 14_000_000),
    (23, 85, 0.88, 1, 0.82, 0.88, 60_000_000),
    (24, 87, 0.88, 1, 0.85, 0.90, 80_000_000),
    (23, 88, 1.00, 1, 0.85, 0.88, 90_000_000),
    (24, 90, 1.00, 1, 0.88, 0.90, 120_000_000),
    (22, 86, 1.00, 1, 0.82, 0.85, 70_000_000),
    (22, 92, 0.95, 1, 0.92, 0.92, 160_000_000),
    (27, 80, 0.88, -1, 0.55, 0.90, 22_000_000),
    (29, 80, 0.88, -1, 0.55, 0.88, 18_000_000),
    (22, 65, 0.25, 0, 0.50, 0.70, 2_000_000),
    (24, 68, 0.25, 0, 0.45, 0.75, 2_500_000),
    (23, 62, 0.50, 0, 0.48, 0.72, 3_000_000),
    (22, 80, 0.65, 1, 0.80, 0.88, 16_000_000),
    (17, 72, 0.50, 1, 0.70, 0.55, 6_000_000),
    (16, 68, 0.88, 1, 0.65, 0.40, 4_000_000),
    (18, 76, 0.72, 1, 0.75, 0.68, 10_000_000),
    (23, 82, 0.82, 1, 0.80, 0.88, 28_000_000),
    (29, 82, 0.88, 0, 0.80, 0.88, 1_000_000),
    (30, 80, 0.95, 0, 0.85, 0.88, 1_500_000),
]


# ── GBM model (trained at import time from real data) ────────────────────────
_gbm_model = None
_gbm_scaler = None
_gbm_rmse_log: float = 0.35  # fallback RMSE in log10 space
_training_source: str = "seed"


def _build_gbm_model() -> None:
    """Train GradientBoostingRegressor on real TM mv_history + seed augmentation."""
    global _gbm_model, _gbm_scaler, _gbm_rmse_log, _training_source
    try:
        import numpy as np
        from sklearn.ensemble import GradientBoostingRegressor
        from sklearn.preprocessing import StandardScaler

        real_samples = _extract_real_training_data()
        if len(real_samples) >= 50:
            # Real data dominates; seed data only for coverage at extremes
            training = real_samples + _SEED_TRANSFERS
            _training_source = f"real({len(real_samples)})+seed({len(_SEED_TRANSFERS)})"
        else:
            # Fall back to seed only
            training = _SEED_TRANSFERS
            _training_source = f"seed_only({len(_SEED_TRANSFERS)})"

        X, y = [], []
        for age, perf, league_p, traj, tp1y, min_ratio, mv in training:
            X.append([age, perf, league_p, traj, tp1y, min_ratio])
            y.append(math.log10(max(mv, 100_000)))

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

        y_pred = gbm.predict(X_scaled)
        _gbm_rmse_log = float(np.sqrt(np.mean((y_arr - y_pred) ** 2)))
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
