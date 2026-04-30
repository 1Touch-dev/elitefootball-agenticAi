"""
Data validation layer: schema validation, range checks, anomaly detection,
and missing-field rejection. Applied before Silver ingestion.
"""
from __future__ import annotations

import logging
import re
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

# ── Schema definitions ────────────────────────────────────────────────────────

PLAYER_PROFILE_SCHEMA: dict[str, type] = {
    "player_name": str,
    "position": (str, type(None)),
    "date_of_birth": (str, type(None)),
    "nationality": (str, type(None)),
    "current_club": (str, type(None)),
}

MATCH_STAT_SCHEMA: dict[str, type] = {
    "player_name": str,
    "goals": (int, type(None)),
    "assists": (int, type(None)),
    "minutes": (int, type(None)),
    "shots": (int, type(None)),
    "yellow_cards": (int, type(None)),
    "red_cards": (int, type(None)),
}

# ── Range bounds ──────────────────────────────────────────────────────────────

RANGE_BOUNDS: dict[str, tuple[float, float]] = {
    "goals": (0, 10),
    "assists": (0, 10),
    "minutes": (0, 120),
    "shots": (0, 20),
    "yellow_cards": (0, 2),
    "red_cards": (0, 1),
    "passes_completed": (0, 200),
    "xg": (0.0, 5.0),
    "xa": (0.0, 5.0),
    "progressive_carries": (0, 50),
    "progressive_passes": (0, 100),
}

# ── Anomaly thresholds (flag but don't reject) ────────────────────────────────

ANOMALY_THRESHOLDS: dict[str, float] = {
    "goals": 5,         # >5 goals per match is very unusual
    "assists": 4,       # >4 assists per match is unusual
    "shots": 15,        # >15 shots is unusual
    "minutes": 95,      # >95 minutes is unusual (extra time allowed to 120)
    "xg": 3.0,
}

# ── Required fields ───────────────────────────────────────────────────────────

REQUIRED_PROFILE_FIELDS = {"player_name"}
REQUIRED_STAT_FIELDS = {"player_name"}


def _safe_num(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _is_valid_type(value: Any, expected: type | tuple) -> bool:
    if isinstance(expected, tuple):
        return isinstance(value, expected)
    return isinstance(value, expected)


# ── Core validators ───────────────────────────────────────────────────────────

def validate_player_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate a player profile dict. Returns result with valid/invalid and issues."""
    issues: list[str] = []
    anomalies: list[str] = []
    confidence = 1.0

    # Required fields
    for field in REQUIRED_PROFILE_FIELDS:
        val = profile.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            issues.append(f"missing_required:{field}")
            confidence -= 0.5

    # Name sanity
    name = str(profile.get("player_name") or "")
    if name and len(name) < 2:
        issues.append("player_name_too_short")
        confidence -= 0.2
    if name and re.search(r"\d{4,}", name):
        anomalies.append("player_name_contains_year")

    # Date of birth format
    dob = profile.get("date_of_birth")
    if dob and not re.match(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\w+ \d+, \d{4}", str(dob)):
        anomalies.append(f"dob_format_unexpected:{dob!r}")

    valid = len(issues) == 0
    confidence = max(0.0, min(1.0, confidence))
    return {
        "valid": valid,
        "confidence": round(confidence, 2),
        "issues": issues,
        "anomalies": anomalies,
        "entity": "player_profile",
        "player_name": profile.get("player_name"),
    }


def validate_match_stat(stat: dict[str, Any]) -> dict[str, Any]:
    """Validate a single player_match_stats row."""
    issues: list[str] = []
    anomalies: list[str] = []
    confidence = 1.0

    # Required fields
    for field in REQUIRED_STAT_FIELDS:
        val = stat.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            issues.append(f"missing_required:{field}")
            confidence -= 0.5

    # Range checks
    for field_name, (lo, hi) in RANGE_BOUNDS.items():
        raw = stat.get(field_name)
        val = _safe_num(raw)
        if val is None:
            continue
        if val < lo:
            issues.append(f"below_min:{field_name}={val}<{lo}")
            confidence -= 0.2
        elif val > hi:
            issues.append(f"above_max:{field_name}={val}>{hi}")
            confidence -= 0.15

    # Anomaly detection
    for field_name, threshold in ANOMALY_THRESHOLDS.items():
        val = _safe_num(stat.get(field_name))
        if val is not None and val > threshold:
            anomalies.append(f"high_value:{field_name}={val}>threshold:{threshold}")
            confidence -= 0.05

    # Cross-field: can't score without minutes
    goals = _safe_num(stat.get("goals"))
    minutes = _safe_num(stat.get("minutes"))
    if goals and goals > 0 and (minutes is None or minutes <= 0):
        anomalies.append("goals_without_minutes")
        confidence -= 0.1

    # Cross-field: minutes must be positive for a stat row to be useful
    if minutes is not None and minutes <= 0:
        issues.append("zero_minutes_row")
        confidence -= 0.3

    valid = len(issues) == 0
    confidence = max(0.0, min(1.0, confidence))
    return {
        "valid": valid,
        "confidence": round(confidence, 2),
        "issues": issues,
        "anomalies": anomalies,
        "entity": "match_stat",
        "player_name": stat.get("player_name"),
        "match_date": stat.get("match_date"),
    }


def validate_silver_tables(tables: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """
    Validate all Silver tables before pipeline processing.
    Returns summary with per-table results and overall pass/fail.
    """
    summary: dict[str, Any] = {"tables": {}, "overall_valid": True, "total_invalid": 0}

    for table_name, rows in tables.items():
        if not rows:
            summary["tables"][table_name] = {"rows": 0, "valid": 0, "invalid": 0, "anomalies": 0}
            continue

        valid_count = invalid_count = anomaly_count = 0
        invalid_rows: list[dict[str, Any]] = []

        for row in rows:
            if table_name == "players":
                result = validate_player_profile(row)
            elif table_name == "player_match_stats":
                result = validate_match_stat(row)
            else:
                continue  # no validation for matches/transfers/per90

            if result["valid"]:
                valid_count += 1
            else:
                invalid_count += 1
                invalid_rows.append(result)
                log_event(logger, logging.WARNING, "validation.row_invalid",
                          table=table_name,
                          player=result.get("player_name"),
                          issues=result["issues"])

            if result.get("anomalies"):
                anomaly_count += 1
                log_event(logger, logging.INFO, "validation.anomaly_detected",
                          table=table_name,
                          player=result.get("player_name"),
                          anomalies=result["anomalies"])

        summary["tables"][table_name] = {
            "rows": len(rows),
            "valid": valid_count,
            "invalid": invalid_count,
            "anomalies": anomaly_count,
            "invalid_details": invalid_rows[:10],  # cap for log readability
        }
        summary["total_invalid"] += invalid_count

    summary["overall_valid"] = summary["total_invalid"] == 0
    log_event(logger, logging.INFO, "validation.complete",
              tables=list(summary["tables"].keys()),
              total_invalid=summary["total_invalid"],
              overall_valid=summary["overall_valid"])
    return summary


def filter_valid_rows(
    rows: list[dict[str, Any]],
    entity_type: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Split rows into valid and invalid lists.
    Returns (valid_rows, invalid_rows).
    """
    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []

    for row in rows:
        if entity_type == "player_profile":
            result = validate_player_profile(row)
        elif entity_type == "match_stat":
            result = validate_match_stat(row)
        else:
            valid.append(row)
            continue

        if result["valid"]:
            valid.append(row)
        else:
            invalid.append(row)

    return valid, invalid


def compute_data_quality_score(tables: dict[str, list[dict[str, Any]]]) -> float:
    """
    Overall data quality score 0–1 based on validity ratio across core tables.
    """
    total = valid = 0
    for table_name, rows in tables.items():
        if table_name not in ("players", "player_match_stats"):
            continue
        for row in rows:
            total += 1
            if table_name == "players":
                r = validate_player_profile(row)
            else:
                r = validate_match_stat(row)
            if r["valid"]:
                valid += 1
    if total == 0:
        return 1.0
    return round(valid / total, 3)
