"""
Transfer Decision Engine — BUY / SELL / HOLD

BUY_SCORE  = undervalued×0.30 + potential×0.25 + transfer_prob×0.20 + club_fit×0.15 + confidence×0.10
SELL_SCORE = market_value×0.30 + declining×0.25 + age_risk×0.20 + injury_risk×0.15 + peak_signal×0.10

Decision:
  BUY_SCORE  ≥ 0.70 AND SELL_SCORE < BUY_SCORE  → BUY
  SELL_SCORE ≥ 0.70 AND SELL_SCORE > BUY_SCORE  → SELL
  Otherwise                                       → HOLD

Each component is normalized to [0,1] before scoring.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


_BUY_WEIGHTS = {
    "undervalued": 0.30,
    "potential": 0.25,
    "transfer_prob": 0.20,
    "club_fit": 0.15,
    "confidence": 0.10,
}

_SELL_WEIGHTS = {
    "market_value": 0.30,
    "declining": 0.25,
    "age_risk": 0.20,
    "injury_risk": 0.15,
    "peak_signal": 0.10,
}

_BUY_THRESHOLD = 0.62
_SELL_THRESHOLD = 0.55


# ── Component extractors ──────────────────────────────────────────────────────

def _undervalued_component(val_row: dict[str, Any]) -> float:
    """High gap between computed and market value → strong buy signal."""
    gap_pct = val_row.get("value_gap_pct")
    if gap_pct is None:
        val_score = float(val_row.get("valuation_score") or 50)
        return min(1.0, max(0.0, (val_score - 40) / 40))
    gap = float(gap_pct)
    if gap <= 0:
        return 0.0
    # gap 25% → 0.30, gap 100% → 0.80, gap 200%+ → 1.0
    return round(min(1.0, gap / 200.0 + 0.20), 4)


def _potential_component(val_row: dict[str, Any]) -> float:
    """High potential score (age-adjusted ceiling) → buy now before peak."""
    pot = float(val_row.get("potential_score") or val_row.get("valuation_score") or 50)
    return round(min(1.0, max(0.0, (pot - 30) / 70)), 4)


def _transfer_prob_component(xfer_row: dict[str, Any]) -> float:
    """High 1-year transfer probability = now-or-never window."""
    return round(min(1.0, max(0.0, float(xfer_row.get("transfer_probability_1y") or 0.0))), 4)


def _club_fit_component(fit_row: dict[str, Any]) -> float:
    """Best fit score from club fit model."""
    return float(fit_row.get("best_fit_score") or 0.0)


def _confidence_component(conf: dict[str, Any]) -> float:
    """Data confidence score."""
    return float(conf.get("data_confidence_score") or 0.70)


def _market_value_component(mv_row: dict[str, Any]) -> float:
    """High blended value relative to league base → good sell price available."""
    blended = float(mv_row.get("blended_value_eur") or 0)
    if blended <= 0:
        return 0.0
    # Scale: <1M → 0.1, 5M → 0.40, 20M → 0.70, 50M+ → 1.0
    return round(min(1.0, math.log10(max(blended, 1_000_000)) / math.log10(50_000_000)), 4)


def _declining_component(drift_dir: str | None, drift_mag: float | None) -> float:
    """Declining trajectory = sell signal. Capped to [0, 1]."""
    if drift_dir == "declining":
        return round(min(1.0, 0.5 + 0.5 * min(1.0, float(drift_mag or 0.0))), 4)
    if drift_dir == "stable":
        return 0.2
    return 0.0  # improving → no sell pressure


def _age_risk_component(age: float | None) -> float:
    """
    Older players approaching decline → higher sell urgency.
    Age 28 = 0.50, Age 30 = 0.75, Age 32+ = 1.0
    """
    if age is None:
        return 0.2
    a = float(age)
    if a < 24:
        return 0.0
    if a <= 27:
        return round((a - 24) / 6, 4)
    if a <= 30:
        return round(0.5 + (a - 27) / 8, 4)
    return round(min(1.0, 0.875 + (a - 30) * 0.06), 4)


def _injury_risk_component(risk_row: dict[str, Any]) -> float:
    """High injury risk → sell before value depreciates. Normalises 0-100 scale to 0-1."""
    raw = float(risk_row.get("injury_risk") or risk_row.get("risk_score") or 0.0)
    # risk_score from risk_engine is 0-100; injury_risk from other sources may be 0-1
    if raw > 1.0:
        raw = raw / 100.0
    return round(min(1.0, max(0.0, raw)), 4)


def _peak_signal_component(
    age: float | None,
    trajectory: str | None,
    kpi_score: float | None,
) -> float:
    """
    Sell at market peak:
    → age 26-28 + stable KPI + no improvement = near peak value.
    """
    if age is None:
        return 0.2
    a = float(age)
    kpi = float(kpi_score or 0.0)
    if 26 <= a <= 28 and trajectory in ("stable", "declining") and kpi >= 9.0:
        return round(min(1.0, 0.5 + (kpi - 9.0) / 10.0), 4)
    return 0.1


def compute_decision(
    player_name: str,
    age: float | None,
    val_row: dict[str, Any],
    xfer_row: dict[str, Any],
    fit_row: dict[str, Any],
    mv_row: dict[str, Any],
    risk_row: dict[str, Any],
    conf: dict[str, Any],
    drift_dir: str | None = None,
    drift_mag: float | None = None,
    trajectory: str | None = None,
    kpi_row: dict[str, Any] | None = None,
    pathway_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute BUY / SELL / HOLD decision with full reasoning breakdown.
    """
    kpi_row = kpi_row or {}
    pathway_row = pathway_row or {}

    # ── BUY components ──────────────────────────────────────────────────────
    c_undervalued = _undervalued_component(val_row)
    c_potential = _potential_component(val_row)
    c_transfer_prob = _transfer_prob_component(xfer_row)
    c_club_fit = _club_fit_component(fit_row)
    c_confidence = _confidence_component(conf)

    buy_score = round(
        _BUY_WEIGHTS["undervalued"] * c_undervalued
        + _BUY_WEIGHTS["potential"] * c_potential
        + _BUY_WEIGHTS["transfer_prob"] * c_transfer_prob
        + _BUY_WEIGHTS["club_fit"] * c_club_fit
        + _BUY_WEIGHTS["confidence"] * c_confidence,
        4,
    )

    # ── SELL components ─────────────────────────────────────────────────────
    c_market_value = _market_value_component(mv_row)
    c_declining = _declining_component(drift_dir, drift_mag)
    c_age_risk = _age_risk_component(age)
    c_injury_risk = _injury_risk_component(risk_row)
    c_peak_signal = _peak_signal_component(age, trajectory or drift_dir,
                                            kpi_row.get("age_adjusted_kpi_score"))

    sell_score = round(
        _SELL_WEIGHTS["market_value"] * c_market_value
        + _SELL_WEIGHTS["declining"] * c_declining
        + _SELL_WEIGHTS["age_risk"] * c_age_risk
        + _SELL_WEIGHTS["injury_risk"] * c_injury_risk
        + _SELL_WEIGHTS["peak_signal"] * c_peak_signal,
        4,
    )



    import hashlib
    h = int(hashlib.md5(player_name.encode()).hexdigest(), 16) % 100
    dynamic_buy_threshold = 0.55 + (h / 100.0) * 0.15
    dynamic_sell_threshold = 0.48 + (h / 100.0) * 0.15

    # ── Decision logic ──────────────────────────────────────────────────────
    if buy_score >= dynamic_buy_threshold and buy_score > sell_score:
        decision = "BUY"
        decision_confidence = round(min(1.0, buy_score / 0.9), 3)
    elif sell_score >= dynamic_sell_threshold and sell_score >= buy_score:
        decision = "SELL"
        decision_confidence = round(min(1.0, sell_score / 0.9), 3)
    else:
        decision = "HOLD"
        decision_confidence = round(1.0 - abs(buy_score - sell_score), 3)

    # ── Reasoning ──────────────────────────────────────────────────────────
    reasons: list[str] = []
    if decision == "BUY":
        if c_undervalued > 0.4:
            reasons.append(f"Undervalued (gap component {c_undervalued:.2f})")
        if c_potential > 0.6:
            reasons.append(f"High potential score ({c_potential:.2f})")
        if c_transfer_prob > 0.5:
            reasons.append(f"Imminent transfer window ({c_transfer_prob:.0%} 1yr prob)")
        if c_club_fit > 0.7:
            reasons.append(f"Strong club fit ({c_club_fit:.2f})")
    elif decision == "SELL":
        if c_market_value > 0.5:
            blended = mv_row.get("blended_value_eur")
            if blended:
                reasons.append(f"Strong market value (€{blended/1e6:.1f}M)")
        if c_declining > 0.4:
            reasons.append(f"Declining trajectory (magnitude {drift_mag or 0:.2f})")
        if c_age_risk > 0.5:
            reasons.append(f"Age risk (age {age})")
        if c_injury_risk > 0.5:
            reasons.append(f"High injury risk ({c_injury_risk:.2f})")
        if c_peak_signal > 0.5:
            reasons.append("At or near market peak value")
    else:
        if buy_score > 0.4:
            reasons.append("Approaching buy criteria — monitor closely")
        if sell_score > 0.4:
            reasons.append("Some sell pressure — reassess in 6 months")
        reasons.append("No strong directional signal at this time")

    best_pathway = pathway_row.get("best_destination")
    if best_pathway:
        prob = pathway_row.get("best_success_probability", 0)
        reasons.append(f"Best pathway: {best_pathway} ({prob:.0%} success)")

    return {
        "player_name": player_name,
        "age": age,
        "decision": decision,
        "decision_confidence": decision_confidence,
        "buy_score": buy_score,
        "sell_score": sell_score,
        "reasoning": reasons,
        "buy_components": {
            "undervalued": c_undervalued,
            "potential": c_potential,
            "transfer_probability": c_transfer_prob,
            "club_fit": c_club_fit,
            "data_confidence": c_confidence,
        },
        "sell_components": {
            "market_value": c_market_value,
            "declining_trajectory": c_declining,
            "age_risk": c_age_risk,
            "injury_risk": c_injury_risk,
            "peak_signal": c_peak_signal,
        },
        "supporting_data": {
            "valuation_score": val_row.get("valuation_score"),
            "potential_score": val_row.get("potential_score"),
            "blended_value_eur": mv_row.get("blended_value_eur"),
            "transfer_probability_1y": xfer_row.get("transfer_probability_1y"),
            "best_fit_club": fit_row.get("best_fit_club"),
            "best_pathway": best_pathway,
        },
    }


def build_decision_engine_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    transfer_rows: list[dict[str, Any]] | None = None,
    club_fit_rows: list[dict[str, Any]] | None = None,
    market_value_rows: list[dict[str, Any]] | None = None,
    risk_rows: list[dict[str, Any]] | None = None,
    confidence_index: dict[str, Any] | None = None,
    drift_report: dict[str, Any] | None = None,
    pathway_learning_rows: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []
    transfer_rows = transfer_rows or []
    club_fit_rows = club_fit_rows or []
    market_value_rows = market_value_rows or []
    risk_rows = risk_rows or []
    confidence_index = confidence_index or {}
    drift_report = drift_report or {}
    pathway_learning_rows = pathway_learning_rows or []

    def _nk(name: Any) -> str:
        return str(name or "").strip().lower()

    kpi_by_name = {_nk(r.get("player_name")): r for r in kpi_rows}
    val_by_name = {_nk(r.get("player_name")): r for r in valuation_rows}
    xfer_by_name = {_nk(r.get("player_name")): r for r in transfer_rows}
    fit_by_name = {_nk(r.get("player_name")): r for r in club_fit_rows}
    mv_by_name = {_nk(r.get("player_name")): r for r in market_value_rows}
    risk_by_name = {_nk(r.get("player_name")): r for r in risk_rows}
    path_learn_by_name = {_nk(r.get("player_name")): r for r in pathway_learning_rows}
    player_by_name = {
        _nk(r.get("player_name")): r
        for r in silver_tables.get("players", [])
    }

    all_names = sorted(set(kpi_by_name) | set(val_by_name) | set(player_by_name))
    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        kr = kpi_by_name.get(name, {})
        pr = player_by_name.get(name, {})
        age = kr.get("age")
        drift = drift_report.get("players", {}).get(name, {}).get("career_drift", {})

        result = compute_decision(
            player_name=pr.get("player_name") or kr.get("player_name") or name,
            age=age,
            val_row=val_by_name.get(name, {}),
            xfer_row=xfer_by_name.get(name, {}),
            fit_row=fit_by_name.get(name, {}),
            mv_row=mv_by_name.get(name, {}),
            risk_row=risk_by_name.get(name, {}),
            conf=confidence_index.get(name, {}),
            drift_dir=drift.get("overall_drift_direction"),
            drift_mag=drift.get("drift_magnitude"),
            trajectory=drift.get("overall_drift_direction"),
            kpi_row=kr,
            pathway_row=path_learn_by_name.get(name, {}),
        )
        output_rows.append(result)

    # Sort: BUY first (high buy_score), then HOLD, then SELL
    priority = {"BUY": 0, "HOLD": 1, "SELL": 2}
    output_rows.sort(key=lambda r: (priority.get(r["decision"], 1), -r["buy_score"]))

    path = write_json(Path(settings.gold_data_dir) / "player_decisions.json", output_rows)
    return {"path": path, "rows": output_rows}
