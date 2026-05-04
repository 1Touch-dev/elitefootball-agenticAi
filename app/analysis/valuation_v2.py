"""
True weighted valuation model v2.
Formula: clamp(perf×0.35 + age×0.20 + minutes×0.15 + league×0.15 + club×0.10 - risk×0.05)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "valuation_v2_weighted"


@dataclass
class ValuationWeights:
    performance: float = 0.35
    age_curve: float = 0.20
    minutes_probability: float = 0.15
    league_adjustment: float = 0.15
    club_development: float = 0.10
    risk_discount: float = 0.05

    def validate(self) -> None:
        total = (
            self.performance
            + self.age_curve
            + self.minutes_probability
            + self.league_adjustment
            + self.club_development
        )
        assert abs(total - 1.0) < 1e-6, f"Weights (excl risk) must sum to 1.0, got {total}"


DEFAULT_WEIGHTS = ValuationWeights()


# ── Age curve ─────────────────────────────────────────────────────────────────

def age_curve_score(age: float | None) -> float:
    """Peak at 24–26 (score=100), Gaussian decay. Returns 0–100."""
    if age is None:
        return 50.0
    peak = 25.0
    sigma = 5.0
    raw = 100.0 * math.exp(-((age - peak) ** 2) / (2 * sigma ** 2))
    return round(max(0.0, min(100.0, raw)), 2)


# ── Performance component ──────────────────────────────────────────────────────

def performance_component(
    base_kpi: float | None,
    xg_per_90: float | None,
    xa_per_90: float | None,
    progression_score: float | None,
    gc_per_90: float | None,
) -> float:
    """Weighted performance score 0–100."""
    kpi = float(base_kpi or 0.0)
    xg = min(float(xg_per_90 or 0.0) * 25.0, 25.0)
    xa = min(float(xa_per_90 or 0.0) * 20.0, 20.0)
    prog = min(float(progression_score or 0.0) * 15.0, 15.0)
    gc = min(float(gc_per_90 or 0.0) * 10.0, 10.0)
    raw = kpi * 0.40 + xg + xa + prog + gc
    return round(max(0.0, min(100.0, raw)), 2)


# ── Minutes probability ────────────────────────────────────────────────────────

def minutes_probability_score(minutes: float | None, matches: int | None) -> float:
    """0–100 based on availability ratio."""
    if not minutes or not matches:
        return 40.0
    availability = float(minutes) / (float(matches) * 90.0)
    return round(max(0.0, min(100.0, availability * 100.0)), 2)


# ── Risk discount ──────────────────────────────────────────────────────────────

def risk_discount_component(risk_score: float | None) -> float:
    """0–25 penalty from risk_score (0–100)."""
    if risk_score is None:
        return 5.0
    return round(max(0.0, min(25.0, float(risk_score) * 0.25)), 2)


# ── Final score ────────────────────────────────────────────────────────────────

def compute_valuation_score(
    perf: float,
    age: float,
    minutes_prob: float,
    league_adj: float,
    club_dev: float,
    risk_disc: float,
    weights: ValuationWeights = DEFAULT_WEIGHTS,
) -> float:
    raw = (
        perf * weights.performance
        + age * weights.age_curve
        + minutes_prob * weights.minutes_probability
        + league_adj * weights.league_adjustment
        + club_dev * weights.club_development
        - risk_disc * weights.risk_discount
    )
    return round(max(0.0, min(100.0, raw)), 2)


def potential_multiplier(age: float | None) -> float:
    """Returns a multiplier >1 for young players to represent upside potential."""
    a = age or 25.0
    if a <= 19:
        return 1.35
    if a <= 21:
        return 1.20
    if a <= 23:
        return 1.10
    if a <= 25:
        return 1.05
    return 1.0


def potential_score(current_score: float, age: float | None) -> float:
    """Ceiling value accounting for youth upside: current × potential_multiplier."""
    return round(min(100.0, current_score * potential_multiplier(age)), 2)


def parse_market_value(raw: str | None) -> float | None:
    """Parse '€1.5m', '€800k', '€30m' style strings into float euros."""
    if not raw:
        return None
    cleaned = str(raw).strip().lower().replace(",", "").replace("€", "").replace("£", "").replace("$", "")
    try:
        if "bn" in cleaned:
            return float(cleaned.replace("bn", "").strip()) * 1_000_000_000
        if "m" in cleaned:
            return float(cleaned.replace("m", "").strip()) * 1_000_000
        if "k" in cleaned:
            return float(cleaned.replace("k", "").strip()) * 1_000
        return float(cleaned.strip())
    except (ValueError, AttributeError):
        return None


def valuation_tier_v2(score: float) -> str:
    if score >= 80:
        return "elite"
    if score >= 65:
        return "high"
    if score >= 50:
        return "mid"
    if score >= 35:
        return "developing"
    return "low"


def future_value_projection(
    current_score: float,
    age: float | None,
    trajectory: str | None,
) -> dict[str, Any]:
    """Simple projection: +2yr, +5yr based on age curve and trajectory."""
    age_now = age or 25.0
    trajectory_mult = {"ascending": 1.08, "stable": 1.0, "declining": 0.90}.get(trajectory or "stable", 1.0)
    score_2yr = max(0.0, min(100.0, current_score * (age_curve_score(age_now + 2) / max(age_curve_score(age_now), 1.0)) * trajectory_mult))
    score_5yr = max(0.0, min(100.0, current_score * (age_curve_score(age_now + 5) / max(age_curve_score(age_now), 1.0)) * (trajectory_mult ** 2)))
    return {
        "current": round(current_score, 2),
        "in_2yr": round(score_2yr, 2),
        "in_5yr": round(score_5yr, 2),
        "peak_window": f"{int(max(18, 25 - abs(25 - age_now)))}–{int(min(35, 25 + abs(25 - age_now) + 3))}",
    }


# ── Builder (Gold output) ─────────────────────────────────────────────────────

def _normalize_key(value: str | None) -> str:
    return str(value or "").strip().lower()


def build_valuation_v2_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    advanced_metric_rows: list[dict[str, Any]] | None = None,
    risk_rows: list[dict[str, Any]] | None = None,
    pathway_rows: list[dict[str, Any]] | None = None,
    league_rows: list[dict[str, Any]] | None = None,
    club_dev_rows: list[dict[str, Any]] | None = None,
    weights: ValuationWeights | None = None,
    confidence_index: dict[str, Any] | None = None,
) -> dict[str, object]:
    from app.analysis.league_adjustment import league_coefficient
    from app.analysis.club_benchmark import club_development_score

    w = weights or DEFAULT_WEIGHTS
    advanced_metric_rows = advanced_metric_rows or []
    risk_rows = risk_rows or []
    pathway_rows = pathway_rows or []
    confidence_index = confidence_index or {}

    players_by_name = {_normalize_key(r.get("player_name")): r for r in silver_tables.get("players", [])}
    features_by_name = {_normalize_key(r.get("player_name")): r for r in gold_tables.get("player_features", [])}
    kpi_by_name = {_normalize_key(r.get("player_name")): r for r in kpi_rows}
    adv_by_name = {_normalize_key(r.get("player_name")): r for r in advanced_metric_rows}
    risk_by_name = {_normalize_key(r.get("player_name")): r for r in risk_rows}
    pathway_by_name = {_normalize_key(r.get("player_name")): r for r in pathway_rows}

    stat_rows_by_name: dict[str, list] = {}
    for row in silver_tables.get("player_match_stats", []):
        k = _normalize_key(row.get("player_name"))
        stat_rows_by_name.setdefault(k, []).append(row)

    all_names = sorted(
        set(players_by_name)
        | set(features_by_name)
        | set(kpi_by_name)
        | set(adv_by_name)
        | set(risk_by_name)
        | set(stat_rows_by_name)
    )

    if not all_names:
        path = write_json(Path(settings.gold_data_dir) / "player_valuation.json", [])
        return {"path": path, "rows": []}

    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        pr = players_by_name.get(name, {})
        fr = features_by_name.get(name, {})
        kr = kpi_by_name.get(name, {})
        ar = adv_by_name.get(name, {})
        rr = risk_by_name.get(name, {})
        patr = pathway_by_name.get(name, {})
        stats = stat_rows_by_name.get(name, [])

        from app.analysis.kpi_formulas import age_in_years
        age = kr.get("age") or age_in_years(pr.get("date_of_birth"))
        minutes = fr.get("minutes") or kr.get("minutes_played")
        matches = fr.get("matches") or kr.get("matches")

        from collections import Counter
        competition = None
        comp_vals = [str(s.get("competition") or "").strip() for s in stats if s.get("competition")]
        if comp_vals:
            competition = Counter(comp_vals).most_common(1)[0][0]

        club_name = pr.get("current_club") or fr.get("current_club")
        if not club_name:
            for s in stats:
                if s.get("club_name"):
                    club_name = s.get("club_name")
                    break

        # Components
        perf = performance_component(
            base_kpi=kr.get("base_kpi_score"),
            xg_per_90=ar.get("xg_per_90"),
            xa_per_90=ar.get("xa_per_90"),
            progression_score=ar.get("progression_score"),
            gc_per_90=fr.get("goal_contribution_per_90"),
        )
        age_c = age_curve_score(age)
        min_c = minutes_probability_score(minutes, int(matches or 0) if matches else None)
        league_c = league_coefficient(competition, club_name) * 6.67  # scale −10..+15 → 0..100
        league_c = max(0.0, min(100.0, league_c))
        club_c = club_development_score(club_name)
        risk_d = risk_discount_component(rr.get("risk_score"))

        final_score = compute_valuation_score(perf, age_c, min_c, league_c, club_c, risk_d, w)
        trajectory = patr.get("trajectory")
        pot_score = potential_score(final_score, age)
        market_val_raw = pr.get("market_value")
        market_val_eur = parse_market_value(market_val_raw)
        # Computed valuation maps to estimated transfer value (€5m per score point above 40)
        computed_val_eur = max(0.0, (final_score - 40.0) * 500_000) if final_score > 40 else 0.0
        conf = confidence_index.get(name, {})
        data_confidence = float(conf.get("data_confidence_score") or 1.0)
        validation_flag = conf.get("validation_flag", "OK")

        # Confidence-weighted valuation score
        confidence_weighted_score = round(final_score * data_confidence, 3)
        confidence_weighted_computed = round(computed_val_eur * data_confidence, 0) if computed_val_eur else 0.0

        value_gap_pct = None
        if market_val_eur and market_val_eur > 0 and computed_val_eur:
            value_gap_pct = round((computed_val_eur - market_val_eur) / market_val_eur * 100, 1)

        is_undervalued = (
            market_val_eur is not None
            and computed_val_eur > 0
            and computed_val_eur > market_val_eur
        )

        display_name = (
            pr.get("player_name")
            or fr.get("player_name")
            or kr.get("player_name")
            or name
        )

        output_rows.append({
            "player_name": display_name,
            "position": pr.get("position"),
            "current_club": club_name,
            "competition": competition,
            "valuation_score": final_score,
            "confidence_weighted_score": confidence_weighted_score,
            "potential_score": pot_score,
            "market_value_raw": market_val_raw,
            "market_value_eur": market_val_eur,
            "computed_value_eur": round(computed_val_eur, 0) if computed_val_eur else None,
            "confidence_weighted_computed_eur": round(confidence_weighted_computed, 0) if confidence_weighted_computed else None,
            "value_gap_pct": value_gap_pct,
            "undervalued": is_undervalued,
            "data_confidence_score": round(data_confidence, 4),
            "validation_flag": validation_flag,
            "valuation_tier": valuation_tier_v2(final_score),
            "future_value": future_value_projection(final_score, age, trajectory),
            "components": {
                "performance_score": perf,
                "age_curve_score": age_c,
                "minutes_probability": min_c,
                "league_adjustment": league_c,
                "club_development": club_c,
                "risk_discount": risk_d,
            },
            "weights_used": {
                "performance": w.performance,
                "age_curve": w.age_curve,
                "minutes_probability": w.minutes_probability,
                "league_adjustment": w.league_adjustment,
                "club_development": w.club_development,
                "risk_discount": w.risk_discount,
            },
            "inputs": {
                "age": age,
                "minutes": minutes,
                "matches": matches,
                "base_kpi_score": kr.get("base_kpi_score"),
                "consistency_score": kr.get("consistency_score"),
                "risk_score": rr.get("risk_score"),
                "xg_per_90": ar.get("xg_per_90"),
                "xa_per_90": ar.get("xa_per_90"),
            },
            "model_version": MODEL_VERSION,
        })

    output_rows.sort(key=lambda r: r["valuation_score"], reverse=True)
    path = write_json(Path(settings.gold_data_dir) / "player_valuation.json", output_rows)
    return {"path": path, "rows": output_rows}
