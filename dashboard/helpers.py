from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def format_sync_time(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        normalized = raw.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        else:
            parsed = parsed.astimezone(UTC)
    except ValueError:
        return raw
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def dashboard_status_message(status_payload: dict[str, Any] | None) -> tuple[str, str]:
    state = build_dashboard_state(status_payload)
    return state["level"], state["message"]


def build_dashboard_state(
    status_payload: dict[str, Any] | None,
    *,
    backend_error: str | None = None,
    no_records_label: str | None = None,
) -> dict[str, str | None]:
    if backend_error:
        return {
            "category": "backend_error",
            "level": "error",
            "title": "Backend unavailable",
            "message": f"The dashboard could not reach the backend API. {backend_error}",
            "action": "Check that the backend is running, then retry.",
            "last_sync": None,
            "failure": None,
        }

    if not status_payload:
        return {
            "category": "unknown",
            "level": "info",
            "title": "Status unavailable",
            "message": "Dashboard status is currently unavailable.",
            "action": "Refresh the page after confirming the backend is running.",
            "last_sync": None,
            "failure": None,
        }

    status = str(status_payload.get("status") or "unknown").strip().lower()
    sync = status_payload.get("sync") if isinstance(status_payload.get("sync"), dict) else {}
    diagnostics = status_payload.get("diagnostics") if isinstance(status_payload.get("diagnostics"), dict) else {}
    last_sync = format_sync_time(sync.get("last_successful_sync_at")) or "No successful sync yet."
    failure_stage = sync.get("last_failure_stage")
    failure_message = sync.get("last_failure_message")
    failure = None
    if failure_stage or failure_message:
        failure = ": ".join(part for part in [str(failure_stage or "").strip() or None, str(failure_message or "").strip() or None] if part)
    action = str(sync.get("recommended_action") or diagnostics.get("recommended_action") or "Refresh the dashboard.")

    if no_records_label:
        last_sync_text = "No successful sync" if not last_sync else last_sync
        return {
            "category": "no_records",
            "level": "info",
            "title": f"No {no_records_label} found",
            "message": f"The dashboard is reachable, but no {no_records_label} are available for the current selection yet.",
            "action": action,
            "last_sync": last_sync_text,
            "failure": failure or "No failure recorded.",
        }

    if status == "ready":
        return {
            "category": "ready",
            "level": "success",
            "title": "Dashboard data is ready",
            "message": "The backend is reachable and the required dashboard artifacts are available.",
            "action": action,
            "last_sync": last_sync,
            "failure": failure,
        }
    if status == "partial":
        return {
            "category": "partial",
            "level": "warning",
            "title": "Dashboard data is only partially available",
            "message": "Some sections can render, but one or more required dashboard artifacts are still empty.",
            "action": action,
            "last_sync": last_sync,
            "failure": failure,
        }
    if status == "empty":
        return {
            "category": "empty",
            "level": "warning",
            "title": "No dashboard data yet",
            "message": "The backend is reachable, but the current dashboard artifacts do not contain any records yet.",
            "action": action,
            "last_sync": last_sync,
            "failure": failure,
        }
    if status == "artifact_missing":
        return {
            "category": "upstream_failure",
            "level": "error",
            "title": "Dashboard data is missing",
            "message": "Required dashboard artifacts are missing, so the scrape or pipeline output is not ready for the UI.",
            "action": action,
            "last_sync": last_sync,
            "failure": failure,
        }
    if status == "artifact_invalid":
        return {
            "category": "upstream_failure",
            "level": "error",
            "title": "Dashboard data is invalid",
            "message": "The backend found dashboard artifacts, but at least one payload is invalid and cannot be rendered safely.",
            "action": action,
            "last_sync": last_sync,
            "failure": failure,
        }
    return {
        "category": "unknown",
        "level": "info",
        "title": "Dashboard status is unknown",
        "message": f"Dashboard status: {status}.",
        "action": action,
        "last_sync": last_sync,
        "failure": failure,
    }


def placeholder_message_lines(state: dict[str, str | None]) -> list[str]:
    lines = [str(state.get("message") or "")]
    if state.get("last_sync"):
        lines.append(f"Last successful sync: {state['last_sync']}")
    if state.get("failure"):
        lines.append(f"Latest failure: {state['failure']}")
    if state.get("action"):
        lines.append(f"Next step: {state['action']}")
    return [line for line in lines if line]


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
        return "Player data is not available yet because the players artifact is empty. The scrape or pipeline has not produced player rows for the dashboard yet."
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
    return "No recent match records were found for this player."


def explain_compare_issue(status_payload: dict[str, Any] | None) -> str:
    artifacts = (status_payload or {}).get("artifacts") or {}
    similarity = artifacts.get("similarity") or {}
    if similarity.get("state") == "empty":
        return "Comparison data is not available yet because the similarity artifact is empty."
    if similarity.get("state") == "missing":
        return "Comparison data is unavailable because the similarity artifact is missing."
    if similarity.get("state") == "invalid":
        return "Comparison data is unavailable because the similarity artifact is invalid."
    return "No comparison records were found for this player yet."


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
