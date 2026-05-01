"""
Advanced metrics engine v2: xG, xA, xT, EPV, OBV.
Uses simplified positional models — no event-level data required.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "advanced_metrics_v2"

# Shot quality multipliers by context (when context unavailable, use average)
SHOT_QUALITY_BASE = 0.10  # avg xG per shot
HEADER_MULTIPLIER = 0.7
SET_PIECE_MULTIPLIER = 1.2
OPEN_PLAY_MULTIPLIER = 1.0

# xT threat value per progressive action type
XT_PROGRESSIVE_CARRY = 0.05
XT_PROGRESSIVE_PASS = 0.04
XT_FINAL_THIRD_ENTRY = 0.07
XT_PENALTY_AREA_ENTRY = 0.12

# OBV baseline
OBV_PER_GOAL = 2.5
OBV_PER_ASSIST = 1.8
OBV_PER_SHOT = 0.15
OBV_PER_KEY_PASS = 0.35


def estimate_xg(
    shots: float | None,
    goals: float | None,
    headers: float | None = None,
    set_pieces: float | None = None,
) -> float | None:
    """Estimate xG from shot counts using average shot quality."""
    if not shots:
        return None
    open_play_shots = float(shots or 0)
    header_shots = float(headers or 0)
    sp_shots = float(set_pieces or 0)
    remaining = max(0.0, open_play_shots - header_shots - sp_shots)
    xg = (
        header_shots * SHOT_QUALITY_BASE * HEADER_MULTIPLIER
        + sp_shots * SHOT_QUALITY_BASE * SET_PIECE_MULTIPLIER
        + remaining * SHOT_QUALITY_BASE * OPEN_PLAY_MULTIPLIER
    )
    # Calibrate: if actual goals are available, blend estimate with goals-based
    if goals is not None and float(shots) > 0:
        goal_rate = float(goals) / float(shots)
        xg = (xg * 0.6 + float(shots) * goal_rate * 0.4)
    return round(max(0.0, xg), 3)


def estimate_xa(
    assists: float | None,
    key_passes: float | None = None,
) -> float | None:
    """Estimate xA from assists and key passes."""
    if assists is None and key_passes is None:
        return None
    a = float(assists or 0)
    kp = float(key_passes or 0)
    xa = a * 0.85 + kp * 0.12
    return round(max(0.0, xa), 3)


def estimate_xt(
    progressive_actions: float | None = None,
    final_third_entries: float | None = None,
    penalty_area_entries: float | None = None,
    minutes: float | None = None,
) -> dict[str, float | None]:
    """Estimate Expected Threat from progression metrics."""
    if not any([progressive_actions, final_third_entries, penalty_area_entries]):
        return {"xt_total": None, "xt_per_90": None}

    xt_raw = (
        float(progressive_actions or 0) * XT_PROGRESSIVE_CARRY
        + float(final_third_entries or 0) * XT_FINAL_THIRD_ENTRY
        + float(penalty_area_entries or 0) * XT_PENALTY_AREA_ENTRY
    )
    xt_p90 = (xt_raw / float(minutes) * 90.0) if minutes and minutes > 0 else None
    return {
        "xt_total": round(xt_raw, 3),
        "xt_per_90": round(xt_p90, 3) if xt_p90 is not None else None,
    }


def estimate_epv(
    goals: float | None,
    assists: float | None,
    shots: float | None,
    minutes: float | None,
) -> float | None:
    """Per-90 contribution proxy (labelled EPV for display; not true event-level EPV)."""
    if not minutes or minutes <= 0:
        return None
    raw = (
        float(goals or 0) * 2.0
        + float(assists or 0) * 1.5
        + float(shots or 0) * 0.08
    )
    return round(raw / float(minutes) * 90.0, 3)


def estimate_obv(
    goals: float | None,
    assists: float | None,
    shots: float | None,
    key_passes: float | None = None,
) -> float | None:
    """Weighted output score proxy (labelled OBV for display; not true StatsBomb OBV)."""
    g = float(goals or 0) * OBV_PER_GOAL
    a = float(assists or 0) * OBV_PER_ASSIST
    s = float(shots or 0) * OBV_PER_SHOT
    kp = float(key_passes or 0) * OBV_PER_KEY_PASS
    return round(g + a + s + kp, 3)


def per_90(value: float | None, minutes: float | None) -> float | None:
    if value is None or not minutes or minutes <= 0:
        return None
    return round(float(value) / float(minutes) * 90.0, 3)


# ── Builder ───────────────────────────────────────────────────────────────────

def build_advanced_metrics_v2_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    gold_tables: dict[str, list[dict[str, Any]]],
) -> dict[str, object]:
    features_by_name = {
        str(r.get("player_name") or "").strip().lower(): r
        for r in gold_tables.get("player_features", [])
    }

    stat_rows_by_name: dict[str, list] = defaultdict(list)
    for row in silver_tables.get("player_match_stats", []):
        k = str(row.get("player_name") or "").strip().lower()
        stat_rows_by_name[k].append(row)

    all_names = sorted(set(features_by_name) | set(stat_rows_by_name))

    if not all_names:
        path = write_json(Path(settings.gold_data_dir) / "advanced_metrics.json", [])
        return {"path": path, "rows": []}

    output_rows: list[dict[str, Any]] = []

    for name in all_names:
        fr = features_by_name.get(name, {})
        stats = stat_rows_by_name.get(name, [])

        total_goals = sum(float(s.get("goals") or 0) for s in stats)
        total_assists = sum(float(s.get("assists") or 0) for s in stats)
        total_shots = sum(float(s.get("shots") or 0) for s in stats)
        total_minutes = sum(float(s.get("minutes") or 0) for s in stats)
        # FBref xG/xA — use source data directly when available
        fbref_xg = sum(float(s.get("xg") or 0) for s in stats if s.get("xg") is not None)
        fbref_xa = sum(float(s.get("xa") or 0) for s in stats if s.get("xa") is not None)
        has_fbref_xg = any(s.get("xg") is not None for s in stats)
        has_fbref_xa = any(s.get("xa") is not None for s in stats)
        # Progressive action totals for xT
        prog_carries = sum(int(s.get("progressive_carries") or 0) for s in stats)
        final_third = sum(
            int(s.get("carries_into_final_third") or 0) + int(s.get("passes_into_final_third") or 0)
            for s in stats
        )
        penalty_area = sum(
            int(s.get("carries_into_penalty_area") or 0) + int(s.get("passes_into_penalty_area") or 0)
            for s in stats
        )

        # Fall back to feature row if no stats
        goals = total_goals or float(fr.get("goals") or 0)
        assists = total_assists or float(fr.get("assists") or 0)
        shots = total_shots or float(fr.get("shots") or 0)
        minutes = total_minutes or float(fr.get("minutes") or 0)

        # Use FBref xG/xA when available; fall back to estimate
        xg = fbref_xg if has_fbref_xg else estimate_xg(shots, goals)
        xa = fbref_xa if has_fbref_xa else estimate_xa(assists)
        # xT uses real progressive action data
        xt = estimate_xt(
            progressive_actions=prog_carries or None,
            final_third_entries=final_third or None,
            penalty_area_entries=penalty_area or None,
            minutes=minutes or None,
        )
        epv = estimate_epv(goals, assists, shots, minutes)
        obv = estimate_obv(goals, assists, shots)

        prog_score_raw = float(fr.get("goal_contribution_per_90") or 0) * 10.0

        display_name = fr.get("player_name") or stats[0].get("player_name") if stats else name

        output_rows.append({
            "player_name": display_name or name,
            "xg_total": xg,
            "xa_total": xa,
            "xg_per_90": per_90(xg, minutes),
            "xa_per_90": per_90(xa, minutes),
            "xt_total": xt.get("xt_total"),
            "xt_per_90": xt.get("xt_per_90"),
            "epv_proxy_per_90": epv,
            "obv_proxy_total": obv,
            "progression_score": round(min(10.0, prog_score_raw), 3),
            "inputs": {
                "goals": goals,
                "assists": assists,
                "shots": shots,
                "minutes": minutes,
            },
            "model_version": MODEL_VERSION,
        })

    output_rows.sort(key=lambda r: r.get("obv_proxy_total") or 0.0, reverse=True)
    path = write_json(Path(settings.gold_data_dir) / "advanced_metrics.json", output_rows)
    return {"path": path, "rows": output_rows}
