"""
Feature store builder.

Consolidates all player features from every Gold-layer module into a single
normalized record per player at data/gold/feature_store.json.

This is the authoritative single source of truth used by:
  - similarity engine
  - clustering engine
  - alert system
  - API /players endpoint
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json
from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_NORMALIZABLE_FIELDS = [
    "goals_per_90", "assists_per_90", "shots_per_90",
    "passes_completed_per_90", "xg_per_90", "xa_per_90",
    "base_kpi_score", "age_adjusted_kpi_score",
    "valuation_score", "risk_score",
]


def _norm_key(name: str | None) -> str:
    return str(name or "").strip().lower()


def _safe_float(v: Any, default: float | None = None) -> float | None:
    if v is None:
        return default
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _min_max_normalize(
    rows: list[dict[str, Any]],
    fields: list[str],
) -> list[dict[str, Any]]:
    """Add `{field}_norm` columns (0-1) to each row."""
    for field in fields:
        vals = [_safe_float(r.get(field)) for r in rows if _safe_float(r.get(field)) is not None]
        if not vals:
            continue
        lo, hi = min(vals), max(vals)
        span = hi - lo
        for r in rows:
            v = _safe_float(r.get(field))
            if v is None or span <= 0:
                r[f"{field}_norm"] = None
            else:
                r[f"{field}_norm"] = round((v - lo) / span, 4)
    return rows


def build_feature_store(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    valuation_rows: list[dict[str, Any]] | None = None,
    advanced_metric_rows: list[dict[str, Any]] | None = None,
    risk_rows: list[dict[str, Any]] | None = None,
    pathway_rows: list[dict[str, Any]] | None = None,
    similarity_rows: list[dict[str, Any]] | None = None,
    transfer_rows: list[dict[str, Any]] | None = None,
    market_value_rows: list[dict[str, Any]] | None = None,
    cluster_rows: list[dict[str, Any]] | None = None,
    confidence_index: dict[str, Any] | None = None,
) -> dict[str, object]:
    """
    Merge all Gold-layer outputs into one normalized feature record per player.
    """
    valuation_rows = valuation_rows or []
    advanced_metric_rows = advanced_metric_rows or []
    risk_rows = risk_rows or []
    pathway_rows = pathway_rows or []
    similarity_rows = similarity_rows or []
    transfer_rows = transfer_rows or []
    market_value_rows = market_value_rows or []
    cluster_rows = cluster_rows or []
    confidence_index = confidence_index or {}

    # Build per-module lookups
    kpi_by_name = {_norm_key(r.get("player_name")): r for r in kpi_rows}
    val_by_name = {_norm_key(r.get("player_name")): r for r in valuation_rows}
    adv_by_name = {_norm_key(r.get("player_name")): r for r in advanced_metric_rows}
    risk_by_name = {_norm_key(r.get("player_name")): r for r in risk_rows}
    path_by_name = {_norm_key(r.get("player_name")): r for r in pathway_rows}
    sim_by_name = {_norm_key(r.get("player_name")): r for r in similarity_rows}
    xfer_by_name = {_norm_key(r.get("player_name")): r for r in transfer_rows}
    mv_by_name = {_norm_key(r.get("player_name")): r for r in market_value_rows}
    clust_by_name = {_norm_key(r.get("player_name")): r for r in cluster_rows}
    player_by_name = {
        _norm_key(r.get("player_name")): r
        for r in silver_tables.get("players", [])
    }

    # Competition per player
    from collections import Counter
    comp_by_name: dict[str, str] = {}
    for row in silver_tables.get("player_match_stats", []):
        k = _norm_key(row.get("player_name"))
        if row.get("competition"):
            comp_by_name.setdefault(k, row["competition"])

    all_names = sorted(
        set(kpi_by_name) | set(val_by_name) | set(player_by_name)
    )

    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        pr = player_by_name.get(name, {})
        kr = kpi_by_name.get(name, {})
        vr = val_by_name.get(name, {})
        ar = adv_by_name.get(name, {})
        rr = risk_by_name.get(name, {})
        patr = path_by_name.get(name, {})
        xr = xfer_by_name.get(name, {})
        mvr = mv_by_name.get(name, {})
        cr = clust_by_name.get(name, {})
        conf = confidence_index.get(name, {})

        row: dict[str, Any] = {
            # Identity
            "player_name": pr.get("player_name") or kr.get("player_name") or name,
            "position": pr.get("position"),
            "nationality": pr.get("nationality"),
            "date_of_birth": pr.get("date_of_birth"),
            "current_club": pr.get("current_club"),
            "competition": comp_by_name.get(name),

            # KPI
            "age": kr.get("age"),
            "minutes_played": kr.get("minutes_played"),
            "goals_per_90": kr.get("goals_per_90"),
            "assists_per_90": kr.get("assists_per_90"),
            "shots_per_90": kr.get("shots_per_90"),
            "passes_completed_per_90": kr.get("passes_completed_per_90"),
            "goal_contributions_per_90": kr.get("goal_contributions_per_90"),
            "consistency_score": kr.get("consistency_score"),
            "base_kpi_score": kr.get("base_kpi_score"),
            "age_adjusted_kpi_score": kr.get("age_adjusted_kpi_score"),
            "age_multiplier": kr.get("age_multiplier"),

            # Advanced metrics
            "xg_per_90": ar.get("xg_per_90"),
            "xa_per_90": ar.get("xa_per_90"),
            "xt_total": ar.get("xt_total"),
            "epv_proxy": ar.get("epv_proxy"),
            "obv_proxy": ar.get("obv_proxy"),
            "progression_score": ar.get("progression_score"),

            # Risk
            "risk_score": rr.get("risk_score"),
            "injury_risk": rr.get("injury_risk"),
            "volatility_risk": rr.get("volatility_risk"),
            "discipline_risk": rr.get("discipline_risk"),

            # Valuation
            "valuation_score": vr.get("valuation_score"),
            "potential_score": vr.get("potential_score"),
            "market_value_eur": vr.get("market_value_eur"),
            "computed_value_eur": vr.get("computed_value_eur"),
            "undervalued": vr.get("undervalued"),
            "value_gap_pct": vr.get("value_gap_pct"),

            # Market value model
            "predicted_value_eur": mvr.get("predicted_value_eur"),
            "blended_value_eur": mvr.get("blended_value_eur"),
            "value_confidence": mvr.get("value_confidence"),

            # Pathway
            "development_stage": patr.get("development_stage"),
            "trajectory": patr.get("trajectory"),
            "best_pathway": patr.get("best_pathway"),
            "success_probability": patr.get("success_probability"),
            "next_recommended_league": patr.get("next_recommended_league"),

            # Similarity
            "top_comps": (sim_by_name.get(name) or {}).get("top_comps"),

            # Transfer probability
            "transfer_probability_1y": xr.get("transfer_probability_1y"),
            "transfer_probability_2y": xr.get("transfer_probability_2y"),
            "transfer_category": xr.get("transfer_category"),

            # Clustering
            "cluster_id": cr.get("cluster_id"),
            "cluster_label": cr.get("cluster_label"),

            # Data quality
            "data_confidence_score": conf.get("data_confidence_score"),
            "validation_flag": conf.get("validation_flag"),
            "source_count": conf.get("source_count"),
        }
        output_rows.append(row)

    # Add normalized columns
    output_rows = _min_max_normalize(output_rows, _NORMALIZABLE_FIELDS)

    output_rows.sort(
        key=lambda r: float(r.get("age_adjusted_kpi_score") or 0), reverse=True
    )

    path = write_json(Path(settings.gold_data_dir) / "feature_store.json", output_rows)
    log_event(logger, logging.INFO, "feature_store.built",
              players=len(output_rows), path=str(path))
    return {"path": path, "rows": output_rows}
