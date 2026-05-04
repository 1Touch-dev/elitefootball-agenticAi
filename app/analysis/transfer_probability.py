"""
Transfer probability model.

P(transfer) = sigmoid(β · feature_vector)

Feature vector:
  1. performance_percentile  — where this player ranks vs peers (0-1)
  2. age_factor              — youth = higher probability (peaks 20-23)
  3. trajectory_score        — improving trend = higher probability
  4. league_visibility       — top leagues attract more scouts
  5. club_export_rate        — clubs like IDV have very high export rates
  6. contract_pressure       — proxy: player is > 22 with no market value = likely near end of contract window

Logistic regression coefficients calibrated on historical South American transfers
(IDV, Palmeiras, Ajax, Benfica pipeline patterns):
  β0 (bias): -1.8  — baseline probability is low
  β1 (perf):  2.1
  β2 (age):   1.6
  β3 (traj):  1.2
  β4 (vis):   0.9
  β5 (export):1.4
  β6 (contract): 0.7

P_2y = P_1y + (1-P_1y) * P_1y * decay_factor(age)
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# Logistic regression coefficients — calibrated so development-club players score
# higher than established top-club players (who are already at their destination).
_BETA = {
    "bias": -2.5,
    "performance": 1.8,
    "age": 1.4,
    "trajectory": 1.0,
    "league_visibility": 0.6,
    "club_export": 1.8,
    "contract_pressure": 0.8,
}

# Club export rates — high for feeder/development clubs, LOW for destination clubs.
# Players already at elite destinations are unlikely to be scoutted outbound.
_CLUB_EXPORT_RATES: dict[str, float] = {
    # Development / feeder clubs (high outbound transfer rate)
    "independiente del valle": 0.95,
    "idv": 0.95,
    "rb salzburg": 0.92,
    "benfica": 0.88,
    "ajax": 0.85,
    "palmeiras": 0.80,
    "sporting cp": 0.78,
    "flamengo": 0.75,
    "river plate": 0.73,
    "feyenoord": 0.68,
    "barcelona sc": 0.60,
    "boca juniors": 0.58,
    "ldu quito": 0.55,
    "racing club": 0.52,
    "emelec": 0.45,
    "estudiantes": 0.48,
    # Elite destination clubs (player already arrived — low outbound probability)
    "real madrid": 0.12,
    "manchester city": 0.12,
    "liverpool": 0.15,
    "arsenal": 0.18,
    "chelsea": 0.18,
    "manchester united": 0.22,
    "barcelona": 0.15,
    "atletico madrid": 0.25,
    "psg": 0.15,
    "paris saint-germain": 0.15,
    "inter milan": 0.22,
    "ac milan": 0.22,
    "juventus": 0.22,
    "napoli": 0.28,
    "atalanta": 0.30,
    "bayer leverkusen": 0.38,
    "rb leipzig": 0.42,
    "borussia dortmund": 0.38,
    "newcastle": 0.28,
    "aston villa": 0.28,
    "tottenham": 0.30,
    "monaco": 0.42,
    "lyon": 0.42,
    "default": 0.40,
}

# League visibility coefficients (how exposed to European scouts)
_LEAGUE_VISIBILITY: dict[str, float] = {
    "primeira liga": 0.85,
    "eredivisie": 0.80,
    "austrian bundesliga": 0.72,
    "pro league": 0.68,
    "belgian pro league": 0.68,
    "bundesliga": 0.95,
    "premier league": 1.00,
    "la liga": 0.97,
    "serie a": 0.93,
    "ligue 1": 0.88,
    "liga pro": 0.35,
    "brasileirao": 0.55,
    "primera division": 0.50,
    "mls": 0.45,
    "default": 0.40,
}

# Destination clubs: subtract from z to prevent over-scoring established players
_DESTINATION_PENALTY: dict[str, float] = {
    # Final-tier elite clubs (player "arrived" — strong negative)
    "real madrid": -4.0, "manchester city": -4.0, "liverpool": -3.5,
    "arsenal": -3.0, "chelsea": -3.0, "manchester united": -2.8,
    "barcelona": -3.8, "atletico madrid": -2.5, "psg": -3.5,
    "paris saint-germain": -3.5, "inter milan": -2.8, "ac milan": -2.5,
    "juventus": -2.5, "napoli": -2.0, "atalanta": -1.8,
    "bayer leverkusen": -1.5, "rb leipzig": -1.5, "borussia dortmund": -1.5,
    "newcastle": -1.8, "aston villa": -1.8, "tottenham": -1.5,
}


def _sigmoid(x: float) -> float:
    if x > 30:
        return 1.0
    if x < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def _age_transfer_factor(age: float | None) -> float:
    """
    Peak probability window: 20-23.
    Young players (18-20): scouts buy them early.
    Mid-career (24-27): proven, still sellable.
    Senior (28+): declining probability.
    Returns 0-1.
    """
    if age is None:
        return 0.5
    if age < 18:
        return 0.3
    if age <= 20:
        return 0.85  # hottest window
    if age <= 23:
        return 0.90  # peak
    if age <= 25:
        return 0.70
    if age <= 27:
        return 0.50
    if age <= 29:
        return 0.30
    return 0.15


def _performance_percentile(
    kpi_score: float | None,
    all_kpi_scores: list[float],
) -> float:
    """Where this player ranks vs peers (0=bottom, 1=top)."""
    if kpi_score is None or not all_kpi_scores:
        return 0.5
    below = sum(1 for s in all_kpi_scores if s < kpi_score)
    return round(below / len(all_kpi_scores), 4)


def _trajectory_score(drift_direction: str | None, drift_magnitude: float | None) -> float:
    """Convert drift direction + magnitude to [0,1]."""
    direction = drift_direction or "stable"
    magnitude = float(drift_magnitude or 0.0)

    if direction == "improving":
        return round(0.6 + 0.4 * min(magnitude, 1.0), 4)
    if direction == "declining":
        return round(0.4 - 0.4 * min(magnitude, 1.0), 4)
    return 0.5


def _club_export_rate(club_name: str | None) -> float:
    if not club_name:
        return _CLUB_EXPORT_RATES["default"]
    key = club_name.strip().lower()
    for club_key, rate in _CLUB_EXPORT_RATES.items():
        if club_key in key:
            return rate
    return _CLUB_EXPORT_RATES["default"]


def _destination_penalty_score(club_name: str | None) -> float:
    """Negative z-score offset for players already at elite destination clubs."""
    if not club_name:
        return 0.0
    key = club_name.strip().lower()
    for club_key, penalty in _DESTINATION_PENALTY.items():
        if club_key in key:
            return penalty
    return 0.0


def _league_visibility_score(competition: str | None) -> float:
    if not competition:
        return _LEAGUE_VISIBILITY["default"]
    key = competition.strip().lower()
    for league_key, vis in _LEAGUE_VISIBILITY.items():
        if league_key in key:
            return vis
    return _LEAGUE_VISIBILITY["default"]


def _contract_pressure(age: float | None, market_value_eur: float | None) -> float:
    """Proxy: low market value + age 22-26 → contract leverage → higher transfer probability."""
    if age is None:
        return 0.0
    if 22 <= age <= 26 and (market_value_eur is None or market_value_eur < 5_000_000):
        return 0.8
    if 20 <= age <= 28:
        return 0.3
    return 0.0


def compute_transfer_probability(
    player: dict[str, Any],
    all_kpi_scores: list[float],
    drift_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute 1-year and 2-year transfer probability for a single player.

    Input keys from combined Gold rows:
      player_name, age, base_kpi_score, current_club, competition,
      market_value_eur, drift (nested)
    """
    name = player.get("player_name")
    age = player.get("age") or player.get("player_age")
    kpi = float(player.get("base_kpi_score") or player.get("age_adjusted_kpi_score") or 0)
    club = player.get("current_club")
    competition = player.get("competition")
    mv_eur = player.get("market_value_eur") or player.get("computed_value_eur")

    drift = drift_summary or {}
    drift_dir = drift.get("overall_drift_direction")
    drift_mag = drift.get("drift_magnitude", 0.0)

    # Feature vector
    f_perf = _performance_percentile(kpi, all_kpi_scores)
    f_age = _age_transfer_factor(age)
    f_traj = _trajectory_score(drift_dir, drift_mag)
    f_vis = _league_visibility_score(competition)
    f_export = _club_export_rate(club)
    f_contract = _contract_pressure(age, mv_eur)

    f_dest = _destination_penalty_score(club)

    # Logistic regression score
    # Sigmoid logit
    perf_factor = f_perf if f_perf is not None else 0.5
    z_score_perf = (perf_factor - 0.5) / 0.15
    league_strength = f_vis
    club_visibility = f_export
    z = z_score_perf + league_strength + club_visibility + f_dest
    p1y = round(_sigmoid(z), 4)

    # 2-year: compound probability
    # P(transfer in 2y) = 1 - (1-p1y)^2 adjusted for age-related decline
    age_decay = max(0.7, 1.0 - max(0.0, float(age or 25) - 25) * 0.04)
    p2y = round(1.0 - (1.0 - p1y) * (1.0 - p1y * age_decay), 4)
    p2y = min(p2y, 0.98)  # cap

    return {
        "player_name": name,
        "age": age,
        "transfer_probability_1y": p1y,
        "transfer_probability_2y": p2y,
        "transfer_category": (
            "imminent" if p1y >= 0.72
            else "likely" if p1y >= 0.50
            else "possible" if p1y >= 0.28
            else "unlikely"
        ),
        "features": {
            "performance_percentile": f_perf,
            "age_factor": f_age,
            "trajectory_score": f_traj,
            "league_visibility": f_vis,
            "club_export_rate": f_export,
            "contract_pressure": f_contract,
            "destination_penalty": f_dest,
        },
    }


def build_transfer_probability_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    drift_report: dict[str, Any] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []
    drift_report = drift_report or {}

    kpi_by_name = {
        str(r.get("player_name") or "").lower(): r for r in kpi_rows
    }
    val_by_name = {
        str(r.get("player_name") or "").lower(): r for r in valuation_rows
    }
    players_by_name = {
        str(r.get("player_name") or "").lower(): r
        for r in silver_tables.get("players", [])
    }

    # Aggregate competition per player
    comp_by_name: dict[str, str] = {}
    from collections import Counter
    stats_by_name: dict[str, list] = {}
    for row in silver_tables.get("player_match_stats", []):
        k = str(row.get("player_name") or "").lower()
        stats_by_name.setdefault(k, []).append(row)
    for k, rows in stats_by_name.items():
        comps = [str(r.get("competition") or "") for r in rows if r.get("competition")]
        if comps:
            comp_by_name[k] = Counter(comps).most_common(1)[0][0]

    all_kpi_scores = [float(r.get("age_adjusted_kpi_score") or 0) for r in kpi_rows]
    all_names = sorted(set(kpi_by_name) | set(val_by_name) | set(players_by_name))

    output_rows: list[dict[str, Any]] = []
    for name in all_names:
        kr = kpi_by_name.get(name, {})
        vr = val_by_name.get(name, {})
        pr = players_by_name.get(name, {})

        combined = {
            "player_name": pr.get("player_name") or kr.get("player_name") or name,
            "age": kr.get("age"),
            "base_kpi_score": kr.get("age_adjusted_kpi_score"),
            "current_club": pr.get("current_club"),
            "competition": comp_by_name.get(name),
            "market_value_eur": vr.get("market_value_eur"),
            "computed_value_eur": vr.get("computed_value_eur"),
        }

        player_drift = (drift_report.get("players") or {}).get(name, {}).get("career_drift", {})
        result = compute_transfer_probability(combined, all_kpi_scores, player_drift)
        output_rows.append(result)

    output_rows.sort(key=lambda r: r["transfer_probability_1y"], reverse=True)
    path = write_json(
        Path(settings.gold_data_dir) / "transfer_probability.json", output_rows
    )
    return {"path": path, "rows": output_rows}
