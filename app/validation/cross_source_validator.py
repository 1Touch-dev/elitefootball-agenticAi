"""
Cross-source validation engine.

For each player, compares Transfermarkt vs FBref stats (goals, assists, minutes, appearances).
Produces:
  consistency_score ∈ [0,1]  — per-metric agreement across sources
  data_confidence_score ∈ [0,1] — overall confidence to weight Gold-layer outputs

Formula (per metric):
  agreement_i = 1 - abs(a - b) / max(a, b, 1)

Final:
  consistency_score = mean(agreement_i for all available metric pairs)
  data_confidence_score = (
      0.45 * cross_source_consistency  # 0 if single-source
    + 0.35 * internal_consistency      # CV-based match-to-match stability
    + 0.20 * coverage_score            # how many expected fields are populated
  )

Single-source: cross_source_consistency defaults to 0.65 (assumed, not verified)
"""
from __future__ import annotations

import logging
import math
import statistics
from collections import defaultdict
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_CROSS_SOURCE_METRICS = ["goals", "assists", "minutes", "appearances"]
_COVERAGE_FIELDS = ["goals", "assists", "minutes", "shots", "passes_completed", "position", "date_of_birth"]

# Weight of each metric in cross-source consistency
_METRIC_WEIGHTS: dict[str, float] = {
    "goals": 0.30,
    "assists": 0.25,
    "minutes": 0.30,
    "appearances": 0.15,
}


def _normalize_key(name: str | None) -> str:
    return str(name or "").strip().lower()


def _agreement(a: float, b: float) -> float:
    """Per-metric agreement: 1 - |a-b| / max(a, b, 1). Returns [0,1]."""
    denom = max(abs(a), abs(b), 1.0)
    return max(0.0, 1.0 - abs(a - b) / denom)


def _internal_consistency(match_stats: list[dict[str, Any]]) -> float:
    """
    Coefficient-of-variation-based consistency over match-level data.
    Low CV → high consistency. Returns [0,1].
    """
    if len(match_stats) < 2:
        return 0.70  # insufficient data — moderate confidence

    gc_values = [
        float((r.get("goals") or 0) + (r.get("assists") or 0))
        for r in match_stats
        if (r.get("minutes") or 0) > 10
    ]
    if len(gc_values) < 2:
        return 0.70

    mu = statistics.mean(gc_values)
    if mu <= 0:
        return 0.80  # consistent zeros
    sigma = statistics.stdev(gc_values)
    cv = sigma / mu
    # CV=0 → 1.0, CV=1 → 0.5, CV=2+ → 0.0
    return round(max(0.0, min(1.0, 1.0 - cv / 2.0)), 4)


def _coverage_score(player_row: dict[str, Any], stat_rows: list[dict[str, Any]]) -> float:
    """Fraction of expected fields that are non-null."""
    total_fields = len(_COVERAGE_FIELDS)
    non_null = sum(
        1 for f in _COVERAGE_FIELDS
        if player_row.get(f) is not None
        or any(r.get(f) is not None for r in stat_rows)
    )
    return round(non_null / total_fields, 4)


def _cross_source_consistency(
    stats_by_source: dict[str, list[dict[str, Any]]],
) -> float:
    """
    Compare aggregated totals across sources using weighted metric agreements.
    Returns 0.65 for single-source data (no cross-validation possible).
    """
    sources = list(stats_by_source.keys())
    if len(sources) < 2:
        return 0.65  # single-source assumption

    # Aggregate per source
    agg: dict[str, dict[str, float]] = {}
    for src, rows in stats_by_source.items():
        agg[src] = {
            "goals": sum(float(r.get("goals") or 0) for r in rows),
            "assists": sum(float(r.get("assists") or 0) for r in rows),
            "minutes": sum(float(r.get("minutes") or 0) for r in rows),
            "appearances": float(len(rows)),
        }

    # Pairwise comparison (use first two sources)
    src_a, src_b = sources[0], sources[1]
    a_agg, b_agg = agg[src_a], agg[src_b]

    weighted_agreement = 0.0
    total_weight = 0.0
    for metric, weight in _METRIC_WEIGHTS.items():
        a_val = a_agg.get(metric, 0.0)
        b_val = b_agg.get(metric, 0.0)
        # Only compare if at least one source has a non-zero value
        if a_val > 0 or b_val > 0:
            weighted_agreement += weight * _agreement(a_val, b_val)
            total_weight += weight

    if total_weight <= 0:
        return 0.65
    return round(weighted_agreement / total_weight, 4)


def compute_player_confidence(
    player_row: dict[str, Any],
    stat_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compute validation_flag, consistency_score, and data_confidence_score
    for a single player.

    Returns:
      {
        "player_name": str,
        "source_count": int,
        "cross_source_consistency": float,
        "internal_consistency": float,
        "coverage_score": float,
        "data_confidence_score": float,
        "validation_flag": "OK" | "LOW_CONFIDENCE" | "SINGLE_SOURCE",
      }
    """
    stats_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in stat_rows:
        src = str(row.get("source") or "unknown")
        stats_by_source[src].append(row)

    source_count = len(stats_by_source)
    cross_src = _cross_source_consistency(stats_by_source)
    internal = _internal_consistency(stat_rows)
    coverage = _coverage_score(player_row, stat_rows)

    # Weighted composite
    data_confidence = round(
        0.45 * cross_src + 0.35 * internal + 0.20 * coverage,
        4,
    )

    if data_confidence < 0.45:
        flag = "LOW_CONFIDENCE"
    elif source_count < 2:
        flag = "SINGLE_SOURCE"
    else:
        flag = "OK"

    return {
        "player_name": player_row.get("player_name"),
        "source_count": source_count,
        "cross_source_consistency": cross_src,
        "internal_consistency": internal,
        "coverage_score": coverage,
        "data_confidence_score": data_confidence,
        "validation_flag": flag,
    }


def build_confidence_index(
    silver_tables: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """
    Build a player_name → confidence record mapping for the entire Silver dataset.
    Used downstream to weight KPI, valuation, similarity, and pathway outputs.
    """
    players_by_name: dict[str, dict[str, Any]] = {}
    for row in silver_tables.get("players", []):
        key = _normalize_key(row.get("player_name"))
        players_by_name[key] = row

    stats_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in silver_tables.get("player_match_stats", []):
        key = _normalize_key(row.get("player_name"))
        stats_by_name[key].append(row)

    all_names = set(players_by_name) | set(stats_by_name)
    index: dict[str, dict[str, Any]] = {}

    for name in all_names:
        player_row = players_by_name.get(name, {})
        stat_rows = stats_by_name.get(name, [])
        result = compute_player_confidence(player_row, stat_rows)
        index[name] = result

        if result["validation_flag"] == "LOW_CONFIDENCE":
            log_event(logger, logging.WARNING, "cross_source.low_confidence",
                      player=name,
                      score=result["data_confidence_score"],
                      flag=result["validation_flag"])

    log_event(logger, logging.INFO, "cross_source.index_built",
              total=len(index),
              low_confidence=sum(1 for r in index.values() if r["validation_flag"] == "LOW_CONFIDENCE"),
              single_source=sum(1 for r in index.values() if r["validation_flag"] == "SINGLE_SOURCE"),
              ok=sum(1 for r in index.values() if r["validation_flag"] == "OK"))
    return index


def filter_confident_rows(
    rows: list[dict[str, Any]],
    confidence_index: dict[str, dict[str, Any]],
    min_confidence: float = 0.60,
    name_field: str = "player_name",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Split rows into (confident, excluded) based on data_confidence_score threshold.
    Rows with no confidence entry are kept (no evidence to exclude them).
    """
    confident: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for row in rows:
        key = _normalize_key(row.get(name_field))
        conf = confidence_index.get(key, {})
        score = conf.get("data_confidence_score", 1.0)  # default: keep
        flag = conf.get("validation_flag", "OK")

        if flag == "LOW_CONFIDENCE" and score < min_confidence:
            excluded.append({**row, "_excluded_reason": "LOW_CONFIDENCE", "_confidence": score})
            log_event(logger, logging.INFO, "cross_source.excluded_row",
                      player=key, score=score)
        else:
            confident.append(row)

    return confident, excluded
