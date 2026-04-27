from __future__ import annotations

from typing import Any


def dashboard_status_message(status_payload: dict[str, Any] | None) -> tuple[str, str]:
    if not status_payload:
        return "info", "Dashboard status is currently unavailable."

    status = str(status_payload.get("status") or "unknown").strip().lower()
    if status == "ready":
        return "success", "Dashboard data is ready."
    if status == "partial":
        return "info", "Dashboard data is partially available. Some sections may still be empty."
    if status == "empty":
        return "warning", "No dashboard data is available yet. The backend is reachable, but the current artifacts are empty."
    if status == "artifact_missing":
        return "error", "Required dashboard artifacts are missing. Run the pipeline first."
    if status == "artifact_invalid":
        return "error", "Dashboard artifacts exist but are invalid. Check backend outputs."
    return "info", f"Dashboard status: {status}."


def artifact_summary_rows(status_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    artifacts = (status_payload or {}).get("artifacts") or {}
    rows: list[dict[str, Any]] = []
    for name, artifact in artifacts.items():
        if not isinstance(artifact, dict):
            continue
        rows.append(
            {
                "artifact": name,
                "state": artifact.get("state"),
                "row_count": artifact.get("row_count"),
                "required": artifact.get("required"),
                "error": artifact.get("error"),
            }
        )
    return rows


def explain_players_empty(status_payload: dict[str, Any] | None) -> str:
    artifacts = (status_payload or {}).get("artifacts") or {}
    players = artifacts.get("players") or {}
    if players.get("state") == "empty":
        return "Player data is not available yet because the players artifact is empty. Run the pipeline and refresh."
    if players.get("state") == "missing":
        return "Player data is not available because the players artifact is missing. Run the pipeline first."
    if players.get("state") == "invalid":
        return "Player data is not available because the players artifact is invalid. Check backend outputs."
    return "Player data is not available yet."


def explain_stats_issue(status_payload: dict[str, Any] | None) -> str:
    artifacts = (status_payload or {}).get("artifacts") or {}
    stats = artifacts.get("player_match_stats") or {}
    if stats.get("state") == "empty":
        return "Match stats are not available yet because the player-match-stats artifact is empty."
    if stats.get("state") == "missing":
        return "Match stats are unavailable because the player-match-stats artifact is missing."
    if stats.get("state") == "invalid":
        return "Match stats are unavailable because the player-match-stats artifact is invalid."
    return "Match stats are currently unavailable for this player."


def explain_compare_issue(status_payload: dict[str, Any] | None) -> str:
    artifacts = (status_payload or {}).get("artifacts") or {}
    similarity = artifacts.get("similarity") or {}
    if similarity.get("state") == "empty":
        return "Comparison data is not available yet because the similarity artifact is empty."
    if similarity.get("state") == "missing":
        return "Comparison data is unavailable because the similarity artifact is missing."
    if similarity.get("state") == "invalid":
        return "Comparison data is unavailable because the similarity artifact is invalid."
    return "Comparison data is unavailable right now."


def enrich_similarity_rows(similar_rows: list[dict[str, Any]], valuation_lookup: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    enriched_rows: list[dict[str, Any]] = []
    for row in similar_rows:
        merged = dict(row)
        valuation = valuation_lookup.get(row.get("player_name")) or {}
        if valuation:
            merged["valuation_score"] = valuation.get("valuation_score")
            merged["valuation_tier"] = valuation.get("valuation_tier")
            merged["valuation_model_version"] = valuation.get("model_version")
            if not merged.get("position"):
                merged["position"] = valuation.get("position")
            if not merged.get("current_club"):
                merged["current_club"] = valuation.get("current_club")
        enriched_rows.append(merged)
    return enriched_rows
