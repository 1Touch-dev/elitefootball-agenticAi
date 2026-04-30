"""
Alert system — generates player alerts for three categories:

  UNDERVALUED   — model value significantly exceeds market price
  BREAKOUT      — young improving player entering peak performance window
  DECLINE       — older player showing consistent performance drop

Each alert has:
  - alert_type
  - severity: "critical" | "high" | "medium" | "low"
  - player_name
  - trigger_reason (human-readable)
  - supporting_metrics
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json
from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_UNDERVALUED_THRESHOLD = 1.25   # model value > market × 1.25
_BREAKOUT_MAX_AGE = 23
_BREAKOUT_MIN_KPI = 8.0
_DECLINE_MIN_AGE = 26
_DECLINE_MIN_DRIFT_MAGNITUDE = 0.25


def _severity(value: float, thresholds: tuple[float, float, float]) -> str:
    """thresholds = (critical_floor, high_floor, medium_floor)"""
    if value >= thresholds[0]:
        return "critical"
    if value >= thresholds[1]:
        return "high"
    if value >= thresholds[2]:
        return "medium"
    return "low"


def generate_undervalued_alerts(
    valuation_rows: list[dict[str, Any]],
    confidence_index: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Alert when model-predicted value significantly exceeds market price.
    Enhanced with confidence weighting.
    """
    confidence_index = confidence_index or {}
    alerts: list[dict[str, Any]] = []

    for row in valuation_rows:
        name = str(row.get("player_name") or "")
        computed = float(row.get("computed_value_eur") or 0)
        market = float(row.get("market_value_eur") or 0)
        val_score = float(row.get("valuation_score") or 0)
        data_conf = confidence_index.get(name.lower(), {}).get("data_confidence_score", 1.0)

        if computed <= 0:
            continue

        # Weight by data confidence
        effective_computed = computed * data_conf

        if market > 0:
            gap_ratio = effective_computed / market
            gap_pct = round((gap_ratio - 1.0) * 100, 1)
            if gap_ratio < _UNDERVALUED_THRESHOLD:
                continue

            severity = _severity(gap_pct, (100, 60, 30))
        else:
            # No market data — alert if high model score
            if val_score < 55:
                continue
            gap_pct = None
            severity = "medium"

        alert = {
            "alert_type": "UNDERVALUED",
            "severity": severity,
            "player_name": row.get("player_name"),
            "trigger_reason": (
                f"Model value €{computed:,.0f} vs market €{market:,.0f} "
                f"({gap_pct:+.0f}% gap)" if gap_pct is not None else
                f"No market data but model score {val_score:.1f}"
            ),
            "supporting_metrics": {
                "computed_value_eur": computed,
                "market_value_eur": market if market > 0 else None,
                "valuation_score": val_score,
                "value_gap_pct": gap_pct,
                "data_confidence": data_conf,
            },
        }
        alerts.append(alert)
        log_event(logger, logging.INFO, "alert.undervalued",
                  player=name, gap_pct=gap_pct, severity=severity)

    return alerts


def generate_breakout_alerts(
    kpi_rows: list[dict[str, Any]],
    drift_report: dict[str, Any] | None = None,
    transfer_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """
    Alert for young players showing strong improving trajectory.
    Trigger: age ≤ 23, KPI ≥ threshold, drift = improving
    """
    drift_report = drift_report or {}
    transfer_rows = transfer_rows or []
    xfer_by_name = {str(r.get("player_name") or "").lower(): r for r in transfer_rows}

    alerts: list[dict[str, Any]] = []

    for row in kpi_rows:
        name = str(row.get("player_name") or "")
        age = float(row.get("age") or 99)
        kpi = float(row.get("age_adjusted_kpi_score") or 0)

        if age > _BREAKOUT_MAX_AGE or kpi < _BREAKOUT_MIN_KPI:
            continue

        drift = drift_report.get("players", {}).get(name.lower(), {}).get("career_drift", {})
        direction = drift.get("overall_drift_direction", "stable")
        magnitude = float(drift.get("drift_magnitude", 0.0))
        tp = float((xfer_by_name.get(name.lower()) or {}).get("transfer_probability_1y") or 0)

        if direction != "improving":
            continue

        severity = _severity(magnitude, (0.8, 0.5, 0.25))

        alert = {
            "alert_type": "BREAKOUT",
            "severity": severity,
            "player_name": row.get("player_name"),
            "trigger_reason": (
                f"Age {age:.0f}, KPI {kpi:.2f}, improving trajectory "
                f"(magnitude {magnitude:.2f})"
            ),
            "supporting_metrics": {
                "age": age,
                "kpi_score": kpi,
                "drift_direction": direction,
                "drift_magnitude": magnitude,
                "transfer_probability_1y": tp,
            },
        }
        alerts.append(alert)
        log_event(logger, logging.INFO, "alert.breakout",
                  player=name, age=age, kpi=kpi, magnitude=magnitude)

    return alerts


def generate_decline_alerts(
    kpi_rows: list[dict[str, Any]],
    drift_report: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Alert for players showing consistent performance drop.
    Trigger: age ≥ 26, drift = declining, magnitude ≥ threshold
    """
    drift_report = drift_report or {}
    alerts: list[dict[str, Any]] = []

    for row in kpi_rows:
        name = str(row.get("player_name") or "")
        age = float(row.get("age") or 0)
        kpi = float(row.get("age_adjusted_kpi_score") or 0)

        if age < _DECLINE_MIN_AGE:
            continue

        drift = drift_report.get("players", {}).get(name.lower(), {}).get("career_drift", {})
        direction = drift.get("overall_drift_direction", "stable")
        magnitude = float(drift.get("drift_magnitude", 0.0))

        if direction != "declining" or magnitude < _DECLINE_MIN_DRIFT_MAGNITUDE:
            continue

        severity = _severity(magnitude, (0.8, 0.55, 0.25))

        alert = {
            "alert_type": "DECLINE",
            "severity": severity,
            "player_name": row.get("player_name"),
            "trigger_reason": (
                f"Age {age:.0f}, declining trajectory "
                f"(magnitude {magnitude:.2f}, KPI {kpi:.2f})"
            ),
            "supporting_metrics": {
                "age": age,
                "kpi_score": kpi,
                "drift_direction": direction,
                "drift_magnitude": magnitude,
            },
        }
        alerts.append(alert)
        log_event(logger, logging.INFO, "alert.decline",
                  player=name, age=age, kpi=kpi, magnitude=magnitude)

    return alerts


def build_alert_output(
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    drift_report: dict[str, Any] | None = None,
    transfer_rows: list[dict[str, Any]] | None = None,
    confidence_index: dict[str, Any] | None = None,
) -> dict[str, object]:
    valuation_rows = valuation_rows or []
    drift_report = drift_report or {}
    transfer_rows = transfer_rows or []
    confidence_index = confidence_index or {}

    undervalued = generate_undervalued_alerts(valuation_rows, confidence_index)
    breakout = generate_breakout_alerts(kpi_rows, drift_report, transfer_rows)
    decline = generate_decline_alerts(kpi_rows, drift_report)

    all_alerts = undervalued + breakout + decline
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_alerts.sort(key=lambda a: (severity_order.get(a["severity"], 9), a["player_name"]))

    result = {
        "alerts": all_alerts,
        "summary": {
            "total": len(all_alerts),
            "undervalued": len(undervalued),
            "breakout": len(breakout),
            "decline": len(decline),
            "critical": sum(1 for a in all_alerts if a["severity"] == "critical"),
            "high": sum(1 for a in all_alerts if a["severity"] == "high"),
        },
    }

    path = write_json(Path(settings.gold_data_dir) / "alerts.json", result)
    log_event(logger, logging.INFO, "alerts.generated",
              total=result["summary"]["total"],
              undervalued=len(undervalued),
              breakout=len(breakout),
              decline=len(decline))
    return {"path": path, "rows": all_alerts, "summary": result["summary"]}
