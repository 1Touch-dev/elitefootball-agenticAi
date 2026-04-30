"""
Development & Pathway Intelligence Engine.
Computes age-vs-league percentile, improvement rate, development velocity,
career trajectory, and best pathway recommendation.
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "pathway_v1"

# Comparable club pathway presets (source → likely next tier).
# Keys are substrings matched against lowercased club name.
PATHWAY_TEMPLATES: dict[str, list[str]] = {
    "independiente del valle": ["primeira liga", "eredivisie", "austrian bundesliga", "bundesliga"],
    "idv": ["primeira liga", "eredivisie", "austrian bundesliga", "bundesliga"],
    "barcelona sc": ["copa libertadores", "brasileirao", "primera división"],
    "barcelona": ["premier league", "la liga", "bundesliga"],
    "emelec": ["copa libertadores", "liga mx", "primera división"],
    "ldu quito": ["copa libertadores", "eredivisie", "primeira liga"],
    "benfica": ["premier league", "la liga", "bundesliga"],
    "ajax": ["premier league", "bundesliga", "la liga"],
    "salzburg": ["bundesliga", "premier league", "serie a"],
    "porto": ["premier league", "la liga", "serie a"],
    "sporting": ["premier league", "la liga", "bundesliga"],
}

# Historical IDV success comps (role → outcome)
IDV_HISTORICAL_OUTCOMES: list[dict[str, Any]] = [
    {"name": "Caicedo analogue", "age_at_breakout": 19, "role": "midfielder", "outcome": "premier league", "success": True},
    {"name": "Villalba analogue", "age_at_breakout": 22, "role": "forward", "outcome": "libertadores run", "success": True},
]


def _normalize(v: str | None) -> str:
    return str(v or "").strip().lower()


def age_league_percentile(age: float | None, kpi_score: float | None, competition: str | None) -> float:
    """
    Rough percentile of player vs expected performance for their age in that league.
    Returns 0–100.
    """
    if age is None or kpi_score is None:
        return 50.0
    expected_kpi_at_age = _expected_kpi(age)
    ratio = float(kpi_score) / max(expected_kpi_at_age, 1.0)
    percentile = min(99.0, max(1.0, ratio * 50.0))
    return round(percentile, 1)


def _expected_kpi(age: float) -> float:
    """Age→expected KPI curve calibrated to actual score range (8–14, peaks at 26)."""
    peak = 26.0
    if age <= peak:
        return 8.0 + (age / peak) * 6.0
    return max(6.0, 14.0 - (age - peak) * 0.4)


def improvement_rate(kpi_history: list[float]) -> float:
    """Linear regression slope of KPI over time periods. Returns KPI delta per period."""
    n = len(kpi_history)
    if n < 2:
        return 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(kpi_history) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, kpi_history))
    den = sum((x - x_mean) ** 2 for x in xs)
    return round(num / den if den > 0 else 0.0, 3)


def development_velocity(kpi_history: list[float], age: float | None) -> float:
    """
    Rate of improvement weighted by age — young players at same improvement rate
    score higher velocity.
    """
    rate = improvement_rate(kpi_history)
    if age is None:
        return round(rate, 3)
    age_multiplier = max(0.5, 1.5 - (max(0, float(age) - 20) * 0.05))
    return round(rate * age_multiplier, 3)


def minutes_growth_curve(minutes_history: list[float]) -> dict[str, Any]:
    """Trend in minutes played across seasons/periods."""
    if not minutes_history:
        return {"trend": "unknown", "delta": 0.0, "series": []}
    deltas = [minutes_history[i] - minutes_history[i - 1] for i in range(1, len(minutes_history))]
    avg_delta = sum(deltas) / len(deltas) if deltas else 0.0
    if avg_delta > 100:
        trend = "ascending"
    elif avg_delta < -100:
        trend = "declining"
    else:
        trend = "stable"
    return {"trend": trend, "delta": round(avg_delta, 1), "series": [round(m, 0) for m in minutes_history]}


def career_trajectory(kpi_history: list[float], age: float | None) -> str:
    n = len(kpi_history)
    if n < 2:
        # Single data point — infer from age: young players assumed ascending
        if age and age <= 22:
            return "ascending"
        if age and age >= 32:
            return "declining"
        return "stable"
    rate = improvement_rate(kpi_history)
    if age and age > 30 and rate <= 0:
        return "declining"
    if rate > 0.5:
        return "ascending"
    if rate >= -0.3:
        return "stable"
    return "declining"


def best_pathway(
    current_club: str | None,
    position: str | None,
    age: float | None,
    trajectory: str = "stable",
    valuation_score: float = 50.0,
) -> list[str]:
    """Recommend next club tiers based on current club and player profile."""
    club_key = _normalize(current_club)
    for alias, pathways in PATHWAY_TEMPLATES.items():
        if alias in club_key:
            if trajectory == "ascending" and valuation_score >= 60:
                return pathways[:2]
            return pathways[:1]
    if valuation_score >= 70:
        return ["tier-1 european league"]
    if valuation_score >= 50:
        return ["tier-2 european league", "copa libertadores"]
    return ["domestic league improvement"]


def success_probability(
    age: float | None,
    valuation_score: float,
    trajectory: str,
    percentile: float,
) -> float:
    """0–1 estimate based on comparable player outcomes."""
    base = valuation_score / 100.0
    traj_mult = {"ascending": 1.2, "stable": 1.0, "declining": 0.7}.get(trajectory, 1.0)
    age_mult = 1.0 if (age or 25) <= 24 else max(0.5, 1.0 - ((age or 25) - 24) * 0.04)
    perc_mult = (percentile / 100.0) * 0.5 + 0.5
    raw = base * traj_mult * age_mult * perc_mult
    return round(min(1.0, max(0.0, raw)), 3)


def development_stage(age: float | None, valuation_score: float) -> str:
    a = age or 25
    if a < 21:
        return "prospect"
    if a < 24:
        return "emerging"
    if a < 29:
        return "peak"
    return "veteran"


# ── Builder ───────────────────────────────────────────────────────────────────

def build_pathway_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    from app.analysis.kpi_formulas import age_in_years

    valuation_rows = valuation_rows or []

    players_by_name = {_normalize(r.get("player_name")): r for r in silver_tables.get("players", [])}
    features_by_name = {_normalize(r.get("player_name")): r for r in gold_tables.get("player_features", [])}
    kpi_by_name = {_normalize(r.get("player_name")): r for r in kpi_rows}
    val_by_name = {_normalize(r.get("player_name")): r for r in valuation_rows}

    stat_rows_by_name: dict[str, list] = defaultdict(list)
    for row in silver_tables.get("player_match_stats", []):
        stat_rows_by_name[_normalize(row.get("player_name"))].append(row)

    all_names = sorted(set(players_by_name) | set(features_by_name) | set(kpi_by_name))

    if not all_names:
        path = write_json(Path(settings.gold_data_dir) / "player_pathway.json", [])
        return {"path": path, "rows": []}

    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        pr = players_by_name.get(name, {})
        fr = features_by_name.get(name, {})
        kr = kpi_by_name.get(name, {})
        vr = val_by_name.get(name, {})
        stats = stat_rows_by_name.get(name, [])

        age = kr.get("age") or age_in_years(pr.get("date_of_birth"))
        kpi_score = float(kr.get("base_kpi_score") or 0.0)
        val_score = float(vr.get("valuation_score") or 50.0)
        club_name = pr.get("current_club") or fr.get("current_club")
        position = pr.get("position")

        # Build multi-point KPI history from match stats sorted by date
        sorted_stats = sorted(stats, key=lambda s: s.get("match_date") or "")
        minutes_series = [float(s.get("minutes") or 0) for s in sorted_stats]

        # Rolling contribution score per match as a proxy KPI history
        def _match_contribution(s: dict) -> float:
            mins = float(s.get("minutes") or 1)
            gc = float(s.get("goals") or 0) + float(s.get("assists") or 0)
            shots = float(s.get("shots") or 0)
            xg = float(s.get("xg") or 0)
            xa = float(s.get("xa") or 0)
            return round((gc * 2.5 + shots * 0.2 + xg * 1.5 + xa * 1.2) / max(mins / 90, 0.1), 3)

        match_contributions = [_match_contribution(s) for s in sorted_stats]
        kpi_history: list[float]
        if len(match_contributions) >= 3:
            # Use rolling 3-match windows as history points
            window = 3
            kpi_history = [
                sum(match_contributions[i:i+window]) / window
                for i in range(0, len(match_contributions) - window + 1)
            ]
        elif len(match_contributions) >= 1:
            kpi_history = match_contributions
        else:
            kpi_history = [kpi_score]

        traj = career_trajectory(kpi_history, age)
        percentile = age_league_percentile(age, kpi_score, None)
        velocity = development_velocity(kpi_history, age)
        mg_curve = minutes_growth_curve(minutes_series)
        pathways = best_pathway(club_name, position, age, traj, val_score)
        prob = success_probability(age, val_score, traj, percentile)
        stage = development_stage(age, val_score)

        display_name = pr.get("player_name") or fr.get("player_name") or kr.get("player_name") or name

        output_rows.append({
            "player_name": display_name,
            "position": position,
            "current_club": club_name,
            "development_stage": stage,
            "trajectory": traj,
            "age_league_percentile": percentile,
            "improvement_rate": improvement_rate(kpi_history),
            "development_velocity": velocity,
            "minutes_growth": mg_curve,
            "best_pathway": pathways,
            "success_probability": prob,
            "inputs": {
                "age": age,
                "kpi_score": kpi_score,
                "valuation_score": val_score,
            },
            "model_version": MODEL_VERSION,
        })

    output_rows.sort(key=lambda r: r["success_probability"], reverse=True)
    path = write_json(Path(settings.gold_data_dir) / "player_pathway.json", output_rows)
    return {"path": path, "rows": output_rows}
