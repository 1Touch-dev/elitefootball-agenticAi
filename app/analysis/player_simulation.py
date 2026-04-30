"""
Player Simulation Engine.

Simulates projected performance for a player moving to a target league or club.

Model:
  projected_kpi = current_kpi
    × league_difficulty_factor(current → target)
    × tactical_fit_factor(player, target_club)
    × minutes_probability(age, performance, new_club_competition)
    × trajectory_momentum(age, direction)

  projected_valuation = current_valuation_score × same adjustments (slightly compressed)

  adaptation_months = f(prestige_gap, age, trajectory)

Output per (player, target_league):
  projected_kpi, projected_valuation_score, projected_value_eur,
  minutes_probability, adaptation_months, simulation_confidence
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# ── League difficulty coefficients ───────────────────────────────────────────
# How much raw performance typically degrades moving to a harder league.
# Current prestige → target prestige → factor on current metrics.
# Factor < 1.0 means harder league (player looks worse initially).
# Factor > 1.0 means easier league (player looks better).
_PRESTIGE_LEVELS: dict[str, float] = {
    "liga pro": 0.25,
    "primera division": 0.50,
    "brasileirao": 0.55,
    "austrian bundesliga": 0.60,
    "pro league": 0.65,
    "primera liga": 0.70,
    "eredivisie": 0.72,
    "ligue 1": 0.82,
    "bundesliga": 0.88,
    "serie a": 0.90,
    "la liga": 0.95,
    "premier league": 1.00,
}

_TARGET_LEAGUES = [
    "liga pro", "austrian bundesliga", "primera liga", "eredivisie",
    "pro league", "brasileirao", "ligue 1", "bundesliga", "serie a",
    "la liga", "premier league",
]

# Club → league mapping for simulation
_CLUB_LEAGUE: dict[str, str] = {
    "rb salzburg": "austrian bundesliga",
    "brighton": "premier league",
    "chelsea": "premier league",
    "bayer leverkusen": "bundesliga",
    "benfica": "primeira liga",
    "sporting cp": "primeira liga",
    "porto": "primeira liga",
    "ajax": "eredivisie",
    "feyenoord": "eredivisie",
    "eindhoven": "eredivisie",
    "club brugge": "pro league",
    "atalanta": "serie a",
    "inter milan": "serie a",
    "real madrid": "la liga",
    "barcelona": "la liga",
    "atletico madrid": "la liga",
    "villarreal": "la liga",
    "nottingham forest": "premier league",
}

# Minutes probability: how likely is a new signing to get adequate minutes (≥60/game)
# Depends on: age (young = uncertain), performance tier, club prestige gap
def _minutes_probability(
    age: float | None,
    performance_score: float | None,
    prestige_gap: float,
) -> float:
    """
    Probability of getting regular minutes (≥45/game) at target club.
    Young high-performers at modest step-ups get high probability.
    Big jumps → harder to displace established players.
    """
    a = float(age or 22)
    perf = float(performance_score or 60)

    # Base probability from performance
    base = min(0.95, max(0.30, (perf - 50) / 50.0 + 0.55))

    # Age adjustment: prime age (22-28) slightly better than very young or old
    if a < 20:
        age_adj = -0.10  # youth → often rotation
    elif a <= 28:
        age_adj = 0.0
    else:
        age_adj = -0.05 * (a - 28)  # declining minutes with age

    # Prestige gap: bigger jump → harder to get minutes
    if prestige_gap > 0.40:
        gap_adj = -0.15 * (prestige_gap - 0.40) / 0.60
    elif prestige_gap > 0.20:
        gap_adj = -0.05
    else:
        gap_adj = 0.05  # small step or lateral → established player goes straight in

    prob = base + age_adj + gap_adj
    return round(min(0.95, max(0.25, prob)), 4)


def _adaptation_months(
    age: float | None,
    prestige_gap: float,
    trajectory: str | None,
) -> int:
    """
    How many months before player reaches peak projected performance.
    Young + improving + modest gap → fast (2-3 months).
    Older + declining + big gap → slow (6-12 months).
    """
    a = float(age or 22)
    base_months = 3

    # Gap penalty
    if prestige_gap > 0.50:
        base_months += 5
    elif prestige_gap > 0.30:
        base_months += 3
    elif prestige_gap > 0.10:
        base_months += 1

    # Age factor
    if a < 21:
        base_months += 1  # youth needs time
    elif a > 28:
        base_months += 2  # veterans adapt slower

    # Trajectory
    if trajectory == "improving":
        base_months = max(2, base_months - 1)
    elif trajectory == "declining":
        base_months += 2

    return min(12, max(2, base_months))


def _league_difficulty_factor(src_prestige: float, dst_prestige: float) -> float:
    """
    Multiplicative factor on current metrics when moving to target league.
    Harder league → factor < 1.0, easier → > 1.0.
    """
    delta = dst_prestige - src_prestige
    if delta <= 0:
        # Moving to an easier or same-level league — some uplift
        return round(1.0 + abs(delta) * 0.15, 4)
    # Steeper curve for bigger jumps — performance drops non-linearly
    factor = 1.0 - delta * 0.55 - delta ** 2 * 0.15
    return round(max(0.55, factor), 4)


def _trajectory_momentum(age: float | None, trajectory: str | None) -> float:
    """
    Improving young players often continue growing after a move (positive momentum).
    Declining older players risk accelerating decline under new pressure.
    """
    a = float(age or 22)
    if trajectory == "improving" and a <= 25:
        return 1.05
    if trajectory == "improving" and a <= 28:
        return 1.02
    if trajectory == "declining" and a >= 28:
        return 0.95
    if trajectory == "declining":
        return 0.97
    return 1.00


def simulate_player_in_league(
    player_name: str,
    age: float | None,
    current_kpi: float | None,
    current_valuation_score: float | None,
    current_league: str | None,
    trajectory: str | None,
    target_league: str,
    tactical_fit_score: float | None = None,
    performance_score: float | None = None,
) -> dict[str, Any]:
    """Simulate one player's performance in a specific target league."""
    src_prestige = _PRESTIGE_LEVELS.get(
        (current_league or "").lower().strip(), 0.40
    )
    dst_prestige = _PRESTIGE_LEVELS.get(target_league.lower().strip(), 0.50)
    prestige_gap = max(0.0, dst_prestige - src_prestige)

    diff_factor = _league_difficulty_factor(src_prestige, dst_prestige)
    fit_boost = float(tactical_fit_score or 0.5) * 0.10 + 0.95  # 0.95 to 1.05
    minutes_prob = _minutes_probability(age, performance_score, prestige_gap)
    momentum = _trajectory_momentum(age, trajectory)
    adapt_months = _adaptation_months(age, prestige_gap, trajectory)

    # Combined simulation factor
    sim_factor = diff_factor * fit_boost * momentum

    # Projected KPI (capped to realistic range)
    base_kpi = float(current_kpi or 8.0)
    proj_kpi = round(base_kpi * sim_factor * minutes_prob ** 0.3, 3)
    proj_kpi = max(5.0, min(14.0, proj_kpi))

    # Projected valuation score
    base_val = float(current_valuation_score or 50)
    proj_val = round(base_val * (sim_factor ** 0.7), 2)
    proj_val = max(20.0, min(95.0, proj_val))

    # Projected € value (using analytical formula in target league context)
    from app.analysis.market_value_model import _base_value, _performance_factor, _age_factor
    target_base = _base_value(target_league)
    proj_value_eur = round(target_base * _performance_factor(proj_val) * _age_factor(age), 0)

    # Simulation confidence
    sim_conf = round(
        0.50  # base
        + 0.20 * (1.0 - prestige_gap)  # smaller gap = more reliable
        + 0.15 * minutes_prob
        + 0.15 * (float(tactical_fit_score or 0.5)),
        4,
    )

    return {
        "target_league": target_league,
        "target_league_prestige": dst_prestige,
        "projected_kpi": proj_kpi,
        "projected_valuation_score": proj_val,
        "projected_value_eur": proj_value_eur,
        "minutes_probability": minutes_prob,
        "adaptation_months": adapt_months,
        "simulation_confidence": round(min(1.0, sim_conf), 4),
        "factors": {
            "league_difficulty": diff_factor,
            "tactical_fit": round(fit_boost, 4),
            "trajectory_momentum": momentum,
            "prestige_gap": round(prestige_gap, 3),
        },
    }


def compute_player_simulation(
    player: dict[str, Any],
    club_fit_row: dict[str, Any] | None = None,
    target_leagues: list[str] | None = None,
) -> dict[str, Any]:
    """
    Full simulation for one player across multiple target leagues.
    Returns top recommendations sorted by projected_value_eur.
    """
    name = player.get("player_name")
    age = player.get("age")
    current_kpi = player.get("age_adjusted_kpi_score") or player.get("base_kpi_score")
    val_score = player.get("valuation_score")
    current_league = player.get("competition")
    trajectory = player.get("trajectory") or player.get("drift_direction")
    performance_score = val_score

    # Build fit score index
    fit_by_league: dict[str, float] = {}
    if club_fit_row:
        for fit in club_fit_row.get("top_5_club_fits") or []:
            club = str(fit.get("club") or "").lower()
            league = _CLUB_LEAGUE.get(club)
            if league:
                fit_by_league[league] = float(fit.get("fit_score") or 0.5)

    leagues_to_sim = target_leagues or _TARGET_LEAGUES
    simulations: list[dict[str, Any]] = []

    for league in leagues_to_sim:
        fit_score = fit_by_league.get(league, 0.5)
        sim = simulate_player_in_league(
            player_name=str(name or ""),
            age=age,
            current_kpi=current_kpi,
            current_valuation_score=val_score,
            current_league=current_league,
            trajectory=trajectory,
            target_league=league,
            tactical_fit_score=fit_score,
            performance_score=performance_score,
        )
        simulations.append(sim)

    simulations.sort(key=lambda s: s["projected_value_eur"], reverse=True)

    best = simulations[0] if simulations else {}
    return {
        "player_name": name,
        "age": age,
        "current_league": current_league,
        "current_kpi": current_kpi,
        "current_valuation_score": val_score,
        "trajectory": trajectory,
        "best_projection": {
            "target_league": best.get("target_league"),
            "projected_kpi": best.get("projected_kpi"),
            "projected_value_eur": best.get("projected_value_eur"),
            "minutes_probability": best.get("minutes_probability"),
            "simulation_confidence": best.get("simulation_confidence"),
        },
        "league_simulations": simulations,
    }


def build_player_simulation_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    club_fit_rows: list[dict[str, Any]] | None = None,
    drift_report: dict[str, Any] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []
    club_fit_rows = club_fit_rows or []
    drift_report = drift_report or {}

    def _nk(name: Any) -> str:
        return str(name or "").strip().lower()

    kpi_by_name = {_nk(r.get("player_name")): r for r in kpi_rows}
    val_by_name = {_nk(r.get("player_name")): r for r in valuation_rows}
    fit_by_name = {_nk(r.get("player_name")): r for r in club_fit_rows}
    players_by_name = {
        _nk(r.get("player_name")): r
        for r in silver_tables.get("players", [])
    }

    comp_by_name: dict[str, str] = {}
    for row in silver_tables.get("player_match_stats", []):
        k = _nk(row.get("player_name"))
        if row.get("competition"):
            comp_by_name.setdefault(k, row["competition"])

    all_names = sorted(set(kpi_by_name) | set(val_by_name) | set(players_by_name))
    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        kr = kpi_by_name.get(name, {})
        vr = val_by_name.get(name, {})
        pr = players_by_name.get(name, {})
        drift = drift_report.get("players", {}).get(name, {}).get("career_drift", {})

        player = {
            "player_name": pr.get("player_name") or kr.get("player_name") or name,
            "age": kr.get("age"),
            "valuation_score": vr.get("valuation_score"),
            "age_adjusted_kpi_score": kr.get("age_adjusted_kpi_score"),
            "base_kpi_score": kr.get("base_kpi_score"),
            "competition": comp_by_name.get(name) or vr.get("competition"),
            "trajectory": drift.get("overall_drift_direction"),
        }

        result = compute_player_simulation(
            player=player,
            club_fit_row=fit_by_name.get(name),
        )
        output_rows.append(result)

    # Sort by best projected value
    output_rows.sort(
        key=lambda r: r.get("best_projection", {}).get("projected_value_eur", 0),
        reverse=True,
    )

    path = write_json(Path(settings.gold_data_dir) / "player_simulations.json", output_rows)
    return {"path": path, "rows": output_rows}
