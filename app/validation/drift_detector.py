"""
Data drift detection for player statistics.

Detects:
  - Sudden goal/assist/minutes spikes between consecutive windows
  - Unrealistic single-match values (already in range-checker but this is trend-based)
  - Performance cliff-drops (injury/suspension signals)

Uses z-score and rolling-window deviation:
  spike_score = abs(x_new - rolling_mean) / (rolling_std + ε)

spike_score > SPIKE_Z_THRESHOLD → flag anomaly and log event.
"""
from __future__ import annotations

import logging
import math
import statistics
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_SPIKE_Z_THRESHOLD = 3.0   # > 3 sigma above rolling mean = spike
_DROP_Z_THRESHOLD = 3.0    # > 3 sigma below rolling mean = cliff drop
_MIN_WINDOW = 4            # minimum matches needed to compute baseline
_METRICS = ["goals", "assists", "minutes", "shots"]


def _rolling_baseline(values: list[float], window: int = 5) -> tuple[float, float]:
    """Mean and std of last `window` values (before the new point)."""
    recent = values[-window:]
    if len(recent) < 2:
        return (sum(recent) / max(len(recent), 1), 0.0)
    return statistics.mean(recent), statistics.stdev(recent)


def detect_match_spikes(
    match_stats: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Detect per-match spikes or drops in goals/assists/minutes/shots.
    Returns a list of anomaly records (empty if none detected).

    Anomaly record: {metric, match_date, value, rolling_mean, rolling_std, z_score, type}
    """
    if len(match_stats) < _MIN_WINDOW + 1:
        return []  # insufficient history

    sorted_stats = sorted(match_stats, key=lambda s: s.get("match_date") or "")
    anomalies: list[dict[str, Any]] = []

    for metric in _METRICS:
        history: list[float] = []
        for match in sorted_stats:
            val = float(match.get(metric) or 0)
            if len(history) >= _MIN_WINDOW:
                mu, sigma = _rolling_baseline(history)
                eps = 0.5
                z = (val - mu) / (sigma + eps)
                match_date = match.get("match_date") or "unknown"

                if z > _SPIKE_Z_THRESHOLD:
                    anomalies.append({
                        "metric": metric,
                        "match_date": match_date,
                        "value": val,
                        "rolling_mean": round(mu, 3),
                        "rolling_std": round(sigma, 3),
                        "z_score": round(z, 3),
                        "type": "spike",
                    })
                    log_event(logger, logging.INFO, "drift.spike_detected",
                              metric=metric, match_date=match_date,
                              value=val, mu=mu, z=z)

                elif z < -_DROP_Z_THRESHOLD and mu > 0.5:
                    anomalies.append({
                        "metric": metric,
                        "match_date": match_date,
                        "value": val,
                        "rolling_mean": round(mu, 3),
                        "rolling_std": round(sigma, 3),
                        "z_score": round(z, 3),
                        "type": "drop",
                    })
                    log_event(logger, logging.INFO, "drift.drop_detected",
                              metric=metric, match_date=match_date,
                              value=val, mu=mu, z=z)

            history.append(val)

    return anomalies


def detect_career_drift(
    match_stats: list[dict[str, Any]],
    window_size: int = 5,
) -> dict[str, Any]:
    """
    Compare last N matches vs prior N matches for each metric.
    Returns drift summary:
      {
        "goals_drift": float,   # positive = improving, negative = declining
        "assists_drift": float,
        "minutes_drift": float,
        "overall_drift_direction": "improving" | "stable" | "declining",
        "drift_magnitude": float,  # 0-1 severity
      }
    """
    sorted_stats = sorted(match_stats, key=lambda s: s.get("match_date") or "")
    n = len(sorted_stats)

    if n < window_size * 2:
        return {
            "goals_drift": 0.0,
            "assists_drift": 0.0,
            "minutes_drift": 0.0,
            "overall_drift_direction": "stable",
            "drift_magnitude": 0.0,
        }

    recent = sorted_stats[-window_size:]
    prior = sorted_stats[-(window_size * 2):-window_size]

    def _avg(rows: list[dict[str, Any]], key: str) -> float:
        vals = [float(r.get(key) or 0) for r in rows]
        return sum(vals) / max(len(vals), 1)

    goals_drift = _avg(recent, "goals") - _avg(prior, "goals")
    assists_drift = _avg(recent, "assists") - _avg(prior, "assists")
    minutes_drift = _avg(recent, "minutes") - _avg(prior, "minutes")

    # Normalise by typical range
    combined_drift = (
        goals_drift / 0.5
        + assists_drift / 0.4
        + minutes_drift / 30.0
    ) / 3.0

    if combined_drift > 0.15:
        direction = "improving"
    elif combined_drift < -0.15:
        direction = "declining"
    else:
        direction = "stable"

    magnitude = round(min(1.0, abs(combined_drift)), 4)

    return {
        "goals_drift": round(goals_drift, 4),
        "assists_drift": round(assists_drift, 4),
        "minutes_drift": round(minutes_drift, 2),
        "overall_drift_direction": direction,
        "drift_magnitude": magnitude,
    }


def build_drift_report(
    silver_tables: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """
    Run drift detection across all players in the Silver dataset.
    Returns per-player anomalies and career drift summaries.
    """
    stats_by_name: dict[str, list[dict[str, Any]]] = {}
    for row in silver_tables.get("player_match_stats", []):
        key = str(row.get("player_name") or "").strip().lower()
        stats_by_name.setdefault(key, []).append(row)

    report: dict[str, Any] = {"players": {}, "total_anomalies": 0}

    for name, stats in stats_by_name.items():
        match_anomalies = detect_match_spikes(stats)
        career_drift = detect_career_drift(stats)

        report["players"][name] = {
            "match_anomalies": match_anomalies,
            "career_drift": career_drift,
            "anomaly_count": len(match_anomalies),
        }
        report["total_anomalies"] += len(match_anomalies)

    log_event(logger, logging.INFO, "drift.report_complete",
              players=len(report["players"]),
              total_anomalies=report["total_anomalies"])
    return report
