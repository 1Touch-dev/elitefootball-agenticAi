"""
Club fit model — tactical profiles included.

For each player, scores compatibility with a set of target clubs.

Fit score = Σ w_i * component_i

Components:
  1. role_similarity       (0-1) — position/style match
  2. age_profile_match     (0-1) — player age vs club's typical buy window
  3. league_step_up        (0-1) — logical prestige progression
  4. value_accessibility   (0-1) — affordable relative to club's typical spend
  5. tactical_fit          (0-1) — pressing intensity, formation, physical/technical demand
  6. historical_pathway    (0-1) — South-American players have succeeded here
  7. positional_demand     (0-1) — how urgently the club needs this position

Weights: role=0.25, age=0.20, league=0.18, value=0.12, tactical=0.12, pathway=0.08, demand=0.05
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


# Club profiles: typical buy age, typical spend (EUR), league prestige 0-1,
# historical_pathway (clubs that have taken IDV/South-Am exports),
# pressing_intensity (0=low block, 1=gegenpressing),
# formation_style, physical_demand, technical_demand,
# positional_need: {"FW": 0-1, "MF": 0-1, "DF": 0-1, "GK": 0-1}
_CLUB_PROFILES: dict[str, dict[str, Any]] = {
    "brighton": {
        "typical_buy_age": (19, 23), "typical_spend_eur": 15_000_000,
        "prestige": 0.72, "roles": ["MF", "DF", "FW"], "pathway_score": 0.90,
        "pressing_intensity": 0.80, "formation_style": "4-2-3-1",
        "physical_demand": 0.75, "technical_demand": 0.85,
        "positional_need": {"FW": 0.7, "MF": 0.9, "DF": 0.8, "GK": 0.4},
    },
    "chelsea": {
        "typical_buy_age": (17, 22), "typical_spend_eur": 35_000_000,
        "prestige": 0.88, "roles": ["FW", "MF", "DF"], "pathway_score": 0.85,
        "pressing_intensity": 0.70, "formation_style": "4-3-3",
        "physical_demand": 0.80, "technical_demand": 0.90,
        "positional_need": {"FW": 0.8, "MF": 0.85, "DF": 0.7, "GK": 0.3},
    },
    "bayer leverkusen": {
        "typical_buy_age": (18, 24), "typical_spend_eur": 20_000_000,
        "prestige": 0.85, "roles": ["MF", "FW", "DF"], "pathway_score": 0.75,
        "pressing_intensity": 0.90, "formation_style": "4-2-3-1",
        "physical_demand": 0.88, "technical_demand": 0.85,
        "positional_need": {"FW": 0.8, "MF": 0.9, "DF": 0.75, "GK": 0.3},
    },
    "rb salzburg": {
        "typical_buy_age": (17, 22), "typical_spend_eur": 8_000_000,
        "prestige": 0.68, "roles": ["FW", "MF", "DF"], "pathway_score": 0.92,
        "pressing_intensity": 0.95, "formation_style": "4-2-2-2",
        "physical_demand": 0.92, "technical_demand": 0.75,
        "positional_need": {"FW": 0.95, "MF": 0.90, "DF": 0.80, "GK": 0.5},
    },
    "benfica": {
        "typical_buy_age": (18, 24), "typical_spend_eur": 12_000_000,
        "prestige": 0.78, "roles": ["FW", "MF", "DF"], "pathway_score": 0.88,
        "pressing_intensity": 0.72, "formation_style": "4-4-2",
        "physical_demand": 0.75, "technical_demand": 0.82,
        "positional_need": {"FW": 0.85, "MF": 0.80, "DF": 0.75, "GK": 0.4},
    },
    "sporting cp": {
        "typical_buy_age": (18, 25), "typical_spend_eur": 10_000_000,
        "prestige": 0.76, "roles": ["FW", "MF", "DF"], "pathway_score": 0.80,
        "pressing_intensity": 0.75, "formation_style": "4-3-3",
        "physical_demand": 0.76, "technical_demand": 0.82,
        "positional_need": {"FW": 0.80, "MF": 0.85, "DF": 0.70, "GK": 0.4},
    },
    "ajax": {
        "typical_buy_age": (17, 22), "typical_spend_eur": 10_000_000,
        "prestige": 0.80, "roles": ["FW", "MF", "DF"], "pathway_score": 0.88,
        "pressing_intensity": 0.80, "formation_style": "4-3-3",
        "physical_demand": 0.72, "technical_demand": 0.95,
        "positional_need": {"FW": 0.80, "MF": 0.90, "DF": 0.75, "GK": 0.4},
    },
    "feyenoord": {
        "typical_buy_age": (19, 25), "typical_spend_eur": 8_000_000,
        "prestige": 0.72, "roles": ["FW", "MF", "DF"], "pathway_score": 0.70,
        "pressing_intensity": 0.78, "formation_style": "4-3-3",
        "physical_demand": 0.74, "technical_demand": 0.80,
        "positional_need": {"FW": 0.75, "MF": 0.80, "DF": 0.70, "GK": 0.4},
    },
    "club brugge": {
        "typical_buy_age": (19, 25), "typical_spend_eur": 7_000_000,
        "prestige": 0.65, "roles": ["FW", "MF", "DF"], "pathway_score": 0.65,
        "pressing_intensity": 0.72, "formation_style": "4-3-3",
        "physical_demand": 0.72, "technical_demand": 0.78,
        "positional_need": {"FW": 0.70, "MF": 0.75, "DF": 0.65, "GK": 0.4},
    },
    "atalanta": {
        "typical_buy_age": (20, 26), "typical_spend_eur": 15_000_000,
        "prestige": 0.82, "roles": ["FW", "MF", "DF"], "pathway_score": 0.70,
        "pressing_intensity": 0.88, "formation_style": "3-4-1-2",
        "physical_demand": 0.90, "technical_demand": 0.82,
        "positional_need": {"FW": 0.85, "MF": 0.80, "DF": 0.85, "GK": 0.4},
    },
    "inter milan": {
        "typical_buy_age": (21, 27), "typical_spend_eur": 25_000_000,
        "prestige": 0.92, "roles": ["FW", "MF", "DF"], "pathway_score": 0.65,
        "pressing_intensity": 0.65, "formation_style": "3-5-2",
        "physical_demand": 0.80, "technical_demand": 0.88,
        "positional_need": {"FW": 0.75, "MF": 0.80, "DF": 0.85, "GK": 0.3},
    },
    "real madrid": {
        "typical_buy_age": (18, 26), "typical_spend_eur": 60_000_000,
        "prestige": 1.00, "roles": ["FW", "MF", "DF"], "pathway_score": 0.70,
        "pressing_intensity": 0.60, "formation_style": "4-3-3",
        "physical_demand": 0.78, "technical_demand": 0.98,
        "positional_need": {"FW": 0.70, "MF": 0.75, "DF": 0.65, "GK": 0.3},
    },
    "barcelona": {
        "typical_buy_age": (16, 24), "typical_spend_eur": 45_000_000,
        "prestige": 0.98, "roles": ["FW", "MF", "DF"], "pathway_score": 0.72,
        "pressing_intensity": 0.78, "formation_style": "4-3-3",
        "physical_demand": 0.72, "technical_demand": 0.98,
        "positional_need": {"FW": 0.80, "MF": 0.85, "DF": 0.70, "GK": 0.3},
    },
    "atletico madrid": {
        "typical_buy_age": (20, 27), "typical_spend_eur": 30_000_000,
        "prestige": 0.90, "roles": ["FW", "MF", "DF"], "pathway_score": 0.68,
        "pressing_intensity": 0.82, "formation_style": "4-4-2",
        "physical_demand": 0.92, "technical_demand": 0.80,
        "positional_need": {"FW": 0.80, "MF": 0.75, "DF": 0.70, "GK": 0.3},
    },
    "porto": {
        "typical_buy_age": (18, 25), "typical_spend_eur": 12_000_000,
        "prestige": 0.78, "roles": ["FW", "MF", "DF"], "pathway_score": 0.75,
        "pressing_intensity": 0.75, "formation_style": "4-4-2",
        "physical_demand": 0.78, "technical_demand": 0.80,
        "positional_need": {"FW": 0.80, "MF": 0.82, "DF": 0.75, "GK": 0.4},
    },
    "nottingham forest": {
        "typical_buy_age": (20, 27), "typical_spend_eur": 20_000_000,
        "prestige": 0.68, "roles": ["FW", "MF", "DF"], "pathway_score": 0.72,
        "pressing_intensity": 0.70, "formation_style": "4-2-3-1",
        "physical_demand": 0.78, "technical_demand": 0.75,
        "positional_need": {"FW": 0.75, "MF": 0.80, "DF": 0.78, "GK": 0.5},
    },
    "villarreal": {
        "typical_buy_age": (19, 26), "typical_spend_eur": 15_000_000,
        "prestige": 0.78, "roles": ["FW", "MF", "DF"], "pathway_score": 0.72,
        "pressing_intensity": 0.72, "formation_style": "4-3-3",
        "physical_demand": 0.75, "technical_demand": 0.85,
        "positional_need": {"FW": 0.78, "MF": 0.82, "DF": 0.72, "GK": 0.4},
    },
    "eindhoven": {
        "typical_buy_age": (17, 23), "typical_spend_eur": 8_000_000,
        "prestige": 0.75, "roles": ["FW", "MF", "DF"], "pathway_score": 0.75,
        "pressing_intensity": 0.78, "formation_style": "4-3-3",
        "physical_demand": 0.74, "technical_demand": 0.88,
        "positional_need": {"FW": 0.80, "MF": 0.85, "DF": 0.72, "GK": 0.4},
    },
}

# League prestige ladder (for step-up scoring)
_LEAGUE_PRESTIGE: dict[str, float] = {
    "liga pro": 0.25,
    "primeira liga": 0.70,
    "eredivisie": 0.72,
    "austrian bundesliga": 0.60,
    "pro league": 0.65,
    "brasileirao": 0.55,
    "primera division": 0.50,
    "bundesliga": 0.88,
    "premier league": 1.00,
    "la liga": 0.95,
    "serie a": 0.90,
    "ligue 1": 0.82,
    "default": 0.40,
}

_WEIGHTS = {
    "role": 0.25,
    "age": 0.20,
    "league": 0.18,
    "value": 0.12,
    "tactical": 0.12,
    "pathway": 0.08,
    "demand": 0.05,
}


def _current_league_prestige(competition: str | None) -> float:
    if not competition:
        return _LEAGUE_PRESTIGE["default"]
    key = competition.strip().lower()
    for k, v in _LEAGUE_PRESTIGE.items():
        if k in key:
            return v
    return _LEAGUE_PRESTIGE["default"]


def _age_profile_match(age: float | None, club: dict[str, Any]) -> float:
    """How well does the player's age fit the club's typical buy window?"""
    if age is None:
        return 0.5
    lo, hi = club.get("typical_buy_age", (18, 26))
    if lo <= age <= hi:
        return 1.0
    # Gaussian decay outside window
    mid = (lo + hi) / 2.0
    sigma = (hi - lo) / 2.0 + 1.5
    return round(math.exp(-((age - mid) ** 2) / (2 * sigma ** 2)), 4)


def _league_step_up(current_prestige: float, club_prestige: float) -> float:
    """
    Is this club a logical step up? Best if club is 0.10-0.40 higher prestige.
    Exact same level = 0.5, too big a jump = harder to get playing time.
    """
    delta = club_prestige - current_prestige
    if delta < -0.1:
        return round(max(0.1, 0.5 + delta), 4)  # step down
    if delta <= 0.40:
        return round(min(1.0, 0.5 + delta * 1.5), 4)  # sweet spot, capped at 1.0
    return round(max(0.3, 0.5 - (delta - 0.40)), 4)  # too big a jump


def _value_accessibility(
    computed_value: float | None,
    market_value: float | None,
    club: dict[str, Any],
) -> float:
    """Can the club likely afford this player?"""
    player_value = computed_value or market_value or 3_000_000
    club_budget = club.get("typical_spend_eur", 10_000_000)
    ratio = player_value / max(club_budget, 1)
    if ratio <= 1.0:
        return round(1.0 - ratio * 0.3, 4)  # affordable
    if ratio <= 2.0:
        return round(0.7 - (ratio - 1.0) * 0.4, 4)  # stretch
    return max(0.1, round(0.3 - (ratio - 2.0) * 0.1, 4))  # expensive


def _position_role_match(position: str | None, club: dict[str, Any]) -> float:
    """Does this player's position align with the club's typical roles?"""
    if not position:
        return 0.5
    pos_upper = position.upper()
    club_roles = [r.upper() for r in club.get("roles", [])]
    # Broad match
    broad_map = {
        "FW": ["ST", "CF", "LW", "RW", "SS", "FORWARD", "STRIKER", "WINGER"],
        "MF": ["CM", "AM", "DM", "LM", "RM", "MID", "MIDFIELDER"],
        "DF": ["CB", "LB", "RB", "LWB", "RWB", "DEFENDER"],
        "GK": ["GK", "GOALKEEPER"],
    }
    for broad, variants in broad_map.items():
        if pos_upper in variants or broad in pos_upper:
            return 1.0 if broad in club_roles else 0.5
    return 0.5


def _tactical_fit_score(player: dict[str, Any], club: dict[str, Any]) -> float:
    """
    How well does the player's physical/technical profile match the club's demands?
    Uses player stats as proxy: pressing-heavy clubs need high work-rate (minutes+runs proxy).
    """
    position = (player.get("position") or player.get("player_position") or "").upper()
    club_pressing = float(club.get("pressing_intensity", 0.70))
    club_physical = float(club.get("physical_demand", 0.75))
    club_technical = float(club.get("technical_demand", 0.80))

    # Estimate player attributes from available data
    val_score = float(player.get("valuation_score") or 55)
    kpi = float(player.get("age_adjusted_kpi_score") or 8.5)

    # Technical proxy: valuation score (encompasses passing, xG, xA)
    technical_proxy = min(1.0, val_score / 80.0)
    # Physical proxy: derived from KPI + position (defenders/midfielders = more physical)
    physical_proxy = min(1.0, kpi / 12.0)
    if "DF" in position or "MF" in position:
        physical_proxy = min(1.0, physical_proxy + 0.05)

    # Match scores: how well player attributes match club requirements
    technical_match = 1.0 - abs(technical_proxy - club_technical) * 0.8
    physical_match = 1.0 - abs(physical_proxy - club_physical) * 0.6
    pressing_suitability = 1.0 - abs(physical_proxy - club_pressing) * 0.5

    return round((technical_match * 0.45 + physical_match * 0.30 + pressing_suitability * 0.25), 4)


def _positional_demand(position: str | None, club: dict[str, Any]) -> float:
    """How urgently does this club need this position?"""
    if not position:
        return 0.5
    pos_upper = position.upper()
    need_map = club.get("positional_need", {})
    broad_map = {
        "FW": ["ST", "CF", "LW", "RW", "SS", "FORWARD", "STRIKER", "WINGER"],
        "MF": ["CM", "AM", "DM", "LM", "RM", "MID", "MIDFIELDER"],
        "DF": ["CB", "LB", "RB", "LWB", "RWB", "DEFENDER"],
        "GK": ["GK", "GOALKEEPER"],
    }
    for broad, variants in broad_map.items():
        if pos_upper in variants or broad in pos_upper:
            return float(need_map.get(broad, 0.5))
    return 0.5


def compute_club_fit(
    player: dict[str, Any],
    target_clubs: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Score player fit against all (or specified) target clubs.
    Returns list sorted by fit_score descending.
    """
    clubs_to_evaluate = target_clubs or list(_CLUB_PROFILES.keys())
    age = player.get("age")
    position = player.get("position") or player.get("player_position")
    competition = player.get("competition")
    computed_value = player.get("computed_value_eur")
    market_value = player.get("market_value_eur")

    current_prestige = _current_league_prestige(competition)
    results: list[dict[str, Any]] = []

    for club_name in clubs_to_evaluate:
        club = _CLUB_PROFILES.get(club_name.lower())
        if not club:
            continue

        role_score = _position_role_match(position, club)
        age_score = _age_profile_match(age, club)
        league_score = _league_step_up(current_prestige, club["prestige"])
        value_score = _value_accessibility(computed_value, market_value, club)
        tactical_score = _tactical_fit_score(player, club)
        pathway_score = club.get("pathway_score", 0.5)
        demand_score = _positional_demand(position, club)

        fit_score = round(
            _WEIGHTS["role"] * role_score
            + _WEIGHTS["age"] * age_score
            + _WEIGHTS["league"] * league_score
            + _WEIGHTS["value"] * value_score
            + _WEIGHTS["tactical"] * tactical_score
            + _WEIGHTS["pathway"] * pathway_score
            + _WEIGHTS["demand"] * demand_score,
            4,
        )

        results.append({
            "club": club_name,
            "fit_score": fit_score,
            "components": {
                "role_similarity": role_score,
                "age_profile_match": age_score,
                "league_step_up": league_score,
                "value_accessibility": value_score,
                "tactical_fit": tactical_score,
                "pathway_score": pathway_score,
                "positional_demand": demand_score,
            },
            "club_profile": {
                "pressing_intensity": club.get("pressing_intensity"),
                "formation_style": club.get("formation_style"),
                "physical_demand": club.get("physical_demand"),
                "technical_demand": club.get("technical_demand"),
            },
        })

    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results[:5]  # top 5


def build_club_fit_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    drift_report: dict[str, Any] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []

    kpi_by_name = {str(r.get("player_name") or "").lower(): r for r in kpi_rows}
    val_by_name = {str(r.get("player_name") or "").lower(): r for r in valuation_rows}
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

        player = {
            "player_name": pr.get("player_name") or kr.get("player_name") or name,
            "age": kr.get("age"),
            "position": pr.get("position"),
            "competition": comp_by_name.get(name) or vr.get("competition"),
            "computed_value_eur": vr.get("computed_value_eur"),
            "market_value_eur": vr.get("market_value_eur"),
            "valuation_score": vr.get("valuation_score"),
            "age_adjusted_kpi_score": kr.get("age_adjusted_kpi_score"),
        }

        top5 = compute_club_fit(player)
        output_rows.append({
            "player_name": player["player_name"],
            "age": player["age"],
            "position": player["position"],
            "top_5_club_fits": top5,
            "best_fit_club": top5[0]["club"] if top5 else None,
            "best_fit_score": top5[0]["fit_score"] if top5 else 0.0,
        })

    output_rows.sort(key=lambda r: r["best_fit_score"], reverse=True)
    path = write_json(
        Path(settings.gold_data_dir) / "club_fit.json", output_rows
    )
    return {"path": path, "rows": output_rows}
