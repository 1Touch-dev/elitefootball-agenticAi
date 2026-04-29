"""
Club Benchmarking System: IDV vs Benfica vs Ajax vs Salzburg.
Metrics: player_improvement_rate, resale_multiplier, success_rate.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


MODEL_VERSION = "club_benchmark_v2"

TRACKED_CLUBS = ["IDV", "Benfica", "Ajax", "Salzburg"]

CLUB_ALIASES: dict[str, str] = {
    "idv": "IDV",
    "independiente del valle": "IDV",
    "c.s.d. independiente del valle": "IDV",
    "benfica": "Benfica",
    "sl benfica": "Benfica",
    "sport lisboa e benfica": "Benfica",
    "ajax": "Ajax",
    "afc ajax": "Ajax",
    "amsterdamsche football club ajax": "Ajax",
    "salzburg": "Salzburg",
    "rb salzburg": "Salzburg",
    "red bull salzburg": "Salzburg",
}

# Reference benchmarks (historical data seeded)
REFERENCE_BENCHMARKS: dict[str, dict[str, float]] = {
    "IDV": {
        "avg_player_improvement_rate": 8.5,
        "avg_resale_multiplier": 4.2,
        "success_rate": 0.62,
        "avg_age_at_breakout": 20.1,
        "players_exported_to_europe": 12,
    },
    "Benfica": {
        "avg_player_improvement_rate": 12.0,
        "avg_resale_multiplier": 6.8,
        "success_rate": 0.71,
        "avg_age_at_breakout": 21.5,
        "players_exported_to_europe": 45,
    },
    "Ajax": {
        "avg_player_improvement_rate": 14.0,
        "avg_resale_multiplier": 8.5,
        "success_rate": 0.76,
        "avg_age_at_breakout": 20.8,
        "players_exported_to_europe": 60,
    },
    "Salzburg": {
        "avg_player_improvement_rate": 11.5,
        "avg_resale_multiplier": 7.2,
        "success_rate": 0.68,
        "avg_age_at_breakout": 20.4,
        "players_exported_to_europe": 38,
    },
}


def _normalize_club(value: str | None) -> str | None:
    key = str(value or "").strip().lower()
    return CLUB_ALIASES.get(key)


def club_development_score(club_name: str | None) -> float:
    """Return 0–100 score for club's development quality."""
    canonical = _normalize_club(club_name)
    scores = {
        "Ajax": 95.0,
        "Benfica": 90.0,
        "Salzburg": 88.0,
        "IDV": 75.0,
    }
    return scores.get(canonical or "", 50.0)


def compute_live_club_metrics(
    kpi_rows: list[dict[str, Any]],
    silver_players: list[dict[str, Any]],
    transfer_rows: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Compute live club metrics from available data."""
    transfer_rows = transfer_rows or []

    by_club: dict[str, list[dict]] = defaultdict(list)
    for row in kpi_rows:
        for p in silver_players:
            if str(p.get("player_name") or "").strip().lower() == str(row.get("player_name") or "").strip().lower():
                club = _normalize_club(p.get("current_club"))
                if club:
                    by_club[club].append({**row, "club": club})

    live_metrics: dict[str, dict[str, Any]] = {}
    for club in TRACKED_CLUBS:
        players = by_club.get(club, [])
        if not players:
            live_metrics[club] = {"live_data": False, "player_count": 0}
            continue

        avg_kpi = sum(float(p.get("base_kpi_score") or 0) for p in players) / len(players)
        avg_consistency = sum(float(p.get("consistency_score") or 0) for p in players) / len(players)

        live_metrics[club] = {
            "live_data": True,
            "player_count": len(players),
            "avg_kpi_score": round(avg_kpi, 2),
            "avg_consistency_score": round(avg_consistency, 3),
        }

    return live_metrics


def build_club_benchmark_output(
    silver_tables: dict[str, list[dict[str, Any]]],
    kpi_rows: list[dict[str, Any]],
    transfer_rows: list[dict[str, Any]] | None = None,
) -> dict[str, object]:
    transfer_rows = transfer_rows or []
    silver_players = silver_tables.get("players", [])

    live_metrics = compute_live_club_metrics(kpi_rows, silver_players, transfer_rows)

    output_rows: list[dict[str, Any]] = []
    for club in TRACKED_CLUBS:
        reference = REFERENCE_BENCHMARKS.get(club, {})
        live = live_metrics.get(club, {})

        output_rows.append({
            "club": club,
            "development_score": club_development_score(club),
            "reference_benchmarks": reference,
            "live_metrics": live,
            "comparison_vs_idv": _compare_vs_idv(club, reference),
            "model_version": MODEL_VERSION,
        })

    path = write_json(Path(settings.gold_data_dir) / "club_development_rankings.json", output_rows)
    return {"path": path, "rows": output_rows}


def _compare_vs_idv(club: str, reference: dict[str, float]) -> dict[str, Any]:
    if club == "IDV":
        return {"note": "baseline"}
    idv_ref = REFERENCE_BENCHMARKS.get("IDV", {})
    result: dict[str, Any] = {}
    for metric in ["avg_player_improvement_rate", "avg_resale_multiplier", "success_rate"]:
        club_val = reference.get(metric)
        idv_val = idv_ref.get(metric)
        if club_val is not None and idv_val and idv_val > 0:
            result[f"{metric}_delta_vs_idv"] = round(club_val - idv_val, 2)
            result[f"{metric}_ratio_vs_idv"] = round(club_val / idv_val, 2)
    return result
